#!/usr/bin/env python3
"""Storyboard the approved Hindi narration into animated cut-out Vox scenes.

Uses upstream render.py's `pop`, `slideL`, `slideR`, `rise`, code-drawn clocks,
red cross-outs, exact text labels and complex-script ASS burn-in.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "japan-savings-habits"
SENTENCES_FILE = PROJECT / "SENTENCES.tsv"
WORDS_FILE = PROJECT / "WORDS.tsv"
OUT = PROJECT / "SCENES.tsv"

ASSET_LABELS = {
    "phone": "UPI",
    "ledger": "कॉपी",
    "writing_hand": "लिखिए",
    "coins": "खर्च",
    "fridge": "फ्रिज",
    "produce": "खाना",
    "shopping_cart": "खरीद",
    "tiffin": "टिफ़िन",
    "meal_prep": "तैयारी",
    "pantry": "सामान",
    "japan_map": "जापान के द्वीप",
    "kintsugi_bowl": "किंत्सुगी",
    "mending_kit": "मरम्मत",
    "calendar28": "28 तारीख",
    "chai_snack": "चाय • नाश्ता",
    "food_waste": "खाना बर्बाद",
    "takeout_bag": "बाहर का खाना",
    "idli_lunch": "इडली • घर का खाना",
    "donation_bag": "दोबारा इस्तेमाल",
    "mending_shirt": "कपड़े की मरम्मत",
    "shoe_repair": "जूते की मरम्मत",
    "wood_repair": "लकड़ी की मरम्मत",
    "budget_closeup": "घर का हिसाब",
    "bar_kakeibo": "कॉपी",
    "bar_food": "खाना",
    "bar_pause": "ऑनलाइन",
    "bar_lunch": "दोपहर",
    "bar_dinner": "रात",
    "bar_duplicate": "दोहरी खरीद",
}
ASSET_SIZES = {
    "phone": .48, "ledger": .52, "writing_hand": .42, "coins": .43,
    "fridge": .53, "produce": .44, "shopping_cart": .44, "tiffin": .47,
    "meal_prep": .47, "pantry": .48, "japan_map": .48, "kintsugi_bowl": .48,
    "mending_kit": .43, "calendar28": .45,
    "chai_snack": .43, "food_waste": .45, "takeout_bag": .47,
    "idli_lunch": .45, "donation_bag": .45, "mending_shirt": .49,
    "shoe_repair": .50, "wood_repair": .49, "budget_closeup": .49,
}
SECTION_TITLES = {
    "hook": "पैसा गया कहाँ?",
    "kakeibo": "आदत 1 • काकेबो",
    "mottainai": "आदत 2 • मोत्ताइनाई",
    "pause": "आदत 3 • 24 घंटे का विराम",
    "interlude": "एक पल सोचिए",
    "bento": "आदत 4 • बेंटो और थर्मस",
    "prep": "आदत 5 • हफ्ते की तैयारी",
    "danshari": "आदत 6 • दनशारी",
    "kintsugi": "आदत 7 • किंत्सुगी",
    "math": "असली हिसाब",
    "outro": "इस हफ्ते एक बदलाव",
}

# These ranges become one animated shot so a calculation can build on screen.
SPECIAL_GROUPS = [
    (16, 19, "questions"),
    (25, 25, "cashless_study"),
    (26, 26, "cashless_effect"),
    (27, 27, "cashless_caveat"),
    (28, 29, "kakeibo_example"),
    (46, 47, "food_example"),
    (59, 61, "pause_example"),
    (73, 76, "bento_example"),
    (88, 90, "prep_example"),
    (118, 123, "total_chart"),
    (133, 134, "outro_actions"),
]


@dataclass
class Event:
    cue_pos: int
    cue: str
    kind: str
    what: str
    x: float
    y: float
    size: float | None
    motion: str
    out: str
    label: str
    serial: int


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


sentences = read_tsv(SENTENCES_FILE)
word_rows = read_tsv(WORDS_FILE)
words_by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
line_global_start: dict[str, int] = {}
word_global: dict[tuple[str, int], int] = {}
for row in word_rows:
    words_by_line[row["line"]].append(row)
for line_id in words_by_line:
    words_by_line[line_id].sort(key=lambda r: int(r["i"]))
    line_global_start[line_id] = len(word_global)
    for row in words_by_line[line_id]:
        word_global[(line_id, int(row["i"]))] = len(word_global)


def token_text(row: dict[str, str]) -> str:
    return row["word"].strip()


def cue_clean(token: str) -> str:
    # The upstream find() strips danda/ASCII sentence punctuation but searches
    # by substring, so remove surrounding quotes while retaining ₹/Devanagari.
    token = re.sub(r"[।?,.!]", "", token.strip())
    return re.sub(r"^[\"'“”‘’()\[\]{}]+|[\"'“”‘’()\[\]{}]+$", "", token)


def get_cue(line_id: str, terms: tuple[str, ...] | list[str] = (), start_at: int = 0) -> tuple[int, str]:
    rows = words_by_line[line_id]
    lowered_terms = tuple(t.lower() for t in terms)
    for row in rows[start_at:]:
        token = token_text(row)
        cleaned = cue_clean(token)
        lower = token.lower()
        if lowered_terms and any(term in lower or term in cleaned.lower() for term in lowered_terms):
            return int(row["i"]), cleaned or token
    if start_at < len(rows):
        row = rows[start_at]
        return int(row["i"]), cue_clean(token_text(row))
    row = rows[-1]
    return int(row["i"]), cue_clean(token_text(row))


def cue_for_text(line_id: str, needle: str) -> tuple[int, str]:
    rows = words_by_line[line_id]
    for row in rows:
        token = token_text(row)
        if needle in token:
            return int(row["i"]), cue_clean(token)
    return get_cue(line_id)


def global_position(line_id: str, word_index: int) -> int:
    return word_global[(line_id, word_index)]


def event(line_id: str, cue_terms: tuple[str, ...] | list[str], kind: str, what: str,
          x: float, y: float, size: float | None = None, motion: str = "pop",
          out: str = "-", label: str = "", serial: int = 0, cue_override: str | None = None) -> Event:
    idx, cue = get_cue(line_id, cue_terms)
    pos = global_position(line_id, idx)
    if cue_override is not None:
        cue = cue_clean(cue_override)
    normalized_out = cue_clean(out) if out != "-" else out
    return Event(pos, cue, kind, what, x, y, size, motion, normalized_out, label or "-", serial)


def text_event(line_id: str, cue_terms: tuple[str, ...] | list[str], style: str, text: str,
               x: float = .50, y: float = .86, out: str = "-", serial: int = 0) -> Event:
    return event(line_id, cue_terms, "text", style, x, y, None, "pop", out, text, serial)


def image_event(line_id: str, asset: str, cue_terms: tuple[str, ...] | list[str],
                x: float = .50, y: float = .54, size: float | None = None,
                motion: str = "pop", label: str | None = None, serial: int = 0) -> Event:
    return event(line_id, cue_terms, "img", asset, x, y,
                 size if size is not None else ASSET_SIZES.get(asset, .46), motion, "-",
                 label or ASSET_LABELS.get(asset, "-"), serial)


def row(scene_id: str, cue: str, kind: str, what: str, x: float | None = None,
        y: float | None = None, size: float | None = None, motion: str = "-",
        out: str = "-", label: str = "-") -> list[str]:
    return [scene_id, cue, kind, what,
            "-" if x is None else f"{x:.3f}",
            "-" if y is None else f"{y:.3f}",
            "-" if size is None else f"{size:.3f}",
            motion, out, label]


def line_for(sentence: dict[str, str]) -> str:
    return sentence["id"]


def primary_assets(section: str, text: str) -> list[tuple[str, tuple[str, ...]]]:
    t = text.lower()
    # Concrete, topic-specific cut-outs take priority over generic symbols.
    if "अट्ठाईस" in t or "28" in t:
        return [("calendar28", ("अट्ठाईस", "28"))]
    if section == "hook" and "चाय" in t:
        return [("chai_snack", ("चाय", "नाश्ता")), ("phone", ("डिजिटल", "भुगतान"))]
    if "upi" in t or "फोन" in t or "लेन-देन" in t or "डिजिटल भुगतान" in t:
        return [("phone", ("upi", "फोन", "लेन-देन", "डिजिटल"))]
    if "1904" in t or "हानी मोतोको" in t or "जापानी पत्रकार" in t:
        return [("japan_map", ("जापानी", "जापान", "1904")), ("ledger", ("बही", "तरीके"))]
    if "काकेबो" in t or "कॉपी" in t or "हिसाब" in t or "लिखे हुए" in t or "दर्ज" in t:
        return [("ledger", ("काकेबो", "कॉपी", "हिसाब", "लिखे", "दर्ज")), ("writing_hand", ("लिख", "पन्नों", "नज़र"))]
    if section == "mottainai" and any(k in t for k in ("कूड़ेदान", "बर्बाद", "फेंक", "खराब", "बचा हुआ")):
        return [("food_waste", ("कूड़ेदान", "बर्बाद", "फेंक", "खराब", "बचा")), ("produce", ("सब्ज़ी", "खाना", "पैकेट"))]
    if section == "mottainai" and ("फ्रिज" in t or "रसोई" in t):
        return [("fridge", ("फ्रिज", "रसोई")), ("produce", ("खाना", "सब्ज़ी", "खराब"))]
    if section == "bento" and "इडली" in t:
        return [("tiffin", ("रोटी", "सब्ज़ी", "डिब्बा")), ("idli_lunch", ("इडली",))]
    if section == "prep" and any(k in t for k in ("मँगाया", "मँगाए", "बाहर से खाना", "ऑर्डर")):
        return [("takeout_bag", ("मँगाया", "मँगाए", "ऑर्डर", "बाहर")), ("meal_prep", ("खाना", "पकाना", "तैयार"))]
    if section == "danshari" and any(k in t for k in ("दान", "दोबारा इस्तेमाल", "किसी और")):
        return [("donation_bag", ("दान", "दोबारा", "किसी और"))]
    if section == "kintsugi":
        repair_assets: list[tuple[str, tuple[str, ...]]] = []
        if any(k in t for k in ("कपड़े", "फटना", "सिलना")):
            repair_assets.append(("mending_shirt", ("कपड़े", "फटना", "सिलना")))
        if "जूते" in t or "जूतों" in t:
            repair_assets.append(("shoe_repair", ("जूतों", "जूते", "देखभाल")))
        if "लकड़ी" in t:
            repair_assets.append(("wood_repair", ("लकड़ी", "ठीक")))
        if repair_assets:
            return repair_assets
        if any(k in t for k in ("किंत्सुगी", "टूटी", "उरुशी", "सोने", "चाँदी", "बर्तन", "वाबी-साबी")):
            return [("kintsugi_bowl", ("किंत्सुगी", "टूटी", "उरुशी", "सोने", "चाँदी", "वाबी-साबी"))]
        if any(k in t for k in ("मरम्मत", "कारीगर", "सुरक्षित")):
            return [("mending_kit", ("मरम्मत", "कारीगर", "सुरक्षित"))]
    if section == "math" and any(k in t for k in ("परिवार", "काल्पनिक घर")):
        return [("budget_closeup", ("परिवार", "घर", "काल्पनिक"))]
    if section == "outro" and any(k in t for k in ("आदत", "हिसाब", "कमाई", "बचत")):
        return [("budget_closeup", ("आदत", "हिसाब", "कमाई", "बचत"))]
    if "जापान" in t or "जापानी" in t:
        return [("japan_map", ("जापान", "जापानी"))]
    if any(k in t for k in ("खरीद", "ऑर्डर", "छूट", "इच्छा-सूची", "विराम", "गैर-ज़रूरी")):
        return [("shopping_cart", ("खरीद", "ऑर्डर", "छूट", "विराम", "इच्छा"))]
    if any(k in t for k in ("बेंटो", "डिब्बा", "दोपहर", "थर्मस", "टिफ़िन", "टिफिन")):
        return [("tiffin", ("बेंटो", "डिब्बा", "दोपहर", "थर्मस", "टिफ़िन", "टिफिन"))]
    if any(k in t for k in ("चने", "तैयार", "पकाना", "थकान", "चीला", "दाल")):
        return [("meal_prep", ("चने", "तैयार", "पकाना", "थकान", "चीला", "दाल"))]
    if any(k in t for k in ("दनशारी", "अलमारी", "सामान", "मसाला", "साबुन", "रैक")):
        return [("pantry", ("दनशारी", "अलमारी", "सामान", "मसाला", "साबुन", "रैक"))]
    if any(k in t for k in ("किंत्सुगी", "टूटी", "उरुशी", "सोने", "चाँदी", "बर्तन", "वाबी-साबी")):
        return [("kintsugi_bowl", ("किंत्सुगी", "टूटी", "उरुशी", "सोने", "चाँदी", "वाबी-साबी"))]
    if any(k in t for k in ("मरम्मत", "सिलना", "जूते", "कारीगर", "कपड़े")):
        return [("mending_kit", ("मरम्मत", "सिलना", "जूते", "कारीगर", "कपड़े")), ("kintsugi_bowl", ("जोड़", "बर्तन"))]
    if "₹" in t or "रकम" in t or "खर्च" in t or "बचत" in t:
        return [("coins", ("₹", "रकम", "खर्च", "बचत"))]
    defaults = {
        "hook": "phone", "kakeibo": "ledger", "mottainai": "produce",
        "pause": "shopping_cart", "interlude": "pantry", "bento": "tiffin",
        "prep": "meal_prep", "danshari": "pantry", "kintsugi": "kintsugi_bowl",
        "math": "coins", "outro": "ledger",
    }
    return [(defaults.get(section, "ledger"), ())]


def secondary_for(primary: str, section: str, text: str) -> list[tuple[str, tuple[str, ...]]]:
    t = text.lower()
    if primary == "phone" and any(k in t for k in ("खर्च", "रकम", "कॉपी", "बचत")):
        return [("coins", ("खर्च", "रकम", "बचत"))]
    if primary == "ledger" and any(k in t for k in ("लिख", "दर्ज", "पन्नों", "सवाल")):
        return [("writing_hand", ("लिख", "दर्ज", "पन्नों", "सवाल"))]
    if primary == "fridge":
        return [("produce", ("खाना", "सब्ज़ी", "खराब", "बचा"))]
    if primary == "produce" and "फ्रिज" in t:
        return [("fridge", ("फ्रिज",))]
    if primary == "shopping_cart" and "24 घंटे" in t:
        return [("coins", ("खरीद", "₹"))]
    if primary == "shopping_cart" and "छूट" in t:
        return [("pantry", ("अलमारी", "घर"))]
    if primary == "tiffin" and any(k in t for k in ("चाय", "थर्मस", "खर्च", "₹")):
        return [("coins", ("चाय", "खर्च", "₹"))]
    if primary == "meal_prep" and "टिफ़िन" in t:
        return [("tiffin", ("टिफ़िन",))]
    if primary == "pantry" and "₹" in t:
        return [("coins", ("₹",))]
    if primary == "kintsugi_bowl" and any(k in t for k in ("मरम्मत", "सिलना", "कारीगर")):
        return [("mending_kit", ("मरम्मत", "सिलना", "कारीगर"))]
    if primary == "coins" and section in ("kakeibo", "math"):
        return [("ledger", ("कॉपी", "हिसाब", "सूची"))]
    if primary == "ledger" and section == "outro":
        return [("shopping_cart", ("खरीद", "रोकिए"))]
    return []


def amount_text(text: str) -> str | None:
    values = re.findall(r"₹\s*[0-9][0-9,]*", text)
    if not values:
        return None
    if len(values) >= 2 and ("₹12,000" in text and "₹15,000" in text):
        return "₹12,000–₹15,000"
    return values[0].replace(" ", "")


def cue_terms_for_asset(asset: str) -> tuple[str, ...]:
    return {
        "phone": ("UPI", "फोन", "लेन-देन", "डिजिटल"),
        "ledger": ("काकेबो", "कॉपी", "बही", "हिसाब", "सूची", "लिखिए"),
        "writing_hand": ("लिख", "दर्ज", "पन्नों", "सवाल"),
        "coins": ("₹", "रकम", "खर्च", "बचत"),
        "fridge": ("फ्रिज", "रसोई"),
        "produce": ("सब्ज़ी", "खाना", "खराब", "बर्बाद", "पैकेट"),
        "shopping_cart": ("खरीद", "ऑर्डर", "छूट", "विराम", "इच्छा"),
        "tiffin": ("बेंटो", "डिब्बा", "दोपहर", "थर्मस"),
        "meal_prep": ("चने", "तैयार", "पकाना", "थकान", "चीला"),
        "pantry": ("दनशारी", "अलमारी", "सामान", "मसाला", "साबुन"),
        "japan_map": ("जापान", "जापानी", "1904"),
        "kintsugi_bowl": ("किंत्सुगी", "टूटी", "उरुशी", "सोने", "बर्तन"),
        "mending_kit": ("मरम्मत", "सिलना", "जूते", "कारीगर", "कपड़े"),
        "calendar28": ("अट्ठाईस", "28"),
        "chai_snack": ("चाय", "नाश्ता"),
        "food_waste": ("कूड़ेदान", "बर्बाद", "फेंक", "खराब", "बचा"),
        "takeout_bag": ("मँगाया", "मँगाए", "ऑर्डर", "बाहर"),
        "idli_lunch": ("इडली",),
        "donation_bag": ("दान", "दोबारा", "किसी और"),
        "mending_shirt": ("कपड़े", "फटना", "सिलना"),
        "shoe_repair": ("जूतों", "जूते", "देखभाल"),
        "wood_repair": ("लकड़ी", "ठीक"),
        "budget_closeup": ("परिवार", "घर", "हिसाब", "आदत"),
    }.get(asset, ())


def build_normal_group(group: list[dict[str, str]], scene_id: str, first_in_section: bool, section_seen: set[str]) -> list[list[str]]:
    first = group[0]
    first_id = line_for(first)
    rows = [row(scene_id, "@" + first_id, "bg", "paper")]
    events: list[Event] = []
    serial = 0
    if first["section"] not in section_seen:
        events.append(text_event(first_id, (), "TAG", SECTION_TITLES[first["section"]], .50, .08, serial=serial))
        serial += 1
        section_seen.add(first["section"])
    if first_id == "001":
        events.append(text_event(first_id, (), "KEY", "खर्च कहाँ गया?", .50, .88, serial=serial))
        serial += 1

    for line_offset, s in enumerate(group):
        line_id, text, section = s["id"], s["text"], s["section"]
        specs = primary_assets(section, text)
        if not specs:
            specs = [("ledger", ())]
        primary = specs[0][0]
        specs += secondary_for(primary, section, text)
        # A chapter scene should not be crowded: at most two bespoke objects.
        deduped: list[tuple[str, tuple[str, ...]]] = []
        for asset, terms in specs:
            if asset not in [a for a, _ in deduped]:
                deduped.append((asset, terms or cue_terms_for_asset(asset)))
        max_objects = 3 if len(words_by_line[line_id]) >= 24 or line_id == "109" else 2
        deduped = deduped[:max_objects]
        if len(deduped) == 1:
            positions = [(.50, .52, ASSET_SIZES.get(deduped[0][0], .46), "rise")]
        elif len(deduped) == 2:
            positions = [(.28, .55, min(.47, ASSET_SIZES.get(deduped[0][0], .45)), "slideL"),
                         (.72, .55, min(.47, ASSET_SIZES.get(deduped[1][0], .45)), "slideR")]
        else:
            positions = [(.18, .55, .36, "slideL"), (.50, .55, .34, "rise"), (.82, .55, .36, "slideR")]
        for (asset, terms), (x, y, size, motion) in zip(deduped, positions):
            cue_terms = terms if terms else cue_terms_for_asset(asset)
            events.append(image_event(line_id, asset, cue_terms, x, y, size, motion, serial=serial))
            serial += 1
            if asset == "japan_map":
                events.append(event(line_id, cue_terms, "pin", "जापान", .50, .50, .05,
                                    "pop", "-", "जापान", serial))
                serial += 1

        # The renderer/code carries exact numeric text; the artwork remains text-free.
        amt = amount_text(text)
        if amt:
            events.append(text_event(line_id, ("₹",), "NUM", amt, .50, .14, serial=serial))
            serial += 1
        elif re.search(r"\b(?:1904|2024|71|24|30|12|7)\b", text):
            match = re.search(r"\b(?:1904|2024|71|24|30|12|7)\b", text)
            if match:
                number = match.group(0)
                label = number
                if number == "71": label = "71"
                if number == "24" and "घंटे" in text: label = "24 घंटे"
                elif number == "30" and "दिन" in text: label = "30 दिन"
                elif number == "7" and "दिन" in text: label = "7 दिन"
                events.append(text_event(line_id, (number,), "NUM", label, .50, .14, serial=serial))
                serial += 1

        # Short, truthful caveats are emphasized without adding new claims.
        caveat = None
        cue = ()
        if "गारंटी" in text or ("संभव नहीं" in text and "₹" in text):
            caveat, cue = "गारंटी नहीं", ("नहीं",)
        elif "राष्ट्रीय औसत नहीं" in text:
            caveat, cue = "राष्ट्रीय औसत नहीं", ("औसत",)
        elif "प्राचीन" in text:
            caveat, cue = "प्राचीन परंपरा नहीं", ("प्राचीन",)
        elif "दो बार" in text:
            caveat, cue = "दो बार न जोड़ें", ("दो बार",)
        elif "सुरक्षा पहले" in text:
            caveat, cue = "सुरक्षा पहले", ("सुरक्षा",)
        elif "मासिक जोड़" in text and "नहीं" in text:
            caveat, cue = "मासिक रकम तय नहीं", ("मासिक",)
        elif "हर UPI उपयोगकर्ता" in text:
            caveat, cue = "हर उपयोगकर्ता नहीं", ("हर",)
        if caveat:
            events.append(text_event(line_id, cue, "KEY", caveat, .50, .86, serial=serial))
            serial += 1

        # Exact, code-drawn clock visuals for the waiting rule; no AI clock faces.
        if "24 घंटे" in text:
            events.append(event(line_id, ("24",), "clocks", "24", .50, .44, .026, "pop", "-", "24 घंटे", serial))
            serial += 1
        if "नहीं" in text and section == "pause" and any(k in text for k in ("ऑर्डर", "खरीद")):
            # A red cross marks only the non-essential purchase action.
            asset_x, asset_y = (.50, .55)
            events.append(event(line_id, ("नहीं",), "cross", "-", asset_x, asset_y, .34, "pop", "-", "-", serial))
            serial += 1

    # Sort within the shot so scene entries follow narration order. Equal cues
    # intentionally enter together as one visual beat.
    events.sort(key=lambda e: (e.cue_pos, e.serial))
    for e in events:
        rows.append(row(scene_id, e.cue, e.kind, e.what, e.x, e.y, e.size, e.motion, e.out, e.label))
    return rows


def special_scene(name: str, group: list[dict[str, str]], scene_id: str, section_seen: set[str]) -> list[list[str]]:
    first = group[0]
    first_id = first["id"]
    rows = [row(scene_id, "@" + first_id, "bg", "paper")]
    events: list[Event] = []
    serial = 0
    section = first["section"]
    if section not in section_seen:
        events.append(text_event(first_id, (), "TAG", SECTION_TITLES[section], .50, .08, serial=serial))
        serial += 1
        section_seen.add(section)

    by_num = {int(s["id"]): s for s in group}
    def add_img(line: int, asset: str, terms: tuple[str, ...], x: float, y: float, size: float, motion: str, label: str | None = None):
        nonlocal serial
        s = by_num[line]
        events.append(image_event(s["id"], asset, terms, x, y, size, motion, label, serial))
        serial += 1
    def add_txt(line: int, terms: tuple[str, ...], style: str, text: str, x: float, y: float, out: str = "-"):
        nonlocal serial
        s = by_num[line]
        events.append(text_event(s["id"], terms, style, text, x, y, out=out, serial=serial))
        serial += 1

    if name == "questions":
        add_img(16, "ledger", ("चार", "सवाल"), .50, .54, .35, "rise", "चार सवाल")
        add_txt(16, ("कुल", "आमदनी"), "TAG", "आमदनी कितनी?", .27, .32)
        add_txt(17, ("बचाना",), "TAG", "कितना बचाएँ?", .73, .32)
        add_txt(18, ("पैसा",), "TAG", "खर्च कहाँ?", .27, .67)
        add_txt(19, ("बदल",), "TAG", "अगले महीने क्या बदलें?", .73, .67)
    elif name == "cashless_study":
        add_img(25, "ledger", ("विश्लेषण", "शोधपत्रों"), .50, .55, .40, "rise", "संयुक्त विश्लेषण")
        add_txt(25, ("2024",), "NUM", "2024", .28, .16)
        add_txt(25, ("71",), "NUM", "71 शोधपत्र", .72, .16)
    elif name == "cashless_effect":
        add_img(26, "phone", ("डिजिटल", "भुगतान"), .30, .53, .42, "slideL", "डिजिटल भुगतान")
        add_img(26, "coins", ("खर्च", "औसत"), .72, .53, .38, "slideR", "खर्च का औसत असर")
        add_txt(26, ("छोटा",), "KEY", "औसत असर छोटा", .50, .86)
    elif name == "cashless_caveat":
        add_img(27, "phone", ("UPI", "उपयोगकर्ता"), .42, .53, .42, "rise", "UPI भुगतान")
        add_txt(27, ("हर",), "KEY", "हर उपयोगकर्ता नहीं", .68, .65)
    elif name == "kakeibo_example":
        add_img(28, "ledger", ("कॉपी", "दर्ज"), .30, .54, .48, "slideL", "खर्च की कॉपी")
        add_img(28, "coins", ("₹4,000",), .73, .55, .39, "rise", "छोटे खर्च")
        add_txt(28, ("₹4,000",), "NUM", "₹4,000", .50, .13)
        add_txt(29, ("आधे",), "KEY", "आधा कम", .30, .83)
        add_txt(29, ("₹2,000",), "NUM", "₹2,000", .72, .13)
    elif name == "food_example":
        add_img(46, "fridge", ("सूची", "खाना"), .28, .54, .47, "slideL", "खाने की सूची")
        add_img(46, "food_waste", ("फेंका", "नुकसान"), .72, .55, .41, "slideR", "खाने की बर्बादी")
        add_txt(46, ("₹2,500",), "NUM", "₹2,500", .50, .13)
        add_txt(47, ("औसत", "उदाहरण"), "KEY", "घर का रिकॉर्ड • औसत नहीं", .50, .86)
    elif name == "pause_example":
        add_img(59, "shopping_cart", ("ऑनलाइन", "खरीद"), .50, .55, .43, "rise", "दो खरीदारी")
        add_img(59, "coins", ("₹1,500",), .24, .52, .29, "slideL", "पहली खरीद")
        add_img(59, "coins", ("₹1,500",), .76, .52, .29, "slideR", "दूसरी खरीद")
        add_txt(59, ("₹1,500",), "NUM", "₹1,500 × 2", .50, .13, "₹3,000")
        add_txt(60, ("₹3,000",), "NUM", "₹3,000", .50, .13, "लेकिन")
        add_txt(61, ("बचत", "मत"), "KEY", "बाद में खरीदा? बचत नहीं", .50, .86)
        events.append(event("061", ("मत",), "cross", "-", .50, .55, .34, "pop", "-", "-", serial)); serial += 1
    elif name == "bento_example":
        add_img(73, "tiffin", ("खाने", "फ़र्क़"), .24, .53, .43, "slideL", "घर का खाना")
        add_img(73, "coins", ("बिल", "फ़र्क़"), .76, .54, .35, "slideR", "असली लागत")
        add_txt(74, ("₹350",), "NUM", "₹350", .30, .16, "₹100")
        add_txt(74, ("₹100",), "NUM", "₹100", .70, .16, "₹250")
        add_txt(75, ("₹250",), "KEY", "अंतर = ₹250", .50, .84, "₹3,000")
        add_txt(76, ("₹3,000",), "NUM", "₹3,000", .50, .14)
    elif name == "prep_example":
        add_img(88, "takeout_bag", ("बाहर", "मँगाए"), .24, .53, .41, "slideL", "मँगाया खाना")
        add_img(88, "meal_prep", ("घर", "खाने"), .76, .54, .41, "slideR", "घर का खाना")
        add_txt(88, ("₹900",), "NUM", "₹900", .26, .16, "₹400")
        add_txt(88, ("₹400",), "NUM", "₹400", .74, .16, "₹500")
        add_txt(89, ("₹500",), "KEY", "हर बार ₹500 कम", .50, .83, "₹2,000")
        add_txt(89, ("₹2,000",), "NUM", "₹2,000", .50, .15, "अगर")
        add_txt(90, ("नहीं",), "KEY", "पहले से खर्च न हो तो नहीं", .50, .86)
    elif name == "total_chart":
        # The ledger hands off to a continuous build: each exact bar arrives on its spoken amount.
        add_txt(118, ("काल्पनिक", "कॉपी"), "TAG", "काल्पनिक घर का उदाहरण", .50, .08)
        events.append(event("118", ("कॉपी",), "img", "budget_closeup", .50, .54, .42,
                            "rise", "₹2,000", "घर का हिसाब", serial))
        serial += 1
        specs = [
            (118, "bar_kakeibo", ("₹2,000",), .15),
            (119, "bar_food", ("₹2,500",), .29),
            (120, "bar_pause", ("₹3,000",), .43),
            (121, "bar_lunch", ("₹3,000",), .57),
            (122, "bar_dinner", ("चार", "रात"), .71),
            (122, "bar_duplicate", ("₹500",), .85),
        ]
        for line_no, asset, terms, x in specs:
            s = by_num[line_no]
            events.append(image_event(s["id"], asset, terms, x, .53, .35, "rise", ASSET_LABELS[asset], serial))
            serial += 1
        # The last word cue safely follows the sixth bar and ends the total animation.
        add_txt(123, ("कुल", "जोड़"), "NUM", "₹13,000", .50, .14)
    elif name == "outro_actions":
        add_txt(133, ("तीन", "काम"), "TAG", "इस हफ्ते • तीन काम", .50, .08)
        add_img(133, "budget_closeup", ("खर्च", "लिखिए"), .18, .55, .34, "rise", "खर्च लिखें")
        add_img(133, "pantry", ("सामान", "घर"), .50, .55, .34, "pop", "घर में देखें")
        add_img(133, "shopping_cart", ("रोकिए", "खरीद"), .82, .55, .34, "rise", "खरीद टालें")
        add_txt(134, ("सात", "दिन"), "KEY", "7 दिन बाद अपना हिसाब देखें", .50, .87)
    else:
        raise ValueError(f"Unknown special scene {name}")

    events.sort(key=lambda e: (e.cue_pos, e.serial))
    for e in events:
        rows.append(row(scene_id, e.cue, e.kind, e.what, e.x, e.y, e.size, e.motion, e.out, e.label))
    return rows


def fill_opening_visual_gaps(rows: list[list[str]], threshold: float = 0.9) -> int:
    """Carry the previous cut-out into a new shot when its first cue is late.

    The renderer resets to paper at every scene cut. A `hold` row preserves a
    relevant visual from the preceding scene until this scene's first cue, so
    narration never sits over an empty paper frame while waiting for an asset.
    """
    timing_words = sorted(word_rows, key=lambda r: word_global[(r["line"], int(r["i"]))])
    groups: dict[str, list[list[str]]] = defaultdict(list)
    for r in rows:
        groups[r[0]].append(r)

    def find_index(cue: str, start_at: int) -> int:
        if cue.startswith("@"):
            line_id = cue[1:]
            for i in range(start_at, len(timing_words)):
                if timing_words[i]["line"] == line_id:
                    return i
        else:
            for i in range(start_at, len(timing_words)):
                token = cue_clean(token_text(timing_words[i]))
                if cue in token:
                    return i
        raise ValueError(f"cannot time continuity cue {cue!r} from word {start_at}")

    previous_image: list[str] | None = None
    additions = 0
    for scene_rows in groups.values():
        original = list(scene_rows)
        if not original or original[0][2] != "bg" or not original[0][1].startswith("@"):
            raise ValueError(f"scene {original[0][0] if original else '?'} has no opening background row")
        first_line = original[0][1][1:]
        start_i = find_index("@" + first_line, 0)
        scene_start = max(0.0, float(timing_words[start_i]["start"]) - 0.12)
        cursor = start_i
        first_event: list[str] | None = None
        first_time = scene_start
        for r in original[1:]:
            cue = r[1]
            if cue in ("", "-"):
                when = scene_start
            elif cue.startswith("@"):
                i = find_index(cue, cursor)
                when = max(scene_start, float(timing_words[i]["start"]) - 0.06)
            else:
                i = find_index(cue, cursor)
                cursor = i
                when = float(timing_words[i]["start"]) - 0.06
            if r[2] != "bg":
                first_event, first_time = r, when
                break

        gap = first_time - scene_start
        if gap > threshold and previous_image is not None and first_event is not None:
            same_opening = (
                first_event[2] == "img"
                and first_event[3] == previous_image[3]
                and first_event[4:7] == previous_image[4:7]
            )
            if same_opening:
                # The same cut-out already serves as the first cue; keep it
                # visible from the cut instead of drawing a duplicate copy.
                first_event[7] = "hold"
            else:
                held = row(
                    original[0][0], "-", "img", previous_image[3],
                    float(previous_image[4]), float(previous_image[5]),
                    float(previous_image[6]), "hold", first_event[1], "-",
                )
                scene_rows.insert(1, held)
            additions += 1

        persistent = [r for r in original if r[2] == "img" and r[8] == "-"]
        if persistent:
            previous_image = persistent[-1]
        elif not previous_image:
            fallback = [r for r in original if r[2] == "img"]
            if fallback:
                previous_image = fallback[-1]
    rows[:] = [r for scene_rows in groups.values() for r in scene_rows]
    return additions


def main() -> None:
    starts = {start: (end, name) for start, end, name in SPECIAL_GROUPS}
    covered = {line for start, end, _ in SPECIAL_GROUPS for line in range(start, end + 1)}
    groups: list[tuple[list[dict[str, str]], str | None]] = []
    i = 0
    while i < len(sentences):
        line_no = int(sentences[i]["id"])
        if line_no in starts:
            end, name = starts[line_no]
            group = [s for s in sentences[i:] if line_no <= int(s["id"]) <= end]
            groups.append((group, name))
            i += len(group)
            continue
        if line_no in covered:
            i += 1
            continue
        groups.append(([sentences[i]], None))
        i += 1

    all_rows: list[list[str]] = []
    section_seen: set[str] = set()
    for index, (group, special) in enumerate(groups, 1):
        scene_id = f"{index:03d}"
        if special:
            all_rows.extend(special_scene(special, group, scene_id, section_seen))
        else:
            all_rows.extend(build_normal_group(group, scene_id, True, section_seen))
    continuity_holds = fill_opening_visual_gaps(all_rows)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["scene", "cue", "kind", "what", "x", "y", "size", "motion", "out", "label"])
        writer.writerows(all_rows)
    print(f"Wrote {OUT} — {len(groups)} animated scenes, {len(all_rows)} cues.")
    print(f"Added {continuity_holds} opening holds to eliminate empty scene openings.")
    print("Special builds: four-question cards, data caveat, sample calculations, six-bar ₹13,000 reveal, three-step outro.")


if __name__ == "__main__":
    main()
