#!/usr/bin/env python3
# Copyright 2026 the ArabGeoText authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Compose the README banner from the project mark.

The mark (`logo.png`) is artwork: a map pin whose aperture shows an aerial view with a
detected place name boxed in magenta -- localization and map text in one image. This script
only lays it out beside the wordmark, so the banner can be regenerated whenever the mark or
the wording changes.

Transparent background, so it sits on GitHub's light or dark theme without a halo.

Usage:
    python assets/make_logo.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BLUE = (100, 143, 255)
MAGENTA = (220, 38, 127)
INK = (24, 27, 34)
MUTED = (110, 120, 135)
PAPER = (247, 249, 252)

HERE = Path(__file__).resolve().parent


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def mark(height: int) -> Image.Image:
    """The project mark, scaled to `height`. Falls back to a plain pin if it is missing."""
    path = HERE / "logo.png"
    if not path.exists():
        raise SystemExit(f"missing {path}; place the logo artwork there first")
    img = Image.open(path).convert("RGBA")
    bbox = img.split()[3].getbbox()          # ignore transparent margin when scaling
    if bbox:
        img = img.crop(bbox)
    return img.resize((round(height * img.width / img.height), height), Image.LANCZOS)


def banner(width: int = 1200, height: int = 300) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    logo = mark(int(height * 0.78))
    img.alpha_composite(logo, (int(width * 0.06), (height - logo.height) // 2))

    d = ImageDraw.Draw(img)
    x = int(width * 0.06) + logo.width + int(width * 0.035)
    d.text((x, height * 0.30), "ArabGeoText", font=font(int(height * 0.25), True), fill=INK)
    sub = "Arabic geospatial text spotting in maps and satellite imagery"
    f = font(int(height * 0.085))
    while x + d.textlength(sub, font=f) > width - int(width * 0.05) and f.size > 8:
        f = font(f.size - 1)
    d.text((x + 3, height * 0.60), sub, font=f, fill=MUTED)
    return img


def main() -> None:
    mark(128).save(HERE / "logo-small.png")
    banner().save(HERE / "banner.png")
    for name in ("logo.png", "logo-small.png", "banner.png"):
        p = HERE / name
        print(f"  {name:<16}{Image.open(p).size}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
