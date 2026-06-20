# -*- coding: utf-8 -*-
"""Definicje „kolekcji" śpiewników (typy śpiewnika budowane z bazy).

Każda kolekcja to katalog w `Baza_piesni/` (płaski albo z podkatalogami) plus opis
okładki/plików wyjściowych/miejsca publikacji. Generatory `pdf_full.py` i `site.py`
biorą konfigurację stąd, więc dodanie nowego śpiewnika = jeden wpis w BOOKS (bez
duplikowania logiki układu). Kolekcja religijna jest domyślna i zachowuje dotychczasowe
nazwy plików, żeby nic w pipelinie nie pękło."""
import os
from common import DB, ROOT
from plan_data import EVENT

DOCS = os.path.join(ROOT, "docs")

BOOKS = {
    # ── śpiewnik religijny (pełna baza) — domyślny, nazwy plików jak dotąd ──
    "religijne": {
        "src":           os.path.join(DB, "religijne"),
        "recursive":     False,
        "header":        EVENT["header"],                       # prawy róg żywej paginy
        "cover_title":   "Śpiewnik",                            # duży tytuł na okładce
        "kicker_chords": "ŚPIEWNIK RELIGIJNY NA GITARĘ",        # nadtytuł (wersja z chwytami)
        "kicker_plain":  "ŚPIEWNIK RELIGIJNY — TEKSTY",         # nadtytuł (wersja bez chwytów)
        "subtitle":      EVENT["short"],                        # podtytuł pod kreską
        "credit":        "Źródła różne, zebranie i opracowanie: Konrad Zdanowicz 2026",
        "notation_note": "NOTACJA POLSKA (h = H-moll, małe litery = molowe)",
        "base_chords":   "Śpiewnik pełny – chwyty",             # nazwa pliku PDF (z chwytami)
        "base_plain":    "Śpiewnik pełny – teksty",             # nazwa pliku PDF (bez chwytów)
        "pdf_dir":       ROOT,                                  # gdzie zapisać PDF-y
        "site_dir":      DOCS,                                  # katalog publikacji (GitHub Pages)
        "qr":            True,                                  # QR do żywej strony na okładce
        "chord_index":   True,                                  # załącznik „Indeks akordów"
        "site_title":    "Śpiewnik",
    },
    # ── śpiewnik na 18. urodziny Nadii (kolekcja świecka, podział polskie/zagraniczne) ──
    "18-nadia": {
        "src":           os.path.join(DB, "18-nadia"),
        "recursive":     True,
        "header":        "OSIEMNASTKA NADII",
        "cover_title":   "Nadia",
        "kicker_chords": "ŚPIEWNIK NA OSIEMNASTKĘ — CHWYTY",
        "kicker_plain":  "ŚPIEWNIK NA OSIEMNASTKĘ — TEKSTY",
        "subtitle":      "Osiemnastka Nadii · 2026",
        "credit":        "Zebranie i opracowanie: Konrad Zdanowicz 2026",
        "notation_note": "NOTACJA POLSKA (h = H-moll, małe litery = molowe)",
        "base_chords":   "Śpiewnik Nadia – chwyty",
        "base_plain":    "Śpiewnik Nadia – teksty",
        "pdf_dir":       os.path.join(ROOT, "18-nadia"),
        "site_dir":      os.path.join(DOCS, "18-nadia"),
        "qr":            False,
        "chord_index":   False,   # 4 piosenki pop — generyczny indeks akordów (i strony notatek) zbędny
        "site_title":    "Śpiewnik Nadii",
    },
}

DEFAULT_BOOK = "religijne"


def get_book(name=DEFAULT_BOOK):
    if name not in BOOKS:
        raise SystemExit("Nieznana kolekcja: %r (dostępne: %s)" % (name, ", ".join(BOOKS)))
    return BOOKS[name]
