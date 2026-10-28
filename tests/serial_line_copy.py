#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Check that examples/serial-line is still a copy of its original in the maike repository.

    python3 tests/serial_line_copy.py [MAIKE]    MAIKE: the maike repository, default ../maike

The two trees must be byte-identical except for what each copy has for itself: the
README.md of the example, the folder maike/ and the `ignore` entry for it in the
root unifold.yaml (only in the original), and the generated unifold.html (only here).
Prints the first difference and exits 1; exits 0 silently when the maike repository
is not present, as in CI, which checks out this repository only.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COPY = REPO / "examples/serial-line"
SKIP = {"README.md", "maike", "unifold.html"}   # top-level entries each copy has for itself
IGNORE = b"ignore:\n  - maike\n"                  # the original's entry for maike/


def files(root: Path) -> dict[str, bytes]:
    out = {}
    for f in sorted(root.rglob("*")):
        rel = f.relative_to(root)
        if f.is_file() and rel.parts[0] not in SKIP and f.name != ".DS_Store" and "__pycache__" not in rel.parts:
            out[rel.as_posix()] = f.read_bytes()
    return out


def main() -> int:
    maike = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO.parent / "maike"
    original = maike / "examples/serial-line"
    if not original.is_dir():
        return 0
    a, b = files(original), files(COPY)
    a["unifold.yaml"] = a.get("unifold.yaml", b"").replace(IGNORE, b"", 1)
    for name in sorted(a.keys() | b.keys()):
        if name not in b:
            print(f"examples/serial-line/{name}: only in {original}")
        elif name not in a:
            print(f"examples/serial-line/{name}: not in {original}")
        elif a[name] != b[name]:
            print(f"examples/serial-line/{name}: differs from {original / name}")
        else:
            continue
        return 1
    print(f"examples/serial-line: a copy of {original}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
