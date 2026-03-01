"""Auto-seed challenges on startup"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Create folders
os.makedirs("challenges", exist_ok=True)
for cat in ["web", "pwn", "crypto", "forensics", "reverse", "misc"]:
    os.makedirs(f"challenges/{cat}", exist_ok=True)
print("[SEED] ✅ Folders ready")

from ctf_core.challenge_manager import ChallengeManager
from ctf_core.database import Database
from ctf_core.config import Config

config = Config()
print(f"[SEED] DB path: {config.db_path}")
print(f"[SEED] Challenges dir: {config.challenges_dir}")

manager = ChallengeManager(config)

existing = manager.list_challenges()
print(f"[SEED] Existing challenges: {len(existing)}")

if len(existing) >= 6:
    print("[SEED] Already seeded, skipping.")
    sys.exit(0)

challenges = [
    ("web", "SQL Injection 101", 100, "easy",
     "A login form is hiding something. Can you bypass authentication and retrieve the admin flag? Try messing with the input fields."),
    ("web", "JWT Bypass", 200, "medium",
     "This API uses JSON Web Tokens for authentication. The dev made a classic mistake. Can you forge a token and access the admin panel?"),
    ("crypto", "Broken RSA", 200, "medium",
     "We intercepted an RSA-encrypted message. The developer reused primes across two public keys. Use that weakness to recover the plaintext."),
    ("pwn", "Buffer Overflow", 300, "hard",
     "A vulnerable C binary is running on the server. There is no stack canary and no PIE. Overflow the buffer and hijack execution to call the win() function."),
    ("reverse", "Crack Me", 150, "easy",
     "A Python binary checks your input against a secret key using XOR encoding. Reverse the logic and figure out what input makes it print Correct!"),
    ("forensics", "Hidden Message", 250, "hard",
     "We captured a suspicious image file from a hacker's USB drive. Something is hidden inside. Look beyond what the eye can see."),
]

for category, name, points, difficulty, desc in challenges:
    try:
        ch = manager.create_challenge(
            category, name, points, difficulty, description=desc
        )
        print(f"[SEED] ✅ {ch.name} — {ch.flag}")
    except Exception as e:
        print(f"[SEED] ❌ Error: {name} — {e}")

print("[SEED] Done!")
