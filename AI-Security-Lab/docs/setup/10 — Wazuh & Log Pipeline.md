# 10 — Wazuh & Log Pipeline

> 蓝队检测的生命线:靶机日志 → Wazuh → Splunk。GCP 版**内网直连**,无隧道。在 **lab VM** 上配。

---

## 10.1 日志管道

```
靶机 app.py ──FileHandler──> 共享卷 ai-logs (/var/log/ai-lab/*.json, 单层 JSON)
        ──Wazuh 只读挂载──> Wazuh Manager (custom_ai_rules.xml 匹配)
        ──同 VPC 内网直发 8088 (Wazuh_Token)──> Splunk HEC ──> index=ai_logs
```

- 靶机写**单层 JSON** 到共享命名卷 `ai-logs`(`docker-compose.yml` 已配),Wazuh 直接读,
  **绕开 Docker 双层 JSON 包装**。
- `ossec.conf` 的 `<localfile>` 用通配符 `/var/log/ai-lab/*.json`,自动收全 llm/rag/agent/ml-api。

## 10.2 配置 `infrastructure/configs/wazuh/ossec.conf`

> 这份文件比"填两个占位符"复杂——下面每一块都是从实际踩坑里摸出来的必需项,少一块都会导致 wazuh-manager
> 启动失败或者检测链路断在中间。完整内容如下,只需改 `hook_url`/`api_key` 两处占位符:

```xml
<!-- Wazuh Manager Configuration for AI Security Lab -->
<ossec_config>

  <!-- 1. Splunk HEC Integration (Alert Forwarding) -->
  <integration>
    <name>custom-splunk-hec</name>
    <hook_url>https://YOUR_SPLUNK_INTERNAL_IP:8088/services/collector</hook_url>
    <api_key>YOUR_SPLUNK_HEC_TOKEN</api_key>   <!-- 填 Wazuh_Token,真实值记在本地 docs/setup/credentials.md(不上传) -->
    <level>5</level>
    <alert_format>json</alert_format>
  </integration>

  <!-- 1a. Remote listener — 必需,不是可选项。wazuh-control 启动时如果 wazuh-remoted
       完全没有 <remote> 配置会报 CRITICAL 并让整个 manager 启动流程失败退出(不只是
       remoted 自己崩,analysisd/db/modulesd 全部起不来)。我们不用真实 Wazuh agent,
       这里只是让 remoted 能正常初始化。 -->
  <remote>
    <connection>secure</connection>
    <port>1514</port>
    <protocol>tcp</protocol>
    <queue_size>131072</queue_size>
  </remote>

  <!-- 2. AI App Log Collection (Shared Volume) -->
  <!-- 靶机写单层 JSON 到共享卷,Wazuh 直接读,绕开 Docker 双层 JSON 包装。
       通配符自动收全 llm-app/rag-app/agent-app/ml-api。 -->
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/ai-lab/*.json</location>
  </localfile>

  <!-- 3. Ruleset — decoder_dir/rule_dir 的官方路径必须排在 etc/rules 之前。
       没有 if_sid/if_group/if_level 的规则(比如我们自己的检测规则)靠 category
       挂到"已存在的同类别根节点"上;如果官方 ruleset/rules 没有显式声明在前面,
       我们的规则会因为找不到根节点挂载点而报 "Category was not found",
       最终 0 条规则启用,analysisd 直接崩溃退出。
       另外排除 Suricata 规则(0475):它的 86600 通用兜底规则条件是
       "json 解码 + 有 timestamp 字段 + 有 event_type 字段",我们的 AI app 日志刚好
       两个字段都有,会被它先"抢走"事件,导致我们自己的规则永远匹配不到。
       这个 lab 不用 Suricata,直接排除最干净。 -->
  <ruleset>
    <decoder_dir>ruleset/decoders</decoder_dir>
    <rule_dir>ruleset/rules</rule_dir>
    <rule_exclude>0475-suricata_rules.xml</rule_exclude>
    <rule_dir>etc/rules</rule_dir>
  </ruleset>

</ossec_config>
```
- `YOUR_SPLUNK_INTERNAL_IP` = Splunk VM 的 **VPC 内网 IP**(`04` 查过,同 VPC,**不要**填公网 IP)。
- ⚠️ **不要**改成 `host.docker.internal` 或 IAP——GCP 版是内网直连。

