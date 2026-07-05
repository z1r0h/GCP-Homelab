#!/usr/bin/env python3
"""
nl_to_spl.py — Natural-Language-to-SPL middleware (Scenario 12: AI Threat Hunting).

A tiny Flask service that turns plain-English hunting questions into Splunk SPL using
the local Ollama LLM. Point your browser/curl at it, type a question, get SPL back.

  POST /translate  {"query": "show powershell spawning from temp dirs in last 24h"}
       -> {"spl": "index=sysmon EventCode=1 ParentImage=... | ..."}
  GET  /health

Env vars: OLLAMA_URL, OLLAMA_MODEL

Usage:
  python3 nl_to_spl.py                      # serve on :5010
  python3 nl_to_spl.py --once "find C2 beacons"   # one-shot, prints SPL, no server
"""
import argparse
import os
import sys

import requests
from flask import Flask, jsonify, request

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

SPL_PROMPT = (
    "You are a Splunk SPL expert. Translate the user's request into a single valid SPL "
    "query. Output ONLY the SPL, no explanation, no markdown fences.\n\nRequest: {q}"
)

app = Flask(__name__)


def translate(nl_query: str) -> str:
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": SPL_PROMPT.format(q=nl_query),
                  "stream": False},
            timeout=60,
        )
        return resp.json().get("response", "").strip()
    except (requests.RequestException, ValueError) as e:
        return f"# translation error: {e}"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": OLLAMA_MODEL})


@app.route("/translate", methods=["POST"])
def translate_endpoint():
    nl = (request.get_json(silent=True) or {}).get("query", "")
    if not nl:
        return jsonify({"error": "missing 'query'"}), 400
    return jsonify({"query": nl, "spl": translate(nl)})


def main():
    ap = argparse.ArgumentParser(description="NL -> SPL middleware")
    ap.add_argument("--once", metavar="QUERY", help="translate one query and exit")
    ap.add_argument("--port", type=int, default=5010)
    args = ap.parse_args()

    if args.once:
        print(translate(args.once))
        sys.exit(0)
    app.run(host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
