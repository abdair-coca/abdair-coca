#!/usr/bin/env python3
"""Generates the custom animated SVGs used by the profile README.

Run from the repo root:  python3 scripts/build_assets.py
Edit PROJECTS / PROFILE below and re-run to update the cards and terminal.
"""
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# ── Palette: blue · white · black ─────────────────────────────────────────────
BLACK = "#05070D"
CARD = "#0D1117"
BORDER = "#1C2A44"
BLUE = "#3B82F6"
BLUE_DEEP = "#1D4ED8"
BLUE_LIGHT = "#60A5FA"
WHITE = "#F8FAFC"
MUTED = "#A3B1C6"
DIM = "#64748B"

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', 'Cascadia Code', Consolas, 'Liberation Mono', Menlo, monospace"

PROJECTS = [
    ("LazoGraph", "Your life as a graph: connect people, memories, places and projects to explore your story with context.", ["Python", "Neo4j", "AI"]),
    ("abdAIr", "AI-powered CLI assistant with streaming responses, persistent chat history and auto-summarization.", ["Python", "Groq", "LLM"]),
    ("Titi_Edu", "Learning social network with courses, gamification and certificates, powered by Neo4j + PostgreSQL.", ["Neo4j", "PostgreSQL", "JavaScript"]),
    ("machine-learning-App", "Interactive platform to learn ML fundamentals, running real Python in the browser via Pyodide.", ["Python", "TypeScript", "Pyodide"]),
    ("ReadEnglishAloud", "AI-generated short stories for English learners, with text-to-speech and CEFR levels from A1 to C2.", ["JavaScript", "HTML", "AI"]),
    ("Notas-App", "Notes and reminders app with full CRUD and an interactive pet mascot that keeps you company.", ["Laravel", "PostgreSQL", "Tailwind"]),
]

PROFILE = [
    ("name", "Abdair Coca"),
    ("role", "Software Engineering Student"),
    ("location", "Potosí, Bolivia"),
    ("focus", "[ AI agents, LLMs, Machine Learning ]"),
    ("builds", "Full-stack apps with Laravel, Neo4j & Python"),
    ("motto", '"Programming is a craft, not just a career."'),
]
CURRENTLY = "llm-agents/    machine-learning/    lazograph/"


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n{body}\n</svg>\n'
    )


def fade_in(begin, dur=0.6, dy=10):
    return (
        f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="{dur}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 {dy}" to="0 0" '
        f'begin="{begin}s" dur="{dur}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>'
    )


