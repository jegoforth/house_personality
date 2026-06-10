"""Render House Personality brand PNGs from the source SVG."""

from __future__ import annotations

from pathlib import Path

import skia

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SVG = ROOT / "custom_components" / "house_personality" / "icon.svg"
BRAND_DIR = ROOT / "custom_components" / "house_personality" / "brand"


def _render_png(size: int, output: Path) -> None:
    """Render the source SVG to a square PNG."""
    stream = skia.FILEStream(str(SOURCE_SVG))
    dom = skia.SVGDOM.MakeFromStream(stream)
    if dom is None:
        raise RuntimeError(f"Unable to parse {SOURCE_SVG}")

    surface = skia.Surface(size, size)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorTRANSPARENT)
    dom.setContainerSize(skia.Size(size, size))
    dom.render(canvas)
    image = surface.makeImageSnapshot()
    data = image.encodeToData(skia.kPNG, 100)
    output.write_bytes(bytes(data))


def main() -> None:
    """Render Home Assistant local brand icon assets."""
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    _render_png(256, BRAND_DIR / "icon.png")
    _render_png(512, BRAND_DIR / "icon@2x.png")


if __name__ == "__main__":
    main()
