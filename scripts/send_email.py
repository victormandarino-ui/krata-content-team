#!/usr/bin/env python3
"""Envia email via Gmail SMTP. Chamado pelo n8n webhook."""

import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Credenciais — lidas do .env na mesma pasta
env_path = Path(__file__).parent.parent / ".env"
creds = {}
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip()

GMAIL_USER = creds.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = creds.get("GMAIL_APP_PASSWORD", "")

def send(to: str, subject: str, html: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to, msg.as_string())

    return {"success": True, "to": to, "subject": subject}

if __name__ == "__main__":
    # Lê JSON do stdin (enviado pelo n8n Execute Command via pipe)
    payload = json.loads(sys.stdin.read())
    result = send(payload["to"], payload["subject"], payload["html"])
    print(json.dumps(result))
