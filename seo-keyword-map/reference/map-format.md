# keyword-map.xlsx and the changes file

## Contents
- [Workbook](#workbook)
- [Columns](#columns)
- [Changes file](#changes-file)
- [What apply.py checks](#what-applypy-checks)

## Workbook

| Sheet | Holds |
|---|---|
| `Keyword map` | One row per keyword: which page it targets and in what role |
| `Rank tracker` | Column A the keyword, then one dated `Position <Mon D>` column per check. A number is a position, `—` means checked and not ranking, blank means not checked |
| `Draft list triage` | Every research candidate decided: Keyword, Volume, Disposition, Where it went, or why not |

Other sheets are left alone. If a project's headers differ, map them under `map.columns`
in `seo-project.json` (`{"Target page": "URL"}`) rather than renaming the client's sheet.

## Columns

| Column | Values | Set by |
|---|---|---|
| Service line | one of `service_lines` in the config | triage |
| Keyword | lower case | research |
| Volume | monthly searches, from a tool | research |
| Difficulty | 0–100, blank if unknown (never 0 for unknown) | research |
| Intent | `Local`, `Commercial`, `Informational` | triage |
| Cluster | short name of the page's topic | apply (from `pages`) |
| Current rank, Best competitor | legacy export data; not used by the scripts | — |
| Target page | URL path, e.g. `/drain-cleaning/` | group |
| Page exists | `Yes` / `No` | apply |
| Status | `Mapped to page`, `No page yet`, `Unmapped`, `Excluded` | apply |
| Priority | 1 build first … 3; from `priority_rules` for pages to build | apply |
| Action | the evidence and reason for this keyword's assignment | group / triage |
| Role | `Primary` (one per page), `Secondary`, `Support` | group |
| Cluster volume | total volume of the page's keywords | apply |
| Page type | `hub`, `service`, `location`, `post` | apply (from `pages`) |

## Changes file

JSON. Every key is optional. `apply.py changes.json --check` validates it and prints
the result per page; without `--check` it writes.

```json
{
  "note": "Regroup after the January SERP pull.",
  "pages": {
    "/drain-cleaning-calgary/": {"type": "location", "cluster": "Calgary drain cleaning"},
    "/how-much-does-drain-cleaning-cost/": {"type": "post", "cluster": "Drain cleaning cost", "priority": 2},
    "/plumbing/": {"type": "hub"}
  },
  "rename": {"/blog/drain-cleaning-cost/": "/how-much-does-drain-cleaning-cost/"},
  "assign": [
    {"keyword": "drain cleaning cost", "page": "/how-much-does-drain-cleaning-cost/", "role": "Primary",
     "note": "SERP 2026-01-15: ARTICLE; shares 0 with 'drain cleaning'. Cost guides rank, not service pages."},
    {"keyword": "drain cleaning calgary", "role": "Secondary"}
  ],
  "add": [
    {"keyword": "drain cleaning calgary", "volume": 210, "difficulty": 12, "service_line": "Drains",
     "intent": "Local", "page": "/drain-cleaning-calgary/", "role": "Primary",
     "note": "Added 2026-01-15, Google Ads volume via DataForSEO."}
  ],
  "exclude": [{"keyword": "plumber jobs calgary", "reason": "Careers intent"}],
  "triage": [
    {"keyword": "drain cleaning calgary", "volume": 210, "disposition": "Added to Keyword map", "reason": "/drain-cleaning-calgary/"},
    {"keyword": "drains cleaning calgary", "volume": 30, "disposition": "Folded into a kept term", "reason": "drain cleaning calgary"},
    {"keyword": "acme plumbing", "volume": 480, "disposition": "Removed", "reason": "Company or brand name"}
  ]
}
```

- `pages`: needed for every **new** page (with a `type`). Optional for existing pages,
  to set or change `type`, `cluster`, `priority` or `exists` (`true` once a page is
  published).
- `rename`: moves every keyword from one URL to another (e.g. when the live site's URL
  pattern differs from the plan).
- `assign`: existing keywords only. Omit `page` to keep it; `"page": null` unmaps it.
- `add`: new keywords only. Leave out `page` to add it as `Unmapped`.
- `exclude`: keeps the row (so it's never re-added) with Status `Excluded`.
- `triage`: appended to the triage sheet.

When a page goes live, set `"pages": {"/url/": {"exists": true}}`. Its keywords become
`Mapped to page`.

## What apply.py checks

Stops (nothing written):
- a keyword in `assign`/`exclude` that isn't in the map, or one in `add` that already is
- a page with zero or several Primary keywords
- a new page with no `type`, or a type outside `hub/service/location/post`
- a role outside `Primary/Secondary/Support`; a service line not in the config
- the workbook is open in Excel

Warns (still writes): a page under the volume floor; an existing page without a type;
a rename that matched nothing.

On write: backup `keyword-map-backup-<date>.xlsx`, Cluster volume and Priority
recomputed, new keywords appended to the Rank tracker, triage rows appended, summary
appended to `<data_dir>/map-changelog.md`.
