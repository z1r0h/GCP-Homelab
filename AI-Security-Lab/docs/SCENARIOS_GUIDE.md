# 🎯 Cyber AI Lab - 23 场景超详细操作指南

> 本指南包含 **建议执行顺序**、**标准作业程序 (SOP)** 以及 **全部 23 个场景的索引**。
> 每个场景的**超详细操作步骤**收录在 `docs/scenarios/` 下的独立指南文件中（单一信息源，避免重复）。
> 仓库已自带每个场景文件夹（如 `scenarios/01-ai-autonomous-pentest/`）的 `README.md` 报告模板。完成场景后，请直接填写那个 `README.md`！

---

## 📅 1. 建议执行顺序与快速跳转 (Quick Links)

不要试图一口气做完 23 个场景！建议按照“从易到难、从单点到综合”的顺序，每周完成 2-3 个场景。点击链接可直接跳转到指定场景的详细指南。

### 第一阶段：AI 脆弱性与红队基础 (Week 1)
*目标：熟悉本地大模型交互，了解 LLM 自身漏洞。无需复杂的网络配置。*
- [🔗 场景 03: LLM 提示注入与越狱](<scenarios/03-LLM-Prompt-Injection-&-Jailbreak.md>)
- [🔗 场景 04: RAG 投毒攻击](<scenarios/04-RAG-Poisoning-Attack.md>)
- [🔗 场景 02: AI 钓鱼与社工攻击](<scenarios/02-AI-Powered-Phishing-&-Social-Engineering.md>)
- [🔗 场景 19: LLM 幻觉与虚假信息防御](<scenarios/19-LLM-Misinformation-&-Hallucination-Defense.md>)

### 第二阶段：AI 辅助攻防与自动化 (Week 2-3)
*目标：开始使用 Splunk HEC 和 Wazuh，打通日志管道。*
- [🔗 场景 09: AI 生成恶意代码分析](<scenarios/09-AI-Generated-Malware-Analysis.md>)
- [🔗 场景 07: Agentic AI 劫持](<scenarios/07-Agentic-AI-Hijacking-(Excessive-Agency).md>)
- [🔗 场景 10: AI SOC 分析师](<scenarios/10-AI-SOC-Analyst-(Alert-Triage).md>)
- [🔗 场景 12: AI 威胁猎捕](<scenarios/12-AI-Threat-Hunting-via-NL-Queries.md>)
- [🔗 场景 15: DNS 隧道 + AI 检测](<scenarios/15-DNS-Tunneling-+-AI-Detection.md>)

### 第三阶段：机器学习安全 (Week 4-5)
*目标：进入 Jupyter Lab，处理数据科学和对抗性机器学习。*
- [🔗 场景 08: 模型提取与成员推理攻击](<scenarios/08-Model-Extraction-&-Membership-Inference.md>)
- [🔗 场景 06: AI 供应链攻击](<scenarios/06-AI-Supply-Chain-Attack-(Malicious-Pickle).md>)
- [🔗 场景 05: 对抗性 ML - 模型逃逸](<scenarios/05-Adversarial-ML-Evasion-(ZOO-Attack).md>)
- [🔗 场景 11: AI 行为异常检测](<scenarios/11-AI-Anomaly-Detection-(Isolation-Forest).md>)
- [🔗 场景 13: Deepfake 检测与防御](<scenarios/13-Deepfake-Detection-&-Defense.md>)
- [🔗 场景 16: 数据投毒攻防](<scenarios/16-Data-Poisoning-Defense.md>)

