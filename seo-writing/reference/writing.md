# Writing a post

## Contents

- [The bar](#the-bar)
- [Structure](#structure)
- [Evidence](#evidence)
- [Voice](#voice)
- [Readability](#readability)
- [Links](#links)
- [Frontmatter and format](#frontmatter-and-format)
- [Trust](#trust)
- [Calls to action](#calls-to-action)

## The bar

A post earns its place when the reader finishes it able to do or decide
something the top results didn't help with. Before drafting, name that
**gain** in one sentence. It is usually one of these:

- first-hand data, results, screenshots or mistakes, which only the user can supply
- a sharper synthesis: primary sources that other pages paraphrase badly, reconciled
- a worked example taken all the way through
- a decision rule: "use X when…, Y when…"
- a disagreement with the consensus, backed by evidence

If you can't name one, the draft would just restate page one. Say so and ask the
user for what's missing (data, an example, an opinion) instead of padding the
post to look complete.

## Structure

**Open with the answer or the promise.** Put it in the first two or three
sentences. Drop scene-setting, "In this article", and definitions the reader
already knows.

> Before: When it comes to cast iron care, it's important to note that cleaning
> is a pivotal step. It's not just about hygiene, it's about preserving your
> seasoning. So how do you do it right?
>
> After: Rinse the pan while it's warm, scrub with coarse salt, dry it on the
> burner, then wipe on a thin film of oil. It takes three minutes and keeps the
> seasoning intact.

- **Each H2 delivers its heading's promise in its first paragraph.** The rest of
  the section supports it. A section should still make sense if someone lifts it
  out alone: readers skim, and answer engines quote single passages.
- **Key Takeaways** go after the intro on posts over about 1,200 words: 3 to 5
  bullets, each a complete claim that stands on its own. Take the label from
  BLOG.md.
- **Headings describe the content.** Phrase one as a question only where readers
  actually ask it that way, never every H2. One H1, which is the title. Go H2,
  then H3, and never skip a level.
- **Pick the right container.** Lists hold parallel items or steps. Tables hold
  comparisons across two or more attributes. Prose holds reasoning.
- **End on the next step, not a recap.** If the post has a conclusion section,
  it adds a decision or an action.
- **Length:** the template's range is a planning estimate. Stop when the job is
  done, and cut any section that exists only to look thorough.

## Evidence

- Every number, quote and disputable fact traces to a row in the source ledger
  ([research.md](research.md)), and someone opened that page and saw the figure.
  If it isn't in the ledger, cut it or say it qualitatively.
- **Cite at the claim:** `[Publisher or report title](url)`. Give the year or
  date whenever recency changes the meaning. Link the primary source, not the
  article that reported it.
- **Keep the figure's scope:** who was measured, how many, when, and the unit.
  "61% of the 1,100 US developers surveyed in 2025" is a fact. "61% of
  developers" is a distortion.
- Quotes are verbatim, attributed, and linked.
- Never write "studies show", "experts agree" or "research suggests" without
  naming the study, expert or research.
- **No invented experience.** Write "we tested" or "in my experience" only when
  the user supplied that experience. Never invent anecdotes, customers, quotes,
  results or case studies, including "illustrative" ones presented as real.
- **YMYL topics** (health, money, legal, safety): use primary and official
  sources only, state the limits, give no advice beyond the evidence, and say
  when to see a professional.

## Voice

BLOG.md wins. Without it, write plain and direct: second person, contractions,
active voice, concrete nouns, and sentences that vary in length because the
thoughts do. Explain jargon the first time it appears.

### Tells that make prose read machine-written

Cut these on sight. `check_post.py` flags most of them.

**Words and phrases:** delve, tapestry, testament, landscape, realm, navigate
(used figuratively), leverage (as a verb), robust, seamless, cutting-edge,
game-changer, revolutionize, unlock, unleash, harness, elevate, empower, foster,
streamline, pivotal, crucial, paramount, multifaceted, comprehensive,
meticulous, "in today's…", "ever-evolving", "it's important/worth noting",
"when it comes to", "in conclusion", and "furthermore" or "moreover" as
sentence openers.

**Structures:**
- "It's not X, it's Y" and "not just X, but Y" reframes
- setup questions answered at once ("The result?", "Why does this matter?")
- triplets everywhere: three adjectives, three clauses, three examples
- every section ending in a one-line moral or summary ("In short, …")
- hedge stacks: may, might, often, typically, all in one sentence
- symmetric lists where every bullet has the same length and shape, and bolded
  lead-ins on every bullet
- **em dashes**, banned by default. Use a comma, colon, parentheses or two
  sentences
- emoji and exclamation marks in informational posts

The fix is rarely a synonym. Usually the sentence had nothing to say: delete it,
or replace it with the specific fact it was gesturing at.

## Readability

- **The audience sets the density.** General readers want short sentences and
  plain words, roughly Flesch 60 to 70. Practitioners can take more, but never
  more filler. BLOG.md overrides both.
- **One idea per paragraph.** Split when a second idea starts, not at a word
  count.
- **Watch the load.** Introduce no more than about three new terms or numbers
  per paragraph. Move number-heavy comparisons into a table, give every abstract
  claim an example, and give context where it's needed instead of "as we'll see
  later".

## Links

- **Internal:** 3 to 8 per post. Resolve them against the real content
  directory by grepping titles and slugs. Make anchors descriptive (2 to 6 words
  naming the destination), put at least one in the first few paragraphs, and
  put no more than two in one paragraph. A cluster post links to its pillar.
- **Linking back:** list the existing posts that should now link to the new one,
  and offer to add those links.
- **Missing targets:** if a target doesn't exist yet, write
  `[INTERNAL-LINK: anchor → planned topic]`. `check_post.py` fails on
  placeholders, so these get listed instead of shipping silently.
- **External links:** point to the source of each claim. Use `rel="sponsored"`
  on paid or affiliate links and `rel="ugc"` on user content.

## Frontmatter and format

Match the project's existing posts, and read two of them first: field names,
date format, cover-image path, slug style, and any MDX components. With no
precedent, use:

```yaml
title: ""          # specific, about 60 chars or fewer, topic early, no clickbait
description: ""    # 70-160 chars: what the reader gets; numbers only if sourced in the post
date: YYYY-MM-DD
updated: YYYY-MM-DD   # only after a substantive change; never touch `date`
author: ""
tags: []
image: ""          # cover, 1200x630, local path
imageAlt: ""
```

- Put a year in the title only when the content really is year-specific.
- Slugs are short and readable, with no dates on evergreen posts. Never change a
  published slug without a redirect.
- Platform gotchas (MDX, Hugo, Jekyll, Astro, WordPress, Ghost) are in
  [seo.md](seo.md#platform-conventions).

## Trust

- **Byline:** a named person whose bio shows relevant experience. Never "Admin"
  or "Team".
- **Disclose** affiliate links, sponsorships, and any case where the author's
  company makes a product the post discusses.
- **Self-promotion:** an informational post mentions the brand at most once,
  where it's relevant. Reviews and case studies can do more if they disclose it.
- **Dates:** show the published date, plus an updated date when the post truly
  was updated.

## Calls to action

One focused CTA, placed after the value it follows from:

| Post type | Place the CTA |
|---|---|
| How-to, tutorial | after the first working result |
| Listicle | mid-list (after item 3 or 4) and at the end |
| Comparison, review | after the verdict |
| Case study, data study | after the results or key finding |
| Opinion | at the conclusion |
| Pillar | at 2 or 3 natural section breaks, no more |

Write the CTA as a specific next action tied to the post's topic, never a
generic "Contact us". Use `<a>` for navigation and `<button>` for actions.
