---
name: seo-keyword-map
description: Plans which page of a site should rank for which keyword, using real Google results. Finds keywords through DataForSEO (service x place volume grid, competitor rankings, suggestions, related searches) and imported Semrush exports, pulls and classifies SERPs, groups keywords into landing pages and posts by the kind of page Google ranks, maintains keyword-map.xlsx (target page, role, priority, rank tracker), tracks rankings on demand or on a schedule the user picks, lists the next pages to build with the existing page to copy, and writes page briefs for the seo-writing skill. Use in an SEO client project for keyword research, keyword mapping, keyword grouping or clustering, rank tracking, cannibalization between pages, deciding which pages to build next, briefing a service page, or when someone asks "what now", "what's next", "how do I start", "where are we" or "help" in a folder with seo-project.json. Triggers on "/seo-keyword-map <command>".
version: 0.2.1
user-invocable: true
argument-hint: "[start|init|research|triage|serp|group|plan|brief|ranks|apply] [details]"
license: MIT
---

# SEO keyword map

Decides which page should rank for which keyword, from what Google actually shows, and
keeps that decision in one workbook the whole team works from: `keyword-map.xlsx`. One
page per distinct search need. A need is distinct when Google answers it with a
different kind of page, not when the words differ.

Paths below are relative to this skill's directory. Run every script **from the client
project folder** (the one holding `seo-project.json`); they find the config by walking
up. Python 3.9+ and `openpyxl` (`pip install openpyxl`). Use `python3` on macOS/Linux.

## Rules that always apply

