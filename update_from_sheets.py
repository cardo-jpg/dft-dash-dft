import re, urllib.request

SHEET_ID="17CuuYKxf13NHpJHRAZPoGW9_1Ni_xnIcVTeDQHXb5yQ"
GID_GADS="550644796"; GID_META="734559877"
HTML_FILE="index.html"

def fetch_csv(gid):
    url=f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req) as r: return r.read().decode("utf-8")

def parse_brl(s):
    s=s.strip().replace("R$ ","").replace("R$","").replace(".","").replace(",",".")
    try: return float(s)
    except: return 0.0

def parse_int(s):
    s=s.strip().replace(".","").replace(",","")
    try: return int(s)
    except: return 0

def split_csv(line):
    parts=[]; cur=""; iq=False
    for ch in line:
        if ch=='"': iq=not iq
        elif ch==',' and not iq: parts.append(cur.strip().strip('"')); cur=""
        else: cur+=ch
    parts.append(cur.strip().strip('"')); return parts

print("Fetching Google Ads...")
gads=fetch_csv(GID_GADS)
rows=[]
for line in gads.splitlines()[1:]:
    if not line.strip(): continue
    p=split_csv(line)
    if len(p)<6: continue
    d=p[0].split("/")
    if len(d)!=3: continue
    iso=f"{d[2]}-{d[1]}-{d[0]}"
    if "Branding" in p[1]: ck="Branding"
    elif "Demanda" in p[1]: ck="Demanda Ativa"
    elif "Segmentos" in p[1]: ck="Segmentos"
    else: continue
    rows.append({"date":iso,"camp":ck,"invest":parse_brl(p[2]),"imp":parse_int(p[3]),"clk":parse_int(p[4]),"leads":parse_int(p[5])})

rows.sort(key=lambda r:(r["date"],r["camp"]))
today=max(r["date"] for r in rows)
print(f"  {len(rows)} rows, ultimo: {today}")

raw_js="const RAW=[\n"
for r in rows:
    raw_js+=f"  {{date:'{r['date']}',camp:'{r['camp']}',invest:{r['invest']},imp:{r['imp']},clk:{r['clk']},leads:{r['leads']}}},\n"
raw_js+="];"

print("Fetching Meta Ads...")
meta=fetch_csv(GID_META)
agg={}; dm=[]
for line in meta.splitlines()[1:]:
    if not line.strip(): continue
    p=split_csv(line)
    if len(p)<10: continue
    if p[0]: dm.append(p[0])
    criativo=p[3]; invest=parse_brl(p[5]); imp=parse_int(p[6]); viz=parse_int(p[7])
    alcance=parse_int(p[8]); viz3s=parse_int(p[9]); p25=parse_int(p[11]) if len(p)>11 else 0
    if criativo not in agg:
        agg[criativo]={"name":criativo,"camp":p[1],"url":p[4].strip(),"invest":0,"imp":0,"viz":0,"alcance":0,"viz3s":0,"p25":0}
    a=agg[criativo]; a["invest"]+=invest; a["imp"]+=imp; a["viz"]+=viz; a["alcance"]+=alcance; a["viz3s"]+=viz3s; a["p25"]+=p25

ads=list(agg.values())
pct=lambda a,b: round(a/b*100,1) if b else 0
brl=lambda v: f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
hcls=lambda v: "otimo" if v>=60 else "bom" if v>=45 else "medio" if v>=30 else "bad"
rcls=lambda v: "otimo" if v>=50 else "bom" if v>=35 else "medio" if v>=20 else "bad"
def acao(invest,h,r):
    if invest<2: return "basica","AMOSTRA BASICA"
    if h>=45 and r>=35: return "escalar","ESCALAR"
    if h<20 and r<20: return "ruim","RUIM"
    if invest<8: return "basica","AMOSTRA BASICA"
    return "aguardar","AGUARDAR DADOS"

ti=sum(a["invest"] for a in ads); tm=sum(a["imp"] for a in ads); tv=sum(a["viz"] for a in ads)
tz=sum(a["viz3s"] for a in ads); tp=sum(a["p25"] for a in ads)
hook=pct(tz,tm); ret=pct(tp,tz); cpm=round(ti/tm*1000,2) if tm else 0
v1=[a for a in ads if "V2" not in a["camp"]]; v2=[a for a in ads if "V2" in a["camp"]]
sv=lambda lst:{k:sum(a[k] for a in lst) for k in ["invest","imp","viz3s","p25"]}
s1=sv(v1); s2=sv(v2)
dmin=min(dm) if dm else ""; dmax=max(dm) if dm else ""
print(f"  {brl(ti)} | {tm:,} imp | hook {hook}% | ret {ret}%")

