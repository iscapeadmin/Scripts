import json
import sys
import types
from datetime import date
from pathlib import Path

import pytest

from workideas import cli
from workideas.ai import summarise_snapshot, suggest_ideas
from workideas.collectors import merge_devices
from workideas.model import ClientSnapshot, Device, Ticket, snapshot_from_dict
from workideas.rules import run_rules, settings_from
from workideas.rules.lifecycle import load_eol, match_eol

DEMO = Path(__file__).resolve().parent.parent / "sample_data" / "demo_client.json"
AS_OF = date(2026, 11, 21)


@pytest.fixture
def demo():
    snap = snapshot_from_dict(json.loads(DEMO.read_text()))
    snap.as_of = AS_OF
    return snap


@pytest.mark.parametrize("os_name,product", [
    ("Microsoft Windows 10 Pro 22H2", "Windows 10"),
    ("Windows 10 Enterprise LTSC 2021", "Windows 10 Enterprise LTSC 2021"),
    ("Microsoft Windows 11 Pro 23H2 (22631)", "Windows 11 23H2"),
    ("Windows 11 Enterprise 23H2", "Windows 11 23H2 (Enterprise/Education)"),
    ("Microsoft Windows 11 Pro (26100)", "Windows 11 24H2"),
    ("Microsoft Windows Server 2012 R2 Standard", "Windows Server 2012 / 2012 R2"),
    ("Windows Server 2016 Datacenter", "Windows Server 2016"),
    ("Microsoft Windows 11 Pro 25H2 (26200)", None),
    ("macOS 15.1", None),
])
def test_eol_matching(os_name, product):
    match = match_eol(os_name, load_eol())
    assert (match["product"] if match else None) == product


def test_demo_produces_expected_ideas(demo):
    ideas, errors = run_rules(demo, settings_from({}))
    assert not errors
    rules = {i.rule for i in ideas}
    for expected in ["lifecycle.os_eol", "lifecycle.warranty", "lifecycle.hardware_age", "lifecycle.support_renewal",
                     "security.expiring_certs_domains", "security.stale_credentials", "reliability.offline_devices",
                     "reliability.firmware_drift", "documentation.undocumented_devices", "documentation.coverage_gaps",
                     "documentation.stale_articles", "tickets.recurring_theme", "tickets.password_resets",
                     "tickets.repeat_offenders", "tickets.aged_open"]:
        assert expected in rules, expected
    # ranked: highest score first
    assert [i.score for i in ideas] == sorted((i.score for i in ideas), reverse=True)
    p1 = [i.title for i in ideas if i.priority == "P1"]
    assert any("Windows 10" in t for t in p1)
    assert any("SSL" in t for t in p1)
    # routine feature updates shouldn't outrank an unsupported OS
    win11 = next(i for i in ideas if "Windows 11 23H2" in i.title)
    assert win11.priority == "P2" and win11.billing == "Agreement"


def test_disabled_rule_and_thresholds(demo):
    ideas, _ = run_rules(demo, settings_from({"disabled": ["tickets.aged_open"], "theme_min_tickets": 50}))
    rules = {i.rule for i in ideas}
    assert "tickets.aged_open" not in rules
    assert "tickets.recurring_theme" not in rules


def test_fingerprint_stable(demo):
    a, _ = run_rules(demo, settings_from({}))
    b, _ = run_rules(demo, settings_from({}))
    assert [i.fingerprint for i in a] == [i.fingerprint for i in b]
    assert len({i.fingerprint for i in a}) == len(a)


def test_merge_devices_across_sources():
    hudu = Device(name="HSD-SW01", kind="network", serial="CN12", documented=True, sources=["hudu"])
    domotz = Device(name="hsd-sw01", kind="network", mac="aa:bb:cc:dd:ee:ff", firmware="16.11", online=True,
                    monitored=True, sources=["domotz"])
    other = Device(name="PRN-1", kind="printer", monitored=True, sources=["domotz"])
    merged = merge_devices([hudu, domotz, other])
    assert len(merged) == 2
    sw = merged[0]
    assert sw.documented and sw.monitored and sw.firmware == "16.11" and sw.sources == ["domotz", "hudu"]


def test_no_documentation_source_means_no_doc_gap_ideas():
    snap = ClientSnapshot(name="X", as_of=AS_OF, sources=["domotz"],
                          devices=[Device(name="SW", kind="network", monitored=True, online=True)])
    ideas, _ = run_rules(snap, settings_from({}))
    assert not any(i.rule.startswith("documentation.") for i in ideas)


def test_redaction(demo):
    demo.tickets.append(Ticket(id="1", summary="Sarah Nguyen can't reach 10.20.0.5", user="Sarah Nguyen", created=AS_OF))
    summary = summarise_snapshot(demo, redact=True)
    blob = json.dumps(summary["tickets"])
    assert "Sarah Nguyen" not in blob and "10.20.0.5" not in blob
    assert "[ip]" in blob and "user-" in blob


def test_ai_suggestions_with_fake_client(demo, monkeypatch):
    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            payload = {"ideas": [{
                "title": "Test restore of practice imaging database", "description": "No restore test documented.",
                "category": "Reliability", "impact": 3, "urgency": 2, "effort_hours": 3,
                "billing": "Agreement", "evidence": ["Backup restore procedure last updated 30 Nov 2022"],
                "affected": ["HSD-APP01"]}]}
            return types.SimpleNamespace(stop_reason="end_turn",
                                         content=[types.SimpleNamespace(type="text", text=json.dumps(payload))])

    class FakeAnthropic:
        def __init__(self):
            self.beta = types.SimpleNamespace(messages=FakeMessages())

    monkeypatch.setitem(sys.modules, "anthropic", types.SimpleNamespace(Anthropic=FakeAnthropic))
    rule_ideas, _ = run_rules(demo, settings_from({}))
    ideas = suggest_ideas(demo, rule_ideas, {"max_ideas": 5})
    assert len(ideas) == 1 and ideas[0].source == "ai" and ideas[0].priority == "P2"
    assert captured["model"] == "claude-opus-5-5"
    assert captured["output_config"]["format"]["type"] == "json_schema"
    assert "Sarah Nguyen" not in captured["messages"][0]["content"]


def test_cli_end_to_end(tmp_path, capsys):
    code = cli.main(["--snapshot", str(DEMO), "--as-of", "2026-11-21", "--out", str(tmp_path)])
    assert code == 0
    files = sorted(p.name for p in tmp_path.iterdir())
    stem = "harbourside-dental-group-demo-2026-11-21"
    for ext in ("md", "html", "csv", "json"):
        assert f"{stem}.{ext}" in files
    data = json.loads((tmp_path / f"{stem}.json").read_text())
    assert data["ideas"] and data["ideas"][0]["priority"] == "P1"
    assert "<!doctype html>" in (tmp_path / f"{stem}.html").read_text()
