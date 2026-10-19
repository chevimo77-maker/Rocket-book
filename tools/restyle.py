"""SeaBeans-style redesign: flat bright colours, thick navy outlines, no paper texture,
chubby characters with big heads and open smiles.

apply(tpl, page) restyles one page template (the HTML string produced by the export):
  1. global pass: palette, outlines on scene objects, sticker-style UI, no texture
  2. per-page character redraws from ART below
"""
import re

NAVY = '#1E2A4A'

# Old export palette (purple night, paper texture) -> bright SeaBeans-like palette.
PALETTE = {
    '#221859': '#3F67E0',  # sky
    '#1B1440': NAVY,
    '#2A1A3A': NAVY,
    '#3A1F14': NAVY,
    '#B5520F': NAVY,       # button/number shadows
    '#2A1E6E': '#2F55C8',
    '#24125E': '#2A4BB8',
    '#33257E': '#3559D0',  # ground
    '#1E3A8A': NAVY,
    '#4B33A8': '#6E95F5',  # glows
    '#7A2E8E': '#7FB0FF',
    '#5A45B8': '#9DBBFF',
    '#8E7BE0': '#7FB8FF',
    '#8C7BF0': '#A9C8FF',  # star dust
    '#C6BDF8': '#D2E4FF',
    '#2F5BD6': '#51D0E0',  # accent blue -> aqua (cobalt is now the sky)
    '#4E8BF0': '#4F86F7',
    '#7FD3F7': '#51D0E0',
    '#CFE3FA': '#D2FAFF',
    '#F7C948': '#FFCC5E',
    '#F29BA0': '#FD8CA7',
    '#F07A22': '#FF9F45',
    '#F7A75A': '#FFB870',
    '#E8483A': '#FF6B6B',
    '#D6336C': '#FD6F95',
    '#DCD5F2': '#D2E6FF',
    '#E6E1F7': '#E2F1FF',
    '#C9C1EA': '#B9D4F5',
    '#F4F1FC': '#FFFFFF',
    '#C9CDE0': '#B9D4F5',  # spaceship greys -> light blue
    '#E2E4F0': '#E2F1FF',
    '#B3B7D0': '#9DBBFF',
    '#9A5B3A': '#A86A45',  # Ana's skin
    '#F3C9A8': '#FFD9B8',  # Leo's skin
    '#5A3220': '#6B3E26',
}

OUTLINE = 'stroke="%s" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"' % NAVY


def _recolour(tpl):
    def sub(m):
        return PALETTE.get(m.group(0).upper(), m.group(0))
    return re.sub(r'#[0-9A-Fa-f]{6}\b', sub, tpl)


def _ui(tpl):
    # Caption cards: translucent night panel -> white sticker card with navy text.
    tpl = re.sub(r'(background: rgba\(27,20,64,\.6\); pointer-events: none">\s*<p style="[^"]*?)color: #FFF7E8',
                 r'\1color: ' + NAVY, tpl)
    tpl = tpl.replace('background: rgba(27,20,64,.6);',
                      'background: #FFFFFF; border: 5px solid %s; box-shadow: 0 7px 0 %s;' % (NAVY, NAVY))
    # Round buttons and pills get the thick outline too.
    tpl = tpl.replace('box-shadow: 0 6px 0 rgba(27,20,64,.35)', 'border: 5px solid %s; box-shadow: 0 6px 0 %s' % (NAVY, NAVY))
    tpl = tpl.replace('box-shadow: 0 6px 0 %s"' % NAVY, 'border: 5px solid %s; box-shadow: 0 6px 0 %s"' % (NAVY, NAVY))
    tpl = re.sub(r'border-radius: 999px; background: (#[0-9A-F]{6});', r'border-radius: 999px; background: \1; border: 4px solid ' + NAVY + ';', tpl)
    # Big titles: white letters with a fat navy outline, like the SeaBeans logo.
    tpl = tpl.replace('text-shadow: 0 6px 0 rgba(27,20,64,.45)',
                      '-webkit-text-stroke: 10px %s; paint-order: stroke fill; text-shadow: 0 8px 0 %s' % (NAVY, NAVY))
    return tpl


