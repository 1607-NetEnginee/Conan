"""
Conan – Session Manager
Menyimpan semua hasil investigasi dalam satu sesi untuk laporan.
"""

import json
import datetime
from pathlib import Path

SESSION_FILE = Path.home() / "conan_session.json"


def _load() -> dict:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text())
        except Exception:
            pass
    return {
        "dibuat": datetime.datetime.now().isoformat(),
        "investigator": "Cyberoutcast",
        "data": []
    }


def _save(session: dict):
    SESSION_FILE.write_text(json.dumps(session, ensure_ascii=False, indent=2))


def session_add(modul: str, target: str, data: dict):
    session = _load()
    session["data"].append({
        "modul": modul,
        "target": target,
        "waktu": datetime.datetime.now().isoformat(),
        "hasil": data,
    })
    session["terakhir_diperbarui"] = datetime.datetime.now().isoformat()
    _save(session)


def session_get() -> dict:
    return _load()


def session_clear():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
