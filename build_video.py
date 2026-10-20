# -*- coding: utf-8 -*-
"""
build_video.py  -  Blender 3.6 LTS ke liye (4.x par bhi chalta hai)

CMD se chalayein (render.bat ye sab khud kar deta hai):
  blender.exe -b -P build_video.py -- lkg1            poora video: render + mp4 (awaaz ke saath)
  blender.exe -b -P build_video.py -- lkg1 test       sirf 3 frame, render ka time naapne ke liye
  blender.exe -b -P build_video.py -- lkg1 build      sirf scene + .srt + full.wav banata hai
Extra options (kisi bhi order mein):
  draft       aadhe size (640x360) par jaldi render
  workbench   sabse tez, sapaat rang (agar Eevee mein dikkat aaye)
  cycles      (sirf agar Eevee na chale) CPU render, bahut dheema

Kaam:
  1. <video>/scene01.wav, scene02.wav ... ki lambai padhta hai (nahi mile to andaza lagata hai)
  2. frames = awaaz ki lambai x 12 fps
  3. <video>/<video>.srt aur <video>/full.wav banata hai
  4. 3D scene (bhaalu, board, cheezein) banakar <video>/frames/0001.png ... render karta hai
  5. frames + full.wav ko jodkar <video>/<video>.mp4 banata hai
"""
import bpy
import sys
import os
import math
import random
import time
import wave
import glob
import contextlib

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import videos  # noqa: E402

FPS = 12
RES = (1280, 720)
LEAD, GAP, TAIL = 0.5, 0.5, 0.6      # seconds
CX = 1.65                            # content area ka center (x)

WHITE = (1, 1, 1)
DARK = (0.12, 0.12, 0.20)
BROWN = (0.52, 0.31, 0.14)
CREAM = (0.98, 0.90, 0.72)
PALETTE = [videos.RED, videos.BLUE, videos.GREEN, videos.ORANGE, videos.PINK, videos.YELLOW]


# ------------------------------------------------------------------ args
def parse_args():
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    if not args or args[0] not in videos.VIDEOS:
        print("\nVideo ka naam dein. Options:", ", ".join(videos.ORDER))
        raise SystemExit(1)
    return args[0], set(a.lower() for a in args[1:])


# ------------------------------------------------------------------ audio / timeline
def wav_info(path):
    with contextlib.closing(wave.open(path, "rb")) as w:
        return w.getparams()


def wav_env(path, fps):
    """Har video-frame ke liye awaaz ki tezi (0..1). Hont isi se hilenge."""
    import struct
    with contextlib.closing(wave.open(path, "rb")) as w:
        ch, sw, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw != 2:
        return None
    vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
    if ch > 1:
        vals = vals[::ch]
    step = rate / float(fps)
    out = []
    i = 0
    k = 0
    while int(k * step) < len(vals):
        seg = vals[int(k * step):int((k + 1) * step)]
        if seg:
            out.append((sum(x * x for x in seg) / float(len(seg))) ** 0.5)
        k += 1
    if not out:
        return None
    srt = sorted(out)
    ref = srt[int(len(srt) * 0.9)] or 1.0
    return [min(1.0, v / ref) for v in out]


def estimate_dur(text, lang):
    chars = len(text.replace(" ", ""))
    return max(2.0, chars / (8.0 if lang == "hi" else 11.0))


def fr(t):
    return int(round(t * FPS)) + 1


def make_timeline(vid, V, outdir):
    scenes = V["scenes"]
    paths = [os.path.join(outdir, "scene%02d.wav" % (i + 1)) for i in range(len(scenes))]
    have = [os.path.isfile(p) for p in paths]
    exact = all(have)
    if any(have) and not exact:
        miss = ["scene%02d.wav" % (i + 1) for i, h in enumerate(have) if not h]
        print("\nWARNING: ye audio files nahi mili:", ", ".join(miss))
        print("         Isliye abhi ANDAZE (estimate) se timing banegi.\n")
    elif not any(have):
        print("\nNOTE: scene wav files nahi mili. ANDAZE (estimate) se timing ban rahi hai.")
        print("      Test/preview ke liye theek hai; asli video ke liye pehle Balabolka se awaaz banayein.\n")
    params = None
    t = LEAD
    for i, s in enumerate(scenes):
        if exact:
            p = wav_info(paths[i])
            if params is None:
                params = p
            elif (p.nchannels, p.sampwidth, p.framerate) != (params.nchannels, params.sampwidth, params.framerate):
                print("ERROR: scene%02d.wav ka format baaki se alag hai. Sab wav ek hi voice/setting se banayein." % (i + 1))
                raise SystemExit(1)
            s["adur"] = p.nframes / float(p.framerate)
            s["env"] = wav_env(paths[i], FPS)
        else:
            s["adur"] = estimate_dur(s["text"], V["lang"])
        s["pause"] = s.get("pause", 0)
        s["t0"] = t
        s["dur"] = s["adur"] + s["pause"] + GAP
        t += s["dur"]
    total = t + TAIL
    return exact, paths, params, total


def write_full_wav(outdir, scenes, paths, params):
    out = os.path.join(outdir, "full.wav")
    sw, ch, rate = params.sampwidth, params.nchannels, params.framerate
    zero = b"\x80" if sw == 1 else b"\x00"

    def silence(sec):
        return zero * (int(round(sec * rate)) * ch * sw)

    with contextlib.closing(wave.open(out, "wb")) as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(rate)
        w.writeframes(silence(LEAD))
        for s, p in zip(scenes, paths):
            with contextlib.closing(wave.open(p, "rb")) as r:
                w.writeframes(r.readframes(r.getnframes()))
            w.writeframes(silence(s["pause"] + GAP))
        w.writeframes(silence(TAIL))
    return out


