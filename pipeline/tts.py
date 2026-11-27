"""Narration: Edge TTS (free, fa-IR-FaridNeural) with word timings; Piper (free, offline) as fallback.

Persian pronunciation: config/lexicon_fa.json fixes names and loanwords on whole words; homographs are diacritized by the
writer in each beat's `say` field. Diacritics are stripped again for the on-screen captions.

voice(ep, out_dir) -> (wav_path, timeline) where timeline = list of beats with start/end seconds and word timings.
Quiz Shorts: a silent countdown (quiz.countdown_s) is inserted after the first beat (the question).
"""
import asyncio, json, os, pathlib, re, subprocess, sys, urllib.request
import numpy as np, soundfile as sf
from .common import CFG, ROOT, sh, load

HARAKAT = re.compile('[ً-ْٰ]')         # fatha, kasra, damma, tanwin, sukun, shadda, superscript alef
_LEX = None


def strip_marks(s):
    return HARAKAT.sub('', s)


def lexicon():
    global _LEX
    if _LEX is None:
        _LEX = (load(CFG['voice'].get('lexicon', 'config/lexicon_fa.json'), {}) or {}).get('words', {})
    return _LEX


def spoken(text):
    """Apply the fixed-pronunciation lexicon on whole words (Persian letters, ZWNJ and diacritics count as word letters)."""
    for w, say in sorted(lexicon().items(), key=lambda x: -len(x[0])):
        text = re.sub(r'(?<![\w‌ً-ْ])' + re.escape(w) + r'(?![\w‌ً-ْ])', say, text)
    return text


SR = 48000
GAP_BEAT, GAP_SCENE = 0.22, 0.55


async def _edge_async(text, voice, rate, mp3):
    import edge_tts
    try:
        com = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    except TypeError:                                   # older edge-tts: word boundaries are the default
        com = edge_tts.Communicate(text, voice, rate=rate)
    words = []
    with open(mp3, 'wb') as f:
        async for ch in com.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append({'w': ch['text'], 't0': ch['offset'] / 1e7, 't1': (ch['offset'] + ch['duration']) / 1e7})
    return words


def _edge(text, mp3, voice, rate):
    for attempt in range(4):
        try:
            return asyncio.run(_edge_async(text, voice, rate, mp3))
        except Exception as e:
            print('edge-tts retry', attempt, e, file=sys.stderr)
    raise RuntimeError('edge-tts failed 4 times')


def _piper(text, wav):
    fb = CFG['voice']['fallback']; name = fb['model']
    d = ROOT / 'work/piper'; d.mkdir(parents=True, exist_ok=True)
    lang, voice, q = name.split('-')                      # tr_TR, fahrettin, medium
    base = f'https://huggingface.co/rhasspy/piper-voices/resolve/main/{lang.split("_")[0]}/{lang}/{voice}/{q}/{name}.onnx'
    for suf in ('', '.json'):
        f = d / f'{name}.onnx{suf}'
        if not f.exists():
            urllib.request.urlretrieve(base + suf, f)
    subprocess.run([sys.executable, '-m', 'piper', '-m', str(d / f'{name}.onnx'), '-f', str(wav)], input=text.encode('utf8'), check=True)


