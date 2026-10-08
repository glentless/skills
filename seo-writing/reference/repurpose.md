# Repurposing a post

`repurpose <file> [channels]` turns one post into native content for other
channels. If no channels are named, ask which ones. Offer the ones BLOG.md lists
first.

## Rules for every channel

- **Rebuild, don't excerpt.** Each channel gets its own hook and structure.
  Pasting the intro under a link is not repurposing.
- **Reuse only claims that are sourced in the post,** with their attribution. If
  a format wants a number and none fits, use a qualitative point. Never round a
  number up into something new.
- **Lead with the single most useful or surprising point.** Native platforms
  reward value that's complete without a click.
- **Follow each community's rules.** Check a subreddit's or group's
  self-promotion policy, disclose affiliation, and never post on the user's
  behalf without their go-ahead.
- **Same voice as BLOG.md,** adjusted to the platform's register.

## Channels

| Channel | Shape |
|---|---|
| X / Threads / Bluesky | Hook post (a claim, number or contrarian line under 280 chars), 4 to 8 posts each carrying one idea that stands alone, a closing post with the link. At most 2 hashtags, and only where the platform uses them |
| LinkedIn post | Up to about 3,000 chars. The first two lines must earn the "see more" click. Short paragraphs, a first-person angle (what the author saw or learned), one question at the end. The link either in the post or in the first comment: test both |
| LinkedIn article or newsletter | 600 to 1,200 words, rewritten around one insight, linking to the full post |
| Reddit | A title framed as a finding or question, never "my new post". The value is in the post body. Disclose affiliation. The link goes at the end, only where the rules allow. Suggest 2 or 3 subreddits and check their rules |
| Email newsletter | Subject line (40 to 60 chars) plus preview text (40 to 90) that complements it. 120 to 200 words: the takeaway, 2 or 3 bullets, one CTA button |
| Short video (Shorts, Reels, TikTok) | 30 to 90 seconds: a hook in the first 2 seconds, 3 beats, a payoff, then the CTA. Mark on-screen text, captions and B-roll |
| YouTube (long) | Hook (0 to 15 s), what they'll learn, 3 to 5 segments built from the H2s, each with a visual cue (`[SCREEN: …]`, `[CHART: …]`). CTA and description with chapters. About 150 spoken words per minute |
| Podcast or audio script | 5 to 12 minutes, solo or host-and-guest, with spoken transitions in place of headings and no URLs read aloud. For two voices, label each line `Host:` or `Guest:` |
| Slack / Discord community | A short discussion prompt with the key finding and the link. No hard sell |

## Output

Save each piece as `repurposed/<slug>-<channel>.md`. Ask before overwriting an
existing file. Then give a summary: each file, with its length and the angle
it takes. Recommend posting times only from the user's own analytics. Without
analytics, say that timing is a guess to test.
