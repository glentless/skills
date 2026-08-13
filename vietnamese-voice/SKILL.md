---
name: vietnamese-voice
description: Use whenever Vietnamese text is written, reviewed, translated, or generated for real people to read — UI strings, error messages, emails, notifications, landing copy, AI system prompts, docs. Ensures the Vietnamese reads as though a Vietnamese person wrote it, not as a well-translated English sentence. Covers register (formal bank/government vs warm SaaS vs casual games), forms of address (Quý khách / thầy cô / anh-chị / em / bạn), sentence-final softeners (nhé, giúp, ạ, rồi), translationese (hệ thống, chúng tôi, Vui lòng, đường dẫn, dữ liệu, Đã xảy ra lỗi), title case, number/date/currency format, classifiers, NFC normalisation, and industry glossaries. Ships a rule engine with CLI, vitest and Python harnesses reading JSON, ARB, PO, YAML, .strings and Android XML. Also use to audit existing Vietnamese copy, set up a copy guard, or write a VOICE.md.
version: 2.0.0
user-invocable: true
argument-hint: "[write|review|audit|install] [target files or copy]"
license: MIT
---

# Vietnamese that sounds Vietnamese

Correct is not the bar. Natural is the bar.

Vietnamese written by someone thinking in English comes out grammatically
perfect, vocabulary-accurate, and instantly recognisable as a translation. The
reader's word for it is *lủng củng* — clunky. They often cannot point at the
broken word, because no word is broken. The habits are what give it away.

## The first decision: register

**There is no universal banned list.** The most common mistake is not a wrong
word, it is the right word in the wrong register.

- `Vui lòng` is stilted in a consumer app and **correct in a bank**
- `Hệ thống` is an English subject in disguise on a teacher's dashboard and
  **the plain right word** on a government portal
- `bạn` is the tell of translated SaaS in one product and **exactly how a game
  should talk** in another

So before writing anything, read [reference/registers.md](reference/registers.md)
and pick one of `formal`, `warm`, `casual`. Everything else follows from it.

## Do this

### 1. Pick the register and the profile

```bash
node harness/check-vietnamese.mjs --list-profiles
```

Eight industry profiles ship with the skill — banking-finance, healthcare,
government-public, b2b-enterprise (formal); consumer-saas, education (warm);
ecommerce-retail, gaming-social (casual). Take the closest, or copy
`consumer-saas.json` and narrow it.

The profile carries the register, the forms of address, which core rules are
disabled because they are correct in that industry, and a **glossary** of terms
that are not yours to improve. In regulated industries the glossary matters more
than the banned list: the wrong synonym for a statutory term is a compliance
problem, not a style one.

### 2. Establish the audience

Vietnamese has no neutral "you". You cannot write a string until you know who
reads it. If the project has a `VOICE.md`, read it. If not, copy
`assets/VOICE.template.md` into the project root and fill it in — per surface:

| Question | What it decides |
| --- | --- |
| Who reads this? | The pronoun: `Quý khách`, `thầy cô`, `anh/chị`, `em`, `bạn` |
| What does the product call itself? | `chúng tôi` / `bên mình` / `mình` / nothing |
| Is the reader under time pressure? | Under pressure = zero softeners |
| Northern or southern Vietnamese? | `mẹ`/`má`, `vâng`/`dạ`, and forty other pairs |
| Which tone-mark convention? | `hòa` or `hoà` — pick one, stay consistent |

Ask the user if the audience is genuinely ambiguous. Do not guess between
`Quý khách` and `bạn` — that one choice sets the tone of the whole product.

### 3. Read the principles, then write

- [reference/naturalness.md](reference/naturalness.md) — the three habits that
  produce almost all translationese, forms of address, when a softener earns its
  place, rhythm. **Read before writing, not after the guard goes red.**
- [reference/mechanics.md](reference/mechanics.md) — title case, numbers, dates,
  money, classifiers, text expansion, NFC, tone marks, punctuation. These are the
  same in every register and are the fastest visible tells.

Then actually read the string out loud in Vietnamese. The test is not "is this
correct" but "would a person say this, or only write it".

### 4. Install the guard

See [reference/enforcement.md](reference/enforcement.md). Three harnesses over
one rule set:

```bash
# anything: JSON, ARB, PO, YAML, .strings, Android XML
node harness/check-vietnamese.mjs --profile=education src/messages/

# Django/Flask, no Node needed
python harness/check_vietnamese.py --profile=government-public locale/vi/

# JS/TS where strings are a module — also checks message *functions*
cp harness/voice.test.ts <project>/  # then edit the three marked lines
```

Findings are one of three things: a real tell (fix the string), correct for your
industry (add to the profile's `disable`), or a one-off false positive (add to
`allow`, with the reason). **Tune the profile, not the strings.**

### 5. Every rule needs a reason

A pattern added to the rules needs a row in the project's `VOICE.md` explaining
why. A ban with no documented reason gets deleted by the next person who trips
over it, and the tell comes straight back.

## Hard rules

- **No softener on a label, button, or field error** — in any register. `Lưu`,
  not `Lưu nhé`. Field errors are read at speed while fixing a form.
- **No semicolons.** They do not occur in ordinary written Vietnamese.
- **Sentence case, never title case.** `Lưu thay đổi`, not `Lưu Thay Đổi`.
- **Numbers Vietnamese-style.** `1.000.000 ₫`, `0,8`, `13/08/2026`, `14h30`.
- **Normalise to NFC** at every boundary. Vietnamese has two Unicode spellings
  per word; they look identical and are not equal.
- **Keep the loanwords people actually say** — `link`, `file`, `email`, `ship`,
  `online`, `Zalo`. Purifying these is its own kind of unnatural.
- **One idea per string.**
- **Never rewrite a founder's own words for style.** Fix typos, not rhythm.
- **In regulated industries, prescribed wording is not yours to improve.** Quote
  it, and route changes back to whoever owns it.

## The ceiling

Say this out loud when handing over work: **a green guard is not a natural
product.** The rules catch known tells and cannot hear rhythm. A catalogue can
pass everything here and still read as a translation.

Get a native speaker who uses products in this category, from the right region,
to read it **on the actual screen**. Ask: *"đọc có tự nhiên không, hay giống dịch
từ tiếng Anh?"* — then ask them to point at the worst sentence.

## Files

```
reference/registers.md     the register dial — read first
reference/naturalness.md   the principles
reference/mechanics.md     format, typography, Unicode, classifiers
reference/enforcement.md   installing and extending the guard
rules/rules.json           the rule data, shared by every harness
rules/profiles/*.json      eight industry profiles
harness/check-vietnamese.mjs   CLI, any format, no dependencies
harness/check_vietnamese.py    same rules, no Node
harness/voice.test.ts          vitest/jest, walks a JS module
harness/engine.mjs             the shared engine
harness/extract.mjs            the format readers
assets/VOICE.template.md       per-project voice document
```
