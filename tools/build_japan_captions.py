#!/usr/bin/env python3
"""Build a full Hindi SRT from the project's estimated word timings.

The word timings are proportional estimates within the selected voice chunks,
not forced alignment. Captions are grouped into readable phrase-sized cues.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "japan-savings-habits"
WORDS = PROJECT / "WORDS.tsv"
OUT = PROJECT / "captions.srt"
MAX_SECONDS = 4.2
MAX_CHARS = 70
LINE_WIDTH = 38


def timestamp(seconds: float) -> str:
    millis = max(0, round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    whole, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole:02d},{millis:03d}"


def wrap_words(words: list[str]) -> str:
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > LINE_WIDTH:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if len(lines) > 2:
        raise ValueError(f"caption exceeds two lines: {' '.join(words)}")
    return "\n".join(lines)


def main() -> None:
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    with WORDS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            by_line[row["line"]].append(row)

    cues: list[tuple[float, float, str]] = []
    for line in sorted(by_line, key=int):
        rows = sorted(by_line[line], key=lambda r: int(r["i"]))
        current: list[dict[str, str]] = []

        def emit() -> None:
            nonlocal current
            if not current:
                return
            text = wrap_words([r["word"] for r in current])
            cues.append((float(current[0]["start"]), float(current[-1]["end"]), text))
            current = []

        for word in rows:
            candidate = current + [word]
            duration = float(candidate[-1]["end"]) - float(candidate[0]["start"])
            text_length = len(" ".join(r["word"] for r in candidate))
            if current and (duration > MAX_SECONDS or text_length > MAX_CHARS):
                emit()
            current.append(word)
            token = word["word"].rstrip('"\'”’)]}')
            if token.endswith(("।", "?", "!")):
                emit()
        emit()

    if not cues:
        raise ValueError("WORDS.tsv contains no captionable words")
    for i, (start, end, text) in enumerate(cues):
        if end <= start:
            raise ValueError(f"zero-duration caption {i + 1}: {text}")
        if i and start < cues[i - 1][1] - 0.01:
            raise ValueError(f"overlapping captions {i} and {i + 1}")

    blocks = [
        f"{i}\n{timestamp(start)} --> {timestamp(end)}\n{text}"
        for i, (start, end, text) in enumerate(cues, 1)
    ]
    OUT.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}: {len(cues)} Hindi caption cues, through {cues[-1][1]:.3f}s.")
    print("Timing note: caption boundaries use the project's estimated word timings, not forced alignment.")


if __name__ == "__main__":
    main()
