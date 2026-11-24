"""Gera assets/svg/atividade.svg: o gráfico de contribuições no estilo neon.

Roda todo dia pela automação em .github/workflows/atividade.yml.
Localmente:  GITHUB_TOKEN=... python assets/contrib.py
             (ou  python assets/contrib.py dados.json  para testar com um arquivo)
"""
import json
import os
import sys
import urllib.request
from datetime import date

from build import NEON, NEON_HI, OUT, PANEL, estrelas, fonts, moldura, svg

USUARIO = "SaraRebeka"
MESES = "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()
CORES = ["#1a001f", "#4a0057", "#8a00a3", "#c400e0", NEON_HI]
NIVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
         "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

CONSULTA = """query($login:String!){user(login:$login){contributionsCollection{
  contributionCalendar{totalContributions weeks{contributionDays{
    date contributionCount contributionLevel}}}}}}"""


def buscar():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": CONSULTA, "variables": {"login": USUARIO}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        dados = json.load(r)
    return dados["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def sequencias(dias):
    maior = atual = 0
    for d in dias:
        atual = atual + 1 if d["contributionCount"] > 0 else 0
        maior = max(maior, atual)
    # sequência atual: conta de trás pra frente (hoje sem nada ainda não quebra)
    agora = 0
    for i, d in enumerate(reversed(dias)):
        if d["contributionCount"] > 0:
            agora += 1
        elif i > 0:
            break
    return maior, agora


def desenhar(cal):
    semanas = cal["weeks"]
    dias = [d for s in semanas for d in s["contributionDays"]]
    total = cal["totalContributions"]
    maior, agora = sequencias(dias)
    recorde = max((d["contributionCount"] for d in dias), default=0)

    W, H = 860, 300
    c, g = 11, 3                      # célula e espaço
    x0 = 80
    y0 = 104

    celulas, meses, mes_ant = [], [], None
    for i, s in enumerate(semanas):
        x = x0 + i * (c + g)
        primeiro = date.fromisoformat(s["contributionDays"][0]["date"])
        if primeiro.month != mes_ant and primeiro.day <= 7 and i < len(semanas) - 2:
            meses.append(f'<text x="{x:.0f}" y="{y0 - 10}" class="mes">{MESES[primeiro.month - 1]}</text>')
        mes_ant = primeiro.month
        quad = []
        for d in s["contributionDays"]:
            wd = (date.fromisoformat(d["date"]).weekday() + 1) % 7   # domingo = 0
            nv = NIVEL.get(d["contributionLevel"], 0)
            extra = ' class="hot"' if nv == 4 else ""
            borda = f' stroke="{NEON}" stroke-opacity=".18"' if nv == 0 else ""
            quad.append(f'<rect x="{x:.0f}" y="{y0 + wd * (c + g)}" width="{c}" height="{c}" rx="2.5" '
                        f'fill="{CORES[nv]}"{borda}{extra}/>')
        celulas.append(f'<g class="col" style="animation-delay:{i * 0.025:.3f}s">{"".join(quad)}</g>')

    dias_sem = "".join(
        f'<text x="{x0 - 10:.0f}" y="{y0 + r * (c + g) + 10}" class="mes" text-anchor="end">{n}</text>'
        for r, n in [(1, "SEG"), (3, "QUA"), (5, "SEX")])
    legenda_x = W - 72 - 5 * (c + g)
    legenda = "".join(
        f'<rect x="{legenda_x + i * (c + g)}" y="{H - 44}" width="{c}" height="{c}" rx="2.5" fill="{cor}"'
        + (f' stroke="{NEON}" stroke-opacity=".18"' if i == 0 else "") + "/>"
        for i, cor in enumerate(CORES))
    stats = [("TOTAL NO ANO", total), ("MAIOR SEQUÊNCIA", f"{maior} DIAS"),
             ("SEQUÊNCIA ATUAL", f"{agora} DIAS"), ("RECORDE NUM DIA", recorde)]
    bloco = "".join(
        f'<text x="{40 + i * 150}" y="{H - 52}" class="lbl">{k}</text>'
        f'<text x="{40 + i * 150}" y="{H - 30}" class="num" filter="url(#soft)">{v}</text>'
        for i, (k, v) in enumerate(stats))
    gx_fim = x0 + len(semanas) * (c + g)

    texto = ("ATIVIDADE NO MULTIVERSO ÚLTIMOS 12 MESES MENOS MAIS SEG QUA SEX " + " ".join(MESES)
             + "".join(k + str(v) for k, v in stats))
    style = f"""{fonts(texto, mono=True)}
.h{{font-family:'Orbitron';font-weight:700;font-size:18px;fill:#fff;letter-spacing:4px}}
.sub{{font-family:'STM';font-size:13px;fill:#888}}
.mes{{font-family:'Orbitron';font-size:9px;fill:#777;letter-spacing:1px}}
.lbl{{font-family:'Orbitron';font-size:9px;fill:#777;letter-spacing:2px}}
.num{{font-family:'Orbitron';font-weight:700;font-size:17px;fill:{NEON_HI};letter-spacing:1px}}
.col{{opacity:0;animation:in .4s ease forwards}}
.hot{{filter:drop-shadow(0 0 4px {NEON_HI});animation:hot 2.2s ease-in-out infinite}}
.scan{{animation:scan 7s linear infinite}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes hot{{0%,100%{{opacity:.75}}50%{{opacity:1}}}}
@keyframes scan{{0%{{transform:translateX(0);opacity:0}}5%{{opacity:.9}}90%{{opacity:.9}}100%{{transform:translateX({gx_fim - x0:.0f}px);opacity:0}}}}"""
    body = f"""{moldura(W, H)}
  {estrelas(W, H, 25, 99)}
  <text x="40" y="44" class="h" filter="url(#soft)">ATIVIDADE NO MULTIVERSO</text>
  <text x="{W - 40}" y="44" class="sub" text-anchor="end">últimos 12 meses</text>
  {''.join(meses)}{dias_sem}
  {''.join(celulas)}
  <rect x="{x0 - 2:.0f}" y="{y0 - 4}" width="2" height="{7 * (c + g) + 5}" fill="{NEON_HI}" class="scan" filter="url(#glow)"/>
  {bloco}
  <text x="{legenda_x - 8}" y="{H - 34}" class="mes" text-anchor="end">MENOS</text>
  {legenda}
  <text x="{legenda_x + 5 * (c + g) + 4}" y="{H - 34}" class="mes">MAIS</text>"""
    return svg(W, H, style, body, f"Atividade no GitHub: {total} contribuições nos últimos 12 meses")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cal = json.load(open(sys.argv[1]))
    else:
        cal = buscar()
    (OUT / "atividade.svg").write_text(desenhar(cal), encoding="utf-8")
    print("atividade.svg gerado")
