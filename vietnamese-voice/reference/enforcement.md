# Installing the guard

The guard fails a build when a known tell appears in user-facing Vietnamese. It
is a floor, not a standard — it cannot hear rhythm. Its job is to stop the
regressions a human reviewer will not notice in six months.

Three harnesses, one set of rules. `rules/rules.json` and `rules/profiles/*.json`
are shared by all of them, so a rule is written once.

| Harness | Use when |
| --- | --- |
| `harness/check-vietnamese.mjs` | Anything. Reads JSON, ARB, PO, YAML, `.strings`, Android XML. No dependencies. |
| `harness/voice.test.ts` | The project is JS/TS and strings live in a module rather than a data file. |
| `harness/check_vietnamese.py` | Django/Flask, and you would rather not add Node. Reads JSON, ARB, PO, YAML. |

---

## Prerequisite: the strings must be reachable

The guard checks what it can read. If copy is hardcoded in components, it sees a
fraction and reports green, which is worse than no guard because it reads as
coverage.

Before installing, sweep for Vietnamese living outside the catalogue:

```bash
rg '"[^"]*[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ][^"]*"' \
  src --glob '!**/messages/**' --glob '!**/locales/**' --glob '!**/*.test.*'
```

Hits mean copy the guard cannot see. Move it into the catalogue first. If that
is a big job, say so and do it as its own change — do not install a guard over
copy it cannot read.

---

## 1. Pick a profile

```bash
node harness/check-vietnamese.mjs --list-profiles
```

```
b2b-enterprise       formal   Enterprise SaaS, admin consoles, ERP…
banking-finance      formal   Banks, e-wallets, lending, insurance…
consumer-saas        warm     The default profile…
ecommerce-retail     casual   Marketplaces, D2C shops, food delivery…
education            warm     Schools, tutoring centres, LMS…
gaming-social        casual   Games, social apps, community products…
government-public    formal   Public services, e-government, utilities…
healthcare           formal   Hospitals, clinics, booking, telemedicine…
```

Take the closest one. If none fits, copy `consumer-saas.json`, rename it, and
narrow it. See [registers.md](registers.md) for choosing the register.

## 2. Run it

```bash
node harness/check-vietnamese.mjs --profile=education src/messages/
python harness/check_vietnamese.py --profile=government-public locale/vi/
```

Exit codes: `0` clean, `1` errors (or warnings under `--strict`), `2` misuse —
including "read 0 strings", which is deliberately a failure rather than a pass.

## 3. Tune the profile, not the strings

Every finding is one of three things:

**A real tell** — fix the string. Most findings.

**Correct for your industry** — add the rule id to the profile's `disable`, with
the reason in `notes`. A bank disabling `vui-long` is right. A consumer app
disabling it is giving up.

**A false positive on one string** — add the exact string to the profile's
`allow`, keyed by rule id, with the reason beside it:

```jsonc
{
  "allow": {
    "english-ui-leftover": [
      "Zalo Official Account"   // product name, not untranslated copy
    ]
  }
}
```

An exemption list nobody justifies grows until the rule means nothing.

## 4. Wire it into CI

```yaml
- name: Vietnamese copy
  run: node skills/vietnamese-voice/harness/check-vietnamese.mjs
       --profile=education --strict src/messages/
```

`--strict` makes warnings fail too. Worth turning on once the catalogue is clean
— title case and number formats are exactly the things that creep back.

---

## The vitest harness

Use this when strings are a JS/TS module rather than a data file, because it can
call message *functions* and check what they produce. A template that only goes
wrong at `n = 0` is invisible to a file-based check.

1. Copy `harness/` and `rules/` into the project.
2. Put `harness/voice.test.ts` wherever the test runner will find it.
3. Edit the three marked lines at the top: the import, the profile, the floor.

The import is the part that varies by setup:

```ts
// Bundler-style resolution (Next.js, most Vite setups)
import * as messages from "../../src/messages";

// Strict ESM may need the explicit file
import * as messages from "../../src/messages/index.ts";

// Copy spread across modules — combine them
import * as auth from "../../src/messages/auth";
import * as exams from "../../src/messages/exams";
const messages = { auth, exams };
```

4. Set `MINIMUM_STRINGS` near the real count. This guards the guard: if the
   walker stops finding the catalogue, every rule would otherwise pass while
   checking nothing.

Errors fail the test. Warnings print and pass — failing a build on a heuristic
trains people to add exemptions until the rule means nothing. Use the CLI with
`--strict` in CI if you want warnings enforced; that is the right place to decide
it.

Vitest only prints console output for **failing** tests by default, so warnings
show up under `--reporter=verbose`.

---

## Writing a rule

```jsonc
{
  "id": "kebab-case-id",
  "kind": "string",              // "string" | "titlecase" | "corpus"
  "registers": ["warm", "casual"],
  "severity": "error",           // "error" | "warn"
  "severityByRegister": { "formal": "warn" },   // optional
  "pattern": "hệ thống",
  "flags": "iu",                 // never "g" — it breaks repeated .test()
  "ignoring": "thầy cô",         // optional: correct longer form, stripped first
  "unless": "không bao giờ",     // optional: context that flips the meaning
  "why": "…",                    // English, for whoever's build just went red
  "instead": "…",                // concretely what to write
  "falsePositives": "…"          // optional, but write it if you know of any
}
```

Four things that bite:

- **Word boundaries.** `\b` does not work reliably on Vietnamese diacritics. Use
  `(^|[^\p{L}])word([^\p{L}]|$)` with the `u` flag.
- **`ignoring` exists because correct longer forms contain banned shorter ones.**
  `thầy cô` contains `cô`. Strip the good form before testing for the bad.
- **`unless` exists because negation is invisible to a forward pattern.** A
  bank's fraud warning contains the exact phrase its fraud rule looks for. Do not
  reach for variable-length lookbehind — JavaScript allows it, Python does not,
  and the rules have to run in both.
- **Open vs closed syllables** matter for orthography patterns. `hoà`/`hòa` is a
  real choice; `toàn` has only one spelling. Anchor with `(?![\p{L}])` or every
  `toàn diện` in the catalogue turns into a finding.

Every new rule needs a row in the project's `VOICE.md`.

---

## Porting to another stack

The engine is about 150 lines over a JSON rule list. `check_vietnamese.py` is the
reference for what a port has to handle:

- **Normalise to NFC** — the text *and* the patterns. Without it the guard
  silently passes decomposed input, which is most of the reason to have a guard.
  See §7 of [mechanics.md](mechanics.md).
- **Translate `\p{L}`** if the target engine lacks Unicode property escapes.
  Python's `re`: `[^\W\d_]`.
- **Never compile a `g` pattern for repeated `.test()`** — `lastIndex` carries
  between calls and it starts skipping matches.
- **Skip metadata.** The PO header is not copy, and ARB `@key` objects are notes
  to translators. Checking them reports gettext's punctuation as a finding.

For catching hardcoded strings at authoring time rather than in CI, an ESLint
rule matching the same patterns against JSX text is a good companion. Use both:
lint while writing, guard on the catalogue.
