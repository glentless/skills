#!/usr/bin/env python3
"""Accessible inline SVG charts for blog posts. Stdlib only.

    python chart.py spec.json [--mdx | --standalone] [--out chart.html]
    echo '{...}' | python chart.py - --mdx

Spec (JSON):
    {
      "type": "bar | grouped_bar | donut | line | area | lollipop | radar",
      "title": "Weekly downloads by package",
      "subtitle": "optional",
      "unit": "%",            optional suffix for values ("prefix": "$" also works)
      "data": [{"label": "A", "value": 42}, ...],          most types
      "series": [{"name": "2025", "data": [{"label": "Q1", "value": 3}]}, ...],   grouped_bar
      "source": {"title": "Publisher, report name", "date": "2026-03", "url": "https://..."},
      "colors": ["#2563eb", "#f97316"]                      optional brand palette
    }

Text uses currentColor, so charts follow the page's light or dark theme. The
figure carries <title>, <desc> with every value, and a linked source caption.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

W, H = 560, 330
PALETTE = ["#f97316", "#0ea5e9", "#8b5cf6", "#16a34a", "#eab308", "#e11d48"]
ALIASES = {"bar": "bar", "horizontal_bar": "bar", "hbar": "bar", "grouped_bar": "grouped_bar",
           "grouped": "grouped_bar", "donut": "donut", "pie": "donut", "line": "line", "area": "area",
           "lollipop": "lollipop", "radar": "radar"}
MUTED = 'fill="currentColor" opacity="0.72"'  # >= 4.5:1 on typical light and dark backgrounds


class SpecError(ValueError):
    pass


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def num(v) -> float:
    try:
        n = float(v)
    except (TypeError, ValueError):
        raise SpecError(f"not a number: {v!r}")
    if not math.isfinite(n) or n < 0:
        raise SpecError(f"values must be finite and non-negative: {v!r}")
    return n


def wrap(text, width: int, max_lines: int = 3) -> list[str]:
    lines, cur = [], ""
    for word in str(text).split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,") + "…"
    return lines


def text(t, x, y, width=18, anchor="middle", size=11, extra=MUTED, lh=12) -> str:
    spans = "".join(f'<tspan x="{x:.1f}" dy="{0 if i == 0 else lh}">{esc(l)}</tspan>'
                    for i, l in enumerate(wrap(t, width)))
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" {extra}>{spans}</text>'


class Chart:
    def __init__(self, spec: dict):
        self.spec = spec
        self.type = ALIASES.get(str(spec.get("type", "bar")).lower().replace("-", "_").replace(" ", "_"))
        if not self.type:
            raise SpecError(f"unsupported type {spec.get('type')!r}; use one of {sorted(set(ALIASES.values()))}")
        self.colors = spec.get("colors") or PALETTE
        self.unit, self.prefix = str(spec.get("unit", "")), str(spec.get("prefix", ""))

    def fmt(self, v: float) -> str:
        return f"{self.prefix}{v:,.10g}{self.unit}"

    def color(self, i: int) -> str:
        c = str(self.colors[i % len(self.colors)])
        if not re.fullmatch(r"#[0-9a-fA-F]{3,8}|[a-z]+", c):
            raise SpecError(f"bad color {c!r}")
        return c

    def data(self) -> list[tuple[str, float]]:
        d = self.spec.get("data")
        if not isinstance(d, list) or not d:
            raise SpecError("'data' must be a non-empty list of {label, value}")
        return [(str(x["label"]), num(x["value"])) for x in d]

    def grouped(self):
        series = self.spec.get("series")
        if not isinstance(series, list) or not series:
            raise SpecError("grouped_bar needs 'series': [{name, data: [{label, value}]}]")
        labels, names, vals = [], [], {}
        for s in series:
            names.append(str(s["name"]))
            for p in s["data"]:
                if str(p["label"]) not in labels:
                    labels.append(str(p["label"]))
                vals[(str(p["label"]), str(s["name"]))] = num(p["value"])
        return labels, names, vals

    def grid(self, x, y, w, h, n=4) -> str:
        return "".join(f'<line x1="{x}" y1="{y + h - h * i / n:.1f}" x2="{x + w}" y2="{y + h - h * i / n:.1f}" '
                       'stroke="currentColor" opacity="0.1"/>' for i in range(n + 1))

    # -- renderers
    def bar(self, lollipop=False) -> str:
        d = self.data()
        top = max(v for _, v in d) or 1
        x0, y0, cw, ch = 150, 78, 330, 230
        row = ch / len(d)
        out = [self.grid(x0, y0, cw, ch)]
        for i, (label, v) in enumerate(d):
            cy, w = y0 + row * i + row / 2, cw * v / top
            out.append(text(label, x0 - 10, cy + 4 - 6 * (len(wrap(label, 20)) - 1), 20, "end"))
            if lollipop:
                out.append(f'<line x1="{x0}" y1="{cy:.1f}" x2="{x0 + w:.1f}" y2="{cy:.1f}" stroke="currentColor" opacity="0.25"/>'
                           f'<circle cx="{x0 + w:.1f}" cy="{cy:.1f}" r="6" fill="{self.color(i)}"/>')
            else:
                bh = min(row - 8, 34)
                out.append(f'<rect x="{x0}" y="{cy - bh / 2:.1f}" width="{w:.1f}" height="{bh:.1f}" rx="3" fill="{self.color(i)}"/>')
            out.append(f'<text x="{x0 + w + 10:.1f}" y="{cy + 4:.1f}" font-size="11" font-weight="600" fill="currentColor">{esc(self.fmt(v))}</text>')
        return "".join(out)

    def grouped_bar(self) -> str:
        labels, names, vals = self.grouped()
        top = max(vals.values()) or 1
        x0, y0, cw, ch = 60, 92, 460, 200
        gw = cw / len(labels)
        bw = min(26, (gw - 16) / len(names))
        if bw < 4:
            raise SpecError("too many groups or series for one chart; split it")
        out, lx = [self.grid(x0, y0, cw, ch)], x0
        for s, name in enumerate(names):
            out.append(f'<rect x="{lx}" y="58" width="10" height="10" rx="2" fill="{self.color(s)}"/>'
                       f'<text x="{lx + 15}" y="67" font-size="11" fill="currentColor">{esc(name)}</text>')
            lx += 30 + 6.5 * len(name)
        for g, label in enumerate(labels):
            cx = x0 + gw * g + gw / 2
            for s, name in enumerate(names):
                v = vals.get((label, name), 0)
                h, x = ch * v / top, cx - bw * len(names) / 2 + bw * s
                out.append(f'<rect x="{x:.1f}" y="{y0 + ch - h:.1f}" width="{bw - 3:.1f}" height="{h:.1f}" rx="2" fill="{self.color(s)}"/>')
                if bw >= 14:
                    out.append(f'<text x="{x + (bw - 3) / 2:.1f}" y="{y0 + ch - h - 4:.1f}" text-anchor="middle" font-size="9" fill="currentColor">{esc(self.fmt(v))}</text>')
            out.append(text(label, cx, y0 + ch + 16, max(6, int(gw / 6.5))))
        return "".join(out)

    def donut(self) -> str:
        d = self.data()
        total = sum(v for _, v in d) or 1
        cx, cy, ro, ri = 200, 200, 110, 64
        a, out = -math.pi / 2, []
        for i, (label, v) in enumerate(d):
            b = a + math.tau * v / total
            if v / total >= 0.9999:  # a single full slice cannot be drawn as one arc
                b -= 1e-4
            big = 1 if b - a > math.pi else 0
            p = lambda r, t: (cx + r * math.cos(t), cy + r * math.sin(t))
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p(ro, a), p(ro, b), p(ri, b), p(ri, a)
            out.append(f'<path d="M{x1:.2f} {y1:.2f}A{ro} {ro} 0 {big} 1 {x2:.2f} {y2:.2f}L{x3:.2f} {y3:.2f}'
                       f'A{ri} {ri} 0 {big} 0 {x4:.2f} {y4:.2f}Z" fill="{self.color(i)}"/>')
            a = b
            ly = 110 + i * 30
            out.append(f'<rect x="350" y="{ly - 10}" width="12" height="12" rx="2" fill="{self.color(i)}"/>')
            share = "" if self.unit == "%" else f" ({100 * v / total:.0f}%)"
            out.append(text(f"{label}: {self.fmt(v)}{share}", 370, ly, 26, "start", 11, 'fill="currentColor"'))
        return "".join(out)

    def line(self, area=False) -> str:
        d = self.data()
        top = max(v for _, v in d) or 1
        x0, y0, cw, ch = 60, 84, 440, 200
        step = cw / max(len(d) - 1, 1)
        pts = [(x0 + step * i, y0 + ch - ch * v / top) for i, (_, v) in enumerate(d)]
        out = [self.grid(x0, y0, cw, ch)]
        c = self.color(0)
        if area:
            path = f"M{x0} {y0 + ch}L" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + f"L{pts[-1][0]:.1f} {y0 + ch}Z"
            out.append(f'<path d="{path}" fill="{c}" opacity="0.18"/>')
        out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{c}" '
                   'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
        every = max(1, math.ceil(len(d) / 8))  # label at most ~8 x positions so they don't collide
        for i, ((x, y), (label, v)) in enumerate(zip(pts, d)):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{c}"/>')
            if i % every == 0 or i == len(d) - 1:
                out.append(f'<text x="{x:.1f}" y="{y - 9:.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="currentColor">{esc(self.fmt(v))}</text>')
                out.append(text(label, x, y0 + ch + 18, max(6, int(step * every / 6.5)), size=10))
        return "".join(out)

    def radar(self) -> str:
        d = self.data()
        if len(d) < 3:
            raise SpecError("radar needs at least 3 axes")
        top = max(v for _, v in d) or 1
        cx, cy, r = 280, 190, 98
        ang = lambda i: -math.pi / 2 + math.tau * i / len(d)
        out = []
        for lv in (0.25, 0.5, 0.75, 1):
            out.append('<polygon points="' + " ".join(f"{cx + r * lv * math.cos(ang(i)):.1f},{cy + r * lv * math.sin(ang(i)):.1f}"
                                                      for i in range(len(d))) + '" fill="none" stroke="currentColor" opacity="0.15"/>')
        pts = []
        for i, (label, v) in enumerate(d):
            t = ang(i)
            ax, ay = cx + r * math.cos(t), cy + r * math.sin(t)
            out.append(f'<line x1="{cx}" y1="{cy}" x2="{ax:.1f}" y2="{ay:.1f}" stroke="currentColor" opacity="0.15"/>')
            pts.append(f"{cx + r * v / top * math.cos(t):.1f},{cy + r * v / top * math.sin(t):.1f}")
            lx, ly = cx + (r + 22) * math.cos(t), cy + (r + 22) * math.sin(t)
            anchor = "end" if lx < cx - 15 else "start" if lx > cx + 15 else "middle"
            out.append(text(f"{label} ({self.fmt(v)})", lx, ly + 4, 16, anchor, 10))
        c = self.color(0)
        out.append(f'<polygon points="{" ".join(pts)}" fill="{c}" fill-opacity="0.25" stroke="{c}" stroke-width="2"/>')
        return "".join(out)

    def describe(self) -> str:
        if self.type == "grouped_bar":
            labels, names, vals = self.grouped()
            parts = [f"{l}: " + ", ".join(f"{n} {self.fmt(vals.get((l, n), 0))}" for n in names) for l in labels]
        else:
            parts = [f"{l} {self.fmt(v)}" for l, v in self.data()]
        return f"{self.spec.get('title', 'Chart')}. " + "; ".join(parts) + "."

    def render(self, mdx=False, standalone=False) -> str:
        body = {"bar": self.bar, "lollipop": lambda: self.bar(True), "grouped_bar": self.grouped_bar,
                "donut": self.donut, "line": self.line, "area": lambda: self.line(True), "radar": self.radar}[self.type]()
        title = str(self.spec.get("title") or "Chart")
        cid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "chart"
        src = self.spec.get("source") or {}
        if isinstance(src, str):
            src = {"title": src}
        s_title, s_date, s_url = str(src.get("title", "")), str(src.get("date", "")), str(src.get("url", ""))
        if not s_title:
            print("warning: no source; every chart of real data needs one", file=sys.stderr)
        if s_url and urlparse(s_url).scheme not in ("http", "https"):
            s_url = ""
        credit = f"Source: {s_title}" + (f" ({s_date})" if s_date else "")
        sub = text(self.spec["subtitle"], W / 2, 50, 80, size=12) if self.spec.get("subtitle") else ""
        cap = f'<a href="{esc(s_url)}">{esc(s_title)}</a>' if s_url else esc(s_title)
        h = H + (22 if standalone else 0)
        ns = ' xmlns="http://www.w3.org/2000/svg"' if standalone else ""
        svg = (f'<svg{ns} viewBox="0 0 {W} {h}" width="100%" style="max-width: {W}px; height: auto; '
               f'font-family: system-ui, sans-serif" role="img" aria-labelledby="{cid}-t {cid}-d">\n'
               f'<title id="{cid}-t">{esc(title)}</title>\n<desc id="{cid}-d">{esc(self.describe())}</desc>\n'
               f'<text x="{W / 2}" y="30" text-anchor="middle" font-size="17" font-weight="700" fill="currentColor">{esc(title)}</text>\n'
               f'{sub}\n{body}\n'
               + (f'<text x="{W / 2}" y="{h - 8}" text-anchor="middle" font-size="10" {MUTED}>{esc(credit)}</text>\n'
                  if s_title and standalone else "") + "</svg>")
        if not standalone:  # in a post, the linked figcaption carries the source
            svg = ('<figure class="blog-chart">\n' + svg + "\n"
                   + (f"<figcaption>Source: {cap}{', ' + esc(s_date) if s_date else ''}.</figcaption>\n" if s_title else "")
                   + "</figure>")
        return to_mdx(svg) if mdx else svg


def to_mdx(markup: str) -> str:
    """HTML attributes to JSX: camelCase, className, style objects."""
    for a, b in (("class=", "className="), ("text-anchor", "textAnchor"), ("font-size", "fontSize"),
                 ("font-weight", "fontWeight"), ("font-family", "fontFamily"), ("stroke-width", "strokeWidth"),
                 ("stroke-linejoin", "strokeLinejoin"), ("stroke-linecap", "strokeLinecap"),
                 ("fill-opacity", "fillOpacity"), ("aria-labelledby", "aria-labelledby")):
        markup = markup.replace(a, b)

    def style(m):
        pairs = [d.split(":", 1) for d in m.group(1).split(";") if ":" in d]
        return "style={{" + ", ".join(f"{re.sub(r'-(.)', lambda x: x.group(1).upper(), k.strip())}: {json.dumps(v.strip())}"
                                      for k, v in pairs) + "}}"
    return re.sub(r'style="([^"]*)"', style, markup)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="JSON spec file, or - for stdin")
    ap.add_argument("--mdx", action="store_true", help="emit JSX-safe markup for MDX")
    ap.add_argument("--standalone", action="store_true",
                    help="bare SVG with the source drawn inside, for social images or export")
    ap.add_argument("--out", help="write to this file instead of stdout")
    args = ap.parse_args()
    try:
        raw = sys.stdin.read() if args.spec == "-" else Path(args.spec).read_text(encoding="utf-8")
        markup = Chart(json.loads(raw)).render(args.mdx, args.standalone)
    except (OSError, json.JSONDecodeError, SpecError, KeyError, TypeError) as e:
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if args.out:
        Path(args.out).write_text(markup + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(markup)
    return 0


if __name__ == "__main__":
    sys.exit(main())
