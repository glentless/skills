# VOICE.md — how <PRODUCT> writes Vietnamese

Every user-facing string in this product is Vietnamese, and it has to read as
though a Vietnamese person wrote it — not as though an English sentence was
translated well.

Correct is not the same as natural, and the gap is invisible if you are thinking
in English while you type Vietnamese.

**Read this before writing or editing anything in `<PATH TO MESSAGES>`.** It is
enforced by `<GUARD COMMAND>`, which fails the build on the known tells. The
guard catches words; it cannot hear rhythm, so the principles below matter more
than the list.

---

## 0. The settings

These four decide everything else. Set them once.

| Setting | This project | Why |
| --- | --- | --- |
| **Register** | `formal` / `warm` / `casual` | <what the reader loses if we get it wrong> |
| **Profile** | `<rules/profiles/NAME.json>` | |
| **Region** | northern / southern / diaspora | <where our users are> |
| **Tone marks** | kiểu mới (`hòa`) / kiểu cũ (`hoà`) | consistency, not correctness |

---

## 1. Who the product is talking to

| Reader | Address them as | Never |
| --- | --- | --- |
| <primary user> | `<pronoun>` | |
| <secondary user> | `<pronoun>` | |
| The product itself | `<chúng tôi / bên mình / mình / no subject>` | |

Choices here that are easy to get wrong, and why we made them:

- <e.g. a bare `cô` addresses a woman; our users are mixed, so `thầy cô`>
- <e.g. to a parent, the child is `con`, not `em`>

---

## 2. Words

The left column is usually not wrong. It is just not what anyone says *in this
register*.

| Instead of | Write | Why |
| --- | --- | --- |
| | | |

**Locked terms** — prescribed by law, by a regulator, or by documents our users
already hold. Not style choices:

| Term | Never | Why |
| --- | --- | --- |
| | | |

**Loanwords we keep:** `link`, `file`, `email`, `<others>`.

---

## 3. Softeners

<Delete whichever does not apply.>

- **formal** — none. Courtesy comes from distance and the honorific.
- **warm** — only where the sentence costs the reader something: a failure, a
  wait, a request, a refusal.
- **casual** — plentiful. `nhé`, `nha`, `luôn`.

Never on labels, buttons, table headers, status chips, field validation errors,
numbered steps, or anything read under time pressure.

---

## 4. Mechanics

- Sentence case, never title case: `Lưu thay đổi`
- Numbers `1.000.000`, decimals `0,8`, money `1.000.000 ₫`
- Dates `13/08/2026`, times `14h30`
- No semicolons
- All text normalised to NFC

---

## 5. Register per surface

| Surface | Reader | Voice | Softeners |
| --- | --- | --- | --- |
| | | | |

---

## 6. Checklist before you add or change a string

1. Which surface, and what register is it?
2. Who reads it? Is the address right?
3. Read it out loud. Would a person say it, or only write it?
4. Abstract noun where a verb belongs?
5. Is the subject an institution we are not?
6. Does it cost the reader something? Exactly one softener.
7. Label, button, or field error? No softeners.
8. Sentence case. Vietnamese number and date format.
9. Run `<GUARD COMMAND>`.

If you add a pattern to the rules, add a row to §2 here too. The guard is the
enforcement; this file is the reason.

---

## 7. Review

The guard is a floor. Before anything ships to real users, <NAME> reads it on the
actual screens and answers: *"đọc có tự nhiên không, hay giống dịch từ tiếng
Anh?"*
