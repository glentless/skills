#!/usr/bin/env python3
"""The same guard, for projects without Node.

Reads the same ``rules/rules.json`` and the same profiles as the JavaScript
harness, so a rule is written once and enforced everywhere. Standard library
only — it drops into a Django or Flask repo with nothing to install.

    python check_vietnamese.py --profile=education locale/vi/LC_MESSAGES/django.po
    python check_vietnamese.py --profile=government-public --strict locale/

Handles JSON, ARB, gettext PO and (best-effort) YAML. For iOS ``.strings`` and
Android XML use the Node CLI, which parses both.

Exit codes: 0 clean, 1 errors (or warnings under --strict), 2 misuse.

Two portability notes, both load-bearing:

* **NFC.** Vietnamese has precomposed and decomposed Unicode spellings that look
  identical and do not match the same pattern. Everything is normalised before
  matching, or the guard silently passes what it exists to catch.
* **``\\p{L}``.** The rules are written in ECMAScript regex. Python's ``re`` has
  no ``\\p{L}``, so patterns are translated on load to ``[^\\W\\d_]``, the
  standard idiom for a Unicode letter. Variable-length lookbehind is never used
  in the rules for the same reason — that is what a rule's ``unless`` is for.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES_PATH = HERE.parent / "rules" / "rules.json"
PROFILES_DIR = HERE.parent / "rules" / "profiles"


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def to_python_regex(pattern: str) -> str:
    """Translate the ECMAScript Unicode property escapes the rules use."""
    pattern = pattern.replace(r"[^\p{L}]", r"[\W\d_]")
    pattern = pattern.replace(r"[\p{L}]", r"[^\W\d_]")
    pattern = pattern.replace(r"\p{L}", r"[^\W\d_]")
    pattern = pattern.replace(r"[^\p{N}]", r"\D")
    pattern = pattern.replace(r"[\p{N}]", r"\d")
    pattern = pattern.replace(r"\p{N}", r"\d")
    return pattern


def compile_pattern(pattern: str, flags: str = "u"):
    py_flags = re.UNICODE
    if "i" in flags:
        py_flags |= re.IGNORECASE
    return re.compile(to_python_regex(nfc(pattern)), py_flags)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


# ── rule assembly ────────────────────────────────────────────────────────────


def slug(text: str) -> str:
    stripped = "".join(
        c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c)
    )
    stripped = stripped.replace("đ", "d").replace("Đ", "D").lower()
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", stripped))


def glossary_rules(glossary, register):
    rules = []
    for i, entry in enumerate(glossary):
        wrong = entry.get("wrong") or []
        if not wrong:
            continue
        rules.append(
            {
                "id": f"glossary-{slug(entry['right']) or i}",
                "kind": "string",
                "registers": [register],
                "severity": entry.get("severity", "error"),
                "pattern": "|".join(re.escape(w) for w in wrong),
                "flags": "iu",
                "why": entry.get(
                    "why", f"`{entry['right']}` is the locked term for this concept."
                ),
                "instead": entry["right"],
                "tags": ["glossary"],
            }
        )
    return rules


def load_rules(profile_name: str):
    core = read_json(RULES_PATH)
    profile_path = PROFILES_DIR / f"{profile_name}.json"
    if not profile_path.exists():
        available = ", ".join(sorted(p.stem for p in PROFILES_DIR.glob("*.json")))
        sys.exit(f'Unknown profile "{profile_name}". Available: {available}')
    profile = read_json(profile_path)

    register = profile.get("register", "warm")
    disabled = set(profile.get("disable", []))

    def applies(rule):
        registers = rule.get("registers", ["formal", "warm", "casual"])
        return register in registers and rule["id"] not in disabled

    rules = (
        [r for r in core["rules"] if applies(r)]
        + [r for r in profile.get("extraRules", []) if applies(r)]
        + glossary_rules(profile.get("glossary", []), register)
    )
    return rules, profile, register


# ── extractors ───────────────────────────────────────────────────────────────


def from_json(value, path, out):
    if isinstance(value, str):
        if not any(seg.startswith("@") for seg in path.split(".")):
            out.append((path, value))
        return out
    if isinstance(value, list):
        for i, v in enumerate(value):
            from_json(v, f"{path}[{i}]", out)
        return out
    if isinstance(value, dict):
        for k, v in value.items():
            from_json(v, f"{path}.{k}", out)
    return out


def unescape(text: str) -> str:
    return (
        text.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def from_po(source: str, label: str):
    out, current_id, collecting, buffer = [], None, None, ""

    def flush():
        nonlocal current_id, collecting, buffer
        # The empty-msgid entry is the PO header — Content-Type and friends.
        # Checking it reports gettext's punctuation, not the copy's.
        if collecting == "msgstr" and buffer.strip() and current_id:
            out.append((f"{label} · {current_id}", buffer))
        if collecting == "msgid":
            current_id = buffer
        buffer, collecting = "", None

    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            flush()
            continue
        m = re.match(r'^msgid(?:_plural)?\s+"(.*)"$', stripped, re.DOTALL)
        if m:
            flush()
            collecting, buffer = "msgid", unescape(m.group(1))
            continue
        m = re.match(r'^msgstr(?:\[\d+\])?\s+"(.*)"$', stripped, re.DOTALL)
        if m:
            flush()
            collecting, buffer = "msgstr", unescape(m.group(1))
            continue
        m = re.match(r'^"(.*)"$', stripped, re.DOTALL)
        if m and collecting:
            buffer += unescape(m.group(1))
            continue
        flush()
    flush()
    return out


def unquote(raw: str) -> str:
    value = re.sub(r"\s+#.*$", "", raw).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return unescape(value[1:-1])
    return value


def from_yaml(source: str, label: str):
    """Best-effort: ``key: value``, ``- item`` and ``|``/``>`` block scalars.

    Anchors, aliases and flow collections are skipped rather than guessed at.
    """
    out, stack = [], []
    lines = source.splitlines()

    def path_at(indent, key):
        while stack and stack[-1][0] >= indent:
            stack.pop()
        return " · ".join([label] + [k for _, k in stack] + [key])

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or re.match(r"^\s*#", line) or re.match(r"^\s*---", line):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        item = re.match(r"^-\s+(.*)$", stripped)
        if item and ": " not in item.group(1):
            text = unquote(item.group(1))
            if text:
                out.append((path_at(indent, "-"), text))
            i += 1
            continue

        kv = re.match(r"""^["']?([\w.\-\s]+?)["']?\s*:\s*(.*)$""", stripped)
        if not kv:
            i += 1
            continue
        key, raw = kv.group(1), kv.group(2).strip()

        if raw == "":
            path_at(indent, key)
            stack.append((indent, key))
            i += 1
            continue

        if re.match(r"^[|>][-+]?\d*$", raw):
            block, j = [], i + 1
            while j < len(lines):
                nxt = lines[j]
                if not nxt.strip():
                    j += 1
                    continue
                if len(nxt) - len(nxt.lstrip()) <= indent:
                    break
                block.append(nxt.strip())
                j += 1
            text = " ".join(block).strip()
            if text:
                out.append((path_at(indent, key), text))
            i = j
            continue

        if raw[0] in "&*[{":
            i += 1
            continue

        text = unquote(raw)
        if text:
            out.append((path_at(indent, key), text))
        i += 1
    return out


def extract(path: Path, force=None):
    suffix = force or path.suffix.lower().lstrip(".")
    source = path.read_text(encoding="utf-8-sig")
    label = path.name
    if suffix in ("json", "arb"):
        return from_json(json.loads(source), label, [])
    if suffix in ("po", "pot"):
        return from_po(source, label)
    if suffix in ("yml", "yaml"):
        return from_yaml(source, label)
    if suffix == "txt":
        return [
            (f"{label}:{i + 1}", line.strip())
            for i, line in enumerate(source.splitlines())
            if line.strip()
        ]
    raise ValueError(f"unsupported format .{suffix}")


# ── checks ───────────────────────────────────────────────────────────────────

PLACEHOLDER = re.compile(r"\{\{?[^{}]*\}?\}|%[\d$sdfx@]*|\$\{[^}]*\}|<[^>]+>")


def string_check(entries, rule, allowed):
    if not rule.get("pattern"):
        return []
    pattern = compile_pattern(rule["pattern"], rule.get("flags", "u"))
    ignoring = (
        compile_pattern(rule["ignoring"], rule.get("ignoringFlags", "iu"))
        if rule.get("ignoring")
        else None
    )
    unless = (
        compile_pattern(rule["unless"], rule.get("unlessFlags", "iu"))
        if rule.get("unless")
        else None
    )

    hits = []
    for path, text in entries:
        if text in allowed:
            continue
        if unless and unless.search(text):
            continue
        subject = ignoring.sub("", text) if ignoring else text
        if pattern.search(subject):
            hits.append({"path": path, "text": text})
    return hits


def title_case_check(entries, rule, profile, allowed):
    nouns = sorted((nfc(n) for n in profile.get("properNouns", [])), key=len, reverse=True)
    threshold = rule.get("threshold", 2)
    hits = []
    for path, text in entries:
        if text in allowed:
            continue
        stripped = PLACEHOLDER.sub(" ", text)
        for noun in nouns:
            stripped = stripped.replace(noun, " ")
        words = [
            re.sub(r"^[^\w]+|[^\w]+$", "", w, flags=re.UNICODE)
            for w in re.split(r"[\s/|·—–-]+", stripped)
        ]
        words = [w for w in words if w]
        capitalised = 0
        for w in words[1:]:
            if len(w) > 1 and w == w.upper():
                continue  # acronym
            if w[0] != w[0].lower() and w[0] == w[0].upper():
                capitalised += 1
        if capitalised >= threshold:
            hits.append({"path": path, "text": text})
    return hits


def corpus_check(entries, rule):
    present = []
    for label, pattern in (rule.get("variants") or {}).items():
        compiled = compile_pattern(pattern, rule.get("flags", "u"))
        examples = [(p, t) for p, t in entries if compiled.search(t)]
        if examples:
            present.append((label, examples))
    if len(present) < 2:
        return []
    return [
        {"path": p, "text": t, "variant": label}
        for label, examples in present
        for p, t in examples[:3]
    ]


def check(entries, rules, profile, register):
    entries = [(p, nfc(t)) for p, t in entries]
    findings = []
    for rule in rules:
        severity = rule.get("severityByRegister", {}).get(
            register, rule.get("severity", "error")
        )
        allowed = {
            nfc(s)
            for s in (rule.get("allow", []) + profile.get("allow", {}).get(rule["id"], []))
        }
        kind = rule.get("kind", "string")
        if kind == "corpus":
            hits = corpus_check(entries, rule)
        elif kind == "titlecase":
            hits = title_case_check(entries, rule, profile, allowed)
        else:
            hits = string_check(entries, rule, allowed)
        if hits:
            findings.append(
                {
                    "id": rule["id"],
                    "severity": severity,
                    "why": rule["why"],
                    "instead": rule["instead"],
                    "falsePositives": rule.get("falsePositives"),
                    "occurrences": hits,
                }
            )
    rank = {"error": 0, "warn": 1}
    findings.sort(key=lambda f: (rank[f["severity"]], -len(f["occurrences"])))
    return findings


# ── cli ──────────────────────────────────────────────────────────────────────


def main(argv):
    # Windows consoles default to a legacy code page, and every line of this
    # report contains Vietnamese. Without this the first print raises
    # UnicodeEncodeError and the run dies after one finding — which looks
    # exactly like a clean-ish result.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    flags = [a for a in argv if a.startswith("--")]
    targets = [a for a in argv if not a.startswith("--")]

    def flag(name, default=None):
        for f in flags:
            if f.startswith(f"--{name}="):
                return f.split("=", 1)[1]
        return default

    if "--help" in flags or not targets:
        print(__doc__)
        return 0 if "--help" in flags else 2

    strict = "--strict" in flags
    show_all = "--all" in flags
    profile_name = flag("profile", "consumer-saas")
    rules, profile, register = load_rules(profile_name)

    files = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*") if p.is_file()))
        elif path.exists():
            files.append(path)

    entries, skipped = [], []
    for path in files:
        try:
            entries.extend(extract(path, flag("format")))
        except Exception as error:  # noqa: BLE001 — report and continue
            skipped.append(f"{path} — {error}")

    if not entries:
        print("Read 0 strings. Nothing was checked, which is not the same as a pass.")
        for s in skipped:
            print(f"  {s}")
        return 2

    findings = check(entries, rules, profile, register)
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warn")
    limit = None if show_all else 5

    print(
        f"\nvietnamese-voice · profile {profile_name} · register {register}"
        f" · {len(entries)} strings from {len(files)} file(s)\n"
    )
    for f in findings:
        tag = "error" if f["severity"] == "error" else "warn "
        print(f"{tag} {f['id']} — {len(f['occurrences'])} occurrence(s)")
        print(f"      {f['why']}")
        print(f"      Write instead: {f['instead']}")
        if f.get("falsePositives"):
            print(f"      False positives: {f['falsePositives']}")
        for o in f["occurrences"][:limit]:
            variant = f" [{o['variant']}]" if o.get("variant") else ""
            print(f"        {o['path']}{variant}\n          \"{o['text']}\"")
        if limit and len(f["occurrences"]) > limit:
            print(f"        … and {len(f['occurrences']) - limit} more (--all)")
        print("")

    if skipped:
        print(f"Skipped {len(skipped)} file(s):")
        for s in skipped:
            print(f"  {s}")
        print("")

    if not findings:
        print("Clean. No known tells.")
        print(
            "This is a floor, not a standard — it cannot hear rhythm. "
            "Read reference/naturalness.md."
        )
        return 0

    print(
        f"{errors} error(s), {warnings} warning(s). "
        "A rule you disagree with belongs in the profile, not in an ignore comment."
    )
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
