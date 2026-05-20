"""
Conan – Modul 2: Social Media OSINT
Cek keberadaan username di berbagai platform.
"""

import requests
import concurrent.futures
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import box
from modules.session import session_add

console = Console()

# Platform yang dicek — semua endpoint publik
PLATFORMS = {
    "Instagram":    "https://www.instagram.com/{}/",
    "Twitter/X":    "https://twitter.com/{}",
    "Facebook":     "https://www.facebook.com/{}",
    "TikTok":       "https://www.tiktok.com/@{}",
    "YouTube":      "https://www.youtube.com/@{}",
    "GitHub":       "https://github.com/{}",
    "LinkedIn":     "https://www.linkedin.com/in/{}",
    "Pinterest":    "https://www.pinterest.com/{}/",
    "Reddit":       "https://www.reddit.com/user/{}",
    "Telegram":     "https://t.me/{}",
    "Shopee":       "https://shopee.co.id/{}",
    "Tokopedia":    "https://www.tokopedia.com/{}",
    "Kaskus":       "https://www.kaskus.co.id/user/{}",
    "Medium":       "https://medium.com/@{}",
    "Linktree":     "https://linktr.ee/{}",
    "Spotify":      "https://open.spotify.com/user/{}",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

NOT_FOUND_INDICATORS = [
    "Page Not Found", "404", "doesn't exist",
    "page isn't available", "user not found",
    "This account doesn't exist", "pengguna tidak ditemukan",
    "Halaman tidak ditemukan",
]


def check_platform(platform: str, url_template: str, username: str) -> dict:
    url = url_template.format(username)
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code == 404:
            return {"platform": platform, "url": url, "status": "❌ Tidak ada", "code": 404}
        if r.status_code == 200:
            body = r.text.lower()
            for indicator in NOT_FOUND_INDICATORS:
                if indicator.lower() in body:
                    return {"platform": platform, "url": url, "status": "❌ Tidak ada", "code": 200}
            return {"platform": platform, "url": url, "status": "✅ Ditemukan", "code": 200}
        return {"platform": platform, "url": url, "status": f"⚠️  HTTP {r.status_code}", "code": r.status_code}
    except requests.Timeout:
        return {"platform": platform, "url": url, "status": "⏱️  Timeout", "code": 0}
    except Exception as e:
        return {"platform": platform, "url": url, "status": f"⚠️  Error", "code": -1}


def run(username: str):
    console.rule(f"[bold cyan]SOCIAL MEDIA OSINT — @{username}[/]")
    console.print(f"\n[yellow]Mencari username [bold]{username}[/] di {len(PLATFORMS)} platform...[/]\n")

    results = []
    found = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(check_platform, name, url, username): name
            for name, url in PLATFORMS.items()
        }
        for future in track(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            description="Scanning...",
            console=console
        ):
            result = future.result()
            results.append(result)
            if "Ditemukan" in result["status"]:
                found.append(result)

    # Tampilkan tabel
    table = Table(
        title=f"Hasil Social Media OSINT — @{username}",
        box=box.ROUNDED, border_style="cyan"
    )
    table.add_column("Platform", style="bold white", width=16)
    table.add_column("Status", width=18)
    table.add_column("URL", style="dim")

    # Urutkan: ditemukan dulu
    results.sort(key=lambda x: (0 if "Ditemukan" in x["status"] else 1))

    for r in results:
        color = "green" if "Ditemukan" in r["status"] else "red"
        table.add_row(r["platform"], f"[{color}]{r['status']}[/]", r["url"])

    console.print(table)
    console.print(f"\n[bold green]Ditemukan di {len(found)} platform.[/]")

    # Simpan ke session
    session_add("social_osint", username, {
        "username": username,
        "total_platform": len(PLATFORMS),
        "ditemukan": len(found),
        "hasil": results,
    })

    console.print("[dim]✅ Data disimpan ke session laporan.[/]\n")
    return results
