"""Rank tracking: check where the site ranks, write it to the Rank tracker, report changes.

  python ranks.py check [--keywords tracked|all|primary] [--only "kw1,kw2"] [--depth 50]
                        [--max-cost N] [--project PATH] [--scheduled]
  python ranks.py sync                      write saved checks into the workbook (if Excel was open)
  python ranks.py report [--date D] [--vs D | --vs-column "Position Sep 8"]
  python ranks.py schedule --every daily|weekly|biweekly|monthly|quarterly
                           [--day 8] [--weekday MON] [--time 09:00] [--yes]
  python ranks.py unschedule [--yes]

check     One SERP pull per keyword at the configured depth, from the same location rules
          as serp.py, so every check is comparable with the last. Saves
          <data_dir>/ranks/<date>.json, then adds a "Position <Mon D>" column to the Rank
          tracker: a number is a position, "—" means not in the top <depth>.
          If the workbook is open, the check is kept and `sync` writes it later.
report    Movement against the previous check: top-3/10/20 counts, gains, losses, new
          entries, and keywords where a different page of the site ranks than the target.
schedule  Creates a Windows scheduled task (or prints a cron line elsewhere) that runs
          `check --scheduled` and records the cadence in seo-project.json, so status.py
          can say when a check is due. Without --yes it only prints what it would do.

Cost: about $0.0006 for the first 10 results plus $0.00045 per further 10
(measured Oct 2026): ~$0.0024 per keyword at depth 50, ~$0.0047 at depth 100.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402
import serp  # noqa: E402

DEFAULT_DEPTH = 50  # positions past 50 rarely change a decision, and depth 100 doubles the cost
EVERY_DAYS = c.EVERY_DAYS
NOT_RANKING = "—"


def task_cost(depth: int) -> float:
    pages = max(1, math.ceil(depth / 10))
    return 0.0006 + 0.00045 * (pages - 1)


def rcfg(cfg) -> dict:
    r = cfg.setdefault("ranks", {})
    r.setdefault("depth", DEFAULT_DEPTH)
    r.setdefault("keywords", "tracked")
    return r


def ranks_dir(cfg, root) -> Path:
    d = c.data_dir(cfg, root) / "ranks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def checks(cfg, root) -> list[Path]:
    return sorted(p for p in ranks_dir(cfg, root).glob("????-??-??.json"))


def header_for(date: str) -> str:
    d = dt.date.fromisoformat(date)
    return f"Position {d.strftime('%b')} {d.day}"  # "Position Oct 9", same as hand-added columns


def norm_path(u: str) -> str:
    p = serp.norm_url(u)
    return "/" + p.split("/", 1)[1].strip("/") + "/" if "/" in p and p.split("/", 1)[1].strip("/") else "/"


def log(cfg, root, msg):
    with (ranks_dir(cfg, root) / "schedule.log").open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now():%Y-%m-%d %H:%M} {msg}\n")


# ---------------------------------------------------------------- check

def tracked_keywords(cfg, root, mode) -> list[str]:
    rows = [r for r in c.read_map(cfg, root) if r.get("Status") != "Excluded"]
    if mode == "primary":
        return [r["Keyword"] for r in rows if r.get("Role") == "Primary"]
    if mode == "tracked":
        wb, _ = c.open_map(cfg, root, read_only=True)
        sheet = cfg["map"].get("rank_sheet", "Rank tracker")
        if sheet in wb.sheetnames:
            kws = [str(r[0]).strip() for r in wb[sheet].iter_rows(min_row=2, values_only=True) if r and r[0]]
            wb.close()
            if kws:
                return kws
        wb.close()
    return [r["Keyword"] for r in rows]


def cmd_check(a, cfg, root):
    r = rcfg(cfg)
    depth = a.depth or r["depth"]
    kws = [k.strip() for k in a.only.split(",")] if a.only else tracked_keywords(cfg, root, a.keywords or r["keywords"])
    kws = list(dict.fromkeys(c.norm_kw(k) for k in kws if k))
    if not kws:
        c.die("No keywords to check.")
    passes = a.passes or r.get("passes", 1)
    api = c.DataForSEO(cfg, root, a.max_cost, label=f"rank check {len(kws)} kw d{depth} x{passes}")
    est = len(kws) * task_cost(depth) * passes * (2 if a.fast else 1)
    if a.scheduled and est > api.cap:
        log(cfg, root, f"SKIPPED: estimate ${est:.2f} over cap ${api.cap:.2f}")
        c.die(f"Scheduled check skipped: ${est:.2f} is over the ${api.cap:.2f} cap.")
    api.preflight(est)
    date = c.TODAY
    raw = ranks_dir(cfg, root) / "raw" / date
    for p in range(1, passes + 1):
        if passes > 1:
            print(f"Pass {p} of {passes}")
        serp.run_pass(api, cfg, kws, raw / f"pass{p}", depth=depth, device=r.get("device"), fast=a.fast)
    dom = cfg["domain"].lower().removeprefix("www.")
    target = {c.norm_kw(x["Keyword"]): x.get("Target page") for x in c.read_map(cfg, root)}
    seen, pack = {}, {}
    for f in raw.glob("pass*/*.json"):
        t = json.loads(f.read_text(encoding="utf-8"))
        k = c.norm_kw(t["keyword"])
        hit = next((i for i in t["organic"] if (i.get("domain") or "").lower().removeprefix("www.").endswith(dom)), None)
        seen.setdefault(k, []).append((hit["rank"], hit["url"]) if hit else (None, None))
        in_pack = any(dom in str(x or "").lower() for x in t.get("local_pack", []))
        pack[k] = pack.get(k, False) or in_pack
    out = {}
    for k, hits in seen.items():
        found = [h for h in hits if h[0]]
        # several passes: the mean of the passes where the site was found; flagged when they disagree
        pos = round(sum(h[0] for h in found) / len(found)) if found else None
        spread = (max(h[0] for h in found) - min(h[0] for h in found)) if found else 0
        out[k] = {"pos": pos, "url": found[0][1] if found else None, "passes": [h[0] for h in hits],
                  "unstable": bool(len(hits) > 1 and (0 < len(found) < len(hits) or spread > 10)),
                  "map_pack": pack.get(k, False),
                  "target": target.get(k), "location": serp.location_for(k, cfg)}
    missing = [k for k in kws if k not in out]
    data = {"date": date, "depth": depth, "passes": passes,
            "device": r.get("device") or cfg["market"].get("device", "desktop"),
            "source": "DataForSEO Google organic", "written": False, "keywords": out}
    path = ranks_dir(cfg, root) / f"{date}.json"
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    api.done()
    ranked = sum(1 for v in out.values() if v["pos"])
    msg = (f"checked {len(out)} keywords at depth {depth}: {ranked} ranking, "
           f"{sum(1 for v in out.values() if v['pos'] and v['pos'] <= 10)} in the top 10, "
           f"{sum(1 for v in out.values() if v['map_pack'])} in the map pack")
    print(msg[0].upper() + msg[1:] + (f"; {len(missing)} returned no result" if missing else ""))
    if a.scheduled:
        log(cfg, root, msg + f", ${api.spent:.3f}")
    write_column(cfg, root, path)
    print("Next: python ranks.py report")


def write_column(cfg, root, path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    mp = c.map_path(cfg, root)
    if c.lock_file(mp).exists():
        print(f"{mp.name} is open in Excel: the check is saved in {path.name}. "
              "Close the workbook and run `ranks.py sync` to add the column.")
        return False
    wb, _ = c.open_map(cfg, root)
    sheet = cfg["map"].get("rank_sheet", "Rank tracker")
    ws = wb[sheet] if sheet in wb.sheetnames else wb.create_sheet(sheet)
    if ws.max_row == 1 and not ws.cell(1, 1).value:
        ws.cell(1, 1, "Keyword")
    head = header_for(data["date"])
    cols = {ws.cell(1, i).value: i for i in range(1, ws.max_column + 1)}
    col_i = cols.get(head) or (max([i for h, i in cols.items() if h] or [1]) + 1)  # same day re-run overwrites
    ws.cell(1, col_i, head)
    rows = {c.norm_kw(ws.cell(i, 1).value): i for i in range(2, ws.max_row + 1) if ws.cell(i, 1).value}
    for k, v in data["keywords"].items():
        i = rows.get(k)
        if i is None:
            ws.append([k])
            i = ws.max_row
            rows[k] = i
        ws.cell(i, col_i, v["pos"] if v["pos"] else NOT_RANKING)
    b = c.backup(mp)
    try:
        wb.save(mp)
    except PermissionError:
        print(f"Could not save {mp.name} (open in another program). Run `ranks.py sync` later.")
        return False
    data["written"] = True
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Added '{head}' to the {sheet} sheet ({len(data['keywords'])} keywords). Backup: {b.name}")
    return True


def cmd_sync(a, cfg, root):
    pending = [p for p in checks(cfg, root) if not json.loads(p.read_text(encoding="utf-8")).get("written")]
    if not pending:
        print("Nothing to sync: every check is already in the workbook.")
        return
    for p in pending:
        if not write_column(cfg, root, p):
            break


# ---------------------------------------------------------------- report

def load_check(cfg, root, date=None) -> dict:
    files = checks(cfg, root)
    if not files:
        c.die("No rank checks yet. Run: python ranks.py check")
    p = ranks_dir(cfg, root) / f"{date}.json" if date else files[-1]
    if not p.exists():
        c.die(f"No check for {date}. Available: {', '.join(f.stem for f in files)}")
    return json.loads(p.read_text(encoding="utf-8"))


def column_positions(cfg, root, header) -> dict:
    wb, _ = c.open_map(cfg, root, read_only=True)
    ws = wb[cfg["map"].get("rank_sheet", "Rank tracker")]
    rows = list(ws.iter_rows(values_only=True))
    if header not in rows[0]:
        c.die(f"No column '{header}' in the Rank tracker. Columns: {[h for h in rows[0] if h]}")
    i = rows[0].index(header)
    out = {}
    for r in rows[1:]:
        if r and r[0] and i < len(r) and r[i] not in (None, ""):
            out[c.norm_kw(r[0])] = c.as_int(r[i])  # "—" -> None (checked, not ranking)
    wb.close()
    return out


def cmd_report(a, cfg, root):
    now = load_check(cfg, root, a.date)
    if a.vs_column:
        before, label = column_positions(cfg, root, a.vs_column), a.vs_column
    else:
        older = [p for p in checks(cfg, root) if p.stem < now["date"]]
        if a.vs:
            prev = load_check(cfg, root, a.vs)
        elif older:
            prev = json.loads(older[-1].read_text(encoding="utf-8"))
        else:
            prev = None
        before = {k: v["pos"] for k, v in prev["keywords"].items()} if prev else {}
        label = prev["date"] if prev else None
    vols = {c.norm_kw(r["Keyword"]): r.get("Volume") or 0 for r in c.read_map(cfg, root)}
    cur = {k: v["pos"] for k, v in now["keywords"].items()}

    def bands(d):
        vals = [v for v in d.values() if v]
        return [sum(1 for v in vals if v <= n) for n in (3, 10, 20)] + [len(vals)]

    L = [f"# Rankings: {cfg['domain']}, {now['date']}", "",
         f"{len(cur)} keywords, Google {now['device']}, top {now['depth']} checked, "
         f"location per keyword as in seo-project.json." + (f" Compared with {label}." if label else " First check."), ""]
    bn = bands(cur)
    if label:
        common = {k: before.get(k) for k in cur if k in before}
        bb = bands(common)
        L += ["| | top 3 | top 10 | top 20 | ranking |", "|---|---|---|---|---|",
              f"| {now['date']} | {bn[0]} | {bn[1]} | {bn[2]} | {bn[3]} |",
              f"| {label} (same keywords) | {bb[0]} | {bb[1]} | {bb[2]} | {bb[3]} |", ""]
        if a.vs_column:
            L += ["Note: the comparison column came from the workbook, possibly another tool or location. "
                  "Positions from different sources are not like for like.", ""]
        moves = []
        for k, p in cur.items():
            if k not in before:
                continue
            b = before[k]
            if p and b:
                moves.append((b - p, k, b, p))
            elif p and not b:
                moves.append((999, k, None, p))
            elif b and not p:
                moves.append((-999, k, b, None))
        fmt = lambda x: str(x) if x else NOT_RANKING  # noqa: E731
        up = sorted([m for m in moves if m[0] > 0], key=lambda m: (-m[0], m[3]))
        down = sorted([m for m in moves if m[0] < 0], key=lambda m: m[0])
        for title, ms in (("Gained", up), ("Lost ground", down)):
            if ms:
                L += [f"## {title} ({len(ms)})", "", "| keyword | vol | was | now |", "|---|---|---|---|"]
                L += [f"| {k} | {vols.get(k, '')} | {fmt(b)} | {fmt(p)} |" for _, k, b, p in ms[:40]]
                L.append("")
    else:
        L += [f"Top 3: {bn[0]} · top 10: {bn[1]} · top 20: {bn[2]} · ranking at all: {bn[3]}", ""]
    packs = [k for k, v in now["keywords"].items() if v.get("map_pack")]
    if packs:
        L += [f"**In Google's map pack for {len(packs)} keywords** (not counted as organic positions): "
              + ", ".join(packs[:25]), ""]
    shaky = [k for k, v in now["keywords"].items() if v.get("unstable")]
    if shaky:
        L += [f"**{len(shaky)} positions moved more than 10 places between passes, or appeared in only some "
              f"passes:** {', '.join(shaky[:20])}. Read their changes as noise unless they repeat next check.", ""]
    wrong = [(k, v) for k, v in now["keywords"].items()
             if v["pos"] and v.get("target") and v.get("url") and norm_path(v["url"]) != v["target"]]
    if wrong:
        L += [f"## A different page ranks than the target ({len(wrong)})", "",
              "Either the target page doesn't exist yet, or two pages compete (check internal links and the target page's copy).", "",
              "| keyword | pos | ranking page | target page |", "|---|---|---|---|"]
        L += [f"| {k} | {v['pos']} | {norm_path(v['url'])} | {v['target']} |" for k, v in sorted(wrong, key=lambda x: x[1]['pos'])]
        L.append("")
    out = c.data_dir(cfg, root) / f"ranks-report-{now['date']}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12]))
    print(f"Full report: {out}")


# ---------------------------------------------------------------- schedule

def task_name(cfg) -> str:
    return f"SEO rank check - {cfg['domain']}"


def cmd_schedule(a, cfg, root):
    every = a.every
    script = Path(__file__).resolve()
    run = [sys.executable, str(script), "check", "--scheduled", "--project", str(root)]
    r = rcfg(cfg)
    r.update({"frequency": every, "time": a.time})
    if every in ("monthly", "quarterly"):
        r["day"] = a.day
    if every in ("weekly", "biweekly"):
        r["weekday"] = a.weekday
    if platform.system() == "Windows":
        # schtasks caps /TR at 261 characters, so the task runs a launcher file in the project
        launcher = ranks_dir(cfg, root) / "run-rank-check.cmd"
        launcher_text = (f'@echo off\r\ncd /d "{root}"\r\n'
                         f'"{sys.executable}" "{script}" check --scheduled --project "{root}" '
                         f'>> "{ranks_dir(cfg, root) / "schedule.log"}" 2>&1\r\n')
        run = [str(launcher)]
        sc = {"daily": ["/SC", "DAILY"], "weekly": ["/SC", "WEEKLY", "/D", a.weekday],
              "biweekly": ["/SC", "WEEKLY", "/MO", "2", "/D", a.weekday],
              "monthly": ["/SC", "MONTHLY", "/D", str(a.day)],
              "quarterly": ["/SC", "MONTHLY", "/MO", "3", "/D", str(a.day)]}[every]
        cmd = ["schtasks", "/Create", "/F", "/TN", task_name(cfg), "/TR", subprocess.list2cmdline(run),
               *sc, "/ST", a.time]
        print("Windows scheduled task:\n  " + subprocess.list2cmdline(cmd))
        print("It runs while you're logged in. If the computer is off at that time the check is "
              "missed; status.py will then say it's due.")
    else:
        h, m = a.time.split(":")
        cron = {"daily": f"{int(m)} {int(h)} * * *", "weekly": f"{int(m)} {int(h)} * * {a.weekday[:3].lower()}",
                "biweekly": f"{int(m)} {int(h)} * * {a.weekday[:3].lower()}",
                "monthly": f"{int(m)} {int(h)} {a.day} * *", "quarterly": f"{int(m)} {int(h)} {a.day} */3 *"}[every]
        line = f"{cron} cd {root} && {' '.join(run)}"
        print("Add this line with `crontab -e`" + (" (cron can't do every other week; this runs weekly)" if every == "biweekly" else "") + ":\n  " + line)
        cmd = None
    est = len(tracked_keywords(cfg, root, r["keywords"])) * task_cost(r["depth"])
    per_year = 365 / EVERY_DAYS[every]
    print(f"Each check: about ${est:.2f} at depth {r['depth']} (about ${est * per_year:.0f} a year at this cadence).")
    if not a.yes:
        print("\nNothing created yet. Run again with --yes to create it.")
        return
    if cmd:
        launcher.write_text(launcher_text, encoding="utf-8")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            c.die(f"schtasks failed: {res.stderr.strip() or res.stdout.strip()}")
        print(res.stdout.strip())
    save_config(cfg, root)
    print(f"Recorded in {c.CONFIG_NAME}: ranks.frequency = {every}.")


def cmd_unschedule(a, cfg, root):
    if platform.system() == "Windows":
        cmd = ["schtasks", "/Delete", "/F", "/TN", task_name(cfg)]
        print("  " + subprocess.list2cmdline(cmd))
        if not a.yes:
            print("Run again with --yes to delete it.")
            return
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(res.stdout.strip() or res.stderr.strip())
    else:
        print("Remove the line with `crontab -e`.")
    rcfg(cfg).pop("frequency", None)
    save_config(cfg, root)
    print("Rank checks are now manual: type 'check rankings' when you want one.")


def save_config(cfg, root):
    p = root / c.CONFIG_NAME
    raw = json.loads(p.read_text(encoding="utf-8"))
    raw["ranks"] = cfg["ranks"]
    p.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="project folder (used by scheduled runs)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("check")
    p.add_argument("--keywords", choices=["tracked", "all", "primary"])
    p.add_argument("--only")
    p.add_argument("--depth", type=int)
    p.add_argument("--passes", type=int, help="checks per keyword, averaged (default ranks.passes or 1)")
    p.add_argument("--max-cost", type=float)
    p.add_argument("--fast", action="store_true", help="high-priority queue, ~2x the price")
    p.add_argument("--scheduled", action="store_true")
    p.add_argument("--project")
    p.set_defaults(fn=cmd_check)
    p = sp.add_parser("sync"); p.set_defaults(fn=cmd_sync)
    p = sp.add_parser("report"); p.add_argument("--date"); p.add_argument("--vs"); p.add_argument("--vs-column")
    p.set_defaults(fn=cmd_report)
    p = sp.add_parser("schedule")
    p.add_argument("--every", required=True, choices=list(EVERY_DAYS))
    p.add_argument("--day", type=int, default=1, help="day of month (monthly, quarterly)")
    p.add_argument("--weekday", default="MON", help="MON..SUN (weekly, biweekly)")
    p.add_argument("--time", default="09:00")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(fn=cmd_schedule)
    p = sp.add_parser("unschedule"); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_unschedule)
    a = ap.parse_args()
    if getattr(a, "project", None):
        os.chdir(a.project)
    if not hasattr(a, "max_cost"):
        a.max_cost = None
    cfg, root = c.load_config()
    a.fn(a, cfg, root)


if __name__ == "__main__":
    main()
