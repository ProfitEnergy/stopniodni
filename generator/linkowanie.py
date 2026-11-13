import re, os, sys, html
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
L = {  # adres: (krótka nazwa linku, jedno zdanie)
 'water-ai.html': ('Water AI – niższe koszty ogrzewania bez inwestycji', 'Sterowanie predykcyjne w modelu ESCO, płatność z oszczędności.'),
 'wspolnoty-i-spoldzielnie.html': ('Energia i ciepło dla wspólnot i spółdzielni', 'Prąd, gaz i koszty ogrzewania budynków mieszkalnych.'),
 'prad-i-gaz-dla-firm.html': ('Prąd i gaz dla firm', 'Przetarg między sprzedawcami, wybór produktu, zmiana sprzedawcy.'),
 'dla-zakladow.html': ('Energia dla zakładów produkcyjnych', 'Dystrybucja, moc umowna, moc bierna, DSR.'),
 'kalkulator-kosztow-ogrzewania.html': ('Kalkulator kosztów ogrzewania', 'Zużycie i koszt ciepła z faktur, z korektą pogodową.'),
 'stopniodni.html': ('Stopniodni w Polsce – dane IMGW', 'Ostatni miesiąc i sezon rok do roku, Twoja miejscowość.'),
 'stopniodni-warszawa.html': ('Stopniodni Warszawa', 'Sezony grzewcze, miesiące i porównania dla Warszawy.'),
 'poradnik-metoda-stopniodni.html': ('Metoda stopniodni – jak policzyć oszczędność', 'Korekta pogodowa zużycia ciepła krok po kroku.'),
 'poradnik-ogrzewanie-wspolnoty.html': ('Ogrzewanie wspólnoty bez inwestycji', 'Jak wspólnota może obniżyć koszty ogrzewania.'),
 'poradnik-oplaty-za-cieplo-spoldzielnia.html': ('Opłaty za ciepło w spółdzielni i wspólnocie', 'Z czego się składają i jak je obniżyć.'),
 'poradnik-ogrzewanie-szpitala.html': ('Ogrzewanie szpitala bez inwestycji', 'Oszczędność na sterowaniu, nie na temperaturze.'),
 'poradnik-ogrzewanie-hotelu.html': ('Ogrzewanie hotelu bez inwestycji', 'Ciepło przy pustych pokojach i zmiennym obłożeniu.'),
 'poradnik-ogrzewanie-biurowca.html': ('Ogrzewanie biurowca bez inwestycji', 'Ciepło poza godzinami pracy, strefy i BMS.'),
 'poradnik-ogrzewanie-szkol-i-urzedow.html': ('Ogrzewanie szkół i urzędów', 'Grzanie pustych budynków w ferie i weekendy.'),
 'poradnik-ogrzewanie-basenu.html': ('Ciepło na basenie', 'Hala, niecka, prysznice i kamień w wymiennikach.'),
 'poradnik-water-ai-czy-budynek-sie-nadaje.html': ('Czy budynek nadaje się do Water AI', 'Jak sprawdzić potencjał oszczędności na ogrzewaniu.'),
 'poradnik-predykcja-hydraulika-scat.html': ('Predykcja, hydraulika i SCAT', 'Jak trzy technologie obniżają zużycie ciepła.'),
 'poradnik-kamien-kotlowy-spoldzielnia.html': ('Kamień kotłowy w węźle i instalacji c.w.u.', 'Jak go ograniczyć w bloku.'),
 'poradnik-plukanie-instalacji-co-blok.html': ('Płukanie instalacji c.o. w bloku', 'Kiedy jest konieczne i jak ograniczyć osady.'),
 'poradnik-biale-certyfikaty-spoldzielnia.html': ('Białe certyfikaty dla spółdzielni i wspólnot', 'Kto może je dostać, ile są warte, jak złożyć wniosek.'),
 'poradnik-faktura-za-prad.html': ('Jak czytać fakturę za prąd', 'Pozycje sprzedaży i dystrybucji na fakturze firmy.'),
 'poradnik-zmiana-sprzedawcy-pradu.html': ('Zmiana sprzedawcy prądu krok po kroku', 'Terminy, dokumenty i wypowiedzenie umowy.'),
 'poradnik-cena-stala-czy-indeks.html': ('Cena stała, indeks czy transze', 'Jak wybrać produkt energii dla firmy.'),
 'poradnik-grupa-taryfowa.html': ('Grupa taryfowa w firmie', 'C11, C12a, C12b, C21 czy C22a – która się opłaca.'),
 'poradnik-osd-operator-systemu-dystrybucyjnego.html': ('OSD – operator systemu dystrybucyjnego', 'Co robi i dlaczego zostaje przy zmianie sprzedawcy.'),
 'poradnik-terminy-energetyczne.html': ('Kalendarz terminów energetycznych', 'Daty, których firma nie może przegapić.'),
 'poradnik-grupy-taryfowe-gazu.html': ('Grupy taryfowe gazu dla firm', 'Kwalifikacja i zmiana grupy.'),
 'poradnik-rachunek-za-gaz-firma.html': ('Rachunek za gaz w firmie', 'Z czego się składa i co obniżyć.'),
 'poradnik-moc-umowna.html': ('Moc umowna w firmie', 'Jak sprawdzić, czy przepłacasz.'),
 'poradnik-energia-bierna.html': ('Moc bierna i kompensacja', 'Jak obniżyć opłaty za moc bierną.'),
 'poradnik-dsr.html': ('DSR – przychód dla firmy', 'Jak zarabiać na gotowości do ograniczenia poboru mocy.'),
}
SEG = ['poradnik-ogrzewanie-wspolnoty.html', 'poradnik-ogrzewanie-szpitala.html', 'poradnik-ogrzewanie-hotelu.html', 'poradnik-ogrzewanie-biurowca.html', 'poradnik-ogrzewanie-szkol-i-urzedow.html', 'poradnik-ogrzewanie-basenu.html']
TECH = ['poradnik-metoda-stopniodni.html', 'poradnik-oplaty-za-cieplo-spoldzielnia.html', 'poradnik-water-ai-czy-budynek-sie-nadaje.html', 'poradnik-predykcja-hydraulika-scat.html', 'poradnik-kamien-kotlowy-spoldzielnia.html', 'poradnik-plukanie-instalacji-co-blok.html', 'poradnik-biale-certyfikaty-spoldzielnia.html']
PRAD = ['poradnik-faktura-za-prad.html', 'poradnik-zmiana-sprzedawcy-pradu.html', 'poradnik-cena-stala-czy-indeks.html', 'poradnik-grupa-taryfowa.html', 'poradnik-osd-operator-systemu-dystrybucyjnego.html', 'poradnik-terminy-energetyczne.html', 'poradnik-grupy-taryfowe-gazu.html', 'poradnik-rachunek-za-gaz-firma.html']
ZAKL = ['poradnik-moc-umowna.html', 'poradnik-energia-bierna.html', 'poradnik-dsr.html', 'poradnik-grupa-taryfowa.html', 'poradnik-osd-operator-systemu-dystrybucyjnego.html']
HEAT = set(SEG + TECH)

