#!/usr/bin/env python3
# Tez tarika: kam request bhejta hai. Bahut saari lines ek saath bulwata hai, phir khaamoshi dekhkar clip-clip kaat deta hai.
# audio_list.csv ke jo clips audio/ mein abhi nahi bane, sirf wahi banata hai.   Chalayein:  python3 make_audio_fast.py
import asyncio, csv, os, re, shutil, subprocess, sys, tempfile

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts nahi mila. Pehle chalao:  pip install -U edge-tts --break-system-packages")
FF = shutil.which("ffmpeg"); FP = shutil.which("ffprobe")
if not FF or not FP: sys.exit("ffmpeg/ffprobe chahiye:  sudo apt install ffmpeg")
here = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(here, "audio"); os.makedirs(out, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(here, "audio_list.csv"), encoding="utf-8-sig")))
VOICE = {"hi": os.environ.get("HI_VOICE", "hi-IN-SwaraNeural"), "en": os.environ.get("EN_VOICE", "en-IN-NeerjaNeural")}
CH = int(os.environ.get("CHUNK", "30")); tmp = tempfile.mkdtemp(); flagged = []
run = lambda *a, **k: subprocess.run(*a, stdin=subprocess.DEVNULL, **k)

def dur(p): return float(run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())

def segments(p, noise, d):
    r = run([FF, "-nostdin", "-i", p, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    total = dur(p); segs = []; cur = 0.0
    for i, s in enumerate(st):
        if s - cur > 0.05: segs.append([cur, s])
        cur = en[i] if i < len(en) else total
    if total - cur > 0.05: segs.append([cur, total])
    return segs

def fit(segs, n):
    while len(segs) > n:
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]; i = gaps.index(min(gaps))
        segs[i] = [segs[i][0], segs[i + 1][1]]; del segs[i + 1]
    return segs

def tidy(src, a, b, dst):
    af = "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.08,areverse,apad=pad_dur=0.12"
    run([FF, "-nostdin", "-y", "-loglevel", "error", "-ss", f"{max(0, a - 0.06):.3f}", "-to", f"{b + 0.10:.3f}", "-i", src, "-af", af, "-ac", "1", "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "64k", dst])

async def synth(text, voice, path, rate):
    err = None
    for k in range(4):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(path)
            if os.path.getsize(path) > 500: return True
        except Exception as e:
            err = e
        await asyncio.sleep(2 * (k + 1))
    print("   request fail:", err); return False

def punct(t):
    t = t.strip().replace("\n", " ")
    return t if t[-1] in "।.?!" else (t + ("।" if re.search("[ऀ-ॿ]", t) else "."))

async def do_chunk(chunk, lang, sem, tag, depth=0):
    n = len(chunk); dst = [os.path.join(out, r["file_name"]) for r in chunk]
    if n == 1:
        raw = os.path.join(tmp, f"{tag}.mp3")
        async with sem: ok = await synth(chunk[0]["text_to_speak"], VOICE[lang], raw, "-25%" if len(chunk[0]["text_to_speak"]) <= 2 else "-10%")
        if ok: tidy(raw, 0, dur(raw), dst[0]); return 1
        return 0
    raw = os.path.join(tmp, f"{tag}.mp3"); text = "\n\n".join(punct(r["text_to_speak"]) for r in chunk)
    async with sem: ok = await synth(text, VOICE[lang], raw, "-8%")
    segs = None
    if ok:
        for d in (0.45, 0.35, 0.28, 0.22, 0.17):
            s = segments(raw, "-38dB", d)
            if len(s) >= n: segs = fit(s, n); break
    if not segs:           # tukde gine nahi mile -> aadha-aadha karke dobara
        h = n // 2; print(f"   {tag}: tukde nahi mile, {n} ko {h}+{n-h} mein baant raha hoon")
        a = await do_chunk(chunk[:h], lang, sem, tag + "a", depth + 1); b = await do_chunk(chunk[h:], lang, sem, tag + "b", depth + 1); return a + b
    for (a, b), r, d in zip(segs, chunk, dst):
        tidy(raw, a, b, d)
        L = max(1, len(r["text_to_speak"])); flagged.append((b - a, L, r))
    return n

async def main():
    todo = [r for r in rows if not os.path.exists(os.path.join(out, r["file_name"]))]
    print(f"Kul {len(rows)} | baaki {len(todo)}")
    sem = asyncio.Semaphore(3); jobs = []
    for lang in ("hi", "en"):
        rs = [r for r in todo if (r["language"] == "hi") == (lang == "hi")]
        for k in range(0, len(rs), CH): jobs.append(do_chunk(rs[k:k + CH], lang, sem, f"{lang}{k // CH}"))
    done = 0
    for f in asyncio.as_completed(jobs):
        done += await f; print(f"  {done}/{len(todo)} ban gaye")
    left = [r for r in rows if not os.path.exists(os.path.join(out, r["file_name"]))]
    odd = [r["file_name"] + "  " + r["text_to_speak"] for d, L, r in flagged if not (0.4 < d / (0.4 + 0.07 * L) < 3.2)]
    if odd:
        open(os.path.join(here, "audio_suspect.txt"), "w", encoding="utf-8").write("\n".join(odd))
        print(f"NOTE: {len(odd)} clips ki lambai ajeeb lagi - inhe zaroor sun lein (list: audio_suspect.txt)")
    print("Poora ho gaya!" if not left else f"{len(left)} clips baaki - dobara chalayein.")
asyncio.run(main())
