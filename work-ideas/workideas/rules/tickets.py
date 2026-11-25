"""Ticket-history rules: recurring themes, repeat devices/users, password resets, aged tickets.

The idea: if the same thing keeps getting fixed reactively, there is a root-cause project
(or an automation) that pays for itself.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import timedelta

from ..model import ClientSnapshot, Idea, Ticket
from . import fmt, plural, rule

# theme -> (keywords, suggested proactive fix)
THEMES: dict[str, tuple[list[str], str]] = {
    "Printing & scanning": (
        ["printer", "printing", "print ", "scan", "scanner", "toner", "copier", "mfp"],
        "Standardise printer deployment (Universal Print or a GPO/Intune print policy), update drivers, and "
        "check whether the fleet or managed-print contract needs review."),
    "Email & Outlook": (
        ["outlook", "email", "e-mail", "mailbox", "calendar", "shared mailbox", "exchange"],
        "Review mailbox sizes and archiving, Outlook profile and add-in health, and shared mailbox permissions. "
        "Consider New Outlook readiness and a short user tip sheet."),
    "Network & Wi-Fi": (
        ["wifi", "wi-fi", "wireless", "internet", "network", "dropout", "drop out", "no connection", "disconnect"],
        "Run a wireless survey and network health check (AP placement, channel plan, switch errors, ISP SLA). "
        "Quote any upgrade it shows is needed."),
    "Remote access & VPN": (
        ["vpn", "remote desktop", "rdp", "remote access", "citrix", "rd gateway", "work from home", "wfh"],
        "Review the remote access design: VPN client versions, MFA, split tunnelling, and whether it can move "
        "to ZTNA or cloud-hosted apps."),
    "Performance": (
        ["slow", "freez", "frozen", "hang", "not responding", "performance", "crash"],
        "Correlate the slow devices with hardware age, disk and RAM, and startup bloat. Clean up at scale with "
        "RMM scripts and add any machine below spec to the refresh plan."),
    "Teams & telephony": (
        ["teams", "phone", "call quality", "headset", "voip", "audio", "microphone", "handset"],
        "Check Teams/VoIP call quality data and QoS, and standardise approved headsets. Review the network "
        "path for voice traffic."),
    "File access & sync": (
        ["onedrive", "sharepoint", "shared drive", "mapped drive", "file share", "permission", "access denied", "sync"],
        "Review the file storage design and permissions model, map drives consistently through policy, and "
        "fix OneDrive Known Folder Move and sync health."),
    "Onboarding & offboarding": (
        ["new starter", "new user", "onboard", "offboard", "leaver", "termination", "new employee", "starter"],
        "Automate joiner/leaver steps with a Halo template and an M365/Entra automation runbook. Agree a "
        "standard lead time with the client."),
    "Software installs & updates": (
        ["install", "update", "upgrade", "licen", "activation", "adobe"],
        "Package the commonly requested software for self-service or automatic deployment through RMM/Intune, "
        "and review licence allocation."),
}

PASSWORD_WORDS = ["password", "locked out", "lockout", "account locked", "mfa", "authenticator", "reset my", "sign in", "sign-in", "login"]


def _text(t: Ticket) -> str:
    return f" {t.summary} {t.category} ".lower()


def _recent(snap: ClientSnapshot, s: dict) -> list[Ticket]:
    since = snap.as_of - timedelta(days=s["ticket_window_days"])
    return [t for t in snap.tickets if t.created and t.created >= since]


@rule("tickets.recurring_theme")
def recurring_theme(snap: ClientSnapshot, s: dict) -> list[Idea]:
    recent = _recent(snap, s)
    themes = {**THEMES, **{k: (v["keywords"], v["suggestion"]) for k, v in s.get("ticket_themes", {}).items()}}
    hits: dict[str, list[Ticket]] = defaultdict(list)
    for t in recent:
        text = _text(t)
        for theme, (words, _) in themes.items():
            if any(w in text for w in words):
                hits[theme].append(t)
    ideas = []
    window = s["ticket_window_days"]
    for theme, tickets in hits.items():
        if len(tickets) < s["theme_min_tickets"]:
            continue
        hours = sum(t.hours for t in tickets)
        share = len(tickets) / max(len(recent), 1)
        ideas.append(Idea(
            rule="tickets.recurring_theme",
            title=f"Root-cause project: {theme} ({len(tickets)} tickets in {window} days)",
            description=f"{theme} made up {share:.0%} of tickets in the last {window} days"
                        + (f", about {hours:g} hours of reactive time" if hours else "")
                        + f". {themes[theme][1]}",
            category="Service Improvement",
            impact=3 if share >= 0.2 or hours >= 10 else 2,
            urgency=2,
            effort_hours=max(2.0, round(hours * 0.3, 1)),
            billing="Project / Quote" if hours >= 10 else "Agreement",
            evidence=[f"#{t.id} {fmt(t.created)}: {t.summary}" for t in sorted(tickets, key=lambda x: x.created, reverse=True)],
            affected=[theme],
        ))
    return ideas


@rule("tickets.repeat_offenders")
def repeat_offenders(snap: ClientSnapshot, s: dict) -> list[Idea]:
    recent = _recent(snap, s)
    by_device: dict[str, list[Ticket]] = defaultdict(list)
    by_user: dict[str, list[Ticket]] = defaultdict(list)
    for t in recent:
        if t.device:
            by_device[t.device].append(t)
        if t.user:
            by_user[t.user].append(t)
    ideas = []
    hot_devices = {d: ts for d, ts in by_device.items() if len(ts) >= s["repeat_device_min_tickets"]}
    if hot_devices:
        ideas.append(Idea(
            rule="tickets.repeat_offenders",
            title=f"Investigate {plural(len(hot_devices), 'device')} with repeated tickets",
            description="These devices keep coming back. Do a full health check (hardware diagnostics, event logs, "
                        "reimage if needed). If they are old or out of warranty, recommend replacement.",
            category="Reliability",
            impact=2, urgency=2,
            effort_hours=1.5 * len(hot_devices),
            evidence=[f"{d}: {len(ts)} tickets ({'; '.join(t.summary for t in ts[:3])})" for d, ts in
                      sorted(hot_devices.items(), key=lambda kv: -len(kv[1]))],
            affected=sorted(hot_devices),
        ))
    hot_users = {u: ts for u, ts in by_user.items() if len(ts) >= s["repeat_user_min_tickets"]}
    if hot_users:
        ideas.append(Idea(
            rule="tickets.repeat_offenders",
            title=f"Offer a 1:1 check-in or training for {plural(len(hot_users), 'high-ticket user')}",
            description="A short desk-side session often uncovers a bad device, a missing permission or a "
                        "workflow gap behind a run of tickets. This is a good account-management touchpoint.",
            category="Service Improvement",
            impact=1, urgency=2,
            effort_hours=1.0 * len(hot_users),
            evidence=[f"{u}: {len(ts)} tickets" for u, ts in sorted(hot_users.items(), key=lambda kv: -len(kv[1]))],
            affected=sorted(hot_users),
        ))
    return ideas


@rule("tickets.password_resets")
def password_resets(snap: ClientSnapshot, s: dict) -> list[Idea]:
    recent = _recent(snap, s)
    resets = [t for t in recent if any(w in _text(t) for w in PASSWORD_WORDS)]
    if len(resets) < s["password_reset_min_tickets"]:
        return []
    return [Idea(
        rule="tickets.password_resets",
        title=f"Roll out self-service password reset ({len(resets)} lockout/password tickets in {s['ticket_window_days']} days)",
        description="Turn on Entra ID SSPR with password writeback and combined MFA/SSPR registration. Run a short "
                    "enrolment campaign, and consider passkeys or Windows Hello for Business to cut password "
                    "use entirely.",
        category="Service Improvement",
        impact=2, urgency=2,
        effort_hours=4,
        billing="Project / Quote",
        evidence=[f"#{t.id} {fmt(t.created)}: {t.summary}" for t in resets],
        affected=["Password / account lockout tickets"],
    )]


@rule("tickets.aged_open")
def aged_open(snap: ClientSnapshot, s: dict) -> list[Idea]:
    limit = s["aged_open_days"]
    closed_words = re.compile(r"closed|resolved|cancel", re.I)
    aged = [t for t in snap.tickets if not t.closed and t.created and not closed_words.search(t.status or "")
            and (snap.as_of - t.created).days > limit]
    if not aged:
        return []
    return [Idea(
        rule="tickets.aged_open",
        title=f"Review {plural(len(aged), 'ticket')} open more than {limit} days",
        description="Close, escalate or convert each one to a project. Long-open tickets hurt client satisfaction "
                    "and often hide a bigger issue.",
        category="Service Improvement",
        impact=2, urgency=2,
        effort_hours=round(0.25 * len(aged), 1),
        billing="Internal",
        evidence=[f"#{t.id} opened {fmt(t.created)}: {t.summary}" for t in sorted(aged, key=lambda x: x.created)],
        affected=[f"#{t.id}" for t in aged],
    )]
