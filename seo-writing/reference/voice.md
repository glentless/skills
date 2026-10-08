# Voice and project context: BLOG.md

Every workflow reads one file from the project root: **BLOG.md**. It holds what
can't be inferred from a single post: who the readers are, what the brand
believes, how it sounds, and the site's conventions. It replaces the old
BRAND.md, VOICE.md and persona JSON. If those exist and BLOG.md doesn't, read
them, and offer to merge them into BLOG.md.

A `VOICE.md` written by the `vietnamese-voice` skill governs Vietnamese UI
copy. Read it when writing Vietnamese posts. Don't merge it into BLOG.md.

## Commands

- **`voice init`:** interview the user and write BLOG.md from
  `assets/BLOG.template.md`.
- **`voice learn <posts or dir>`:** derive the voice section from 5 to 10 of
  the user's best posts.
- **`voice show`:** summarize the current BLOG.md, and flag sections that are
  empty or contradict the posts.
- **`voice update`:** edit the relevant section. Keep the rest as it is.

## init: the interview

Ask in two short rounds, not one long form. Pre-fill whatever the site already
shows (the about page, existing posts, author pages), so the user only confirms.

1. **Readers and positioning:**
   - the primary reader (role, expertise, the problem they bring)
   - what the brand helps them do
   - the point of view that sets it apart
   - what it is *not*
   - 2 or 3 competitors, with how it differs from each
   - topics in scope, adjacent, and out of scope
2. **Voice and rules:**
   - pronoun stance: we, I, or neither
   - formality
   - 3 to 5 do's and don'ts
   - banned phrases
   - required disclosures, such as affiliate links or AI assistance
   - Key Takeaways label
   - whether em dashes are allowed
   - CTA and conversion goal

Fill the site conventions yourself by reading the repository: content
directory, frontmatter fields, image directory, URL pattern, authors and
platform. Confirm them with the user at the end.

If the user's answers are thin, write what you have and mark the gaps `TODO`.
Don't invent positioning.

## learn: deriving voice from samples

1. **Get the numbers:**
   ```bash
   python scripts/check_post.py --voice <5-10 posts or a dir>
   ```
   They cover sentence length (mean and spread), paragraph length, contraction
   and pronoun rates, question-heading share, the filler-phrase rate, and
   recurring phrases.
2. **Read three of the posts in full.** Numbers miss what matters most:
   - how the author opens
   - how they handle evidence
   - their humour, or the lack of it
   - typical metaphors and sentence rhythm
   - what they never do
3. **Write the Voice section of BLOG.md:**
   - 4 to 6 plain rules
   - two short excerpts that sound most like the author
   - the measured ranges, as guides rather than targets

   **Imitate the author, not their bad habits:** if the samples are full of
   filler, say so and ask the user whether to keep or drop it.

## How BLOG.md is applied

- **Precedence:** the user's instruction in the current request beats BLOG.md,
  which beats this skill's defaults.
- **Overrides:** BLOG.md can switch off default rules, such as allowing em
  dashes. It cannot switch off the evidence rules: no fabricated facts, quotes
  or experience.
- **Banned phrases:** pass them to the checker with
  `check_post.py --ban-file <file with one phrase per line>`.
- **Brand colours** go to `chart.py` (`"colors"`) and into image prompts.
- **Authors:** use the author's name and bio exactly as BLOG.md gives them for
  the byline and the Person schema.