def srt_time(t):
    ms = int(round(t * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def chunk_times(s):
    """Ek scene ke har subtitle tukde ka (shuru, ant) samay. Asli awaaz ho to chuppi (sannate) ke beech mein tukda badalta hai."""
    chunks = s["subs"]
    wts = [max(len(c.replace("\n", "")), 1) for c in chunks]
    tot = float(sum(wts))
    t0 = s["t0"]
    end_all = t0 + s["adur"] + s["pause"] + GAP * 0.6
    starts = None
    env = s.get("env")
    if env and len(chunks) > 1:
        voiced = [1 if v >= 0.18 else 0 for v in env]
        V = sum(voiced)
        if V >= len(chunks):
            targets = [sum(wts[:i + 1]) / tot * V for i in range(len(chunks) - 1)]
            starts = [t0]
            cum, ti = 0, 0
            for j, vv in enumerate(voiced):
                cum += vv
                while ti < len(targets) and cum >= targets[ti] - 1e-9:
                    e = j + 1
                    while e < len(voiced) and not voiced[e]:
                        e += 1
                    mid = (j + 1 + e) / 2.0 if e < len(voiced) else j + 1
                    starts.append(t0 + mid / FPS)
                    ti += 1
            if len(starts) != len(chunks):
                starts = None
    if starts is None:
        starts, t = [], t0
        for wt in wts:
            starts.append(t)
            t += s["adur"] * wt / tot
    out = []
    for i, st in enumerate(starts):
        en = starts[i + 1] if i + 1 < len(starts) else end_all
        out.append((st, en))
    return out


def write_srt(outdir, vid, scenes):
    lines = []
    n = 1
    for s in scenes:
        for c, (st, en) in zip(s["subs"], chunk_times(s)):
            lines.append("%d\n%s --> %s\n%s\n" % (n, srt_time(st), srt_time(en - 0.04), c))
            n += 1
    path = os.path.join(outdir, vid + ".srt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def build_overlays(vid, V):
    """Screen par jalne wale subtitle aur naam-patti ki list: (png, shuru_sec, ant_sec, kism)."""
    name = videos.NAME_LKG if vid.startswith("lkg") else videos.NAME_C1
    banner = os.path.join(BASE, "img", "name_T.png" if vid.startswith("lkg") else "name_R.png")
    items, missing = [], 0
    last = len(V["scenes"]) - 1
    for k, s in enumerate(V["scenes"]):
        for c, (text, (st, en)) in enumerate(zip(s["subs"], chunk_times(s))):
            png = os.path.join(BASE, "img", "subs", "%s_%02d_%02d.png" % (vid, k + 1, c + 1))
            if os.path.isfile(png):
                items.append((png, st, en - 0.04, "sub"))
            else:
                missing += 1
            if k in (0, last) and name in text and os.path.isfile(banner):
                items.append((banner, st, max(en - 0.04, st + 2.2), "name"))
    if missing:
        print("NOTE: %d subtitle ki tasveer nahi mili (python make_subs.py chalayein)." % missing)
    return items


# ------------------------------------------------------------------ blender helpers
_mats = {}


def mat(color, rough=0.5):
    key = (tuple(round(c, 3) for c in color[:3]), rough)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new("m%d" % len(_mats))
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1)
        b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (color[0], color[1], color[2], 1)
    _mats[key] = m
    return m


def smooth(o):
    try:
        o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))
        o.data.update()
    except Exception:
        pass


def empty(name, parent=None, loc=(0, 0, 0), scale=1.0, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.parent = parent
    e.location = loc
    e.rotation_euler = rot
    e.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
    return e


def prim(kind, p, loc=(0, 0, 0), sc=(1, 1, 1), col=WHITE, rot=(0, 0, 0), rough=0.5):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=1)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(size=2)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=1, depth=2)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=1, depth=2)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25, major_segments=28, minor_segments=10)
    elif kind == "plane":
        bpy.ops.mesh.primitive_plane_add(size=2)
    o = bpy.context.active_object
    o.parent = p
    o.location = loc
    o.scale = sc
    o.rotation_euler = rot
    o.data.materials.append(mat(col, rough))
    if kind in ("sphere", "torus"):
        smooth(o)
    return o


def img_key(s):
    return "_".join("%04x" % ord(c) for c in s)


_gm = {}
PX_EM, CANVAS_H = 400.0, 600.0


def glyph_mat(img, col):
    k = (img.name, tuple(round(c, 3) for c in col))
    if k in _gm:
        return _gm[k]
    m = bpy.data.materials.new("g")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    mul = nt.nodes.new("ShaderNodeMixRGB")
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    mul.inputs[2].default_value = (col[0], col[1], col[2], 1)
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    L = nt.links.new
    L(tex.outputs["Color"], mul.inputs[1])
    L(mul.outputs["Color"], em.inputs["Color"])
    L(tex.outputs["Alpha"], mx.inputs[0])
    L(tr.outputs["BSDF"], mx.inputs[1])
    L(em.outputs["Emission"], mx.inputs[2])
    L(mx.outputs["Shader"], out.inputs["Surface"])
    for attr, val in (("blend_method", "BLEND"), ("shadow_method", "NONE"), ("show_transparent_back", False)):
        try:
            setattr(m, attr, val)
        except Exception:
            pass
    _gm[k] = m
    return m


def glyph_w(body, size):
    """Is akshar/ank ki tasveer ki (kinaare ke khaali hisse samet) chaudai, Blender units mein."""
    path = os.path.join(BASE, "img", img_key(body) + ".png")
    if not os.path.isfile(path):
        return size
    img = bpy.data.images.load(path, check_existing=True)
    return img.size[0] * size / PX_EM


