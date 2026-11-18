#!/usr/bin/env python3
"""news-image-20261117 — one image summing up world news of Tuesday 17 November 2026.

Draws a front-page-style news summary (800x800 PNG) with pure stdlib Python:
a hand-rolled raster canvas, a 5x7 bitmap font, and a minimal PNG encoder.
No network, no downloaded assets, no randomness — the output is byte-identical
on every run.

Stories depicted (all reported on Tuesday 17 November 2026):
  1. Ukraine strikes the Kerch Bridge — a road span collapses; Russia hits
     two bridges in Kyiv in reply.
  2. Tankers hit by mines near the Strait of Hormuz; a third US aircraft
     carrier (USS Theodore Roosevelt) arrives in the Middle East.
  3. Trump arrives in Manila for the ASEAN summit; China confirms a
     Trump–Xi–Putin trilateral in Shenzhen on Thursday 19 Nov (APEC).
  4. Five European states announce a joint migrant return hub in Rwanda.
  5. A ULA Vulcan rocket fails in flight, destroying 40 Amazon Leo satellites.
"""

import math
import os
import struct
import zlib

W, H = 800, 800

# ---------------------------------------------------------------- palette
NAVY = (16, 38, 74)
NAVY_DK = (10, 26, 52)
GOLD = (232, 182, 76)
PAPER = (247, 243, 234)
INK = (24, 24, 28)
WHITE = (255, 255, 255)
SKY_TOP = (150, 190, 220)
SKY_BOT = (222, 234, 240)
SEA = (46, 95, 122)
SEA_DK = (30, 70, 95)
GREY = (120, 125, 130)
SMOKE = (150, 150, 148)
ORANGE = (235, 110, 30)
FIRE = (245, 170, 40)
RED = (190, 40, 35)
DARK = (40, 42, 48)

# ------------------------------------------------------------------- font
# 5x7 bitmap font, rows top to bottom, '#' = on. All text is upper-case.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


