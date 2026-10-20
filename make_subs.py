# -*- coding: utf-8 -*-
"""
make_subs.py - screen par jalne wale subtitle aur bacche ke naam wali patti ki tasveerein (img/subs/, img/) banata hai.
Ye pehle se bana kar de diya gaya hai. Videos.py ka text badalne par dobara chalayein:
    pip install pillow
    python make_subs.py
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, features

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import videos  # noqa: E402

W, H = 1280, 720
FONT_HI = os.path.join(BASE, "fonts", "baloo_deva.ttf")
FONT_EN = os.path.join(BASE, "fonts", "baloo_latin.ttf")
SUBDIR = os.path.join(BASE, "img", "subs")


def is_hi(s):
    return any(0x900 <= ord(c) <= 0x97F for c in s)



def runs(text):
    """Text ko (hindi-run, latin-run) tukdon mein todta hai, taaki '!' ':' jaise chinh bhi dikhein."""
    out = []
    for c in text:
        hi = 0x900 <= ord(c) <= 0x97F or c in "\u200d\u200c"
        if c == " " and out:
            hi = out[-1][0]
        if out and out[-1][0] == hi:
            out[-1][1] += c
        else:
            out.append([hi, c])
    return out


def get_fonts(size):
    return ImageFont.truetype(FONT_HI, size), ImageFont.truetype(FONT_EN, size)


def line_width(text, size):
    fh, fe = get_fonts(size)
    return sum((fh if hi else fe).getlength(t) for hi, t in runs(text))


def draw_line(d, x, y, text, size, fill, sw, sf):
    fh, fe = get_fonts(size)
    ascent = max(fh.getmetrics()[0], fe.getmetrics()[0])
    for hi, t in runs(text):
        f = fh if hi else fe
        d.text((x, y + ascent), t, font=f, fill=fill, stroke_width=sw, stroke_fill=sf, anchor="ls")
        x += f.getlength(t)


def fit_size(line, max_w, size):
    while size > 24 and line_width(line, size) > max_w:
        size -= 2
    return size


def _old_fit_font(line, max_w, size):
    path = FONT_HI if is_hi(line) else FONT_EN
    while size > 26:
        f = ImageFont.truetype(path, size)
        if f.getlength(line) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, size)


def make_sub(text, out):
    lines = text.split("\n")
    two = len(lines) > 1
    base = 44 if not two else 40
    max_w = 940
    sizes = [fit_size(l, max_w, base) for l in lines]
    lh = [int(sz * 1.45) for sz in sizes]
    gap = 0
    th = sum(lh) + gap * (len(lines) - 1)
    tw = max(int(line_width(l, sz)) for l, sz in zip(lines, sizes))
    padx, pady = 34, 12
    pw, ph = tw + 2 * padx, th + 2 * pady
    cx, bottom = 770, H - 12
    x0, y0 = max(cx - pw // 2, 280), bottom - ph
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=28, fill=(20, 20, 40, 170))
    y = y0 + pady
    for i, (l, sz) in enumerate(zip(lines, sizes)):
        col = (255, 226, 90, 255) if (two and i == 0) else (255, 255, 255, 255)
        lw = line_width(l, sz)
        draw_line(d, x0 + pw / 2 - lw / 2, y, l, sz, col, 3, (10, 10, 30, 255))
        y += lh[i] + gap
    im.save(out)


def star(d, cx, cy, r, fill):
    import math
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=(255, 255, 255, 255))


def make_name(name, out):
    size = 94
    nw = int(line_width(name, size))
    fh, _ = get_fonts(size)
    asc, desc = fh.getmetrics()
    pw, ph = nw + 160, asc + desc + 26
    cx, top = 700, 8
    x0, y0 = cx - pw // 2, top
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0 + 8, y0 + 10, x0 + pw + 8, y0 + ph + 10), radius=60, fill=(0, 0, 0, 70))
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=60, fill=(255, 224, 110, 255),
                        outline=(255, 255, 255, 255), width=10)
    draw_line(d, cx - nw / 2, y0 + 2, name, size, (214, 40, 110, 255), 7, (255, 255, 255, 255))
    for (sx, sy, sr, col) in ((x0 + 28, y0 + 24, 20, (255, 120, 120, 255)), (x0 + pw - 30, y0 + 28, 24, (110, 190, 255, 255)),
                              (x0 + pw - 70, y0 + ph - 20, 16, (130, 220, 130, 255)), (x0 + 80, y0 + ph - 14, 14, (255, 160, 60, 255))):
        star(d, sx, sy, sr, col)
    im.save(out)


if __name__ == "__main__":
    if not features.check("raqm"):
        print("WARNING: Pillow mein raqm nahi hai, Hindi matra galat ban sakti hain.")
    os.makedirs(SUBDIR, exist_ok=True)
    n = 0
    for vid in videos.ORDER:
        for si, s in enumerate(videos.VIDEOS[vid]["scenes"], 1):
            for ci, c in enumerate(s["subs"], 1):
                make_sub(c, os.path.join(SUBDIR, "%s_%02d_%02d.png" % (vid, si, ci)))
                n += 1
    make_name(videos.NAME_LKG, os.path.join(BASE, "img", "name_T.png"))
    make_name(videos.NAME_C1, os.path.join(BASE, "img", "name_R.png"))
    print("Bane: %d subtitle + 2 naam-patti" % n)