def mkpi(cls,lbl,val,sub=""):
    s=f'<div class="mkpi-sub">{sub}</div>' if sub else ""
    return f'<div class="mkpi {cls}"><div class="mkpi-lbl">{lbl}</div><div class="mkpi-val">{val}</div>{s}</div>'

kpis="".join([mkpi("or","Investido",brl(ti)),mkpi("bl","Visualizacoes",f"{tv:,}"),
    mkpi("go","Hook Rate",f"{hook}%","ruim &lt;30% · medio 30-45%<br/>bom 45-60% · otimo &gt;60%"),
    mkpi("pu","Retencao 25%",f"{ret}%","ruim &lt;20% · medio 20-35%<br/>bom 35-50% · otimo &gt;50%"),
    mkpi("im","Impressoes",f"{tm:,}"),mkpi("vi","Viz. 3s",f"{tz:,}"),mkpi("cp","CPM",brl(cpm))])

def cc(cls,title,bcls,badge,s):
    h=pct(s["viz3s"],s["imp"]); r=pct(s["p25"],s["viz3s"])
    return (f'<div class="meta-sum-card {cls}"><div class="ms-header"><div class="ms-title">{title} <span class="camp-pill {bcls}">{badge}</span></div>'
            f'<div class="ms-invest">{brl(s["invest"])}</div></div><div class="ms-metrics">'
            f'<div><div class="ms-m-lbl">Impressoes</div><div class="ms-m-val">{s["imp"]:,}</div></div>'
            f'<div><div class="ms-m-lbl">Viz. 3s</div><div class="ms-m-val">{s["viz3s"]:,}</div></div>'
            f'<div><div class="ms-m-lbl">Hook Rate</div><div class="ms-m-val rt-{hcls(h)}">{h}%</div></div>'
            f'<div><div class="ms-m-lbl">Retencao</div><div class="ms-m-val rt-{rcls(r)}">{r}%</div></div></div></div>')

def cr(a):
    h=pct(a["viz3s"],a["imp"]); r=pct(a["p25"],a["viz3s"])
    cp=round(a["invest"]/a["imp"]*1000,2) if a["imp"] else 0
    badge="V1" if "V2" not in a["camp"] else "V2"; bcls="pf" if badge=="V1" else "pf2"
    ac,al=acao(a["invest"],h,r)
    return (f'<tr><td class="cname">{a["name"]} <span class="bp {bcls}">{badge}</span></td>'
            f'<td><span class="stativo">Ativo</span></td><td class="nr">{brl(a["invest"])}</td>'
            f'<td class="nr">{a["alcance"]:,}</td><td class="nr">{a["viz3s"]:,}</td><td class="nr">{a["viz"]:,}</td>'
            f'<td class="nr">{brl(cp)}</td><td class="nr rt-{hcls(h)}">{h}%</td><td class="nr rt-{rcls(r)}">{r}%</td>'
            f'<td><span class="ap ac-{ac}">{al}</span></td>'
            f'<td><a class="abtn" href="{a["url"]}" target="_blank">&#8599; Anuncio</a></td></tr>')

rows_html="\n".join(cr(a) for a in sorted(ads,key=lambda x:x["invest"],reverse=True))
label=f"Meta Ads — Brand Awareness · {dmin} a {dmax}/2026"

new_meta=f"""<!-- META ADS -->
<div class="slbl">{label}</div>
<div class="mkstrip">{kpis}</div>
<div class="meta-camp-sum">{cc("sv1","DFT_Visitas_F","pf","V1",s1)}{cc("sv2","DFT_Visitas_F_V2","pf2","V2",s2)}</div>
<div class="slbl">Criativos - Meta Ads</div>
<div style="display:block;width:100%;background:var(--card);border:1px solid var(--brd);border-radius:15px;overflow-x:auto;">
  <table class="ct"><thead><tr><th>Criativo</th><th>Status</th><th>Investido</th><th>Alcance</th><th>Vis. 3s</th><th>Cliques</th><th>CPM</th><th>Hook</th><th>Retencao</th><th>Acao</th><th></th></tr></thead>
  <tbody>{rows_html}</tbody></table></div>
"""

with open(HTML_FILE,"r",encoding="utf-8") as f: html=f.read()
s=html.find("const RAW=["); e=html.find("];",s)+2
html=html[:s]+raw_js+html[e:]
html=re.sub(r"const TODAY='[0-9-]+'",f"const TODAY='{today}'",html)
ms=html.find("<!-- META ADS -->"); mc=html.find("</main>",ms if ms>0 else 0)
if ms>0 and mc>ms: html=html[:ms]+new_meta+"\n</main>"+html[mc+7:]
with open(HTML_FILE,"w",encoding="utf-8") as f: f.write(html)
print(f"Done! {len(rows)} rows ate {today}")
