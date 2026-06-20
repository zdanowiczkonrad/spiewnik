# -*- coding: utf-8 -*-
"""Wspólna logika generatorów śpiewnika.

Tu mieszka wszystko, co dzielą `pdf.py`, `pdf_full.py`, `pdf_plain.py`, `pdf_lud.py`:
ścieżki, paleta, parsowanie bazy `Baza_piesni/*.md`, rozpoznawanie i usuwanie chwytów,
formatowanie tonacji, ładowanie fontów oraz bazowa klasa PDF (nagłówek/stopka).
Baza `.md` jest źródłem prawdy — ten moduł niczego nie zapisuje."""
import os, re, glob, unicodedata, subprocess
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# --- ścieżki (wyliczane z położenia pliku — bez zaszytych ścieżek absolutnych) ---
ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC    = os.path.join(ROOT, "zrodla")
DB     = os.path.join(ROOT, "Baza_piesni")        # korzeń bazy (katalog z kolekcjami)
REL    = os.path.join(DB, "religijne")            # główna kolekcja: pieśni religijne (domyślne źródło)
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

# --- notacja: kanoniczna postać POLSKA + konwersja na amerykańską (dla web-toggle) ---
# Zasada (wg ustaleń): WIELKA litera = dur, mała = moll; krzyżyk = „is", bemol = „es".
# Pułapka H/B: międzynarodowe B = polskie H; międzynarodowe Bb = polskie B; polskie samotne „B" = Bb.
# Stąd: „Bm"→„h", „Bb"→„B", a samotne „B" zostaje „B". Krzyżyk „#" jest ZAWSZE międzynarodowy.
_PL_ROOT={  # (litera_C-systemu, rodzaj_akcydencji '', 'is', 'es') → polski zapis duru
    ("C",""):"C",("C","is"):"Cis",("C","es"):"Ces",
    ("D",""):"D",("D","is"):"Dis",("D","es"):"Des",
    ("E",""):"E",("E","is"):"Eis",("E","es"):"Es",
    ("F",""):"F",("F","is"):"Fis",("F","es"):"Fes",
    ("G",""):"G",("G","is"):"Gis",("G","es"):"Ges",
    ("A",""):"A",("A","is"):"Ais",("A","es"):"As",
    ("H",""):"H",("H","is"):"His",("H","es"):"B",
    ("B",""):"B",                       # samotne B = Bb (dur)
}
_PL2US={"C":"C","Cis":"C#","Ces":"Cb","D":"D","Dis":"D#","Des":"Db","E":"E","Eis":"E#","Es":"Eb",
        "F":"F","Fis":"F#","Fes":"Fb","G":"G","Gis":"G#","Ges":"Gb","A":"A","Ais":"A#","As":"Ab",
        "H":"B","His":"B#","B":"Bb"}
_ACCMAP={"#":"is","is":"is","b":"es","es":"es","s":"es"}   # „s" (polski bemol jak Es/As) traktujemy jak „es"
# akcydencja „s" tylko gdy NIE rozpoczyna „sus" (inaczej „Esus4” → błędnie „Es”+„us4”)
_CHORD_RE=re.compile(r"^([A-Ha-h])(is|es|#|b|s(?!us))?(.*)$")

def _parse_chord(tok):
    """Token akordu → (polski_root_durowy, moll?, sufiks) albo None. Rozumie zapis polski i międzynarodowy."""
    m=_CHORD_RE.match(tok.strip())
    if not m: return None
    letter, acc, rest = m.group(1), m.group(2) or "", m.group(3)
    minor = letter.islower()
    intl_minor=False
    if not minor:
        mm=re.match(r"^m(?!aj)(.*)$", rest)     # „m" międzynarodowe (ale nie „maj")
        if mm: minor=True; intl_minor=True; rest=mm.group(1)
    L=letter.upper(); a=_ACCMAP.get(acc, "")
    # międzynarodowe natural-B z minorem = polskie H (B-moll); samotne/duro-B zostaje B (Bb)
    if L=="B" and intl_minor: root="H"
    else: root=_PL_ROOT.get((L,a)) or _PL_ROOT.get((L,""))
    if root is None: return None
    return root, minor, rest

