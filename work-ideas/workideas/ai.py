"""Optional Claude pass: suggests extra, evidence-based work ideas the fixed rules don't cover.

Needs `pip install anthropic` and ANTHROPIC_API_KEY (or an `ant auth login` profile).
By default identifiers (IPs, MACs, serials, user names) are redacted before anything is sent.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter

from .model import ClientSnapshot, Idea

DEFAULT_MODEL = "claude-opus-5-5"
CATEGORIES = ["Lifecycle", "Security", "Reliability", "Documentation", "Service Improvement", "Project Opportunity"]
BILLING = ["Agreement", "Project / Quote", "Internal"]

SYSTEM_PROMPT = """You are the service delivery lead at an Australian managed service provider (MSP). \
You review one client's environment data and propose concrete, proactive work for the MSP's technicians.

Good ideas are:
- grounded in the data provided: cite the specific devices, tickets or records that justify each one in `evidence`
- actionable by a technician or project engineer, written as a task title a dispatcher could assign
- valuable to the client (risk reduction, fewer tickets, compliance such as the ACSC Essential Eight, \
cyber-insurance requirements, or a sensible project/upsell)
- not duplicates of the ideas already raised by the rules engine (listed in the input)

Do not invent facts that are not in the data, and do not pad the list with generic best-practice advice \
that the data gives no reason to raise. If the data supports only a few good ideas, return only those. \
impact and urgency are 1 (low) to 3 (high). effort_hours is a realistic technician estimate."""

IDEA_SCHEMA = {
    "type": "object",
    "properties": {
        "ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "impact": {"type": "integer", "enum": [1, 2, 3]},
                    "urgency": {"type": "integer", "enum": [1, 2, 3]},
                    "effort_hours": {"type": "number"},
                    "billing": {"type": "string", "enum": BILLING},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "affected": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "description", "category", "impact", "urgency", "effort_hours",
                             "billing", "evidence", "affected"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["ideas"],
    "additionalProperties": False,
}

_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_MAC = re.compile(r"\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b", re.I)


class Redactor:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def text(self, value: str) -> str:
        if not self.enabled or not value:
            return value
        return _MAC.sub("[mac]", _IP.sub("[ip]", value))

    def person(self, value: str) -> str:
        if not self.enabled or not value:
            return value
        return "user-" + hashlib.sha1(value.lower().encode()).hexdigest()[:6]


def summarise_snapshot(snap: ClientSnapshot, redact: bool = True, max_tickets: int = 300) -> dict:
    """Compact, model-friendly view of the snapshot. Never includes passwords (none are collected)."""
    r = Redactor(redact)
    users = {t.user for t in snap.tickets if t.user}

    def scrub(text: str) -> str:
        text = r.text(text)
        if redact:
            for u in users:
                if len(u) > 3:
                    text = re.sub(re.escape(u), r.person(u), text, flags=re.I)
        return text

    tickets = sorted(snap.tickets, key=lambda t: t.created or snap.as_of, reverse=True)[:max_tickets]
    return {
        "client": snap.name,
        "as_of": snap.as_of.isoformat(),
        "data_sources": snap.sources,
        "device_counts": dict(Counter(d.kind for d in snap.devices)),
        "os_counts": dict(Counter(d.os for d in snap.devices if d.os)),
        "devices": [{
            "name": d.name, "kind": d.kind, "os": d.os, "make_model": f"{d.manufacturer} {d.model}".strip(),
            "firmware": d.firmware or None,
            "purchased": d.purchase_date.isoformat() if d.purchase_date else None,
            "warranty_expiry": d.warranty_expiry.isoformat() if d.warranty_expiry else None,
            "support_renewal": d.support_renewal.isoformat() if d.support_renewal else None,
            "online": d.online, "last_seen": d.last_seen.isoformat() if d.last_seen else None,
            "in_documentation": d.documented, "in_monitoring": d.monitored,
        } for d in snap.devices],
        "tickets": [{
            "id": t.id, "created": t.created.isoformat() if t.created else None,
            "closed": t.closed.isoformat() if t.closed else None, "status": t.status,
            "category": t.category, "summary": scrub(t.summary), "user": r.person(t.user),
            "device": t.device, "hours": t.hours or None,
        } for t in tickets],
        "ticket_count_total": len(snap.tickets),
        "expirations": [{"name": e.name, "kind": e.kind, "expires": e.expires.isoformat() if e.expires else None}
                        for e in snap.expirations],
        "credentials": [{"name": c.name, "kind": c.kind, "last_changed": c.updated.isoformat() if c.updated else None}
                        for c in snap.credentials],
        "kb_articles": [{"title": a.title, "updated": a.updated.isoformat() if a.updated else None}
                        for a in snap.articles],
        "documentation_layouts_present": snap.asset_layouts_present,
    }


def suggest_ideas(snap: ClientSnapshot, existing: list[Idea], cfg: dict | None = None) -> list[Idea]:
    import anthropic  # imported lazily so the rules engine works without the SDK installed

    cfg = cfg or {}
    payload = {
        "environment": summarise_snapshot(snap, redact=cfg.get("redact", True)),
        "ideas_already_raised_by_rules": [{"title": i.title, "category": i.category} for i in existing],
    }
    max_ideas = int(cfg.get("max_ideas", 8))
    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model=cfg.get("model", DEFAULT_MODEL),
        max_tokens=16000,
        # If a safety classifier declines, the API re-runs the request on a fallback model in the same call.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": cfg.get("effort", "high"),
                       "format": {"type": "json_schema", "schema": IDEA_SCHEMA}},
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Propose up to {max_ideas} additional work ideas for this client.\n\n"
                       f"<client_data>\n{json.dumps(payload, indent=1, default=str)}\n</client_data>",
        }],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined the request (stop_reason=refusal)")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Claude's response was cut off (max_tokens); try lowering ai.max_ideas")
    text = next((b.text for b in response.content if b.type == "text"), "")
    data = json.loads(text)

    ideas = []
    for raw in data.get("ideas", [])[:max_ideas]:
        ideas.append(Idea(
            rule="ai.suggestion",
            title=raw["title"],
            description=raw["description"],
            category=raw["category"],
            impact=int(raw["impact"]),
            urgency=int(raw["urgency"]),
            effort_hours=float(raw["effort_hours"]),
            billing=raw["billing"],
            evidence=list(raw.get("evidence", [])),
            affected=sorted(raw.get("affected", [])),
            source="ai",
        ))
    return ideas
