#!/usr/bin/env python3
"""Mechanical checks for blog posts. Stdlib only, Python 3.9+.

Lint posts (exit 1 if any post has errors):
    python check_post.py post.md [more.md ...] [--json]
Site inventory (link graph, overlap candidates, staleness, taxonomy, locales):
    python check_post.py --site content/blog [--json]
Voice profile from sample posts:
    python check_post.py --voice a.md b.md c.md

Options:
    --allow-em-dash     do not treat em dashes as errors
    --ban-file FILE     extra banned phrases, one per line (e.g. from BLOG.md)
    --base-url URL      treat absolute links to this host as internal
    --stale-months N    site mode: flag posts not updated in N months (default 12)

This script reports facts and lints. It does not score quality; judgment
lives in reference/review.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

POST_EXTS = {".md", ".mdx", ".markdown", ".html", ".htm"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "_site",
             "public", "vendor", ".cache", "coverage", "reports", ".astro"}
SKIP_NAMES = {"readme", "changelog", "license", "_index", "contributing"}

# Phrases that read as machine-written filler. Style warnings, not errors.
SLOP = [
    "delve", "tapestry", "testament to", "in today's", "ever-evolving",
    "ever-changing", "fast-paced world", "digital landscape", "navigate the",
    "navigating the", "game-changer", "game changer", "revolutionize",
    "unlock the", "unleash", "harness the power", "elevate your", "seamless",
    "cutting-edge", "state-of-the-art", "robust", "leverage",
    "it's important to note", "it is important to note", "it's worth noting",
    "it is worth noting", "worth mentioning", "in conclusion", "in summary",
    "furthermore", "moreover", "embark", "realm", "pivotal", "paramount",
    "multifaceted", "meticulous", "comprehensive guide", "dive into",
    "deep dive", "let's explore", "let's dive", "look no further",
    "whether you're a", "in the world of", "when it comes to", "crucial role",
    "a myriad of", "plethora", "foster", "underscore", "streamline",
    "empower", "transformative", "synergy", "holistic", "at its core",
    "the key insight", "here's the thing",
]
SLOP_PATTERNS = [
    (re.compile(r"\bnot (just|only|merely) [^.;:]{1,60}, but\b", re.I), "not just X, but Y"),
    (re.compile(r"\bit'?s not (about )?[^.;:]{1,40}[,;] it'?s\b", re.I), "it's not X, it's Y"),
    (re.compile(r"(?:^|\. )(?:why does this matter|what does this mean for [^?]{1,40}|the result|the catch|the takeaway)\?", re.I), "rhetorical setup question"),
]
PLACEHOLDER = re.compile(
    r"\[(?:INTERNAL-LINK|STAT|IMAGE|CHART|VISUAL|INFO-GAIN|ANSWER-FIRST|CTA|VIDEO|CALLOUT|SOURCE|CITATION)[^\]]*\]"
    r"|\bTODO\b|\bTKTK\b|\bTK\b|\bXX%|lorem ipsum|\[citation needed\]", re.I)
GENERIC_ANCHORS = {"click here", "here", "read more", "learn more", "this article",
                   "this post", "link", "this link", "more", "this"}
STAT = re.compile(
    r"\d[\d,.]*\s?(?:%|percent\b|x\b|×|times (?:more|less|higher|lower|faster))"
    r"|[$€£¥]\s?\d|\d[\d,.]*\s?(?:million|billion|trillion)\b"
    r"|\b\d+ (?:out of|in) (?:every )?\d+\b", re.I)
STOCK_HOSTS = ("pixabay.com", "unsplash.com", "pexels.com")
EN_STOP = {"the", "and", "to", "of", "a", "in", "is", "that", "for", "it", "you", "with", "on", "are"}
STOPWORDS = EN_STOP | {"how", "what", "why", "your", "best", "guide", "vs", "an", "or", "do",
                       "does", "can", "from", "by", "at", "be", "this", "my", "our", "complete",
                       "ultimate", "tips", "ways", "top", "new", "2024", "2025", "2026", "2027"}
UPDATED_KEYS = ("lastupdated", "last_updated", "updated", "lastmod", "datemodified",
                "date_modified", "modified", "updatedat", "updated_at")
DESC_KEYS = ("description", "summary", "excerpt", "meta_description", "metadescription", "seo_description")
KEYWORD_KEYS = ("primary_keyword", "focus_keyword", "focus_keyphrase", "keyword")


# ---------------------------------------------------------------- parsing

def parse_frontmatter(text: str) -> tuple[dict, int, str]:
    """Return (fields, number of frontmatter lines, body). YAML or TOML subset."""
    fm: dict = {}
    for fence, sep in (("---", ":"), ("+++", "=")):
        if not text.startswith(fence + "\n"):
            continue
        end = text.find("\n" + fence, len(fence))
        if end == -1:
            break
        block = text[len(fence) + 1:end]
        body_start = text.find("\n", end + 1)
        body = "" if body_start == -1 else text[body_start + 1:]
        key = None
        for line in block.splitlines():
            m = re.match(r"^([A-Za-z_][\w-]*)\s*" + re.escape(sep) + r"\s*(.*)$", line)
            if m:
                key, val = m.group(1).lower(), m.group(2).strip()
                if val.startswith("[") and val.endswith("]"):
                    fm[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
                elif val in ("", "|", ">", "|-", ">-"):
                    fm[key] = []
                else:
                    fm[key] = val.strip("'\"")
            elif key and re.match(r"^\s+-\s+", line):
                if not isinstance(fm.get(key), list):
                    fm[key] = []
                fm[key].append(re.sub(r"^\s+-\s+", "", line).strip().strip("'\""))
            elif key and isinstance(fm.get(key), list) and line.startswith("  ") and not fm[key]:
                fm[key] = line.strip()  # folded scalar, first line is enough
        return fm, block.count("\n") + 3, body  # opening fence + block lines + closing fence
    return fm, 0, text


def mask_code(body: str) -> str:
    """Blank fenced code, inline code, <script> and <style>, keeping line count."""
    def blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))
    body = re.sub(r"^(```|~~~)[^\n]*\n.*?^\1[^\n]*$", blank, body, flags=re.S | re.M)
    body = re.sub(r"<(script|style)\b.*?</\1>", blank, body, flags=re.S | re.I)
    body = re.sub(r"`[^`\n]+`", blank, body)
    return body


def plain(s: str) -> str:
    """Markdown/HTML inline markup to plain text."""
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[*_~]{1,3}", "", s)
    return re.sub(r"\s+", " ", s).strip()


def attr(tag: str, name: str) -> str | None:
    m = re.search(name + r"""\s*=\s*(?:"([^"]*)"|'([^']*)'|\{["'`]([^"'`]*)["'`]\})""", tag, re.I)
    return None if not m else next(g for g in m.groups() if g is not None)


class Post:
    def __init__(self, path: Path, base_host: str = ""):
        self.path = path
        raw = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        self.is_html = path.suffix.lower() in (".html", ".htm")
        self.fm, self.offset, body = parse_frontmatter(raw)
        self.raw_body = body
        self.jsonld = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', body, re.S | re.I)
        self.body = mask_code(body)
        self.lines = self.body.split("\n")
        self.base_host = base_host
        if self.is_html:
            self.fm.setdefault("title", plain((re.search(r"<title>(.*?)</title>", raw, re.S | re.I) or [None, ""])[1]))
            m = re.search(r'<meta[^>]+name=["\']description["\'][^>]*>', raw, re.I)
            if m and attr(m.group(0), "content"):
                self.fm.setdefault("description", attr(m.group(0), "content"))
        self._extract()

    def ln(self, idx: int) -> int:
        return idx + 1 + self.offset

    def _extract(self) -> None:
        self.headings, self.images, self.links = [], [], []
        for i, line in enumerate(self.lines):
            m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if m and not self.is_html:
                self.headings.append((len(m.group(1)), plain(m.group(2)), self.ln(i)))
            for m in re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1>", line, re.I):
                self.headings.append((int(m.group(1)), plain(m.group(2)), self.ln(i)))
            for m in re.finditer(r"!\[([^\]]*)\]\(\s*<?([^)\s>]+)", line):
                self.images.append((m.group(1).strip(), m.group(2), self.ln(i), ""))
            for m in re.finditer(r"<(?:img|Image)\b[^>]*>", line):
                tag = m.group(0)
                self.images.append(((attr(tag, "alt") or "").strip(), attr(tag, "src") or "", self.ln(i), tag))
            for m in re.finditer(r"(?<!!)\[([^\]]+)\]\(\s*<?([^)\s>]+)", line):
                self.links.append((plain(m.group(1)), m.group(2), self.ln(i)))
            for m in re.finditer(r"<a\b[^>]*>(.*?)</a>", line, re.I | re.S):
                href = attr(m.group(0), "href")
                if href:
                    self.links.append((plain(m.group(1)), href, self.ln(i)))
            for m in re.finditer(r'\{\{<\s*(?:rel)?ref\s+"([^"]+)"\s*>\}\}', line):
                self.links.append(("", m.group(1), self.ln(i)))
        # Blocks: paragraphs and list items with their first line number.
        self.paragraphs, self.items = [], []
        buf, start = [], 0
        for i, line in enumerate(self.lines + [""]):
            s = line.strip()
            if not s:
                if buf:
                    block = " ".join(buf)
                    if not re.match(r"^(#|\||<(?!a\b|strong|em|b\b|i\b)|!\[|\{\{|import |export )", block):
                        self.paragraphs.append((plain(block.lstrip("> ")), self.ln(start)))
                buf = []
                continue
            if re.match(r"^([-*+]|\d+[.)])\s+", s):
                self.items.append((plain(re.sub(r"^([-*+]|\d+[.)])\s+", "", s)), self.ln(i)))
                continue
            if not buf:
                start = i
            buf.append(s)
        self.prose = " ".join(p for p, _ in self.paragraphs + self.items)
        self.words = re.findall(r"[^\W\d_][\w'’-]*", self.prose)

    def title(self) -> str:
        return str(self.fm.get("title", "")) or next((t for lv, t, _ in self.headings if lv == 1), "")

    def description(self) -> str:
        return next((str(self.fm[k]) for k in DESC_KEYS if self.fm.get(k)), "")

    def keyword(self) -> str:
        return next((str(self.fm[k]).strip() for k in KEYWORD_KEYS if self.fm.get(k)), "")

    def opening(self, n: int = 100) -> str:
        """First n words of body text, in document order."""
        text = " ".join(t for t, _ in sorted(self.paragraphs + self.items, key=lambda b: b[1] or 0))
        return " ".join(text.split()[:n])

    def slug(self) -> str:
        if self.fm.get("slug"):
            return str(self.fm["slug"]).strip("/").split("/")[-1].lower()
        stem = self.path.stem.lower()
        if stem in ("index", "page", "+page"):
            stem = self.path.parent.name.lower()
        return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)  # Jekyll date prefix

    def is_internal(self, href: str) -> bool:
        if href.startswith(("mailto:", "tel:", "#", "javascript:")):
            return False
        u = urlparse(href)
        if not u.scheme and not u.netloc:
            return True
        return bool(self.base_host) and u.netloc.lower().removeprefix("www.") == self.base_host

    def date(self, keys) -> dt.date | None:
        for k in keys:
            v = self.fm.get(k)
            if isinstance(v, str):
                m = re.match(r"(\d{4})-(\d{2})-(\d{2})", v)
                if m:
                    try:
                        return dt.date(*map(int, m.groups()))
                    except ValueError:
                        return None
        return None


def _kw_norm(text: str) -> str:
    text = re.sub(r"['’]", "", text.lower())
    return " ".join(re.findall(r"[^\W_]+", text))  # hyphens split: as-built == as built


def _kw_stem(w: str) -> str:
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def _kw_stems(text: str) -> set[str]:
    return {_kw_stem(w) for w in _kw_norm(text).split() if w not in STOPWORDS}


def keyword_match(keyword: str, text: str, near: bool = False) -> tuple[str, set[str]]:
    """'exact' (phrase, ignoring case and hyphens), 'variant' (every content word, any order
    or plural), 'partial' or 'missing'; plus the content words that are absent. With near,
    a variant's words must fall within a few words of each other, as in body text."""
    if re.search(rf"\b{re.escape(_kw_norm(keyword))}\b", _kw_norm(text)):
        return "exact", set()
    want = _kw_stems(keyword)
    absent = want - _kw_stems(text)
    if not absent and near:
        words = [_kw_stem(w) for w in _kw_norm(text).split()]
        span = len(_kw_norm(keyword).split()) + 3
        if not any(want <= set(words[i:i + span]) for i in range(len(words))):
            return "partial", set()
    if not absent:
        return "variant", set()
    return ("partial" if absent != want else "missing"), absent