def _global(tpl):
    tpl = _recolour(tpl)
    # Flat look: drop the paper/grain overlays and the rim-shading filter; every object that
    # used the filter gets a thick navy sticker outline instead (cheaper to render, too).
    tpl = re.sub(r'<div class="nz nz-\w+"[^>]*></div>\n?', '', tpl)
    tpl = re.sub(r'<filter id="shade".*?</filter>\n?', '', tpl, flags=re.S)
    tpl = re.sub(r'class="([^"]+)" filter="url\(#shade\)"', r'class="\1 ol"', tpl)
    tpl = tpl.replace(' filter="url(#shade)"', ' class="ol"')
    return _ui(tpl)


def _group(tpl, opening):
    """(start, end) of the <g ...> element that begins with `opening`, matched by nesting."""
    start = tpl.index(opening)
    depth, i = 0, start
    for m in re.finditer(r'<g\b|</g>', tpl[start:]):
        depth += 1 if m.group(0) == '<g' else -1
        if depth == 0:
            return start, start + m.end()
    raise ValueError(opening)


def _swap(tpl, opening, new):
    s, e = _group(tpl, opening)
    return tpl[:s] + new + tpl[e:]


# ---------------------------------------------------------------- characters

ROCKET_BODY = 'M-64 -40 Q-86 -40 -86 -90 L-86 -210 Q-86 -340 0 -380 Q86 -340 86 -210 L86 -90 Q86 -40 64 -40Z'


def rocket_face(dy=0, mouth=True):
    y = lambda v: v + dy
    m = (f'<path d="M-28 {y(-184)} Q0 {y(-182)} 28 {y(-184)} Q26 {y(-142)} 0 {y(-140)} Q-26 {y(-142)} -28 {y(-184)}Z" fill="#B23A5A" {OUTLINE}></path>'
         f'<path d="M-14 {y(-152)} Q0 {y(-165)} 14 {y(-152)} Q9 {y(-142)} 0 {y(-141)} Q-9 {y(-142)} -14 {y(-152)}Z" fill="#FD8CA7"></path>') if mouth else \
        f'<path d="M-16 {y(-170)} Q0 {y(-156)} 16 {y(-170)}" fill="none" stroke="{NAVY}" stroke-width="6" stroke-linecap="round"></path>'
    return (f'<ellipse cx="-30" cy="{y(-206)}" rx="12" ry="15" fill="{NAVY}"></ellipse><ellipse cx="30" cy="{y(-206)}" rx="12" ry="15" fill="{NAVY}"></ellipse>'
            f'<circle cx="-25" cy="{y(-212)}" r="5" fill="#FFFFFF"></circle><circle cx="35" cy="{y(-212)}" r="5" fill="#FFFFFF"></circle>'
            f'<ellipse cx="-56" cy="{y(-176)}" rx="15" ry="9" fill="#FD8CA7" opacity=".9"></ellipse><ellipse cx="56" cy="{y(-176)}" rx="15" ry="9" fill="#FD8CA7" opacity=".9"></ellipse>' + m)


def rocket(flk='flk', cid='rkC', *, flame=True, flame_cls='flame', face=True, face_dy=0, band=True,
           windows=None, crew_cls=None, inside='', front='', fins=True):
    """Chubby smiling rocket. Origin at the nozzle bottom, pointing up (~380 tall, 172 wide).
    windows: (who_left, who_right) faces in two portholes on the nose cone ('ana'/'leo'/None=glass).
    inside: extra art clipped to the body; front: extra art drawn on top."""
    body = ROCKET_BODY
    out = ''
    if flame:
        out += (f'<g class="{flame_cls}"><path class="{flk}" d="M-36 -6 Q0 150 36 -6Z" fill="#FF9F45" {OUTLINE}></path>'
                f'<path class="{flk}" d="M-22 -6 Q0 100 22 -6Z" fill="#FFCC5E"></path><path class="{flk}" d="M-11 -6 Q0 58 11 -6Z" fill="#FFF8EC"></path></g>')
    if fins:
        out += (f'<path d="M-78 -150 Q-134 -112 -130 -48 Q-128 -22 -100 -36 L-78 -62Z" fill="#FD8CA7" {OUTLINE}></path>'
                f'<path d="M78 -150 Q134 -112 130 -48 Q128 -22 100 -36 L78 -62Z" fill="#FD8CA7" {OUTLINE}></path>')
    out += f'<path d="M-38 -44 L-44 -8 Q0 4 44 -8 L38 -44Z" fill="#51D0E0" {OUTLINE}></path>'
    out += f'<clipPath id="{cid}"><path d="{body}"></path></clipPath><path d="{body}" fill="#FFFFFF"></path><g clip-path="url(#{cid})">'
    out += '<path d="M46 -30 Q82 -200 30 -400 L110 -400 L110 -30Z" fill="#D2E6FF"></path>'
    out += f'<path d="M-110 -288 Q0 -322 110 -288 L110 -400 L-110 -400Z" fill="#FF6B6B"></path><path d="M-110 -288 Q0 -322 110 -288" fill="none" stroke="{NAVY}" stroke-width="5"></path>'
    if band:
        out += (f'<rect x="-110" y="-112" width="220" height="30" fill="#FFCC5E"></rect><path d="M-110 -112 H110 M-110 -82 H110" stroke="{NAVY}" stroke-width="5"></path>'
                f'<g fill="{NAVY}"><circle cx="-40" cy="-97" r="4.5"></circle><circle cx="0" cy="-97" r="4.5"></circle><circle cx="40" cy="-97" r="4.5"></circle></g>')
    out += inside
    out += '<path d="M-52 -326 Q-38 -348 -16 -358" fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" opacity=".8"></path></g>'
    out += f'<path d="{body}" fill="none" stroke="{NAVY}" stroke-width="7" stroke-linejoin="round"></path>'
    if windows:
        for x, who in ((-24, windows[0]), (24, windows[1])):
            out += f'<circle cx="{x}" cy="-326" r="17" fill="#FFCC5E" {OUTLINE}></circle>'
            if who:
                out += window_face(who, x, -326, 12, crew_cls or '')
            else:
                out += f'<circle cx="{x}" cy="-326" r="11" fill="#51D0E0"></circle><circle cx="{x - 4}" cy="-330" r="3" fill="#FFFFFF"></circle>'
    if face:
        out += rocket_face(face_dy)
    return out + front


