# -*- coding: utf-8 -*-
"""Wspólna logika generatorów śpiewnika.

Tu mieszka wszystko, co dzielą `pdf.py`, `pdf_full.py`, `pdf_plain.py`, `pdf_lud.py`:
ścieżki, paleta, parsowanie bazy `Baza_piesni/*.md`, rozpoznawanie i usuwanie chwytów,
formatowanie tonacji, ładowanie fontów oraz bazowa klasa PDF (nagłówek/stopka).
Baza `.md` jest źródłem prawdy — ten moduł niczego nie zapisuje."""
import os, re, glob, unicodedata, subprocess
from fpdf import FPDF

# --- ścieżki (wyliczane z położenia pliku — bez zaszytych ścieżek absolutnych) ---
ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC    = os.path.join(ROOT, "zrodla")
DB     = os.path.join(ROOT, "Baza_piesni")
FONTS  = os.path.join(SRC, "fonts")
ASSETS = os.path.join(SRC, "assets")

# --- publikacja (GitHub Pages) ---
SITE_URL = "https://zdanowicz.dev/spiewnik/"          # adres żywej strony — cel kodu QR na okładkach
QR_PATH  = os.path.join(ASSETS, "qr-spiewnik.png")    # statyczny QR (regeneracja: zrodla/make_qr.py)

# --- paleta (czarno-biały + szarości) ---
INK=(17,17,17); GRY=(120,120,120); LGY=(175,175,175); HAIR=(205,205,205)
CHORDCOL=(85,85,85)   # #555 — kolor chwytów

# --- helpery tekstowe ---
def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()

