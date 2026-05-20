"""
Conan – Modul 3: WhatsApp Info
Ambil informasi publik profil WhatsApp target.
"""

import requests
import re
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from modules.session import session_add

console = Console()


def check_wa_profile(number: str) -> dict:
    """
    Cek informasi publik WhatsApp via wa.me
    Hanya mengakses data yang memang publik.
    """
    result = {
        "nomor": number,
        "wa_me_url": f"https://wa.me/{number}",
        "terdaftar": False,
        "nama": "-",
        "about": "-",
        "foto_profil": "-",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "Chrome/124.0 Safari/537.36"
        )
    }

    # Cek via wa.me
    try:
        r = requests.get(
            f"https://wa.me/{number}",
            headers=headers, timeout=10, allow_redirects=True
        )
        if r.status_code == 200:
            result["terdaftar"] = True
            # Cari nama dari meta tag jika ada
            name_match = re.search(r'<meta[^>]+og:title[^>]+content="([^"]+)"', r.text)
            if name_match:
                result["nama"] = name_match.group(1)
    except Exception as e:
        result["error"] = str(e)

    # Hint link profil
    result["link_profil"]   = f"https://wa.me/{number}"
    result["chat_langsung"] = f"https://api.whatsapp.com/send?phone={number}"

    return result


def format_number_id(number: str) -> str:
    """Pastikan format nomor benar untuk Indonesia."""
    number = re.sub(r'[^\d]', '', number)
    if number.startswith('0'):
        number = '62' + number[1:]
    if not number.startswith('62'):
        number = '62' + number
    return number


def run(number: str):
    number = format_number_id(number)
    console.rule(f"[bold cyan]WHATSAPP INFO — {number}[/]")
    console.print("\n[yellow]▶ Mengambil informasi WhatsApp...[/]")

    result = check_wa_profile(number)

    table = Table(title="Hasil WhatsApp Info", box=box.ROUNDED, border_style="cyan")
    table.add_column("Parameter", style="bold white")
    table.add_column("Nilai", style="green")

    table.add_row("Nomor", number)
    table.add_row("Terdaftar di WA", "✅ Ya" if result["terdaftar"] else "❌ Tidak terdeteksi")
    table.add_row("Nama Profil", result.get("nama", "-"))
    table.add_row("Link wa.me", result.get("wa_me_url", "-"))
    table.add_row("Link Chat", result.get("chat_langsung", "-"))

    console.print(table)

    console.print(Panel(
        "[yellow]Catatan:[/]\n"
        "WhatsApp tidak mengekspos foto profil/status ke publik tanpa koneksi akun.\n"
        "Untuk info lebih lengkap, simpan nomor ini di HP → buka WhatsApp → lihat profil.\n"
        "Atau gunakan GetContact: [link]https://getcontact.com[/link]",
        title="Info", border_style="yellow"
    ))

    session_add("whatsapp_info", number, result)
    console.print("[dim]✅ Data disimpan ke session laporan.[/]\n")
    return result
