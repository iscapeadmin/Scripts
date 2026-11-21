"""Domotz collector: network devices seen by the client's Domotz agent(s).

base_url is your region's public API, e.g. https://api-us-east-1-cell-1.domotz.com/public-api/v1
(shown next to the API key in the Domotz portal). Header: X-Api-Key.
"""

from __future__ import annotations

from ..model import ClientSnapshot, Device, parse_date
from .base import Http, classify_kind, secret, unwrap


class DomotzCollector:
    name = "domotz"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.http = Http(cfg["base_url"], headers={"X-Api-Key": secret(cfg, "api_key_env", "DOMOTZ_API_KEY")})

    def collect(self, snap: ClientSnapshot, client_cfg: dict) -> None:
        snap.sources.append(self.name)
        for agent_id in client_cfg.get("domotz_agent_ids", []):
            for d in unwrap(self.http.get(f"agent/{agent_id}/device"), "devices"):
                status = str(d.get("status", "")).upper()
                if status == "HIDDEN":
                    continue
                user = d.get("user_data") or {}
                details = d.get("details") or {}
                ips = d.get("ip_addresses") or []
                name = user.get("name") or d.get("display_name") or d.get("hw_address") or f"device {d.get('id')}"
                model = user.get("model") or d.get("model") or ""
                vendor = user.get("vendor") or d.get("vendor") or ""
                type_hint = str(user.get("type") or (d.get("type") or {}).get("label") or "")
                snap.devices.append(Device(
                    name=name,
                    kind=classify_kind(type_hint, model, vendor, name),
                    manufacturer=vendor,
                    model=model,
                    serial=details.get("serial") or "",
                    mac=(d.get("hw_address") or "").lower(),
                    ip=ips[0] if ips else "",
                    firmware=details.get("firmware_version") or "",
                    online=status == "ONLINE",
                    last_seen=snap.as_of if status == "ONLINE" else parse_date(d.get("last_status_change")),
                    sources=[self.name],
                    monitored=True,
                ))
