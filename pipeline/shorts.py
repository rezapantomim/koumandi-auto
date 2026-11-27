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


def _owner_ok(chat):
    """Private chat of the owner with the bot (TELEGRAM_CHAT_ID): old channel posts forwarded there count as Shorts too."""
    own = os.environ.get('TELEGRAM_CHAT_ID') or ''
    return bool(own) and chat.get('type') == 'private' and str(chat.get('id')) == own


def poll():
    """Read new channel posts (and videos the owner forwards to the bot) into the inbox. Returns number of new videos."""
    tok = _tok()
    if not tok or not os.environ.get('TELEGRAM_SOURCE_CHAT'):
        print('shorts: TELEGRAM_BOT_TOKEN / TELEGRAM_SOURCE_CHAT not set -> skip'); return 0
    st = load(STATE, {'offset': 0}); inbox = load(INBOX, {'items': []})
    known = {(i['chat'], i['msg']) for i in inbox['items']}
    r = requests.get(f'{API}/bot{tok}/getUpdates', params={'offset': st['offset'], 'timeout': 0,
                     'allowed_updates': '["channel_post","edited_channel_post","message"]'}, timeout=30).json()
    if not r.get('ok'):
        raise RuntimeError(f'telegram getUpdates: {r}')
    photos, new = {}, 0
    for u in r['result']:
        st['offset'] = u['update_id'] + 1
        p = u.get('channel_post') or u.get('edited_channel_post') or u.get('message')
        if not p or not (_src_ok(p['chat']) or _owner_ok(p['chat'])):
            continue
        if p.get('photo'):                               # possible cover: same album or reply to a video
            best = p['photo'][-1]['file_id']
            if p.get('media_group_id'):
                photos[p['media_group_id']] = best
            if p.get('reply_to_message'):
                photos[('reply', p['reply_to_message']['message_id'])] = best
        v = p.get('video') or (p.get('document') if (p.get('document') or {}).get('mime_type', '').startswith('video/') else None)
        if not v:
            continue
        key = (p['chat']['id'], p['message_id'])
        cap = p.get('caption') or ''
        if key in known:                                 # edited caption -> update
            for i in inbox['items']:
                if (i['chat'], i['msg']) == key and i['status'] == 'new':
                    i['caption'] = cap
            continue
        orig = p.get('forward_origin') or {}
        date = orig.get('date') or p.get('forward_date') or p['date']      # forwarded backlog keeps the original order
        vcover = (v.get('cover') or [None])[-1]                              # Telegram's own video cover, if set
        inbox['items'].append({'chat': p['chat']['id'], 'msg': p['message_id'], 'date': date, 'file_id': v['file_id'],
                               'size': v.get('file_size', 0), 'width': v.get('width'), 'height': v.get('height'),
                               'seconds': v.get('duration'), 'caption': cap, 'group': p.get('media_group_id'),
                               'cover': vcover['file_id'] if vcover else None, 'status': 'skip' if any(t in cap for t in SKIP_TAGS) else 'new'})
        known.add(key); new += 1
    for i in inbox['items']:                             # attach covers found in this batch
        c = photos.get(i.get('group')) or photos.get(('reply', i['msg']))
        if c and not i.get('cover'):
            i['cover'] = c
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


def publish_due(yt, hist, left, dry=False):
    """Upload up to short_max_per_day new inbox videos (oldest first). Returns report lines."""
    from . import youtube
    inbox = load(INBOX, {'items': []}); out = []
    today = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
    done_today = sum(1 for e in hist['episodes'] if e.get('kind') == 'short' and (e.get('uploaded_at') or '').startswith(today))
    room = min(left, CFG['schedule']['short_max_per_day'] - done_today)
    for i in sorted((x for x in inbox['items'] if x['status'] == 'new'), key=lambda x: x['date']):
        if room <= 0:
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
            ep = {'id': sid, 'kind': 'short', 'publish_at': dt.datetime.now(dt.timezone.utc).isoformat()}
            vid = youtube.upload(yt, mp4, ep, title + ' #Shorts', desc, tags)
            thumb = youtube.set_thumb(yt, vid, cover) if cover else None
            try:
                youtube.add_to_playlist(yt, vid, 'short')
            except Exception as e:
                print('playlist failed', e)
            i['status'] = 'done'; i['video_id'] = vid
            hist['episodes'].append({'id': sid, 'kind': 'short', 'title': title, 'caption': i.get('caption', ''), 'video_id': vid,
                                     'tg_file_id': i['file_id'], 'seconds': round(secs, 1), 'thumb': thumb,
                                     'uploaded_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')})
            room -= 1
            out.append(f'✅ شورت {sid} -> https://youtu.be/{vid}')
        except Exception as e:
            out.append(f'❌ {sid}: {str(e)[:300]}')
    save(INBOX, inbox)
    return out
