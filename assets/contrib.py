"""Gera o gráfico de contribuições no estilo neon.

- assets/svg/secao-atividade.svg: a faixa do meio do README (títulos
  "Atividade" e "Contato" + o gráfico), encaixada entre as outras peças.
- assets/svg/grafico.svg: só o gráfico, usado no site.

Roda todo dia pela automação em .github/workflows/atividade.yml.
Localmente:  GITHUB_TOKEN=... python assets/contrib.py
             (ou  python assets/contrib.py dados.json  para testar com um arquivo)
"""
import json
import os
import sys
import urllib.request
from datetime import date

from build import NEON, NEON_HI, OUT, W, estrelas, fonts, pagina, painel, svg, titulo_secao

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


CSS = f"""
.gh{{font-family:'Orbitron';font-weight:700;font-size:18px;fill:#fff;letter-spacing:4px}}
.gsub{{font-family:'STM';font-size:13px;fill:#888}}
.mes{{font-family:'Orbitron';font-size:9px;fill:#777;letter-spacing:1px}}
.lbl{{font-family:'Orbitron';font-size:9px;fill:#777;letter-spacing:2px}}
.num{{font-family:'Orbitron';font-weight:700;font-size:17px;fill:{NEON_HI};letter-spacing:1px}}
.col{{animation:in .4s ease backwards}}
.hot{{filter:drop-shadow(0 0 2px {NEON_HI});animation:hot 2.2s ease-in-out infinite}}
@keyframes in{{from{{opacity:.2}}to{{opacity:1}}}}
@keyframes hot{{0%,100%{{opacity:.75}}50%{{opacity:1}}}}"""


def grafico(cal, ox, oy):
    """Painel 800x300 com o gráfico, a partir de (ox, oy)."""
    semanas = cal["weeks"]
    dias = [d for s in semanas for d in s["contributionDays"]]
    total = cal["totalContributions"]
    maior, agora = sequencias(dias)
    recorde = max((d["contributionCount"] for d in dias), default=0)

    PW, PH = 800, 300
    c, g = 10, 3
    x0 = ox + 72
    y0 = oy + 104
    celulas, meses, mes_ant = [], [], None
    for i, s in enumerate(semanas):
        x = x0 + i * (c + g)
        primeiro = date.fromisoformat(s["contributionDays"][0]["date"])
        if primeiro.month != mes_ant and primeiro.day <= 7 and i < len(semanas) - 2:
            meses.append(f'<text x="{x}" y="{y0 - 10}" class="mes">{MESES[primeiro.month - 1]}</text>')
        mes_ant = primeiro.month
        quad = []
        for d in s["contributionDays"]:
            wd = (date.fromisoformat(d["date"]).weekday() + 1) % 7   # domingo = 0
            nv = NIVEL.get(d["contributionLevel"], 0)
            extra = ' class="hot"' if nv == 4 else ""
            borda = f' stroke="{NEON}" stroke-opacity=".18"' if nv == 0 else ""
            quad.append(f'<rect x="{x}" y="{y0 + wd * (c + g)}" width="{c}" height="{c}" rx="2.5" '
                        f'fill="{CORES[nv]}"{borda}{extra}/>')
        celulas.append(f'<g class="col" style="animation-delay:{i * 0.025:.3f}s">{"".join(quad)}</g>')
    fim = x0 + len(semanas) * (c + g)

    dias_sem = "".join(
        f'<text x="{x0 - 10}" y="{y0 + r * (c + g) + 10}" class="mes" text-anchor="end">{n}</text>'
        for r, n in [(1, "SEG"), (3, "QUA"), (5, "SEX")])
    lx = ox + PW - 64 - 5 * (c + g)
    ly = oy + PH - 44
    legenda = "".join(
        f'<rect x="{lx + i * (c + g)}" y="{ly}" width="{c}" height="{c}" rx="2.5" fill="{cor}"'
        + (f' stroke="{NEON}" stroke-opacity=".18"' if i == 0 else "") + "/>"
        for i, cor in enumerate(CORES))
    stats = [("TOTAL NO ANO", total), ("MAIOR SEQUÊNCIA", f"{maior} DIAS"),
             ("SEQUÊNCIA ATUAL", f"{agora} DIAS"), ("RECORDE NUM DIA", recorde)]
    bloco = "".join(
        f'<text x="{ox + 36 + i * 140}" y="{oy + PH - 52}" class="lbl">{k}</text>'
        f'<text x="{ox + 36 + i * 140}" y="{oy + PH - 30}" class="num" filter="url(#soft)">{v}</text>'
        for i, (k, v) in enumerate(stats))
    css = CSS + f"""
.scan{{animation:scan 7s linear infinite}}
@keyframes scan{{0%{{transform:translateX(0);opacity:0}}5%{{opacity:.9}}90%{{opacity:.9}}100%{{transform:translateX({fim - x0}px);opacity:0}}}}"""
    corpo = f"""{painel(ox, oy, PW, PH)}
  <text x="{ox + 36}" y="{oy + 44}" class="gh" filter="url(#soft)">ATIVIDADE NO MULTIVERSO</text>
  <text x="{ox + PW - 36}" y="{oy + 44}" class="gsub" text-anchor="end">últimos 12 meses</text>
  {''.join(meses)}{dias_sem}
  {''.join(celulas)}
  <rect x="{x0 - 2}" y="{y0 - 4}" width="2" height="{7 * (c + g) + 5}" fill="{NEON_HI}" class="scan" filter="url(#glow)"/>
  {bloco}
  <text x="{lx - 8}" y="{ly + 10}" class="mes" text-anchor="end">MENOS</text>
  {legenda}
  <text x="{lx + 5 * (c + g) + 4}" y="{ly + 10}" class="mes">MAIS</text>"""
    texto = ("ATIVIDADE NO MULTIVERSO últimos 12 meses MENOS MAIS SEG QUA SEX " + " ".join(MESES)
             + "".join(k + str(v) for k, v in stats))
    rotulo = f"Atividade no GitHub: {total} contribuições nos últimos 12 meses"
    return corpo, css, texto, rotulo


def secao(cal):
    H = 520
    corpo, css, texto, rotulo = grafico(cal, 30, 108)
    style = fonts(texto + "ATIVIDADE CONTATO // 02 03", mono=True) + css
    body = f"""{pagina(W, H)}
  {estrelas(W, H, 40, 99)}
  {titulo_secao("ATIVIDADE", 2, 28)}
  {corpo}
  {titulo_secao("CONTATO", 3, 444)}"""
    return svg(W, H, style, body, rotulo)


def solto(cal):
    corpo, css, texto, rotulo = grafico(cal, 0, 0)
    return svg(800, 300, fonts(texto, mono=True) + css, corpo, rotulo)


if __name__ == "__main__":
    cal = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else buscar()
    (OUT / "secao-atividade.svg").write_text(secao(cal), encoding="utf-8")
    (OUT / "grafico.svg").write_text(solto(cal), encoding="utf-8")
    print("secao-atividade.svg e grafico.svg gerados")
