"""Gera os SVGs do perfil no estilo neon da Multiversal Void Company.

Uso:  pip install fonttools brotli  &&  python assets/build.py
Edite os textos nas constantes abaixo e rode de novo.
As fontes (Orbitron e Share Tech Mono) vão embutidas em cada SVG,
porque o GitHub não deixa SVG carregar fonte externa.
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

NEON = "#e100ff"
NEON_HI = "#ff52ff"
DEEP = "#0d0010"
PANEL = "#1a001f"

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

PROJETOS = {
    "mvc": dict(
        codigo="PROJETO 01",
        titulo=["MULTIVERSAL", "VOID COMPANY"],
        texto=["Site institucional da MVC, uma empresa",
               "fictícia de soluções interdimensionais."],
        tags=["HTML", "CSS"],
    ),
    "ecommerce": dict(
        codigo="PROJETO 02",
        titulo=["MVC", "E-COMMERCE"],
        texto=["Lojinha, checkout e painel admin da MVC,",
               "com back-end em Node e PostgreSQL."],
        tags=["JS", "NODE", "POSTGRES"],
    ),
}


# ---------------------------------------------------------------- fontes
def font_face(family, file, text, weight="normal"):
    """Subconjunto da fonte só com os caracteres usados, em base64."""
    font = TTFont(HERE / "fonts" / file, recalcTimestamp=False)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    sub = subset.Subsetter(opts)
    chars = set(text) | set("0123456789 >_./:-·()")
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
def defs():
    return f"""
  <radialGradient id="void" cx="50%" cy="50%" r="75%">
    <stop offset="0" stop-color="#1a0420"/><stop offset=".45" stop-color="#0f0f0f"/>
    <stop offset="1" stop-color="#000"/>
  </radialGradient>
  <filter id="glow" x="-30%" y="-60%" width="160%" height="220%">
    <feGaussianBlur stdDeviation="3" result="a"/>
    <feGaussianBlur stdDeviation="9" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="2.2" result="a"/>
    <feMerge><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#fff" opacity=".025"/>
  </pattern>"""


def estrelas(w, h, n, seed):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([.6, .8, 1, 1.3])
        cor = rnd.choice(["#fff", "#fff", "#f3c6ff", NEON_HI])
        d = rnd.uniform(0, 4)
        dur = rnd.uniform(2.5, 5.5)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{cor}" '
                   f'class="tw" style="animation-delay:{d:.2f}s;animation-duration:{dur:.2f}s"/>')
    return "\n  ".join(out)


def svg(w, h, style, body, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<style>
{style}
.tw{{animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
<defs>{defs()}</defs>
{body}
</svg>
"""


def moldura(w, h, r=14):
    return (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="url(#void)"/>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="url(#scan)"/>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="none" '
            f'stroke="{NEON}" stroke-opacity=".55" stroke-width="1.5" filter="url(#soft)"/>')


def fundo(w, h, r=14):
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#void)"/>'
            f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#scan)"/>')


