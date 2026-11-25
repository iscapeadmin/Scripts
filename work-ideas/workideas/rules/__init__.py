"""Rule registry.

A rule is a function (snapshot, settings) -> list[Idea]. Register it with @rule("area.name").
Thresholds live in DEFAULT_SETTINGS and can be overridden in config.toml under [rules].
Disable a rule with  [rules] disabled = ["tickets.aged_open"].
"""

from __future__ import annotations

from datetime import date
from typing import Callable

from ..model import ClientSnapshot, Idea

RuleFn = Callable[[ClientSnapshot, dict], list[Idea]]
REGISTRY: dict[str, RuleFn] = {}

DEFAULT_SETTINGS: dict = {
    "disabled": [],
    # lifecycle
    "eol_warn_days": 180,
    "warranty_warn_days": 90,
    "max_age_years": {"workstation": 5, "server": 6, "network": 7, "firewall": 6, "storage": 6, "ups": 6},
    "renewal_warn_days": 60,
    # security
    "ssl_warn_days": 30,
    "domain_warn_days": 60,
    "credential_max_age_days": 365,
    "privileged_credential_words": ["admin", "administrator", "global", "domain", "root", "firewall",
                                    "break glass", "breakglass", "service", "svc", "vpn", "wifi", "router"],
    # reliability
    "offline_days": 7,
    "critical_kinds": ["server", "firewall", "network", "storage"],
    # documentation
    "undocumented_kinds": ["server", "firewall", "network", "storage", "printer", "ups"],
    "article_stale_days": 540,
    "expected_documentation": [
        {"name": "Backup", "any_of": ["Backup", "Backups", "Datto"]},
        {"name": "Firewall", "any_of": ["Firewalls"]},
        {"name": "Network diagram", "any_of": ["Network Diagrams"]},
        {"name": "Internet circuit", "any_of": ["internet circuit"]},
        {"name": "Site details", "any_of": ["Sites"]},
        {"name": "UPS", "any_of": ["UPS"], "when_kind": "server"},
        {"name": "Wireless", "any_of": ["Wireless"], "when_kind": "network"},
    ],
    # tickets
    "ticket_window_days": 90,
    "theme_min_tickets": 4,
    "repeat_device_min_tickets": 3,
    "repeat_user_min_tickets": 5,
    "password_reset_min_tickets": 4,
    "aged_open_days": 30,
}


def rule(rule_id: str) -> Callable[[RuleFn], RuleFn]:
    def deco(fn: RuleFn) -> RuleFn:
        REGISTRY[rule_id] = fn
        fn.rule_id = rule_id  # type: ignore[attr-defined]
        return fn
    return deco


def settings_from(cfg: dict | None) -> dict:
    merged = {**DEFAULT_SETTINGS, **(cfg or {})}
    merged["max_age_years"] = {**DEFAULT_SETTINGS["max_age_years"], **(cfg or {}).get("max_age_years", {})}
    return merged


def run_rules(snap: ClientSnapshot, settings: dict) -> tuple[list[Idea], list[str]]:
    """Returns (ideas, errors). A failing rule is reported, never fatal."""
    from . import documentation, lifecycle, reliability, security, tickets  # noqa: F401  (registers rules)

    ideas: list[Idea] = []
    errors: list[str] = []
    for rule_id, fn in REGISTRY.items():
        if rule_id in settings.get("disabled", []):
            continue
        try:
            for idea in fn(snap, settings):
                idea.rule = idea.rule or rule_id
                ideas.append(idea)
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f"{rule_id}: {type(exc).__name__}: {exc}")
    return rank(ideas), errors


def rank(ideas: list[Idea]) -> list[Idea]:
    return sorted(ideas, key=lambda i: (-i.score, i.due or date.max, -i.impact, i.title))


# ---- helpers shared by rule modules -------------------------------------------------

def fmt(d: date | None) -> str:
    return f"{d.day} {d:%b %Y}" if d else "unknown"


def plural(n: int, word: str, plural_word: str | None = None) -> str:
    return f"{n} {word if n == 1 else (plural_word or word + 's')}"


def names(items) -> list[str]:
    return sorted({getattr(i, "name", None) or getattr(i, "title", None) or str(i) for i in items})