# ── Header ────────────────────────────────────────────────────────────────────
def header():
    W, H = 1200, 340
    nodes = {
        "core": (935, 175, 11, None),
        "ai": (790, 95, 6, "AI"),
        "ml": (1055, 82, 6, "ML"),
        "neo": (1110, 215, 6, "Neo4j"),
        "py": (835, 268, 6, "Python"),
        "lar": (1010, 290, 5, "Laravel"),
        "a": (875, 160, 3, None),
        "b": (995, 235, 3, None),
        "c": (720, 190, 3, None),
        "d": (1160, 120, 3, None),
        "e": (1165, 295, 3, None),
        "f": (915, 55, 3, None),
        "g": (760, 300, 3, None),
    }
    edges = [
        ("core", "ai"), ("core", "ml"), ("core", "neo"), ("core", "py"), ("core", "lar"),
        ("core", "a"), ("core", "b"), ("ai", "a"), ("ai", "c"), ("ai", "f"), ("ml", "f"),
        ("ml", "d"), ("neo", "d"), ("neo", "e"), ("neo", "b"), ("lar", "b"), ("lar", "e"),
        ("py", "c"), ("py", "g"), ("py", "a"),
    ]
    parts = [f"""<defs>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  <radialGradient id="glow1" cx="78%" cy="52%" r="45%">
    <stop offset="0" stop-color="{BLUE_DEEP}" stop-opacity="0.45"/>
    <stop offset="1" stop-color="{BLUE_DEEP}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glow2" cx="5%" cy="0%" r="55%">
    <stop offset="0" stop-color="{BLUE}" stop-opacity="0.16"/>
    <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="coreGlow">
    <stop offset="0" stop-color="{WHITE}" stop-opacity="0.9"/>
    <stop offset="0.35" stop-color="{BLUE_LIGHT}" stop-opacity="0.45"/>
    <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="{WHITE}" fill-opacity="0.07"/>
  </pattern>
  <linearGradient id="sweep" x1="0" x2="1">
    <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{WHITE}"/>
    <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
  </linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BLACK}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <rect width="{W}" height="{H}" fill="url(#glow1)"/>
  <rect width="{W}" height="{H}" fill="url(#glow2)"/>
  <rect y="{H-3}" width="{W}" height="3" fill="{BLUE}" fill-opacity="0.25"/>
  <rect y="{H-3}" x="-300" width="300" height="3" fill="url(#sweep)">
    <animate attributeName="x" from="-300" to="{W}" dur="4s" repeatCount="indefinite"/>
  </rect>"""]

    # edges: faint base line + travelling data pulse
    parts.append('<g stroke-linecap="round">')
    for i, (a, b) in enumerate(edges):
        x1, y1, *_ = nodes[a]
        x2, y2, *_ = nodes[b]
        L = math.hypot(x2 - x1, y2 - y1)
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BLUE}" stroke-opacity="0.32" stroke-width="1.2"/>')
        if i % 2 == 0:
            dur = 2.2 + (i % 5) * 0.45
            parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BLUE_LIGHT}" stroke-width="2.2" '
                f'stroke-dasharray="14 {L:.0f}" stroke-dashoffset="{L + 14:.0f}">'
                f'<animate attributeName="stroke-dashoffset" from="{L + 14:.0f}" to="0" dur="{dur:.2f}s" '
                f'begin="{(i * 0.37) % 2:.2f}s" repeatCount="indefinite"/></line>'
            )
    parts.append("</g>")

    # nodes
    for i, (key, (x, y, r, label)) in enumerate(nodes.items()):
        if key == "core":
            parts.append(f'<circle cx="{x}" cy="{y}" r="60" fill="url(#coreGlow)"><animate attributeName="r" values="52;64;52" dur="4s" repeatCount="indefinite"/></circle>')
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{WHITE}"/>')
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{BLUE_LIGHT}" stroke-width="1.5">'
                         f'<animate attributeName="r" from="{r}" to="{r + 26}" dur="2.4s" repeatCount="indefinite"/>'
                         f'<animate attributeName="stroke-opacity" from="0.9" to="0" dur="2.4s" repeatCount="indefinite"/></circle>')
            continue
        fill = WHITE if label else BLUE_LIGHT
        if label:
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{BLUE_LIGHT}" stroke-width="1.2">'
                         f'<animate attributeName="r" from="{r}" to="{r + 14}" dur="3s" begin="{i * 0.5:.1f}s" repeatCount="indefinite"/>'
                         f'<animate attributeName="stroke-opacity" from="0.8" to="0" dur="3s" begin="{i * 0.5:.1f}s" repeatCount="indefinite"/></circle>')
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{BLACK}" stroke-width="2"/>')
        if label:
            parts.append(f'<text x="{x + r + 8}" y="{y + 5}" font-family="{MONO}" font-size="14" fill="{MUTED}">{escape(label)}</text>')

    # text block
    parts.append(f"""<g opacity="0">{fade_in(0.1)}
  <text x="72" y="112" font-family="{MONO}" font-size="18" fill="{BLUE_LIGHT}" letter-spacing="1">// hello, world — I'm</text>
</g>
<g opacity="0">{fade_in(0.35, 0.8, 16)}
  <text x="68" y="196" font-family="{SANS}" font-size="84" font-weight="800" fill="{WHITE}" letter-spacing="-2">Abdair Coca</text>
</g>
<g opacity="0">{fade_in(0.7)}
  <text x="72" y="244" font-family="{SANS}" font-size="27" fill="#CBD5E1">Software Engineering Student</text>
</g>
<g opacity="0">{fade_in(1.0)}
  <text x="72" y="290" font-family="{MONO}" font-size="18" fill="{BLUE_LIGHT}">AI agents · Machine Learning · Full-stack</text>
  <rect x="535" y="275" width="10" height="20" fill="{WHITE}">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>
  </rect>
</g>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{BORDER}"/>""")
    return svg(W, H, "\n".join(parts), "Abdair Coca — Software Engineering Student")


