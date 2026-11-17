#!/usr/bin/env python3
"""Generates the cartoon-style animated SVGs used by the profile README.

Run from the repo root:
    pip install fonttools brotli
    python3 scripts/build_assets.py

Edit PROJECTS / PROFILE below and re-run. Fonts (Fredoka, JetBrains Mono — SIL OFL)
are subset and embedded in every SVG, so they look the same everywhere.
"""
import base64
import io
import math
import re
from html import escape, unescape
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = Path(__file__).resolve().parent / "fonts"

# ── Palette: flat cartoon in blue · white · black ─────────────────────────────
INK = "#111318"
WHITE = "#FFFFFF"
ICE = "#DBEAFE"
SKY = "#93C5FD"
BLUE2 = "#3B82F6"
BLUE = "#2563EB"
NAVY = "#1E3A8A"
SLATE = "#334155"

F = "font-family=\"Fredoka, 'Comic Sans MS', sans-serif\""
M = "font-family=\"JetBrainsMono, Consolas, monospace\""

FONT_FILES = {
    ("Fredoka", 500): "fredoka-latin-500-normal.woff",
    ("Fredoka", 600): "fredoka-latin-600-normal.woff",
    ("Fredoka", 700): "fredoka-latin-700-normal.woff",
    ("JetBrainsMono", 500): "jetbrains-mono-latin-500-normal.woff",
    ("JetBrainsMono", 700): "jetbrains-mono-latin-700-normal.woff",
}

PROJECTS = [
    dict(repo="Titi_Edu", band=SKY, art="book",
         desc="A learning social network with courses, gamification and certificates, powered by Neo4j + PostgreSQL.",
         tags=["JavaScript", "Neo4j", "PostgreSQL"]),
    dict(repo="Robotsito", band=BLUE, art="robot",
         desc="Meet Bob: a fair robot that recognizes faces, follows you with its head, shows emotions on an OLED and chats by voice.",
         tags=["Python", "ESP32", "MediaPipe", "Groq"]),
    dict(repo="JevCharacter", band=ICE, art="blob",
         desc="JEVLING: a tiny digital creature that watches your cursor, touch and activity, and turns it into AI-driven behavior.",
         tags=["TypeScript", "React", "XState", "AI"]),
    dict(repo="explicador", band=NAVY, art="diagram",
         desc="A Claude Code plugin that explains any codebase with animated, interactive diagrams, one scene at a time.",
         tags=["TypeScript", "Node.js", "Claude Code"]),
]

WHOAMI = "Abdair Coca, I build robots, AI creatures & apps"
PROFILE = [
    ("name", "Abdair Coca"),
    ("from", "Potosí, Bolivia"),
    ("role", "Software Engineering Student"),
    ("loves", "[ robots, AI agents, machine learning ]"),
    ("builds", "Robot Bob, JEVLING, Titi_Edu & more"),
    ("motto", '"Code is a craft, and it should be fun."'),
]
CURRENTLY = "llm-agents/    machine-learning/"


# ── Font embedding ────────────────────────────────────────────────────────────
def font_css(body):
    text = unescape("".join(re.findall(r">([^<>]+)<", body)))
    chars = set(text) | set(" ")
    css = []
    for (family, weight), fname in FONT_FILES.items():
        if f"font-family=\"{family}" not in body:
            continue
        font = TTFont(FONTS / fname)
        opts = Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga"]
        sub = Subsetter(opts)
        sub.populate(text="".join(sorted(chars)))
        sub.subset(font)
        buf = io.BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        css.append(f"@font-face{{font-family:{family};font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "<style>" + "".join(css) + "</style>"


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n'
            f'{font_css(body)}\n{body}\n</svg>\n')


# ── Cartoon helpers ───────────────────────────────────────────────────────────
def sticker(x, y, w, h, r, fill, shadow=8, sw=5, extra=""):
    s = f'<rect x="{x + shadow}" y="{y + shadow}" width="{w}" height="{h}" rx="{r}" fill="{INK}"/>' if shadow else ""
    return s + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" {extra}/>'


