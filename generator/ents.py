import json, re, sys, os
B = 'https://energetycznybroker.pl/'
FIRMA = {"@id": B + "#firma", "@type": "ProfessionalService", "name": "Profit Energy Konrad Bojakowski",
         "alternateName": "PROFIT ENERGY", "url": B, "logo": B + "img/logo-profit-energy-jasne.webp",
         "image": B + "img/konrad-bojakowski.webp", "telephone": "+48722149551", "email": "biuro@energetycznybroker.pl",
         "address": {"@type": "PostalAddress", "addressLocality": "Warszawa", "addressCountry": "PL"},
         "areaServed": {"@type": "Country", "name": "Polska"}, "founder": {"@id": B + "#konrad"},
         "sameAs": ["https://www.facebook.com/ProfitEnergy.Konrad.Bojakowski/", "https://www.linkedin.com/company/profit-energy-konrad-bojakowski/", "https://www.google.com/maps?cid=4109496446711617530"]}
OSOBA = {"@id": B + "#konrad", "@type": "Person", "name": "Konrad Bojakowski", "jobTitle": "Niezależny doradca i broker energetyczny",
         "url": B + "o-mnie.html", "image": B + "img/konrad-bojakowski.webp", "sameAs": ["https://www.linkedin.com/in/konrad-bojakowski/"],
         "worksFor": {"@id": B + "#firma"}}
WITRYNA = {"@id": B + "#witryna", "@type": "WebSite", "url": B, "name": "Profit Energy Konrad Bojakowski", "inLanguage": "pl", "publisher": {"@id": B + "#firma"}}
SKIP = {'index.html', '404.html'}

def blok(f):
    if f in SKIP: return ''
    g = [FIRMA, WITRYNA] + ([] if f == 'o-mnie.html' else [OSOBA])
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False) + '</script>'

def apply(path):
    f = os.path.basename(path); s = open(path, encoding='utf-8').read()
    if f in SKIP or '"@id": "https://energetycznybroker.pl/#firma", "@type"' in s: return False
    s = s.replace('</head>', blok(f) + '\n</head>', 1)
    open(path, 'w', encoding='utf-8').write(s); return True

if __name__ == '__main__':
    n = [os.path.basename(p) for p in sys.argv[1:] if apply(p)]
    print(len(n))
