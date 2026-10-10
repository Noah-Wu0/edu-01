"""Send each narration line to a TTS service and save one wav per line.

    TTS_URL=http://host:port/tts python3 scripts/tts_api.py <slug> [--force]

The rest of the pipeline only needs works/<slug>/audio/voice/<id:04d>.wav,
any sample rate, mono or stereo. Change speak() to match your service.
TTS_BODY is a JSON object merged into every request, for voice, speed or
anything else the service takes.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def speak(text):
    body = {"text": text, "language": "ru", **json.loads(os.environ.get("TTS_BODY", "{}"))}
    req = urllib.request.Request(
        os.environ["TTS_URL"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return resp.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if "TTS_URL" not in os.environ:
        raise SystemExit("set TTS_URL")
    lesson = ROOT / "works" / args.slug
    lines = json.loads((lesson / "narration_ru.json").read_text(encoding="utf-8"))
    out = lesson / "audio" / "voice"
    out.mkdir(parents=True, exist_ok=True)
    for item in lines:
        path = out / f"{item['id']:04d}.wav"
        if path.exists() and not args.force:
            print(f"reuse {path.name}", flush=True)
            continue
        data = speak(item.get("spoken") or item["text"])
        if data[:4] != b"RIFF":
            raise SystemExit(f"L{item['id']}: service did not return a wav")
        path.write_bytes(data)
        print(f"{path.name}  {len(data)} bytes", flush=True)


if __name__ == "__main__":
    main()