def rel(p):  # lista powiązanych dla poradnika
    if p in SEG:
        r = ['water-ai.html'] + [x for x in SEG if x != p] + ['poradnik-metoda-stopniodni.html', 'poradnik-predykcja-hydraulika-scat.html']
        if p == 'poradnik-ogrzewanie-wspolnoty.html': r.insert(1, 'wspolnoty-i-spoldzielnie.html')
    elif p in TECH:
        r = ['water-ai.html', 'wspolnoty-i-spoldzielnie.html'] + [x for x in TECH if x != p] + ['poradnik-ogrzewanie-wspolnoty.html']
    elif p in ZAKL and p not in PRAD:
        r = ['dla-zakladow.html'] + [x for x in ZAKL if x != p] + ['poradnik-faktura-za-prad.html']
    else:
        r = ['prad-i-gaz-dla-firm.html'] + [x for x in PRAD if x != p]
        if p in ZAKL: r.insert(1, 'dla-zakladow.html'); r += ['poradnik-moc-umowna.html']
    seen = []; [seen.append(x) for x in r if x not in seen and x != p]
    return seen[:9]

CSS = '''<style>.pe-cols{display:grid;grid-template-columns:minmax(0,760px) 300px;gap:56px;align-items:start}.pe-side{display:grid;gap:16px;position:sticky;top:96px}.pe-card{border:1px solid var(--line);border-radius:14px;padding:18px;background:var(--card,#fff)}.pe-card.k{border:2px solid var(--volt);box-shadow:0 10px 28px rgba(0,0,0,.08);display:grid;gap:10px}.pe-card small{font-size:.74rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}.pe-card strong{font-size:1.2rem;line-height:1.25}.pe-card p{margin:0;font-size:.92rem;line-height:1.45}.pe-card .btn{width:100%;padding:14px 16px;font-weight:700}.pe-card ul{list-style:none;margin:8px 0 0;padding:0;display:grid;gap:2px}.pe-card li a{display:block;padding:7px 0;border-bottom:1px solid var(--line);text-decoration:none;color:var(--fg);font-size:.93rem;line-height:1.35}.pe-card li:last-child a{border-bottom:0}.pe-card li a:hover{color:var(--muted)}.pe-sd{display:block;font-weight:600;font-size:.93rem;color:var(--fg)}.pe-mk{display:none}
@media(max-width:1120px){.pe-cols{grid-template-columns:1fr;gap:28px}.pe-side{position:static}.pe-side .pe-card.k{display:none}.pe-mk{display:grid;margin:14px 0}}
.pe-g{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin-top:18px}.pe-g a{display:grid;gap:6px;padding:16px 18px;border:1px solid var(--line);border-radius:14px;text-decoration:none;color:var(--fg);background:var(--card,#fff)}.pe-g a:hover{border-color:var(--volt)}.pe-g b{font-size:1.02rem;line-height:1.3}.pe-g span{font-size:.9rem;color:var(--muted);line-height:1.4}</style>'''

