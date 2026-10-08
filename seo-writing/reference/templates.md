# Post templates

Twelve shapes. Each one shows the sections in order, the gain to look for, and a
typical length. These are **flexible defaults**: adapt them to the topic and the
evidence. Every template also inherits the rules in [writing.md](writing.md):
answer first, Key Takeaways on long posts, an optional FAQ only for real
questions, and one CTA.

## Contents

- [Choosing](#choosing)
- [How-to](#how-to) · [Tutorial](#tutorial) · [Listicle](#listicle) · [Comparison](#comparison)
- [Review](#review) · [Case study](#case-study) · [Data study](#data-study) · [Pillar](#pillar)
- [Explainer and FAQ](#explainer-and-faq) · [News analysis](#news-analysis) · [Opinion](#opinion) · [Roundup](#roundup)

## Choosing

| Signal in the query or brief | Template |
|---|---|
| "how to", a process, setup | how-to (no code) / tutorial (code or config) |
| "best X", "top N", tools for | listicle |
| "X vs Y", "X alternatives" | comparison |
| "X review", "is X worth it" | review |
| a result someone achieved | case study |
| original survey, experiment, dataset | data study |
| broad head topic, hub for a cluster | pillar |
| "what is X", a cluster of questions | explainer and FAQ |
| something just happened | news analysis |
| a stance against the consensus | opinion |
| multiple experts' views | roundup |

Match the format already ranking for the query. If page one is all listicles,
a 3,000-word essay is fighting the reader's intent.

## How-to

**Length:** 1,200 to 2,500 words. **Title:** "How to [outcome]", plus a qualifier
if it helps ("without [pain]", "in [time]").

1. Intro: the outcome, who it's for, time needed, difficulty.
2. Before you start: requirements, versions, accounts, cost.
3. One H2 per step, written "Step N: [verb] [object]". Each step says what the
   reader will have afterwards, lists the actions as a numbered list, and ends
   with how to check it worked. Add a screenshot wherever there's a UI.
4. Common mistakes: the mistake, why it happens, the fix.
5. What success looks like, then the next step.

**Gain:** the non-obvious detail in each step, the versions it was tested on,
and the real error messages with their fixes.

## Tutorial

**Length:** 1,500 to 3,000 words. A how-to for code or configuration.

1. What we're building, shown as an image or the final output first.
2. Prerequisites with exact versions.
3. Setup: commands in code blocks, with the expected output.
4. Steps: explain *why* as well as what, show complete runnable snippets, and
   add a checkpoint after each.
5. Testing: how to verify, with the commands.
6. Troubleshooting: the actual error strings and their fixes.
7. Full source, or a link to the repo, plus next steps.

**Gain:** code that actually runs, with versions pinned. Never publish code you
haven't checked against the docs for the version you name.

## Listicle

**Length:** 1,200 to 2,500 words. **Title:** "N best [things] for [use case]".

1. Intro: who this is for, the selection criteria in one line, and the top pick.
2. Optional quick-pick table: item, best for, price, one standout fact.
3. One H2 per item: what it is, who it's best for, strengths, the honest
   drawback, price or availability, and a link.
4. How we chose: the criteria, plus what was actually tested versus researched.
   Say which is which.
5. Optional comparison matrix, then a closing recommendation by use case.

**Gain:** real testing, or a clear method. Items must differ in substance, not
just in name. Keep the intro short: readers came for the list.

## Comparison

**Length:** 1,200 to 2,500 words. **Title:** "X vs Y: [the deciding question]".

1. The verdict in the first paragraph: who should pick X, who should pick Y.
2. Comparison table: the criteria that decide the choice, each with values,
   not adjectives.
3. One H2 per decisive criterion, with a winner for each and the evidence.
4. Pricing, compared like for like at the same tier and usage.
5. Who should choose what, framed as scenarios.
6. Alternatives worth a look.

**Gain:** like-for-like testing and current pricing. Be fair to both. Disclose
any affiliation with either product.

## Review

**Length:** 1,200 to 2,500 words. **Title:** "[Product] review: [verdict in a few words]".

1. A verdict box: rating if the site uses ratings, who it's for, who should
   skip it, price.
2. Pros and cons.
3. How it was tested: duration, setup, what was measured. Without real hands-on
   testing this is not a review; tell the user, and make it an explainer or
   comparison instead.
4. One H2 per key feature, with findings and screenshots.
5. Pricing and value.
6. Alternatives (two or three), then the final verdict.

**Gain:** original screenshots, measurements, and long-term notes. Add a
`Review` schema only with a real rating.

## Case study

**Length:** 1,000 to 2,000 words. **Title:** "How [who] [achieved result] [in timeframe]".

1. Summary box: the client or context, the problem, the result in numbers, the
   timeframe.
2. The challenge, with a baseline metric.
3. The approach: what was done and why, including what was ruled out.
4. Implementation: steps, tools, obstacles.
5. Results: before and after, with method and timeframe. Show a chart.
6. Takeaways another reader can apply.

**Gain:** real numbers and permission to publish them. Every figure comes from
the user. Never construct a plausible case study.

## Data study

**Length:** 1,500 to 3,000 words. **Title:** "[Finding]: [what we studied]" or "State of X [year]".

1. Key findings: 3 to 5 bullets, each a number with its context.
2. Methodology: data source, sample size and how it was drawn, timeframe,
   analysis method, and limitations. This section is what makes the study
   citable.
3. One H2 per finding, phrased as the finding itself, with a chart and its
   interpretation.
4. Surprises and outliers.
5. What it means, for each audience segment.
6. Data appendix with the summary table, plus how to cite the study.

**Gain:** this is the gain. Publish the summary data so others can cite it.

## Pillar

**Length:** 2,500 to 4,000 words. **Title:** "[Topic]: the complete guide" or a sharper equivalent.

1. Intro, plus a table of contents.
2. What it is, and why it matters, briefly.
3. Six to eight H2s, one per core subtopic. Each gives the essential answer in
   200 to 400 words, then links to the spoke post that covers it in depth.
4. An advanced section, tools and resources, and how to get started.
5. Links to every spoke in the cluster.

**Gain:** clear organization and a coherent model of the whole topic. A pillar
is a hub: depth belongs in the spokes.

## Explainer and FAQ

**Length:** 800 to 2,000 words. **Title:** "What is X?" or "[Topic]: questions answered".

1. A direct definition in the first two sentences, then why it matters.
2. Group the questions under H2s such as basics, how it works, problems, and
   advanced. Each question is an H3 answered directly in its first sentence.
3. Related resources.

**Gain:** precise answers drawn from primary sources. Questions come from real
data (People Also Ask, forums, support tickets), not invention. A FAQ section no
longer earns a rich result, so it's only worth including for readers.

## News analysis

**Length:** 600 to 1,200 words. **Title:** "[What happened]: what it means for [audience]".

1. What happened: the facts, the date, and a link to the primary announcement.
2. Why it matters.
3. What changes for the reader, one H3 per impact.
4. What to do now.
5. The bigger picture, plus what is still unknown. Separate confirmed facts from
   speculation.

**Gain:** speed with accuracy, and context from someone who knows the area. Use
only sources from the last few days. Note in the text when the post was written
and what is still developing.

## Opinion

**Length:** 1,000 to 2,500 words. **Title:** "Why [conventional view] is wrong" or "[Claim]".

1. Hook: state the claim plainly.
2. The conventional view, presented fairly with its best argument.
3. Why it's wrong or incomplete, with evidence.
4. The better approach, and how to apply it.
5. Caveats: where the conventional view still holds.

**Gain:** a real position held by the author. Get the stance from the user;
don't manufacture contrarianism.

## Roundup

**Length:** 1,200 to 2,500 words. **Title:** "N [experts] on [question]".

1. Intro: the question asked, and who answered.
2. One section per expert: name, role, link, and their quote, verbatim and
   approved by them.
3. Synthesis: where they agree, where they disagree, and why.
4. Takeaways and methodology: how the experts were chosen and asked.

**Gain:** real, attributed quotes. Never write quotes for real people.
