# Critic checklist (independent second pass — score 0–10, publish only if passed)

Read the episode as a strict reviewer who did NOT write it. Re-read config/rules.md first.
Any HARD item failing → `passed: false` regardless of score.

## HARD (any failure = reject)
1. Every factual claim and number is correct and backed by `sources` (re-verify with a web search when unsure).
2. Safe for kids: nothing scary, violent, adult, political or medical-advice; no brand logos; no stereotypes.
3. Persian: natural, grammatical modern Persian, correct spelling and نیم‌فاصله; no English sentence in narration.
4. Pronunciation: read every `say` line word by word as the voice would. Every word with two possible readings carries the
   diacritics of the meant reading; ezafe kasra where the voice could miss it; names via config/lexicon_fa.json;
   `pronunciation_checked` lists the marked homographs. One missed homograph = fail.
5. `say` = `text` + diacritics only (same words); `text` has no diacritics.
6. Every `stock` beat has a `clip` whose `checked` note confirms it shows what the sentence says. No `short_clip` at all.
   ≥ 50% of beats image/collage, ≥ 33% collage, text cards ≤ 15%.
7. Length within limits (config/channel.json); structure hook → story → fact → summary → cta.
8. No repeated title/hook (data/history.json, archive/).
9. Tone: read it aloud — it must sound like a friendly YouTuber talking (محاوره‌ی خودمونی), not a book. Any bookish sentence
   (می‌باشد، گردید، نمودن، لذا، …) = fail.
10. Hooks: open loop in the first 10 s that is paid off later; a `rehook` beat at least every ~200 words.

## SOFT (affect score)
- Hook strength in the first 10 s; the story feels like a real adventure (goal, obstacle, surprise, payoff) with کوروش، میا و ایمان.
- Visual variety: a change every 3–6 s; collages that really tell the moment.
- Title curiosity without clickbait; clear takeaway a kid can retell.

## Output
Set `critic = {"passed": bool, "score": n, "notes": [...]}`. Score < 7.5 → rewrite the weak parts and review again (max 2 rounds);
still failing → do NOT queue the episode; report it.
