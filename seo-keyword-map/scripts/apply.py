"""Validate a changes file and write it into the keyword map.

  python apply.py changes.json --check    # validate and preview, writes nothing
  python apply.py changes.json            # back up, then write

The changes file format is in reference/map-format.md. Every write:
  - refuses to run while the workbook is open in Excel
  - backs the workbook up next to itself first
  - keeps exactly one Primary per page (or stops)
  - recomputes Cluster volume, sets Priority on pages to build from priority_rules
  - adds new keywords to the Rank tracker sheet and triage rows to the triage sheet
  - appends a summary to <data_dir>/map-changelog.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

TOP_KEYS = {"note", "pages", "rename", "assign", "add", "triage", "exclude"}


def load_changes(path: Path) -> dict:
    try:
        ch = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        c.die(f"Changes file not found: {path}")
    except json.JSONDecodeError as e:
        c.die(f"{path.name} is not valid JSON: {e}")
    bad = set(ch) - TOP_KEYS
    if bad:
        c.die(f"Unknown key(s) {sorted(bad)} in {path.name}. Allowed: {sorted(TOP_KEYS)}")
    return ch


def priority_for(page: dict, cfg: dict):
    for rule in cfg.get("priority_rules", []):
        lines, types = rule.get("service_line", "*"), rule.get("page_types", ["*"])
        if (lines == "*" or lines == page["line"]) and ("*" in types or page["type"] in types):
            return rule["priority"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("changes")
    ap.add_argument("--check", action="store_true", help="validate and preview only")
    a = ap.parse_args()
    cfg, root = c.load_config()
    ch = load_changes(Path(a.changes))
    path = c.map_path(cfg, root)
    if not a.check:
        c.check_not_open(path)
    wb, ws = c.open_map(cfg, root)
    idx = c.header_index(ws, cfg)
    errors, warns = [], []

    # make sure Page type exists (older maps don't have it)
    if "Page type" not in idx:
        ws.cell(1, ws.max_column + 1, c.col(cfg, "Page type"))
        idx = c.header_index(ws, cfg)
        warns.append("added a 'Page type' column")
    head_len = max(idx.values()) + 1

    # in-memory model: keyword -> row dict, keeping the worksheet row for writing back
    model, order = {}, []
    for row in ws.iter_rows(min_row=2):
        cells = list(row) + [None] * (head_len - len(row))
        kv = cells[idx["Keyword"]].value if cells[idx["Keyword"]] is not None else None
        if not kv:
            continue
        d = {k: (cells[i].value if cells[i] is not None else None) for k, i in idx.items()}
        d["_row"] = row[0].row
        k = c.norm_kw(kv)
        model[k] = d
        order.append(k)
    existing_pages = {d["Target page"] for d in model.values() if d.get("Target page")}
    # whether each page is live, from the map as it was: a keyword moved in from a live page
    # must not make a planned page look live
    page_live = {}
    for d in model.values():
        if d.get("Target page"):
            live = str(d.get("Page exists") or "").strip().lower() in ("yes", "true", "1")
            page_live[d["Target page"]] = page_live.get(d["Target page"], False) or live
    page_defs = ch.get("pages", {})
    for url, pdef in page_defs.items():
        if pdef.get("type") and pdef["type"] not in c.PAGE_TYPES:
            errors.append(f"pages['{url}'].type '{pdef['type']}' is not one of {c.PAGE_TYPES}")

    # renames
    for old, new in ch.get("rename", {}).items():
        hit = [k for k, d in model.items() if d.get("Target page") == old]
        if not hit:
            warns.append(f"rename: no keyword targets '{old}'")
        for k in hit:
            model[k]["Target page"] = new
        if hit:
            existing_pages.add(new)  # a renamed page is still the same page, not a new one
            page_live[new] = page_live.get(new, False) or page_live.get(old, False)

    def set_assignment(d, item, label):
        if "page" in item:
            d["Target page"] = item["page"] or None
        if "role" in item:
            if item["role"] not in c.ROLES:
                errors.append(f"{label}: role '{item['role']}' must be one of {c.ROLES}")
            d["Role"] = item["role"]
        if item.get("note"):
            d["Action"] = item["note"]
        if "priority" in item:
            d["Priority"] = item["priority"]

    for item in ch.get("assign", []):
        k = c.norm_kw(item.get("keyword", ""))
        if k not in model:
            near = [o for o in model if k and (k in o or o in k)][:3]
            errors.append(f"assign: '{item.get('keyword')}' is not in the map"
                          + (f" (did you mean {near}?)" if near else " (use 'add' for new keywords)"))
            continue
        set_assignment(model[k], item, f"assign '{item['keyword']}'")

    added = []
    for item in ch.get("add", []):
        k = c.norm_kw(item.get("keyword", ""))
        if not k:
            errors.append("add: an item has no keyword")
            continue
        if k in model:
            errors.append(f"add: '{item['keyword']}' is already in the map (use 'assign')")
            continue
        if item.get("service_line") and cfg.get("service_lines") and item["service_line"] not in cfg["service_lines"]:
            errors.append(f"add '{item['keyword']}': service_line '{item['service_line']}' not in {cfg['service_lines']}")
        d = {"Keyword": item["keyword"], "Volume": item.get("volume"), "Difficulty": item.get("difficulty"),
             "Service line": item.get("service_line"), "Intent": item.get("intent"),
             "Current rank": "unknown", "Best competitor": "-", "_row": None}
        set_assignment(d, item, f"add '{item['keyword']}'")
        model[k] = d
        order.append(k)
        added.append(k)

    for item in ch.get("exclude", []):
        k = c.norm_kw(item.get("keyword", ""))
        if k not in model:
            errors.append(f"exclude: '{item.get('keyword')}' is not in the map")
            continue
        model[k].update({"Status": "Excluded", "Role": None, "Target page": None,
                         "Action": item.get("reason") or model[k].get("Action")})

    # derive page facts, statuses, types and priorities
    by_page = defaultdict(list)
    for k in order:
        d = model[k]
        if d.get("Status") == "Excluded":
            continue
        if not d.get("Target page"):
            d["Status"], d["Role"] = "Unmapped", None
            continue
        by_page[d["Target page"]].append(d)
    pages = {}
    for url, ds in by_page.items():
        pdef = page_defs.get(url, {})
        is_new = url not in existing_pages
        if is_new and url not in page_defs:
            errors.append(f"page '{url}' is new: add it under 'pages' with a type ({'/'.join(c.PAGE_TYPES)})")
        exists = bool(pdef.get("exists", page_live.get(url, False)))
        ptype = pdef.get("type") or next((d.get("Page type") for d in ds if d.get("Page type")), None)
        lines = Counter(d.get("Service line") or "" for d in ds)
        pg = {"url": url, "exists": exists, "type": ptype, "line": lines.most_common(1)[0][0],
              "volume": sum(c.as_int(d.get("Volume")) or 0 for d in ds), "n": len(ds),
              "primary": [d["Keyword"] for d in ds if d.get("Role") == "Primary"]}
        if "priority" in pdef:
            pg["priority"] = pdef["priority"]
        elif not exists:
            pg["priority"] = priority_for(pg, cfg) or next((d.get("Priority") for d in ds if d.get("Priority")), None)
        else:
            pg["priority"] = Counter(d.get("Priority") for d in ds if d.get("Priority")).most_common(1)[0][0] \
                if any(d.get("Priority") for d in ds) else None
        if len(pg["primary"]) != 1:
            errors.append(f"page '{url}' has {len(pg['primary'])} Primary keywords {pg['primary']} (needs exactly 1)")
        if not ptype:
            (errors if is_new else warns).append(f"page '{url}' has no Page type")
        if pg["volume"] < cfg["min_volume"]:
            warns.append(f"page '{url}' totals {pg['volume']}/mo, under the {cfg['min_volume']}/mo floor")
        cluster = pdef.get("cluster") or next((d.get("Cluster") for d in ds if d.get("Cluster")), None)
        for d in ds:
            d["Page exists"] = "Yes" if exists else "No"
            d["Status"] = "Mapped to page" if exists else "No page yet"
            d["Page type"] = ptype
            d["Priority"] = pg["priority"]
            d["Cluster volume"] = pg["volume"]
            if cluster:
                d["Cluster"] = cluster
        pages[url] = pg

    # report
    print(f"{len(model)} keywords, {len(pages)} pages, {len(added)} added, "
          f"{sum(1 for d in model.values() if d.get('Status') == 'Unmapped')} unmapped, "
          f"{sum(1 for d in model.values() if d.get('Status') == 'Excluded')} excluded")
    for pg in sorted(pages.values(), key=lambda p: (p["priority"] or 9, p["exists"], -p["volume"])):
        print(f"  P{pg['priority'] or '?'} {'live ' if pg['exists'] else 'BUILD'} {pg['volume']:>6}/mo "
              f"{pg['n']:>3} kw  {(pg['type'] or '?'):<8} {pg['url']:<50} primary: {', '.join(pg['primary']) or '-'}")
    for w in warns:
        print(f"WARNING: {w}")
    if errors:
        print(f"\n{len(errors)} error(s); nothing written:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    if a.check:
        print("\nCheck passed. Run again without --check to write.")
        return

    # write
    b = c.backup(path)
    for k in order:
        d = model[k]
        if d["_row"] is None:
            ws.append([None] * head_len)
            d["_row"] = ws.max_row
        for std, i in idx.items():
            if std in d:
                ws.cell(d["_row"], i + 1, d[std])
    last = ws.cell(1, head_len).column_letter
    ws.auto_filter.ref = f"A1:{last}{ws.max_row}"
    rank_sheet = cfg["map"].get("rank_sheet", "Rank tracker")
    if rank_sheet in wb.sheetnames:
        rt = wb[rank_sheet]
        have = {c.norm_kw(r[0]) for r in rt.iter_rows(min_row=2, values_only=True) if r and r[0]}
        for k in order:
            if model[k].get("Status") != "Excluded" and k not in have:
                rt.append([model[k]["Keyword"]])
    if ch.get("triage"):
        tname = cfg["map"].get("triage_sheet", "Draft list triage")
        ts = wb[tname] if tname in wb.sheetnames else wb.create_sheet(tname)
        if ts.max_row == 1 and not ts.cell(1, 1).value:
            ts.append(c.TRIAGE_COLUMNS)
        for t in ch["triage"]:
            if t.get("disposition") not in c.DISPOSITIONS:
                print(f"WARNING: triage '{t.get('keyword')}' disposition should be one of {c.DISPOSITIONS}")
            ts.append([t.get("keyword"), t.get("volume"), t.get("disposition"), t.get("reason")])
    try:
        wb.save(path)
    except PermissionError:
        c.die(f"Could not save {path.name}: it is open in another program. Close it and run again.")
    log = c.data_dir(cfg, root) / "map-changelog.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## {c.TODAY} — {Path(a.changes).name}\n\n{ch.get('note', '')}\n\n"
                f"- assigned {len(ch.get('assign', []))}, added {len(added)}, excluded {len(ch.get('exclude', []))}, "
                f"triaged {len(ch.get('triage', []))}, renamed {len(ch.get('rename', {}))} page URLs\n"
                f"- backup: {b.name}\n")
    print(f"\nWritten. Backup: {b.name}. Logged to {log.name}.")
    print("Next: python plan.py")


if __name__ == "__main__":
    main()
