"""Reliability rules: offline devices, inconsistent firmware."""

from __future__ import annotations

from collections import defaultdict

from ..model import ClientSnapshot, Idea
from . import fmt, names, plural, rule


@rule("reliability.offline_devices")
def offline_devices(snap: ClientSnapshot, s: dict) -> list[Idea]:
    offline = [d for d in snap.devices if d.monitored and d.online is False]
    if not offline:
        return []
    critical = [d for d in offline if d.kind in s["critical_kinds"]]
    stale = [d for d in offline if d not in critical and d.last_seen
             and (snap.as_of - d.last_seen).days >= s["offline_days"]]
    ideas = []
    if critical:
        ideas.append(Idea(
            rule="reliability.offline_devices",
            title=f"Investigate {plural(len(critical), 'infrastructure device')} showing offline in monitoring",
            description="Find out whether each device is down, replaced or simply not polled. Fix it, or update the "
                        "monitoring and documentation so the alerting can be trusted.",
            category="Reliability",
            impact=3, urgency=3,
            effort_hours=0.5 * len(critical) + 0.5,
            evidence=[f"{d.name} ({d.kind}, {d.ip or 'no IP'}): offline since {fmt(d.last_seen)}" for d in critical],
            affected=names(critical),
            due=snap.as_of,
        ))
    if stale:
        ideas.append(Idea(
            rule="reliability.offline_devices",
            title=f"Clean up {plural(len(stale), 'device')} offline for {s['offline_days']}+ days",
            description="These devices haven't been seen for a while. Confirm with the client whether they're "
                        "retired, then remove them from monitoring and archive them in documentation, so asset "
                        "counts and billing stay accurate.",
            category="Documentation",
            impact=1, urgency=2,
            effort_hours=0.1 * len(stale) + 0.5,
            evidence=[f"{d.name}: last seen {fmt(d.last_seen)}" for d in sorted(stale, key=lambda x: x.last_seen)],
            affected=names(stale),
        ))
    return ideas


@rule("reliability.firmware_drift")
def firmware_drift(snap: ClientSnapshot, s: dict) -> list[Idea]:
    by_model: dict[tuple[str, str], list] = defaultdict(list)
    for d in snap.devices:
        if d.firmware and d.model and d.kind in ("network", "firewall", "storage", "ups", "printer"):
            by_model[(d.manufacturer.lower(), d.model.lower())].append(d)
    drift = {k: v for k, v in by_model.items() if len({d.firmware for d in v}) > 1}
    if not drift:
        return []
    devices = [d for v in drift.values() for d in v]
    return [Idea(
        rule="reliability.firmware_drift",
        title=f"Standardise firmware across {plural(len(drift), 'device model')} running mixed versions",
        description="The same model is running different firmware versions. Check the vendor advisories, then bring "
                    "every unit up to the current recommended release in a maintenance window.",
        category="Security",
        impact=2, urgency=2,
        effort_hours=0.75 * len(devices),
        evidence=[f"{v[0].manufacturer} {v[0].model}: " + ", ".join(sorted(f"{d.name}={d.firmware}" for d in v))
                  for v in drift.values()],
        affected=names(devices),
    )]
