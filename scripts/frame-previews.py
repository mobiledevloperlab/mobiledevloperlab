"""Build self-contained SVG previews; NimoteShot uses rounded corners only."""

import argparse
import base64
from pathlib import Path
import struct
import xml.etree.ElementTree as ET


ASSETS = Path(__file__).resolve().parent.parent / "assets"
WIDTH = 1600
PRODUCTS = {
    "nimotecode": ("NimoteCode", "#bfc5d2"),
    "nimoteshot": ("NimoteShot", None),
}


def frame(name, title, outline):
    output = ASSETS / f"{name}-framed.svg"
    source = ASSETS / f"{name}.png"
    if source.exists():
        data = source.read_bytes()
    else:
        # Existing previews embed the original PNG; no separate source is needed.
        root = ET.fromstring(output.read_text())
        image = root.find("{http://www.w3.org/2000/svg}image")
        href = image.attrib["{http://www.w3.org/1999/xlink}href"]
        if not href.startswith("data:image/png;base64,"):
            raise ValueError(f"{name}: expected an embedded PNG image")
        data = base64.b64decode(href.split(",", 1)[1], validate=True)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{name}: expected a PNG image")

    source_width, source_height = struct.unpack(">II", data[16:24])
    height = round(WIDTH * source_height / source_width, 2)
    encoded = base64.b64encode(data).decode("ascii")
    description = "Product screenshot with rounded corners only."
    border = ""
    if outline:
        description = "Product screenshot with rounded corners and a fine outline."
        border = f'  <rect x="0.75" y="0.75" width="{WIDTH - 1.5}" height="{round(height - 1.5, 2)}" rx="23.25" fill="none" stroke="{outline}" stroke-width="1.5"/>\n'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title} product preview</title>
  <desc id="desc">{description}</desc>
  <defs>
    <clipPath id="rounded">
      <rect width="{WIDTH}" height="{height}" rx="24"/>
    </clipPath>
  </defs>
  <image width="{WIDTH}" height="{height}" clip-path="url(#rounded)" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{encoded}"/>
{border}</svg>
'''
    output.write_text(svg)
    print(f"Built {output.name} ({WIDTH} × {height})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("products", nargs="*", help="Products to rebuild (default: all)")
    args = parser.parse_args()
    for name in args.products:
        if name not in PRODUCTS:
            parser.error(f"unknown product: {name}")
    for name in args.products or PRODUCTS:
        frame(name, *PRODUCTS[name])