def txt(p, body, size, col, loc, extrude=0.0, max_w=None):
    """Akshar/ank ki tasveer (img/ folder se) rang chadhakar ek plane par lagata hai.
    max_w dene par chaudai us se zyada nahi hoti (chaudi matra wale akshar card se bahar na jaayein)."""
    path = os.path.join(BASE, "img", img_key(body) + ".png")
    if not os.path.isfile(path):
        print("TASVEER NAHI MILI:", body, "-> make_images.py chalayein")
        return empty("missing", p, loc)
    img = bpy.data.images.load(path, check_existing=True)
    w_px, h_px = img.size
    k = size / PX_EM
    if max_w and w_px * k > max_w:
        k = max_w / float(w_px)
    o = prim("plane", p, loc, (w_px * k / 2.0, h_px * k / 2.0, 1), col, rot=(math.pi / 2, 0, 0))
    o.data.materials.clear()
    o.data.materials.append(glyph_mat(img, col))
    return o


@contextlib.contextmanager
def interp(kind):
    ed = bpy.context.preferences.edit
    old = ed.keyframe_new_interpolation_type
    ed.keyframe_new_interpolation_type = kind
    try:
        yield
    finally:
        ed.keyframe_new_interpolation_type = old


TINY = 0.0001


def const_keys(o, path):
    """Is object ke 'path' (scale/location...) ki sab keys ko CONSTANT (jhatke se badlav) kar do."""
    try:
        for fc in o.animation_data.action.fcurves:
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"
    except Exception as e:  # noqa
        print("interpolation set nahi hui:", e)


def popin(o, f, bounce=False):
    s = tuple(o.scale)
    z0 = o.location.z
    o.scale = (s[0] * TINY, s[1] * TINY, s[2] * TINY)
    o.keyframe_insert("scale", frame=1)
    o.keyframe_insert("scale", frame=max(1, f - 1))
    o.scale = (s[0] * 1.18, s[1] * 1.18, s[2] * 1.18)
    o.keyframe_insert("scale", frame=f + 3)
    o.scale = s
    o.keyframe_insert("scale", frame=f + 6)
    if bounce:
        o.location.z = z0
        o.keyframe_insert("location", index=2, frame=max(1, f - 1))
        o.location.z = z0 + 0.7
        o.keyframe_insert("location", index=2, frame=f + 2)
        o.location.z = z0
        o.keyframe_insert("location", index=2, frame=f + 5)
        o.location.z = z0 + 0.2
        o.keyframe_insert("location", index=2, frame=f + 7)
        o.location.z = z0
        o.keyframe_insert("location", index=2, frame=f + 9)


def sway(o, f0, f1, amp=0.3, period=24):
    rz = o.rotation_euler.z
    f = f0
    i = 0
    vals = [0, amp, 0, -amp]
    while f <= f1:
        o.rotation_euler.z = rz + vals[i % 4]
        o.keyframe_insert("rotation_euler", index=2, frame=f)
        f += period // 4
        i += 1
    o.rotation_euler.z = rz


# ------------------------------------------------------------------ objects  (bottom z=0, ~2 units tall)
def obj_anar(p):
    prim("sphere", p, (0, 0, 0.85), (0.9, 0.9, 0.85), (0.80, 0.07, 0.10), rough=0.35)
    prim("cyl", p, (0, 0, 1.68), (0.26, 0.26, 0.07), (0.55, 0.05, 0.08))
    for dx, dy in ((0.15, 0), (-0.15, 0), (0, 0.15), (0, -0.15)):
        prim("cone", p, (dx, dy, 1.82), (0.09, 0.09, 0.16), (0.65, 0.06, 0.08))
    prim("sphere", p, (-0.42, -0.62, 1.2), (0.16, 0.08, 0.26), (1, 0.75, 0.75), rot=(0, -0.5, 0), rough=0.2)


def obj_aam(p):
    r = empty("aam", p, rot=(0, 0.35, 0))
    prim("sphere", r, (0, 0, 1.0), (0.75, 0.62, 1.0), (1.0, 0.76, 0.08), rough=0.4)
    prim("sphere", r, (0.2, 0, 1.55), (0.42, 0.45, 0.5), (0.95, 0.62, 0.05), rough=0.4)
    prim("cyl", r, (0.05, 0, 2.05), (0.05, 0.05, 0.14), BROWN)
    prim("sphere", r, (0.42, 0, 2.12), (0.42, 0.05, 0.16), (0.15, 0.6, 0.15), rot=(0, -0.35, 0))


def obj_imli(p):
    r = empty("imli", p, rot=(0, 0.25, 0))
    for x, z in ((-0.95, 0.40), (-0.35, 0.58), (0.30, 0.62), (0.92, 0.46)):
        prim("sphere", r, (x, 0, z + 0.2), (0.42, 0.36, 0.38), (0.50, 0.28, 0.12), rough=0.7)
    prim("cyl", r, (-1.35, 0, 0.55), (0.05, 0.05, 0.22), BROWN, rot=(0, 1.2, 0))


def obj_eekh(p):
    r = empty("eekh", p, rot=(0, 0.12, 0))
    cols = [(0.42, 0.13, 0.48), (0.30, 0.09, 0.36), (0.42, 0.13, 0.48)]
    for i in range(3):
        prim("cyl", r, (0, 0, 0.5 + i), (0.24, 0.24, 0.5), cols[i], rough=0.4)
        if i < 2:
            prim("cyl", r, (0, 0, 1.0 + i), (0.3, 0.3, 0.04), (0.75, 0.85, 0.45))
    for a in (0, 2.1, 4.2):
        prim("cone", r, (0.35 * math.sin(a), 0.35 * math.cos(a), 3.2), (0.1, 0.1, 0.7), (0.2, 0.65, 0.2),
             rot=(0.7 * math.cos(a), -0.7 * math.sin(a), 0))
    r.scale = (0.8, 0.8, 0.8)


