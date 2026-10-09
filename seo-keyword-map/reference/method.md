# Grouping method: which keywords share a page

## Contents
- [The test](#the-test)
- [Why page type comes before URL overlap](#why-page-type-comes-before-url-overlap)
- [Rules](#rules)
- [Choosing the Primary](#choosing-the-primary)
- [Page types](#page-types)
- [Worked examples](#worked-examples)
- [Lessons](#lessons)

## The test

Two keywords belong on the same page when Google answers them with the same kind of
page for the same need. They need separate pages when Google answers them differently.
A separate page is worth building when it can rank for something the existing page
can't, and its keywords reach the volume floor (`min_volume`, default 20/mo).

Evidence, in order of weight:
1. **SERP type**: what kind of page ranks (from `serp.py classify`):
   - `SERVICE` / `SERVICE+local`: firms' service pages and homepages; `+local` means a map pack
   - `ARTICLE`: explainers, guides, cost articles, forums
   - `DIRECTORY/ORG`: directories, associations, government, job boards, dictionaries
   - `MIXED`: no kind reaches half
2. **Overlap**: non-homepage URLs shared by the two keywords' pooled top 10s
   (two passes). 6 or more means Google treats them as one query. Under 3 is no
   evidence either way.
3. **The need**: what the searcher wants to do next (hire, compare, learn, find a form).

## Why page type comes before URL overlap

Measured on a 194-keyword local-services map (20–300 searches/mo each):
- **SERPs rotate.** Two pulls an hour apart kept a median 43% of the same top-10 URLs.
  Google draws on a large pool of similar pages for low-volume queries, so two close
  variants can share 0–2 URLs in one pull while both lists are wall-to-wall explainers
  of the same thing. One quick search makes two keywords look different when they aren't.
- **Local markets saturate.** The same 4–6 firms' homepages rank for every service in a
  city, so every service looks like every other. `group.py` leaves homepages out of
  the overlap for that reason.
- **The kind of page is stable.** Across both pulls, explainer queries stayed explainer
  queries and hire-a-firm queries stayed hire-a-firm queries.

Shared-URL clustering tools (and a single manual Google search) therefore over-split low-volume
keywords. Use overlap to confirm, and to find merges, not as the deciding test.

## Rules

1. **Close variants stay together** whatever the overlap: plural/singular, word order,
   hyphenation, "surveyor"/"surveyors", "company"/"companies".
2. **Different SERP type → different page.** A `SERVICE` keyword belongs on a service,
   location or hub page. An `ARTICLE` keyword belongs in a post. A service page holding
   explainer keywords won't rank for them; neither will a post for hire-a-firm keywords.
3. **Same type and overlap ≥ 6 → same page**, even if the plan had them apart. This
   works in both directions: two planned posts whose SERPs draw on the same pages become
   one post.
4. **Directory/association-led keywords are never a Primary**, and no page is built for
   them. They stay as Support on the nearest page, or are excluded when nothing the site
   could publish would rank (a professional association's name, a job board query).
5. **Place pages need volume and something local to say.** A place gets its own page
   when its keywords reach the floor and the page can carry facts true only there
   (municipal rules, permits, local process). Otherwise the place keyword goes on the
   main service page as Support. Never stamp out near-identical city pages: Google treats
   them as doorway pages.
6. **One page per service per place**, even when two of its keywords share little
   overlap ("plumbers [city]" and "plumbing services [city]"). Two pages for the same
   service in the same city compete with each other.
7. **Unqualified keywords that Google answers locally** ("surveying companies", "plumbers")
   go to the page for the business's home city, not a new generic page.
8. **Don't move a keyword the site already ranks top 10 for** (`our rank` in the group
   report) unless the new page is clearly the better answer; say so in the note.
9. **A merge candidate is a question, not an instruction.** Keep pages apart when they
   are different page types on purpose (a city page and an explainer can share results)
   or the client decided it.
10. **Every moved keyword gets a note** in `Action`: `SERP <date>: <type>; shares N with
    '<keyword>'` plus the reason in a few words. The next person must be able to see why.
11. **Mixed SERPs** stay where they are unless a top-3 result shows which page type wins;
    then follow the top 3.

## Choosing the Primary

The Primary leads the page's title tag and H1, so it must:
- have a SERP type that fits the page type (rule 2), and
- not be directory-led (rule 4), and
- be the highest-volume keyword that passes both, unless a slightly smaller one matches
  the URL and reads naturally as a title. In that case, say why in the note.

Exactly one Primary per page; `apply.py` refuses anything else. Secondary: the next
keyword the title or H1 should carry. Support: worked into headings and copy.

## Page types

| Type | Is | Typical SERP | Examples |
|---|---|---|---|
| `hub` | The service-line overview that links down to every service | SERVICE+local | /plumbing/ |
| `service` | One service, area-wide | SERVICE | /drain-cleaning/ |
| `location` | One service (or the whole line) in one place | SERVICE+local | /drain-cleaning-calgary/ |
| `post` | Answers a question: what is, how to, cost, vs | ARTICLE | /how-much-does-drain-cleaning-cost/ |

Priority for pages to build comes from `priority_rules` in the config (first match by
service line and page type). Existing pages keep their priority.

## Worked examples

From a local land-surveying firm's map (names and figures generalised):
- **"as built drawings" (one of the biggest terms in the set) sat on the as-built
  survey service page.** Its SERP: explainers and CAD drafting firms, sharing nothing
  with "as built survey". → moved to a new post *What are as-built drawings*. The
  service page's Primary became "as built survey".
- **"topographic survey" was the topographic service page's Primary.** Its SERP: "what
  is a topographic survey" articles, sharing nothing with "topographic survey services".
  → new post; the service page took the service-led term.
- **Two planned posts, "what is a [property certificate]" and "how to get one", plus
  its cost and compliance queries.** All shared 5–10 results: one topic to Google. →
  merged into one guide post.
- **"[province] land surveyors" was the hub's Primary.** SERP: the professional
  association, career profiles and directories. → demoted to Secondary; the hub took
  "land surveying services [province]".
- **"surveying companies" sat on the hub.** Google answered it with the map pack and
  home-city firms. → moved to the home-city page.
- **"final grading [city]"** was found by research, in no export. SERP: the city's
  grade-approval pages, a surveyor's lot-grading page and landscapers. The firm sells
  grade certificates, so → a new location page.

## Lessons

Add dated entries here when a project teaches something the rules above don't cover.

- 2026-10: First version, from a 194-keyword local-services rework on Canadian city
  SERPs.
- 2026-10: A primary picked by volume can be a phrase nobody titles a page with
  ("survey boundary lines": 0 of 12 page-one titles). A brief that demands it in the H1
  gets ignored by a writer told to write naturally, and the keyword then lands nowhere.
  Check ranking titles before demanding the exact phrase.
