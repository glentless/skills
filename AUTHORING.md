# Authoring skills — working notes

Condensed from Anthropic's
[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
What matters when building a skill in this repo.

## Core principles

- **Concise.** Only the `name` and `description` load at startup; the
  SKILL.md body and other files load on demand. Once loaded, every token
  competes with the conversation. Claude is already smart, so cut anything it
  knows ("what a PDF is", "why use a library").
- **Match freedom to fragility.**
  - High (prose heuristics): many valid approaches, context decides.
  - Medium (pseudocode or a parameterised script): there's a preferred pattern
    with some variation allowed.
  - Low (exact command, "do not modify"): fragile work, or a fixed sequence.
  - The guide's image: a narrow bridge needs guardrails; an open field needs a
    direction.
- **Test on every model it'll run on.** Haiku may need more guidance; Opus may
  find the same text over-explained.

## Frontmatter

```yaml
---
name: processing-pdfs   # ≤64 chars, [a-z0-9-], no XML, no "anthropic"/"claude"
description: Extracts text and tables from PDFs, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

- `description`: non-empty, ≤1024 chars, no XML tags. Must say **what it does
  + when to use it**, with the key terms users say. Claude picks one skill out
  of 100+ using this text alone.
- **Third person always**: "Processes Excel files…", never "I can help…" or
  "You can use this…". The description is injected into the system prompt.
- Naming: a gerund is preferred (`processing-pdfs`); `pdf-processing` and
  `process-pdfs` are acceptable. Avoid `helper`, `utils`, `data`, `files`. Use
  one pattern across the repo.

## Structure and progressive disclosure

- SKILL.md body **under 500 lines**. It works like a table of contents: a quick
  start, then pointers to detail files.
- **References one level deep**: every file is linked directly from SKILL.md.
  Claude may only `head` files it reached through another file, and miss the
  rest.
- Reference files over 100 lines get a **Contents** list at the top.
- Organise by domain (`reference/finance.md`, `reference/sales.md`) so Claude
  reads only the slice it needs. Use descriptive filenames, not `doc2.md`.
- Bundled files cost nothing until they're read, so it's fine to ship complete
  API docs and big datasets.
- Forward slashes in every path, never `\`.

## Writing the body

- **Workflows**: number the steps. For long ones, give a checklist Claude copies
  into its reply and ticks off.
- **Feedback loops**: run the validator → fix → repeat, and only proceed once it
  passes. The validator can be a script or a style-guide file Claude checks
  against.
- **Conditional workflows**: "Creating? → A. Editing? → B." If a branch gets
  big, move it into its own file.
- **Templates**: strict ("ALWAYS use this exact structure") or flexible ("a
  sensible default, adapt as needed"). Say which.
- **Examples**: show input → output pairs when style matters; they beat
  descriptions.
- **One default, not a menu**: "Use pdfplumber. For scanned PDFs, use
  pytesseract instead." Don't list five libraries.
- **One term per concept**: always "field", never field/box/element.
- **No time-sensitive text**: put superseded approaches in a collapsed "Old
  patterns" section.
- **Stronger wording when a rule gets ignored**: "MUST filter" beats "always
  filter"; moving the rule higher in the file also helps.

## Scripts

- **Solve, don't defer**: handle errors inside the script instead of crashing
  and leaving Claude to work it out.
- **No voodoo constants**: comment why a value is 30 or 3.
- Prefer shipped scripts to generated code: more reliable, consistent, and
  cheaper (only the output costs tokens).
- Say whether to **run** a script ("Run `x.py` to…") or **read** it ("See `x.py`
  for the algorithm").
- **Plan → validate → execute** for batch, destructive or high-stakes work:
  Claude writes a plan file (`changes.json`), a script validates it, then the
  change is applied and verified. Make validator errors specific, e.g. "Field
  'x' not found. Available: a, b, c".
- When an input can be rendered as an image, render it so Claude can look at
  it.
- **Dependencies**: list packages and how to install them; don't assume they're
  present. claude.ai can install from npm/PyPI; the API has no network access
  and can't install packages at runtime.
- MCP tools: use fully qualified names, `ServerName:tool_name`.

## Evaluation and iteration

- **Evals before docs:**
  1. Run Claude on real tasks without the skill and note where it fails.
  2. Write 3 eval scenarios that cover those failures.
  3. Measure the baseline.
  4. Write the *minimum* instructions that fix it.
  5. Re-run and compare with the baseline.
- Eval shape: `{skills, query, files, expected_behavior[]}`. Nothing runs these
  for you; bring your own harness.
- **Claude A / Claude B**:
  - Do the task with Claude A and notice the context you keep supplying.
  - Have A write that context into the skill, then trim the explanations.
  - Test with a fresh Claude B on real tasks.
  - Take B's specific misses back to A.
- **Watch how Claude navigates the skill.** Files read in an unexpected order
  mean the structure is unclear. A link that's never followed needs to be more
  prominent. A file read every time belongs in SKILL.md. A file never read may
  not be needed.

## Pre-ship checklist

**Core**
- [ ] Description is specific, third person, what + when
- [ ] Body under 500 lines, with detail in separate files
- [ ] References one level deep; files over 100 lines have a Contents list
- [ ] Consistent terms, concrete examples, no time-sensitive text
- [ ] Workflows have clear steps

**Code**
- [ ] Scripts handle errors and every constant is justified
- [ ] Packages listed and verified as available
- [ ] Forward-slash paths only
- [ ] Validation and feedback loops on critical steps

**Testing**
- [ ] At least 3 evals
- [ ] Tested on Haiku, Sonnet and Opus
- [ ] Tested in real usage
