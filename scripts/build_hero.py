"""Build the self-hosted animated profile banner.

Run: python scripts/build_hero.py
Requires Pillow. The output is intentionally a GIF so GitHub can display the
animation without JavaScript or an external image service.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "hero.gif"
W, H = 1200, 370
FRAMES = 90

INK = (241, 246, 255)
MUTED = (164, 181, 205)
CYAN = (83, 231, 214)
VIOLET = (169, 139, 250)
PINK = (245, 125, 190)


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [Path("C:/Windows/Fonts/consola.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")]
        if mono
        else [
            Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


F_NAME = font(65, bold=True)
F_BODY = font(25)
F_LABEL = font(15, bold=True)
F_MONO = font(21, mono=True)
F_NODE = font(13, bold=True)


def base_image() -> Image.Image:
    image = Image.new("RGB", (W, H))
    pixels = image.load()
    for y in range(H):
        for x in range(W):
            t = x / W * 0.6 + y / H * 0.4
            glow = max(0, 1 - math.hypot((x - 980) / 410, (y - 160) / 330))
            pixels[x, y] = (
                int(10 + 16 * t + 11 * glow),
                int(18 + 13 * t + 7 * glow),
                int(34 + 29 * t + 28 * glow),
            )
    draw = ImageDraw.Draw(image)
    for x in range(0, W, 34):
        draw.line((x, 0, x, H), fill=(28, 39, 61), width=1)
    for y in range(0, H, 34):
        draw.line((0, y, W, y), fill=(28, 39, 61), width=1)
    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=24, outline=(62, 79, 111), width=2)
    return image


BASE = base_image()
NODE_C = (973, 185)
NODES = [
    ((831, 103), "AGENTS"),
    ((1110, 90), "DATA"),
    ((1115, 286), "PRODUCT"),
    ((822, 274), "VISION"),
]
PHRASES = [
    "orchestrating multi-agent systems",
    "grounding answers in real data",
    "shipping applied AI products",
]


def pill(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, color: tuple[int, int, int]) -> int:
    width = int(draw.textlength(label, font=F_LABEL)) + 28
    draw.rounded_rectangle((x, y, x + width, y + 31), radius=15, fill=(25, 39, 60), outline=(53, 76, 104))
    draw.ellipse((x + 11, y + 12, x + 17, y + 18), fill=color)
    draw.text((x + 23, y + 8), label, fill=INK, font=F_LABEL)
    return width


def frame_image(index: int) -> Image.Image:
    image = BASE.copy()
    draw = ImageDraw.Draw(image)
    phase, local = divmod(index, 30)

    # Identity and project focus stay legible even in the first frame.
    draw.rounded_rectangle((53, 31, 76, 54), radius=6, fill=CYAN)
    draw.line((60, 43, 65, 48, 71, 37), fill=(10, 22, 36), width=3)
    draw.text((89, 34), "AZIZ / SYSTEMS LAB", fill=CYAN, font=F_LABEL)
    draw.text((750, 35), "TUNISIA · ENSTAB", fill=MUTED, font=F_LABEL)
    draw.text((50, 79), "Med Aziz Hraghi", fill=INK, font=F_NAME)
    draw.text((55, 165), "I build systems where AI becomes useful.", fill=MUTED, font=F_BODY)

    x = 55
    for label, color in [("MULTI-AGENT AI", CYAN), ("RAG", VIOLET), ("COMPUTER VISION", PINK)]:
        x += pill(draw, x, 214, label, color) + 10

    draw.rounded_rectangle((54, 277, 713, 341), radius=14, fill=(9, 20, 33), outline=(48, 72, 92), width=2)
    draw.ellipse((73, 293, 82, 302), fill=(255, 110, 115))
    draw.ellipse((90, 293, 99, 302), fill=(255, 205, 100))
    draw.ellipse((107, 293, 116, 302), fill=(105, 221, 146))
    draw.text((75, 309), ">", fill=CYAN, font=F_MONO)
    phrase = PHRASES[phase]
    chars = min(len(phrase), max(0, (local - 2) * 2))
    draw.text((99, 309), phrase[:chars], fill=INK, font=F_MONO)
    if local % 10 < 6:
        cursor_x = 99 + draw.textlength(phrase[:chars], font=F_MONO) + 3
        draw.rectangle((cursor_x, 313, cursor_x + 10, 332), fill=CYAN)

    # The moving packets link the four applied-AI domains to a central system.
    for node_index, (point, label) in enumerate(NODES):
        active = node_index == phase or (phase == 2 and node_index == 3)
        line_color = (75, 142, 165) if active else (50, 75, 105)
        draw.line((*NODE_C, *point), fill=line_color, width=3 if active else 2)
        packet_t = ((index / 28) + node_index * 0.23) % 1
        packet_x = int(NODE_C[0] + (point[0] - NODE_C[0]) * packet_t)
        packet_y = int(NODE_C[1] + (point[1] - NODE_C[1]) * packet_t)
        packet_color = [CYAN, VIOLET, PINK, CYAN][node_index]
        draw.ellipse((packet_x - 4, packet_y - 4, packet_x + 4, packet_y + 4), fill=packet_color)

    pulse = int(2 + 3 * (1 + math.sin(index * 0.24)) / 2)
    draw.ellipse((NODE_C[0] - 39 - pulse, NODE_C[1] - 39 - pulse, NODE_C[0] + 39 + pulse, NODE_C[1] + 39 + pulse), outline=(47, 115, 127), width=2)
    draw.ellipse((NODE_C[0] - 38, NODE_C[1] - 38, NODE_C[0] + 38, NODE_C[1] + 38), fill=(24, 45, 66), outline=CYAN, width=3)
    draw.text((NODE_C[0] - 22, NODE_C[1] - 10), "SHIP", fill=INK, font=F_NODE)

    for node_index, (point, label) in enumerate(NODES):
        active = node_index == phase or (phase == 2 and node_index == 3)
        color = [CYAN, VIOLET, PINK, CYAN][node_index] if active else (105, 148, 173)
        draw.ellipse((point[0] - 13, point[1] - 13, point[0] + 13, point[1] + 13), fill=(20, 35, 54), outline=color, width=3)
        label_w = draw.textlength(label, font=F_NODE)
        label_y = point[1] - 40 if node_index < 2 else point[1] + 22
        draw.text((point[0] - label_w / 2, label_y), label, fill=MUTED if not active else INK, font=F_NODE)

    return image


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [frame_image(i) for i in range(FRAMES)]
    palette = frame_image(20).quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.2f} MiB, {FRAMES} frames)")


if __name__ == "__main__":
    main()
