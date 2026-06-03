# -*- coding: utf-8 -*-
# Wspólne dane planu liturgii i listy pieśni (dla pdf.py = z chwytami i pdf_plain.py = bez chwytów)

# Konfiguracja wydarzenia — używana w okładkach, nagłówkach i nazwach plików PDF.
# Zmiana tutaj przenosi się na wszystkie generatory (zamiast literałów rozsianych po kodzie).
EVENT={
 "top":      "KRĄG WYJAZDOWY",                 # nadtytuł okładki
 "header":   "BOŻE CIAŁO 2026",                # prawy róg żywej paginy (wersalikami)
 "subtitle": "Boże Ciało · 4–7 czerwca 2026",  # podtytuł okładki (z datami)
 "short":    "Boże Ciało 2026",                # krótka nazwa (okładka pełnego śpiewnika, nazwy plików)
 "dates":    "Boże Ciało · 4–7 czerwca 2026",
}

SELECTED=[
 "Części stałe","Apel Jasnogórski",
 "Bądźże pozdrowiona Hostio żywa","Bo góry mogą ustąpić","Chcę wywyższać Imię Twe","Chlebie najcichszy",
 "Chrystus Pan Boży Syn","Cóż Ci Jezu damy","Dotknij, Panie, moich oczu","Dzięki Ci, Panie, za Ciało Twe i Krew",
 "Idzie mój Pan","Jeden chleb","Kłaniam się Tobie","Kochajmy Pana","Memu Bogu, Królowi","Mów do mnie, Panie",
 "Niech będzie chwała","O Panie, Ty nam dajesz Ciało swe i Krew","O Zbawcza Hostio","Oceany","Oto ja, poślij mnie",
 "Oto jest dzień","Otwórz me oczy, o Panie","Pan jest mocą swojego ludu","Pan jest pasterzem moim","Panie dobry jak chleb",
 "Przed tak wielkim Sakramentem","Przyjdź jak deszcz","Skosztujcie i zobaczcie",
 "Ta krew z grzechu obmywa mnie","Ukaż mi, Panie, swą twarz","Wciąż mnie zadziwiasz, Panie",
 "Wielbię Ciebie w każdym momencie","Witaj Pokarmie","Wspaniały Dawco miłości","Wszystko Tobie oddać pragnę","Zbliżam się w pokorze",
]

