/**
 * Pull user-facing strings out of the file formats localisation actually ships
 * in, so the guard does not depend on the project being JavaScript.
 *
 * Each extractor returns `{path, text}[]`, where `path` is whatever will help
 * someone find the string again — a key path, a msgid, a line number.
 *
 * JSON, ARB, PO, iOS .strings and Android XML are parsed properly. YAML is
 * best-effort by design: parsing it fully would mean a dependency, and i18n
 * YAML is overwhelmingly `key: "value"`. Anything it cannot read it skips
 * rather than guesses, and the CLI says how many strings it found so a silent
 * near-miss is visible.
 */

import { readFileSync } from "node:fs";
import { extname, basename } from "node:path";

const read = (file) => readFileSync(file, "utf8").replace(/^﻿/, "");

const unescape = (s) =>
  s
    .replace(/\\n/g, "\n")
    .replace(/\\t/g, "\t")
    .replace(/\\"/g, '"')
    .replace(/\\'/g, "'")
    .replace(/\\\\/g, "\\");

export function extract(file, formatOverride) {
  const format = formatOverride ?? formatOf(file);
  const source = read(file);
  const label = basename(file);

  switch (format) {
    case "json":
    case "arb":
      return fromJson(JSON.parse(source), label);
    case "po":
      return fromPo(source, label);
    case "yaml":
      return fromYaml(source, label);
    case "strings":
      return fromStrings(source, label);
    case "xml":
      return fromAndroidXml(source, label);
    case "txt":
      return source
        .split(/\r?\n/)
        .map((line, i) => ({ path: `${label}:${i + 1}`, text: line.trim() }))
        .filter((e) => e.text);
    default:
      throw new Error(
        `Unknown format for ${file}. Pass --format=json|arb|po|yaml|strings|xml|txt.`,
      );
  }
}

function formatOf(file) {
  const ext = extname(file).toLowerCase();
  if (ext === ".json") return "json";
  if (ext === ".arb") return "arb";
  if (ext === ".po" || ext === ".pot") return "po";
  if (ext === ".yml" || ext === ".yaml") return "yaml";
  if (ext === ".strings") return "strings";
  if (ext === ".xml") return "xml";
  if (ext === ".txt") return "txt";
  return null;
}

function fromJson(value, path, out = []) {
  if (typeof value === "string") {
    // ARB metadata (`@@locale`, and the `@key` object describing `key`) documents
    // strings rather than being strings. The whole subtree is metadata, so test
    // every segment, not just the last one — `@welcome.description` is prose
    // written for translators and nobody ships it.
    const isMetadata = path.split(".").some((seg) => seg.startsWith("@"));
    if (!isMetadata) out.push({ path, text: value });
    return out;
  }
  if (Array.isArray(value)) {
    value.forEach((v, i) => fromJson(v, `${path}[${i}]`, out));
    return out;
  }
  if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value)) fromJson(v, `${path}.${k}`, out);
  }
  return out;
}

/**
 * gettext. Only `msgstr` is checked — `msgid` is the English source, and
 * flagging it for being English would be absurd. Empty translations are skipped
 * so an unfinished catalogue does not read as a clean one.
 */
function fromPo(source, label) {
  const out = [];
  const lines = source.split(/\r?\n/);
  let currentId = null;
  let collecting = null;
  let buffer = "";

  const flush = () => {
    // The entry with an empty msgid is the PO header — Content-Type, Plural-Forms,
    // the generator's name. It is metadata with semicolons in it, and checking it
    // reports a punctuation error against gettext rather than against the copy.
    if (collecting === "msgstr" && buffer.trim() && currentId) {
      out.push({ path: `${label} · ${currentId}`, text: buffer });
    }
    if (collecting === "msgid") currentId = buffer;
    buffer = "";
    collecting = null;
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("#") || trimmed === "") {
      flush();
      continue;
    }
    let m = /^msgid(?:_plural)?\s+"([\s\S]*)"$/.exec(trimmed);
    if (m) {
      flush();
      collecting = "msgid";
      buffer = unescape(m[1]);
      continue;
    }
    m = /^msgstr(?:\[\d+\])?\s+"([\s\S]*)"$/.exec(trimmed);
    if (m) {
      flush();
      collecting = "msgstr";
      buffer = unescape(m[1]);
      continue;
    }
    m = /^"([\s\S]*)"$/.exec(trimmed);
    if (m && collecting) {
      buffer += unescape(m[1]);
      continue;
    }
    flush();
  }
  flush();
  return out;
}

