# AGENTS.md

Wskazówki dla agentów/współtwórców pracujących nad tym projektem. Najpierw przeczytaj
[`README.md`](README.md) (architektura i pipeline). Poniżej konwencje i pułapki, których
nie widać wprost z kodu.

## Struktura kodu

- `zrodla/common.py` — **cała wspólna logika** (ścieżki z `__file__`, paleta, `parse_md`,
  `is_chord`/`strip_chords`, `fmt_key`, `slug`/`fold`/`norm`, `add_fonts`, klasa `SongbookPDF`).
  Nową logikę dziel tutaj — nie kopiuj między generatorami.
- `zrodla/plan_data.py` — dane: `EVENT` (nazwa wydarzenia → okładki/nagłówki/nazwy plików;
  zmiana w jednym miejscu), `SELECTED`, `PLAN`.
- `zrodla/pdf*.py` — tylko warstwa układu (okładka, rysowanie pieśni, paginacja).
- `tests/` — `pytest`; uruchom po każdej zmianie logiki lub bazy.
- Ścieżki wylicza się z `__file__` (bez zaszytych absolutnych) — kod działa po sklonowaniu.

## Reguły bazy

- **`Baza_piesni/**/*.md` to jedyne źródło prawdy.** Pieśni dodaje się i poprawia WPROST w plikach
  `.md`. Generatory tylko je czytają.
- **Kolekcje (typy śpiewnika).** Baza dzieli się na kolekcje skonfigurowane w `zrodla/books.py`
  (`BOOKS`), dwojakiego rodzaju: **folderowe** (`src` → `Baza_piesni/<nazwa>/`: `religijne`, `polskie`,
  `zagraniczne`) i **składanki/listowe** (`list`+`from` → plik `Baza_piesni/18-nadia.md` z samymi
  tytułami, zbierany po tytule z kolekcji `from`; treść NIE jest kopiowana). Pieśni kolekcji daje
  `books.load_book(book) → (songs, missing)` — używają go `pdf_full.py`, `site.py`, `generuj.py`;
  nie wczytuj bazy ręcznie. Religijne generatory (`pdf.py`, `pdf_plain.py`, `pdf_lud.py`) nadal idą
  przez `load_by_title()` (domyślnie `common.REL`). Każda kolekcja ma `slug` (URL pod `docs/<slug>/`,
  `religijne` = root) i `nav_label` (linki w stopce do innych śpiewników, względne URL-e z `rel_url`).
  Nowy śpiewnik = wpis w `BOOKS`, nie nowy generator.
- **Pułapka H/B przy imporcie tabów pop.** Samotne `B` w zapisie międzynarodowym = H (B-dur);
  `canon_chord` traktuje samotne `B` jak Bb (polskie B), więc po `unify_notation.py` ręcznie zamień
  takie `B`→`H` (zob. `szampan-sanah.md`). `Bb`→`B`, `Em`→`e`, `C#m`→`cis`, `F#m`→`fis` idą automatem.
- **`generuj.py` niczego nie tworzy ani nie nadpisuje** — skanuje bazę i odświeża `_INDEKS.md`.
  Uruchamiaj po ręcznych zmianach w bazie, przed generowaniem PDF.
