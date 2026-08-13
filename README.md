# skills

Portable [agent skills](https://code.claude.com/docs/en/skills) for Claude Code.
Each folder is one skill, self-contained, with no dependency on the project it
came out of.

| Skill | What it does |
| --- | --- |
| [vietnamese-voice](vietnamese-voice/) | Makes Vietnamese copy read as though a Vietnamese person wrote it, not as a well-translated English sentence. Register-aware principles, eight industry profiles, and a rule engine with CLI, vitest and Python harnesses. |

## Install

Clone once, then symlink whichever skills you want. Symlinks mean `git pull`
updates every project at the same time.

**Personal — available in every project:**

```powershell
git clone https://github.com/glentless/skills.git D:\Builds\skills
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\vietnamese-voice" -Target "D:\Builds\skills\vietnamese-voice"
```

```bash
git clone https://github.com/glentless/skills.git ~/src/skills
ln -s ~/src/skills/vietnamese-voice ~/.claude/skills/vietnamese-voice
```

**Scoped to one repo, committed with it** — copy rather than symlink, so
teammates get it too:

```bash
cp -r ~/src/skills/vietnamese-voice <that repo>/.claude/skills/
```

Then invoke it by name — `/vietnamese-voice` — or just describe the task. Each
skill declares when it applies and gets picked up on its own.

---

## vietnamese-voice

Vietnamese written by someone thinking in English comes out grammatically
correct, vocabulary-accurate, and instantly recognisable as a translation. The
reader's word for it is *lủng củng*. They often cannot point at the broken word,
because no word is broken — the habits are what give it away.

This came out of shipping a Vietnamese product where a teacher read the site and
said *"đọc rất lủng củng, rõ ràng là tiếng Anh dịch sang tiếng Việt"*. Every
string she reacted to had passed review, because review checks for errors and
there were none.

### There is no universal banned list

The most common mistake is not a wrong word. It is the right word in the wrong
register.

- `Vui lòng` is stilted in a consumer app and **correct in a bank**
- `Hệ thống` is an English subject in disguise on a teacher's dashboard and
  **the plain right word** on a government portal
- `bạn` is the tell of translated SaaS in one product and **exactly how a game
  should talk** in another

So the skill sets a register first — `formal`, `warm` or `casual` — and derives
the rules from it. Eight industry profiles ship with it:

| Profile | Register |
| --- | --- |
| `banking-finance`, `healthcare`, `government-public`, `b2b-enterprise` | formal |
| `consumer-saas`, `education` | warm |
| `ecommerce-retail`, `gaming-social` | casual |

Each carries its forms of address, which core rules are switched off because
they are correct in that industry, a **glossary** of terms that are not yours to
improve, and rules for what that industry specifically gets wrong — a bank's
copy training customers to hand over an OTP, a health app's copy interpreting a
lab result, a game's loot-box odds.

### What it checks

**Translationese** — `hệ thống`, `chúng tôi`, `Vui lòng`, `đường dẫn`,
`dữ liệu`, `Đã xảy ra lỗi`, officialese passives, honorifics in the wrong
register, forms of address.

**Mechanics that mark text as foreign regardless of register** — title case
(`Lưu Thay Đổi` should be `Lưu thay đổi`), English thousands separators, `$`,
AM/PM, ISO dates, untranslated leftovers, and mixed tone-mark conventions across
the catalogue.

**Unicode.** Vietnamese has two spellings per word — precomposed and decomposed.
They render identically and do not match the same regex. Text from macOS and
some CMSes arrives decomposed, so a guard that skips NFC normalisation silently
passes what it exists to catch. Both the patterns and the text are normalised.

### Running it

```bash
# any format: JSON, ARB, gettext PO, YAML, iOS .strings, Android XML
node harness/check-vietnamese.mjs --profile=education src/messages/

# same rules, no Node — for Django/Flask
python harness/check_vietnamese.py --profile=government-public locale/vi/

# JS/TS where strings are a module: also calls message functions
#   and checks what they produce
cp harness/voice.test.ts <project>/
```

All three read the same `rules/rules.json`, so a rule is written once and
enforced everywhere. No dependencies in any of them.

### What it does not do

The guard catches known tells. It cannot hear rhythm, and a catalogue can pass
every rule and still read as a translation. It is a floor, not a standard.

The skill says so where it matters, and says what to do instead: get a native
speaker who uses products in that category, from the right region, to read it on
the actual screens.

Not Vietnamese-only in spirit — the same shape works for any language where
politeness and address are grammatical rather than optional.

---

## License

[MIT](LICENSE). Copy a skill into your own project, change the rules, ship it —
attribution in the file is enough.
