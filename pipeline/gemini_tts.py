"""Gemini TTS (Persian) + Gemini pronunciation check.

speak(text, wav_path, voice=None) -> seconds        (24 kHz mono PCM from the API, written as WAV)
check(wav_path, expected_text)    -> {"ok": bool, "issues": [{"word", "heard", "note"}]}
Key: env GEMINI_API_KEY (or .env).
"""
import base64, json, os, pathlib, sys, time
import numpy as np, requests, soundfile as sf

API = 'https://generativelanguage.googleapis.com/v1beta/models'


def _key():
    k = os.environ.get('GEMINI_API_KEY')
    if not k:
        f = pathlib.Path(__file__).resolve().parent.parent / '.env'
        if f.exists():
            for line in f.read_text(encoding='utf8').splitlines():
                if line.strip().startswith('GEMINI_API_KEY='):
                    k = line.split('=', 1)[1].strip().strip('"').strip("'")
    if not k:
        raise RuntimeError('GEMINI_API_KEY is not set')
    return k


def _cfg():
    from .common import CFG
    return CFG['voice'].get('gemini', {})


def _post(model, body, tries=4):
    for i in range(tries):
        r = requests.post(f'{API}/{model}:generateContent', headers={'x-goog-api-key': _key()}, json=body, timeout=300)
        if r.status_code in (429, 500, 503) and i < tries - 1:
            wait = 20 * (i + 1); print(f'gemini {r.status_code}, retry in {wait}s', file=sys.stderr); time.sleep(wait); continue
        if r.status_code >= 400:
            raise RuntimeError(f'Gemini {model} {r.status_code}: {r.text[:400]}')
        return r.json()


def speak(text, wav, voice=None, model=None, style=None):
    g = _cfg()
    model = model or g.get('model', 'gemini-3.8-flash-tts')
    voice = voice or g.get('voice', 'Charon')
    style = style if style is not None else g.get('style', '')
    prompt = f'{style}\n\n{text}' if style else text
    body = {'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'responseModalities': ['AUDIO'],
                                 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}}}
    j = _post(model, body)
    part = j['candidates'][0]['content']['parts'][0]['inlineData']
    pcm = np.frombuffer(base64.b64decode(part['data']), dtype='<i2')
    rate = int(part.get('mimeType', 'rate=24000').split('rate=')[-1].split(';')[0]) if 'rate=' in part.get('mimeType', '') else 24000
    sf.write(str(wav), pcm, rate, subtype='PCM_16')
    return len(pcm) / rate


CHECK_PROMPT = """You are a strict native Persian (Farsi) speech reviewer. Listen to the audio and compare it with the script below.
The script may carry diacritics (اعراب) that show the intended reading of ambiguous words.
List every word the speaker pronounced wrongly: wrong vowel (e.g. kerm vs karam), a homograph read with the wrong meaning,
a missing or wrong ezafe, a skipped/added word, or a clearly non-standard (non-Tehrani) reading. Ignore small differences in
speed, emotion or pauses. Answer only JSON: {"ok": true|false, "issues": [{"word": "<script word>", "heard": "<what you heard, in Persian letters with diacritics>", "note": "<short reason>"}]}

Script:
"""


def check(wav, expected, model=None):
    model = model or _cfg().get('check_model', 'gemini-3.8-flash')
    data = base64.b64encode(pathlib.Path(wav).read_bytes()).decode()
    body = {'contents': [{'parts': [{'inlineData': {'mimeType': 'audio/wav', 'data': data}}, {'text': CHECK_PROMPT + expected}]}],
            'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0}}
    j = _post(model, body)
    txt = j['candidates'][0]['content']['parts'][0]['text']
    return json.loads(txt)
