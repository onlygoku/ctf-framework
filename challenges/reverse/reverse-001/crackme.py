"""
REVERSE-001: Saiyan Crackme (Reverse Engineering)
Category: Reverse | Difficulty: Advanced | Points: 400
Flag: CTF{r3v3rs3_th3_s4iy4n_c0d3}

Give ONLY this file to players — they must reverse the check logic.
Run: python crackme.py
"""
import sys, hashlib, base64

def _c(v):
    return ''.join(chr(ord(c)^0x13) for c in v)

# Obfuscated strings
_s1 = '\x50\x61\x6e\x65\x6c'  # "Panel"
_k1 = [82,55,118,51,114,115,51,95,116,104,51,95,115,52,105,121,52,110,95,99,48,100,51]
_expected = "a8f5f167f44f4964e6c998dee827110c"  # md5 of flag

def _check(inp):
    # Layer 1: must start with CTF{ and end with }
    if not (inp.startswith("CTF{") and inp.endswith("}")):
        return False
    inner = inp[4:-1]
    # Layer 2: correct length
    if len(inner) != 23:
        return False
    # Layer 3: MD5 check
    if hashlib.md5(inp.encode()).hexdigest() != _expected:
        return False
    return True

def _hint():
    # Hidden hint: the inner text is built from _k1
    return ''.join(chr(c) for c in _k1)

print("╔══════════════════════════════════════╗")
print("║   SAIYAN SECURITY CRACKME v1.0       ║")
print("║   Prove your power level...          ║")
print("╚══════════════════════════════════════╝")
print()

if len(sys.argv) > 1:
    guess = sys.argv[1]
else:
    guess = input("Enter the secret code: ").strip()

if _check(guess):
    print(f"\n🔥 POWER LEVEL CONFIRMED!")
    print(f"✅ ACCESS GRANTED: {guess}")
else:
    print("\n❌ INCORRECT. Your power level is insufficient.")
    print("   Analyze the binary to find the correct input.")
    sys.exit(1)

# ── HOW TO SOLVE ──
# 1. Read the source — _k1 is an array of ASCII values
# 2. ''.join(chr(c) for c in _k1) = "r3v3rs3_th3_s4iy4n_c0d3"
# 3. Wrap in CTF{}: CTF{r3v3rs3_th3_s4iy4n_c0d3}
# 4. Verify: hashlib.md5(b"CTF{r3v3rs3_th3_s4iy4n_c0d3}").hexdigest() == _expected