def kcard(cls='pe-card k'):
    return (f'<div class="{cls}"><small>Kalkulator kosztów ogrzewania</small><strong>Czy Twój budynek zużywa za dużo ciepła?</strong>'
            '<p>Wgraj faktury za ciepło w PDF. Kalkulator przeliczy zużycie przez stopniodni z najbliższej stacji IMGW i pokaże potencjał oszczędności.</p>'
            '<a class="btn primary" href="kalkulator-kosztow-ogrzewania.html">Sprawdź swoje faktury →</a>'
            '<a class="pe-sd" href="stopniodni.html">Stopniodni dla Twojej miejscowości →</a></div>')

def acard():
    return ('<div class="pe-card k"><small>Bezpłatna analiza</small><strong>Ile przepłacasz na fakturze?</strong>'
            '<p>Wyślij ostatnią fakturę za prąd lub gaz. Sprawdzę cenę, grupę taryfową, moc umowną i opłaty dystrybucyjne.</p>'
            '<a class="btn primary" href="kontakt.html">Wyślij fakturę do analizy →</a></div>')

def tcard(items, tytul='W tym temacie'):
    return f'<div class="pe-card"><small>{tytul}</small><ul>' + ''.join(f'<li><a href="{x}">{L[x][0]}</a></li>' for x in items) + '</ul></div>'

def grid(items):
    return '<div class="pe-g">' + ''.join(f'<a href="{x}"><b>{L[x][0]}</b><span>{L[x][1]}</span></a>' for x in items) + '</div>'

def section(h, intro, items):
    return f'<section class="tight pe-rel"><div class="wrap"><h2>{h}</h2><p>{intro}</p>{grid(items)}</div></section>'

