"""Report writers: Markdown, HTML, CSV and JSON."""

from __future__ import annotations

import csv
import html
import io
import json
from collections import Counter

from .model import ClientSnapshot, Idea

MAX_LIST = 15


def _date(d) -> str:
    return f"{d.day} {d:%b %Y}" if d else ""


def _clip(items: list[str], limit: int = MAX_LIST) -> list[str]:
    return items[:limit] + ([f"…and {len(items) - limit} more"] if len(items) > limit else [])


def to_json(snap: ClientSnapshot, ideas: list[Idea], errors: list[str]) -> str:
    return json.dumps({
        "client": snap.name,
        "as_of": snap.as_of.isoformat(),
        "sources": snap.sources,
        "warnings": snap.notes + errors,
        "ideas": [i.to_dict() for i in ideas],
    }, indent=2)


def to_csv(snap: ClientSnapshot, ideas: list[Idea]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["client", "priority", "title", "category", "impact", "urgency", "effort_hours", "billing",
                "due", "source", "rule", "fingerprint", "description", "affected", "evidence"])
    for i in ideas:
        w.writerow([snap.name, i.priority, i.title, i.category, i.impact, i.urgency, i.effort_hours, i.billing,
                    i.due.isoformat() if i.due else "", i.source, i.rule, i.fingerprint, i.description,
                    "; ".join(i.affected), " | ".join(i.evidence)])
    return buf.getvalue()


def to_markdown(snap: ClientSnapshot, ideas: list[Idea], errors: list[str]) -> str:
    lines = [f"# Work ideas: {snap.name}", "",
             f"Generated {_date(snap.as_of)} from {', '.join(snap.sources) or 'no sources'}. "
             f"{len(ideas)} ideas, about {round(sum(i.effort_hours for i in ideas), 1):g} technician hours in total.", ""]
    counts = Counter(i.priority for i in ideas)
    lines += ["| Priority | Ideas |", "|---|---|"] + [f"| {p} | {counts.get(p, 0)} |" for p in ("P1", "P2", "P3", "P4")] + [""]
    if snap.notes or errors:
        lines += ["> **Data warnings:** " + "; ".join(snap.notes + errors), ""]
    lines += ["| # | Pri | Idea | Category | Effort | Billing | Due |", "|---|---|---|---|---|---|---|"]
    for n, i in enumerate(ideas, 1):
        lines.append(f"| {n} | {i.priority} | {i.title}{' 🤖' if i.source == 'ai' else ''} | {i.category} | "
                     f"{i.effort_hours:g}h | {i.billing} | {_date(i.due)} |")
    lines.append("")
    for n, i in enumerate(ideas, 1):
        lines += [f"## {n}. [{i.priority}] {i.title}", "",
                  f"*{i.category} · impact {i.impact}/3 · urgency {i.urgency}/3 · ~{i.effort_hours:g}h · {i.billing}"
                  f"{' · due ' + _date(i.due) if i.due else ''} · `{i.rule}` · id `{i.fingerprint}`*", "",
                  i.description, ""]
        if i.evidence:
            lines += ["**Evidence**", ""] + [f"- {e}" for e in _clip(i.evidence)] + [""]
    if any(i.source == "ai" for i in ideas):
        lines += ["---", "🤖 = suggested by Claude from the client data. Check it before you action it."]
    return "\n".join(lines) + "\n"


