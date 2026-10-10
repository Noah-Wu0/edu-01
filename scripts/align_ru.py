"""Place Russian line recordings on one timeline.

    python3 scripts/align_ru.py <slug>

Recordings may come from any TTS at any sample rate. Word times come from
faster-whisper small (assets/voice/whisper-small if present, else it
downloads). A line with "chapter": true
gets a longer gap before it. This script does not use the scene splits of
one finished lesson.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from mix_ru import mono, resample

ROOT = Path(__file__).resolve().parents[1]


def whisper_dir():
    env = os.environ.get("WHISPER_MODEL")
    return Path(env) if env else ROOT / "assets" / "voice" / "whisper-small"


def tokens(text):
    return re.findall(r"[a-zа-яё0-9әғқңөұүһі]+", text.lower().replace("ё", "е"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    args = ap.parse_args()
    lesson = ROOT / "works" / args.slug
    lines = json.loads((lesson / "narration_ru.json").read_text(encoding="utf-8"))
    out = lesson / "audio"
    voice = out / "voice"
    model_dir = whisper_dir()
    model_dir = str(model_dir) if (model_dir / "model.bin").is_file() else "small"
    reports_path = out / "recognition.json"
    reports = json.loads(reports_path.read_text(encoding="utf-8")) if reports_path.exists() else {}
    hashes = {
        str(item["id"]): hashlib.sha256((voice / f"{item['id']:04d}.wav").read_bytes()).hexdigest()
        for item in lines
    }
    pending = [item for item in lines if reports.get(str(item["id"]), {}).get("audio_sha256") != hashes[str(item["id"])]]
    model = WhisperModel(model_dir, device="cpu", compute_type="int8", cpu_threads=4) if pending else None
    for item in pending:
        file = voice / f"{item['id']:04d}.wav"
        segments, _ = model.transcribe(
            str(file),
            language=os.environ.get("ALIGN_LANG", "ru"),
            beam_size=5,
            word_timestamps=True,
            vad_filter=False,
            condition_on_previous_text=False,
        )
        segments = list(segments)
        recognized = " ".join(segment.text.strip() for segment in segments)
        words = [
            {
                "word": word.word.strip(),
                "start": round(word.start, 3),
                "end": round(word.end, 3),
                "probability": round(word.probability, 3),
            }
            for segment in segments
            for word in (segment.words or [])
        ]
        ratio = difflib.SequenceMatcher(None, tokens(item["text"]), tokens(recognized)).ratio()
        reports[str(item["id"])] = {
            "expected": item["text"],
            "recognized": recognized,
            "audio_sha256": hashes[str(item["id"])],
            "token_match": round(ratio, 4),
            "words": words,
        }
        reports_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"L{item['id']} match={ratio:.3f} {recognized}", flush=True)

    rows = []
    lengths = []
    t = 0.65
    for index, item in enumerate(lines):
        samples, rate = sf.read(voice / f"{item['id']:04d}.wav", dtype="float32")
        samples = resample(mono(samples), rate, 24000)
        duration = len(samples) / 24000
        gap = 0.65 if index == 0 else (0.9 if item.get("chapter") else 0.6)
        if index:
            t += gap
        recognition = reports[str(item["id"])]
        rows.append({
            **item,
            "start": round(t, 6),
            "end": round(t + duration, 6),
            "duration": duration,
            "gap_before": gap,
            "recognized": recognition["recognized"],
            "audio_sha256": hashes[str(item["id"])],
            "words": [
                {**word, "start": round(t + word["start"], 6), "end": round(t + word["end"], 6)}
                for word in recognition["words"]
            ],
        })
        lengths.append(samples)
        t += duration
    duration = rows[-1]["end"] + 1.4
    timeline = {
        "duration": duration,
        "sample_rate": 24000,
        "fps": 24,
        "lines": rows,
    }
    (lesson / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cues = {
        "duration": duration,
        "lines": [row["start"] for row in rows],
        "len": [row["duration"] for row in rows],
        "words": [row["words"] for row in rows],
    }
    (lesson / "cues.js").write_text("const CUES = " + json.dumps(cues, ensure_ascii=False) + ";\n", encoding="utf-8")
    narration = np.zeros(int(np.ceil(duration * 24000)), dtype=np.float32)
    for row, samples in zip(rows, lengths):
        start = round(row["start"] * 24000)
        narration[start:start + len(samples)] += samples
    sf.write(out / "narration.wav", narration, 24000, subtype="PCM_16")
    print(json.dumps({"duration": duration, "lines": len(rows)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    sys.exit(main())
