# Mechanics

These are register-independent. A bank, a game and a school all get them the
same way, and getting one wrong marks the text as foreign faster than any word
choice does.

---

## 1. Vietnamese does not title-case

English UI capitalises every significant word: *Save Changes*, *Forgot
Password*. Vietnamese capitalises the first word and proper nouns. That is all.

| Wrong | Right |
| --- | --- |
| `Lưu Thay Đổi` | `Lưu thay đổi` |
| `Quên Mật Khẩu` | `Quên mật khẩu` |
| `Danh Sách Học Sinh` | `Danh sách học sinh` |

This survives translation almost every time, because the translator works
string-by-string and the capitalisation looks like part of the source. It is the
single most visible tell on a screen.

Headings, buttons, tab labels, table headers, menu items — all sentence case.

## 2. Numbers

Vietnamese groups with a **dot** and marks decimals with a **comma**. Exactly
the opposite of English.

| | |
| --- | --- |
| One million | `1.000.000` |
| Zero point eight | `0,8` |
| Percentage | `85%` or `85 %` |

A `1,500,000` in your catalogue is an en-US locale leaking through a formatter,
not a typo — fix the formatter, not the string.

Spoken shorthand in casual copy: `50k` = 50.000, `2 triệu` = 2.000.000, `1 tỷ` =
1.000.000.000. Keep the full form on invoices, checkout totals and anything
legal.

## 3. Money

- Symbol **after** the number: `1.000.000 ₫`, or `1.000.000đ`
- `VNĐ` and `VND` both appear; pick one
- Never a `$` unless the product genuinely prices in dollars

## 4. Dates and time

- **Day first**: `13/08/2026`, or `13 tháng 8 năm 2026`
- **24-hour clock**: `14h30`, `14:30`, `14 giờ 30`. Never `2:30 PM`
- Weekdays are numbered from Sunday: `Chủ nhật`, `Thứ hai`, `Thứ ba` … `Thứ
  bảy`. `Thứ hai` is Monday, not "second day"
- An ISO `2026-08-13` on a screen a person reads is a leaked timestamp

## 5. No plurals, and classifiers

Vietnamese nouns do not inflect for number. The count does the work.

- `3 học sinh` — never a plural marker
- `nhiều bài tập`, `các lớp`, `những câu hỏi`

Counting usually takes a **classifier** between the number and the noun, and the
right one depends on the thing:

| Classifier | For |
| --- | --- |
| `cái` | generic objects |
| `con` | animals, and some objects (`con dao`, `con đường`) |
| `chiếc` | vehicles, single items of a pair |
| `quyển` / `cuốn` | books |
| `bài` | exercises, articles, lessons |
| `tờ` | sheets of paper |
| `bức` | letters, pictures |

`3 cái bài` is wrong; `3 bài` is right. A wrong classifier is a strong tell —
when unsure, drop it rather than guess, which is usually acceptable.

Interpolated counts are where this breaks: a `{count} items` template that works
in English needs the classifier baked into the Vietnamese string, and it may
differ per noun. Do not build one generic pluraliser.

## 6. Vietnamese runs longer

Expect **10–30% more characters** than the English source, sometimes more for
short UI labels where English has a one-syllable word and Vietnamese needs three
syllables (`Save` → `Lưu thay đổi`).

Consequences:
- Buttons and tabs overflow. Test the longest string, not the average one
- Diacritics need vertical room. Tight `line-height` clips `ệ` and `ỳ`; a
  1.5 line-height that looks generous in English is normal here
- `text-transform: uppercase` destroys legibility on diacritics and is common in
  English design systems. Turn it off for Vietnamese

## 7. Unicode: NFC, always

Vietnamese has **two Unicode spellings for the same word**:

- Precomposed (NFC): `ệ` is one code point, U+1EC7
- Decomposed (NFD): `ê` + combining dot below, or even `e` + circumflex + dot

They render identically. They are different strings. `"Hệ" === "Hệ"` can be
`false`.

This breaks more than a guard:

- Search and filter miss matches
- Deduplication fails
- Database uniqueness constraints let both through
- Sorting misplaces words
- A regex written in NFC does not match NFD text

macOS filesystems, some CMSes, and some XML toolchains produce NFD. **Normalise
to NFC at every boundary** — on input, before storing, before comparing.

```js
const clean = input.normalize("NFC");
```

```python
import unicodedata
clean = unicodedata.normalize("NFC", text)
```

```sql
-- Postgres, with the unaccent/normalize available in 13+
SELECT normalize(col, NFC) FROM t;
```

The harnesses in this skill normalise both the text and the patterns before
matching, which is the only reason they catch anything in NFD input.

## 8. Tone-mark placement: pick one

Two conventions are in use and neither is an error:

| kiểu cũ | kiểu mới |
| --- | --- |
| `hoà` | `hòa` |
| `thuý` | `thúy` |
| `khoá` | `khóa` |

Most modern software and dictionaries use **kiểu mới** (tone on the first
vowel). Pick one, record it in `VOICE.md`, and stay consistent — a catalogue
containing both was written by two people and reads that way.

This only applies to **open** syllables. `toàn`, `khoản`, `chuyện` have one
correct spelling and are not part of the choice.

Same for `i`/`y` in Sino-Vietnamese syllables: `kĩ`/`kỹ`, `bác sĩ`/`bác sỹ`.
`sĩ` and `kỹ` are the more standard modern forms. Consistency matters more than
which you pick.

## 9. Punctuation

- **No semicolons.** They do not occur in ordinary written Vietnamese
- Em dashes sparingly, only where a Vietnamese writer would pause
- Quotes: `"…"` or `“…”`. `«…»` reads as translated French
- Ellipsis `…` rather than three dots
- No space before `:` `?` `!` — that is a French habit, not a Vietnamese one

## 10. What machine translation leaves behind

If any Vietnamese in the project started as Google Translate or DeepL output,
look for these specifically:

- Every softener missing — MT never produces `nhé`, `giúp`, `ạ`
- `bạn` everywhere, because MT has to pick a pronoun and picks the safe one
- Abstract nouns preserved from English: `việc thực hiện`, `sự thay đổi`
- English word order in questions
- Title case preserved from the source
- Placeholders translated or reordered wrongly: `{count} học sinh` becoming
  `học sinh {count}` where the classifier now sits wrong

MT output that has been lightly edited is the hardest case in this whole skill,
because every sentence is defensible and the whole is flat.
