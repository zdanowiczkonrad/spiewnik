# -*- coding: utf-8 -*-
# Plan oprawy DLA GITARZYSTY — sama rozpiska do druku: dzień, czytania, myśl przewodnia
# i pieśni (bez opisów), bez okładki i bez nagłówków/stopki. Adnotacja przy pieśni:
# numer · strona w śpiewniku z chwytami · tonacja.
import os, re
from fpdf.enums import XPos, YPos
from common import INK, GRY, LGY, HAIR, add_fonts, SongbookPDF
from plan_data import PLAN, EVENT
from pdf import BYT, pages   # numeracja i strony ze śpiewnika z chwytami (ten sam skład)

ML=16; PW=210-2*ML
_SEP=re.compile(r"\s*(→|·)\s*")   # separatory pieśni w slocie planu

pdf=SongbookPDF(format="A4")      # chrome=False → bez żywej paginy i numeru strony
pdf.set_margins(ML,16,ML); pdf.set_auto_page_break(True,12)
add_fonts(pdf); pdf.add_page()
def cspace(v): pdf.set_char_spacing(v)

# pojedyncza linijka tytułowa (to nie okładka)
pdf.set_x(ML); pdf.set_font("semi","",8); pdf.set_text_color(*GRY); cspace(2)
pdf.cell(0,5,("Oprawa muzyczna · "+EVENT["dates"]).upper(),new_x=XPos.LMARGIN,new_y=YPos.NEXT)
cspace(0); pdf.set_text_color(*INK)
y=pdf.get_y()+1; pdf.set_draw_color(*INK); pdf.set_line_width(0.3); pdf.line(ML,y,210-ML,y); pdf.ln(3)

def ann_for(part):
    s=BYT.get(part)
    if not s: return ""
    a=f"  {s['nr']} · s. {pages[s['title']]}"
    if s.get("key"): a+=f" · {s['key']}"
    return a

def piesn_line(piesn,ytop,x):
    # tytuły pieśni + szara adnotacja „nr · s. strona · tonacja"; zawijanie do kolumny x
    pdf.set_left_margin(x); pdf.set_xy(x,ytop)
    for part in _SEP.split(piesn):
        pdf.set_font("play","B",10); pdf.set_text_color(*INK)
        if part in ("→","·"): pdf.write(4.9,"  "+part+"  "); continue
        ann=ann_for(part)
        w=pdf.get_string_width(part)
        if ann:
            pdf.set_font("sans","",6.8); w+=pdf.get_string_width(ann); pdf.set_font("play","B",10)
        # tytuł+adnotacja trzymamy razem — łamiemy linię przed segmentem, nie w środku słowa
        if pdf.get_x()>x and pdf.get_x()+w>210-ML: pdf.ln(4.9)
        pdf.write(4.9,part)
        if ann:
            pdf.set_font("sans","",6.8); pdf.set_text_color(*GRY); pdf.write(4.9,ann)
    pdf.ln(4.9); pdf.set_left_margin(ML); pdf.set_x(ML); pdf.set_text_color(*INK)

for dzien,uroczystosc,charakter,czyt,mysl,sloty in PLAN:
    if pdf.get_y()>250: pdf.add_page()
    pdf.ln(2.5)
    pdf.set_x(ML); pdf.set_font("play","B",13); pdf.set_text_color(*INK)
    pdf.cell(0,7,dzien,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.set_x(ML); pdf.set_font("play","",9.5); pdf.set_text_color(70,70,70)
    pdf.multi_cell(PW,4.4,uroczystosc+" · "+charakter,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    y=pdf.get_y()+0.8; pdf.set_draw_color(*HAIR); pdf.set_line_width(0.2); pdf.line(ML,y,210-ML,y); pdf.ln(2.2)
    pdf.set_x(ML); pdf.set_font("sans","",7.6); pdf.set_text_color(90,90,90)
    pdf.multi_cell(PW,3.9,czyt,new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(0.8)
    pdf.set_x(ML); pdf.set_font("play","",9); pdf.set_text_color(30,30,30)
    pdf.multi_cell(PW,4.3,mysl,new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(1.6)
    for rola,piesn,opis in sloty:   # opis pomijany — sama rozpiska
        if pdf.get_y()>275: pdf.add_page()
        ytop=pdf.get_y()
        pdf.set_x(ML); pdf.set_font("semi","",6.8); pdf.set_text_color(*GRY); cspace(0.5)
        pdf.cell(26,4.9,rola.upper(),new_x=XPos.RIGHT,new_y=YPos.TOP); cspace(0)
        piesn_line(piesn,ytop,ML+26)

pdf.ln(2)
pdf.set_x(ML); pdf.set_font("semi","",6.8); pdf.set_text_color(*GRY); cspace(0.5)
pdf.cell(0,4.9,"NA ZAKOŃCZENIE KAŻDEGO DNIA (WIECZÓR)",new_x=XPos.LMARGIN,new_y=YPos.NEXT); cspace(0)
piesn_line("Apel Jasnogórski",pdf.get_y(),ML)
pdf.ln(2)
pdf.set_x(ML); pdf.set_font("sans","",7); pdf.set_text_color(*LGY)
pdf.multi_cell(PW,3.8,"Numery i strony odsyłają do pliku „Śpiewnik wyjazd – "+EVENT["short"]+"” (wersja z chwytami).",
               new_x=XPos.LMARGIN,new_y=YPos.NEXT)

out=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 f"Oprawa dla gitarzysty – {EVENT['short']}.pdf")
pdf.output(out)
print("OK:",out,"| stron:",pdf.page_no())
