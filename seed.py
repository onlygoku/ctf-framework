"""
seed.py - DBZ CTF Platform Database Seeder

"""

import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from ctf_core.config import Config
from ctf_core.challenge_manager import ChallengeManager

CHALLENGES = [

    # ── WEB ──────────────────────────────────────────────────
    {
        "category":    "web",
        "name":        "Dragon Ball Database",
        "points":      200,
        "difficulty":  "intermediate",
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
    },
    {
        "category":    "web",
        "name":        "Saiyan Auth Bypass",
        "points":      350,
        "difficulty":  "advanced",
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
    },
    {
        "category":    "web",
        "name":        "Frieza's Secret Files",
        "points":      250,
        "difficulty":  "intermediate",
        "description": (
            "Frieza Corp's file system lets authenticated warriors download their own files. "
            "Frieza has a classified document hidden in the system. "
            "You have valid credentials — can you access files that aren't yours?"
        ),
        "flag":  "CTF{id0r_acc3ss_c0ntr0l_byp4ss}",
        "hints": [
            "Login with: goku / kakarot",
            "Notice your file ID returned in the response.",
            "Try accessing a different file ID — does the server verify ownership?",
        ],
    },

    # ── CRYPTO ───────────────────────────────────────────────
    {
        "category":    "crypto",
        "name":        "Broken Saiyan Cipher",
        "points":      400,
        "difficulty":  "advanced",
        "description": (
            "We intercepted an RSA-encrypted transmission from Frieza's fleet. "
            "The public key uses an unusually small exponent (e=3). "
            "The message was short enough that m^e never wrapped around n. "
            "Recover the plaintext."
        ),
        "flag":  "CTF{rs4_sm4ll_exp0n3nt_cub3_r00t}",
        "hints": [
            "RSA with small e is vulnerable when the plaintext m is small enough that m^e < n.",
            "When m^e < n, modular reduction never activates — ciphertext is literally m^e.",
            "Take the integer cube root of the ciphertext to recover m.",
        ],
    },
    {
        "category":    "crypto",
        "name":        "Namekian XOR Scroll",
        "points":      250,
        "difficulty":  "intermediate",
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
    },

    # ── FORENSICS ────────────────────────────────────────────
    {
        "category":    "forensics",
        "name":        "Hidden Power Level",
        "points":      300,
        "difficulty":  "intermediate",
        "description": (
            "A suspicious radar image was recovered from Frieza's scouter device. "
            "Our analysts believe a message is hidden inside the image data. "
            "Find it."
        ),
        "flag":  "CTF{l5b_st3g0_p0w3r_l3v3l}",
        "hints": [
            "Steganography — secret data can be hidden inside image pixels.",
            "Check the least significant bits (LSB) of the red channel.",
            "The first 16 bits encode the message length, followed by the flag bytes.",
        ],
    },
    {
        "category":    "forensics",
        "name":        "Namek Ruins Fragment",
        "points":      300,
        "difficulty":  "intermediate",
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
    },

    # ── REVERSE ──────────────────────────────────────────────
    {
        "category":    "reverse",
        "name":        "Saiyan Crackme",
        "points":      400,
        "difficulty":  "advanced",
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
    },

    # ── OSINT ────────────────────────────────────────────────
    {
        "category":    "osint",
        "name":        "Find Kakarot",
        "points":      200,
        "difficulty":  "intermediate",
        "description": (
            "Intelligence reports indicate that a Saiyan operative codenamed Kakarot "
            "has been hiding in plain sight. We recovered a suspicious image from his "
            "last known location. Find the flag he left behind."
        ),
        "flag":  "CTF{0s1nt_k4k4r0t_f0und}",
        "hints": [
            "Images carry metadata that is invisible to the naked eye.",
            "Tools like exiftool, strings, or identify -verbose can reveal hidden fields.",
            "Check every EXIF field — the flag is in a standard metadata tag.",
        ],
    },

    # ── MISC ─────────────────────────────────────────────────
    {
        "category":    "misc",
        "name":        "Hyperbolic Time Chamber",
        "points":      450,
        "difficulty":  "advanced",
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
    },
]

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",    "admin@ctf.local")


def seed():
    print("=" * 55)
    print("  DBZ CTF Platform - Database Seeder")
    print("=" * 55)

    config = Config()
    cm     = ChallengeManager(config)
    db     = cm.db

    # ── Wipe old challenges, solves, hint unlocks ────────────
    print("\n[*] Clearing old challenge data...")
    db.execute("DELETE FROM challenges")
    db.execute("DELETE FROM solves")
    db.execute("DELETE FROM hint_unlocks")
    print("  [+] Cleared challenges, solves, hint_unlocks")

    # ── Seed challenges ──────────────────────────────────────
    print("\n[*] Seeding challenges...")
    seeded = 0

    for ch in CHALLENGES:
        try:
            created = cm.create_challenge(
                category    = ch["category"],
                name        = ch["name"],
                points      = ch["points"],
                difficulty  = ch["difficulty"],
                description = ch["description"],
            )

            # Set the real flag + hints
            db.execute(
                "UPDATE challenges SET flag=?, hints=? WHERE id=?",
                (ch["flag"], json.dumps(ch.get("hints", [])), created.id)
            )

            print(f"  [+] ADDED  {ch['category']}/{ch['name']} ({ch['points']} pts)")
            seeded += 1

        except Exception as e:
            print(f"  [!] ERROR  {ch['category']}/{ch['name']} — {e}")

    print(f"\n  {seeded}/{len(CHALLENGES)} challenges seeded.")

    # ── Admin account ────────────────────────────────────────
    print("\n[*] Setting up admin account...")
    try:
        from ctf_core.auth import AuthManager
        auth = AuthManager(config)

        existing = db.fetchone(
            "SELECT username FROM teams WHERE username=?", (ADMIN_USERNAME,)
        )
        if existing:
            print(f"  [~] Admin '{ADMIN_USERNAME}' already exists — skipping.")
        else:
            auth.register(
                username = ADMIN_USERNAME,
                password = ADMIN_PASSWORD,
                email    = ADMIN_EMAIL,
            )
            db.execute(
                "UPDATE teams SET is_admin=1, verified=1 WHERE username=?",
                (ADMIN_USERNAME,)
            )
            print(f"  [+] Admin created: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
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
    print(f"  Admin login      : {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print("=" * 55)


if __name__ == "__main__":
    seed()