# ---------------------------------------------------------------- 1. cabeçalho
def header():
    W, H = 860, 380
    texto = NOME + SUBTITULO + "".join(NAV) + "MVCSR SINAL: ESTÁVEL UNIVERSO 42-S TRANSMISSÃO"
    nav = "".join(
        f'<text x="{x}" y="44" class="nav">{n}</text>'
        for x, n in zip([570, 676, 782], NAV))
    aneis = "".join(
        f'<ellipse cx="430" cy="196" rx="{rx}" ry="{rx*0.28:.0f}" class="ring r{i}"/>'
        for i, rx in enumerate([360, 300, 240]))
    style = f"""{fonts(texto)}
text{{font-family:'Orbitron',sans-serif}}
.logo{{font-weight:800;font-size:18px;fill:#fff;letter-spacing:3px}}
.nav{{font-size:12px;fill:#ddd;letter-spacing:2px;text-anchor:middle}}
.nome{{font-weight:800;font-size:64px;fill:#fff;letter-spacing:8px;text-anchor:middle;
  animation:flick 6s infinite}}
.sub{{font-size:14px;fill:#ccc;letter-spacing:4px;text-anchor:middle}}
.meta{{font-size:10px;fill:#888;letter-spacing:2px}}
.ring{{fill:none;stroke:{NEON};stroke-width:1.2;stroke-dasharray:6 10;opacity:.35;
  animation:spin 40s linear infinite}}
.r1{{animation-direction:reverse;animation-duration:28s;opacity:.25}}
.r2{{animation-duration:18s;opacity:.18}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes spin{{to{{stroke-dashoffset:-320}}}}
@keyframes pulse{{0%,100%{{opacity:.3}}50%{{opacity:1}}}}
@keyframes flick{{0%,18%,22%,25%,53%,57%,100%{{opacity:1}}20%,24%,55%{{opacity:.55}}}}"""
    body = f"""{moldura(W, H, 18)}
  {estrelas(W, H, 90, 42)}
  {aneis}
  <g>
    <rect x="34" y="24" width="34" height="30" rx="5" fill="none" stroke="{NEON}" filter="url(#soft)"/>
    <text x="51" y="45" class="logo" style="font-size:13px;letter-spacing:1px" text-anchor="middle">SR</text>
    <text x="80" y="45" class="logo" style="font-size:12px;font-weight:500;letter-spacing:3px;fill:#ccc">MVC</text>
    {nav}
    <line x1="30" y1="70" x2="830" y2="70" stroke="{NEON}" stroke-opacity=".3"/>
  </g>
  <text x="430" y="215" class="nome" filter="url(#glow)">{NOME}</text>
  <text x="430" y="258" class="sub">{SUBTITULO}</text>
  <line x1="300" y1="282" x2="560" y2="282" stroke="{NEON}" stroke-width="2" filter="url(#soft)"/>
  <circle cx="44" cy="346" r="4" fill="{NEON_HI}" class="pulse"/>
  <text x="56" y="350" class="meta">SINAL: ESTÁVEL</text>
  <text x="826" y="350" class="meta" text-anchor="end">UNIVERSO 42-S · TRANSMISSÃO</text>"""
    return svg(W, H, style, body, f"{NOME} — {SUBTITULO}")


# ---------------------------------------------------------------- 2. sobre (terminal)
def sobre():
    W = 860
    top, lh = 136, 30
    H = top + lh * len(TERMINAL) + 112
    texto = "QUEM SOU EU STACK > sara@void:~$ whoami" + "".join(k + v for k, v in TERMINAL) + "".join(STACK)
    linhas = []
    for i, (k, v) in enumerate(TERMINAL):
        d = 0.6 + i * 0.55
        linhas.append(
            f'<g class="ln" style="animation-delay:{d:.2f}s">'
            f'<text x="56" y="{top + i*lh}" class="mono"><tspan class="k">{escape(k.ljust(10))}</tspan>'
            f'<tspan class="arrow">› </tspan><tspan class="v">{escape(v)}</tspan></text></g>')
    cursor_y = top + lh * len(TERMINAL)
    chips, x = [], 56
    for s in STACK:
        cw = len(s) * 9.5 + 28
        chips.append(f'<g class="ln" style="animation-delay:{0.6 + len(TERMINAL)*0.55 + 0.3:.2f}s">'
                     f'<rect x="{x}" y="{H-62}" width="{cw:.0f}" height="30" rx="6" fill="{PANEL}" '
                     f'stroke="{NEON}" stroke-opacity=".7"/>'
                     f'<text x="{x + cw/2:.0f}" y="{H-42}" class="chip">{s}</text></g>')
        x += cw + 12
    style = f"""{fonts(texto, mono=True)}
.h{{font-family:'Orbitron';font-weight:700;font-size:22px;fill:#fff;letter-spacing:4px}}
.mono{{font-family:'STM',monospace;font-size:17px;fill:#eee;white-space:pre}}
.k{{fill:{NEON_HI}}} .arrow{{fill:#666}} .v{{fill:#ddd}}
.prompt{{font-family:'STM',monospace;font-size:15px;fill:#888}}
.chip{{font-family:'Orbitron';font-size:11px;fill:{NEON_HI};letter-spacing:2px;text-anchor:middle}}
.small{{font-family:'Orbitron';font-size:10px;fill:#777;letter-spacing:3px}}
.ln{{animation:in .5s ease backwards}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{50%{{opacity:0}}}}"""
    body = f"""{moldura(W, H)}
  {estrelas(W, H, 35, 7)}
  <circle cx="30" cy="28" r="5" fill="#ff5f7a" opacity=".8"/><circle cx="48" cy="28" r="5" fill="{NEON}" opacity=".8"/><circle cx="66" cy="28" r="5" fill="#8a5cff" opacity=".8"/>
  <text x="830" y="32" class="small" text-anchor="end">sara@void:~$ whoami</text>
  <line x1="1" y1="48" x2="{W-1}" y2="48" stroke="{NEON}" stroke-opacity=".25"/>
  <text x="56" y="{top-36}" class="h" filter="url(#soft)">QUEM SOU EU</text>
  {''.join(linhas)}
  <rect x="56" y="{cursor_y-16}" width="10" height="19" fill="{NEON_HI}" class="cur"/>
  <text x="56" y="{H-76}" class="small">STACK</text>
  {''.join(chips)}"""
    return svg(W, H, style, body, "Quem sou eu: " + "; ".join(f"{k}: {v}" for k, v in TERMINAL))


