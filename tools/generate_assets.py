#!/usr/bin/env python3
"""Generate pixel-art PNGs and the sanctuary collision scene."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCENES = ROOT / "scenes"
TILE = 16


def write_png(path: Path, width: int, height: int, pixels: list[list[tuple[int, int, int, int]]]) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y][x])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as file:
        file.write(b"\x89PNG\r\n\x1a\n")
        file.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
        file.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        file.write(chunk(b"IEND", b""))


def blank(width: int, height: int, color: tuple[int, int, int, int] = (0, 0, 0, 0)) -> list[list[tuple[int, int, int, int]]]:
    return [[color for _ in range(width)] for _ in range(height)]


def put(pixels: list[list[tuple[int, int, int, int]]], x: int, y: int, color: tuple[int, int, int, int]) -> None:
    if 0 <= y < len(pixels) and 0 <= x < len(pixels[0]) and color[3] > 0:
        pixels[y][x] = color


def blit(
    dest: list[list[tuple[int, int, int, int]]],
    src: list[list[tuple[int, int, int, int]]],
    ox: int,
    oy: int,
) -> None:
    for y, row in enumerate(src):
        for x, color in enumerate(row):
            if color[3]:
                put(dest, ox + x, oy + y, color)


def hash_xy(x: int, y: int) -> int:
    return (x * 374761393 + y * 668265263) & 0xFFFFFFFF


# --- palette ---
TRANSPARENT = (0, 0, 0, 0)
SHADOW = (12, 10, 14, 90)

HAT = (22, 18, 26, 255)
HAT_HI = (42, 36, 52, 255)
HAT_DK = (12, 10, 16, 255)
BRIM = (28, 24, 34, 255)
MASK = (230, 218, 192, 255)
MASK_SH = (198, 180, 148, 255)
BEAK = (196, 158, 86, 255)
BEAK_DK = (148, 110, 52, 255)
LENS = (22, 42, 48, 255)
GLINT = (110, 176, 184, 255)
ROBE = (32, 30, 40, 255)
ROBE_HI = (52, 48, 64, 255)
ROBE_DK = (18, 16, 24, 255)
STRAP = (92, 68, 42, 255)
POUCH = (70, 98, 62, 255)
BOOT = (46, 34, 28, 255)
BOOT_HI = (70, 52, 40, 255)
STAFF = (96, 68, 42, 255)
STAFF_DK = (64, 44, 26, 255)
STAFF_TIP = (168, 196, 92, 255)

STONE_A = (74, 74, 82, 255)
STONE_B = (62, 62, 70, 255)
STONE_C = (88, 86, 94, 255)
STONE_D = (52, 52, 58, 255)
MOSS = (58, 74, 52, 255)
CRACK = (40, 40, 46, 255)

WOOD_A = (92, 62, 44, 255)
WOOD_B = (74, 48, 34, 255)
WOOD_C = (110, 76, 54, 255)
WOOD_DK = (48, 30, 22, 255)
WOOD_LINE = (36, 22, 16, 255)

CARPET = (92, 36, 40, 255)
CARPET_DK = (68, 24, 28, 255)
CARPET_HI = (122, 52, 54, 255)

BED_SHEET = (186, 176, 158, 255)
BED_SH = (148, 136, 118, 255)
BED_WOOD = (86, 56, 40, 255)
PILLOW = (214, 206, 188, 255)

CRATE = (118, 84, 52, 255)
CRATE_DK = (86, 58, 34, 255)
CRATE_HI = (148, 110, 70, 255)
CRATE_LINE = (52, 34, 22, 255)

ALTAR = (168, 160, 148, 255)
ALTAR_DK = (120, 112, 102, 255)
ALTAR_HI = (204, 196, 180, 255)
CANDLE = (232, 214, 150, 255)
FLAME = (232, 140, 48, 255)
FLAME_HI = (255, 220, 120, 255)

PILLAR = (120, 116, 124, 255)
PILLAR_DK = (78, 76, 84, 255)
PILLAR_HI = (158, 154, 162, 255)


def draw_sprite(rows: list[str], palette: dict[str, tuple[int, int, int, int]]) -> list[list[tuple[int, int, int, int]]]:
    height = len(rows)
    width = len(rows[0])
    pixels = blank(width, height)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            put(pixels, x, y, palette.get(ch, TRANSPARENT))
    return pixels


def make_player() -> list[list[tuple[int, int, int, int]]]:
    palette = {
        "H": HAT,
        "h": HAT_HI,
        "d": HAT_DK,
        "B": BRIM,
        "M": MASK,
        "m": MASK_SH,
        "K": BEAK,
        "k": BEAK_DK,
        "L": LENS,
        "g": GLINT,
        "R": ROBE,
        "r": ROBE_HI,
        "D": ROBE_DK,
        "S": STRAP,
        "P": POUCH,
        "F": BOOT,
        "f": BOOT_HI,
        "W": STAFF,
        "w": STAFF_DK,
        "T": STAFF_TIP,
        "s": SHADOW,
    }
    idle = [
        "      hh        ",
        "     hHHh       ",
        "    hHHHHh      ",
        "   dHHHHHHd     ",
        "   HHHHHHHH     ",
        "    BBBBBB      ",
        "    LgMm gL     ",
        "     mKKm       ",
        "      kK        ",
        "     rRRRr      ",
        "    rRRRRRr  T  ",
        "    RRS SRR  W  ",
        "   rRRPPRRRr w  ",
        "   RRRRRRRR  W  ",
        "   RR RDD RR W  ",
        "   RRRRRRRR  w  ",
        "   DRR  RRD  W  ",
        "   RRRRRRRR  w  ",
        "    FFf fFF  W  ",
        "    FF   FF  w  ",
        "    ff   ff     ",
        "   sssssssss    ",
        "    sssssss     ",
        "                ",
    ]
    walk = [
        "      hh        ",
        "     hHHh       ",
        "    hHHHHh      ",
        "   dHHHHHHd     ",
        "   HHHHHHHH     ",
        "    BBBBBB      ",
        "    LgMm gL     ",
        "     mKKm       ",
        "      kK        ",
        "     rRRRr      ",
        "    rRRRRRr  T  ",
        "    RRS SRR  W  ",
        "   rRRPPRRRr w  ",
        "   RRRRRRRR  W  ",
        "   RR RDD RR W  ",
        "   RRRRRRRR  w  ",
        "   DRR  RRD  W  ",
        "   RRRRRRRR  w  ",
        "     FFf     W  ",
        "    fFFFf    w  ",
        "   FF   FF      ",
        "   sssssssss    ",
        "    sssssss     ",
        "                ",
    ]
    idle_px = draw_sprite(idle, palette)
    walk_px = draw_sprite(walk, palette)
    sheet = blank(32, 24)
    blit(sheet, idle_px, 0, 0)
    blit(sheet, walk_px, 16, 0)
    return sheet


def stone_tile(tx: int, ty: int) -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE)
    for y in range(TILE):
        for x in range(TILE):
            gx = tx * TILE + x
            gy = ty * TILE + y
            row = gy // 8
            ox = 4 if row % 2 else 0
            n = hash_xy((gx + ox) // 8, row) % 4
            color = (STONE_A, STONE_B, STONE_C, STONE_D)[n]
            if (gx + ox) % 8 == 0 or gy % 8 == 0:
                color = CRACK
            elif hash_xy((gx + ox) // 8, row) % 17 == 0 and (x + y) % 4 == 0:
                color = MOSS
            pixels[y][x] = color
    return pixels


def wood_floor_tile(tx: int, ty: int) -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE)
    for y in range(TILE):
        for x in range(TILE):
            plank = (ty * TILE + y) // 4
            n = hash_xy(plank, tx) % 3
            color = (WOOD_A, WOOD_B, WOOD_C)[n]
            if (ty * TILE + y) % 4 == 0:
                color = WOOD_LINE
            elif hash_xy(tx * TILE + x, plank) % 23 == 0:
                color = WOOD_DK
            pixels[y][x] = color
    return pixels


def wall_tile(tx: int, ty: int, top: bool) -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE)
    for y in range(TILE):
        for x in range(TILE):
            brick_y = (ty * TILE + y) // 5
            offset = 6 if brick_y % 2 else 0
            brick_x = (tx * TILE + x + offset) // 8
            n = hash_xy(brick_x, brick_y) % 3
            color = (WOOD_B, WOOD_A, WOOD_DK)[n]
            if top:
                color = WOOD_DK if n else HAT
            if x % 8 == (0 if brick_y % 2 == 0 else 6) or y % 5 == 0:
                color = WOOD_LINE if not top else HAT_DK
            pixels[y][x] = color
    if top:
        for x in range(TILE):
            pixels[0][x] = HAT_HI if x % 3 else HAT
            pixels[1][x] = HAT
    return pixels


def carpet_tile() -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE)
    for y in range(TILE):
        for x in range(TILE):
            color = CARPET
            if (x + y) % 6 == 0:
                color = CARPET_HI
            if x in (0, TILE - 1) or y in (0, TILE - 1):
                color = CARPET_DK
            pixels[y][x] = color
    return pixels


def bed_tile() -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE)
    for y in range(3, 15):
        for x in range(1, 15):
            if y in (3, 14) or x in (1, 14):
                pixels[y][x] = BED_WOOD
            elif y < 7:
                pixels[y][x] = PILLOW
            else:
                pixels[y][x] = BED_SH if (x + y) % 5 == 0 else BED_SHEET
    return pixels


def crate_tile() -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE, TRANSPARENT)
    for y in range(3, 15):
        for x in range(2, 14):
            pixels[y][x] = CRATE_HI if x < 5 or y < 5 else CRATE
            if x in (2, 13) or y in (3, 14):
                pixels[y][x] = CRATE_LINE
            if y == 8 or x == 8:
                pixels[y][x] = CRATE_DK
    return pixels


def altar_tile() -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE, TRANSPARENT)
    for y in range(8, 16):
        for x in range(1, 15):
            pixels[y][x] = ALTAR_DK if y > 12 else ALTAR
            if x in (1, 14):
                pixels[y][x] = ALTAR_HI
    for y in range(4, 9):
        for x in range(3, 13):
            pixels[y][x] = ALTAR_HI
    pixels[2][7] = FLAME_HI
    pixels[3][7] = FLAME
    pixels[4][7] = CANDLE
    pixels[5][7] = CANDLE
    pixels[3][8] = FLAME
    return pixels


def pillar_tile() -> list[list[tuple[int, int, int, int]]]:
    pixels = blank(TILE, TILE, TRANSPARENT)
    for y in range(TILE):
        for x in range(4, 12):
            color = PILLAR
            if x in (4, 11):
                color = PILLAR_DK
            if x in (6, 7):
                color = PILLAR_HI
            if y < 2 or y > 13:
                color = PILLAR_HI if x not in (4, 11) else PILLAR_DK
            pixels[y][x] = color
    return pixels


MAP = [
    "##############################################",
    "#............................................#",
    "#............................................#",
    "#..##############............##############..#",
    "#..#++++++++++++#............#++++++++++++#..#",
    "#..#++==++++==++#............#++==++++==++#..#",
    "#..#++++++++++++#............#++++++++++++#..#",
    "#..####++++++####............####++++++####..#",
    "#.....#++++++#..................#++++++#.....#",
    "#.....#++++++#........PP........#++++++#.....#",
    "#.....#++++++####################++++++#.....#",
    "#.....#++++++++++++++++++++++++++++++++#.....#",
    "#.....#+++++++++++++~AA~+++++++++++++++#.....#",
    "#.....#++++++++++++++++++++++++++++++++#.....#",
    "#.....#++++++####################++++++#.....#",
    "#.....#++++++#..................#++++++#.....#",
    "#.....#++++++#..................#++++++#.....#",
    "#.....########..................########.....#",
    "#............................................#",
    "#...............ccc..........................#",
    "#............................................#",
    "#............................................#",
    "##############################################",
]

SOLID = set("#=cAP")


def neighbors_wall(mx: int, my: int) -> bool:
    if not (0 <= my < len(MAP) and 0 <= mx < len(MAP[0])):
        return False
    return MAP[my][mx] == "#"


def render_map() -> list[list[tuple[int, int, int, int]]]:
    h = len(MAP) * TILE
    w = len(MAP[0]) * TILE
    pixels = blank(w, h, HAT_DK)
    for ty, row in enumerate(MAP):
        for tx, cell in enumerate(row):
            ox, oy = tx * TILE, ty * TILE
            if cell == "#":
                above = neighbors_wall(tx, ty - 1)
                tile = wall_tile(tx, ty, top=not above)
            elif cell == "+":
                tile = wood_floor_tile(tx, ty)
            elif cell == "=":
                blit(pixels, wood_floor_tile(tx, ty), ox, oy)
                tile = bed_tile()
            elif cell == "c":
                blit(pixels, stone_tile(tx, ty), ox, oy)
                tile = crate_tile()
            elif cell == "A":
                blit(pixels, carpet_tile(), ox, oy)
                tile = altar_tile()
            elif cell == "~":
                tile = carpet_tile()
            elif cell == "P":
                tile = pillar_tile()
                blit(pixels, stone_tile(tx, ty), ox, oy)
            else:
                tile = stone_tile(tx, ty)
            blit(pixels, tile, ox, oy)
    return pixels


def merge_solids() -> list[tuple[int, int, int, int]]:
    """Return merged rectangles as (x, y, w, h) in pixels."""
    rows, cols = len(MAP), len(MAP[0])
    used = [[False] * cols for _ in range(rows)]
    rects: list[tuple[int, int, int, int]] = []
    for y in range(rows):
        for x in range(cols):
            if used[y][x] or MAP[y][x] not in SOLID:
                continue
            width = 1
            while x + width < cols and MAP[y][x + width] in SOLID and not used[y][x + width]:
                width += 1
            height = 1
            done = False
            while y + height < rows and not done:
                for dx in range(width):
                    if MAP[y + height][x + dx] not in SOLID or used[y + height][x + dx]:
                        done = True
                        break
                if not done:
                    height += 1
            for dy in range(height):
                for dx in range(width):
                    used[y + dy][x + dx] = True
            rects.append((x * TILE, y * TILE, width * TILE, height * TILE))
    return rects


def write_world_scene(rects: list[tuple[int, int, int, int]]) -> None:
    map_w = len(MAP[0]) * TILE
    map_h = len(MAP) * TILE
    spawn_x = 23 * TILE + 8
    spawn_y = 19 * TILE + 8

    resources = []
    nodes = []
    for i, (x, y, w, h) in enumerate(rects, start=1):
        resources.append(
            f"[sub_resource type=\"RectangleShape2D\" id=\"WallShape_{i}\"]\nsize = Vector2({w}, {h})\n"
        )
        cx = x + w / 2
        cy = y + h / 2
        nodes.append(
            f"[node name=\"Wall{i}\" type=\"CollisionShape2D\" parent=\"Walls\"]\n"
            f"position = Vector2({cx}, {cy})\n"
            f"shape = SubResource(\"WallShape_{i}\")\n"
        )

    load_steps = 4 + len(resources)
    content = f"""; Generated by tools/generate_assets.py
