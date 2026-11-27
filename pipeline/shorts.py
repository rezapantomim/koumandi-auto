"""Shorts from the owner's Telegram channel -> YouTube Shorts (no editing of the video itself).

The bot (TELEGRAM_BOT_TOKEN) must be an admin of the channel (TELEGRAM_SOURCE_CHAT = @username or -100… id).
Telegram keeps channel posts for the bot for 24 h, so the workflow runs at least twice a day; everything seen is stored in
data/shorts_inbox.json (committed), so nothing is lost between runs.

A post = a video (+ caption). Optional cover: post a photo in the same album as the video, or reply to the video with a photo.
Caption format (all optional):
    first line            -> YouTube title
    rest                  -> description
    #hashtags             -> hashtags + tags
A caption line "#نه_یوتیوب" (or #no_youtube) skips that post.
"""
import datetime as dt, os, pathlib, re, requests
from .common import CFG, ROOT, load, save, sh, duration

INBOX = 'data/shorts_inbox.json'
STATE = 'data/telegram_state.json'
API = 'https://api.telegram.org'
MAX_BOT_DOWNLOAD = 20 * 1024 * 1024                  # Bot API getFile limit
SKIP_TAGS = {'#نه_یوتیوب', '#no_youtube'}


def _tok():
    return os.environ.get('TELEGRAM_BOT_TOKEN')


def _src_ok(chat):
    want = (os.environ.get('TELEGRAM_SOURCE_CHAT') or '').lstrip('@').lower()
    return bool(want) and (str(chat.get('id')) == want or (chat.get('username') or '').lower() == want)


LABELS = ('ویدیو', 'ویدئو', 'کاور', 'کپشن', 'video', 'cover', 'caption')
WAIT_HOURS = 6


def _unlabel(text):
    """Drop helper labels the owner types ("ویدیو", "کاور", "کپشن:" ...) - alone or at the start of a message."""
    t = (text or '').strip()
    for lab in LABELS:
        if t.lower() == lab:
            return ''
        for sep in (':', '：', '-', '\n', ' '):
            if t.lower().startswith(lab + sep):
                t = t[len(lab) + 1:].strip(); break
    return t


def _status(cap):
    return 'skip' if any(t in (cap or '') for t in SKIP_TAGS) else 'new'


def _owner_ok(chat):
    """Private chat of the owner with the bot (TELEGRAM_CHAT_ID): old channel posts forwarded there count as Shorts too."""
    own = os.environ.get('TELEGRAM_CHAT_ID') or ''
    return bool(own) and chat.get('type') == 'private' and str(chat.get('id')) == own


def _has_words(t):
    return any(ch.isalnum() for ch in (t or ''))       # "👍", "✅" ... are not captions


def _video_of(p):
    d = p.get('document') or {}
    return p.get('video') or (d if d.get('mime_type', '').startswith('video/') else None)


