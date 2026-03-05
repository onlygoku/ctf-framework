# ── generate.py  (run this to create the challenge file) ──
"""
FORENSICS-002: Namek Ruins Data Fragment (File Carving)
Category: Forensics | Difficulty: Intermediate | Points: 300
Flag: CTF{f1l3_c4rv1ng_d4t4_r3c0v3ry}

Run to generate 'namek_ruins.bin' — give that to players.
Players must find and extract a hidden ZIP inside binary data.
"""
import zipfile, io, os, random

FLAG = "CTF{f1l3_c4rv1ng_d4t4_r3c0v3ry}"

# Create a ZIP in memory containing the flag
zip_buf = io.BytesIO()
with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("flag.txt", f"You found the hidden archive!\n\nFlag: {FLAG}\n")
    zf.writestr("readme.txt", "Namek's ancient data recovered from the ruins.")
zip_bytes = zip_buf.getvalue()

# Wrap with random junk data before and after
prefix = bytes([random.randint(0,255) for _ in range(random.randint(800,1200))])
suffix = bytes([random.randint(0,255) for _ in range(random.randint(400,800))])

# Add a fake header so it looks like binary telemetry data
header = b"NAMEK_TELEMETRY_DUMP_V2\x00\x00\x00\x00" + bytes([0xFF,0xFE]*16)

with open("namek_ruins.bin", "wb") as f:
    f.write(header + prefix + zip_bytes + suffix)

print("[+] namek_ruins.bin created — give this to players")
print(f"[+] ZIP signature PK\\x03\\x04 is embedded at offset {len(header)+len(prefix)}")