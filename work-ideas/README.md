# work-ideas

Looks at a client's systems and produces a ranked list of **proactive work ideas** for technicians:
lifecycle risks, security gaps, recurring ticket patterns, documentation holes, and project/upsell
opportunities. Each idea comes with evidence, a priority, an effort estimate and a billing suggestion.

```
Hudu (assets, passwords, KB, expirations) ┐
HaloPSA (tickets, assets)                 ├─> client snapshot ─> rules engine ─┬─> Markdown / HTML report
Domotz (network devices, online status)   ┘                    (+ Claude, opt) ├─> CSV (all clients) / JSON
                                                                               └─> Halo tickets (opt-in)
```

## Quick start

```bash
cd work-ideas
pip install -r requirements.txt

# Try it on the bundled demo client (fictional data, no API keys needed)
python -m workideas --snapshot sample_data/demo_client.json --as-of 2026-11-21
# -> output/harbourside-dental-group-demo-2026-11-21.{md,html,csv,json}
```

For real clients:

```bash
cp config.example.toml config.toml          # map each client to its Hudu / Halo / Domotz ids
export HUDU_API_KEY=...  HALO_CLIENT_SECRET=...  DOMOTZ_API_KEY=...
python -m workideas --config config.toml                       # every client in the config
python -m workideas --config config.toml --client "Acme Pty Ltd"
python -m workideas --config config.toml --ai                  # add Claude's suggestions (needs ANTHROPIC_API_KEY)
python -m workideas --config config.toml --push-halo           # dry run: shows the tickets it would raise
python -m workideas --config config.toml --push-halo --yes     # actually raise new P1/P2 ideas as Halo tickets
```

Any source can be left out. A client with only Halo still gets the ticket-pattern ideas. If a source
fails (bad key, API down), the report still generates and the warning appears at the top.

## What it looks for

| Area | Rule | Example idea |
|---|---|---|
| Lifecycle | `lifecycle.os_eol` | Remediate Windows 10 end of support on 6 devices |
| | `lifecycle.warranty` | Review 2 infrastructure devices with expired warranty |
| | `lifecycle.hardware_age` | Build a replacement plan for 12 workstations older than 5 years |
| | `lifecycle.support_renewal` | Renew support/security subscriptions on 1 device (firewall) |
| Security | `security.expiring_certs_domains` | Renew 2 SSL certificates (1 already expired) |
| | `security.stale_credentials` | Rotate 5 credentials not changed in over 12 months (4 privileged) |
| | `reliability.firmware_drift` | Standardise firmware across 2 device models running mixed versions |
| Reliability | `reliability.offline_devices` | Investigate 1 infrastructure device showing offline in monitoring |
| Documentation | `documentation.undocumented_devices` | Document 5 devices found by Domotz but missing from Hudu |
| | `documentation.coverage_gaps` | Fill documentation gaps: Backup, Network diagram, UPS |
| | `documentation.stale_articles` / `incomplete_records` | Review 5 KB articles not updated in 18+ months |
| Tickets | `tickets.recurring_theme` | Root-cause project: Printing & scanning (10 tickets in 90 days) |
| | `tickets.password_resets` | Roll out self-service password reset |
| | `tickets.repeat_offenders` | Investigate 2 devices with repeated tickets |
| | `tickets.aged_open` | Review 3 tickets open more than 30 days |
| AI (optional) | `ai.suggestion` | Anything else the data supports, e.g. "Test a restore of the imaging DB" |

**Priority** = impact (1–3) × urgency (1–3): P1 ≥ 9, P2 ≥ 6, P3 ≥ 3, P4 below that.
Ideas are sorted by score, then due date.

## Tuning

- **Thresholds, disabled rules, custom ticket themes:** `[rules]` in `config.toml` (see the example file).
- **End-of-life dates:** `workideas/data/eol.json`. Check and update these as Microsoft and other vendors
  publish new dates. The first regex that matches the OS string wins.
- **Hudu field labels and device layouts:** `[hudu]` in config. The defaults match the current iScape
  layouts (`Operating system`, `Service tag`, `Brand`, `Subscription/Support Renewal`, …).
- **New rule:** add a function decorated with `@rule("area.name")` in `workideas/rules/`. It takes a
  `ClientSnapshot` and returns a list of `Idea`. See any existing module for the pattern.
- **New data source:** write a collector that fills a `ClientSnapshot` (see `collectors/domotz.py`, the
  shortest one) and register it in `collectors/__init__.py`. Devices are merged across sources on
  serial, then MAC, then name.

## Claude (optional `--ai`)

After the rules run, the snapshot and the rule ideas are sent to Claude (`claude-opus-5-5` by default).
Claude is asked only for additional ideas backed by evidence in the data. Its ideas are marked 🤖/AI in
the reports, and a technician should check them before acting on them.

- Needs `pip install anthropic` and `ANTHROPIC_API_KEY`.
- With `redact = true` (the default), IPs, MACs and ticket user names are masked before sending.
  Device names, client name, OS versions and ticket summaries are still sent. Check that this fits your
  client agreements before you enable it. Passwords are never collected, so they can't be sent.
- Server-side refusal fallback is on: if a safety classifier declines the request, the API retries it
  on a fallback model within the same call.

## Pushing to HaloPSA

`--push-halo` raises one ticket per new idea at or above `--push-min-priority` (default P2), using
`work_idea_tickettype_id` from config. Without `--yes` it only prints what it would do. Raised ideas are
recorded by fingerprint in `output/pushed_ideas.json`, so weekly runs don't create duplicates. Keep that
file between runs.

## Scheduling

Run it weekly (Windows Task Scheduler, cron, or an Azure Automation runbook) and point `--out` at a
shared folder. `all-clients-<date>.csv` drops straight into Excel or a Power BI dashboard for the
service delivery meeting.

## Tests

```bash
python -m pytest -q
```

## Before first live run

The Hudu, HaloPSA and Domotz collectors are written against those vendors' public REST APIs and are
tested against mocked responses, but they have **not yet been run against iScape's live tenants**.
Field names can differ by version and configuration, so do a first run on one client with
`--save-snapshot`. Check the snapshot JSON looks right, then adjust `[hudu.fields]` and the other mappings
as needed.
