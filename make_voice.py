#!/usr/bin/env python3
# Bhaalu Run: Madhur + Swara (Microsoft Neural) awaaz banata hai.
# Chalane ka tarika (game.html wale folder mein):  python3 make_voice.py
import asyncio, base64, json, os, re, shutil, subprocess, sys, tempfile

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts nahi mila. Pehle chalao:  pip install -U edge-tts --break-system-packages")

HTML = sys.argv[1] if len(sys.argv) > 1 else "game.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(HTML)), "voices.js")
src = open(HTML, encoding="utf-8").read()
m = re.search(r"const VOICE_PHRASES = (\[.*?\]);", src, re.S)
if not m:
    sys.exit("game.html mein VOICE_PHRASES nahi mila. Naya game.html (v12) use karo.")
PHRASES = json.loads(m.group(1))
VOICES = {"madhur": "hi-IN-MadhurNeural", "swara": "hi-IN-SwaraNeural"}
FF = shutil.which("ffmpeg")
print(f"{len(PHRASES)} jumle x {len(VOICES)} awaaz | ffmpeg: {'haan' if FF else 'nahi (silence trim nahi hoga)'}")

async def synth(text, voice, path):
    rate = "-20%" if len(text) <= 5 else "-8%"          # chhote akshar thoda dheere
    err = None
    for k in range(5):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(path)
            if os.path.getsize(path) > 500:
                return
        except Exception as e:
            err = e
        await asyncio.sleep(1.5 * (k + 1))
    raise RuntimeError(f"'{text}' ({voice}) nahi bana: {err}")

def tidy(src_mp3, dst_mp3):
    if not FF:
        shutil.copy(src_mp3, dst_mp3); return
    af = ("silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,areverse,"
          "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.08,areverse,apad=pad_dur=0.12")
    r = subprocess.run([FF, "-y", "-loglevel", "error", "-i", src_mp3, "-af", af, "-ac", "1", "-ar", "24000",
                        "-c:a", "libmp3lame", "-b:a", "48k", dst_mp3])
    if r.returncode != 0:
        shutil.copy(src_mp3, dst_mp3)

async def main():
    packs = {}
    tmp = tempfile.mkdtemp()
    sem = asyncio.Semaphore(4)
    for key, voice in VOICES.items():
        pack = {}
        async def one(i, t):
            raw = os.path.join(tmp, f"{key}_{i}.raw.mp3"); fin = os.path.join(tmp, f"{key}_{i}.mp3")
            async with sem:
                await synth(t, voice, raw)
            tidy(raw, fin)
            pack[t] = "data:audio/mpeg;base64," + base64.b64encode(open(fin, "rb").read()).decode()
        await asyncio.gather(*[one(i, t) for i, t in enumerate(PHRASES)])
        packs[key] = {t: pack[t] for t in PHRASES}
        kb = sum(len(v) for v in pack.values()) * 3 // 4 // 1024
        print(f"  {key}: {len(pack)} jumle, ~{kb} KB")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("window.VOICE_EXTRA = " + json.dumps(packs, ensure_ascii=False) + ";\n")
    print("Ban gaya:", OUT, f"({os.path.getsize(OUT)//1024} KB)")

asyncio.run(main())