- **Nazwa pliku = slug tytułu.** Dla nowej pieśni nazwij plik zgodnie z tytułem z nagłówka `#`,
  z ręcznym mapowaniem `ł→l`/`Ł→L` (NFKD nie rozkłada „ł"), małe litery, spacje → `-`.
- **Tytuł ↔ `SELECTED`:** śpiewnik wyjazdowy (`pdf.py`, `pdf_plain.py`, `pdf_lud.py`) dopasowuje
  pieśni po dokładnym **tytule** z listy `SELECTED` w `plan_data.py`. Zmiana `# Tytuł` w pliku =
  pieśń znika z wyjazdowego, dopóki nie zaktualizujesz `SELECTED`.

## Rozpoznawanie i kolorowanie akordów

- `is_chord(token)` rozpoznaje token akordowy (root A–H/a–h + akcydencje `is/es/#/b` +
  sufiksy `m, maj7, sus, dim, add, 7, 9…`, klastry typu `GDCG`, akordy z basem `G/h`,
  nawiasy wewnętrzne `G(7)`→`G7`, sekwencje łączone `-` i wiodący `/`: `h-A-h`, `/D-Dsus4`)
  oraz markery (`|`, `/x2`…).
- **Który token to chwyt liczy współdzielony `chord_run(toks, ns)`** (NIE kopiuj pętli — używają
  go `pdf.py`, `pdf_full.py`, `site.py`): domyślnie **końcowy ciąg tokenów-akordów** (od końca
  do pierwszego nie-akordu), więc chwyty nad tekstem i kolumny na końcu linii są szare, a słowa
  czarne. Wyjątek — **linia-legenda**: gdy wszystkie nie-akordy to nazwy sekcji (`is_section_label`:
  `zwrotka:`, `ref.:`, `bridge:`, `intro:`…), kolorowane są **wszystkie** chwyty w linii.
- W wersjach bez chwytów `strip_chords()` usuwa markery powtórzeń (`/x2`, `(bis)`, `x4`…) i
  pomija całe linie-legendy oraz czysto akordowe.
- Uwaga na kolizję nazw: w bloku rozpoznawania akordów używaj `_cROOT/_cACC/_cSUF`, nie
  `_ROOT/_ACC/_SUF` (te ostatnie należą do `fmt_key`).

## Wersja buildu i kod QR

- `BUILD_VERSION` (w `common.py`) = `RRRR-MM-DD · hash` ostatniego commita (z gita; przy braku
  repo → `""` i stempel jest pomijany). Trafia na okładki, stopki PDF (`SongbookPDF.footer`,
  własna stopka `pdf_lud`) i stopkę strony web — żeby poznać aktualność luźnej wydrukowanej kartki.
- Kod QR na okładkach prowadzi do `SITE_URL` (`zdanowicz.dev/spiewnik`). Osadza go `draw_site_qr()`
  ze statycznego `zrodla/assets/qr-spiewnik.png`. **Regeneracja po zmianie URL:** `python3 zrodla/make_qr.py`
  (tylko biblioteka standardowa — pobiera PNG z publicznego API; NIE jest częścią runtime/CI),
  potem zacommituj nowy PNG. Brak assetu = okładka bez QR (graceful).

## Pułapki fpdf2

- Po `cell`/`multi_cell` ustawiaj `new_x=XPos.LMARGIN, new_y=YPos.NEXT` (albo `set_x`), inaczej
  zawijany tekst ucieka na prawą krawędź.
- `header()`/`footer()` działają w izolowanym stanie graficznym — zmiany `set_char_spacing`
  w nagłówku są COFANE po jego zakończeniu. Po każdej sekcji z rozstrzeleniem (np. okładka)
  rób jawnie `set_char_spacing(0)`; treść pieśni musi mieć char_spacing 0.
- Na końcu `header()` daj `self.set_y(self.t_margin)`, żeby nagłówek nie nachodził na treść.
- Rozmiar fontu bloku pieśni dobierany jest **dynamicznie** wg najdłuższej linii
  (`bs = min(CAP, 10*PW/maxw)`), żeby najdłuższa linia zmieściła się w szerokości kolumny.
  Nie zastępuj tego stałym rozmiarem.

## Źródło prawdy, bez materiałów zewnętrznych

Teksty i chwyty w `Baza_piesni/*.md` są opracowane ręcznie i stanowią jedyne źródło prawdy.
Projekt nie zawiera ani nie zależy od żadnych zewnętrznych kopii śpiewników. **Nie wprowadzaj
do drzewa projektu cudzych ekstrakcji/skanów śpiewników.**

## Środowisko

- Jedyna zależność zewnętrzna: `fpdf2`. Reszta — biblioteka standardowa Pythona 3.
- Brak `pandoc`/`libreoffice`. Dostępne: `pdftotext`/`pdftoppm` (poppler), python-`docx`.
- Po zmianach w bazie weryfikuj regeneracją wszystkich wariantów PDF (patrz README) i podglądem.
