# -*- coding: utf-8 -*-
# Śpiewnik wyjazdowy — WERSJA BEZ CHWYTÓW (same teksty, czcionka bezszeryfowa Instrument Sans).
# Porządek nabożeństw pokazuje przy każdej pieśni jej numer i stronę w śpiewniku —
# strony znane są dopiero po składzie, więc budujemy PDF wielokrotnie (do punktu stałego).
import os, re
from fpdf.enums import XPos, YPos
from common import (INK, GRY, LGY, HAIR, fold, strip_chords, parse_md,
                    load_by_title, add_fonts, SongbookPDF)
from plan_data import SELECTED, PLAN, EVENT

BYALL=load_by_title()
content=[]
for t in SELECTED:
    s=BYALL.get(t)
    if not s or s["stub"]: print("[POMINIĘTO]",t); continue
    content.append(s)
for i,s in enumerate(content,1): s["nr"]=i
BYT={s["title"]:s for s in content}

class PDF(SongbookPDF):
    left_label="ŚPIEWNIK · TEKSTY"; right_label=EVENT["header"]

ML=18; PW=210-2*ML
_SEP=re.compile(r"\s*(→|·)\s*")   # separatory pieśni w slocie planu

def build(pages):
    """Jeden przebieg składu. `pages`: tytuł → strona (z poprzedniego przebiegu).
    Zwraca (pdf, zmierzone strony pieśni)."""
    song_pages={}
    pdf=PDF(format="A4"); pdf.set_margins(18,18,18); pdf.set_auto_page_break(True,15)
    add_fonts(pdf)
    def cspace(v): pdf.set_char_spacing(v)

    # ---------- OKŁADKA ----------
    pdf.chrome=False; pdf.add_page()
    pdf.set_draw_color(*INK); pdf.set_line_width(0.4); pdf.rect(10,10,190,277)
    pdf.set_y(64)
    pdf.set_font("sans","",10); pdf.set_text_color(*GRY); cspace(4)
    pdf.cell(0,6,EVENT["top"],align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT); cspace(0)
    pdf.ln(6)
    pdf.set_font("play","B",58); pdf.set_text_color(*INK)
    pdf.cell(0,28,"Śpiewnik",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.ln(3); pdf.line(105-22,pdf.get_y(),105+22,pdf.get_y()); pdf.ln(8)
    pdf.set_font("play","",16)
    pdf.cell(0,9,"teksty pieśni — wersja bez chwytów",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.ln(3); pdf.set_font("sans","",11); pdf.set_text_color(*GRY)
    pdf.cell(0,7,EVENT["subtitle"],align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_y(297-44)
    pdf.set_font("sans","",8.5); pdf.set_text_color(*GRY); cspace(2)
    pdf.cell(0,5,"PROWADZENIE MUZYCZNE: KONRAD · WYZNANIE RZYMSKOKATOLICKIE",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    cspace(0)
    pdf.cell(0,5,f"{len(content)} pieśni — teksty do wspólnego śpiewu",align="C")
    pdf.set_text_color(*INK)

    # ---------- PORZĄDEK NABOŻEŃSTW ----------
    pdf.chrome=True; pdf.add_page()
    pdf.set_font("play","B",26); pdf.set_text_color(*INK); pdf.set_x(ML)
    pdf.cell(0,14,"Porządek nabożeństw",new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(2)
    def lab(txt,size=7.5,col=GRY,track=1.6,w=0,x=ML,h=4.6,nl=True):
        pdf.set_x(x); pdf.set_font("semi","",size); pdf.set_text_color(*col); cspace(track)
        pdf.cell(w,h,txt.upper(), new_x=XPos.LMARGIN if nl else XPos.RIGHT, new_y=YPos.NEXT if nl else YPos.TOP)
        cspace(0); pdf.set_text_color(*INK)
    def piesn_line(piesn,ytop,x):
        # tytuły pieśni + szara adnotacja „nr · s. strona"; zawijanie wyrównane do kolumny x
        pdf.set_left_margin(x); pdf.set_xy(x,ytop)
        for part in _SEP.split(piesn):
            pdf.set_font("play","B",10.5); pdf.set_text_color(*INK)
            if part in ("→","·"): pdf.write(5.2,"  "+part+"  "); continue
            s=BYT.get(part)
            ann=f"  {s['nr']} · s. {pages.get(part,0)}" if s else ""
            w=pdf.get_string_width(part)
            if ann:
                pdf.set_font("sans","",7.3); w+=pdf.get_string_width(ann); pdf.set_font("play","B",10.5)
            # tytuł+adnotacja trzymamy razem — łamiemy linię przed segmentem, nie w środku słowa
            if pdf.get_x()>x and pdf.get_x()+w>210-ML: pdf.ln(5.2)
            pdf.write(5.2,part)
            if s:
                pdf.set_font("sans","",7.3); pdf.set_text_color(*GRY); pdf.write(5.2,ann)
        pdf.ln(5.2); pdf.set_left_margin(ML); pdf.set_x(ML); pdf.set_text_color(*INK)
    for dzien,uroczystosc,charakter,czyt,mysl,sloty in PLAN:
        if pdf.get_y()>232: pdf.add_page()
        pdf.ln(2)
        pdf.set_x(ML); pdf.set_font("play","B",15); pdf.set_text_color(*INK)
        pdf.cell(0,8,dzien,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        pdf.set_x(ML); pdf.set_font("play","",11.5); pdf.set_text_color(40,40,40)
        pdf.multi_cell(PW,5.4,uroczystosc,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        pdf.ln(0.6); lab(charakter, size=7.5, col=GRY, track=1.8)
        y=pdf.get_y()+0.5; pdf.set_draw_color(*HAIR); pdf.set_line_width(0.2); pdf.line(ML,y,210-ML,y); pdf.ln(2.5)
        lab("Czytania", size=7, col=LGY, track=1.6)
        pdf.set_x(ML); pdf.set_font("sans","",8.4); pdf.set_text_color(55,55,55)
        pdf.multi_cell(PW,4.4,czyt,new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(1.2)
        lab("Myśl przewodnia", size=7, col=LGY, track=1.6)
        pdf.set_x(ML); pdf.set_font("play","",10); pdf.set_text_color(30,30,30)
        pdf.multi_cell(PW,4.8,mysl,new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(2)
        for rola,piesn,opis in sloty:
            if pdf.get_y()>250: pdf.add_page()
            ytop=pdf.get_y()
            lab(rola, size=7.3, col=GRY, track=0.6, w=34, x=ML, h=5.2, nl=False)
            piesn_line(piesn,ytop,ML+34)
            pdf.set_x(ML+34); pdf.set_font("sans","",8.2); pdf.set_text_color(*GRY)
            pdf.multi_cell(PW-34,4.1,opis,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
            pdf.set_text_color(*INK); pdf.ln(1.6)
        pdf.ln(3)
    if pdf.get_y()>250: pdf.add_page()
    lab("Na zakończenie każdego dnia (wieczór)", size=7, col=LGY, track=1.4)
    piesn_line("Apel Jasnogórski",pdf.get_y(),ML)

    # ---------- PIEŚNI (teksty, bezszeryfowo) ----------
    def draw_letter(letter):
        if pdf.get_y()+22>297-20: pdf.add_page()
        pdf.ln(3); pdf.set_font("play","B",24); pdf.set_text_color(*LGY)
        pdf.set_x(ML); pdf.cell(12,12,letter,new_x=XPos.RIGHT,new_y=YPos.TOP)
        y=pdf.get_y()+9; pdf.set_draw_color(*HAIR); pdf.set_line_width(0.2); pdf.line(ML+13,y,210-ML,y)
        pdf.set_text_color(*INK); pdf.set_y(pdf.get_y()+14)

    def draw_song(s):
        lines=strip_chords(s["body"]) or [" "]
        pdf.set_font("sans","",11)
        maxw=max((pdf.get_string_width(l) for l in lines), default=0.0)
        bs=11.0 if maxw<=0 else max(9.0, min(11.0, 11.0*PW/maxw))
        lh=bs*0.52
        need=16+lh*len(lines)+8
        if pdf.get_y()+min(need,70)>297-18 and pdf.get_y()>40: pdf.add_page()
        song_pages[s["title"]]=pdf.page_no()
        sq=6.5; gap=3; y0=pdf.get_y()
        pdf.set_fill_color(*INK); pdf.rect(ML,y0+1.0,sq,sq,style="F")
        pdf.set_xy(ML,y0+1.0); pdf.set_font("sans","B",9); pdf.set_text_color(255,255,255)
        pdf.cell(sq,sq,str(s['nr']),align="C"); pdf.set_text_color(*INK)
        pdf.set_xy(ML+sq+gap,y0); pdf.set_font("play","B",17)
        pdf.multi_cell(PW-sq-gap,8,s["title"],new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        if s.get("section"):
            pdf.set_x(ML+sq+gap); pdf.set_font("sans","",7.8); pdf.set_text_color(*GRY); cspace(0.8)
            pdf.multi_cell(PW-sq-gap,4,s["section"].upper(),new_x=XPos.LMARGIN,new_y=YPos.NEXT); cspace(0)
        pdf.ln(1.4); y=pdf.get_y(); pdf.set_draw_color(*INK); pdf.set_line_width(0.3); pdf.line(ML,y,210-ML,y); pdf.ln(2.6)
        pdf.set_text_color(*INK); pdf.set_font("sans","",bs)
        for l in lines:
            if pdf.get_y()+lh>297-16: pdf.add_page()
            pdf.set_x(ML); pdf.multi_cell(PW,lh,l if l.strip() else " ",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        pdf.ln(7)

    pdf.add_page()
    pdf.set_font("play","B",26); pdf.set_text_color(*INK); pdf.set_x(ML)
    pdf.cell(0,14,"Pieśni",new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(2)
    cur=""
    for s in content:
        L="—" if s["title"].startswith("Części") else fold(s["title"])[0:1].upper()
        if L!=cur: cur=L; draw_letter(L)
        draw_song(s)
    return pdf,song_pages

pages={}
for _ in range(4):                       # zwykle 2 przebiegi; pętla do punktu stałego
    pdf,newpages=build(pages)
    if newpages==pages: break
    pages=newpages

out=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 f"Śpiewnik wyjazd – {EVENT['short']} (bez chwytów).pdf")
pdf.output(out)
print("OK:",out,"| stron:",pdf.page_no(),"| pieśni:",len(content))
for s in content: print(f"{s['nr']:>2}. {s['title']} — s. {pages[s['title']]}")
