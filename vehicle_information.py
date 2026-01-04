#!/usr/bin/env python3
"""
VEHICLE_INFORMATION (AZOD08)
Author  : azod08
License : MIT

Educational & Ethical Use Only
"""

import os
import json
import time
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlencode

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt
from rich import box

# ================= CONFIG =================

API_BASE = "https://vehicleinfobyterabaap.vercel.app/lookup"
VERSION = "1.1"
console = Console()

# ================= UTILS =================

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def ensure_dirs():
    for d in ["results", "logs", "cache"]:
        os.makedirs(d, exist_ok=True)

def log(msg):
    with open("logs/activity.log", "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def cache_path(rc):
    return f"cache/{hashlib.md5(rc.encode()).hexdigest()}.json"

def mask_phone(phone):
    phone = str(phone)
    if len(phone) > 4:
        return phone[:-4] + "XXXX"
    return phone

# ================= UI =================

def banner():
    console.rule("[bold cyan]VEHICLE INFORMATION (AZOD08)")
    console.print(
        Align.center(
            f"[bold white]Professional Vehicle OSINT Tool[/bold white]\n"
            f"[dim]Version {VERSION} • Author: azod08[/dim]"
        )
    )
    console.print(
        Panel(
            "[bold red]DISCLAIMER[/bold red]\n"
            "This tool is for educational and lawful use only.\n"
            "Unauthorized usage may be illegal.",
            style="red",
        )
    )
    console.rule()

# ================= CORE =================

def fetch_data(rc):
    cache_file = cache_path(rc)

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f), True

    url = f"{API_BASE}?{urlencode({'rc': rc})}"
    start = time.time()

    try:
        r = requests.get(url, timeout=15)
        data = r.json()
    except Exception as e:
        return {"error": str(e)}, False

    data["_response_time_ms"] = round((time.time() - start) * 1000, 2)

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=4)

    return data, False

def display(rc, data, cached):
    if "error" in data:
        console.print(Panel(f"[bold red]{data['error']}[/bold red]", title="ERROR"))
        return

    response_time = data.pop("_response_time_ms", "N/A")

    console.print(
        Panel(
            f"[bold green]API Status:[/bold green] OK\n"
            f"[bold cyan]Cached:[/bold cyan] {'YES' if cached else 'NO'}\n"
            f"[bold yellow]Response Time:[/bold yellow] {response_time} ms",
            title="STATUS",
            style="green",
        )
    )

    table = Table(
        title=f"[bold yellow]Vehicle Information — {rc}[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold magenta",
        show_lines=True,
    )

    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value", style="bold white")

    for k, v in data.items():
        if k.lower() == "phone":
            v = mask_phone(v)
        table.add_row(k.replace("_", " ").title(), str(v))

    console.print(table)

    with open(f"results/{rc}.json", "w") as f:
        json.dump(data, f, indent=4)

    console.print(
        Panel(
            Align.center(
                "[bold white]VEHICLE_INFORMATION (AZOD08)\n"
                "[dim]Built for learning • Powered by ethics[/dim]"
            ),
            style="blue",
        )
    )

# ================= MAIN =================

def main():
    ensure_dirs()
    clear()
    banner()

    rc = Prompt.ask(
        "[bold cyan]Enter Vehicle RC Number[/bold cyan]"
    ).strip().upper()

    if not rc:
        console.print("[bold red]RC number is required. Exiting.[/bold red]")
        return

    log(f"Lookup started for RC: {rc}")

    console.print("\n[bold green]Fetching vehicle information...[/bold green]\n")
    time.sleep(0.4)

    data, cached = fetch_data(rc)
    display(rc, data, cached)

    log(f"Lookup finished for RC: {rc}")
    console.print("\n[bold green]Done.[/bold green]")

if __name__ == "__main__":
    main()
