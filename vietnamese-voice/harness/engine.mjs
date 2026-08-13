/**
 * The rule engine.
 *
 * Every harness — the CLI, the vitest guard, the Python script's sibling logic —
 * runs these same checks over the same `rules/rules.json`. A rule added there
 * reaches every stack at once, which is the whole reason the rules are data and
 * not code.
 *
 * Two things this file exists to get right:
 *
 * 1. **NFC normalisation.** Vietnamese has two Unicode spellings for the same
 *    word: precomposed (`ệ`, one code point) and decomposed (`e` + two combining
 *    marks). They render identically and they do not match the same regex. Text
 *    out of macOS, some CMSes and some XML toolchains arrives decomposed, so a
 *    guard that skips this step silently passes the strings it was written to
 *    catch. Both the patterns and the text are normalised before matching.
 *
 * 2. **Register.** A rule is not universally true. `Vui lòng` is wrong in a
 *    consumer app and correct in a bank. Each rule declares the registers it
 *    applies to, and the profile picks the register.
 */

import { readFileSync } from "node:fs";

/** Unicode NFC. The single most important line in this file — see above. */
export const nfc = (s) => s.normalize("NFC");

const readJson = (path) =>
  JSON.parse(readFileSync(path, "utf8").replace(/^﻿/, ""));

/**
 * `.test()` on a regex carrying the `g` flag advances `lastIndex` between calls,
 * so the same pattern starts skipping matches once it has found one. Strip it.
 */
const compile = (pattern, flags = "u") =>
  new RegExp(nfc(pattern), flags.replace(/g/g, ""));

/**
 * Effective rules for a project: core rules filtered to the profile's register,
 * minus what the profile disables, plus its own rules and its glossary.
 */
export function loadRules(rulesPath, profilePath) {
  const core = readJson(rulesPath);
  const profile = profilePath
    ? readJson(profilePath)
    : { name: "none", register: "warm" };

  const register = profile.register ?? "warm";
  const disabled = new Set(profile.disable ?? []);

  const applies = (rule) =>
    (rule.registers ?? ["formal", "warm", "casual"]).includes(register) &&
    !disabled.has(rule.id);

  const rules = [
    ...core.rules.filter(applies),
    ...(profile.extraRules ?? []).filter(applies),
    ...glossaryRules(profile.glossary ?? [], register),
  ];

  return { rules, profile, register, coreVersion: core.version };
}

/**
 * A locked-terminology entry is just a rule with a generated pattern. Regulated
 * industries need this more than they need the banned-word list: the wrong
 * synonym for a statutory term is a compliance problem, not a style one.
 */
function glossaryRules(glossary, register) {
  return glossary.map((entry, i) => ({
    id: `glossary-${slug(entry.right) || i}`,
    kind: "string",
    registers: [register],
    severity: entry.severity ?? "error",
    pattern: (entry.wrong ?? []).map(escapeRe).join("|"),
    flags: "iu",
    why: entry.why ?? `\`${entry.right}\` is the locked term for this concept.`,
    instead: entry.right,
    tags: ["glossary"],
  }));
}

const slug = (s) =>
  nfc(s)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/gi, "d")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/**
 * @param entries {{path: string, text: string}[]}
 * @returns findings, most severe first
 */
export function check(entries, { rules, profile, register }) {
  const normalised = entries.map((e) => ({ ...e, text: nfc(e.text) }));
  const findings = [];

  for (const rule of rules) {
    const severity = rule.severityByRegister?.[register] ?? rule.severity ?? "error";
    const allowed = new Set(
      (rule.allow ?? []).concat(profile.allow?.[rule.id] ?? []).map(nfc),
    );

    const occurrences =
      rule.kind === "corpus"
        ? corpusCheck(normalised, rule)
        : rule.kind === "titlecase"
          ? titleCaseCheck(normalised, rule, profile, allowed)
          : stringCheck(normalised, rule, allowed);

    if (occurrences.length > 0) {
      findings.push({
        id: rule.id,
        severity,
        why: rule.why,
        instead: rule.instead,
        tags: rule.tags ?? [],
        falsePositives: rule.falsePositives,
        occurrences,
      });
    }
  }

  const rank = { error: 0, warn: 1 };
  return findings.sort(
    (a, b) => rank[a.severity] - rank[b.severity] || b.occurrences.length - a.occurrences.length,
  );
}

