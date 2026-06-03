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

  // ---- init ----
  setSize(curSize());
  renderFilters();
  render();
  q.addEventListener("input", render);
  window.addEventListener("hashchange", route);
  window.addEventListener("keydown", function (e) { if (e.key === "Escape" && !songview.hidden) history.back(); });
  route();
})();
