"""List the pages to build next, or write a writing brief for one page.

  python plan.py [--count N] [--all]
  python plan.py --brief /url/

List: for each page to build, priority, type, monthly searches, the Primary / Secondary
/ Support keywords, the SERP type of the Primary, People also ask questions (FAQ
material), and the existing page to copy as a template. Writes
<data_dir>/plan-<date>.md. --count defaults to batch_size in seo-project.json.

--brief: writes <briefs_dir>/<slug>.md in the shape the seo-writing skill's `write`
command consumes, plus the project's page requirements (page_requirements in
seo-project.json) and, for service and location pages, the live page whose sections to
copy. That is how a service page gets written with a blog-writing skill: the brief
carries what is different about the page.

The template suggestion scores every live page by shared keyword words (place names
and filler removed) with a bonus for the same page type, unless a `^regex` rule in
copy_from matches the URL. It is a suggestion: check it.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

STOP = {"a", "an", "the", "of", "for", "in", "to", "and", "or", "my", "your", "is", "how", "what",
        "does", "do", "much", "near", "me", "vs", "services", "service", "company", "companies"}
SAME_TYPE_BONUS = 0.15  # enough to break ties toward the same layout, not to beat a clear topic match


def words(kws, places) -> set:
    out = set()
    for k in kws:
        t = k.lower()
        for p in places:
            t = re.sub(r"\b" + re.escape(p) + r"\b", " ", t)
        out |= {w.rstrip("s") for w in re.findall(r"[a-z]+", t) if w not in STOP and len(w) > 2}
    return out


def flat(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", s.lower().replace("'", "").replace("’", "")))


def primary_line(prim: str, titles: list) -> str:
    """The brief's primary-keyword instruction. A phrase no page-one title uses is how people
    search, not how pages are titled; forcing it into an H1 reads badly, so the brief says so."""
    rule = f"- Primary: **{prim}**. In the title tag, H1, first 100 words and meta description."
    if not titles:
        return rule
    exact = [t for t in titles if re.search(rf"\b{re.escape(flat(prim))}\b", flat(t))]
    if exact:
        return rule[:-1] + f" ({len(exact)} of {len(titles)} page-one titles use it)."
    want = words([prim], [])
    near = sorted((t for t in titles if want & words([t], [])), key=lambda t: -len(want & words([t], [])))[:3]
    return (f"- Primary: **{prim}**. None of the {len(titles)} page-one titles uses this exact phrase: it is how "
            "people search, not how pages are titled. In the title tag and H1, use a natural form that keeps "
            "its main words" + (" (ranking titles: " + " · ".join(f'"{t}"' for t in near) + ")" if near else "")
            + ". Put the exact phrase once in the meta description or body where a sentence carries it, and "
            "the phrase or its natural form in the first 100 words.")


class Planner:
    def __init__(self):
        self.cfg, self.root = c.load_config()
        self.rows = c.read_map(self.cfg, self.root)
        self.pages = c.pages_from_rows(self.rows)
        self.serp = c.latest_serp(self.cfg, self.root)
        self.places = list(self.cfg.get("places", {})) + self.cfg.get("research", {}).get("places", [])
        self.live = [p for p in self.pages.values() if p["exists"]]
        self.lw = {p["url"]: words([r["Keyword"] for r in p["keywords"]], self.places) for p in self.live}

    def ordered(self, p):
        return sorted(p["keywords"], key=lambda r: ({"Primary": 0, "Secondary": 1}.get(r.get("Role"), 2),
                                                    -(r.get("Volume") or 0)))

    def copy_for(self, p) -> list[str]:
        cf = self.cfg.get("copy_from", {})
        rule = next((u for pat, u in cf.items() if pat.startswith("^") and re.search(pat, p["url"])), None)
        fallback = cf.get(p["type"] or "")
        if rule:  # a project rule ("^/land-surveying-": "/surveying/") beats the word score
            return [rule]
        if p["type"] == "post" and fallback:  # posts share one blog layout whatever the topic
            return [fallback]
        mine = words([r["Keyword"] for r in p["keywords"]], self.places)
        scored = []
        for q in self.live:
            if q["url"] == p["url"] or not self.lw[q["url"]]:
                continue
            j = len(mine & self.lw[q["url"]]) / len(mine | self.lw[q["url"]])
            scored.append((j + (SAME_TYPE_BONUS if q["type"] == p["type"] else 0), q["url"]))
        scored.sort(reverse=True)
        return [u for s, u in scored[:2] if s > SAME_TYPE_BONUS] or ([fallback] if fallback else [])

    def paa(self, kws) -> list[str]:
        qs = []
        for r in kws:
            qs += self.serp.get(c.norm_kw(r["Keyword"]), {}).get("paa", [])
        drop = self.cfg.get("exclude_patterns", []) + self.cfg.get("out_of_area_patterns", [])
        return [q for q in dict.fromkeys(qs) if not any(re.search(x, q.lower()) for x in drop)][:8]

    def related_pages(self, p) -> list[str]:
        """Live pages a new page should link to: the hub of its service line, then same-line pages
        sharing the most keyword words."""
        mine = words([r["Keyword"] for r in p["keywords"]], self.places)
        same = [q for q in self.live if q["line"] == p["line"] and q["url"] != p["url"]]
        hubs = [q["url"] for q in same if q["type"] == "hub"]
        near = sorted(same, key=lambda q: -len(mine & self.lw.get(q["url"], set())))
        return list(dict.fromkeys(hubs + [q["url"] for q in near[:4]]))[:5]

    # ------------------------------------------------------------ list
    def listing(self, count, show_all):
        todo = sorted((p for p in self.pages.values() if not p["exists"]),
                      key=lambda p: (p["priority"] or 9, -p["volume"]))
        if not todo:
            print("No pages to build: every target page in the map exists.")
            return
        n = len(todo) if show_all else (count or self.cfg.get("batch_size", 4))
        L = [f"# Pages to build: {self.cfg['domain']}, {c.TODAY}", "",
             f"{len(todo)} pages to build in the map. The next {min(n, len(todo))}, by priority then monthly searches:", "",
             "| # | page | type | P | searches/mo | primary | copy from |", "|---|---|---|---|---|---|---|"]
        detail = []
        for i, p in enumerate(todo[:n], 1):
            kws = self.ordered(p)
            copy = self.copy_for(p)
            prim = p["primary"] or "?"
            st = self.serp.get(c.norm_kw(prim), {})
            L.append(f"| {i} | `{p['url']}` | {p['type'] or '?'} | {p['priority'] or '?'} | {p['volume']:,} | "
                     f"{prim} | {' or '.join(f'`{u}`' for u in copy) or 'none found'} |")
            detail += [f"## {i}. `{p['url']}`", "",
                       f"- **Type / priority:** {p['type'] or '?'}, P{p['priority'] or '?'}; {p['volume']:,} searches/mo "
                       f"across {len(kws)} keywords; service line {p['line'] or '?'}",
                       f"- **Primary:** {prim} ({st.get('type', 'no SERP data')}). Leads the title tag and H1.",
                       "- **Secondary:** " + (", ".join(f"{r['Keyword']} ({r.get('Volume') or '?'})" for r in kws if r.get("Role") == "Secondary") or "none"),
                       "- **Support:** " + (", ".join(f"{r['Keyword']} ({r.get('Volume') or '?'})" for r in kws if r.get("Role") == "Support") or "none"),
                       f"- **Copy from:** {' or '.join(copy) or 'no close match; use the nearest page of the same type'}"]
            q = self.paa(kws)
            if q:
                detail.append("- **People also ask (FAQ material):** " + " · ".join(q))
            notes = {r.get("Action") for r in kws if r.get("Action")}
            if notes:
                detail.append("- **Map notes:** " + " / ".join(sorted(notes))[:600])
            detail.append("")
        if len(todo) > n:
            L += ["", f"Later ({len(todo) - n}): " + ", ".join(f"`{p['url']}` (P{p['priority'] or '?'}, {p['volume']})" for p in todo[n:])]
        out = c.data_dir(self.cfg, self.root) / f"plan-{c.TODAY}.md"
        out.write_text("\n".join(L + [""] + detail), encoding="utf-8")
        print("\n".join(L))
        print(f"\nDetail per page (keywords, FAQ questions, notes): {out}")
        print("To write one: python plan.py --brief /url/  (a brief the seo-writing skill can write from)")

    # ------------------------------------------------------------ brief
    def brief(self, arg):
        url = c.resolve_page(arg, self.pages)
        p = self.pages.get(url) if url else None
        if not p:
            tail = arg.replace("\\", "/").strip("/").split("/")[-1]
            near = [u for u in self.pages if tail and tail in u]
            c.die(f"'{arg}' is not a target page in the map." + (f" Did you mean {near[:3]}?" if near else ""))
        kws = self.ordered(p)
        prim = p["primary"] or kws[0]["Keyword"]
        st = self.serp.get(c.norm_kw(prim), {})
        req = self.cfg.get("page_requirements", {})
        is_post = p["type"] == "post"
        intent = next((r.get("Intent") for r in kws if r.get("Role") == "Primary"), None) or "?"
        copy = self.copy_for(p)
        sec = [r for r in kws if r.get("Role") == "Secondary"]
        sup = [r for r in kws if r.get("Role") == "Support"]
        L = [f"# Brief: {prim[:1].upper() + prim[1:]}", "",
             f"Page: `{url}` ({p['type'] or '?'} page, {'new' if not p['exists'] else 'live, rewrite'}; "
             f"priority {p['priority'] or '?'}; {p['volume']:,} searches/mo). Domain: {self.cfg['domain']}.",
             f"Query and intent: **{prim}** ({intent}; Google shows {st.get('type', 'no SERP data')})"
             + (" + " + ", ".join(r["Keyword"] for r in (sec + sup)[:6]) if sec + sup else ""),
             "Template: " + ("seo-writing's choice for the query." if is_post else
                             f"NOT a blog post. A {p['type']} page: copy the sections of "
                             f"{' or '.join(f'`{u}`' for u in copy) or 'the nearest live page of the same type'} "
                             "(same sections, same number of items per section, similar word counts). "
                             "Read that page before outlining."),
             "Gain: what this page can say that the pages ranking now don't (local facts, process, "
             "credentials, prices). Ask the user for anything only the client knows.", "",
             "## Keywords", "",
             primary_line(prim, c.raw_titles(self.cfg, self.root, prim, st["_snapshot"]) if st else []),
             "- Secondary: " + (", ".join(f"{r['Keyword']} ({r.get('Volume') or '?'})" for r in sec) or "none")
             + ". In an H2 or the title where it reads naturally.",
             "- Support: " + (", ".join(f"{r['Keyword']} ({r.get('Volume') or '?'})" for r in sup) or "none")
             + ". Worked into headings and copy once each at most; never listed.", ""]
        L += ["## What page one does", ""]
        mix = st.get("mix", {})
        if mix:
            L.append("Kinds of page ranking: " + ", ".join(f"{k} {int(v * 100)}%" for k, v in sorted(mix.items(), key=lambda x: -x[1])))
        if st.get("urls"):
            L.append("Ranking now (pooled): " + ", ".join(st["urls"][:8]))
        q = self.paa(kws)
        if q:
            L.append("People also ask (answer the relevant ones, as an FAQ for a service page): " + " · ".join(q))
        L.append("")
        L += ["## Page requirements", ""]
        files = req.get("files", [])
        if files:
            L.append("Read before writing: " + ", ".join(f"`{f}`" for f in files) + ".")
        for key in ("all", p["type"] or ""):
            if req.get(key):
                L.append(req[key] if isinstance(req[key], str) else "\n".join(f"- {x}" for x in req[key]))
        if self.cfg.get("url_conventions"):
            L.append(f"URL conventions: {self.cfg['url_conventions']}")
        if self.cfg.get("notes"):
            L.append(f"Client decisions: {self.cfg['notes']}")
        if not (files or req):
            L.append("(None recorded. Add page_requirements to seo-project.json: brand/voice files, layout "
                     "rules, claims the client can and can't make, calls to action.)")
        L += ["", "## Links", "",
              "Link to: " + (", ".join(f"`{u}`" for u in self.related_pages(p)) or "none found") +
              ". Ask for a link back to this page from the first of those.", ""]
        notes = {r.get("Action") for r in kws if r.get("Action")}
        if notes:
            L += ["## Map notes", ""] + [f"- {n}" for n in sorted(notes)] + [""]
        d = self.root / self.cfg.get("briefs_dir", "briefs")
        d.mkdir(parents=True, exist_ok=True)
        out = d / f"{url.strip('/').replace('/', '-') or 'home'}.md"
        out.write_text("\n".join(L), encoding="utf-8")
        print(f"Wrote {out}")
        if not req:
            print("WARNING: seo-project.json has no page_requirements, so the brief carries none of this "
                  "site's rules. Ask the user for them (brand/voice files, layout, claims) and add them, "
                  "then write the brief again.")
        print(f"Next: /seo-writing write {out.relative_to(self.root).as_posix()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int)
    ap.add_argument("--all", action="store_true", help="every page to build, not just the next batch")
    ap.add_argument("--brief", metavar="URL", help="write a writing brief for one target page")
    a = ap.parse_args()
    pl = Planner()
    if a.brief:
        pl.brief(a.brief)
    else:
        pl.listing(a.count, a.all)


if __name__ == "__main__":
    main()
