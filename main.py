"""Sum up 24 November's world news in one image.

A standard-library-only Python program that draws an English newspaper
front page for Tuesday 24 November 2026 and writes it as a deterministic
1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
No network, no randomness: two runs write exactly the same bytes.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (176, 32, 32)
GRAY = (110, 105, 95)
SMOKE = (168, 162, 150)
ORANGE = (228, 116, 28)
YELLOW = (242, 178, 44)
WHITE = (250, 248, 242)


class Canvas:
    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        self.px = bytearray(color) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def triangle(self, pts, color):
        (x1, y1), (x2, y2), (x3, y3) = pts
        area = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        if area == 0:
            return
        minx = max(0, min(x1, x2, x3))
        maxx = min(self.w - 1, max(x1, x2, x3))
        miny = max(0, min(y1, y2, y3))
        maxy = min(self.h - 1, max(y1, y2, y3))
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                d1 = (xx - x1) * (y2 - y1) - (x2 - x1) * (yy - y1)
                d2 = (xx - x2) * (y3 - y2) - (x3 - x2) * (yy - y2)
                d3 = (xx - x3) * (y1 - y3) - (x1 - x3) * (yy - y3)
                if (d1 >= 0 and d2 >= 0 and d3 >= 0) or \
                   (d1 <= 0 and d2 <= 0 and d3 <= 0):
                    self.set(xx, yy, color)

    def to_png(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(tag, data):
            out = struct.pack(">I", len(data)) + tag + data
            out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


# 5x7 bitmap font, drawn for this entry. Each glyph is 7 rows of 5 pixels.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "%": ("#...#", "#..#.", "....#", "...#.", "..#..", ".#...", "#..#."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "#":
                    cv.rect(cx + col_i * scale, y + row_i * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(cv, y, s, scale, color):
    x = (W - text_width(s, scale)) // 2
    return draw_text(cv, x, y, s, scale, color)


def wrap(s, chars):
    lines = []
    cur = ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if len(trial) <= chars:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(cv, x, y, s, scale, color, max_w, line_h):
    chars = max(1, max_w // (6 * scale))
    for i, line in enumerate(wrap(s, chars)):
        draw_text(cv, x, y + i * line_h, line, scale, color)
    return y + len(wrap(s, chars)) * line_h


def draw_refinery(cv, x, y):
    """Simple refinery under fire: towers, pipes, flames and smoke."""
    ground = y + 118
    cv.hline(x, ground, 280, INK, 3)
    # three distillation towers
    for i, (tx, th) in enumerate(((18, 86), (96, 104), (182, 74))):
        cv.rect(x + tx, ground - th, 34, th, INK)
        cv.rect(x + tx - 4, ground - th, 42, 6, INK)
        for shelf in range(ground - th + 16, ground - 8, 16):
            cv.hline(x + tx - 3, shelf, 40, PAPER, 2)
    # connecting pipes
    cv.hline(x + 40, ground - 60, 190, INK, 5)
    cv.hline(x + 40, ground - 34, 220, INK, 5)
    # flames on the middle and first towers
    cv.triangle(((x + 108, ground - 104), (x + 126, ground - 140),
                 (x + 144, ground - 104)), RED)
    cv.triangle(((x + 116, ground - 104), (x + 126, ground - 126),
                 (x + 136, ground - 104)), ORANGE)
    cv.triangle(((x + 121, ground - 104), (x + 126, ground - 116),
                 (x + 131, ground - 104)), YELLOW)
    cv.triangle(((x + 24, ground - 86), (x + 35, ground - 112),
                 (x + 46, ground - 86)), RED)
    cv.triangle(((x + 29, ground - 86), (x + 35, ground - 100),
                 (x + 41, ground - 86)), ORANGE)
    # smoke clouds
    for cx, cy, r in ((150, ground - 128, 16), (178, ground - 140, 20),
                      (210, ground - 130, 14), (236, ground - 142, 11)):
        cv.circle(x + cx, cy, r, SMOKE)


def story(cv, x, y, w, headline, body):
    yy = draw_paragraph(cv, x, y, headline, 3, INK, w, 27)
    yy += 6
    draw_paragraph(cv, x, yy, body, 2, INK, w, 19)


def build():
    cv = Canvas(W, H, PAPER)
    m = 48  # margin
    # --- masthead ---
    draw_centered(cv, 30, "TUESDAY 24 NOVEMBER 2026 - ONE DAY, ONE PICTURE", 2, GRAY)
    cv.hline(m, 62, W - 2 * m, INK, 3)
    draw_centered(cv, 82, "THE WORLD IN ONE DAY", 7, INK)
    draw_centered(cv, 148, "ALL THE DAY'S WORLD NEWS, DRAWN BY A PROGRAM", 2, GRAY)
    cv.hline(m, 182, W - 2 * m, INK, 5)
    cv.hline(m, 191, W - 2 * m, INK, 2)

    # --- lead story ---
    draw_text(cv, m, 208, "RUSSIA - UKRAINE WAR", 2, RED)
    yy = draw_paragraph(cv, m, 234, "PUTIN VOWS RETALIATION AS REFINERY "
                        "STRIKES CUT RUSSIAN OUTPUT BY 45%", 5, INK,
                        W - 2 * m, 44)
    body = ("MOSCOW - President Vladimir Putin told a Kremlin meeting on "
            "Tuesday that retaliation was unavoidable, as Ukrainian "
            "long-range drones kept hitting Russian oil refineries. "
            "Industry estimates put refining runs down about 45 percent "
            "since late October, and the energy truce proclaimed last "
            "month has collapsed.")
    draw_paragraph(cv, m, yy + 10, body, 2, INK, 600, 20)
    draw_refinery(cv, 676, yy - 6)
    draw_text(cv, 676, yy + 122, "A REFINERY UNDER FIRE", 1, GRAY)

    # --- four stories, two by two ---
    top = 556
    cv.hline(m, top - 14, W - 2 * m, INK, 2)
    cv.vline(512, top + 2, 300, GRAY, 1)
    colw = 448
    rx = m + colw + 32
    story(cv, m, top, colw, "ICJ ROHINGYA RULING BACKED BY 14 STATES",
          "Britain, Spain, Canada and Australia led fourteen countries "
          "recognising the World Court's ruling that Myanmar committed "
          "genocide against the Rohingya people.")
    story(cv, rx, top, colw, "UN: AGREE AI RULES WITHIN A YEAR",
          "UN chief Antonio Guterres urged member states to build a "
          "multilateral framework for AI risks within a year, as talks "
          "on regulating killer robots stalled.")
    row2 = top + 158
    story(cv, m, row2, colw, "RIYADH'S TALLEST TOWER HIT AGAIN, 11 HURT",
          "Houthi drones struck the Saudi capital's tallest skyscraper "
          "for the second time in under a week, injuring eleven people, "
          "two of them Indian workers.")
    story(cv, rx, row2, colw, "IRAN REJECTS TALKS; TANKERS HIT MINES",
          "Tehran ruled out talks until Washington meets its seven "
          "conditions, as three oil tankers hit mines and caught fire "
          "in the Strait of Hormuz.")

    # --- markets band ---
    band_y = 884
    cv.rect(m, band_y, W - 2 * m, 40, INK)
    draw_centered(cv, band_y + 13,
                  "MARKETS RALLY: S&P +4.7%  NASDAQ +6.5%  NIKKEI +3.9%  "
                  "DAX +2.2%  BRENT $86.7", 2, WHITE)

    # --- briefs ---
    by = 940
    draw_text(cv, m, by, "IN BRIEF", 2, RED)
    briefs_left = [
        "US YET TO APPROVE 60 PATRIOT MISSILES FOR UKRAINE",
        "M5.6 EARTHQUAKE STRIKES NEPAL NEAR THE CHINA BORDER",
        "CHINA OPENS TIANGONG STATION TO A FOREIGN ASTRONAUT",
    ]
    briefs_right = [
        "MEASLES CLAIMS A NINTH LIFE IN PENNSYLVANIA",
        "LUKASHENKO OFFERS TO FLY ZELENSKYY TO MOSCOW",
    ]
    for i, b in enumerate(briefs_left):
        draw_text(cv, m + 130, by + i * 15, "- " + b, 1, INK)
    for i, b in enumerate(briefs_right):
        draw_text(cv, 640, by + i * 15, "- " + b, 1, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = build().to_png()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
