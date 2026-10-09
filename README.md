# skills

Portable [agent skills](https://code.claude.com/docs/en/skills) for Claude Code.
Each folder is one skill, self-contained, with no dependency on the project it
came out of.

| Skill | What it does |
| --- | --- |
| [vietnamese-voice](vietnamese-voice/) | Makes Vietnamese copy read as though a Vietnamese person wrote it, not as a well-translated English sentence. Register-aware principles, eight industry profiles, and a rule engine with CLI, vitest and Python harnesses. |
| [seo-writing](seo-writing/) | Writes, rewrites, reviews and plans blog posts that rank and get cited, with every number traced to a source. Research, 12 post templates, a 100-point review, site audits, charts, images, repurposing and translation. |
| [seo-keyword-map](seo-keyword-map/) | Decides which page should rank for which keyword from what Google actually shows. Keyword research and SERP pulls through DataForSEO, grouping by the kind of page that ranks, a validated keyword-map workbook, and the next pages to build. Type "what now" in a project to start. |

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

On Windows without Developer Mode, a junction works the same and needs no
admin rights: `New-Item -ItemType Junction -Path ... -Target ...`.

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

## seo-writing

A post is worth publishing when it answers the reader better than page one,
every claim traces to a source, and it reads like a person wrote it. What ranks
in search and what AI answer engines cite are the same thing, so the skill
optimises for those three and nothing else.

### What it does

| Command | |
| --- | --- |
| `write`, `rewrite`, `update` | Research → source ledger → outline → draft → check → fresh-eyes review → deliver |
| `review` (`--seo`, `--geo`), `factcheck` | 100-point score, P0–P3 findings, every claim checked against its source |
| `research`, `plan brief/outline/strategy/calendar/cluster` | Source ledgers, recent-discussion briefs, planning documents, hub-and-spoke clusters |
| `audit`, `cannibalization`, `decay`, `taxonomy`, `locales` | Link graph, overlapping posts, traffic decay from Search Console exports, tag health |
| `schema`, `repurpose`, `translate`/`localize`, `voice`, `chart`, `image` | JSON-LD, channel versions, hreflang, a `BLOG.md` context file, SVG charts, licensed or generated images |

### What keeps it honest

- **No fabricated anything.** Every figure in a post comes from a page someone
  opened, cited at the claim. No invented anecdotes, customers or test results.
- **A checker that fails the build.** `scripts/check_post.py` exits non-zero on
  leftover placeholders, skipped headings, images without alt text, impossible
  dates, invalid JSON-LD and em dashes. It warns on numbers without a source and
  on machine-written filler.
- **The author doesn't review their own draft.** A separate pass scores it, and
  nothing ships with a P0 or P1.

### Running it

```bash
python seo-writing/scripts/check_post.py post.md                 # lint one post
python seo-writing/scripts/check_post.py --site content/blog     # orphans, overlaps, staleness, tags
python seo-writing/scripts/decay.py gsc-pages-compare.csv        # posts losing Search traffic
python seo-writing/scripts/chart.py spec.json --mdx              # accessible SVG chart
python seo-writing/scripts/images.py stock "cast iron skillet"   # licensed stock, credit logged
```

Python 3.9+, standard library only. Pillow is optional, for resizing images.
Image generation uses whichever of `OPENAI_API_KEY` or `GEMINI_API_KEY` is set,
or an image MCP tool if one is loaded.

### What it does not do

It doesn't measure live sites (Core Web Vitals, crawling, indexing). It hands
those to an SEO skill. It can't supply first-hand experience either: when a post
needs data or opinions only you have, it asks rather than inventing them.

---

## seo-keyword-map

A keyword map says which page should rank for which search. Most maps group keywords
by how they sound. This one groups them by what Google shows: two keywords share a page
when Google answers them with the same kind of page, and get separate pages when it
doesn't.

That turns out to need care at the volumes local businesses live on. At 20–300
searches a month, about half of a keyword's top 10 changes between two pulls an hour
apart, and the same few local firms' homepages rank for every service. So the skill
pulls each SERP twice, labels every result (service page, article, directory,
association), and decides on the kind of page first and shared URLs second.

### What it does

| Command | |
| --- | --- |
| `what now` | Where the project stands and the one next step, with its cost |
| `init` | Sets a client folder up: `seo-project.json` and an empty `keyword-map.xlsx` |
| `research`, `triage` | Service × place volume grid, competitor rankings, suggestions, related searches, imports; every candidate kept, folded or removed with a reason |
| `serp`, `group` | Pulls and classifies Google results, then reassigns keywords to pages with the evidence noted on each move |
| `plan`, `brief` | The next pages to build, with keywords, FAQ questions and the existing page to copy; a brief per page that `seo-writing` writes from, carrying the site's own page rules |
| `ranks` | Positions and map-pack presence, on demand or on a schedule you pick, added to the Rank tracker with a report of what moved |

### What keeps it safe to hand to a team

- **The workbook only changes through a validated changes file.** `apply.py --check`
  refuses a page with no main keyword or two, an unknown keyword, an untyped new page;
  every write makes a backup first.
- **A shared API account with a cap.** Every paid step states its estimate and stops
  over the per-run limit; every call is logged per client. Credentials live in the
  user folder and the scripts warn if they turn up anywhere else.
- **Client decisions are recorded, not re-argued.** `seo-project.json` holds what is
  specific to a client, so the skill itself never changes per project.

### Running it

```bash
pip install openpyxl
python seo-keyword-map/scripts/status.py          # in a client folder: state and next step
python seo-keyword-map/scripts/serp.py pull        # Google results for keywords without data
python seo-keyword-map/scripts/group.py            # grouping evidence report
python seo-keyword-map/scripts/apply.py changes.json --check
```

Needs a [DataForSEO](https://dataforseo.com) account for research and SERP pulls; a
200-keyword local project costs about a dollar. Python 3.9+, `openpyxl`.

### What it does not do

It doesn't write the pages (it hands `seo-writing` a brief),
or know what the client sells: a keyword whose results show another trade needs a
person who knows the business.

---

## License

[MIT](LICENSE). Copy a skill into your own project, change the rules, ship it —
attribution in the file is enough.
