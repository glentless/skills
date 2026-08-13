# VOICE.md — how <PRODUCT> writes Vietnamese

Every user-facing string in this product is Vietnamese, and it has to read as
though a Vietnamese person wrote it — not as though an English sentence was
translated well.

Correct is not the same as natural, and the gap between them is invisible if you
are thinking in English while you type Vietnamese.

**Read this before writing or editing anything in `<PATH TO MESSAGES>`.** The
rules below are enforced by `<PATH TO voice.test.ts>`, which fails the build on
the specific words that give the game away. The test catches the known tells; it
cannot catch the rhythm, so the principles matter more than the word list.

---

## 1. Who the product is talking to

| Reader | Address them as | Never |
| --- | --- | --- |
| <primary user> | `<pronoun>` | `bạn`, … |
| <secondary user> | `<pronoun>` | … |
| The product itself | `bên mình`, or no subject at all | `chúng tôi`, `hệ thống` |

Notes on choices that are easy to get wrong here:

- <e.g. a bare `cô` addresses a woman; the audience is mixed, so `thầy cô`>
- <e.g. to a parent, the child is `con`, not `em`>

---

## 2. Words to use and words to avoid

The left column is what the copy said before a Vietnamese reader called it
stilted. Most are not wrong — they are just not what anyone says.

| Instead of | Write | Why |
| --- | --- | --- |
| `đường dẫn`, `liên kết` | `link` | Everyone says "gửi link". `đường dẫn` is dictionary Vietnamese. |
| `hệ thống` | `<Product>`, `máy`, or nothing | "The system" is an English subject. |
| `chúng tôi` | `bên mình`, or drop it | <who actually made this> |
| `Vui lòng …` | `… giúp nhé` | `Vui lòng` is "Please" in a suit. |
| `Đã xảy ra lỗi` | `Có lỗi rồi`, or name what failed | Say what broke. |
| `Chưa có dữ liệu` | `Chưa có gì ở đây` | `dữ liệu` is a database word. |
| `nhấp chuột` | `bấm` | Nobody clicks a mouse on a phone. |
| <add rows as you add test rules> | | |

**Keep the loanwords people actually use.** `link`, `file`, `email`, `copy`,
`online`, `Word`, `Excel`, `Zalo`.

---

## 3. Softeners

Use `nhé`, `giúp`, `rồi`, `ạ`, `nha`, `thôi` **when the product is asking
something of the reader, or interrupting her**.

Do **not** use them in field validation errors, labels, buttons, table headers,
status chips, or anything read under time pressure.

The rule of thumb: **a softener earns its place when the sentence costs the
reader something** — a failure, a wait, a request, a refusal. Everywhere else it
is noise.

---

## 4. Rhythm

- Short clauses joined by commas beat subordinate clauses.
- No semicolons.
- Em dashes sparingly.
- Front-load the outcome: what happened, then what to do.
- One idea per string.

---

## 5. Register per surface

- **<surface>** — <who reads it, how it should feel, softener policy>
- **<surface>** — …

---

## 6. Checklist before you add or change a string

1. Who reads it? Is the address right?
2. Read it out loud in Vietnamese. Would a person say it that way?
3. Is there an abstract noun where a verb belongs?
4. Is `hệ thống` or `chúng tôi` the subject? Replace it.
5. Does it cost the reader something? Add exactly one softener.
6. Is it a label, a button, or a field error? Remove every softener.
7. Run `<test command>`.

If you add a word to the banned list in the test, add a row to §2 here too. The
test is the enforcement; this file is the reason.
