# -*- coding: utf-8 -*-
"""Testy czystej logiki ze wspólnego modułu: rozpoznawanie/usuwanie chwytów,
formatowanie tonacji, slug, parsowanie pliku pieśni."""
import pytest
import common


@pytest.mark.parametrize("tok", [
    "G", "D", "e", "h", "A7", "Cmaj7", "D/F#", "gis", "fis", "Dsus2", "Bm7",
    "Asus4", "H7", "|", "/x2", "(", "[/]",
    # warianty zapisu naprawione po zgłoszeniu (nawiasy wewnętrzne, łączenie „-", wiodący „/")
    "G(7)", "(h)", "(fis)", "G/h", "h-A-h", "/D-Dsus4",
])
def test_is_chord_positive(tok):
    assert common.is_chord(tok)


@pytest.mark.parametrize("tok", [
    "Chcemy", "wielbić", "Pan", "Jezu", "twarzy", "Panie", "życie", "Tobie",
    "miłość", "świat",
])
def test_is_chord_negative(tok):
    assert not common.is_chord(tok)


def test_strip_chords_removes_chord_lines_and_capo():
    body = "\n".join([
        "Capo 1",
        " G        D",
        "Pan kocha mnie   A7",
        " e   A   D",
        "i prowadzi mnie",
    ])
    assert common.strip_chords(body) == ["Pan kocha mnie", "i prowadzi mnie"]


def test_strip_chords_keeps_lyrics_without_chords():
    body = "Idzie mój Pan, idzie mój Pan"
    assert common.strip_chords(body) == ["Idzie mój Pan, idzie mój Pan"]


def _run(line):
    import re
    toks = [t for t in re.split(r"(\s+)", line) if t != ""]
    ns = [i for i, t in enumerate(toks) if t.strip()]
    return {toks[i] for i in common.chord_run(toks, ns)}


def test_chord_run_trailing():
    # tylko końcowy ciąg akordów, słowa tekstu nietknięte
    assert _run("Panie, któż jak Ty, od wieków   e C G(7)") == {"e", "C", "G(7)"}


def test_chord_run_legenda():
    # linia-legenda: wszystkie akordy kolorowane, etykiety sekcji zostają tekstem
    got = _run("zwrotka: E H A  |  ref.: E H cis A  |  bridge: H E A")
    assert got == {"E", "H", "A", "cis", "|"}
    assert "zwrotka:" not in got and "ref.:" not in got


def test_chord_run_nie_lapie_lirycznego_dwukropka():
    # słowo z dwukropkiem (NIE nazwa sekcji) nie robi z wersu legendy
    assert _run("Powiedziałeś:   F") == {"F"}


@pytest.mark.parametrize("tok,exp", [("zwrotka:", True), ("ref.:", True), ("bridge:", True),
                                     ("Powiedziałeś:", False), ("Pan", False)])
def test_is_section_label(tok, exp):
    assert common.is_section_label(tok) is exp


def test_build_version_zwraca_str():
    assert isinstance(common.build_version(), str)


@pytest.mark.parametrize("raw,expected", [
    ("G", "G-dur"),
    ("e", "e-moll"),
    ("d / e", "d-moll / e-moll"),
    ("a (capo 1)", "a-moll (capo 1)"),
    ("", ""),
])
def test_fmt_key(raw, expected):
    assert common.fmt_key(raw) == expected


@pytest.mark.parametrize("title,expected", [
    ("Cóż Ci Jezu damy", "coz-ci-jezu-damy"),
    ("Będę śpiewać", "bede-spiewac"),
    ("Idzie mój Pan", "idzie-moj-pan"),
    ("Łódź — Wełna", "lodz-welna"),
])
def test_slug(title, expected):
    assert common.slug(title) == expected


def test_parse_md(tmp_path):
    p = tmp_path / "x.md"
    p.write_text(
        "# Przykład\n\n- **Przeznaczenie:** na komunię\n- **Tonacja:** G\n\n"
        "```\n A   D\nLinia tekstu\n```\n",
        encoding="utf-8",
    )
    s = common.parse_md(str(p))
    assert s["title"] == "Przykład"
    assert s["section"] == "na komunię"
    assert s["key"] == "G"
    assert "Linia tekstu" in s["body"]
    assert s["stub"] is False


def test_parse_md_stub(tmp_path):
    p = tmp_path / "stub.md"
    p.write_text("# Stub\n\n- **Przeznaczenie:** dla dzieci\n\n> ⚠️ Tekst do uzupełnienia.\n", encoding="utf-8")
    s = common.parse_md(str(p))
    assert s["stub"] is True
    assert s["body"] == ""
