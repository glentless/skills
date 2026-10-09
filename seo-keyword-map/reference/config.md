# seo-project.json

## Contents
- [Fields](#fields)
- [Page requirements](#page-requirements)
- [Regex fields](#regex-fields)
- [Adapting an existing project](#adapting-an-existing-project)

One per client project, at its root. Everything project-specific lives here, so the
skill itself never changes per client. `init_project.py` writes a starting copy from
`assets/seo-project.template.json`.

## Fields

| Field | Meaning | Example |
|---|---|---|
| `domain` | The client's domain, no scheme or www | `acme-plumbing.ca` |
| `market.country` | Country for volumes (Labs, Ads) | `Canada`, `United States` |
| `market.language_code` | | `en` |
| `market.device` | SERP device | `desktop` |
| `market.default_serp_location` | City SERPs are checked from (the client's home city) | `Calgary,Alberta,Canada` |
| `places` | Place name → its own SERP location, or `null` to use the default. A keyword naming a place with a location is checked from there | `{"calgary": "Calgary,Alberta,Canada", "airdrie": null}` |
| `service_lines` | Allowed values of the Service line column | `["Plumbing", "Drains"]` |
| `competitors` | 3–4 local competitor domains for `research.py competitors` | `["rivalplumbing.ca"]` |
| `competitor_brands` | Names to flag at triage (whole words) | `["rival", "roto"]` |
| `brand_patterns` | Regexes for company-name shapes | `["^\\w+ plumbing( ltd)?$"]` |
| `exclude_patterns` | Regexes flagged as never-a-prospect (jobs, courses) | `["\\bjobs?\\b", "salary"]` |
| `out_of_area_patterns` | Regexes for places the client doesn't serve; also drop matching FAQ questions | `["toronto", "\\bbc\\b"]` |
| `research.services` | Service phrases for the grid, in customers' words | `["drain cleaning", "water heater installation"]` |
| `research.places` | Places for the grid | `["calgary", "airdrie", "okotoks"]` |
| `min_volume` | Floor for a keyword to be worth triaging and for a page to be worth building | `20` |
| `batch_size` | Pages per batch in `plan.py` (the monthly delivery) | `4` |
| `map.path` / `map.sheet` | Workbook and sheet | `keyword-map.xlsx` / `Keyword map` |
| `map.rank_sheet` / `map.triage_sheet` | Other sheet names | `Rank tracker` / `Draft list triage` |
| `map.columns` | Rename standard columns to this workbook's headers | `{"Target page": "URL"}` |
| `data_dir` | Where snapshots, research, plans, ledger go | `seo-data` |
| `priority_rules` | First match sets Priority for pages to build: `service_line` (or `*`), `page_types` (or `["*"]`), `priority` | see below |
| `copy_from` | Template page per page type, plus `^regex` rules on the new URL, which win | `{"^/drain-": "/drain-cleaning/", "post": "/blog-sample/"}` |
| `url_conventions` | Free text Claude follows when naming new pages | `"Posts at /slug/, no /blog/"` |
| `classify.extra_org_patterns` | Government/association domains of this market (municipalities) | `["\\.ab\\.ca", "calgary\\.ca"]` |
| `classify.extra_directory_patterns` | Local directories missing from `assets/domain-classes.json` | `["localsearch\\.ca"]` |
| `budget.max_usd_per_run` | DataForSEO per-run cap | `1.0` |
| `ranks.depth` / `ranks.passes` / `ranks.keywords` | Rank check settings ([ranks](ranks.md)) | `50` / `1` / `tracked` |
| `ranks.frequency`, `day`, `weekday`, `time` | Written by `ranks.py schedule`; absent = checks only on demand | `monthly`, `8`, —, `09:00` |
| `briefs_dir` | Where `plan.py --brief` writes briefs | `briefs` |
| `page_requirements` | What every page brief must carry; see below | |
| `notes` | Client decisions that override the method. Claude reads this before grouping | `"Emergency plumbing gets its own page."` |

`priority_rules` example: one service line first, its posts second, everything else third:

```json
"priority_rules": [
  {"service_line": "Plumbing", "page_types": ["hub", "service", "location"], "priority": 1},
  {"service_line": "Plumbing", "page_types": ["post"], "priority": 2},
  {"service_line": "*", "page_types": ["*"], "priority": 3}
]
```

## Page requirements

What makes a service page on this site different from a blog post. `plan.py --brief` copies
it into every brief, so a general writing skill (seo-writing) writes to this site's rules.
Each key except `files` is a string or a list of strings.

```json
"page_requirements": {
  "files": ["BRAND.md", "VOICE.md", "content/_SPEC.md", "content/_CLIENT-BRIEF.md"],
  "all": ["The client brief is the authority on what the business sells and claims; never claim more."],
  "service": "Same sections and word counts as the page being copied, block by block, so it pastes into the page builder.",
  "location": "Lead with what is true only in this place (permits, local rules). Nothing may repeat another city page.",
  "post": "Posts live at /slug/."
}
```

Ask the user for these the first time a brief is needed; don't guess them.

## Regex fields

`brand_patterns`, `exclude_patterns`, `out_of_area_patterns` and `classify.*` are Python
regexes matched against lower-case text. In JSON every backslash is doubled: write
`"\\bjobs?\\b"`, not `"\bjobs?\b"` (that is a backspace character and silently matches
nothing). Test one with:

```bash
python -c "import json,re; p=json.load(open('seo-project.json'))['exclude_patterns']; print([x for x in p if re.search(x, 'plumber jobs calgary')])"
```

## Adapting an existing project

- Workbook already exists in another shape: set `map.path`, `map.sheet` and
  `map.columns`; `init_project.py` then checks the columns and names any missing.
  `apply.py` adds a `Page type` column on its first write if there isn't one.
- Existing SERP or research data elsewhere: point `data_dir` at the folder holding it;
  snapshots are read from `<data_dir>/serp/*.json`.
