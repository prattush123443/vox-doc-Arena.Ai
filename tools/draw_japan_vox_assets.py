#!/usr/bin/env python3
"""Draw exact, transparent Vox-style graphics that should not be AI-generated."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "projects" / "japan-savings-habits" / "elements" / "cut"
FONT = ROOT / "projects" / "japan-savings-habits" / "assets" / "fonts" / "NotoSansDevanagari.ttf"
INK = (37, 43, 55, 255)
GOLD = (218, 166, 61, 255)
CREAM = (244, 235, 215, 255)
SAGE = (127, 151, 108, 255)
TERRA = (194, 102, 75, 255)
NAVY = (48, 63, 83, 255)


def save_japan_map():
    im = Image.new("RGBA", (620, 720), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Simplified archipelago silhouette; intentionally schematic, not a border map.
    hokkaido = [(380, 65), (440, 42), (505, 68), (530, 110), (500, 152), (440, 160), (395, 132), (365, 100)]
    honshu = [(325, 145), (365, 155), (390, 205), (382, 250), (350, 287), (333, 330), (308, 370), (285, 421), (260, 457), (238, 440), (252, 392), (260, 350), (278, 308), (284, 266), (300, 225), (300, 183)]
    shikoku = [(238, 430), (275, 429), (292, 448), (274, 468), (242, 464), (224, 448)]
    kyushu = [(180, 413), (217, 426), (224, 465), (205, 510), (181, 535), (155, 516), (160, 479), (145, 452)]
    islands = [(128, 575), (151, 584), (160, 596), (145, 604), (124, 594)]
    for poly in (hokkaido, honshu, shikoku, kyushu, islands):
        d.polygon(poly, fill=SAGE, outline=INK, width=8)
    # Restrained highlight strokes make the silhouette read as illustrated cut-out art.
    d.line([(387, 99), (433, 75), (482, 87)], fill=(178, 194, 151, 255), width=7)
    d.line([(322, 175), (340, 230), (321, 285), (300, 340), (276, 398)], fill=(178, 194, 151, 255), width=7)
    im.save(OUT / "11-japan-map.png")


def save_kintsugi_bowl():
    im = Image.new("RGBA", (620, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # A broad ceramic bowl with a visible interior rim.
    d.polygon([(94, 171), (526, 171), (497, 304), (449, 376), (380, 418), (240, 418), (171, 376), (123, 304)], fill=(52, 57, 67, 255), outline=INK, width=10)
    d.ellipse((76, 91, 544, 241), fill=(202, 181, 147, 255), outline=INK, width=10)
    d.ellipse((119, 112, 501, 216), fill=(57, 61, 69, 255), outline=INK, width=7)
    # Gold repair seams, drawn as exact graphic strokes (not pseudo-text).
    crack = [(164, 143), (212, 170), (196, 202), (252, 228), (239, 263), (291, 289), (274, 326), (314, 367), (300, 412)]
    d.line(crack, fill=INK, width=19, joint="curve")
    d.line(crack, fill=GOLD, width=11, joint="curve")
    crack2 = [(352, 126), (331, 163), (364, 188), (341, 225), (389, 253), (373, 291), (416, 317), (401, 355)]
    d.line(crack2, fill=INK, width=17, joint="curve")
    d.line(crack2, fill=GOLD, width=9, joint="curve")
    d.arc((100, 330, 520, 452), 5, 175, fill=(114, 125, 139, 255), width=8)
    im.save(OUT / "12-kintsugi-bowl.png")


def save_mending_kit():
    im = Image.new("RGBA", (600, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cloth = [(104, 176), (446, 118), (520, 344), (176, 405)]
    d.polygon(cloth, fill=(202, 128, 91, 255), outline=INK, width=9)
    d.line([(145, 207), (463, 169)], fill=(229, 182, 140, 255), width=8)
    # stitched patch
    d.rounded_rectangle((260, 209, 380, 315), radius=16, fill=(130, 151, 111, 255), outline=INK, width=7)
    for x in range(270, 380, 19):
        d.line([(x, 220), (x + 6, 228)], fill=CREAM, width=4)
        d.line([(x, 294), (x + 6, 302)], fill=CREAM, width=4)
    # Needle with thread, kept clear of the cutout edge.
    d.line([(169, 120), (405, 44)], fill=INK, width=13)
    d.line([(173, 116), (405, 44)], fill=(186, 193, 197, 255), width=6)
    d.ellipse((397, 36, 416, 55), outline=INK, width=5)
    d.arc((352, 31, 474, 163), 25, 210, fill=TERRA, width=6)
    im.save(OUT / "13-mending-kit.png")


def save_calendar():
    im = Image.new("RGBA", (420, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((42, 38, 378, 482), radius=28, fill=CREAM, outline=INK, width=10)
    d.rounded_rectangle((42, 38, 378, 154), radius=28, fill=TERRA, outline=INK, width=10)
    d.rectangle((42, 114, 378, 154), fill=TERRA)
    d.line((42, 151, 378, 151), fill=INK, width=8)
    for x in (132, 288):
        d.rounded_rectangle((x - 12, 22, x + 12, 116), radius=12, fill=GOLD, outline=INK, width=5)
    # Blank days are decorative; only the narrated date is exact and legible.
    for y in (214, 286, 358):
        for x in (106, 184, 262, 340):
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(172, 179, 169, 255))
    d.ellipse((230, 324, 369, 463), outline=TERRA, width=9)
    font = ImageFont.truetype(str(FONT), 98)
    text = "28"
    box = d.textbbox((0, 0), text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text((299 - tw / 2, 391 - th / 2 - 8), text, font=font, fill=INK)
    im.save(OUT / "20-calendar28.png")


def save_bar(filename: str, amount: int, label: str, color):
    im = Image.new("RGBA", (300, 650), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    baseline = 575
    bar_h = int(410 * amount / 3000)
    left, right, top = 82, 218, baseline - bar_h
    # A true zero-based bar with a shared zero-axis, baseline, and exact amount label.
    # The vertical axis preserves a consistent crop box even for the ₹500 bar,
    # whose zero-based fill is intentionally much shorter than the others.
    d.line((32, 95, 32, baseline + 2), fill=(112, 106, 93, 190), width=4)
    d.line((32, baseline + 2, 268, baseline + 2), fill=INK, width=5)
    d.rounded_rectangle((left, top, right, baseline), radius=13, fill=color, outline=INK, width=7)
    d.line((left + 14, top + 15, right - 14, top + 15), fill=(255, 247, 223, 225), width=6)
    font = ImageFont.truetype(str(FONT), 36)
    value = f"₹{amount:,}"
    box = d.textbbox((0, 0), value, font=font)
    tw = box[2] - box[0]
    pill = (150 - tw / 2 - 10, max(17, top - 61), 150 + tw / 2 + 10, max(17, top - 61) + 48)
    d.rounded_rectangle(pill, radius=11, fill=CREAM, outline=INK, width=3)
    d.text((150 - tw / 2, pill[1] + 3), value, font=font, fill=INK, stroke_width=0)
    im.save(OUT / filename)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    save_japan_map()
    save_kintsugi_bowl()
    save_mending_kit()
    save_calendar()
    save_bar("14-bar-kakeibo.png", 2000, "काकेबो", GOLD)
    save_bar("15-bar-food.png", 2500, "खाना", SAGE)
    save_bar("16-bar-pause.png", 3000, "खरीद", TERRA)
    save_bar("17-bar-lunch.png", 3000, "टिफ़िन", NAVY)
    save_bar("18-bar-dinner.png", 2000, "रात", GOLD)
    save_bar("19-bar-duplicate.png", 500, "सामान", SAGE)
    print(f"wrote code-drawn graphics to {OUT}")


if __name__ == "__main__":
    main()
