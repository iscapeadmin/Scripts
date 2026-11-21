"""Hudu collector: assets, passwords, articles and expirations for one company.

API reference: https://<your-hudu>/api_docs  (header: x-api-key)
"""

from __future__ import annotations

from ..model import Article, ClientSnapshot, Credential, Device, Expiration, parse_date
from .base import Http, classify_kind, secret, unwrap

# Defaults match the field labels in iScape's Hudu layouts; override in config [hudu.fields].
DEFAULT_FIELDS = {
    "os": ["Operating system", "Operating System", "OS"],
    "serial": ["Service tag", "Serial Number", "Serial"],
    "manufacturer": ["Brand", "Manufacturer", "Vendor"],
    "model": ["Model"],
    "warranty_expiry": ["Warranty Expiry", "Warranty Expiration", "Warranty End", "Warranty"],
    "purchase_date": ["Purchase Date", "Purchased", "Install Date"],
    "support_renewal": ["Subscription/Support Renewal", "Support Renewal", "Licence Expiry", "License Expiry"],
    "ip": ["IP Address", "Management IP"],
    "mac": ["MAC Address", "MAC"],
    "firmware": ["Firmware", "Firmware Version"],
}

DEFAULT_DEVICE_LAYOUTS = [
    "Assets", "Computer Assets", "Desktops", "Laptops", "Virtual Servers", "Hyper-V Hosts",
    "Firewalls", "Switches", "Network Devices", "Wireless", "NAS", "UPS", "ILO", "Ninja Assets",
]

EXPIRATION_KINDS = {
    "ssl_certificate": "ssl",
    "domain": "domain",
    "warranty": "warranty",
    "asset_field": "other",
    "article_expiration": "other",
}


class HuduCollector:
    name = "hudu"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.http = Http(cfg["base_url"].rstrip("/") + "/api/v1",
                         headers={"x-api-key": secret(cfg, "api_key_env", "HUDU_API_KEY")})
        self.fields = {**DEFAULT_FIELDS, **cfg.get("fields", {})}
        self.device_layouts = {n.lower() for n in cfg.get("device_layouts", DEFAULT_DEVICE_LAYOUTS)}
        self.web_base = cfg["base_url"].rstrip("/")

    def _paged(self, path: str, key: str, params: dict) -> list[dict]:
        out: list[dict] = []
        page = 1
        while True:
            batch = unwrap(self.http.get(path, {**params, "page": page, "page_size": 100}), key)
            out.extend(batch)
            if len(batch) < 100 or page > 200:
                return out
            page += 1

    def _field(self, asset: dict, logical: str) -> str:
        labels = {l.lower() for l in self.fields.get(logical, [])}
        for f in asset.get("fields", []) or []:
            if str(f.get("label", "")).lower() in labels and f.get("value") not in (None, ""):
                return str(f["value"]).strip()
        return ""

    def collect(self, snap: ClientSnapshot, client_cfg: dict) -> None:
        company_id = client_cfg["hudu_company_id"]
        snap.sources.append(self.name)

        assets = self._paged("assets", "assets", {"company_id": company_id, "archived": "false"})
        layouts_present = set()
        for a in assets:
            layout = a.get("asset_type") or a.get("asset_layout_name") or ""
            if layout:
                layouts_present.add(layout)
            if layout.lower() not in self.device_layouts:
                continue
            os_name = self._field(a, "os")
            snap.devices.append(Device(
                name=a.get("name", ""),
                kind=classify_kind(layout, os_name, a.get("primary_model", "")),
                os=os_name,
                manufacturer=self._field(a, "manufacturer") or a.get("primary_manufacturer") or "",
                model=self._field(a, "model") or a.get("primary_model") or "",
                serial=self._field(a, "serial") or a.get("primary_serial") or "",
                mac=self._field(a, "mac"),
                ip=self._field(a, "ip"),
                purchase_date=parse_date(self._field(a, "purchase_date")),
                warranty_expiry=parse_date(self._field(a, "warranty_expiry")),
                support_renewal=parse_date(self._field(a, "support_renewal")),
                firmware=self._field(a, "firmware"),
                sources=[self.name],
                documented=True,
                url=self._url(a.get("url")),
            ))
        snap.asset_layouts_present = sorted(layouts_present)

        for p in self._paged("asset_passwords", "asset_passwords", {"company_id": company_id}):
            snap.credentials.append(Credential(
                name=p.get("name", ""), updated=parse_date(p.get("updated_at")),
                kind=p.get("password_type") or "", url=self._url(p.get("url"))))

        for art in self._paged("articles", "articles", {"company_id": company_id}):
            snap.articles.append(Article(
                title=art.get("name", ""), updated=parse_date(art.get("updated_at")), url=self._url(art.get("url"))))

        for e in self._paged("expirations", "expirations", {"company_id": company_id}):
            if e.get("discarded_at"):
                continue
            kind = EXPIRATION_KINDS.get(e.get("expiration_type", ""), "other")
            label = e.get("name") or e.get("expirationable_name") or \
                f"{e.get('expirationable_type', 'Item')} #{e.get('expirationable_id', '?')}"
            snap.expirations.append(Expiration(
                name=label, kind=kind,
                expires=parse_date(e.get("date") or e.get("expiration_date"))))

    def _url(self, url: str | None) -> str:
        if not url:
            return ""
        return url if url.startswith("http") else f"{self.web_base}{url}"

