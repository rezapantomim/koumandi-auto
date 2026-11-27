---
name: koumandi-writer
description: Write the next KOUMANDI long YouTube videos (Persian, one every other day) end to end — pick topics from the published Shorts, research, script with correct Persian pronunciation (diacritics in `say`), storyboard with checked visuals and our own Short clips, critic pass, validate, queue and push to GitHub. Use when the scheduled writer run starts, or when the user asks to write/plan/queue KOUMANDI long videos.
---

# KOUMANDI — long-video writer

You write the long videos for the next days and push them to `queue/`. GitHub Actions turns each queued file into a video
(Persian TTS, visuals, captions, thumbnail) and uploads it at its `publish_at`. Shorts are NOT your job: Actions republishes
the owner's Telegram videos by itself. Nobody reviews your output before it goes public: the critic pass and the validator are
the only gates. Skipping an episode is better than publishing a wrong one.

Run everything from the project root. Python tools live in `tools/` (run as `python tools/<name>.py`).

## 0. Read first (every run)
- `config/rules.md` (content, Persian and pronunciation rules), `config/critic.md`, `config/channel.json` (limits, schedule),
  `schema/episode.schema.json`, `config/lexicon_fa.json`.
- One file in `archive/` (if any) as an example, and `data/history.json` for what was already published.

## 1. Plan
`git pull --rebase` first (Actions writes history and moves files). Then `python tools/plan_week.py --write`.
It prints the empty long `slots` (with `publish_at`), `topics_todo`, and `shorts_not_yet_used` (title, caption, `tg_file_id`).
No slots → report "queue full" and stop.

### Topics
For every slot without a todo topic, add one to `data/topics.json`:
`{"id": "T<next>", "title": "<Persian working title>", "brief": "<the question the video answers + why kids care>",
"from_shorts": ["TG-…"], "status": "todo"}`.
Prefer topics that grow out of `shorts_not_yet_used` (the most interesting question a Short raises). Without Shorts, use the
fallback themes in config/rules.md. Never repeat a title in data/topics.json or history.

## 2. For each long video
1. **Research.** Verify every fact with web search in reliable sources (encyclopaedias, NASA, National Geographic, museums,
   universities, Persian sources like دانشنامه‌ها). Note 2–5 sources with URLs.
2. **Script** (Persian, 650–950 words, 5–9 scenes, structure from config/rules.md). Each beat = one spoken idea (≈ 3–6 s):
   `text` (on screen, no diacritics) and `say` (same words + diacritics on every ambiguous word). Read each `say` aloud in your
   head the way a machine would; mark every homograph and the ezafe where needed. Fill `pronunciation_checked`.
   New names → add to `config/lexicon_fa.json`.
3. **Storyboard.** A `visual` for every beat:
   - Our own Shorts: `{"type": "short_clip", "short": {"id": "TG-…", "tg_file_id": "…", "start": s, "end": e}}` — only Shorts
     listed in the plan; pick moments that match the sentence (you know them from the caption; keep them short, 3–8 s).
   - Stock video: `python tools/stock_search.py "<precise English query>" --orientation landscape`, **open the contact sheet
     and look at it**; pick only if it clearly shows what the sentence says; copy `provider`, `id`, `url`, `checked`.
   - Pictures: `python tools/image_search.py "<query>" --source pixabay --kind photo|illustration|vector` (or `--source wikimedia`),
     open the sheet, never a NO PREVIEW candidate; copy provider, id, url, license, credit, page, `checked`.
   - Text cards: `title`, `keyword`, `list`, `stat`, `compare`, `quote` (Persian).
   - A change every beat; never 3 identical non-video types in a row.
4. **Thumbnail:** `thumb_text` (2–4 Persian words, curiosity), `thumb_highlight` (one word of it).
5. **Upload package** per config/rules.md; `playlist`: `long`.
6. `id` = slot (`L-YYYYMMDD-<short-english-slug>`), `kind` = long, `topic_id`, `publish_at`, `sources`, `from_shorts`.

## 3. Critic (separate pass, per episode)
Re-read the finished JSON as a reviewer who did not write it, against `config/critic.md` — pronunciation line by line.
Fix and review again (max 2 rounds). Write `critic`. HARD failure or score < 7.5 → do not queue.

## 4. Validate, queue, push
- Save drafts to `work/episodes/<id>.json` (UTF-8). `python tools/validate.py work/episodes/*.json`; fix every FAIL.
- `python tools/enqueue.py work/episodes/*.json`.
- `git add queue data config/lexicon_fa.json && git commit -m "queue: <dates>" && git push` (on rejection: `git pull --rebase`, push again).
- Never commit `work/` or `.env`.

## 5. Report (Persian, short)
Each queued video (id, publish time Tehran, title, critic score), skipped ones and why, warnings. The scheduled runner sends it
to Telegram.
