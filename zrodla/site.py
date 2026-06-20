# -*- coding: utf-8 -*-
"""Generator statycznej strony śpiewnika (GitHub Pages).

Buduje samodzielny katalog `docs/` z bazy `Baza_piesni/*.md`:
- index.html (lista + wyszukiwarka + widok pieśni, dane wbudowane inline),
- style.css, app.js (kopiowane z web/), fonts/ (Cousine/Playfair/Instrument),
- pdf/ (kopie wygenerowanych śpiewników do pobrania).
Linki są względne — działa pod dowolną ścieżką (np. zdanowicz.dev/spiewnik/)."""
import os, re, sys, json, glob, html, shutil
from common import ROOT, FONTS, fold, fmt_key, chord_run, is_section_label, BUILD_VERSION, load_all, load_chords
from books import BOOKS, DEFAULT_BOOK, get_book

WEB  = os.path.join(ROOT, "web")
DOCS = os.path.join(ROOT, "docs")

SITE_FONTS = ["PlayfairDisplay-Bold.ttf", "InstrumentSans-Regular.ttf",
              "InstrumentSans-SemiBold.ttf", "Cousine-Regular.ttf", "Cousine-Bold.ttf"]

def render_body_html(body):
    """Linie pieśni → <div class="ln">; chwyty (końcowy ciąg tokenów) w <span class="ch">,
    linie samych chwytów / „Capo" oznaczone .chordline (ukrywane w trybie bez chwytów)."""
    out = []
    for raw in body.split("\n"):
        if raw.strip() == "":
            out.append('<div class="ln blank"></div>'); continue
        capo = bool(re.match(r"(?i)^\s*capo\b", raw))
        toks = [t for t in re.split(r"(\s+)", raw) if t != ""]
        ns = [i for i, t in enumerate(toks) if t.strip()]
        run = chord_run(toks, ns)
        # linia samych chwytów lub legenda (zwrotka:/ref.:) → .chordline (ukrywana bez chwytów)
        chordonly = capo or (len(ns) > 0 and all((i in run) or is_section_label(toks[i]) for i in ns))
        parts = []
        for i, t in enumerate(toks):
            esc = html.escape(t)
            parts.append('<span class="ch">' + esc + '</span>' if (i in run and not capo) else esc)
        out.append('<div class="ln%s">%s</div>' % (" chordline" if chordonly else "", "".join(parts)))
    return "".join(out)

def build_songs(book):
    songs = [s for s in load_all(book["src"], book["recursive"]) if not s["stub"]]
    songs.sort(key=lambda s: fold(s["title"]))
    data = []
    for i, s in enumerate(songs, 1):
        data.append({
            "nr": i,
            "title": s["title"],
            "section": s["section"],
            "keyfmt": fmt_key(s["key"]),
            "q": fold(s["title"]),
            "html": render_body_html(s["body"]),
        })
    return data

