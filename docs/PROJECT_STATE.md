# Project state — 2026-11-27

## Done
- Project created from rezfitlab-auto (same mix: writer on the owner's PC via Claude Code + Task Scheduler, render/upload on
  GitHub Actions). Not committed / no GitHub repo yet.
- Channel: KOUMANDI, @koumandiapp (app = educational adventure game, characters کوروش، میا، ایمان). Instagram link set.
- Shorts: `pipeline/shorts.py` — Telegram channel posts (bot admin) → inbox → YouTube Shorts (caption → title/desc/hashtags,
  optional cover photo in the same album). Caption parsing tested.
- Long: Persian rules/critic/skill (`koumandi-writer`), schema (layers hook/story/fact/game/summary/cta, `short_clip` visual,
  `pronunciation_checked`), validator (diacritics only in `say`, same words as `text`), planner (every 2 days from 2026-11-28, 19:00 Tehran).
- Voice: edge-tts rejected by the owner; ElevenLabs code kept (engine "elevenlabs") but no budget. Active: Gemini TTS
  (`pipeline/gemini_tts.py`, gemini-3.8-flash-tts, voice Puck, free AI Studio key in .env / secret GEMINI_API_KEY).
  Gemini misreads homographs without diacritics; with diacritics OK. Every episode is listened back by gemini-3.5-flash
  (blocks of 12 beats), wrong beats re-voiced twice, then the episode fails. Test video OK. Free-tier 429s seen (retry works);
  daily request cap for ~80 beats/video unknown until the first real long video.
- Renderer: Vazirmatn, RTL, Persian labels, new RTL thumbnail. Local test render OK (tests/L-20261128-test-silkworm.json).

## Decisions
- Shorts source = Telegram (Instagram needs Business account + Meta app). Long = narrated educational, topics from Shorts.
- made_for_kids = false (general audience), owner decision 2026-11-27.

## Live (2026-11-27)
- Google Cloud project `koumandi-youtube` (separate from the app's own `koumandi` project, which holds the app's Supabase
  Google sign-in - do not touch its OAuth): YouTube Data API v3, OAuth app "KOUMANDI Uploader" In production, Desktop client
  `koumandi-uploader`; home/privacy on GitHub Pages (main /docs). Token verified for @koumandiapp.
- Repo github.com/rezapantomim/koumandi-auto (public). Secrets: TELEGRAM_BOT_TOKEN, TELEGRAM_SOURCE_CHAT (-1004409679328, private
  inbox channel KOUMANDI.APP, bot @KOUMANDIBOT admin), GEMINI_API_KEY, PIXABAY_API_KEY, YT_TOKEN_JSON. TELEGRAM_CHAT_ID not set
  (owner never pressed Start) -> no Telegram reports yet.
- First Shorts published by Actions: TG-144 youtu.be/rb_qw_wn4wQ, TG-115 youtu.be/dznWn9pqHjg (public, covers set).
- Inbox: owner posts cover + caption + video in any order; 10 videos > 20 MB marked too_big (owner re-sends compressed).

## Next
- Long videos: queue empty. Register the writer (`scripts/install-schedule.ps1`) and do a first writer run; first slot 2026-11-28 19:00 Tehran.
- Verify the first scheduled (cron) run of Publish.

## Open issues
- Custom thumbnails need a phone-verified channel; for Shorts the API thumbnail does not show in the Shorts feed.
- Telegram Bot API downloads only files ≤ 20 MB.
- tools/stock_search.py, image_search.py and Diagrams.tsx still carry rezfitlab defaults (Turkish diagram labels) — diagrams
  are not in the KOUMANDI visual list; stock/image tools are language-neutral.
