# Rzeczy do dodania

# Key features
- Czytanie na dzis (kalendarz) + generator oprawy na podstawie czytan
- PWA, generator do druku PDF/obstawa piesni
- Konfigurator obstawy w apce (wybor piesni na poszczegolne czesci mszy)

## Baza pieśni
- Edytor pieśni webowy za hasłem (P1)
- ✅ Unifikacja notacji chwytów (P0) — `canon_chord()` w common.py; baza ujednolicona do notacji polskiej (Am→a, C#m7→cis7, C#7→Cis7); `zrodla/unify_notation.py`

## Print, skład
- ✅ Raportuj za mały font w pieśniach i zasugeruj przerzucenie akordow "nad linijke" — raport po buildzie `pdf_full.py` (próg 7.0 chwyty / 8.5 teksty)
- nie pozwalaj na łamanie linii z chwytami od tekstu 
- Cała pieśń bez przekładania strony - zeby podczas grania nie bylo trzeba sie meczyc
- ✅ Kod QR prowadzacy do aktualnego spiewnika — na okładkach (→ zdanowicz.dev/spiewnik), regeneracja `zrodla/make_qr.py`
- ✅ wersja spiewnika — auto-stempel z gita (data · hash) na okładce/stopce PDF i stronie web

## Engine, formatowanie
- Indeks source'ów i linki do youtube
- ✅ Indeks fajnych akordów — `chords.json` + `draw_chord_index` (sus/otwartostrunowe wojsingi pogrupowane parami dur/moll, z funkcjami); załącznik w `pdf_full` + widok na web (SVG). TODO: stroje open E/C/D, jazzowe
- Generator progresji z pochodami basowymi oraz ergonomicznymi pozycjami

## Web
- lista historyczna doboru pieśni (P0)
- Oprawa Mszy - opcja podglądu pieśni + wejścia rozwinięcia pieśni (P0)
- ✅ Przełącznik notacji chwytow — toggle PL↔US w app.js (H↔B), domyślnie polska; `to_american()` + port JS
* Transpozycja 
* schematy akordow po hover — jest pełny WIDOK indeksu akordów (przycisk „Akordy"); hover-na-akord-w-pieśni wymaga biblioteki pojedynczych kształtów (osobne dane)

## Poprawki w pieśniach


## Nowe pieśni


## Generator

## Misc
- Kategorie pieśni - nie tylko religijne? (P0)
- Osobne entrypointy do róznych spiewnikow (P1)


# Muzyka Polska - poezja
- Smierc na piec
* Trudno nie wierzyc w nic
* Jutro mozemy byc szczesliwi
- niebo do wynajecia