function stringCheck(entries, rule, allowed) {
  if (!rule.pattern) return [];
  const pattern = compile(rule.pattern, rule.flags ?? "u");
  // Built with `g` on purpose: this one is used with .replace, which has to
  // clear every occurrence, not just the first.
  const ignoring = rule.ignoring
    ? new RegExp(nfc(rule.ignoring), rule.ignoringFlags ?? "giu")
    : null;

  /**
   * An escape hatch for rules whose pattern is right but whose meaning flips
   * on context. A bank's fraud warning contains the exact phrase its fraud rule
   * looks for — `không bao giờ yêu cầu cung cấp mã OTP` — and negation is not
   * something a forward pattern can see. Expressing this as a second pattern
   * rather than a lookbehind keeps the rules portable: JavaScript allows
   * variable-length lookbehind, Python's `re` does not.
   */
  const unless = rule.unless ? compile(rule.unless, rule.unlessFlags ?? "iu") : null;

  const hits = [];
  for (const { path, text } of entries) {
    if (allowed.has(text)) continue;
    if (unless && unless.test(text)) continue;
    // A correct longer form can contain a banned shorter one — `thầy cô`
    // contains `cô`. Strip the good form before testing for the bad.
    const subject = ignoring ? text.replace(ignoring, "") : text;
    if (pattern.test(subject)) hits.push({ path, text });
  }
  return hits;
}

const PLACEHOLDER = /\{\{?[^{}]*\}?\}|%[\d$sdfx@]*|\$\{[^}]*\}|<[^>]+>/g;

const startsUpper = (word) => {
  const c = [...word][0];
  return c && c !== c.toLowerCase() && c === c.toUpperCase();
};

/**
 * Vietnamese does not title-case. English UI does — "Save Changes" — and the
 * habit survives translation into `Lưu Thay Đổi`.
 *
 * A heuristic, hence a warning: two or more capitalised words after the first,
 * once proper nouns, placeholders and acronyms are taken out.
 */
function titleCaseCheck(entries, rule, profile, allowed) {
  const nouns = [...(profile.properNouns ?? [])]
    .map(nfc)
    .sort((a, b) => b.length - a.length);
  const threshold = rule.threshold ?? 2;
  const hits = [];

  for (const { path, text } of entries) {
    if (allowed.has(text)) continue;
    let stripped = text.replace(PLACEHOLDER, " ");
    for (const noun of nouns) stripped = stripped.split(noun).join(" ");

    const words = stripped
      .split(/[\s/|·—–-]+/)
      .map((w) => w.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, ""))
      .filter(Boolean);

    let capitalised = 0;
    for (let i = 1; i < words.length; i++) {
      const w = words[i];
      if (w.length > 1 && w === w.toUpperCase()) continue; // acronym
      if (startsUpper(w)) capitalised++;
    }
    if (capitalised >= threshold) hits.push({ path, text });
  }
  return hits;
}

/**
 * Corpus rules look at the catalogue as a whole rather than at one string.
 * Mixed tone-placement conventions are the case this exists for: neither
 * `hoà` nor `hòa` is wrong, but a catalogue holding both was written by two
 * people and reads that way.
 */
function corpusCheck(entries, rule) {
  const present = [];
  for (const [label, pattern] of Object.entries(rule.variants ?? {})) {
    const re = compile(pattern, rule.flags ?? "u");
    const examples = entries.filter((e) => re.test(e.text));
    if (examples.length > 0) present.push({ label, examples });
  }
  if (present.length < 2) return [];

  return present.flatMap(({ label, examples }) =>
    examples.slice(0, 3).map((e) => ({ path: e.path, text: e.text, variant: label })),
  );
}

export const counts = (findings) => ({
  errors: findings.filter((f) => f.severity === "error").length,
  warnings: findings.filter((f) => f.severity === "warn").length,
});
