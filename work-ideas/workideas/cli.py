"""Command line entry point.

    python -m workideas --config config.toml                 # all clients in config
    python -m workideas --config config.toml --client "Acme"  # one client
    python -m workideas --snapshot sample_data/demo_client.json --as-of 2026-11-21
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

from . import report
from .collectors import build_snapshot
from .model import parse_date
from .rules import rank, run_rules, settings_from

FORMATS = {"md": report.to_markdown, "html": report.to_html, "json": report.to_json}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "client"


def load_state(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="workideas", description="Generate MSP technician work ideas from client systems.")
    ap.add_argument("--config", type=Path, help="config.toml (sources, clients, rule thresholds)")
    ap.add_argument("--client", action="append", help="only run for this client (repeatable)")
    ap.add_argument("--snapshot", type=Path, help="run against a saved JSON snapshot instead of live APIs")
    ap.add_argument("--as-of", help="evaluate as if today were this date (YYYY-MM-DD)")
    ap.add_argument("--out", type=Path, default=Path("output"), help="output folder (default ./output)")
    ap.add_argument("--format", default="md,html,csv,json", help="comma list of md,html,csv,json")
    ap.add_argument("--ai", action="store_true", help="also ask Claude for extra ideas (needs `anthropic` + API key)")
    ap.add_argument("--save-snapshot", action="store_true", help="also write the collected snapshot JSON")
    ap.add_argument("--push-halo", action="store_true", help="raise new P1/P2 ideas as Halo tickets")
    ap.add_argument("--push-min-priority", default="P2", choices=["P1", "P2", "P3", "P4"])
    ap.add_argument("--yes", action="store_true", help="actually create Halo tickets (otherwise dry run)")
    args = ap.parse_args(argv)

    cfg = tomllib.loads(args.config.read_text()) if args.config else {}
    as_of = parse_date(args.as_of) if args.as_of else None
    settings = settings_from(cfg.get("rules"))
    formats = [f.strip() for f in args.format.split(",") if f.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    if args.snapshot:
        clients = {"(snapshot)": {"snapshot_file": str(args.snapshot)}}
    else:
        clients = cfg.get("clients", {})
        if args.client:
            wanted = {c.lower() for c in args.client}
            clients = {k: v for k, v in clients.items() if k.lower() in wanted}
        if not clients:
            ap.error("no clients to run: add [clients.\"Name\"] sections to the config or pass --snapshot")

    state_path = args.out / "pushed_ideas.json"
    state = load_state(state_path)
    all_csv_rows: list[str] = []
    exit_code = 0

    for client_name, client_cfg in clients.items():
        snap = build_snapshot(client_name, client_cfg, cfg, as_of=as_of or date.today())
        ideas, errors = run_rules(snap, settings)

        if args.ai or cfg.get("ai", {}).get("enabled"):
            try:
                from .ai import suggest_ideas
                ideas = rank(ideas + suggest_ideas(snap, ideas, cfg.get("ai", {})))
            except Exception as exc:
                errors.append(f"ai: {type(exc).__name__}: {exc}")

        base = args.out / f"{slug(snap.name)}-{snap.as_of.isoformat()}"
        for fmt in formats:
            if fmt == "csv":
                text = report.to_csv(snap, ideas)
                lines = text.splitlines(keepends=True)
                all_csv_rows.extend(lines if not all_csv_rows else lines[1:])
            elif fmt in FORMATS:
                text = FORMATS[fmt](snap, ideas, errors)
            else:
                continue
            Path(f"{base}.{fmt}").write_text(text, encoding="utf-8")
        if args.save_snapshot:
            Path(f"{base}.snapshot.json").write_text(json.dumps(snap.to_dict(), indent=2), encoding="utf-8")

        p = {k: 0 for k in ("P1", "P2", "P3", "P4")}
        for i in ideas:
            p[i.priority] += 1
        print(f"{snap.name}: {len(ideas)} ideas (P1 {p['P1']}, P2 {p['P2']}, P3 {p['P3']}, P4 {p['P4']}) -> {base}.*")
        for w in snap.notes + errors:
            print(f"  warning: {w}", file=sys.stderr)
            exit_code = 2

        if args.push_halo:
            exit_code |= _push(cfg, client_cfg, snap.name, ideas, state, args)

    if "csv" in formats and all_csv_rows:
        (args.out / f"all-clients-{(as_of or date.today()).isoformat()}.csv").write_text("".join(all_csv_rows), encoding="utf-8")
    if args.push_halo and args.yes:
        state_path.write_text(json.dumps(state, indent=2))
    return exit_code


def _push(cfg, client_cfg, client_name, ideas, state, args) -> int:
    if "halo" not in cfg or not client_cfg.get("halo_client_id"):
        print("  halo push skipped: no [halo] config or halo_client_id for this client", file=sys.stderr)
        return 2
    order = ["P1", "P2", "P3", "P4"]
    limit = order.index(args.push_min_priority)
    already = set(state.get(client_name, []))
    todo = [i for i in ideas if order.index(i.priority) <= limit and i.fingerprint not in already]
    if not todo:
        print("  halo: nothing new to raise")
        return 0
    if not args.yes:
        print(f"  halo DRY RUN: would raise {len(todo)} tickets (add --yes to create them):")
        for i in todo:
            print(f"    [{i.priority}] {i.title}")
        return 0
    from .collectors.halo import push_ideas_to_halo
    created = push_ideas_to_halo(cfg["halo"], client_cfg, todo, client_name)
    state[client_name] = sorted(already | set(created))
    print(f"  halo: raised {len(created)} tickets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