# ---- astronauts: Ana (curly hair) and Leo (glasses). Helmet centre at (0, 0), boots at y~126.

SKIN = {'ana': '#A86A45', 'leo': '#FFD9B8'}


def face(who):
    """Face for a head of radius ~47 centred at (0, 10): big eyes, blush, open smile."""
    if who == 'ana':
        hair_back = '<circle cx="0" cy="-18" r="14" fill="#2A1A14"></circle>'
        hair = ('<g fill="#2A1A14"><circle cx="-32" cy="0" r="13"></circle><circle cx="-19" cy="-12" r="14"></circle>'
                '<circle cx="0" cy="-17" r="14"></circle><circle cx="19" cy="-12" r="14"></circle><circle cx="32" cy="0" r="13"></circle>'
                '<circle cx="-39" cy="15" r="8"></circle><circle cx="39" cy="15" r="8"></circle></g>')
        eyes = (f'<ellipse cx="-16" cy="15" rx="7" ry="9" fill="{NAVY}"></ellipse><ellipse cx="16" cy="15" rx="7" ry="9" fill="{NAVY}"></ellipse>'
                '<circle cx="-13.5" cy="11.5" r="2.8" fill="#FFFFFF"></circle><circle cx="18.5" cy="11.5" r="2.8" fill="#FFFFFF"></circle>'
                f'<path d="M-24 7 l-5 -4 M24 7 l5 -4" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"></path>')
    else:
        hair_back = ''
        hair = '<path d="M-46 4 Q-48 -34 0 -34 Q46 -34 46 2 Q34 -12 20 -12 Q10 0 -4 -10 Q-22 -2 -46 4Z" fill="#6B3E26"></path>'
        eyes = (f'<g fill="none" stroke="{NAVY}" stroke-width="4"><circle cx="-17" cy="12" r="14"></circle><circle cx="17" cy="12" r="14"></circle><path d="M-3 10 Q0 7 3 10"></path></g>'
                f'<ellipse cx="-17" cy="13" rx="5.5" ry="7" fill="{NAVY}"></ellipse><ellipse cx="17" cy="13" rx="5.5" ry="7" fill="{NAVY}"></ellipse>'
                '<circle cx="-15" cy="10" r="2.2" fill="#FFFFFF"></circle><circle cx="19" cy="10" r="2.2" fill="#FFFFFF"></circle>')
    return (hair_back + f'<circle cy="10" r="47" fill="{SKIN[who]}"></circle>' + hair + eyes +
            '<ellipse cx="-31" cy="34" rx="8" ry="5" fill="#FD8CA7"></ellipse><ellipse cx="31" cy="34" rx="8" ry="5" fill="#FD8CA7"></ellipse>'
            f'<path d="M-13 30 Q0 31 13 30 Q11 48 0 48 Q-11 48 -13 30Z" fill="#B23A5A" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"></path>'
            '<path d="M-6 42 Q0 36 6 42 Q3 47 0 47 Q-3 47 -6 42Z" fill="#FD8CA7"></path>')


