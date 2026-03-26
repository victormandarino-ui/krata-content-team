#!/usr/bin/env python3
"""
Faz upload de uma pasta de slides PNG para o Google Drive.
Cria subpasta com nome "YYYY-MM-DD — Título" dentro da pasta raiz do conteúdo.

Input (stdin JSON):
{
  "titulo": "R$ 25 mil economizados. Nenhuma linha de código.",
  "data": "2026-03-25",
  "pasta_local": "/Users/victormandarino/projetos/krata/content-team/output/2026-03-25/slug/"
}

Output (stdout JSON):
{
  "success": true,
  "folder_id": "...",
  "folder_url": "https://drive.google.com/drive/folders/...",
  "arquivos_enviados": 6
}
"""

import sys
import json
import os
import urllib.request
import urllib.parse
import mimetypes
from pathlib import Path

# Configurações
TOKEN_PATH = Path.home() / ".config/google-docs-mcp/token.json"
DRIVE_PARENT_FOLDER_ID = "1CNFttpb_hri-iXBSqJQu37XKilLouhfl"
DRIVE_API = "https://www.googleapis.com/drive/v3"
DRIVE_UPLOAD_API = "https://www.googleapis.com/upload/drive/v3"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"


def get_access_token():
    creds = json.loads(TOKEN_PATH.read_text())
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request(OAUTH_TOKEN_URL, data=data,
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]


def drive_request(method, path, token, body=None, params=None):
    url = DRIVE_API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def create_folder(name, parent_id, token):
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]}
    res = drive_request("POST", "/files", token, body=meta,
                         params={"fields": "id,webViewLink"})
    return res["id"], res["webViewLink"]


def upload_file(filepath, folder_id, token):
    filepath = Path(filepath)
    mime = mimetypes.guess_type(filepath.name)[0] or "application/octet-stream"

    # Upload multipart
    meta = json.dumps({"name": filepath.name, "parents": [folder_id]}).encode()
    content = filepath.read_bytes()

    boundary = "krata_boundary_12345"
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
    ).encode() + meta + (
        f"\r\n--{boundary}\r\n"
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--".encode()

    url = f"{DRIVE_UPLOAD_API}/files?uploadType=multipart&fields=id,name"
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/related; boundary={boundary}",
        "Content-Length": str(len(body))
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    payload = json.loads(sys.stdin.read())
    titulo = payload["titulo"]
    data = payload["data"]
    pasta_local = Path(payload["pasta_local"])

    # Nome da pasta no Drive: "YYYY-MM-DD — Título" (truncado em 100 chars)
    folder_name = f"{data} — {titulo}"[:100]

    token = get_access_token()

    # Cria subpasta no Drive
    folder_id, folder_url = create_folder(folder_name, DRIVE_PARENT_FOLDER_ID, token)

    # Faz upload dos PNGs em ordem
    pngs = sorted(pasta_local.glob("*.png"))
    uploaded = 0
    for png in pngs:
        upload_file(png, folder_id, token)
        uploaded += 1

    result = {
        "success": True,
        "folder_id": folder_id,
        "folder_url": folder_url,
        "folder_name": folder_name,
        "arquivos_enviados": uploaded
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
