#!/usr/bin/env python3
"""
CTF Framework - Advanced Capture The Flag Challenge Platform
"""

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

BANNER = """
 ██████╗████████╗███████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
██╔════╝╚══██╔══╝██╔════╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
██║        ██║   █████╗      █████╗  ██████╔╝███████║██╔████╔██║█████╗  
██║        ██║   ██╔══╝      ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝  
╚██████╗   ██║   ██║         ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
 ╚═════╝   ╚═╝   ╚═╝         ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
"""


@click.group()
@click.version_option("1.0.0")
def cli():
    """CTF Framework - A powerful Capture The Flag challenge platform."""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=5000, help="Server port")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def server(host, port, debug):
    """Start the CTF web server."""
    from web.app import create_app
    console.print(Panel(BANNER, style="bold green"))
    console.print(f"[bold cyan]🚀 Starting CTF Server on {host}:{port}[/bold cyan]")
    app = create_app()
    app.run(host=host, port=port, debug=debug)


@cli.command()
@click.argument("category")
@click.argument("name")
@click.option("--points", default=100, help="Challenge point value")
@click.option("--difficulty", type=click.Choice(["easy", "medium", "hard", "insane"]), default="medium")
@click.option("--desc", default="", help="Challenge description")
def create(category, name, points, difficulty, desc):
    """Create a new CTF challenge."""
    from ctf_core.challenge_manager import ChallengeManager
    manager = ChallengeManager()
    challenge = manager.create_challenge(category, name, points, difficulty, description=desc)
    console.print(f"[bold green]✅ Challenge '{name}' created in '{category}'[/bold green]")
    console.print(f"   Points: {points} | Difficulty: {difficulty}")
    console.print(f"   Description: {desc or 'N/A'}")
    console.print(f"   Path: {challenge.path}")
    console.print(f"   Flag: {challenge.flag}")


@cli.command("list")
@click.option("--category", default=None, help="Filter by category")
@click.option("--difficulty", default=None, help="Filter by difficulty")
def list_challenges(category, difficulty):
    """List all available challenges."""
    from ctf_core.challenge_manager import ChallengeManager
    from rich.table import Table

    manager = ChallengeManager()
    challenges = manager.list_challenges(category=category, difficulty=difficulty)

    if not challenges:
        console.print("[yellow]No challenges found. Create one with: python ctf.py create[/yellow]")
        return

    table = Table(title="CTF Challenges", style="cyan")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold white")
    table.add_column("Category", style="yellow")
    table.add_column("Points", style="green")
    table.add_column("Difficulty", style="magenta")
    table.add_column("Solves", style="cyan")
    table.add_column("Flag", style="dim")

    diff_colors = {"easy": "green", "medium": "yellow", "hard": "red", "insane": "bold red"}
    for ch in challenges:
        color = diff_colors.get(ch.difficulty, "white")
        table.add_row(
            str(ch.id), ch.name, ch.category, str(ch.points),
            f"[{color}]{ch.difficulty}[/{color}]",
            str(ch.solves), ch.flag
        )

    console.print(table)


@cli.command()
@click.argument("challenge_id")
@click.argument("flag")
@click.option("--team", default="anonymous", help="Team name")
def submit(challenge_id, flag, team):
    """Submit a flag for a challenge."""
    from ctf_core.flag_validator import FlagValidator
    validator = FlagValidator()
    result = validator.validate(challenge_id, flag, team)
    if result.correct:
        console.print(f"[bold green]🎉 CORRECT! +{result.points} points[/bold green]")
    else:
        console.print(f"[bold red]❌ Wrong flag. Try again![/bold red]")
        if result.hint:
            console.print(f"[yellow]💡 Hint: {result.hint}[/yellow]")


@cli.command()
@click.option("--top", default=10, help="Number of teams to show")
def scoreboard(top):
    """Display the scoreboard."""
    from ctf_core.scoreboard import Scoreboard
    from rich.table import Table

    sb = Scoreboard()
    scores = sb.get_top(top)

    if not scores:
        console.print("[yellow]No teams on the scoreboard yet.[/yellow]")
        return

    table = Table(title=f"🏆 Top {top} Teams", style="gold1")
    table.add_column("Rank", style="bold yellow")
    table.add_column("Team", style="bold white")
    table.add_column("Score", style="bold green")
    table.add_column("Solves", style="cyan")
    table.add_column("Last Solve", style="dim")

    medals = ["🥇", "🥈", "🥉"]
    for i, entry in enumerate(scores):
        rank = medals[i] if i < 3 else str(i + 1)
        table.add_row(rank, entry.team, str(entry.score), str(entry.solves), entry.last_solve)

    console.print(table)


@cli.command()
@click.argument("challenge_id")
def delete(challenge_id):
    """Delete a challenge by ID."""
    from ctf_core.challenge_manager import ChallengeManager
    manager = ChallengeManager()
    if manager.delete_challenge(challenge_id):
        console.print(f"[bold green]✅ Challenge {challenge_id} deleted.[/bold green]")
    else:
        console.print(f"[bold red]❌ Challenge {challenge_id} not found.[/bold red]")


@cli.group()
def docker():
    """Docker challenge management."""
    pass


@docker.command("build")
@click.argument("challenge_id")
def docker_build(challenge_id):
    """Build Docker image for a challenge."""
    from ctf_core.docker_manager import DockerManager
    dm = DockerManager()
    console.print(f"[cyan]🐳 Building image for {challenge_id}...[/cyan]")
    result = dm.build(challenge_id)
    if result.success:
        console.print(f"[green]✅ Image built: {result.image_name}[/green]")
    else:
        console.print(f"[red]❌ Build failed: {result.error}[/red]")


@docker.command("deploy")
@click.argument("challenge_id")
@click.option("--port", default=None, type=int)
def docker_deploy(challenge_id, port):
    """Deploy a challenge container."""
    from ctf_core.docker_manager import DockerManager
    dm = DockerManager()
    result = dm.deploy(challenge_id, port=port)
    if result.success:
        console.print(f"[green]✅ Deployed at port {result.port}[/green]")
    else:
        console.print(f"[red]❌ Deploy failed: {result.error}[/red]")


@cli.command()
def init():
    """Initialize a new CTF event."""
    from ctf_core.init import initialize_ctf
    console.print(Panel(BANNER, style="bold green"))
    console.print("[bold cyan]🎯 Initializing CTF Framework...[/bold cyan]\n")
    initialize_ctf()
    console.print("\n[bold green]✅ CTF Framework initialized![/bold green]")
    console.print("[dim]Next steps:[/dim]")
    console.print("[cyan]  1. python ctf.py create web 'My Challenge' --points 100 --difficulty easy --desc 'description'[/cyan]")
    console.print("[cyan]  2. python ctf.py list[/cyan]")
    console.print("[cyan]  3. python ctf.py server[/cyan]")


if __name__ == "__main__":
    cli()