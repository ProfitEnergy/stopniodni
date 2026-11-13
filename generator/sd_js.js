(function(){
// Stopniodni – odświeżanie danych, wyszukiwanie miejscowości/kodu i porównywarka okresów (lustrzane do sd_core.py)
var CDN='https://cdn.jsdelivr.net/gh/ProfitEnergy/stopniodni@main/dane/',LOC='dane/';
function getJSON(f){return fetch(CDN+f).then(function(r){if(!r.ok)throw 0;return r.json();}).catch(function(){return fetch(LOC+f).then(function(r){if(!r.ok)throw 0;return r.json();});});}
var MIES=['styczeń','luty','marzec','kwiecień','maj','czerwiec','lipiec','sierpień','wrzesień','październik','listopad','grudzień'];
var MIES_L=['styczniu','lutym','marcu','kwietniu','maju','czerwcu','lipcu','sierpniu','wrześniu','październiku','listopadzie','grudniu'];
var MIES_D=['stycznia','lutego','marca','kwietnia','maja','czerwca','lipca','sierpnia','września','października','listopada','grudnia'];
var SEZ_M=[9,10,11,12,1,2,3,4,5];
function $(i){return document.getElementById(i);}
function dn(iso){var p=iso.split('-');return Date.UTC(+p[0],+p[1]-1,+p[2])/864e5;}
function dd(n){return new Date(n*864e5);}
function ms(y,m){return Date.UTC(y,m-1,1)/864e5;}
function me(y,m){return Date.UTC(y,m,1)/864e5-1;}
function sdd(S,a,b){var s=0;for(var x=a;x<=b;x++){var i=x-S.od;if(i<0||i>=S.t.length||S.t[i]==null)return null;var T=S.t[i]/10;if(T<15)s+=18-T;}return s;}
function r0(v){return v==null?'–':String(Math.floor(v+0.5));}
function pct(v,a){return Math.floor((v/a-1)*100+0.5);}
function sl(y){return y+'/'+String(y+1).slice(2);}
function pdat(n){var d=dd(n);return d.getUTCDate()+' '+MIES_D[d.getUTCMonth()]+' '+d.getUTCFullYear();}
function cap(s){return s.charAt(0).toUpperCase()+s.slice(1);}
function sg(p){return (p>0?'+':'')+p;}
function ryr(p,ref,val){if(p===0)return 'tyle samo co '+ref+' ('+val+')';return 'o '+Math.abs(p)+'% '+(p<0?'mniej':'więcej')+' niż '+ref+' ('+val+'), czyli '+(p<0?'cieplej':'zimniej');}
function info(S){var end=S.od+S.t.length-1,e=dd(end),Y=e.getUTCFullYear(),M=e.getUTCMonth()+1,ly,lm;
 if(end===me(Y,M)){ly=Y;lm=M;}else if(M>1){ly=Y;lm=M-1;}else{ly=Y-1;lm=12;}
 var ps=M>=9?Y:(M<=5?Y-1:null),lc=ps!==null?ps-1:Y-1,base=[],sez={},sum=0,y;
 for(y=lc-9;y<=lc;y++){base.push(y);sez[y]=sdd(S,ms(y,9),me(y+1,5));sum+=sez[y];}
 var I={end:end,ly:ly,lm:lm,ps:ps,lc:lc,base:base,sez:sez,avg_s:sum/10};
 I.lv=sdd(S,ms(ly,lm),me(ly,lm));var la=0;for(y=ly-10;y<ly;y++)la+=sdd(S,ms(y,lm),me(y,lm));I.la=la/10;I.lp=pct(I.lv,I.la);
 I.ly0=sdd(S,ms(ly-1,lm),me(ly-1,lm));I.lpy=pct(I.lv,I.ly0);sez[lc-10]=sdd(S,ms(lc-10,9),me(lc-9,5));
 if(ps!==null){var a=ms(ps,9),b=Math.min(end,me(ps+1,5)),off=b-a,pa=0;I.pv=sdd(S,a,b);base.forEach(function(y){pa+=sdd(S,ms(y,9),ms(y,9)+off);});I.pa=pa/10;I.pp=pct(I.pv,I.pa);I.pb=b;
  I.pv0=sdd(S,ms(ps-1,9),ms(ps-1,9)+off);I.ppy=pct(I.pv,I.pv0);}
 return I;}
function htmlSum(I){var o='<ul class="sd-sum">';
 o+='<li><b>'+cap(MIES[I.lm-1])+' '+I.ly+':</b> '+r0(I.lv)+' stopniodni – '+ryr(I.lpy,'w '+MIES_L[I.lm-1]+' '+(I.ly-1),r0(I.ly0))+'.</li>';
 if(I.ps!==null)o+='<li><b>Sezon grzewczy '+sl(I.ps)+' od 1 września do '+pdat(I.pb)+':</b> '+r0(I.pv)+' stopniodni – '+ryr(I.ppy,'w tym samym okresie sezonu '+sl(I.ps-1),r0(I.pv0))+'.</li>';
 else{var lcv=I.sez[I.lc],pr=I.sez[I.lc-1];o+='<li><b>Sezon grzewczy '+sl(I.lc)+' (wrzesień–maj):</b> '+r0(lcv)+' stopniodni – '+ryr(pct(lcv,pr),'w sezonie '+sl(I.lc-1),r0(pr))+'.</li>';}
 return o+'</ul>';}
function htmlSez(S,I){var o='<table><thead><tr><th scope="col">Sezon grzewczy</th><th scope="col">Stopniodni IX–V</th><th scope="col">Zmiana do poprzedniego sezonu</th></tr></thead><tbody>';
 if(I.ps!==null)o+='<tr><th scope="row">'+sl(I.ps)+' (do '+pdat(I.pb)+')</th><td>'+r0(I.pv)+'</td><td>'+sg(I.ppy)+'% wobec tego samego okresu '+sl(I.ps-1)+'</td></tr>';
 I.base.slice().reverse().forEach(function(y){o+='<tr><th scope="row">'+sl(y)+'</th><td>'+r0(I.sez[y])+'</td><td>'+sg(pct(I.sez[y],I.sez[y-1]))+'%</td></tr>';});
 o+='<tr><th scope="row">Średnia '+sl(I.base[0])+'–'+sl(I.lc)+'</th><td><b>'+r0(I.avg_s)+'</b></td><td>–</td></tr>';
 return o+'</tbody></table>';}
function htmlMies(S,I){var cols=[],y;for(y=I.lc-4;y<=I.lc;y++)cols.push(y);if(I.ps!==null)cols.push(I.ps);
 var o='<table><thead><tr><th scope="col">Miesiąc</th>'+cols.map(function(y){return '<th scope="col">'+sl(y)+'</th>';}).join('')+'<th scope="col">Średnia '+sl(I.base[0])+'–'+sl(I.lc)+'</th></tr></thead><tbody>';
 SEZ_M.forEach(function(m){o+='<tr><th scope="row">'+MIES[m-1]+'</th>';
  cols.forEach(function(y){var yy=m>=9?y:y+1;o+='<td>'+r0(me(yy,m)<=I.end?sdd(S,ms(yy,m),me(yy,m)):null)+'</td>';});
  var av=0;I.base.forEach(function(y){var yy=m>=9?y:y+1;av+=sdd(S,ms(yy,m),me(yy,m));});o+='<td><b>'+r0(av/10)+'</b></td></tr>';});
 return o+'</tbody></table>';}
function htmlLata(S,I){var Y=dd(I.end).getUTCFullYear(),out=[];for(var y=Y-10;y<Y;y++){var v=sdd(S,ms(y,1),me(y,12));if(v!=null)out.push(y+' – '+r0(v));}return out.join(', ');}
function htmlTldr(I,mw,st){var t=cap(MIES[I.lm-1])+' '+I.ly+' '+mw+' (stacja IMGW '+st+'): '+r0(I.lv)+' stopniodni, '+ryr(I.lpy,'w '+MIES_L[I.lm-1]+' '+(I.ly-1),r0(I.ly0))+'.';
 if(I.ps!==null)t+=' Sezon grzewczy '+sl(I.ps)+' do '+pdat(I.pb)+': '+r0(I.pv)+' stopniodni wobec '+r0(I.pv0)+' w tym samym okresie sezonu '+sl(I.ps-1)+'.';return t;}
function hubRow(c,I){var s='<tr><th scope="row">'+(c.slug?'<a href="stopniodni-'+c.slug+'.html">'+c.n+'</a>':c.n)+'</th><td>'+r0(I.lv)+'</td><td>'+r0(I.la)+'</td><td>'+sg(I.lp)+'%</td>';
 if(I.ps!==null)s+='<td>'+r0(I.pv)+'</td><td>'+r0(I.pa)+'</td><td>'+sg(I.pp)+'%</td>';
 else{var lcv=I.sez[I.lc];s+='<td>'+r0(lcv)+'</td><td>'+r0(I.avg_s)+'</td><td>'+sg(pct(lcv,I.avg_s))+'%</td>';}return s+'</tr>';}
function hubHead(I){var sez,sav;if(I.ps!==null){var d=dd(I.pb),ds=d.getUTCDate()+'.'+('0'+(d.getUTCMonth()+1)).slice(-2);sez='Sezon '+sl(I.ps)+' (1.09–'+ds+')';sav='Średnia 1.09–'+ds+' z 10 sezonów';}else{sez='Sezon '+sl(I.lc);sav='Średnia 10 sezonów';}
 return '<table><thead><tr><th scope="col">Miasto</th><th scope="col">'+cap(MIES[I.lm-1])+' '+I.ly+'</th><th scope="col">Średnia '+(I.ly-10)+'–'+(I.ly-1)+'</th><th scope="col">Różnica</th><th scope="col">'+sez+'</th><th scope="col">'+sav+'</th><th scope="col">Różnica</th></tr></thead><tbody>';}
function set(id,h,txt){var e=$(id);if(!e)return;if(txt)e.textContent=h;else e.innerHTML=h;}
function ser(d){return {od:dn(d.od),t:d.t};}
var cfg=$('sd-cfg');if(!cfg)return;var C=JSON.parse(cfg.textContent);

// ---------- porównywarka okresów ----------
function okresy(typ,S){var end=S.od+S.t.length-1,e=dd(end),Y=e.getUTCFullYear(),M=e.getUTCMonth()+1,L=[],y,m;
 if(typ==='m'){for(y=Y;y>=2016;y--)for(m=12;m>=1;m--){if(me(y,m)>end)continue;L.push({id:y+'-'+m,y:y,m:m,a:ms(y,m),b:me(y,m),full:true,n:MIES[m-1]+' '+y});}}
 else if(typ==='s'){for(y=(M>=9?Y:Y-1);y>=2015;y--){if(ms(y,9)>end)continue;var b=Math.min(end,me(y+1,5));L.push({id:'s'+y,y:y,a:ms(y,9),b:b,full:b===me(y+1,5),n:'sezon '+sl(y)+(b<me(y+1,5)?' (do '+pdat(b)+')':' (IX–V)')});}}
 else{for(y=Y;y>=2015;y--){var b2=Math.min(end,me(y,12));if(ms(y,1)>end)continue;L.push({id:'r'+y,y:y,a:ms(y,1),b:b2,full:b2===me(y,12),n:'rok '+y+(b2<me(y,12)?' (do '+pdat(b2)+')':'')});}}
 return L;}
function wartosc(S,P,A){// P – okres porównawczy; jeśli A niepełny, bierzemy ten sam fragment okresu P
 if(A.full)return sdd(S,P.a,P.b);return sdd(S,P.a,P.a+(A.b-A.a));}
function pokazPor(){var box=$('sd-wynik');if(!box||!ST)return;var S=ST.S,typ=$('sd-typ').value,L=okresy(typ,S),A=L.filter(function(o){return o.id===$('sd-a').value;})[0];if(!A)return;
 var tryb=$('sd-b').value,va=sdd(S,A.a,A.b),vb=null,nb='',i,cnt=0,sum=0;
 var idx=L.indexOf(A),prev=L.filter(function(o){return (typ==='m'?(o.m===A.m&&o.y<A.y):o.y<A.y);});
 if(tryb==='rok'){var P=prev[0];if(P){vb=wartosc(S,P,A);nb=P.n.replace(/ \(.*\)$/,'')+(A.full?'':' (ten sam fragment)');}}
 else if(tryb==='s10'||tryb==='s5'){var N=tryb==='s10'?10:5;for(i=0;i<prev.length&&cnt<N;i++){var v=wartosc(S,prev[i],A);if(v!=null){sum+=v;cnt++;}}if(cnt===N){vb=sum/N;nb='średnia '+N+' poprzednich lat ('+prev[N-1].n.replace(/ \(.*\)$/,'').replace(/^(sezon|rok) /,'')+'–'+prev[0].n.replace(/ \(.*\)$/,'').replace(/^(sezon|rok) /,'')+')';}}
 else{var Q=L.filter(function(o){return o.id===tryb;})[0];if(Q){vb=wartosc(S,Q,A);nb=Q.n.replace(/ \(.*\)$/,'')+(A.full?'':' (ten sam fragment)');}}
 var h='<div class="sd-wyn"><div><span>'+cap(A.n)+'</span><b>'+r0(va)+'</b></div><div><span>'+(nb?cap(nb):'porównanie')+'</span><b>'+r0(vb)+'</b></div>';
 if(va!=null&&vb!=null&&vb>0){var p=pct(va,vb);h+='<div class="sd-roz '+(p<0?'cie':'zim')+'"><span>Różnica</span><b>'+sg(p)+'%</b></div></div>';
  h+='<p>'+(p===0?'Pogoda w obu okresach była praktycznie taka sama.':(p<0?'Było cieplej':'Było zimniej')+' o '+Math.abs(p)+'%. Przy takiej samej pracy instalacji zużycie ciepła na ogrzewanie powinno być w przybliżeniu o tyle '+(p<0?'niższe':'wyższe')+'. Jeśli faktury pokazują coś innego, budynek zużywa ciepło gorzej lub lepiej niż wynikałoby z pogody.')+'</p>';}
 else h+='</div><p>Brak pełnych danych do tego porównania – wybierz inny okres.</p>';
 box.innerHTML=h;}
function wypelnij(){if(!ST)return;var S=ST.S,typ=$('sd-typ').value,L=okresy(typ,S),a=$('sd-a'),b=$('sd-b'),stary=a.value;
 a.innerHTML=L.map(function(o){return '<option value="'+o.id+'">'+cap(o.n)+'</option>';}).join('');if(L.some(function(o){return o.id===stary;}))a.value=stary;
 var bo='<option value="rok">'+(typ==='m'?'rok wcześniej':typ==='s'?'poprzedni sezon':'poprzedni rok')+'</option><option value="s10">średnia 10 poprzednich lat</option><option value="s5">średnia 5 poprzednich lat</option><optgroup label="wybrany okres">'+L.map(function(o){return '<option value="'+o.id+'">'+cap(o.n)+'</option>';}).join('')+'</optgroup>';
 var sb=b.value;b.innerHTML=bo;if([].some.call(b.options,function(o){return o.value===sb;}))b.value=sb;pokazPor();}
var ST=null,META=null,WOJ=null,cacheL={},cacheK={};
function km(a,b,c,d){var r=Math.PI/180,x=Math.sin((c-a)*r/2),y=Math.sin((d-b)*r/2);return 12742*Math.asin(Math.sqrt(x*x+Math.cos(a*r)*Math.cos(c*r)*y*y));}
function norm(s){return s.toLowerCase().replace(/ł/g,'l').normalize('NFD').replace(/[̀-ͯ]/g,'');}
function ustawStacje(lat,lon,opis){if(!META)return;var best=null;META.stacje.forEach(function(s){var d=km(lat,lon,s.lat,s.lon);if(!best||d<best.d)best={s:s,d:d};});
 set('sd-stacja','Stacja IMGW '+best.s.n+' – ok. '+Math.round(best.d)+' km od: '+opis+'.'+(best.d>60?' Stacja jest daleko – wynik orientacyjny.':''),true);
 getJSON('stopniodni/'+best.s.id+'.json').then(function(d){ST={s:best.s,S:ser(d)};var I=info(ST.S);
  var t=$('sd-tabele');if(t){t.innerHTML='<details><summary>Tabele dla stacji '+best.s.n+': sezony i miesiące</summary><h4>Sezony grzewcze</h4><div class="tbl">'+htmlSez(ST.S,I)+'</div><h4>Miesiące sezonu grzewczego</h4><div class="tbl">'+htmlMies(ST.S,I)+'</div><p>Lata kalendarzowe: '+htmlLata(ST.S,I)+' stopniodni.</p></details>';}
  $('sd-por').hidden=false;wypelnij();});}
function wojZKodu(k){var n=parseInt(k.slice(0,2),10);if(isNaN(n))return -1;var t=[[0,9,6],[10,14,13],[15,19,9],[20,24,2],[25,29,12],[30,34,5],[35,39,8],[40,44,11],[45,49,7],[50,59,0],[60,64,14],[65,69,3],[70,78,15],[80,84,10],[85,89,1],[90,99,4]];for(var i=0;i<t.length;i++)if(n>=t[i][0]&&n<=t[i][1])return t[i][2];return -1;}
function initSzukaj(){var inp=$('sd-msc'),kod=$('sd-kod'),list=$('sd-lista');if(!inp)return;
 function opis(r){return r[0]+' ('+(r[1]==='M'?'miasto':r[1]==='W'?'wieś':'osada')+(r[3]==='='?'':', gm. '+r[3])+(WOJ?', woj. '+WOJ[r[2]]:'')+')';}
 function pokaz(items){list.innerHTML='';if(!items.length){list.hidden=true;return;}items.forEach(function(r){var li=document.createElement('li');li.setAttribute('role','option');li.textContent=opis(r);li.addEventListener('mousedown',function(e){e.preventDefault();inp.value=r[0];list.hidden=true;ustawStacje(r[4],r[5],opis(r));});list.appendChild(li);});list.hidden=false;}
 function kand(q,cb){q=norm(q.trim());if(q.length<2)return cb([]);var k=q[0];if(!/[a-z]/.test(k))return cb([]);
  var go=function(arr){var wk=wojZKodu(kod.value.replace(/\D/g,''));var res=arr.filter(function(r){return norm(r[0]).indexOf(q)===0;});res.sort(function(a,b){var ea=norm(a[0])===q?0:1,eb=norm(b[0])===q?0:1;if(ea!==eb)return ea-eb;var wa=a[2]===wk?0:1,wb=b[2]===wk?0:1;if(wa!==wb)return wa-wb;var o={M:0,W:1,O:2};return o[a[1]]-o[b[1]];});cb(res);};
  if(cacheL[k])go(cacheL[k]);else getJSON('miejscowosci/'+k+'.json').then(function(a){cacheL[k]=a;go(a);}).catch(function(){cb([]);});}
 inp.addEventListener('input',function(){kand(inp.value,function(r){pokaz(r.slice(0,12));});});
 inp.addEventListener('blur',function(){setTimeout(function(){list.hidden=true;},150);});
 inp.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();kand(inp.value,function(r){if(r.length){inp.value=r[0][0];list.hidden=true;ustawStacje(r[0][4],r[0][5],opis(r[0]));}});}});
 kod.addEventListener('input',function(){var v=kod.value.replace(/\D/g,'');if(v.length>2&&kod.value.indexOf('-')<0){kod.value=v.slice(0,2)+'-'+v.slice(2,5);}
  if(v.length===5){var k=v.slice(0,2)+'-'+v.slice(2),c=v[0];var go=function(m){var r=m&&m[k];if(r){if(!inp.value)inp.value=r[2];ustawStacje(r[0],r[1],'kod '+k+(r[2]?' ('+r[2]+')':''));}else if(!ST)set('sd-stacja','Nie znam kodu '+k+' – wpisz miejscowość.',true);};
   if(cacheK[c]!==undefined)go(cacheK[c]);else getJSON('kody/'+c+'.json').then(function(m){cacheK[c]=m;go(m);}).catch(function(){cacheK[c]=null;if(!ST)set('sd-stacja','Po samym kodzie nie znalazłem miejscowości – wpisz też jej nazwę.',true);});}});}
