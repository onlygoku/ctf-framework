"""
Init - Bootstrap a new CTF event
"""

import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()


def initialize_ctf():
    console.print("[bold cyan]Welcome to the CTF Framework Setup Wizard![/bold cyan]\n")

    name = Prompt.ask("[yellow]CTF Name[/yellow]", default="MyCTF2025")
    description = Prompt.ask("[yellow]Description[/yellow]", default="A hacking competition")
    flag_prefix = Prompt.ask("[yellow]Flag prefix[/yellow]", default="CTF")
    dynamic = Confirm.ask("[yellow]Enable dynamic scoring?[/yellow]", default=True)

    with open(".env", "w") as f:
        f.write(f"""CTF_NAME={name}
CTF_DESCRIPTION={description}
CTF_FLAG_PREFIX={flag_prefix}
CTF_DYNAMIC_SCORING={str(dynamic).lower()}
CTF_SECRET_KEY={os.urandom(32).hex()}
CTF_DB_PATH=ctf.db
CTF_CHALLENGES_DIR=challenges
CTF_PORT=5000
CTF_MAX_ATTEMPTS=10
CTF_RATE_WINDOW=60
CTF_REGISTRATION=true
""")
    console.print("[green]✓ Created .env[/green]")

    for cat in ["web", "pwn", "crypto", "forensics", "reverse", "misc"]:
        Path(f"challenges/{cat}").mkdir(parents=True, exist_ok=True)
    console.print("[green]✓ Created challenge directories[/green]")

    from .database import Database
    Database("ctf.db")
    console.print("[green]✓ Initialized database[/green]")