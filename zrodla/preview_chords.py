# -*- coding: utf-8 -*-
"""Podgląd „Indeksu akordów" (chords.json) jako osobny PDF — do weryfikacji kształtów.
Używa wspólnego renderera draw_chord_index (ten sam co załącznik w pdf_full)."""
import os
from common import draw_chord_index, add_fonts, SongbookPDF, ROOT

pdf = SongbookPDF(format="A4"); pdf.set_margins(16, 16, 16); pdf.set_auto_page_break(True, 15)
add_fonts(pdf); pdf.add_page()
draw_chord_index(pdf, 16, 210, 297)

out = os.path.join(ROOT, "_podglad_akordy.pdf")
pdf.output(out)
print("OK:", out)
