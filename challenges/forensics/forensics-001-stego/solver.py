# ── solver.py  (solution — do NOT give to players) ──
from PIL import Image

img = Image.open("dragon_radar.png")
pixels = img.load()
w, h = img.size

bits = []
for y in range(h):
    for x in range(w):
        r, g, b = pixels[x, y]
        bits.append(r & 1)

# Read length (first 16 bits)
length = int(''.join(map(str, bits[:16])), 2)

# Read flag bytes
flag_bits = bits[16:16 + length*8]
flag = []
for i in range(0, len(flag_bits), 8):
    byte = int(''.join(map(str, flag_bits[i:i+8])), 2)
    flag.append(chr(byte))

print("Flag:", ''.join(flag))
# Output: CTF{l5b_st3g0_p0w3r_l3v3l}