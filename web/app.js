/* Śpiewnik — logika strony (vanilla JS). Dane: window.SONGS (z site.py). */
(function () {
  "use strict";
  var SONGS = window.SONGS || [];
  var byNr = {};
  SONGS.forEach(function (s) { byNr[s.nr] = s; });

  // wyszukiwanie nieczułe na wielkość liter i polskie znaki (ł→l, NFD bez znaków diakr.)
  function fold(s) {
    return (s || "").replace(/ł/g, "l").replace(/Ł/g, "L")
      .normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  var $ = function (sel) { return document.querySelector(sel); };
  var list = $("#list"), q = $("#q"), filtersEl = $("#filters");
  var songview = $("#songview"), songEl = $("#song");
  var activeCat = "";

  // ---- filtry kategorii ----
  var cats = [];
  SONGS.forEach(function (s) { if (s.section && cats.indexOf(s.section) < 0) cats.push(s.section); });
  function makeChip(label, val) {
    var b = document.createElement("button");
    b.className = "chip"; b.textContent = label;
    b.setAttribute("aria-pressed", val === activeCat ? "true" : "false");
    b.addEventListener("click", function () { activeCat = val; renderFilters(); render(); });
    return b;
  }
  function renderFilters() {
    filtersEl.innerHTML = "";
    filtersEl.appendChild(makeChip("Wszystkie", ""));
    cats.forEach(function (c) { filtersEl.appendChild(makeChip(c, c)); });
  }

  // ---- lista ----
  function render() {
    var query = fold(q.value.trim());
    var isNum = /^\d+$/.test(q.value.trim());
    var n = isNum ? parseInt(q.value.trim(), 10) : null;
    list.innerHTML = "";
    var shown = 0;
    SONGS.forEach(function (s) {
      if (activeCat && s.section !== activeCat) return;
      var match = !query
        || s.q.indexOf(query) >= 0
        || (isNum && s.nr === n)
        || (isNum && String(s.nr).indexOf(q.value.trim()) === 0);
      if (!match) return;
      shown++;
      var b = document.createElement("button");
      b.className = "item";
      b.innerHTML = '<span class="num">' + s.nr + '</span>'
        + '<span class="t">' + escapeHtml(s.title)
        + (s.section ? '<span class="s">' + escapeHtml(s.section) + '</span>' : '') + '</span>';
      b.addEventListener("click", function () { location.hash = "#" + s.nr; });
      list.appendChild(b);
    });
    if (!shown) { var e = document.createElement("div"); e.className = "empty"; e.textContent = "Brak wyników"; list.appendChild(e); }
  }

  function escapeHtml(t) {
    return t.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  // ---- widok pieśni ----
  function openSong(nr) {
    var s = byNr[nr];
    if (!s) { closeSong(); return; }
    var lyricsOnly = localStorage.getItem("lyricsOnly") === "1";
    songEl.innerHTML =
      '<span class="num">' + s.nr + '</span>'
      + '<h2>' + escapeHtml(s.title) + '</h2>'
      + '<div class="meta">' + [s.section, s.keyfmt ? "tonacja " + escapeHtml(s.keyfmt) : ""]
          .filter(Boolean).map(function (x) { return x.toUpperCase(); }).join("  ·  ") + '</div>'
      + '<div class="body' + (lyricsOnly ? " lyrics-only" : "") + '" id="body">' + s.html + '</div>';
    $("#toggleChords").setAttribute("aria-pressed", lyricsOnly ? "false" : "true");
    applyNotation(songEl);
    songview.hidden = false;
    document.body.style.overflow = "hidden";
    songview.scrollTop = 0;
  }
  function closeSong() {
    songview.hidden = true;
    document.body.style.overflow = "";
  }

  function route() {
    var h = location.hash.replace(/^#/, "");
    if (/^\d+$/.test(h)) openSong(parseInt(h, 10)); else closeSong();
  }

  // ---- sterowanie widokiem pieśni ----
  $("#back").addEventListener("click", function () { history.back(); });
  $("#toggleChords").addEventListener("click", function () {
    var body = $("#body"); if (!body) return;
    var on = body.classList.toggle("lyrics-only");
    localStorage.setItem("lyricsOnly", on ? "1" : "0");
    this.setAttribute("aria-pressed", on ? "false" : "true");
  });
  function setSize(px) {
    px = Math.max(12, Math.min(28, px));
    document.documentElement.style.setProperty("--song-size", px + "px");
    localStorage.setItem("songSize", px);
  }
  $("#fontPlus").addEventListener("click", function () { setSize(curSize() + 1); });
  $("#fontMinus").addEventListener("click", function () { setSize(curSize() - 1); });
  function curSize() { return parseInt(localStorage.getItem("songSize") || "16", 10); }

  // ===== akordy: notacja PL↔US + diagramy (SVG) =====
  var CHORDS = window.CHORDS || {};
  var OPEN = [4, 9, 2, 7, 11, 4];                       // pc pustych strun E A D G B e
  var PL2US = { C:"C", Cis:"C#", Ces:"Cb", D:"D", Dis:"D#", Des:"Db", E:"E", Es:"Eb", Eis:"E#",
    F:"F", Fis:"F#", Fes:"Fb", G:"G", Gis:"G#", Ges:"Gb", A:"A", Ais:"A#", As:"Ab", H:"B", His:"B#", B:"Bb" };

  function chordToUS(tok) {
    var m = tok.match(/^([A-Ha-h])(is|es|s(?!us))?(.*)$/);
    if (!m) return tok;
    var L = m[1], acc = m[2] || "", rest = m[3], minor = (L === L.toLowerCase()), U = L.toUpperCase(), root;
    if (acc === "is") root = U + "is";
    else if (acc === "es" || acc === "s") root = ({ E:"Es", A:"As", H:"B" })[U] || (U + "es");
    else root = U;
    var us = PL2US[root] || root;
    return minor ? us + "m" + rest : us + rest;
  }
  function tokenToUS(tok) {                              // całe „pole" chwytu: bas po /, sekwencje -, nawiasy
    if (/^[|/()\[\]:]+$/.test(tok) || /^\/?x\d+$/i.test(tok) || /^\/?bis$/i.test(tok)) return tok;
    var m = tok.match(/^([(\[]*)(.*?)([)\].,;]*)$/), pre = m[1], core = m[2], post = m[3];
    core = core.split(/([/\-])/).map(function (p) { return (p === "/" || p === "-") ? p : chordToUS(p); }).join("");
    return pre + core + post;
  }
  function notationUS() { return localStorage.getItem("notation") === "us"; }
  function applyNotation(root) {
    var us = notationUS();
    (root || document).querySelectorAll(".ch").forEach(function (el) {
      if (el.dataset.pl === undefined) el.dataset.pl = el.textContent;
      el.textContent = us ? tokenToUS(el.dataset.pl) : el.dataset.pl;
    });
    document.querySelectorAll("#toggleNotation,#toggleNotationCd").forEach(function (b) {
      b.setAttribute("aria-pressed", us ? "true" : "false");
      b.textContent = us ? "B→H" : "H→B";
    });
  }

  function chordSVG(frets) {
    var W = 64, H = 82, padX = 9, padTop = 19, gw = W - 2 * padX, sp = gw / 5;
    var fr = frets.filter(function (f) { return typeof f === "number" && f > 0; });
    var top = 1, rows = 4;
    if (fr.length) { var lo = Math.min.apply(null, fr), hi = Math.max.apply(null, fr); if (hi > 4) { top = lo; rows = Math.max(4, hi - lo + 1); } }
    var rh = (H - padTop - 6) / rows, s = '<svg viewBox="0 0 ' + W + ' ' + H + '" class="cd">';
    for (var i = 0; i < 6; i++) { var x = padX + i * sp; s += '<line x1="' + x + '" y1="' + padTop + '" x2="' + x + '" y2="' + (padTop + rh * rows) + '"/>'; }
    for (var r = 0; r <= rows; r++) { var y = padTop + rh * r; s += '<line x1="' + padX + '" y1="' + y + '" x2="' + (padX + gw) + '" y2="' + y + '"' + (r === 0 && top === 1 ? ' stroke-width="3"' : '') + '/>'; }
    if (top > 1) s += '<text x="' + (padX + gw + 2) + '" y="' + (padTop + rh * 0.7) + '" class="cdfr">' + top + '</text>';
    frets.forEach(function (f, i) {
      var x = padX + i * sp;
      if (f === "x") s += '<text x="' + x + '" y="' + (padTop - 3) + '" class="cdx">×</text>';
      else if (f === 0) s += '<circle cx="' + x + '" cy="' + (padTop - 7) + '" r="2.6" class="cdo"/>';
      else { var cy = padTop + rh * ((f - top + 1) - 0.5); s += '<circle cx="' + x + '" cy="' + cy + '" r="' + (sp * 0.34).toFixed(1) + '" class="cddot"/>'; }
    });
    return s + "</svg>";
  }

  var chordsview = $("#chordsview"), chordsEl = $("#chordsbody");
  function renderChords() {
    var us = notationUS(), h = '<h2>Indeks akordów</h2>'
      + '<p class="cdnote">Otwartostrunowe / sus wojsingi pogrupowane parami równoległymi dur/moll. Struny E–A–D–G–B–e.</p>';
    Object.keys(CHORDS).forEach(function (key) {
      h += '<h3 class="cdgrp">' + escapeHtml(key) + '</h3><div class="cdrow">';
      CHORDS[key].forEach(function (v) {
        var nm = us ? tokenToUS(v.name) : v.name;
        h += '<figure class="cdcell">' + chordSVG(v.frets)
          + '<figcaption>' + escapeHtml(nm) + (v.role ? '<span class="cdrole">' + escapeHtml(v.role) + '</span>' : "") + '</figcaption></figure>';
      });
      h += "</div>";
    });
    chordsEl.innerHTML = h;
  }
  function openChords() { renderChords(); chordsview.hidden = false; document.body.style.overflow = "hidden"; chordsview.scrollTop = 0; }
  function closeChords() { chordsview.hidden = true; document.body.style.overflow = ""; }
  $("#openChords").addEventListener("click", openChords);
  $("#chordsBack").addEventListener("click", closeChords);
  function toggleNotation() {
    localStorage.setItem("notation", notationUS() ? "pl" : "us");
    applyNotation(document);
    if (!chordsview.hidden) renderChords();
  }
  $("#toggleNotation").addEventListener("click", toggleNotation);
  $("#toggleNotationCd").addEventListener("click", toggleNotation);

  // ---- init ----
  setSize(curSize());
  renderFilters();
  render();
  applyNotation(document);                 // ustaw etykiety przycisków notacji
  q.addEventListener("input", render);
  window.addEventListener("hashchange", route);
  window.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (!chordsview.hidden) closeChords();
    else if (!songview.hidden) history.back();
  });
  route();
})();