def obj_ullu(p):
    prim("sphere", p, (0, 0, 1.0), (0.85, 0.65, 1.0), BROWN)
    prim("sphere", p, (0, -0.45, 0.9), (0.55, 0.3, 0.7), CREAM)
    for sx in (-1, 1):
        prim("sphere", p, (sx * 0.38, -0.5, 1.55), (0.38, 0.2, 0.38), WHITE)
        prim("sphere", p, (sx * 0.38, -0.66, 1.55), (0.17, 0.1, 0.17), (0.05, 0.05, 0.08))
        prim("cone", p, (sx * 0.5, 0, 2.05), (0.18, 0.18, 0.3), (0.4, 0.23, 0.1), rot=(0, sx * 0.4, 0))
        prim("sphere", p, (sx * 0.88, 0.05, 0.95), (0.2, 0.45, 0.7), (0.38, 0.22, 0.1))
        prim("sphere", p, (sx * 0.3, -0.35, 0.06), (0.22, 0.3, 0.06), (1.0, 0.55, 0.1))
    prim("cone", p, (0, -0.85, 1.3), (0.13, 0.13, 0.2), (1.0, 0.55, 0.1), rot=(math.pi / 2, 0, 0))


def obj_ball(p, col=None):
    col = col or videos.RED
    prim("sphere", p, (0, 0, 0.5), (0.5, 0.5, 0.5), col, rough=0.25)
    prim("cyl", p, (0, 0, 0.5), (0.505, 0.505, 0.09), WHITE, rot=(0.35, 0, 0), rough=0.3)


def obj_ball_blue(p):
    obj_ball(p, videos.BLUE)
    p.scale = (1.5, 1.5, 1.5)


def obj_patta(p):
    prim("cyl", p, (0, 0, 0.35), (0.06, 0.06, 0.4), (0.35, 0.22, 0.08))
    for ang in (-0.45, 0.45):
        r = empty("leaf", p, (0, 0, 0.6), rot=(0, ang, 0))
        prim("sphere", r, (0, 0, 0.95), (0.6, 0.07, 1.0), (0.15, 0.65, 0.2))
        prim("cube", r, (0, -0.07, 0.95), (0.03, 0.03, 0.9), (0.08, 0.4, 0.1))


def obj_sun(p):
    prim("sphere", p, (0, 0, 1.3), (0.9, 0.5, 0.9), (1.0, 0.8, 0.05), rough=0.3)
    for i in range(10):
        a = i * 2 * math.pi / 10
        prim("cone", p, (1.3 * math.sin(a), -0.1, 1.3 + 1.3 * math.cos(a)), (0.16, 0.1, 0.34),
             (1.0, 0.55, 0.05), rot=(0, a, 0))
    for sx in (-1, 1):
        prim("sphere", p, (sx * 0.33, -0.5, 1.5), (0.1, 0.06, 0.13), DARK)
    prim("torus", p, (0, -0.5, 1.1), (0.3, 0.3, 0.3), (0.8, 0.25, 0.1), rot=(math.pi / 2, 0, 0)).scale = (0.3, 0.3, 0.3)


def obj_egg(p):
    prim("sphere", p, (0, 0, 0.98), (0.72, 0.72, 0.98), (0.98, 0.95, 0.88), rough=0.35)
    prim("cyl", p, (0, 0, 0.04), (0.8, 0.8, 0.04), (0.9, 0.6, 0.3))


def obj_cup(p):
    prim("cyl", p, (0, 0, 0.06), (1.15, 1.15, 0.06), WHITE)
    prim("cyl", p, (0, 0, 0.7), (0.75, 0.75, 0.6), (0.15, 0.4, 0.9), rough=0.25)
    prim("cyl", p, (0, 0, 1.28), (0.66, 0.66, 0.02), (0.98, 0.98, 0.95))
    t = prim("torus", p, (0.8, 0, 0.7), (0.4, 0.4, 0.4), (0.15, 0.4, 0.9), rot=(math.pi / 2, 0, 0))


def obj_hat(p):
    prim("cyl", p, (0, 0, 0.08), (1.25, 1.25, 0.08), (0.85, 0.12, 0.15))
    prim("cyl", p, (0, 0, 0.68), (0.72, 0.72, 0.6), (0.85, 0.12, 0.15))
    prim("cyl", p, (0, 0, 0.42), (0.74, 0.74, 0.1), (1.0, 0.8, 0.1))


OBJ = {"anar": obj_anar, "aam": obj_aam, "imli": obj_imli, "eekh": obj_eekh, "ullu": obj_ullu,
       "ball": obj_ball, "ball_blue": obj_ball_blue, "patta": obj_patta, "sun": obj_sun,
       "egg": obj_egg, "cup": obj_cup, "hat": obj_hat}


def place_obj(parent, name, loc, scale, f, bounce=False, sway_to=None, color=None):
    r = empty("o_" + name, parent, loc, scale)
    if name == "ball" and color:
        obj_ball(r, color)
    else:
        OBJ[name](r)
    popin(r, f, bounce)
    if sway_to:
        sway(r, f + 8, sway_to)
    return r


def panel(p, loc, w, h, border, f=None):
    a = prim("cube", p, loc, (w + 0.14, 0.10, h + 0.14), border)
    b = prim("cube", p, (loc[0], loc[1] - 0.05, loc[2]), (w, 0.10, h), WHITE)
    if f is not None:
        popin(a, f)
        popin(b, f)


