import time
import math
try:
    import urllib.request, io
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

TARGET_WIDTH = 64
TARGET_HEIGHT = 32
PALETTE_SIZE = 16

def generate_time_pattern(animation_frame, forced_hour=None):
    current_hour = forced_hour if forced_hour is not None else time.localtime().tm_hour
    
    def swirl(x, y, frame):
        cx, cy = x - TARGET_WIDTH/2, y - TARGET_HEIGHT/2
        dist = math.sqrt(cx*cx + cy*cy)
        angle = math.atan2(cy, cx) + frame * 0.1 + dist * 0.1
        return math.sin(angle + dist * 0.2) * 0.5 + 0.5
    
    if 5 <= current_hour < 8:
        palette = [0xFF8844, 0xFFAA00, 0xFF5500, 0xFFCC88] + [0xFF9966] * (PALETTE_SIZE - 4)
        pixels = []
        for y in range(TARGET_HEIGHT):
            for x in range(TARGET_WIDTH):
                swirl_val = swirl(x, y, animation_frame)
                if y < TARGET_HEIGHT//2:
                    pixels.append(1 if swirl_val > 0.6 else 0)
                else:
                    pixels.append(3 if swirl_val > 0.5 else 2)
    
    elif 8 <= current_hour < 12:
        palette = [0x66CCFF, 0xFFFF00, 0xFFFFFF, 0x99DDFF] + [0x77CCFF] * (PALETTE_SIZE - 4)
        pixels = []
        for y in range(TARGET_HEIGHT):
            for x in range(TARGET_WIDTH):
                swirl_val = swirl(x, y, animation_frame * 0.8)
                pixels.append(1 if swirl_val > 0.7 else (2 if swirl_val > 0.5 else 0))
    
    elif 12 <= current_hour < 17:
        palette = [0x0088FF, 0xFFFF00, 0xFFFFFF, 0x00AAFF] + [0x0099FF] * (PALETTE_SIZE - 4)
        pixels = []
        for y in range(TARGET_HEIGHT):
            for x in range(TARGET_WIDTH):
                swirl_val = swirl(x, y, animation_frame * 0.5)
                sun_dist = math.sqrt((x-TARGET_WIDTH/2)**2 + (y-TARGET_HEIGHT/3)**2)
                if sun_dist < 6:
                    pixels.append(1)
                else:
                    pixels.append(2 if swirl_val > 0.6 else 0)
    
    elif 17 <= current_hour < 20:
        palette = [0xFF5500, 0xFF8800, 0xFFAA00, 0xFF6622] + [0xFF7733] * (PALETTE_SIZE - 4)
        pixels = []
        for y in range(TARGET_HEIGHT):
            for x in range(TARGET_WIDTH):
                swirl_val = swirl(x, y, animation_frame * 0.7)
                if y > TARGET_HEIGHT * 2/3:
                    pixels.append(3)
                else:
                    pixels.append(1 if swirl_val > 0.6 else (2 if swirl_val > 0.4 else 0))
    
    else:
        palette = [0x000066, 0x0000AA, 0xFFFFFF, 0x000088] + [0x000077] * (PALETTE_SIZE - 4)
        pixels = []
        for y in range(TARGET_HEIGHT):
            for x in range(TARGET_WIDTH):
                swirl_val = swirl(x, y, animation_frame * 0.3)
                star_pattern = (x * y + animation_frame * 3) % 29
                if star_pattern < 2 and swirl_val > 0.7:
                    pixels.append(2)
                else:
                    pixels.append(1 if swirl_val > 0.5 else 0)
    
    return palette, pixels

def get_time_display(frame, demo_hour=None):
    try:
        return generate_time_pattern(frame, demo_hour)
    except Exception as e:
        print("Error generating time pattern:", e)
        fallback_palette = [0x000000, 0xFFFFFF] + [0x000000] * (PALETTE_SIZE - 2)
        fallback_pixels = []
        for y in range(TARGET_HEIGHT):
            for x in range(TARGET_WIDTH):
                fallback_pixels.append(1 if (x + y + frame) % 2 else 0)
        return fallback_palette, fallback_pixels

def update_display(palette, pixels, display):
    bitmap_time = displayio.Bitmap(TARGET_WIDTH, TARGET_HEIGHT, PALETTE_SIZE)
    if len(pixels) != TARGET_WIDTH * TARGET_HEIGHT:
        raise IndexError("TIME_PIXELS length does not match TARGET_WIDTH * TARGET_HEIGHT!")
    for y in range(TARGET_HEIGHT):
        for x in range(TARGET_WIDTH):
            bitmap_time[x, y] = pixels[y * TARGET_WIDTH + x]
    pal_time = displayio.Palette(PALETTE_SIZE)
    for i, color in enumerate(palette):
        pal_time[i] = color
    tg_time = displayio.TileGrid(bitmap_time, pixel_shader=pal_time)
    group_time = displayio.Group()
    group_time.append(tg_time)
    display.root_group = group_time

import board, displayio, framebufferio, rgbmatrix

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=TARGET_WIDTH, height=TARGET_HEIGHT, bit_depth=4,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

demo_hours = [6, 10, 14, 18, 22]
animation_frame = 0
for demo_hour in demo_hours:
    start_time = time.monotonic()
    while time.monotonic() - start_time < 4:
        TIME_PALETTE, TIME_PIXELS = get_time_display(animation_frame, demo_hour)
        update_display(TIME_PALETTE, TIME_PIXELS, display)
        animation_frame = (animation_frame + 1) % 60
        time.sleep(0.1)

animation_frame = 0
while True:
    TIME_PALETTE, TIME_PIXELS = get_time_display(animation_frame)
    update_display(TIME_PALETTE, TIME_PIXELS, display)
    animation_frame = (animation_frame + 1) % 60
    time.sleep(0.1)
