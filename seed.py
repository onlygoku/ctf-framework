import os
import sys

print("=" * 50)
print("[SEED] Starting seed.py")
print(f"[SEED] Current directory: {os.getcwd()}")
print(f"[SEED] Files here: {os.listdir('.')}")
print("=" * 50)

from dotenv import load_dotenv
load_dotenv()

os.makedirs("challenges", exist_ok=True)
for cat in ["web", "pwn", "crypto", "forensics", "reverse", "misc"]:
    os.makedirs(f"challenges/{cat}", exist_ok=True)
print("[SEED] ✅ Folders created")

from ctf_core.challenge_manager import ChallengeManager
from ctf_core.config import Config

config = Config()
print(f"[SEED] DB: {config.db_path}")
print(f"[SEED] Challenges dir: {config.challenges_dir}")

manager = ChallengeManager(config)
existing = manager.list_challenges()
print(f"[SEED] Existing: {len(existing)}")

if len(existing) >= 11:
    print("[SEED] Already seeded!")
    sys.exit(0)

challenges = [
    ("web", "SQL Injection 101", 100, "easy",
     "A login form is hiding something. Can you bypass authentication and retrieve the admin flag?"),
    ("web", "JWT Bypass", 200, "medium",
     "This API uses JSON Web Tokens for authentication. The dev made a classic mistake."),
    ("crypto", "Broken RSA", 200, "medium",
     "We intercepted an RSA-encrypted message. The developer reused primes across two public keys."),
    ("pwn", "Buffer Overflow", 300, "hard",
     "A vulnerable C binary is running on the server. Overflow the buffer and hijack execution."),
    ("reverse", "Crack Me", 150, "easy",
     "A Python binary checks your input against a secret key using XOR encoding. Reverse it!"),
    ("forensics", "Hidden Message", 250, "hard",
     "We captured a suspicious image file. Something is hidden inside."),

    # 5 NEW CHALLENGES
    ("web", "XSS Attack", 150, "medium",
     "A comment section on this blog reflects user input directly. Inject a script and steal the admin cookie."),
    ("crypto", "Caesar's Secret", 100, "easy",
     "An ancient encryption method was used to hide this message. Shift your thinking and decode the secret."),
    ("osint", "Find The Hacker", 200, "medium",
     "A hacker left traces across the internet. Use open source intelligence to track them down and find the flag they left behind."),
    ("misc", "Base Madness", 100, "easy",
     "This string has been encoded multiple times using different base encodings. Decode it layer by layer to find the flag."),
    ("network", "Packet Secrets", 250, "hard",
     "We captured network traffic during a suspicious data transfer. Analyze the pcap file and extract the hidden flag from the packets."),
]
for category, name, points, difficulty, desc in challenges:
    try:
        ch = manager.create_challenge(category, name, points, difficulty, description=desc)
        print(f"[SEED] ✅ {ch.name} — {ch.flag}")
    except Exception as e:
        print(f"[SEED] ❌ {name} — {e}")

print("[SEED] ✅ Done!")


