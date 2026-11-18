"""Kopia cen rynku dnia następnego (cena SDAC dla Polski) z API PSE S.A.

Zapisuje dane/rdn/RRRR-MM.json: {"RRRR-MM-DD": [["00:00 - 00:15", 723.24], ...], ...}
oraz dane/rdn/ostatnie.json (ostatnie 3 doby + data aktualizacji).
Źródło: https://api.raporty.pse.pl/api/csdac-pln (dane publiczne PSE S.A.).
Przy pierwszym uruchomieniu pobiera historię od 2024-06-14; potem odświeża bieżący
i poprzedni miesiąc (żeby złapać ceny na jutro i ewentualne korekty).
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import date, timedelta

API = 'https://api.raporty.pse.pl/api/csdac-pln'
OUT = os.path.join(os.path.dirname(__file__), '..', 'dane', 'rdn')
START = date(2024, 6, 14)


def pobierz(od, do):
    q = "$filter=business_date ge '%s' and business_date le '%s'&$first=20000" % (od.isoformat(), do.isoformat())
    url = API + '?' + urllib.parse.quote(q, safe="$=&'")
    wynik = []
    while url:
        for proba in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'energetycznybroker.pl kopia RDN'}), timeout=60) as r:
                    j = json.load(r)
                break
            except Exception as e:
                if proba == 3:
                    raise
                time.sleep(5 * (proba + 1))
        wynik += j.get('value', [])
        url = j.get('nextLink') or j.get('@odata.nextLink')
    return wynik


def miesiace(od, do):
    d = date(od.year, od.month, 1)
    while d <= do:
        nast = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
        yield d, min(nast - timedelta(days=1), do)
        d = nast


def zapisz_miesiac(m0, m1):
    rek = pobierz(m0, m1)
    dni = {}
    for x in rek:
        try:
            dni.setdefault(x['business_date'], []).append([x['period'], round(float(x['csdac_pln']), 2)])
        except (KeyError, TypeError, ValueError):
            pass
    if not dni:
        return 0
    for k in dni:
        dni[k].sort(key=lambda p: p[0])
    plik = os.path.join(OUT, m0.strftime('%Y-%m') + '.json')
    stare = {}
    if os.path.exists(plik):
        with open(plik, encoding='utf-8') as f:
            stare = json.load(f)
    stare.update(dni)
    with open(plik, 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(stare.items())), f, ensure_ascii=False, separators=(',', ':'))
    return len(dni)


def main():
    os.makedirs(OUT, exist_ok=True)
    dzis = date.today()
    jutro = dzis + timedelta(days=1)
    pelna = '--pelna' in sys.argv or not any(n.endswith('.json') and n[:4].isdigit() for n in os.listdir(OUT))
    od = START if pelna else date(dzis.year, dzis.month, 1) - timedelta(days=1)
    od = date(od.year, od.month, 1) if not pelna else od
    n = 0
    for m0, m1 in miesiace(od, jutro):
        n += zapisz_miesiac(m0, m1)
        print(m0.strftime('%Y-%m'), 'ok')
    # ostatnie 3 doby do szybkiego odczytu
    ost = {}
    for d in (dzis - timedelta(days=1), dzis, jutro):
        plik = os.path.join(OUT, d.strftime('%Y-%m') + '.json')
        if os.path.exists(plik):
            with open(plik, encoding='utf-8') as f:
                m = json.load(f)
            if d.isoformat() in m:
                ost[d.isoformat()] = m[d.isoformat()]
    with open(os.path.join(OUT, 'ostatnie.json'), 'w', encoding='utf-8') as f:
        json.dump({'zrodlo': 'PSE S.A., cena SDAC (api.raporty.pse.pl)', 'dni': ost}, f, ensure_ascii=False, separators=(',', ':'))
    print('dni zapisanych:', n)


if __name__ == '__main__':
    main()