# ---------------------------------------------------------------- metrics

def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?…])\s+(?=[\"“(\[]?[A-ZÀ-Ý0-9])", text) if len(s.split()) >= 2]


def syllables(word: str) -> int:
    w = word.lower().strip("'’")
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def readability(post: Post) -> dict:
    sents = sentences(post.prose)
    lens = [len(s.split()) for s in sents] or [0]
    out = {"sentences": len(sents), "avg_sentence_words": round(statistics.mean(lens), 1),
           "sentence_stdev": round(statistics.pstdev(lens), 1),
           "long_sentences_40plus": sum(1 for n in lens if n >= 40)}
    words = post.words
    english = words and sum(1 for w in words if w.lower() in EN_STOP) / len(words) >= 0.08
    if english and sents:
        syl = sum(syllables(w) for w in words)
        out["flesch_reading_ease"] = round(206.835 - 1.015 * len(words) / len(sents) - 84.6 * syl / len(words), 1)
    return out


# ---------------------------------------------------------------- lint

def lint(post: Post, allow_em_dash: bool, banned: list[str]) -> dict:
    errors, warnings, notes = [], [], []
    E = lambda line, msg: errors.append({"line": line, "msg": msg})
    W = lambda line, msg: warnings.append({"line": line, "msg": msg})
    fm = post.fm

    # Title and headings
    body_h1 = [h for h in post.headings if h[0] == 1]
    title = post.title()
    if not title:
        E(None, "no title (no frontmatter title and no H1)")
    if len(body_h1) > 1:
        E(body_h1[1][2], f"{len(body_h1)} H1 headings; use one")
    if body_h1 and fm.get("title") and not post.is_html:
        W(body_h1[0][2], "body H1 plus frontmatter title: most themes render the title as H1, so this "
                         "likely duplicates it. Match the project's existing posts")
    prev = 1
    for level, text, line in post.headings:
        if level > prev + 1:
            E(line, f"heading level skips H{prev} -> H{level}: '{text}'")
        prev = level
    if title and not 20 <= len(title) <= 65:
        W(None, f"title is {len(title)} chars; 20-65 survives most result previews")

    # Meta
    desc = post.description()
    if not desc:
        W(None, "no meta description (description/summary/excerpt)")
    elif not 70 <= len(desc) <= 170:
        W(None, f"description is {len(desc)} chars; 70-170 avoids truncation and thin snippets")

    # Declared primary keyword: title, description, opening
    kw = post.keyword()
    if kw:
        for where, text, near in (("title", title, False), ("description", desc, False),
                                  ("first 100 words", post.opening(), True)):
            if not text:
                continue
            match, absent = keyword_match(kw, text, near)
            if match == "variant":
                notes.append(f"primary keyword '{kw}' is in the {where} as a variant, not the exact phrase")
            elif match != "exact":
                W(None, f"primary keyword '{kw}' not in the {where}"
                        + (f" (missing: {', '.join(sorted(absent))})" if absent and match == "partial" else ""))
    if fm and not fm.get("author") and not fm.get("authors"):
        W(None, "no author in frontmatter")
    published, updated = post.date(("date", "published", "pubdate", "publishdate", "datepublished")), post.date(UPDATED_KEYS)
    if published and updated and updated < published:
        E(None, f"updated date {updated} is before published date {published}")

    # Placeholders, dashes, slop, banned
    phrases = [(p, re.compile(r"\b" + re.escape(p).replace("'", "['’]") + r"\b", re.I)) for p in SLOP]
    bans = [(b, re.compile(re.escape(b), re.I)) for b in banned]
    for i, line in enumerate(post.lines):
        n = post.ln(i)
        if re.match(r"^\s*(import|export) ", line):
            continue
        for m in PLACEHOLDER.finditer(line):
            E(n, f"leftover placeholder {m.group(0)!r}")
        if "—" in line and not allow_em_dash:
            E(n, f"em dash x{line.count(chr(0x2014))}; use a comma, colon, period or parentheses")
        if " – " in line and not allow_em_dash:
            E(n, "spaced en dash used as a dash")
        text = plain(line)
        for p, rx in bans:
            if rx.search(text):
                E(n, f"banned phrase '{p}'")
        for p, rx in phrases:
            if rx.search(text):
                W(n, f"filler phrase '{p}'")
        for rx, label in SLOP_PATTERNS:
            if rx.search(text):
                W(n, f"pattern: {label}")

    # Statistics without a source in the same paragraph or item
    for block_text, line in _raw_blocks(post):
        if STAT.search(plain(block_text)) and not re.search(r"\]\(https?://|href=|\[\^\w+\]|<cite", block_text):
            W(line, f"number with no source link in this paragraph: \"{plain(block_text)[:80]}...\"")

    # Images
    for i, (alt, src, line, tag) in enumerate(post.images):
        if not alt:
            E(line, f"image without alt text: {src}")
        elif len(alt) < 10:
            W(line, f"alt text too thin: '{alt}'")
        if any(h in src for h in STOCK_HOSTS):
            W(line, "hotlinked stock image; download it locally and keep the credit")
        if i == 0 and 'loading="lazy"' in tag:
            W(line, "first image is lazy-loaded; the hero/LCP image should not be")
        if src and not local_image_exists(post.path, src):
            W(line, f"local image not found: {src} (looked beside the post and in static/, public/, assets/ up the tree)")
    cover = next((str(fm[k]) for k in ("image", "cover", "coverimage", "featured_image", "hero") if isinstance(fm.get(k), str) and fm.get(k)), "")
    if cover and not local_image_exists(post.path, cover):
        W(None, f"frontmatter image not found: {cover}")

    # Links
    internal = [l for l in post.links if post.is_internal(l[1])]
    external = [l for l in post.links if l[1].startswith("http") and not post.is_internal(l[1])]
    for text, href, line in post.links:
        if text.lower().strip(" .") in GENERIC_ANCHORS:
            W(line, f"generic anchor text '{text}' -> {href}")
    if re.search(r"(?<![(\"'<=])https?://\S+", " ".join(t for t, _ in post.paragraphs)):
        W(None, "bare URL in prose; link descriptive text instead")
    words = len(post.words)
    if words < 300:
        W(None, f"only {words} words; make sure it fully serves the intent (or that it isn't a stub)")
    if words > 500 and not internal:
        W(None, "no internal links")
    if words > 600 and not any(h[0] == 2 for h in post.headings):
        W(None, "no H2 sections in a post over 600 words")
    dupes = [u for u, c in Counter(h for _, h, _ in post.links).items() if c > 1 and not u.startswith("#")]
    if dupes:
        notes.append(f"links repeated: {', '.join(dupes[:5])}")

    # Structured data
    for block in post.jsonld:
        try:
            data = json.loads(block)
            if "FAQPage" in json.dumps(data):
                notes.append("FAQPage schema present: earns no rich result; keep only if the visible FAQ helps readers")
        except json.JSONDecodeError as e:
            E(None, f"invalid JSON-LD: {e.msg} at char {e.pos}")

    longest = max(((len(p.split()), ln) for p, ln in post.paragraphs), default=(0, None))
    if longest[0] > 200:
        W(longest[1], f"paragraph of {longest[0]} words")
    facts = {
        "title": title, "title_chars": len(title), "description_chars": len(desc), "words": words,
        "reading_minutes": max(1, round(words / 230)),
        "outline": [f"{'  ' * (lv - 1)}H{lv} {t}" for lv, t, _ in post.headings],
        "paragraphs": len(post.paragraphs), "longest_paragraph_words": longest[0],
        "images": len(post.images), "internal_links": len(internal), "external_links": len(external),
        "question_headings": sum(1 for h in post.headings if h[1].endswith("?")),
        "has_summary_box": bool(re.search(r"(key takeaways|tl;dr|the bottom line|at a glance|in brief)", post.body, re.I)),
        "jsonld_blocks": len(post.jsonld),
        "published": str(published or ""), "updated": str(updated or ""),
        **readability(post),
    }
    by_line = lambda x: x["line"] or 0
    return {"file": str(post.path), "errors": sorted(errors, key=by_line),
            "warnings": sorted(warnings, key=by_line), "notes": notes, "facts": facts}


