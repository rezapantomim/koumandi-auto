# KOUMANDI — content rules (long videos)

## Channel
- KOUMANDI (@koumandiapp): YouTube channel of the Koumandi app — an educational adventure game. Tagline:
  «یاد بگیر • کشف کن • رقابت کن». Characters: کوروش، میا، ایمان («با کوروش، میا و ایمان به دنیای دانش سفر کن»).
- Audience: general (NOT made for kids, owner decision 2026-11-27): curious kids, teens and families. Tone: warm, curious, energetic, simple sentences, never childish
  or preachy. Address the viewer as «تو».
- Shorts are the owner's own videos (Telegram channel → YouTube as they are). Long videos are written by us.

## Topics
- Each long video grows out of one or more published Shorts (their captions = what the channel talks about): take the most
  interesting question a Short raises and answer it in depth. Record them in `from_shorts` (topic only — the Short's video
  itself is never shown in the long video).
- When there are no (unused) Shorts yet: general-knowledge topics that fit a learning-adventure game — science
  wonders, animals, space, the human body, history and civilisations (incl. Iranian history), geography, inventions,
  "how does it work", riddles and logic.
- Evergreen, true, verifiable. No politics, religion debates, violence, scary or medical-advice content.

## Structure (5–9 minutes, 650–950 words, 5–9 scenes)
`hook` (a question or surprising fact, 10–20 s) → `story` scene(s) (the adventure: narrated as if کوروش، میا و ایمان discover
it — narration only, the characters do not speak in their own voices) → `fact` scene(s) (the real knowledge, clear and
concrete) → optional `game` scene (a mini quiz/riddle for the viewer, answer after a pause) → `summary` (۳ نکته) → `cta`
(«اپ کومندی به‌زودی…» / subscribe / comment the answer). Every scene has a `layer`.

## Voice and tone (owner, 2026-11-27: "too bookish, viewers get tired")
- Write like a friendly YouTuber talking to one viewer, NOT like a book. Spoken Tehrani Persian (محاوره‌ی خودمونی، مؤدب):
  «می‌دونستی…؟»، «حالا یه چیز عجیب‌تر»، «فکرشو بکن»، «بذار یه سؤال ازت بپرسم». Short sentences, everyday words, «تو» not «شما».
- Avoid literary/written forms: می‌باشد، گردید، نمودن، اینجانب، آن‌گاه، لذا، بسیار (→ خیلی)، نمی‌تابد (→ نمی‌تابه)…
- Use the same spoken spelling on screen and in narration (کتاب‌ها → کتابا only where natural; keep it readable).
- Funny, surprising, concrete comparisons a 12-year-old gets («قد یه اتوبوس»، «به اندازه‌ی ده تا زمین فوتبال»).

## Story and hooks (keep viewers watching)
- First 10 s: a strong question or a surprising claim, plus an OPEN LOOP the video only closes near the end
  («آخر ویدیو می‌گم کدوم ماهی برنده‌ی این مسابقه‌ست…»).
- A RE-HOOK at least every ~60–90 s (≈ every 150–200 words): a teaser, a twist, a mini-mystery, a question to the viewer
  («ولی صبر کن، عجیب‌ترش هنوز مونده…»، «حدس بزن بعدش چی شد؟»). Mark that beat with `"rehook": true`.
- The story is a real adventure with کوروش، میا و ایمان: a goal, an obstacle, a surprise, a payoff. Facts are discovered
  inside the story, not listed like a textbook.

## Pronunciation (the owner is strict about this)
- `text` = what appears on screen: no diacritics.
- `say` = the same words with diacritics on every SPECIAL word: homographs (کِرم/کَرَم، عِلم/عَلَم، مُهر/مِهر، کُشتی/کِشتی،
  گُل/گِل، سِحر/سَحَر، مَلِک/مُلک، شِکَر/شُکر، پُر/پَر، کُرد/کَرد…)، rare/scientific words, names, foreign words, numbers and
  every ezafe the voice could miss (کرمِ ابریشم). Do NOT diacritize ordinary words that cannot be misread (it makes the voice
  stiff). Same words as `text` — only marks added (the validator checks).
- Add every homograph/special word you marked to `pronunciation_checked`. Names and fixed words: config/lexicon_fa.json.
- Numbers as Persian words in `say` when the reading matters.

## Visuals (owner: many more collages, much less text on screen)
- Our own Shorts are NEVER used inside long videos (no `short_clip`).
- Pictures first: at least half of all beats are `image` or `collage`, and at least a third of all beats are `collage`
  (2–4 pictures that tell the moment together). Pixabay photos/illustrations/vectors + Wikimedia (licence rules in the
  validator), always chosen by looking at the contact sheet. Stock video (`stock`) for motion moments.
- Text cards (`title`, `keyword`, `list`, `stat`, `compare`, `quote`) at most 15% of beats — only for the title, a number
  that matters, the riddle and the summary.
- Every beat changes the picture. Never show scary, violent or adult material; no brand logos, no real children's faces as
  the main subject.

## Upload
- Title ≤ 70 characters, Persian, curiosity + clarity, no clickbait lies. Description: 2–3 lines + `{CHAPTERS}` + sources,
  3–5 hashtags (always #کومندی). 12–20 tags (Persian + a few English). `thumb_text` 2–4 Persian words.
- `pinned_comment`: a question for the viewer (e.g. the answer to the riddle).
