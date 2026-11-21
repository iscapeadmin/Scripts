"""Build a ClientSnapshot from whichever sources are configured for a client."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from ..model import ClientSnapshot, Device, snapshot_from_dict
from .base import CollectorError


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def merge_devices(devices: list[Device]) -> list[Device]:
    """Merge the same physical device seen by several tools (match on serial, MAC, then name)."""
    merged: list[Device] = []
    index: dict[str, Device] = {}
    for d in devices:
        keys = [k for k in (f"s:{_norm(d.serial)}" if d.serial else "",
                            f"m:{_norm(d.mac)}" if d.mac else "",
                            f"n:{_norm(d.name)}" if d.name else "") if k]
        target = next((index[k] for k in keys if k in index), None)
        if target is None:
            merged.append(d)
            target = d
        else:
            for attr in ("os", "manufacturer", "model", "serial", "mac", "ip", "firmware", "url"):
                if not getattr(target, attr) and getattr(d, attr):
                    setattr(target, attr, getattr(d, attr))
            for attr in ("purchase_date", "warranty_expiry", "support_renewal", "last_seen"):
                if getattr(target, attr) is None and getattr(d, attr) is not None:
                    setattr(target, attr, getattr(d, attr))
            if target.kind == "other":
                target.kind = d.kind
            if d.online is not None:
                target.online = d.online
            target.documented |= d.documented
            target.monitored |= d.monitored
            target.sources = sorted(set(target.sources) | set(d.sources))
        for k in keys:
            index.setdefault(k, target)
    return merged


def build_snapshot(client_name: str, client_cfg: dict, cfg: dict, as_of: date | None = None) -> ClientSnapshot:
    if client_cfg.get("snapshot_file"):
        data = json.loads(Path(client_cfg["snapshot_file"]).read_text())
        snap = snapshot_from_dict(data)
        if as_of:
            snap.as_of = as_of
        return snap

    snap = ClientSnapshot(name=client_name, as_of=as_of or date.today())
    collectors = []
    if client_cfg.get("hudu_company_id") and "hudu" in cfg:
        from .hudu import HuduCollector
        collectors.append((HuduCollector, cfg["hudu"]))
    if client_cfg.get("halo_client_id") and "halo" in cfg:
        from .halo import HaloCollector
        collectors.append((HaloCollector, cfg["halo"]))
    if client_cfg.get("domotz_agent_ids") and "domotz" in cfg:
        from .domotz import DomotzCollector
        collectors.append((DomotzCollector, cfg["domotz"]))

    for cls, section in collectors:
        try:
            cls(section).collect(snap, client_cfg)
        except (CollectorError, KeyError, ValueError) as exc:
            # One broken source shouldn't stop the others; the gap is shown in the report.
            snap.notes.append(f"{cls.name}: {exc}")
        except Exception as exc:  # network errors etc.
            snap.notes.append(f"{cls.name}: {type(exc).__name__}: {exc}")

    snap.devices = merge_devices(snap.devices)
    return snap
