# Register: the dial you set before writing anything

The single most common way to get Vietnamese wrong is not a bad word. It is the
right word in the wrong register.

`Vui lòng` is stilted in a consumer app and correct in a bank. `Hệ thống` is an
English subject wearing a Vietnamese coat on a teacher's dashboard, and the
plain right word on a government portal. `bạn` is the tell of translated SaaS in
one product and exactly how a game should talk in another.

So there is no universal banned list. There are three registers, and a rule
belongs to some of them.

---

## The three

### `formal`

Bank, insurance, securities, government, hospital admin, legal, airline,
enterprise contracts.

**Distance is the courtesy.** The reader is not your friend and does not want to
be. Formality signals that the institution is taking their money or their health
seriously.

- Address: `Quý khách`, `Ông/Bà`, `Anh/Chị`, `Quý công ty`
- Self: `Ngân hàng`, `Công ty`, `Cơ quan`, `chúng tôi`
- `Vui lòng`, `Hệ thống`, `dữ liệu`, `đường dẫn` — all correct
- No sentence-final particles. No `nhé`, no `nha`. `ạ` only in live support
- Officialese is tolerated **where it mirrors a real legal phrase**, and nowhere
  else. An error message is not a statute

The failure mode here is not stiffness. It is *false warmth*: a chatty tone on a
screen about someone's mortgage reads as unserious.

### `warm`

SaaS, education, clinics, small business tools, D2C services, marketplaces'
seller side. **The default.**

**A competent person talking to another.** Direct, unfussy, assumes the reader
knows their job.

- Address: `Anh/Chị`, or the role — `thầy cô`, `chủ shop`, `bác sĩ`
- Self: `bên mình`, the product name, or no subject at all
- `Vui lòng`, `hệ thống`, `chúng tôi` are all banned — they import an
  institution the product does not have
- Softeners **only** where the sentence costs the reader something: a failure,
  a wait, a request, a refusal

The failure mode is the one this whole skill was written for: correct,
translated, and lifeless.

### `casual`

Games, social, creator tools, Gen-Z retail, food delivery.

**Speech, not writing.**

- Address: `bạn`, `mình`, `các bạn`, or the in-game role
- Self: `mình`, `shop`, the product's name
- Particles are plentiful and correct: `nhé`, `nha`, `nhen`, `luôn`, `á`
- Slang is fine — and dates fast, so keep it out of strings you cannot change
  quickly

The failure mode is the opposite of the usual one: corporate politeness nobody
asked for. `Kính gửi Quý khách` in a game reads as a parody.

---

## Picking one

Ask what the reader loses if the product gets it wrong.

| The reader is… | Register |
| --- | --- |
| trusting you with money, health, or a legal status | `formal` |
| doing their job with your tool | `warm` |
| enjoying themselves | `casual` |

When two surfaces of one product differ — a game's age-rating and payment
screens, a bank's marketing site — **split them.** Run the guard twice with two
profiles rather than averaging into a voice that fits neither.

Averaging is how products end up sounding like a bank trying to be fun.

---

## What this means mechanically

`rules/rules.json` tags every rule with the registers it applies to.
`rules/profiles/*.json` picks a register per industry and adjusts from there:

```jsonc
{
  "register": "formal",
  "disable": ["he-thong", "vui-long"],   // correct in this industry
  "glossary": [ /* terms that are not yours to improve */ ],
  "extraRules": [ /* what this industry gets wrong specifically */ ]
}
```

Start from the closest profile, copy it, and narrow it. `consumer-saas` is the
neutral starting point if nothing fits.

The register is not a style preference to revisit per string. Set it once,
record it in `VOICE.md`, and let it decide.

---

## Regional variety

Vietnamese has real regional differences, and they are not errors:

| North | South |
| --- | --- |
| `bố`, `mẹ` | `ba`, `má` |
| `vâng` | `dạ` |
| `bát` | `chén` |
| `cốc` | `ly` |
| `ô tô` | `xe hơi` |

Pick one to match your users — Hà Nội-centred products lean northern, HCMC-
centred lean southern — and stay consistent. Southern reads warmer and is the
more common choice for consumer products nationally.

**This is deliberately not automated.** The pairs overlap with unrelated common
words (`ba` is also "three"), so a regex check would cry wolf constantly. Record
the choice in `VOICE.md` and let a reviewer hold it.

Diaspora Vietnamese (US, Australia) differs again — more English loanwords,
some vocabulary that reads dated in Vietnam. If that is your audience, say so in
`VOICE.md`; do not let a reviewer in Hà Nội "correct" it.
