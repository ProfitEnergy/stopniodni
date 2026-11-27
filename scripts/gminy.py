"""Lista gmin do wyszukiwarki stopniodni dla gminy (dane/gminy.json).
Źródło: dane/miejscowosci/*.json (miejscowość, typ, nr woj., gmina lub '=', lat, lon).
Współrzędne gminy = siedziba (miejscowość o nazwie gminy), a gdy jej brak – środek miejscowości gminy.
Gminy o tej samej nazwie w jednym województwie rozdzielane po siedzibach (opis: najbliższe miasto).
Wynik: [nazwa, nr_woj, lat, lon, dopisek] posortowane alfabetycznie."""
import json, glob, math, collections
def km(a,b,c,d):
    r=math.pi/180;x=math.sin((c-a)*r/2);y=math.sin((d-b)*r/2)
    return 12742*math.asin(math.sqrt(x*x+math.cos(a*r)*math.cos(c*r)*y*y))
rows=[]
for f in sorted(glob.glob('dane/miejscowosci/*.json')):
    if not f.endswith('woj.json'): rows+=json.load(open(f,encoding='utf-8'))
towns=[r for r in rows if r[1]=='M']
g=collections.defaultdict(list)
for r in rows: g[(r[0] if r[3]=='=' else r[3], r[2])].append(r)
out=[]
for (gm,w),L in g.items():
    seeds=[r for r in L if r[0]==gm and r[3]=='=']
    # siedziby rozproszone > 25 km = osobne gminy o tej samej nazwie
    uniq=[]
    for s in seeds:
        if all(km(s[4],s[5],u[4],u[5])>25 for u in uniq): uniq.append(s)
    if len(uniq)<=1:
        if uniq: la,lo=uniq[0][4],uniq[0][5]
        else: la=sum(r[4] for r in L)/len(L); lo=sum(r[5] for r in L)/len(L)
        out.append([gm,w,round(la,3),round(lo,3),''])
    else:
        for s in uniq:
            near=min((t for t in towns if t[0]!=gm), key=lambda t:km(s[4],s[5],t[4],t[5]))
            out.append([gm,w,round(s[4],3),round(s[5],3),'okolice: '+near[0]])
out.sort(key=lambda x:(x[0].lower(),x[1]))
json.dump(out,open('dane/gminy.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(out),'gmin;', sum(1 for x in out if x[4]),'z dopiskiem')
