# What makes Vietnamese read as translated

Vietnamese and English put the human in different places.

English UI copy is happy to be subject-less and abstract — *"An error
occurred"*, *"Data unavailable"*, *"Please try again"*. Translate that word for
word and you get Vietnamese that is comprehensible and faintly robotic, because
Vietnamese normally names who is doing what, and normally ends a sentence aimed
at a person with a particle that says how it is meant.

---

## 1. The three habits

Almost all translationese comes from these.

### Abstract nouns doing the work of verbs

*"Đã xảy ra lỗi"* is a literal cast of "an error has occurred" and nobody says
it out loud. Vietnamese says what broke.

| Instead of | Write |
| --- | --- |
| `Đã xảy ra lỗi` | `Có lỗi rồi` — or better, name it: `Chưa lưu được` |
| `Quá trình xử lý đã hoàn tất` | `Xong rồi` |
| `Việc gửi email đã thất bại` | `Chưa gửi được email` |

### A system as the subject

*"Hệ thống sẽ xử lý file"* is "the system will process the file" wearing a
Vietnamese coat. `Hệ thống` is banned in user-facing copy. Three ways out:

1. Name the product: *"Mầm Class đọc file"*
2. Use `máy` — what people actually say about a computer doing something:
   *"máy chấm"*, *"máy đọc"*
3. Drop the subject entirely: *"Đang đọc file"*

Same for `chúng tôi`. That is a company voice. A small business says
`bên mình`. Best of all is no subject: *"Gửi link đặt lại mật khẩu"* needs no
`chúng tôi`.

### No softeners

This is the big one, and the one that survives a *good* translation. Vietnamese
marks the **relationship** at the end of the clause: `nhé`, `giúp`, `ạ`, `rồi`,
`thôi`, `nha`. Copy with zero particles reads as a form letter from an
institution even when every word is right. Copy with a particle in every string
reads as babying. Section 3 has the rule.

---

## 2. Forms of address

Vietnamese has no neutral "you". Pick per reader, and be consistent.

| Reader | Address them as | Never |
| --- | --- | --- |
| Teacher | `thầy cô` | `bạn`, a bare `cô`, `quý thầy cô` |
| Student / young person | `em`, `các em` | `bạn`, `các bạn` |
| Parent | `anh/chị`; their child is `con` | `quý phụ huynh`, the child as `em` |
| Older customer | `cô/chú`, `anh/chị` | `bạn` |
| Broad anonymous public | `bạn` (only here) | — |
| The product itself | `bên mình`, product name, or no subject | `chúng tôi`, `hệ thống` |

Traps that bite:

- **A bare `cô` addresses a woman.** If your audience is mixed-gender, `thầy cô`
  covers both. Where a neutral noun reads better, use the role: `giáo viên`,
  `khách hàng`, `phụ huynh`.
- **`bạn` is the tell of translated SaaS.** It is grammatical and it is the
  default of every localised product in this market, which is exactly why not
  using it is worth something. Only reach for it when you truly do not know who
  is reading.
- **To a parent, the child is `con`**, not `em`. `em` is what a teacher calls
  them; a parent reading about their own child expects `con`.
- **`quý …` is the register of an official circular**, not a tool.

---

## 3. Softeners: where the warmth actually lives

Vietnamese carries politeness at the end of the clause. Getting this right is
most of the difference between "friendly product" and "government form".

| Particle | Does what | Example |
| --- | --- | --- |
| `nhé` | Softens an instruction into a suggestion | *"Thầy cô thử lại nhé."* |
| `nha` | Same, warmer and more casual | *"Chờ chút nha."* |
| `giúp` | Makes a request a favour, not an order | *"Thầy cô chọn đáp án giúp."* |
| `rồi` | Marks a completed state warmly | *"Đã lưu rồi."*, *"Có lỗi rồi."* |
| `ạ` | Deferential. Sparingly, and only upward | *"Dạ vâng ạ."* |
| `thôi`, `là được` | Makes a small task sound small | *"Mỗi dòng một tên là được."* |

**The rule:** a softener earns its place when the sentence **costs the reader
something** — a failure, a wait, a request, a refusal. Everywhere else it is
noise.

So: use them when the product is asking something of the reader or interrupting
her. Do **not** use them in:

- **Field validation errors.** Read at speed while fixing a form. *"Nhập tên
  lớp."* is right; *"Thầy cô nhập tên lớp giúp nhé."* is four words of friction
  on the eleventh attempt.
- **Labels, buttons, table headers, status chips.** *"Lưu"*, *"Đã nộp"*,
  *"Cần chấm"*.
- **Anything read under time pressure** — a test in progress, a checkout, a
  countdown.
