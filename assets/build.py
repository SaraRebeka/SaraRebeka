"""Gera os SVGs do perfil no estilo neon da Multiversal Void Company.

Uso:  pip install fonttools brotli  &&  python assets/build.py
Edite os textos nas constantes abaixo e rode de novo.

O README empilha as imagens coladas umas nas outras (align="left"),
então todas têm 860 de largura (ou 430, as metades) e o mesmo fundo:
juntas parecem uma página só. A faixa de atividade é gerada à parte
por assets/contrib.py, todo dia, pela automação.

As fontes vão embutidas em cada SVG, porque o GitHub não deixa SVG
carregar fonte externa.
"""
import base64
import io
import random
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
OUT = HERE / "svg"
OUT.mkdir(exist_ok=True)

W = 860                 # largura da "página"
MEIO = W // 2
BG = "#08060c"
NEON = "#e100ff"
NEON_HI = "#ff52ff"
PANEL = "#1a001f"

SITE = "https://sararebeka.github.io/SaraRebeka/"

# ---------------------------------------------------------------- textos
NOME = "SARA REBEKA"
SUBTITULO = "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS"
NAV = ["SOBRE", "PROJETOS", "CONTATO"]

TERMINAL = [
    ("nome", "Sara Rebeka Pinheiro Mendes"),
    ("origem", "Brasil"),
    ("status", "estudando Análise e Desenvolvimento de Sistemas"),
    ("interesse", "programação (e universos que ainda não existem)"),
    ("colabora", "em qualquer coisa que eu consiga fazer"),
]
STACK = ["HTML", "CSS", "JAVASCRIPT", "NODE.JS", "POSTGRESQL"]

PROJETOS = [
    dict(codigo="PROJETO 01", titulo=["MULTIVERSAL", "VOID COMPANY"],
         texto=["Site institucional da MVC, uma empresa",
                "fictícia de soluções interdimensionais."],
         tags=["HTML", "CSS"]),
    dict(codigo="PROJETO 02", titulo=["MVC", "E-COMMERCE"],
         texto=["Lojinha, checkout e painel admin da MVC,",
                "com back-end em Node e PostgreSQL."],
         tags=["JS", "NODE", "POSTGRES"]),
]
RODAPE = ("© MULTIVERSAL VOID COMPANY", "FIM DA TRANSMISSÃO · FEITO NO BRASIL")


# ---------------------------------------------------------------- fontes
def font_face(family, file, text, weight="normal"):
    """Subconjunto da fonte só com os caracteres usados, em base64."""
    font = TTFont(HERE / "fonts" / file, recalcTimestamp=False)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    sub = subset.Subsetter(opts)
    chars = set(text) | set("0123456789 >_./:-·()↗→")
    sub.populate(text="".join(chars) + "".join(c.lower() for c in chars))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


def fonts(text, orbitron=True, mono=False):
    css = []
    if orbitron:
        css.append(font_face("Orbitron", "Orbitron.woff2", text, "400 900"))
    if mono:
        css.append(font_face("STM", "ShareTechMono.woff2", text))
    return "".join(css)


# ---------------------------------------------------------------- peças comuns
DEFS = f"""
  <radialGradient id="cardbg" cx="30%" cy="20%" r="90%">
    <stop offset="0" stop-color="#1c0622"/><stop offset="1" stop-color="#0a070d"/>
  </radialGradient>
  <filter id="glow" x="-30%" y="-60%" width="160%" height="220%">
    <feGaussianBlur stdDeviation="2" result="a"/>
    <feGaussianBlur stdDeviation="7" result="b0"/>
    <feComponentTransfer in="b0" result="b"><feFuncA type="linear" slope=".45"/></feComponentTransfer>
    <feComponentTransfer in="a" result="a2"><feFuncA type="linear" slope=".6"/></feComponentTransfer>
    <feMerge><feMergeNode in="b"/><feMergeNode in="a2"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="1.6" result="a0"/>
    <feComponentTransfer in="a0" result="a"><feFuncA type="linear" slope=".55"/></feComponentTransfer>
    <feMerge><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#fff" opacity=".022"/>
  </pattern>"""

BASE_CSS = f"""
.tw{{animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
.t-h{{font-family:'Orbitron';font-weight:700;fill:#fff}}
.t-sec{{font-family:'Orbitron';font-weight:700;font-size:26px;fill:#fff;letter-spacing:6px;text-anchor:middle}}
.t-num{{font-family:'Orbitron';font-size:12px;fill:{NEON_HI};letter-spacing:3px;text-anchor:middle}}
.t-small{{font-family:'Orbitron';font-size:10px;fill:#777;letter-spacing:3px}}
.bar{{stroke:{NEON};stroke-width:2;stroke-dasharray:420;stroke-dashoffset:420;animation:draw 1.6s ease forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}"""


