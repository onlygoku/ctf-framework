# ── generate.py  (run this to CREATE the challenge image) ──
"""
FORENSICS-001: Hidden Power Level (LSB Steganography)
Category: Forensics | Difficulty: Intermediate | Points: 300
Flag: CTF{l5b_st3g0_p0w3r_l3v3l}

Run this script to generate 'dragon_radar.png' — give that PNG to players.
Players must extract the LSB of each pixel's R channel to find the flag.
"""
from PIL import Image
import struct

FLAG = b"CTF{l5b_st3g0_p0w3r_l3v3l}"

def hide_flag(img_path, flag):
    img = Image.new("RGB", (200, 200), color=(30, 10, 0))
    # Draw a simple "radar" pattern
    import math
    pixels = img.load()
    cx, cy = 100, 100
    for y in range(200):
        for x in range(200):
            dx, dy = x-cx, y-cy
            dist = math.sqrt(dx*dx + dy*dy)
            if abs(dist - 40) < 2 or abs(dist - 70) < 2 or abs(dist - 95) < 2:
                pixels[x,y] = (0, 180, 0)
            elif abs(dx) < 1 or abs(dy) < 1:
                pixels[x,y] = (0, 120, 0)
            else:
                pixels[x,y] = (10, int(dist*.3)%40, 5)

    # Encode flag length then flag in LSB of R channel, row by row
    bits = []
    length_bits = format(len(flag), '016b')  # 16 bits for length
    for b in length_bits:
        bits.append(int(b))
    for byte in flag:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    pixels = img.load()
    bit_idx = 0
    for y in range(200):
        for x in range(200):
            if bit_idx >= len(bits):
                break
            r, g, b = pixels[x, y]
            r = (r & 0xFE) | bits[bit_idx]
            pixels[x, y] = (r, g, b)
            bit_idx += 1
        if bit_idx >= len(bits):
            break

    img.save("dragon_radar.png")
    print("[+] dragon_radar.png created — give this to players")
    print(f"[+] Flag hidden: {flag.decode()}")

hide_flag("dragon_radar.png", FLAG)