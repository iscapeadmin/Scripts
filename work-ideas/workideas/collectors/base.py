"""Shared HTTP helpers for collectors."""

from __future__ import annotations

import os
import re
import time
from typing import Any

import requests


class CollectorError(RuntimeError):
    pass


def secret(cfg: dict, key_env_field: str, default_env: str) -> str:
    """Read a secret from the env var named in config (never from the file itself)."""
    env_name = cfg.get(key_env_field, default_env)
    value = os.environ.get(env_name, "")
    if not value:
        raise CollectorError(f"Environment variable {env_name} is not set")
    return value


class Http:
    def __init__(self, base_url: str, headers: dict[str, str] | None = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", **(headers or {})})
        self.timeout = timeout

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, json: Any = None, data: Any = None) -> Any:
        return self._request("POST", path, json=json, data=data)

    def _request(self, method: str, path: str, **kw: Any) -> Any:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        for attempt in range(4):
            resp = self.session.request(method, url, timeout=self.timeout, **kw)
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = float(resp.headers.get("Retry-After", 2 ** attempt))
                time.sleep(min(wait, 30))
                continue
            if resp.status_code >= 400:
                raise CollectorError(f"{method} {url} -> {resp.status_code}: {resp.text[:300]}")
            return resp.json() if resp.content else None
        raise CollectorError(f"{method} {url} kept failing after retries")


def unwrap(payload: Any, key: str) -> list[dict]:
    """APIs variously return a bare list or {"key": [...]}."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        val = payload.get(key)
        if isinstance(val, list):
            return val
    return []


def classify_kind(*hints: str) -> str:
    """Guess a device kind from layout names, device types, OS strings etc."""
    text = " ".join(h for h in hints if h).lower()
    rules = [
        ("firewall", r"firewall|fortigate|sonicwall|watchguard|sophos xg|meraki mx|pfsense"),
        ("ups", r"ups|apc smart|eaton"),
        ("printer", r"printer|mfp|copier|laserjet"),
        ("storage", r"nas|synology|qnap|san|storage"),
        ("server", r"server|hyper-v hosts?|esxi|vmware|domain controller"),
        ("network", r"switch(es)?|router|access point|wireless|wifi|network devices?|unifi|ilo|idrac"),
        ("workstation", r"laptops?|desktops?|workstation|computer|windows (10|11)|macos|notebook|pc"),
    ]
    for kind, pattern in rules:
        if re.search(rf"\b({pattern})\b", text):
            return kind
    return "other"
