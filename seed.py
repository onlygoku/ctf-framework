"""
seed.py - DBZ CTF Platform Database Seeder
Run: python seed.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from ctf_core.auth import AuthManager
from ctf_core.challenge_manager import ChallengeManager
from ctf_core.config import Config

# ─────────────────────────────────────────────────────────────
# CHALLENGES
# ─────────────────────────────────────────────────────────────

CHALLENGES = [

    # ── WEB ──────────────────────────────────────────────────
    {
        "id":          "web-001",
        "name":        "Dragon Ball Database",
        "category":    "Web",
        "difficulty":  "intermediate",
        "points":      200,
        "description": (
            "The DBZ Warrior Database lets you search for warriors by name. "
            "Something feels off about how it handles your input... "
            "Maybe the database holds more secrets than just warrior stats."
        ),
        "flag":  "CTF{sqli_union_s3lect_p0wer}",
        "hints": [
            "SQL queries can be manipulated if user input is not sanitised.",
            "Try injecting a UNION SELECT statement into the search box.",
            "SQLite stores all table names in a special table called sqlite_master.",
        ],
        "url":   "",   # set to http://YOUR_SERVER:5001 when deployed
        "files": [],
    },

    {
        "id":          "web-002",
        "name":        "Saiyan Auth Bypass",
        "category":    "Web",
        "difficulty":  "advanced",
        "points":      350,
        "description": (
            "The Saiyan Authentication Portal uses JWT tokens to control access. "
            "Only the Supreme Kai role can unlock the secret chamber. "
            "Can you forge your identity and elevate your privileges?"
        ),
        "flag":  "CTF{jwt_n0n3_alg_byp4ss}",
        "hints": [
            "Decode your JWT token at jwt.io — examine the header carefully.",
            "What algorithms does the server accept in the alg field?",
            "Some JWT libraries skip signature verification when alg is set to none.",
        ],
        "url":   "",   # set to http://YOUR_SERVER:5002 when deployed
        "files": [],
    },

    {
        "id":          "web-003",
        "name":        "Frieza's Secret Files",
        "category":    "Web",
        "difficulty":  "intermediate",
        "points":      250,
        "description": (
            "Frieza Corp's file system lets authenticated warriors download their own files. "
            "Frieza has a classified document hidden in the system. "
            "You have valid credentials — can you access files that aren't yours?"
        ),
        "flag":  "CTF{id0r_acc3ss_c0ntr0l_byp4ss}",
        "hints": [
            "Login with: goku / kakarot",
            "Notice your file ID returned in the response.",
            "Try accessing a different file ID — does the server actually verify ownership?",
        ],
        "url":   "",   # set to http://YOUR_SERVER:5003 when deployed
        "files": [],
    },

    # ── CRYPTO ───────────────────────────────────────────────
    {
        "id":          "crypto-001",
        "name":        "Broken Saiyan Cipher",
        "category":    "Crypto",
        "difficulty":  "advanced",
        "points":      400,
        "description": (
            "We intercepted an RSA-encrypted transmission from Frieza's fleet. "
            "The public key uses an unusually small exponent (e=3). "
            "The message was short enough that m^e never wrapped around n... "
            "Recover the plaintext."
        ),
        "flag":  "CTF{rs4_sm4ll_exp0n3nt_cub3_r00t}",
        "hints": [
            "RSA with small e is vulnerable when the plaintext m is small enough that m^e < n.",
            "When m^e < n, the modular reduction never activates — ciphertext is literally m^e.",
            "Take the integer cube root of the ciphertext to recover m.",
        ],
        "url":   "",
        "files": ["challenge.py"],
    },

    {
        "id":          "crypto-002",
        "name":        "Namekian XOR Scroll",
        "category":    "Crypto",
        "difficulty":  "intermediate",
        "points":      250,
        "description": (
            "Two ancient Namekian scrolls were encrypted with the same XOR key. "
            "One plaintext is already known to our intelligence team. "
            "Recover the key, then decrypt the second scroll to find the flag."
        ),
        "flag":  "CTF{x0r_k3y_r3us3_att4ck}",
        "hints": [
            "XOR ciphertext1 with the known plaintext to recover the key stream.",
            "The key is short and repeating — find the period.",
            "Use the recovered key to decrypt ciphertext 2.",
        ],
        "url":   "",
        "files": ["challenge.py"],
    },

    # ── FORENSICS ────────────────────────────────────────────
    {
        "id":          "forensics-001",
        "name":        "Hidden Power Level",
        "category":    "Forensics",
        "difficulty":  "intermediate",
        "points":      300,
        "description": (
            "A suspicious radar image was recovered from Frieza's scouter device. "
            "Our analysts believe a message is hidden inside the image data. "
            "Find it."
        ),
        "flag":  "CTF{l5b_st3g0_p0w3r_l3v3l}",
        "hints": [
            "Steganography — secret data can be hidden in image pixels.",
            "Check the least significant bits (LSB) of the red channel.",
            "The first 16 bits encode the message length, followed by the flag bytes.",
        ],
        "url":   "",
        "files": ["dragon_radar.png"],
    },

    {
        "id":          "forensics-002",
        "name":        "Namek Ruins Fragment",
        "category":    "Forensics",
        "difficulty":  "intermediate",
        "points":      300,
        "description": (
            "A binary data dump was recovered from the ruins of Planet Namek. "
            "Somewhere inside this file is an archive containing vital intelligence. "
            "Extract it."
        ),
        "flag":  "CTF{f1l3_c4rv1ng_d4t4_r3c0v3ry}",
        "hints": [
            "Binary files can contain embedded archives hidden inside junk data.",
            "ZIP files always start with a magic signature: PK\\x03\\x04",
            "Use binwalk, strings, or write a Python script to find and extract it.",
        ],
        "url":   "",
        "files": ["namek_ruins.bin"],
    },

    # ── REVERSE ──────────────────────────────────────────────
    {
        "id":          "reverse-001",
        "name":        "Saiyan Crackme",
        "category":    "Reverse",
        "difficulty":  "advanced",
        "points":      400,
        "description": (
            "A mysterious program guards a Saiyan secret. "
            "Find the correct input to unlock it. "
            "No brute force — you must understand the logic."
        ),
        "flag":  "CTF{r3v3rs3_th3_s4iy4n_c0d3}",
        "hints": [
            "Read the source carefully — Python is not fully compiled.",
            "Look for arrays of numbers that could represent ASCII character codes.",
            "chr() converts an integer to its character. Try it on each value.",
        ],
        "url":   "",
        "files": ["crackme.py"],
    },

    # ── OSINT ────────────────────────────────────────────────
    {
        "id":          "osint-001",
        "name":        "Find Kakarot",
        "category":    "OSINT",
        "difficulty":  "intermediate",
        "points":      200,
        "description": (
            "Intelligence reports indicate that a Saiyan operative codenamed Kakarot "
            "has been hiding in plain sight. We recovered a suspicious image from his last "
            "known location. Find the flag he left behind."
        ),
        "flag":  "CTF{0s1nt_k4k4r0t_f0und}",
        "hints": [
            "Images carry metadata that is invisible to the naked eye.",
            "Tools like exiftool, strings, or identify -verbose can reveal hidden fields.",
            "Check every EXIF field — the flag is in a standard metadata tag.",
        ],
        "url":   "",
        "files": ["challenge.jpg"],
    },

    # ── MISC ─────────────────────────────────────────────────
    {
        "id":          "misc-001",
        "name":        "Hyperbolic Time Chamber",
        "category":    "Misc",
        "difficulty":  "advanced",
        "points":      450,
        "description": (
            "You have been locked inside the Hyperbolic Time Chamber — "
            "a restricted Python jail. Most builtins have been stripped away. "
            "Escape the sandbox and prove your power level."
        ),
        "flag":  "CTF{j4il_3sc4p3_built1ns_byp4ss}",
        "hints": [
            "Every Python object has a __class__ attribute — start there.",
            "Follow the MRO: __class__ -> __bases__ -> __subclasses__()",
            "__init__.__globals__ can give you back what was taken away.",
        ],
        "url":   "",   # set to nc YOUR_SERVER 4444 when deployed
        "files": [],
    },
]

# ─────────────────────────────────────────────────────────────
# ADMIN ACCOUNT
# ─────────────────────────────────────────────────────────────

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",    "admin@ctf.local")

# ─────────────────────────────────────────────────────────────
# SEED
# ─────────────────────────────────────────────────────────────

def seed():
    print("=" * 55)
    print("  DBZ CTF Platform — Database Seeder")
    print("=" * 55)

    config = Config()
    auth   = AuthManager(config)
    cm     = ChallengeManager(config)

    # ── Challenges ──────────────────────────────────────────
    print("\n[*] Seeding challenges...")
    seeded = 0
    for ch in CHALLENGES:
        try:
            existing = cm.get_challenge(ch["id"])
            if existing:
                print(f"  [~] SKIP   {ch['id']} — {ch['name']} (already exists)")
                continue
            cm.create_challenge(
                id          = ch["id"],
                name        = ch["name"],
                category    = ch["category"],
                difficulty  = ch["difficulty"],
                points      = ch["points"],
                description = ch["description"],
                flag        = ch["flag"],
                hints       = ch.get("hints", []),
                url         = ch.get("url", ""),
                files       = ch.get("files", []),
            )
            print(f"  [+] ADDED  {ch['id']} — {ch['name']} ({ch['points']} pts)")
            seeded += 1
        except Exception as e:
            # Fallback: try without optional fields
            try:
                cm.create_challenge(
                    id          = ch["id"],
                    name        = ch["name"],
                    category    = ch["category"],
                    difficulty  = ch["difficulty"],
                    points      = ch["points"],
                    description = ch["description"],
                    flag        = ch["flag"],
                    hints       = ch.get("hints", []),
                )
                print(f"  [+] ADDED  {ch['id']} — {ch['name']} ({ch['points']} pts)")
                seeded += 1
            except Exception as e2:
                print(f"  [!] ERROR  {ch['id']} — {e2}")

    print(f"\n  {seeded}/{len(CHALLENGES)} challenges seeded.")

    # ── Admin account ────────────────────────────────────────
    print("\n[*] Setting up admin account...")
    try:
        existing = auth.get_user(ADMIN_USERNAME)
        if existing:
            print(f"  [~] Admin '{ADMIN_USERNAME}' already exists — skipping.")
        else:
            auth.register(
                username = ADMIN_USERNAME,
                password = ADMIN_PASSWORD,
                email    = ADMIN_EMAIL,
                is_admin = True,
                verified = True,
            )
            print(f"  [+] Admin account created: {ADMIN_USERNAME}")
    except Exception as e:
        print(f"  [!] Admin error: {e}")

    # ── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  SEED COMPLETE")
    print("=" * 55)
    cats = {}
    for ch in CHALLENGES:
        cats[ch["category"]] = cats.get(ch["category"], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat:<12} {count} challenge(s)")
    total = sum(ch["points"] for ch in CHALLENGES)
    print(f"\n  Total challenges : {len(CHALLENGES)}")
    print(f"  Total points     : {total}")
    print(f"  Admin account    : {ADMIN_USERNAME}")
    print("=" * 55)
    print()

if __name__ == "__main__":
    seed()