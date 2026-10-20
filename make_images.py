# -*- coding: utf-8 -*-
"""
make_images.py  -  video ke bade akshar / ankon ki tasveerein (img/ folder) banata hai.
Ye pehle se bana kar de diya gaya hai. Dobara banana ho (naya akshar jodne par) to:
    pip install pillow
    python make_images.py
Font: Baloo 2 (SIL Open Font License) - fonts/ folder mein.
Hindi ki matra/jodakshar yahan sahi tarah se banti hain, isliye Blender mein Hindi font ki zaroorat nahi.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, features

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import videos  # noqa: E402

if not features.check("raqm"):
    print("WARNING: Pillow mein raqm nahi hai, Hindi matra galat ban sakti hain.")

PX = 400
PAD = 40
CH = 600          # canvas height
BASELINE = 430


def key(s):
    return "_".join("%04x" % ord(c) for c in s)


def all_strings():
    S = set(str(i) for i in range(0, 11)) | set("?+=") | set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for v in videos.VIDEOS.values():
        for sc in v["scenes"]:
            vis = sc["vis"]
            for k in ("row", "quiz"):
                S.update(vis.get(k, []))
            if "letter" in vis:
                S.add(vis["letter"])
            if "word" in vis:
                S.update(vis["word"])
            for ch, _ in vis.get("recap", []):
                S.add(ch)
    return sorted(S)


def render(s):
    hi = any(ord(c) > 0x900 for c in s)
    font = ImageFont.truetype(os.path.join(BASE, "fonts", "baloo_deva.ttf" if hi else "baloo_latin.ttf"), PX)
    w = int(font.getlength(s)) + 2 * PAD
    im = Image.new("RGBA", (w, CH), (255, 255, 255, 0))
    d = ImageDraw.Draw(im)
    d.text((PAD, BASELINE), s, font=font, anchor="ls", fill=(255, 255, 255, 255),
           stroke_width=14, stroke_fill=(70, 70, 70, 255))
    return im


if __name__ == "__main__":
    out = os.path.join(BASE, "img")
    os.makedirs(out, exist_ok=True)
    for s in all_strings():
        render(s).save(os.path.join(out, key(s) + ".png"))
    print("Bane:", len(all_strings()), "tasveerein ->", out)