/** `"key" = "value";` */
function fromStrings(source, label) {
  const out = [];
  const re = /"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;/g;
  let m;
  while ((m = re.exec(source)) !== null) {
    out.push({ path: `${label} · ${unescape(m[1])}`, text: unescape(m[2]) });
  }
  return out;
}

/** Android `<string name="k">v</string>` and `<item>v</item>`. */
function fromAndroidXml(source, label) {
  const out = [];
  const strings = /<string\s+[^>]*name="([^"]+)"[^>]*>([\s\S]*?)<\/string>/g;
  let m;
  while ((m = strings.exec(source)) !== null) {
    out.push({ path: `${label} · ${m[1]}`, text: decodeXml(m[2]) });
  }
  const items = /<item[^>]*>([\s\S]*?)<\/item>/g;
  let i = 0;
  while ((m = items.exec(source)) !== null) {
    out.push({ path: `${label} · item[${i++}]`, text: decodeXml(m[1]) });
  }
  return out.filter((e) => e.text.trim());
}

const decodeXml = (s) =>
  s
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
    .replace(/&amp;/g, "&")
    .trim();

/**
 * Best-effort YAML: `key: value`, quoted or bare, plus `- item` lists and
 * `|`/`>` block scalars. Indentation drives the reported key path. Anchors,
 * aliases, flow collections and multi-document files are skipped, not guessed.
 */
function fromYaml(source, label) {
  const out = [];
  const lines = source.split(/\r?\n/);
  const stack = []; // {indent, key}

  const pathAt = (indent, key) => {
    while (stack.length && stack[stack.length - 1].indent >= indent) stack.pop();
    return [label, ...stack.map((s) => s.key), key].join(" · ");
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim() || /^\s*#/.test(line) || /^\s*---/.test(line)) continue;

    const indent = line.length - line.trimStart().length;
    const trimmed = line.trim();

    const listItem = /^-\s+(.*)$/.exec(trimmed);
    if (listItem && !listItem[1].includes(": ")) {
      const text = unquote(listItem[1]);
      if (text) out.push({ path: pathAt(indent, "-"), text });
      continue;
    }

    const kv = /^["']?([\w.\-\s]+?)["']?\s*:\s*(.*)$/.exec(trimmed);
    if (!kv) continue;
    const [, key, rawValue] = kv;
    const value = rawValue.trim();

    if (value === "" ) {
      const p = pathAt(indent, key);
      stack.push({ indent, key });
      void p;
      continue;
    }

    if (value === "|" || value === ">" || /^[|>][-+]?\d*$/.test(value)) {
      const block = [];
      let j = i + 1;
      while (j < lines.length) {
        const next = lines[j];
        if (next.trim() === "") { block.push(""); j++; continue; }
        const nextIndent = next.length - next.trimStart().length;
        if (nextIndent <= indent) break;
        block.push(next.trim());
        j++;
      }
      const text = block.join(" ").trim();
      if (text) out.push({ path: pathAt(indent, key), text });
      i = j - 1;
      continue;
    }

    if (value.startsWith("&") || value.startsWith("*") || value.startsWith("[") || value.startsWith("{")) {
      continue;
    }

    const text = unquote(value);
    if (text) out.push({ path: pathAt(indent, key), text });
  }
  return out;
}

function unquote(raw) {
  const v = raw.replace(/\s+#.*$/, "").trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return unescape(v.slice(1, -1));
  }
  return v;
}
