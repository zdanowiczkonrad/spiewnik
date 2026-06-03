# -*- coding: utf-8 -*-
# Śpiewnik DLA LUDU — kompaktowy: 2 kolumny, mały font bezszeryfowy, same teksty (bez chwytów).
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from common import INK, GRY, HAIR, fold, strip_chords, load_by_title, add_fonts
from plan_data import SELECTED, EVENT

LGY=(170,170,170)   # „dla ludu" ma odrobinę ciemniejszą szarość niż reszta generatorów

BYALL=load_by_title()
content=[]
for t in SELECTED:
    s=BYALL.get(t)
    if not s or s["stub"]: print("[POMINIĘTO]",t); continue
    content.append(s)
for i,s in enumerate(content,1): s["nr"]=i

# pdf_lud ma własny, kompaktowy nagłówek/stopkę (inna geometria niż SongbookPDF)
class PDF(FPDF):
    chrome=False
    def header(self):
        if not self.chrome or self.page_no()==1: return
        self.set_draw_color(*HAIR); self.set_line_width(0.2)
        self.line(self.l_margin,10.5,self.w-self.r_margin,10.5)
        self.set_xy(self.l_margin,5.5); self.set_font("sans","",7); self.set_text_color(*LGY)
        self.set_char_spacing(1.1); self.cell(0,4,"ŚPIEWNIK DLA LUDU"); self.set_char_spacing(0)
        self.set_xy(self.l_margin,5.5); self.cell(self.w-2*self.l_margin,4,EVENT["header"],align="R")
        self.set_text_color(*INK)
    def footer(self):
        if not self.chrome or self.page_no()==1: return
        self.set_y(-11); self.set_font("play","",8.5); self.set_text_color(*GRY)
        self.cell(0,6,str(self.page_no()),align="C"); self.set_text_color(*INK)

pdf=PDF(format="A4"); pdf.set_margins(14,16,14); pdf.set_auto_page_break(False)
add_fonts(pdf)
ML=14; PW=210-2*ML; GUT=9; COLW=(PW-GUT)/2; XS=[ML, ML+COLW+GUT]; TOP=16.5; BOT=297-13
BS=9.0; LH=4.05; TLH=4.7   # rozmiar tekstu / interlinia / interlinia tytułu

# ---------- OKŁADKA ----------
pdf.chrome=False; pdf.add_page()
pdf.set_draw_color(*INK); pdf.set_line_width(0.4); pdf.rect(10,10,190,277)
pdf.set_y(74)
pdf.set_font("sans","",10); pdf.set_text_color(*GRY); pdf.set_char_spacing(4)
pdf.cell(0,6,EVENT["top"],align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.set_char_spacing(0)
pdf.ln(6)
pdf.set_font("play","B",54); pdf.set_text_color(*INK)
pdf.cell(0,26,"Śpiewnik dla ludu",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
pdf.ln(3); pdf.line(105-22,pdf.get_y(),105+22,pdf.get_y()); pdf.ln(8)
pdf.set_font("play","",15)
pdf.cell(0,9,"teksty pieśni do wspólnego śpiewu",align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
pdf.ln(3); pdf.set_font("sans","",11); pdf.set_text_color(*GRY)
pdf.cell(0,7,EVENT["subtitle"],align="C",new_x=XPos.LMARGIN,new_y=YPos.NEXT)
pdf.set_y(297-38)
pdf.set_font("sans","",8.5); pdf.set_text_color(*GRY); pdf.set_char_spacing(2)
pdf.cell(0,5,f"{len(content)} PIEŚNI · WERSJA KOMPAKTOWA (BEZ CHWYTÓW)",align="C")
pdf.set_char_spacing(0)          # WAŻNE: reset — fpdf2 cofa zmiany char_spacing z header(), więc leak z okładki trzeba wyzerować tutaj
pdf.set_text_color(*INK)

# ---------- silnik kolumn ----------
st={"col":0,"y":TOP}
def new_cols_page():
    pdf.add_page(); st["col"]=0; st["y"]=TOP
def ensure(h):
    if st["y"]+h > BOT:
        if st["col"]==0: st["col"]=1; st["y"]=TOP
        else: new_cols_page()
def wrap(txt,fam,style,size):
    pdf.set_font(fam,style,size)
    txt=txt.rstrip()
    if not txt: return [""]
    words=txt.split(" "); out=[]; cur=""
    for w in words:
        tr=(cur+" "+w) if cur else w
        if cur=="" or pdf.get_string_width(tr)<=COLW: cur=tr
        else: out.append(cur); cur=w
    if cur: out.append(cur)
    return out
def put(txt,fam,style,size,h,color=INK):
    ensure(h)
    pdf.set_xy(XS[st["col"]], st["y"])
    pdf.set_font(fam,style,size); pdf.set_text_color(*color)
    pdf.cell(COLW,h,txt,new_x=XPos.LMARGIN,new_y=YPos.TOP)
    st["y"]+=h

def song(s):
    tlines=wrap(f"{s['nr']}.  {s['title']}","play","B",10.5)
    # nie osieracaj tytułu: zapewnij tytuł + ~2 linijki tekstu
    ensure(len(tlines)*TLH + 2*LH + 1.5)
    for tl in tlines: put(tl,"play","B",10.5,TLH,INK)
    st["y"]+=0.8
    pdf.set_text_color(*INK)
    for raw in strip_chords(s["body"]) or [" "]:
        if raw.strip()=="":
            st["y"]+=LH*0.5; continue
        for piece in wrap(raw,"sans","",BS):
            put(piece,"sans","",BS,LH,INK)
    st["y"]+=3.2

# ---------- strona z pieśniami ----------
pdf.chrome=True; pdf.add_page()
pdf.set_xy(ML,TOP); pdf.set_font("play","B",20); pdf.set_text_color(*INK)
pdf.cell(0,10,"Pieśni"); st["y"]=TOP+13
for s in content: song(s)

out=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 f"Śpiewnik dla ludu – {EVENT['short']}.pdf")
pdf.output(out)
print("OK:",out,"| stron:",pdf.page_no(),"| pieśni:",len(content))
