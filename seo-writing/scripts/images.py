#!/usr/bin/env python3
"""Find or generate blog images, and record where every image came from.

Stock (licensed, downloaded locally, never hotlinked):
    python images.py stock "cast iron skillet" [--provider openverse|pexels|pixabay] [--preview DIR]
    python images.py stock "cast iron skillet" --pick 3 --out public/images/blog/hero.webp --size 1200x630

Generate (provider-agnostic; picks the provider whose key is set):
    python images.py generate "A cast iron skillet on a gas burner, ..." --out public/images/blog/hero.webp --aspect 16:9 --size 1200x630
    python images.py models [--provider openai|gemini]      # list image models the key can use

Keys (environment): OPENAI_API_KEY, GEMINI_API_KEY or GOOGLE_AI_API_KEY, PEXELS_API_KEY,
PIXABAY_API_KEY. Openverse needs none. Override with BLOG_IMAGE_PROVIDER and BLOG_IMAGE_MODEL.

Every saved image gets an entry in image-credits.json beside it: source, license,
creator, landing page, or provider/model/prompt for generated images.
Resizing and format conversion need Pillow (pip install pillow); without it the
original bytes are saved as-is.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "blog-skill-images/1.0"}
# Image models turn over every few months. If a default is retired, `images.py models` lists what the key can use.
DEFAULT_MODEL = {"openai": "gpt-image-2.5-flare", "gemini": "gemini-nano-banana-2.1"}
OPENAI_SIZES = {"landscape": "1536x1024", "square": "1024x1024", "portrait": "1024x1536"}
GEMINI_ASPECTS = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"}
TIMEOUT = 120  # generation can take a minute; stock calls finish far sooner


class Fail(Exception):
    pass


def http(url: str, data: dict | None = None, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                                 headers={**UA, **({"Content-Type": "application/json"} if data is not None else {}),
                                          **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        hint = ""
        if e.code in (400, 404) and "model" in body.lower():
            hint = "\nhint: model not available to this key. Run `images.py models` and pass --model or set BLOG_IMAGE_MODEL."
        if e.code in (401, 403):
            hint = "\nhint: the API key is missing, wrong, or lacks access (some image models need billing enabled)."
        raise Fail(f"HTTP {e.code} from {urllib.parse.urlparse(url).netloc}: {body}{hint}")
    except urllib.error.URLError as e:
        raise Fail(f"network error for {urllib.parse.urlparse(url).netloc}: {e.reason}")


# ------------------------------------------------------------------ stock

def search(query: str, provider: str, count: int, orientation: str) -> list[dict]:
    q = urllib.parse.quote(query)
    if provider == "openverse":
        aspect = {"landscape": "wide", "portrait": "tall", "square": "square"}[orientation]
        data = json.loads(http(f"https://api.openverse.org/v1/images/?q={q}&license_type=commercial,modification"
                               f"&aspect_ratio={aspect}&page_size={count}&mature=false"))
        return [{"id": r["id"], "title": r.get("title") or "", "creator": r.get("creator") or "unknown",
                 "license": f"CC {r['license'].upper()} {r.get('license_version') or ''}".strip(),
                 "license_url": r.get("license_url"), "page": r.get("foreign_landing_url"),
                 "url": r["url"], "thumb": r.get("thumbnail") or r["url"],
                 "width": r.get("width"), "height": r.get("height"), "provider": f"openverse/{r.get('source')}"}
                for r in data.get("results", [])]
    if provider == "pexels":
        key = os.environ.get("PEXELS_API_KEY") or _need("PEXELS_API_KEY")
        data = json.loads(http(f"https://api.pexels.com/v1/search?query={q}&orientation={orientation}&per_page={count}",
                               headers={"Authorization": key}))
        return [{"id": p["id"], "title": p.get("alt") or "", "creator": p["photographer"], "license": "Pexels License",
                 "license_url": "https://www.pexels.com/license/", "page": p["url"], "url": p["src"]["original"],
                 "thumb": p["src"]["medium"], "width": p["width"], "height": p["height"], "provider": "pexels"}
                for p in data.get("photos", [])]
    if provider == "pixabay":
        key = os.environ.get("PIXABAY_API_KEY") or _need("PIXABAY_API_KEY")
        orient = {"landscape": "horizontal", "portrait": "vertical", "square": "all"}[orientation]
        data = json.loads(http(f"https://pixabay.com/api/?key={key}&q={q}&image_type=photo&orientation={orient}"
                               f"&per_page={max(count, 3)}&safesearch=true"))
        return [{"id": h["id"], "title": h.get("tags") or "", "creator": h["user"], "license": "Pixabay Content License",
                 "license_url": "https://pixabay.com/service/license-summary/", "page": h["pageURL"],
                 "url": h.get("largeImageURL") or h["webformatURL"], "thumb": h["previewURL"],
                 "width": h["imageWidth"], "height": h["imageHeight"], "provider": "pixabay"}
                for h in data.get("hits", [])[:count]]
    raise Fail(f"unknown stock provider {provider}")


def _need(var: str):
    raise Fail(f"{var} is not set. Use --provider openverse (no key), or export {var}.")


# ------------------------------------------------------------------ generate

def pick_provider(explicit: str | None) -> str:
    p = explicit or os.environ.get("BLOG_IMAGE_PROVIDER")
    if p:
        return p
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_API_KEY"):
        return "gemini"
    raise Fail("no image provider configured: set OPENAI_API_KEY or GEMINI_API_KEY (or use an image MCP tool, "
               "or fall back to `images.py stock`).")


def gemini_key() -> str:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_API_KEY") or _need("GEMINI_API_KEY")


def generate(prompt: str, provider: str, model: str, aspect: str, dry: bool) -> tuple[bytes, str]:
    w, h = (float(x) for x in aspect.split(":"))
    shape = "square" if abs(w - h) < 0.01 else "landscape" if w > h else "portrait"
    if provider == "openai":
        body = {"model": model, "prompt": prompt, "size": OPENAI_SIZES[shape], "n": 1}
        if dry:
            return json.dumps(body, indent=2).encode(), "dry"
        key = os.environ.get("OPENAI_API_KEY") or _need("OPENAI_API_KEY")
        data = json.loads(http("https://api.openai.com/v1/images/generations", body,
                               {"Authorization": f"Bearer {key}"}))
        return base64.b64decode(data["data"][0]["b64_json"]), "image/png"
    if provider == "gemini":
        if aspect not in GEMINI_ASPECTS:
            aspect = {"landscape": "16:9", "portrait": "9:16", "square": "1:1"}[shape]
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
        if dry:
            return json.dumps(body, indent=2).encode(), "dry"
        data = json.loads(http(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                               body, {"x-goog-api-key": gemini_key()}))
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline:
                    return base64.b64decode(inline["data"]), inline.get("mimeType", "image/png")
        reason = (data.get("candidates") or [{}])[0].get("finishReason") or data.get("promptFeedback")
        raise Fail(f"no image returned (reason: {reason}). If blocked by safety filters, describe the scene "
                   "positively and remove real people's names.")
    raise Fail(f"unknown provider {provider}; use openai or gemini")


def list_models(provider: str) -> list[str]:
    if provider == "openai":
        key = os.environ.get("OPENAI_API_KEY") or _need("OPENAI_API_KEY")
        data = json.loads(http("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}))
        return sorted(m["id"] for m in data["data"] if "image" in m["id"])
    data = json.loads(http("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000",
                           headers={"x-goog-api-key": gemini_key()}))
    return sorted(m["name"].removeprefix("models/") for m in data.get("models", [])
                  if "image" in m["name"] and "generateContent" in m.get("supportedGenerationMethods", []))


# ------------------------------------------------------------------ save

def save(raw: bytes, out: Path, size: str | None) -> str:
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image, ImageOps
    except ImportError:
        if size or out.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            print("warning: Pillow not installed; saved original bytes without resizing/converting", file=sys.stderr)
        out.write_bytes(raw)
        return "original"
    img = Image.open(io.BytesIO(raw))
    if size:
        tw, th = (int(x) for x in size.lower().split("x"))
        if img.width < tw or img.height < th:
            print(f"warning: source is {img.width}x{img.height}, upscaled to {tw}x{th}; prefer a larger image", file=sys.stderr)
        img = ImageOps.fit(img.convert("RGB"), (tw, th), Image.LANCZOS, centering=(0.5, 0.5))
    fmt = {".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP", ".png": "PNG", ".avif": "AVIF"}.get(out.suffix.lower(), "PNG")
    if fmt in ("JPEG", "WEBP", "AVIF") and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img.save(out, fmt, **({"quality": 82} if fmt != "PNG" else {"optimize": True}))
    return f"{img.width}x{img.height} {fmt}"


def record(out: Path, entry: dict) -> Path:
    ledger = out.parent / "image-credits.json"
    try:
        items = json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else []
    except json.JSONDecodeError:
        items = []
    items = [i for i in items if i.get("file") != out.name] + [{"file": out.name, "date": str(dt.date.today()), **entry}]
    ledger.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ledger


# ------------------------------------------------------------------ cli

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stock")
    s.add_argument("query")
    s.add_argument("--provider", default="openverse", choices=("openverse", "pexels", "pixabay"))
    s.add_argument("--orientation", default="landscape", choices=("landscape", "portrait", "square"))
    s.add_argument("--count", type=int, default=8)
    s.add_argument("--preview", help="download thumbnails here so they can be looked at before picking")
    s.add_argument("--pick", type=int, help="1-based result number to download")
    s.add_argument("--out")
    s.add_argument("--size", help="crop/resize, e.g. 1200x630")
    g = sub.add_parser("generate")
    g.add_argument("prompt")
    g.add_argument("--out", required=True)
    g.add_argument("--provider", choices=("openai", "gemini"))
    g.add_argument("--model")
    g.add_argument("--aspect", default="16:9")
    g.add_argument("--size", help="crop/resize after generation, e.g. 1200x630")
    g.add_argument("--dry-run", action="store_true")
    m = sub.add_parser("models")
    m.add_argument("--provider", choices=("openai", "gemini"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if a.cmd == "models":
            p = pick_provider(a.provider)
            print(f"{p}:\n  " + "\n  ".join(list_models(p) or ["(none found)"]))
            return 0
        if a.cmd == "generate":
            p = pick_provider(a.provider)
            model = a.model or os.environ.get("BLOG_IMAGE_MODEL") or DEFAULT_MODEL[p]
            raw, mime = generate(a.prompt, p, model, a.aspect, a.dry_run)
            if mime == "dry":
                print(f"{p} / {model}\n{raw.decode()}")
                return 0
            out = Path(a.out)
            info = save(raw, out, a.size)
            ledger = record(out, {"source": "ai-generated", "provider": p, "model": model, "prompt": a.prompt,
                                  "license": "AI-generated; check the provider's terms for commercial use"})
            print(f"saved {out} ({info}); credit logged in {ledger}")
            return 0
        results = search(a.query, a.provider, a.count, a.orientation)
        if not results:
            print("no results; try broader or more concrete terms (objects and scenes, not abstractions)")
            return 1
        if a.pick:
            if not a.out:
                raise Fail("--pick needs --out")
            r = results[a.pick - 1]
            out = Path(a.out)
            info = save(http(r["url"]), out, a.size)
            ledger = record(out, {k: r[k] for k in ("provider", "title", "creator", "license", "license_url", "page", "url")})
            needs = "" if r["provider"] in ("pexels", "pixabay") else f'\nattribution required: "{r["title"] or "Photo"}" by {r["creator"]}, {r["license"]}'
            print(f"saved {out} ({info}); credit logged in {ledger}{needs}")
            return 0
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title'][:70] or '(untitled)'} | {r['width']}x{r['height']} | {r['license']} | "
                  f"{r['creator']} | {r['page']}")
            if a.preview:
                d = Path(a.preview)
                d.mkdir(parents=True, exist_ok=True)
                try:
                    (d / f"{i}.jpg").write_bytes(http(r["thumb"]))
                except Fail as e:
                    print(f"   (thumbnail failed: {e})")
        if a.preview:
            print(f"thumbnails in {a.preview}/ (1.jpg ...). Look at them, then rerun with --pick N --out PATH")
        return 0
    except (Fail, IndexError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
