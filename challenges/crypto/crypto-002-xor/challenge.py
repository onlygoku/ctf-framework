# ── challenge.py  (give this to players) ──
"""
CRYPTO-002: Namekian XOR Scroll (XOR Key Reuse)
Category: Crypto | Difficulty: Intermediate | Points: 250
Flag: CTF{x0r_k3y_r3us3_att4ck}

Two messages encrypted with the SAME XOR key.
One plaintext is known. Recover the key, decrypt the flag.
"""

key = b"NAMEK"   # repeating key, 5 bytes

msg1 = b"Piccolo is the strongest Namekian warrior alive!!"
msg2 = b"CTF{x0r_k3y_r3us3_att4ck} - Dende's secret note"

def xor_encrypt(data, key):
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

ct1 = xor_encrypt(msg1, key)
ct2 = xor_encrypt(msg2, key)

print("=" * 60)
print("CRYPTO-002: Namekian XOR Scroll")
print("=" * 60)
print(f"Known plaintext  : {msg1.decode()}")
print(f"Ciphertext 1 (hex): {ct1.hex()}")
print()
print(f"Ciphertext 2 (hex): {ct2.hex()}")
print("=" * 60)
print("Both messages were encrypted with the same repeating key.")
print("Recover the key from ciphertext 1 + known plaintext.")
print("Use that key to decrypt ciphertext 2.")