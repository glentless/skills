# Reviewing a post

Covers `review` (the full score) and its focused modes: `--seo`, `--geo` and
`factcheck`. It also covers the review step inside `write` and `rewrite`.

## Contents

- [Procedure](#procedure)
- [Severity](#severity)
- [Rubric (100 points)](#rubric-100-points)
- [Focused modes](#focused-modes)
- [Fact-check](#fact-check)
- [Report format](#report-format)
- [Fresh-eyes reviewer brief](#fresh-eyes-reviewer-brief)

## Procedure

1. **Get the content.**
   - Local file: read it.
   - URL: fetch the page and review the rendered content. For Core Web Vitals,
     indexing, robots and canonical checks on a live site, use the `seo` skill
     if it's installed.
   - Directory: batch mode, one row per post, then a priority list sorted by
     score.
2. **Run `python scripts/check_post.py <file>`.** Its errors are facts, not
   opinions. Quote its output as evidence. Don't re-derive word counts by eye.
3. **Read the post as its reader would.** Check: does it answer the intent? What
   does it give that the top results don't? Where do you lose interest or trust?
4. **Score the rubric.** Give every lost point a location and a fix.
5. **Classify each finding** by severity, then write the report.

**Score honestly.** A 74 that is really a 74 is useful. A generous 88 is not.
Mark a check N/A when you can't assess it (performance needs a live URL), scale
that category to the points you could assess, and say so in the report.

## Severity

| Level | Meaning | Examples |
|---|---|---|
| **P0** blocks publishing | Wrong, fabricated or harmful | Unverifiable or invented figure, quote, source or first-hand claim; factual error; near-copy of another page; leftover placeholders; harmful YMYL advice; no title or several H1s |
| **P1** fix before publishing | Breaks the reader's trust or task | Load-bearing claim unsourced or sourced from a ✗-tier page; a source credited with something it doesn't say (other wording, wider scope, or another source's point); misses the search intent; misleading title; no meta description; heading levels skipped; images without alt text; no internal links |
| **P2** fix soon | Weakens the post | No clear gain; machine-written tells; a thin or padded section; weak anchor text; missing or mismatched schema; stale examples |
| **P3** polish | Nice to have | Rhythm, word choice, a better chart type |

**Bar for `write` and `rewrite`:** `check_post.py` reports 0 errors, there are
no P0 or P1 findings, and the score is 85 or more. A rewrite must also score
higher than the original did.

## Rubric (100 points)

**Content: 30**

| Check | Pts | Full marks when |
|---|---|---|
| Intent served | 8 | A reader with the query finishes with what they came for. Nothing essential is missing and nothing is padding |
| Gain | 7 | It contains something the top results don't: first-hand data, a worked example, a decision rule, or a better synthesis |
| Clarity for the audience | 6 | Density fits the reader (see [writing.md](writing.md#readability)); jargon is explained; every abstract claim has an example |
| Structure | 5 | Answer first; each H2 keeps its promise early; the right containers (lists, tables, prose) |
| Prose quality | 4 | No filler, no machine-written tells, no repetition |

**SEO: 25**

| Check | Pts | Full marks when |
|---|---|---|
| Title | 4 | Specific, accurate, topic early, about 60 chars or fewer, unique on the site |
| Meta description | 3 | 70 to 160 chars, says what the reader gets, and **every promise in it and in the title is kept in the body** ("four steps" means four steps; "tested on…" means the test is shown). A broken promise of experience is P0 |
| Headings | 4 | One H1, no skipped levels, descriptive H2s, and questions only where natural |
| Topic focus | 4 | One primary topic, consistent terms, no cannibalizing sibling posts |
| Internal links | 5 | 3 to 8, descriptive anchors, one early, pillar linked if the post is in a cluster |
| External links | 2 | Point to the primary sources of the claims |
| Slug | 3 | Short, readable, stable, no date on evergreen posts |

**Trust: 15**

| Check | Pts | Full marks when |
|---|---|---|
| Claims sourced and accurate | 6 | Every load-bearing claim is cited at the claim, to tier 1 or 2, with its scope kept |
| Author | 3 | Named byline, with a bio relevant to the topic |
| First-hand evidence | 3 | Any experience claimed is real and shown. Neutral, well-sourced explainers get full marks too |
| Transparency | 3 | Dates shown and truthful, disclosures present, self-promotion restrained |

**Technical: 15**

| Check | Pts | Full marks when |
|---|---|---|
| Images | 4 | Alt text that describes the image, stored locally with credits, sized, not lazy-loaded above the fold |
| Structured data | 4 | Valid JSON-LD that matches the visible content (see [seo.md](seo.md#structured-data)). N/A when the platform generates it |
| Frontmatter | 3 | Complete and consistent with sibling posts; `updated` is not earlier than `date` |
| Markup | 2 | Correct for the platform: MDX attributes, shortcodes, embeds |
| Performance hints | 2 | Images have dimensions, no heavy embeds above the fold. Live data is the `seo` skill's job |

**Answer-engine readiness: 15**

| Check | Pts | Full marks when |
|---|---|---|
| Self-contained sections | 5 | Each important section states its answer early and makes sense when quoted alone |
| Extractable formats | 4 | Steps, tables, definitions and comparisons where the content has that shape |
| Entity clarity | 3 | The subject is named explicitly, not as "it" or "this tool", and names stay consistent |
| Accessible text | 3 | Key content is in HTML text, not inside images, tabs or client-side-only JavaScript |

**Bands:** 90 or more, publish. 80 to 89, polish first. 70 to 79, targeted fixes.
60 to 69, rework. Below 60, rewrite from the outline.

## Focused modes

- **`--seo`** (on-page checklist): title, meta description, headings, slug,
  canonical, Open Graph and Twitter tags, internal and external links, image
  alt text, and schema. Return pass, fail or N/A for each, with the fix. Details
  are in [seo.md](seo.md).
- **`--geo`** (answer-engine readiness): a per-section table with columns
  *answer in first paragraph? / stands alone? / claim + source? / entity named?*,
  plus crawler access for live URLs. Give rewritten openers for the weakest
  sections. Don't promise citations by any AI product. This is readiness, not
  prediction.
- **`factcheck`**: below.

## Fact-check

1. **Extract every load-bearing claim:**
   - numbers and comparisons
   - superlatives ("first", "only", "fastest")
   - dates, prices and product capabilities
   - legal, medical and policy statements
   - quotes

   Record each claim's location.
2. **Check each cited claim:**
   - Fetch the cited page and find the figure in context.
   - If the page is itself a recap, trace the figure to the primary source.
   - Confirm the scope matches: population, timeframe, unit.
3. **Mark each claim with one status:**

| Status | Meaning |
|---|---|
| VERIFIED | Same figure, same scope, on the cited page |
| PARAPHRASE | Rounded or reworded but faithful ("nearly half" for 47%) |
| MISMATCH | Different number, scope, year or meaning. Give the correct figure |
| NOT FOUND | The page loads but the claim isn't on it |
| UNREACHABLE | 404, paywall, PDF or JavaScript-only. Say so; don't guess. Suggest the archive.org copy |
| UNSOURCED | No citation. Suggest where the primary source would be |
| WEAK SOURCE | Cited to a ✗-tier page or an echo of another source. Name the upstream source if found |

4. **Report the table and the fixes.** Change claims in the file only when the
   user asks, and list every change made.

## Report format

```markdown
## Review: <title>   <score>/100 (<band>)

| Category | Score | Note |
|---|---|---|
| Content | x/30 | |
| SEO | x/25 | |
| Trust | x/15 | |
| Technical | x/15 | (N/A: …) |
| Answer-engine readiness | x/15 | |

**Gain:** <what this post offers that the top results don't, or "none found">

### P0 / P1
- [P0] L42: "73% of marketers…" has no source; the nearest primary is <…>. Fix: …
### P2 / P3
- …

### Check output
<errors and warnings from check_post.py, summarized>

### Top three fixes
1. …
```

Batch mode: a table of file, score, the five category scores, and the top issue,
sorted lowest score first.

## Fresh-eyes reviewer brief

The author is the worst reviewer of their own draft. During `write` and
`rewrite`, run the review as a subagent when one is available, so the reviewer
hasn't seen the drafting:

```text
Review the blog post at [path] as a strict editor. Read reference/review.md and
reference/writing.md from [skill dir] and apply them. The intended reader is
[..]; the target query is [..]; the source ledger is below. Flag every number or
claim in the post that is not in the ledger, and every attribution ("X says…")
that goes beyond what X's ledger quote says. Return the report in the
review.md format, with line numbers and concrete fixes. Do not edit the file.

[source ledger]
```
