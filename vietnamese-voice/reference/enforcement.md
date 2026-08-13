# Installing the copy guard

The guard is a test that fails the build when a known tell appears in
user-facing Vietnamese. It is a floor, not a standard — it cannot hear rhythm.
Its job is to stop the regressions that a human reviewer will not notice in six
months.

---

## Prerequisite: strings must be centralised

The guard walks one module and checks every string it finds. If copy is
hardcoded in components, the guard sees a fraction of it and reports green,
which is worse than having no guard at all.

Before installing, check:

```
rg '"[^"]*[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ][^"]*"' src --glob '!**/messages/**' --glob '!**/*.test.*'
```

Hits mean Vietnamese living outside the catalogue. Move it in first. If that is
a big job, say so to the user and do it as its own change — do not install a
guard over copy it cannot see.

The catalogue module should export plain strings and functions returning
strings, grouped by surface:

```ts
export const auth = {
  signIn: "Đăng nhập",
  emailWrong: "Email này chưa đúng",
  greeting: (name: string) => `Chào ${name}`,
};
```

---

## Install

1. Copy `assets/voice.test.ts` next to the catalogue — e.g.
   `src/messages/voice.test.ts`.

2. Fix the import at the top. If copy spans several modules:

   ```ts
   import * as auth from "./auth";
   import * as exams from "./exams";
   const messages = { auth, exams };
   ```

3. Set the address rules. The last block in `RULES` is marked
   *project-specific*. Delete the `bạn` rule only if the audience is genuinely
   a broad anonymous public. Delete the bare-`cô` rule if the product never
   addresses a teacher. Add rules for whatever the project's VOICE.md forbids.

4. Set the floor. `expect(strings.size).toBeGreaterThan(N)` guards the guard.
   Run the file once, read the actual count off a failing assertion or a
   `console.log`, and set `N` a little under it.

5. Run it. Fix every offender by rewriting the string, not by adding an
   exemption. `allow` exists for the rare real case — a legal notice, a quoted
   third-party name — and every entry needs a comment saying why.

6. Add a row to the project's VOICE.md for each rule you added. A ban with no
   documented reason gets deleted the first time it is inconvenient.

---

## How each rule is shaped

```ts
{
  why: "…",       // English, for whoever's test just went red
  instead: "…",   // what to write, concretely
  pattern: /…/iu, // the tell
  ignoring: /…/giu, // optional: correct longer form stripped first
  allow: ["…"],   // optional: exact strings exempted, each with a comment
}
```

Two things about the patterns:

- **Word-boundary rules need the `\p{L}` dance.** `\b` does not work on
  Vietnamese diacritics in every engine. Use
  `/(^|[^\p{L}])word([^\p{L}]|$)/u` — the `u` flag is required.
- **`ignoring` exists because correct longer forms contain shorter banned
  ones.** `thầy cô` contains `cô`. Strip the good form before testing the bad.

---

## Not using vitest?

The logic is fifty lines and carries no vitest specifics beyond `describe` /
`it` / `expect`. Adapting:

- **Jest** — works as written.
- **node:test** — swap `expect(x).toEqual([])` for
  `assert.deepEqual(x, [])` and `describe`/`it` from `node:test`.
- **A lint rule** — for hardcoded strings in components, an ESLint rule
  matching the same patterns against JSX text catches them at the point of
  writing. Use both: the lint rule for authoring, the test for the catalogue.
- **Not JavaScript** — the guard is a regex list over a string table. Port the
  `RULES` array verbatim into whatever the project's test framework is; the
  patterns are the asset, the harness is not.

---

## When an LLM writes the Vietnamese

Regex cannot check tone in generated output. If a model produces user-facing
Vietnamese:

1. Put the address rules and the softener rule in the system prompt, not just
   in a doc. Name the banned words explicitly.
2. Name the collision risks. If the assistant calls itself `em`, the prompt
   must say that the people it talks about are `học sinh` / `các em`, never a
   bare `em`.
3. Forbid particles on labels, button names, and numbered steps in the prompt —
   models over-apply warmth once you ask for it.
4. **Add a live test against the real API** asserting the warmth is present —
   e.g. that a sample answer contains at least one of `nhé|nha|ạ`, and that a
   step-by-step answer contains none. A model drifting back to flat
   documentation prose is invisible otherwise. Keep it in a separate
   `*.live.test.ts` so the normal suite stays offline.