def window_face(who, x, y, r, cls=''):
    """A face peeking out of a round porthole of radius r centred at (x, y)."""
    k = r / 50.0
    c = f' class="{cls}"' if cls else ''
    return (f'<g{c} transform="translate({x} {y}) scale({k:.3f})"><clipPath id="wf{who}{abs(int(x))}{abs(int(y))}"><circle r="50"></circle></clipPath>'
            f'<g clip-path="url(#wf{who}{abs(int(x))}{abs(int(y))})"><circle r="50" fill="#D2FAFF"></circle><g transform="translate(0 2)">{face(who)}</g></g></g>')


SUIT_LEGS = f'''<rect x="-34" y="86" width="28" height="34" rx="13" fill="#FFFFFF" {OUTLINE}></rect>
<rect x="6" y="86" width="28" height="34" rx="13" fill="#FFFFFF" {OUTLINE}></rect>
<rect x="-38" y="106" width="34" height="20" rx="10" fill="#51D0E0" {OUTLINE}></rect>
<rect x="4" y="106" width="34" height="20" rx="10" fill="#51D0E0" {OUTLINE}></rect>'''
SUIT_BODY = f'''<path d="M-50 100 Q-56 44 0 42 Q56 44 50 100 Q0 112 -50 100Z" fill="#FFFFFF" {OUTLINE}></path>
<rect x="-17" y="70" width="34" height="22" rx="7" fill="#51D0E0" {OUTLINE}></rect>
<circle cx="-6" cy="81" r="3.5" fill="#FFCC5E"></circle><circle cx="6" cy="81" r="3.5" fill="#FF6B6B"></circle>'''


def arm(side, glove=True):
    x = -68 if side < 0 else 42
    g = f'<circle cx="{x + 13}" cy="98" r="13" fill="#D2FAFF" {OUTLINE}></circle>' if glove else ''
    return f'<rect x="{x}" y="58" width="26" height="38" rx="13" fill="#FFFFFF" {OUTLINE}></rect>' + g


def glove(side):
    x = -55 if side < 0 else 55
    return f'<circle cx="{x}" cy="98" r="13" fill="#D2FAFF" {OUTLINE}></circle>'


HELMET_BACK = f'''<path d="M22 -74 Q28 -98 46 -98" fill="none" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"></path><circle cx="48" cy="-99" r="8" fill="#FFCC5E" {OUTLINE}></circle>
<circle cx="-74" cy="0" r="15" fill="#FFCC5E" {OUTLINE}></circle><circle cx="74" cy="0" r="15" fill="#FFCC5E" {OUTLINE}></circle>
<circle r="76" fill="#FFFFFF" stroke="{NAVY}" stroke-width="6"></circle>
<circle cy="4" r="58" fill="#D2FAFF" {OUTLINE}></circle>'''
HELMET_SHINE = '<path d="M-40 -30 Q-28 -46 -10 -50" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"></path>'


def head(who):
    return HELMET_BACK + f'<g transform="translate(0 0)">{face(who)}</g>' + HELMET_SHINE


def astronaut(who, left='', right='', wrap_right=None, wrap_left=None):
    """Full astronaut. wrap_*: class for an animated arm group (e.g. 'wv', 'arm')."""
    la = arm(-1); ra = arm(1)
    if wrap_left:
        la = f'<g class="{wrap_left}">{la}</g>'
    if wrap_right:
        ra = f'<g class="{wrap_right}">{ra}</g>'
    return SUIT_LEGS + la + SUIT_BODY + ra + head(who)


ASTRONAUT = astronaut('leo', wrap_right='wv')


