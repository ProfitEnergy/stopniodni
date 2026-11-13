import json, re, html, math
import os, sys
SP = os.path.dirname(os.path.abspath(__file__)) + '/'
exec(open(SP + 'sd_core.py', encoding='utf-8').read())
OUT = (sys.argv[2] if len(sys.argv) > 2 else SP + 'out') + '/'; os.makedirs(OUT, exist_ok=True)
import os; os.makedirs(OUT, exist_ok=True)
TPL = open(sys.argv[1], encoding='utf-8').read()
META = json.load(open(DD + 'stacje.json', encoding='utf-8'))
SDJS = open(SP + 'sd_js.js', encoding='utf-8').read()
DATE = '2026-11-13'; DATE_PL = '13 listopada 2026'
BASE = 'https://energetycznybroker.pl/'
DANE_DO = META['dane_do']; DANE_DO_PL = pdat(dnum(dt.date.fromisoformat(DANE_DO)))
GITHUB = 'https://github.com/ProfitEnergy/stopniodni'

MIASTA = [('Warszawa', '352200375', 'warszawa'), ('Kraków', '350190566', None), ('Łódź', '351190465', None), ('Wrocław', '351160424', None),
          ('Poznań', '352160330', None), ('Gdańsk', '354180155', None), ('Szczecin', '353140205', None), ('Toruń', '353180250', None),
          ('Lublin', '351220495', None), ('Białystok', '353230295', None), ('Katowice', '350190560', None), ('Kielce', '350200570', None),
          ('Olsztyn', '353200272', None), ('Opole', '350170530', None), ('Rzeszów', '350220580', None), ('Zielona Góra', '351150400', None),
          ('Gorzów Wielkopolski', '352150300', None), ('Płock', '352190360', None), ('Siedlce', '352220385', None)]
STN = {s['id']: s['n'] for s in META['stacje']}

CSS = '''<style>.sd-sum{list-style:none;padding:0;margin:16px 0;display:grid;gap:10px}.sd-sum li{border:1px solid var(--line);border-left:4px solid var(--volt);border-radius:12px;padding:12px 16px;background:var(--card,#fff)}
.sd-wz{border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;background:var(--soft);font-family:var(--f-mono);font-size:.95rem;overflow-x:auto}
.sd-pick{border:2px solid var(--volt);border-radius:var(--r);padding:18px;margin:18px 0;background:var(--card,#fff)}.sd-pick select{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;min-width:260px;max-width:100%}
.sd-pick h3{margin:18px 0 6px}.sd-pick h4{margin:16px 0 6px}.sd-do{font-size:.9rem;color:var(--muted)}.sd-t table{font-size:.9rem}.sd-t th,.sd-t td{padding:10px 10px}.sd-t tbody th{font-size:1rem}.sd-lok{display:grid;grid-template-columns:minmax(120px,160px) 1fr;gap:12px;position:relative}.sd-lok label,.sd-sel label{display:grid;gap:6px;font-weight:600;font-size:.92rem}
.sd-lok input,.sd-sel select{font:inherit;font-weight:400;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card,#fff);color:inherit;width:100%;min-width:0}
#sd-lista{position:absolute;left:0;right:0;top:100%;z-index:20;list-style:none;margin:4px 0 0;padding:6px;background:var(--card,#fff);border:1px solid var(--line);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.12);max-height:300px;overflow:auto}#sd-lista li{padding:8px 10px;border-radius:8px;cursor:pointer;font-size:.92rem}#sd-lista li:hover{background:var(--soft)}
.sd-sel{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:6px}
.sd-wyn{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0 8px}.sd-wyn div{border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:grid;gap:4px}.sd-wyn span{font-size:.85rem;color:var(--muted)}.sd-wyn b{font-size:1.6rem;line-height:1.1}
.sd-roz.cie{background:#E8F4EC;border-color:#BFDCC8}.sd-roz.zim{background:#FDECEC;border-color:#F2C4C4}#sd-tabele h3{margin-top:18px}#sd-tabele2 h4{margin-top:22px}.sd-avg th,.sd-avg td{font-weight:700;background:var(--soft)}
@media(max-width:560px){.sd-lok{grid-template-columns:1fr}}
.article{max-width:none}.sd-top{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:18px;align-items:start;margin:8px 0 10px}.sd-top .tldr{margin:0}.sd-kc{display:flex;flex-direction:column;gap:10px;padding:18px;border-radius:14px;background:var(--card,#fff);border:2px solid var(--volt);box-shadow:0 10px 28px rgba(0,0,0,.08)}.sd-kc small{font-size:.75rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}.sd-kc strong{font-size:1.35rem;line-height:1.25}.sd-kc p{margin:0;font-size:.92rem;line-height:1.45}.sd-kc .btn{margin-top:auto;width:100%;padding:15px 16px;font-size:1.05rem;font-weight:700}@media(max-width:720px){.sd-top{grid-template-columns:1fr}}
</style>'''


