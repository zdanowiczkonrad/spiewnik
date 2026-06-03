# -*- coding: utf-8 -*-
"""Testy integralności bazy Baza_piesni/*.md (źródło prawdy) i listy SELECTED."""
import glob, os
import common
from plan_data import SELECTED

MD = [p for p in glob.glob(os.path.join(common.DB, "*.md"))
      if not os.path.basename(p).startswith("_")]


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
    by_title = common.load_by_title()
    brakuje = [t for t in SELECTED if t not in by_title]
    assert not brakuje, "tytuły z SELECTED nieobecne w bazie: " + ", ".join(brakuje)
    stuby = [t for t in SELECTED if by_title[t]["stub"]]
    assert not stuby, "tytuły z SELECTED będące stubami: " + ", ".join(stuby)
