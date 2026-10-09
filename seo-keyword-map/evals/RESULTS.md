# Eval results

## 2026-10-09: v0.1.0, scripts only

The scenarios in `evals.json` have not yet been run end to end by a fresh agent. What was
tested:

- Every script on the synthetic fixture (`make_fixture.py`): status, group, research
  review, plan, apply `--check` (including a deliberate two-Primary error, which stopped
  with a specific message), and apply. The grouping report flagged both service pages
  holding ARTICLE keywords, the association-led keyword, and the cost-post merge (7 shared
  results).
- Every script on a real 205-keyword local-services project: SERP classify on two pooled
  passes, group, research (grid, suggest, competitors, harvest, volume, import, review),
  plan, apply. The apply output reproduced the hand-made mapping exactly.

Bugs found and fixed while testing:
- Raw SERP files for "as built" and "as-built" collided on one file name; names now carry a hash.
- One phrase with a comma made Google Ads reject a 1,000-keyword call, and the script then
  recorded 0 volume for all of them. It now drops phrases Ads names and retries, and only
  writes volumes Ads returned.
- A keyword moved from a live page into a planned post made the post look live. Page
  status now comes from the page, not the keyword.
- Homepages of the same few local firms made unrelated services look like one query;
  they are now left out of the overlap.

To do: run the scenarios with the skill and without it (baseline), on Opus, Sonnet
and Haiku, and record the results here.