def canon_chord(tok):
    """Dowolny zapis pojedynczego akordu → kanoniczna postać polska (Am→a, C#m7→cis7, C#7→Cis7, Bm7→h7).
    Nie-akord zwraca bez zmian."""
    p=_parse_chord(tok)
    if p is None: return tok
    root, minor, suf = p
    return (root.lower() if minor else root) + suf

def to_american(tok):
    """Kanoniczny polski akord → zapis amerykański (cis7→C#m7, Cis7→C#7, h7→Bm7, B7→Bb7). Dla web-toggle."""
    p=_parse_chord(tok)
    if p is None: return tok
    root, minor, suf = p
    us=_PL2US.get(root, root)
    return (us+"m"+suf) if minor else (us+suf)

_SEQSPLIT=re.compile(r"([/\-])")           # bas po „/" oraz sekwencje łączone „-"
def map_chord_token(tok, fn):
    """Stosuje fn (canon_chord / to_american) do każdego akordu w tokenie, zachowując
    nawiasy, markery (|, /x2), bas po „/" i sekwencje „-". Nie-akordy zwraca bez zmian."""
    t=tok.strip()
    if not t or _MARK.fullmatch(t) or _REP.fullmatch(t) or is_section_label(t) or not is_chord(t): return tok
    pre=""; post=""
    m=re.match(r"^([(\[]*)(.*?)([)\].,;]*)$", t)
    if m: pre,t,post = m.group(1),m.group(2),m.group(3)
    parts=_SEQSPLIT.split(t)               # ['G','/','h'] / ['h','-','A','-','h']
    out="".join(p if p in ("/","-") else fn(p) for p in parts)
    return pre+out+post

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

def _md_files(db, recursive=False):
    """Pliki .md kolekcji (z pominięciem _*.md). recursive=True → także podkatalogi
    (np. kolekcja „18-nadia" z podziałem na polskie/zagraniczne)."""
    pat = os.path.join(db, "**", "*.md") if recursive else os.path.join(db, "*.md")
    files = glob.glob(pat, recursive=recursive)
    return sorted(p for p in files if not os.path.basename(p).startswith("_"))

def load_by_title(db=REL, recursive=False):
    out={}
    for p in _md_files(db, recursive):
        s=parse_md(p); out[s["title"]]=s
    return out

def load_all(db=REL, recursive=False):
    return [parse_md(p) for p in _md_files(db, recursive)]

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

# --- diagramy chwytów (chords.json) ---
def load_chords():
    import json
    with open(os.path.join(SRC, "chords.json"), encoding="utf-8") as f:
        return json.load(f)