def estrelas(w, h, n, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([.6, .8, 1, 1.3])
        cor = rnd.choice(["#fff", "#fff", "#f3c6ff", NEON_HI])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{cor}" class="tw" '
                   f'style="animation-delay:{rnd.uniform(0, 4):.2f}s;animation-duration:{rnd.uniform(2.5, 5.5):.2f}s"/>')
    return "\n  ".join(out)


def svg(w, h, style, body, label):
    assert h % 4 == 0, "altura múltipla de 4 mantém as linhas de scan alinhadas entre peças"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<style>
{style}
{BASE_CSS}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
<defs>{DEFS}</defs>
{body}
</svg>
"""


def pagina(w, h, topo=False, base=False, lado=None):
    """Fundo da página + borda neon externa. Só arredonda os cantos de fora:
    o retângulo passa do limite da imagem nos lados que encostam em outra peça."""
    r, ext = 22, 40
    x, rw = 1, w - 2
    if lado == "esq":
        rw += ext
    elif lado == "dir":
        x, rw = 1 - ext, rw + ext
    y, rh = 1, h - 2
    if not topo:
        y, rh = y - ext, rh + ext
    if not base:
        rh += ext
    ret = f'x="{x}" y="{y}" width="{rw}" height="{rh}" rx="{r}"'
    return (f'<rect {ret} fill="{BG}"/><rect {ret} fill="url(#scan)"/>'
            f'<rect {ret} fill="none" stroke="{NEON}" stroke-opacity=".45" stroke-width="1.5" filter="url(#soft)"/>')


def painel(x, y, w, h, r=14):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#cardbg)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#scan)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" '
            f'stroke="{NEON}" stroke-opacity=".4" stroke-width="1.5" filter="url(#soft)"/>')


def titulo_secao(nome, idx, y):
    """Título de seção centralizado, com as barras que se desenham."""
    return f"""
  <text x="{MEIO}" y="{y}" class="t-num">// 0{idx}</text>
  <text x="{MEIO}" y="{y + 36}" class="t-sec" filter="url(#glow)">{escape(nome)}</text>
  <line x1="40" y1="{y + 30}" x2="250" y2="{y + 30}" class="bar" filter="url(#soft)"/>
  <line x1="820" y1="{y + 30}" x2="610" y2="{y + 30}" class="bar" filter="url(#soft)"/>"""


# ---------------------------------------------------------------- 1. topo: cabeçalho + sobre + título projetos
def topo():
    H = 868
    nav = "".join(f'<text x="{x}" y="44" class="nav">{n}</text>'
                  for x, n in zip([570, 676, 782], NAV))
    aneis = "".join(f'<ellipse cx="{MEIO}" cy="190" rx="{rx}" ry="{rx * .28:.0f}" class="ring r{i}"/>'
                    for i, rx in enumerate([360, 300, 240]))
    # terminal
    py, lh = 372, 30
    linhas = []
    for i, (k, v) in enumerate(TERMINAL):
        linhas.append(
            f'<g class="ln" style="animation-delay:{.6 + i * .55:.2f}s">'
            f'<text x="66" y="{py + 132 + i * lh}" class="mono"><tspan class="k">{escape(k.ljust(10))}</tspan>'
            f'<tspan class="arrow">› </tspan><tspan class="v">{escape(v)}</tspan></text></g>')
    cur_y = py + 132 + len(TERMINAL) * lh - 16
    chips, x = [], 66
    for s in STACK:
        cw = len(s) * 9.5 + 28
        chips.append(f'<rect x="{x}" y="{py + 336}" width="{cw:.0f}" height="30" rx="6" fill="{PANEL}" '
                     f'stroke="{NEON}" stroke-opacity=".7"/>'
                     f'<text x="{x + cw / 2:.0f}" y="{py + 356}" class="chip">{s}</text>')
        x += cw + 12

    texto = (NOME + SUBTITULO + "".join(NAV) + "MVCSR ENTRAR NO SITE ↗ QUEM SOU EU STACK sara@void:~$ whoami PROJETOS"
             + "".join(k + v for k, v in TERMINAL) + "".join(STACK))
    style = f"""{fonts(texto, mono=True)}
