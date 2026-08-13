import { describe, expect, it } from "vitest";
// ── ADAPT ME ─────────────────────────────────────────────────────────────────
// Point this at the module that exports every user-facing string. If the copy
// is spread across several modules, import them all and pass an object holding
// each one to collectStrings — a guard that sees half the copy is worse than
// no guard, because it reads as coverage.
import * as messages from "./index";
// ─────────────────────────────────────────────────────────────────────────────

/**
 * The copy guard.
 *
 * Vietnamese copy written by someone thinking in English comes out
 * grammatically correct and instantly recognisable as a translation — "lủng
 * củng, rõ ràng là tiếng Anh dịch sang tiếng Việt". Every string a native
 * reader reacts to is usually correct, which is why review does not catch it:
 * the problem is not errors, it is a handful of words and habits that only ever
 * appear when someone is thinking in English.
 *
 * VOICE.md explains the reasoning. This file is the part that cannot be
 * forgotten in six months, because it fails the build.
 *
 * **What it can and cannot do.** It catches known tells — the words and the
 * wrong forms of address. It cannot hear rhythm, and a string can pass every
 * rule here and still read as a translation. It is a floor, not a standard;
 * VOICE.md is the standard.
 *
 * Adding a rule means adding a row to VOICE.md as well. A ban with no
 * explanation gets deleted by the next person who trips over it.
 */

type Rule = {
  /** What is wrong, in English, for whoever's test just went red. */
  readonly why: string;
  /** What to write instead. */
  readonly instead: string;
  readonly pattern: RegExp;
  /**
   * Text removed from the string before the pattern runs, so a correct longer
   * form cannot trip a rule aimed at a shorter one — `thầy cô` contains `cô`.
   */
  readonly ignoring?: RegExp;
  /**
   * Strings allowed to match anyway, by full text. Every entry needs a reason
   * beside it — an exemption list nobody justifies grows until the rule means
   * nothing.
   */
  readonly allow?: readonly string[];
};

const RULES: readonly Rule[] = [
  // ── Universal. These are translationese in any Vietnamese product. ────────
  {
    why: "`hệ thống` is the English subject 'the system' wearing a Vietnamese coat.",
    instead: "the product's name, or `máy` — what a person calls a computer doing something",
    pattern: /hệ thống/iu,
  },
  {
    why: "`chúng tôi` is a company voice. Most products are a handful of people.",
    instead: "bên mình, or no subject at all",
    pattern: /chúng tôi/iu,
  },
  {
    why: "`đường dẫn` and `liên kết` are dictionary Vietnamese. Everyone says 'gửi link'.",
    instead: "link (the noun), Sao chép link (the button)",
    pattern: /đường dẫn|liên kết/iu,
  },
  {
    why: "`Vui lòng` is 'Please' in a suit — the politeness of a form, not of a person.",
    instead: "… giúp / … nhé",
    pattern: /vui lòng/iu,
  },
  {
    why: "`Đã xảy ra lỗi` is a literal cast of 'An error occurred'. Nobody says it out loud.",
    instead: "Có lỗi rồi, or name the thing that failed: Chưa lưu được",
    pattern: /đã xảy ra lỗi/iu,
  },
  {
    why: "`dữ liệu` is a database word on a screen an ordinary person reads.",
    instead: "Chưa có gì ở đây, or name the missing thing",
    pattern: /dữ liệu/iu,
  },
  {
    why: "`định dạng` asks the reader to care what a file format is.",
    instead: "Email này chưa đúng / File này không mở được",
    pattern: /định dạng/iu,
  },
  {
    why: "Officialese. Vietnamese speech uses an active verb.",
    instead: "an active verb — làm, chạy, gửi, mở",
    pattern: /được thực hiện|được tiến hành/iu,
  },
  {
    why: "Nobody clicks a mouse on a phone, and most people are on phones.",
    instead: "bấm",
    pattern: /nhấp chuột|nhấn chuột/iu,
  },
  {
    why: "`quý …` is the register of an official circular, not of a tool.",
    instead: "the plain form of address",
    pattern: /quý (thầy cô|phụ huynh|khách hàng|vị)/iu,
  },
  {
    why: "Semicolons do not appear in ordinary written Vietnamese; they read as imported punctuation.",
    instead: "a full stop, or a comma",
    pattern: /;/u,
  },

  // ── Project-specific. Set these from your VOICE.md address profile. ───────
  // Delete or edit these two if they do not match your audience.
  {
    why: "`bạn` is how every translated SaaS in this market addresses a user.",
    instead: "the real form of address for this reader — see VOICE.md",
    pattern: /(^|[^\p{L}])bạn([^\p{L}]|$)/u,
  },
  {
    why: "`cô` alone addresses a woman, which excludes half the audience.",
    instead: "thầy cô, or a neutral role noun",
    // `thầy cô` is the correct longer form and contains `cô`.
    ignoring: /thầy cô/giu,
    pattern: /(^|[^\p{L}])cô([^\p{L}]|$)/u,
  },
];

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

/** Every user-facing string in the product, with the path that produced it. */
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

const strings = new Map<string, string>();
collectStrings(messages, "", strings);

describe("Vietnamese copy", () => {
  it("has strings to check", () => {
    // A guard on the guard: if the walker ever stops finding the messages, this
    // whole file would pass silently while checking nothing. Set the floor near
    // the current count.
    expect(strings.size).toBeGreaterThan(50);
  });

  for (const rule of RULES) {
    it(`avoids: ${rule.why}`, () => {
      const offenders: string[] = [];

      for (const [text, path] of strings) {
        if (rule.allow?.includes(text)) continue;
        const subject = rule.ignoring ? text.replace(rule.ignoring, "") : text;
        if (rule.pattern.test(subject)) {
          offenders.push(`  ${path}\n    "${text}"`);
        }
      }

      expect(
        offenders,
        `\n${rule.why}\nWrite instead: ${rule.instead}\nSee VOICE.md.\n\n${offenders.join("\n")}\n`,
      ).toEqual([]);
    });
  }
});
