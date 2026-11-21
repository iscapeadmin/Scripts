"""HaloPSA collector (tickets, optionally assets) and ticket writer.

Uses an API application with Client Credentials auth (Configuration > Integrations > HaloPSA API).
Give it read access to Tickets/Customers/Assets, plus write access to Tickets if you
want --push-halo to raise the ideas as tickets.
"""

from __future__ import annotations

from datetime import timedelta

from ..model import ClientSnapshot, Device, Idea, Ticket, parse_date
from .base import CollectorError, Http, classify_kind, secret, unwrap


def _halo_date(value):
    """Halo uses 1900-01-01 as its 'no date' value."""
    d = parse_date(value)
    return d if d and d.year > 1900 else None


class HaloClient:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        base = cfg["base_url"].rstrip("/")
        auth_url = cfg.get("auth_url", f"{base}/auth").rstrip("/")
        token_params = {"tenant": cfg["tenant"]} if cfg.get("tenant") else None
        auth = Http(auth_url)
        auth.session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        resp = auth.session.post(f"{auth_url}/token", params=token_params, timeout=30, data={
            "grant_type": "client_credentials",
            "client_id": cfg["client_id"],
            "client_secret": secret(cfg, "client_secret_env", "HALO_CLIENT_SECRET"),
            "scope": cfg.get("scope", "all"),
        })
        if resp.status_code != 200:
            raise CollectorError(f"Halo auth failed: {resp.status_code} {resp.text[:200]}")
        token = resp.json()["access_token"]
        self.http = Http(f"{base}/api", headers={"Authorization": f"Bearer {token}"})
        self.web_base = base

    def paged(self, path: str, key: str, params: dict, page_size: int = 100) -> list[dict]:
        out: list[dict] = []
        page = 1
        while True:
            payload = self.http.get(path, {**params, "pageinate": "true", "page_size": page_size, "page_no": page})
            batch = unwrap(payload, key)
            out.extend(batch)
            total = payload.get("record_count") if isinstance(payload, dict) else None
            if not batch or len(batch) < page_size or (total is not None and len(out) >= total) or page > 200:
                return out
            page += 1


class HaloCollector:
    name = "halo"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.client = HaloClient(cfg)

    def collect(self, snap: ClientSnapshot, client_cfg: dict) -> None:
        client_id = client_cfg["halo_client_id"]
        snap.sources.append(self.name)
        lookback = int(self.cfg.get("ticket_lookback_days", 180))
        start = snap.as_of - timedelta(days=lookback)

        tickets = self.client.paged("Tickets", "tickets", {
            "client_id": client_id,
            "open_only": "false",
            "datesearch": "dateoccured",
            "startdate": start.isoformat(),
            "enddate": (snap.as_of + timedelta(days=1)).isoformat(),
        })
        for t in tickets:
            snap.tickets.append(Ticket(
                id=str(t.get("id")),
                summary=t.get("summary", "") or "",
                created=_halo_date(t.get("dateoccurred")),
                closed=_halo_date(t.get("dateclosed")),
                status=str(t.get("status_name") or t.get("status_id") or ""),
                category=t.get("category_1") or "",
                user=t.get("user_name") or "",
                device=t.get("inventory_number") or t.get("asset_name") or "",
                hours=float(t.get("timetaken") or 0),
                url=f"{self.client.web_base}/ticket?id={t.get('id')}",
            ))

        if self.cfg.get("include_assets", False):
            for a in self.client.paged("Asset", "assets", {"client_id": client_id}):
                name = a.get("inventory_number") or a.get("key_field") or f"Halo asset {a.get('id')}"
                snap.devices.append(Device(
                    name=name,
                    kind=classify_kind(a.get("assettype_name", ""), name),
                    serial=a.get("key_field2") or "",
                    sources=[self.name],
                    url=f"{self.client.web_base}/assets?id={a.get('id')}",
                ))


def push_ideas_to_halo(cfg: dict, client_cfg: dict, ideas: list[Idea], client_name: str) -> list[str]:
    """Raise each idea as a Halo ticket. Returns the fingerprints that were created."""
    halo = HaloClient(cfg)
    created = []
    priority_map = cfg.get("priority_ids", {})  # e.g. {"P1": 1, "P2": 2, ...}
    for idea in ideas:
        body = {
            "summary": f"[Work idea] {idea.title}"[:250],
            "details": _details_html(idea),
            "client_id": client_cfg["halo_client_id"],
            "tickettype_id": cfg["work_idea_tickettype_id"],
        }
        if client_cfg.get("halo_site_id"):
            body["site_id"] = client_cfg["halo_site_id"]
        if idea.priority in priority_map:
            body["priority_id"] = priority_map[idea.priority]
        if cfg.get("work_idea_category"):
            body["category_1"] = cfg["work_idea_category"]
        halo.http.post("Tickets", json=[body])
        created.append(idea.fingerprint)
    return created


def _details_html(idea: Idea) -> str:
    ev = "".join(f"<li>{e}</li>" for e in idea.evidence)
    aff = ", ".join(idea.affected[:30])
    return (
        f"<p>{idea.description}</p>"
        f"<p><b>Category:</b> {idea.category} &nbsp; <b>Priority:</b> {idea.priority} "
        f"&nbsp; <b>Est. effort:</b> {idea.effort_hours:g}h &nbsp; <b>Billing:</b> {idea.billing}</p>"
        + (f"<p><b>Evidence</b></p><ul>{ev}</ul>" if ev else "")
        + (f"<p><b>Affected:</b> {aff}</p>" if aff else "")
        + f"<p><small>Generated by work-ideas (rule {idea.rule}, id {idea.fingerprint})</small></p>"
    )