def otext(x, y, txt, size, fill=WHITE, sw=9, shadow=6, weight=700, anchor="start", extra=""):
    """Comic-style text: thick ink outline plus a hard drop shadow."""
    common = f'{F} font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" stroke-linejoin="round" paint-order="stroke" {extra}'
    out = ""
    if shadow:
        out += f'<text x="{x + shadow}" y="{y + shadow}" {common} fill="{INK}" stroke="{INK}" stroke-width="{sw}">{escape(txt)}</text>'
    out += f'<text x="{x}" y="{y}" {common} fill="{fill}" stroke="{INK}" stroke-width="{sw}">{escape(txt)}</text>'
    return out


def halftone(pid, color=WHITE, opacity=0.14, step=22, r=3):
    return (f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{step / 2}" cy="{step / 2}" r="{r}" fill="{color}" fill-opacity="{opacity}"/></pattern>')


def star(x, y, s, fill=WHITE, delay=0.0):
    d = f"M0 {-s} Q{s * .18} {-s * .18} {s} 0 Q{s * .18} {s * .18} 0 {s} Q{-s * .18} {s * .18} {-s} 0 Q{-s * .18} {-s * .18} 0 {-s}Z"
    return (f'<g transform="translate({x} {y})"><g><path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<animateTransform attributeName="transform" type="scale" values="1;0.55;1" dur="1.6s" begin="{delay}s" repeatCount="indefinite"/></g></g>')


def cloud(x, y, s=1.0, dx=30, dur=9):
    circles = [(0, 0, 34), (38, -14, 42), (82, 0, 32), (40, 12, 30)]
    outline = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}" stroke="{INK}" stroke-width="10"/>' for cx, cy, r in circles)
    fill = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WHITE}"/>' for cx, cy, r in circles)
    return (f'<g transform="translate({x} {y}) scale({s})"><g>{outline}{fill}'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} 0;0 0" dur="{dur}s" repeatCount="indefinite"/></g></g>')


def burst(cx, cy, r1, r2, n=22, fill=SKY):
    pts = []
    for k in range(n * 2):
        a = math.pi * k / n
        r = r1 if k % 2 == 0 else r2
        pts.append(f"{r * math.cos(a):.1f},{r * math.sin(a):.1f}")
    return (f'<g transform="translate({cx} {cy})"><polygon points="{" ".join(pts)}" fill="{fill}" stroke="{INK}" stroke-width="5" stroke-linejoin="round">'
            f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/></polygon></g>')


def limb(d, color, w=22):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w - 10}" stroke-linecap="round"/>')


def robot_head(blink_begin=0.0):
    """Robot Bob's head, centered on (0, -70). Antenna bulb + blinking OLED eyes."""
    return f'''<line x1="0" y1="-125" x2="0" y2="-150" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>
<circle cx="0" cy="-158" r="12" fill="{SKY}" stroke="{INK}" stroke-width="5"><animate attributeName="fill" values="{SKY};{WHITE};{SKY}" dur="1.2s" repeatCount="indefinite"/></circle>
<rect x="-92" y="-92" width="22" height="40" rx="8" fill="{BLUE2}" stroke="{INK}" stroke-width="5"/>
<rect x="70" y="-92" width="22" height="40" rx="8" fill="{BLUE2}" stroke="{INK}" stroke-width="5"/>
<rect x="-76" y="-125" width="152" height="112" rx="30" fill="{WHITE}" stroke="{INK}" stroke-width="6"/>
<rect x="-56" y="-106" width="112" height="74" rx="20" fill="{NAVY}" stroke="{INK}" stroke-width="5"/>
<g fill="{SKY}"><rect x="-34" y="-86" width="20" height="28" rx="10"><animate attributeName="height" values="28;28;3;28" keyTimes="0;0.9;0.95;1" dur="3.5s" begin="{blink_begin}s" repeatCount="indefinite"/><animate attributeName="y" values="-86;-86;-73;-86" keyTimes="0;0.9;0.95;1" dur="3.5s" begin="{blink_begin}s" repeatCount="indefinite"/></rect>
<rect x="14" y="-86" width="20" height="28" rx="10"><animate attributeName="height" values="28;28;3;28" keyTimes="0;0.9;0.95;1" dur="3.5s" begin="{blink_begin}s" repeatCount="indefinite"/><animate attributeName="y" values="-86;-86;-73;-86" keyTimes="0;0.9;0.95;1" dur="3.5s" begin="{blink_begin}s" repeatCount="indefinite"/></rect></g>
<path d="M-14 -48 Q0 -38 14 -48" fill="none" stroke="{SKY}" stroke-width="5" stroke-linecap="round"/>'''


