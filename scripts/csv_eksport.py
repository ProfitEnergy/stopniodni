"""Eksport stopniodni do CSV (otwarte dane, m.in. dane.gov.pl).

dane/csv/stopniodni_miesieczne.csv – miesięczne stopniodni grzania dla każdej stacji IMGW-PIB
dane/csv/stopniodni_sezony.csv     – sezony grzewcze (wrzesień–maj)
dane/csv/stacje.csv                – lista stacji
Metoda: Eurostat – suma (18°C − średnia dobowa) dla dni ze średnią < 15°C.
Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy. Dane IMGW-PIB zostały przetworzone.
"""
import csv, datetime as dt, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'dane', 'stopniodni'); OUT = os.path.join(ROOT, 'dane', 'csv')
os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(D, 'stacje.json'), encoding='utf-8'))

def hdd(t): return 18 - t if t < 15 else 0.0

with open(os.path.join(OUT, 'stacje.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['kod_stacji', 'nazwa_stacji', 'szerokosc', 'dlugosc', 'dane_od', 'dni_uzupelnione'])
    for s in M['stacje']: w.writerow([s['id'], s['n'], s['lat'], s['lon'], s['od'], s.get('u', 0)])

mies = open(os.path.join(OUT, 'stopniodni_miesieczne.csv'), 'w', newline='', encoding='utf-8')
sez = open(os.path.join(OUT, 'stopniodni_sezony.csv'), 'w', newline='', encoding='utf-8')
wm = csv.writer(mies); ws = csv.writer(sez)
wm.writerow(['kod_stacji', 'nazwa_stacji', 'rok', 'miesiac', 'stopniodni', 'dni_z_danymi', 'dni_w_miesiacu', 'srednia_temperatura_c'])
ws.writerow(['kod_stacji', 'nazwa_stacji', 'sezon', 'stopniodni', 'kompletny'])
for s in M['stacje']:
    d = json.load(open(os.path.join(D, s['id'] + '.json'), encoding='utf-8'))
    od = dt.date.fromisoformat(d['od']); t = d['t']
    acc = {}
    for i, v in enumerate(t):
        if v is None: continue
        day = od + dt.timedelta(days=i); k = (day.year, day.month)
        a = acc.setdefault(k, [0.0, 0, 0.0]); T = v / 10; a[0] += hdd(T); a[1] += 1; a[2] += T
    for (y, m) in sorted(acc):
        h, n, st = acc[(y, m)]
        dim = ((dt.date(y + (m == 12), m % 12 + 1, 1)) - dt.date(y, m, 1)).days
        wm.writerow([s['id'], s['n'], y, m, round(h, 1), n, dim, round(st / n, 1)])
    for y in range(od.year, dt.date.today().year + 1):
        ks = [(y, m) for m in range(9, 13)] + [(y + 1, m) for m in range(1, 6)]
        if not all(k in acc for k in ks[:1]): continue
        full = all(k in acc and acc[k][1] == ((dt.date(k[0] + (k[1] == 12), k[1] % 12 + 1, 1)) - dt.date(*k, 1)).days for k in ks)
        tot = sum(acc[k][0] for k in ks if k in acc)
        ws.writerow([s['id'], s['n'], f'{y}/{str(y + 1)[2:]}', round(tot, 1), 'tak' if full else 'nie'])
mies.close(); sez.close()
print('ok')
