# Eval results

## 2026-10-08: first run (v3.0.0)

Each scenario in `evals.json` was run by a fresh agent in its own copy of
`fixtures/`, once following the skill and once with skills forbidden
(baseline). The main model was Opus 5.5; two scenarios were also run on Haiku 4.5
with the skill.

| Scenario | With skill | Baseline | Verdict |
|---|---|---|---|
| write | 91/100 after 2 review rounds, 0 lint errors and 0 warnings. 7 sources (4 primary), each quote checked against the page's HTML. Rejected an unattributed "lab study of 120 pans". Credited cover image, back-links listed, first-hand gap flagged | Clean post, 0 lint errors. Sourced, correct summary label, answer first. No image, no review pass | Skill slightly better on rigour. About 4x the time (15 min vs 3.5) and 2x the tokens |
| review | P0–P3 findings with line numbers and concrete fixes. Caught the duplicate H1. Scaled N/A categories | Found every planted defect, but no severity ranking, and it recommended adding an FAQ "for featured snippets", which is outdated | Skill better |
| audit | Scored each post. Found the unsourced 80%, broken description promises, orphan, broken link, merge plan held for approval. Saved the report. Refused the mismatched GSC data | Equally thorough. Also found the missing `/images/rinse.jpg` | Tie. The missing-image check has since been added to `check_post.py` |
| decay | Correct diagnosis for every page, /e excluded | Same | Tie. The skill adds a fixed tool and format, not insight |
| review without testing | Run failed (API rate limit) | Refused to invent testing and left `[TESTING NOTE]` slots. Confounded: the fixture's BLOG.md states the rule | Re-run with a fixture whose BLOG.md doesn't state the rule |
| review (Haiku, skill) | Ran the checker and caught every blocker. Thinner fixes than Opus | – | OK |
| audit (Haiku, skill) | Ran the inventory and saved the report, but folded the unrelated GSC export into the site's story | – | Fixed: site-audit.md now requires GSC URLs to match the site |

### Changes made from this run

- `check_post.py`: line numbers were one too low after frontmatter (found by
  the review agent). It now also warns about local images and frontmatter
  covers that don't exist.
- `review.md`: the title and description must keep their promises in the body;
  a broken experience claim is P0.
- `site-audit.md`: use a Search Console export only if its URLs belong to the
  blog.
- `fixtures/site/BLOG.md`: content paths made relative, since they confused
  agents.
- Review rounds (from the timing analysis below): the second round now runs
  only when the first finds a P0 or P1. Crediting a source with something it
  doesn't say is now P1, and the reviewer brief asks for attribution checks.

### Where the write run's 15 minutes went

| Phase | Time | Found |
|---|---|---|
| Research A (sources and ledger) | 3 min, in parallel with B | 7 sources, the fake "120 pans" study rejected |
| Research B (results page and forums) | 8 min | Gaps and reader vocabulary |
| Review round 1 | 1.5 min | 86/100: 3 P1s, all claims missing from the ledger |
| Fixes, then review round 2 | 3.5 min | 91/100: no P1, but **two claims credited to Field Company that it never makes**, and an intro that blamed water for seasoning loss instead of rust |

The second round is worth keeping: it caught misattributions the first round
missed, and a post that has just been patched needs someone to check the patch.
It cost about 2 minutes. The earlier guess that it doubled the cost was wrong:
research B is the slow step.

### Takeaways

- On Opus, the skill's advantage is consistency and rigour (a severity
  ranking, verified quotes, a review loop, an image with credit), not raw
  capability. The baseline is strong.
- The second review round is cheap and useful when round 1 finds P0 or P1
  problems; it's skipped otherwise. Most of the time goes on results-page and
  forum research.
- Haiku follows the workflow but needs explicit guard rails on data scoping.

## 2026-10-08: Sonnet 5.5 on the write scenario

The same write task ran on Sonnet 5.5, with Sonnet for every subagent too. One
Opus judge then scored all three posts under neutral file names, fetching every
cited page to check each quote.

| Run | Time | Tokens | Steps followed | Judge score | Attribution errors |
|---|---|---|---|---|---|
| Opus | 15 min | 138k | All: research subagents, 2 reviews, credited cover | **93** | 0 of 28 |
| Sonnet, first run | 2 min | 77k | Skipped the research subagent, the review ("approval wait") and the image | 83 | 0 of 12; two unsupported "I" opinions |
| Sonnet, after the step-9 rewording | 5.5 min | 87k | 2 reviews (71, then 87); still no image | 83, **with a P0** | 2 of 21: a Lodge quote Lodge never wrote, survived both Sonnet reviews |

**Changes:** SKILL.md now says step 4 is the only one that waits for the user,
and that reviewing your own draft doesn't count. Sonnet then ran the reviews.

**Verdict:** use Opus for `write` and `rewrite`. Sonnet's posts are thinner
(about 550 words against 1,000), and its reviewers miss misquotes. It's about 3x
faster. Not tested: a Sonnet writer with an Opus reviewer.
