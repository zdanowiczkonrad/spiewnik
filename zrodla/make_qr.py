# -*- coding: utf-8 -*-
"""Regeneracja statycznego kodu QR prowadzącego do strony śpiewnika (SITE_URL).

Narzędzie DEWELOPERSKIE, uruchamiane raz (gdy zmieni się adres) — NIE jest częścią
runtime'u ani CI. Korzysta wyłącznie z biblioteki standardowej (urllib): pobiera PNG
z publicznego API QR i zapisuje do zrodla/assets/. Generatory PDF tylko osadzają
gotowy plik (bez żadnej nowej zależności). Po regeneracji: zacommituj nowy PNG."""
import os, urllib.parse, urllib.request
from common import SITE_URL, QR_PATH, ASSETS

API = "https://api.qrserver.com/v1/create-qr-code/"

def main():
    os.makedirs(ASSETS, exist_ok=True)
    q = urllib.parse.urlencode({"size": "640x640", "margin": "0", "ecc": "M", "data": SITE_URL})
    with urllib.request.urlopen(API + "?" + q, timeout=20) as r:
        data = r.read()
    if not data.startswith(b"\x89PNG"):
        raise SystemExit("API nie zwróciło PNG — przerwano (nie nadpisuję assetu).")
    with open(QR_PATH, "wb") as f:
        f.write(data)
    print(f"OK: {QR_PATH} ({len(data)} B) → {SITE_URL}")

if __name__ == "__main__":
    main()
