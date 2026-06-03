# Śpiewnik

Generator śpiewników PDF (z chwytami gitarowymi i bez) na oprawę muzyczną mszy —
przygotowywany na kręgi wyjazdowe Domowego Kościoła. Pieśni trzymane są jako pliki
Markdown, a skrypty Pythona składają z nich gotowe śpiewniki w kilku wariantach.

## Zasada działania

**Źródłem prawdy jest katalog [`Baza_piesni/`](Baza_piesni/)** — jeden plik `.md` = jedna pieśń.
Pieśni poprawia się i dodaje **wprost w plikach `.md`**, a potem regeneruje PDF-y.
Generatory nigdy nie nadpisują bazy.

### Format pliku pieśni

```markdown
# Idzie mój Pan

- **Przeznaczenie:** na komunię
- **Tonacja:** d / e

​```
 d          g     d
Mija góry, łąki, lasy,
 C           F  G     A7
By Komunii stał się cud.
​```
```

- `# Tytuł` — nagłówek (jeden, pierwszy).
- `- **Przeznaczenie:**` — część mszy (na wejście / ofiarowanie / komunię /
  uwielbienie… / klasyczne / części stałe / dla dzieci / na wyjście).
- `- **Tonacja:**` — notacja polska (patrz niżej). Pole opcjonalne.
- Treść pieśni w bloku ` ``` ` — chwyty zapisane w linii **nad** tekstem lub na końcu linii.

(Parser akceptuje też opcjonalne `- **Źródło:**`, ale nie jest ono drukowane w PDF.)

### Notacja chwytów (polska)

Wielka litera = akord **durowy**, mała litera = **molowy**, `h` = H-moll.
Generator dopisuje `-dur` / `-moll` w metryczce automatycznie i zachowuje zapis `(capo n)`.

## Szybki start

```bash
pip install -r requirements.txt   # jedyna zależność: fpdf2 (reszta to biblioteka standardowa)
cd zrodla
python3 generuj.py         # (opcjonalnie) odświeża _INDEKS.md po edycji bazy
python3 pdf_full.py        # pełny śpiewnik (A4, z chwytami)
python3 pdf.py             # śpiewnik wyjazdowy + porządek nabożeństw
```

## Generatory

| Skrypt | Czyta | Produkuje |
|---|---|---|
| `zrodla/generuj.py` | skan `Baza_piesni/*.md` | `Baza_piesni/_INDEKS.md` (odświeżenie indeksu) |
| `zrodla/pdf_full.py` | `Baza_piesni/*.md`, fonty | `Śpiewnik pełny – chwyty[.pdf / (A5)]`, `… teksty[.pdf / (A5)]` |
| `zrodla/pdf.py` | `Baza_piesni/*.md`, `plan_data.py`, fonty | `Śpiewnik wyjazd – Boże Ciało 2026.pdf` (z chwytami + plan liturgii) |
| `zrodla/pdf_plain.py` | `Baza_piesni/*.md`, `plan_data.py`, fonty | `Śpiewnik wyjazd … (bez chwytów).pdf` |
| `zrodla/pdf_lud.py` | `Baza_piesni/*.md`, `plan_data.py`, fonty | `Śpiewnik dla ludu – Boże Ciało 2026.pdf` (2 kolumny, kompaktowy) |

Flagi `pdf_full.py`: `--a5` (format kieszonkowy A5), `--plain` (same teksty, bez chwytów).
Cztery warianty pełnego śpiewnika powstają z kombinacji tych flag.

Wspólna logika wszystkich generatorów (parsowanie bazy, rozpoznawanie/usuwanie chwytów,
tonacja, fonty, bazowa klasa PDF, ścieżki) mieszka w [`zrodla/common.py`](zrodla/common.py) —
generatory tylko ją importują, bez duplikacji.

[`zrodla/plan_data.py`](zrodla/plan_data.py) to wspólne dane: `EVENT` (nazwa wydarzenia w
okładkach/nagłówkach/nazwach plików), `SELECTED` (lista pieśni na dany wyjazd, w kolejności jak
w śpiewniku) i `PLAN` (harmonogram liturgii z czytaniami).

## Testy

```bash
pip install pytest
pytest                     # logika chwytów/tonacji, integralność bazy, smoke-build PDF-ów
```
Testy w [`tests/`](tests/) sprawdzają m.in. że nazwa każdego pliku == slug(tytułu), że każdy
tytuł z `SELECTED` istnieje w bazie i nie jest stubem, oraz że każdy generator buduje poprawny
PDF. CI (GitHub Actions, [`.github/workflows/ci.yml`](.github/workflows/ci.yml)) uruchamia je na
każdy push.

## Fonty

W [`zrodla/fonts/`](zrodla/fonts/). Realnie używane: **Playfair Display** (tytuły/okładka,
OFL), **Instrument Sans** (etykiety/teksty, OFL), **Cousine** (chwyty + treść pieśni, Apache 2.0).

## Źródło prawdy

Teksty i chwyty w `Baza_piesni/*.md` zostały opracowane i zapisane ręcznie i to one są jedynym
źródłem prawdy projektu. Cały pipeline czyta wyłącznie `Baza_piesni/*.md` + `plan_data.py` —
nie korzysta z żadnych zewnętrznych kopii śpiewników.

## Plan liturgiczny

[`Oprawa muzyczna – Boże Ciało 2026.md`](Oprawa%20muzyczna%20–%20Boże%20Ciało%202026.md) —
dobór pieśni do każdej części mszy na poszczególne dni, z odniesieniem do czytań.
