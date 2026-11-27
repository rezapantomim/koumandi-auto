# koumandi-auto

Automation for the KOUMANDI YouTube channel (@koumandiapp). Free: GitHub Actions + edge-tts + Pixabay/Pexels + YouTube Data API.

- **Shorts** — the owner posts a video to the Koumandi Telegram channel (caption: first line = title, rest = description,
  #hashtags; optional cover = a photo in the same album). GitHub Actions (twice a day) republishes it as a YouTube Short.
  `#نه_یوتیوب` in the caption skips a post.
- **Long videos** — every other day. On the owner's PC, Task Scheduler runs Claude Code with the `koumandi-writer` skill
  (Sun + Wed): it picks topics from the published Shorts, writes Persian scripts with diacritics for correct pronunciation,
  picks visuals and queues them in `queue/`. GitHub Actions renders (Remotion, Persian voice fa-IR-FaridNeural, Vazirmatn font,
  right-to-left) and uploads at `publish_at`.

Key files: `config/channel.json` (schedule, voice, style), `config/rules.md`, `config/lexicon_fa.json` (fixed pronunciations),
`pipeline/shorts.py` (Telegram → Shorts), `pipeline/run.py` (daily publisher), `.claude/skills/koumandi-writer/`.

Voice test: `python tools/voice_sample.py "متن"` → `work/voice-samples/`.
Manual run on GitHub: Actions → Publish → Run workflow (dry run by default; uncheck to upload).