def local_image_exists(post_path: Path, src: str) -> bool:
    """True for remote/data URLs (not ours to check) or a local file found in a usual place."""
    src = src.split("?")[0].split("#")[0]
    if re.match(r"^[a-z]+:|^//|\{", src, re.I):  # http:, data:, protocol-relative, template expressions
        return True
    rel = src.lstrip("/")
    if not src.startswith("/") and (post_path.parent / src).exists():
        return True
    # Root-relative paths resolve against the site's static root; walk up to 5 levels to find it.
    for base in [post_path.parent, *list(post_path.parents)[:5]]:
        for prefix in ("", "static", "public", "assets", "src/assets"):
            if (base / prefix / rel).exists():
                return True
    return False


def _raw_blocks(post: Post):
    """Paragraphs and list items with markup intact, for source-link detection."""
    buf, start = [], 0
    for i, line in enumerate(post.lines + [""]):
        s = line.strip()
        if s.startswith("#") or s.startswith("|") or s.startswith("<!--"):
            s = ""
        if re.match(r"^([-*+]|\d+[.)])\s+", s):
            if buf:
                yield " ".join(buf), post.ln(start)
            yield s, post.ln(i)
            buf = []
            continue
        if not s:
            if buf:
                yield " ".join(buf), post.ln(start)
            buf = []
            continue
        if not buf:
            start = i
        buf.append(s)


