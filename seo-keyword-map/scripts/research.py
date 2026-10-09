"""Find keyword candidates and collect them in one file for triage.

  python research.py grid [--services "a,b"] [--places "x,y"]     Google Ads volume for service x place
  python research.py suggest SEED [SEED ...] [--limit 100]        phrases containing each seed (Labs)
  python research.py competitors [DOMAIN ...] [--limit 300]       what competitors rank for (Labs)
  python research.py harvest                                      related searches + People also ask, free
  python research.py volume [--missing | KW ...]                  Google Ads volume for candidates
  python research.py import FILE [--source semrush]               a CSV/XLSX export from another tool
  python research.py review [--all]                               write the triage sheet for Claude

Everything lands in <data_dir>/research/candidates.csv (one row per keyword, sources
merged). `review` writes research/review-<date>.md: candidates not yet in the map or
the triage sheet, with flags (jobs, competitor brand, out of area, under the volume
floor, question). Claude triages them with reference/research.md and writes a changes
file for apply.py.

Costs (Oct 2026): Ads volume ~$0.09 per call of up to 1,000 keywords, whatever the
count, so batch. Labs ~$0.01 per call plus $0.0001 per keyword returned.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

FIELDS = ["keyword", "volume", "kd", "cpc", "source", "seed", "first_seen"]
ADS_CALL = 0.09        # observed per search_volume call, regardless of keyword count
ADS_BATCH = 1000       # Google Ads accepts at most 1,000 keywords per task
LABS_CALL, LABS_ITEM = 0.01, 0.0001
QUESTION = re.compile(r"^(how|what|why|when|where|which|who|is|are|can|do|does|should|will)\b|\bvs\b|\bversus\b")


def store(cfg, root) -> Path:
    d = c.data_dir(cfg, root) / "research"
    d.mkdir(parents=True, exist_ok=True)
    return d / "candidates.csv"


def load(cfg, root) -> dict:
    f = store(cfg, root)
    if not f.exists():
        return {}
    with f.open(encoding="utf-8", newline="") as fh:
        return {c.norm_kw(r["keyword"]): r for r in csv.DictReader(fh)}


def save(cfg, root, rows: dict):
    with store(cfg, root).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in sorted(rows.values(), key=lambda r: -(c.as_int(r.get("volume")) or 0)):
            w.writerow({k: r.get(k, "") for k in FIELDS})


def merge(cfg, root, new: list[dict], source: str) -> int:
    rows = load(cfg, root)
    added = 0
    for n in new:
        k = c.norm_kw(n["keyword"])
        if not k:
            continue
        r = rows.get(k)
        if not r:
            rows[k] = {"keyword": k, "volume": n.get("volume") if n.get("volume") is not None else "",
                       "kd": n.get("kd") if n.get("kd") is not None else "", "cpc": n.get("cpc") or "",
                       "source": source, "seed": n.get("seed", ""), "first_seen": c.TODAY}
            added += 1
            continue
        if n.get("volume") is not None and (c.as_int(r.get("volume")) is None):
            r["volume"] = n["volume"]
        for f in ("kd", "cpc"):
            if n.get(f) not in (None, "") and r.get(f) in (None, ""):
                r[f] = n[f]
        if source not in r["source"].split("+"):
            r["source"] += "+" + source
    save(cfg, root, rows)
    return added


def market(cfg):
    return {"location_name": cfg["market"]["country"], "language_code": cfg["market"]["language_code"]}


def ads_ok(k: str) -> bool:
    """Google Ads rejects long phrases and some symbols; one bad phrase fails the whole call."""
    return len(k) <= 80 and len(k.split()) <= 10 and not re.search(r"[,.!@%^*()={};~`<>?\\|\[\]\"]", k)


def ads_volume(api, cfg, kws: list[str]) -> list[dict]:
    """Volumes for the keywords Google Ads answered. A keyword missing from the result was not checked."""
    kws = [k for k in dict.fromkeys(c.norm_kw(k) for k in kws) if k]
    skipped = [k for k in kws if not ads_ok(k)]
    kws = [k for k in kws if ads_ok(k)]
    if skipped:
        print(f"  skipped {len(skipped)} phrases Google Ads won't accept (punctuation, over 10 words or 80 chars): {skipped[:4]}")
    out = []
    for s in range(0, len(kws), ADS_BATCH):
        chunk = kws[s:s + ADS_BATCH]
        res = None
        for _ in range(12):  # each retry drops one phrase Ads named as invalid, or retries an empty result
            d = api.post("keywords_data/google_ads/search_volume/live", [{"keywords": chunk, **market(cfg)}])
            t = d["tasks"][0]
            if t["status_code"] == 20000 and t.get("result"):
                res = t["result"]
                break
            bad = re.search(r"invalid characters or symbols: '([^']+)'", t.get("status_message", ""))
            if bad and bad.group(1) in chunk:
                print(f"  Ads rejected '{bad.group(1)}'; dropped it and retried")
                chunk = [k for k in chunk if k != bad.group(1)]
                continue
            if t["status_code"] != 20000:
                print(f"  Ads error {t['status_code']}: {t['status_message']} ({len(chunk)} keywords left unchecked)")
                break
        for r in res or []:
            out.append({"keyword": r["keyword"], "volume": r.get("search_volume"), "cpc": r.get("cpc")})
    return out


def labs_items(d) -> list:
    t = d["tasks"][0]
    if t["status_code"] != 20000:
        print(f"  {t['status_code']} {t['status_message']}")
        return []
    return ((t.get("result") or [{}])[0] or {}).get("items") or []


# ---------------------------------------------------------------- commands

def cmd_grid(a, cfg, root):
    rcfg = cfg.get("research", {})
    services = [s.strip() for s in (a.services.split(",") if a.services else rcfg.get("services", [])) if s.strip()]
    places = [p.strip() for p in (a.places.split(",") if a.places else rcfg.get("places", [])) if p.strip()]
    if not services or not places:
        c.die("No services or places. Pass --services/--places or set research.services/places in seo-project.json.")
    kws = [f"{s} {p}" for s in services for p in places]
    api = c.DataForSEO(cfg, root, a.max_cost, label=f"grid {len(kws)}")
    api.preflight(math.ceil(len(kws) / ADS_BATCH) * ADS_CALL)
    res = ads_volume(api, cfg, kws)
    for r in res:
        r["seed"] = "grid"
    hits = [r for r in res if (r["volume"] or 0) >= cfg["min_volume"]]
    print(f"{len(kws)} combinations checked, {len(hits)} at or over {cfg['min_volume']}/mo, "
          f"{merge(cfg, root, hits, 'grid')} new candidates.")
    for r in sorted(hits, key=lambda r: -r["volume"])[:30]:
        print(f"  {r['volume']:>6}  {r['keyword']}")
    api.done()


def cmd_suggest(a, cfg, root):
    api = c.DataForSEO(cfg, root, a.max_cost, label=f"suggest {len(a.seeds)}")
    api.preflight(len(a.seeds) * (LABS_CALL + LABS_ITEM * a.limit))
    new = []
    for seed in a.seeds:
        d = api.post("dataforseo_labs/google/keyword_suggestions/live",
                     [{"keyword": seed, **market(cfg), "limit": a.limit, "include_seed_keyword": True}])
        items = labs_items(d)
        print(f"  {seed}: {len(items)}")
        for i in items:
            ki = i.get("keyword_info") or {}
            new.append({"keyword": i["keyword"], "volume": ki.get("search_volume"), "cpc": ki.get("cpc"),
                        "kd": (i.get("keyword_properties") or {}).get("keyword_difficulty"), "seed": seed})
    print(f"{len(new)} suggestions, {merge(cfg, root, new, 'suggest')} new candidates.")
    api.done()


def cmd_competitors(a, cfg, root):
    doms = a.domains or cfg.get("competitors", [])
    if not doms:
        c.die("No competitor domains. Pass them, or set competitors in seo-project.json.")
    api = c.DataForSEO(cfg, root, a.max_cost, label=f"competitors {len(doms)}")
    api.preflight(len(doms) * (LABS_CALL + LABS_ITEM * a.limit))
    new = []
    for dom in doms:
        d = api.post("dataforseo_labs/google/ranked_keywords/live", [{
            "target": dom, **market(cfg), "limit": a.limit,
            "filters": [["ranked_serp_element.serp_item.rank_group", "<=", a.max_rank]],
            "order_by": ["keyword_data.keyword_info.search_volume,desc"]}])
        items = labs_items(d)
        print(f"  {dom}: {len(items)} keywords in the top {a.max_rank}")
        for i in items:
            kd = i.get("keyword_data") or {}
            ki = kd.get("keyword_info") or {}
            se = ((i.get("ranked_serp_element") or {}).get("serp_item") or {})
            new.append({"keyword": kd.get("keyword"), "volume": ki.get("search_volume"), "cpc": ki.get("cpc"),
                        "kd": (kd.get("keyword_properties") or {}).get("keyword_difficulty"),
                        "seed": f"{dom} #{se.get('rank_group')}"})
    print(f"{len(new)} competitor keywords, {merge(cfg, root, new, 'competitor')} new candidates.")
    api.done()


def cmd_harvest(a, cfg, root):
    serp = c.latest_serp(cfg, root)
    if not serp:
        c.die("No SERP snapshot to harvest. Run serp.py pull and classify first.")
    new = []
    for k, s in serp.items():
        for r in s.get("related", []):
            new.append({"keyword": r, "seed": f"related: {k}"})
        if a.paa:  # questions are usually zero-volume; they serve better as FAQ material in plan.py
            for q in s.get("paa", []):
                new.append({"keyword": q, "seed": f"PAA: {k}"})
    n = merge(cfg, root, new, "serp")
    print(f"{len(new)} related searches{' and questions' if a.paa else ''} from {len(serp)} SERPs, {n} new candidates "
          "(no volume yet: run `research.py volume --missing`).")


def cmd_volume(a, cfg, root):
    rows = load(cfg, root)
    kws = a.keywords or [k for k, r in rows.items() if c.as_int(r.get("volume")) is None
                         and r.get("volume") != "0"]
    if a.missing:
        kws = [k for k, r in rows.items() if r.get("volume") in (None, "")]
    if not kws:
        print("Every candidate already has a volume.")
        return
    api = c.DataForSEO(cfg, root, a.max_cost, label=f"volume {len(kws)}")
    api.preflight(math.ceil(len(kws) / ADS_BATCH) * ADS_CALL)
    res = ads_volume(api, cfg, kws)
    got = {c.norm_kw(r["keyword"]): r for r in res}
    for k in kws:  # phrases Ads refuses can't be checked; 0 stops them being offered again
        if not ads_ok(c.norm_kw(k)) and c.norm_kw(k) in rows:
            rows[c.norm_kw(k)]["volume"] = 0
    for k, g in got.items():  # 0 = checked, no volume, so it isn't bought again
        r = rows.get(k)
        if r is None:
            continue
        r["volume"] = g["volume"] if g["volume"] is not None else 0
        if g.get("cpc") is not None:
            r["cpc"] = g["cpc"]
    save(cfg, root, rows)
    print(f"Volumes for {len(got)} of {len(kws)} candidates; "
          f"{sum(1 for r in res if (r['volume'] or 0) >= cfg['min_volume'])} at or over {cfg['min_volume']}/mo.")
    api.done()


def cmd_import(a, cfg, root):
    f = Path(a.file)
    if not f.exists():
        c.die(f"File not found: {f}")
    if f.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
        rows = []
        for ws in wb.worksheets:
            rows += [list(r) for r in ws.iter_rows(values_only=True)]
    else:
        with f.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
    # find the header row: the first row with a cell that says "keyword"
    hi = next((i for i, r in enumerate(rows) if any(str(x or "").strip().lower() in ("keyword", "keywords", "query", "top queries") for x in r)), None)
    if hi is None:
        c.die("No header row with a 'Keyword' (or 'Query') column found.")
    head = [str(x or "").strip().lower() for x in rows[hi]]

    def find(*names):
        return next((head.index(n) for n in names if n in head), None)
    ki = find("keyword", "keywords", "query", "top queries")
    vi = find("volume", "search volume", "avg. monthly searches", "impressions")
    di = find("keyword difficulty", "kd", "difficulty", "kd %")
    new = []
    for r in rows[hi + 1:]:
        if ki < len(r) and r[ki] and str(r[ki]).strip().lower() not in ("keyword", "keywords"):
            new.append({"keyword": str(r[ki]), "volume": c.as_int(r[vi]) if vi is not None and vi < len(r) else None,
                        "kd": c.as_int(r[di]) if di is not None and di < len(r) else None, "seed": f.name})
    print(f"{len(new)} rows read from {f.name}; {merge(cfg, root, new, a.source)} new candidates.")
    if vi is not None and head[vi] == "impressions":
        print("  Note: the volume column is Search Console impressions, not search volume. "
              "Run `research.py volume` on the ones worth keeping.")


def flags_for(k: str, vol, cfg, in_map, triaged) -> list[str]:
    f = []
    if k in in_map:
        f.append("in map")
    if k in triaged:
        f.append(f"triaged: {triaged[k]}")
    for p in cfg.get("exclude_patterns", []):
        if re.search(p, k):
            f.append("excluded pattern")
            break
    brands = [r"\b" + re.escape(b.lower()) + r"\b" for b in cfg.get("competitor_brands", [])]
    for b in brands + cfg.get("brand_patterns", []):
        if re.search(b, k):
            f.append("brand name")
            break
    for p in cfg.get("out_of_area_patterns", []):
        if re.search(p, k):
            f.append("out of area")
            break
    v = c.as_int(vol)
    if v is None:
        f.append("no volume yet")
    elif v < cfg["min_volume"]:
        f.append(f"under {cfg['min_volume']}/mo")
    if QUESTION.search(k):
        f.append("question")
    return f


def cmd_review(a, cfg, root):
    rows = load(cfg, root)
    if not rows:
        c.die("No candidates yet. Run grid, suggest, competitors, harvest or import first.")
    in_map = {c.norm_kw(r["Keyword"]) for r in c.read_map(cfg, root)}
    triaged = {}
    try:
        wb, _ = c.open_map(cfg, root, read_only=True)
        tname = cfg["map"].get("triage_sheet", "Draft list triage")
        if tname in wb.sheetnames:
            for r in wb[tname].iter_rows(min_row=2, values_only=True):
                if r and r[0]:
                    triaged[c.norm_kw(r[0])] = r[2] if len(r) > 2 else "?"
        wb.close()
    except SystemExit:
        pass
    out, auto, novol = [], 0, 0
    for k, r in rows.items():
        fl = flags_for(k, r.get("volume"), cfg, in_map, triaged)
        if not a.all and ("in map" in fl or any(x.startswith("triaged") for x in fl)):
            continue
        if not a.all and "no volume yet" in fl:
            novol += 1
            continue
        if not a.all and any(x.startswith("under ") for x in fl):
            auto += 1
            continue
        out.append((c.as_int(r.get("volume")) or 0, k, r, fl))
    out.sort(key=lambda x: (-x[0], x[1]))
    path = store(cfg, root).with_name(f"review-{c.TODAY}.md")
    L = [f"# Keyword candidates to triage: {cfg['domain']}, {c.TODAY}", "",
         f"{len(out)} candidates not yet in the map or the triage sheet. "
         f"Left out: {auto} under the {cfg['min_volume']}/mo floor, {novol} with no volume yet "
         "(run `research.py volume --missing` first). Use --all to list everything.",
         "Triage each with reference/research.md: add to the map, fold into a kept term, or remove with a reason.", "",
         "| volume | keyword | KD | CPC | source | seed | flags |", "|---|---|---|---|---|---|---|"]
    L += [f"| {v or ''} | {k} | {r.get('kd') or ''} | {cpc(r.get('cpc'))} | {r.get('source')} | "
          f"{(r.get('seed') or '')[:40]} | {', '.join(fl)} |" for v, k, r, fl in out]
    path.write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {path}: {len(out)} candidates to triage; left out {auto} under the floor "
          f"and {novol} without volume.")
    if novol:
        print(f"Next: python research.py volume --missing  (about ${math.ceil(novol / ADS_BATCH) * ADS_CALL:.2f})")


def cpc(v) -> str:
    try:
        return f"{float(v):.2f}"
    except (TypeError, ValueError):
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("grid"); p.add_argument("--services"); p.add_argument("--places"); p.set_defaults(fn=cmd_grid)
    p = sp.add_parser("suggest"); p.add_argument("seeds", nargs="+"); p.add_argument("--limit", type=int, default=100)
    p.set_defaults(fn=cmd_suggest)
    p = sp.add_parser("competitors"); p.add_argument("domains", nargs="*"); p.add_argument("--limit", type=int, default=300)
    p.add_argument("--max-rank", type=int, default=30, help="ignore positions below this (default 30)")
    p.set_defaults(fn=cmd_competitors)
    p = sp.add_parser("harvest"); p.add_argument("--paa", action="store_true", help="also People also ask questions")
    p.set_defaults(fn=cmd_harvest)
    p = sp.add_parser("volume"); p.add_argument("keywords", nargs="*"); p.add_argument("--missing", action="store_true")
    p.set_defaults(fn=cmd_volume)
    p = sp.add_parser("import"); p.add_argument("file"); p.add_argument("--source", default="import")
    p.set_defaults(fn=cmd_import)
    p = sp.add_parser("review"); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_review)
    for name in ("grid", "suggest", "competitors", "volume"):
        sp.choices[name].add_argument("--max-cost", type=float)
    a = ap.parse_args()
    if not hasattr(a, "max_cost"):
        a.max_cost = None
    cfg, root = c.load_config()
    a.fn(a, cfg, root)


if __name__ == "__main__":
    main()
