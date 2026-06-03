# -*- coding: utf-8 -*-
"""Smoke test: każdy generator uruchamia się bez błędu i tworzy poprawny, niepusty PDF."""
import os, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "zrodla")

CASES = [
    (["pdf.py"],                 "Śpiewnik wyjazd – Boże Ciało 2026.pdf"),
    (["pdf_plain.py"],           "Śpiewnik wyjazd – Boże Ciało 2026 (bez chwytów).pdf"),
    (["pdf_lud.py"],             "Śpiewnik dla ludu – Boże Ciało 2026.pdf"),
    (["pdf_full.py"],            "Śpiewnik pełny – chwyty.pdf"),
    (["pdf_full.py", "--a5"],    "Śpiewnik pełny – chwyty (A5).pdf"),
    (["pdf_full.py", "--plain"], "Śpiewnik pełny – teksty.pdf"),
    (["pdf_full.py", "--a5", "--plain"], "Śpiewnik pełny – teksty (A5).pdf"),
]


@pytest.mark.parametrize("argv,outfile", CASES, ids=[" ".join(c[0]) for c in CASES])
def test_generator_buduje_poprawny_pdf(argv, outfile):
    r = subprocess.run([sys.executable, *argv], cwd=SRC, capture_output=True, text=True)
    assert r.returncode == 0, f"generator zwrócił błąd:\n{r.stderr}"
    assert "OK:" in r.stdout, f"brak potwierdzenia OK:\n{r.stdout}\n{r.stderr}"
    assert "[POMINIĘTO" not in r.stdout, f"pominięto pieśń z SELECTED:\n{r.stdout}"
    path = os.path.join(ROOT, outfile)
    assert os.path.exists(path), f"nie powstał plik: {outfile}"
    with open(path, "rb") as f:
        head = f.read(5)
    assert head.startswith(b"%PDF"), "plik nie jest PDF-em"
    assert os.path.getsize(path) > 5000, "PDF podejrzanie mały"
