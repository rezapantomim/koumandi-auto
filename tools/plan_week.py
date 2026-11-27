"""Plan the next long-video slots (one every schedule.long_every_days days, from schedule.long_first_date).

Usage: python tools/plan_week.py [--days N] [--write]
Prints JSON: the empty long slots in the next N days (default schedule.plan_days_ahead), the todo topics, and the
Shorts published so far (their captions are the raw material for new long topics). Slots already in queue/, archive/
or history are skipped, so re-running is safe. --write saves it to work/plan.json for the skill.
"""
import argparse, datetime as dt, json
from zoneinfo import ZoneInfo
from common import ROOT, CFG, load, save


def taken_days():
    ds = set()
    for d in ('queue', 'archive', 'failed'):
        for f in (ROOT / d).glob('L-*.json'):
            ds.add(f.stem.split('-')[1])
    for e in load('data/history.json', {'episodes': []})['episodes']:
        if e['id'].startswith('L-'):
            ds.add(e['id'].split('-')[1])
    return ds


def utc(day, hhmm, tz):
    h, m = map(int, hhmm.split(':'))
    return dt.datetime.combine(day, dt.time(h, m), tzinfo=tz).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int)
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    sc = CFG['schedule']; tz = ZoneInfo(sc['timezone'])
    now = dt.datetime.now(tz)
    first = dt.date.fromisoformat(sc['long_first_date']); every = int(sc['long_every_days'])
    days = a.days or int(sc.get('plan_days_ahead', 7))
    end = now.date() + dt.timedelta(days=days)
    used = taken_days()
    slots, day = [], first
    while day <= end:
        publish = dt.datetime.combine(day, dt.time(*map(int, sc['long_time_local'].split(':'))), tzinfo=tz)
        if publish > now + dt.timedelta(hours=3) and day.strftime('%Y%m%d') not in used:
            slots.append({'slot': 'L-' + day.strftime('%Y%m%d'), 'publish_at': utc(day, sc['long_time_local'], tz)})
        day += dt.timedelta(days=every)
    topics = [t for t in load('data/topics.json', []) if t['status'] == 'todo']
    shorts = [{'id': e['id'], 'title': e.get('title'), 'caption': e.get('caption', ''), 'video_id': e.get('video_id'),
               'tg_file_id': e.get('tg_file_id'), 'seconds': e.get('seconds')}
              for e in load('data/history.json', {'episodes': []})['episodes'] if e.get('kind') == 'short']
    used_shorts = {s for t in load('data/topics.json', []) for s in t.get('from_shorts', [])}
    out = {'today': now.date().isoformat(), 'slots': slots, 'topics_todo': topics,
           'shorts_not_yet_used': [s for s in shorts if s['id'] not in used_shorts], 'shorts_total': len(shorts),
           'warnings': [w for w in [
               f'only {len(topics)} topics for {len(slots)} slots - run topic discovery' if len(topics) < len(slots) else '',
               'no Shorts published yet - topics come from the channel theme and the game (see config/rules.md)' if not shorts else '']
               if w]}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if a.write:
        save(ROOT / 'work/plan.json', out)


if __name__ == '__main__':
    main()
