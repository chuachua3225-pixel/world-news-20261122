#!/usr/bin/env python3
"""Build the entry image for make.fun news-image-20261122.

A newspaper front page for Sunday 22 November 2026, composed with Pillow
from four painterly illustrations generated for this entry (art/*.webp)
plus text drawn with DejaVu fonts. Fully deterministic: fixed layout,
fixed fonts, no timestamps, no randomness, no network.
Run:  python3 build_entry.py   -> writes entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 26
CONTENT_W = W - 2 * MARGIN

PAPER = (246, 241, 230)
INK = (20, 20, 24)
NAVY = (20, 38, 63)
NAVY_DARK = (13, 26, 44)
GOLD = (201, 162, 75)
RED = (158, 43, 37)
GREY = (90, 86, 78)
RULE = (60, 58, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(draw, cx, y, text, fnt, fill, tracking=4):
    """Draw text centred on cx with extra tracking between characters."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def draw_para(draw, x, y, text, fnt, fill, width, leading):
    lines = wrap(draw, text, fnt, width)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def cover_crop(img, tw, th):
    """Centre-crop to the target aspect, then resize (LANCZOS)."""
    iw, ih = img.size
    target = tw / th
    if iw / ih > target:
        nw = int(ih * target)
        x0 = (iw - nw) // 2
        img = img.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(iw / target)
        y0 = (ih - nh) // 2
        img = img.crop((0, y0, iw, y0 + nh))
    return img.resize((tw, th), Image.LANCZOS)


def art(name):
    return Image.open(os.path.join(HERE, "art", name + ".webp")).convert("RGB")


def kicker(draw, x, y, text):
    draw.text((x, y), text, font=SANS_B(16), fill=RED)
    return y + 22


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Double outer frame.
    d.rectangle([10, 10, W - 11, H - 11], outline=NAVY, width=3)
    d.rectangle([18, 18, W - 19, H - 19], outline=RULE, width=1)

    # ---- Masthead -------------------------------------------------------
    d.rectangle([MARGIN, MARGIN, W - MARGIN, 150], fill=NAVY)
    d.text((W // 2, 44), "THE WORLD IN ONE DAY", font=SERIF_B(52),
           fill=(250, 247, 240), anchor="ma")
    draw_tracked(d, W // 2, 104, "SUNDAY 22 NOVEMBER 2026", SANS_B(24),
                 GOLD, tracking=6)
    d.line([(MARGIN, 150), (W - MARGIN, 150)], fill=GOLD, width=3)

    # ---- Lead: COP31 (left column) --------------------------------------
    lx, lw = MARGIN, 620
    y = 164
    y = kicker(d, lx, y, "CLIMATE  —  ANTALYA, TURKEY")
    y = draw_para(d, lx, y + 2,
                  "COP31 deadlocked over fossil fuels as talks run into overtime",
                  SERIF_B(38), INK, lw, 46)
    y = draw_para(d, lx, y + 6,
                  "The presidency tables a final draft that still never names coal, "
                  "oil or gas. Nearly 200 nations face a closing session on Sunday, "
                  "with a goal to lift electricity to 35% of energy by 2035.",
                  SANS(18), (52, 50, 46), lw, 24)
    img_y = y + 8
    img.paste(cover_crop(art("cop31"), lw, 224), (lx, img_y))
    d.rectangle([lx, img_y, lx + lw - 1, img_y + 224 - 1], outline=RULE, width=1)

    # ---- Mexico strip (left column, below lead) -------------------------
    y = img_y + 224 + 14
    d.line([(lx, y), (lx + lw, y)], fill=RULE, width=1)
    y += 10
    y = kicker(d, lx, y, "MEXICO  —  SINALOA")
    img.paste(cover_crop(art("mexico"), 300, 148), (lx, y + 24))
    d.rectangle([lx, y + 24, lx + 300 - 1, y + 24 + 148 - 1],
                outline=RULE, width=1)
    tx = lx + 316
    ty = y + 24
    ty = draw_para(d, tx, ty, "Mexico captures drug lord 'El Chapo Isidro'",
                   SERIF_B(25), INK, lw - 316, 30)
    draw_para(d, tx, ty + 6,
              "Eleven people are killed in Sinaloa violence after the arrest, "
              "the latest in a string of captures of cartel leaders.",
              SANS(16), (52, 50, 46), lw - 316, 21)

    # ---- Right column: Riyadh, then Kryvyi Rih --------------------------
    rx, rw = 666, 332
    y = 164
    img.paste(cover_crop(art("riyadh"), rw, 128), (rx, y))
    d.rectangle([rx, y, rx + rw - 1, y + 128 - 1], outline=RULE, width=1)
    y += 136
    y = kicker(d, rx, y, "MIDDLE EAST  —  RIYADH")
    y = draw_para(d, rx, y + 2,
                  "Houthis strike Riyadh — three missiles intercepted",
                  SERIF_B(24), INK, rw, 28)
    y = draw_para(d, rx, y + 6,
                  "Days after a strike damaged the capital's tallest tower, Saudi "
                  "defences destroy three ballistic missiles headed for Riyadh.",
                  SANS(16), (52, 50, 46), rw, 20)
    y += 12
    d.line([(rx, y), (rx + rw, y)], fill=RULE, width=1)
    y += 10
    img.paste(cover_crop(art("kryvyi-rih"), rw, 128), (rx, y))
    d.rectangle([rx, y, rx + rw - 1, y + 128 - 1], outline=RULE, width=1)
    y += 136
    y = kicker(d, rx, y, "UKRAINE  —  EUROPE")
    y = draw_para(d, rx, y + 2,
                  "Triple-tap strike kills boy, 7, in Zelenskyy's hometown",
                  SERIF_B(24), INK, rw, 28)
    draw_para(d, rx, y + 6,
              "A paramedic also dies; about 60 are wounded. Missiles fall in "
              "Poland, a Russian ship burns in the Baltic, and NATO vows to "
              "defend \u201cevery inch\u201d.",
              SANS(16), (52, 50, 46), rw, 20)

    # ---- Bottom strip: also today ---------------------------------------
    y = 862
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=NAVY, width=2)
    y += 10
    d.text((MARGIN, y), "ALSO TODAY", font=SANS_B(16), fill=NAVY)
    y += 26
    briefs = [
        ("NIGERIA", "Boat capsizes on the way to a funeral — 24 dead."),
        ("INDONESIA", "Jakarta factory fire: 3 dead, 36 missing."),
        ("PERU", "6.7 quake strikes Peru; no deaths reported."),
        ("UNITED STATES", "Trump vows a 10% cap on credit-card rates."),
        ("FRANCE", "Protests over living costs enter a sixth weekend."),
    ]
    bw = (CONTENT_W - 4 * 14) // 5
    for i, (tag, text) in enumerate(briefs):
        x = MARGIN + i * (bw + 14)
        d.text((x, y), tag, font=SANS_B(13), fill=RED)
        draw_para(d, x, y + 18, text, SANS(14), INK, bw, 18)
        if i < 4:
            d.line([(x + bw + 7, y - 2), (x + bw + 7, y + 72)],
                   fill=(200, 192, 172), width=1)

    # ---- Footer ---------------------------------------------------------
    d.line([(MARGIN, 972), (W - MARGIN, 972)], fill=RULE, width=1)
    d.text((W // 2, 980),
           "Geneva opens a path to an accord on \u201ckiller robots\u201d  ·  "
           "Rohingya hail Myanmar genocide verdict  ·  "
           "US farm department and FBI hit by hackers",
           font=SANS(13), fill=GREY, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