def to_html(snap: ClientSnapshot, ideas: list[Idea], errors: list[str], standalone: bool = True) -> str:
    e = html.escape
    counts = Counter(i.priority for i in ideas)
    hours = round(sum(i.effort_hours for i in ideas), 1)
    cats = sorted({i.category for i in ideas})
    rows = []
    for n, i in enumerate(ideas, 1):
        ev = "".join(f"<li>{e(x)}</li>" for x in _clip(i.evidence))
        rows.append(f"""
<details class="idea" data-cat="{e(i.category)}" data-pri="{i.priority}">
  <summary>
    <span class="pri {i.priority}">{i.priority}</span>
    <span class="title">{e(i.title)}{' <span class="ai" title="Suggested by Claude">AI</span>' if i.source == 'ai' else ''}</span>
    <span class="meta">{e(i.category)}</span>
    <span class="meta num">{i.effort_hours:g}h</span>
    <span class="meta">{e(_date(i.due))}</span>
  </summary>
  <div class="body">
    <p>{e(i.description)}</p>
    <p class="facts">Impact {i.impact}/3 · Urgency {i.urgency}/3 · {e(i.billing)} · rule <code>{e(i.rule)}</code> · id <code>{i.fingerprint}</code></p>
    {'<h4>Evidence</h4><ul>' + ev + '</ul>' if ev else ''}
  </div>
</details>""")
    warn = ""
    if snap.notes or errors:
        warn = '<div class="warn"><b>Data warnings:</b> ' + e("; ".join(snap.notes + errors)) + "</div>"
    chips = "".join(f'<button class="chip" data-filter="{e(c)}">{e(c)}</button>' for c in cats)
    head = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">') if standalone else ""
    return head + f"""<title>Work ideas: {e(snap.name)}</title>
<style>
:root {{ --bg:#f7f7f5; --card:#fff; --ink:#1d1d1b; --muted:#6b6b66; --line:#e4e3de; --accent:#2f5d50;
  --p1:#b3261e; --p2:#b8650a; --p3:#3a6ea5; --p4:#77776f; color-scheme: light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#161615; --card:#1f1f1d; --ink:#ecebe6;
  --muted:#a09f98; --line:#33322f; --accent:#7fb8a6; --p1:#f2867f; --p2:#f0a75a; --p3:#88b4e6; --p4:#a09f98; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg:#161615; --card:#1f1f1d; --ink:#ecebe6; --muted:#a09f98; --line:#33322f; --accent:#7fb8a6;
  --p1:#f2867f; --p2:#f0a75a; --p3:#88b4e6; --p4:#a09f98; color-scheme: dark; }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; padding:0 16px; }}
main {{ max-width:980px; margin:0 auto; padding-block:32px 64px; }}
h1 {{ font-size:1.6rem; margin:0 0 4px; letter-spacing:-.01em; }}
.sub {{ color:var(--muted); margin:0 0 24px; }}
.stats {{ display:flex; flex-wrap:wrap; gap:12px; margin-bottom:20px; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px 16px; min-width:90px; }}
.stat b {{ display:block; font-size:1.4rem; font-variant-numeric:tabular-nums; }}
.stat span {{ color:var(--muted); font-size:.8rem; }}
.filters {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:16px; }}
.chip {{ font:inherit; font-size:.85rem; border:1px solid var(--line); background:var(--card); color:var(--ink);
  border-radius:999px; padding:4px 12px; cursor:pointer; }}
.chip[aria-pressed="true"] {{ background:var(--accent); border-color:var(--accent); color:var(--bg); }}
.idea {{ background:var(--card); border:1px solid var(--line); border-radius:10px; margin-bottom:8px; }}
.idea summary {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px; padding:12px 16px; cursor:pointer; list-style:none; }}
.idea summary::-webkit-details-marker {{ display:none; }}
.title {{ flex:1 1 320px; font-weight:600; }}
.meta {{ color:var(--muted); font-size:.85rem; }}
.num {{ font-variant-numeric:tabular-nums; min-width:3ch; text-align:right; }}
.pri {{ font-size:.75rem; font-weight:700; border-radius:6px; padding:2px 7px; color:var(--card); }}
.P1 {{ background:var(--p1); }} .P2 {{ background:var(--p2); }} .P3 {{ background:var(--p3); }} .P4 {{ background:var(--p4); }}
.ai {{ font-size:.7rem; border:1px solid var(--accent); color:var(--accent); border-radius:4px; padding:0 4px; margin-left:6px; vertical-align:middle; }}
.body {{ padding:0 16px 14px; border-top:1px solid var(--line); }}
.facts {{ color:var(--muted); font-size:.85rem; }}
h4 {{ margin:12px 0 4px; font-size:.85rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }}
ul {{ margin:0; padding-left:20px; }} li {{ margin:2px 0; overflow-wrap:anywhere; }}
code {{ font-size:.8rem; }}
.warn {{ border:1px solid var(--p2); border-radius:10px; padding:10px 14px; margin-bottom:16px; }}
</style>
<main>
  <h1>{e(snap.name)}: work ideas</h1>
  <p class="sub">Generated {e(_date(snap.as_of))} from {e(', '.join(snap.sources) or 'no sources')}</p>
  <div class="stats">
    <div class="stat"><b>{len(ideas)}</b><span>ideas</span></div>
    <div class="stat"><b>{counts.get('P1', 0)}</b><span>P1</span></div>
    <div class="stat"><b>{counts.get('P2', 0)}</b><span>P2</span></div>
    <div class="stat"><b>{counts.get('P3', 0) + counts.get('P4', 0)}</b><span>P3–P4</span></div>
    <div class="stat"><b>{hours:g}h</b><span>est. effort</span></div>
  </div>
  {warn}
  <div class="filters"><button class="chip" data-filter="" aria-pressed="true">All</button>{chips}</div>
  {''.join(rows)}
</main>
<script>
document.querySelectorAll('.chip').forEach(btn => btn.addEventListener('click', () => {{
  document.querySelectorAll('.chip').forEach(b => b.setAttribute('aria-pressed', b === btn));
  const f = btn.dataset.filter;
  document.querySelectorAll('.idea').forEach(el => el.hidden = !!f && el.dataset.cat !== f);
}}));
</script>
"""
