# Site audit: health, cannibalization, decay, taxonomy, locales

## Contents

- [Run order](#run-order)
- [Cannibalization](#cannibalization)
- [Decay](#decay)
- [Taxonomy](#taxonomy)
- [Locale audit](#locale-audit)
- [Report](#report)

`audit [dir]` covers the whole blog. The subcommands `cannibalization`, `decay`,
`taxonomy` and `locales` run one section each.

## Run order

1. **Find the content.**
   - If BLOG.md names the content directory, use it.
   - Otherwise look in `content/`, `src/content/`, `posts/`, `_posts/` and
     `blog/`.
   - If you find none, ask. Never scan the whole repository.
2. **Inventory:**
   ```bash
   python scripts/check_post.py --site <dir> [--base-url https://example.com] [--stale-months 12]
   ```
   This gives, per post:
   - lint errors and warnings
   - inbound and outbound links between posts
   - orphans and dead ends
   - internal links that resolve to nothing
   - title overlaps
   - duplicate titles and descriptions
   - stale dates
   - tag and category health
   - languages

   Add `--json` to work with the data.
3. **Score posts with judgment, in proportion to the site's size:**
   - up to about 20 posts: review each one
   - larger sites: review the 10 posts with the most issues, the top-traffic
     posts if Search Console data exists, and a random sample of 5

   Use [review.md](review.md). The inventory finds problems; the review explains
   them.
4. **Run each section below that the data supports.**
5. **Report and save:** `reports/blog-audit-YYYY-MM-DD.md`. Never overwrite an
   earlier report.

For live-site technical checks (crawling, Core Web Vitals, robots, sitemaps,
redirects), hand off to the `seo` skill and link its report.

## Cannibalization

Two posts cannibalize each other when they target the same **intent**. Sharing
words is not enough.

1. **Candidates:** the `overlap_candidates` in the inventory (similar titles),
   plus any posts that declare the same `keyword`.
2. **Evidence that they really compete:**
   - **Best:** Search Console query-to-page data, in a Queries export filtered
     by page, or the API with `query,page` dimensions. The same query sending
     impressions to two or more URLs, with positions swapping, is
     cannibalization.
   - **Next best:** search the query and see whether both URLs, or neither,
     rank.
   - **With DataForSEO** (`seo-*` skills installed): ranked keywords per URL
     give the overlap directly.
3. **Decide what to do:**

| Situation | Action |
|---|---|
| Same intent, both thin | **Merge** the best of both into the stronger URL; 301 the other; update internal links |
| Same intent, one clearly stronger | **Redirect** the weaker to it, after moving anything unique across |
| Related but different intents | **Differentiate:** re-aim the weaker one's title, H1 and intro at its own query; cross-link them |
| One must stay for users but shouldn't rank | **Canonical** to the stronger URL (or `noindex`, rarely) |
| Different intent despite similar words | **No action**; note why |

Redirects and merges are destructive. Write the plan as a table (from URL, to
URL, what content moves) and get the user's approval before touching files.

## Decay

```bash
python scripts/decay.py <gsc-compare.csv>                 # one export with Compare dates
python scripts/decay.py current.csv previous.csv          # or two equal-length periods
```

**Get the data:** in Search Console, go to Performance, open the Pages tab,
choose Compare (last 3 months vs previous 3 months, or the same period a year
earlier for seasonal sites), and export as CSV. API JSON works too.

**Use an export only if its URLs belong to this blog.** Match the host and path
pattern against BLOG.md's URL pattern, or against the posts' slugs. Never fold
another property's numbers into this site's story. If nothing matches, say so
and ask for the right export.

The script lists pages that fell by 20% or more, by severity, and says what to
check first:

- **Impressions held, clicks fell:** the snippet or the results page changed
  (title, meta description, AI answers, new features). Fix the title and the
  answer-first opening.
- **Ranking fell:** refresh the content. Check whether the intent shifted and
  what the new top results do better.
- **Demand fell at a stable position:** probably seasonal or a market change.
  Compare year over year before editing anything.
- **Page dropped out:** confirm the export used the same filters, then check
  indexing, redirects and the canonical.

Queue the refreshes for `rewrite --update`, with the evidence. A falling graph
alone is not a reason to rewrite.

## Taxonomy

From the inventory:

- **Tags used once:** each one creates a thin archive page. Merge it into a
  broader tag, or drop it.
- **Merge candidates:** spelling and plural variants of the same tag, such as
  "cast iron" and "cast-iron".
- **Uncategorized posts:** give every post exactly one primary category.
- **Archive health:** check whether tag and category archive pages are indexed.
  Thin archives (fewer than about 5 posts) are better `noindex`ed or merged.

Targets: 5 to 10 broad categories, 3 to 8 tags per post, and tags that are reused
rather than invented per post. For `taxonomy suggest <file>`, propose 3 to 8 tags
drawn from the post's headings and recurring terms, **preferring tags the site
already uses**.

**Syncing to a CMS** (WordPress, Ghost, Shopify, Strapi, Sanity) is an outward
write:

1. Produce the mapping (old tag → new tag, per post) as a table.
2. Get approval.
3. Use the CMS API with credentials from environment variables.
4. Verify the result.

Watch for one difference: WordPress tags and categories are separate objects
referenced by ID, while Shopify article tags are plain strings.

## Locale audit

For multilingual blogs (see [multilingual.md](multilingual.md)):

1. **Coverage matrix:** source posts against languages, with missing
   translations marked.
2. **Parity:** each translation should have the same H2 count, images, charts
   and claims as its source. Expected length differences: German +20-30%,
   French and Spanish +10-15%, Japanese and Chinese -20-30%.
3. **SEO per locale:**
   - localized title, meta description, slug and alt text
   - `lang` or `inLanguage` set
   - canonical pointing to its own language URL
   - hreflang reciprocal and including `x-default`
4. **Staleness:** if the source was updated after the translation's
   `translatedDate`, the translation needs a refresh.

Output: the matrix, the issues by severity, and the exact command to fix each
one.

## Report

```markdown
# Blog audit: <site> (<date>)

## Summary
<N> posts. Biggest problems in one paragraph: what's hurting most, what to do first.

## Priority actions
| # | Action | Posts | Why | Effort |
|---|---|---|---|---|

## Findings
### Content quality: review scores (sampled or full), common P0/P1 patterns
### Links: orphans, dead ends, unresolved links, missing pillar links
### Cannibalization: confirmed pairs + decision
### Decay: decaying pages + first diagnosis
### Taxonomy: merges, thin archives, uncategorized
### Locales (if any)
### Technical: handed off to `seo` / not checked

## Inventory
<the check_post.py table>
```
