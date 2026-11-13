"""Coolest art entry for make.fun — "SENTINEL-7: The Machine Awakens".

Deterministic Pillow program: draws a sleek tech robot head with a glowing
cyan visor, circuit traces, holographic panels and a reactor core, on a dark
grid background. No network, no randomness (star/particle fields use
fixed-seed LCGs), no fonts, no clock. Output is a 1024x1024 PNG written to
$OUTPUT_PATH (default /output/entry.png). Two runs write identical bytes.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

SS = 2            # supersample factor
W = H = 1024 * SS
OUT = os.environ.get("OUTPUT_PATH", "/output/entry.png")


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def vgrad(draw, width, height, stops):
    """Vertical gradient from a list of (position 0..1, rgb) stops."""
    for y in range(height):
        t = y / max(height - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                draw.line([(0, y), (width, y)], fill=mix(c0, c1, f))
                break


def lcg(seed):
    x = seed
    while True:
        x = (x * 1103515245 + 12345) % (2 ** 31)
        yield x


def hexagon(draw, cx, cy, r, fill, outline, width):
    pts = []
    for k in range(6):
        a = math.pi / 3 * k - math.pi / 6
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill, outline=outline, width=width)


def main():
    img = Image.new("RGB", (W, H), (4, 8, 16))
    d = ImageDraw.Draw(img)

    # --- background: deep blue gradient + faint grid ---
    bg = Image.new("RGB", (W, H))
    bd = ImageDraw.Draw(bg)
    vgrad(bd, W, H, [(0.0, (6, 12, 28)), (0.55, (8, 20, 44)), (1.0, (4, 8, 18))])
    img.paste(bg, (0, 0))
    d = ImageDraw.Draw(img)
    for gx in range(0, W + 1, 128 * SS):
        d.line([(gx, 0), (gx, H)], fill=(16, 34, 58), width=2 * SS)
    for gy in range(0, H + 1, 128 * SS):
        d.line([(0, gy), (W, gy)], fill=(16, 34, 58), width=2 * SS)
    # stars / dust
    gen = lcg(4242)
    for _ in range(120):
        sx = next(gen) % W
        sy = next(gen) % H
        r = 1 + next(gen) % 2
        b = 120 + next(gen) % 120
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(b, b, 255))

    # --- halo ring behind the head ---
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    cx, cy = W // 2, int(H * 0.42)
    R = int(W * 0.335)
    rd.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(0, 200, 255, 70), width=4 * SS)
    rd.ellipse([cx - R - 26 * SS, cy - R - 26 * SS, cx + R + 26 * SS, cy + R + 26 * SS],
               outline=(0, 120, 200, 40), width=3 * SS)
    # tick marks on the ring
    for k in range(48):
        a = math.pi * 2 * k / 48
        r0 = R - 10 * SS if k % 4 == 0 else R - 5 * SS
        rd.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                 (cx + (R + 6 * SS) * math.cos(a), cy + (R + 6 * SS) * math.sin(a))],
                fill=(0, 220, 255, 160), width=3 * SS)
    ring = ring.filter(ImageFilter.GaussianBlur(1 * SS))
    img.paste(ring, (0, 0), ring)
    d = ImageDraw.Draw(img)

    # --- floating hexagons ---
    for (hx, hy, hr, col) in [(int(W * 0.13), int(H * 0.30), 52 * SS, (0, 255, 240)),
                              (int(W * 0.87), int(H * 0.24), 44 * SS, (0, 200, 255)),
                              (int(W * 0.10), int(H * 0.68), 38 * SS, (120, 80, 255)),
                              (int(W * 0.90), int(H * 0.70), 58 * SS, (0, 255, 240))]:
        hexagon(d, hx, hy, hr, None, col, 4 * SS)
        hexagon(d, hx, hy, hr // 2, None, col, 2 * SS)
        d.ellipse([hx - 5 * SS, hy - 5 * SS, hx + 5 * SS, hy + 5 * SS], fill=col)

    # --- holographic side panels ---
    def panel(x0, y0, wdt, hgt, lines):
        d.rounded_rectangle([x0, y0, x0 + wdt, y0 + hgt], radius=10 * SS,
                            outline=(0, 220, 255), width=3 * SS)
        yy = y0 + 16 * SS
        for ln in lines:
            d.line([(x0 + 12 * SS, yy), (x0 + 12 * SS + int(wdt * ln), yy)],
                   fill=(0, 255, 240), width=4 * SS)
            yy += 16 * SS
        d.ellipse([x0 + wdt - 20 * SS, y0 + 12 * SS, x0 + wdt - 8 * SS, y0 + 24 * SS],
                  fill=(255, 60, 90))
    panel(int(W * 0.045), int(H * 0.30), int(W * 0.13), int(H * 0.13), [0.7, 0.5, 0.85, 0.4])
    panel(int(W * 0.825), int(H * 0.30), int(W * 0.13), int(H * 0.13), [0.6, 0.9, 0.45, 0.75])
    panel(int(W * 0.045), int(H * 0.62), int(W * 0.13), int(H * 0.10), [0.8, 0.55, 0.65])
    panel(int(W * 0.825), int(H * 0.62), int(W * 0.13), int(H * 0.10), [0.5, 0.8, 0.6])

    # --- antenna ---
    d.line([(cx, int(H * 0.155)), (cx, int(H * 0.10))], fill=(140, 160, 190), width=8 * SS)
    d.ellipse([cx - 16 * SS, int(H * 0.10) - 16 * SS, cx + 16 * SS, int(H * 0.10) + 16 * SS],
              fill=(0, 255, 240))
    d.ellipse([cx - 26 * SS, int(H * 0.10) - 26 * SS, cx + 26 * SS, int(H * 0.10) + 26 * SS],
              outline=(0, 255, 240), width=3 * SS)

    # --- head: gunmetal shell ---
    hx0, hy0 = int(W * 0.30), int(H * 0.155)
    hx1, hy1 = int(W * 0.70), int(H * 0.60)
    shell = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd = ImageDraw.Draw(shell)
    shd.rounded_rectangle([hx0, hy0, hx1, hy1], radius=64 * SS, fill=(24, 34, 52, 255))
    # top highlight plate
    shd.rounded_rectangle([hx0 + 18 * SS, hy0 + 14 * SS, hx1 - 18 * SS, hy0 + 62 * SS],
                          radius=20 * SS, fill=(52, 68, 92, 255))
    # side cheek plates
    shd.rounded_rectangle([hx0 + 16 * SS, hy0 + 150 * SS, hx0 + 92 * SS, hy1 - 90 * SS],
                          radius=16 * SS, fill=(16, 24, 38, 255))
    shd.rounded_rectangle([hx1 - 92 * SS, hy0 + 150 * SS, hx1 - 16 * SS, hy1 - 90 * SS],
                          radius=16 * SS, fill=(16, 24, 38, 255))
    # chin grill
    for gy in range(hy1 - 66 * SS, hy1 - 18 * SS, 14 * SS):
        shd.line([(hx0 + 150 * SS, gy), (hx1 - 150 * SS, gy)], fill=(8, 12, 22, 255), width=5 * SS)
    # rivets
    for (rx, ry) in [(hx0 + 30 * SS, hy0 + 30 * SS), (hx1 - 30 * SS, hy0 + 30 * SS),
                     (hx0 + 30 * SS, hy1 - 30 * SS), (hx1 - 30 * SS, hy1 - 30 * SS)]:
        shd.ellipse([rx - 7 * SS, ry - 7 * SS, rx + 7 * SS, ry + 7 * SS], fill=(120, 140, 170, 255))
    shell = shell.filter(ImageFilter.GaussianBlur(1 * SS))
    img.paste(shell, (0, 0), shell)
    d = ImageDraw.Draw(img)
    # shell rim light
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=64 * SS,
                        outline=(0, 255, 240), width=5 * SS)

    # --- ear discs ---
    for ex in (hx0 - 6 * SS, hx1 + 6 * SS):
        d.ellipse([ex - 44 * SS, int(H * 0.36) - 44 * SS, ex + 44 * SS, int(H * 0.36) + 44 * SS],
                  fill=(18, 28, 44), outline=(0, 220, 255), width=5 * SS)
        d.ellipse([ex - 18 * SS, int(H * 0.36) - 18 * SS, ex + 18 * SS, int(H * 0.36) + 18 * SS],
                  fill=(0, 255, 240))

    # --- visor: glowing cyan band with two eyes ---
    vx0, vy0 = int(W * 0.335), int(H * 0.27)
    vx1, vy1 = int(W * 0.665), int(H * 0.395)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([vx0 - 24 * SS, vy0 - 24 * SS, vx1 + 24 * SS, vy1 + 24 * SS],
                         radius=40 * SS, fill=(0, 255, 240, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(18 * SS))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img)
    visor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(visor)
    vd.rounded_rectangle([vx0, vy0, vx1, vy1], radius=34 * SS, fill=(4, 10, 18, 255))
    # eye cores
    vd.rounded_rectangle([vx0 + 26 * SS, vy0 + 30 * SS, vx0 + 190 * SS, vy1 - 30 * SS],
                         radius=22 * SS, fill=(0, 255, 240, 255))
    vd.rounded_rectangle([vx1 - 190 * SS, vy0 + 30 * SS, vx1 - 26 * SS, vy1 - 30 * SS],
                         radius=22 * SS, fill=(0, 255, 240, 255))
    # white hot centers
    vd.rounded_rectangle([vx0 + 78 * SS, vy0 + 44 * SS, vx0 + 138 * SS, vy1 - 44 * SS],
                         radius=14 * SS, fill=(235, 255, 255, 255))
    vd.rounded_rectangle([vx1 - 138 * SS, vy0 + 44 * SS, vx1 - 78 * SS, vy1 - 44 * SS],
                         radius=14 * SS, fill=(235, 255, 255, 255))
    # scanlines
    for sy in range(vy0 + 12 * SS, vy1, 12 * SS):
        vd.line([(vx0 + 8 * SS, sy), (vx1 - 8 * SS, sy)], fill=(0, 120, 140, 90), width=2 * SS)
    vd.rounded_rectangle([vx0, vy0, vx1, vy1], radius=34 * SS, outline=(0, 255, 240, 255), width=5 * SS)
    img.paste(visor, (0, 0), visor)
    d = ImageDraw.Draw(img)

    # --- nose / mouth vents ---
    d.line([(cx - 30 * SS, int(H * 0.44)), (cx + 30 * SS, int(H * 0.44))],
           fill=(0, 200, 220), width=4 * SS)
    for mx in range(cx - 60 * SS, cx + 61 * SS, 24 * SS):
        d.line([(mx, int(H * 0.50)), (mx, int(H * 0.53))], fill=(90, 110, 140), width=5 * SS)

    # --- neck + cables ---
    d.polygon([(int(W * 0.42), hy1), (int(W * 0.58), hy1),
               (int(W * 0.62), int(H * 0.68)), (int(W * 0.38), int(H * 0.68))],
              fill=(18, 28, 44))
    d.line([(int(W * 0.42), hy1), (int(W * 0.38), int(H * 0.68))], fill=(0, 255, 240), width=4 * SS)
    d.line([(int(W * 0.58), hy1), (int(W * 0.62), int(H * 0.68))], fill=(0, 255, 240), width=4 * SS)
    for cy2 in range(int(H * 0.615), int(H * 0.675), 16 * SS):
        d.line([(int(W * 0.415), cy2), (int(W * 0.585), cy2)], fill=(60, 80, 110), width=4 * SS)

    # --- chest plate with reactor core ---
    d.rounded_rectangle([int(W * 0.30), int(H * 0.68), int(W * 0.70), int(H * 0.92)],
                        radius=36 * SS, fill=(20, 30, 48))
    d.rounded_rectangle([int(W * 0.30), int(H * 0.68), int(W * 0.70), int(H * 0.92)],
                        radius=36 * SS, outline=(0, 220, 255), width=4 * SS)
    ccx, ccy = W // 2, int(H * 0.79)
    cr = 52 * SS
    core_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cgd = ImageDraw.Draw(core_glow)
    cgd.ellipse([ccx - cr - 30 * SS, ccy - cr - 30 * SS, ccx + cr + 30 * SS, ccy + cr + 30 * SS],
                fill=(0, 255, 240, 60))
    core_glow = core_glow.filter(ImageFilter.GaussianBlur(16 * SS))
    img.paste(core_glow, (0, 0), core_glow)
    d = ImageDraw.Draw(img)
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(4, 12, 20),
              outline=(0, 255, 240), width=5 * SS)
    d.ellipse([ccx - cr // 2, ccy - cr // 2, ccx + cr // 2, ccy + cr // 2],
              fill=(0, 255, 240))
    d.ellipse([ccx - cr // 4, ccy - cr // 4, ccx + cr // 4, ccy + cr // 4],
              fill=(235, 255, 255))
    # data bars flanking the core
    for i, ln in enumerate([0.8, 0.55, 0.95, 0.4, 0.7]):
        yb = int(H * 0.755) + i * 18 * SS
        d.line([(int(W * 0.335), yb), (int(W * 0.335) + int(90 * SS * ln), yb)],
               fill=(0, 255, 240), width=6 * SS)
        d.line([(int(W * 0.665), yb), (int(W * 0.665) - int(90 * SS * ln), yb)],
               fill=(0, 200, 255), width=6 * SS)

    # --- embers / particles rising ---
    pg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pg)
    gen = lcg(777)
    for _ in range(60):
        sx = next(gen) % W
        sy = next(gen) % H
        r2 = 2 + next(gen) % 3 * SS
        col = (0, 255, 240) if next(gen) % 3 == 0 else (120, 80, 255)
        pd.ellipse([sx - r2, sy - r2, sx + r2, sy + r2], fill=col + (200,))
    pg = pg.filter(ImageFilter.GaussianBlur(1 * SS))
    img.paste(pg, (0, 0), pg)

    # --- vignette ---
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd2 = ImageDraw.Draw(vig)
    vd2.ellipse([-int(W * 0.25), -int(H * 0.25), int(W * 1.25), int(H * 1.25)],
                outline=(0, 0, 0, 110), width=int(W * 0.22))
    vig = vig.filter(ImageFilter.GaussianBlur(60 * SS))
    img.paste(vig, (0, 0), vig)

    img = img.resize((1024, 1024), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    img.save(OUT, format="PNG")


if __name__ == "__main__":
    main()
