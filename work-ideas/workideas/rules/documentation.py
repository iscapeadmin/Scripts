"""Documentation rules: undocumented devices, missing layouts, stale articles, incomplete records."""

from __future__ import annotations

from ..model import ClientSnapshot, Idea
from . import fmt, names, plural, rule


@rule("documentation.undocumented_devices")
def undocumented(snap: ClientSnapshot, s: dict) -> list[Idea]:
    if "hudu" not in snap.sources and not any(d.documented for d in snap.devices):
        return []  # no documentation source: can't judge
    missing = [d for d in snap.devices if d.monitored and not d.documented and d.kind in s["undocumented_kinds"]]
    if not missing:
        return []
    return [Idea(
        rule="documentation.undocumented_devices",
        title=f"Document {plural(len(missing), 'infrastructure device')} found by monitoring but missing from Hudu",
        description="Create Hudu assets for these devices with management IP, credentials, firmware, warranty and "
                    "location. Undocumented infrastructure slows down every incident that involves it.",
        category="Documentation",
        impact=2, urgency=2,
        effort_hours=round(0.25 * len(missing) + 0.5, 1),
        billing="Agreement",
        evidence=[f"{d.name} ({d.kind}, {d.manufacturer} {d.model}, {d.ip or d.mac})".replace("  ", " ") for d in missing],
        affected=names(missing),
    )]


@rule("documentation.coverage_gaps")
def coverage_gaps(snap: ClientSnapshot, s: dict) -> list[Idea]:
    if "hudu" not in snap.sources and not snap.asset_layouts_present:
        return []
    present = {l.lower() for l in snap.asset_layouts_present}
    kinds = {d.kind for d in snap.devices}
    gaps = []
    for exp in s["expected_documentation"]:
        if exp.get("when_kind") and exp["when_kind"] not in kinds:
            continue
        if not any(a.lower() in present for a in exp["any_of"]):
            gaps.append(exp["name"])
    if not gaps:
        return []
    backup_missing = "Backup" in gaps
    return [Idea(
        rule="documentation.coverage_gaps",
        title=f"Fill documentation gaps: {', '.join(gaps)}",
        description="The client has no Hudu record for these standard items. Each gap usually means either the "
                    "service isn't in place or the knowledge sits in one technician's head."
                    + (" A missing backup record is the most important. Confirm what is backed up, where to, how "
                       "long it is kept, and when a restore was last tested." if backup_missing else ""),
        category="Documentation",
        impact=3 if backup_missing else 2,
        urgency=2,
        effort_hours=1.0 * len(gaps),
        billing="Agreement",
        evidence=[f"No asset in layout(s) {', '.join(e['any_of'])}" for e in s["expected_documentation"]
                  if e["name"] in gaps],
        affected=gaps,
    )]


@rule("documentation.stale_articles")
def stale_articles(snap: ClientSnapshot, s: dict) -> list[Idea]:
    limit = s["article_stale_days"]
    stale = [a for a in snap.articles if a.updated and (snap.as_of - a.updated).days > limit]
    if not stale:
        return []
    return [Idea(
        rule="documentation.stale_articles",
        title=f"Review {plural(len(stale), 'KB article')} not updated in {limit // 30}+ months",
        description="Check each article against the live environment. Update it, merge it into another, or "
                    "archive it. Out-of-date procedures cause failed fixes and wrong escalations.",
        category="Documentation",
        impact=1, urgency=1,
        effort_hours=round(0.25 * len(stale), 1),
        billing="Internal",
        evidence=[f"{a.title}: last updated {fmt(a.updated)}" for a in sorted(stale, key=lambda x: x.updated)],
        affected=names(stale),
    )]


@rule("documentation.incomplete_records")
def incomplete_records(snap: ClientSnapshot, s: dict) -> list[Idea]:
    checks = {
        "serial": lambda d: not d.serial,
        "warranty date": lambda d: d.kind in ("workstation", "server", "firewall", "storage") and not d.warranty_expiry,
        "operating system": lambda d: d.kind in ("workstation", "server") and not d.os,
    }
    gaps = {}
    for d in snap.devices:
        if not d.documented:
            continue
        missing = [label for label, test in checks.items() if test(d)]
        if missing:
            gaps[d.name] = missing
    if len(gaps) < 3:
        return []
    return [Idea(
        rule="documentation.incomplete_records",
        title=f"Complete missing asset details on {plural(len(gaps), 'Hudu record')}",
        description="Fill in serials, warranty dates and OS versions. Use the RMM/Hudu integration sync or the "
                    "vendor warranty lookup where possible. Lifecycle and warranty reporting is only as good as "
                    "these fields.",
        category="Documentation",
        impact=1, urgency=1,
        effort_hours=round(0.1 * len(gaps) + 0.5, 1),
        billing="Agreement",
        evidence=[f"{n}: missing {', '.join(m)}" for n, m in sorted(gaps.items())],
        affected=sorted(gaps),
    )]
