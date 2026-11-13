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

from lxml import etree
from pyproj import Transformer
gmls = sorted(glob.glob(TMP + '/**/*.gml', recursive=True))
log('gml:', len(gmls))
acc = collections.defaultdict(lambda: [0.0, 0.0, 0, collections.Counter()])
probka = None
def loc(t): return t.rsplit('}', 1)[-1]
for p in gmls:
    n = 0; feat_tag = None
    ctx = etree.iterparse(p, events=('end',), huge_tree=True, recover=True)
    cur = {}
    for ev, el in ctx:
        ln = loc(el.tag)
        if ln in ('kodPocztowy', 'KOD_POCZTOWY', 'kod_pocztowy'):
            cur['kod'] = (el.text or '').strip()
        elif ln in ('miejscowosc', 'MIEJSCOWOSC', 'nazwaMiejscowosci') and (el.text or '').strip():
            cur.setdefault('msc', (el.text or '').strip())
        elif ln == 'pos' and el.text:
            cur['pos'] = el.text.split()
        elif ln.startswith('PRG_PunktAdresowy') or ln in ('PunktAdresowy', 'AD_PunktAdresowy', 'PRG_PunktyAdresowe'):
            if probka is None:
                probka = etree.tostring(el, encoding='unicode')[:1500]; log('próbka:', probka)
            if 'kod' in cur and 'pos' in cur:
                kod = cur['kod']
                if len(kod) == 5 and kod.isdigit(): kod = kod[:2] + '-' + kod[2:]
                if len(kod) == 6 and kod[2] == '-':
                    try:
                        u, v = float(cur['pos'][0]), float(cur['pos'][1])
                        a = acc[kod]; a[0] += u; a[1] += v; a[2] += 1
                        if cur.get('msc'): a[3][cur['msc']] += 1
                        n += 1
                    except ValueError: pass
            cur = {}
            el.clear()
            while el.getprevious() is not None: del el.getparent()[0]
        elif ln == 'featureMember' or ln == 'member':
            el.clear()
    log(os.path.basename(p), 'punktów:', n)
# kolejność osi: sprawdzamy na kodach warszawskich 00-xxx (ok. 52,23 N; 21,01 E)
t = Transformer.from_crs('EPSG:2180', 'EPSG:4326', always_xy=True)
war = [v for k, v in acc.items() if k.startswith('00-')][:50]
def ocen(swap):
    err = 0
    for sx, sy, c, _ in war:
        x, y = (sy / c, sx / c) if swap else (sx / c, sy / c)
        lon, lat = t.transform(x, y); err += abs(lat - 52.23) + abs(lon - 21.01)
    return err
SWAP = ocen(True) < ocen(False)
log('zamiana osi:', SWAP, ocen(True), ocen(False))
class TR:
    def transform(self, a, b):
        return t.transform(b, a) if SWAP else t.transform(a, b)
tr_cache = {'x': TR()}
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
