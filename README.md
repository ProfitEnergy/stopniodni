# Stopniodni – dane do kalkulatora na energetycznybroker.pl

Dobowe średnie temperatury powietrza ze stacji synoptycznych IMGW-PIB (od 2020 r.), przygotowane dla
[kalkulatora stopniodni i oszczędności na ogrzewaniu](https://energetycznybroker.pl/kalkulator-stopniodni.html)
prowadzonego przez PROFIT ENERGY Konrad Bojakowski.

- `dane/stopniodni/stacje.json` – lista stacji (współrzędne, data początku serii, liczba uzupełnionych dni) i data ostatniej aktualizacji.
- `dane/stopniodni/<kod>.json` – temperatury dobowe w dziesiątych częściach °C od daty `od`.
- `dane/miejscowosci/` – miejscowości z Państwowego Rejestru Nazw Geograficznych (GUGiK) ze współrzędnymi.
- `scripts/aktualizuj.py` – pobranie i przeliczenie danych; uruchamiane automatycznie 8. i 15. dnia miesiąca (GitHub Actions).

Stopniodni grzania liczy się jako suma (18°C − średnia dobowa) dla dni ze średnią poniżej 15°C.
Pojedyncze brakujące dni uzupełniane są wartością z najbliższej stacji; stacje wysokogórskie oraz stacje z ponad 10% uzupełnień są pomijane.

Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy.
Dane IMGW-PIB zostały przetworzone. Dane o miejscowościach: Państwowy Rejestr Nazw Geograficznych, GUGiK.
