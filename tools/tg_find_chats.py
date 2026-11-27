"""Show the chat ids the bot has seen (to fill TELEGRAM_SOURCE_CHAT and TELEGRAM_CHAT_ID). Does not consume updates.

1. Make the bot an admin of the Koumandi channel and post anything there.
2. Open the bot in Telegram and press Start (for the report chat).
3. python tools/tg_find_chats.py
Needs TELEGRAM_BOT_TOKEN in .env. Prints only chat ids, types and titles - never the token.
"""
import requests
from common import env

tok = env('TELEGRAM_BOT_TOKEN')
if not tok:
    raise SystemExit('TELEGRAM_BOT_TOKEN missing in .env')
me = requests.get(f'https://api.telegram.org/bot{tok}/getMe', timeout=20).json()
print('bot:', '@' + me['result']['username'] if me.get('ok') else me)
r = requests.get(f'https://api.telegram.org/bot{tok}/getUpdates', params={'timeout': 0}, timeout=30).json()
seen = {}
for u in r.get('result', []):
    for k in ('channel_post', 'edited_channel_post', 'message', 'my_chat_member'):
        c = (u.get(k) or {}).get('chat')
        if c:
            seen[c['id']] = (c['type'], c.get('title') or c.get('first_name') or '', c.get('username') or '')
if not seen:
    print('no chats seen yet: post something in the channel (bot must be admin) and press Start in the bot chat, then retry')
for cid, (typ, title, user) in seen.items():
    print(f'{cid}\t{typ}\t{title}\t{"@" + user if user else ""}')
