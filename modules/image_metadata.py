"""
Conan – Modul 4: Image Metadata
Ekstrak metadata tersembunyi dari gambar (EXIF, GPS, dll).
"""

import os
import json
import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from modules.session import session_add

console = Console()

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import piexif
    PIEXIF_OK = True
except ImportError:
    PIEXIF_OK = False


def get_exif_data(image_path: str) -> dict:
    """Ekstrak semua data EXIF dari gambar."""
    if not PIL_OK:
        return {"error": "Install Pillow: pip3 install Pillow --break-system-packages"}

    result = {}
    try:
        img = Image.open(image_path)
        result["format"]     = img.format
        result["mode"]       = img.mode
        result["ukuran"]     = f"{img.size[0]} x {img.size[1]} pixel"
        result["file_size"]  = f"{os.path.getsize(image_path):,} bytes"

        exif_raw = img._getexif()
        if not exif_raw:
            result["exif"] = "Tidak ada data EXIF"
            return result

        exif_data = {}
        gps_data  = {}

        for tag_id, value in exif_raw.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag] = gps_value
            else:
                # Filter nilai yang bisa dibaca
                if isinstance(value, bytes):
                    try: value = value.decode("utf-8", errors="replace")
                    except: value = repr(value)
                exif_data[str(tag)] = str(value)[:200]

        result["exif"] = exif_data

        # Parse GPS
        if gps_data:
            coords = parse_gps(gps_data)
            if coords:
                result["gps_koordinat"] = coords
                result["google_maps"]   = f"https://maps.google.com/?q={coords['lat']},{coords['lon']}"
                result["osm_maps"]      = f"https://www.openstreetmap.org/?mlat={coords['lat']}&mlon={coords['lon']}"

    except Exception as e:
        result["error"] = str(e)

    return result


def parse_gps(gps_info: dict) -> dict | None:
    """Konversi data GPS EXIF ke koordinat decimal."""
    try:
        def to_degrees(value):
            d, m, s = value
            return float(d) + float(m) / 60 + float(s[0]) / float(s[1]) / 3600 \
                if isinstance(s, tuple) else float(d) + float(m) / 60 + float(s) / 3600

        lat = to_degrees(gps_info.get("GPSLatitude", [0, 0, 0]))
        lon = to_degrees(gps_info.get("GPSLongitude", [0, 0, 0]))

        if gps_info.get("GPSLatitudeRef", "N") == "S":  lat = -lat
        if gps_info.get("GPSLongitudeRef", "E") == "W": lon = -lon

        return {
            "lat": round(lat, 7),
            "lon": round(lon, 7),
            "lat_ref": gps_info.get("GPSLatitudeRef", "N"),
            "lon_ref": gps_info.get("GPSLongitudeRef", "E"),
            "altitude": str(gps_info.get("GPSAltitude", "-")),
            "waktu_gps": str(gps_info.get("GPSTimeStamp", "-")),
        }
    except Exception:
        return None


IMPORTANT_TAGS = [
    "Make", "Model", "Software", "DateTime", "DateTimeOriginal",
    "DateTimeDigitized", "Artist", "Copyright", "ImageDescription",
    "UserComment", "XPComment", "XPAuthor",
]


def run(image_path: str):
    image_path = image_path.strip().strip("'\"")

    if not Path(image_path).exists():
        console.print(f"[red]File tidak ditemukan: {image_path}[/]")
        return

    console.rule(f"[bold cyan]IMAGE METADATA — {Path(image_path).name}[/]")
    console.print("\n[yellow]▶ Mengekstrak metadata...[/]")

    data = get_exif_data(image_path)

    # ── Info dasar ──
    basic = Table(title="Info Dasar", box=box.ROUNDED, border_style="cyan")
    basic.add_column("Parameter", style="bold white")
    basic.add_column("Nilai", style="green")
    basic.add_row("File",      Path(image_path).name)
    basic.add_row("Format",    data.get("format", "-"))
    basic.add_row("Ukuran",    data.get("ukuran", "-"))
    basic.add_row("File Size", data.get("file_size", "-"))
    console.print(basic)

    # ── GPS ──
    if data.get("gps_koordinat"):
        gps = data["gps_koordinat"]
        console.print(Panel(
            f"[bold green]📍 KOORDINAT GPS DITEMUKAN![/]\n\n"
            f"Latitude  : [bold]{gps['lat']}[/]\n"
            f"Longitude : [bold]{gps['lon']}[/]\n"
            f"Altitude  : {gps['altitude']}\n\n"
            f"[bold yellow]Google Maps:[/] {data['google_maps']}\n"
            f"[bold yellow]OpenStreetMap:[/] {data['osm_maps']}",
            title="🗺️  Lokasi GPS", border_style="bold green"
        ))
    else:
        console.print(Panel(
            "[yellow]Tidak ada data GPS dalam gambar ini.[/]\n"
            "GPS biasanya ada pada foto langsung dari kamera HP.\n"
            "Foto yang di-screenshot atau diedit biasanya GPS-nya dihapus.",
            title="GPS", border_style="yellow"
        ))

    # ── EXIF penting ──
    exif = data.get("exif", {})
    if isinstance(exif, dict) and exif:
        table = Table(title="EXIF Data Penting", box=box.ROUNDED, border_style="cyan")
        table.add_column("Tag", style="bold white")
        table.add_column("Nilai", style="green")

        # Tampilkan tag penting dulu
        for tag in IMPORTANT_TAGS:
            if tag in exif:
                table.add_row(tag, str(exif[tag]))

        # Tampilkan sisa tag
        for tag, val in exif.items():
            if tag not in IMPORTANT_TAGS:
                table.add_row(f"[dim]{tag}[/]", f"[dim]{str(val)[:100]}[/]")

        console.print(table)

    session_add("image_metadata", Path(image_path).name, data)
    console.print("[dim]✅ Data disimpan ke session laporan.[/]\n")
    return data
