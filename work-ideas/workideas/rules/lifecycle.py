"""Lifecycle rules: OS end-of-life, warranty, hardware age, subscription renewals."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

from ..model import ClientSnapshot, Device, Idea, parse_date
from . import fmt, names, plural, rule

KIND_LABEL = {"storage": "storage device", "network": "network device", "ups": "UPS", "firewall": "firewall"}
EOL_FILE = Path(__file__).resolve().parent.parent / "data" / "eol.json"


@lru_cache(maxsize=4)
def load_eol(path: str = str(EOL_FILE)) -> list[dict]:
    products = json.loads(Path(path).read_text())["products"]
    for p in products:
        p["_re"] = re.compile(p["match"], re.I)
        p["_eol"] = parse_date(p["eol"])
    return products


def match_eol(os_name: str, products: list[dict]) -> dict | None:
    if not os_name:
        return None
    return next((p for p in products if p["_re"].search(os_name)), None)


@rule("lifecycle.os_eol")
def os_end_of_life(snap: ClientSnapshot, s: dict) -> list[Idea]:
    products = load_eol(s.get("eol_file", str(EOL_FILE)))
    warn_until = snap.as_of + timedelta(days=s["eol_warn_days"])
    groups: dict[str, list[Device]] = defaultdict(list)
    product_by_name: dict[str, dict] = {}
    for d in snap.devices:
        p = match_eol(d.os, products)
        if p and p["_eol"] and p["_eol"] <= warn_until:
            groups[p["product"]].append(d)
            product_by_name[p["product"]] = p

    ideas = []
    for product, devices in groups.items():
        p = product_by_name[product]
        eol: date = p["_eol"]
        expired = eol <= snap.as_of
        servers = any(d.kind == "server" for d in devices)
        effort = sum(p["kind_effort"].get(d.kind, max(p["kind_effort"].values())) for d in devices)
        heavy = bool(re.search(r"replace|rebuild|migrat|move the", p["action"], re.I))
        status = f"ended {fmt(eol)}" if expired else f"ends {fmt(eol)} ({(eol - snap.as_of).days} days)"
        ideas.append(Idea(
            rule="lifecycle.os_eol",
            title=f"{'Remediate' if expired else 'Plan for'} {product} end of support on {plural(len(devices), 'device')}",
            description=f"Vendor support for {product} {status}. Devices that no longer get security patches "
                        f"are a cyber-insurance and Essential Eight gap. {p['action']}.",
            category="Lifecycle",
            # A feature update pushed from RMM is routine; a rebuild/replacement/migration is not.
            impact=3 if servers or (expired and heavy) else 2,
            urgency=3 if expired else 2,
            effort_hours=round(effort, 1),
            billing="Project / Quote" if servers or heavy else "Agreement",
            evidence=[f"{d.name}: {d.os}" for d in devices],
            affected=names(devices),
            due=max(eol, snap.as_of),
        ))
    return ideas


@rule("lifecycle.warranty")
def warranty(snap: ClientSnapshot, s: dict) -> list[Idea]:
    warn_until = snap.as_of + timedelta(days=s["warranty_warn_days"])
    critical = s["critical_kinds"]
    ideas = []
    for infra in (True, False):
        pool = [d for d in snap.devices if d.warranty_expiry and (d.kind in critical) == infra]
        expired = [d for d in pool if d.warranty_expiry < snap.as_of]
        expiring = [d for d in pool if snap.as_of <= d.warranty_expiry <= warn_until]
        what = "infrastructure device" if infra else "device"
        for label, devices in (("expired", expired), ("expiring", expiring)):
            if not devices:
                continue
            ideas.append(Idea(
                rule="lifecycle.warranty",
                title=(f"Review {plural(len(devices), what)} with expired warranty" if label == "expired"
                       else f"Warranty expiring within {s['warranty_warn_days']} days on {plural(len(devices), what)}"),
                description=("Decide for each device whether to extend the warranty, replace it, or accept the risk. "
                             "Put this in the client's next QBR or lifecycle report."
                             + (" These are infrastructure, so an unplanned hardware failure means a site-wide "
                                "outage. Quote an extension or replacement." if infra else "")),
                category="Lifecycle",
                impact=3 if infra else 1,
                urgency=3 if infra and label == "expired" else 2,
                effort_hours=round(1 + 0.25 * len(devices), 1),
                billing="Project / Quote" if infra else "Agreement",
                evidence=[f"{d.name} ({d.kind}, {d.manufacturer} {d.model}): warranty {fmt(d.warranty_expiry)}"
                          .replace("  ", " ") for d in sorted(devices, key=lambda x: x.warranty_expiry)],
                affected=names(devices),
                due=min(d.warranty_expiry for d in devices) if label == "expiring" else snap.as_of,
            ))
    return ideas


@rule("lifecycle.hardware_age")
def hardware_age(snap: ClientSnapshot, s: dict) -> list[Idea]:
    by_kind: dict[str, list[Device]] = defaultdict(list)
    for d in snap.devices:
        limit = s["max_age_years"].get(d.kind)
        if limit and d.purchase_date and (snap.as_of - d.purchase_date).days > limit * 365:
            by_kind[d.kind].append(d)
    ideas = []
    for kind, devices in by_kind.items():
        limit = s["max_age_years"][kind]
        ideas.append(Idea(
            rule="lifecycle.hardware_age",
            title=f"Build a replacement plan for {plural(len(devices), KIND_LABEL.get(kind, kind))} older than {limit} years",
            description=f"These devices are past the {limit}-year replacement guideline. Bring a costed, staged "
                        "refresh plan to the client so the spend can be budgeted rather than forced by failure.",
            category="Project Opportunity",
            impact=3 if kind in s["critical_kinds"] else 2,
            urgency=2,
            effort_hours=2,
            billing="Project / Quote",
            evidence=[f"{d.name}: purchased {fmt(d.purchase_date)}" for d in sorted(devices, key=lambda x: x.purchase_date)],
            affected=names(devices),
        ))
    return ideas


@rule("lifecycle.support_renewal")
def support_renewal(snap: ClientSnapshot, s: dict) -> list[Idea]:
    warn_until = snap.as_of + timedelta(days=s["renewal_warn_days"])
    due = [d for d in snap.devices if d.support_renewal and d.support_renewal <= warn_until]
    if not due:
        return []
    lapsed = [d for d in due if d.support_renewal < snap.as_of]
    return [Idea(
        rule="lifecycle.support_renewal",
        title=f"Renew support/security subscriptions on {plural(len(due), 'device')}"
              + (f" ({len(lapsed)} already lapsed)" if lapsed else ""),
        description="Firewall and appliance subscriptions (IPS, web filtering, firmware access, vendor support) "
                    "must stay current. Raise the renewal quote now so there is no gap in protection.",
        category="Security" if any(d.kind == "firewall" for d in due) else "Lifecycle",
        impact=3 if any(d.kind == "firewall" for d in due) else 2,
        urgency=3 if lapsed else 2,
        effort_hours=0.5 * len(due),
        billing="Project / Quote",
        evidence=[f"{d.name}: renewal {fmt(d.support_renewal)}" for d in sorted(due, key=lambda x: x.support_renewal)],
        affected=names(due),
        due=min(d.support_renewal for d in due),
    )]
