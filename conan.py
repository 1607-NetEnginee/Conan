#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════╗
║           CONAN – Cyberoutcast OSINT Toolkit          ║
║         Investigasi Digital untuk Keadilan            ║
╚═══════════════════════════════════════════════════════╝

Penggunaan:
    python3 conan.py                        # Menu interaktif
    python3 conan.py --phone 6281234567890  # Phone OSINT
    python3 conan.py --social username      # Social Media OSINT
    python3 conan.py --image foto.jpg       # Metadata gambar
    python3 conan.py --rekening 1234567890  # Cek rekening
    python3 conan.py --report               # Buat laporan

Catatan untuk pengembangan lanjutan:
    #CyberoutcastToolkit | Tool: Conan
    Kirim pesan ini di chat baru untuk melanjutkan pengembangan.
"""

import argparse
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

BANNER = """
[bold cyan]╔═══════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold red]  ██████╗ ██████╗ ███╗   ██╗ █████╗ ███╗   ██╗ [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold red] ██╔════╝██╔═══██╗████╗  ██║██╔══██╗████╗  ██║ [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold red] ██║     ██║   ██║██╔██╗ ██║███████║██╔██╗ ██║ [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold white] ██║     ██║   ██║██║╚██╗██║██╔══██║██║╚██╗██║ [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold white] ╚██████╗╚██████╔╝██║ ╚████║██║  ██║██║ ╚████║ [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold white]  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ [/]  [bold cyan]║[/]
[bold cyan]║[/]          [bold yellow]Cyberoutcast OSINT Toolkit v1.0[/]          [bold cyan]║[/]
[bold cyan]║[/]       [bold]Investigasi Digital · Keadilan Sosial[/]       [bold cyan]║[/]
[bold cyan]╚═══════════════════════════════════════════════════╝[/]
"""

MENU = """
[bold white][ MENU UTAMA ][/]

  [bold cyan][1][/]  Phone OSINT          — Investigasi nomor HP
  [bold cyan][2][/]  Social Media OSINT   — Lacak akun media sosial
  [bold cyan][3][/]  WhatsApp Info        — Info profil WhatsApp
  [bold cyan][4][/]  Image Metadata       — Ekstrak data tersembunyi foto
  [bold cyan][5][/]  Rekening OSINT       — Cek rekening penipuan
  [bold cyan][6][/]  Buat Laporan         — Generate laporan forensik
  [bold cyan][0][/]  Keluar

"""

def main_menu():
    from modules.phone_osint    import run as phone_run
    from modules.social_osint   import run as social_run
    from modules.whatsapp_info  import run as wa_run
    from modules.image_metadata import run as img_run
    from modules.rekening_osint import run as rek_run
    from modules.report_gen     import run as report_run

    console.print(BANNER)

    while True:
        console.print(MENU)
        choice = console.input("[bold green]conan>[/] ").strip()

        if choice == "1":
            number = console.input("  Masukkan nomor HP (contoh: 6281234567890): ").strip()
            phone_run(number)
        elif choice == "2":
            username = console.input("  Masukkan username target: ").strip()
            social_run(username)
        elif choice == "3":
            number = console.input("  Masukkan nomor WA (contoh: 6281234567890): ").strip()
            wa_run(number)
        elif choice == "4":
            path = console.input("  Path file gambar: ").strip()
            img_run(path)
        elif choice == "5":
            rek = console.input("  Masukkan nomor rekening: ").strip()
            bank = console.input("  Nama bank (contoh: BCA, BRI, Mandiri): ").strip()
            rek_run(rek, bank)
        elif choice == "6":
            report_run()
        elif choice == "0":
            console.print("\n[bold cyan]Sampai jumpa. — Conan by Cyberoutcast[/]\n")
            sys.exit(0)
        else:
            console.print("[red]Pilihan tidak valid.[/]")


def main():
    ap = argparse.ArgumentParser(description="Conan – Cyberoutcast OSINT Toolkit")
    ap.add_argument("--phone",    metavar="NOMOR",    help="Phone OSINT")
    ap.add_argument("--social",   metavar="USERNAME", help="Social Media OSINT")
    ap.add_argument("--wa",       metavar="NOMOR",    help="WhatsApp Info")
    ap.add_argument("--image",    metavar="FILE",     help="Image Metadata")
    ap.add_argument("--rekening", metavar="REKENING", help="Cek rekening")
    ap.add_argument("--report",   action="store_true",help="Buat laporan")
    args = ap.parse_args()

    if args.phone:
        from modules.phone_osint import run; run(args.phone)
    elif args.social:
        from modules.social_osint import run; run(args.social)
    elif args.wa:
        from modules.whatsapp_info import run; run(args.wa)
    elif args.image:
        from modules.image_metadata import run; run(args.image)
    elif args.rekening:
        from modules.rekening_osint import run; run(args.rekening, "")
    elif args.report:
        from modules.report_gen import run; run()
    else:
        main_menu()


if __name__ == "__main__":
    main()
