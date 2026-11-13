"""Kody pocztowe -> współrzędne (środek punktów adresowych) z PRG GUGiK.

Pobiera punkty adresowe Państwowego Rejestru Granic (GUGiK, dane otwarte),
grupuje je po kodzie pocztowym i zapisuje środek ciężkości oraz najczęstszą
miejscowość dla każdego kodu. Wynik: dane/kody/<pierwsza cyfra>.json
w formacie {"00-001": [lat, lon, "Warszawa"], ...}.
Źródło: Główny Urząd Geodezji i Kartografii, Państwowy Rejestr Granic – punkty adresowe.
"""
import collections, glob, json, os, sys, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dane', 'kody')
TMP = '/tmp/prg'
URLS = [
    'https://opendata.geoportal.gov.pl/prg/adresy/PRG-punkty_adresowe.zip',
    'https://opendata.geoportal.gov.pl/prg/adresy/PunktyAdresowe/POLSKA.zip',
    'https://opendata.geoportal.gov.pl/prg/adresy/adresy.zip',
]
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
diag = []


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); diag.append(s)


def done(ok):
    open(os.path.join(OUT, '_diag.txt'), 'w', encoding='utf-8').write('\n'.join(diag) + '\n')
    sys.exit(0 if ok else 1)


zp = os.path.join(TMP, 'prg.zip')
for u in URLS:
    try:
        log('pobieram', u)
        req = urllib.request.Request(u, headers={'User-Agent': 'stopniodni-energetycznybroker/1.0'})
        with urllib.request.urlopen(req, timeout=600) as r, open(zp, 'wb') as f:
            while True:
                b = r.read(1 << 20)
                if not b: break
                f.write(b)
        log('rozmiar', os.path.getsize(zp)); break
    except Exception as e:
        log('błąd', u, repr(e))
else:
    done(False)

with zipfile.ZipFile(zp) as z:
    names = z.namelist(); log('pliki w zip:', len(names), names[:30])
    z.extractall(TMP)
# zagnieżdżone zipy (np. per województwo)
for inner in glob.glob(TMP + '/**/*.zip', recursive=True):
    if inner == zp: continue
    try:
        with zipfile.ZipFile(inner) as z: z.extractall(os.path.dirname(inner))
    except Exception as e: log('zip wewn.', inner, e)

import shapefile
from pyproj import Transformer
shps = [p for p in glob.glob(TMP + '/**/*.shp', recursive=True) if 'adres' in os.path.basename(p).lower() or 'pkt' in os.path.basename(p).lower() or 'punkt' in os.path.basename(p).lower()]
if not shps: shps = glob.glob(TMP + '/**/*.shp', recursive=True)
log('shp:', len(shps), shps[:20])
acc = collections.defaultdict(lambda: [0.0, 0.0, 0, collections.Counter()])
tr_cache = {}
for p in shps:
    sf = shapefile.Reader(p, encoding='utf-8', encodingErrors='replace')
    fields = [f[0] for f in sf.fields[1:]]
    low = [f.lower() for f in fields]
    ik = next((i for i, f in enumerate(low) if 'kod' in f and 'pocz' in f), next((i for i, f in enumerate(low) if f in ('kod', 'pna', 'kodpocztow')), None))
    im = next((i for i, f in enumerate(low) if f.startswith('miejsc') and 'id' not in f), None)
    log(os.path.basename(p), 'pola:', fields, 'kod:', ik, 'msc:', im, 'rekordów:', len(sf))
    if ik is None: continue
    prj = p[:-4] + '.prj'
    wkt = open(prj, encoding='utf-8', errors='replace').read() if os.path.exists(prj) else ''
    src = 'EPSG:2180' if ('1992' in wkt or 'CS92' in wkt or not wkt) else ('EPSG:4326' if 'GCS_ETRS_1989' in wkt or 'WGS' in wkt else 'EPSG:2180')
    if src not in tr_cache: tr_cache[src] = Transformer.from_crs(src, 'EPSG:4326', always_xy=True)
    tr = tr_cache[src]
    n = 0
    for sr in sf.iterShapeRecords():
        if not sr.shape.points: continue
        kod = str(sr.record[ik]).strip()
        if len(kod) == 5 and kod.isdigit(): kod = kod[:2] + '-' + kod[2:]
        if len(kod) != 6 or kod[2] != '-': continue
        x, y = sr.shape.points[0]
        a = acc[kod]; a[0] += x; a[1] += y; a[2] += 1
        if im is not None: a[3][str(sr.record[im]).strip()] += 1
        n += 1
    log('  przetworzono', n)
    a_src = src
if not acc: done(False)
tr = list(tr_cache.values())[0]
out = collections.defaultdict(dict)
for kod, (sx, sy, c, mc) in acc.items():
    lon, lat = tr.transform(sx / c, sy / c)
    if not (48.5 < lat < 55.2 and 13.8 < lon < 24.5): continue
    out[kod[0]][kod] = [round(lat, 4), round(lon, 4), mc.most_common(1)[0][0] if mc else '']
for d, m in out.items():
    json.dump(dict(sorted(m.items())), open(os.path.join(OUT, d + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
log('kodów:', sum(len(m) for m in out.values()))
done(True)
