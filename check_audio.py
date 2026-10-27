# Usage:  python3 check_audio.py      (rjp folder ke andar chalayein: audio_list.csv aur audio/ folder saath hon)
import csv, os, sys
here = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(here, "audio_list.csv"), encoding="utf-8-sig")))
have = set(os.listdir(os.path.join(here, "audio"))) if os.path.isdir(os.path.join(here, "audio")) else set()
need = {r["file_name"]: r for r in rows}
miss = [r for f, r in need.items() if f not in have]
extra = sorted(f for f in have if f.endswith((".mp3", ".wav", ".ogg")) and f not in need)
print(f"Total chahiye: {len(need)} | bane hue: {len(need)-len(miss)} | baaki: {len(miss)}")
if extra: print("Ye files list mein nahi hain (naam check karein):", ", ".join(extra[:20]))
if miss:
    with open(os.path.join(here, "audio_missing.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["file_name", "language", "text_to_speak", "note"]); [w.writerow([r["file_name"], r["language"], r["text_to_speak"], r["note"]]) for r in miss]
    print("Baaki clips ki list: audio_missing.csv")