[gd_scene load_steps={load_steps} format=3]

[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="1_player"]
[ext_resource type="Texture2D" uid="uid://cjvchgir0yfm7" path="res://assets/sanctuary.png" id="2_map"]
[ext_resource type="Script" uid="uid://m2cvgh4ektnr" path="res://scripts/world.gd" id="3_world"]

{chr(10).join(resources)}
[node name="World" type="Node2D"]
y_sort_enabled = true
script = ExtResource("3_world")

[node name="CanvasModulate" type="CanvasModulate" parent="."]
color = Color(0.82, 0.86, 0.78, 1)

[node name="Sanctuary" type="Sprite2D" parent="."]
texture_filter = 1
z_index = -10
texture = ExtResource("2_map")
centered = false

[node name="Walls" type="StaticBody2D" parent="."]

{chr(10).join(nodes)}
[node name="Player" parent="." instance=ExtResource("1_player")]
position = Vector2({spawn_x}, {spawn_y})

[node name="Camera2D" type="Camera2D" parent="Player"]
position_smoothing_enabled = true
position_smoothing_speed = 8.0
limit_left = 0
limit_top = 0
limit_right = {map_w}
limit_bottom = {map_h}
limit_smoothed = true

[node name="CanvasLayer" type="CanvasLayer" parent="."]

[node name="Hint" type="Label" parent="CanvasLayer"]
offset_left = 6.0
offset_top = 6.0
offset_right = 314.0
offset_bottom = 28.0
theme_override_colors/font_color = Color(0.9, 0.86, 0.74, 1)
theme_override_colors/font_shadow_color = Color(0.07, 0.06, 0.08, 1)
theme_override_constants/shadow_offset_x = 1
theme_override_constants/shadow_offset_y = 1
theme_override_font_sizes/font_size = 8
text = "ZQSD ou flèches pour vous déplacer"
"""
    (SCENES / "world.tscn").write_text(content)


def main() -> None:
    player = make_player()
    write_png(ASSETS / "player.png", 32, 24, player)
    sanctuary = render_map()
    write_png(ASSETS / "sanctuary.png", len(MAP[0]) * TILE, len(MAP) * TILE, sanctuary)
    write_world_scene(merge_solids())
    print("Wrote assets/player.png, assets/sanctuary.png, scenes/world.tscn")


if __name__ == "__main__":
    main()