def robot(x, y, s=1.0, wave=True):
    """Full Robot Bob, feet at about y+130. Bounces and waves."""
    arm = limb("M58 22 Q92 0 98 -34", WHITE)
    hand = f'<circle cx="99" cy="-42" r="16" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>'
    wave_anim = ('<animateTransform attributeName="transform" type="rotate" values="0 58 22;-22 58 22;0 58 22;-22 58 22;0 58 22" '
                 'dur="1.6s" repeatCount="indefinite"/>') if wave else ""
    return f'''<g transform="translate({x} {y}) scale({s})">
<ellipse cx="0" cy="138" rx="70" ry="10" fill="{INK}" fill-opacity="0.25"><animate attributeName="rx" values="70;58;70" dur="1.2s" repeatCount="indefinite"/></ellipse>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -10;0 0" dur="1.2s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
{limb("M-24 92 L-26 122", NAVY, 24)}{limb("M24 92 L26 122", NAVY, 24)}
<ellipse cx="-30" cy="126" rx="20" ry="11" fill="{INK}"/><ellipse cx="30" cy="126" rx="20" ry="11" fill="{INK}"/>
{limb("M-58 22 Q-88 50 -84 86", WHITE)}<circle cx="-84" cy="92" r="15" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>
<g>{arm}{hand}{wave_anim}</g>
<rect x="-12" y="-16" width="24" height="20" fill="{BLUE2}" stroke="{INK}" stroke-width="5"/>
<rect x="-62" y="0" width="124" height="98" rx="26" fill="{BLUE}" stroke="{INK}" stroke-width="6"/>
<circle cx="0" cy="48" r="22" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>
<g transform="translate(0 49)"><path d="M0 9 C-14 0 -12 -12 -5 -12 C-2 -12 0 -9 0 -7 C0 -9 2 -12 5 -12 C12 -12 14 0 0 9Z" fill="{BLUE}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"><animateTransform attributeName="transform" type="scale" values="1;1.25;1" dur="0.9s" repeatCount="indefinite"/></path></g>
{robot_head()}
</g></g>'''


def blob(x, y, s=1.0, look=True, cursor=False):
    """A tiny round creature with big eyes that look around (JEVLING-style)."""
    look_vals = "0 0;7 -3;7 -3;-7 2;-7 2;0 4;0 0"
    pupils = (f'<animateTransform attributeName="transform" type="translate" values="{look_vals}" '
              f'keyTimes="0;0.15;0.35;0.5;0.7;0.85;1" dur="5s" repeatCount="indefinite"/>') if look else ""
    cur = ""
    if cursor:
        cur = (f'<g><path d="M0 0 L0 30 L8 23 L14 36 L20 33 L14 21 L25 21 Z" fill="{WHITE}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
               f'<animateTransform attributeName="transform" type="translate" values="40 -60;105 -80;105 -80;-120 -40;-120 -40;10 30;40 -60" '
               f'keyTimes="0;0.15;0.35;0.5;0.7;0.85;1" dur="5s" repeatCount="indefinite"/></g>')
    return f'''<g transform="translate({x} {y}) scale({s})">
<ellipse cx="0" cy="52" rx="56" ry="9" fill="{INK}" fill-opacity="0.25"/>
<g><animateTransform attributeName="transform" type="scale" values="1 1;1.06 0.94;0.97 1.04;1 1" keyTimes="0;0.3;0.6;1" dur="1.4s" repeatCount="indefinite" additive="sum"/>
<ellipse cx="-24" cy="48" rx="14" ry="8" fill="{INK}"/><ellipse cx="24" cy="48" rx="14" ry="8" fill="{INK}"/>
<path d="M-62 20 C-66 -30 -36 -62 0 -62 C36 -62 66 -30 62 20 C58 46 -58 46 -62 20Z" fill="{SKY}" stroke="{INK}" stroke-width="6"/>
<path d="M-18 -66 Q-14 -84 -2 -78" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
<ellipse cx="-22" cy="-10" rx="20" ry="24" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>
<ellipse cx="22" cy="-10" rx="20" ry="24" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>
<g><circle cx="-20" cy="-6" r="10" fill="{INK}"/><circle cx="24" cy="-6" r="10" fill="{INK}"/>
<circle cx="-16" cy="-10" r="3.5" fill="{WHITE}"/><circle cx="28" cy="-10" r="3.5" fill="{WHITE}"/>{pupils}</g>
<ellipse cx="-42" cy="16" rx="8" ry="5" fill="{BLUE2}" fill-opacity="0.6"/><ellipse cx="42" cy="16" rx="8" ry="5" fill="{BLUE2}" fill-opacity="0.6"/>
<path d="M-8 22 Q0 30 8 22" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>
</g>{cur}</g>'''


