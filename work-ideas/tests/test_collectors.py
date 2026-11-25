from datetime import date

from workideas.collectors import build_snapshot
from workideas.collectors.base import Http

HUDU = {
    "assets": {"assets": [
        {"name": "HSD-DC01", "asset_type": "Virtual Servers", "primary_serial": "ABC123", "url": "/a/1",
         "fields": [{"label": "Operating system", "value": "Windows Server 2016 Standard"},
                    {"label": "Warranty Expiry", "value": "2023-03-12"}]},
        {"name": "FW", "asset_type": "Firewalls",
         "fields": [{"label": "Subscription/Support Renewal", "value": "2026/12/15"}]},
        {"name": "Jane Citizen", "asset_type": "Contacts", "fields": []},
    ]},
    "asset_passwords": {"asset_passwords": [{"name": "Domain Admin", "updated_at": "2023-01-01T00:00:00.000Z"}]},
    "articles": {"articles": [{"name": "Old KB", "updated_at": "2021-01-01T00:00:00Z"}]},
    "expirations": [{"expiration_type": "ssl_certificate", "date": "2026-11-30", "expirationable_type": "Website",
                     "expirationable_id": 4}],
}
DOMOTZ = [
    {"id": 1, "display_name": "hsd-dc01", "status": "ONLINE", "hw_address": "AA:BB:CC:00:11:22", "ip_addresses": ["10.0.0.10"]},
    {"id": 2, "display_name": "Core switch", "status": "OFFLINE", "last_status_change": "2026-11-01T10:00:00Z",
     "user_data": {"type": "Switch", "vendor": "Aruba", "model": "2930F"}, "ip_addresses": ["10.0.0.2"]},
    {"id": 3, "display_name": "hidden thing", "status": "HIDDEN"},
]


def test_hudu_and_domotz_collectors(monkeypatch):
    monkeypatch.setenv("HUDU_API_KEY", "x")
    monkeypatch.setenv("DOMOTZ_API_KEY", "y")

    def fake_get(self, path, params=None):
        if "domotz" in self.base_url:
            return DOMOTZ
        if params and params.get("page", 1) > 1:
            return []
        return HUDU[path]

    monkeypatch.setattr(Http, "get", fake_get)
    cfg = {"hudu": {"base_url": "https://docs.example.com"},
           "domotz": {"base_url": "https://api-domotz.example.com/public-api/v1"}}
    snap = build_snapshot("Acme", {"hudu_company_id": 1, "domotz_agent_ids": [9]}, cfg, as_of=date(2026, 11, 21))

    assert snap.notes == []
    assert snap.sources == ["hudu", "domotz"]
    by_name = {d.name.lower(): d for d in snap.devices}
    dc = by_name["hsd-dc01"]
    assert dc.kind == "server" and dc.documented and dc.monitored and dc.online
    assert dc.warranty_expiry == date(2023, 3, 12) and dc.url == "https://docs.example.com/a/1"
    assert by_name["fw"].support_renewal == date(2026, 12, 15)
    sw = by_name["core switch"]
    assert sw.kind == "network" and sw.online is False and not sw.documented
    assert "jane citizen" not in by_name and "hidden thing" not in by_name
    assert "Contacts" in snap.asset_layouts_present
    assert snap.expirations[0].kind == "ssl" and snap.credentials[0].updated == date(2023, 1, 1)


def test_halo_collector(monkeypatch):
    monkeypatch.setenv("HALO_CLIENT_SECRET", "s")

    class Resp:
        status_code = 200

        def json(self):
            return {"access_token": "tok"}

    monkeypatch.setattr("requests.Session.post", lambda *a, **k: Resp())
    pages = {1: {"record_count": 2, "tickets": [
        {"id": 5, "summary": "Printer jam", "dateoccurred": "2026-11-01T09:00:00", "dateclosed": "1900-01-01T00:00:00",
         "category_1": "Printing", "user_name": "Bob", "timetaken": 0.5},
        {"id": 6, "summary": "VPN", "dateoccurred": "2026-10-01T09:00:00", "dateclosed": "2026-10-02T09:00:00"}]}}
    monkeypatch.setattr(Http, "get", lambda self, path, params=None: pages.get(params["page_no"], {"tickets": []}))
    cfg = {"halo": {"base_url": "https://halo.example.com", "client_id": "id"}}
    snap = build_snapshot("Acme", {"halo_client_id": 12}, cfg, as_of=date(2026, 11, 21))
    assert snap.notes == []
    t5, t6 = snap.tickets
    assert t5.closed is None and t5.hours == 0.5 and t5.category == "Printing"
    assert t6.closed == date(2026, 10, 2)


def test_failing_source_becomes_warning(monkeypatch):
    monkeypatch.delenv("HUDU_API_KEY", raising=False)
    snap = build_snapshot("Acme", {"hudu_company_id": 1}, {"hudu": {"base_url": "https://x"}}, as_of=date(2026, 1, 1))
    assert snap.notes and "HUDU_API_KEY" in snap.notes[0]
