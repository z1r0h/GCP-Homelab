#!/usr/bin/env python3
"""
soar_playbook.py — AI-driven SOAR response (Scenario 14, also used by Scenario 20).

Flow:  Splunk notable alert  ->  AI verdict (Ollama)  ->  if high-confidence Critical,
        call the EDR isolate API and write an audit event back to Splunk HEC.

Fails safe: the EDR isolate call is a DRY-RUN by default (--execute to arm it), so you
can rehearse the playbook without actually quarantining anything.

Env vars (all optional):
  OLLAMA_URL / OLLAMA_MODEL   local LLM
  SPLUNK_HEC / SPLUNK_TOKEN   audit-event forwarding
  EDR_API                     default http://localhost:9000  (stub isolate endpoint)

Usage:
  python3 soar_playbook.py --demo            # one synthetic Critical alert (dry-run)
  python3 soar_playbook.py --demo --execute  # actually call the EDR isolate API
"""
import argparse
import json
import os

import requests
import urllib3

urllib3.disable_warnings()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
SPLUNK_HEC = os.getenv("SPLUNK_HEC", "https://localhost:8088/services/collector")
SPLUNK_TOKEN = os.getenv("SPLUNK_TOKEN", "")
EDR_API = os.getenv("EDR_API", "http://localhost:9000")

VERDICT_PROMPT = (
    "You are an automated incident responder. Given this alert, respond with STRICT JSON "
    '{{"confidence":0.0-1.0,"severity":"Low|Medium|High|Critical","action":"isolate|monitor|ignore"}}.'
    "\n\nAlert: {alert}"
)


def ai_verdict(alert: dict) -> dict:
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": VERDICT_PROMPT.format(alert=json.dumps(alert)),
                  "stream": False, "format": "json"},
            timeout=60,
        )
        return json.loads(resp.json().get("response", "{}"))
    except (requests.RequestException, ValueError) as e:
        return {"confidence": 0.0, "severity": "Unknown", "action": "monitor",
                "error": str(e)}


def isolate_host(agent_id: str, execute: bool) -> str:
    if not execute:
        return f"DRY-RUN: would POST {EDR_API}/isolate (agent_id={agent_id})"
    try:
        requests.post(f"{EDR_API}/isolate", json={"agent_id": agent_id}, timeout=10)
        return f"ISOLATED agent_id={agent_id}"
    except requests.RequestException as e:
        return f"isolate failed: {e}"


def audit(event: dict) -> None:
    if not SPLUNK_TOKEN:
        return
    try:
        requests.post(SPLUNK_HEC, headers={"Authorization": f"Splunk {SPLUNK_TOKEN}"},
                      json={"sourcetype": "ai_soar", "index": "ai_logs", "event": event},
                      verify=False, timeout=10)
    except requests.RequestException:
        pass


def run_playbook(alert: dict, execute: bool) -> dict:
    verdict = ai_verdict(alert)
    confidence = float(verdict.get("confidence", 0) or 0)
    severity = verdict.get("severity", "Unknown")
    print(f"[*] AI verdict: confidence={confidence} severity={severity} "
          f"action={verdict.get('action')}")

    result = "no-action"
    if confidence > 0.9 and severity == "Critical":
        result = isolate_host(alert.get("agent_id", "unknown"), execute)
        audit({"event": "Host isolation triggered by AI SOAR", "detail": result,
               "confidence": confidence})
    print(f"[*] Result: {result}")
    return {"verdict": verdict, "result": result}


def main():
    ap = argparse.ArgumentParser(description="AI SOAR response playbook")
    ap.add_argument("--demo", action="store_true", help="run one synthetic Critical alert")
    ap.add_argument("--execute", action="store_true", help="actually call the EDR isolate API")
    args = ap.parse_args()

    if args.demo:
        sample = {"agent_id": "agent-007", "rule": {"id": "100003", "level": 10,
                  "description": "CRITICAL: AI Agent executed a dangerous system command"},
                  "command": "cat /etc/passwd"}
        run_playbook(sample, args.execute)
    else:
        print("[!] No alert source wired in non-demo mode. Use --demo to smoke-test, "
              "or feed Splunk notable events into run_playbook().")


if __name__ == "__main__":
    main()
