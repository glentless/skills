# Visuals: charts, images, video

## Contents

- [When a visual earns its place](#when-a-visual-earns-its-place)
- [Charts](#charts)
- [Images](#images)
- [Generating images](#generating-images)
- [Alt text and embedding](#alt-text-and-embedding)
- [Video](#video)

## When a visual earns its place

Add a visual where it shows something faster than prose can:

- a trend, a comparison or a share → **chart**
- a UI, a result or a before/after → **screenshot or photo**
- a process or architecture → **diagram**
- a demonstration → **video**

Decorative images are optional, and come last.

Rough density: one visual every 300 to 600 words in a standard post, one per
step in a how-to, and one per item in a product listicle. Don't put two visuals
of the same kind back to back. Prefer variety across chart types, but repeat a
type when that's clearer than switching.

## Charts

Charts come from data in the source ledger, and the values must match the
source exactly.

```bash
python scripts/chart.py spec.json            # HTML/Markdown: <figure> with inline SVG
python scripts/chart.py spec.json --mdx      # JSX-safe for MDX
python scripts/chart.py spec.json --standalone --out chart.svg   # bare SVG with the credit inside
```

The spec is in the script header (run it with `-h`). Valid types are bar,
grouped_bar, donut, line, area, lollipop and radar. Add `"unit": "%"` or
`"prefix": "$"` to format values, and `"colors": [...]` to apply brand colours
from BLOG.md.

| Data shape | Chart |
|---|---|
| Rank or compare categories | bar (horizontal) or lollipop for many items |
| Before/after, A vs B across groups | grouped_bar |
| Parts of a whole (2 to 6 parts, summing to 100%) | donut |
| Change over time | line, or area for cumulative values |
| One item scored on 3 to 8 dimensions | radar |

What the script handles, and what it doesn't:

- **Handled:** charts use `currentColor`, so they follow light and dark themes,
  and carry `<title>`, a `<desc>` listing every value, and a linked source
  caption.
- **Your job:** a title that states the takeaway ("Install time dominates
  builds"), not just the subject ("Build time").
- **Not covered:** for diagrams (flows, architecture) use Mermaid if the site
  renders it, or a hand-written SVG using the same `currentColor` approach.
- **Wrong tool:** for a table of numbers, a table beats a chart.

## Images

Try these in order. Each later source is less specific to the post than the one
before it.

1. **Original:** the user's screenshots, photos, product UI, or a screenshot
   you take of a public page or tool with headless Chrome.
2. **Diagram or chart** made from real data (above).
3. **Licensed stock**, downloaded locally with its credit recorded:
   ```bash
   python scripts/images.py stock "concrete scene words" --preview <tmp dir>
   # look at the thumbnails, pick one
   python scripts/images.py stock "concrete scene words" --pick 3 --out <site image dir>/<slug>-cover.webp --size 1200x630
   ```
   - **Providers:** Openverse needs no key. Pexels and Pixabay need
     `PEXELS_API_KEY` or `PIXABAY_API_KEY`.
   - **Credits:** every download is logged in `image-credits.json` beside the
     image. CC BY images need a visible credit line, which the script prints.
4. **Generated**, for abstract or niche topics where stock is generic (below).

**Cover image:** 1200×630 raster (WebP or JPG), relevant, without text baked in
unless it's a designed social card, and with nothing important near the edges,
where crops cut. Use the same file for `og:image` unless the site has a social
card template.

Save images where the project keeps them, following the paths used in existing
posts. Name them `<slug>-<what>.webp`.

## Generating images

Use whichever generator is available, in this order:

1. An image-generation MCP tool, if one is loaded in the session.
2. `python scripts/images.py generate "<prompt>" --out <path> --aspect 16:9 --size 1200x630`.
   - **Provider:** it uses OpenAI when `OPENAI_API_KEY` is set and Gemini when
     `GEMINI_API_KEY` is set. Override with `--provider` or
     `BLOG_IMAGE_PROVIDER`.
   - **Model:** set it with `--model` or `BLOG_IMAGE_MODEL`.
   - **Model rejected:** run `python scripts/images.py models` and pick one from
     the list.
3. No generator available: write the prompt and the specs into the delivery
   notes so the user can generate it elsewhere, and use stock meanwhile.

**Write the prompt as a short scene description, not a keyword list.** Cover, in
order:

- **subject:** what it is, with material and texture detail
- **action or state**
- **setting**
- **composition:** shot type, angle, negative space for the crop
- **lighting**, the biggest quality lever
- **style:** photographic, editorial illustration, flat vector, and so on
- **brand palette** from BLOG.md

Example: *"Editorial photograph of a well-used black cast iron skillet resting
on a gas burner, a pinch of coarse salt in the pan, steam rising. Shot from a
three-quarter angle with the pan off-centre left and empty space on the right.
Soft morning window light from the left, warm tones. Shallow depth of field,
natural colours."*

Rules for generated images:

- **People:** no real people, no logos, no trademarks.
- **Safety refusals:** if the model refuses, describe the scene positively and
  more generically, then retry, at most twice.
- **Small fixes:** edit the image rather than regenerating it.
- **Labelling:** don't present a generated image as a photo of a real event,
  product or customer. Label it per BLOG.md if the site discloses AI imagery.

## Alt text and embedding

- **Alt text** describes what the image shows and why it's there, in a sentence
  of about 10 to 125 characters. Include the topic naturally, never as a keyword
  list. For a chart, state the takeaway. For a screenshot, say what it
  demonstrates. Purely decorative images get `alt=""`, which is rare in posts.
  - Good: `alt="Cast iron skillet drying on a lit gas burner"`
  - Bad: `alt="cast iron skillet cleaning tips best"`
- **Markdown:** `![alt](/images/blog/slug-step-2.webp)`
- **HTML:** `<img src="…" alt="…" width="1200" height="630" loading="lazy" decoding="async">`.
  Above the fold, drop `loading="lazy"` and add `fetchpriority="high"`.
- **Captions:** wrap the image in `<figure>` with a `<figcaption>` when it needs
  a caption or a credit.
- **MDX and framework image components:** follow the project's existing usage
  (`next/image`, Astro `<Image>`).

## Video

Embed a video only when it shows something better than the post can: a
demonstration, a walkthrough, or a primary-source talk. Check that it is
current, accurate and captioned.

- **Placement:** put it after the H2 it supports, not stacked against a chart.
  One or two per post is plenty.
- **Embedding:** use a lightweight embed (`youtube-nocookie.com`, `loading="lazy"`,
  a `title` attribute), or the platform's own shortcode, such as
  `{{< youtube ID >}}` in Hugo.
- **Search engines and screen readers:** put a one-line text description with a
  link next to the embed, so they still get the content.
- **Schema:** add a `VideoObject` to the schema graph ([seo.md](seo.md#structured-data)).
