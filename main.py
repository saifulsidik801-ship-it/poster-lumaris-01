#!/usr/bin/env python3
"""LUMARIS — The Poster for a Place That Isn't There.

Writes the travel poster to /output/entry.png.

The poster image (poster.jpg, 1024x1024, bundled in this repo) was
painted for this entry: Lumaris, a fictional coastal town where the
lighthouse is a living tree — its trunk a tower, its branches hung
with lanterns, its beacon shining over a turquoise sea at dusk.
The place name LUMARIS is set huge in cream serif capitals across
the top, with the subtitle THE LIGHTHOUSE THAT GROWS beneath it.

This program runs in a sandbox with no network, so it ships the
finished poster with the repo and writes it out, verifying the
house gate (whole JPEG, 1024x1024, at most 1 MiB) before it lands.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "poster.jpg")
OUT_DIR = "/output"
OUT = os.path.join(OUT_DIR, "entry.png")

MAX_BYTES = 1_048_576
WANT_W, WANT_H = 1024, 1024


def jpeg_size(path):
    """Read width/height out of a JPEG's SOF marker (stdlib only)."""
    with open(path, "rb") as f:
        data = f.read(2)
        if data != b"\xff\xd8":
            raise ValueError("not a JPEG (missing SOI marker)")
        while True:
            marker = f.read(2)
            if len(marker) < 2 or marker[0] != 0xFF:
                raise ValueError("not a JPEG (bad marker)")
            code = marker[1]
            if code in (0xD8, 0xD9) or 0xD0 <= code <= 0xD7:
                continue
            size_bytes = f.read(2)
            if len(size_bytes) < 2:
                raise ValueError("truncated JPEG segment")
            size = struct.unpack(">H", size_bytes)[0]
            if 0xC0 <= code <= 0xCF and code not in (0xC4, 0xC8, 0xCC):
                frame = f.read(5)
                height, width = struct.unpack(">xHH", frame)
                return width, height
            f.seek(size - 2, os.SEEK_CUR)


def main():
    if not os.path.isfile(SRC):
        print("poster.jpg missing next to main.py", file=sys.stderr)
        return 1
    nbytes = os.path.getsize(SRC)
    if nbytes > MAX_BYTES:
        print("poster.jpg is %d bytes, over the 1 MiB gate" % nbytes,
              file=sys.stderr)
        return 1
    width, height = jpeg_size(SRC)
    if (width, height) != (WANT_W, WANT_H):
        print("poster.jpg is %dx%d, want %dx%d"
              % (width, height, WANT_W, WANT_H), file=sys.stderr)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, OUT)
    done = os.path.getsize(OUT)
    print("wrote %s (%dx%d, %d bytes)" % (OUT, width, height, done))
    return 0


if __name__ == "__main__":
    sys.exit(main())
