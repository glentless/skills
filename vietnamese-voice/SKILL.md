---
name: vietnamese-voice
description: Use whenever Vietnamese text is written, reviewed, translated, or generated for real people to read — UI strings, error messages, emails, notifications, landing copy, AI system prompts, docs. Ensures the Vietnamese reads as though a Vietnamese person wrote it, not as a well-translated English sentence. Covers forms of address (thầy cô / em / anh/chị / bạn), sentence-final softeners (nhé, giúp, ạ, rồi), banned translationese (hệ thống, chúng tôi, Vui lòng, đường dẫn, dữ liệu, Đã xảy ra lỗi), rhythm, register per audience, and installs a vitest guard that fails the build on the known tells. Also use when asked to audit existing Vietnamese copy, set up a copy guard, or write a VOICE.md.
version: 1.0.0
user-invocable: true
argument-hint: "[write|review|audit|install] [target files or copy]"
---

# Vietnamese that sounds Vietnamese

Correct is not the bar. Natural is the bar.

Vietnamese copy written by someone thinking in English comes out grammatically
perfect, vocabulary-accurate, and instantly recognisable as a translation. The
reader's word for it is *lủng củng* — clunky. They cannot always point at the
broken word, because no word is broken. The habits are what give it away.

This skill has two halves, and you need both:

- **The principles** — `reference/naturalness.md`. These catch rhythm and
  register. No test can.
- **The guard** — a vitest file that fails the build on the known tells, so the
  copy cannot rot back six months from now.

A test alone produces copy that dodges banned words and still reads as a
translation. Principles alone get forgotten by the next person.

## When this fires

Any time Vietnamese leaves the codebase toward a human:

- writing or editing UI strings, buttons, empty states, error messages
- translating English copy to Vietnamese (the highest-risk case)
- writing prompts that make an LLM produce Vietnamese
- reviewing or auditing existing Vietnamese copy
- setting up a new project that will ship Vietnamese

Skip it for: Vietnamese in code comments, commit messages, or anything only
developers read.

## Do this

### 1. Read the principles

Read `reference/naturalness.md` **before** writing a string, not after the test
goes red. It is short. It contains the three habits that produce almost all
translationese, the address table, the word swaps, and the softener rule.

### 2. Establish the audience profile

Vietnamese has no neutral "you". You cannot write a single string until you know
who reads it. If the project has a `VOICE.md`, read it — that is the profile.

If it does not, derive it and write one. You need, per surface:

| Question | Why it decides the words |
| --- | --- |
| Who reads this? | Picks the pronoun: `thầy cô`, `em`, `anh/chị`, `cô/chú`, `bạn` |
| What does the product call itself? | `bên mình` (small business), `Tên Sản Phẩm`, `máy`, or nothing |
| How formal is the relationship? | Decides whether `ạ` ever appears |
| Is the reader under time pressure? | Under pressure = zero softeners |

Ask the user if the audience is genuinely ambiguous. Do not guess between
`thầy cô` and `bạn` — that single choice sets the tone of the whole product.
Copy `assets/VOICE.template.md` into the project root and fill it in.

**`bạn` is the default of every translated SaaS in Vietnam.** It is correct and
it is invisible. Use it only when the audience is genuinely a broad anonymous
public and the brand is deliberately casual. Anywhere you know who the reader
is, name them properly.

### 3. Write, then read it out loud

Actually voice it in Vietnamese in your head. The test is not "is this correct"
but "would a person say this, or only write it". If it only ever gets written,
rewrite it.

Run the checklist at the end of `reference/naturalness.md` on each string.

### 4. Install the guard

If the project has no copy guard, install one. See `reference/enforcement.md`
for the full walkthrough. Short version:

1. Copy `assets/voice.test.ts` next to the project's message catalogue.
2. Point its import at the module that exports every user-facing string.
3. Fill in the address rules from the project's VOICE.md profile.
4. Set the `toBeGreaterThan(N)` floor to roughly the current string count — this
   is a guard on the guard, so the file cannot silently pass while walking
   nothing.
5. Run it. Fix what it finds. Do not add exemptions to make it green.

If strings are not centralised in one module, say so and fix that first — a
guard that can only see half the copy is worse than none, because it reads as
coverage.

### 5. Every rule needs a reason

Adding a banned pattern to the test means adding a row to the project's
VOICE.md explaining why. A ban with no explanation gets deleted by the next
person who trips over it, and the tell comes straight back.

## Hard rules

- **Never signal warmth with a softener on a label, button, or field error.**
  `Lưu`, not `Lưu nhé`. Field errors are read at speed while fixing a form; a
  softener there is friction, not kindness.
- **Never use a semicolon.** It does not appear in ordinary written Vietnamese.
- **Keep the loanwords people actually say** — `link`, `file`, `email`, `copy`,
  `online`, `Word`, `Excel`, `Zalo`. Purifying these into `đường dẫn` / `tệp` is
  its own kind of unnatural.
- **One idea per string.** If it needs three sentences, it needs three strings
  or a different screen.
- **Never rewrite a founder's own words for style.** If a landing page is
  someone's real voice, it is the one thing a competitor cannot copy. Fix
  typos, not rhythm.

## Files

- `reference/naturalness.md` — the principles. Read first, always.
- `reference/enforcement.md` — installing and adapting the guard test.
- `assets/voice.test.ts` — portable vitest copy guard.
- `assets/VOICE.template.md` — per-project voice document to fill in.
