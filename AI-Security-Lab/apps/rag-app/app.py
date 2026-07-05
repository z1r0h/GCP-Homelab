from flask import Flask, request, jsonify
import os, requests, json, sys, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone

app = Flask(__name__)
KB_DIR = "knowledge_base"
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

# --- Structured JSON Logger ---
logger = logging.getLogger("rag-app")
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(stdout_handler)

os.makedirs("/var/log/ai-lab", exist_ok=True)
file_handler = RotatingFileHandler("/var/log/ai-lab/rag-app.json", maxBytes=10 * 1024 * 1024, backupCount=3)
file_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)

# Mock RAG retrieval — reads all .txt files in knowledge_base/
def retrieve_docs(query):
    docs = []
    if os.path.exists(KB_DIR):
        for f in os.listdir(KB_DIR):
            fpath = os.path.join(KB_DIR, f)
            if os.path.isfile(fpath):  # Fix #9: skip subdirectories
                try:
                    with open(fpath, 'r', encoding='utf-8') as file:
                        docs.append(file.read())
                except Exception:
                    pass  # Skip unreadable files
    return " ".join(docs)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/reindex', methods=['POST'])
def reindex():
    """Simulates re-indexing the knowledge base (for RAG poisoning demo)."""
    count = len([f for f in os.listdir(KB_DIR) if os.path.isfile(os.path.join(KB_DIR, f))]) if os.path.exists(KB_DIR) else 0
    logger.info(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": "rag-app",
        "endpoint": "/api/reindex",
        "documents_indexed": count,
        "event_type": "rag_reindex"
    }))
    return jsonify({"status": "reindexed", "documents": count})

@app.route('/api/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query', '')
    src_ip = request.remote_addr
    context = retrieve_docs(user_query)

    prompt = f"Use this context to answer: {context}\n\nQuestion: {user_query}"
    response = requests.post(OLLAMA_URL, json={"model": "llama3.1:8b", "prompt": prompt, "stream": False})
    ai_response = response.json().get('response', '')

    # Emit structured log
    log_entry = json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": "rag-app",
        "endpoint": "/api/ask",
        "src_ip": src_ip,
        "query": user_query,
        "context_length": len(context),
        "response": ai_response[:500],
        "event_type": "rag_response"
    })
    logger.info(log_entry)

    return jsonify({"response": ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
