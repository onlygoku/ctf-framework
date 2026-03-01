"""
Challenge Manager - Core challenge lifecycle management
"""

import os
import json
import uuid
import hashlib
import shutil
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from .config import Config
from .database import Database


CHALLENGE_CATEGORIES = [
    "web", "pwn", "crypto", "forensics", "reverse",
    "misc", "osint", "network", "mobile", "blockchain"
]

CHALLENGE_TEMPLATE = {
    "web": """# {name} - Web Challenge\n\n## Description\n{description}\n\n## Flag\n`CTF{{{flag}}}`\n""",
    "crypto": """# {name} - Cryptography Challenge\n\n## Description\n{description}\n\n## Flag\n`CTF{{{flag}}}`\n""",
    "pwn": """# {name} - Binary Exploitation\n\n## Description\n{description}\n\n## Connection\n`nc {host} {port}`\n\n## Flag\n`CTF{{{flag}}}`\n"""
}


@dataclass
class Challenge:
    id: str
    name: str
    category: str
    points: int
    difficulty: str
    description: str = ""
    flag: str = ""
    author: str = "anonymous"
    solves: int = 0
    hints: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    docker_enabled: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    path: str = ""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Challenge":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ChallengeManager:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db = Database(self.config.db_path)
        self.challenges_dir = Path(self.config.challenges_dir)
        self.challenges_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                points INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                description TEXT DEFAULT '',
                flag TEXT NOT NULL,
                author TEXT DEFAULT 'anonymous',
                solves INTEGER DEFAULT 0,
                hints TEXT DEFAULT '[]',
                files TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]',
                docker_enabled INTEGER DEFAULT 0,
                created_at TEXT,
                path TEXT DEFAULT ''
            )
        """)

    def create_challenge(self, category, name, points=100, difficulty="medium",
                         description="", author="anonymous", docker_enabled=False) -> Challenge:
        if category not in CHALLENGE_CATEGORIES:
            raise ValueError(f"Invalid category. Choose from: {CHALLENGE_CATEGORIES}")

        challenge_id = str(uuid.uuid4())[:8]
        flag = self._generate_flag(name, challenge_id)
        slug = name.lower().replace(" ", "_")
        path = str(self.challenges_dir / category / slug)

        challenge = Challenge(
            id=challenge_id, name=name, category=category, points=points,
            difficulty=difficulty,
            description=description or f"Solve this {category} challenge to get the flag.",
            flag=flag, author=author, docker_enabled=docker_enabled, path=path,
        )

        self._scaffold_directory(challenge)
        self._save_to_db(challenge)
        return challenge

    def _generate_flag(self, name: str, challenge_id: str) -> str:
        seed = f"{name}{challenge_id}{os.urandom(8).hex()}"
        h = hashlib.sha256(seed.encode()).hexdigest()[:24]
        return f"CTF{{{h}}}"

    def _scaffold_directory(self, challenge: Challenge):
        path = Path(challenge.path)
        path.mkdir(parents=True, exist_ok=True)

        meta = challenge.to_dict()
        del meta["flag"]
        with open(path / "challenge.json", "w") as f:
            json.dump(meta, f, indent=2)

        with open(path / ".flag", "w") as f:
            f.write(challenge.flag)

        template = CHALLENGE_TEMPLATE.get(challenge.category, CHALLENGE_TEMPLATE["web"])
        readme = template.format(
            name=challenge.name, description=challenge.description,
            flag=challenge.flag, host="challenge.ctf.local", port=self._next_port(),
        )
        with open(path / "README.md", "w") as f:
            f.write(readme)

        if challenge.category == "web":
            self._scaffold_web(path, challenge)
        elif challenge.category == "pwn":
            self._scaffold_pwn(path, challenge)
        elif challenge.category == "crypto":
            self._scaffold_crypto(path, challenge)
        elif challenge.category == "forensics":
            self._scaffold_forensics(path, challenge)
        elif challenge.category == "reverse":
            self._scaffold_reverse(path, challenge)

        if challenge.docker_enabled:
            self._scaffold_docker(path, challenge)

    def _scaffold_web(self, path: Path, challenge: Challenge):
        app_dir = path / "app"
        app_dir.mkdir(exist_ok=True)
        with open(app_dir / "app.py", "w") as f:
            f.write(f'''from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "{challenge.flag}")

INDEX = """<!DOCTYPE html>
<html><head><title>{challenge.name}</title></head>
<body><h1>{challenge.name}</h1><p>Find the flag!</p></body></html>"""

@app.route("/")
def index():
    return render_template_string(INDEX)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
''')
        with open(app_dir / "requirements.txt", "w") as f:
            f.write("flask==3.0.0\n")

    def _scaffold_pwn(self, path: Path, challenge: Challenge):
        src_dir = path / "src"
        src_dir.mkdir(exist_ok=True)
        with open(src_dir / "chall.c", "w") as f:
            f.write(f'''#include <stdio.h>
#include <stdlib.h>

void win() {{
    char flag[64];
    FILE *f = fopen("/flag.txt", "r");
    if (!f) {{ puts("Flag file not found!"); exit(1); }}
    fgets(flag, 64, f);
    printf("Flag: %s\\n", flag);
}}

void vulnerable() {{
    char buf[64];
    printf("Input: ");
    gets(buf);  // Intentionally vulnerable
    printf("You said: %s\\n", buf);
}}

int main() {{
    setbuf(stdout, NULL);
    vulnerable();
    return 0;
}}
''')
        with open(src_dir / "Makefile", "w") as f:
            f.write("all:\n\tgcc -m64 -fno-stack-protector -no-pie -o chall chall.c\n")
        with open(path / "solve.py", "w") as f:
            f.write('''from pwn import *
elf = ELF("./src/chall")
p = remote("challenge.ctf.local", 9001)
win_addr = elf.symbols["win"]
offset = 72  # Find with cyclic()
payload = b"A" * offset + p64(win_addr)
p.sendlineafter(b"Input: ", payload)
print(p.recvall().decode())
''')

    def _scaffold_crypto(self, path: Path, challenge: Challenge):
        with open(path / "chall.py", "w") as f:
            f.write(f'''from Crypto.Util.number import getPrime, bytes_to_long

FLAG = b"{challenge.flag}"

def encrypt(msg):
    p, q = getPrime(512), getPrime(512)
    n = p * q
    e = 65537
    c = pow(bytes_to_long(msg), e, n)
    return {{"n": n, "e": e, "c": c}}

result = encrypt(FLAG)
print(f"n = {{result[\'n\']}}")
print(f"e = {{result[\'e\']}}")
print(f"c = {{result[\'c\']}}")
''')
        with open(path / "solve.py", "w") as f:
            f.write("from Crypto.Util.number import long_to_bytes\nn = \ne = \nc = \n# Implement attack here\n")

    def _scaffold_forensics(self, path: Path, challenge: Challenge):
        (path / "dist").mkdir(exist_ok=True)
        with open(path / "gen.py", "w") as f:
            f.write(f'FLAG = "{challenge.flag}"\n# Generate forensics artifact here\n')

    def _scaffold_reverse(self, path: Path, challenge: Challenge):
        src_dir = path / "src"
        src_dir.mkdir(exist_ok=True)
        with open(src_dir / "chall.py", "w") as f:
            f.write(f'''import sys
SECRET = [ord(c) ^ 0x42 for c in "{challenge.flag}"]

def check(inp):
    return len(inp) == len(SECRET) and all(ord(c)^0x42==s for c,s in zip(inp, SECRET))

if __name__ == "__main__":
    inp = input("Enter the flag: ")
    print("Correct!" if check(inp) else "Wrong!")
''')

    def _scaffold_docker(self, path: Path, challenge: Challenge):
        with open(path / "Dockerfile", "w") as f:
            f.write(f'''FROM python:3.11-slim
RUN useradd -m ctf
WORKDIR /home/ctf
COPY . .
RUN echo "{challenge.flag}" > /flag.txt && chmod 444 /flag.txt
RUN pip install -r app/requirements.txt 2>/dev/null || true
USER ctf
EXPOSE 5000
CMD ["python3", "app/app.py"]
''')
        with open(path / "docker-compose.yml", "w") as f:
            f.write(f'''version: "3.8"
services:
  challenge:
    build: .
    ports:
      - "{self._next_port()}:5000"
    restart: unless-stopped
    environment:
      - FLAG={challenge.flag}
    security_opt:
      - no-new-privileges:true
''')

    def _next_port(self) -> int:
        count = self.db.fetchone("SELECT COUNT(*) FROM challenges")[0] or 0
        return 10000 + count

    def _save_to_db(self, challenge: Challenge):
        self.db.execute("""
            INSERT OR REPLACE INTO challenges
            (id, name, category, points, difficulty, description, flag,
             author, solves, hints, files, tags, docker_enabled, created_at, path)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            challenge.id, challenge.name, challenge.category, challenge.points,
            challenge.difficulty, challenge.description, challenge.flag,
            challenge.author, challenge.solves, json.dumps(challenge.hints),
            json.dumps(challenge.files), json.dumps(challenge.tags),
            int(challenge.docker_enabled), challenge.created_at, challenge.path
        ))

    def list_challenges(self, category=None, difficulty=None) -> List[Challenge]:
        query = "SELECT * FROM challenges WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"; params.append(category)
        if difficulty:
            query += " AND difficulty = ?"; params.append(difficulty)
        query += " ORDER BY category, points ASC"
        return [self._row_to_challenge(r) for r in self.db.fetchall(query, params)]

    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        row = self.db.fetchone("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
        return self._row_to_challenge(row) if row else None

    def _row_to_challenge(self, row) -> Challenge:
        cols = ["id","name","category","points","difficulty","description","flag",
                "author","solves","hints","files","tags","docker_enabled","created_at","path"]
        data = dict(zip(cols, row))
        data["hints"] = json.loads(data["hints"])
        data["files"] = json.loads(data["files"])
        data["tags"] = json.loads(data["tags"])
        data["docker_enabled"] = bool(data["docker_enabled"])
        return Challenge(**data)

    def update_solve_count(self, challenge_id: str):
        self.db.execute("UPDATE challenges SET solves = solves + 1 WHERE id = ?", (challenge_id,))

    def delete_challenge(self, challenge_id: str) -> bool:
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return False
        if challenge.path and os.path.exists(challenge.path):
            shutil.rmtree(challenge.path)
        self.db.execute("DELETE FROM challenges WHERE id = ?", (challenge_id,))
        return True