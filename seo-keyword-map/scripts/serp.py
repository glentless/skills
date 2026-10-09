"""Pull Google results for keywords and classify what kind of page ranks.

  python serp.py pull [--keywords all|missing|stale] [--passes 2] [--gap-minutes 15]
                      [--max-cost 1.0] [--only "kw1,kw2"]
  python serp.py classify [--date YYYY-MM-DD]

pull     Queues one task per keyword per pass on DataForSEO's standard queue (the
         cheap one, about $0.001 per keyword per pass at depth 20), waits, and
         saves a trimmed copy of each result under <data_dir>/serp/raw/<date>/.
classify Turns the raw results into <data_dir>/serp/<date>.json: for every keyword,
         the page-type mix, SERP type, features, related searches, People also ask,
         the project's own positions, and the pooled URLs of all passes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

DEPTH = 20            # depth counts every SERP block, so 10 leaves only ~7 organic results
COST_PER_TASK = 0.00105  # observed standard-queue price for depth 20, Oct 2026
STALE_DAYS = 120      # local SERPs drift; re-pull a keyword after about four months


# ---------------------------------------------------------------- pull

def location_for(kw: str, cfg: dict) -> str:
    """A keyword naming a place with its own SERP location is checked from there."""
    k = kw.lower()
    for place, loc in sorted(cfg.get("places", {}).items(), key=lambda x: -len(x[0])):
        if loc and re.search(r"\b" + re.escape(place) + r"\b", k):
            return loc
    return cfg["market"]["default_serp_location"]


def trim(task: dict) -> dict:
    """Keep what classify needs; full results are ~50 KB each."""
    r = (task.get("result") or [{}])[0]
    items = r.get("items") or []
    keep = {"keyword": r.get("keyword"), "location_code": r.get("location_code"),
            "datetime": r.get("datetime"), "organic": [], "features": [],
            "related": [], "paa": [], "local_pack": []}
    for i in items:
        t = i.get("type")
        if t == "organic":
            keep["organic"].append({"rank": i.get("rank_group"), "url": i.get("url"),
                                    "domain": i.get("domain"), "title": i.get("title")})
        else:
            keep["features"].append(t)
        if t == "related_searches":
            keep["related"] += [x for x in (i.get("items") or []) if isinstance(x, str)]
        if t == "people_also_ask":
            keep["paa"] += [x.get("title") for x in (i.get("items") or []) if x.get("title")]
        if t == "local_pack":
            keep["local_pack"].append(i.get("domain") or i.get("title"))
    return keep


slug = c.serp_file


def run_pass(api, cfg, kws, out: Path, depth: int = DEPTH, device: str | None = None, fast: bool = False):
    out.mkdir(parents=True, exist_ok=True)
    m = cfg["market"]
    tasks = [{"keyword": k, "location_name": location_for(k, cfg), "language_code": m["language_code"],
              "device": device or m.get("device", "desktop"), "depth": depth, "tag": k,
              "priority": 2 if fast else 1} for k in kws]  # 2 = high-priority queue, about twice the price
    ids = {}
    for s in range(0, len(tasks), 100):  # task_post takes at most 100 tasks per call
        d = api.post("serp/google/organic/task_post", tasks[s:s + 100])
        for t in d["tasks"]:
            if t["status_code"] == 20100:
                ids[t["id"]] = t["data"]["tag"]
            else:
                print(f"  not queued: {t['data'].get('keyword')}: {t['status_message']}")
    print(f"  queued {len(ids)} tasks; waiting for results (usually 1-5 minutes)")
    waited = 0
    while ids and waited < 3600:  # the standard queue normally finishes well inside an hour
        time.sleep(20)
        waited += 20
        for tid in list(ids):
            d = api.get(f"serp/google/organic/task_get/advanced/{tid}")
            t = d["tasks"][0]
            if t["status_code"] == 20000:
                (out / f"{slug(ids[tid])}.json").write_text(json.dumps(trim(t)), encoding="utf-8")
                del ids[tid]
            elif t["status_code"] not in (40601, 40602):  # 4060x = still in the queue
                print(f"  failed: {ids[tid]}: {t['status_message']}")
                del ids[tid]
        print(f"  {len(list(out.glob('*.json')))} saved, {len(ids)} pending")
    if ids:
        print(f"  gave up on {len(ids)} tasks after an hour; re-run pull --keywords missing")


def cmd_pull(a):
    cfg, root = c.load_config()
    rows = c.read_map(cfg, root)
    have = c.latest_serp(cfg, root)
    kws = sorted({c.norm_kw(r["Keyword"]) for r in rows if r.get("Status") != "Excluded"})
    if a.only:
        kws = [c.norm_kw(k) for k in a.only.split(",") if k.strip()]
    elif a.keywords == "missing":
        kws = [k for k in kws if k not in have]
    elif a.keywords == "stale":
        cutoff = (c.dt.date.today() - c.dt.timedelta(days=STALE_DAYS)).isoformat()
        kws = [k for k in kws if k not in have or have[k].get("_snapshot", "")[:10] < cutoff]
    if not kws:
        print("Nothing to pull: every keyword already has SERP data.")
        return
    api = c.DataForSEO(cfg, root, a.max_cost, label=f"serp pull {len(kws)} kw")
    api.preflight(len(kws) * a.passes * COST_PER_TASK * (2 if a.fast else 1))
    base = c.snapshot_dir(cfg, root) / "raw" / c.TODAY
    for p in range(1, a.passes + 1):
        if p > 1 and a.gap_minutes:
            print(f"Waiting {a.gap_minutes} min before pass {p}, so the passes sample Google independently")
            time.sleep(a.gap_minutes * 60)
        print(f"Pass {p}: {len(kws)} keywords")
        run_pass(api, cfg, kws, base / f"pass{p}", fast=a.fast)
    api.done()
    print(f"Next: python {Path(__file__).name} classify")


# ---------------------------------------------------------------- classify

def load_classes(cfg) -> dict:
    d = json.loads((c.SKILL_DIR / "assets" / "domain-classes.json").read_text(encoding="utf-8"))
    extra = cfg.get("classify", {})
    d["directory"] += extra.get("extra_directory_patterns", [])
    d["org"] += extra.get("extra_org_patterns", [])
    return {k: re.compile("|".join(v), re.I) for k, v in d.items() if isinstance(v, list) and v}


def norm_url(u: str) -> str:
    p = urlparse(u or "")
    return p.netloc.lower().removeprefix("www.") + (p.path.rstrip("/") or "/")


def url_kind(u: str, R: dict) -> str:
    """dir, org, soc, home, art or svc. Order matters: a directory's blog is still a directory."""
    if R["directory"].search(u):
        return "dir"
    if R["org"].search(u):
        return "org"
    if R["social"].search(u):
        return "soc"
    path = u.split("/", 1)[1] if "/" in u else ""
    if not path:
        return "home"
    if R["article"].search("/" + path):
        return "art"
    return "svc"


