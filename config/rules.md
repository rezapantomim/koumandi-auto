# KOUMANDI — content rules (long videos)

## Channel
- KOUMANDI (@koumandiapp): YouTube channel of the Koumandi app — an educational adventure game. Tagline:
  «یاد بگیر • کشف کن • رقابت کن». Characters: کوروش، میا، ایمان («با کوروش، میا و ایمان به دنیای دانش سفر کن»).
- Audience: general (NOT made for kids, owner decision 2026-11-27): curious kids, teens and families. Tone: warm, curious, energetic, simple sentences, never childish
  or preachy. Address the viewer as «تو».
- Shorts are the owner's own videos (Telegram channel → YouTube as they are). Long videos are written by us.

## Topics
- Each long video grows out of one or more published Shorts (their captions = what the game/channel talks about):
  take the most interesting question a Short raises and answer it in depth. Record them in `from_shorts`.
- When there are no (unused) Shorts yet: general-knowledge topics that fit a learning-adventure game — science
  wonders, animals, space, the human body, history and civilisations (incl. Iranian history), geography, inventions,
  "how does it work", riddles and logic.
- Evergreen, true, verifiable. No politics, religion debates, violence, scary or medical-advice content.

## Structure (5–9 minutes, 650–950 words, 5–9 scenes)
`hook` (a question or surprising fact, 10–20 s) → `story` scene(s) (the adventure: narrated as if کوروش، میا و ایمان discover
it — narration only, the characters do not speak in their own voices) → `fact` scene(s) (the real knowledge, clear and
concrete) → optional `game` scene (a mini quiz/riddle for the viewer, answer after a pause) → `summary` (۳ نکته) → `cta`
(«اپ کومندی به‌زودی…» / subscribe / comment the answer). Every scene has a `layer`.

## Persian text and pronunciation (the owner is strict about this)
- Standard modern Persian (فارسی معیار), correct spelling, نیم‌فاصله (ZWNJ) in می‌، ها، ترین، ای etc.
- `text` = what appears on screen: no diacritics.
- `say` = the same words with diacritics added wherever a word could be read two ways (کِرم/کَرَم، عِلم/عَلَم، مُهر/مِهر،
  کُشتی/کِشتی، گُل/گِل، سِحر/سَحَر، مَلِک/مُلک، شِکَر/شُکر، قُطر/قَطَر، پُر/پَر، کُرد/کَرد، بُرد/بَرد …), on rare words, foreign
  names and numbers written as words when the reading is ambiguous. Ezafe: write the kasra (ـِ) where the voice could
  miss it (کرمِ ابریشم). Same words as `text` — only marks added (the validator checks).
- Add every homograph you marked to `pronunciation_checked` (e.g. "کِرم = worm").
- Names and fixed words: config/lexicon_fa.json (add new names there, e.g. a new game character).
- Numbers: write them as Persian words in `say` when the reading matters (۱۴۰۳ → هزار و چهارصد و سه).

## Visuals
- Every beat changes the picture. Mix: our own Shorts (`short_clip`, a 3–8 s piece of a Short from `from_shorts`, with
  `tg_file_id` from the plan), stock video (`stock`, Pexels/Pixabay, checked by looking at the contact sheet), pictures
  (`image` / `collage`, Pixabay / Wikimedia, licence rules as in the validator), and text cards (`title`, `keyword`, `list`,
  `stat`, `compare`, `quote`). On-screen text in Persian.
- Never show scary, violent or adult material; no brand logos, no real children's faces as the main subject.

## Upload
- Title ≤ 70 characters, Persian, curiosity + clarity, no clickbait lies. Description: 2–3 lines + `{CHAPTERS}` + sources,
  3–5 hashtags (always #کومندی). 12–20 tags (Persian + a few English). `thumb_text` 2–4 Persian words.
- `pinned_comment`: a question for the viewer (e.g. the answer to the riddle).