def poll():
    """Read the inbox channel (and the owner's private chat with the bot) into data/shorts_inbox.json.

    One Short = one video + its cover photo + its caption text, sent next to each other in ANY order (the video's own caption
    and Telegram's own video cover count too). A part of a type the open group already has starts the next group; a group
    is closed once it has all three. Emoji-only texts and the labels ویدیو/کاور/کپشن are ignored.
    A video whose group is not complete waits (status "wait") up to WAIT_HOURS for the missing parts.
    Returns the number of new videos."""
    tok = _tok()
    if not tok or not (os.environ.get('TELEGRAM_SOURCE_CHAT') or os.environ.get('TELEGRAM_CHAT_ID')):
        print('shorts: TELEGRAM_BOT_TOKEN / TELEGRAM_SOURCE_CHAT not set -> skip'); return 0
    st = load(STATE, {'offset': 0}); inbox = load(INBOX, {'items': []})
    r = requests.get(f'{API}/bot{tok}/getUpdates', params={'offset': st['offset'], 'timeout': 0,
                     'allowed_updates': '["channel_post","edited_channel_post","message"]'}, timeout=30).json()
    if not r.get('ok'):
        raise RuntimeError(f'telegram getUpdates: {r}')
    by_key = {(i['chat'], i['msg']): i for i in inbox['items']}
    groups = st.setdefault('open', {})                  # chat id -> open group {"video": key|None, "cover": id, "caption": text}
    new = 0
    for u in r['result']:
        st['offset'] = u['update_id'] + 1
        edited = 'edited_channel_post' in u
        p = u.get('channel_post') or u.get('edited_channel_post') or u.get('message')
        if not p or not (_src_ok(p['chat']) or _owner_ok(p['chat'])):
            continue
        chat = str(p['chat']['id']); key = (p['chat']['id'], p['message_id'])
        v = _video_of(p)
        if edited:                                      # edited caption of a known video
            if v and key in by_key and by_key[key]['status'] in ('wait', 'new'):
                by_key[key]['caption'] = _unlabel(p.get('caption') or '') or by_key[key]['caption']
            continue
        parts = {}
        if v:
            parts['video'] = v
            vc = (v.get('cover') or [None])[-1]
            if vc:
                parts['cover'] = vc['file_id']
        if p.get('photo'):
            parts['cover'] = p['photo'][-1]['file_id']
        txt = _unlabel(p.get('caption') or p.get('text') or '')
        if _has_words(txt) and not txt.startswith('/'):
            parts['caption'] = txt
        if not parts:
            continue
        g = groups.get(chat)
        # a part the open group already has -> this message belongs to the next Short
        # (a video's built-in Telegram cover never forces a new group: a separate cover photo may already be there)
        clash = [k for k in parts if not (k == 'cover' and 'video' in parts and not p.get('photo'))]
        if g and any(g.get(k) for k in clash):
            g = None
        if g is None:
            g = groups[chat] = {'video': None, 'cover': None, 'caption': None}
        if 'video' in parts:
            orig = p.get('forward_origin') or {}
            item = {'chat': p['chat']['id'], 'msg': p['message_id'], 'date': orig.get('date') or p.get('forward_date') or p['date'],
                    'got': p['date'], 'file_id': v['file_id'], 'size': v.get('file_size', 0), 'width': v.get('width'),
                    'height': v.get('height'), 'seconds': v.get('duration'), 'caption': '', 'cover': None, 'status': 'wait'}
            inbox['items'].append(item); by_key[key] = item; g['video'] = list(key); new += 1
        for k in ('cover', 'caption'):
            if k in parts and not g.get(k):
                g[k] = parts[k]
        if g['video']:                                  # copy what the group has onto its video
            item = by_key[tuple(g['video'])]
            item['cover'] = g['cover'] or item['cover']; item['caption'] = g['caption'] or item['caption']
            if g['cover'] and g['caption']:
                item['status'] = _status(item['caption']); groups.pop(chat, None)
    save(INBOX, inbox); save(STATE, st)
    return new


def download(file_id, dest):
    tok = _tok()
    info = requests.get(f'{API}/bot{tok}/getFile', params={'file_id': file_id}, timeout=30).json()
    if not info.get('ok'):
        raise RuntimeError(f'telegram getFile: {info.get("description")}')
    url = f'{API}/file/bot{tok}/{info["result"]["file_path"]}'
    dest = pathlib.Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
    return dest


HASHTAG = re.compile(r'#[\w‌]+')


def package(item):
    """Title / description / tags from the Telegram caption."""
    cap = (item.get('caption') or '').strip()
    tags_in = HASHTAG.findall(cap)
    lines = [l.strip() for l in HASHTAG.sub('', cap).splitlines() if l.strip()]
    title = lines[0] if lines else 'کومندی'
    body = '\n'.join(lines[1:])
    hashtags = list(dict.fromkeys(tags_in + CFG['channel']['default_hashtags']))
    if '#Shorts' not in hashtags:
        hashtags.append('#Shorts')
    title = title[:90]
    links = CFG['channel'].get('links', {})
    desc = '\n\n'.join(x for x in [body, f'📲 اینستاگرام: {links["instagram"]}' if links.get('instagram') else '',
                                   ' '.join(hashtags)] if x)
    tags = [h.lstrip('#').replace('_', ' ') for h in hashtags if h.lower() != '#shorts'] + ['کومندی', 'Koumandi', 'بازی آموزشی']
    return title, desc, list(dict.fromkeys(tags))[:20]


