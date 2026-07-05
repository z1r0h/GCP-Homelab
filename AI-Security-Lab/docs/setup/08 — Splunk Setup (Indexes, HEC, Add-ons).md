# 08 — Splunk Setup (Indexes, HEC, Add-ons)

> Splunk Enterprise 已在 `04` 装好。本页:建 7 个规范索引 → 建 HEC Token → 装 Add-on → 开 UF 接收口。
> lab VM 与 Splunk **同 VPC**,日志走内网直连。

---

## 8.1 License 省量(10GB/天)
- Sysmon 用 [olafhartong/sysmon-modular](https://github.com/olafhartong/sysmon-modular) 的 **balanced 配置**(装法见 `09` §9.3)——比手写精简版详细得多(数百条规则,按 MITRE ATT&CK 技术打标签),**必须**配合下面 8.1a 的 ingest-time 过滤,否则很容易打爆配额。
- Wazuh 只转发 **Level 5+** 告警(与 `ossec.conf` 的 `<level>5</level>` 一致)。

## 8.1a Sysmon-Modular 省量过滤(强烈建议,`09` 装完 UF 后立刻做)

> sysmon-modular 官方文档自己标注 balanced 配置是"medium verbosity"。其中 **EventID 7(ImageLoad,DLL 加载)**
> 通常占 Sysmon 总日志量的 **60-80%**,而且很少直接用来做检测——业界最常见的省量做法就是在 Splunk **索引前**
> (index-time)直接丢弃它,不写入任何索引、不占用 License 配额。

在 Splunk VM 上(经 IAP SSH,`06`):
```bash
sudo tee -a /opt/splunk/etc/system/local/props.conf <<'EOF'

[source::XmlWinEventLog:Microsoft-Windows-Sysmon/Operational]
TRANSFORMS-drop_imageload = drop_sysmon_imageload
EOF

sudo tee -a /opt/splunk/etc/system/local/transforms.conf <<'EOF'

[drop_sysmon_imageload]
REGEX = <EventID[^>]*>7</EventID>
DEST_KEY = queue
FORMAT = nullQueue
EOF

sudo /opt/splunk/bin/splunk restart
```
> `[source::...]` 匹配的是 `09` 里 inputs.conf 显式写的 `source` 值,不依赖 Splunk 默认怎么分配 sourcetype,更精确。

跑几小时后,用这条 SPL 看剩下的 Sysmon 事件里哪些 EventID 还占大头,超配额就照着这个模式追加规则(常见候选:EventID 10 = 进程访问、EventID 3 = 网络连接可以只保留非本地 IP):
```spl
index=sysmon | stats count by EventID | sort - count
```

## 8.2 安装 Add-ons(Apps → Find More Apps)
1. **Splunk Add-on for Microsoft Windows** — 解析 AD/Client 的 WinEventLog
2. **Splunk Add-on for Sysmon**(App 5709,官方现行版;取代旧版社区版 `TA-microsoft-sysmon`/App 1914)— 解析 Sysmon,CIM 字段映射
3. **Splunk_SA_Scientific_Python_linux_x86_64 + Splunk AI Toolkit** 

## 8.3 创建 7 个规范索引(Settings → Indexes → New Index)

### 为什么是这 7 个,不是「main」一个,也不是 23 个场景各一个?

Splunk 官方对"什么时候该新建一个索引"给的标准就 3 条,缺一条都不该拆:
1. **这份数据需要独立的保留策略**(retention)——比如这份要留 90 天,那份只要 7 天。
2. **这份数据需要独立的访问控制**(access control)——索引是 Splunk 里唯一能按角色/用户精确限制"谁能搜到这份数据"的粒度。
3. **有人会想单独搜这份数据,或者搜别的东西时想把它排除掉**。

官方同时警告:**索引建太多,管理开销会远超你从"隔离/性能"上得到的好处**。所以本 lab 不是每个场景建一个索引(23 个场景就要 20+ 个,谁都记不住也管不过来),而是**按"数据从哪条通道进来 + 谁会想单独搜它"分组**,组内差异交给 `sourcetype` 字段区分:

| Index | 为什么单独拆出来(对应上面 3 条标准) |
|-------|-----------------------------|
| `ai_logs` | 唯一走 **Wazuh_Token** 这条 HEC 通道的数据;4 个 AI 靶机 + SOC triage + SOAR 结论共享同一份访问权限/保留策略,分析师做红蓝对抗场景时只想搜这个、不想被端点噪音干扰。用 `sourcetype`(llm_app/rag_app/agent_app/ml_api/ai_soc_triage/ai_soar/fact_checker)区分子类,没必要每个 app 建一个索引。 |
| `sysmon` | 端点**行为遥测**(进程/网络/文件),量大、噪音多——Splunk 官方给的经典案例就是"敏感的 Windows 安全日志应该和不敏感的日志分开放",这里对应的就是量级/敏感度都跟 `wineventlog` 不一样。 |
| `wineventlog` | Windows **安全审计日志**(登录失败、账户变更),真实环境里往往有更严格的合规保留要求、权限也该比行为遥测收紧——所以跟 `sysmon` 分开,对应"独立访问控制"那条。 |
| `ml_alerts` | 走**另一个 Token(ML_Token)**——不同 Token 本身就是 HEC 层面天然的访问边界;做 ML 场景(11/15/23)时只关心这个,不想搜到安全告警噪音。 |
| `web_logs` | DVWA/Juice Shop 的 Web 访问日志,格式(URI/状态码/UA)和分析方式跟安全事件完全不同,场景 21/23 要单独搜流量模式。 |
| `dns_logs` | DNS 遥测真实环境里量极大、格式独立,场景 15(DNS 隧道)要单独搜。 |
| `email_gateway` | 邮件/钓鱼数据真实组织里通常涉及 PII,合规敏感度更高,理应单独存放,场景 02 单独搜。 |

> 一句话:**分组标准不是"哪个场景",而是"从哪条通道进来 + 谁会想单独搜它/排除它"**——这也是本 lab 早期从 14 个零散 index 收敛成这 7 个规范索引的原因。

| Index | 用途 | 典型 sourcetype |
|-------|------|-----------------|
| `ai_logs` | AI 应用安全事件 + SOC triage + SOAR | llm_app, rag_app, agent_app, ml_api, ai_soc_triage, ai_soar, fact_checker |
| `sysmon` | 端点遥测 | sysmon |
| `wineventlog` | Windows 安全日志 | wineventlog |
| `ml_alerts` | ML 检测输出 | isolation_forest, data_drift, deepfake, model_metrics |
| `web_logs` | Web 靶机访问 | juice_shop, dvwa |
| `dns_logs` | DNS 遥测 | dns |
| `email_gateway` | 邮件/钓鱼 | smtp |

## 8.4 创建 HEC Tokens(Settings → Data Inputs → HTTP Event Collector)

> Splunk 10.x 的 New Token 是个 3 步向导,**Index 字段在第 2 步,不在第 1 步**——按下面的步骤走,别在第 1 页找 Index。

1. 先点右上角 **Global Settings** → 勾 **All Tokens: Enable**(端口默认 8088,不用改)→ Save。
2. 点 **New Token**,对下面两个 Token 各走一遍向导:
   - **Step 1(Select Source)**:填 `Name`(`Wazuh_Token` 或 `ML_Token`),`Source name override`/`Description` 留空,不勾 `Enable indexer acknowledgment` → Next。
   - **Step 2(Input Settings)**:`Source type` 选 `_json`;`Index` 勾选对应的 Default Index(两个索引已在 8.3 建好,**这一步选不了新建索引**)→ Review。
   - **Step 3(Review)**:核对无误 → Submit,记下弹出的 Token 值(只显示这一次)。

| Token | Default Index | 用途 |
|-------|---------------|------|
| `Wazuh_Token` | `ai_logs` | Wazuh 转发 AI 告警(填进 `ossec.conf` 的 `<api_key>`,见 `10`)。实际 Token 值记在本地 `credentials.md`(不上传) |
| `ML_Token` | `ml_alerts` | 本地脚本/notebook 转发 ML 结果(设为环境变量 `SPLUNK_TOKEN`)。实际 Token 值记在本地 `credentials.md`(不上传) |

> 防火墙:`02` 的 `allow-internal` 已放行子网内 8088,Wazuh 从 lab VM 直接发到 Splunk 内网 IP 即可。

## 8.5 开启 Universal Forwarder 接收口(给 Windows 用)

Splunk Web → **Settings → Forwarding and receiving → Configure receiving → New Receiving Port → `9997`**。
> Windows 的 Sysmon/WinEventLog 由各机的 UF 推到 Splunk VM 内网 IP:9997(`02` 的 `allow-internal` 已放行)。装 UF 见 `09`。

## 8.6 验证

Splunk Web 跑:
```spl
| eventcount summarize=false index=ai_logs index=sysmon index=wineventlog index=ml_alerts index=web_logs index=dns_logs index=email_gateway
```
7 个索引都应列出(此刻 count 可能为 0,正常)。

➡️ 下一步:有 Windows VM 就去 [`09 — Windows Config`](<09 — Windows Config (AD, Sysmon, UF).md>);否则直接 [`10 — Wazuh & Log Pipeline`](<10 — Wazuh & Log Pipeline.md>)。
