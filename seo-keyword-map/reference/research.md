# Keyword research and triage

## Contents
- [What each source is good for](#what-each-source-is-good-for)
- [Order](#order)
- [Triage](#triage)
- [Triage examples](#triage-examples)

## What each source is good for

| Source | Command | Finds | Watch out for | Cost |
|---|---|---|---|---|
| Service × place grid | `research.py grid` | Exact local phrases ("drain cleaning calgary") with Google Ads volume. The most reliable volumes you can get. | Small towns come back empty or under 20: that is a real answer, not a failure. Ads groups close variants and gives them all the group's volume, so never add variants together. | ~$0.09 per call of up to 1,000 phrases |
| Competitors | `research.py competitors` | What 3–4 local competitors rank for in the top 30, including terms nobody would think to seed | Competitors that serve other regions bring their cities in; their brand names and staff names show up. Flags catch most. | ~$0.04 per domain at `--limit 300` |
| Suggestions | `research.py suggest SEED` | Longer phrases containing a seed ("lot grading" → "lot grading certificate cost") | Country-level data: thin for small cities and new phrasing. | ~$0.02 per seed |
| Related searches | `research.py harvest` | Google's own "related searches" from every SERP already pulled: local phrasing, adjacent needs | Free but noisy: brands, job boards, government services. Needs a `volume` pass. `--paa` adds People-also-ask questions, which are usually zero-volume and better used as FAQ material. | free, then volume |
| Exports | `research.py import FILE` | Anything from Semrush, Ahrefs or Search Console (CSV/XLSX with a Keyword or Query column) | A Semrush gap export only lists what the chosen competitors rank for, and stops at its row cap. Search Console impressions are not search volume. | free |
| Volume | `research.py volume --missing` | Google Ads volume for candidates without one | Ads refuses phrases with punctuation or over 10 words; the script skips them. | ~$0.09 per 1,000 |

Do not use DataForSEO Labs "keyword ideas": it matches on category, not meaning, and
for a city-qualified seed returned home shows and home inspectors. Suggestions and
competitor rankings stay on topic.

What DataForSEO can't tell you: whether the client sells the thing. "final grading"
returns landscapers too; only the client's service list says whether a surveyor's
grade certificate is the same need. Check the project's service notes before keeping a
keyword whose SERP shows other trades.

## Order

For a new project, stating each estimate before running it:

1. `grid` with the config's `research.services` × `research.places`. Fix the lists
   first: services in the words customers use, places the client really serves.
2. `competitors` for the 3–4 local competitors in the config.
3. `suggest` on the 5–10 core service phrases (no place names; the grid covers those).
4. `import` any exports the user already has.
5. `volume --missing`, then `review`, then [triage](#triage).
6. After the first `serp pull` and `classify`: `harvest`, `volume --missing`, `review`,
   triage again. Related searches surface local phrasing the other sources miss.

For an existing project, `status.py` says which of these is due.

## Triage

`research.py review` lists candidates at or over the floor that are not yet in the map
or the triage sheet, with flags. Decide each one, and record **every** decision in the
changes file's `triage` list with a reason, so it is never re-triaged:

| Disposition | When | Also |
|---|---|---|
| `Added to Keyword map` | Someone searching it could buy from this business, in its service area, and it is not just a variant of a kept keyword | Put it under `add` with `service_line`, `intent`, `volume`, `difficulty`. Give a `page` only when obvious; otherwise leave it Unmapped for `group`. |
| `Folded into a kept term` | A close variant (plural, word order, typo, extra filler) of a keyword already kept | Reason names the kept keyword. Not added: the kept keyword's page covers it. |
| `Removed` | Fails one of the tests below | Reason uses one of the standard phrases below. |

Standard reasons for `Removed` (consistent wording keeps the sheet scannable):
- `Careers, licensing or education intent, not a prospect` (jobs, salary, courses, degrees)
- `Company or brand name` (competitors, suppliers, unrelated firms)
- `Outside the service area`
- `Different trade or DIY, not this service` (landscaping, equipment sales, products)
- `Navigational to a government or association service` (zoning maps, city portals),
  unless the business sells help with that process
- `Dictionary or general-knowledge intent with no path to the service`
- `Under the volume floor`
- `'Near me' query: answered by the Google Business Profile, not a page`

**Read flagged rows before removing them.** Flags are hints. Brand patterns over-reach:
`^\w+ surveys` flagged "property surveys cost", and a competitor called "Geodetic" flagged
"geodetic elevation". Write brand patterns narrowly (`surveys? (inc|ltd)`, full firm names).

**When a variant carries the volume and the kept keyword doesn't** (a map keyword with no
volume, its reordered twin at 480/mo), add the variant rather than folding it, and say so
in the note: the volume has to be on a row for the page to be prioritised.

Informational keywords are **not** a reason to remove. "how much does X cost", "what is
X", "X vs Y" near the business's services are post candidates: add them.

`intent` values: `Local` (place named or local pack), `Commercial`, `Informational`.

## Triage examples

| Candidate | Decision | Why |
|---|---|---|
| plumber calgary jobs (390) | Removed: Careers… | job seekers |
| acme plumbing reviews (210) | Removed: Company or brand name | a competitor |
| drain cleaning cost (320) | Added (Informational) | cost post candidate |
| drains cleaning calgary (30) | Folded into "drain cleaning calgary" | word-form variant |
| calgary zoning map (880) | Removed: Navigational to a government service | the city's own tool |
| final grading calgary (210) | Added (Local) | client sells grade certificates; SERP mixes city pages and landscapers, check at `group` |