def book_art():
    return f'''<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="2.4s" repeatCount="indefinite"/>
<path d="M0 10 Q-44 -6 -92 6 L-92 52 Q-44 40 0 56Z" fill="{WHITE}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
<path d="M0 10 Q44 -6 92 6 L92 52 Q44 40 0 56Z" fill="{WHITE}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
<path d="M-74 20 Q-44 12 -16 22 M-74 34 Q-44 26 -16 36 M16 22 Q44 12 74 20 M16 36 Q44 26 74 34" fill="none" stroke="{SKY}" stroke-width="4" stroke-linecap="round"/></g>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -12;0 0" dur="2.4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
<path d="M-30 -36 L-30 -16 Q0 -4 30 -16 L30 -36Z" fill="{NAVY}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
<polygon points="0,-70 70,-46 0,-22 -70,-46" fill="{BLUE}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
<g><path d="M0 -46 L44 -36 L44 -8" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/><circle cx="44" cy="-4" r="7" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>
<animateTransform attributeName="transform" type="rotate" values="-6 0 -46;6 0 -46;-6 0 -46" dur="1.6s" repeatCount="indefinite"/></g></g>'''


def robot_art():
    waves = "".join(
        f'<path d="M{100 + k * 16} {-82 - k * 10} Q{116 + k * 22} -62 {100 + k * 16} {-42 + k * 10}" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linecap="round" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="{k * 0.25}s" repeatCount="indefinite"/></path>' for k in range(3))
    bracket = (f'<g fill="none" stroke="{WHITE}" stroke-width="5" stroke-linecap="round">'
               f'<path d="M-150 -96 V-112 H-134 M-102 -112 H-86 V-96 M-86 -50 V-34 H-102 M-134 -34 H-150 V-50"/>'
               f'<circle cx="-118" cy="-80" r="10"/><path d="M-134 -46 Q-118 -62 -102 -46"/>'
               f'<animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite"/></g>')
    return (f'<g transform="translate(0 70) scale(0.82)"><g>{robot_head(0.4)}'
            f'<animateTransform attributeName="transform" type="translate" values="-10 0;10 0;-10 0" dur="3s" repeatCount="indefinite"/></g>{waves}{bracket}</g>')


def diagram_art():
    boxes = [(-130, -40), (-30, 0), (70, -40)]
    out = (f'<path d="M-82 -18 C-70 18 -50 22 -36 22" fill="none" stroke="{WHITE}" stroke-width="5" stroke-dasharray="2 10" stroke-linecap="round"/>'
           f'<path d="M46 22 C66 22 80 10 90 -12" fill="none" stroke="{WHITE}" stroke-width="5" stroke-dasharray="2 10" stroke-linecap="round"/>')
    for k, (bx, by) in enumerate(boxes):
        out += f'<rect x="{bx}" y="{by}" width="76" height="48" rx="12" fill="{WHITE if k != 1 else SKY}" stroke="{INK}" stroke-width="5"/>'
        out += f'<rect x="{bx + 12}" y="{by + 14}" width="44" height="7" rx="3.5" fill="{INK}" fill-opacity="0.75"/><rect x="{bx + 12}" y="{by + 28}" width="30" height="7" rx="3.5" fill="{BLUE2}"/>'
    out += (f'<circle r="9" fill="{SKY}" stroke="{INK}" stroke-width="4"><animateMotion dur="2.4s" repeatCount="indefinite" '
            f'path="M-82 -18 C-70 18 -50 22 -36 22 L46 22 C66 22 80 10 90 -12"/></circle>')
    out += (f'<g transform="translate(0 -62)"><circle r="22" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M-6 -11 L12 0 L-6 11Z" fill="{BLUE}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 -62;0 -68;0 -62" dur="1.6s" repeatCount="indefinite"/></g>')
    return out


