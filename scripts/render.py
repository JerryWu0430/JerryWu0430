# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==11.3.0"]
# ///
"""Render the profile artwork: uv run scripts/render.py [--font /path/to/font]."""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1280, 600
FRAMES, DURATION = 100, 80
BG, INK, MUTED, DIM = 8, 225, 145, 78


def font_path():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path)
    args = parser.parse_args()
    candidates = [args.font, Path("/System/Library/Fonts/Menlo.ttc"),
                  Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return str(candidate)
    parser.error("Supply a monospace TrueType font with --font")


FONT_PATH = font_path()


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def rotate(point, angle):
    x, y, z = point
    x, z = x * math.cos(angle) + z * math.sin(angle), -x * math.sin(angle) + z * math.cos(angle)
    tilt = 0.28
    return x * math.cos(tilt) - y * math.sin(tilt), x * math.sin(tilt) + y * math.cos(tilt), z


def sculpture(draw, phase):
    # An elongated octahedron. Rasterize its actual faces into a character grid;
    # changing depth and light, rather than random glyphs, describe its rotation.
    vertices = [(0, -1.65, 0), (0, 1.65, 0), (-0.95, 0, 0),
                (0, 0, 0.95), (0.95, 0, 0), (0, 0, -0.95)]
    vertices = [rotate(p, phase + 0.55) for p in vertices]
    faces = [(pole, ring, 2 + (ring - 1) % 4) for pole in (0, 1) for ring in range(2, 6)]
    cols, rows, cw, ch = 51, 39, 9, 12
    depth = [[-math.inf] * cols for _ in range(rows)]
    chars = [[None] * cols for _ in range(rows)]
    for a, b, c in faces:
        va, vb, vc = vertices[a], vertices[b], vertices[c]
        edge1, edge2 = [vb[i] - va[i] for i in range(3)], [vc[i] - va[i] for i in range(3)]
        normal = [edge1[1] * edge2[2] - edge1[2] * edge2[1],
                  edge1[2] * edge2[0] - edge1[0] * edge2[2],
                  edge1[0] * edge2[1] - edge1[1] * edge2[0]]
        center = [sum(p[i] for p in (va, vb, vc)) / 3 for i in range(3)]
        if sum(normal[i] * center[i] for i in range(3)) < 0:
            normal = [-n for n in normal]
        length = math.sqrt(sum(n * n for n in normal))
        shade = max(0, sum(normal[i] * (-0.5, -0.4, 0.76)[i] for i in range(3)) / length)
        glyph = ".:=1/0"[min(5, int(shade * 6))]
        color = round(85 + 155 * shade)
        ax, ay, az = va
        bx, by, bz = vb
        cx, cy, cz = vc
        determinant = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(determinant) < 1e-8:
            continue
        for row in range(rows):
            y = (row - (rows - 1) / 2) * ch / 132
            for col in range(cols):
                x = (col - (cols - 1) / 2) * cw / 132
                u = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / determinant
                v = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / determinant
                w = 1 - u - v
                if min(u, v, w) < 0:
                    continue
                z = u * az + v * bz + w * cz
                if z > depth[row][col]:
                    depth[row][col] = z
                    chars[row][col] = (glyph, color)
    ascii_font = font(14)
    for row in range(rows):
        for col in range(cols):
            if chars[row][col]:
                glyph, color = chars[row][col]
                draw.text((45 + col * cw, 70 + row * ch), glyph, font=ascii_font, fill=color)


def frame(phase):
    image = Image.new("L", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.text((38, 27), "jerrywu@github:~", font=font(17), fill=MUTED)
    draw.text((1110, 27), "~/profile", font=font(15), fill=DIM)
    draw.line((38, 63, WIDTH - 38, 63), fill=34)
    sculpture(draw, phase)
    draw.text((560, 153), "$ whoami", font=font(18), fill=MUTED)
    draw.text((557, 201), "jerry wu", font=font(53), fill=INK)
    draw.text((562, 294), "Founding Engineer @ Movable Voice", font=font(20), fill=INK)
    draw.text((562, 345), "TypeScript / Python / JavaScript", font=font(16), fill=MUTED)
    draw.text((562, 410), "$ ls projects/", font=font(18), fill=MUTED)
    draw.text((562, 446), "claude-usage   StackScout   StarPlex", font=font(16), fill=INK)
    draw.line((38, 550, WIDTH - 38, 550), fill=34)
    draw.text((38, 567), "01 / PROFILE", font=font(13), fill=DIM)
    draw.text((1015, 567), "JerryWu0430 / github", font=font(13), fill=MUTED)
    return image


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    frames = [frame(i * 2 * math.pi / FRAMES) for i in range(FRAMES)]
    frames[0].save(assets / "terminal.png")
    # A fixed grayscale palette keeps characters stable between GIF frames.
    palette = Image.new("P", (1, 1))
    palette.putpalette([channel for i in range(256) for channel in (i, i, i)])
    frames = [im.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    frames[0].save(assets / "terminal.gif", save_all=True, append_images=frames[1:],
                   duration=DURATION, loop=0, optimize=True, disposal=1)
    for filename in ("terminal.png", "terminal.gif"):
        path = assets / filename
        print(f"{path.relative_to(ROOT)}: {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
