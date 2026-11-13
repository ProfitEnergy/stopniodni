# Wspólne obliczenia stopniodni (lustrzane do sd_js.js – wynik HTML musi być identyczny)
import json, math, datetime as dt
import os
SP = os.path.dirname(os.path.abspath(__file__)) + '/'
DD = os.path.join(os.path.dirname(SP.rstrip('/')), 'dane', 'stopniodni') + '/'
EPOCH = dt.date(1970, 1, 1)
MIES = ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień']
MIES_L = ['styczniu', 'lutym', 'marcu', 'kwietniu', 'maju', 'czerwcu', 'lipcu', 'sierpniu', 'wrześniu', 'październiku', 'listopadzie', 'grudniu']
MIES_D = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']
SEZ_M = [9, 10, 11, 12, 1, 2, 3, 4, 5]


def dnum(d): return (d - EPOCH).days
def ddate(n): return EPOCH + dt.timedelta(days=n)
def mstart(y, m): return dnum(dt.date(y, m, 1))
def mend(y, m): return dnum(dt.date(y + (m == 12), m % 12 + 1, 1)) - 1


def load(sid):
    d = json.load(open(DD + sid + '.json', encoding='utf-8'))
    return {'od': dnum(dt.date.fromisoformat(d['od'])), 't': d['t']}


def sdd(S, a, b):
    s = 0.0
    for x in range(a, b + 1):
        i = x - S['od']
        if i < 0 or i >= len(S['t']) or S['t'][i] is None:
            return None
        T = S['t'][i] / 10
        if T < 15:
            s += 18 - T
    return s


def r0(v): return '–' if v is None else str(int(math.floor(v + 0.5)))
def pct(v, a): return int(math.floor((v / a - 1) * 100 + 0.5))
def sl(y): return f'{y}/{str(y + 1)[2:]}'
def pdat(n):
    d = ddate(n); return f'{d.day} {MIES_D[d.month - 1]} {d.year}'


def por(p, ref, avg, suf=True):
    if p == 0: return f'tyle samo co {ref} ({avg})'
    return f'o {abs(p)}% ' + ('mniej' if p < 0 else 'więcej') + f' niż {ref} ({avg})' + ((' – cieplej niż zwykle' if p < 0 else ' – zimniej niż zwykle') if suf else '')


def info(S):
    end = S['od'] + len(S['t']) - 1
    e = ddate(end)
    # ostatni pełny miesiąc
    if end == mend(e.year, e.month): ly, lm = e.year, e.month
    else: ly, lm = (e.year, e.month - 1) if e.month > 1 else (e.year - 1, 12)
    ps = e.year if e.month >= 9 else (e.year - 1 if e.month <= 5 else None)
    lc = ps - 1 if ps is not None else e.year - 1
    base = list(range(lc - 9, lc + 1))
    sez = {y: sdd(S, mstart(y, 9), mend(y + 1, 5)) for y in base}
    avg_s = sum(sez.values()) / 10
    I = {'end': end, 'ly': ly, 'lm': lm, 'ps': ps, 'lc': lc, 'base': base, 'sez': sez, 'avg_s': avg_s}
    lv = sdd(S, mstart(ly, lm), mend(ly, lm))
    la = sum(sdd(S, mstart(y, lm), mend(y, lm)) for y in range(ly - 10, ly)) / 10
    I.update(lv=lv, la=la, lp=pct(lv, la))
    ly0 = sdd(S, mstart(ly - 1, lm), mend(ly - 1, lm)); I.update(ly0=ly0, lpy=pct(lv, ly0))
    sez[lc - 10] = sdd(S, mstart(lc - 10, 9), mend(lc - 9, 5))
    if ps is not None:
        a = mstart(ps, 9); b = min(end, mend(ps + 1, 5)); off = b - a
        pv = sdd(S, a, b)
        pa = sum(sdd(S, mstart(y, 9), mstart(y, 9) + off) for y in base) / 10
        pv0 = sdd(S, mstart(ps - 1, 9), mstart(ps - 1, 9) + off)
        I.update(pv=pv, pa=pa, pp=pct(pv, pa), pb=b, pv0=pv0, ppy=pct(pv, pv0))
    return I


def ryr(p, ref, val):
    if p == 0: return f'tyle samo co {ref} ({val})'
    return f'o {abs(p)}% ' + ('mniej' if p < 0 else 'więcej') + f' niż {ref} ({val}), czyli ' + ('cieplej' if p < 0 else 'zimniej')


def html_sum(I):
    o = '<ul class="sd-sum">'
    o += f'<li><b>{MIES[I["lm"] - 1].capitalize()} {I["ly"]}:</b> {r0(I["lv"])} stopniodni – {ryr(I["lpy"], f'w {MIES_L[I["lm"] - 1]} {I["ly"] - 1}', r0(I["ly0"]))}.</li>'
    if I['ps'] is not None:
        o += f'<li><b>Sezon grzewczy {sl(I["ps"])} od 1 września do {pdat(I["pb"])}:</b> {r0(I["pv"])} stopniodni – {ryr(I["ppy"], f'w tym samym okresie sezonu {sl(I["ps"] - 1)}', r0(I["pv0"]))}.</li>'
    else:
        lcv = I['sez'][I['lc']]; pr = I['sez'][I['lc'] - 1]
        o += f'<li><b>Sezon grzewczy {sl(I["lc"])} (wrzesień–maj):</b> {r0(lcv)} stopniodni – {ryr(pct(lcv, pr), f'w sezonie {sl(I["lc"] - 1)}', r0(pr))}.</li>'
    return o + '</ul>'