MOON = f'''
<circle r="306" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-dasharray="4 16" stroke-linecap="round" opacity=".5"></circle>
<clipPath id="moonC"><circle r="280"></circle></clipPath>
<circle r="280" fill="#F7C25C"></circle>
<g clip-path="url(#moonC)">
<circle cx="-34" cy="-30" r="276" fill="#FFE08A"></circle>
<circle cx="-150" cy="-160" r="34" fill="#F7C25C" {OUTLINE}></circle><circle cx="176" cy="-120" r="22" fill="#F7C25C" {OUTLINE}></circle>
<circle cx="170" cy="80" r="40" fill="#F7C25C" {OUTLINE}></circle><circle cx="-210" cy="70" r="22" fill="#F7C25C" {OUTLINE}></circle>
</g>
<circle r="280" fill="none" stroke="{NAVY}" stroke-width="8"></circle>
<g transform="translate(-10 -80)">
<ellipse cx="-50" cy="0" rx="17" ry="22" fill="{NAVY}"></ellipse><ellipse cx="50" cy="0" rx="17" ry="22" fill="{NAVY}"></ellipse>
<circle cx="-44" cy="-8" r="6" fill="#FFFFFF"></circle><circle cx="56" cy="-8" r="6" fill="#FFFFFF"></circle>
<rect class="lid" x="-72" y="-26" width="44" height="52" rx="22" fill="#FFE08A"></rect>
<rect class="lid" x="28" y="-26" width="44" height="52" rx="22" fill="#FFE08A"></rect>
<path d="M-72 -40 Q-50 -54 -28 -42" fill="none" stroke="{NAVY}" stroke-width="7" stroke-linecap="round"></path>
<path d="M28 -42 Q50 -54 72 -40" fill="none" stroke="{NAVY}" stroke-width="7" stroke-linecap="round"></path>
<ellipse cx="-96" cy="46" rx="22" ry="13" fill="#FD8CA7"></ellipse><ellipse cx="96" cy="46" rx="22" ry="13" fill="#FD8CA7"></ellipse>
<path d="M-42 34 Q0 38 42 34 Q38 96 0 98 Q-38 96 -42 34Z" fill="#B23A5A" stroke="{NAVY}" stroke-width="7" stroke-linejoin="round"></path>
<path d="M-22 80 Q0 62 22 80 Q14 96 0 97 Q-14 96 -22 80Z" fill="#FD8CA7"></path>
</g>
'''


def art(transform, inner, cls=''):
    """Wrap redrawn art; .art keeps the generic .ol outline rule off it."""
    c = ('art ' + cls).strip()
    return f'<g class="{c}" transform="{transform}">{inner}</g>'


# ---------------------------------------------------------------- generic passes

_OLD_ASTRO = re.compile(
    r'<rect x="-32" y="74" width="26" height="44" rx="12" fill="#FFFFFF"></rect><rect x="6" y="74".*?'
    r'<path d="M-30 -18 Q-20 -30 -6 -32" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity="\.9"></path>',
    re.S)
_OLD_MINI = re.compile(
    r'<g transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([\d.]+)\)">\n<rect x="-42" y="34" width="84" height="56" rx="24" fill="#FFFFFF"></rect>.*?\n</g>',
    re.S)


def _astronauts(tpl):
    """Every old full-body astronaut (Ana / Leo) -> the new chubby one, keeping its arm animation."""
    def full(m):
        g = m.group(0)
        who = 'ana' if SKIN['ana'] in g else 'leo'
        arm_cls = re.search(r'<g class="(wv|arm)">', g)
        return '<g class="art">' + astronaut(who, wrap_right=arm_cls.group(1) if arm_cls else None) + '</g>'
    tpl = _OLD_ASTRO.sub(full, tpl)

    def mini(m):
        who = 'ana' if SKIN['ana'] in m.group(0) else 'leo'
        k = float(m.group(3)) * 0.85
        return art(f'translate({m.group(1)} {m.group(2)}) scale({k:.3f})', astronaut(who))
    return _OLD_MINI.sub(mini, tpl)


def _mouths(tpl):
    """Small closed smiles -> open SeaBeans smiles with a tongue (any remaining face)."""
    def open_mouth(x1, y, xc, x2, sw):
        w = x2 - x1
        h = w * 0.75
        return (f'<path d="M{x1:g} {y:g} Q{xc:g} {y + 1:g} {x2:g} {y:g} Q{x2 - w * .08:g} {y + h:g} {xc:g} {y + h:g} '
                f'Q{x1 + w * .08:g} {y + h:g} {x1:g} {y:g}Z" fill="#B23A5A" stroke="{NAVY}" stroke-width="{sw:g}" stroke-linejoin="round"></path>'
                f'<ellipse cx="{xc:g}" cy="{y + h * .72:g}" rx="{w * .24:g}" ry="{h * .2:g}" fill="#FD8CA7"></ellipse>')

    num = r'(-?[\d.]+)'
    stroked = re.compile(rf'<path d="M{num} {num} Q{num} {num} {num} \2" fill="none" stroke="{NAVY}" stroke-width="{num}" stroke-linecap="round"></path>')

    def s1(m):
        x1, y, xc, yc, x2, sw = (float(m.group(i)) for i in (1, 2, 3, 4, 5, 6))
        if yc <= y or not 8 <= x2 - x1 <= 44:
            return m.group(0)
        return open_mouth(x1 - 2, y - 1, xc, x2 + 2, max(2.5, sw * .8))
    tpl = stroked.sub(s1, tpl)

    filled = re.compile(rf'<path d="M{num} {num} Q{num} {num} {num} \2Z" fill="#FD6F95"></path>')

    def s2(m):
        x1, y, xc, yc, x2 = (float(m.group(i)) for i in (1, 2, 3, 4, 5))
        if yc <= y or not 8 <= x2 - x1 <= 44:
            return m.group(0)
        return open_mouth(x1 - 3, y - 1, xc, x2 + 3, 3)
    return filled.sub(s2, tpl)


