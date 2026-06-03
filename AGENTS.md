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

- **`Baza_piesni/*.md` to jedyne źródło prawdy.** Pieśni dodaje się i poprawia WPROST w plikach
  `.md`. Generatory tylko je czytają.
- **`generuj.py` niczego nie tworzy ani nie nadpisuje** — skanuje bazę i odświeża `_INDEKS.md`.
  Uruchamiaj po ręcznych zmianach w bazie, przed generowaniem PDF.
- **Nazwa pliku = slug tytułu.** Dla nowej pieśni nazwij plik zgodnie z tytułem z nagłówka `#`,
  z ręcznym mapowaniem `ł→l`/`Ł→L` (NFKD nie rozkłada „ł"), małe litery, spacje → `-`.
- **Tytuł ↔ `SELECTED`:** śpiewnik wyjazdowy (`pdf.py`, `pdf_plain.py`, `pdf_lud.py`) dopasowuje
  pieśni po dokładnym **tytule** z listy `SELECTED` w `plan_data.py`. Zmiana `# Tytuł` w pliku =
  pieśń znika z wyjazdowego, dopóki nie zaktualizujesz `SELECTED`.

## Rozpoznawanie i kolorowanie akordów

- `_is_chord(token)` rozpoznaje token akordowy (root A–H/a–h + akcydencje `is/es/#/b` +
  sufiksy `m, maj7, sus, dim, add, 7, 9…` oraz klastry typu `GDCG`) i markery (`|`, `/x2`…).
- W linii kolorowany (szary `#555`, pogrubiony) jest **tylko końcowy ciąg tokenów-akordów** —
  liczony od końca aż do pierwszego nie-akordu. Dzięki temu chwyty nad tekstem i kolumny chwytów
  na końcu linii są szare, a słowa tekstu czarne.
- W wersjach bez chwytów `strip_chords()` usuwa też markery powtórzeń (`/x2`, `(bis)`, `x4`…).
- Uwaga na kolizję nazw: w bloku kolorowania akordów używaj `_cROOT/_cACC/_cSUF`, nie
  `_ROOT/_ACC/_SUF` (te ostatnie należą do `fmt_key`).

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