.logo{{font-family:'Orbitron';font-weight:800;fill:#fff}}
.nav{{font-family:'Orbitron';font-size:12px;fill:#ddd;letter-spacing:2px;text-anchor:middle}}
.nome{{font-family:'Orbitron';font-weight:800;font-size:64px;fill:#fff;letter-spacing:8px;text-anchor:middle;animation:flick 6s infinite}}
.sub{{font-family:'Orbitron';font-size:14px;fill:#ccc;letter-spacing:4px;text-anchor:middle}}
.cta{{font-family:'Orbitron';font-weight:600;font-size:13px;fill:{NEON};letter-spacing:3px;text-anchor:middle}}
.cta-b{{fill:#000;stroke:{NEON};stroke-width:2;animation:cta 2.6s ease-in-out infinite}}
.ring{{fill:none;stroke:{NEON};stroke-width:1.2;stroke-dasharray:6 10;opacity:.35;animation:spin 40s linear infinite}}
.r1{{animation-direction:reverse;animation-duration:28s;opacity:.25}}
.r2{{animation-duration:18s;opacity:.18}}
.mono{{font-family:'STM',monospace;font-size:17px;fill:#eee;white-space:pre}}
.k{{fill:{NEON_HI}}} .arrow{{fill:#666}} .v{{fill:#ddd}}
.chip{{font-family:'Orbitron';font-size:11px;fill:{NEON_HI};letter-spacing:2px;text-anchor:middle}}
.ln{{animation:in .5s ease backwards}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes spin{{to{{stroke-dashoffset:-320}}}}
@keyframes cta{{0%,100%{{stroke-opacity:.85}}50%{{stroke-opacity:1}}}}
@keyframes flick{{0%,18%,22%,25%,53%,57%,100%{{opacity:1}}20%,24%,55%{{opacity:.55}}}}
@keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{50%{{opacity:0}}}}"""
    body = f"""{pagina(W, H, topo=True)}
  {estrelas(W, H, 110, 42)}
  {aneis}
  <rect x="34" y="24" width="34" height="30" rx="5" fill="none" stroke="{NEON}" filter="url(#soft)"/>
  <text x="51" y="45" class="logo" style="font-size:13px" text-anchor="middle">SR</text>
  <text x="80" y="45" class="logo" style="font-size:12px;font-weight:500;letter-spacing:3px;fill:#ccc">MVC</text>
  {nav}
  <line x1="30" y1="70" x2="830" y2="70" stroke="{NEON}" stroke-opacity=".3"/>
  <text x="{MEIO}" y="200" class="nome" filter="url(#glow)">{NOME}</text>
  <text x="{MEIO}" y="242" class="sub">{SUBTITULO}</text>
  <rect x="{MEIO - 120}" y="272" width="240" height="46" rx="8" class="cta-b" filter="url(#soft)"/>
  <text x="{MEIO}" y="300" class="cta" filter="url(#soft)">ENTRAR NO SITE ↗</text>
  {painel(30, py, 800, 396)}
  <circle cx="54" cy="{py + 24}" r="5" fill="#ff5f7a" opacity=".8"/><circle cx="72" cy="{py + 24}" r="5" fill="{NEON}" opacity=".8"/><circle cx="90" cy="{py + 24}" r="5" fill="#8a5cff" opacity=".8"/>
  <text x="806" y="{py + 28}" class="t-small" text-anchor="end">sara@void:~$ whoami</text>
  <line x1="31" y1="{py + 46}" x2="829" y2="{py + 46}" stroke="{NEON}" stroke-opacity=".25"/>
  <text x="66" y="{py + 90}" class="t-h" style="font-size:22px;letter-spacing:4px" filter="url(#soft)">QUEM SOU EU</text>
  {''.join(linhas)}
  <rect x="66" y="{cur_y}" width="10" height="19" fill="{NEON_HI}" class="cur"/>
  <text x="66" y="{py + 322}" class="t-small">STACK</text>
  {''.join(chips)}
  {titulo_secao("PROJETOS", 1, py + 428)}"""
    return svg(W, H, style, body, f"{NOME} — {SUBTITULO}. Quem sou eu: "
               + "; ".join(f"{k}: {v}" for k, v in TERMINAL))


# ---------------------------------------------------------------- 2. cartões de projeto (metades)
def card(p, lado):
    H = 280
    cw, ch, cy = 390, 250, 8
    cx = 30 if lado == "esq" else 10
    texto = p["codigo"] + "".join(p["titulo"]) + "".join(p["texto"]) + "".join(p["tags"]) + "ACESSAR →"
    tags, x = [], cx + 28
    for t in p["tags"]:
        tw = len(t) * 8.5 + 22
        tags.append(f'<rect x="{x}" y="{cy + 186}" width="{tw:.0f}" height="24" rx="5" fill="{PANEL}" stroke="{NEON}" stroke-opacity=".6"/>'
                    f'<text x="{x + tw / 2:.0f}" y="{cy + 202}" class="tag">{t}</text>')
        x += tw + 8
    style = f"""{fonts(texto, mono=True)}
.cod{{font-family:'STM';font-size:13px;fill:{NEON_HI};letter-spacing:2px}}
.tt{{font-family:'Orbitron';font-weight:800;font-size:24px;fill:#fff;letter-spacing:2px}}
.tx{{font-family:'STM';font-size:15px;fill:#bbb}}
.tag{{font-family:'Orbitron';font-size:10px;fill:{NEON_HI};letter-spacing:1px;text-anchor:middle}}
.go{{font-family:'Orbitron';font-size:11px;fill:{NEON};letter-spacing:2px;text-anchor:end;animation:pulse 2.4s ease-in-out infinite}}
.edge{{fill:none;stroke:{NEON};stroke-width:2;stroke-dasharray:120 1200;animation:run 6s linear infinite}}
@keyframes run{{to{{stroke-dashoffset:-1320}}}}
@keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}"""
    body = f"""{pagina(MEIO, H, lado=lado)}
  {estrelas(MEIO, H, 18, sum(map(ord, p['codigo'])))}
  {painel(cx, cy, cw, ch)}
  <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" class="edge" filter="url(#soft)"/>
  <text x="{cx + 28}" y="{cy + 40}" class="cod">{p['codigo']}</text>
  <text x="{cx + 28}" y="{cy + 80}" class="tt" filter="url(#soft)">{escape(p['titulo'][0])}</text>
  <text x="{cx + 28}" y="{cy + 110}" class="tt" filter="url(#soft)">{escape(p['titulo'][1])}</text>
  <text x="{cx + 28}" y="{cy + 146}" class="tx">{escape(p['texto'][0])}</text>
  <text x="{cx + 28}" y="{cy + 166}" class="tx">{escape(p['texto'][1])}</text>
  {''.join(tags)}
  <text x="{cx + cw - 26}" y="{cy + 204}" class="go">ACESSAR →</text>"""
    return svg(MEIO, H, style, body, " ".join(p["titulo"]) + ": " + " ".join(p["texto"]))


# ---------------------------------------------------------------- 3. contato + rodapé (metades)
def contato(rotulo, lado):
    H = 192
    bw, bh, by = 260, 54, 16
    bx = MEIO - bw - 20 if lado == "esq" else 20
    rod = RODAPE[0] if lado == "esq" else RODAPE[1]
    rx, anchor = (MEIO - 14, "end") if lado == "esq" else (14, "start")
    lx1, lx2 = (40, MEIO) if lado == "esq" else (0, MEIO - 40)
    style = f"""{fonts(rotulo + rod)}
.b{{fill:#000;stroke:{NEON};stroke-width:2;animation:glow 2.6s ease-in-out infinite}}
.l{{font-family:'Orbitron';font-weight:600;font-size:15px;fill:{NEON};letter-spacing:3px;text-anchor:middle}}
.f{{font-family:'Orbitron';font-size:10px;fill:#666;letter-spacing:3px}}
@keyframes glow{{0%,100%{{stroke-opacity:.85}}50%{{stroke-opacity:1}}}}"""
    body = f"""{pagina(MEIO, H, base=True, lado=lado)}
  {estrelas(MEIO, H, 14, len(rotulo) * 7)}
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" class="b" filter="url(#soft)"/>
  <text x="{bx + bw / 2}" y="{by + bh / 2 + 6}" class="l" filter="url(#soft)">{escape(rotulo)}</text>
  <line x1="{lx1}" y1="118" x2="{lx2}" y2="118" stroke="{NEON}" stroke-opacity=".35"/>
  <text x="{rx}" y="152" class="f" text-anchor="{anchor}">{escape(rod)}</text>"""
    return svg(MEIO, H, style, body, rotulo)


if __name__ == "__main__":
    for velho in OUT.glob("*.svg"):
        if velho.name not in ("secao-atividade.svg", "grafico.svg"):
            velho.unlink()
    arquivos = {
        "topo.svg": topo(),
        "card-mvc.svg": card(PROJETOS[0], "esq"),
        "card-ecommerce.svg": card(PROJETOS[1], "dir"),
        "contato-linkedin.svg": contato("LINKEDIN", "esq"),
        "contato-instagram.svg": contato("INSTAGRAM", "dir"),
    }
    for nome, conteudo in arquivos.items():
        (OUT / nome).write_text(conteudo, encoding="utf-8")
        print(f"{nome:24} {len(conteudo.encode()) // 1024:>4} KB")
