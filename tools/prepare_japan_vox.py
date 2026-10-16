#!/usr/bin/env python3
"""Create sentence/word timing tables for the selected voice-02 WAV chunks.

Timing is proportionally estimated inside each generated chunk (text weights,
punctuation pauses); it is not Whisper forced alignment. The narration WAV itself
is unchanged and is the timing master for the upstream renderer/mixer.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "japan-savings-habits"
SCRIPT = ROOT / "content" / "japan-savings-habits" / "SCRIPT.md"
VOICE_DIR = PROJECT / "audio" / "voice-02"
CHUNK_JSON = VOICE_DIR / "VOICE_CHUNKS.json"
JOINED = VOICE_DIR / "VOICEOVER.wav"
GAP = 0.15


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    return [s.strip() for s in re.split(r"(?<=[।?!])\s+", text) if s.strip()]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def section_for_heading(heading: str, current: str) -> str:
    h = heading.strip()
    if h == "## HOOK": return "hook"
    if h.startswith("## आदत 1"): return "kakeibo"
    if h.startswith("## आदत 2"): return "mottainai"
    if h.startswith("## आदत 3"): return "pause"
    if h.startswith("### बीच का विराम"): return "interlude"
    if h.startswith("## आदत 4"): return "bento"
    if h.startswith("## आदत 5"): return "prep"
    if h.startswith("## आदत 6"): return "danshari"
    if h.startswith("## आदत 7"): return "kintsugi"
    if h.startswith("## असली हिसाब"): return "math"
    if h.startswith("## OUTRO"): return "outro"
    return current


def script_sentences() -> list[tuple[str, str]]:
    lines = SCRIPT.read_text(encoding="utf-8").splitlines()
    started = False
    section = "hook"
    result: list[tuple[str, str]] = []
    for line in lines:
        text = line.strip()
        if text == "## HOOK":
            started, section = True, "hook"
            continue
        if not started:
            continue
        if text.startswith("## Production / fact-check notes"):
            break
        if not text or text.startswith("---"):
            continue
        if text.startswith("## ") or text.startswith("### "):
            section = section_for_heading(text, section)
            continue
        for sentence in split_sentences(text):
            result.append((sentence, section))
    return result


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as f:
        return f.getnframes() / f.getframerate()


def text_weight(text: str) -> float:
    compact = re.sub(r"\s+", "", text)
    pause = (3.0 * text.count("।") + 2.4 * text.count("?") + 2.4 * text.count("!")
             + 1.0 * text.count(",") + 1.0 * text.count("—") + 0.7 * text.count(":"))
    return max(1.0, len(compact) + pause)


def word_weight(word: str) -> float:
    stripped = re.sub(r"\s+", "", word)
    pause = 1.8 if word.endswith(("।", "?", "!")) else 0.65 if word.endswith((",", ";", ":")) else 0.0
    return max(1.0, len(stripped) + pause)


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    records = json.loads(CHUNK_JSON.read_text(encoding="utf-8"))
    approved = script_sentences()
    pointer = 0
    sentence_rows: list[dict] = []
    cursor = 0.0
    for chunk_index, record in enumerate(records):
        filename = record["file"]
        chunk_sentences = split_sentences(record["text"])
        duration = wav_duration(VOICE_DIR / "chunks" / filename)
        selected: list[tuple[str, str]] = []
        for sentence in chunk_sentences:
            if pointer >= len(approved):
                raise ValueError("Voice contains more sentences than the approved narration.")
            expected, section = approved[pointer]
            if normalize(sentence) != normalize(expected):
                raise ValueError(f"Text mismatch at sentence {pointer + 1}: {sentence!r} != {expected!r}")
            selected.append((sentence, section))
            pointer += 1
        weights = [text_weight(sentence) for sentence, _ in selected]
        total_weight = sum(weights)
        local = 0.0
        for index, ((sentence, section), weight) in enumerate(zip(selected, weights)):
            seg_dur = duration - local if index == len(selected) - 1 else duration * weight / total_weight
            line_id = f"{len(sentence_rows) + 1:03d}"
            sentence_rows.append({
                "id": line_id,
                "section": section,
                "chunk": filename,
                "start": cursor + local,
                "dur": seg_dur,
                "text": sentence,
            })
            local += seg_dur
        cursor += duration + (GAP if chunk_index < len(records) - 1 else 0.0)
    if pointer != len(approved):
        raise ValueError(f"Voice covers {pointer} sentences; approved narration has {len(approved)}.")

    # The joined WAV already contains precisely these gaps between generated clips.
    if abs(cursor - wav_duration(JOINED)) > 0.03:
        raise ValueError(f"VO duration mismatch: table {cursor:.3f}s, audio {wav_duration(JOINED):.3f}s")
    shutil.copyfile(JOINED, PROJECT / "VO.wav")

    vo_rows: list[list[object]] = []
    lines_rows: list[list[object]] = []
    word_rows: list[list[object]] = []
    detail_rows: list[list[object]] = []
    for s in sentence_rows:
        line_id, start, duration, text = s["id"], s["start"], s["dur"], s["text"]
        vo_rows.append([line_id, f"{start:.3f}", f"{duration:.3f}", text])
        lines_rows.append([line_id, text, f"{GAP:.2f}"])
        words = text.split()
        weights = [word_weight(word) for word in words]
        denom = sum(weights)
        cumulative_weight = 0.0
        for i, (word, weight) in enumerate(zip(words, weights)):
            ws = start + duration * cumulative_weight / denom
            cumulative_weight += weight
            we = start + duration if i == len(words) - 1 else start + duration * cumulative_weight / denom
            word_rows.append([line_id, i, f"{ws:.3f}", f"{we:.3f}", word])
        detail_rows.append([line_id, s["section"], s["chunk"], f"{start:.3f}", f"{duration:.3f}", text])

    write_tsv(PROJECT / "VO.tsv", ["id", "start", "dur", "text"], vo_rows)
    write_tsv(PROJECT / "LINES.tsv", ["id", "text", "gap"], lines_rows)
    write_tsv(PROJECT / "WORDS.tsv", ["line", "i", "start", "end", "word"], word_rows)
    write_tsv(PROJECT / "SENTENCES.tsv", ["id", "section", "chunk", "start", "dur", "text"], detail_rows)
    print(f"Prepared {len(sentence_rows)} sentence lines, {len(word_rows)} word timings, {cursor:.2f}s audio.")
    print("Timing note: word and sentence positions are estimated proportionally inside each selected-voice chunk.")


if __name__ == "__main__":
    main()
