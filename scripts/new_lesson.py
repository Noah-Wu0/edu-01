"""Create the blank page for a new lesson.

    python3 scripts/new_lesson.py <slug>

The page is paper, shared fonts, and cues.js. It does not copy another lesson.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "lesson"


def main():
    if len(sys.argv) != 2 or not sys.argv[1].replace("-", "").isalnum():
        raise SystemExit("usage: python3 scripts/new_lesson.py <slug>")
    slug = sys.argv[1]
    dest = ROOT / "works" / slug
    if dest.exists():
        raise SystemExit(f"{dest} already exists")
    dest.mkdir(parents=True)
    (dest / "check").mkdir()
    (dest / "audio").mkdir()
    for name in ("scene.js", "cues.js"):
        shutil.copyfile(TEMPLATE / name, dest / name)
    html = (TEMPLATE / "studio.html").read_text(encoding="utf-8").replace("__SLUG__", slug)
    (dest / "studio.html").write_text(html, encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
