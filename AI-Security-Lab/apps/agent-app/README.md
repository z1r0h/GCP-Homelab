# 🕵️ Vulnerable Agent App
**Vulnerability**: Excessive Agency / Command Injection (OWASP LLM06)
**Operation**: Runs on port 5003. This AI agent has a "SystemShell" tool. It blindly trusts user intent. Instruct it to `run this command: cat /etc/passwd` and it will happily execute the command on the underlying Linux container and return the output.