PLAN=[
 ("Czwartek · 4 czerwca","Uroczystość Najświętszego Ciała i Krwi Chrystusa (Boże Ciało)","msza kameralna · Rok A",
  "Pwt 8,2-3.14b-16a (manna na pustyni — „nie samym chlebem żyje człowiek”)  ·  Ps 147B  ·  "
  "1 Kor 10,16-17 („Chleb, który łamiemy… jeden chleb, jedno ciało”)  ·  Sekwencja Lauda Sion  ·  "
  "J 6,51-58 („Ja jestem chlebem żywym… Ciało moje jest prawdziwym pokarmem”).",
  "Eucharystia — Chleb żywy, który daje życie, i jedność jednego Ciała.",
  [("Wejście","Oto jest dzień","Radość uroczystości — „weselmy się i radujmy się w nim”."),
   ("Ofiarowanie","Wspaniały Dawco miłości","„Składamy na Twoim stole wszystko, co mamy” — dar ofiarny w odpowiedzi na dar Ciała."),
   ("Komunia","O Panie, Ty nam dajesz Ciało swe i Krew  →  Idzie mój Pan","Wprost echo 1 Kor 10 i J 6; Pan „biegnie, by w Komunii nakarmić nasz głód” — nowa manna."),
   ("Dziękczynienie","Dzięki Ci, Panie, za Ciało Twe i Krew","Dziękczynienie eucharystyczne wprost — „za dary nieskończone wielbimy Cię”."),
   ("Wyjście","Niech będzie chwała i cześć","Uwielbienie Chrystusa obecnego w Najświętszym Sakramencie."),
   ("Adoracja","Kłaniam się Tobie · Bądźże pozdrowiona Hostio żywa · Witaj Pokarmie · Zbliżam się w pokorze","Tradycyjna adoracja eucharystyczna. 3–4 pieśni.")]),
 ("Piątek · 5 czerwca","Piątek IX tygodnia zwykłego, św. Bonifacego","msza kameralna",
  "2 Tm 3,10-17 (Pismo Święte natchnione, „pożyteczne do nauczania, wychowania w sprawiedliwości”)  ·  "
  "Ps 119 („Obfity pokój miłującym Prawo”)  ·  Mk 12,35-37 (Mesjasz Synem i Panem Dawida).",
  "Słowo Boże — światło, które otwiera serce i prowadzi.",
  [("Wejście","Dotknij, Panie, moich oczu","Prośba o otwarcie oczu, warg i serca na Słowo."),
   ("Ofiarowanie","Oto ja, poślij mnie","Odpowiedź ucznia na usłyszane Słowo — gotowość i posłanie."),
   ("Komunia","Chlebie najcichszy","Wyciszenie po Słowie — „otul mnie swym milczeniem, przemień mnie w Siebie”."),
   ("Dziękczynienie","Mów do mnie, Panie","Wyciszone słuchanie: „chcę słyszeć Cię, przyjąć od Ciebie, co masz dla mnie”."),
   ("Wyjście","Chcę wywyższać Imię Twe","Posłanie z radością — „ogłaszać Słowo Twe wśród narodów”."),
   ("Adoracja","Otwórz me oczy, o Panie · Ukaż mi, Panie, swą twarz · Wciąż mnie zadziwiasz, Panie","„Daj mi usłyszeć Twój głos” — wpatrzenie w Pana w Słowie. 3 pieśni.")]),
 ("Sobota · 6 czerwca","Sobota IX tygodnia zwykłego, św. Norberta","msza kameralna",
  "2 Tm 4,1-8 („w dobrych zawodach wystąpiłem, bieg ukończyłem, wiary ustrzegłem”)  ·  "
  "Ps 71 („Będę wysławiał Twoją sprawiedliwość”)  ·  Mk 12,38-44 (grosz wdowy — „wrzuciła wszystko, co miała”).",
  "Oddać Bogu wszystko; wierność do końca, hojność ubogiego serca.",
  [("Wejście","Przyjdź jak deszcz","Prośba o ożywienie i świeżość Ducha na nowy dzień."),
   ("Ofiarowanie","Wszystko Tobie oddać pragnę","Wprost grosz wdowy: „Serce moje weź” — oddanie Bogu wszystkiego."),
   ("Komunia","Pan jest pasterzem moim","Ps 23 — Pan prowadzi i karmi; nic mi nie braknie."),
   ("Dziękczynienie","Bo góry mogą ustąpić","Wierność Boża, która nie ustaje — „miłość moja nigdy nie odstąpi”."),
   ("Wyjście","Memu Bogu, Królowi","„Teraz, zawsze, na wieki” — wytrwanie i wierność do końca."),
   ("Adoracja","Chrystus Pan Boży Syn · Oceany · Wielbię Ciebie w każdym momencie","„O żywy Chlebie nasz w tym Sakramencie” — uwielbienie Baranka. 3 pieśni.")]),
 ("Niedziela · 7 czerwca","X Niedziela zwykła, Rok A — MSZA Z LUDEM","pieśni tradycyjne, śpiewne",
  "Oz 6,3-6 („Miłości pragnę, nie krwawej ofiary”)  ·  Ps 50  ·  Rz 4,18-25 (wiara Abrahama: „wbrew nadziei "
  "uwierzył nadziei”)  ·  Mt 9,9-13 (powołanie celnika Mateusza; „Chcę raczej miłosierdzia niż ofiary”).",
  "Miłosierdzie większe niż grzech; powołanie grzesznika; miłość ponad ofiarę. Czerwiec — miesiąc Najśw. Serca Pana Jezusa.",
  [("Wejście","Pan jest mocą swojego ludu","Mocna, wspólnotowa pieśń ludu Bożego."),
   ("Ofiarowanie","Panie dobry jak chleb","Ukochana, tradycyjna: „bo Tyś do końca nas umiłował”."),
   ("Komunia","Jeden chleb  →  Ta krew z grzechu obmywa mnie","„Jeden chleb… jedno ciało” (1 Kor 10); potem miłosierdzie — Krew obmywa grzesznika (celnik Mateusz)."),
   ("Dziękczynienie","Skosztujcie i zobaczcie · Cóż Ci Jezu damy","Radosne, śpiewne; „Króluj Jezu nam” — tradycyjne, miesiąc Serca Jezusowego."),
   ("Wyjście","Kochajmy Pana","„Bo Serce Jego żąda i pragnie serca naszego” — wprost Oz 6; miesiąc Serca Jezusowego."),
   ("Adoracja","Przed tak wielkim Sakramentem · O Zbawcza Hostio","Wieczorna adoracja (kameralnie, bez ludu) — wielkie hymny eucharystyczne.")]),
]