def serp_type(mix: dict, local: bool) -> str:
    """Thresholds set on a 194-keyword local-services run; see reference/method.md."""
    biz = mix.get("svc", 0) + mix.get("home", 0)
    info = mix.get("art", 0) + mix.get("soc", 0)
    if mix.get("dir", 0) + mix.get("org", 0) >= 0.45:
        return "DIRECTORY/ORG"
    if biz >= 0.5:
        return "SERVICE+local" if local else "SERVICE"
    if info >= 0.5:
        return "ARTICLE"
    return "MIXED+local" if local else "MIXED"


def cmd_classify(a):
    cfg, root = c.load_config()
    date = a.date or c.TODAY
    raw = c.snapshot_dir(cfg, root) / "raw" / date
    if not raw.exists():
        c.die(f"No raw results for {date} in {raw}. Run pull first.")
    R = load_classes(cfg)
    vols = {c.norm_kw(r["Keyword"]): r.get("Volume") for r in c.read_map(cfg, root)}
    dom = cfg["domain"].lower().removeprefix("www.")
    out = {}
    passes = sorted(p for p in raw.iterdir() if p.is_dir())
    for pdir in passes:
        for f in pdir.glob("*.json"):
            t = json.loads(f.read_text(encoding="utf-8"))
            k = c.norm_kw(t["keyword"])
            o = out.setdefault(k, {"vol": vols.get(k), "urls": [], "features": set(), "related": set(),
                                   "paa": set(), "pg": [], "passes": 0})
            o["passes"] += 1
            for i in t["organic"][:10]:
                u = norm_url(i["url"])
                if u not in o["urls"]:
                    o["urls"].append(u)
                if dom in (i.get("domain") or ""):
                    o["pg"].append(i["rank"])
            o["features"] |= set(t["features"])
            o["related"] |= set(t["related"])
            o["paa"] |= set(t["paa"])
    for k, o in out.items():
        n = len(o["urls"]) or 1
        cnt = {}
        for u in o["urls"]:
            kind = url_kind(u, R)
            cnt[kind] = cnt.get(kind, 0) + 1
        o["mix"] = {x: round(y / n, 2) for x, y in cnt.items()}
        o["type"] = serp_type(o["mix"], "local_pack" in o["features"])
        o["pg"] = sorted(set(o["pg"]))
        for s in ("features", "related", "paa"):
            o[s] = sorted(o[s])
    snap = {"_note": f"Google top-10 organic via DataForSEO, {len(passes)} pass(es) pooled per keyword. "
                     "type = which kind of page ranks; mix = share of results by kind "
                     "(svc, home, art, soc, dir, org); pg = this site's positions seen.",
            "date": date, "domain": cfg["domain"], "keywords": out}
    path = c.snapshot_dir(cfg, root) / f"{date}.json"
    path.write_text(json.dumps(snap, indent=1, ensure_ascii=False), encoding="utf-8")
    types = {}
    for o in out.values():
        types[o["type"]] = types.get(o["type"], 0) + 1
    ranked = sum(1 for o in out.values() if o["pg"])
    print(f"Saved {path} ({len(out)} keywords, {len(passes)} pass(es)).")
    print("SERP types: " + ", ".join(f"{t} {n}" for t, n in sorted(types.items(), key=lambda x: -x[1])))
    print(f"{cfg['domain']} appears in the top 10 for {ranked} of them.")
    print("Next: python group.py")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("pull")
    p.add_argument("--keywords", choices=["all", "missing", "stale"], default="missing")
    p.add_argument("--only", help="comma-separated keywords instead of the map")
    p.add_argument("--passes", type=int, default=2)
    p.add_argument("--gap-minutes", type=int, default=15)
    p.add_argument("--max-cost", type=float)
    p.add_argument("--fast", action="store_true", help="high-priority queue: minutes instead of up to an hour, ~2x the price")
    p.set_defaults(fn=cmd_pull)
    p = sp.add_parser("classify")
    p.add_argument("--date")
    p.set_defaults(fn=cmd_classify)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