def copy_assets(book):
    site = book["site_dir"]
    os.makedirs(os.path.join(site, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(site, "pdf"), exist_ok=True)
    for f in ("style.css", "app.js"):
        shutil.copy2(os.path.join(WEB, f), os.path.join(site, f))
    for f in SITE_FONTS:
        shutil.copy2(os.path.join(FONTS, f), os.path.join(site, "fonts", f))
    pdfs = sorted(p for p in glob.glob(os.path.join(book["pdf_dir"], "*.pdf"))
                  if not os.path.basename(p).startswith("_"))   # pomiń pliki robocze (_podglad…)
    for p in pdfs:
        shutil.copy2(p, os.path.join(site, "pdf", os.path.basename(p)))
    return [os.path.basename(p) for p in pdfs]

def downloads_html(pdf_names):
    if not pdf_names: return ""
    items = "".join(
        '<a href="pdf/%s" download>%s</a>' % (html.escape(n.replace('"', "%22")),
                                              html.escape(n[:-4] if n.lower().endswith(".pdf") else n))
        for n in pdf_names)
    return '<section class="downloads"><div class="wrap"><h2>Do pobrania (PDF)</h2>%s</div></section>' % items

PAGE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<meta name="description" content="Śpiewnik z chwytami — wyszukaj pieśń lub wybierz po numerze.">
<title>__TITLE__</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="top"><div class="wrap">
  <div class="toprow"><h1>__TITLE__</h1><button id="openChords" class="navbtn">♪ Akordy</button></div>
  <div class="searchbar"><input id="q" type="search" inputmode="search" enterkeyhint="search"
       placeholder="Szukaj tytułu lub wpisz numer…" autocomplete="off" autocapitalize="none"></div>
  <div class="filters" id="filters"></div>
</div></header>
<main class="wrap"><div id="list" class="list"></div></main>
__DOWNLOADS__
<footer class="sitever"><div class="wrap">__VERSION__</div></footer>
<div id="songview" class="songview" hidden>
  <div class="songbar">
    <button id="back" class="iconbtn" aria-label="Wróć do listy">‹ Lista</button>
    <div class="songtools">
      <button id="toggleNotation" class="iconbtn" aria-pressed="false" title="Notacja polska / amerykańska">H↔B</button>
      <button id="toggleChords" class="iconbtn" aria-pressed="true">♪ chwyty</button>
      <button id="fontMinus" class="iconbtn" aria-label="Mniejszy tekst">A−</button>
      <button id="fontPlus" class="iconbtn" aria-label="Większy tekst">A+</button>
    </div>
  </div>
  <article id="song" class="song"></article>
</div>
<div id="chordsview" class="songview" hidden>
  <div class="songbar">
    <button id="chordsBack" class="iconbtn" aria-label="Wróć do listy">‹ Lista</button>
    <div class="songtools">
      <button id="toggleNotationCd" class="iconbtn" aria-pressed="false" title="Notacja polska / amerykańska">H↔B</button>
    </div>
  </div>
  <article id="chordsbody" class="chordsbody"></article>
</div>
<script>window.SONGS=__DATA__;window.CHORDS=__CHORDS__;window.CHORD_SHAPES=__SHAPES__;</script>
<script src="app.js"></script>
</body>
</html>
"""

def build_site(name, book):
    site = book["site_dir"]
    os.makedirs(site, exist_ok=True)
    songs = build_songs(book)
    pdf_names = copy_assets(book)
    ver = ("wersja " + html.escape(BUILD_VERSION)) if BUILD_VERSION else ""
    cdata = load_chords()
    page = (PAGE
            .replace("__TITLE__", html.escape(book["site_title"]))
            .replace("__DOWNLOADS__", downloads_html(pdf_names))
            .replace("__VERSION__", ver)
            .replace("__CHORDS__", json.dumps(cdata.get("voicings", {}), ensure_ascii=False, separators=(",", ":")))
            .replace("__SHAPES__", json.dumps(cdata.get("chords", {}), ensure_ascii=False, separators=(",", ":")))
            .replace("__DATA__", json.dumps(songs, ensure_ascii=False, separators=(",", ":"))))
    with open(os.path.join(site, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    # .nojekyll — żeby GitHub Pages nie przetwarzał katalogu przez Jekyll
    open(os.path.join(site, ".nojekyll"), "w").close()
    print("OK: %s | kolekcja: %s | pieśni: %d | PDF do pobrania: %d" % (site, name, len(songs), len(pdf_names)))

def main():
    # --collection NAZWA → tylko ta kolekcja; bez flagi → wszystkie zdefiniowane w books.py
    if "--collection" in sys.argv:
        i = sys.argv.index("--collection")
        name = sys.argv[i+1] if i+1 < len(sys.argv) else DEFAULT_BOOK
        build_site(name, get_book(name))
    else:
        for name, book in BOOKS.items():
            build_site(name, book)

if __name__ == "__main__":
    main()
