# Changelog

Bump `version` in SKILL.md with each entry. Lessons about the method go in
`reference/method.md#lessons`; API pitfalls in `reference/dataforseo.md#pitfalls`.

## 0.2.1 — 2026-10-10

- Briefs check the primary keyword against page-one titles in the raw SERP results. When
  no ranking title uses the exact phrase, the brief says to put a natural form in the
  title and H1 (quoting the closest ranking titles) and the exact phrase once in the
  description or body. Otherwise it gives the strict rule with the count of titles using it.

## 0.2.0 — 2026-10-09

- research.md: read flagged rows before removing (brand patterns over-reach); the 'near me' removal reason; add a volume-bearing variant when the kept keyword has none. From the first real triage (320 candidates).

- Rank tracking (`ranks.py`): check on demand or on a schedule the user picks (daily to
  quarterly; Windows Task Scheduler or a cron line), averaged passes with unstable
  positions flagged, map-pack presence, "a different page ranks than the target", reports
  against the last check or an existing Rank tracker column. Checks made while Excel is
  open are kept and synced later. `status.py` says when a scheduled check is due.
- Page briefs (`plan.py --brief /url/`) in seo-writing's brief format, carrying the
  project's `page_requirements`, so service and location pages can be written with
  seo-writing.
- `--fast` (priority queue) for SERP pulls and rank checks.
- Fixed: the ledger counted `task_get` responses as spend (they repeat the task's price).
- Fixed: Git Bash on Windows turning `/page/` arguments into file paths.
- Console output is UTF-8 on Windows.

## 0.1.0 — 2026-10-09

First version, extracted from a local-services keyword-map rework.

- `status.py` ("what now"), `init_project.py`, `research.py` (grid, suggest, competitors,
  harvest, volume, import, review), `serp.py` (pull with two pooled passes, classify by
  page type), `group.py` (evidence report), `apply.py` (validated writes with backup),
  `plan.py` (next batch, page to copy, FAQ questions).
- Method: split by SERP page type first, non-homepage URL overlap second.
- Spending cap per run and a per-project ledger for the shared DataForSEO account.
- Synthetic eval fixture and six scenarios (not yet run by an agent).
