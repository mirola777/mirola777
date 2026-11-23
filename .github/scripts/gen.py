import base64
import html
import sys
from pathlib import Path

SHOTS = Path(__file__).parent / "shots"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
BG = "#0b0d12"
PANEL = "#0f1219"
LINE = "#20242f"
TEXT = "#e8eaf0"
MUTED = "#8a90a2"
DIM = "#555b6b"
ACC = "#a78bfa"
ACC2 = "#5eead4"


def esc(s):
    return html.escape(s, quote=True)


def b64(name):
    return base64.b64encode((SHOTS / name).read_bytes()).decode()


def defs_common():
    return f"""
  <linearGradient id="acc" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC2}"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="1" fill="#ffffff" fill-opacity="0.07"/>
  </pattern>"""


def hero():
    W, H = 1000, 320
    phrases = [
        "software engineer on checkout @ yuno",
        "i make payments feel invisible",
        "and build little apps for people i love",
        "go · kotlin · typescript · svelte · three.js",
    ]
    cw = 12.0
    x0, y0 = 64, 214
    n = len(phrases)
    win = 100 / n
    T = 18
    styles, groups = [], []
    for i, p in enumerate(phrases):
        w = len(p) * cw
        s = i * win
        t_end = s + win * 0.38
        hold = s + win * 0.82
        d_end = s + win * 0.96
        kf = (
            f"0%{{transform:translateX(0)}}"
            + (f"{s:.3f}%{{transform:translateX(0);animation-timing-function:steps({len(p)},end)}}" if s > 0 else f"0%{{transform:translateX(0);animation-timing-function:steps({len(p)},end)}}")
            + f"{t_end:.3f}%{{transform:translateX({w:.1f}px)}}"
            + f"{hold:.3f}%{{transform:translateX({w:.1f}px);animation-timing-function:steps({len(p)},end)}}"
            + f"{d_end:.3f}%{{transform:translateX(0)}}"
            + f"100%{{transform:translateX(0)}}"
        )
        vis = (
            f"0%{{opacity:0}}"
            + (f"{s - 0.001:.3f}%{{opacity:0}}" if s > 0 else "")
            + f"{s:.3f}%{{opacity:1}}{d_end:.3f}%{{opacity:1}}{d_end + 0.001:.3f}%{{opacity:0}}100%{{opacity:0}}"
        )
        styles.append(f"@keyframes t{i}{{{kf}}} @keyframes v{i}{{{vis}}}")
        styles.append(f".m{i}{{animation:t{i} {T}s infinite}} .c{i}{{animation:t{i} {T}s infinite}} .g{i}{{animation:v{i} {T}s infinite}}")
        groups.append(f"""
  <clipPath id="clip{i}"><rect class="m{i}" x="{x0 - w:.1f}" y="{y0 - 24}" width="{w:.1f}" height="34"/></clipPath>
  <g class="g{i}">
    <text x="{x0}" y="{y0}" clip-path="url(#clip{i})" font-family="{MONO}" font-size="20" fill="{TEXT}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs">{esc(p)}</text>
    <rect class="c{i}" x="{x0 + 2}" y="{y0 - 19}" width="10" height="23" fill="url(#acc)"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect>
  </g>""")
    css = "\n".join(styles)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mirola — software engineer on Checkout at Yuno. Medellín, Colombia.">