def page(slug, title, desc, h1, crumbs, eyebrow, body, faq, lds, cfg):
    kh = 'kalkulator-kosztow-ogrzewania.html' + ('?msc=Warszawa' if cfg.get('typ') == 'miasto' else '')
    kc = ('<aside class="sd-kc" aria-label="Kalkulator kosztów ogrzewania"><small>Kalkulator kosztów ogrzewania</small>'
          '<strong>Czy Twój budynek zużywa za dużo ciepła?</strong>'
          '<p>Wgraj faktury za ciepło w PDF. Kalkulator przeliczy zużycie przez stopniodni z najbliższej stacji IMGW i pokaże potencjał oszczędności.</p>'
          f'<a class="btn primary" href="{kh}">Sprawdź swoje faktury →</a></aside>')
    body = re.sub(r'^(<div class="tldr">.*?</div>)', lambda m: '<div class="sd-top">' + m.group(1) + kc + '</div>', body, count=1, flags=re.S)
    assert 'sd-top' in body
    url = BASE + slug
    faq_html = '<h2>Najczęstsze pytania</h2><div class="faq">' + ''.join(
        f'<details{" open" if i == 0 else ""}><summary>{html.escape(q)}</summary><p class="a">{html.escape(a)}</p></details>' for i, (q, a) in enumerate(faq)) + '</div>'
    cr = ' › '.join([f'<a href="{u}">{n}</a>' for n, u in crumbs] + [crumbs and h1.split(' – ')[0]])
    main = (f'<main><section class="phero"><div class="wrap"><p class="crumbs">{cr}</p>'
            f'<span class="eyebrow">{eyebrow}</span><h1 style="margin-top:10px">{h1}</h1>'
            f'<div class="byline"><img src="img/konrad-bojakowski.webp" alt="" width="44" height="44"><span><b style="color:var(--fg)">Konrad Bojakowski</b>, doradca energetyczny PROFIT ENERGY · aktualizacja: {DATE_PL} · dane IMGW do: <span id="sd-do">{DANE_DO_PL}</span></span></div></div></section>'
            f'<section class="tight"><div class="wrap"><article class="article">{CSS}{body}{faq_html}</article></div></section>'
            f'<section class="tight"><div class="wrap"><div class="ctaband"><div><h2>Sprawdź, ile ciepła zużywa Twój budynek po korekcie pogodowej</h2><p>Wrzuć faktury za ciepło do kalkulatora – policzy roczne zużycie, koszt i potencjał oszczędności ze stopniodni z najbliższej stacji IMGW. Albo wyślij faktury do mnie.</p></div><a class="btn primary" href="kalkulator-kosztow-ogrzewania.html">Kalkulator kosztów ogrzewania</a></div></div></section></main>')
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    bc = {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + (u if u != './' else '')} for i, (n, u) in enumerate(crumbs)] +
          [{"@type": "ListItem", "position": len(crumbs) + 1, "name": h1.split(' – ')[0], "item": url}]}
    page_ld = {"@context": "https://schema.org", "@graph": [bc, {"@type": "WebPage", "@id": url + "#strona", "url": url, "name": title, "description": desc, "inLanguage": "pl",
               "dateModified": DATE, "isPartOf": {"@id": BASE + "#witryna"}, "about": {"@id": BASE + "#firma"}}]}
    out = TPL
    head_old = out[:out.index('<link rel="preconnect"')]
    head_new = f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="icon" type="image/png" href="img/favicon.png">
