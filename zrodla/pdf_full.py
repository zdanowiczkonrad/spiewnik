# -*- coding: utf-8 -*-
# Pełny śpiewnik (wszystkie pieśni z bazy). Flagi: --a5 (kieszonkowy), --plain (same teksty, bez chwytów).
import os, re, sys
from fpdf.enums import XPos, YPos
from common import (INK, GRY, LGY, HAIR, CHORDCOL, fold, fmt_key, chord_run,
                    strip_chords, load_all, add_fonts, SongbookPDF, ROOT, BUILD_VERSION,
                    draw_site_qr, draw_chord_index)
from plan_data import EVENT

# ---------- wczytanie bazy z plików MD ----------
songs=load_all()
content=sorted([s for s in songs if not s["stub"]], key=lambda s: fold(s["title"]))
stubs  =sorted([s for s in songs if s["stub"]],     key=lambda s: fold(s["title"]))
for i,s in enumerate(content,1): s["nr"]=i
N=len(content)

# ---------- PDF ----------
class PDF(SongbookPDF):
    left_label="ŚPIEWNIK · BAZA PIEŚNI"; right_label=EVENT["header"]

A5 = "--a5" in sys.argv
PLAIN = "--plain" in sys.argv          # bez chwytów (same teksty, font bezszeryfowy)
W,H = (148,210) if A5 else (210,297)
ML  = 12 if A5 else 18
TOPM= 14 if A5 else 18
TITLE_SZ = 14 if A5 else 17     # rozmiar tytułu pieśni
def new_pdf():
    pdf=PDF(format=("A5" if A5 else "A4")); pdf.set_margins(ML,TOPM,ML); pdf.set_auto_page_break(True, 12 if A5 else 15)
    add_fonts(pdf); return pdf
PW=W-2*ML

