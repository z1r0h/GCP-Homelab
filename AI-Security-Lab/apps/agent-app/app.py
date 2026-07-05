from flask import Flask, request, jsonify
import os, requests, json, sys, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone

app = Flask(__name__)
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

# --- Structured JSON Logger ---
logger = logging.getLogger("agent-app")
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(stdout_handler)

os.makedirs("/var/log/ai-lab", exist_ok=True)
file_handler = RotatingFileHandler("/var/log/ai-lab/agent-app.json", maxBytes=10 * 1024 * 1024, backupCount=3)
file_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/agent', methods=['POST'])
def agent():
    user_input = request.json.get('input', '')
    src_ip = request.remote_addr

    # VULNERABILITY: Excessive Agency. The LLM decides what to run on the OS without human approval.
    # In a real app, this is done via LangChain Tools. We simulate it here.
    if "run this command:" in user_input.lower():
        cmd = user_input.split("run this command:")[1].strip()
        result = os.popen(cmd).read()

        # Emit structured log — this is what detection rules key on
        logger.info(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "app": "agent-app",
            "endpoint": "/api/agent",
            "src_ip": src_ip,
            "tool_invoked": "SystemShell",
            "command": cmd,
            "response": result[:500],
            "event_type": "agent_tool_use"
        }))

        return jsonify({"tool_invoked": "SystemShell", "command": cmd, "response": result})

    # Normal interaction (no tool called)
    logger.info(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": "agent-app",
        "endpoint": "/api/agent",
        "src_ip": src_ip,
        "tool_invoked": "None",
        "input": user_input,
        "event_type": "agent_query"
    }))

    return jsonify({"response": "I am an agent. Tell me to 'run this command: [cmd]' to manage the server."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
