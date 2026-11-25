"""Security rules: certificate/domain expiry, credential rotation."""

from __future__ import annotations

from datetime import timedelta

from ..model import ClientSnapshot, Idea
from . import fmt, names, plural, rule


@rule("security.expiring_certs_domains")
def expiring(snap: ClientSnapshot, s: dict) -> list[Idea]:
    ideas = []
    for kind, warn, label, what in (
        ("ssl", s["ssl_warn_days"], "SSL certificate", "Renew and install the certificate, then check every "
         "place it is bound (firewall SSL-VPN, RD Gateway, web server, mail)."),
        ("domain", s["domain_warn_days"], "domain", "Renew the domain and set it to auto-renew. Confirm the "
         "registrar contact details are current and registrar lock is on."),
    ):
        items = [e for e in snap.expirations if e.kind == kind and e.expires
                 and e.expires <= snap.as_of + timedelta(days=warn)]
        if not items:
            continue
        expired = [e for e in items if e.expires < snap.as_of]
        ideas.append(Idea(
            rule="security.expiring_certs_domains",
            title=f"Renew {plural(len(items), label)}" + (f" ({len(expired)} already expired)" if expired else
                                                          f" expiring within {warn} days"),
            description=what,
            category="Security",
            impact=3,
            urgency=3 if expired or min(e.expires for e in items) <= snap.as_of + timedelta(days=14) else 2,
            effort_hours=0.5 * len(items),
            billing="Agreement",
            evidence=[f"{e.name}: {fmt(e.expires)}" for e in sorted(items, key=lambda x: x.expires)],
            affected=names(items),
            due=min(e.expires for e in items),
        ))
    return ideas


@rule("security.stale_credentials")
def stale_credentials(snap: ClientSnapshot, s: dict) -> list[Idea]:
    limit = s["credential_max_age_days"]
    stale = [c for c in snap.credentials if c.updated and (snap.as_of - c.updated).days > limit]
    if not stale:
        return []
    words = [w.lower() for w in s["privileged_credential_words"]]
    privileged = [c for c in stale if any(w in f"{c.name} {c.kind}".lower() for w in words)]
    ordered = privileged + [c for c in stale if c not in privileged]
    return [Idea(
        rule="security.stale_credentials",
        title=f"Rotate {plural(len(stale), 'credential')} not changed in over {limit // 30} months"
              + (f" ({len(privileged)} privileged)" if privileged else ""),
        description="Rotate these passwords and update the vault. Start with privileged, shared and service "
                    "accounts. For any account that turns out to be unused, disable it instead of rotating it. "
                    "Where possible, move service accounts to managed identities or gMSAs.",
        category="Security",
        impact=3 if privileged else 2,
        urgency=2,
        effort_hours=round(0.25 * len(stale) + 0.5, 1),
        billing="Agreement",
        evidence=[f"{c.name}: last changed {fmt(c.updated)}" for c in ordered],
        affected=names(stale),
    )]