# ---------------------------------------------------------------- pages

def _cover(tpl):
    tpl = _swap(tpl, '<g transform="translate(880 700)" class="ol">', art('translate(880 700)', MOON))
    tpl = _swap(tpl, '<g transform="translate(1010 380) rotate(-18) scale(.95)" class="ol">',
                art('translate(1010 380) rotate(-18) scale(1.05)', ASTRONAUT))
    tpl = _swap(tpl, '<g transform="translate(300 830) rotate(22) scale(1)" class="ol">',
                art('translate(300 812) rotate(22) scale(.98)', '<g class="rk">' + rocket('flk', 'rkC', windows=(None, None)) + '</g>'))
    return tpl


LAYERED_LEO = (
    '<g class="me">'
    '<rect x="-34" y="86" width="28" height="34" rx="13" fill="#A9C8FF" ' + OUTLINE + '></rect>'
    '<rect x="6" y="86" width="28" height="34" rx="13" fill="#A9C8FF" ' + OUTLINE + '></rect>'
    '<rect x="-68" y="58" width="26" height="38" rx="13" fill="#A9C8FF" ' + OUTLINE + '></rect>'
    '<rect x="42" y="58" width="26" height="38" rx="13" fill="#A9C8FF" ' + OUTLINE + '></rect>'
    '<path d="M-50 100 Q-56 44 0 42 Q56 44 50 100 Q0 112 -50 100Z" fill="#A9C8FF" ' + OUTLINE + '></path>'
    '<circle cx="-55" cy="98" r="11" fill="#FFD9B8" ' + OUTLINE + '></circle><circle cx="55" cy="98" r="11" fill="#FFD9B8" ' + OUTLINE + '></circle>'
    '<g class="suit">' + SUIT_LEGS + arm(-1, glove=False) + arm(1, glove=False) + SUIT_BODY + '</g>'
    '<g class="glv">' + glove(-1) + '</g><g class="glv">' + glove(1) + '</g>'
    + face('leo') +
    '<g class="helm">'
    '<path d="M22 -74 Q28 -98 46 -98" fill="none" stroke="' + NAVY + '" stroke-width="5" stroke-linecap="round"></path><circle cx="48" cy="-99" r="8" fill="#FFCC5E" ' + OUTLINE + '></circle>'
    '<circle cx="-74" cy="0" r="15" fill="#FFCC5E" ' + OUTLINE + '></circle><circle cx="74" cy="0" r="15" fill="#FFCC5E" ' + OUTLINE + '></circle>'
    '<circle cy="4" r="58" fill="#D2FAFF" opacity=".3"></circle>'
    '<path d="M-76 0 A76 76 0 1 0 76 0 A76 76 0 1 0 -76 0Z M-58 4 A58 58 0 1 1 58 4 A58 58 0 1 1 -58 4Z" fill="#FFFFFF" fill-rule="evenodd" stroke="' + NAVY + '" stroke-width="6"></path>'
    + HELMET_SHINE + '</g></g>')


def _suit_up(tpl):
    return _swap(tpl, '<g transform="translate(600 470) scale(1.55)" class="ol">', art('translate(600 470) scale(1.4)', LAYERED_LEO))


def _rollout(tpl):
    strut = (f'<rect x="96" y="-470" width="20" height="450" fill="{NAVY}"></rect>'
             '<path d="M96 -430 L116 -390 M116 -430 L96 -390 M96 -330 L116 -290 M116 -330 L96 -290 M96 -230 L116 -190 M116 -230 L96 -190" stroke="#FFCC5E" stroke-width="4"></path>')
    tpl = _swap(tpl, '<g transform="translate(860 600)" class="ol">',
                art('translate(860 600)', '<g class="tilt"><g transform="scale(.8)">' + strut + rocket(cid='rkR', flame=False, windows=(None, None)) + '</g></g>'))
    return tpl.replace('<g class="truck">', '<g class="truck ol">')


