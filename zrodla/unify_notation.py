# -*- coding: utf-8 -*-
"""Ujednolicenie zapisu chwytów w bazie do kanonicznej notacji POLSKIEJ (canon_chord).

Narzędzie DEWELOPERSKIE. Rewrite dotyka WYŁĄCZNIE tokenów-akordów (pozycje z chord_run) —
tekst pieśni i markery powtórzeń (/bis, /x2) zostają nietknięte. Domyślnie DRY-RUN
(pokazuje zmiany); `--apply` zapisuje pliki. Po zastosowaniu: testy + regeneracja PDF/web."""
import os, re, glob, sys
from common import DB, chord_run, map_chord_token, canon_chord

FENCE = re.compile(r"(```[^\n]*\n)(.*?)(\n```)", re.S)

def unify_body(body):
    out, changes = [], []
    for line in body.split("\n"):
        toks = [t for t in re.split(r"(\s+)", line) if t != ""]
        ns = [i for i, t in enumerate(toks) if t.strip()]
        new = list(toks)
        for i in chord_run(toks, ns):
            c = map_chord_token(toks[i], canon_chord)
            if c != toks[i]:
                changes.append((toks[i], c)); new[i] = c
        out.append("".join(new))
    return "\n".join(out), changes

def main(apply=False):
    total = 0
    for p in sorted(glob.glob(os.path.join(DB, "**", "*.md"), recursive=True)):   # wszystkie kolekcje, też podkatalogi
        if os.path.basename(p).startswith("_"): continue
        txt = open(p, encoding="utf-8").read()
        m = FENCE.search(txt)
        if not m: continue
        newbody, changes = unify_body(m.group(2))
        if changes:
            total += len(changes)
            print(f"  {os.path.basename(p)}: " + ", ".join(f"{a}→{b}" for a, b in changes))
            if apply:
                open(p, "w", encoding="utf-8").write(txt[:m.start()] + m.group(1) + newbody + m.group(3) + txt[m.end():])
    print(("ZASTOSOWANO" if apply else "DRY-RUN (użyj --apply)") + f": {total} zmian")

if __name__ == "__main__":
    main("--apply" in sys.argv)
