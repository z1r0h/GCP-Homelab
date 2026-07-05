# 📚 Vulnerable RAG App
**Vulnerability**: RAG Data Poisoning (OWASP LLM04)
**Operation**: Runs on port 5001. It reads all `.txt` files in the `knowledge_base` folder to answer questions. As an attacker, write a malicious text file to that directory containing a phishing URL, then query the API to see the LLM recommend the phishing link.