['sd-typ','sd-a','sd-b'].forEach(function(id){var e=$(id);if(e)e.addEventListener('change',id==='sd-typ'?wypelnij:pokazPor);});
window.SD={info:info,htmlSum:htmlSum,htmlSez:htmlSez,htmlMies:htmlMies,htmlLata:htmlLata,htmlTldr:htmlTldr,hubRow:hubRow,hubHead:hubHead,ser:ser,getJSON:getJSON,okresy:okresy,C:C};
function odswiez(){
 if(C.typ==='miasto'){getJSON('stopniodni/'+C.st+'.json').then(function(d){var S=ser(d),I=info(S);
   set('sd-tldr',htmlTldr(I,C.mw,C.stn),true);set('sd-sum',htmlSum(I));set('sd-sez',htmlSez(S,I));set('sd-mies',htmlMies(S,I));set('sd-lata',htmlLata(S,I),true);});}
 else{Promise.all(C.miasta.map(function(c){return getJSON('stopniodni/'+c.st+'.json').then(function(d){return {c:c,S:ser(d)};});})).then(function(L){var I0=info(L[0].S);
   var h=hubHead(I0);L.forEach(function(x){h+=hubRow(x.c,info(x.S));});set('sd-tab',h+'</tbody></table>');set('sd-sum',htmlSum(I0));});}}
getJSON('miejscowosci/woj.json').then(function(w){WOJ=w;}).catch(function(){});
getJSON('stopniodni/stacje.json').then(function(m){META=m;var e=$('sd-do');if(m.dane_do>C.dane_do||C.force){odswiez();if(e)e.textContent=pdat(dn(m.dane_do));}
 initSzukaj();if(C.start)ustawStacje(C.start[0],C.start[1],C.start[2]);}).catch(function(){});
})();