# ------------------------------------------------------------------ stage + bear
def build_stage(V, scn):
    w = bpy.data.worlds.new("W")
    scn.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (1, 1, 1, 1)
    bg.inputs[1].default_value = 0.35
    st = empty("stage")
    bgc, fl = V["bg"], V["floor"]
    prim("plane", st, (0, 5, 4), (18, 6, 1), bgc, rot=(math.pi / 2, 0, 0), rough=0.9)
    prim("plane", st, (0, 4.98, 0.9), (18, 0.9, 1), tuple(c * 0.82 for c in bgc), rot=(math.pi / 2, 0, 0), rough=0.9)
    prim("plane", st, (0, 0, 0), (18, 12, 1), fl, rough=0.8)
    prim("cyl", st, (1.6, -0.4, 0.015), (4.6, 2.3, 0.015), tuple(min(1, c * 1.15 + 0.05) for c in fl), rough=0.9)
    # wall ki sajaawat (bade pastel gole)
    for x, z, r, k in ((-6.5, 5.2, 0.9, 0), (5.8, 5.6, 0.7, 2), (2.0, 5.9, 0.5, 3)):
        prim("cyl", st, (x, 4.9, z), (r, r, 0.03), PALETTE[k], rot=(math.pi / 2, 0, 0)).data.materials[0] = mat(
            tuple(min(1, c * 0.35 + 0.65) for c in PALETTE[k]), 0.9)
    ld = bpy.data.lights.new("sun", "SUN")
    ld.energy = 1.8
    ld.angle = math.radians(12)
    lo = bpy.data.objects.new("sun", ld)
    scn.collection.objects.link(lo)
    lo.rotation_euler = (math.radians(52), 0, math.radians(-28))
    cd = bpy.data.cameras.new("cam")
    cd.lens = 35
    co = bpy.data.objects.new("cam", cd)
    scn.collection.objects.link(co)
    co.location = (0.0, -11.0, 3.4)
    tg = empty("target", None, (0, 0, 2.3))
    c = co.constraints.new("TRACK_TO")
    c.target = tg
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    scn.camera = co


def build_bear():
    root = empty("bear", None, (-3.9, -0.3, 0), 0.88)
    fur, belly, pink, dark = BROWN, CREAM, (0.95, 0.55, 0.6), (0.08, 0.05, 0.05)
    prim("sphere", root, (0, 0, 1.25), (0.95, 0.75, 1.15), fur)
    prim("sphere", root, (0, -0.55, 1.2), (0.65, 0.3, 0.85), belly)
    prim("torus", root, (0, 0, 2.3), (0.8, 0.7, 0.8), (0.85, 0.12, 0.15))
    head = empty("head", root, (0, 0, 2.9))
    prim("sphere", head, (0, 0, 0), (0.9, 0.85, 0.85), fur)
    for sx in (-1, 1):
        prim("sphere", head, (sx * 0.66, 0, 0.7), (0.3, 0.2, 0.3), fur)
        prim("sphere", head, (sx * 0.66, -0.12, 0.7), (0.17, 0.1, 0.17), pink)
    prim("sphere", head, (0, -0.68, -0.18), (0.45, 0.32, 0.32), belly)
    prim("sphere", head, (0, -0.96, -0.02), (0.15, 0.1, 0.1), dark)
    eyes = empty("eyes", head, (0, -0.72, 0.2))
    for sx in (-1, 1):
        prim("sphere", eyes, (sx * 0.32, 0, 0), (0.17, 0.1, 0.19), WHITE)
        prim("sphere", eyes, (sx * 0.32, -0.08, 0), (0.09, 0.06, 0.11), dark)
    mouth = prim("sphere", head, (0, -0.97, -0.3), (0.17, 0.05, 0.03), (0.35, 0.05, 0.08))
    for sx in (-1, 1):
        prim("sphere", root, (sx * 0.5, -0.15, 0.3), (0.38, 0.5, 0.3), fur)
    arm_l = empty("arm_l", root, (-1.0, 0, 1.9), rot=(0, 0.15, 0))
    prim("sphere", arm_l, (0, 0, -0.5), (0.28, 0.28, 0.65), fur)
    arm_r = empty("arm_r", root, (1.0, 0, 1.9), rot=(0, -0.15, 0))
    prim("sphere", arm_r, (0, 0, -0.5), (0.28, 0.28, 0.65), fur)
    return root, mouth, eyes, arm_r


# ------------------------------------------------------------------ visuals
def vis_row(R, items, fs, fb):
    n = len(items)
    size = min(2.6, 10.2 / n)
    total = sum(glyph_w(ch, size) for ch in items)
    if total > 7.6:                      # kul chaudai kam rakhne ke liye sab ko ek saath chhota karo
        size *= 7.6 / total
    widths = [glyph_w(ch, size) for ch in items]
    x = CX - sum(widths) / 2.0
    for i, ch in enumerate(items):
        col = PALETTE[i % 5] if ch not in ("+", "=") else DARK
        o = txt(R, ch, size, col, (x + widths[i] / 2.0, -0.3, 2.7))
        x += widths[i]
        popin(o, fs + 4 + int((fb - fs) * 0.6 * i / max(n, 1)))
        sway(o, fs + 12, fb, 0.12, 24)


def vis_letter(R, text, obj, fs, fb, color, word=False):
    if word:
        # rang wale scene: Hindi shabd ki jagah rang ka bada dabba (Blender Hindi jodakshar/matra nahi jodta)
        a = prim("cube", R, (-0.2, 0, 1.75), (1.55, 0.10, 1.6), WHITE)
        b = prim("cube", R, (-0.2, -0.06, 1.75), (1.3, 0.10, 1.35), color, rough=0.3)
        popin(a, fs + 1)
        popin(b, fs + 3)
    else:
        panel(R, (-0.2, 0, 1.75), 1.35, 1.6, color, fs + 1)
        t = txt(R, text, 3.1, color, (-0.2, -0.24, 1.75), max_w=3.0)
        popin(t, fs + 3)
    place_obj(R, obj, (3.5, -0.2, 0.05), 1.35, fs + 12, bounce=True, sway_to=fb)


def vis_recap(R, pairs, fs, fb):
    n = len(pairs)
    for i, (ch, ob) in enumerate(pairs):
        x = CX + (i - (n - 1) / 2.0) * 1.6
        f = fs + 3 + int((fb - fs) * 0.7 * i / n)
        t = txt(R, ch, 1.4, PALETTE[i % 5], (x, -0.3, 2.7))
        popin(t, f)
        place_obj(R, ob, (x, -0.2, 0.05), 0.5, f + 2, bounce=True)