# ---------------------------------------------------------------- site mode

def find_posts(root: Path) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in POST_EXTS or not p.is_file():
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in p.relative_to(root).parts[:-1]):
            continue
        if p.stem.lower() in SKIP_NAMES or p.stem.isupper():  # README, BLOG.md, CLAUDE.md and the like
            continue
        out.append(p)
    return out


def tokens(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[^\W_]+", text.lower()):
        if w in STOPWORDS or len(w) < 3:
            continue
        out.add(re.sub(r"(ies|es|s|ing|ed)$", "", w) if len(w) > 5 else w)
    return out


def site(root: Path, args) -> dict:
    posts = [Post(p, args.base_host) for p in find_posts(root)]
    if not posts:
        return {"error": f"no posts found under {root}"}
    by_slug = {p.slug(): p for p in posts}
    inbound, outbound, unresolved = Counter(), Counter(), []
    for p in posts:
        for _, href, line in p.links:
            if not p.is_internal(href):
                continue
            target = re.split(r"[?#]", urlparse(href).path)[0].rstrip("/").split("/")[-1].lower()
            target = re.sub(r"\.(md|mdx|markdown|html?)$", "", target)
            target = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", target)
            if not target:
                continue
            if target in by_slug and by_slug[target] is not p:
                inbound[target] += 1
                outbound[p.slug()] += 1
            elif target not in by_slug:
                unresolved.append(f"{p.path.name}:{line} -> {href}")
    rows, err_files = [], 0
    for p in posts:
        r = lint(p, args.allow_em_dash, args.banned)
        err_files += bool(r["errors"])
        rows.append({"file": str(p.path.relative_to(root)), "slug": p.slug(), "title": r["facts"]["title"],
                     "words": r["facts"]["words"], "errors": len(r["errors"]), "warnings": len(r["warnings"]),
                     "inbound": inbound[p.slug()], "outbound": outbound[p.slug()],
                     "updated": r["facts"]["updated"] or r["facts"]["published"]})
    # Overlap candidates: same declared keyword, or similar title tokens
    overlaps = []
    keyed = [(p, tokens(p.title() + " " + p.keyword())) for p in posts]
    for i in range(len(keyed)):
        for j in range(i + 1, len(keyed)):
            (a, ta), (b, tb) = keyed[i], keyed[j]
            if not ta or not tb:
                continue
            score = len(ta & tb) / len(ta | tb)
            if score >= 0.5:
                overlaps.append({"a": a.slug(), "b": b.slug(), "similarity": round(score, 2),
                                 "shared": sorted(ta & tb)})
    overlaps.sort(key=lambda o: -o["similarity"])
    titles = Counter(p.title().strip().lower() for p in posts if p.title())
    descs = Counter(p.description().strip().lower() for p in posts if p.description())
    cutoff = dt.date.today() - dt.timedelta(days=30.4 * args.stale_months)
    stale = sorted((r["updated"], r["slug"]) for r in rows if r["updated"] and r["updated"] < str(cutoff))
    tags, cats, no_cat = Counter(), Counter(), []
    for p in posts:
        for t in _as_list(p.fm.get("tags")):
            tags[t.lower()] += 1
        cs = _as_list(p.fm.get("categories") or p.fm.get("category"))
        for c in cs:
            cats[c.lower()] += 1
        if not cs:
            no_cat.append(p.slug())
    norm = defaultdict(list)
    for t in tags:
        norm[re.sub(r"[^a-z0-9]", "", t).rstrip("s")].append(t)
    langs = Counter(str(p.fm.get("lang") or p.fm.get("language") or _path_lang(p.path, root) or "") for p in posts)
    many = len(posts) > 1
    return {
        "root": str(root), "posts": len(posts), "posts_with_errors": err_files, "table": rows,
        "orphans": [r["slug"] for r in rows if many and r["inbound"] == 0],
        "dead_ends": [r["slug"] for r in rows if many and r["outbound"] == 0],
        "unresolved_internal_links": unresolved[:200],
        "overlap_candidates": overlaps[:100],
        "duplicate_titles": [t for t, c in titles.items() if c > 1],
        "duplicate_descriptions": [d[:80] for d, c in descs.items() if c > 1],
        "stale": [{"slug": s, "updated": u} for u, s in stale],
        "tags": {"total": len(tags), "used_once": sorted(t for t, c in tags.items() if c == 1),
                 "merge_candidates": [v for v in norm.values() if len(v) > 1], "top": tags.most_common(15)},
        "categories": dict(cats.most_common()), "uncategorized": no_cat if cats else [],
        "languages": {k or "unknown": v for k, v in langs.items()},
    }


def _as_list(v) -> list[str]:
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [s.strip() for s in str(v).split(",") if s.strip()] if v else []


def _path_lang(path: Path, root: Path) -> str:
    for part in path.relative_to(root).parts[:-1]:
        if re.fullmatch(r"[a-z]{2}(-[A-Za-z]{2,4})?", part):
            return part
    return ""


# ---------------------------------------------------------------- voice mode

def voice(paths: list[Path]) -> dict:
    posts = [Post(p) for p in paths]
    sent_lens, para_lens, words_all, q_heads, heads = [], [], [], 0, 0
    for p in posts:
        sent_lens += [len(s.split()) for s in sentences(p.prose)]
        para_lens += [len(t.split()) for t, _ in p.paragraphs]
        words_all += [w.lower() for w in p.words]
        heads += len(p.headings)
        q_heads += sum(1 for h in p.headings if h[1].endswith("?"))
    n = len(words_all) or 1
    per_k = lambda rx: round(1000 * sum(1 for w in words_all if re.fullmatch(rx, w)) / n, 1)
    grams = Counter()
    clean = [w for w in words_all if w not in STOPWORDS]
    for size in (2, 3):
        grams.update(" ".join(clean[i:i + size]) for i in range(len(clean) - size + 1))
    slop_hits = sum(len(re.findall(r"\b" + re.escape(s) + r"\b", " ".join(words_all))) for s in SLOP)
    return {
        "samples": len(posts), "words": len(words_all),
        "sentence_words": {"mean": round(statistics.mean(sent_lens or [0]), 1),
                           "median": statistics.median(sent_lens or [0]),
                           "stdev": round(statistics.pstdev(sent_lens or [0]), 1),
                           "share_under_8": round(sum(1 for x in sent_lens if x < 8) / max(len(sent_lens), 1), 2),
                           "share_over_30": round(sum(1 for x in sent_lens if x > 30) / max(len(sent_lens), 1), 2)},
        "paragraph_words": {"mean": round(statistics.mean(para_lens or [0]), 1),
                            "median": statistics.median(para_lens or [0])},
        "per_1000_words": {"contractions": per_k(r"\w+['’](s|re|ve|ll|d|t|m)"), "i_me_my": per_k(r"i|me|my|mine"),
                           "we_our": per_k(r"we|us|our|ours"), "you_your": per_k(r"you|your|yours"),
                           "filler_phrases": round(1000 * slop_hits / n, 1)},
        "question_heading_share": round(q_heads / max(heads, 1), 2),
        "recurring_phrases": [g for g, c in grams.most_common(40) if c >= max(3, len(posts))][:15],
    }


# ---------------------------------------------------------------- output

def print_lint(results: list[dict]) -> None:
    for r in results:
        f = r["facts"]
        print(f"\n== {r['file']}")
        fre = f" | Flesch {f['flesch_reading_ease']}" if "flesch_reading_ease" in f else ""
        print(f"{f['words']} words (~{f['reading_minutes']} min) | {f['paragraphs']} paragraphs | "
              f"avg sentence {f['avg_sentence_words']}w (sd {f['sentence_stdev']}){fre} | "
              f"{f['images']} images | links {f['internal_links']} internal / {f['external_links']} external")
        print("outline:\n  " + "\n  ".join(f["outline"] or ["(no headings)"]))
        for kind in ("errors", "warnings"):
            if r[kind]:
                print(f"{kind.upper()} ({len(r[kind])}):")
                for x in r[kind]:
                    print(f"  {'L' + str(x['line']) if x['line'] else '--'}: {x['msg']}")
        for note in r["notes"]:
            print(f"note: {note}")
    bad = sum(1 for r in results if r["errors"])
    print(f"\n{len(results)} file(s), {bad} with errors.")


def print_site(s: dict) -> None:
    if "error" in s:
        print(s["error"])
        return
    print(f"# Site inventory: {s['root']}\n\n{s['posts']} posts, {s['posts_with_errors']} with lint errors.\n")
    print("| file | words | err | warn | in | out | updated |\n|---|---|---|---|---|---|---|")
    for r in sorted(s["table"], key=lambda r: (-r["errors"], r["inbound"])):
        print(f"| {r['file']} | {r['words']} | {r['errors']} | {r['warnings']} | {r['inbound']} | {r['outbound']} | {r['updated']} |")
    sections = [("Orphans (no inbound links from other posts)", s["orphans"]),
                ("Dead ends (no links to other posts)", s["dead_ends"]),
                ("Internal links that match no post (may be non-post pages)", s["unresolved_internal_links"]),
                ("Overlap candidates (check intent before merging)",
                 [f"{o['a']} <> {o['b']} ({o['similarity']}: {', '.join(o['shared'])})" for o in s["overlap_candidates"]]),
                ("Duplicate titles", s["duplicate_titles"]), ("Duplicate descriptions", s["duplicate_descriptions"]),
                ("Not updated within the stale window", [f"{x['slug']} ({x['updated']})" for x in s["stale"]]),
                ("Tags used once", s["tags"]["used_once"]),
                ("Tag merge candidates", [" / ".join(v) for v in s["tags"]["merge_candidates"]]),
                ("Uncategorized", s["uncategorized"])]
    for name, items in sections:
        if items:
            print(f"\n## {name} ({len(items)})\n" + "\n".join(f"- {x}" for x in items[:50]))
    print(f"\n## Taxonomy\n{s['tags']['total']} tags; top: {s['tags']['top']}\ncategories: {s['categories']}")
    if set(s["languages"]) != {"unknown"}:
        print(f"\n## Languages\n{s['languages']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--site")
    ap.add_argument("--voice", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-em-dash", action="store_true")
    ap.add_argument("--ban-file")
    ap.add_argument("--base-url", default="")
    ap.add_argument("--stale-months", type=int, default=12)
    args = ap.parse_args()
    args.base_host = urlparse(args.base_url).netloc.lower().removeprefix("www.") if args.base_url else ""
    args.banned = []
    if args.ban_file:
        try:
            args.banned = [l.strip() for l in Path(args.ban_file).read_text(encoding="utf-8").splitlines()
                           if l.strip() and not l.startswith("#")]
        except OSError as e:
            print(f"warning: cannot read ban file: {e}", file=sys.stderr)
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.site:
        root = Path(args.site)
        if not root.is_dir():
            print(f"not a directory: {root}", file=sys.stderr)
            return 2
        s = site(root, args)
        print(json.dumps(s, indent=2, ensure_ascii=False)) if args.json else print_site(s)
        return 0

    files = []
    for p in map(Path, args.paths):
        if p.is_dir():
            files += find_posts(p)
        elif p.is_file():
            files.append(p)
        else:
            print(f"not found: {p}", file=sys.stderr)
    if not files:
        ap.print_usage()
        return 2
    if args.voice:
        v = voice(files)
        print(json.dumps(v, indent=2, ensure_ascii=False))
        if len(files) < 5:
            print("warning: fewer than 5 samples; treat the profile as rough", file=sys.stderr)
        return 0
    results = [lint(Post(f, args.base_host), args.allow_em_dash, args.banned) for f in files]
    print(json.dumps(results, indent=2, ensure_ascii=False)) if args.json else print_lint(results)
    return 1 if any(r["errors"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
