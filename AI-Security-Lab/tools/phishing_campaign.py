#!/usr/bin/env python3
"""
phishing_campaign.py — AI-generated phishing campaign via GoPhish (Scenario 02).

Two-phase, matching how a real phishing test works — a human plays the victim
rather than the script faking a click:
  --launch          Ollama writes the email; creates/reuses GoPhish resources
                     (sending profile -> Mailpit, template, landing page, group)
                     and launches the campaign. Then YOU open Mailpit, read the
                     email, and click the link inside it yourself.
  --report ID       After you've opened/clicked in Mailpit, pulls the real
                     GoPhish campaign stats (opened/clicked) plus the actual
                     sent content, and forwards both to Splunk HEC.

One-time manual setup: log into GoPhish (https://localhost:3333), go to Settings,
generate an API key, then `export GOPHISH_API_KEY=...` (or store it in this
repo's docs/setup/credentials.md per the existing convention).

Env vars:
  OLLAMA_URL, OLLAMA_MODEL
  GOPHISH_URL      default https://localhost:3333
  GOPHISH_API_KEY  required
  SPLUNK_HEC, SPLUNK_TOKEN   (only needed for --report; skips forwarding if empty)

Usage:
  python3 phishing_campaign.py --launch
  # ... open http://localhost:8025 (Mailpit), read + click the email yourself ...
  python3 phishing_campaign.py --report 3
"""
import argparse
import json
import os
import sys
import time

import requests
import urllib3

urllib3.disable_warnings()  # GoPhish uses a self-signed cert by default

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
GOPHISH_URL = os.getenv("GOPHISH_URL", "https://localhost:3333")
GOPHISH_API_KEY = os.getenv("GOPHISH_API_KEY", "")
SPLUNK_HEC = os.getenv("SPLUNK_HEC", "https://localhost:8088/services/collector")
SPLUNK_TOKEN = os.getenv("SPLUNK_TOKEN", "")

# Fixed, reusable resource names. get_or_create() below reuses them across runs
# instead of erroring on "name already in use".
PROFILE_NAME = "ai-lab-mailpit"
TEMPLATE_NAME = "ai-lab-phishing-template"
PAGE_NAME = "ai-lab-landing-page"
GROUP_NAME = "ai-lab-test-group"
SUBJECT = "URGENT: Your VPN Access Will Be Deactivated"

EMAIL_PROMPT = (
    "Write a short, highly urgent phishing email from 'IT Support' warning the "
    "recipient their VPN access will be deactivated unless they act immediately. "
    "Output ONLY the email body text, no subject line, no markdown."
)


def gophish_headers():
    return {"Authorization": GOPHISH_API_KEY, "Content-Type": "application/json"}


def gophish_get(path):
    resp = requests.get(f"{GOPHISH_URL}{path}", headers=gophish_headers(), verify=False, timeout=15)
    resp.raise_for_status()
    return resp.json()


def gophish_post(path, body):
    resp = requests.post(f"{GOPHISH_URL}{path}", headers=gophish_headers(), json=body, verify=False, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_or_create(path, name, payload):
    """GoPhish errors on duplicate names, so reuse an existing resource by name
    instead of creating a new one every run."""
    for item in gophish_get(path):
        if item.get("name") == name:
            return item
    return gophish_post(path, payload)


def ask_llm(prompt: str) -> str:
    resp = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=90)
    return resp.json().get("response", "").strip()


def require_api_key():
    if not GOPHISH_API_KEY:
        print("[!] GOPHISH_API_KEY not set. Log into https://localhost:3333, "
              "Settings -> generate an API key, then: export GOPHISH_API_KEY=...")
        sys.exit(1)


