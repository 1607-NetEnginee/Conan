"""
Conan – Modul 1: Phone OSINT
Investigasi informasi publik dari nomor HP.
"""

import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
import json
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from modules.session import session_add

console = Console()


def lookup_numverify(number: str) -> dict:
    """Cek via NumVerify API (gratis tier tersedia)."""
    # Gunakan endpoint publik tanpa API key dulu
    try:
        r = requests.get(
            f"https://phonevalidation.abstractapi.com/v1/",
            params={"api_key": "free", "phone": number},
            timeout=8
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def lookup_truecaller_hint(number: str) -> dict:
    """Cek nama dari beberapa sumber publik."""
    result = {}
    # Cek via Truecaller web (tanpa login, data terbatas)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(
            f"https://search5-noneu.truecaller.com/v2/search",
            params={"q": number, "countryCode": "ID", "type": 4},
            headers=headers, timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("data"):
                d = data["data"][0]
                result["name"] = d.get("name", "")
                result["score"] = d.get("score", 0)
    except Exception:
        pass
    return result


def check_whatsapp_exists(number: str) -> bool:
    """Cek apakah nomor terdaftar di WhatsApp (via wa.me)."""
    try:
        r = requests.get(
            f"https://wa.me/{number}",
            allow_redirects=True, timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        return "send" in r.url or r.status_code == 200
    except Exception:
        return False


def check_telegram_exists(number: str) -> str:
    """Hint keberadaan di Telegram via fragment.com (nomor premium)."""
    # Ini hanya untuk nomor premium, nomor biasa tidak terdaftar publik
    return "Tidak dapat dicek tanpa autentikasi"


def run(number: str):
    console.rule(f"[bold cyan]PHONE OSINT — {number}[/]")

    # Bersihkan input
    number = re.sub(r'[^\d+]', '', number)
    if not number.startswith('+'):
        number = '+' + number

    results = {}

    # ── 1. Parse dengan phonenumbers ──
    console.print("\n[yellow]▶ Parsing nomor...[/]")
    try:
        parsed = phonenumbers.parse(number)
        is_valid   = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)
        region     = geocoder.description_for_number(parsed, "id")
        op         = carrier.name_for_number(parsed, "id")
        zones      = timezone.time_zones_for_number(parsed)
        fmt_intl   = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_e164   = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        results.update({
            "nomor_internasional": fmt_intl,
            "nomor_e164": fmt_e164,
            "valid": is_valid,
            "possible": is_possible,
            "wilayah": region,
            "operator": op,
            "timezone": list(zones),
            "kode_negara": parsed.country_code,
            "nomor_nasional": parsed.national_number,
        })
    except Exception as e:
        console.print(f"[red]Gagal parse: {e}[/]")

    # ── 2. Cek WhatsApp ──
    console.print("[yellow]▶ Cek WhatsApp...[/]")
    clean = number.lstrip('+')
    wa_exists = check_whatsapp_exists(clean)
    results["whatsapp_terdaftar"] = wa_exists

    # ── 3. Cek database Indonesia ──
    console.print("[yellow]▶ Cek sumber publik Indonesia...[/]")
    results["cekrekening_hint"] = f"https://cekrekening.id"
    results["getcontact_hint"]  = f"Cek manual: https://getcontact.com/search/{clean}"

    # ── Tampilkan tabel hasil ──
    table = Table(title="Hasil Phone OSINT", box=box.ROUNDED, border_style="cyan")
    table.add_column("Parameter", style="bold white")
    table.add_column("Nilai", style="green")

    display_map = {
        "nomor_internasional": "Nomor Internasional",
        "valid": "Valid",
        "wilayah": "Wilayah",
        "operator": "Operator",
        "timezone": "Timezone",
        "kode_negara": "Kode Negara",
        "whatsapp_terdaftar": "WhatsApp Terdaftar",
        "getcontact_hint": "GetContact",
    }

    for key, label in display_map.items():
        val = results.get(key, "-")
        if isinstance(val, list): val = ", ".join(str(v) for v in val)
        if isinstance(val, bool): val = "✅ Ya" if val else "❌ Tidak"
        table.add_row(label, str(val))

    console.print(table)

    # ── Simpan ke session ──
    session_add("phone_osint", number, results)
    console.print(f"\n[dim]✅ Data disimpan ke session laporan.[/]\n")
    return results
