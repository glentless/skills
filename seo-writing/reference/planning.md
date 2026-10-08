# Planning: briefs, outlines, strategy, calendars, clusters

## Contents

- [Brief](#brief)
- [Outline](#outline)
- [Strategy](#strategy)
- [Calendar](#calendar)
- [Cluster plan](#cluster-plan)
- [Cluster execute](#cluster-execute)

Every plan starts from BLOG.md (audience, scope, voice) and a scan of what the
site already has: `python scripts/check_post.py --site <content dir>`. Don't plan
a post the site already has. Plan its refresh instead.

## Brief

A brief is everything a writer needs to produce the post without asking anything
else. Run the research first ([research.md](research.md)), then save the brief to
`briefs/<slug>.md` or wherever BLOG.md says. `write` consumes it directly.

```markdown
# Brief: <working title>
Reader: <who, what they already know, what they're trying to do>
Query and intent: <primary query> (informational | commercial | transactional) + 3-5 related queries and questions
Template: <name> and why
Gain: <what this post will have that the top results don't>, and what we need from the user to deliver it
Title options: 3      Meta description draft: 1
Length: <planning estimate from the template, adjusted to what top results need>

## What page one does
Table stakes: …   Gaps: …   Formats ranking: …   Freshest: <date>

## Outline
H2s with one line each on what the section must establish, and evidence row numbers from the ledger.

## Evidence
<source ledger, or the rows that matter>

## Visuals
Cover concept · charts (data rows) · screenshots to take

## Links
Internal links out: <existing posts + anchors>   Posts to link back: <existing posts>
Cluster: <pillar / spoke / standalone>

## Distribution (optional)
Channels from repurpose.md worth using for this post, with the angle for each
```

## Outline

An outline is the lighter version: title options, a one-line intent statement,
H2 and H3 headings, each with the point it must make and the evidence or visual
it needs, plus the gaps in page one that the post fills. Base it on a quick SERP
read. Save it to `outlines/<slug>.md` when asked to keep it.

## Strategy

`plan strategy <niche or site>` produces the positioning and content
architecture.

1. **Discovery.** Ask only what BLOG.md and the site don't already answer:
   - business goal for the blog (leads, authority, sales, audience)
   - who the readers are and what they search
   - competitors
   - unique expertise or data the business has
   - publishing capacity
2. **Competitive read.** For 3 to 5 competitors' blogs, note:
   - topics and formats
   - cadence and freshness
   - where they're thin
   - what makes their best posts work
3. **Audience segments**, 2 or 3 of them. For each: job, problems, how they
   search and ask, and their stage (learning, comparing, buying).
4. **Pillars**, 3 to 5. Each pillar is a topic the business has a right to own,
   with a hub page and 6 to 12 spoke topics. Give each spoke a template, a
   primary query and an intent. Every spoke has a distinct intent: no two posts
   compete for one query.
5. **Gain plan.** What original material can feed the content: data, case
   studies, expert access, tools, opinions. Content without a gain source
   becomes commodity. Say so.
6. **Distribution.** Name 2 or 3 channels where the audience already is (see
   [repurpose.md](repurpose.md)). Pick them for audience fit, not to chase AI
   citations.
7. **Measurement.**
   - Search: clicks, impressions and positions per cluster in Search Console.
   - Business: conversions from blog sessions.
   - Quality: the review score at publish.
   - Answer engines: AI referral sessions, segmented in analytics by source
     (chatgpt.com, perplexity.ai and so on), plus a monthly manual check of 10
     to 20 target questions in the main AI assistants. Record whether the site
     is cited.
8. **90-day roadmap:** foundation (pillar plus its first spokes), expansion,
   then optimization (refresh the posts that are decaying or underperforming).

Save it as `strategy/<yyyy-mm>-strategy.md`. Next steps: `plan calendar`, then
`plan cluster` for the first pillar.

## Calendar

`plan calendar [month|quarter]`

1. **Inputs:**
   - cadence, from BLOG.md, or ask; a sustainable 1 post a week beats an
     abandoned 3
   - the strategy's clusters
   - the site inventory, for refresh candidates
   - `decay.py` output, if Search Console data exists
2. **Mix**, as a starting point: about 60% new posts, 30% substantive refreshes,
   10% repurposed. Shift toward refreshes when decay is high.
3. **Order:**
   - Finish a cluster before starting the next one.
   - Publish the pillar first, or early, so spokes have something to link to.
   - Place seasonal topics 4 to 6 weeks before their peak.
   - Check upcoming industry events and report releases with a quick search
     rather than from memory.
4. **Format** (one table per week):

```markdown
| Date | Type (new/refresh/repurpose) | Working title | Template | Cluster | Primary query | Owner | Status |
```

Add a refresh queue showing each refresh's evidence (what changed: facts,
product, intent, traffic) and a cluster progress table (spokes published out of
spokes planned). Save it as `calendars/<yyyy-mm>.md`.

## Cluster plan

`plan cluster <seed>` builds a hub-and-spoke plan from a seed topic.

1. **Expand the seed into 30 to 50 queries.** Use the SERP, People Also Ask,
   related searches, and modifier variants:
   - "best", "vs", "for <audience>"
   - "how to", "what is"
   - "examples", "tools", "pricing"
   - "not working"

   Use `seo-keywords` when it's available, for volume.
2. **Group the queries by intent.** Two queries belong in one post when their
   top-10 results overlap heavily (about 4 or more shared URLs) or when they ask
   the same question. Each group becomes one post. Each post gets one primary
   query, and no other post in the cluster targets it.
3. **Shape the cluster:**
   - one pillar on the broadest query
   - 5 to 15 spokes
   - each spoke links up to the pillar and across to 2 or 3 related spokes
   - the pillar links down to every spoke
   - every post has at least two inbound links
4. **Write `cluster-<seed-slug>/cluster-plan.json`:**

```json
{
  "seed": "…",
  "pillar": {"id": "P", "title": "…", "query": "…", "template": "pillar", "slug": "…"},
  "spokes": [
    {"id": "S1", "title": "…", "query": "…", "intent": "informational", "template": "how-to",
     "slug": "…", "links_to": ["P", "S2"], "status": "planned"}
  ]
}
```

5. **Show the plan as a table:** id, title, query, template and links. Wait for
   approval before writing anything.

If a strategy document already has a cluster table, import it, check its
groupings against the SERP, and point out any conflicts. Don't silently
override the user's choices.

## Cluster execute

`cluster execute [plan path]` writes the posts in the plan. This is a batch, so
it gets batch discipline.

1. **Order:** the pillar first, then spokes, alternating between sub-themes.
2. **Write each post with the full `write` workflow.** Don't stop for outline
   approval, since the plan was approved. Every post still passes the shipping
   bar: research, verified evidence, `check_post.py` clean, and the review.
   Prepend a cluster context block: cluster name, the post's role, its query,
   the posts already written (link to these with their real paths), and the
   upcoming posts (use placeholders).
3. **After each post, resolve links.** Replace placeholders in earlier posts
   that point to the post just written. Set `status` in the plan.
4. **Stop the batch on the first post that fails the bar.** Report it, and
   resume only when the user says. Generating a dozen weak posts in a row is
   the scaled-content pattern search engines demote.
5. **Finish:**
   - Run `check_post.py --site` on the cluster directory: no orphans, no
     unresolved placeholders, no overlapping titles.
   - Write `cluster-scorecard.md`: each post's score and links, plus anything
     left to do.

Resume an interrupted run from the `status` fields.
