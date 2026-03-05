# ── encrypt.py  (this ran to generate the challenge — give to players) ──
"""
CRYPTO-001: Broken Saiyan Cipher (RSA small exponent e=3)
Category: Crypto | Difficulty: Advanced | Points: 400
Flag: CTF{rs4_sm4ll_exp0n3nt_cub3_r00t}
"""
import math

# Small public exponent — VULNERABLE to cube root attack when m^e < n
n = 114763848510684933037248898264492126489496495691797523280746308838099
e = 3
# This ciphertext was produced with: c = pow(m, 3, n)  where m = int.from_bytes(flag, 'big')
# Since m^3 < n, the modular reduction never kicked in — just take cube root of c
c = 148456361628992144539540754444784478402898681038990893026358720730496679423064

print("=" * 60)
print("CRYPTO-001: Broken Saiyan Cipher")
print("=" * 60)
print(f"Public Key:")
print(f"  n = {n}")
print(f"  e = {e}")
print(f"\nCiphertext:")
print(f"  c = {c}")
print("=" * 60)
print("The message was encrypted as: c = m^e mod n")
print("Recover the plaintext message (it's a CTF flag).")