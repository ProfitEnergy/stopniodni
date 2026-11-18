"""Kopia indeksu gazowego TGEgasDA (Rynek Dnia Następnego gazu, TGE S.A.).

Źródło: publiczne dane opóźnione TGE (wykres indeksu na https://tge.pl/gaz-rdn,
endpoint graph-days zwraca 8 dób kończących się na dateStart).
Zapis: dane/rdng/tgegasda.json -> {"zrodlo": ..., "aktualizacja": ..., "dni": {"RRRR-MM-DD": kurs_PLN_MWh}}
Pierwsze uruchomienie pobiera historię od 2023-01-01, potem ostatnie ok. 3 tygodnie + jutro.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone

URL = 'https://tge.pl/graph-days'
OUT = os.path.join(os.path.dirname(__file__), '..', 'dane', 'rdng', 'tgegasda.json')
START = date(2023, 1, 1)
UA = 'Mozilla/5.0 (kopia indeksu TGEgasDA dla energetycznybroker.pl)'


def okno(koniec):
    q = urllib.parse.urlencode({'targetId': 'POLPX_GAS', 'dateStart': koniec.isoformat(), 'soapType': 'RDNG_INDEX'})
    for proba in range(4):
        try:
            req = urllib.request.Request(URL + '?' + q, headers={'User-Agent': UA, 'Referer': 'https://tge.pl/gaz-rdn', 'X-Requested-With': 'XMLHttpRequest'})
            with urllib.request.urlopen(req, timeout=60) as r:
                t = r.read().decode('utf-8', 'replace').strip()
            return json.loads(t) if t.startswith('[') else []
        except Exception:
            if proba == 3:
                raise
            time.sleep(5 * (proba + 1))


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    dane = {}
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            j = json.load(f)
        dane = j.get('dni', {})
        if j.get('klucz') != 'dzien_dostawy':  # stary format: data sesji -> przesuń o +1 dzień
            dane = {(date.fromisoformat(d) + timedelta(days=1)).isoformat(): v for d, v in dane.items()}
    dzis = date.today()
    pelna = '--pelna' in sys.argv or len(dane) < 30
    od = START if pelna else dzis - timedelta(days=21)
    k = dzis + timedelta(days=1)
    while k >= od:
        for x in okno(k):
            try:
                if x.get('kurs') not in (None, ''):
                    # TGE podaje datę sesji; indeks dotyczy dostawy w dniu następnym
                    dd = date.fromisoformat(x['date'][:10]) + timedelta(days=1)
                    dane[dd.isoformat()] = round(float(x['kurs']), 2)
            except (TypeError, ValueError, KeyError):
                pass
        k -= timedelta(days=8)
        time.sleep(1 if pelna else 0.3)
    wynik = {'zrodlo': 'TGE S.A., indeks TGEgasDA (Rynek Dnia Następnego gazu), dane opóźnione', 'klucz': 'dzien_dostawy', 'aktualizacja': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'dni': dict(sorted(dane.items()))}
    stare = None
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            sj = json.load(f)
            stare = sj.get('dni') if sj.get('klucz') == 'dzien_dostawy' else None
    if stare == wynik['dni']:
        print('bez zmian', len(dane)); return
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(wynik, f, ensure_ascii=False, separators=(',', ':'))
    print('zapisano dni:', len(dane))


if __name__ == '__main__':
    main()
