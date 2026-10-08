# On-page SEO, schema and platforms

## Contents

- [On-page checklist](#on-page-checklist)
- [Structured data](#structured-data)
- [Answer engines and crawlers](#answer-engines-and-crawlers)
- [Platform conventions](#platform-conventions)
- [Don't](#dont)

Search engines and AI answer products reward the same things: a page that
clearly answers a query, is crawlable, and is trustworthy. Optimizing for AI
answers is ordinary SEO done well. No special markup, file or "GEO" trick
replaces it.

## On-page checklist

| Element | Pass when |
|---|---|
| Title tag | Specific to this page, about 60 chars or fewer, main topic near the front, matches the H1's intent, unique on the site |
| Meta description | 70 to 160 chars, states what the reader gets, contains nothing that isn't on the page, unique |
| H1 | Exactly one per page. In most static-site setups the theme renders the frontmatter `title` as the H1, so the body shouldn't add another |
| Headings | No skipped levels; each describes its section |
| Slug | Lowercase, hyphenated, 3 to 6 meaningful words, no date on evergreen posts, stable once published |
| Canonical | Absolute and self-referencing, unless the page is deliberately consolidated into another |
| Internal links | 3 to 8 contextual links with descriptive anchors; the post links to its pillar, and related posts link back |
| External links | To primary sources; `rel="sponsored"` for paid links, `rel="ugc"` for user content |
| Images | Descriptive alt text, explicit width and height, local files, WebP or AVIF, hero not lazy-loaded |
| Open Graph | `og:title`, `og:description`, `og:image` (a 1200×630 raster file, never SVG), `og:type=article`, `og:url` = the canonical URL |
| Twitter/X | `twitter:card=summary_large_image`; it falls back to the OG tags |
| Dates | Published date visible; the updated date shown only after a real update, and matching `dateModified` |

Most frameworks generate the head tags from frontmatter. Check the frontmatter
and the template that consumes it, then confirm on the rendered page.

## Structured data

Emit one JSON-LD `@graph` per post unless the platform or an SEO plugin already
does it. **Check before adding:** duplicate, conflicting graphs are worse than
none.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "https://example.com/blog/slug#article",
      "headline": "Post title",
      "description": "Meta description",
      "image": "https://example.com/images/blog/slug-cover.webp",
      "datePublished": "2026-03-01",
      "dateModified": "2026-05-20",
      "author": {"@id": "https://example.com/authors/jo-tran#person"},
      "publisher": {"@id": "https://example.com/#org"},
      "mainEntityOfPage": "https://example.com/blog/slug",
      "inLanguage": "en"
    },
    {
      "@type": "Person",
      "@id": "https://example.com/authors/jo-tran#person",
      "name": "Jo Tran",
      "url": "https://example.com/authors/jo-tran",
      "jobTitle": "…",
      "sameAs": ["https://www.linkedin.com/in/…"]
    },
    {
      "@type": "Organization",
      "@id": "https://example.com/#org",
      "name": "Example",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png",
      "sameAs": ["…"]
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Blog", "item": "https://example.com/blog"},
        {"@type": "ListItem", "position": 2, "name": "Post title", "item": "https://example.com/blog/slug"}
      ]
    }
  ]
}
```

- **Add only what the page actually contains:**
  - `VideoObject` for each embedded video: name, description, thumbnailUrl,
    uploadDate, embedUrl
  - `Review` or `Product` only for a real review with a real rating
  - `ProfilePage` on author pages
- **Every value must match the visible content.** Use absolute URLs. Stable
  `@id`s let entities reference each other.
- **Build it with a JSON encoder, never string concatenation.** When inlining
  it in HTML, escape `</` as `<\/`.
- **Validate it:**
  - `check_post.py` catches invalid JSON.
  - Google's Rich Results Test and the Schema.org validator check the types.
- **Not worth adding:**
  - `FAQPage`: Google retired FAQ rich results in May 2026. The markup is still
    valid; keep it only if the visible FAQ is genuinely useful and the site
    already emits it.
  - `HowTo` has no rich result.
  - `QAPage` is only for pages with a single question and user-submitted
    answers.
  - There is no special schema for AI answers.

## Answer engines and crawlers

- **What helps:**
  - sections that answer early and make sense alone
  - explicit entity names
  - tables for comparisons and numbered steps for processes
  - claims cited at the source
  - content in server-rendered HTML

  Many AI crawlers don't run JavaScript, so text that only appears after
  client-side rendering, or inside tabs that load on click, may be invisible to
  them.
- **Robots policy is a business decision, not a default.** The common AI user
  agents are `GPTBot`, `OAI-SearchBot`, `ChatGPT-User`, `ClaudeBot`,
  `Claude-User`, `Claude-SearchBot`, `PerplexityBot`, `Perplexity-User`,
  `Applebot-Extended` and `Google-Extended`. `Google-Extended` controls Gemini
  training and grounding, not Google Search's AI features. Blocking a search bot removes the site from that product's answers.
  CDNs such as Cloudflare can block AI crawlers by default, so check what the
  site actually serves to them.
- **llms.txt** is optional. Google doesn't use it. It can help some tools, and
  it should never come before crawlability and good content.
- For live-site checks (robots, rendering, Core Web Vitals, indexing), hand off
  to the `seo` skill.

## Platform conventions

Read two existing posts before writing a new one and copy their conventions.
These are the defaults when there's nothing to copy.

| Platform | Posts live in | Frontmatter and markup notes |
|---|---|---|
| Next.js / MDX | `content/`, `posts/`, `app/blog/` | JSX rules: `className`, camelCase attributes (`strokeWidth`), `style={{…}}`, every tag closed; a literal `{` or `<` in prose must be escaped; inline SVG must use JSX attributes (`chart.py --mdx`); components must be imported |
| Astro | `src/content/blog/` | The content collection schema in `content.config.*` validates frontmatter, so read it and match its field names and types exactly; MDX rules apply to `.mdx` |
| Hugo | `content/posts/` or page bundles `content/posts/<slug>/index.md` | YAML `---` or TOML `+++`; raw HTML (SVG, figures) needs `markup.goldmark.renderer.unsafe = true`, or use a shortcode; `{{< ref "x.md" >}}` for internal links; images go in the page bundle |
| Jekyll | `_posts/YYYY-MM-DD-slug.md` | The filename sets the date and slug; `layout:` in frontmatter; `{% link %}` or `{{ site.baseurl }}` for internal links |
| 11ty | per config, often `posts/` | The data cascade means defaults may come from `posts.json`, so don't repeat them |
| Gatsby | `content/blog/<slug>/index.md(x)` | Images co-located with the post; MDX rules apply |
| WordPress | CMS, not files | Write Gutenberg block HTML or clean HTML; the SEO plugin (Yoast or Rank Math) usually owns the title, meta and schema, so fill its fields instead of adding JSON-LD; featured image and excerpt are separate fields |
| Ghost | CMS | HTML or Markdown cards; built-in meta fields; Admin API to publish |
| Plain HTML | site root | Semantic `<article>` with `<header>`, `<time datetime>`, `<figure>` and `<figcaption>`, JSON-LD in the `<head>` |

Publishing to a CMS through its API is an outward action. Draft locally, show
the user, and push only on their go-ahead. Read credentials from environment
variables and never write them to files.

## Don't

- Stuff keywords into headings, alt text or anchors.
- Change `date` to look fresh, or bump `updated` without a substantive change.
- Publish many near-identical pages for keyword variants. That is scaled
  low-value content, whoever or whatever writes it.
- Hotlink stock images, or use an SVG as `og:image`.
- Add schema for content the page doesn't show.
- Rewrite a published slug without a 301 redirect and updated internal links.
