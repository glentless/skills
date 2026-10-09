# DataForSEO

## Contents
- [Credentials](#credentials)
- [Spending](#spending)
- [Endpoints used](#endpoints-used)
- [Pitfalls](#pitfalls)

## Credentials

One shared company account. The login and API password live in a file **in each
person's user folder**, never in a project, this skill, a chat or a commit:

```bash
# macOS / Linux / Git Bash
printf 'DATAFORSEO_LOGIN=%s\nDATAFORSEO_PASSWORD=%s\n' 'LOGIN' 'API_PASSWORD' > ~/.dataforseo.env
chmod 600 ~/.dataforseo.env
```

```powershell
# Windows PowerShell
Set-Content -Path "$HOME\.dataforseo.env" -Value "DATAFORSEO_LOGIN=LOGIN`nDATAFORSEO_PASSWORD=API_PASSWORD"
```

The API password is the one under *API Access* in the DataForSEO dashboard, not the
website login password. The scripts also read the environment variables
`DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`, `~/.config/dataforseo/.env`, and
`~/.claude/skills/seo/.env` (used by other SEO skills), in that order after the
variables. They warn if a credentials file turns up inside a project or the skill.

If the password is ever pasted into a chat or a file that could be shared, change it in
the dashboard and update everyone's file.

## Spending

- Every paid script prints an estimate and stops if it is over the per-run cap
  (`budget.max_usd_per_run`, default $1.00) or the account balance. `--max-cost N`
  raises the cap for one run; only use it after the user agrees to the figure.
- Every paid call is logged to `<data_dir>/dataforseo-ledger.csv` in the project, so
  spend per client is visible. `status.py` shows the total.
- Typical costs for a 200-keyword local project: research ~$0.40, SERP pull (2 passes)
  ~$0.45, re-pull a quarter later ~$0.45, rank check ~$0.50 (depth 50, one pass) or
  ~$1.00 (two passes).

## Endpoints used

| Script | Endpoint | Price (Oct 2026, observed) |
|---|---|---|
| `serp.py pull`, `ranks.py check` | `serp/google/organic/task_post` + `task_get/advanced` (standard queue) | $0.0006 for the first 10 results + $0.00045 per further 10: ~$0.00105 at depth 20, ~$0.0024 at 50, ~$0.0047 at 100. `--fast` (priority queue) about doubles it. `task_get` is free: its `cost` field repeats the task's price |
| `research.py grid`, `volume` | `keywords_data/google_ads/search_volume/live` | ~$0.09 per call, up to 1,000 keywords |
| `research.py suggest` | `dataforseo_labs/google/keyword_suggestions/live` | $0.01 + $0.0001 per keyword returned |
| `research.py competitors` | `dataforseo_labs/google/ranked_keywords/live` | $0.01 + $0.0001 per keyword returned |
| all | `appendix/user_data` (balance) | free |

Locations: Labs and Ads use the country (`market.country`, e.g. `Canada`). SERPs use a
city (`market.default_serp_location`, or the place's entry in `places`), written as
DataForSEO names it: `Calgary,Alberta,Canada`.

## Pitfalls

- **Depth 20, not 10.** Depth counts every block on the page (map pack, AI overview,
  videos), so depth 10 returns only about 7 organic results.
- **One pull is not enough** for low-volume keywords: about half the top 10 changes
  between pulls. `serp.py` runs two passes 15 minutes apart and pools them.
- **Google Ads refuses** commas, most punctuation, over 10 words or over 80 characters,
  and one bad phrase fails the whole call. `research.py` filters them out and retries without
  any phrase Ads names.
- **Grouped volumes.** Ads and Labs give close variants the volume of their whole group
  ("plumber calgary" and "calgary plumbers" both get the group's figure). Never add
  variants up.
- **Ads charges per call**, not per keyword: batch everything into one call.
- **Labs "keyword ideas" drifts off topic** (category matching). Not used.
- **The live Ads endpoint occasionally returns an empty result**; the script retries.
- **Small places return nothing.** Under 20/mo for every service in a town is a real
  finding: those towns don't justify their own pages.
- **The site's own rank in a SERP pull** reflects one location and device at one time.
  Don't compare it with rank-tracker figures from another tool or location.

- **The standard queue can take an hour** at busy times (usually 1–5 minutes). Use
  `--fast` when someone is waiting; scheduled runs don't need it.
- **Don't add up `cost` from `task_get` responses**: it repeats the price of the task, which
  was charged once at `task_post` (checked against the balance, Oct 2026).
- **Positions swing between checks.** One keyword went from #2 to outside the top 50 in a
  day on a local SERP. Use 2 passes for anything reported to a client.

Add new pitfalls here with the date.