<meta property="og:type" content="article">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Profit Energy Konrad Bojakowski">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://energetycznybroker.pl/img/og-profit-energy.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(page_ld, ensure_ascii=False)}</script>
'''
    out = head_new + out[len(head_old):]
    a = out.index('<main>'); b = out.index('<footer class="foot">')
    extra = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in [faq_ld] + lds)
    extra += f'<script type="application/json" id="sd-cfg">{json.dumps(cfg, ensure_ascii=False)}</script><script>{SDJS}</script>\n'
    out = out[:a] + main + extra + out[b:]
    open(OUT + slug, 'w', encoding='utf-8').write(out)
    print(slug, len(out), len(re.sub('<[^>]+>', ' ', main).split()), 'słów')


def dataset(url, name, desc, place, sid=None):
    d = {"@context": "https://schema.org", "@type": "Dataset", "name": name, "description": desc, "url": url, "inLanguage": "pl",
         "creator": {"@id": BASE + "#firma"}, "isBasedOn": "https://danepubliczne.imgw.pl/", "temporalCoverage": f"2016-01-01/{DANE_DO}",
         "spatialCoverage": {"@type": "Place", "name": place}, "dateModified": META['aktualizacja'], "isAccessibleForFree": True,
         "variableMeasured": "stopniodni grzania (HDD), baza 18°C, próg 15°C", "measurementTechnique": "Eurostat: suma (18°C − średnia temperatura dobowa) dla dni ze średnią poniżej 15°C",
         "creditText": "Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy. Dane IMGW-PIB zostały przetworzone.",
         "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json",
                           "contentUrl": f"https://cdn.jsdelivr.net/gh/ProfitEnergy/stopniodni@main/dane/stopniodni/{sid or 'stacje'}.json"}], "sameAs": GITHUB}
    return d


def art(url, h1, desc, about):
    return {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "datePublished": DATE, "dateModified": DATE, "inLanguage": "pl",
            "about": about, "author": {"@type": "Person", "@id": BASE + "#konrad", "name": "Konrad Bojakowski", "url": BASE + "o-mnie.html"},
            "publisher": {"@id": BASE + "#firma"}, "mainEntityOfPage": url, "image": BASE + "img/og-profit-energy.jpg"}


# ===================== STRONA ZBIORCZA =====================
D = {}
for n, sid, slug in MIASTA:
    S = load(sid); D[sid] = (S, info(S))
Sw, Iw = D['352200375']
AP = agg([D[sid][1] for n, sid, slug in MIASTA])
hub_tab = hub_head(Iw) + ''.join(hub_row({'n': n, 'slug': slug}, D[sid][1]) for n, sid, slug in MIASTA) + hub_avg(AP) + '</tbody></table>'
LM = f'{MIES[Iw["lm"] - 1]} {Iw["ly"]}'
def sgp(p): return ('+' if p > 0 else '') + str(p)
# wnioski z tabeli
by_l = sorted(MIASTA, key=lambda m: D[m[1]][1]['lpy'])
by_s = sorted(MIASTA, key=lambda m: D[m[1]][1]['pv'])
lc = Iw['lc']
sez_min = min(D[m[1]][1]['avg_s'] for m in MIASTA); sez_max = max(D[m[1]][1]['avg_s'] for m in MIASTA)
m_min = min(MIASTA, key=lambda m: D[m[1]][1]['avg_s']); m_max = max(MIASTA, key=lambda m: D[m[1]][1]['avg_s'])
cieplej = sum(1 for m in MIASTA if D[m[1]][1]['lpy'] < 0)

H1 = 'Stopniodni w Polsce – aktualne dane IMGW i raport miesięczny'
TITLE = 'Stopniodni w Polsce – aktualne dane IMGW, raport miesięczny'
DESC = f'Liczba stopniodni grzania dla 19 miast i 54 stacji IMGW: ostatni miesiąc, bieżący sezon i 10 sezonów wstecz. Wzór, metoda Eurostat, dane co miesiąc.'
SLUG = 'stopniodni.html'; URL = BASE + SLUG
body = f'''<div class="tldr"><b>W skrócie</b><strong>Stopniodni (liczba stopniodni grzania)</strong> mówią, jak zimny był dany okres i ile ciepła potrzebował budynek do ogrzania. Dla każdego dnia liczy się różnicę 18°C minus średnia temperatura dobowa – tylko w dniach chłodniejszych niż 15°C – i sumuje za miesiąc lub sezon. Ta strona pokazuje aktualne stopniodni dla 19 miast i 54 stacji IMGW-PIB, przeliczane co miesiąc. {LM.capitalize()} – średnio w 19 miastach: <strong>{r0(AP["lv"])}</strong> stopniodni wobec {r0(AP["ly0"])} w {MIES_L[Iw["lm"] - 1]} {Iw["ly"] - 1}; w Warszawie {r0(Iw["lv"])} wobec {r0(Iw["ly0"])}.</div>
<h2>Stopniodni w Polsce – najnowsze dane</h2>
<p>Polska – średnia z 19 miast z tabeli poniżej (stacje IMGW-PIB):</p>
<div id="sd-sum">{html_sum(AP)}</div>
<p>{LM.capitalize()} był cieplejszy niż rok wcześniej w {cieplej} z 19 miast. Największa zmiana w stronę ciepła: {by_l[0][0]} ({sgp(D[by_l[0][1]][1]["lpy"])}% wobec {MIES_D[Iw["lm"] - 1]} {Iw["ly"] - 1}), w stronę zimna: {by_l[-1][0]} ({sgp(D[by_l[-1][1]][1]["lpy"])}%). Od początku sezonu {sl(Iw["ps"])} najcieplej było w mieście {by_s[0][0]} ({r0(D[by_s[0][1]][1]["pv"])} stopniodni), najzimniej w mieście {by_s[-1][0]} ({r0(D[by_s[-1][1]][1]["pv"])}).</p>
<h2 id="miasta">Stopniodni w 19 miastach – {LM} i sezon {sl(Iw["ps"])} rok do roku</h2>
<p>Dla każdego miasta stacja synoptyczna IMGW-PIB położona w mieście lub tuż obok (np. Kraków-Balice, Gdańsk-Świbno). Pierwsze trzy kolumny: ostatni pełny miesiąc i ten sam miesiąc rok wcześniej. Trzy ostatnie: bieżący sezon grzewczy od 1 września do ostatniego dnia z danymi i ten sam okres poprzedniego sezonu. Zmiana dodatnia oznacza, że było zimniej niż rok wcześniej, ujemna – cieplej. Ostatni wiersz to średnia z 19 miast. Porównanie z dowolnym innym okresem zrobisz <a href="#stacja">w narzędziu poniżej</a>.</p>
<div class="tbl sd-t" id="sd-tab">{hub_tab}</div>
<p class="sd-do">Dane do: {DANE_DO_PL}. Kolejne miesiące dopisują się automatycznie po publikacji danych przez IMGW-PIB (zwykle w pierwszej połowie następnego miesiąca).</p>

