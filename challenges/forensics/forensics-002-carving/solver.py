# ── solver.py  (solution) ──
import zipfile, io

with open("namek_ruins.bin", "rb") as f:
    data = f.read()

# Find ZIP magic bytes PK\x03\x04
offset = data.find(b'PK\x03\x04')
print(f"[+] ZIP found at offset: {offset}")

zip_data = data[offset:]
with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
    print("[+] ZIP contents:", zf.namelist())
    print(zf.read("flag.txt").decode())
# Output: CTF{f1l3_c4rv1ng_d4t4_r3c0v3ry}