## 10.2a 补 `ar.conf`(必需,否则 analysisd 启动即崩)

`wazuh-analysisd` 启动时会强制尝试打开 `etc/shared/ar.conf`(Active Response 配置),就算完全不用 Active Response,
文件不存在也会直接 `CRITICAL: Configuration error` 退出。新建一个**空文件**就够了:

```bash
touch infrastructure/configs/wazuh/ar.conf
```
挂进 `docker-compose.yml` 的 `wazuh-manager` → `volumes:`:
```yaml
- ../infrastructure/configs/wazuh/ar.conf:/var/ossec/etc/shared/ar.conf
```

## 10.2b 补 Splunk HEC 集成脚本(必做,`docker-compose.yml` 里默认没有)

> ⚠️ Wazuh **没有内置的 Splunk 集成**——`<name>` 只要是以 `custom-` 开头(这里是 `custom-splunk-hec`),Wazuh 就只会去容器里的
> `/var/ossec/integrations/custom-splunk-hec` 找一个你自己提供的可执行脚本,把 `hook_url`/`api_key`/告警文件路径当参数传给它,
> 由脚本自己去 POST。光填 10.2 的两个占位符,没有这个脚本,Wazuh 侧什么都不会往 Splunk 发。

1. 新建 `infrastructure/configs/wazuh/custom-splunk-hec`:
```python
#!/usr/bin/env python3
import sys, json, ssl, urllib.request

alert_file, api_key, hook_url = sys.argv[1], sys.argv[2], sys.argv[3]

with open(alert_file) as f:
    alert = json.load(f)

# 只用标准库(urllib.request),不用 requests —— wazuh-manager 容器自带的 Python
# 环境没装 requests,用了会 ModuleNotFoundError,集成脚本静默失败。
payload = json.dumps({"event": alert, "sourcetype": "_json"}).encode("utf-8")
req = urllib.request.Request(
    hook_url,
    data=payload,
    headers={"Authorization": f"Splunk {api_key}", "Content-Type": "application/json"},
    method="POST",
)

# Splunk HEC 默认自签名证书,内网 lab 场景可以忽略校验
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    urllib.request.urlopen(req, context=ctx, timeout=10)
except Exception:
    pass
```

2. `docker-compose.yml` 的 `wazuh-manager` 服务 `volumes:` 里加一行,把脚本挂进容器:
```yaml
- ../infrastructure/configs/wazuh/custom-splunk-hec:/var/ossec/integrations/custom-splunk-hec
```

> ⚠️ 脚本权限(`chown root:wazuh` + `chmod 750`)必须在 **lab VM** 上、紧挨着点火前设置,挪到了 [`11 — Igniting the Lab`](<11 — Igniting the Lab.md>) §11.3a,跟其它点火前收尾步骤放一起。
> **这一步会连带改掉宿主机上这个文件的权限**(bind mount 共享同一个 inode),之后想在 VM 上再编辑这个脚本,
> 普通用户会 `Permission denied`,必须用 `sudo tee` 写,不能用 `cat > file` 或编辑器直接保存(细节见 `11` §11.3a)。

## 10.3 防火墙(已在 `02` 放行)

`02` 的 `allow-internal` 已放行子网内 8088,**无需额外操作**。如当时拆成单端口规则,确认 8088 在内。

## 10.4 自定义检测规则(已随 compose 挂载)
`detection-rules/wazuh/custom_ai_rules.xml` 被挂进 Wazuh:
- Rule 100000 (L0,不产生告警) 基础指纹规则——靠 `app` 字段(`llm-app`/`rag-app`/`agent-app`/`ml-api`)确认"这是我们自己的
  AI app 日志",后面几条规则全部 `<if_sid>` 挂在它下面。这条不能省:如果没有专属父规则,自己的规则会跟其它规则集
  (比如 Suricata)在 category 根节点上抢事件,谁先加载谁赢,不保证一定轮到我们自己的规则。
- Rule 100001 (L3) AI `/api/` 访问基线
- Rule 100002 (L8) 提示注入关键词
- Rule 100003 (L10) Agent 危险命令

➡️ 下一步:**[`11 — Igniting the Lab`](<11 — Igniting the Lab.md>)**
