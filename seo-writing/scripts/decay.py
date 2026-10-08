#!/usr/bin/env python3
"""Find posts losing Search traffic from Google Search Console exports. Stdlib only.

    python decay.py compare.csv                    # one GSC "Compare" export (Pages tab)
    python decay.py current.csv previous.csv       # two exports of equal-length periods
    python decay.py cur.json prev.json --metric impressions --threshold 0.3 --json

Accepts the Pages CSV from the Search Console UI (Performance > Pages > Export),
with or without date comparison, and Search Console API JSON ({"rows": [...]}
with keys, or a list of {page, clicks, impressions, ctr, position}).

Severity by decline: 20-39% warning, 40-59% high, 60%+ critical.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

MIN_PRIOR = 10  # below this many prior clicks a drop is noise, not decay


def number(v) -> float:
    if v is None or v == "":
        return 0.0
    s = str(v).strip().replace(",", "").rstrip("%")
    try:
        return float(s)
    except ValueError:
        return 0.0


def load(path: Path) -> tuple[dict, dict | None]:
    """Return (current, previous-or-None); each maps page -> metrics."""
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        rows = data.get("rows", data) if isinstance(data, dict) else data
        out = {}
        for r in rows:
            page = r.get("page") or r.get("url") or (r.get("keys") or [None])[0]
            if page:
                out[page] = {k: number(r.get(k)) for k in ("clicks", "impressions", "ctr", "position")}
        return out, None
    reader = csv.DictReader(text.splitlines())
    cols = reader.fieldnames or []
    page_col = next((c for c in cols if re.search(r"page|url|address", c, re.I)), cols[0] if cols else None)
    clicks = [c for c in cols if c.lower().endswith("clicks")]
    cur, prev = {}, {}
    compare = len(clicks) == 2
    for r in reader:
        page = r.get(page_col)
        if not page:
            continue
        for target, prefix in ((cur, "last|current"), (prev, "previous|prior")) if compare else ((cur, ""),):
            m = {}
            for metric in ("clicks", "impressions", "ctr", "position"):
                col = next((c for c in cols if c.lower().endswith(metric) and
                            (not prefix or re.match(prefix, c, re.I))), None)
                m[metric] = number(r.get(col)) if col else 0.0
            target[page] = m
    if compare and not prev:
        raise ValueError("found two Clicks columns but could not tell current from previous")
    return cur, (prev if compare else None)


def diagnose(c: dict, p: dict) -> str:
    if not c:
        return "dropped out: confirm same filters/row limit, then inspect indexing, redirects and canonical"
    imp_change = (c["impressions"] - p["impressions"]) / p["impressions"] if p["impressions"] else 0
    pos_change = c["position"] - p["position"] if c["position"] and p["position"] else 0
    if imp_change > -0.1:
        return "impressions held, clicks fell: snippet/SERP change (title, meta, AI answers, new features)"
    if pos_change > 2:
        return f"ranking loss (position {p['position']:.1f} -> {c['position']:.1f}): refresh content, check intent and competitors"
    return "demand fell at stable position: compare year over year for seasonality before editing"


def analyze(cur: dict, prev: dict, metric: str, threshold: float, min_prior: int) -> dict:
    rows = []
    for page, p in prev.items():
        before = p[metric]
        if before < (min_prior if metric == "clicks" else min_prior * 10):
            continue
        c = cur.get(page)
        after = c[metric] if c else 0.0
        change = (after - before) / before
        if change <= -threshold:
            sev = "critical" if change <= -0.6 else "high" if change <= -0.4 else "warning"
            rows.append({"page": page, "before": before, "after": after, "change": round(change, 3),
                         "lost": before - after, "severity": sev, "diagnosis": diagnose(c, p)})
    rows.sort(key=lambda r: -r["lost"])
    total = lambda d: sum(x[metric] for x in d.values())
    gainers = sum(1 for pg, c in cur.items() if pg in prev and c[metric] > prev[pg][metric] * (1 + threshold))
    return {"metric": metric, "threshold": threshold, "pages_compared": len(prev),
            "total_before": total(prev), "total_after": total(cur), "decaying": rows, "gaining_pages": gainers}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("current")
    ap.add_argument("previous", nargs="?")
    ap.add_argument("--metric", choices=("clicks", "impressions"), default="clicks")
    ap.add_argument("--threshold", type=float, default=0.2, help="decline that counts as decay (default 0.2)")
    ap.add_argument("--min-prior", type=int, default=MIN_PRIOR, help=f"ignore pages under this many prior clicks (default {MIN_PRIOR})")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        cur, prev = load(Path(a.current))
        if a.previous:
            prev = load(Path(a.previous))[0]
        if prev is None:
            print("error: one file without comparison columns; export with Compare dates, or pass two files", file=sys.stderr)
            return 2
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    r = analyze(cur, prev, a.metric, a.threshold, a.min_prior)
    if a.json:
        print(json.dumps(r, indent=2))
        return 0
    tb, ta = r["total_before"], r["total_after"]
    site = f"{(ta - tb) / tb:+.0%}" if tb else "n/a"
    print(f"# Content decay ({a.metric}, threshold {a.threshold:.0%})\n")
    print(f"{r['pages_compared']} pages compared. Site total {tb:,.0f} -> {ta:,.0f} ({site}). "
          f"{len(r['decaying'])} decaying, {r['gaining_pages']} gaining.\n")
    if r["decaying"]:
        print("| page | before | after | change | severity | first thing to check |\n|---|---|---|---|---|---|")
        for x in r["decaying"]:
            print(f"| {x['page']} | {x['before']:,.0f} | {x['after']:,.0f} | {x['change']:+.0%} | {x['severity']} | {x['diagnosis']} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
