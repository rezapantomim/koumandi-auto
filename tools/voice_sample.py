"""Make Persian voice samples so the owner can pick the voice and check pronunciation.

python tools/voice_sample.py                      # default test text, both voices -> work/voice-samples/*.mp3
python tools/voice_sample.py "متن دلخواه"          # your own sentence
"""
import asyncio, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pipeline.common import CFG, ROOT
from pipeline.tts import spoken

TEXT = ('سلام دوستان! به کانال کومندی خوش آمدید. امروز با کوروش، میا و ایمان به سفری پر از دانش می‌رویم. '
        'می‌دانستید که کِرمِ ابریشم، نخِ ابریشم را می‌سازد؟ پادشاهی هخامنشی را کوروشِ بزرگ بنیان گذاشت. '
        'عِلم یعنی دانستن، و پرچم را عَلَم هم می‌گویند.')


async def one(text, voice, mp3):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=CFG['voice']['edge']['rate']).save(str(mp3))


def main():
    text = sys.argv[1] if len(sys.argv) > 1 else TEXT
    out = ROOT / 'work/voice-samples'; out.mkdir(parents=True, exist_ok=True)
    for v in CFG['voice']['alternatives']:
        mp3 = out / f'{v}.mp3'
        asyncio.run(one(spoken(text), v, mp3))
        print(mp3)


if __name__ == '__main__':
    main()
