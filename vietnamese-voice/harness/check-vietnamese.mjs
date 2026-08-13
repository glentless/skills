#!/usr/bin/env node
/**
 * The stack-independent guard.
 *
 * Reads localisation files in whatever format the project ships — JSON, ARB,
 * PO, YAML, .strings, Android XML — and applies `rules/rules.json` filtered by
 * an industry profile. No dependencies, so it runs anywhere Node does, in CI or
 * in a pre-commit hook.
 *
 *   node check-vietnamese.mjs --profile=education src/messages/*.json
 *   node check-vietnamese.mjs --profile=banking-finance --strict locale/vi/LC_MESSAGES/django.po
 *
 * Exit codes: 0 clean, 1 errors found (or warnings under --strict), 2 misuse.
 */

import { readdirSync, statSync, existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { loadRules, check, counts } from "./engine.mjs";
import { extract } from "./extract.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const RULES = resolve(here, "../rules/rules.json");
const PROFILES = resolve(here, "../rules/profiles");

const argv = process.argv.slice(2);
const flag = (name, fallback = null) => {
  const hit = argv.find((a) => a.startsWith(`--${name}=`));
  return hit ? hit.slice(name.length + 3) : fallback;
};
const has = (name) => argv.includes(`--${name}`);

if (has("help") || argv.length === 0) {
  console.log(`
vietnamese-voice — check Vietnamese copy for translationese

  node check-vietnamese.mjs [options] <files or directories>

  --profile=<name>   industry profile (default: consumer-saas)
                     available: ${listProfiles().join(", ")}
  --format=<fmt>     force a format: json arb po yaml strings xml txt
  --strict           treat warnings as failures
  --all              show every occurrence, not just the first few
  --list-profiles    print the profiles and exit
`);
  process.exit(argv.length === 0 ? 2 : 0);
}

if (has("list-profiles")) {
  for (const name of listProfiles()) {
    const p = JSON.parse(readFileSync(join(PROFILES, `${name}.json`), "utf8"));
    console.log(`${name.padEnd(20)} ${p.register.padEnd(7)} ${p.appliesTo ?? ""}`);
  }
  process.exit(0);
}

function listProfiles() {
  if (!existsSync(PROFILES)) return [];
  return readdirSync(PROFILES)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""))
    .sort();
}

const profileName = flag("profile", "consumer-saas");
const profilePath = join(PROFILES, `${profileName}.json`);
if (!existsSync(profilePath)) {
  console.error(
    `Unknown profile "${profileName}". Available: ${listProfiles().join(", ")}`,
  );
  process.exit(2);
}

const targets = argv.filter((a) => !a.startsWith("--"));
const files = targets.flatMap(expand);
if (files.length === 0) {
  console.error("No files matched.");
  process.exit(2);
}

function expand(target) {
  const path = resolve(target);
  if (!existsSync(path)) return [];
  if (!statSync(path).isDirectory()) return [path];
  return readdirSync(path).flatMap((entry) => expand(join(path, entry)));
}

const config = loadRules(RULES, profilePath);
const entries = [];
const skipped = [];

for (const file of files) {
  try {
    const found = extract(file, flag("format"));
    entries.push(...found.map((e) => ({ ...e, text: String(e.text) })));
  } catch (error) {
    skipped.push(`${file} — ${error.message}`);
  }
}

if (entries.length === 0) {
  console.error(
    "Read 0 strings. Nothing was checked, which is not the same as a pass.",
  );
  if (skipped.length) console.error(skipped.map((s) => `  ${s}`).join("\n"));
  process.exit(2);
}

const findings = check(entries, config);
const { errors, warnings } = counts(findings);
const limit = has("all") ? Infinity : 5;

const BOLD = "\u001b[1m";
const DIM = "\u001b[2m";
const RED = "\u001b[31m";
const YELLOW = "\u001b[33m";
const GREEN = "\u001b[32m";
const OFF = "\u001b[0m";
const paint = process.stdout.isTTY ? (c, s) => `${c}${s}${OFF}` : (_, s) => s;

console.log(
  `\n${paint(BOLD, "vietnamese-voice")} · profile ${profileName} · register ${config.register}` +
    ` · ${entries.length} strings from ${files.length} file(s)\n`,
);

for (const f of findings) {
  const tag = f.severity === "error" ? paint(RED, "error") : paint(YELLOW, "warn ");
  console.log(`${tag} ${paint(BOLD, f.id)} — ${f.occurrences.length} occurrence(s)`);
  console.log(`      ${f.why}`);
  console.log(`      ${paint(DIM, "Write instead:")} ${f.instead}`);
  if (f.falsePositives) console.log(`      ${paint(DIM, "False positives:")} ${f.falsePositives}`);
  for (const o of f.occurrences.slice(0, limit)) {
    const variant = o.variant ? paint(DIM, ` [${o.variant}]`) : "";
    console.log(`        ${paint(DIM, o.path)}${variant}\n          "${o.text}"`);
  }
  if (f.occurrences.length > limit) {
    console.log(paint(DIM, `        … and ${f.occurrences.length - limit} more (--all)`));
  }
  console.log("");
}

if (skipped.length) {
  console.log(paint(DIM, `Skipped ${skipped.length} file(s):`));
  for (const s of skipped) console.log(paint(DIM, `  ${s}`));
  console.log("");
}

if (errors === 0 && warnings === 0) {
  console.log(paint(GREEN, "Clean.") + " No known tells.");
  console.log(
    paint(DIM, "This is a floor, not a standard — it cannot hear rhythm. Read reference/naturalness.md."),
  );
  process.exit(0);
}

console.log(
  `${errors} error(s), ${warnings} warning(s). ` +
    paint(DIM, "A rule you disagree with belongs in the profile, not in an ignore comment."),
);
process.exit(errors > 0 || (has("strict") && warnings > 0) ? 1 : 0);
