# Translating, localizing and publishing in several languages

## Contents

- [Commands](#commands)
- [Translate](#translate)
- [Localize](#localize)
- [Hreflang and schema](#hreflang-and-schema)
- [Locale formats](#locale-formats)

## Commands

- `translate <file> --to de,fr,es-MX`: language conversion that keeps the
  structure intact.
- `localize <file> --locale de-DE`: cultural adaptation of a post that is
  already translated.
- `multilingual <topic> --languages de,fr`: writes the source post (the full
  `write` workflow), translates it, localizes it, then emits hreflang.
- Locale QA is part of the site audit ([site-audit.md](site-audit.md#locale-audit)).

**Language codes:** use the language, plus a region where it matters. Ask when
it's ambiguous: `es` (Spain or Latin America?), `pt` (`pt-BR` or `pt-PT`?), `zh`
(`zh-Hans` or `zh-Hant`?).

**Batch size:** do at most about 8 languages per run, and review each one. Ten
mechanical translations of a post nobody will read locally is scaled content.
Ask whether each market actually has an audience.

**Parallel work:** when the Agent tool is available, run one subagent per
language. Each gets the source file, the keyword map, the locale and the rules
below.

**Vietnamese:** when the target is Vietnamese, also apply the
`vietnamese-voice` skill. It owns register, forms of address and
translationese for that language.

## Translate

1. **Map the keywords first.** For each primary and secondary keyword, decide
   whether the source term is what people in that market actually search
   (often "Content Marketing" stays in German) or whether a local term wins.
   Check the SERP in that language when you're unsure. Use the mapped terms in
   the title, meta description, slug and H2s.
2. **Translate the meaning, not the words.**
   - Match the source's register.
   - Choose formal or informal address once and keep it consistent: Sie or du,
     vous or tu, usted or tú.
   - Replace idioms with local equivalents.
   - Restructure sentences in the target language's natural order. Never keep
     English word order.
3. **Translate everything a reader sees:**
   - frontmatter title, description and tags
   - headings and body
   - alt text and figure captions
   - chart text (`<text>`/`<tspan>`, or regenerate the chart with
     `chart.py` from a translated spec)
   - CTA, Key Takeaways and FAQ
   - internal link anchors, pointed at the localized URL when one exists
4. **Leave these alone:**
   - URLs and code (comments may be translated only if the post is a tutorial)
   - product, company and person names
   - schema `@id`s
   - citations' publisher names
5. **Add frontmatter:** `lang`, `translatedFrom`, `translatedDate`, a localized
   `slug`, and a shared `translationKey` (or whatever field the site's i18n
   uses).
6. **Check before saving.** Look for:
   - no leftover source-language fragments, other than real loanwords
   - numbers, dates, currencies and quotation marks in local format
   - the same section, image and chart count as the source
   - no machine-translation tells (literal idioms, calque word order)

   Save to the site's i18n structure. Without one, use
   `translations/<lang>/<slug>.<ext>`.

## Localize

Localizing goes past translation, so that the post reads as if it had been
written for that market.

| Element | Adapt |
|---|---|
| Examples, brands, retailers | Use local equivalents the reader knows (search to confirm they're current), keeping the same argument |
| Statistics | Prefer a local source with a comparable method. If the only data is foreign, keep it and **say where it's from** ("in the US, …"). Never swap in a local number measured differently without rewriting the claim |
| Law and regulation | Map by issue and jurisdiction: CCPA becomes GDPR (DSGVO in German, RGPD in French) in the EU, LGPD in Brazil, APPI in Japan. Keep the original law where the claim really is about it |
| Currency and prices | Convert where it helps, with the rate date, or keep the original and say so |
| CTA tone | Germany, Austria and Switzerland, and Japan, prefer informational over pushy. US-style urgency often reads as spam |
| Holidays, seasons, events | Local calendar; seasons flip in the southern hemisphere |
| Formality | Fit the market and the product. B2B German usually uses Sie; Japanese register shifts sharply with the audience |

Record each non-obvious substitution (the source, the date, and why), so a
reviewer can check it.

## Hreflang and schema

For each group of translations:

```html
<link rel="alternate" hreflang="en" href="https://example.com/blog/slug/" />
<link rel="alternate" hreflang="de" href="https://example.com/de/blog/lokalisierter-slug/" />
<link rel="alternate" hreflang="x-default" href="https://example.com/blog/slug/" />
```

- **Placement:** put the tags in every version.
- **Required on each version:**
  - a link to every version, including itself
  - absolute HTTPS URLs
  - reciprocal links (if A points to B, B points to A)
  - `x-default` pointing to the fallback, such as a language picker or the main
    market
- **Canonical:** each version's canonical points to itself, never to the source
  language.
- **Sitemap alternative:** add `<xhtml:link rel="alternate" hreflang="…">`
  entries in the sitemap. Use either the tags or the sitemap, consistently.
- **Schema:** each version's `BlogPosting` gets its own `inLanguage`, plus
  `translationOfWork: {"@id": "<source URL>#article"}`.
- **Frameworks:** many i18n plugins (Next.js, Astro, Hugo multilingual, Polylang
  or WPML) generate all of this. Configure the plugin rather than hand-writing
  tags.

## Locale formats

| Locale | Number | Date | Currency | Quotes |
|---|---|---|---|---|
| en-US | 1,234.5 | March 5, 2026 | $1,234 | “…” |
| en-GB | 1,234.5 | 5 March 2026 | £1,234 | ‘…’ or “…” |
| de | 1.234,5 | 5. März 2026 | 1.234 € | „…“ |
| fr | 1 234,5 | 5 mars 2026 | 1 234 € | « … » (with spaces) |
| es | 1234,5 / 1.234,5 | 5 de marzo de 2026 | 1234 € (ES), $1,234 MXN (MX) | «…» or “…” |
| pt-BR | 1.234,5 | 5 de março de 2026 | R$ 1.234 | “…” |
| it | 1.234,5 | 5 marzo 2026 | 1.234 € | «…» |
| nl | 1.234,5 | 5 maart 2026 | € 1.234 | “…” |
| ja | 1,234.5 | 2026年3月5日 | ¥1,234 / 1,234円 | 「…」 |
| zh | 1,234.5 | 2026年3月5日 | ¥1,234 | “…” / 「…」 |
| ko | 1,234.5 | 2026년 3월 5일 | ₩1,234 | “…” |
| vi | 1.234,5 | 05/03/2026 | 1.234 ₫ | “…” |
