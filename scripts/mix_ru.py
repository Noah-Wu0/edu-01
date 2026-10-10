"""Mix a lesson narration with one music file.

    python3 scripts/mix_ru.py <slug> --music works/<slug>/audio/music.mp3 [--sfx hit.ogg@41.2]

Music stays about 18 dB under the voice for the whole film. Each --sfx lands
at its time in seconds, for the answer moment only. The output is
works/<slug>/audio/mix.wav at 24000 Hz stereo.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
DUCK = 10 ** (-18 / 20)


def mono(samples):
    if samples.ndim == 1:
        return samples
    return samples.mean(axis=1)


def resample(samples, source_rate, target_rate):
    if source_rate == target_rate:
        return samples
    duration = len(samples) / source_rate
    target_len = int(round(duration * target_rate))
    source_x = np.linspace(0, 1, len(samples), endpoint=False)
    target_x = np.linspace(0, 1, target_len, endpoint=False)
    return np.interp(target_x, source_x, samples).astype(np.float32)


def fade(samples, rate):
    n = min(len(samples), int(rate * 0.5))
    if n == 0:
        return samples
    ramp = np.linspace(0, 1, n, dtype=np.float32)
    samples[:n] *= ramp
    samples[-n:] *= ramp[::-1]
    return samples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--music", type=Path, required=True)
    ap.add_argument("--sfx", action="append", default=[], metavar="FILE@SECONDS")
    args = ap.parse_args()
    lesson = ROOT / "works" / args.slug / "audio"
    voice, rate = sf.read(lesson / "narration.wav", dtype="float32", always_2d=False)
    voice = mono(voice)
    music, music_rate = sf.read(args.music, dtype="float32", always_2d=False)
    music = resample(mono(music), music_rate, rate)
    if len(music) < len(voice):
        tiled = np.resize(music, len(voice))
        music = tiled
    music = music[:len(voice)] * DUCK
    fade(music, rate)
    bed = voice + music
    for spec in args.sfx:
        path, at = spec.rsplit("@", 1)
        hit, hit_rate = sf.read(path, dtype="float32", always_2d=False)
        hit = resample(mono(hit), hit_rate, rate) * 0.5
        start = int(round(float(at) * rate))
        end = min(len(bed), start + len(hit))
        bed[start:end] += hit[:end - start]
    mix = np.column_stack([bed, bed])
    peak = float(np.max(np.abs(mix)))
    if peak > 0.98:
        mix *= 0.98 / peak
    out = lesson / "mix.wav"
    sf.write(out, mix, rate, subtype="PCM_16")
    print(f"{out}  {len(voice) / rate:.2f}s  peak {float(np.max(np.abs(mix))):.3f}")


if __name__ == "__main__":
    main()