def draw_chord_diagram(pdf, x, y, name, frets, cell=4.0):
    """Diagram chwytu. (x,y) = lewy-górny róg bloku. frets: 6 wartości w kolejności
    strun E→e (int / 0 = pusta / 'x' = tłumiona). Okno progów liczone automatycznie
    (obsługuje wojsingi wysoko na gryfie). Zwraca (szerokość, wysokość) bloku."""
    n=6; gw=cell*(n-1)
    fr=[f for f in frets if isinstance(f,int) and f>0]
    if fr:
        lo,hi=min(fr),max(fr)
        top,rows = (1,4) if hi<=4 else (lo, max(4, hi-lo+1))
    else:
        top,rows = 1,4
    rh=cell
    # nazwa
    pdf.set_xy(x-2, y); pdf.set_font("play","B",8.5); pdf.set_text_color(*INK)
    pdf.cell(gw+4, 4, name, align="C")
    gy=y+6.2; my=gy-1.9                    # góra siatki / środek wiersza markerów o-x
    # markery o (pusta) / x (tłumiona) — rysowane kształtami (bez zależności od glifów fontu)
    for i,f in enumerate(frets):
        sx=x+i*cell
        if f=="x":
            pdf.set_draw_color(*GRY); pdf.set_line_width(0.3); d=0.85
            pdf.line(sx-d,my-d,sx+d,my+d); pdf.line(sx-d,my+d,sx+d,my-d)
        elif f==0:
            pdf.set_draw_color(*GRY); pdf.set_line_width(0.25); r=0.85
            pdf.ellipse(sx-r,my-r,2*r,2*r,style="D")
    # siatka
    pdf.set_draw_color(*GRY); pdf.set_line_width(0.2)
    for i in range(n): sx=x+i*cell; pdf.line(sx,gy,sx,gy+rh*rows)
    for r in range(rows+1): yy=gy+rh*r; pdf.line(x,yy,x+gw,yy)
    if top==1:
        pdf.set_line_width(0.8); pdf.line(x,gy,x+gw,gy); pdf.set_line_width(0.2)
    else:
        pdf.set_font("sans","",5.5); pdf.set_text_color(*GRY)
        pdf.set_xy(x+gw+0.4, gy-0.6); pdf.cell(6,3,f"{top}")
    # kropki
    pdf.set_fill_color(*INK)
    for i,f in enumerate(frets):
        if isinstance(f,int) and f>0:
            cyc=gy+rh*((f-top+1)-0.5); cxc=x+i*cell; rad=cell*0.30
            pdf.ellipse(cxc-rad, cyc-rad, rad*2, rad*2, style="F")
    pdf.set_text_color(*INK)
    return gw, (gy+rh*rows)-y

def draw_chord_index(pdf, ML, W, H, intro=True):
    """Renderuje „Indeks akordów" (wojsingi z chords.json, pogrupowane parami dur/moll)
    na bieżącej stronie `pdf`. ML = margines, W/H = wymiary strony. Łamie strony sam."""
    data=load_chords()
    botm = 12 if W < 160 else 15
    if intro:
        pdf.set_x(ML); pdf.set_font("play","B", 18 if W<160 else 24); pdf.set_text_color(*INK)
        pdf.cell(0,12,"Indeks akordów", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(ML); pdf.set_font("sans","",8.2); pdf.set_text_color(*GRY)
        pdf.multi_cell(W-2*ML, 4.2, "Otwartostrunowe / sus wojsingi pogrupowane parami równoległymi dur/moll "
                       "(ten sam burdon pustych strun). Struny E–A–D–G–B–e; kółko = struna pusta, x = tłumiona. "
                       "Pod diagramem funkcja względem tonacji durowej.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2); pdf.set_text_color(*INK)
    COLW = 23 if W < 160 else 26
    ROWH = 31 if W < 160 else 33
    perrow = max(4, int((W-2*ML)//COLW))
    for key, voicings in data["voicings"].items():
        if pdf.get_y()+ROWH+14 > H-botm: pdf.add_page()
        pdf.set_x(ML); pdf.set_font("play","B", 12 if W<160 else 13); pdf.set_text_color(*INK)
        pdf.cell(0,8,key, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        yb=pdf.get_y(); pdf.set_draw_color(*HAIR); pdf.set_line_width(0.2); pdf.line(ML,yb,W-ML,yb); yb+=3
        for i,v in enumerate(voicings):
            col=i%perrow
            if col==0 and i>0: yb+=ROWH
            if col==0 and yb+ROWH>H-botm: pdf.add_page(); yb=pdf.t_margin
            x=ML+2+col*COLW
            draw_chord_diagram(pdf, x, yb, v["name"], v["frets"])
            if v.get("role"):
                pdf.set_xy(x-2, yb+26); pdf.set_font("sans","",6); pdf.set_text_color(*GRY)
                pdf.cell(COLW-4, 3, v["role"], align="C"); pdf.set_text_color(*INK)
        pdf.set_y(yb+ROWH+2)

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