<style>
{css}
@keyframes drift {{ 0% {{ transform: translate(0,0) }} 50% {{ transform: translate(-60px,30px) }} 100% {{ transform: translate(0,0) }} }}
@keyframes drift2 {{ 0% {{ transform: translate(0,0) }} 50% {{ transform: translate(50px,-25px) }} 100% {{ transform: translate(0,0) }} }}
@keyframes pulse {{ 0%,100% {{ opacity: 1 }} 50% {{ opacity: .35 }} }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(8px) }} to {{ opacity: 1; transform: translateY(0) }} }}
.o1 {{ animation: drift 14s ease-in-out infinite }}
.o2 {{ animation: drift2 18s ease-in-out infinite }}
.live {{ animation: pulse 2s ease-in-out infinite }}
.r1 {{ animation: rise .8s ease-out both }}
.r2 {{ animation: rise .8s .15s ease-out both }}
</style>
<defs>{defs_common()}
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
  <clipPath id="panel"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0.35" stop-color="{BG}" stop-opacity="1"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#panel)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <circle class="o1" cx="820" cy="80" r="140" fill="{ACC}" fill-opacity="0.45" filter="url(#blur)"/>
  <circle class="o2" cx="930" cy="260" r="120" fill="{ACC2}" fill-opacity="0.22" filter="url(#blur)"/>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{LINE}"/>
<g class="r1">
  <circle class="live" cx="70" cy="66" r="4" fill="{ACC2}"/>
  <text x="84" y="71" font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="1.5">MEDELLÍN, COLOMBIA</text>
</g>
<text class="r2" x="60" y="160" font-family="{SANS}" font-size="84" font-weight="800" fill="{TEXT}" letter-spacing="-4">mirola<tspan fill="url(#acc)">.</tspan></text>
{"".join(groups)}
<text x="64" y="276" font-family="{MONO}" font-size="12" fill="{DIM}" letter-spacing="1">bald, occasionally programming.</text>
</svg>
"""


def chips(x, y, items, size=12):
    out, cx = [], x
    for it in items:
        w = len(it) * size * 0.62 + 22
        out.append(
            f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="26" rx="13" fill="#ffffff" fill-opacity="0.04" stroke="{LINE}"/>'
            f'<text x="{cx + w / 2:.1f}" y="{y + 17.5}" text-anchor="middle" font-family="{MONO}" font-size="{size}" fill="{MUTED}">{esc(it)}</text>'
        )
        cx += w + 8
    return "".join(out)


def lines(x, y, txt, size, fill, lh, family=SANS, weight=400):
    ts = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else lh}">{esc(t)}</tspan>' for i, t in enumerate(txt))
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" font-weight="{weight}">{ts}</text>'


def featured(stat="1,000+", stat_label="AID POINTS MAPPED"):
    W, H = 1000, 420
    ix, iy, iw, ih = 18, 18, 576, 360
    img = b64("unidos.jpg")
    tx = 630
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Unidos por Colombia: collaborative map of aid points after the 2026 earthquake">
<style>
@keyframes pulse {{ 0%,100% {{ opacity: 1 }} 50% {{ opacity: .35 }} }}
@keyframes sweep {{ 0% {{ transform: translateX(-300px) }} 100% {{ transform: translateX(1300px) }} }}
.live {{ animation: pulse 2s ease-in-out infinite }}
.sweep {{ animation: sweep 6s ease-in-out infinite }}
</style>
<defs>{defs_common()}
  <clipPath id="img"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="14"/></clipPath>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{PANEL}"/>
  <rect class="sweep" x="0" y="0" width="200" height="{H}" fill="url(#shine)"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{LINE}"/>
<image clip-path="url(#img)" x="{ix}" y="{iy}" width="{iw}" height="{ih}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{img}" xlink:href="data:image/jpeg;base64,{img}"/>
<rect x="{ix + .5}" y="{iy + .5}" width="{iw - 1}" height="{ih - 1}" rx="14" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
<circle class="live" cx="{tx + 5}" cy="50" r="4" fill="{ACC2}"/>
<text x="{tx + 18}" y="54" font-family="{MONO}" font-size="12" fill="{MUTED}" letter-spacing="1.5">FEATURED</text>
<text x="{tx}" y="104" font-family="{SANS}" font-size="32" font-weight="750" fill="{TEXT}" letter-spacing="-1">Unidos por Colombia</text>
{lines(tx, 140, ["A collaborative map of aid points for the", "people hit by the August 2026 earthquake.", "Built in days, with friends, for strangers."], 15.5, MUTED, 24)}
<text x="{tx}" y="262" font-family="{SANS}" font-size="44" font-weight="800" fill="url(#acc)" letter-spacing="-1.5">{esc(stat)}</text>
<text x="{tx}" y="286" font-family="{MONO}" font-size="12" fill="{DIM}" letter-spacing="1">{esc(stat_label)}</text>
{chips(tx, 316, ["next.js", "supabase", "leaflet", "ocr"])}
<text x="{tx}" y="382" font-family="{MONO}" font-size="13" fill="{TEXT}">unidos-por-colombia.vercel.app <tspan fill="{ACC}">↗</tspan></text>
</svg>
"""


def card(shot, title, desc, tags, url, accent):
    W, H = 492, 520
    ix, iy, iw, ih = 16, 16, 460, 288
    img = b64(shot)
    tx = 28
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}: {esc(' '.join(desc))}">
<defs>
  <clipPath id="img"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="12"/></clipPath>
  <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="{PANEL}" stroke="{LINE}"/>