def html_sez(S, I):
    o = '<table><thead><tr><th scope="col">Sezon grzewczy</th><th scope="col">Stopniodni IX–V</th><th scope="col">Zmiana do poprzedniego sezonu</th></tr></thead><tbody>'
    if I['ps'] is not None:
        o += f'<tr><th scope="row">{sl(I["ps"])} (do {pdat(I["pb"])})</th><td>{r0(I["pv"])}</td><td>{("+" if I["ppy"] > 0 else "") + str(I["ppy"])}% wobec tego samego okresu {sl(I["ps"] - 1)}</td></tr>'
    for y in reversed(I['base']):
        p = pct(I['sez'][y], I['sez'][y - 1])
        o += f'<tr><th scope="row">{sl(y)}</th><td>{r0(I["sez"][y])}</td><td>{("+" if p > 0 else "") + str(p)}%</td></tr>'
    o += f'<tr><th scope="row">Średnia {sl(I["base"][0])}–{sl(I["lc"])}</th><td><b>{r0(I["avg_s"])}</b></td><td>–</td></tr>'
    return o + '</tbody></table>'


def html_mies(S, I):
    cols = list(range(I['lc'] - 4, I['lc'] + 1)) + ([I['ps']] if I['ps'] is not None else [])
    o = '<table><thead><tr><th scope="col">Miesiąc</th>' + ''.join(f'<th scope="col">{sl(y)}</th>' for y in cols) + f'<th scope="col">Średnia {sl(I["base"][0])}–{sl(I["lc"])}</th></tr></thead><tbody>'
    for m in SEZ_M:
        o += f'<tr><th scope="row">{MIES[m - 1]}</th>'
        for y in cols:
            yy = y if m >= 9 else y + 1
            o += f'<td>{r0(sdd(S, mstart(yy, m), mend(yy, m)) if mend(yy, m) <= I["end"] else None)}</td>'
        av = sum(sdd(S, mstart(y if m >= 9 else y + 1, m), mend(y if m >= 9 else y + 1, m)) for y in I['base']) / 10
        o += f'<td><b>{r0(av)}</b></td></tr>'
    return o + '</tbody></table>'


def html_lata(S, I):
    e = ddate(I['end']); out = []
    for y in range(e.year - 10, e.year):
        v = sdd(S, mstart(y, 1), mend(y, 12))
        if v is not None: out.append(f'{y} – {r0(v)}')
    return ', '.join(out)


def html_tldr(I, msc_w, st_n):
    t = f'{MIES[I["lm"] - 1].capitalize()} {I["ly"]} {msc_w} (stacja IMGW {st_n}): {r0(I["lv"])} stopniodni, {ryr(I["lpy"], f'w {MIES_L[I["lm"] - 1]} {I["ly"] - 1}', r0(I["ly0"]))}.'
    if I['ps'] is not None:
        t += f' Sezon grzewczy {sl(I["ps"])} do {pdat(I["pb"])}: {r0(I["pv"])} stopniodni wobec {r0(I["pv0"])} w tym samym okresie sezonu {sl(I["ps"] - 1)}.'
    return t


def hub_row(c, I):
    a = f'<a href="stopniodni-{c["slug"]}.html">{c["n"]}</a>' if c.get('slug') else c['n']
    s = f'<tr><th scope="row">{a}</th><td>{r0(I["lv"])}</td><td>{r0(I["la"])}</td><td>{("+" if I["lp"] > 0 else "") + str(I["lp"])}%</td>'
    if I['ps'] is not None:
        s += f'<td>{r0(I["pv"])}</td><td>{r0(I["pa"])}</td><td>{("+" if I["pp"] > 0 else "") + str(I["pp"])}%</td>'
    else:
        lcv = I['sez'][I['lc']]; p = pct(lcv, I['avg_s'])
        s += f'<td>{r0(lcv)}</td><td>{r0(I["avg_s"])}</td><td>{("+" if p > 0 else "") + str(p)}%</td>'
    return s + '</tr>'


def hub_head(I):
    if I['ps'] is not None:
        d = ddate(I['pb']); sez = f'Sezon {sl(I["ps"])} (1.09–{d.day}.{d.month:02d})'; sav = f'Średnia 1.09–{d.day}.{d.month:02d} z 10 sezonów'
    else:
        sez = f'Sezon {sl(I["lc"])}'; sav = 'Średnia 10 sezonów'
    return (f'<table><thead><tr><th scope="col">Miasto</th><th scope="col">{MIES[I["lm"] - 1].capitalize()} {I["ly"]}</th><th scope="col">Średnia {MIES_D[I["lm"] - 1] if False else ""}{I["ly"] - 10}–{I["ly"] - 1}</th><th scope="col">Różnica</th>'
            f'<th scope="col">{sez}</th><th scope="col">{sav}</th><th scope="col">Różnica</th></tr></thead><tbody>')
