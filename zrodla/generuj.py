# -*- coding: utf-8 -*-
import os, glob
from common import norm
from books import BOOKS   # kolekcje (katalogi w Baza_piesni) z konfiguracją źródeł

# Baza_piesni/*.md jest JEDYNYM źródłem prawdy. Pieśni dodaje się i poprawia WPROST w plikach .md.
# Ten skrypt nie tworzy ani nie nadpisuje treści — tylko odświeża indeks każdej kolekcji (_INDEKS.md)
# na podstawie skanu plików. Po edycji bazy: ten skrypt, a potem pdf_full.py / pdf.py.

def read_title(p):
    for ln in open(p, encoding="utf-8"):
        if ln.startswith("# "): return ln[2:].strip()
    return os.path.basename(p)

def is_stub_file(p):
    return "⚠️" in open(p, encoding="utf-8").read()

def reindex(name, book):
    src, rec = book["src"], book["recursive"]
    pat = os.path.join(src, "**", "*.md") if rec else os.path.join(src, "*.md")
    files = sorted([p for p in glob.glob(pat, recursive=rec) if not os.path.basename(p).startswith("_")],
                   key=lambda p: norm(read_title(p)))
    rows = []; nstub = 0
    for p in files:
        t = read_title(p); st = is_stub_file(p); nstub += st
        link = os.path.relpath(p, src)   # względny link (działa też dla podkatalogów polskie/zagraniczne)
        rows.append(f"| {t}{' ⚠️' if st else ''} | [{link}]({link}) |")
    idx = [f"# Kolekcja „{name}” — indeks", "",
           f"Łącznie pieśni: **{len(files)}**  ·  z chwytami: **{len(files)-nstub}**  ·  do uzupełnienia: **{nstub}**.", "",
           "> `Baza_piesni/` to źródło prawdy. Edytuj pliki wprost; potem `python3 zrodla/pdf_full.py` i `python3 zrodla/site.py`.", "",
           "| Pieśń | Plik |", "|---|---|", *rows]
    open(os.path.join(src, "_INDEKS.md"), "w", encoding="utf-8").write("\n".join(idx) + "\n")
    print(f"INDEKS [{name}]: {len(files)} pieśni, stubów: {nstub}")

for name, book in BOOKS.items():
    reindex(name, book)