<image clip-path="url(#img)" x="{ix}" y="{iy}" width="{iw}" height="{ih}" preserveAspectRatio="xMidYMin slice" href="data:image/jpeg;base64,{img}" xlink:href="data:image/jpeg;base64,{img}"/>
<rect x="{ix + .5}" y="{iy + .5}" width="{iw - 1}" height="{ih - 1}" rx="12" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
<rect x="{tx}" y="330" width="36" height="3" rx="1.5" fill="url(#bar)"/>
<text x="{tx}" y="368" font-family="{SANS}" font-size="24" font-weight="750" fill="{TEXT}" letter-spacing="-0.6">{esc(title)}</text>
{lines(tx, 398, desc, 14.5, MUTED, 22)}
{chips(tx, 448, tags, 11.5)}
<text x="{tx}" y="500" font-family="{MONO}" font-size="12.5" fill="{TEXT}">{esc(url)} <tspan fill="{accent}">↗</tspan></text>
</svg>
"""


def lab():
    rows = [
        ("blackjack-2000", "PS2-style 3D blackjack for game nights with friends", "three.js"),
        ("el-parche", "a Gather-style virtual office for my group of friends", "websockets"),
        ("william-english", "an English course I built for my dad", "next.js"),
        ("alexa-ai", "my own Alexa skill with DeepSeek and long-term memory", "python"),
        ("slop-factory", "one prompt in, a fully produced AI video out", "python"),
        ("claude-plugin", "agents that work my tickets, on-call and deploys", "claude code"),
    ]
    W = 1000
    top = 92
    lh = 38
    H = top + lh * len(rows) + 70
    body = []
    css = []
    for i, (name, desc, tech) in enumerate(rows):
        y = top + 40 + i * lh
        d = 0.6 + i * 0.18
        css.append(f".l{i}{{animation:lin .5s {d:.2f}s ease-out both}}")
        body.append(
            f'<g class="l{i}">'
            f'<text x="40" y="{y}" font-family="{MONO}" font-size="14" fill="{DIM}">drwx</text>'
            f'<text x="100" y="{y}" font-family="{MONO}" font-size="14" fill="{ACC}">{esc(name)}/</text>'
            f'<text x="290" y="{y}" font-family="{MONO}" font-size="14" fill="{TEXT}">{esc(desc)}</text>'
            f'<text x="{W - 40}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{DIM}">{esc(tech)}</text>'
            f"</g>"
        )
    end_y = top + 40 + len(rows) * lh + 4
    dl = 0.6 + len(rows) * 0.18
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Private lab: side projects I build for friends and family">
<style>
@keyframes lin {{ from {{ opacity: 0; transform: translateX(-6px) }} to {{ opacity: 1; transform: translateX(0) }} }}
@keyframes ltype {{ from {{ transform: translateX(0) }} to {{ transform: translateX(96px) }} }}
{" ".join(css)}
.cmd {{ animation: ltype .5s steps(11,end) both }}
.end {{ animation: lin .3s {dl:.2f}s both }}
</style>
<defs><clipPath id="cmd"><rect class="cmd" x="-96" y="36" width="96" height="26"/></clipPath></defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="{PANEL}" stroke="{LINE}"/>
<circle cx="30" cy="26" r="5.5" fill="#ff5f57" fill-opacity=".8"/><circle cx="48" cy="26" r="5.5" fill="#febc2e" fill-opacity=".8"/><circle cx="66" cy="26" r="5.5" fill="#28c840" fill-opacity=".8"/>
<text x="{W / 2}" y="31" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{DIM}">~/lab — private side projects</text>
<line x1="0" y1="50" x2="{W}" y2="50" stroke="{LINE}"/>
<text x="40" y="{top}" font-family="{MONO}" font-size="14" fill="{ACC2}">❯</text>
<g transform="translate(60,{top - 54})"><text x="0" y="54" clip-path="url(#cmd)" font-family="{MONO}" font-size="14" fill="{TEXT}" textLength="92.4" lengthAdjust="spacingAndGlyphs">ls -l ~/lab</text></g>
{"".join(body)}
<g class="end"><text x="40" y="{end_y + 20}" font-family="{MONO}" font-size="14" fill="{ACC2}">❯</text><rect x="58" y="{end_y + 6}" width="9" height="18" fill="url(#acc)"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect></g>
<defs>{defs_common()}</defs>
</svg>
"""


def render_static(out):
    out = Path(out)
    (out / "assets").mkdir(parents=True, exist_ok=True)
    OUT = out
    (OUT / "assets/hero.svg").write_text(hero())
    (OUT / "assets/pdf-editor.svg").write_text(card("pdf-editor.jpg", "PDF Editor", ["Edit text, merge, split, sign, compress and", "OCR. 100% client side: files never leave you."], ["svelte", "pdf.js", "pdf-lib", "tesseract"], "mirola-pdf-editor.vercel.app", ACC))
    (OUT / "assets/grid-maker.svg").write_text(card("grid-maker.jpg", "Grid Maker", ["Drawing-grid overlay for artists. Drop a", "reference, tune the grid, export in high-res."], ["svelte", "vite", "canvas"], "mirola-grid-maker.vercel.app", "#fb923c"))
    (OUT / "assets/lab.svg").write_text(lab())


if __name__ == "__main__":
    render_static(sys.argv[1])
