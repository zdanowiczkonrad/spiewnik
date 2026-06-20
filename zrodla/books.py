# -*- coding: utf-8 -*-
"""Definicje „kolekcji" śpiewników (typy śpiewnika budowane z bazy).

Dwa rodzaje kolekcji:
- **folderowe** (`src`): katalog `Baza_piesni/<nazwa>/` z plikami `.md` (religijne, polskie, zagraniczne),
- **listowe** (`list` + `from`): plik `.md` z samymi TYTUŁAMI pieśni (np. `18-nadia.md`) — składanka
  zbierana po tytule z innych kolekcji (bez kopiowania treści; źródłem prawdy są pliki w `from`).

Każda kolekcja publikuje się pod `docs/<slug>/` (religijne pod rootem, `slug=""`), a w stopce strony
dostaje linki do pozostałych śpiewników. Dodanie nowego śpiewnika = jeden wpis w BOOKS — generatory
`pdf_full.py` i `site.py` biorą resztę z `load_book()`."""
import os, re, glob
from common import DB, ROOT, parse_md
from plan_data import EVENT

DOCS = os.path.join(ROOT, "docs")
NOTE = "NOTACJA POLSKA (h = H-moll, małe litery = molowe)"
CREDIT = "Zebranie i opracowanie: Konrad Zdanowicz 2026"

BOOKS = {
    # ── śpiewnik religijny (pełna baza) — root /spiewnik/, nazwy plików jak dotąd ──
    "religijne": {
        "src":           os.path.join(DB, "religijne"),
        "recursive":     False,
        "slug":          "",                                   # publikacja w korzeniu docs/
        "nav_label":     "Religijne",
        "header":        EVENT["header"],
        "cover_title":   "Śpiewnik",
        "kicker_chords": "ŚPIEWNIK RELIGIJNY NA GITARĘ",
        "kicker_plain":  "ŚPIEWNIK RELIGIJNY — TEKSTY",
        "subtitle":      EVENT["short"],
        "credit":        "Źródła różne, zebranie i opracowanie: Konrad Zdanowicz 2026",
        "notation_note": NOTE,
        "base_chords":   "Śpiewnik pełny – chwyty",
        "base_plain":    "Śpiewnik pełny – teksty",
        "pdf_dir":       ROOT,
        "qr":            True,
        "chord_index":   True,
        "site_title":    "Śpiewnik",
    },
    # ── pieśni polskie (świeckie) ──
    "polskie": {
        "src":           os.path.join(DB, "polskie"),
        "recursive":     False,
        "slug":          "polskie",
        "nav_label":     "Polskie",
        "header":        "PIEŚNI POLSKIE",
        "cover_title":   "Polskie",
        "kicker_chords": "ŚPIEWNIK · PIEŚNI POLSKIE — CHWYTY",
        "kicker_plain":  "ŚPIEWNIK · PIEŚNI POLSKIE — TEKSTY",
        "subtitle":      "Pieśni polskie",
        "credit":        CREDIT,
        "notation_note": NOTE,
        "base_chords":   "Śpiewnik polskie – chwyty",
        "base_plain":    "Śpiewnik polskie – teksty",
        "pdf_dir":       os.path.join(ROOT, "polskie"),
        "qr":            False,
        "chord_index":   False,
        "site_title":    "Pieśni polskie",
    },
    # ── pieśni zagraniczne ──
    "zagraniczne": {
        "src":           os.path.join(DB, "zagraniczne"),
        "recursive":     False,
        "slug":          "zagraniczne",
        "nav_label":     "Zagraniczne",
        "header":        "PIEŚNI ZAGRANICZNE",
        "cover_title":   "Zagraniczne",
        "kicker_chords": "ŚPIEWNIK · PIEŚNI ZAGRANICZNE — CHWYTY",
        "kicker_plain":  "ŚPIEWNIK · PIEŚNI ZAGRANICZNE — TEKSTY",
        "subtitle":      "Pieśni zagraniczne",
        "credit":        CREDIT,
        "notation_note": NOTE,
        "base_chords":   "Śpiewnik zagraniczne – chwyty",
        "base_plain":    "Śpiewnik zagraniczne – teksty",
        "pdf_dir":       os.path.join(ROOT, "zagraniczne"),
        "qr":            False,
        "chord_index":   False,
        "site_title":    "Pieśni zagraniczne",
    },
    # ── 18. urodziny Nadii — składanka po TYTUŁACH z polskie + zagraniczne ──
    "18-nadia": {
        "list":          os.path.join(DB, "18-nadia.md"),
        "from":          [os.path.join(DB, "polskie"), os.path.join(DB, "zagraniczne")],
        "slug":          "18-nadii",
        "nav_label":     "18 Nadii",
        "header":        "OSIEMNASTKA NADII",
        "cover_title":   "Nadia",
        "kicker_chords": "ŚPIEWNIK NA OSIEMNASTKĘ — CHWYTY",
        "kicker_plain":  "ŚPIEWNIK NA OSIEMNASTKĘ — TEKSTY",
        "subtitle":      "Osiemnastka Nadii · 2026",
        "credit":        CREDIT,
        "notation_note": NOTE,
        "base_chords":   "Śpiewnik Nadia – chwyty",
        "base_plain":    "Śpiewnik Nadia – teksty",
        "pdf_dir":       os.path.join(ROOT, "18-nadii"),
        "qr":            False,
        "chord_index":   False,
        "site_title":    "Śpiewnik Nadii",
    },
}

DEFAULT_BOOK = "religijne"


def get_book(name=DEFAULT_BOOK):
    if name not in BOOKS:
        raise SystemExit("Nieznana kolekcja: %r (dostępne: %s)" % (name, ", ".join(BOOKS)))
    return BOOKS[name]


def site_dir(book):
    """Katalog publikacji w docs/ (root dla slug=='')."""
    return DOCS if not book["slug"] else os.path.join(DOCS, book["slug"])


def rel_url(from_slug, to_slug):
    """Względny URL między dwoma kolekcjami (po slugach), zakończony „/"."""
    a = DOCS if not from_slug else os.path.join(DOCS, from_slug)
    b = DOCS if not to_slug else os.path.join(DOCS, to_slug)
    r = os.path.relpath(b, a)
    return "./" if r == "." else r.rstrip("/") + "/"


def _folder_songs(src, recursive=False):
    pat = os.path.join(src, "**", "*.md") if recursive else os.path.join(src, "*.md")
    return [parse_md(p) for p in sorted(glob.glob(pat, recursive=recursive))
            if not os.path.basename(p).startswith("_")]


def _list_titles(list_path):
    """Tytuły z pliku-listy: wiersze zaczynające się od „- " / „* "."""
    titles = []
    for ln in open(list_path, encoding="utf-8"):
        m = re.match(r"^\s*[-*]\s+(.+?)\s*$", ln)
        if m:
            titles.append(m.group(1).strip())
    return titles


def load_book(book):
    """Pieśni kolekcji (lista dictów z parse_md). Zwraca (songs, missing).
    `missing` = tytuły z listy nieobecne w kolekcjach `from` (dla składanek)."""
    if "list" in book:
        by = {}
        for d in book["from"]:
            for s in _folder_songs(d):
                by[s["title"]] = s
        songs, missing = [], []
        for t in _list_titles(book["list"]):
            (songs.append(by[t]) if t in by else missing.append(t))
        return songs, missing
    return _folder_songs(book["src"], book.get("recursive", False)), []
