"""Build self-contained SVG previews with only rounded corners and a fine outline."""

import base64
from pathlib import Path
import struct


ASSETS = Path(__file__).resolve().parent.parent / "assets"
WIDTH = 1600
PRODUCTS = {
    "nimotecode": ("NimoteCode", "#bfc5d2"),
    "nimoteshot": ("NimoteShot", "#c8d5ea"),
}


def frame(name, title, outline):
    data = (ASSETS / f"{name}.png").read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{name}: expected a PNG image")

    source_width, source_height = struct.unpack(">II", data[16:24])
    height = round(WIDTH * source_height / source_width, 2)
    encoded = base64.b64encode(data).decode("ascii")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title} product preview</title>
  <desc id="desc">Product screenshot with rounded corners and a fine outline.</desc>
  <defs>
    <clipPath id="rounded">
      <rect width="{WIDTH}" height="{height}" rx="24"/>
    </clipPath>
  </defs>
  <image width="{WIDTH}" height="{height}" clip-path="url(#rounded)" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{encoded}"/>
  <rect x="0.75" y="0.75" width="{WIDTH - 1.5}" height="{round(height - 1.5, 2)}" rx="23.25" fill="none" stroke="{outline}" stroke-width="1.5"/>
</svg>
'''
    output = ASSETS / f"{name}-framed.svg"
    output.write_text(svg)
    print(f"Built {output.name} ({WIDTH} × {height})")


for product_name, (product_title, border_color) in PRODUCTS.items():
    frame(product_name, product_title, border_color)
