"""Aktualizacja danych temperatur dobowych ze stacji synoptycznych IMGW-PIB.

Pobiera dobowe dane synoptyczne (pliki s_d) z https://danepubliczne.imgw.pl,
wybiera średnią dobową temperaturę powietrza (kolumna STD), uzupełnia pojedyncze
braki wartością z najbliższej stacji i zapisuje pliki JSON używane przez
kalkulator stopniodni na energetycznybroker.pl.

Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej –
Państwowy Instytut Badawczy. Dane IMGW-PIB zostały przetworzone.
"""
import datetime as dt
import io
import json
import math
import os
import re
import sys
import time
import urllib.request
import zipfile

BASE = 'https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/dobowe/synop/'
START = dt.date(2016, 1, 1)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dane', 'stopniodni')
COORDS = json.load(open(os.path.join(ROOT, 'scripts', 'stacje_wspolrzedne.json'), encoding='utf-8'))
WYKLUCZONE = {'KASPROWY WIERCH', 'ŚNIEŻKA', 'HALA GĄSIENICOWA'}  # stacje wysokogórskie
MAKS_UZUPELNIEN = 0.10  # stacja z >10% dni uzupełnionych jest pomijana


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'stopniodni-energetycznybroker/1.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    raise RuntimeError('Nie udało się pobrać ' + url)


def zip_urls():
    urls = []
    today = dt.date.today()
    for y in range(START.year, today.year):
        html = get(BASE + f'{y}/')
        if html is None:
            continue
        for m in re.findall(r'href="([^"]+\.zip)"', html.decode('utf-8', 'replace')):
            urls.append(BASE + f'{y}/' + m)
    # rok bieżący: pliki miesięczne ze wszystkich stacji
    html = get(BASE + f'{today.year}/')
    if html:
        for m in re.findall(r'href="([^"]+\.zip)"', html.decode('utf-8', 'replace')):
            urls.append(BASE + f'{today.year}/' + m)
    return urls


def parse(text, temps, names):
    for line in text.splitlines():
        if not line.strip():
            continue
        f = [s.strip().strip('"').strip() for s in line.split(',')]
        if len(f) < 11 or not f[0].isdigit():
            continue
        code, name = f[0], f[1]
        try:
            d = dt.date(int(f[2]), int(f[3]), int(f[4]))
        except ValueError:
            continue
        if d < START:
            continue
        if len(name) > len(names.get(code, '')):
            names[code] = name
        t, status = f[9], f[10]
        if status == '8' or t == '':
            continue
        try:
            temps.setdefault(code, {})[d] = float(t)
        except ValueError:
            pass


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a['lat'], a['lon'], b['lat'], b['lon']])
    return 12742 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


def nazwa(n):
    n = n.title()
    return re.sub(r'-(\w)', lambda m: '-' + m.group(1).upper(), n)


def main():
    temps, names = {}, {}
    urls = zip_urls()
    print('plików:', len(urls))
    for u in urls:
        raw = get(u)
        if raw is None:
            continue
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for nm in z.namelist():
                if re.match(r'^s_d_\d', os.path.basename(nm)):
                    parse(z.read(nm).decode('cp1250', 'replace'), temps, names)
    if not temps:
        sys.exit('Brak danych – przerywam bez zmian.')
    last = max(max(v) for v in temps.values())
    nd = (last - START).days + 1
    codes = [c for c in temps if names.get(c, '').upper() not in WYKLUCZONE and c[-3:] in {k[-3:] for k in COORDS}]
    pos = {c: next(v for k, v in COORDS.items() if k[-3:] == c[-3:]) for c in codes}
    series = {c: [temps[c].get(START + dt.timedelta(days=i)) for i in range(nd)] for c in codes}
    os.makedirs(OUT, exist_ok=True)
    stacje = []
    for c in sorted(codes):
        v = series[c][:]
        valid = [i for i, x in enumerate(v) if x is not None]
        if len(valid) < 365:
            continue
        first = valid[0]
        neigh = sorted([k for k in codes if k != c], key=lambda k: km(pos[c], pos[k]))
        filled = 0
        for i in range(first, nd):
            if v[i] is None:
                for k in neigh:
                    if series[k][i] is not None:
                        v[i] = series[k][i]
                        filled += 1
                        break
        if filled > MAKS_UZUPELNIEN * (nd - first):
            continue
        od = START + dt.timedelta(days=first)
        n = nazwa(names[c])
        json.dump({'id': c, 'n': n, 'od': od.isoformat(), 't': [None if x is None else round(x * 10) for x in v[first:]], 'uzupelnione': filled},
                  open(os.path.join(OUT, c + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        stacje.append({'id': c, 'n': n, 'lat': pos[c]['lat'], 'lon': pos[c]['lon'], 'od': od.isoformat(), 'u': filled})
    keep = {s['id'] for s in stacje}
    for f in os.listdir(OUT):
        if f.endswith('.json') and f != 'stacje.json' and f[:-5] not in keep:
            os.remove(os.path.join(OUT, f))
    meta = {'aktualizacja': dt.date.today().isoformat(), 'dane_do': last.isoformat(), 'baza': 18, 'prog': 15,
            'zrodlo': 'IMGW-PIB, dane synoptyczne dobowe (średnia dobowa temperatura powietrza)', 'stacje': stacje}
    json.dump(meta, open(os.path.join(OUT, 'stacje.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('stacji:', len(stacje), 'dane do:', last)


if __name__ == '__main__':
    main()