# ---------------------------------------------------------------- 3. títulos de seção
def titulo(nome, idx):
    W, H = 860, 86
    texto = nome + f"0{idx}/"
    style = f"""{fonts(texto)}
text{{font-family:'Orbitron'}}
.t{{font-weight:700;font-size:26px;fill:#fff;letter-spacing:6px;text-anchor:middle}}
.n{{font-size:12px;fill:{NEON_HI};letter-spacing:3px;text-anchor:middle}}
.bar{{stroke:{NEON};stroke-width:2;stroke-dasharray:420;stroke-dashoffset:420;animation:draw 1.6s ease forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}"""
    body = f"""{fundo(W, H)}
  <text x="430" y="22" class="n">// 0{idx}</text>
  <text x="430" y="58" class="t" filter="url(#glow)">{escape(nome)}</text>
  <line x1="40" y1="52" x2="250" y2="52" class="bar" filter="url(#soft)"/>
  <line x1="820" y1="52" x2="610" y2="52" class="bar" filter="url(#soft)"/>"""
    return svg(W, H, style, body, nome)


# ---------------------------------------------------------------- 4. cards de projeto
def card(p, lado):
    W, H = 420, 250
    gx = 0 if lado == "esq" else 10
    texto = p["codigo"] + "".join(p["titulo"]) + "".join(p["texto"]) + "".join(p["tags"]) + "ACESSAR →"
    tags, x = [], 28
    for t in p["tags"]:
        cw = len(t) * 8.5 + 22
        tags.append(f'<rect x="{x}" y="186" width="{cw:.0f}" height="24" rx="5" fill="{PANEL}" stroke="{NEON}" stroke-opacity=".6"/>'
                    f'<text x="{x + cw/2:.0f}" y="202" class="tag">{t}</text>')
        x += cw + 8
    style = f"""{fonts(texto, mono=True)}
.cod{{font-family:'STM';font-size:13px;fill:{NEON_HI};letter-spacing:2px}}
.tt{{font-family:'Orbitron';font-weight:800;font-size:24px;fill:#fff;letter-spacing:2px}}
.tx{{font-family:'STM';font-size:15px;fill:#bbb}}
.tag{{font-family:'Orbitron';font-size:10px;fill:{NEON_HI};letter-spacing:1px;text-anchor:middle}}
.go{{font-family:'Orbitron';font-size:11px;fill:{NEON};letter-spacing:2px;text-anchor:end;animation:pulse 2.4s ease-in-out infinite}}
.edge{{fill:none;stroke:{NEON};stroke-width:2;stroke-dasharray:120 1200;animation:run 6s linear infinite}}
@keyframes run{{to{{stroke-dashoffset:-1320}}}}
@keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}"""
    body = f"""<g transform="translate({gx},0)">{moldura(W, H)}
  {estrelas(W, H, 22, sum(map(ord, p['codigo'])))}
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" class="edge" filter="url(#soft)"/>
  <text x="28" y="40" class="cod">{p['codigo']}</text>
  <text x="28" y="80" class="tt" filter="url(#soft)">{escape(p['titulo'][0])}</text>
  <text x="28" y="110" class="tt" filter="url(#soft)">{escape(p['titulo'][1])}</text>
  <text x="28" y="146" class="tx">{escape(p['texto'][0])}</text>
  <text x="28" y="166" class="tx">{escape(p['texto'][1])}</text>
  {''.join(tags)}
  <text x="392" y="204" class="go">ACESSAR →</text></g>"""
    return svg(W + 10, H, style, body, " ".join(p["titulo"]) + ": " + " ".join(p["texto"]))


