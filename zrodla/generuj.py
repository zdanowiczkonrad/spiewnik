# -*- coding: utf-8 -*-
import os, glob
from common import DB, norm   # DB = ścieżka do Baza_piesni (wyliczona z __file__), bez ścieżek absolutnych

# Baza_piesni/*.md jest JEDYNYM źródłem prawdy. Pieśni dodaje się i poprawia WPROST w plikach .md.
# Ten skrypt nie tworzy ani nie nadpisuje treści — tylko odświeża indeks bazy (_INDEKS.md)
# na podstawie skanu plików. Po edycji bazy: ten skrypt, a potem pdf_full.py / pdf.py.

def read_title(p):
    for ln in open(p, encoding="utf-8"):
        if ln.startswith("# "): return ln[2:].strip()
    return os.path.basename(p)

def is_stub_file(p):
    return "⚠️" in open(p, encoding="utf-8").read()

# indeks budowany ze SKANU realnych plików (odzwierciedla ręczne edycje bazy)
files = sorted([p for p in glob.glob(os.path.join(DB, "*.md")) if not os.path.basename(p).startswith("_")],
               key=lambda p: norm(read_title(p)))
rows = []; nstub = 0
for p in files:
    t = read_title(p); st = is_stub_file(p); nstub += st
    rows.append(f"| {t}{' ⚠️' if st else ''} | [{os.path.basename(p)}]({os.path.basename(p)}) |")
idx = ["# Baza pieśni — indeks", "",
       f"Łącznie pieśni: **{len(files)}**  ·  z chwytami: **{len(files)-nstub}**  ·  do uzupełnienia: **{nstub}**.", "",
       "> `Baza_piesni/*.md` to źródło prawdy. Edytuj pliki wprost; potem `python3 zrodla/pdf_full.py` i `python3 zrodla/pdf.py`.", "",
       "| Pieśń | Plik |", "|---|---|", *rows]
open(os.path.join(DB, "_INDEKS.md"), "w", encoding="utf-8").write("\n".join(idx) + "\n")
print(f"INDEKS: {len(files)} pieśni, stubów: {nstub}")
