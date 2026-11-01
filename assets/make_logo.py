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

"""Generate the ArabGeoText mark and README banner.

The mark is a map pin whose aperture is a detection box over map linework -- the two things
the project is about, localization and map text, in one shape. Drawn rather than hand-made so
it can be regenerated at any size, and kept to the paper's palette so figures and branding
match: detection blue #648FFF, reference magenta #DC267F.

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


def pin(size: int) -> Image.Image:
    """A map pin: circular head over a tapered point, with a detection box inside."""
    s = size * 4                       # supersample, then downscale for clean edges
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx, cy, r = s * 0.5, s * 0.40, s * 0.30
    tip = s * 0.95

    # Body: head circle unioned with the triangle running down to the tip.
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE)
    half = r * math.sin(math.radians(52))
    dy = r * math.cos(math.radians(52))
    d.polygon([(cx - half, cy + dy), (cx + half, cy + dy), (cx, tip)], fill=BLUE)

    # Aperture: a white window standing for the tile being read.
    w, h = r * 0.80, r * 0.56
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=r * 0.16, fill=PAPER)

    # Map linework inside the window: one road running diagonally, as labels do.
    d.line([(cx - w * 0.82, cy + h * 0.46), (cx + w * 0.82, cy - h * 0.50)],
           fill=(214, 221, 231), width=int(s * 0.030))

    # The detected label: a rotated box on that road, in the reference colour.
    box_w, box_h = w * 1.30, h * 0.52
    label = Image.new("RGBA", (int(box_w), int(box_h)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(label)
    ld.rectangle([0, 0, box_w - 1, box_h - 1], outline=MAGENTA, width=int(s * 0.022))
    for i in range(3):                 # glyph strokes, suggesting text without spelling it
        x0 = box_w * (0.16 + i * 0.26)
        ld.line([(x0, box_h * 0.30), (x0 + box_w * 0.13, box_h * 0.70)],
                fill=MAGENTA, width=int(s * 0.018))
    label = label.rotate(21, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(label, (int(cx - label.width / 2), int(cy - label.height / 2)))

    return img.resize((size, size), Image.LANCZOS)


def banner(width: int = 1200, height: int = 300) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mark = pin(int(height * 0.72))
    img.alpha_composite(mark, (int(width * 0.085), (height - mark.height) // 2))

    d = ImageDraw.Draw(img)
    x = int(width * 0.085) + mark.width + int(width * 0.035)
    d.text((x, height * 0.30), "ArabGeoText", font=font(int(height * 0.25), True), fill=INK)
    sub = "Arabic geospatial text spotting in maps and satellite imagery"
    f = font(int(height * 0.085))
    while x + d.textlength(sub, font=f) > width - int(width * 0.05) and f.size > 8:
        f = font(f.size - 1)
    d.text((x + 3, height * 0.60), sub, font=f, fill=MUTED)
    return img


def main() -> None:
    pin(512).save(HERE / "logo.png")
    pin(128).save(HERE / "logo-small.png")
    banner().save(HERE / "banner.png")
    for name in ("logo.png", "logo-small.png", "banner.png"):
        p = HERE / name
        print(f"  {name:<16}{Image.open(p).size}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
