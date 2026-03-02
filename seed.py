
import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

def seed():
    os.makedirs("challenges", exist_ok=True)
    for cat in ["web","pwn","crypto","forensics","reverse","misc","osint","network"]:
        os.makedirs(f"challenges/{cat}", exist_ok=True)
    print("[SEED] Folders created")

    from ctf_core.challenge_manager import ChallengeManager
    from ctf_core.config import Config
    config = Config()
    manager = ChallengeManager(config)

    existing = manager.list_challenges()
    print(f"[SEED] Existing: {len(existing)}")

    if len(existing) >= 11:
        print("[SEED] Already seeded!")
        return

    challenges = [
        ("web","SQL Injection 101",100,"easy",
         "A login form is hiding something. Can you bypass authentication?",
         ["Try adding a single quote to the input","Look up SQL injection login bypass payloads"]),
        ("web","JWT Bypass",200,"medium",
         "This API uses JSON Web Tokens. The dev made a classic mistake.",
         ["Check the algorithm field in the JWT header","Try changing the algorithm to none"]),
        ("web","XSS Attack",150,"medium",
         "A comment section reflects user input directly. Inject a script!",
         ["Try a basic script alert first","Look for ways to steal document.cookie"]),
        ("crypto","Broken RSA",200,"medium",
         "We intercepted an RSA-encrypted message. The developer reused primes.",
         ["Try computing GCD of the two moduli","Use the common factor to factor both keys"]),
        ("crypto","Caesars Secret",100,"easy",
         "An ancient encryption method was used. Shift your thinking!",
         ["Try all 26 possible shifts","Look for a shift that gives readable English"]),
        ("pwn","Buffer Overflow",300,"hard",
         "A vulnerable C binary is running. Overflow the buffer and hijack execution.",
         ["Use cyclic pattern to find the offset","Check for a win function in the binary"]),
        ("reverse","Crack Me",150,"easy",
         "A Python binary checks your input using XOR encoding. Reverse it!",
         ["XOR is reversible - apply the same key twice","Try XORing each byte with 0x42"]),
        ("forensics","Hidden Message",250,"hard",
         "We captured a suspicious image file. Something is hidden inside.",
         ["Try running strings on the file","Check for steganography tools like steghide"]),
        ("osint","Find The Hacker",200,"medium",
         "A hacker left traces across the internet. Track them down.",
         ["Check common social media platforms","Try searching their username across multiple sites"]),
        ("misc","Base Madness",100,"easy",
         "This string has been encoded multiple times. Decode it layer by layer.",
         ["Start with base64 decoding","Try base64 then base32 then hex"]),
        ("network","Packet Secrets",250,"hard",
         "We captured network traffic during a suspicious transfer. Analyze the pcap.",
         ["Open in Wireshark and filter by protocol","Follow the TCP stream to see the full data"]),
    ]

    for category, name, points, difficulty, desc, hints in challenges:
        try:
            ch = manager.create_challenge(category, name, points, difficulty, description=desc)
            manager.db.execute(
                "UPDATE challenges SET hints=? WHERE id=?",
                (json.dumps(hints), ch.id)
            )
            print(f"[SEED] OK {ch.name} - {ch.flag}")
        except Exception as e:
            print(f"[SEED] ERROR {name} - {e}")

    print("[SEED] Done!")

seed()
