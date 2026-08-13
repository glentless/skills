# What makes Vietnamese read as translated

> **Read [registers.md](registers.md) first.** Everything below assumes a
> register is already set. Most of it is written from `warm`, the default, where
> translationese does the most damage. Where `formal` and `casual` differ it says
> so — and where a rule flips outright, the profile in `rules/profiles/` is the
> authority, not this file. `Vui lòng` is banned here and correct in a bank.
>
> For title case, number and date formats, classifiers, text expansion and
> Unicode normalisation, see [mechanics.md](mechanics.md). Those are the same in
> every register.

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
Vietnamese coat. In `warm` and `casual`, `hệ thống` is banned — in `formal` it
is the plain right word, and the rule is off. Three ways out:

1. Name the product: *"<Tên sản phẩm> đọc file"*
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
| Patient | `anh/chị`; older: `cô/chú`, `bác` | `bạn` |
| Older customer | `cô/chú`, `anh/chị` | `bạn` |
| Bank / insurance customer | `Quý khách` | `bạn`, `mình` |
| Citizen, on a public service | `công dân`, `ông/bà` on forms | `bạn` |
| Client company (B2B) | `Quý công ty`, `anh/chị` | `bạn` |
| Shopper, casual retail | `bạn`; `anh/chị` at payment | `quý khách` mid-flow |
| Player, casual product | `bạn`, `các bạn`, the in-game role | `quý khách` |
| The product itself | depends — see below | — |

**What the product calls itself** is the choice people skip, and it leaks
register faster than anything else:

| Register | Self-reference |
| --- | --- |
| `formal` | `Ngân hàng`, `Công ty`, `Cơ quan`, `chúng tôi` |
| `warm` | `bên mình`, the product name, or **no subject at all** |
| `casual` | `mình`, `shop`, the product name |

Dropping the subject is usually the best option in `warm`: *"Gửi link đặt lại
mật khẩu"* needs no `chúng tôi` and no `bên mình`.

Traps that bite:

- **A bare `cô` addresses a woman.** If your audience is mixed-gender, `thầy cô`
  covers both. Where a neutral noun reads better, use the role: `giáo viên`,
  `khách hàng`, `phụ huynh`.
- **`bạn` is the tell of translated SaaS — in `warm` and `formal`.** It is
  grammatical and it is the default of every localised product in this market,
  which is exactly why not using it is worth something. In `casual` it is
  correct and the `ban-pronoun` rule is off; a game addressing players as
  `Quý khách` is the joke in the other direction.
- **To a parent, the child is `con`**, not `em`. `em` is what a teacher calls
  them; a parent reading about their own child expects `con`.
- **`quý …` is the register of an official circular** — which is exactly right
  when you are one. Banned in `warm` and `casual`, expected in `formal`.
  `Quý khách` is what every Vietnamese bank says, and dropping it there reads as
  a startup that has not grown up.

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

**Per register:**

- `formal` — **none.** No `nhé`, no `nha`. Courtesy comes from distance and the
  honorific. `ạ` appears only in live support, where a human is speaking.
- `warm` — by the rule above. This is where judgement is needed.
- `casual` — plentiful and correct. `nhé`, `nha`, `nhen`, `luôn`, `á`. The
  failure mode here is having too few, not too many.

So, in `warm`: use them when the product is asking something of the reader or
interrupting her. Do **not** use them in:

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

**These apply to `warm` and `casual` only.** In `formal`, most of the left
column is the correct word — see the `disable` list in the formal profiles.

The left column is not wrong. It is just not what anyone says *in a product that
is not an institution*.

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

1. What register is this surface? (If you cannot answer, stop and read
   [registers.md](registers.md).)
2. Who reads it? Is the address right for that person?
3. Read it out loud in Vietnamese. Would a person say it that way, or only
   write it?
4. Is there an abstract noun where a verb belongs?
5. Is the subject an institution the product is not? Replace it.
6. Does the sentence cost the reader something? Add exactly one softener — if
   the register allows any at all.
7. Is it a label, a button, or a field error? Remove every softener.
8. Sentence case, not title case. Numbers and dates in Vietnamese format.
9. Run the guard.

If you add a pattern to the rules, add a row to the project's `VOICE.md` too.
The guard is the enforcement; the document is the reason. A ban with no
documented reason gets deleted by the next person who trips over it.

---

## 8. What this cannot do

Be honest about the ceiling, because a green test is persuasive.

**The guard catches known tells.** It cannot hear rhythm. A catalogue can pass
every rule and still read as a translation, because the thing that gives it away
is the shape of the sentences, and no regex sees that.

**This document is written from general Vietnamese.** It does not know your
industry's terminology. In banking, medicine, law and government, the correct
word is frequently prescribed and is not a style choice — that is what a
profile's `glossary` is for, and filling it in needs someone who knows the
domain.

**Get a native speaker to read it.** Specifically:

- Someone who uses products in this category, not just someone who speaks
  Vietnamese
- From the region your users are in — see the regional note in
  [registers.md](registers.md)
- Reading it **on the actual screen**, not in a spreadsheet of strings. Half the
  problems in this file are only visible in context: a softener that is right in
  isolation and wrong as the eleventh interruption

Ask them one question: *"đọc có tự nhiên không, hay giống dịch từ tiếng Anh?"*
Then ask them to point at the worst sentence. The answer to that second question
is worth more than the whole rule list.

**When the copy is generated by an LLM**, none of the above is checkable
statically. Put the register, the address rules and the softener rule in the
system prompt — naming the banned words explicitly — and add a live test against
the real API asserting that warmth is present where it should be and absent from
labels and numbered steps. A model drifting back to flat documentation prose is
invisible otherwise.
