#!/usr/bin/env python3
"""
Notifica o QG da KRATA sobre mudanças de estado dos agentes.
Uso: python3 notify_qg.py <agent> <status> [message]

Agents:  victor, yago, kaua, joyce, ana, davi, lara, pedro, rafa
Status:  working, done, error, progress, meeting, idle
"""

import json
import sys
import urllib.request
import urllib.error

QG_URL = "http://localhost:3737/api/agent"


def notify(agent: str, status: str, message: str = None) -> bool:
    """Notifica o QG sobre mudança de estado de um agente.
    Retorna True se enviou, False se QG offline (silencioso)."""
    payload = {"agent": agent, "status": status}
    if message:
        payload["message"] = message[:200]  # limite do servidor
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            QG_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=2)
        return True
    except Exception:
        return False  # QG offline não deve quebrar o pipeline


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Uso: python3 notify_qg.py <agent> <status> [message]")
        sys.exit(1)
    agent_id = args[0]
    status_val = args[1]
    msg = args[2] if len(args) > 2 else None
    ok = notify(agent_id, status_val, msg)
    if ok:
        print(f"✅ QG notificado: {agent_id} → {status_val}")
    else:
        print(f"⚠️  QG offline (ignorado): {agent_id} → {status_val}")
