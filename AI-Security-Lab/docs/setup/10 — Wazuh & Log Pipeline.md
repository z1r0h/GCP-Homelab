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

只需改两处占位符:
```xml
<hook_url>https://YOUR_SPLUNK_INTERNAL_IP:8088/services/collector</hook_url>
<api_key>YOUR_SPLUNK_HEC_TOKEN</api_key>   <!-- 填 Wazuh_Token -->
```
- `YOUR_SPLUNK_INTERNAL_IP` = Splunk VM 的 **VPC 内网 IP**(`04` 查过,同 VPC,**不要**填公网 IP)。
- ⚠️ **不要**改成 `host.docker.internal` 或 IAP——GCP 版是内网直连。

## 10.2a 补 Splunk HEC 集成脚本(必做,`docker-compose.yml` 里默认没有)

> ⚠️ Wazuh **没有内置的 Splunk 集成**——`<name>` 只要是以 `custom-` 开头(这里是 `custom-splunk-hec`),Wazuh 就只会去容器里的
> `/var/ossec/integrations/custom-splunk-hec` 找一个你自己提供的可执行脚本,把 `hook_url`/`api_key`/告警文件路径当参数传给它,
> 由脚本自己去 POST。光填 10.2 的两个占位符,没有这个脚本,Wazuh 侧什么都不会往 Splunk 发。

1. 新建 `infrastructure/configs/wazuh/custom-splunk-hec`:
```python
#!/usr/bin/env python3
import sys, json, requests

alert_file, api_key, hook_url = sys.argv[1], sys.argv[2], sys.argv[3]

with open(alert_file) as f:
    alert = json.load(f)

requests.post(
    hook_url,
    headers={"Authorization": f"Splunk {api_key}"},
    json={"event": alert, "sourcetype": "_json"},
    verify=False,   # Splunk HEC 默认自签名证书,内网 lab 场景可以忽略校验
    timeout=10,
)
```

2. `docker-compose.yml` 的 `wazuh-manager` 服务 `volumes:` 里加一行,把脚本挂进容器:
```yaml
- ../infrastructure/configs/wazuh/custom-splunk-hec:/var/ossec/integrations/custom-splunk-hec
```

> ⚠️ 脚本权限(`chown root:wazuh` + `chmod 750`)必须在 **lab VM** 上、紧挨着点火前设置,挪到了 [`11 — Igniting the Lab`](<11 — Igniting the Lab.md>) §11.3a,跟其它点火前收尾步骤放一起。

## 10.3 防火墙(已在 `02` 放行)

`02` 的 `allow-internal` 已放行子网内 8088,**无需额外操作**。如当时拆成单端口规则,确认 8088 在内。

## 10.4 自定义检测规则(已随 compose 挂载)
`detection-rules/wazuh/custom_ai_rules.xml` 被挂进 Wazuh:
- Rule 100001 (L3) AI `/api/` 访问基线
- Rule 100002 (L8) 提示注入关键词
- Rule 100003 (L10) Agent 危险命令

➡️ 下一步:**[`11 — Igniting the Lab`](<11 — Igniting the Lab.md>)**