<h2 id="stacja">Porównaj stopniodni dla swojej miejscowości</h2>
<p>Wpisz kod pocztowy albo miejscowość. Pokażę te same dane co dla Polski i Warszawy – ostatni miesiąc i bieżący sezon rok do roku, sezony grzewcze od {sl(SEZ_OD)} – a w porównywarce wybierzesz miesiąc, sezon lub rok i to, z czym go zestawić: ten sam okres rok wcześniej, średnią z 5 lub 10 lat albo dowolny okres z listy.</p>
<div class="sd-pick" id="sd-narz">
<div class="sd-lok"><label for="sd-kod">Kod pocztowy<input id="sd-kod" inputmode="numeric" placeholder="00-000" maxlength="6" autocomplete="postal-code"></label><label for="sd-msc">Miejscowość<input id="sd-msc" autocomplete="off" placeholder="np. Piaseczno" role="combobox" aria-controls="sd-lista"></label><ul id="sd-lista" role="listbox" hidden></ul></div>
<p id="sd-stacja" class="sd-do">Wpisz kod pocztowy albo miejscowość – dobiorę najbliższą stację IMGW-PIB.</p>
<div id="sd-tabele"></div>
<div id="sd-por" hidden><div class="sd-sel"><label for="sd-typ">Porównuję<select id="sd-typ"><option value="m">miesiące</option><option value="s">sezony grzewcze (IX–V)</option><option value="r">lata kalendarzowe</option></select></label><label for="sd-a">Okres<select id="sd-a"></select></label><label for="sd-b">Porównaj z<select id="sd-b"></select></label></div><div id="sd-wynik" aria-live="polite"></div></div>
<div id="sd-tabele2"></div></div>
<p class="sd-do">Ten sam mechanizm wyboru stacji działa w <a href="kalkulator-kosztow-ogrzewania.html">kalkulatorze kosztów ogrzewania</a>, który dodatkowo odczytuje faktury za ciepło.</p>