# ---------------------------------------------------------------- 5. botões de contato
def botao(rotulo, lado):
    """Meia faixa escura (430px); as duas metades lado a lado formam um painel só."""
    W, H = 430, 110
    bw, bh = 260, 54
    bx = W - bw - 20 if lado == "esq" else 20
    by = (H - bh) / 2
    px = 0 if lado == "esq" else -30
    style = f"""{fonts(rotulo)}
.b{{fill:transparent;stroke:{NEON};stroke-width:2;animation:glow 2.6s ease-in-out infinite}}
.l{{font-family:'Orbitron';font-weight:600;font-size:15px;fill:{NEON};letter-spacing:3px;text-anchor:middle}}
@keyframes glow{{0%,100%{{stroke-opacity:.7}}50%{{stroke-opacity:1}}}}"""
    body = f"""
  <rect x="{px}" width="{W + 30}" height="{H}" rx="14" fill="#0b070d"/>
  <rect x="{px}" width="{W + 30}" height="{H}" rx="14" fill="url(#scan)"/>
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="#000"/>
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" class="b" filter="url(#glow)"/>
  <text x="{bx + bw/2}" y="{by + bh/2 + 6}" class="l" filter="url(#soft)">{escape(rotulo)}</text>"""
    return svg(W, H, style, body, rotulo)


# ---------------------------------------------------------------- 6. rodapé
def rodape():
    W, H = 860, 90
    texto = "© MULTIVERSAL VOID COMPANY · FIM DA TRANSMISSÃO · FEITO NO BRASIL"
    style = f"""{fonts(texto)}
.f{{font-family:'Orbitron';font-size:11px;fill:#666;letter-spacing:3px;text-anchor:middle}}
.dot{{animation:pulse 1.6s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}"""
    body = f"""{fundo(W, H)}
  <line x1="40" y1="24" x2="820" y2="24" stroke="{NEON}" stroke-opacity=".4"/>
  <circle cx="400" cy="24" r="3" fill="{NEON_HI}" class="dot"/><circle cx="430" cy="24" r="3" fill="{NEON_HI}" class="dot" style="animation-delay:.3s"/><circle cx="460" cy="24" r="3" fill="{NEON_HI}" class="dot" style="animation-delay:.6s"/>
  <text x="430" y="62" class="f">{texto}</text>"""
    return svg(W, H, style, body, texto)


if __name__ == "__main__":
    arquivos = {
        "header.svg": header(),
        "sobre.svg": sobre(),
        "titulo-projetos.svg": titulo("PROJETOS", 1),
        "titulo-contato.svg": titulo("CONTATO", 2),
        "card-mvc.svg": card(PROJETOS["mvc"], "esq"),
        "card-ecommerce.svg": card(PROJETOS["ecommerce"], "dir"),
        "btn-linkedin.svg": botao("LINKEDIN", "esq"),
        "btn-instagram.svg": botao("INSTAGRAM", "dir"),
        "rodape.svg": rodape(),
    }
    for nome, conteudo in arquivos.items():
        (OUT / nome).write_text(conteudo, encoding="utf-8")
        print(f"{nome:24} {len(conteudo.encode())//1024:>4} KB")