### 第四阶段：紫队综合与云端联动 (Week 6)
*目标：结合 GCP 真实环境，进行复杂的攻击链模拟。*
- [🔗 场景 17: Purple Team AD 攻防](<scenarios/17-Purple-Team-AD-Attack-+-AI-Detection.md>)
- [🔗 场景 18: MFA 绕过与凭证攻击](<scenarios/18-MFA-Bypass-&-Credential-Attacks-+-AI.md>)
- [🔗 场景 14: AI 自动化事件响应](<scenarios/14-AI-Powered-Automated-SOAR.md>)
- [🔗 场景 01: AI 自主渗透测试代理](<scenarios/01-AI-Autonomous-Pentesting-Agent.md>)
- [🔗 场景 20: AI vs AI 综合对抗演练 (Final Boss)](<scenarios/20-AI-vs-AI-Comprehensive-Exercise-(Final-Boss).md>)

### 第五阶段：扩展演练 — 传统靶机 + 自主对抗 (Week 7+)
*目标：引入经典 Web 靶机 (DVWA/Juice Shop) 与 CALDERA，给 AI 攻防提供真实攻击面。*
*✅ 这 3 个扩展场景的依赖组件 (Juice Shop / CALDERA / DVWA) 已全部接入 `docker-compose.yml`，点火后即可执行。*
- [🔗 场景 21: AI 驱动 Web 渗透 (Juice Shop)](<scenarios/21-AI-Driven-Web-Pentest-(Juice-Shop).md>)
- [🔗 场景 22: CALDERA 自主红队 vs AI 蓝队](<scenarios/22-CALDERA-Autonomous-Red-vs-AI-Blue.md>)
- [🔗 场景 23: 真实流量训练 AI 异常检测](<scenarios/23-Real-Traffic-Anomaly-Detection-Training.md>)

---

## 📝 2. 标准作业程序 (SOP)

为确保你的 GitHub 仓库看起来专业且活跃，请在**每个场景**中严格执行以下 4 步闭环：

1. **实施攻击与取证 (Red Team)**：在 Kali 容器或本地环境中执行攻击命令。只要拿到 Shell、越狱成功或看到敏感信息，**立即截图**！将截图保存到该场景的 `evidence/` 目录下（例如 `scenarios/03-prompt-injection/evidence/01-attack-success.png`）。
2. **检测与分析 (Blue Team)**：登录 GCP Splunk Web。编写 SPL 查询语句找出攻击记录，**截图**保存到 `evidence/`。复制你的 SPL 代码。
3. **完成报告**：打开该场景文件夹下的 `README.md`，填入本次实验的截图、SPL 代码、MITRE 映射以及 "Lessons Learned"。
4. **提交到 GitHub**：
   ```bash
   # 更新根目录主 README.md 中的状态表为 🟢 COMPLETED
   git add .
   git commit -m "Completed Scenario XX: [Name] with Splunk detection rules"
   git push origin main
   ```

---

## 🔥 3. 全部场景索引 (Full Scenario Index)

> 详细操作步骤（背景理论 / 环境搭建 / 红队 / 蓝队 / 缓解）见每个场景的独立指南文件。
> 按编号排列，便于查阅；推荐学习顺序见上方第 1 节。

