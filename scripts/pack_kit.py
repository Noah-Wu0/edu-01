"""Pack this MVP for a machine that will not clone the repository.

    python3 scripts/pack_kit.py [--out out/edu-01.tar.gz]

The archive is the repository itself, without node_modules, out, or .git.
Other courses are not in this tree, so they are not packed.
"""

from __future__ import annotations

import argparse
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", "out", "__pycache__", ".DS_Store"}


def files():
    out = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if SKIP & set(path.relative_to(ROOT).parts):
            continue
        out.append(path)
    return sorted(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "edu-01.tar.gz")
    args = parser.parse_args()
    paths = files()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.out, "w:gz") as tar:
        for path in paths:
            tar.add(path, arcname=f"edu-01/{path.relative_to(ROOT)}")
    size = sum(path.stat().st_size for path in paths)
    print(f"{args.out}  {len(paths)} files  {size / 1e6:.0f} MB before gzip")


if __name__ == "__main__":
    main()