class Canvas:
    """A plain RGB pixel buffer with simple filled-shape drawing."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def vgrad(self, x, y, w, h, top, bot):
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
            self.fill_rect(x, y + yy, w, 1, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c)

    def line(self, x0, y0, x1, y1, c, th=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for a in range(-(th // 2), th // 2 + 1):
                for b in range(-(th // 2), th // 2 + 1):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def border(self, x, y, w, h, c, th=2):
        self.fill_rect(x, y, w, th, c)
        self.fill_rect(x, y + h - th, w, th, c)
        self.fill_rect(x, y, th, h, c)
        self.fill_rect(x + w - th, y, th, h, c)


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------- masthead
def draw_masthead(cv):
    cv.fill_rect(0, 0, W, 100, NAVY)
    cv.fill_rect(0, 96, W, 4, GOLD)
    cv.text_center(W // 2, 16, "THE WORLD IN ONE DAY", 4, WHITE)
    cv.text_center(W // 2, 64, "TUESDAY 17 NOVEMBER 2026", 2, GOLD)


# --------------------------------------------------------- hero: Kerch Bridge
def draw_hero(cv, x, y, w, h):
    # sky and sea
    cv.vgrad(x, y, w, 190, SKY_TOP, SKY_BOT)
    cv.fill_rect(x, y + 190, w, h - 190, SEA)
    cv.fill_rect(x, y + 190, w, 3, (120, 160, 180))
    # distant shore
    cv.fill_rect(x, y + 178, w, 12, (110, 140, 130))
    deck_y = y + 168
    # bridge towers (two pylons either side of the gap)
    for tx in (x + 150, x + w - 190):
        cv.fill_rect(tx, y + 60, 14, deck_y - y - 60 + 8, DARK)
        cv.fill_rect(tx - 6, y + 52, 26, 10, DARK)
        # stay cables
        cv.line(tx + 7, y + 62, tx - 110, deck_y, GREY, 2)
        cv.line(tx + 7, y + 62, tx + 124, deck_y, GREY, 2)
    # deck, left and right of the collapsed middle span
    gap0, gap1 = x + w // 2 - 70, x + w // 2 + 70
    cv.fill_rect(x + 8, deck_y, gap0 - x - 8, 10, DARK)
    cv.fill_rect(gap1, deck_y, x + w - 8 - gap1, 10, DARK)
    # deck supports
    for sx in (x + 60, x + 130, x + w - 140, x + w - 70):
        cv.fill_rect(sx, deck_y + 10, 8, y + 190 - deck_y - 10, DARK)
    # broken deck pieces tumbling into the gap
    cv.poly([(gap0 - 6, deck_y + 2), (gap0 + 34, deck_y + 6),
             (gap0 + 26, deck_y + 26), (gap0 - 12, deck_y + 22)], (70, 72, 80))
    cv.poly([(gap1 - 30, deck_y + 10), (gap1 + 4, deck_y + 2),
             (gap1 + 12, deck_y + 30), (gap1 - 26, deck_y + 38)], (60, 62, 70))
    # explosion burst over the gap: an irregular fireball, no spokes
    cx, cy = x + w // 2, deck_y - 18
    for bx, by, r, col in (
            (cx - 26, cy + 6, 26, ORANGE), (cx + 24, cy + 8, 24, ORANGE),
            (cx, cy - 12, 30, FIRE), (cx - 10, cy - 2, 20, (255, 220, 120)),
            (cx + 14, cy - 16, 16, (255, 220, 120)),
            (cx - 34, cy - 14, 14, FIRE), (cx + 36, cy - 6, 12, FIRE)):
        cv.circle(bx, by, r, col)
    # smoke plumes
    for sx, sy, r in ((cx - 70, deck_y - 46, 26), (cx - 46, deck_y - 66, 30),
                      (cx + 58, deck_y - 52, 28), (cx + 84, deck_y - 30, 20)):
        cv.circle(sx, sy, r, SMOKE)
        cv.circle(sx - 8, sy - 6, r - 8, (170, 170, 168))
    # waves
    for wx in range(x + 20, x + w - 20, 46):
        cv.line(wx, y + 216, wx + 24, y + 216, (150, 190, 205), 2)
    # caption strip
    cv.fill_rect(x, y + h - 48, w, 48, NAVY)
    cv.text_center(W // 2, y + h - 42,
                   "KERCH BRIDGE HIT - UKRAINE STRIKES, ROAD SPAN COLLAPSES", 2, WHITE)
    cv.text_center(W // 2, y + h - 22,
                   "RUSSIA HITS TWO KYIV BRIDGES IN REPLY", 2, GOLD)
    cv.border(x, y, w, h, INK, 2)


# ------------------------------------------------- small panel: Hormuz
def draw_hormuz(cv, x, y, w, h):
    cv.vgrad(x, y, w, 100, (170, 200, 220), (215, 228, 235))
    cv.fill_rect(x, y + 100, w, h - 100, SEA)
    # aircraft carrier silhouette in the distance, hull on the sea line
    cv.fill_rect(x + 190, y + 92, 170, 12, (70, 78, 86))
    cv.fill_rect(x + 300, y + 70, 34, 22, (70, 78, 86))
    cv.fill_rect(x + 306, y + 60, 6, 12, (70, 78, 86))
    # oil tanker, foreground
    hx, hy = x + 24, y + 96
    cv.poly([(hx, hy), (hx + 220, hy), (hx + 200, hy + 34),
             (hx + 16, hy + 34)], (52, 56, 62))
    cv.fill_rect(hx + 8, hy + 34, 200, 6, RED)  # waterline
    cv.fill_rect(hx + 150, hy - 26, 34, 26, (210, 210, 205))  # bridge block
    cv.fill_rect(hx + 190, hy - 34, 16, 34, (200, 60, 45))   # funnel
    cv.circle(hx + 198, hy - 44, 12, SMOKE)
    cv.circle(hx + 206, hy - 54, 15, (170, 170, 168))
    # flames on the tanker deck
    cv.poly([(hx + 82, hy), (hx + 100, hy), (hx + 91, hy - 24)], FIRE)
    cv.poly([(hx + 88, hy), (hx + 96, hy), (hx + 92, hy - 14)], (255, 230, 130))
    cv.poly([(hx + 112, hy), (hx + 124, hy), (hx + 118, hy - 16)], FIRE)
    # waves
    for wx in range(x + 12, x + w - 12, 40):
        cv.line(wx, y + 116, wx + 22, y + 116, (150, 190, 205), 2)
    cv.fill_rect(x, y + h - 52, w, 52, NAVY)
    cv.text_center(x + w // 2, y + h - 50, "STRAIT OF HORMUZ", 2, WHITE)
    cv.text_center(x + w // 2, y + h - 33, "TANKERS HIT BY MINES", 2, GOLD)
    cv.text_center(x + w // 2, y + h - 16, "3RD US CARRIER ARRIVES", 2, GOLD)
    cv.border(x, y, w, h, INK, 2)


# ------------------------------------------------- small panel: APEC Shenzhen
def draw_apec(cv, x, y, w, h):
    cv.vgrad(x, y, w, 118, (140, 170, 205), (225, 232, 238))
    # Shenzhen skyline
    base = y + 118
    towers = [(x + 18, 58), (x + 62, 84), (x + 112, 44), (x + 160, 70),
              (x + 208, 52), (x + 252, 88), (x + 296, 62), (x + 336, 78)]
    for tx, th in towers:
        cv.fill_rect(tx, base - th, 34, th, (88, 104, 126))
        for wy in range(base - th + 8, base - 6, 12):
            cv.fill_rect(tx + 5, wy, 24, 4, (200, 215, 225))
    cv.fill_rect(x, base, w, 4, (70, 82, 100))
    # three flag poles: China, USA, Russia
    flags = [
        ((205, 40, 40), "CN"),
        ((60, 80, 160), "US"),
        ((220, 220, 220), "RU"),
    ]
    for i, (col, _lab) in enumerate(flags):
        fx = x + 96 + i * 100
        cv.fill_rect(fx, y + 14, 3, 62, DARK)
        cv.fill_rect(fx + 3, y + 14, 52, 30, col)
        if i == 0:  # China: gold stars
            cv.circle(fx + 14, y + 24, 4, GOLD)
            cv.circle(fx + 28, y + 20, 2, GOLD)
            cv.circle(fx + 30, y + 30, 2, GOLD)
        if i == 1:  # USA: stripes
            for s in range(5):
                cv.fill_rect(fx + 3, y + 18 + s * 6, 52, 2, WHITE)
            cv.fill_rect(fx + 3, y + 14, 22, 14, NAVY)
        if i == 2:  # Russia: blue + red bands
            cv.fill_rect(fx + 3, y + 24, 52, 10, (40, 80, 180))
            cv.fill_rect(fx + 3, y + 34, 52, 10, RED)
    cv.fill_rect(x, y + h - 52, w, 52, NAVY)
    cv.text_center(x + w // 2, y + h - 50, "APEC SHENZHEN", 2, WHITE)
    cv.text_center(x + w // 2, y + h - 33, "TRUMP, XI AND PUTIN", 2, GOLD)
    cv.text_center(x + w // 2, y + h - 16, "TO MEET THURSDAY", 2, GOLD)
    cv.border(x, y, w, h, INK, 2)


# ---------------------------------------------- small panel: Rwanda hub
def draw_rwanda(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h - 52, (214, 228, 205))
    # five member-state flag chips
    chips = [
        ((0, 0, 0), (205, 0, 0), (255, 205, 0)),      # Germany
        ((200, 20, 40), (255, 255, 255), (200, 20, 40)),  # Denmark (bands)
        ((205, 0, 0), (255, 255, 255), (205, 0, 0)),  # Austria
        ((40, 90, 180), (255, 255, 255), (40, 90, 180)),  # Greece
        ((175, 30, 40), (255, 255, 255), (35, 70, 160)),  # Netherlands
    ]
    for i, (c1, c2, c3) in enumerate(chips):
        fx = x + 22 + i * 68
        cv.fill_rect(fx, y + 22, 56, 12, c1)
        cv.fill_rect(fx, y + 34, 56, 12, c2)
        cv.fill_rect(fx, y + 46, 56, 12, c3)
        cv.border(fx, y + 22, 56, 36, INK, 1)
    # arrow from the flags down to Rwanda
    cv.line(x + w // 2, y + 66, x + w // 2, y + 96, RED, 3)
    cv.poly([(x + w // 2 - 9, y + 88), (x + w // 2 + 9, y + 88),
             (x + w // 2, y + 104)], RED)
    # Rwanda pin + label
    cv.circle(x + w // 2, y + 108, 8, RED)
    cv.circle(x + w // 2, y + 108, 3, WHITE)
    cv.text(x + w // 2 + 14, y + 102, "RWANDA", 1, INK)
    cv.fill_rect(x, y + h - 52, w, 52, NAVY)
    cv.text_center(x + w // 2, y + h - 50, "EU RETURN HUB", 2, WHITE)
    cv.text_center(x + w // 2, y + h - 33, "FIVE STATES PLAN", 2, GOLD)
    cv.text_center(x + w // 2, y + h - 16, "RWANDA CENTRE", 2, GOLD)
    cv.border(x, y, w, h, INK, 2)


# ---------------------------------------------- small panel: Vulcan rocket
def draw_vulcan(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h - 52, (14, 18, 34))
    # stars
    for sx, sy in ((x + 30, y + 16), (x + 90, y + 30), (x + 150, y + 12),
                   (x + 220, y + 26), (x + 300, y + 14), (x + 350, y + 40),
                   (x + 60, y + 60), (x + 260, y + 58), (x + 330, y + 70)):
        cv.circle(sx, sy, 2, WHITE)
    # rocket body
    rx = x + w // 2
    cv.poly([(rx - 12, y + 78), (rx + 12, y + 78), (rx + 12, y + 30),
             (rx, y + 12), (rx - 12, y + 30)], (225, 228, 232))
    cv.fill_rect(rx - 12, y + 78, 24, 6, RED)
    cv.poly([(rx - 12, y + 78), (rx - 24, y + 96), (rx - 12, y + 92)], RED)
    cv.poly([(rx + 12, y + 78), (rx + 24, y + 96), (rx + 12, y + 92)], RED)
    cv.circle(rx, y + 48, 5, (90, 140, 200))
    # flame and smoke trail
    cv.poly([(rx - 8, y + 86), (rx + 8, y + 86), (rx, y + 118)], FIRE)
    cv.poly([(rx - 4, y + 86), (rx + 4, y + 86), (rx, y + 104)], (255, 230, 130))
    # debris: falling satellite pieces
    for dx, dy, r in ((x + 60, y + 92, 6), (x + 96, y + 108, 4),
                      (x + 300, y + 100, 5), (x + 330, y + 78, 4)):
        cv.fill_rect(dx - r, dy - 2, r * 2, 4, (180, 185, 190))
        cv.fill_rect(dx - 2, dy - r, 4, r * 2, (140, 145, 150))
    cv.fill_rect(x, y + h - 52, w, 52, NAVY)
    cv.text_center(x + w // 2, y + h - 50, "VULCAN ROCKET FAILS", 2, WHITE)
    cv.text_center(x + w // 2, y + h - 33, "40 AMAZON SATELLITES", 2, GOLD)
    cv.text_center(x + w // 2, y + h - 16, "LOST IN FLIGHT", 2, GOLD)
    cv.border(x, y, w, h, INK, 2)


# ------------------------------------------------------------------ build
def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_hero(cv, 8, 108, 784, 288)
    draw_hormuz(cv, 8, 404, 384, 176)
    draw_apec(cv, 408, 404, 384, 176)
    draw_rwanda(cv, 8, 588, 384, 176)
    draw_vulcan(cv, 408, 588, 384, 176)
    cv.text_center(W // 2, 774, "FIVE STORIES FROM TUESDAY 17 NOVEMBER 2026", 1, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build(), path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
