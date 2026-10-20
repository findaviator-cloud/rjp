# -*- coding: utf-8 -*-
"""make_text.py - har scene ka Balabolka text (scene01.txt, scene02.txt ...) video ke folder mein banata hai."""
import os
import sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import videos  # noqa: E402

for vid in videos.ORDER:
    V = videos.VIDEOS[vid]
    d = os.path.join(BASE, vid)
    os.makedirs(d, exist_ok=True)
    for i, s in enumerate(V["scenes"], 1):
        with open(os.path.join(d, "scene%02d.txt" % i), "w", encoding="utf-8-sig") as f:
            f.write(s["text"] + "\n")
print("scene text files ban gayi.")