def _fuel(tpl):
    gauges = (f'<rect x="-50" y="-150" width="42" height="96" rx="14" fill="#2F55C8" {OUTLINE}></rect>'
              '<rect class="lv lvB" x="-50" y="-150" width="42" height="96" rx="14" fill="#51D0E0"></rect>'
              f'<rect x="8" y="-150" width="42" height="96" rx="14" fill="#2F55C8" {OUTLINE}></rect>'
              '<rect class="lv lvO" x="8" y="-150" width="42" height="96" rx="14" fill="#FFCC5E"></rect>'
              f'<rect x="-50" y="-150" width="42" height="96" rx="14" fill="none" stroke="{NAVY}" stroke-width="5"></rect>'
              f'<rect x="8" y="-150" width="42" height="96" rx="14" fill="none" stroke="{NAVY}" stroke-width="5"></rect>')
    ice = ('<g class="ice" fill="#FFFFFF"><rect x="-100" y="-290" width="200" height="60" opacity=".75"></rect>'
           '<rect x="-60" y="-232" width="8" height="18" rx="4"></rect><rect x="-14" y="-232" width="8" height="24" rx="4"></rect><rect x="40" y="-232" width="8" height="15" rx="4"></rect></g>')
    return _swap(tpl, '<g transform="translate(700 716) scale(1.35)" class="ol">',
                 art('translate(700 716) scale(1.3)', rocket(cid='rkF', flame=False, band=False, face_dy=-30, windows=(None, None), inside=ice, front=gauges)))


def _board(tpl):
    hatch = (f'<rect x="44" y="-292" width="26" height="34" rx="9" fill="{NAVY}"></rect>'
             f'<rect class="hatch" x="44" y="-292" width="26" height="34" rx="9" fill="#D2E6FF" {OUTLINE}></rect>')
    tpl = _swap(tpl, '<g transform="translate(700 740) scale(1.4)" class="ol">',
                art('translate(672 740) scale(1.15)', rocket(cid='rkB', flame=False, windows=('ana', 'leo'), crew_cls='faces', front=hatch)))
    # The chubby rocket is shorter: the elevator and access arm stop at its portholes.
    tpl = tpl.replace('translateY(-536px)', 'translateY(-330px)')
    tpl = tpl.replace('<rect x="750" y="198" width="56" height="12"', '<rect x="750" y="372" width="56" height="12"')
    tpl = tpl.replace('<path d="M752 198 V170 H806"', '<path d="M752 372 V344 H806"')
    return tpl.replace('<path d="M770 170 V198 M788 170 V198"', '<path d="M770 344 V372 M788 344 V372"')


def _countdown(tpl):
    tpl = _swap(tpl, '<g transform="translate(300 726) scale(1.45)" class="ol">',
                art('translate(300 726) scale(1.3)', rocket('flick', 'rkC', windows=('ana', 'leo'))))
    # Countdown planet and launch clamps get outlines; the numbers a navy edge.
    tpl = tpl.replace('<circle cx="880" cy="480" r="175" fill="#FF9F45"></circle>',
                      '<circle cx="880" cy="480" r="175" fill="#FF9F45" stroke="%s" stroke-width="8"></circle>' % NAVY)
    tpl = tpl.replace('<g fill="#FF6B6B">\n<g class="clL">', '<g fill="#FF6B6B" %s>\n<g class="clL">' % OUTLINE)
    tpl = tpl.replace('<g fill="#FFF7E8">\n<circle class="smoke"', '<g fill="#FFF8EC" %s>\n<circle class="smoke"' % OUTLINE)
    return tpl


def _liftoff(tpl):
    tpl = _swap(tpl, '<g transform="translate(600 716) scale(1.3)" class="ol">',
                art('translate(600 716) scale(1.2)', rocket('flick', 'rkL', windows=('ana', 'leo'))))
    tpl = _swap(tpl, '<g transform="scale(.45)">', art('scale(.5)', rocket('flick', 'rkL2', flame_cls='fl2', windows=(None, None))))
    return tpl.replace('<g fill="#FFF7E8">\n<circle class="smoke"', '<g fill="#FFF8EC" %s>\n<circle class="smoke"' % OUTLINE)


