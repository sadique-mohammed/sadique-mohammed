#!/usr/bin/env python3
"""Turn a photo into ascii.svg — a self-typing, monochrome ASCII portrait.

Adapted from andriidrok1's original script. The only change: background
removal uses OpenCV's GrabCut instead of `rembg`, because rembg needs to
download a ~176 MB model from the internet on first run, and that isn't
always available. GrabCut is classical computer vision (no model download,
runs anywhere Python + OpenCV run) — the cutout is a little rougher around
stray hair and glasses edges than rembg's, but for a plain, evenly lit
background it holds up fine.

If you have internet access on your own machine later and want the cleaner
cutout, swap `prep()` below back to `rembg.remove()` — the rest of the file
(ramp, curve, SVG builder) is untouched from the original.

    pip install pillow numpy opencv-python-headless
    python3 scripts/make_portrait.py photo.jpg --crop 40,20,760,780
    python3 scripts/embed_portrait_font.py

Two things decide whether the output is any good, and neither is a parameter:

  * The photo. ASCII draws with shadow, not detail — about 13 brightness levels
    in total. You need a tight crop from chin to just above the hair, and real
    resolution. A 320px headshot fails: thin features like glasses frames are
    averaged away on downscale. Flat frontal light renders the face as a hole.
  * The darkening curve below. Without it the face comes out washed out and
    featureless — brows, glasses and lips all dissolve.

The grid bakes in an advance width of exactly 0.600 em (CHAR_W / FONT_SIZE), so
after generating, run scripts/embed_portrait_font.py to inline JetBrains Mono.
Otherwise a viewer whose default monospace is narrower — Consolas is ≈0.55 —
sees the portrait about 7% too narrow.

Motion is SMIL, because GitHub strips <script> from READMEs: each row is
revealed by a clipPath wipe with a cursor block riding its edge, staggered top
to bottom, frozen at the end so it prints once and stops.
"""
import argparse
import sys

import cv2
import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"     # bright/sparse -> dark/dense; leading space = blank
COLS = 90                  # below ~88 the face muddies; far above it dominates
CLAHE_CLIP = 3.0           # higher amplifies skin texture into noise
GAMMA = 1.0                # ramp mapping exponent
CURVE = 1.7                # the darkening curve — the difference-maker
CROP_BOTTOM = 0.0          # fraction to trim off the bottom (torso, chair)
ROW_RATIO = 0.48           # monospace cells are about twice as tall as wide
GRABCUT_MARGIN = 0.06      # fraction of width/height kept as certain background