def short_slots(hist, now=None):
    """Free daily Short slots (schedule.short_time_local, Tehran) from today up to short_days_ahead days, oldest first.
    A slot counts as taken when history has a Short with that `slot`. Today's slot only if it is still > 20 min away."""
    from zoneinfo import ZoneInfo
    sc = CFG['schedule']; tz = ZoneInfo(sc['timezone'])
    now = now or dt.datetime.now(dt.timezone.utc)
    h, m = map(int, sc['short_time_local'].split(':'))
    taken = {e.get('slot') for e in hist['episodes'] if e.get('kind') == 'short'}
    out = []
    for d in range(int(sc.get('short_days_ahead', 2)) + 1):
        day = (now.astimezone(tz) + dt.timedelta(days=d)).date()
        at = dt.datetime.combine(day, dt.time(h, m), tzinfo=tz).astimezone(dt.timezone.utc)
        if at > now + dt.timedelta(minutes=20) and day.isoformat() not in taken:
            out.append((day.isoformat(), at))
    return out[:int(sc.get('short_days_ahead', 2))]


def publish_due(yt, hist, left, dry=False):
    """Fill the free daily Short slots with the oldest ready inbox videos: uploaded now as private with YouTube's publishAt
    = the slot time (exactly 17:00 Tehran), so GitHub's cron delays never matter. Returns report lines."""
    from . import youtube
    inbox = load(INBOX, {'items': []}); out = []
    slots = short_slots(hist)
    now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
    ready = lambda x: x['status'] == 'new' or (x['status'] == 'wait' and now_ts - x.get('got', x['date']) > WAIT_HOURS * 3600)
    for i in sorted((x for x in inbox['items'] if ready(x)), key=lambda x: x['date']):
        if not slots or left <= 0:
            break
        sid = f'TG-{i["msg"]}'
        if i.get('size', 0) > MAX_BOT_DOWNLOAD:
            i['status'] = 'too_big'
            out.append(f'⚠️ {sid}: فایل بزرگ‌تر از ۲۰ مگابایت است؛ ربات تلگرام نمی‌تواند دانلودش کند. نسخه‌ی فشرده‌تر بفرستید.'); continue
        work = ROOT / 'work' / sid
        try:
            mp4 = download(i['file_id'], work / 'video.mp4')
            secs = duration(mp4)
            if secs > CFG['short']['max_seconds']:
                i['status'] = 'too_long'; out.append(f'⚠️ {sid}: {secs:.0f} ثانیه، بیشتر از حد شورت'); continue
            cover = download(i['cover'], work / 'cover.jpg') if i.get('cover') else None
            title, desc, tags = package(i)
            if dry:
                out.append(f'🧪 {sid}: {title} ({secs:.0f}s) - not uploaded'); continue
            slot_day, slot_at = slots[0]
            ep = {'id': sid, 'kind': 'short', 'publish_at': slot_at.strftime('%Y-%m-%dT%H:%M:%SZ')}
            vid = youtube.upload(yt, mp4, ep, title + ' #Shorts', desc, tags)
            thumb = youtube.set_thumb(yt, vid, cover) if cover else None
            try:
                youtube.add_to_playlist(yt, vid, 'short')
            except Exception as e:
                print('playlist failed', e)
            i['status'] = 'done'; i['video_id'] = vid
            hist['episodes'].append({'id': sid, 'kind': 'short', 'title': title, 'caption': i.get('caption', ''), 'video_id': vid,
                                     'tg_file_id': i['file_id'], 'seconds': round(secs, 1), 'thumb': thumb,
                                     'slot': slot_day, 'publish_at': ep['publish_at'],
                                     'uploaded_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')})
            slots.pop(0); left -= 1
            out.append(f'✅ شورت {sid} -> https://youtu.be/{vid} (انتشار {slot_day} ساعت {CFG["schedule"]["short_time_local"]})')
        except Exception as e:
            out.append(f'❌ {sid}: {str(e)[:300]}')
    save(INBOX, inbox)
    return out
