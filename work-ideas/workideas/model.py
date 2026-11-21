"""Normalised data model shared by collectors, rules and reports.

Every collector (Hudu, HaloPSA, Domotz, JSON file) converts what it fetches
into a ClientSnapshot. Rules only ever look at a ClientSnapshot, so adding a
new data source never means touching the rules.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any


def parse_date(value: Any) -> date | None:
    """Best-effort parse of the date formats the various APIs return."""
    if value in (None, "", 0):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    # ISO 8601 with time / zone (Hudu, Halo, Domotz)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


@dataclass
class Device:
    name: str
    kind: str = "other"  # workstation | server | network | firewall | printer | storage | ups | other
    os: str = ""
    manufacturer: str = ""
    model: str = ""
    serial: str = ""
    mac: str = ""
    ip: str = ""
    purchase_date: date | None = None
    warranty_expiry: date | None = None
    support_renewal: date | None = None
    last_seen: date | None = None
    online: bool | None = None
    firmware: str = ""
    sources: list[str] = field(default_factory=list)
    documented: bool = False  # present in the documentation platform (Hudu)
    monitored: bool = False  # present in network monitoring (Domotz)
    url: str = ""


@dataclass
class Ticket:
    id: str
    summary: str
    created: date | None = None
    closed: date | None = None
    status: str = ""
    category: str = ""
    user: str = ""
    device: str = ""
    hours: float = 0.0
    url: str = ""


@dataclass
class Expiration:
    name: str
    kind: str  # ssl | domain | licence | warranty | contract | other
    expires: date | None
    url: str = ""


@dataclass
class Credential:
    name: str
    updated: date | None
    kind: str = ""
    url: str = ""


@dataclass
class Article:
    title: str
    updated: date | None
    url: str = ""


@dataclass
class ClientSnapshot:
    name: str
    as_of: date
    devices: list[Device] = field(default_factory=list)
    tickets: list[Ticket] = field(default_factory=list)
    expirations: list[Expiration] = field(default_factory=list)
    credentials: list[Credential] = field(default_factory=list)
    articles: list[Article] = field(default_factory=list)
    asset_layouts_present: list[str] = field(default_factory=list)  # Hudu layouts with >=1 asset
    sources: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)  # collector warnings

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass
class Idea:
    """One suggested piece of work for a technician."""

    rule: str
    title: str
    description: str
    category: str  # Lifecycle | Security | Reliability | Documentation | Service Improvement | Project Opportunity
    impact: int  # 1 (low) .. 3 (high)
    urgency: int  # 1 (low) .. 3 (high)
    effort_hours: float
    billing: str = "Agreement"  # Agreement | Project / Quote | Internal
    evidence: list[str] = field(default_factory=list)
    affected: list[str] = field(default_factory=list)
    due: date | None = None
    source: str = "rules"  # rules | ai

    @property
    def score(self) -> int:
        return self.impact * self.urgency

    @property
    def priority(self) -> str:
        s = self.score
        if s >= 9:
            return "P1"
        if s >= 6:
            return "P2"
        if s >= 3:
            return "P3"
        return "P4"

    @property
    def fingerprint(self) -> str:
        """Stable id so the same idea isn't raised as a new ticket every run."""
        key = f"{self.rule}|{self.title}|{'|'.join(sorted(self.affected))}"
        return hashlib.sha1(key.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        d = _jsonable(asdict(self))
        d.update(priority=self.priority, score=self.score, fingerprint=self.fingerprint)
        return d


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj


def snapshot_from_dict(data: dict[str, Any]) -> ClientSnapshot:
    """Inverse of ClientSnapshot.to_dict (used by the JSON collector and tests)."""

    def dates(d: dict, *keys: str) -> dict:
        d = dict(d)
        for k in keys:
            if k in d:
                d[k] = parse_date(d[k])
        return d

    return ClientSnapshot(
        name=data["name"],
        as_of=parse_date(data.get("as_of")) or date.today(),
        devices=[Device(**dates(d, "purchase_date", "warranty_expiry", "support_renewal", "last_seen"))
                 for d in data.get("devices", [])],
        tickets=[Ticket(**dates(t, "created", "closed")) for t in data.get("tickets", [])],
        expirations=[Expiration(**dates(e, "expires")) for e in data.get("expirations", [])],
        credentials=[Credential(**dates(c, "updated")) for c in data.get("credentials", [])],
        articles=[Article(**dates(a, "updated")) for a in data.get("articles", [])],
        asset_layouts_present=list(data.get("asset_layouts_present", [])),
        sources=list(data.get("sources", [])),
        notes=list(data.get("notes", [])),
    )
