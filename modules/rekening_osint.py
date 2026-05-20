"""
Conan – Modul 5: Rekening OSINT
Cek nomor rekening di database penipuan publik Indonesia.
"""

import requests
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from modules.session import session_add

console = Console()

BANK_CODES = {
    "BCA": "014", "BNI": "009", "BRI": "002", "MANDIRI": "008",
    "BSI": "451", "CIMB": "022", "DANAMON": "011", "PERMATA": "013",
    "BTN": "200", "OCBC": "028", "MEGA": "426", "PANIN": "019",
    "MAYBANK": "016", "HSBC": "041", "CITIBANK": "031",
    "GOPAY": "gopay", "OVO": "ovo", "DANA": "dana",
    "SHOPEEPAY": "shopeepay", "LINKAJA": "linkaja",
}


def check_cekrekening(account: str, bank: str) -> dict:
    """
    Cek via cekrekening.id — database resmi pemerintah Indonesia
    untuk pelaporan rekening penipuan.
    """
    result = {
        "sumber": "cekrekening.id",
        "url_manual": f"https://cekrekening.id/home",
        "nomor": account,
        "bank": bank.upper(),
        "status": "Perlu dicek manual",
        "instruksi": "Buka cekrekening.id, masukkan nomor rekening dan nama bank"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Coba akses API publik cekrekening.id
    try:
        bank_code = BANK_CODES.get(bank.upper(), "")
        r = requests.post(
            "https://cekrekening.id/api/report/check",
            json={"accountNumber": account, "bankCode": bank_code},
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            result["raw_response"] = data
            if data.get("data"):
                d = data["data"]
                result["status"]       = d.get("status", "-")
                result["jumlah_laporan"] = d.get("totalReport", 0)
                result["nama_pemilik"] = d.get("accountName", "-")
    except Exception as e:
        result["api_error"] = str(e)

    return result


def check_kredibel(account: str, bank: str) -> dict:
    """Cek via kredibel.co.id."""
    return {
        "sumber": "kredibel.co.id",
        "url_manual": f"https://www.kredibel.co.id/scammer?q={account}",
        "instruksi": f"Buka URL di atas untuk cek laporan penipuan"
    }


def check_tipidsiber(account: str) -> dict:
    """Referensi ke Lapor Siber Polri."""
    return {
        "sumber": "Siber Polri",
        "url_lapor": "https://patrolisiber.id",
        "url_lapor2": "https://lapor.go.id",
        "instruksi": "Untuk laporan resmi ke Polri"
    }


def run(account: str, bank: str):
    account = re.sub(r'[^\d]', '', account)

    if not bank:
        console.print("\n[yellow]Nama bank tidak diisi.[/]")
        bank = console.input("  Bank (contoh: BCA, BRI, Mandiri, DANA, GOPAY): ").strip()

    console.rule(f"[bold cyan]REKENING OSINT — {account} ({bank.upper()})[/]")
    console.print("\n[yellow]▶ Mengecek database penipuan...[/]")

    all_results = {}

    # Cek semua sumber
    r1 = check_cekrekening(account, bank)
    r2 = check_kredibel(account, bank)
    r3 = check_tipidsiber(account)

    all_results.update({"cekrekening": r1, "kredibel": r2, "siber_polri": r3})

    # Tabel cekrekening.id
    table = Table(title="Hasil Cek Rekening", box=box.ROUNDED, border_style="cyan")
    table.add_column("Parameter", style="bold white")
    table.add_column("Nilai", style="green")

    table.add_row("Nomor Rekening", account)
    table.add_row("Bank", bank.upper())
    table.add_row("Status", r1.get("status", "-"))
    table.add_row("Jumlah Laporan", str(r1.get("jumlah_laporan", "-")))
    table.add_row("Nama Pemilik", r1.get("nama_pemilik", "Tidak tersedia"))
    table.add_row("Cek Manual", r1["url_manual"])

    console.print(table)

    # Link pengecekan manual
    console.print(Panel(
        f"[bold yellow]Link Pengecekan Manual:[/]\n\n"
        f"1. cekrekening.id    : {r1['url_manual']}\n"
        f"2. Kredibel          : {r2['url_manual']}\n"
        f"3. Lapor Siber Polri : {r3['url_lapor']}\n\n"
        f"[dim]Buka link di atas untuk verifikasi manual jika API tidak merespons.[/]",
        title="Referensi", border_style="yellow"
    ))

    session_add("rekening_osint", account, all_results)
    console.print("[dim]✅ Data disimpan ke session laporan.[/]\n")
    return all_results
