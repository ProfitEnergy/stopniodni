# Generator stron stopniodni (energetycznybroker.pl)

python3 generator/stopniodni_gen.py <szablon: poradnik-metoda-stopniodni.html z serwera> <katalog wyjściowy>

Tworzy stopniodni.html i stopniodni-warszawa.html z liczbami wpisanymi w HTML (dla robotów)
na podstawie dane/stopniodni/*.json. Skrypt sd_js.js jest wklejany do stron i przelicza to samo w przeglądarce.

## Raporty miesięczne (raporty.json)
Lista raportów miesięcznych (najnowszy pierwszy). Generator wstawia na stopniodni.html blok „Raporty miesięczne” (id="raporty", karta najnowszego + lista starszych), a na stopniodni-warszawa.html link do najnowszego raportu. Po opublikowaniu nowego raportu (np. stopniodni-listopad-2026.html) dopisz go NA POCZĄTEK listy i wygeneruj strony ponownie. Pozycja menu „Raport miesięczny” prowadzi do stopniodni.html#raporty, więc menu nie wymaga zmian co miesiąc.
