# Stopniodni grzania w Polsce – dane IMGW-PIB i kalkulator kosztów ogrzewania

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24418033.svg)](https://doi.org/10.5281/zenodo.24418033)

Cytowanie: Bojakowski, K. (PROFIT ENERGY Konrad Bojakowski). *Stopniodni grzania w Polsce – stacje synoptyczne IMGW-PIB*. Zenodo. https://doi.org/10.5281/zenodo.24418033

Otwarte dane o stopniodniach grzania dla 54 stacji synoptycznych IMGW-PIB, aktualizowane co miesiąc.
Z tych danych korzysta bezpłatny
[kalkulator kosztów ogrzewania](https://energetycznybroker.pl/kalkulator-kosztow-ogrzewania.html)
na energetycznybroker.pl, prowadzony przez PROFIT ENERGY Konrad Bojakowski – niezależnego doradcę i brokera energetycznego z Warszawy.

## Czym są stopniodni

Stopniodni grzania mierzą, jak zimny był dany okres. Dla każdego dnia ze średnią temperaturą poniżej 15°C
liczy się różnicę między 18°C a średnią dobową temperaturą zewnętrzną (metoda Eurostatu). Suma z miesiąca
albo sezonu pokazuje, ile budynek musiał grzać.

Dzięki temu da się uczciwie porównać zużycie ciepła w różnych sezonach. Przykład dla Warszawy
(stacja Warszawa-Okęcie): sezon grzewczy 2025/26 miał 3219 stopniodni, sezon 2024/25 – 2859,
a średnia z sezonów 2016/17–2025/26 to 3024. Styczeń 2026 miał 728 stopniodni, styczeń 2025 – 481.

## Jak skorygować faktury za ciepło o pogodę

Przykład (zużycie umowne): budynek zużył w sezonie 2024/25 1000 GJ na ogrzewanie. Przy pogodzie sezonu
2025/26 ten sam budynek, bez żadnych zmian, zużyłby ok. 1000 × 3219 ÷ 2859 ≈ 1126 GJ. Jeśli faktury
pokazują mniej, to realna oszczędność; jeśli więcej, coś w budynku pracuje gorzej.

To uproszczenie dotyczy części zużycia zależnej od pogody. Ta sama zasada jest stosowana przy
rozliczaniu oszczędności energii według protokołu IPMVP. Dokładniejszy rachunek oddziela ciepłą wodę
użytkową i stałe straty.

## Gdzie zobaczyć gotowe liczby

- [Kalkulator kosztów ogrzewania](https://energetycznybroker.pl/kalkulator-kosztow-ogrzewania.html) – wgrywasz faktury PDF za ciepło, kalkulator dobiera najbliższą stację IMGW i liczy zużycie z korektą pogodową.
- [Stopniodni w Polsce – raport miesięczny](https://energetycznybroker.pl/stopniodni.html) – wszystkie stacje i miasta.
- [Stopniodni Warszawa](https://energetycznybroker.pl/stopniodni-warszawa.html) – miesiąc po miesiącu, sezony od 2020/21.
- [Stopniodni dla gminy – kalkulator](https://energetycznybroker.pl/stopniodni-dla-gminy.html) – każda z 2324 gmin: miesiące i sezony od 2010, CSV; gmina ze stacją w promieniu 10 km dostaje jej pomiary, pozostałe – średnią ważoną odległością z 3 najbliższych stacji.
- [Widżet „Stopniodni dla Twojej gminy” – jak wstawić na stronę](https://energetycznybroker.pl/jak-wstawic-widzet-stopniodni.html) – bezpłatna ramka dla stron gmin, spółdzielni i wspólnot: 5 największych miejscowości gminy, sezony grzewcze od 2021/22 z wykresem i miesiące rok do roku (lista miejscowości: `dane/gminy-miejscowosci.json`).
- [Poradnik: metoda stopniodni](https://energetycznybroker.pl/poradnik-metoda-stopniodni.html) – jak mierzy się oszczędności ciepła.
- [Czy budynek zużywa za dużo ciepła](https://energetycznybroker.pl/czy-budynek-zuzywa-za-duzo-ciepla.html) – wskaźnik GJ/m² z korektą pogodową.
- [Porównanie zużycia ciepła wielu budynków](https://energetycznybroker.pl/porownanie-zuzycia-ciepla-wielu-budynkow.html) – benchmark dla spółdzielni, zarządców i gmin.
- [Ciepłomierz – jak odczytać GJ, moc i temperatury](https://energetycznybroker.pl/cieplomierz-jak-odczytac.html).
- [Ile można zaoszczędzić na ogrzewaniu](https://energetycznybroker.pl/ile-mozna-zaoszczedzic-na-ogrzewaniu.html).

## Zawartość repozytorium

- `dane/stopniodni/stacje.json` – lista stacji (współrzędne, data początku serii, liczba uzupełnionych dni) i data ostatniej aktualizacji.
- `dane/stopniodni/<kod>.json` – temperatury dobowe w dziesiątych częściach °C od daty `od`.
- `dane/csv/stopniodni_miesieczne.csv` – miesięczne stopniodni grzania dla każdej stacji od 2010 r. (CSV, UTF-8).
- `dane/csv/stopniodni_sezony.csv` – stopniodni w sezonach grzewczych wrzesień–maj.
- `dane/csv/stacje.csv` – lista stacji.
- `dane/miejscowosci/` – miejscowości z Państwowego Rejestru Nazw Geograficznych (GUGiK) ze współrzędnymi.
- `dane/gminy.json` – 2324 gminy (siedziba gminy, numer województwa, współrzędne, dopisek dla gmin o tej samej nazwie) – wybór stacji w kalkulatorze stopniodni dla gminy; budowany skryptem `scripts/gminy.py` z `dane/miejscowosci/`.
- `dane/gminy-miejscowosci.json` – do 5 największych miejscowości każdej gminy (kolejność jak w `dane/gminy.json`; nazwa, szerokość, długość, liczba mieszkańców) – widok „5 największych miejscowości” w widżecie i kalkulatorze stopniodni dla gminy. Liczba mieszkańców: Wikidata (P1082, w większości wyniki NSP 2021), dopasowana do `dane/miejscowosci/` po nazwie i odległości do 6 km.
- `scripts/aktualizuj.py` – pobranie i przeliczenie danych; uruchamiane automatycznie 8. i 15. dnia miesiąca (GitHub Actions).

Stopniodni grzania liczy się jako suma (18°C − średnia dobowa) dla dni ze średnią poniżej 15°C.
Pojedyncze brakujące dni uzupełniane są wartością z najbliższej stacji; stacje wysokogórskie oraz stacje z ponad 10% uzupełnień są pomijane.

## Źródła i licencja danych

Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy.
Dane IMGW-PIB zostały przetworzone. Dane o miejscowościach: Państwowy Rejestr Nazw Geograficznych, GUGiK.

Kontakt: PROFIT ENERGY Konrad Bojakowski, Warszawa – [energetycznybroker.pl](https://energetycznybroker.pl/), biuro@energetycznybroker.pl, tel. +48 722 149 551.

Licencja opracowania: CC BY 4.0 – przy wykorzystaniu prosimy o podanie źródła „PROFIT ENERGY Konrad Bojakowski (energetycznybroker.pl) na podstawie danych IMGW-PIB”.

## Ceny RDN (rynek dnia następnego) – kopia danych PSE

Folder `dane/rdn/` to kopia publicznych cen SDAC dla Polski z API PSE S.A. (`api.raporty.pse.pl/api/csdac-pln`), w zł/MWh, co 15 minut, od 14.06.2024. Pliki `RRRR-MM.json` (doba → lista `[okres, cena]`) i `ostatnie.json` (ostatnie 3 doby). Aktualizacja co godzinę (`.github/workflows/rdn.yml`). Używane jako zapas przez stronę https://energetycznybroker.pl/ceny-energii-rdn.html, gdy API PSE nie odpowiada. Źródło danych: PSE S.A.

## Gaz – indeks TGEgasDA (Rynek Dnia Następnego gazu) – kopia danych TGE

`dane/rdng/tgegasda.json` – dzienny indeks TGEgasDA (zł/MWh) od 2023 r., z publicznych danych opóźnionych TGE S.A. (wykres indeksu na tge.pl/gaz-rdn). Aktualizacja co godzinę (`.github/workflows/rdng.yml`). Używane przez https://energetycznybroker.pl/ceny-gazu-rdn.html. Źródło danych: TGE S.A.

## Opinie – liczniki na energetycznybroker.pl

`dane/opinie/opinie.json` – liczba opinii w Google, na Facebooku, Oferteo i w zestawieniu Złota Firma. Aktualizowane codziennie przez zadanie zaplanowane Claude (sprawdzenie profili). Strona główna i „O mnie” podmieniają liczniki po załadowaniu.