HUBS = {
 'water-ai.html': ('Poradniki o kosztach ogrzewania', 'Jak obniżyć koszty ciepła w konkretnym typie budynku i jak uczciwie zmierzyć oszczędność.', SEG + TECH[1:] + ['poradnik-metoda-stopniodni.html', 'kalkulator-kosztow-ogrzewania.html', 'stopniodni.html']),
 'wspolnoty-i-spoldzielnie.html': ('Poradniki dla zarządów wspólnot i spółdzielni', 'Ciepło, prąd i rozliczenia w budynkach mieszkalnych – konkretnie, z liczbami z faktur.', ['poradnik-ogrzewanie-wspolnoty.html', 'poradnik-oplaty-za-cieplo-spoldzielnia.html', 'poradnik-kamien-kotlowy-spoldzielnia.html', 'poradnik-plukanie-instalacji-co-blok.html', 'poradnik-biale-certyfikaty-spoldzielnia.html', 'poradnik-metoda-stopniodni.html', 'poradnik-water-ai-czy-budynek-sie-nadaje.html', 'poradnik-faktura-za-prad.html', 'poradnik-zmiana-sprzedawcy-pradu.html', 'kalkulator-kosztow-ogrzewania.html', 'stopniodni-warszawa.html', 'water-ai.html']),
 'prad-i-gaz-dla-firm.html': ('Poradniki: prąd i gaz w firmie', 'Zanim podpiszesz nową umowę – co sprawdzić na fakturze i w ofercie.', PRAD + ['poradnik-moc-umowna.html']),
 'dla-zakladow.html': ('Poradniki dla zakładów produkcyjnych', 'Opłaty dystrybucyjne, moc i dodatkowe przychody – tam leżą największe pieniądze w zakładzie.', ZAKL + ['poradnik-faktura-za-prad.html', 'poradnik-cena-stala-czy-indeks.html', 'prad-i-gaz-dla-firm.html', 'water-ai.html']),
 'o-mnie.html': ('Czym się zajmuję', 'Jeden doradca do całej faktury: energia, dystrybucja, ciepło i DSR.', ['prad-i-gaz-dla-firm.html', 'dla-zakladow.html', 'water-ai.html', 'wspolnoty-i-spoldzielnie.html', 'kalkulator-kosztow-ogrzewania.html', 'stopniodni.html']),
 'index.html': ('Narzędzia i najczęściej czytane poradniki', 'Sprawdź swoje koszty sam albo przeczytaj, jak to robię.', ['kalkulator-kosztow-ogrzewania.html', 'stopniodni.html', 'poradnik-metoda-stopniodni.html', 'poradnik-ogrzewanie-wspolnoty.html', 'poradnik-faktura-za-prad.html', 'poradnik-moc-umowna.html', 'poradnik-cena-stala-czy-indeks.html', 'poradnik-dsr.html']),
}
done = []
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.html'): continue
    s = open(os.path.join(SRC, f), encoding='utf-8').read(); o = s
    if 'pe-cols' in s or 'pe-rel' in s: sys.exit('już zmienione: ' + f)
    if f.startswith('poradnik-'):
        a = '<section class="tight"><div class="wrap"><article class="article">'
        assert s.count(a) == 1, f
        s = s.replace(a, '<section class="tight"><div class="wrap pe-cols"><article class="article">')
        side = (kcard() if f in HEAT else acard()) + tcard(rel(f))
        s = s.replace('</article>', '</article><aside class="pe-side" aria-label="Powiązane">' + side + '</aside>', 1)
        if f in HEAT:  # karta kalkulatora pod „W skrócie” na telefonie
            i = s.index('<div class="tldr">'); j = s.index('</div>', i) + 6
            s = s[:j] + kcard('pe-card k pe-mk') + s[j:]
    elif f in HUBS:
        h, intro, items = HUBS[f]
        items = [x for x in dict.fromkeys(items) if x != f]
        sec = section(h, intro, items)
        k = s.rfind('<section class="tight"><div class="wrap"><div class="ctaband">')
        if k < 0: k = s.index('<footer class="foot">')
        s = s[:k] + sec + s[k:]
    if s != o:
        s = s.replace('</head>', CSS + '\n</head>', 1)
        open(os.path.join(OUT, f), 'w', encoding='utf-8').write(s); done.append(f)
print(len(done), done)