ART = {"book": book_art, "robot": robot_art, "blob": lambda: blob(0, 4, 0.85, cursor=True), "diagram": diagram_art}


# ── Header ────────────────────────────────────────────────────────────────────
def header():
    W, H, PAD = 1200, 420, 12
    title = otext(64, 200, "Abdair Coca", 104, sw=12, shadow=8)
    chips, cx = [], 64
    for label, fill in [("Robots", WHITE), ("AI agents", WHITE), ("Web apps", WHITE), ("Potosí, Bolivia", SKY)]:
        w = len(label) * 12.5 + 44
        chips.append(sticker(cx, 300, w, 46, 23, fill, shadow=5, sw=4) +
                     f'<text x="{cx + w / 2}" y="331" text-anchor="middle" {F} font-weight="600" font-size="22" fill="{INK}">{escape(label)}</text>')
        cx += w + 16
    body = f'''<defs><clipPath id="frame"><rect width="{W}" height="{H}" rx="30"/></clipPath>{halftone("dots")}</defs>
<rect x="{PAD}" y="{PAD}" width="{W}" height="{H}" rx="30" fill="{INK}"/>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BLUE}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>
  {cloud(560, 70, 0.8, 40, 11)}{cloud(150, 418, 0.9, -30, 9)}{cloud(1080, 380, 0.7, -25, 8)}
  {burst(965, 232, 180, 146)}
  <circle cx="965" cy="232" r="120" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>
  {robot(965, 248, 0.92)}
</g>
<rect width="{W}" height="{H}" rx="30" fill="none" stroke="{INK}" stroke-width="6"/>
<g><animateTransform attributeName="transform" type="rotate" values="-3 1110 70;3 1110 70;-3 1110 70" dur="2s" repeatCount="indefinite"/>
  <path d="M1040 40 H1176 Q1188 40 1188 52 V92 Q1188 104 1176 104 H1080 L1060 124 L1064 104 H1040 Q1028 104 1028 92 V52 Q1028 40 1040 40Z" fill="{WHITE}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
  <text x="1108" y="81" text-anchor="middle" {F} font-weight="700" font-size="25" fill="{INK}">beep boop!</text></g>
<g transform="rotate(-4 160 72)">{sticker(64, 48, 236, 50, 25, WHITE, shadow=5, sw=4)}
  <text x="182" y="82" text-anchor="middle" {F} font-weight="700" font-size="24" fill="{INK}">HI THERE, I'M</text></g>
<g><animateTransform attributeName="transform" type="translate" values="0 -30;0 6;0 0" keyTimes="0;0.7;1" dur="0.7s" fill="freeze"/>{title}</g>
<text x="68" y="264" {F} font-weight="600" font-size="31" fill="{WHITE}" stroke="{INK}" stroke-width="6" paint-order="stroke" stroke-linejoin="round">Software Engineering Student</text>
{"".join(chips)}
{star(720, 210, 16, WHITE, 0)}{star(760, 70, 12, SKY, 0.5)}{star(1150, 300, 14, WHITE, 0.9)}{star(700, 360, 10, WHITE, 1.2)}'''
    return svg(W + PAD, H + PAD, body, "Hi there, I'm Abdair Coca, Software Engineering Student")


