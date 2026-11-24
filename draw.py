"""Build entry.png: a newspaper front page for Tuesday 24 November 2026."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
W = H = 1024
SS = 3  # supersampling factor for illustrations

PAPER = (246, 241, 228)
INK = (28, 28, 30)
GREY = (62, 62, 68)
RED = (196, 40, 40)
BLUE = (40, 90, 170)
YELLOW = (240, 196, 40)
GREEN = (46, 140, 80)
ORANGE = (236, 120, 30)
SKY = (205, 222, 236)


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(d, t, f) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(d, s, name, size, width, max_lines):
    """Largest font size <= size whose wrapped text fits in max_lines and width."""
    while size > 8:
        f = font(name, size)
        lines = wrap(d, s, f, width)
        if len(lines) <= max_lines and all(text_w(d, l, f) <= width for l in lines):
            return f, lines
        size -= 1
    raise SystemExit("text does not fit: " + s)


def draw_lines(d, x, y, lines, f, fill, gap=1.18, center_w=None):
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * gap)
    for l in lines:
        lx = x if center_w is None else x + (center_w - text_w(d, l, f)) / 2
        d.text((lx, y), l, font=f, fill=fill)
        y += lh
    return y


# ---------- illustrations (drawn at SS x, coordinates in a 0..w,0..h box) ----------

def illo(w, h, painter):
    im = Image.new("RGB", (w * SS, h * SS), PAPER)
    d = ImageDraw.Draw(im)
    painter(d, w * SS, h * SS, SS)
    return im.resize((w, h), Image.LANCZOS)


def p_nvidia(d, w, h, s):
    # chip
    cx, cy, r = w * 0.30, h * 0.52, h * 0.30
    for i in range(5):
        off = -r + (i + 0.5) * (2 * r / 5)
        for (x0, y0, x1, y1) in [
            (cx + off - 4 * s, cy - r - 18 * s, cx + off + 4 * s, cy - r),
            (cx + off - 4 * s, cy + r, cx + off + 4 * s, cy + r + 18 * s),
            (cx - r - 18 * s, cy + off - 4 * s, cx - r, cy + off + 4 * s),
            (cx + r, cy + off - 4 * s, cx + r + 18 * s, cy + off + 4 * s),
        ]:
            d.rectangle((x0, y0, x1, y1), fill=GREY)
    d.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), radius=10 * s, fill=INK)
    d.rounded_rectangle((cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6),
                        radius=6 * s, fill=(118, 185, 0))
    # rising chart
    x0, y0, x1, y1 = w * 0.60, h * 0.15, w * 0.97, h * 0.88
    d.line((x0, y1, x1, y1), fill=INK, width=3 * s)
    d.line((x0, y0, x0, y1), fill=INK, width=3 * s)
    pts = [(x0 + 8 * s, y1 - 40 * s), (x0 + (x1 - x0) * 0.3, y1 - 55 * s),
           (x0 + (x1 - x0) * 0.5, y1 - 45 * s), (x1 - 22 * s, y0 + 30 * s)]
    d.line(pts, fill=GREEN, width=7 * s, joint="curve")
    ax, ay = pts[-1]
    d.polygon([(ax + 18 * s, ay - 16 * s), (ax - 14 * s, ay - 8 * s), (ax + 6 * s, ay + 18 * s)],
              fill=GREEN)


def p_ukraine(d, w, h, s):
    d.rectangle((0, 0, w, h * 0.5), fill=(70, 120, 200))
    d.rectangle((0, h * 0.5, w, h), fill=YELLOW)
    # buildings silhouette
    base = h * 0.92
    blds = [(0.08, 0.40), (0.24, 0.55), (0.42, 0.35), (0.60, 0.62), (0.80, 0.45)]
    for bx, bh in blds:
        x0 = w * bx
        d.rectangle((x0, base - h * bh, x0 + w * 0.15, base), fill=INK)
        for wy in range(int(base - h * bh + 8 * s), int(base - 8 * s), 14 * s):
            d.rectangle((x0 + 6 * s, wy, x0 + 11 * s, wy + 6 * s), fill=(80, 80, 85))
    d.rectangle((0, base, w, h), fill=INK)
    # smoke plume
    for i, (px, py, pr) in enumerate([(0.66, 0.30, 16), (0.72, 0.18, 20), (0.80, 0.08, 24)]):
        d.ellipse((w * px - pr * s, h * py - pr * s, w * px + pr * s, h * py + pr * s),
                  fill=(120, 120, 125))
    # burst
    cx, cy = w * 0.67, h * 0.36
    import math
    pts = []
    for i in range(16):
        a = math.pi * 2 * i / 16
        rr = (26 if i % 2 == 0 else 12) * s
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=ORANGE)


def flame(d, cx, by, fw, fh, s):
    d.polygon([(cx - fw, by), (cx - fw * 0.6, by - fh * 0.6), (cx - fw * 0.2, by - fh * 0.4),
               (cx, by - fh), (cx + fw * 0.3, by - fh * 0.5), (cx + fw * 0.7, by - fh * 0.7),
               (cx + fw, by)], fill=RED)
    d.polygon([(cx - fw * 0.55, by), (cx - fw * 0.2, by - fh * 0.45), (cx, by - fh * 0.65),
               (cx + fw * 0.25, by - fh * 0.4), (cx + fw * 0.55, by)], fill=ORANGE)
    d.polygon([(cx - fw * 0.25, by), (cx, by - fh * 0.3), (cx + fw * 0.25, by)], fill=YELLOW)


def p_fire(d, w, h, s):
    d.rectangle((0, 0, w, h), fill=(60, 50, 60))
    base = h * 0.90
    # factory with sawtooth roof
    x0, x1 = w * 0.12, w * 0.88
    roof = h * 0.52
    d.rectangle((x0, roof, x1, base), fill=(150, 130, 120))
    n = 4
    step = (x1 - x0) / n
    for i in range(n):
        a = x0 + i * step
        d.polygon([(a, roof), (a + step, roof - h * 0.14), (a + step, roof)], fill=(150, 130, 120))
    d.rectangle((w * 0.70, h * 0.16, w * 0.77, roof), fill=(120, 100, 95))
    for i in range(4):
        wx = x0 + 14 * s + i * step
        d.rectangle((wx, roof + 16 * s, wx + step * 0.5, roof + 34 * s), fill=YELLOW)
    d.rectangle((0, base, w, h), fill=(40, 34, 40))
    # candy wrapper motif on the wall
    cx, cy = w * 0.30, base - 18 * s
    d.ellipse((cx - 11 * s, cy - 8 * s, cx + 11 * s, cy + 8 * s), fill=(230, 90, 150))
    d.polygon([(cx - 11 * s, cy), (cx - 22 * s, cy - 9 * s), (cx - 22 * s, cy + 9 * s)], fill=(230, 90, 150))
    d.polygon([(cx + 11 * s, cy), (cx + 22 * s, cy - 9 * s), (cx + 22 * s, cy + 9 * s)], fill=(230, 90, 150))
    flame(d, w * 0.42, roof + 4 * s, 30 * s, 70 * s, s)
    flame(d, w * 0.60, roof - h * 0.05, 24 * s, 56 * s, s)


def p_grok(d, w, h, s):
    d.rectangle((0, 0, w, h), fill=SKY)
    # chat bubble with blocked image
    bx0, by0, bx1, by1 = w * 0.08, h * 0.12, w * 0.55, h * 0.70
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=14 * s, fill=(255, 255, 255), outline=INK, width=3 * s)
    d.polygon([(bx0 + 30 * s, by1), (bx0 + 20 * s, by1 + 26 * s), (bx0 + 55 * s, by1)], fill=INK)
    d.polygon([(bx0 + 33 * s, by1 - 3 * s), (bx0 + 25 * s, by1 + 16 * s), (bx0 + 50 * s, by1 - 3 * s)],
              fill=(255, 255, 255))
    ix0, iy0, ix1, iy1 = bx0 + 18 * s, by0 + 14 * s, bx1 - 18 * s, by1 - 14 * s
    d.rectangle((ix0, iy0, ix1, iy1), fill=(200, 200, 205))
    d.line((ix0, iy0, ix1, iy1), fill=RED, width=6 * s)
    d.line((ix0, iy1, ix1, iy0), fill=RED, width=6 * s)
    # gavel
    gx, gy = w * 0.76, h * 0.42
    d.line((gx - 50 * s, gy + 60 * s, gx + 4 * s, gy + 4 * s), fill=(120, 70, 30), width=10 * s)
    head = [(gx - 20 * s, gy - 18 * s), (gx + 10 * s, gy - 48 * s), (gx + 48 * s, gy - 10 * s),
            (gx + 18 * s, gy + 20 * s)]
    d.polygon(head, fill=(140, 85, 40))
    d.rounded_rectangle((w * 0.62, h * 0.82, w * 0.95, h * 0.92), radius=4 * s, fill=(120, 70, 30))


def p_cop(d, w, h, s):
    d.rectangle((0, 0, w, h), fill=SKY)
    cx, cy, r = w * 0.38, h * 0.52, h * 0.38
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(70, 140, 210))
    d.polygon([(cx - r * 0.6, cy - r * 0.5), (cx - r * 0.1, cy - r * 0.7), (cx + r * 0.1, cy - r * 0.2),
               (cx - r * 0.3, cy + r * 0.1), (cx - r * 0.7, cy - r * 0.1)], fill=GREEN)
    d.polygon([(cx + r * 0.2, cy + r * 0.1), (cx + r * 0.7, cy), (cx + r * 0.6, cy + r * 0.6),
               (cx + r * 0.2, cy + r * 0.7)], fill=GREEN)
    # smokestack and smoke
    fx = w * 0.78
    d.rectangle((fx - 14 * s, h * 0.45, fx + 14 * s, h * 0.95), fill=(110, 110, 115))
    d.rectangle((fx - 18 * s, h * 0.45, fx + 18 * s, h * 0.50), fill=INK)
    for px, py, pr in [(0.80, 0.36, 14), (0.85, 0.24, 18), (0.91, 0.12, 22)]:
        d.ellipse((w * px - pr * s, h * py - pr * s, w * px + pr * s, h * py + pr * s), fill=(90, 90, 95))


def p_train(d, w, h, s):
    d.rectangle((0, 0, w, h), fill=SKY)
    d.rectangle((0, h * 0.86, w, h), fill=(150, 130, 100))
    d.line((0, h * 0.86, w, h * 0.86), fill=INK, width=3 * s)
    for x in range(0, int(w), 22 * s):
        d.rectangle((x, h * 0.88, x + 10 * s, h * 0.93), fill=(110, 80, 50))
    # locomotive
    y1 = h * 0.80
    d.rounded_rectangle((w * 0.10, h * 0.30, w * 0.62, y1), radius=10 * s, fill=(200, 60, 50))
    d.polygon([(w * 0.62, h * 0.40), (w * 0.82, h * 0.58), (w * 0.82, y1), (w * 0.62, y1)],
              fill=(200, 60, 50))
    d.rectangle((w * 0.10, h * 0.56, w * 0.82, h * 0.62), fill=YELLOW)
    for i in range(3):
        x = w * 0.15 + i * w * 0.15
        d.rectangle((x, h * 0.37, x + w * 0.10, h * 0.50), fill=(230, 240, 250))
    d.rectangle((w * 0.64, h * 0.44, w * 0.72, h * 0.54), fill=(230, 240, 250))
    for x in (0.20, 0.40, 0.70):
        cx, cy, r = w * x, y1, 12 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK)
    # two flags at the front: India and Nepal (simplified)
    d.line((w * 0.88, h * 0.20, w * 0.88, h * 0.80), fill=INK, width=3 * s)
    d.rectangle((w * 0.88, h * 0.20, w * 0.99, h * 0.25), fill=(255, 153, 51))
    d.rectangle((w * 0.88, h * 0.25, w * 0.99, h * 0.30), fill=(255, 255, 255))
    d.rectangle((w * 0.88, h * 0.30, w * 0.99, h * 0.35), fill=(19, 136, 8))
    d.line((w * 0.04, h * 0.10, w * 0.04, h * 0.80), fill=INK, width=3 * s)
    d.polygon([(w * 0.04, h * 0.10), (w * 0.10, h * 0.17), (w * 0.06, h * 0.17), (w * 0.10, h * 0.26),
               (w * 0.04, h * 0.26)], fill=(220, 20, 60))


def p_storm(d, w, h, s):
    d.rectangle((0, 0, w, h), fill=(150, 160, 175))
    # rain
    for i in range(14):
        x = w * 0.08 + i * w * 0.065
        d.line((x, h * 0.55, x - 10 * s, h * 0.80), fill=(60, 100, 180), width=3 * s)
    # cloud
    for (px, py, pr) in [(0.25, 0.42, 0.16), (0.42, 0.30, 0.22), (0.62, 0.36, 0.18), (0.76, 0.46, 0.13)]:
        d.ellipse((w * px - h * pr * 1.4, h * py - h * pr * 1.4, w * px + h * pr * 1.4, h * py + h * pr * 1.4),
                  fill=(70, 75, 90))
    d.rectangle((w * 0.12, h * 0.42, w * 0.86, h * 0.60), fill=(70, 75, 90))
    # lightning
    d.polygon([(w * 0.50, h * 0.50), (w * 0.40, h * 0.74), (w * 0.48, h * 0.74), (w * 0.42, h * 0.98),
               (w * 0.60, h * 0.66), (w * 0.51, h * 0.66), (w * 0.58, h * 0.50)], fill=YELLOW)
    # small plane
    px, py = w * 0.82, h * 0.82
    d.polygon([(px - 40 * s, py), (px + 34 * s, py - 6 * s), (px + 40 * s, py), (px + 34 * s, py + 6 * s)],
              fill=(255, 255, 255))
    d.polygon([(px - 4 * s, py), (px + 10 * s, py - 30 * s), (px + 18 * s, py - 30 * s), (px + 10 * s, py)],
              fill=(255, 255, 255))
    d.polygon([(px - 4 * s, py), (px + 10 * s, py + 30 * s), (px + 18 * s, py + 30 * s), (px + 10 * s, py)],
              fill=(255, 255, 255))
    d.polygon([(px - 40 * s, py), (px - 46 * s, py - 16 * s), (px - 36 * s, py - 16 * s), (px - 28 * s, py)],
              fill=(255, 255, 255))


# ---------- page ----------

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28

    # masthead
    f_name = font("DejaVuSerif-Bold.ttf", 62)
    name = "THE WORLD DAILY"
    d.text(((W - text_w(d, name, f_name)) / 2, 14), name, font=f_name, fill=INK)
    d.line((M, 92, W - M, 92), fill=INK, width=3)
    d.rectangle((M, 99, W - M, 153), fill=INK)
    f_date = font("DejaVuSans-Bold.ttf", 40)
    date = "TUESDAY 24 NOVEMBER 2026"
    d.text(((W - text_w(d, date, f_date)) / 2, 103), date, font=f_date, fill=PAPER)
    d.line((M, 160, W - M, 160), fill=INK, width=1)

    # lead story
    top = 172
    lead_h = 274
    img.paste(illo(360, lead_h - 16, p_nvidia), (M, top + 4))
    tx = M + 384
    tw = W - M - tx
    kf = font("DejaVuSans-Bold.ttf", 22)
    d.text((tx, top + 6), "TECH  |  MARKETS", font=kf, fill=RED)
    hf, hl = fit(d, "Huang returns as Nvidia chief", "DejaVuSerif-Bold.ttf", 50, tw, 2)
    y = draw_lines(d, tx, top + 34, hl, hf, INK, gap=1.08)
    bf, bl = fit(d, "Back as CEO 11 days after stepping down. Trump says he helped broker it. "
                    "Shares jump about 33%.", "DejaVuSans.ttf", 24, tw, 3)
    yb = draw_lines(d, tx, y + 10, bl, bf, GREY, gap=1.18)
    assert yb <= top + lead_h, yb

    d.line((M, top + lead_h + 8, W - M, top + lead_h + 8), fill=INK, width=3)

    # six-story grid
    stories = [
        (p_ukraine, "Kyiv region strikes kill at least 14", "Zelenskyy calls for four-way talks with Russia soon"),
        (p_fire, "Indonesia candy factory fire", "At least 24 dead, about 30 missing; search goes on"),
        (p_grok, "US states sue Musk firms", "Lawsuits over Grok AI making sexualised images"),
        (p_cop, "COP31 ends in Antalya", "No deal on stronger fossil fuel phase-out wording"),
        (p_train, "Modi and Shah flag off train", "Saryu-Kamala Express links Ayodhya and Janakpur"),
        (p_storm, "Storms hit Thanksgiving travel", "Messy US holiday journeys threatened"),
    ]
    gy0 = top + lead_h + 22
    cols, rows = 3, 2
    gap = 22
    cw = (W - 2 * M - gap * (cols - 1)) / cols
    ch = (H - M - gy0 - 14) / rows
    hfs = []
    for _, head, body in stories:
        hfs.append(fit(d, head, "DejaVuSerif-Bold.ttf", 26, int(cw), 2)[0].size)
    hsize = min(hfs)  # one consistent headline size across the grid
    for i, (painter, head, body) in enumerate(stories):
        c, r = i % cols, i // cols
        x = int(M + c * (cw + gap))
        y = int(gy0 + r * (ch + 14))
        ih = 112
        img.paste(illo(int(cw), ih, painter), (x, y))
        d.rectangle((x, y, x + int(cw) - 1, y + ih - 1), outline=INK, width=1)
        hf = font("DejaVuSerif-Bold.ttf", hsize)
        hl = wrap(d, head, hf, int(cw))
        yy = draw_lines(d, x, y + ih + 6, hl, hf, INK, gap=1.05)
        bf, bl = fit(d, body, "DejaVuSans.ttf", 21, int(cw), 2)
        draw_lines(d, x, yy + 4, bl, bf, GREY, gap=1.15)
        if c < cols - 1:
            lx = x + int(cw) + gap // 2
            d.line((lx, y, lx, y + ch - 6), fill=(170, 165, 150), width=1)
    d.line((M, gy0 + ch + 4, W - M, gy0 + ch + 4), fill=(170, 165, 150), width=1)

    img.save(os.path.join(HERE, "entry.png"), optimize=True)


if __name__ == "__main__":
    main()
