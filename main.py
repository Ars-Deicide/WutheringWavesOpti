"""
WutheringWavesOpti — CLI entry point

Commands:
  link      Show your linked account info (parsed from game logs)
  convene   Fetch and display your convene history + pity stats
  echoes    Score your echo build for a chosen resonator
"""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from wuwa.log_parser import load_credentials
from wuwa.convene import fetch_all, pity_stats, POOL_TYPES, RARITY_COLOR
from wuwa.echo import (
    score_build, prompt_echo, RESONATOR_ARCHETYPES, ARCHETYPES,
    ECHO_SLOTS, grade
)

console = Console()


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Wuthering Waves account optimizer."""
    pass


# ---------------------------------------------------------------------------
# link — show parsed account credentials
# ---------------------------------------------------------------------------

HOW_TO_GET_URL = """
[bold cyan]How to get your Convene URL[/bold cyan]

The convene URL is a temporary link the game generates when you open your
pull history. It contains your player ID and a session token.

[bold]Method — Fiddler (free, 2 minutes):[/bold]

  1. Download Fiddler Classic from [link]https://www.telerik.com/fiddler[/link]
  2. Install and open Fiddler
  3. Go to Tools → Options → HTTPS → tick "Decrypt HTTPS traffic" → OK
  4. Launch Wuthering Waves and open Convene → Convene Records
  5. In Fiddler, press Ctrl+F and search for [yellow]aki-gm-resources[/yellow]
  6. Click the matching request and copy the full URL from the top bar
  7. Paste it here:

     [bold]python main.py link --url "PASTE_URL_HERE"[/bold]
"""


@cli.command()
@click.option("--url", default=None, help="Paste your convene URL to link your account.")
@click.option("--how", is_flag=True, help="Show instructions for getting your convene URL.")
def link(url, how):
    """Link your Wuthering Waves account."""
    if how:
        console.print(HOW_TO_GET_URL)
        return

    if url:
        from wuwa.log_parser import parse_convene_url, save_credentials
        creds = parse_convene_url(url)
        if not creds:
            console.print("[red]Could not parse that URL. Make sure you copied the full convene URL.[/red]")
            console.print("Run [bold]python main.py link --how[/bold] for instructions.")
            sys.exit(1)
        save_credentials(creds)
        console.print("[green]Account linked and saved![/green]")
    else:
        console.print("\n[bold]Searching for Wuthering Waves account...[/bold]")
        try:
            creds = load_credentials()
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")
            sys.exit(1)

    panel = Panel(
        f"[green]Player ID:[/green]  {creds['player_id']}\n"
        f"[green]Server ID:[/green]  {creds['server_id']}\n"
        f"[green]Region:  [/green]  {creds['svr_area'].upper()}\n"
        f"[green]Language:[/green]  {creds['lang']}",
        title="[bold cyan]Linked Account[/bold cyan]",
        border_style="cyan",
    )
    console.print(panel)


# ---------------------------------------------------------------------------
# convene — fetch history and show pity
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--pools", default="1,2,3,4", show_default=True,
              help="Comma-separated pool type IDs to fetch.")
def convene(pools):
    """Fetch convene history and show pity counters for each banner."""
    try:
        creds = load_credentials()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    pool_ids = [int(p) for p in pools.split(",") if p.strip().isdigit()]

    console.print(f"\n[bold]Fetching convene history for {len(pool_ids)} pool(s)...[/bold]")
    try:
        all_records = fetch_all(creds, pool_ids)
    except Exception as e:
        console.print(f"[red]Failed to fetch records: {e}[/red]")
        sys.exit(1)

    for pool_type, records in all_records.items():
        pool_name = POOL_TYPES.get(pool_type, f"Pool {pool_type}")
        if not records:
            console.print(f"\n[dim]{pool_name}: no records found[/dim]")
            continue

        stats = pity_stats(records)

        # Summary panel
        console.print(Panel(
            f"Pulls: [bold]{stats['total_pulls']}[/bold]  |  "
            f"5★ count: [bold yellow]{stats['total_5star']}[/bold yellow]  |  "
            f"5★ rate: [bold]{stats['rate_5star']}%[/bold]\n"
            f"Current pity (5★): [bold red]{stats['current_pity_5']}[/bold red]  |  "
            f"Current pity (4★): [bold magenta]{stats['current_pity_4']}[/bold magenta]",
            title=f"[bold]{pool_name}[/bold]",
            border_style="blue",
        ))

        # Recent 20 pulls table
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", min_width=18)
        table.add_column("Type", width=12)
        table.add_column("Rarity", width=6, justify="center")
        table.add_column("Time", width=20)

        for r in records[:20]:
            star = "★" * r.rarity
            rarity_style = {"5": "bold yellow", "4": "bold magenta", "3": "blue"}.get(str(r.rarity), "")
            table.add_row(
                str(r.pull_number),
                r.name,
                r.type,
                f"[{rarity_style}]{star}[/{rarity_style}]",
                r.pull_time,
            )

        console.print(table)


# ---------------------------------------------------------------------------
# echoes — score an echo build
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("resonator", required=False)
def echoes(resonator):
    """Score your echo build for RESONATOR (e.g. 'Jiyan', 'Carlotta')."""
    known = sorted(RESONATOR_ARCHETYPES.keys())

    if not resonator:
        console.print("\n[bold]Known resonators:[/bold]")
        for i, name in enumerate(known, 1):
            console.print(f"  {i:2}. {name}  [dim]({RESONATOR_ARCHETYPES[name]})[/dim]")
        resonator = input("\nEnter resonator name: ").strip()

    if resonator not in RESONATOR_ARCHETYPES:
        console.print(f"[yellow]'{resonator}' not in database — defaulting to crit_dps weights.[/yellow]")

    archetype = RESONATOR_ARCHETYPES.get(resonator, "crit_dps")
    console.print(f"\n[bold cyan]{resonator}[/bold cyan] — archetype: [bold]{archetype}[/bold]")
    console.print("Enter stats for each echo slot. Leave substat name blank to stop.\n")

    echo_list = []
    for slot in range(1, ECHO_SLOTS + 1):
        echo_list.append(prompt_echo(slot))

    results = score_build(echo_list, resonator)

    table = Table(title=f"\n{resonator} — Echo Scores", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Slot", width=5, justify="center")
    table.add_column("Name", min_width=16)
    table.add_column("Main Stat", min_width=14)
    table.add_column("Score", width=7, justify="right")
    table.add_column("Grade", width=6, justify="center")

    for r in results:
        grade_style = {
            "S": "bold green",
            "A": "bold cyan",
            "B": "bold yellow",
            "C": "yellow",
            "D": "dim red",
        }.get(r["grade"], "")
        table.add_row(
            str(r["slot"]),
            r["name"],
            r["main_stat"],
            str(r["score"]),
            f"[{grade_style}]{r['grade']}[/{grade_style}]",
        )

    console.print(table)

    avg = sum(r["score"] for r in results) / len(results) if results else 0
    overall = grade(avg)
    console.print(f"\n[bold]Overall build score: {avg:.1f} / 100  —  Grade {overall}[/bold]\n")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
