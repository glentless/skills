"""Where is this project, and what should happen next? Behind "what now" / "how do I start".

  python status.py [--balance]

Checks, in order: project config, Python packages, DataForSEO credentials, keyword map,
research candidates waiting for triage, keywords without SERP data, grouping problems,
stale SERP data, and pages to build. Prints the state and ONE next step, with the
command to type. --balance also asks DataForSEO for the account balance (free call).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

STALE_DAYS = 120  # same as serp.py: local SERPs drift over a few months


def step(n, text, cmd=None):
    print(f"\nNEXT STEP: {text}")
    if cmd:
        print(f"  Type: {cmd}")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--balance", action="store_true")
    a = ap.parse_args()
    cfg, root = c.load_config(required=False)
    print("SEO keyword map: project status")
    print("-" * 40)
    if not root:
        print(f"No {c.CONFIG_NAME} in this folder or above it: this isn't set up as an SEO project yet.")
        step(1, "Set the project up. You'll be asked for the domain, country, main city and competitors.",
             "/seo-keyword-map init   (or say: set this folder up as an SEO project for example.com)")
    print(f"Project:   {cfg.get('domain')}  ({root})")

    try:
        import openpyxl  # noqa: F401
        pk = True
    except ImportError:
        pk = False
    if not pk:
        step(2, "Install the one Python package the scripts need.", "pip install openpyxl")

    cred = c.credentials()
    print(f"DataForSEO: {'credentials found in ' + cred[2] if cred else 'NO CREDENTIALS'}")
    c.warn_stray_credentials(root)

    mp = c.map_path(cfg, root)
    if not mp.exists():
        print(f"Map:       missing ({mp.name})")
        step(3, "Create the keyword map workbook.", "/seo-keyword-map init")
    if c.lock_file(mp).exists():
        print(f"           note: {mp.name} is open in Excel; close it before any step that writes")
    rows = c.read_map(cfg, root)
    pages = c.pages_from_rows(rows)
    todo = [p for p in pages.values() if not p["exists"]]
    unm = [r for r in rows if r.get("Status") == "Unmapped" or (not r.get("Target page") and r.get("Status") != "Excluded")]
    no_type = [p for p in pages.values() if not p["type"]]
    print(f"Map:       {mp.name}: {len(rows)} keywords, {len(pages)} pages ({len(todo)} to build), "
          f"{len(unm)} unmapped")

    serp = c.latest_serp(cfg, root)
    live = [r for r in rows if r.get("Status") != "Excluded"]
    missing = [r for r in live if c.norm_kw(r["Keyword"]) not in serp]
    snaps = c.snapshots(cfg, root)
    last = snaps[-1].stem[:10] if snaps else None
    print(f"SERP data: {len(live) - len(missing)} of {len(live)} keywords"
          + (f", latest pull {last}" if last else ", none yet"))

    cand = c.data_dir(cfg, root) / "research" / "candidates.csv"
    waiting = None
    if cand.exists():
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import research as rs
        rows_c = rs.load(cfg, root)
        in_map = {c.norm_kw(r["Keyword"]) for r in rows}
        tri = set()
        try:
            wb, _ = c.open_map(cfg, root, read_only=True)
            tn = cfg["map"].get("triage_sheet", "Draft list triage")
            if tn in wb.sheetnames:
                tri = {c.norm_kw(r[0]) for r in wb[tn].iter_rows(min_row=2, values_only=True) if r and r[0]}
            wb.close()
        except SystemExit:
            pass
        fresh = [k for k in rows_c if k not in in_map and k not in tri]
        novol = [k for k in fresh if rows_c[k].get("volume") in (None, "")]
        waiting = [k for k in fresh if (c.as_int(rows_c[k].get("volume")) or 0) >= cfg["min_volume"]]
        print(f"Research:  {len(rows_c)} candidates; {len(waiting)} at {cfg['min_volume']}+/mo waiting for triage, "
              f"{len(novol)} without volume")
    rdir = c.data_dir(cfg, root) / "ranks"
    rfiles = sorted(rdir.glob("????-??-??.json")) if rdir.exists() else []
    unsynced = [p.stem for p in rfiles if not json.loads(p.read_text(encoding="utf-8")).get("written")]
    rc = cfg.get("ranks", {})
    every = rc.get("frequency")
    last_rank = rfiles[-1].stem if rfiles else None
    next_rank = c.next_rank_due(last_rank, rc)
    print("Ranks:     " + (f"last check {last_rank}" if last_rank else "never checked")
          + (f"; {every}, next due {next_rank}" if every else "; checked when you ask (no schedule)")
          + (f"; {len(unsynced)} check(s) not yet in the workbook" if unsynced else ""))
    spent = c.ledger_total(cfg, root)
    print(f"Spend:     ${spent:.2f} on DataForSEO for this project (cap ${cfg['budget']['max_usd_per_run']:.2f} per run)")
    if a.balance and cred:
        api = c.DataForSEO(cfg, root)
        print(f"Balance:   ${api.balance() or 0:.2f}")

    # one next step, first match wins
    if not cred:
        step(4, "Add the DataForSEO login to your user folder (never inside a project). "
                "reference/tutorial.md, setup step 2, shows how.", None)
    if unsynced:
        step(4.5, f"Rank check(s) {', '.join(unsynced)} were saved while the workbook was open. "
                  "Close Excel and add them to the Rank tracker.", "/seo-keyword-map ranks sync")
    if next_rank and next_rank <= c.TODAY and rows:
        n = len(rows)
        est = n * (0.0006 + 0.00045 * (max(1, -(-rc.get("depth", 50) // 10)) - 1)) * rc.get("passes", 1)
        step(4.6, f"A {every} rank check is due (last {last_rank or 'never'}), about ${est:.2f}.",
             "/seo-keyword-map ranks check")
    if not rows:
        step(5, "Find keywords. Start with the service x place grid, then competitors.",
             "/seo-keyword-map research")
    if cand.exists() and novol:
        step(6, f"Look up volume for {len(novol)} candidates before triage (about $0.09 per 1,000).",
             "/seo-keyword-map research volume")
    if waiting:
        step(7, f"Triage {len(waiting)} keyword candidates: add, fold into a kept term, or remove.",
             "/seo-keyword-map triage")
    if missing:
        est = len(missing) * 2 * 0.00105
        step(8, f"Pull Google results for {len(missing)} keywords without SERP data (about ${est:.2f}).",
             "/seo-keyword-map serp")
    if unm or no_type:
        step(9, f"Group keywords into pages ({len(unm)} unmapped, {len(no_type)} pages without a type).",
             "/seo-keyword-map group")
    if last and (dt.date.today() - dt.date.fromisoformat(last)).days > STALE_DAYS:
        step(10, f"SERP data is from {last}, over {STALE_DAYS} days old. Refresh it, then regroup.",
             "/seo-keyword-map serp --stale")
    if todo:
        step(11, f"The map is in shape. {len(todo)} pages are waiting to be built; list the next batch.",
             "/seo-keyword-map plan")
    step(12, "Every mapped page exists. Look for new keywords, or check rankings.",
         "/seo-keyword-map research")


if __name__ == "__main__":
    main()
