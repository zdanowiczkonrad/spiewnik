# -*- coding: utf-8 -*-
"""Testy integralności bazy Baza_piesni (źródło prawdy) i listy SELECTED.
Baza dzieli się na kolekcje (książki) — patrz zrodla/books.py — każda we własnym katalogu
(płaskim albo z podkatalogami, np. „18-nadia": polskie/zagraniczne)."""
import glob, os
import common
from books import BOOKS
from plan_data import SELECTED


def _files(book):
    return common._md_files(book["src"], book["recursive"])

# wszystkie pliki ze wszystkich kolekcji
MD = [p for book in BOOKS.values() for p in _files(book)]


def test_baza_niepusta():
    assert len(MD) >= 1


def test_kazdy_plik_sie_parsuje_i_ma_tytul():
    for p in MD:
        s = common.parse_md(p)
        assert s["title"].strip(), f"pusty tytuł: {p}"


def test_nazwa_pliku_rowna_slug_tytulu():
    bad = []
    for p in MD:
        s = common.parse_md(p)
        expected = common.slug(s["title"]) + ".md"
        if os.path.basename(p) != expected:
            bad.append(f"{os.path.basename(p)} != {expected} (tytuł: {s['title']})")
    assert not bad, "nazwa pliku ≠ slug(tytułu):\n" + "\n".join(bad)


def test_piesn_ma_tresc_albo_jest_stubem():
    for p in MD:
        s = common.parse_md(p)
        assert s["body"].strip() or s["stub"], f"brak treści i nie-stub: {p}"


def test_selected_unikalne():
    assert len(SELECTED) == len(set(SELECTED))


def test_selected_obecne_w_bazie_i_nie_stuby():
    by_title = common.load_by_title()   # domyślnie kolekcja religijna (common.REL)
    brakuje = [t for t in SELECTED if t not in by_title]
    assert not brakuje, "tytuły z SELECTED nieobecne w bazie: " + ", ".join(brakuje)
    stuby = [t for t in SELECTED if by_title[t]["stub"]]
    assert not stuby, "tytuły z SELECTED będące stubami: " + ", ".join(stuby)


def test_kazda_kolekcja_niepusta():
    for name, book in BOOKS.items():
        assert _files(book), f"pusta kolekcja: {name}"


def test_tytuly_unikalne_w_kolekcji():
    for name, book in BOOKS.items():
        titles = [common.parse_md(p)["title"] for p in _files(book)]
        dup = {t for t in titles if titles.count(t) > 1}
        assert not dup, f"zdublowane tytuły w kolekcji {name}: " + ", ".join(dup)