<h2>Wzór na stopniodni</h2>
<p>Stosuję metodę Eurostatu, tę samą, którą Unia Europejska publikuje dla wszystkich krajów:</p>
<div class="sd-wz">HDD = Σ (18°C − T<sub>m</sub>) dla dni, w których T<sub>m</sub> &lt; 15°C<br>T<sub>m</sub> – średnia temperatura dobowa powietrza; w dniach z T<sub>m</sub> ≥ 15°C stopniodni = 0</div>
<p>Przykład: dzień ze średnią temperaturą 2°C daje 18 − 2 = <b>16 stopniodni</b>, dzień z 10°C – 8, a dzień z 16°C – zero. Suma za {LM} w Warszawie to {r0(Iw["lv"])} stopniodni.</p>
<p>W audycie energetycznym przy termomodernizacji stosuje się inną definicję: liczbę stopniodni sezonu grzewczego S<sub>d</sub> liczy się z projektowej temperatury wewnętrznej i wieloletnich średnich temperatur miesięcznych dla lokalizacji (rozporządzenie w sprawie szczegółowego zakresu i form audytu energetycznego, Dz.U. 2009 nr 43 poz. 346, ze zm.). Taki wskaźnik opisuje „typowy” rok. Do porównywania faktur rok do roku potrzebne są stopniodni rzeczywiste – takie jak na tej stronie.</p>

<h2>Jak wykorzystać stopniodni – korekta pogodowa zużycia ciepła</h2>
<p>Zużycie ciepła na ogrzewanie rośnie mniej więcej proporcjonalnie do stopniodni. Jeśli w sezonie z liczbą stopniodni o 10% mniejszą budynek zużył o 10% mniej ciepła, to nie jest oszczędność – to łagodniejsza zima. Uczciwe porównanie wymaga przeliczenia zużycia na tę samą pogodę:</p>
<div class="sd-wz">zużycie skorygowane = zużycie z faktury × (stopniodni sezonu odniesienia ÷ stopniodni sezonu porównywanego)</div>
<p>To uproszczenie dla części zużycia zależnej od pogody. Ciepła woda i straty stałe nie zależą od temperatury zewnętrznej, dlatego <a href="kalkulator-kosztow-ogrzewania.html">kalkulator kosztów ogrzewania</a> wyznacza je osobno z faktur (regresja zgodna z protokołem IPMVP). Całą metodę opisuję w poradniku <a href="poradnik-metoda-stopniodni.html">Metoda stopniodni</a>, a dla Warszawy szczegółowe tabele są na stronie <a href="stopniodni-warszawa.html">Stopniodni Warszawa</a>.</p>

<h2>Skąd są dane</h2>
<p>Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy (dobowe dane synoptyczne, średnia dobowa temperatura powietrza). Dane IMGW-PIB zostały przetworzone: obliczenie stopniodni, uzupełnienie pojedynczych braków wartością z najbliższej stacji. Pomijam stacje wysokogórskie i stacje z ponad 10% uzupełnionych dni. Przeliczenie wykonuje się automatycznie co miesiąc, a pliki z danymi są publicznie dostępne w repozytorium <a href="{GITHUB}" target="_blank" rel="noopener">ProfitEnergy/stopniodni</a> na GitHubie.</p>

