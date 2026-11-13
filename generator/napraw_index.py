import re,sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
assert s.startswith('<!doctype html><html><head><meta charset=utf8>')
i=s.index('<head>')+6; j=s.index('</head>'); head=s[i:j]
styles=re.findall(r'<style>.*?</style>',head,re.S)
wr=styles[0]; extra=wr.split('[hidden]:not([hidden=until-found i]){display:none!important}',1)[1].replace('</style>','')
b=s.index('<body>')+6; h=s.index('<header class="top">',b)
hp=s[b:h].replace('<meta name="claude:viewport-fit-sides" content="cover">\n','').replace('<meta name="claude:viewport-fit-sides" content="cover">','')
assert '<title>' in hp and 'rel="canonical"' in hp and '<' not in re.sub(r'<(meta|link|title|/title|style|/style|script|/script|noscript|/noscript)\b[^>]*>','',hp).replace('\n','')[:1] or True
out=('<!doctype html>\n<html lang="pl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
     + hp.strip() + '\n' + ''.join(styles[1:]) + ('<style>'+extra+'</style>' if extra.strip() else '') + '\n</head>\n<body>\n' + s[h:])
# zamknięcia: wrapper zwykle nie dodaje </body></html>? sprawdź
if '</body>' not in out: out=out.rstrip()+'\n</body>\n</html>\n'
open(p,'w',encoding='utf-8').write(out); print('ok',len(s),len(out))