# ── Terminal ──────────────────────────────────────────────────────────────────
def terminal():
    W = 1200
    LH, FS, X0, TOP = 32, 20, 48, 100
    CH = FS * 0.61  # approx. monospace advance
    prompt_w = len("abdair@potosi:~$ ") * CH
    lines = []  # (kind, payload)
    lines.append(("cmd", "whoami"))
    lines.append(("out", [("Abdair Coca", WHITE), (" — Software Engineering Student from Bolivia", MUTED)]))
    lines.append(("blank", None))
    lines.append(("cmd", "cat profile.yml"))
    for k, v in PROFILE:
        lines.append(("kv", (k, v)))
    lines.append(("blank", None))
    lines.append(("cmd", "ls ./currently-learning"))
    lines.append(("out", [(CURRENTLY, BLUE_LIGHT)]))
    lines.append(("blank", None))
    lines.append(("end", None))
    H = TOP + LH * len(lines) + 16

    body = [f"""<defs><clipPath id="win"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="tglow" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{BLUE}" stop-opacity="0.10"/><stop offset="0.6" stop-color="{BLUE}" stop-opacity="0"/>
</linearGradient></defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{CARD}"/>
<rect width="{W}" height="{H}" fill="url(#tglow)"/>
<rect width="{W}" height="48" fill="#111827"/>
<rect y="48" width="{W}" height="1" fill="{BORDER}"/>
<circle cx="28" cy="24" r="7" fill="{BLUE}"/><circle cx="52" cy="24" r="7" fill="{BLUE_LIGHT}"/><circle cx="76" cy="24" r="7" fill="{WHITE}" fill-opacity="0.85"/>
<text x="{W / 2}" y="30" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{DIM}">abdair@potosi: ~ — zsh</text>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{BORDER}"/>
<g font-family="{MONO}" font-size="{FS}" xml:space="preserve">"""]

    t = 0.5
    for i, (kind, payload) in enumerate(lines):
        y = TOP + i * LH
        if kind == "blank":
            continue
        if kind in ("cmd", "end"):
            body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
                        f'<text x="{X0}" y="{y}"><tspan fill="{BLUE}" font-weight="700">abdair@potosi</tspan>'
                        f'<tspan fill="{WHITE}">:~$ </tspan></text></g>')
            t += 0.35
            if kind == "end":
                body.append(f'<rect x="{X0 + prompt_w:.0f}" y="{y - FS + 3}" width="{CH:.0f}" height="{FS + 2}" fill="{BLUE_LIGHT}" opacity="0">'
                            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
                continue
            n = len(payload)
            dur = max(0.4, n * 0.07)
            steps = ";".join(f"{k * CH + 1:.0f}" for k in range(n + 1)) + f";{W}"
            cid = f"type{i}"
            body.append(f'<clipPath id="{cid}"><rect x="{X0 + prompt_w:.0f}" y="{y - FS - 4}" height="{LH}" width="0">'
                        f'<animate attributeName="width" values="{steps}" begin="{t:.2f}s" dur="{dur:.2f}s" calcMode="discrete" fill="freeze"/></rect></clipPath>')
            body.append(f'<text x="{X0 + prompt_w:.0f}" y="{y}" fill="{WHITE}" clip-path="url(#{cid})">{escape(payload)}</text>')
            t += dur + 0.35
        elif kind == "out":
            spans = "".join(f'<tspan fill="{c}">{escape(s).replace("  ", "&#160; ")}</tspan>' for s, c in payload)
            body.append(f'<text x="{X0}" y="{y}" opacity="0">{spans}'
                        f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.3s" fill="freeze"/></text>')
            t += 0.35
        elif kind == "kv":
            k, v = payload
            body.append(f'<text x="{X0}" y="{y}" opacity="0"><tspan fill="{BLUE_LIGHT}">{escape(k)}:</tspan>'
                        f'<tspan x="{X0 + 11 * CH:.0f}" fill="{WHITE}">{escape(v)}</tspan>'
                        f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.3s" fill="freeze"/></text>')
            t += 0.16
    body.append("</g>")
    return svg(W, H, "\n".join(body), "About Abdair Coca")


# ── Project cards ─────────────────────────────────────────────────────────────
def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    return lines + [cur]


def card(idx, name, desc, tags):
    W, H = 600, 250
    desc_lines = wrap(desc, 54)[:3]
    chips, cx = [], 32
    for tag in tags:
        w = len(tag) * 8.2 + 28
        chips.append(f'<rect x="{cx}" y="190" width="{w:.0f}" height="30" rx="15" fill="{BLUE}" fill-opacity="0.10" stroke="{BLUE}" stroke-opacity="0.55"/>'
                     f'<text x="{cx + w / 2:.0f}" y="210" text-anchor="middle" font-family="{MONO}" font-size="13.5" fill="{BLUE_LIGHT}">{escape(tag)}</text>')
        cx += w + 10
    desc_svg = "".join(
        f'<text x="32" y="{136 + k * 25}" font-family="{SANS}" font-size="17" fill="{MUTED}">{escape(l)}</text>'
        for k, l in enumerate(desc_lines))
    body = f"""<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <radialGradient id="g" cx="100%" cy="0%" r="70%">
    <stop offset="0" stop-color="{BLUE_DEEP}" stop-opacity="0.35"/><stop offset="1" stop-color="{BLUE_DEEP}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="bar" x1="0" x2="1">
    <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset="0.5" stop-color="{WHITE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
  </linearGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{CARD}"/>
  <rect width="{W}" height="{H}" fill="url(#g)"/>
  <rect width="{W}" height="3" fill="{BLUE}" fill-opacity="0.6"/>
  <rect x="-200" width="200" height="3" fill="url(#bar)">
    <animate attributeName="x" from="-200" to="{W}" dur="3.5s" begin="{idx * 0.6:.1f}s" repeatCount="indefinite"/>
  </rect>
  <text x="{W - 28}" y="{H - 24}" text-anchor="end" font-family="{SANS}" font-size="120" font-weight="800" fill="{WHITE}" fill-opacity="0.04">{idx + 1:02d}</text>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{BORDER}"/>
<text x="32" y="50" font-family="{MONO}" font-size="14" fill="{BLUE_LIGHT}" letter-spacing="2">{idx + 1:02d} / PROJECT</text>
<text x="32" y="96" font-family="{SANS}" font-size="31" font-weight="700" fill="{WHITE}">{escape(name)}</text>
<g transform="translate({W - 64} 30)">
  <circle cx="18" cy="18" r="18" fill="none" stroke="{BLUE}" stroke-opacity="0.6"/>
  <path d="M13 23 L23 13 M15 13 H23 V21" stroke="{WHITE}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</g>
{desc_svg}
{''.join(chips)}"""
    return svg(W, H, body, f"{name} — {desc}")


# ── Footer ────────────────────────────────────────────────────────────────────
def footer():
    W, H = 1200, 120
    dots = "".join(
        f'<circle cx="{x}" cy="60" r="4" fill="{BLUE_LIGHT}" opacity="0.3"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" begin="{k * 0.3:.1f}s" repeatCount="indefinite"/></circle>'
        for k, x in enumerate([90, 115, 140, 1060, 1085, 1110]))
    body = f"""<defs><clipPath id="f"><rect width="{W}" height="{H}" rx="20"/></clipPath>
<radialGradient id="fg" cx="50%" cy="120%" r="60%"><stop offset="0" stop-color="{BLUE_DEEP}" stop-opacity="0.5"/><stop offset="1" stop-color="{BLUE_DEEP}" stop-opacity="0"/></radialGradient></defs>
<g clip-path="url(#f)"><rect width="{W}" height="{H}" fill="{BLACK}"/><rect width="{W}" height="{H}" fill="url(#fg)"/></g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{BORDER}"/>
{dots}
<text x="{W / 2}" y="58" text-anchor="middle" font-family="{SANS}" font-size="26" font-weight="700" fill="{WHITE}">Thanks for stopping by.</text>
<text x="{W / 2}" y="88" text-anchor="middle" font-family="{MONO}" font-size="16" fill="{BLUE_LIGHT}">let's build something great together →</text>"""
    return svg(W, H, body, "Thanks for stopping by")


def main():
    (OUT / "projects").mkdir(parents=True, exist_ok=True)
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    (OUT / "terminal.svg").write_text(terminal(), encoding="utf-8")
    (OUT / "footer.svg").write_text(footer(), encoding="utf-8")
    for i, (name, desc, tags) in enumerate(PROJECTS):
        (OUT / "projects" / f"{name}.svg").write_text(card(i, name, desc, tags), encoding="utf-8")
    print("assets written to", OUT)


if __name__ == "__main__":
    main()
