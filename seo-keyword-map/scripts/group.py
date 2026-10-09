"""Lay out the SERP evidence for grouping keywords into pages.

  python group.py [--page /url/] [--out FILE]

Reads the keyword map and every SERP snapshot, then writes <data_dir>/group-<date>.md:
  - per target page: each keyword's SERP type, page-type mix and closest neighbour
  - flags: mixed SERP types on one page, a Primary whose SERP doesn't fit the page type,
    directory-led keywords, pages without exactly one Primary
  - merge candidates: keywords on different pages whose SERPs match
  - unmapped keywords with their closest mapped neighbour

It makes no decisions. Claude reads the report, applies reference/method.md, and writes
a changes file for apply.py.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

# Shared URLs between two keywords' pooled results (two passes, ~14 URLs each).
STRONG = 6   # at or above: Google treats them as the same query
WEAK = 3     # below: no evidence they belong together

FAMILY = {"SERVICE": "service", "SERVICE+local": "service", "ARTICLE": "article",
          "DIRECTORY/ORG": "directory", "MIXED": "mixed", "MIXED+local": "mixed"}
EXPECT = {"hub": "service", "service": "service", "location": "service", "post": "article"}


def pct(mix, *keys):
    return int(round(100 * sum(mix.get(k, 0) for k in keys)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", help="only report this target page")
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg, root = c.load_config()
    rows = c.read_map(cfg, root)
    serp = c.latest_serp(cfg, root)
    if not serp:
        c.die("No SERP snapshot yet. Run: python serp.py pull, then serp.py classify")
    # Homepages are left out: in a local market the same few firms' homepages rank for
    # every service, which makes unrelated services look like one query.
    U = {k: {u for u in v.get("urls", []) if not u.endswith("/") or u.count("/") > 1}
         for k, v in serp.items()}
    kw_page = {c.norm_kw(r["Keyword"]): r for r in rows}
    live = [r for r in rows if r.get("Status") != "Excluded"]
    missing = [r["Keyword"] for r in live if c.norm_kw(r["Keyword"]) not in serp]

    def best(k, exclude_page=None, same_page=None):
        """Closest other keyword by shared URLs."""
        top = (0, None)
        for o, urls in U.items():
            if o == k or o not in kw_page:
                continue
            pg = kw_page[o].get("Target page")
            if exclude_page and pg == exclude_page:
                continue
            if same_page and pg != same_page:
                continue
            n = len(U[k] & urls)
            if n > top[0]:
                top = (n, o)
        return top

    pages = c.pages_from_rows(rows)
    L = [f"# Grouping evidence — {cfg['domain']} — {c.TODAY}", "",
         f"{len(live)} keywords on {len(pages)} pages. SERP data for {len(live) - len(missing)}.",
         f"Overlap = non-homepage URLs shared by two keywords' pooled top-10s. {STRONG}+ = same query to Google; "
         f"under {WEAK} = no evidence they belong together. Low-volume SERPs rotate, so read the "
         "SERP type first and overlap second (reference/method.md).", ""]
    if missing:
        L += [f"**No SERP data for {len(missing)} keywords** (run `serp.py pull`): " + ", ".join(missing[:40]), ""]

    flags_total = 0
    order = sorted(pages.values(), key=lambda p: (p["line"], p["priority"] or 9, -p["volume"]))
    only = c.resolve_page(a.page, pages) if a.page else None
    if a.page and not only:
        c.die(f"'{a.page}' is not a target page in the map.")
    for pg in order:
        if only and pg["url"] != only:
            continue
        ks = sorted(pg["keywords"], key=lambda r: -(r.get("Volume") or 0))
        fams, flags = {}, []
        lines = []
        for r in ks:
            k = c.norm_kw(r["Keyword"])
            s = serp.get(k)
            if not s:
                lines.append(f"| {r['Keyword']} | {r.get('Volume') or ''} | {r.get('Role') or ''} | no data | | | | |")
                continue
            fam = FAMILY.get(s["type"], "mixed")
            fams[fam] = fams.get(fam, 0) + 1
            n_in, o_in = best(k, same_page=pg["url"])
            n_out, o_out = best(k, exclude_page=pg["url"])
            near_out = f"{o_out} ({kw_page[o_out]['Target page']}) {n_out}" if o_out and n_out >= WEAK else ""
            m = s.get("mix", {})
            lines.append(f"| {r['Keyword']} | {r.get('Volume') or ''} | {r.get('Role') or ''} | {s['type']} | "
                         f"{pct(m, 'svc', 'home')}/{pct(m, 'art', 'soc')}/{pct(m, 'dir', 'org')} | "
                         f"{n_in if o_in else ''} | {near_out} | {','.join(map(str, s.get('pg') or []))} |")
            if fam == "directory":
                flags.append(f"'{r['Keyword']}' is directory/association-led")
            if r.get("Role") == "Primary" and pg["type"] in EXPECT and fam not in (EXPECT[pg['type']], "mixed"):
                flags.append(f"Primary '{r['Keyword']}' has a {s['type']} SERP but the page is a {pg['type']} page")
        if "service" in fams and "article" in fams:
            flags.append(f"mixed SERP types on one page: {fams}")
        prim = sum(1 for r in ks if r.get("Role") == "Primary")
        if prim != 1:
            flags.append(f"{prim} Primary keywords (needs exactly 1)")
        if not pg["type"]:
            flags.append("no Page type set")
        if pg["volume"] < cfg["min_volume"]:
            flags.append(f"page volume {pg['volume']} is under the {cfg['min_volume']}/mo floor")
        flags_total += len(flags)
        state = "live" if pg["exists"] else "to build"
        L += [f"## {pg['url']} — {state}, {pg['type'] or 'type?'}, P{pg['priority'] or '?'}, "
              f"{pg['volume']}/mo, {len(ks)} kw", ""]
        if flags:
            L += [f"- ⚑ {f}" for f in flags] + [""]
        L += ["| keyword | vol | role | SERP type | svc/art/dir % | overlap in page | closest elsewhere | our rank |",
              "|---|---|---|---|---|---|---|---|"] + lines + [""]

    # merge candidates across pages
    merges, seen = [], set()
    ks = [k for k in U if k in kw_page and kw_page[k].get("Target page")]
    for i, k1 in enumerate(ks):
        for k2 in ks[i + 1:]:
            p1, p2 = kw_page[k1]["Target page"], kw_page[k2]["Target page"]
            if p1 == p2 or (p1, p2) in seen:
                continue
            n = len(U[k1] & U[k2])
            if n >= STRONG and FAMILY.get(serp[k1]["type"]) == FAMILY.get(serp[k2]["type"]):
                merges.append((n, k1, p1, k2, p2))
    if merges:
        L += ["## Merge candidates (same SERP, different pages)", "",
              "| shared | keyword | page | keyword | page |", "|---|---|---|---|---|"]
        L += [f"| {n} | {a1} | {b1} | {a2} | {b2} |" for n, a1, b1, a2, b2 in sorted(merges, reverse=True)[:60]]
        L.append("")

    unm = [r for r in rows if r.get("Status") != "Excluded"
           and (r.get("Status") == "Unmapped" or not r.get("Target page"))]
    if unm:
        L += ["## Unmapped keywords", "", "| keyword | vol | SERP type | closest mapped keyword (page) | shared |",
              "|---|---|---|---|---|"]
        for r in sorted(unm, key=lambda r: -(r.get("Volume") or 0)):
            k = c.norm_kw(r["Keyword"])
            if k not in serp:
                L.append(f"| {r['Keyword']} | {r.get('Volume') or ''} | no data | | |")
                continue
            n, o = best(k)
            L.append(f"| {r['Keyword']} | {r.get('Volume') or ''} | {serp[k]['type']} | "
                     f"{o + ' (' + str(kw_page[o].get('Target page')) + ')' if o and n >= WEAK else 'none: candidate new page'} | {n} |")
        L.append("")

    out = Path(a.out) if a.out else c.data_dir(cfg, root) / f"group-{c.TODAY}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {out}: {len(order)} pages, {flags_total} flags, {len(merges)} merge candidates, "
          f"{len(unm)} unmapped, {len(missing)} keywords without SERP data.")
    print("Next: read it, apply reference/method.md, write changes.json, then: python apply.py changes.json --check")


if __name__ == "__main__":
    main()