FG_LIGHT = "#6e7681"       # readable on GitHub light — the portrait's grey
FG_DARK = "#c9d1d9"        # and its dark-mode step
CHAR_W = 7.74              # 0.600 em at FONT_SIZE — keep these in step
FONT_SIZE = 12.9
LINE_H = 15
ROW_DELAY = 0.09           # per-row stagger, seconds
FAMILY = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def prep(path, crop=None, bg_threshold=None):
    """Cut out the background, even the local contrast, then darken.

    Two matting strategies, picked automatically:
      * a plain, evenly bright backdrop (the common case for a portrait/
        headshot) -> a brightness threshold, flood-filled from the corners
        so it only removes background connected to the edges, not bright
        skin or shirt patches in the middle of the frame;
      * anything else -> GrabCut, seeded from a border-margin rectangle.
    Pass --bg-threshold to force the brightness path with a specific cutoff.
    """
    src = Image.open(path).convert("RGB")
    if crop:
        src = src.crop(crop)

    bgr = cv2.cvtColor(np.array(src), cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]
    gray0 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    corner = 12
    corners = np.concatenate([
        gray0[:corner, :corner].ravel(), gray0[:corner, -corner:].ravel(),
        gray0[-corner:, :corner].ravel(), gray0[-corner:, -corner:].ravel(),
    ])
    plain_backdrop = bg_threshold or (corners.mean() > 200 and corners.std() < 20)

    if plain_backdrop:
        thresh = bg_threshold if isinstance(bg_threshold, (int, float)) else 220
        bright = (gray0 >= thresh).astype("uint8") * 255
        flood = bright.copy()
        ff_mask = np.zeros((h + 2, w + 2), np.uint8)
        for seed in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
            if flood[seed[1], seed[0]] == 255:
                cv2.floodFill(flood, ff_mask, seed, 128)
        fg = np.where(flood == 128, 0, 255).astype("uint8")
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    else:
        mask = np.zeros((h, w), np.uint8)
        mx, my = int(w * GRABCUT_MARGIN), int(h * GRABCUT_MARGIN)
        rect = (mx, my, w - 2 * mx, h - 2 * my)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(bgr, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

    gray = gray0
    gray = cv2.bilateralFilter(gray, 11, 50, 50)      # smooth skin, keep edges
    gray = cv2.createCLAHE(clipLimit=CLAHE_CLIP,
                           tileGridSize=(8, 8)).apply(gray)
    gray = (255.0 * (gray / 255.0) ** CURVE).astype("uint8")
    gray[fg < 20] = 255                               # force the matte to white
    return Image.fromarray(gray)


def to_lines(img, cols=COLS, gamma=GAMMA):
    w, h = img.size
    if CROP_BOTTOM:
        img = img.crop((0, 0, w, int(h * (1 - CROP_BOTTOM))))
        w, h = img.size

    rows = int(cols * (h / w) * ROW_RATIO)
    img = img.resize((cols, rows), Image.LANCZOS)
    px = list(img.getdata())
    n = len(RAMP)

    out = []
    for r in range(rows):
        out.append("".join(
            RAMP[min(n - 1, int((1 - px[r * cols + c] / 255.0) ** gamma * n))]
            for c in range(cols)
        ).rstrip())

    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def build_svg(lines, cols=COLS):
    pad = 14
    width = int(cols * CHAR_W + pad * 2)
    height = len(lines) * LINE_H + pad * 2

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
         f'height="{height}" viewBox="0 0 {width} {height}" '
         f'font-family="{FAMILY}">',
         f'<style>.a{{fill:{FG_LIGHT}}}'
         f'@media(prefers-color-scheme:dark){{.a{{fill:{FG_DARK}}}}}</style>']

    for i, line in enumerate(lines):
        y = pad + i * LINE_H
        begin = f"{i * ROW_DELAY:.2f}s"
        end = f"{(i + 1) * ROW_DELAY:.2f}s"
        w = max(len(line), 1) * CHAR_W
        safe = (line.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))

        p.append(f'<clipPath id="c{i}"><rect x="{pad}" y="{y}" '
                 f'height="{LINE_H}" width="0">'
                 f'<animate attributeName="width" from="0" to="{w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'</rect></clipPath>')
        p.append(f'<g clip-path="url(#c{i})"><text xml:space="preserve" '
                 f'x="{pad}" y="{y + 11.2:.1f}" class="a" '
                 f'font-size="{FONT_SIZE}">{safe}</text></g>')
        p.append(f'<rect y="{y + 1}" width="6" height="12" class="a" '
                 f'opacity="0">'
                 f'<animate attributeName="x" from="{pad}" to="{pad + w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'<set attributeName="opacity" to="0.8" begin="{begin}"/>'
                 f'<set attributeName="opacity" to="0" begin="{end}"/></rect>')

    p.append("</svg>")
    return "".join(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("photo")
    ap.add_argument("out", nargs="?", default="ascii.svg")
    ap.add_argument("--crop", help="left,top,right,bottom, applied first")
    ap.add_argument("--cols", type=int, default=COLS)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--bg-threshold", type=int, default=None,
                    help="force brightness-matte mode with this cutoff (0-255)")
    args = ap.parse_args()

    crop = None
    if args.crop:
        parts = [int(v) for v in args.crop.split(",")]
        if len(parts) != 4:
            sys.exit("--crop needs four numbers: left,top,right,bottom")
        crop = tuple(parts)

    lines = to_lines(prep(args.photo, crop, args.bg_threshold), cols=args.cols)
    if args.preview:
        print("\n".join(lines))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(build_svg(lines, cols=args.cols))
    print(f"wrote {args.out} — {len(lines)} rows, {args.cols} columns")
    print("next: python3 scripts/embed_portrait_font.py")


if __name__ == "__main__":
    main()
