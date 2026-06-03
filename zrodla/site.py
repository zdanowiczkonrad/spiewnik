# -*- coding: utf-8 -*-
"""Generator statycznej strony śpiewnika (GitHub Pages).

Buduje samodzielny katalog `docs/` z bazy `Baza_piesni/*.md`:
- index.html (lista + wyszukiwarka + widok pieśni, dane wbudowane inline),
- style.css, app.js (kopiowane z web/), fonts/ (Cousine/Playfair/Instrument),
- pdf/ (kopie wygenerowanych śpiewników do pobrania).
Linki są względne — działa pod dowolną ścieżką (np. zdanowicz.dev/spiewnik/)."""
import os, re, json, glob, html, shutil
from common import ROOT, FONTS, fold, fmt_key, is_chord, load_all

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
        run = set()
        for i in reversed(ns):
            if is_chord(toks[i]): run.add(i)
            else: break
        chordonly = capo or (len(ns) > 0 and all(i in run for i in ns))
        parts = []
        for i, t in enumerate(toks):
            esc = html.escape(t)
            parts.append('<span class="ch">' + esc + '</span>' if (i in run and not capo) else esc)
        out.append('<div class="ln%s">%s</div>' % (" chordline" if chordonly else "", "".join(parts)))
    return "".join(out)

def build_songs():
    songs = [s for s in load_all() if not s["stub"]]
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

def copy_assets():
    os.makedirs(os.path.join(DOCS, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "pdf"), exist_ok=True)
    for f in ("style.css", "app.js"):
        shutil.copy2(os.path.join(WEB, f), os.path.join(DOCS, f))
    for f in SITE_FONTS:
        shutil.copy2(os.path.join(FONTS, f), os.path.join(DOCS, "fonts", f))
    pdfs = sorted(glob.glob(os.path.join(ROOT, "*.pdf")))
    for p in pdfs:
        shutil.copy2(p, os.path.join(DOCS, "pdf", os.path.basename(p)))
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
<title>Śpiewnik</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="top"><div class="wrap">
  <h1>Śpiewnik</h1>
  <div class="searchbar"><input id="q" type="search" inputmode="search" enterkeyhint="search"
       placeholder="Szukaj tytułu lub wpisz numer…" autocomplete="off" autocapitalize="none"></div>
  <div class="filters" id="filters"></div>
</div></header>
<main class="wrap"><div id="list" class="list"></div></main>
__DOWNLOADS__
<div id="songview" class="songview" hidden>
  <div class="songbar">
    <button id="back" class="iconbtn" aria-label="Wróć do listy">‹ Lista</button>
    <div class="songtools">
      <button id="toggleChords" class="iconbtn" aria-pressed="true">♪ chwyty</button>
      <button id="fontMinus" class="iconbtn" aria-label="Mniejszy tekst">A−</button>
      <button id="fontPlus" class="iconbtn" aria-label="Większy tekst">A+</button>
    </div>
  </div>
  <article id="song" class="song"></article>
</div>
<script>window.SONGS=__DATA__;</script>
<script src="app.js"></script>
</body>
</html>
"""

def main():
    os.makedirs(DOCS, exist_ok=True)
    songs = build_songs()
    pdf_names = copy_assets()
    page = (PAGE
            .replace("__DOWNLOADS__", downloads_html(pdf_names))
            .replace("__DATA__", json.dumps(songs, ensure_ascii=False, separators=(",", ":"))))
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    # .nojekyll — żeby GitHub Pages nie przetwarzał katalogu przez Jekyll
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("OK: %s | pieśni: %d | PDF do pobrania: %d" % (DOCS, len(songs), len(pdf_names)))

if __name__ == "__main__":
    main()
