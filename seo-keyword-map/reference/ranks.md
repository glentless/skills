# Rank tracking

## Contents
- [What a check does](#what-a-check-does)
- [Choosing depth, passes and keywords](#choosing-depth-passes-and-keywords)
- [When and how often](#when-and-how-often)
- [Reading the report](#reading-the-report)
- [Switching from another tool](#switching-from-another-tool)

## What a check does

`ranks.py check` pulls Google's results for each tracked keyword from the same location
rules as `serp.py` (the place's own city, or the default city), finds the site's first
organic result, and records:
- the position (or nothing, if it isn't in the top `depth`)
- the URL that ranks, and the keyword's target page
- whether the site's Business Profile shows in the map pack (not an organic position, but
  for a local business often worth more than one)

It saves `<data_dir>/ranks/<date>.json` and adds a `Position <Mon D>` column to the Rank
tracker sheet (a number, or `—` for not in the top `depth`). A second check on the same
day overwrites that day's column. If the workbook is open, the check is kept and
`ranks.py sync` writes it once Excel is closed.

## Choosing depth, passes and keywords

| Setting | Default | Cost effect | When to change |
|---|---|---|---|
| `ranks.depth` | 50 | ~$0.0024/kw at 50, ~$0.0047 at 100 | 100 when a new site's pages sit between 50 and 100 and you want to see them climb |
| `ranks.passes` | 1 | × passes | 2 for client reports: low-volume local positions swing 10–40 places between checks an hour apart. Two passes are averaged, and keywords that disagree are flagged |
| `ranks.keywords` | `tracked` (the Rank tracker list) | × keywords | `primary` for a cheap weekly pulse (one keyword per page) |
| `--fast` | off | × 2 | When someone is waiting: minutes instead of up to an hour on the standard queue |

`--only "kw1,kw2"` checks a few keywords without touching the rest.

## When and how often

The user decides. Two ways, and both can be used together:

- **On demand.** "check rankings" whenever they want one: before a monthly report, after
  a batch of pages goes live.
- **On a schedule.** `ranks.py schedule --every daily|weekly|biweekly|monthly|quarterly`
  with `--day N` (monthly, quarterly), `--weekday MON..SUN` (weekly, biweekly) and
  `--time HH:MM`. Without `--yes` it only shows what it would create and what it costs per
  check and per year. On Windows it creates a Task Scheduler task running a launcher in
  `<data_dir>/ranks/`; elsewhere it prints a cron line to add. The cadence is saved in
  `seo-project.json`, so `status.py` says when a check is due, including when the
  computer was off and the scheduled run was missed.

Guidance to offer, not impose:
- Match the reporting period: a monthly report wants a monthly check on the period's last day.
- Weekly checks of `primary` keywords show trends cheaply; single monthly positions are noisy.
- Daily checks rarely pay for themselves on low-volume local keywords.

Scheduled runs respect the per-run cap: a check that would cost more is skipped and logged
to `<data_dir>/ranks/schedule.log`.

## Reading the report

`ranks.py report` compares with the previous check (or `--vs DATE`):
- counts in the top 3, 10, 20 and anywhere, for the same keywords both times
- gained and lost, biggest moves first
- **a different page ranks than the target**: either the target doesn't exist yet (fine),
  or two of the site's pages compete. That's a question for `group` and internal linking.
- **unstable** keywords (with passes ≥ 2): treat their moves as noise until they repeat

When summarising for a client, lead with counts and the pages that moved, not single
keyword swings.

## Switching from another tool

Positions from Semrush, Ahrefs or a manual check aren't comparable with these: different
locations, devices, dates and SERP handling. `report --vs-column "Position Sep 8"`
compares with a column already in the Rank tracker but prints a warning. When a project
switches source, start a new series: note the switch in the report, and compare like
with like from then on.