- **Numbered steps and instructions that name a button.** *"Bấm Gửi điểm"*,
  never *"Bấm Gửi điểm nhé ạ"*.

---

## 4. Word swaps

The left column is not wrong. It is just not what anyone says.

| Instead of | Write | Why |
| --- | --- | --- |
| `đường dẫn`, `liên kết` | `link` | Everyone says "gửi link". `đường dẫn` is dictionary Vietnamese. |
| `hệ thống` | product name, `máy`, or nothing | "The system" is an English subject. |
| `chúng tôi` | `bên mình`, or drop it | Company voice on a small product. |
| `Vui lòng …` | `… giúp`, `… nhé` | `Vui lòng` is "Please" in a suit. |
| `Đã xảy ra lỗi` | `Có lỗi rồi`, or name what failed | Say what broke. |
| `Chưa có dữ liệu` | `Chưa có gì ở đây` | `dữ liệu` is a database word. |
| `… chưa đúng định dạng` | `… này chưa đúng` | Nobody cares what a format is. |
| `Chào mừng trở lại` | say what they can do now | Calque of "Welcome back". |
| `được thực hiện`, `được tiến hành` | an active verb | Officialese, not speech. |
| `nhấp chuột`, `nhấn chuột` | `bấm` | Nobody clicks a mouse on a phone. |
| `tùy chọn` | `chọn`, or name the thing | Menu-ese. |
| `xác nhận thành công` | `Xong rồi`, `Đã lưu rồi` | Status-report voice. |

**Keep the loanwords people actually use.** `link`, `file`, `email`, `copy`,
`online`, `app`, `Word`, `Excel`, `Zalo`. A person says *"file Word"*, never
*"tệp Word"*.

**But loanword noun, Vietnamese verb on the button.** Say `link`, and label the
button `Sao chép link`. That pairing is what Zalo and Facebook do.

**Pick one word per concept and keep it.** Two words for the same operation
(`bóc tách` and `tách`) reads as two people wrote the app.

---

## 5. Rhythm

- **Short clauses joined by commas beat subordinate clauses.** English builds
  one sentence with a `which`; Vietnamese builds two halves with a comma.
- **No semicolons.** They do not appear in ordinary written Vietnamese and read
  as imported punctuation. Use a full stop.
- **Em dashes sparingly**, and only where a Vietnamese writer would pause — not
  everywhere the English original had one.
- **Front-load the outcome.** *"Đã giao xong. Gửi link dưới đây cho học sinh."*
  What happened, then what to do. Never the reasoning first.
- **One idea per string.** A 90-word paragraph of hint text does not get read to
  the end. Three sentences means three strings, or a screen with a different
  shape.

---

## 6. Register per surface

One product speaks to several people and must not use one voice for all of them.

- **Professional / staff-facing** — a competent colleague. Direct, unfussy,
  assumes they know their job. Softeners on failures and requests only.
- **Runtime under pressure** (a test, a checkout, a timer) — shortest sentences
  in the product. Nothing congratulatory: finishing a required task is not an
  achievement.
- **The outsider-facing report** (a parent, a client receiving a summary) —
  someone with one minute who did not ask for an app, and the only surface a
  stranger judges. No jargon at all. Never a word that reads as a verdict on a
  person: `nên luyện thêm`, never `yếu`.
- **Landing and pricing** — if there is a founder, this is their voice. Do not
  rewrite it for style. Anti-reference: *"nền tảng quản lý … toàn diện"* and
  every other generic-SaaS sentence in this market.
- **An AI assistant persona** — the one place a first person is allowed. If it
  calls itself `em`, then the people it talks about must be named explicitly
  (`học sinh`, `các em`, `khách`), because in one answer `em` would otherwise be
  both the assistant and the subject. Warmth via `nhé` / `nha` / `ạ` a few times
  per answer, not once per clause — and never on a label or a numbered step.

If an LLM generates the Vietnamese, put these constraints in the system prompt
and **test the live output**. A model drifting back to flat documentation prose
is invisible unless something asserts the warmth is still there.

---

## 7. Checklist before you add or change a string

1. Who reads it? Is the address right for that person?
2. Read it out loud in Vietnamese. Would a person say it that way, or only
   write it?
3. Is there an abstract noun where a verb belongs?
4. Is `hệ thống` or `chúng tôi` the subject? Replace it.
5. Is it asking something of the reader, or delivering bad news? Add exactly
   one softener.
6. Is it a label, a button, or a field error? Remove every softener.
7. Run the guard test.

If you add a word to the banned list in the test, add a row to the project's
VOICE.md too. The test is the enforcement; the document is the reason.