<div class="sources"><b>Źródła</b><ul>
<li><a href="https://danepubliczne.imgw.pl/" target="_blank" rel="noopener">IMGW-PIB – dane publiczne (dobowe dane synoptyczne)</a></li>
<li><a href="https://ec.europa.eu/eurostat/cache/metadata/en/nrg_chdd_esms.htm" target="_blank" rel="noopener">Eurostat – metodologia stopniodni grzania i chłodzenia</a></li>
<li><a href="https://api.sejm.gov.pl/eli/acts/DU/2015/1606/text.html" target="_blank" rel="noopener">Rozporządzenie zmieniające rozporządzenie w sprawie audytu energetycznego (Dz.U. 2015 poz. 1606) – wzór na S<sub>d</sub></a></li>
<li><a href="{GITHUB}" target="_blank" rel="noopener">Repozytorium danych ProfitEnergy/stopniodni (GitHub)</a></li></ul></div>
'''
FAQ = [
    ('Co to są stopniodni?', 'Stopniodni (stopniodni grzania, ang. heating degree days, HDD) to miara tego, jak zimny był dany okres. Dla każdego dnia ze średnią temperaturą poniżej 15°C liczy się różnicę 18°C minus ta temperatura i sumuje za miesiąc lub sezon. Im więcej stopniodni, tym więcej ciepła potrzebuje budynek.'),
    ('Jaki jest wzór na stopniodni?', 'Według Eurostatu: HDD = suma (18°C − średnia temperatura dobowa) dla dni, w których średnia temperatura jest niższa niż 15°C. W pozostałe dni stopniodni wynoszą zero. Przykład: dzień ze średnią 2°C to 16 stopniodni.'),
    ('Ile stopniodni ma sezon grzewczy w Polsce?', f'W sezonach {sl(Iw["base"][0])}–{sl(lc)} średnia suma od września do maja wynosiła od ok. {r0(sez_min)} stopniodni ({m_min[0]}) do ok. {r0(sez_max)} ({m_max[0]}) w miastach z tabeli. W Warszawie średnio {r0(Iw["avg_s"])}.'),
    ('Czym różnią się stopniodni z rozporządzenia o audycie energetycznym?', 'W audycie energetycznym liczba stopniodni Sd wynika z projektowej temperatury wewnętrznej i wieloletnich średnich temperatur miesięcznych, więc opisuje typowy rok. Na tej stronie są stopniodni rzeczywiste według Eurostatu, liczone z dobowych temperatur IMGW-PIB – potrzebne do porównywania faktur i korekty pogodowej zużycia.'),
    ('Jak często aktualizowane są dane?', 'Co miesiąc. Po publikacji danych dobowych przez IMGW-PIB (zwykle w pierwszej połowie następnego miesiąca) przeliczenie wykonuje się automatycznie, a tabele na stronie pokazują nowe wartości.'),
    ('Czy mogę pobrać dane o stopniodniach?', f'Tak. Pliki JSON z dobowymi temperaturami i listą stacji są publicznie dostępne w repozytorium {GITHUB}. Przy wykorzystaniu podaj źródło: IMGW-PIB (dane przetworzone).'),
    ('Do czego zarządcy budynków używają stopniodni?', 'Do porównywania zużycia ciepła między sezonami niezależnie od pogody, do weryfikacji efektów termomodernizacji lub sterowania ogrzewaniem oraz do rozliczeń w modelu ESCO, w którym wynagrodzenie zależy od zmierzonej oszczędności.'),
]
page(SLUG, TITLE, DESC, H1, [('Strona główna', './'), ('Poradniki', 'poradniki.html')], 'Dane IMGW · co miesiąc', body, FAQ,
     [dataset(URL + '#miasta', 'Stopniodni grzania dla stacji synoptycznych IMGW-PIB w Polsce', 'Miesięczne i sezonowe sumy stopniodni grzania (baza 18°C, próg 15°C) dla 54 stacji synoptycznych IMGW-PIB, od 2016 r., aktualizowane co miesiąc.', 'Polska'),
      art(URL, H1, DESC, ['stopniodni', 'liczba stopniodni', 'stopniodni grzania', 'wzór na stopniodni', 'sezon grzewczy', 'IMGW-PIB', 'korekta pogodowa zużycia ciepła'])],
     {'typ': 'hub', 'dane_do': DANE_DO, 'miasta': [{'n': n, 'st': sid, 'slug': slug} for n, sid, slug in MIASTA]})

# ===================== WARSZAWA =====================
SLUG = 'stopniodni-warszawa.html'; URL = BASE + SLUG
H1 = 'Stopniodni Warszawa – aktualne dane IMGW, sezony grzewcze i miesiące'
TITLE = 'Stopniodni Warszawa – aktualna liczba stopniodni (IMGW)'
DESC = f'Liczba stopniodni dla Warszawy (stacja IMGW Warszawa-Okęcie): ostatni miesiąc, bieżący sezon, 10 sezonów grzewczych i lata kalendarzowe. Aktualizacja co miesiąc.'
y1, y2 = lc - 1, lc
s1, s2 = Iw['sez'][y1], Iw['sez'][y2]
przykl = 1000 * s2 / s1
maz = [('Płock', '352190360'), ('Siedlce', '352220385'), ('Mława', '353200270'), ('Kozienice', '351210488')]
maz_rows = ''
for n, sid in [('Warszawa', '352200375')] + maz:
    S = load(sid); I = info(S)
    p = pct(I['sez'][lc], I['avg_s'])
    maz_rows += f'<tr><th scope="row">{n}</th><td>{STN[sid]}</td><td>{r0(I["sez"][lc])}</td><td>{r0(I["avg_s"])}</td></tr>'
maz_tab = f'<table><thead><tr><th scope="col">Miejscowość</th><th scope="col">Stacja IMGW</th><th scope="col">Sezon {sl(lc)}</th><th scope="col">Średnia {sl(Iw["base"][0])}–{sl(lc)}</th></tr></thead><tbody>{maz_rows}</tbody></table>'
lata = html_lata(Sw, Iw)
v2025 = r0(sdd(Sw, mstart(2025, 1), mend(2025, 12)))
body = f'''<div class="tldr"><b>W skrócie</b><span id="sd-tldr">{html_tldr(Iw, "w Warszawie", "Warszawa-Okęcie")}</span> Stopniodni liczę metodą Eurostatu (18°C, dni poniżej 15°C) z dobowych temperatur IMGW-PIB; dane dopisują się co miesiąc.</div>
<h2>Stopniodni w Warszawie – najnowsze dane</h2>
<div id="sd-sum">{html_sum(Iw)}</div>
<h2>Porównaj okresy – Warszawa</h2>
<p>Wybierz miesiąc, sezon albo rok (od 2020, najnowsze na górze) i porównaj go z tym samym okresem rok wcześniej, ze średnią z 5 lub 10 lat albo z dowolnym okresem z listy. Wpisz inny kod pocztowy lub miejscowość, a pokażę też najnowsze dane i tabele dla jej stacji.</p>
<div class="sd-pick" id="sd-narz">
<div class="sd-lok"><label for="sd-kod">Kod pocztowy<input id="sd-kod" inputmode="numeric" placeholder="00-000" maxlength="6" autocomplete="postal-code"></label><label for="sd-msc">Miejscowość<input id="sd-msc" autocomplete="off" placeholder="np. Piaseczno" role="combobox" aria-controls="sd-lista" value="Warszawa"></label><ul id="sd-lista" role="listbox" hidden></ul></div>
<p id="sd-stacja" class="sd-do">Wpisz kod pocztowy albo miejscowość – dobiorę najbliższą stację IMGW-PIB.</p>
<div id="sd-tabele"></div>
<div id="sd-por" hidden><div class="sd-sel"><label for="sd-typ">Porównuję<select id="sd-typ"><option value="m">miesiące</option><option value="s">sezony grzewcze (IX–V)</option><option value="r">lata kalendarzowe</option></select></label><label for="sd-a">Okres<select id="sd-a"></select></label><label for="sd-b">Porównaj z<select id="sd-b"></select></label></div><div id="sd-wynik" aria-live="polite"></div></div>
<div id="sd-tabele2"></div></div>
<h2>Liczba stopniodni w sezonach grzewczych – Warszawa</h2>
<p>Suma stopniodni od września do maja, stacja IMGW Warszawa-Okęcie, sezony od {sl(SEZ_OD)}; bieżący sezon na górze. Ostatnia kolumna pokazuje zmianę względem poprzedniego sezonu: plus – zimniej, minus – cieplej.</p>
<div class="tbl" id="sd-sez">{html_sez(Sw, Iw)}</div>
<h2>Stopniodni w Warszawie miesiąc po miesiącu</h2>
<p>Miesiące sezonu grzewczego w pięciu ostatnich pełnych sezonach i w sezonie bieżącym. „–” oznacza miesiąc, dla którego nie ma jeszcze danych.</p>
<div class="tbl" id="sd-mies">{html_mies(Sw, Iw)}</div>
<h2>Stopniodni w latach kalendarzowych</h2>
<p>Warszawa-Okęcie, styczeń–grudzień: <span id="sd-lata">{lata}</span> stopniodni.</p>
<h2>Jak użyć tych liczb do faktur za ciepło w Warszawie</h2>
<p>Przykład (liczby zużycia są umowne): budynek zużył w sezonie {sl(y1)} 1000 GJ na ogrzewanie. Sezon {sl(y1)} miał w Warszawie {r0(s1)} stopniodni, a sezon {sl(y2)} – {r0(s2)}. Przy pogodzie sezonu {sl(y2)} ten sam budynek, bez żadnych zmian, zużyłby ok. 1000 × {r0(s2)} ÷ {r0(s1)} ≈ <b>{r0(przykl)} GJ</b>. Jeśli faktury pokazują mniej – to jest rzeczywista oszczędność. Jeśli więcej – coś w budynku pracuje gorzej.</p>
<p>To uproszczenie dla części zużycia zależnej od pogody. Dokładniej policzy to <a href="kalkulator-kosztow-ogrzewania.html?msc=Warszawa">kalkulator kosztów ogrzewania dla budynku w Warszawie</a> – sam odczyta faktury PDF, oddzieli ciepłą wodę i straty stałe i pokaże potencjał oszczędności.</p>
<h2>Stopniodni na Mazowszu</h2>
<p>Dla budynków poza Warszawą lepiej użyć bliższej stacji. Porównanie sezonu {sl(lc)} na stacjach IMGW w województwie mazowieckim:</p>
<div class="tbl">{maz_tab}</div>
<p>Dane dla wszystkich 54 stacji i 19 miast znajdziesz na stronie <a href="stopniodni.html">Stopniodni w Polsce – raport miesięczny</a>.</p>
<div class="sources"><b>Źródła</b><ul>
<li><a href="https://danepubliczne.imgw.pl/" target="_blank" rel="noopener">IMGW-PIB – dane publiczne (dobowe dane synoptyczne, stacja Warszawa-Okęcie)</a></li>
<li><a href="https://ec.europa.eu/eurostat/cache/metadata/en/nrg_chdd_esms.htm" target="_blank" rel="noopener">Eurostat – metodologia stopniodni grzania</a></li>
<li><a href="{GITHUB}" target="_blank" rel="noopener">Repozytorium danych ProfitEnergy/stopniodni (GitHub)</a></li></ul></div>
<p class="sd-do">Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy. Dane IMGW-PIB zostały przetworzone.</p>
'''
ys = sorted(Iw['base'], key=lambda y: Iw['sez'][y])
FAQ = [
    ('Ile stopniodni ma sezon grzewczy w Warszawie?', f'Średnio {r0(Iw["avg_s"])} stopniodni od września do maja (sezony {sl(Iw["base"][0])}–{sl(lc)}, stacja IMGW Warszawa-Okęcie). Najcieplejszy w tym okresie był sezon {sl(ys[0])} ({r0(Iw["sez"][ys[0]])}), najzimniejszy {sl(ys[-1])} ({r0(Iw["sez"][ys[-1]])}).'),
    (f'Ile wynosiła liczba stopniodni w Warszawie w sezonie {sl(lc)}?', f'{r0(Iw["sez"][lc])} stopniodni od września {lc} do maja {lc + 1} – {ryr(pct(Iw["sez"][lc], Iw["sez"][lc - 1]), f"w sezonie {sl(lc - 1)}", r0(Iw["sez"][lc - 1]))}.'),
    ('Ile stopniodni było w Warszawie w 2025 roku?', f'W roku kalendarzowym 2025 stacja Warszawa-Okęcie dała {v2025} stopniodni (styczeń–grudzień, metoda Eurostatu).'),
    ('Z jakiej stacji IMGW są dane dla Warszawy?', 'Ze stacji synoptycznej IMGW-PIB Warszawa-Okęcie. Jest reprezentatywna dla Warszawy i gmin ościennych; dla budynków dalej na Mazowszu lepiej użyć stacji Płock, Siedlce, Mława lub Kozienice.'),
    ('Jak liczone są stopniodni?', 'Dla każdego dnia ze średnią temperaturą poniżej 15°C liczę różnicę 18°C minus średnia temperatura dobowa i sumuję za miesiąc lub sezon (metoda Eurostatu). Dni cieplejsze nie dodają stopniodni.'),
    ('Jak często aktualizowane są stopniodni dla Warszawy?', 'Co miesiąc, automatycznie po publikacji danych dobowych przez IMGW-PIB.'),
]
page(SLUG, TITLE, DESC, H1, [('Strona główna', './'), ('Poradniki', 'poradniki.html'), ('Stopniodni', 'stopniodni.html')], 'Dane IMGW · Warszawa', body, FAQ,
     [dataset(URL + '#sd-sez', 'Stopniodni grzania – Warszawa (stacja IMGW Warszawa-Okęcie)', 'Miesięczne, sezonowe i roczne sumy stopniodni grzania dla Warszawy (baza 18°C, próg 15°C), od 2016 r., aktualizowane co miesiąc.', 'Warszawa', '352200375'),
      art(URL, H1, DESC, ['stopniodni Warszawa', 'liczba stopniodni Warszawa', 'sezon grzewczy Warszawa', 'IMGW-PIB', 'Warszawa-Okęcie'])],
     {'typ': 'miasto', 'dane_do': DANE_DO, 'st': '352200375', 'mw': 'w Warszawie', 'stn': 'Warszawa-Okęcie', 'start': [52.2297, 21.0122, 'Warszawa']})