def _booster(tpl):
    upper = (
        '<g class="upFl"><path class="flick" d="M-22 -236 Q0 -140 22 -236Z" fill="#FF9F45" ' + OUTLINE + '></path>'
        '<path class="flick" d="M-11 -236 Q0 -180 11 -236Z" fill="#FFCC5E"></path></g>'
        '<path d="M-28 -254 L-34 -236 L34 -236 L28 -254Z" fill="#51D0E0" ' + OUTLINE + '></path>'
        '<path d="M-70 -252 L-70 -330 Q-70 -420 0 -452 Q70 -420 70 -330 L70 -252Z" fill="#FFFFFF"></path>'
        '<path d="M-64 -372 Q-52 -425 0 -452 Q52 -425 64 -372 Q0 -394 -64 -372Z" fill="#FF6B6B" ' + OUTLINE + '></path>'
        '<path d="M-70 -252 L-70 -330 Q-70 -420 0 -452 Q70 -420 70 -330 L70 -252Z" fill="none" stroke="' + NAVY + '" stroke-width="7" stroke-linejoin="round"></path>'
        '<circle cx="-24" cy="-318" r="17" fill="#FFCC5E" ' + OUTLINE + '></circle><circle cx="24" cy="-318" r="17" fill="#FFCC5E" ' + OUTLINE + '></circle>'
        + window_face('ana', -24, -318, 12) + window_face('leo', 24, -318, 12))
    body = 'M-70 -236 L70 -236 L70 -60 Q70 -32 46 -32 L-46 -32 Q-70 -32 -70 -60Z'
    booster = (
        '<g class="mainFl"><path class="flick" d="M-34 -2 Q0 150 34 -2Z" fill="#FF9F45" ' + OUTLINE + '></path><path class="flick" d="M-16 -2 Q0 80 16 -2Z" fill="#FFCC5E"></path></g>'
        '<g class="landFl"><path class="flick" d="M-14 -2 Q0 90 14 -2Z" fill="#FF9F45" ' + OUTLINE + '></path></g>'
        '<g class="legs"><path d="M-62 -44 L-104 8 L-88 14 L-54 -16Z" fill="#FD8CA7" ' + OUTLINE + '></path>'
        '<path d="M62 -44 L104 8 L88 14 L54 -16Z" fill="#FD8CA7" ' + OUTLINE + '></path></g>'
        '<path d="M-38 -34 L-44 0 L44 0 L38 -34Z" fill="#51D0E0" ' + OUTLINE + '></path>'
        f'<path d="{body}" fill="#FFFFFF"></path>'
        '<path d="M44 -236 L70 -236 L70 -60 Q70 -32 46 -32 L44 -32Z" fill="#D2E6FF"></path>'
        '<rect x="-70" y="-236" width="140" height="22" fill="#51D0E0"></rect>'
        f'<rect x="-70" y="-90" width="140" height="22" fill="#FFCC5E"></rect><path d="M-70 -214 H70 M-70 -90 H70 M-70 -68 H70" stroke="{NAVY}" stroke-width="5"></path>'
        f'<path d="{body}" fill="none" stroke="{NAVY}" stroke-width="7" stroke-linejoin="round"></path>'
        '<g class="fins"><rect x="-96" y="-232" width="24" height="22" rx="5" fill="#51D0E0" ' + OUTLINE + '></rect>'
        '<rect x="72" y="-232" width="24" height="22" rx="5" fill="#51D0E0" ' + OUTLINE + '></rect></g>'
        + rocket_face(46))
    tpl = _swap(tpl, '<g class="upSep ol">', '<g class="upSep art">' + upper + '</g>')
    return _swap(tpl, '<g class="boFlip ol">', '<g class="boFlip art">' + booster + '</g>')


def _moonwalk(tpl):
    # The lander resting in the distance gets the same outline as on the landing page.
    return tpl.replace('<g transform="translate(140 600) scale(.38)">', '<g class="ol" transform="translate(140 600) scale(.38)">')


PAGES = {
    'p13-moonwalk': _moonwalk,
    'p01-cover': _cover, 'p03-suit-up': _suit_up, 'p04-rollout': _rollout, 'p05-fuel': _fuel,
    'p06-board': _board, 'p07-countdown': _countdown, 'p08-liftoff': _liftoff, 'p09-booster': _booster,
}


def apply(tpl, page):
    tpl = _global(tpl)
    if page in PAGES:
        tpl = PAGES[page](tpl)
    tpl = _astronauts(tpl)
    return _mouths(tpl)
