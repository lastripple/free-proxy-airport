#!/usr/bin/env python3
"""Publish output/clash.yaml to a dedicated GitHub Gist (box copy).

Reads GIST_TOKEN from /workspace/sub-sync/.env (shared with sub-sync).
Stores its own Gist ID in /workspace/free-proxy-airport/.env as FREE_PROXY_GIST_ID;
creates the Gist on first run when the ID is missing.
Never prints the token.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

BASE = Path("/workspace/free-proxy-airport")
OUT = BASE / "output" / "clash.yaml"
LOCAL_ENV = BASE / ".env"
SUBSYNC_ENV = Path("/workspace/sub-sync/.env")
API = "https://api.github.com"


def read_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
    return env


def main() -> int:
    if not OUT.exists():
        print("[publish] output/clash.yaml not found, run generator first")
        return 1
    token = read_env(SUBSYNC_ENV).get("GIST_TOKEN", "")
    if not token:
        print("[publish] GIST_TOKEN missing in sub-sync/.env")
        return 1
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    content = OUT.read_text(encoding="utf-8")
    payload = {
        "description": "free-proxy-airport subscription (generated on Simular box)",
        "files": {"clash.yaml": {"content": content}},
    }
    local = read_env(LOCAL_ENV)
    gist_id = local.get("FREE_PROXY_GIST_ID", "")
    if gist_id:
        resp = requests.patch(f"{API}/gists/{gist_id}", headers=headers, json=payload, timeout=60)
        action = "updated"
    else:
        payload["public"] = False
        resp = requests.post(f"{API}/gists", headers=headers, json=payload, timeout=60)
        action = "created"
    if resp.status_code not in (200, 201):
        print(f"[publish] gist {action} failed: HTTP {resp.status_code} {resp.text[:200]}")
        return 1
    data = resp.json()
    gist_id = data["id"]
    if local.get("FREE_PROXY_GIST_ID") != gist_id:
        lines = [f"{k}={v}" for k, v in local.items() if k != "FREE_PROXY_GIST_ID"]
        lines.append(f"FREE_PROXY_GIST_ID={gist_id}")
        LOCAL_ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")
        LOCAL_ENV.chmod(0o600)
    raw_url = f"https://gist.githubusercontent.com/lastripple/{gist_id}/raw/clash.yaml"
    print(f"[publish] gist {action}: id={gist_id}")
    print(f"[publish] subscription: {raw_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