1. **Credentials MUST NOT go in a project, this skill, a commit, or a reply.** They live
   in `~/.dataforseo.env` (see [dataforseo](reference/dataforseo.md#credentials)). The
   account is shared, so never print, echo or paste the login or password.
2. **Say the cost before every paid step**, from the script's estimate. The scripts stop
   at the per-run cap in `seo-project.json`. Raise it with `--max-cost` only when the user
   says yes to the figure.
3. **The workbook is only changed through `apply.py`.** Write a changes file, run
   `apply.py changes.json --check`, fix every error, then run it without `--check`. Never
   edit `keyword-map.xlsx` with ad-hoc openpyxl code: `apply.py` is what keeps backups,
   one Primary per page, cluster volumes, priorities and the Rank tracker in step.
4. **Excel must be closed** before any write. The scripts check and stop; ask the user to
   close it rather than working around it.
5. **No invented numbers.** Volumes come from a tool and the `Action` note says which.
   When a decision rests on judgment rather than data, the note says that too.
6. **Client decisions win.** `notes` in `seo-project.json` records them (e.g. "emergency
   plumbing gets its own page even though it shares results with the repairs page"). Follow them even where [method](reference/method.md) would
   decide otherwise, and record any new one there.

## Start here: "what now", "how do I start", "help"

Run `python scripts/status.py` (add `--balance` to include the account balance). Then
tell the user, in plain words:
- where the project stands (one or two lines, not the raw output)
- the one next step, what it costs, and what they will be asked to decide
- the command to type, as status.py prints it

If the user is new to this, or asks how it works, read
[tutorial](reference/tutorial.md) and walk them through it in their words. Don't paste
it.

## Commands

| Command | Does | Run | Read first |
|---|---|---|---|
| `start` (also "what now", "help", no command) | Status and the next step | `status.py` | [tutorial](reference/tutorial.md) if they're new |
| `init` | Set a folder up as an SEO project | `init_project.py` | [config](reference/config.md) |
| `research [grid\|competitors\|suggest\|harvest\|import\|volume]` | Find keyword candidates | `research.py` | [research](reference/research.md), [dataforseo](reference/dataforseo.md) |
| `triage` | Decide add / fold / remove for each candidate | `research.py review`, then `apply.py` | [research](reference/research.md#triage) |
| `serp [--stale\|--all]` | Pull and classify Google results | `serp.py pull`, `serp.py classify` | [dataforseo](reference/dataforseo.md) |
| `group [/page/]` | Assign keywords to pages from the SERP evidence | `group.py`, then `apply.py` | [method](reference/method.md), [map-format](reference/map-format.md) |
| `plan [N]` | The next pages to build, with the page to copy | `plan.py` | — |
| `brief /page/` | A writing brief for one page, for seo-writing | `plan.py --brief` | [config](reference/config.md#page-requirements) |
| `ranks [check\|report\|schedule\|unschedule\|sync]` | Where the site ranks, now or on a schedule | `ranks.py` | [ranks](reference/ranks.md) |
| `apply FILE` | Validate and write a changes file | `apply.py` | [map-format](reference/map-format.md) |

With no command, infer it from the request. Ask only if two readings would lead to
different work.

## init

Ask the user once for: domain, country, the main city (its SERP location, e.g.
`Calgary,Alberta,Canada`), 3–4 local competitor domains, and the service lines. Run:

```
python scripts/init_project.py --domain acme.ca --country Canada --city "Calgary,Alberta,Canada" --competitors a.ca,b.ca --service-lines "Plumbing,Drains"
```

Then fill the rest of `seo-project.json` with them: `research.services`, the places
they serve (and which have their own SERP location), `competitor_brands`,
`out_of_area_patterns`, `priority_rules`, `url_conventions`, `copy_from`. If an existing
keyword map is in another shape, map its headers under `map.columns` instead of
rebuilding it. See [config](reference/config.md).

## research → triage

1. Run the sources in the order [research](reference/research.md#order) gives, stating
   each estimate first. `research.py review` writes `research/review-<date>.md`.
2. Triage every row by [the triage rules](reference/research.md#triage). Write the
   result as a changes file: kept keywords under `add` (with `service_line`, `intent`,
   and `page` only when the page is obvious; otherwise leave it out so the keyword is
   Unmapped), and **every** decision, kept or not, under `triage` with its reason.
3. `apply.py changes.json --check`, fix, apply. Report: kept, folded, removed, with the
   biggest kept keywords named.

## serp

`python scripts/serp.py pull` pulls keywords with no SERP data (`--keywords stale` for
data over 120 days old, `--keywords all` to refresh everything). It runs two passes
15 minutes apart, so it takes 20–30 minutes: run it in the background and tell the
user. Then `python scripts/serp.py classify`.

## group

1. `python scripts/group.py` writes `group-<date>.md` in the data folder: per page, each
   keyword's SERP type, page-type mix and nearest neighbours, plus flags, merge candidates
   and unmapped keywords.
2. Work through it with [method](reference/method.md): every flag gets a decision, even
   if the decision is "keep, because…". Write the changes file per
   [map-format](reference/map-format.md). Every moved keyword gets a `note` with its
   evidence.
3. `apply.py --check`. Show the user the per-page result it prints, summarised: new pages,
   pages whose Primary changed, merges. Apply when they agree, or straight away if they
   said they don't need to review.

## plan

`python scripts/plan.py` (or `--count N`) lists the next batch and writes
`plan-<date>.md` with each page's keywords, People-also-ask questions and the page to copy.
The copy suggestion is a word-overlap score: check it makes sense, and add a `copy_from`
rule to the config when it doesn't.

## brief: writing a page

`python scripts/plan.py --brief /page/` writes `<briefs_dir>/<slug>.md` in the shape
`seo-writing write` consumes. For a service or location page it says plainly that the page
is **not a blog post**, names the live page whose sections to copy, and carries the
project's `page_requirements` (brand and voice files, layout rules, what the client can
and can't claim). Then hand over: `/seo-writing write <brief path>`.

If the project has no `page_requirements` yet, ask the user once for them (which files
hold the brand, voice and client facts; how pages are laid out; what to never claim) and
add them to `seo-project.json` before writing the brief. Don't guess them.

## ranks

Rankings are checked only when the user asks, or on the schedule they choose. Never
create a schedule they didn't ask for. Details in [ranks](reference/ranks.md).

- "check rankings": `ranks.py check`, state the estimate first. Then `ranks.py report`
  and summarise: top-10 count, biggest gains and losses, map pack, and keywords where a
  different page ranks than the target (a grouping question for `group`).
- "check rankings every month on the 8th" (any cadence): run `ranks.py schedule --every
  monthly --day 8` without `--yes` first, tell the user the cost per check and per year,
  and create it with `--yes` when they agree. `ranks.py unschedule --yes` stops it.
- If a check ran while the workbook was open, `ranks.py sync` writes it in later.
- Don't compare positions from this tool with figures from another tool or location as if
  they were the same series. Say so when a report crosses sources (`--vs-column`).

## Improving this skill

- New lesson from a project (a rule that was wrong, a pitfall): add it to
  [method](reference/method.md#lessons) or [dataforseo](reference/dataforseo.md#pitfalls)
  with the date, and a line in `CHANGELOG.md`. Bump `version` above.
- Project-specific tweaks go in that project's `seo-project.json`, never here.
- After a change to the rules, re-run the scenarios in `evals/evals.json` on the
  synthetic fixture and note the result in `evals/RESULTS.md`. Client data never goes in
  `evals/`: this repo is public.
