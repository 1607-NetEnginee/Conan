"""
Conan – Modul 6: Report Generator
Buat laporan forensik dari semua data sesi investigasi.
"""

import json
import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from modules.session import session_get, session_clear

console = Console()

REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def generate_txt(session: dict, filepath: Path):
    """Generate laporan dalam format teks."""
    lines = []
    lines.append("=" * 65)
    lines.append("          LAPORAN INVESTIGASI DIGITAL")
    lines.append("          Conan – Cyberoutcast OSINT Toolkit")
    lines.append("=" * 65)
    lines.append(f"Tanggal Laporan  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Investigator     : {session.get('investigator', 'Cyberoutcast')}")
    lines.append(f"Sesi Dimulai     : {session.get('dibuat', '-')}")
    lines.append(f"Total Modul Dijalankan: {len(session.get('data', []))}")
    lines.append("=" * 65)
    lines.append("")

    for i, entry in enumerate(session.get("data", []), 1):
        lines.append(f"[{i}] MODUL  : {entry['modul'].upper().replace('_', ' ')}")
        lines.append(f"    TARGET : {entry['target']}")
        lines.append(f"    WAKTU  : {entry['waktu']}")
        lines.append("    HASIL  :")

        hasil = entry.get("hasil", {})
        _flatten_dict(hasil, lines, indent=6)
        lines.append("")
        lines.append("-" * 65)
        lines.append("")

    lines.append("=" * 65)
    lines.append("CATATAN HUKUM:")
    lines.append("Laporan ini dibuat berdasarkan data publik yang tersedia")
    lines.append("secara legal. Digunakan untuk keperluan investigasi sosial")
    lines.append("dan akan diserahkan kepada pihak berwenang.")
    lines.append("=" * 65)

    filepath.write_text("\n".join(lines), encoding="utf-8")


def generate_json(session: dict, filepath: Path):
    """Generate laporan dalam format JSON."""
    report = {
        "judul": "Laporan Investigasi Digital",
        "toolkit": "Conan – Cyberoutcast OSINT Toolkit v1.0",
        "tanggal": datetime.datetime.now().isoformat(),
        "investigator": session.get("investigator", "Cyberoutcast"),
        "sesi": session,
    }
    filepath.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def _flatten_dict(data, lines: list, indent: int = 0):
    """Ratakan dict/list untuk ditampilkan di teks."""
    prefix = " " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                _flatten_dict(v, lines, indent + 4)
            else:
                lines.append(f"{prefix}{k}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _flatten_dict(item, lines, indent)
                lines.append("")
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{data}")


def run():
    console.rule("[bold cyan]REPORT GENERATOR[/]")

    session = session_get()
    entries = session.get("data", [])

    if not entries:
        console.print(
            "[yellow]Belum ada data investigasi dalam sesi ini.\n"
            "Jalankan modul lain terlebih dahulu.[/]"
        )
        return

    console.print(f"\n[green]Ditemukan {len(entries)} hasil investigasi dalam sesi ini.[/]")

    # Nama file
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_file  = REPORTS_DIR / f"conan_laporan_{ts}.txt"
    json_file = REPORTS_DIR / f"conan_laporan_{ts}.json"

    generate_txt(session, txt_file)
    generate_json(session, json_file)

    console.print(Panel(
        f"[bold green]✅ Laporan berhasil dibuat![/]\n\n"
        f"📄 Teks  : {txt_file}\n"
        f"📊 JSON  : {json_file}\n\n"
        f"[dim]Laporan siap diserahkan ke pihak berwenang.[/]",
        title="Laporan Selesai", border_style="green"
    ))

    # Tanya apakah mau clear sesi
    clear = console.input("\n  Reset sesi investigasi? (y/N): ").strip().lower()
    if clear == "y":
        session_clear()
        console.print("[dim]Sesi direset.[/]")

    return str(txt_file)