# --- rysowanie linii pieśni z kolorowaniem chwytów (końcowy ciąg tokenów-akordów) ---
def draw_body_line(pdf, raw, bs, lh):
    toks=[t for t in re.split(r"(\s+)", raw) if t!=""]
    ns=[i for i,t in enumerate(toks) if t.strip()]
    chord=chord_run(toks, ns)                    # akordy: końcowy ciąg tokenów lub linia-legenda
    pdf.set_x(ML)
    for i,t in enumerate(toks):
        if i in chord: pdf.set_font("mono","B",bs); pdf.set_text_color(*CHORDCOL)
        else:          pdf.set_font("mono","",bs); pdf.set_text_color(*INK)
        pdf.cell(pdf.get_string_width(t), lh, t, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_text_color(*INK); pdf.ln(lh); pdf.set_x(ML)

def label(pdf,txt,size=8,color=GRY,track=1.6):
    pdf.set_font("sans","",size); pdf.set_text_color(*color); pdf.set_char_spacing(track)
    pdf.set_x(ML); pdf.cell(0,size*0.5,txt.upper(),new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_char_spacing(0); pdf.set_text_color(*INK)

# ---------- okładka ----------
def cover(pdf):
    pdf.chrome=False; pdf.add_page()
    pdf.set_draw_color(*INK); pdf.set_line_width(0.4)
    pdf.rect(8,8, W-16, H-16)              # cienka ramka
    pdf.set_y(48 if A5 else 70)
    pdf.set_font("sans","",8 if A5 else 10); pdf.set_text_color(*GRY); pdf.set_char_spacing(3 if A5 else 4)
    pdf.cell(0,6,("ŚPIEWNIK RELIGIJNY — TEKSTY" if PLAIN else "ŚPIEWNIK RELIGIJNY NA GITARĘ"),
             align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_char_spacing(0)
    pdf.ln(4 if A5 else 6)
    pdf.set_font("play","B",40 if A5 else 64); pdf.set_text_color(*INK)
    pdf.cell(0,(20 if A5 else 30),"Śpiewnik",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.ln(3 if A5 else 4)
    cx=W/2; hw=16 if A5 else 22
    pdf.set_draw_color(*INK); pdf.set_line_width(0.3); pdf.line(cx-hw,pdf.get_y(),cx+hw,pdf.get_y())
    pdf.ln(8 if A5 else 11)
    pdf.set_font("sans","",10 if A5 else 11); pdf.set_text_color(*GRY)
    pdf.cell(0,7,EVENT["short"],align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    draw_site_qr(pdf, W/2, (116 if A5 else 168), (22 if A5 else 30))   # QR do żywej strony
    # stopka okładki
    pdf.set_y(H-(28 if A5 else 40))
    pdf.set_font("sans","",7 if A5 else 8.5); pdf.set_text_color(*GRY); pdf.set_char_spacing(1.4 if A5 else 2)
    pdf.cell(0,5,(f"{N} PIEŚNI" if PLAIN else
                  (f"{N} PIEŚNI · NOTACJA POLSKA" if A5 else
                   f"{N} PIEŚNI · NOTACJA POLSKA (h = H-moll, małe litery = molowe)")),
             align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_char_spacing(0)
    pdf.cell(0,5,"Źródła różne, zebranie i opracowanie: Konrad Zdanowicz 2026",align="C",
             new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    if BUILD_VERSION:
        pdf.ln(2); pdf.set_font("sans","",6.5 if A5 else 7); pdf.set_text_color(*LGY); pdf.set_char_spacing(1)
        pdf.cell(0,4,("wersja "+BUILD_VERSION).upper(),align="C"); pdf.set_char_spacing(0)
    pdf.set_text_color(*INK)

# ---------- pomiar wysokości pieśni ----------
def song_metrics(pdf,s):
    if PLAIN:
        lines=strip_chords(s["body"]) or [" "]
        pdf.set_font("sans","",11)
        maxw=max((pdf.get_string_width(l) for l in lines), default=0.0)
        CAP=11.5 if A5 else 11.0
        bs=CAP if maxw<=0 else max(8.5, min(CAP, 11.0*PW/maxw))
        lh=bs*0.52
    else:
        lines=s["body"].split("\n")
        pdf.set_font("mono","",10)
        maxw=max((pdf.get_string_width(l) for l in lines), default=0.0)
        CAP=10.5 if A5 else 9.5                                   # na A5 pozwól na większy font
        bs=CAP if maxw<=0 else max(6.0, min(CAP, 10.0*PW/maxw))   # dobierz, by najdłuższa linia mieściła się w szerokości
        lh=bs*0.46
    head=7+4.5+3.5+3   # tytuł + meta + rule + odstęp
    return lines,bs,lh, head+lh*len(lines)+7

def draw_letter(pdf,letter):
    if pdf.get_y()+22 > H-20: pdf.add_page()
    pdf.ln(3)
    pdf.set_font("play","B",24); pdf.set_text_color(*LGY)
    pdf.set_x(ML); pdf.cell(12,12,letter,new_x=XPos.RIGHT,new_y=YPos.TOP)
    y=pdf.get_y()+9
    pdf.set_draw_color(*HAIR); pdf.set_line_width(0.2); pdf.line(ML+13,y,W-ML,y)
    pdf.set_text_color(*INK); pdf.set_y(pdf.get_y()+14)

def draw_song(pdf,s):
    lines,bs,lh,need=song_metrics(pdf,s)
    # tytuł + pasek meta razem nie powinny się rozjechać u dołu
    if pdf.get_y()+min(need, 70) > H-18 and pdf.get_y()>40:
        pdf.add_page()
    # numer w czarnym kwadracie (biały font) + tytuł
    sq = 6.0 if A5 else 6.5; gap = 3
    y0 = pdf.get_y()
    pdf.set_fill_color(*INK); pdf.rect(ML, y0+1.0, sq, sq, style="F")
    pdf.set_xy(ML, y0+1.0); pdf.set_font("sans","B", 8.5 if A5 else 9); pdf.set_text_color(255,255,255)
    pdf.cell(sq, sq, str(s['nr']), align="C")
    pdf.set_text_color(*INK)
    pdf.set_xy(ML+sq+gap, y0); pdf.set_font("play","B",TITLE_SZ)
    pdf.multi_cell(PW-sq-gap,TITLE_SZ*0.47,s["title"],new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    # meta (bez tonacji w wersji bez chwytów)
    meta=[]
    if s["section"]: meta.append(s["section"])
    if s["key"] and not PLAIN: meta.append("tonacja "+fmt_key(s["key"]))
    if meta:
        pdf.set_x(ML+sq+gap); pdf.set_font("sans","",7.8); pdf.set_text_color(*GRY); pdf.set_char_spacing(0.8)
        pdf.multi_cell(PW-sq-gap,4,"  ·  ".join(meta).upper(),new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        pdf.set_char_spacing(0)
    pdf.ln(1.4)
    y=pdf.get_y(); pdf.set_draw_color(*INK); pdf.set_line_width(0.3); pdf.line(ML,y,W-ML,y)
    pdf.ln(2.6)
    pdf.set_text_color(*INK)
    if PLAIN:
        pdf.set_font("sans","",bs)
        for l in lines:
            if pdf.get_y()+lh>H-16: pdf.add_page()
            pdf.set_x(ML); pdf.multi_cell(PW,lh,l if l.strip() else " ",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    else:
        for l in lines:
            if pdf.get_y()+lh>H-16: pdf.add_page()
            draw_body_line(pdf, l, bs, lh)
    pdf.ln(7)

def render_songs(pdf):
    pdf.chrome=True; pdf.add_page()
    starts={}; cur=""
    for s in content:
        L=fold(s["title"])[0:1].upper()
        if L!=cur:
            cur=L; draw_letter(pdf,L)
        starts[s["nr"]]=pdf.page_no()
        draw_song(pdf,s)
    return starts

# ---------- spis treści ----------
COLS=1 if A5 else 2
PER_COL=30 if A5 else 44
def n_toc_pages():
    import math
    return max(1, math.ceil(N/(PER_COL*COLS)))

def draw_toc(pdf, starts, npages):
    pdf.chrome=True
    colw=(PW-8)/COLS
    idx=0; entries=content
    for pg in range(npages):
        pdf.add_page()
        if pg==0:
            pdf.set_font("play","B",18 if A5 else 26); pdf.set_text_color(*INK); pdf.set_x(ML)
            pdf.cell(0,14,"Spis pieśni",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
            pdf.ln(2); top=pdf.get_y()
        else:
            pdf.ln(6); top=pdf.get_y()
        for c in range(COLS):
            x=ML+c*(colw+8); y=top
            for _ in range(PER_COL):
                if idx>=len(entries): break
                s=entries[idx]; idx+=1
                pdf.set_xy(x,y)
                pdf.set_font("sans","",6.8); pdf.set_text_color(*LGY)
                pdf.cell(7,5,f"{s['nr']:02d}")
                pdf.set_font("sans","",9); pdf.set_text_color(*INK)
                title=s["title"]
                maxw=colw-7-7
                while pdf.get_string_width(title)>maxw and len(title)>4:
                    title=title[:-2]
                pdf.set_xy(x+7,y); pdf.cell(maxw,5,title)
                pdf.set_font("sans","",8); pdf.set_text_color(*GRY)
                pdf.set_xy(x+colw-7,y); pdf.cell(7,5,str(starts[s["nr"]]),align="R")
                y+=5.0
        if pg==npages-1 and stubs:
            yb=top+PER_COL*5.0+8
            pdf.set_xy(ML,yb); pdf.set_draw_color(*HAIR); pdf.set_line_width(0.2)
            pdf.line(ML,yb,W-ML,yb); pdf.ln(3)
            pdf.set_x(ML); pdf.set_font("semi","",7.5); pdf.set_text_color(*GRY); pdf.set_char_spacing(1.4)
            pdf.cell(0,5,"DO UZUPEŁNIENIA — poza źródłami z chwytami",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
            pdf.set_char_spacing(0); pdf.set_x(ML)
            pdf.set_font("sans","",8.5); pdf.set_text_color(*LGY)
            pdf.multi_cell(PW,4.6," · ".join(x["title"] for x in stubs),new_x=XPos.LMARGIN,new_y=YPos.NEXT)
            pdf.set_text_color(*INK)

# ---------- przebieg dwufazowy (numery stron) ----------
ntoc=n_toc_pages()
# pomiar
m=new_pdf(); m.chrome=False
for _ in range(1+ntoc): m.add_page()      # cover + toc placeholdery
starts=render_songs(m)
def add_note_pages(pdf, n=8):
    gap = 8.5
    for i in range(n):
        pdf.chrome=True; pdf.add_page()
        y=pdf.t_margin+2
        if i==0:
            pdf.set_font("play","B",16 if A5 else 22); pdf.set_text_color(*INK); pdf.set_x(ML)
            pdf.cell(0,12,"Notatki",new_x=XPos.LMARGIN,new_y=YPos.NEXT); y=pdf.get_y()+4
        pdf.set_draw_color(*HAIR); pdf.set_line_width(0.15)
        while y < H-16:
            pdf.line(ML, y, W-ML, y); y+=gap

# właściwy
pdf=new_pdf()
cover(pdf)
draw_toc(pdf, starts, ntoc)
starts2=render_songs(pdf)
assert starts==starts2, ("rozjazd paginacji", starts, starts2)
if not PLAIN:
    pdf.chrome=True; pdf.add_page()
    draw_chord_index(pdf, ML, W, H)     # załącznik „Indeks akordów" — tylko wersja z chwytami
    add_note_pages(pdf, 8)              # 8 stron na notatki (linie)

base = "Śpiewnik pełny – teksty" if PLAIN else "Śpiewnik pełny – chwyty"
out=os.path.join(ROOT, base + (" (A5)" if A5 else "") + ".pdf")
pdf.output(out)
print("OK:",out,"| stron:",pdf.page_no(),"| pieśni:",N,"| stuby:",len(stubs),"| spis stron:",ntoc,"| plain:",PLAIN)

# raport: pieśni, w których font spadł poniżej progu (najdłuższa linia za szeroka).
# Sygnał, że warto przerzucić chwyty „nad linijkę” zamiast trzymać kolumnę na końcu wersu.
TIGHT = 8.5 if PLAIN else 7.0
tight=[]
for s in content:
    lines,bs,_,_=song_metrics(pdf,s)
    if bs < TIGHT:
        pdf.set_font("sans" if PLAIN else "mono","",10)
        longest=max(lines, key=pdf.get_string_width).strip()
        tight.append((bs,s["title"],longest))
if tight:
    print(f"[UWAGA] mały font (< {TIGHT}) w {len(tight)} pieśniach — rozważ przerzucenie chwytów „nad linijkę”:")
    for bs,t,l in sorted(tight):
        print(f"   • {t} (font {bs:.1f}) — najdłuższa: {l[:64]}")
