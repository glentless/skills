# skills

Portable [agent skills](https://code.claude.com/docs/en/skills) for Claude Code.
Each folder is one skill, self-contained, with no dependency on the project it
came out of.

| Skill | What it does |
| --- | --- |
| [vietnamese-voice](vietnamese-voice/) | Makes Vietnamese copy read as though a Vietnamese person wrote it, not as a well-translated English sentence. The principles, plus a vitest guard that fails the build on the known tells. |

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

## vietnamese-voice

Vietnamese written by someone thinking in English comes out grammatically
correct, vocabulary-accurate, and instantly recognisable as a translation. The
reader's word for it is *lủng củng*. They often cannot point at the broken word,
because no word is broken — the habits are what give it away.

This skill came out of shipping a Vietnamese product where a teacher read the
site and said *"đọc rất lủng củng, rõ ràng là tiếng Anh dịch sang tiếng Việt"*.
Every string she reacted to had passed review, because review checks for errors
and there were none.

It carries two halves, and both are load-bearing:

- **The principles** (`reference/naturalness.md`) — the three habits that
  produce almost all translationese, the forms of address, when a sentence-final
  softener earns its place and when it is friction, and rhythm. These catch what
  no test can.
- **The guard** (`assets/voice.test.ts`) — a vitest file that walks the message
  catalogue and fails the build on the known tells: `hệ thống`, `chúng tôi`,
  `Vui lòng`, `đường dẫn`, `dữ liệu`, `Đã xảy ra lỗi`, `nhấp chuột`, semicolons,
  and whichever forms of address the project has ruled out.

A guard on its own produces copy that dodges banned words and still reads as a
translation. Principles on their own get forgotten in six months. The rule the
skill enforces is that every banned pattern in the test has a row in the
project's `VOICE.md` saying why — a ban with no reason gets deleted by the next
person who trips over it.

Not Vietnamese-only in spirit: the same shape works for any language where
politeness and address are grammatical rather than optional.