def _load(path):
    """Decode any audio file to mono float32 at SR via ffmpeg."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.float32).copy()
    nz = np.where(np.abs(a) > 0.01)[0]                    # trim leading/trailing silence, keep 40 ms
    if len(nz):
        a = a[max(0, nz[0] - int(0.04 * SR)): nz[-1] + int(0.08 * SR)]
    return a, (nz[0] - int(0.04 * SR)) / SR if len(nz) else 0.0


def _even_words(text, dur):
    ws = text.split(); total = sum(len(w) for w in ws) or 1; t = 0.0; out = []
    for w in ws:
        d = dur * len(w) / total; out.append({'w': w, 't0': t, 't1': t + d}); t += d
    return out


EL_API = 'https://api.elevenlabs.io/v1'


def _el_key():
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key:
        raise RuntimeError('ELEVENLABS_API_KEY is not set')
    return key


def el_remaining():
    """Characters left in the ElevenLabs plan this month."""
    import requests
    r = requests.get(f'{EL_API}/user/subscription', headers={'xi-api-key': _el_key()}, timeout=30)
    r.raise_for_status(); s = r.json()
    return s['character_limit'] - s['character_count']


def el_budget_check(ep):
    """Refuse (before spending anything) when the plan cannot cover this episode plus the reserve - never run into overage."""
    el = CFG['voice']['elevenlabs']
    if not el.get('voice_id'):
        raise RuntimeError('config/channel.json voice.elevenlabs.voice_id is not set (owner picks the voice)')
    need = sum(len(spoken(b.get('say') or b['text'])) for s in ep['scenes'] for b in s['beats'])
    left = el_remaining()
    if left - need < el.get('reserve_chars', 0):
        raise RuntimeError(f'ElevenLabs: {need} characters needed, {left} left this month (reserve {el.get("reserve_chars", 0)}) -> not voiced')
    return need, left


def _eleven(text, mp3):
    """ElevenLabs TTS with character timings -> word timings (words split on spaces)."""
    import base64, requests
    el = CFG['voice']['elevenlabs']
    body = {'text': text, 'model_id': el['model'], 'language_code': CFG['channel']['language']}
    if el.get('settings'):
        body['voice_settings'] = el['settings']
    for attempt in range(3):
        r = requests.post(f'{EL_API}/text-to-speech/{el["voice_id"]}/with-timestamps', params={'output_format': 'mp3_44100_128'},
                          headers={'xi-api-key': _el_key()}, json=body, timeout=180)
        if r.status_code < 500 and r.status_code != 429:
            break
        print('elevenlabs retry', attempt, r.status_code, file=sys.stderr)
    if r.status_code >= 400:
        raise RuntimeError(f'ElevenLabs {r.status_code}: {r.text[:300]}')
    j = r.json()
    pathlib.Path(mp3).write_bytes(base64.b64decode(j['audio_base64']))
    al = j.get('normalized_alignment') or j.get('alignment') or {}
    words, cur, t0, t1 = [], '', None, None
    for ch, a, b in zip(al.get('characters', []), al.get('character_start_times_seconds', []), al.get('character_end_times_seconds', [])):
        if ch.isspace():
            if cur:
                words.append({'w': cur, 't0': t0, 't1': t1}); cur = ''
            continue
        if not cur:
            t0 = a
        cur += ch; t1 = b
    if cur:
        words.append({'w': cur, 't0': t0, 't1': t1})
    return words


def _chunks(says, max_words):
    """Consecutive beat groups of at most max_words words (one Gemini request each)."""
    out, cur, n = [], [], 0
    for i, s in enumerate(says):
        w = len(s.split())
        if cur and n + w > max_words:
            out.append(cur); cur, n = [], 0
        cur.append(i); n += w
    return out + ([cur] if cur else [])


def _trim(a):
    nz = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, nz[0] - int(0.04 * SR)): nz[-1] + int(0.08 * SR)] if len(nz) else a


def split_at_pauses(audio, texts):
    """Cut one chunk of speech into len(texts) beats: expected cut = character share of each beat, snapped to the best
    nearby pause (long pauses preferred). Returns a list of trimmed arrays."""
    n = len(texts)
    if n == 1:
        return [_trim(audio)]
    hop = int(0.02 * SR)
    rms = np.sqrt(np.convolve(audio ** 2, np.ones(hop) / hop, mode='same'))[::hop]
    thr = max(0.012, np.percentile(rms, 20) * 2.5)
    quiet = rms < thr
    pauses, start = [], None                              # (mid seconds, length seconds)
    for k, q in enumerate(np.append(quiet, False)):
        if q and start is None:
            start = k
        elif not q and start is not None:
            ln = (k - start) * 0.02
            if ln >= 0.12:
                pauses.append(((start + k) / 2 * 0.02, ln))
            start = None
    total = len(audio) / SR
    w = np.array([max(1, len(t.replace(' ', ''))) for t in texts], dtype=float)
    exp = w / w.sum() * total                             # expected beat lengths (character share)
    P = [(m, ln) for m, ln in pauses if 0.3 < m < total - 0.3]
    m = len(P)
    if m < n - 1:                                         # not enough pauses: plain proportional cuts
        cuts = list(np.cumsum(exp)[:-1])
    else:
        # global choice of n-1 pauses: minimise sum of squared relative length errors, longer pauses preferred
        pos = [0.0] + [p[0] for p in P]; INF = 1e18
        cost = lambda k, a, b: ((b - a - exp[k]) / exp[k]) ** 2
        D = np.full((n, m + 1), INF); B = np.zeros((n, m + 1), dtype=int)
        for j in range(1, m + 1):                         # first cut at pause j
            D[0][j] = cost(0, 0.0, pos[j]) - 0.3 * P[j - 1][1]
        for k in range(1, n - 1):
            for j in range(k + 1, m + 1):
                best, arg = INF, 0
                for i in range(k, j):
                    if D[k - 1][i] < INF:
                        v = D[k - 1][i] + cost(k, pos[i], pos[j])
                        if v < best:
                            best, arg = v, i
                D[k][j] = best - 0.3 * P[j - 1][1]; B[k][j] = arg
        last = min(range(n - 1, m + 1), key=lambda j: D[n - 2][j] + cost(n - 1, pos[j], total))
        idx = [last]
        for k in range(n - 2, 0, -1):
            idx.append(B[k][idx[-1]])
        cuts = [pos[j] for j in reversed(idx)]
    bounds = [0.0] + list(cuts) + [total]
    return [_trim(audio[int(bounds[k] * SR): int(bounds[k + 1] * SR)]) for k in range(n)]


def _gemini_all(says, seg, out_dir):
    """Voice the episode in a few large Gemini requests (free tier: ~10 requests/day per model), let Gemini listen back to
    each chunk, re-voice a chunk with a mispronounced word (max `retries`), still wrong -> the episode fails. Returns the
    per-beat audio arrays (cut at pauses)."""
    from . import gemini_tts as g
    gc = CFG['voice']['gemini']
    arrays = [None] * len(says); report = []
    for c, idx in enumerate(_chunks(says, int(gc.get('chunk_words', 260)))):
        text = '\n'.join(says[i] for i in idx)
        wav = seg / f'chunk_{c:02d}.wav'
        for rnd in range(int(gc.get('retries', 1)) + 1):
            if rnd or not wav.exists():
                g.speak(text, wav)
            res = None
            for m in [gc.get('check_model')] + gc.get('check_fallback_models', []):
                try:
                    res = g.check(wav, text, model=m); break
                except Exception as e:
                    print('check model failed', m, str(e)[:150], file=sys.stderr)
            if res is None:
                raise RuntimeError('pronunciation check unavailable (all check models failed)')
            issues = res.get('issues') or []
            print(f'chunk {c} round {rnd}: {len(idx)} beats, issues {issues}', file=sys.stderr)
            if not issues:
                break
            if rnd == int(gc.get('retries', 1)):
                report += issues
        audio, _ = _load(wav)
        for i, part in zip(idx, split_at_pauses(audio, [says[i] for i in idx])):
            arrays[i] = part
    if report:
        raise RuntimeError('pronunciation still wrong after retries: ' + json.dumps(report, ensure_ascii=False)[:600])
    return arrays


def voice(ep, out_dir):
    out_dir = pathlib.Path(out_dir); seg = out_dir / 'tts'; seg.mkdir(parents=True, exist_ok=True)
    vc = {**CFG['voice']['edge'], **(ep.get('voice') or {})}
    engine = os.environ.get('KOUMANDI_VOICE_ENGINE') or CFG['voice']['engine']   # local previews: KOUMANDI_VOICE_ENGINE=edge
    if engine == 'elevenlabs':
        need, left = el_budget_check(ep); print(f'ElevenLabs: {need} chars for this episode, {left} left')
    chunks, timeline, t = [], [], 0.0
    beats = [(si, s, b) for si, s in enumerate(ep['scenes']) for b in s['beats']]
    if engine == 'gemini':
        gwav = _gemini_all([spoken(b.get('say') or b['text']) for _, _, b in beats], seg, out_dir)
    for i, (si, scene, b) in enumerate(beats):
        say = spoken(b.get('say') or b['text'])
        shown = strip_marks(b['text'])
        words = None
        if engine == 'gemini':                            # no word timings from Gemini -> captions split evenly per beat
            a, lead = gwav[i], 0.0
        if engine == 'elevenlabs':                       # no silent fallback to another voice: a failure stops this episode
            mp3 = seg / f'{i:03d}.mp3'
            words = _eleven(say, mp3)
            a, lead = _load(mp3)
        if engine == 'edge':
            try:
                mp3 = seg / f'{i:03d}.mp3'
                words = _edge(say, mp3, vc['voice'], vc['rate'])
                a, lead = _load(mp3)
            except Exception as e:
                print('edge failed, falling back to piper:', e, file=sys.stderr); engine = 'piper'
        if engine == 'piper':
            wav = seg / f'{i:03d}.wav'; _piper(say, wav); a, lead = _load(wav)
        dur = len(a) / SR
        if words and len(words) == len(shown.split()):     # same word count -> real timings, shown (undiacritized) words
            words = [{'w': sw, 't0': max(0, w['t0'] - lead), 't1': max(0, w['t1'] - lead)} for sw, w in zip(shown.split(), words)]
        else:
            words = _even_words(shown, dur)                # no timings or different split -> even split of the shown text
        timeline.append({'i': i, 'scene': si, 'start': t, 'end': t + dur, 'words': [{**w, 't0': w['t0'] + t, 't1': w['t1'] + t} for w in words]})
        chunks.append(a); t += dur
        nxt = beats[i + 1][0] if i + 1 < len(beats) else None
        gap = GAP_SCENE if nxt is not None and nxt != si else GAP_BEAT
        if i == 0 and ep.get('quiz'):
            gap = float(ep['quiz'].get('countdown_s', 4)) + 0.3
            timeline[-1]['countdown'] = [t + 0.15, t + gap - 0.15]
        if nxt is not None:
            chunks.append(np.zeros(int(gap * SR), dtype=np.float32)); t += gap
    tail = np.zeros(int(0.6 * SR), dtype=np.float32)
    audio = np.concatenate(chunks + [tail])
    peak = np.max(np.abs(audio)) or 1
    audio = audio / peak * 0.89
    wav = out_dir / 'voice.wav'; sf.write(wav, audio, SR, subtype='PCM_16')
    return wav, timeline, len(audio) / SR
