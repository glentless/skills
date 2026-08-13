import { describe, expect, it } from "vitest";
import { fileURLToPath } from "node:url";
import { loadRules, check } from "./engine.mjs";

// ── ADAPT ME ─────────────────────────────────────────────────────────────────
// 1. Point this at the module exporting every user-facing string. If the copy
//    lives in several modules, import them all and combine — a guard that sees
//    half the copy is worse than none, because it reads as coverage.
import * as messages from "../../src/messages";

// 2. Pick the industry profile. `node harness/check-vietnamese.mjs
//    --list-profiles` prints what is available and which register each carries.
const PROFILE = "consumer-saas";

// 3. Set the floor near the real string count. This guards the guard: if the
//    walker ever stops finding the catalogue, every rule below would pass while
//    checking nothing.
const MINIMUM_STRINGS = 50;
// ─────────────────────────────────────────────────────────────────────────────

/**
 * The copy guard.
 *
 * Vietnamese written by someone thinking in English comes out grammatically
 * correct and instantly recognisable as a translation — "lủng củng, rõ ràng là
 * tiếng Anh dịch sang tiếng Việt". Every string a native reader reacts to is
 * usually correct, which is why review does not catch it: the problem is not
 * errors, it is a handful of words and habits that only appear when someone is
 * thinking in English.
 *
 * The rules live in `rules/rules.json` and the industry profile in
 * `rules/profiles/`, shared with the CLI and the Python harness. Editing this
 * file to change a rule is the wrong move — change the profile, so the CLI and
 * CI agree with the test.
 *
 * **What it can and cannot do.** It catches known tells. It cannot hear rhythm,
 * and a string can pass every rule here and still read as a translation. It is
 * a floor, not a standard; `reference/naturalness.md` is the standard.
 */

const RULES_PATH = fileURLToPath(new URL("../rules/rules.json", import.meta.url));
const PROFILE_PATH = fileURLToPath(
  new URL(`../rules/profiles/${PROFILE}.json`, import.meta.url),
);

/**
 * Sample arguments for message functions.
 *
 * Several tuples rather than one, because these take numbers, names, arrays and
 * pre-formatted values. Every tuple that produces a string is checked — missing
 * a branch matters more than calling a function twice.
 */
const ARGUMENT_SETS: readonly unknown[][] = [
  [1, 2, 3],
  [2, 10, "80"],
  ["Nguyễn Thu Hà", "9A", "0,8"],
  [["Nguyễn Thu Hà", "Trần Minh Quân"]],
];

function collectStrings(
  value: unknown,
  path: string,
  found: Map<string, string>,
): void {
  if (typeof value === "string") {
    if (!found.has(value)) found.set(value, path);
    return;
  }

  if (typeof value === "function") {
    for (const args of ARGUMENT_SETS) {
      try {
        const result = (value as (...a: unknown[]) => unknown)(...args);
        if (typeof result === "string" && !found.has(result)) {
          found.set(result, path);
        }
      } catch {
        // Wrong argument shape for this function. Another tuple will fit.
      }
    }
    return;
  }

  if (Array.isArray(value)) {
    value.forEach((item, index) =>
      collectStrings(item, `${path}[${index}]`, found),
    );
    return;
  }

  if (value && typeof value === "object") {
    for (const [key, child] of Object.entries(value)) {
      collectStrings(child, path ? `${path}.${key}` : key, found);
    }
  }
}

const collected = new Map<string, string>();
collectStrings(messages, "", collected);

const entries = [...collected].map(([text, path]) => ({ path, text }));
const config = loadRules(RULES_PATH, PROFILE_PATH);
const findings = check(entries, config);

const format = (finding: (typeof findings)[number]) =>
  [
    "",
    finding.why,
    `Write instead: ${finding.instead}`,
    finding.falsePositives ? `False positives: ${finding.falsePositives}` : null,
    "See reference/naturalness.md.",
    "",
    ...finding.occurrences.map(
      (o: { path: string; text: string; variant?: string }) =>
        `  ${o.path}${o.variant ? ` [${o.variant}]` : ""}\n    "${o.text}"`,
    ),
    "",
  ]
    .filter((line) => line !== null)
    .join("\n");

describe(`Vietnamese copy (${PROFILE}, ${config.register})`, () => {
  it("has strings to check", () => {
    expect(entries.length).toBeGreaterThan(MINIMUM_STRINGS);
  });

  // One test per rule. Naming the test after the rule means a red run says
  // which habit came back, not just that the file failed.
  for (const rule of config.rules) {
    const finding = findings.find((f) => f.id === rule.id);
    const severity = finding?.severity ?? rule.severity ?? "error";

    it(`avoids: ${rule.why}`, () => {
      if (!finding) return;

      // Warnings are heuristics — title case, number formats, mixed
      // orthography. Failing the build on a heuristic trains people to add
      // exemptions until the rule means nothing, so these are printed and
      // passed. `check-vietnamese.mjs --strict` fails on them in CI when you
      // want that, which is the right place to decide it.
      if (severity === "warn") {
        console.warn(`\n[vietnamese-voice: ${finding.id}]${format(finding)}`);
        return;
      }

      expect(format(finding)).toBe("");
    });
  }
});