def norm(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii","ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()

def slug(t):
    t = t.replace("ł","l").replace("Ł","L")   # NFKD nie rozkłada „ł" — mapujemy ręcznie
    t = unicodedata.normalize("NFKD", t).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",t).strip("-")

# --- rozpoznanie chwytów (notacja polska A-H / a-h) ---
_cACC=r"(?:is|es|#|b)"; _cROOT=r"[A-Ha-h]"+_cACC+"?"
_cSUF=r"(?:maj7|maj|m11|m9|m7|m6|m|sus2|sus4|sus|dim|aug|add9|add|13|11|9|7|6|5|4|2|0|b5|\+)"
_cCHORD=_cROOT+_cSUF+r"*(?:/"+_cROOT+_cSUF+r"*)*"          # akord (+ opcjonalny bas po „/", np. G/h)
_CLUSTER=re.compile(r"^/?"+_cCHORD+r"(?:-"+_cCHORD+r")*$")  # ciąg akordów łączony „-", z opcjonalnym wiodącym „/"
_MARK=re.compile(r"^(?:[|/()\[\]:]+|/?x\d+|\d+x)$")
# etykieta sekcji w linii-legendzie chwytów (NIE każde słowo z dwukropkiem — tylko nazwy sekcji)
_LABEL=re.compile(r"^(?:zwrotka|zwr|zw|ref|refren|refr|bridge|most|intro|outro|coda|pre|prechorus|finał|final|solo|interludium)\.?:$", re.I)
def is_chord(tok):
    t=tok.strip()
    if not t: return False
    if _MARK.fullmatch(t): return True
    core=re.sub(r"[()\[\]]","",t).strip(".,;")             # zdejmij nawiasy (G(7)→G7, (h)→h) i interpunkcję
    return bool(core) and bool(re.search(r"[A-Ha-h]",core)) and bool(_CLUSTER.fullmatch(core))

def is_section_label(tok):
    """Token będący nazwą sekcji w linii-legendzie chwytów („zwrotka:", „ref.:", „bridge:")."""
    return bool(_LABEL.match(tok.strip()))

def chord_run(toks, ns):
    """Indeksy tokenów-akordów do pokolorowania/usunięcia.
    Domyślnie: KOŃCOWY ciąg tokenów-akordów (chwyty dopisane na końcu wersu).
    Wyjątek — linia-legenda (wszystkie nie-akordy to etykiety „zwrotka:"/„ref.:"):
    kolorujemy wszystkie akordy w linii."""
    chordset={i for i in ns if is_chord(toks[i])}
    if chordset and all(is_section_label(toks[i]) for i in ns if i not in chordset):
        return chordset
    run=set()
    for i in reversed(ns):
        if is_chord(toks[i]): run.add(i)
        else: break
    return run

# --- usuwanie chwytów (wersje bez chwytów) — obsługuje markery powtórzeń (/x2, (bis), x4) ---
_REP=re.compile(r"(?i)^/?\(?(?:x?\d+|\d+x|\d+/\d+|x|bis|ba[- ]?ba|baba)\)?$")
def strip_chords(body):
    out=[]
    for raw in body.split("\n"):
        if re.match(r"(?i)^\s*capo\b", raw): continue
        toks=[t for t in re.split(r"(\s+)", raw) if t!=""]
        ns=[i for i,t in enumerate(toks) if t.strip()]
        chordset={i for i in ns if is_chord(toks[i])}
        # linia-legenda lub czysto akordowa → pomiń w wersji bez chwytów
        if chordset and all(_LABEL.match(toks[i]) for i in ns if i not in chordset): continue
        run=set(); saw=False
        for i in reversed(ns):
            t=toks[i].strip()
            if is_chord(t): run.add(i); saw=True
            elif _REP.fullmatch(t): run.add(i)
            else: break
        if not saw: run=set()
        line="".join(t for i,t in enumerate(toks) if i not in run).rstrip()
        if line.strip()=="": continue
        out.append(line)
    res=[]; blank=False
    for l in out:
        if l.strip()=="":
            if not blank: res.append("")
            blank=True
        else: res.append(l); blank=False
    while res and res[0]=="": res.pop(0)
    while res and res[-1]=="": res.pop()
    return res

# --- tonacja: dopisuje -dur/-moll (WIELKA=dur, mała=moll), zachowuje „(capo n)" ---
_KEYROOT=re.compile(r"^[A-Ha-h](is|es|s)?[#b]?$")
def fmt_key(k):
    if not k: return k
    idx=k.find("(")
    head, tail = (k, "") if idx<0 else (k[:idx], k[idx:])
    cm=re.search(r"\bcapo\b", head, re.I)
    if cm: tail=(head[cm.start():]+(" "+tail if tail else "")).strip(); head=head[:cm.start()]
    out=[]
    for tok in re.split(r"(\s+|/)", head):
        st=tok.strip()
        out.append(tok+("-dur" if st[0].isupper() else "-moll") if st and _KEYROOT.match(st) else tok)
    res="".join(out).strip()
    return (res+" "+tail).strip() if tail else res

# --- parsowanie bazy (Baza_piesni/*.md) ---
def parse_md(path):
    txt=open(path,encoding="utf-8").read()
    title=re.search(r"^#\s+(.+)$",txt,re.M).group(1).strip()
    def field(name):
        m=re.search(r"\*\*"+name+r":\*\*\s*(.+)",txt)
        return m.group(1).strip() if m else ""
    mb=re.search(r"```[^\n]*\n(.*?)\n```",txt,re.S)
    body=mb.group(1) if mb else ""
    return {"title":title,"section":field("Przeznaczenie"),"key":field("Tonacja"),
            "source":field("Źródło"),"body":body,"stub":("⚠️" in txt and not body)}

def load_by_title(db=DB):
    out={}
    for p in sorted(glob.glob(os.path.join(db,"*.md"))):
        if os.path.basename(p).startswith("_"): continue
        s=parse_md(p); out[s["title"]]=s
    return out

def load_all(db=DB):
    return [parse_md(p) for p in sorted(glob.glob(os.path.join(db,"*.md")))
            if not os.path.basename(p).startswith("_")]

# --- wersja buildu (auto-stempel z gita: data + krótki hash ostatniego commita) ---
def build_version():
    """„RRRR-MM-DD · hash" ostatniego commita — na okładkę/stopkę i stronę web.
    Gdy git/repo niedostępne (np. po pobraniu ZIP-a) → pusty string (stempel pomijany)."""
    try:
        r=subprocess.run(["git","-C",ROOT,"log","-1","--format=%cd · %h","--date=format:%Y-%m-%d"],
                         capture_output=True, text=True, timeout=3)
        return r.stdout.strip() if r.returncode==0 else ""
    except Exception:
        return ""
BUILD_VERSION=build_version()

# --- fonty (wszystkie używane kroje; nadmiarowe rejestracje są nieszkodliwe) ---
def add_fonts(pdf):
    pdf.add_font("play","",  os.path.join(FONTS,"PlayfairDisplay-Regular.ttf"))
    pdf.add_font("play","B", os.path.join(FONTS,"PlayfairDisplay-Bold.ttf"))
    pdf.add_font("sans","",  os.path.join(FONTS,"InstrumentSans-Regular.ttf"))
    pdf.add_font("sans","B", os.path.join(FONTS,"InstrumentSans-Bold.ttf"))
    pdf.add_font("semi","",  os.path.join(FONTS,"InstrumentSans-SemiBold.ttf"))
    pdf.add_font("mono","",  os.path.join(FONTS,"Cousine-Regular.ttf"))
    pdf.add_font("mono","B", os.path.join(FONTS,"Cousine-Bold.ttf"))

# --- kod QR do strony (na okładkę): osadza statyczny PNG, gdy istnieje ---
def draw_site_qr(pdf, cx, y, size, caption="ŚPIEWNIK ONLINE · ZDANOWICZ.DEV/SPIEWNIK"):
    """Rysuje QR wyśrodkowany w (cx) od góry y, bok=size. Zwraca y pod podpisem.
    Gdy brak assetu (qr-spiewnik.png) — nic nie rysuje (graceful)."""
    if not os.path.exists(QR_PATH): return y
    pdf.image(QR_PATH, x=cx-size/2, y=y, w=size, h=size)
    yb=y+size
    if caption:
        pdf.set_xy(0, yb+1.6); pdf.set_font("sans","",6.8); pdf.set_text_color(*GRY); pdf.set_char_spacing(1.1)
        pdf.cell(pdf.w, 4, caption, align="C"); pdf.set_char_spacing(0); pdf.set_text_color(*INK)
        yb+=5.6
    return yb

# --- bazowa klasa PDF: nagłówek/stopka w stylu śpiewnika A4/A5 ---
# (left_label/right_label nadpisuje każdy generator; pdf_lud.py ma własny, kompaktowy nagłówek)
class SongbookPDF(FPDF):
    chrome=False
    left_label="ŚPIEWNIK"
    right_label=""
    version=BUILD_VERSION
    def header(self):
        if not self.chrome or self.page_no()==1:
            self.set_y(self.t_margin); return
        self.set_draw_color(*HAIR); self.set_line_width(0.2)
        self.line(self.l_margin, 11, self.w-self.r_margin, 11)
        self.set_xy(self.l_margin, 6); self.set_font("sans","",7.5); self.set_text_color(*LGY)
        self.set_char_spacing(1.2); self.cell(0, 4, self.left_label); self.set_char_spacing(0)
        self.set_xy(self.l_margin, 6); self.cell(self.w-2*self.l_margin, 4, self.right_label, align="R")
        self.set_text_color(*INK)
        self.set_y(self.t_margin)            # kursor pod nagłówkiem (bez nachodzenia)
    def footer(self):
        if not self.chrome or self.page_no()==1: return
        self.set_y(-12); self.set_font("play","",9); self.set_text_color(*GRY)
        self.cell(0,6,str(self.page_no()),align="C")
        if self.version:                                   # dyskretny stempel wersji (lewy dół) — by poznać aktualność luźnej kartki
            self.set_xy(self.l_margin,-12); self.set_font("sans","",6.5); self.set_text_color(*LGY)
            self.set_char_spacing(0.4); self.cell(0,6,self.version); self.set_char_spacing(0)
        self.set_text_color(*INK)