def launch():
    require_api_key()
    print("[*] Asking Ollama to write the phishing email...")
    try:
        body_text = ask_llm(EMAIL_PROMPT)
    except (requests.RequestException, ValueError) as e:
        print(f"[!] Ollama unavailable, cannot generate email: {e}")
        sys.exit(1)
    html = (f"<html><body><p>{body_text}</p>"
            f'<p><a href="{{{{.URL}}}}">Click here to keep your access</a></p>'
            f"{{{{.Tracker}}}}</body></html>")

    print("[*] Ensuring GoPhish resources exist (sending profile, template, page, group)...")
    get_or_create("/api/smtp/", PROFILE_NAME, {
        "name": PROFILE_NAME, "from_address": "it-support@lab.local",
        "host": "mailpit:1025", "ignore_cert_errors": True,
    })
    get_or_create("/api/templates/", TEMPLATE_NAME, {
        "name": TEMPLATE_NAME, "subject": SUBJECT, "html": html,
    })
    get_or_create("/api/pages/", PAGE_NAME, {
        "name": PAGE_NAME,
        "html": "<html><body><h1>Access Restored</h1><p>Your VPN session has been renewed.</p></body></html>",
    })
    get_or_create("/api/groups/", GROUP_NAME, {
        "name": GROUP_NAME,
        "targets": [{"email": "victim@lab.local", "first_name": "Lab", "last_name": "User", "position": ""}],
    })

    campaign = gophish_post("/api/campaigns/", {
        "name": f"ai-lab-phishing-{int(time.time())}",
        "template": {"name": TEMPLATE_NAME},
        "url": "http://localhost:8080",
        "page": {"name": PAGE_NAME},
        "smtp": {"name": PROFILE_NAME},
        "groups": [{"name": GROUP_NAME}],
    })
    print(f"\n[+] Campaign launched: id={campaign['id']} name={campaign['name']}")
    print(f"\nSubject: {SUBJECT}\nBody:\n{body_text}\n")
    print("[*] Now go be the victim: open http://localhost:8025 (Mailpit), read the "
          "email, and click the link inside it - same as a real target would.")
    print(f"[*] Once you've clicked it, run:\n    python3 tools/phishing_campaign.py --report {campaign['id']}")


def report(campaign_id: str):
    require_api_key()
    summary = gophish_get(f"/api/campaigns/{campaign_id}/summary")
    stats = summary.get("stats", {})
    print(f"[*] Campaign {campaign_id} stats: {stats}")

    template = next((t for t in gophish_get("/api/templates/") if t.get("name") == TEMPLATE_NAME), {})
    # The stored template still has the raw {{.URL}}/{{.Tracker}} placeholders GoPhish
    # only substitutes per-recipient at send time - swap in the real phishing host so
    # the forwarded body reads like what was actually delivered (and so SPL regexes
    # looking for a literal http(s):// link actually have one to match).
    rendered_body = (template.get("html", "")
                      .replace("{{.URL}}", "http://localhost:8080/")
                      .replace("{{.Tracker}}", ""))
    event = {
        "sender": "it-support@lab.local",
        "subject": template.get("subject", SUBJECT),
        "body": rendered_body,
        "sent": stats.get("sent", 0),
        "opened": stats.get("opened", 0),
        "clicked": stats.get("clicked", 0),
    }
    if not SPLUNK_TOKEN:
        print(f"  [skip] SPLUNK_TOKEN not set - would forward:\n{json.dumps(event, indent=2)}")
        return
    try:
        requests.post(SPLUNK_HEC, headers={"Authorization": f"Splunk {SPLUNK_TOKEN}"},
                      json={"index": "email_gateway", "sourcetype": "smtp", "event": event},
                      verify=False, timeout=10)
        print("  [ok] forwarded to Splunk HEC")
    except requests.RequestException as e:
        print(f"  [warn] Splunk forward failed: {e}")


def main():
    ap = argparse.ArgumentParser(description="AI-generated phishing campaign via GoPhish")
    ap.add_argument("--launch", action="store_true", help="generate email + launch a GoPhish campaign")
    ap.add_argument("--report", metavar="CAMPAIGN_ID",
                     help="pull real stats for a launched campaign and forward to Splunk")
    args = ap.parse_args()

    if args.launch:
        launch()
    elif args.report:
        report(args.report)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