# ── Terminal ("about me") ─────────────────────────────────────────────────────
def terminal():
    W, PAD, TOP_SPACE = 1200, 12, 70
    LH, FS, X0 = 34, 21, 48
    CH = FS * 0.6  # JetBrains Mono advance = 600/1000 em
    prompt = "abdair@potosi:~$ "
    lines = [("cmd", "whoami"), ("out", WHOAMI), ("blank", None), ("cmd", "cat profile.yml")]
    lines += [("kv", kv) for kv in PROFILE]
    lines += [("blank", None), ("cmd", "ls ./currently-learning"), ("out2", CURRENTLY), ("blank", None), ("end", None)]
    BAR = 60
    y0 = TOP_SPACE + BAR + 52
    H = TOP_SPACE + BAR + 40 + LH * len(lines)
    win_h = H - TOP_SPACE

    body = [f'''<defs><clipPath id="win"><rect x="0" y="{TOP_SPACE}" width="{W}" height="{win_h}" rx="24"/></clipPath>{halftone("tdots", BLUE, 0.06, 26, 2.5)}</defs>
<rect x="{PAD}" y="{TOP_SPACE + PAD}" width="{W}" height="{win_h}" rx="24" fill="{INK}"/>
<g clip-path="url(#win)"><rect y="{TOP_SPACE}" width="{W}" height="{win_h}" fill="{WHITE}"/><rect y="{TOP_SPACE}" width="{W}" height="{win_h}" fill="url(#tdots)"/>
<rect y="{TOP_SPACE}" width="{W}" height="{BAR}" fill="{BLUE}"/><rect y="{TOP_SPACE + BAR - 3}" width="{W}" height="6" fill="{INK}"/></g>
<rect x="0" y="{TOP_SPACE}" width="{W}" height="{win_h}" rx="24" fill="none" stroke="{INK}" stroke-width="6"/>
<circle cx="40" cy="{TOP_SPACE + 30}" r="11" fill="{WHITE}" stroke="{INK}" stroke-width="4"/><circle cx="72" cy="{TOP_SPACE + 30}" r="11" fill="{SKY}" stroke="{INK}" stroke-width="4"/><circle cx="104" cy="{TOP_SPACE + 30}" r="11" fill="{NAVY}" stroke="{INK}" stroke-width="4"/>
<text x="{W / 2}" y="{TOP_SPACE + 39}" text-anchor="middle" {F} font-weight="700" font-size="25" fill="{WHITE}" stroke="{INK}" stroke-width="6" paint-order="stroke" stroke-linejoin="round">about-me.sh</text>
{blob(1040, TOP_SPACE - 18, 0.62)}
<g {M} font-size="{FS}" font-weight="500">''']

    t = 0.4
    for i, (kind, payload) in enumerate(lines):
        y = y0 + i * LH
        if kind == "blank":
            continue
        if kind in ("cmd", "end"):
            body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
                        f'<text x="{X0}" y="{y}"><tspan fill="{BLUE}" font-weight="700">abdair@potosi</tspan><tspan fill="{INK}">:~$</tspan></text></g>')
            t += 0.3
            px = X0 + len(prompt) * CH
            if kind == "end":
                body.append(f'<rect x="{px:.0f}" y="{y - FS + 2}" width="{CH:.0f}" height="{FS + 4}" rx="2" fill="{BLUE}" opacity="0">'
                            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
                continue
            n = len(payload)
            dur = max(0.4, n * 0.065)
            steps = ";".join(f"{k * CH:.1f}" for k in range(n + 1))
            body.append(f'<clipPath id="type{i}"><rect x="{px:.1f}" y="{y - FS - 6}" height="{LH}" width="0">'
                        f'<animate attributeName="width" values="{steps}" begin="{t:.2f}s" dur="{dur:.2f}s" calcMode="discrete" fill="freeze"/></rect></clipPath>')
            body.append(f'<text x="{px:.1f}" y="{y}" fill="{INK}" clip-path="url(#type{i})">{escape(payload)}</text>')
            t += dur + 0.3
        elif kind in ("out", "out2"):
            color = SLATE if kind == "out" else BLUE
            body.append(f'<text x="{X0}" y="{y}" fill="{color}" opacity="0" style="white-space:pre">{escape(payload).replace("  ", "&#160; ")}'
                        f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.25s" fill="freeze"/></text>')
            t += 0.3
        elif kind == "kv":
            k, v = payload
            body.append(f'<text x="{X0}" y="{y}" opacity="0"><tspan fill="{BLUE}" font-weight="700">{escape(k)}:</tspan>'
                        f'<tspan x="{X0 + 9 * CH:.1f}" fill="{INK}">{escape(v)}</tspan>'
                        f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.25s" fill="freeze"/></text>')
            t += 0.15
    body.append("</g>")
    return svg(W + PAD, H + PAD, "\n".join(body), "About me: " + WHOAMI)


# ── Project cards ─────────────────────────────────────────────────────────────
def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    return lines + [cur]


def card(idx, p):
    W, H, PAD, BAND = 600, 400, 12, 160
    desc = wrap(p["desc"], 50)[:3]
    dark_band = p["band"] in (BLUE, NAVY)
    chips, cx = [], 32
    for tag in p["tags"]:
        w = len(tag) * 9.6 + 30
        chips.append(f'<rect x="{cx}" y="334" width="{w:.0f}" height="36" rx="18" fill="{ICE}" stroke="{INK}" stroke-width="3.5"/>'
                     f'<text x="{cx + w / 2:.0f}" y="358" text-anchor="middle" {F} font-weight="600" font-size="17" fill="{INK}">{escape(tag)}</text>')
        cx += w + 10
    desc_svg = "".join(f'<text x="32" y="{250 + k * 27}" {F} font-weight="500" font-size="20" fill="{SLATE}">{escape(l)}</text>'
                       for k, l in enumerate(desc))
    body = f'''<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="26"/></clipPath>{halftone("d", WHITE if dark_band else BLUE, 0.16 if dark_band else 0.12)}</defs>
<rect x="{PAD}" y="{PAD}" width="{W}" height="{H}" rx="26" fill="{INK}"/>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{WHITE}"/>
<rect width="{W}" height="{BAND}" fill="{p["band"]}"/><rect width="{W}" height="{BAND}" fill="url(#d)"/>
<rect y="{BAND - 3}" width="{W}" height="6" fill="{INK}"/>
<g transform="translate({W / 2 + 40} {BAND / 2 + 8})">{ART[p["art"]]()}</g></g>
<rect width="{W}" height="{H}" rx="26" fill="none" stroke="{INK}" stroke-width="6"/>
<g transform="rotate(-6 70 46)">{sticker(30, 26, 84, 42, 21, WHITE, shadow=4, sw=4)}<text x="72" y="56" text-anchor="middle" {F} font-weight="700" font-size="24" fill="{INK}">#{idx + 1}</text></g>
<g transform="translate({W - 62} 48)"><circle cx="3" cy="3" r="24" fill="{INK}"/><circle r="24" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>
<path d="M-8 8 L8 -8 M-5 -8 H8 V5" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<animateTransform attributeName="transform" type="translate" values="{W - 62} 48;{W - 58} 44;{W - 62} 48" dur="1.4s" repeatCount="indefinite"/></g>
<text x="32" y="212" {F} font-weight="700" font-size="40" fill="{INK}">{escape(p["repo"])}</text>
{desc_svg}
{"".join(chips)}'''
    return svg(W + PAD, H + PAD, body, f'{p["repo"]}: {p["desc"]}')


# ── Section titles ────────────────────────────────────────────────────────────
def section_title(text, fill=BLUE, txt=WHITE):
    w = int(len(text) * 25 + 120)
    H, PAD = 84, 10
    body = f'''<g transform="rotate(-1.5 {w / 2} 40)">{sticker(6, 10, w - 20, 64, 32, fill, shadow=7, sw=5)}
{star(52, 42, 15, SKY if fill == BLUE else BLUE)}
{otext(86, 56, text, 40, txt, sw=8 if txt == WHITE else 0, shadow=4 if txt == WHITE else 0)}</g>'''
    return svg(w + PAD, H + PAD, body, text)


# ── Social buttons ────────────────────────────────────────────────────────────
def button(label, icon, fill, txt):
    w = len(label) * 15 + 110
    icons = {
        "linkedin": f'<rect x="-17" y="-17" width="34" height="34" rx="8" fill="{WHITE}" stroke="{INK}" stroke-width="3.5"/>'
                    f'<text x="0" y="9" text-anchor="middle" {F} font-weight="700" font-size="22" fill="{BLUE}">in</text>',
        "instagram": f'<rect x="-17" y="-17" width="34" height="34" rx="10" fill="{WHITE}" stroke="{INK}" stroke-width="3.5"/>'
                     f'<circle r="8" fill="none" stroke="{INK}" stroke-width="3.5"/><circle cx="9" cy="-9" r="2.5" fill="{INK}"/>',
        "pin": f'<path d="M0 17 C-14 2 -15 -4 -15 -6 A15 15 0 0 1 15 -6 C15 -4 14 2 0 17Z" fill="{WHITE}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
               f'<circle cy="-6" r="5" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>',
    }
    body = f'''{sticker(4, 4, w, 60, 30, fill, shadow=6, sw=4.5)}
<g transform="translate(44 34)">{icons[icon]}</g>
<text x="76" y="44" {F} font-weight="700" font-size="26" fill="{txt}">{escape(label)}</text>'''
    return svg(w + 14, 74, body, label)


# ── Footer ────────────────────────────────────────────────────────────────────
def footer():
    W, H, PAD = 1200, 240, 12
    body = f'''<defs><clipPath id="f"><rect width="{W}" height="{H}" rx="30"/></clipPath>{halftone("fd")}</defs>
<rect x="{PAD}" y="{PAD}" width="{W}" height="{H}" rx="30" fill="{INK}"/>
<g clip-path="url(#f)"><rect width="{W}" height="{H}" fill="{BLUE}"/><rect width="{W}" height="{H}" fill="url(#fd)"/>
{cloud(300, 18, 0.5, 30, 10)}{cloud(930, 212, 0.6, -30, 9)}
<rect y="{H - 34}" width="{W}" height="40" fill="{NAVY}" stroke="{INK}" stroke-width="5"/>
{robot(150, 104, 0.68)}{blob(1060, 166, 0.85)}</g>
<rect width="{W}" height="{H}" rx="30" fill="none" stroke="{INK}" stroke-width="6"/>
{otext(W / 2, 112, "Thanks for stopping by!", 58, anchor="middle", sw=11, shadow=6)}
{sticker(W / 2 - 230, 140, 460, 48, 24, WHITE, shadow=5, sw=4)}
<text x="{W / 2}" y="173" text-anchor="middle" {F} font-weight="600" font-size="23" fill="{INK}">Let's build something fun together</text>
{star(290, 160, 12, WHITE, 0.3)}{star(930, 50, 14, SKY, 0.8)}'''
    return svg(W + PAD, H + PAD, body, "Thanks for stopping by! Let's build something fun together")


def main():
    for old in [*OUT.glob("projects/*.svg"), *OUT.glob("titles/*.svg"), *OUT.glob("buttons/*.svg")]:
        old.unlink()
    for d in ("projects", "titles", "buttons"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    (OUT / "terminal.svg").write_text(terminal(), encoding="utf-8")
    (OUT / "footer.svg").write_text(footer(), encoding="utf-8")
    for i, p in enumerate(PROJECTS):
        (OUT / "projects" / f'{p["repo"]}.svg').write_text(card(i, p), encoding="utf-8")
    for name, text, fill, txt in [("projects", "My Projects", BLUE, WHITE), ("toolbox", "Toolbox", WHITE, INK), ("stats", "GitHub Stats", BLUE, WHITE)]:
        (OUT / "titles" / f"{name}.svg").write_text(section_title(text, fill, txt), encoding="utf-8")
    for name, label, icon, fill, txt in [("linkedin", "LinkedIn", "linkedin", BLUE, WHITE), ("instagram", "Instagram", "instagram", WHITE, INK)]:
        (OUT / "buttons" / f"{name}.svg").write_text(button(label, icon, fill, txt), encoding="utf-8")
    print("assets written to", OUT)


if __name__ == "__main__":
    main()
