# Tutorial: keyword mapping for a client site

For someone running this for the first time. Claude reads it when a user asks "how do I
start", "how does this work" or seems new, and explains it in conversation.

## Contents
- [What this does](#what-this-does)
- [One-time setup on your computer](#one-time-setup-on-your-computer)
- [Starting a client project](#starting-a-client-project)
- [Every session: type "what now"](#every-session-type-what-now)
- [The steps](#the-steps)
- [Files in a project](#files-in-a-project)
- [When something goes wrong](#when-something-goes-wrong)
- [Words used](#words-used)

## What this does

It answers one question for a client's website: **which page should rank for which
search**, and which pages are missing. It does that from what Google actually shows,
and keeps the answer in one spreadsheet, `keyword-map.xlsx`, that drives what gets
written next.

```
research ──► triage ──► SERP pull ──► group ──► plan ──► brief ──► (seo-writing) ──► ranks
 find        keep or     see what      assign     next     one       writes the       on demand or
 keywords    remove      Google ranks  to pages   pages    page      page             on a schedule
```

You don't need to remember the order. In a project folder, type **what now** and it
tells you the next step.

## One-time setup on your computer

1. **Python 3.9 or newer** and one package:
   ```
   pip install openpyxl
   ```
2. **The DataForSEO login.** Ask your manager for the shared API login and password.
   Save them in your user folder, never in a project:
   ```powershell
   # Windows PowerShell
   Set-Content -Path "$HOME\.dataforseo.env" -Value "DATAFORSEO_LOGIN=the-login`nDATAFORSEO_PASSWORD=the-api-password"
   ```
   ```bash
   # macOS / Linux
   printf 'DATAFORSEO_LOGIN=%s\nDATAFORSEO_PASSWORD=%s\n' 'the-login' 'the-api-password' > ~/.dataforseo.env && chmod 600 ~/.dataforseo.env
   ```
   Never paste the password into a chat, a document or a project file.
3. **The skill.** Clone the skills repo once and link this skill into Claude Code (see
   the repo README). `git pull` in that folder later brings everyone's updates.

Check it worked: open Claude Code in any client project folder and type `what now`.

## Starting a client project

In the client's folder, say: **set this up as an SEO project for acme.ca**. You'll be
asked for:
- the domain, country and main city (where the business is, and where Google is checked from)
- 3–4 local competitors' websites
- the service lines (e.g. Plumbing, Drains)

That creates `seo-project.json` (the project's settings) and an empty
`keyword-map.xlsx`. Then go through the settings with Claude: the services in the words
customers use, the towns the client serves, competitor names, which pages to build
first. Those settings are what make the same skill fit a different client.

## Every session: type "what now"

It checks the project and answers with where things stand and **one** next step, its
cost, and what you'll decide. Then you say "go", or ask questions. Other things you
can type:

| You type | It does |
|---|---|
| `what now` · `where are we` · `help` | Status and the next step |
| `find keywords` · `/seo-keyword-map research` | Keyword research, one source at a time, cost stated first |
| `triage the keywords` | Goes through new candidates: keep, fold into a kept one, or remove |
| `pull the SERPs` | Checks Google for every keyword without data (20–30 min) |
| `group the keywords` | Decides which page each keyword belongs on, from the Google results |
| `what pages should we build next` · `/seo-keyword-map plan` | The next batch, with the page to copy for each |
| `write a brief for /some-page/` | A brief for that page, then `/seo-writing write <brief>` writes it |
| `regroup /some-page/` | Looks again at one page's keywords |
| `check rankings` | Where the site ranks now, and what moved since the last check |
| `check rankings every month on the 8th` (any day, week or cadence) | Shows the cost per check and per year, then sets it up when you agree |
| `stop the scheduled rank checks` | Back to checking only when you ask |

## The steps

| Step | What happens | Takes | Costs (typical) | You decide |
|---|---|---|---|---|
| research | Finds candidates: town × service volumes, competitors' rankings, suggestions, Google's related searches, any Semrush export | minutes | $0.10–0.40 | which sources; nothing else |
| triage | Each candidate: added, folded into a kept keyword, or removed with a reason. Recorded in the triage sheet so it's never redone | minutes | free | skim the kept list; say if a removal is wrong |
| serp | Pulls Google's top 10 twice per keyword and labels what kind of page ranks (service pages, articles, directories) | 20–30 min | ~$0.002 per keyword | nothing |
| group | Moves keywords between pages, creates new pages where Google shows a distinct need, merges where it doesn't. Every move has a note with the evidence | minutes | free | review the summary: new pages, changed main keywords, merges |
| plan | Lists the next pages to build in priority order, with keywords, FAQ questions and the existing page to copy as a template | seconds | free | which pages go into this month |
| brief | One page's brief: keywords and where they go, the page to copy, what ranks now, the client's page rules. seo-writing writes from it | seconds | free | answer what only the client knows |
| ranks | Checks positions (and map pack) for the tracked keywords, adds a column to the Rank tracker, reports what moved | 1–30 min (`--fast`: under a minute) | ~$0.50 per check for 200 keywords | when and how often, or only on demand |

**Writing service pages.** seo-writing is built for blog posts. A brief from this skill
tells it the page isn't a post, which live page's sections to copy, and the site's own
rules (`page_requirements` in the settings). Set those up once per client: which files
hold the brand, voice and client facts, how pages are laid out, what the client can't claim.

Every change to the spreadsheet is backed up first (`keyword-map-backup-<date>.xlsx`).

## Files in a project

| File | What it is |
|---|---|
| `seo-project.json` | Settings for this client. Change it when the client's services, towns or decisions change |
| `keyword-map.xlsx` | The map. **Close it in Excel before running any step that writes** |
| `<data folder>/serp/<date>.json` | What Google showed on that date |
| `<data folder>/research/candidates.csv` | Every keyword ever found, with source |
| `<data folder>/group-<date>.md`, `plan-<date>.md` | Reports from those steps |
| `<data folder>/map-changelog.md` | What changed in the map, when |
| `<data folder>/dataforseo-ledger.csv` | Every paid call, with cost |
| `<data folder>/ranks/<date>.json`, `ranks-report-<date>.md` | Each rank check and its report; `schedule.log` if checks are scheduled |
| `<briefs folder>/<page>.md` | Page briefs for seo-writing |

## When something goes wrong

| Message | Do |
|---|---|
| "is open in Excel" | Close the workbook (check the taskbar), run again |
| "over the per-run cap" | The step would cost more than the limit. Narrow it, or agree a higher figure |
| "credentials not found" / "401" | The `.dataforseo.env` file is missing or wrong: setup step 2 |
| "out of credit (402)" | Tell your manager: the shared account needs topping up |
| "No seo-project.json" | You're not in a client project folder, or it isn't set up yet |
| "N Primary keywords (needs exactly 1)" | A page has no main keyword, or two. Claude fixes the changes file |
| A town shows no volume | Real answer: too few searches there for its own page |
| A ranking jumped or vanished | Local positions swing; check again (or use 2 passes) before reporting it |
| "saved ... run ranks.py sync" | The rank check ran while the workbook was open. Close it, say "sync the rankings" |
| A scheduled check didn't happen | The computer was off or logged out. "what now" will say it's due |

## Words used

- **Keyword / search**: what people type into Google. **Volume**: searches per month.
- **SERP**: the Google results page for a search.
- **Target page**: the page that should rank for a keyword.
- **Primary**: the page's main keyword; it leads the page title and main heading. One per
  page. **Secondary**: the next most important. **Support**: worked into the copy.
- **Page type**: `hub` (overview of a service line), `service`, `location` (a service in
  one town), `post` (answers a question).
- **Priority**: 1 = build first.
- **Triage**: deciding which found keywords are worth keeping.