def vis_seq(R, a, b, ob, fs, fb, labels, big):
    n = b
    cols = 5 if n > 5 else n
    sp = 1.45 if n <= 5 else 1.4
    if big:
        t = txt(R, str(n), 2.8, PALETTE[(n - 1) % 5], (CX, -0.3, 3.8))
        popin(t, fs + 2)
    for i in range(n):
        r, c = (0, i) if n <= 5 else (i // 5, i % 5)
        cnt = cols if n <= 5 else min(5, n - r * 5)
        x = CX + (c - (cnt - 1) / 2.0) * sp
        z = 0.45 if n <= 5 else (0.45 + (1 - r) * 2.1)
        f = fs + 6 + int((fb - fs) * 0.62 * i / max(n, 1)) + (0 if not big else int((fb - fs) * 0.15))
        place_obj(R, ob, (x, -0.2, z), 1.0, f, bounce=True, color=PALETTE[i % 5])
        if labels:
            lt = txt(R, str(i + 1), 0.85, PALETTE[i % 5], (x, -0.3, z + 1.35))
            popin(lt, f + 1)


def vis_quiz(R, items, hi, fs, fb):
    n = len(items)
    sp = min(1.7, 7.9 / n)
    for i, ch in enumerate(items):
        x = CX + (i - (n - 1) / 2.0) * sp
        border = videos.GREEN if i == hi else (videos.ORANGE if ch == "?" else videos.BLUE)
        panel(R, (x, 0, 2.2), 0.6, 0.8, border, fs + 1 + 2 * i)
        t = txt(R, ch, 1.15, border if ch in ("?",) or i == hi else DARK, (x, -0.24, 2.2))
        popin(t, fs + 2 + 2 * i, bounce=(ch == "?" or i == hi))


def vis_sum(R, a, b, fs, fb, hide):
    span = fb - fs
    sp = 1.5
    xs = [CX + (i - 2) * sp for i in range(5)]
    syms = [(str(a), videos.RED, 0.15), ("+", DARK, 0.45), (str(b), videos.BLUE, 0.5), ("=", DARK, 0.78),
            ("?" if hide else str(a + b), videos.GREEN if not hide else videos.ORANGE, 0.86)]
    for x, (s, c, fr_) in zip(xs, syms):
        t = txt(R, s, 1.5, c, (x, -0.3, 3.9))
        popin(t, fs + 3 + int(span * fr_), bounce=(s == "?"))
    n = a + b
    xb = CX - (n - 1) * 0.45 - 0.2
    for i in range(n):
        grp = 0 if i < a else 1
        x = xb + i * 0.9 + (0.4 if grp else 0)
        f = fs + 4 + int(span * ((0.15 + 0.2 * i / max(a, 1)) if grp == 0 else (0.5 + 0.2 * (i - a) / max(b, 1))))
        place_obj(R, "ball", (x, -0.2, 0.8), 0.78, f, bounce=True, color=videos.RED if grp == 0 else videos.BLUE)


def vis_word(R, word, obj, fs, fb):
    cols = [videos.RED, videos.BLUE, videos.GREEN]
    for i, ch in enumerate(word):
        t = txt(R, ch, 2.2, cols[i], (CX + (i - 1) * 1.9, -0.3, 4.0))
        popin(t, fs + 3 + int((fb - fs) * 0.14 * i * 2))
    place_obj(R, obj, (CX, -0.2, 0.05), 1.15, fs + int((fb - fs) * 0.5), bounce=True, sway_to=fb)


def vis_only(R, obj, fs, fb):
    place_obj(R, obj, (2.0, -0.2, 0.05), 1.5, fs + 4, bounce=True, sway_to=fb)
    t = txt(R, "?", 2.6, videos.ORANGE, (-0.6, -0.3, 3.0))
    popin(t, fs + 8, bounce=True)


def vis_balls(R, cols, fs, fb):
    n = len(cols)
    for i, c in enumerate(cols):
        place_obj(R, "ball", (CX + (i - (n - 1) / 2.0) * 1.6, -0.2, 0.9), 1.3,
                  fs + 4 + int((fb - fs) * 0.5 * i / n), bounce=True, color=c)


def build_visual(k, s, fs, fb, fe, scn):
    R = empty("S%02d" % (k + 1))
    v = s["vis"]
    if "row" in v:
        vis_row(R, v["row"], fs, fb)
    elif "letter" in v:
        vis_letter(R, v["letter"], v["obj"], fs, fb, PALETTE[(k - 1) % 5])
    elif "colorword" in v:
        vis_letter(R, v["colorword"], v["obj"], fs, fb, v["color"], word=True)
    elif "recap" in v:
        vis_recap(R, v["recap"], fs, fb)
    elif "seq" in v:
        vis_seq(R, v["seq"][0], v["seq"][1], v["obj"], fs, fb, v.get("labels", False), v.get("big", False))
    elif "quiz" in v:
        vis_quiz(R, v["quiz"], v.get("hi", -1), fs, fb)
    elif "sum" in v:
        vis_sum(R, v["sum"][0], v["sum"][1], fs, fb, v.get("hide_result", False))
    elif "word" in v:
        vis_word(R, v["word"], v["obj"], fs, fb)
    elif "only" in v:
        vis_only(R, v["only"], fs, fb)
    elif "balls" in v:
        vis_balls(R, v["balls"], fs, fb)
    # scene ko apni jagah par dikhana / baad mein chhupana
    with interp("CONSTANT"):
        R.scale = (TINY,) * 3
        R.keyframe_insert("scale", frame=1)
        R.scale = (1, 1, 1)
        R.keyframe_insert("scale", frame=fs)
        R.scale = (TINY,) * 3
        R.keyframe_insert("scale", frame=fe)
    const_keys(R, "scale")
    return R


def animate_bear(bear, mouth, eyes, arm_r, scenes, N):
    random.seed(11)
    with interp("BEZIER"):
        f = 1
        up = False
        while f < N:
            bear.location.z = 0.06 if up else 0.0
            bear.keyframe_insert("location", index=2, frame=f)
            up = not up
            f += 6
        f = 30
        while f < N:
            for ff, val in ((f - 1, 1.0), (f + 1, 0.1), (f + 3, 1.0)):
                eyes.scale.z = val
                eyes.keyframe_insert("scale", index=2, frame=ff)
            f += random.randint(40, 70)
    with interp("CONSTANT"):
        mouth.scale.z = 0.03
        mouth.keyframe_insert("scale", index=2, frame=1)
        for s in scenes:
            fa, fb = fr(s["t0"]), fr(s["t0"] + s["adur"])
            env = s.get("env")
            if env:
                last = None
                for j, v in enumerate(env):
                    f = fa + j
                    if f >= fb:
                        break
                    if v < 0.18:
                        z = 0.03
                    elif v < 0.45:
                        z = random.choice([0.06, 0.08])
                    elif v < 0.75:
                        z = random.choice([0.10, 0.13])
                    else:
                        z = random.choice([0.15, 0.17])
                    if z != last:
                        mouth.scale.z = z
                        mouth.keyframe_insert("scale", index=2, frame=f)
                        last = z
            else:
                f = fa
                while f < fb:
                    mouth.scale.z = random.choice([0.04, 0.08, 0.13, 0.16, 0.06])
                    mouth.keyframe_insert("scale", index=2, frame=f)
                    f += 2
            mouth.scale.z = 0.03
            mouth.keyframe_insert("scale", index=2, frame=fb)
    const_keys(mouth, "scale")
    with interp("BEZIER"):
        arm_r.rotation_euler.y = -0.15
        arm_r.keyframe_insert("rotation_euler", index=1, frame=1)
        for s in scenes:
            if not s.get("wave"):
                continue
            fa, fb = fr(s["t0"]) + 3, fr(s["t0"] + s["adur"])
            arm_r.rotation_euler.y = -0.15
            arm_r.keyframe_insert("rotation_euler", index=1, frame=fa - 1)
            f, hi = fa, True
            while f < fb:
                arm_r.rotation_euler.y = -2.35 if hi else -2.75
                arm_r.keyframe_insert("rotation_euler", index=1, frame=f)
                hi = not hi
                f += 3
            arm_r.rotation_euler.y = -0.15
            arm_r.keyframe_insert("rotation_euler", index=1, frame=fb + 3)


# ------------------------------------------------------------------ render setup
def setup_render(scn, opts, N, vid, outdir):
    r = scn.render
    r.fps = FPS
    r.fps_base = 1
    global RES
    RES = (640, 360) if "draft" in opts else (1280, 720)
    r.resolution_x, r.resolution_y = RES
    r.resolution_percentage = 100
    scn.frame_start, scn.frame_end = 1, N
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.use_overwrite = False
    r.use_placeholder = False
    try:
        scn.view_settings.view_transform = "Standard"
    except Exception:
        pass
    if "workbench" in opts:
        r.engine = "BLENDER_WORKBENCH"
        sh = scn.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        try:
            sh.show_shadows = True
            scn.display.render_aa = "8"
        except Exception:
            pass
    elif "cycles" in opts:
        r.engine = "CYCLES"
        scn.cycles.samples = 24
        scn.cycles.device = "CPU"
        try:
            scn.cycles.use_denoising = False
        except Exception:
            pass
    else:
        for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
            try:
                r.engine = e
                break
            except Exception:
                continue
        for attr, val in (("taa_render_samples", 16), ("use_gtao", False), ("use_ssr", False),
                          ("use_soft_shadows", True), ("use_bloom", False)):
            try:
                setattr(scn.eevee, attr, val)
            except Exception:
                pass


def sync_frames(frames_dir, sig):
    """Agar timing (awaaz/frames) badli hai to purane frames hata do, warna naye video mein purani tasveerein mil jaayengi."""
    os.makedirs(frames_dir, exist_ok=True)
    mark = os.path.join(frames_dir, "_timing.txt")
    old = None
    if os.path.isfile(mark):
        with open(mark, encoding="utf-8") as f:
            old = f.read()
    if old != sig:
        gone = 0
        for fn in glob.glob(os.path.join(frames_dir, "*.png")):
            try:
                os.remove(fn)
                gone += 1
            except Exception:
                pass
        if gone:
            print("\nTiming badli hai (nayi awaaz / naya text), isliye %d purane frames hata diye." % gone)
        with open(mark, "w", encoding="utf-8") as f:
            f.write(sig)


def mux(vid, outdir, N, full_wav, name=None, overlays=None):
    frames_dir = os.path.join(outdir, "frames")
    missing = [i for i in range(1, N + 1) if not os.path.isfile(os.path.join(frames_dir, "%04d.png" % i))]
    if missing:
        print("\nmp4 nahi bana: %d frames abhi baaki hain (pehla: %04d.png). Render dobara chalayein,"
              " woh sirf baaki frames banayega." % (len(missing), missing[0]))
        return None
    ms = bpy.data.scenes.new("mux_" + (name or vid))
    # naye scene mein Blender 'Filmic' lagata hai jisse video fika/dhundhla dikhta hai; asli rang ke liye Standard
    try:
        ms.view_settings.view_transform = "Standard"
        ms.view_settings.look = "None"
        ms.view_settings.exposure = 0.0
        ms.view_settings.gamma = 1.0
    except Exception:
        pass
    r = ms.render
    r.fps, r.fps_base = FPS, 1
    r.resolution_x, r.resolution_y = RES
    r.resolution_percentage = 100
    ms.frame_start, ms.frame_end = 1, N
    r.use_sequencer = True
    ms.sequence_editor_create()
    se = ms.sequence_editor
    seqs = se.strips if hasattr(se, "strips") else se.sequences
    st = seqs.new_image("frames", filepath=os.path.join(frames_dir, "0001.png"), channel=1, frame_start=1)
    for i in range(2, N + 1):
        st.elements.append("%04d.png" % i)
    if full_wav:
        try:
            seqs.new_sound("audio", filepath=full_wav, channel=2, frame_start=1)
        except Exception as e:  # noqa
            print("\nNOTE: Blender awaaz nahi jod paya (%s)." % e)
            print("      mp4 bina awaaz ke banega. CapCut mein full.wav alag se daal dein (dono barabar lambai ke hain).")
    for oi, (png, ts, te, kind) in enumerate(overlays or []):
        try:
            fs = int(round(ts * FPS)) + 1
            fe = min(N + 1, int(round(te * FPS)) + 1)
            if fe <= fs:
                continue
            o = seqs.new_image("ov%d" % oi, filepath=png, channel=3 if kind == "sub" else 4, frame_start=fs)
            o.frame_final_duration = fe - fs
            o.blend_type = "ALPHA_OVER"
            try:
                o.alpha_mode = "STRAIGHT"
            except Exception:
                pass
            if kind == "name":
                try:
                    o.blend_alpha = 0.0
                    o.keyframe_insert("blend_alpha", frame=fs)
                    o.blend_alpha = 1.0
                    o.keyframe_insert("blend_alpha", frame=fs + 3)
                    o.transform.offset_y = -50
                    o.transform.keyframe_insert("offset_y", frame=fs)
                    o.transform.offset_y = 0
                    o.transform.keyframe_insert("offset_y", frame=fs + 4)
                except Exception as e2:  # noqa
                    o.transform.offset_y = 0
                    o.blend_alpha = 1.0
                    print("NOTE: naam-patti ka halka animation nahi laga (%s)" % e2)
        except Exception as e:  # noqa
            print("NOTE: overlay nahi laga (%s)" % e)
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "MEDIUM"
    r.ffmpeg.audio_codec = "AAC"
    r.ffmpeg.audio_bitrate = 128
    out = os.path.join(outdir, name or vid)
    r.filepath = out
    bpy.ops.render.render(animation=True, scene=ms.name)
    # Blender naam mein frame range jod deta hai (jaise lkg10001-0663.mp4); saaf naam rakh do
    final = out + ".mp4"
    for f in glob.glob(out + "[0-9]*.mp4"):
        if os.path.abspath(f) != os.path.abspath(final):
            try:
                if os.path.exists(final):
                    os.remove(final)
                os.replace(f, final)
            except Exception as e:  # noqa
                final = f
    return final


# ------------------------------------------------------------------ main
def main():
    vid, opts = parse_args()
    V = videos.VIDEOS[vid]
    outdir = os.path.join(BASE, vid)
    os.makedirs(outdir, exist_ok=True)
    random.seed(5)

    exact, paths, params, total = make_timeline(vid, V, outdir)
    N = int(math.ceil(total * FPS))
    srt = write_srt(outdir, vid, V["scenes"])
    full = write_full_wav(outdir, V["scenes"], paths, params) if exact else None

    print("\n=== %s ===" % V["title"])
    print("Lambai: %.1f sec  |  Frames: %d (%d fps)  |  Audio: %s" % (
        total, N, FPS, "ASLI" if exact else "ANDAZA (estimate)"))
    print("Subtitles:", srt)
    for k, s in enumerate(V["scenes"]):
        print("  scene%02d: frame %d se %d" % (k + 1, fr(s["t0"]), fr(s["t0"] + s["dur"])))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    build_stage(V, scn)
    bear, mouth, eyes, arm_r = build_bear()
    for k, s in enumerate(V["scenes"]):
        fs, fb, fe = fr(s["t0"]), fr(s["t0"] + s["adur"]), fr(s["t0"] + s["dur"])
        build_visual(k, s, fs, fb, fe, scn)
    animate_bear(bear, mouth, eyes, arm_r, V["scenes"], N)
    setup_render(scn, opts, N, vid, outdir)

    blend = os.path.join(outdir, vid + ".blend")
    try:
        bpy.ops.wm.save_as_mainfile(filepath=blend)
        print("Blend file:", blend)
    except Exception as e:  # noqa
        print("Blend save nahi hua:", e)
    if "build" in opts:
        return

    frames_dir = os.path.join(outdir, "frames")
    if "test" in opts:
        mid = max(1, N // 2)
        for o in opts:
            if o.startswith("frame"):
                mid = int(o[5:])
        scn.frame_start, scn.frame_end = mid, min(N, mid + 2)
        td = os.path.join(outdir, "test")
        os.makedirs(td, exist_ok=True)
        scn.render.filepath = td + os.sep
        scn.render.use_overwrite = True
        t0 = time.time()
        bpy.ops.render.render(animation=True)
        per = (time.time() - t0) / 3.0
        print("\nTEST RENDER pura. Test frames:", td)
        print("Ek frame ka time: %.1f sec  ->  poore %d frames ke liye lagbhag %.1f ghante" % (
            per, N, per * N / 3600.0))
        return
    sig = "%d|%s|%s" % (N, "exact-lip2" if exact else "estimate", ",".join("%.2f" % x["adur"] for x in V["scenes"]))
    sync_frames(frames_dir, sig)
    scn.render.filepath = frames_dir + os.sep
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    print("\nRender ka time: %.1f minute" % ((time.time() - t0) / 60.0))
    ov = build_overlays(vid, V) if "nosubs" not in opts else None
    mp4 = mux(vid, outdir, N, full, None if exact else vid + "_preview", ov)
    if mp4:
        print("\nTAIYAR VIDEO (subtitle + naam ke saath):", mp4)
        if ov:
            clean = mux(vid, outdir, N, full, (vid + "_clean") if exact else vid + "_preview_clean", None)
            if clean:
                print("TAIYAR VIDEO (bina subtitle, CapCut ke liye):", clean)
    if not exact:
        print("\n*** DHYAN: %s ki awaaz (scene wav files) nahi thi. Ye sirf PREVIEW hai (%s_preview.mp4)," % (vid, vid))
        print("*** timing andaze ki hai. Awaaz banane ke baad render dobara chalayein, purane frames khud hat jaayenge.")


main()