| # | 场景 | 类型 | Framework | 详细指南 |
|:---:|------|:---:|------|:---:|
| 01 | AI 自主渗透测试代理 | 🔴 | ATT&CK T1595/T1190, ATLAS AML.T0016 | [↗](<scenarios/01-AI-Autonomous-Pentesting-Agent.md>) |
| 02 | AI 钓鱼与社工攻击 | 🔴 | ATT&CK T1566, ATLAS AML.T0048 | [↗](<scenarios/02-AI-Powered-Phishing-&-Social-Engineering.md>) |
| 03 | LLM 提示注入与越狱 | 🔴 | OWASP LLM01/LLM02/LLM07 | [↗](<scenarios/03-LLM-Prompt-Injection-&-Jailbreak.md>) |
| 04 | RAG 投毒攻击 | 🔴 | OWASP LLM04/LLM08 | [↗](<scenarios/04-RAG-Poisoning-Attack.md>) |
| 05 | 对抗性 ML - 模型逃逸 | 🔴 | ATLAS AML.T0015 | [↗](<scenarios/05-Adversarial-ML-Evasion-(ZOO-Attack).md>) |
| 06 | AI 供应链攻击 (恶意 Pickle) | 🔴 | OWASP LLM03, ATLAS AML.T0010 | [↗](<scenarios/06-AI-Supply-Chain-Attack-(Malicious-Pickle).md>) |
| 07 | Agentic AI 劫持 (越权代理) | 🔴 | OWASP LLM05/LLM06 | [↗](<scenarios/07-Agentic-AI-Hijacking-(Excessive-Agency).md>) |
| 08 | 模型提取与成员推理攻击 | 🔴 | ATLAS AML.T0024/T0025 | [↗](<scenarios/08-Model-Extraction-&-Membership-Inference.md>) |
| 09 | AI 生成恶意代码分析 | 🔴 | ATLAS AML.T0017, ATT&CK T1059 | [↗](<scenarios/09-AI-Generated-Malware-Analysis.md>) |
| 10 | AI SOC 分析师 (告警 Triage) | 🔵 | NIST CSF (DE.AE) | [↗](<scenarios/10-AI-SOC-Analyst-(Alert-Triage).md>) |
| 11 | AI 行为异常检测 (Isolation Forest) | 🔵 | ATT&CK TA0008/TA0010 | [↗](<scenarios/11-AI-Anomaly-Detection-(Isolation-Forest).md>) |
| 12 | AI 威胁猎捕 (自然语言查询) | 🔵 | ATT&CK General | [↗](<scenarios/12-AI-Threat-Hunting-via-NL-Queries.md>) |
| 13 | Deepfake 检测与防御 | 🔵 | ATLAS AML.T0048 | [↗](<scenarios/13-Deepfake-Detection-&-Defense.md>) |
| 14 | AI 自动化事件响应 (SOAR) | 🔵 | NIST CSF (RS.RP/RS.MI) | [↗](<scenarios/14-AI-Powered-Automated-SOAR.md>) |
| 15 | DNS 隧道 + AI 检测 | 🔵 | ATT&CK T1071.004 | [↗](<scenarios/15-DNS-Tunneling-+-AI-Detection.md>) |
| 16 | 数据投毒攻防 | 🟣 | ATLAS AML.T0020, OWASP LLM04 | [↗](<scenarios/16-Data-Poisoning-Defense.md>) |
| 17 | Purple Team AD 攻防 | 🟣 | ATT&CK General (GCP) | [↗](<scenarios/17-Purple-Team-AD-Attack-+-AI-Detection.md>) |
| 18 | MFA 绕过与凭证攻击 | 🟣 | ATT&CK T1556/T1110 | [↗](<scenarios/18-MFA-Bypass-&-Credential-Attacks-+-AI.md>) |
| 19 | LLM 幻觉与虚假信息防御 | 🟣 | OWASP LLM09 | [↗](<scenarios/19-LLM-Misinformation-&-Hallucination-Defense.md>) |
| 20 | AI vs AI 综合对抗演练 (Final Boss) | 🟣 | ALL Frameworks | [↗](<scenarios/20-AI-vs-AI-Comprehensive-Exercise-(Final-Boss).md>) |
| 21 | AI 驱动 Web 渗透 (Juice Shop) | 🔴 | ATT&CK T1595/T1190, ATLAS AML.T0016 | [↗](<scenarios/21-AI-Driven-Web-Pentest-(Juice-Shop).md>) |
| 22 | CALDERA 自主红队 vs AI 蓝队 | 🟣 | ATT&CK (Full Chain) | [↗](<scenarios/22-CALDERA-Autonomous-Red-vs-AI-Blue.md>) |
| 23 | 真实流量训练 AI 异常检测 | 🔵 | ATT&CK TA0008/TA0010, OWASP LLM04 | [↗](<scenarios/23-Real-Traffic-Anomaly-Detection-Training.md>) |

> 类型图例：🔴 红队 (Offense) · 🔵 蓝队 (Defense) · 🟣 紫队 (Both)

---
*END OF GUIDE. Good luck on your path to becoming an AI-Security Specialist!*
