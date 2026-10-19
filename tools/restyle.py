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

def rocket(flk, cid):
    """Chubby smiling rocket. Origin at the nozzle bottom, pointing up (~380 tall)."""
    body = 'M-64 -40 Q-86 -40 -86 -90 L-86 -210 Q-86 -340 0 -380 Q86 -340 86 -210 L86 -90 Q86 -40 64 -40Z'
    return f'''
<g class="flame"><path class="{flk}" d="M-36 -6 Q0 150 36 -6Z" fill="#FF9F45" {OUTLINE}></path><path class="{flk}" d="M-22 -6 Q0 100 22 -6Z" fill="#FFCC5E"></path><path class="{flk}" d="M-11 -6 Q0 58 11 -6Z" fill="#FFF8EC"></path></g>
<path d="M-78 -150 Q-134 -112 -130 -48 Q-128 -22 -100 -36 L-78 -62Z" fill="#FD8CA7" {OUTLINE}></path>
<path d="M78 -150 Q134 -112 130 -48 Q128 -22 100 -36 L78 -62Z" fill="#FD8CA7" {OUTLINE}></path>
<path d="M-38 -44 L-44 -8 Q0 4 44 -8 L38 -44Z" fill="#51D0E0" {OUTLINE}></path>
<clipPath id="{cid}"><path d="{body}"></path></clipPath>
<path d="{body}" fill="#FFFFFF"></path>
<g clip-path="url(#{cid})">
<path d="M46 -30 Q82 -200 30 -400 L110 -400 L110 -30Z" fill="#D2E6FF"></path>
<path d="M-110 -288 Q0 -322 110 -288 L110 -400 L-110 -400Z" fill="#FF6B6B"></path>
<path d="M-110 -288 Q0 -322 110 -288" fill="none" stroke="{NAVY}" stroke-width="5"></path>
<rect x="-110" y="-112" width="220" height="30" fill="#FFCC5E"></rect>
<path d="M-110 -112 H110 M-110 -82 H110" stroke="{NAVY}" stroke-width="5"></path>
<g fill="{NAVY}"><circle cx="-40" cy="-97" r="4.5"></circle><circle cx="0" cy="-97" r="4.5"></circle><circle cx="40" cy="-97" r="4.5"></circle></g>
<path d="M-52 -326 Q-38 -348 -16 -358" fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" opacity=".8"></path>
</g>
<path d="{body}" fill="none" stroke="{NAVY}" stroke-width="7" stroke-linejoin="round"></path>
<ellipse cx="-30" cy="-206" rx="12" ry="15" fill="{NAVY}"></ellipse><ellipse cx="30" cy="-206" rx="12" ry="15" fill="{NAVY}"></ellipse>
<circle cx="-25" cy="-212" r="5" fill="#FFFFFF"></circle><circle cx="35" cy="-212" r="5" fill="#FFFFFF"></circle>
<ellipse cx="-56" cy="-176" rx="15" ry="9" fill="#FD8CA7" opacity=".9"></ellipse><ellipse cx="56" cy="-176" rx="15" ry="9" fill="#FD8CA7" opacity=".9"></ellipse>
<path d="M-28 -184 Q0 -182 28 -184 Q26 -142 0 -140 Q-26 -142 -28 -184Z" fill="#B23A5A" {OUTLINE}></path>
<path d="M-14 -152 Q0 -165 14 -152 Q9 -142 0 -141 Q-9 -142 -14 -152Z" fill="#FD8CA7"></path>
'''


ASTRONAUT = f'''
<rect x="-34" y="86" width="28" height="34" rx="13" fill="#FFFFFF" {OUTLINE}></rect>
<rect x="6" y="86" width="28" height="34" rx="13" fill="#FFFFFF" {OUTLINE}></rect>
<rect x="-38" y="106" width="34" height="20" rx="10" fill="#51D0E0" {OUTLINE}></rect>
<rect x="4" y="106" width="34" height="20" rx="10" fill="#51D0E0" {OUTLINE}></rect>
<rect x="-68" y="58" width="26" height="38" rx="13" fill="#FFFFFF" {OUTLINE}></rect><circle cx="-55" cy="98" r="13" fill="#D2FAFF" {OUTLINE}></circle>
<path d="M-50 100 Q-56 44 0 42 Q56 44 50 100 Q0 112 -50 100Z" fill="#FFFFFF" {OUTLINE}></path>
<rect x="-17" y="70" width="34" height="22" rx="7" fill="#51D0E0" {OUTLINE}></rect>
<circle cx="-6" cy="81" r="3.5" fill="#FFCC5E"></circle><circle cx="6" cy="81" r="3.5" fill="#FF6B6B"></circle>
<g class="wv"><rect x="42" y="58" width="26" height="38" rx="13" fill="#FFFFFF" {OUTLINE}></rect><circle cx="55" cy="98" r="13" fill="#D2FAFF" {OUTLINE}></circle></g>
<path d="M22 -74 Q28 -98 46 -98" fill="none" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"></path><circle cx="48" cy="-99" r="8" fill="#FFCC5E" {OUTLINE}></circle>
<circle cx="-74" cy="0" r="15" fill="#FFCC5E" {OUTLINE}></circle><circle cx="74" cy="0" r="15" fill="#FFCC5E" {OUTLINE}></circle>
<circle r="76" fill="#FFFFFF" stroke="{NAVY}" stroke-width="6"></circle>
<circle cy="4" r="58" fill="#D2FAFF" {OUTLINE}></circle>
<circle cy="10" r="47" fill="#FFD9B8"></circle>
<path d="M-46 4 Q-48 -34 0 -34 Q46 -34 46 2 Q34 -12 20 -12 Q10 0 -4 -10 Q-22 -2 -46 4Z" fill="#6B3E26"></path>
<g fill="none" stroke="{NAVY}" stroke-width="4"><circle cx="-17" cy="12" r="14"></circle><circle cx="17" cy="12" r="14"></circle><path d="M-3 10 Q0 7 3 10"></path></g>
<ellipse cx="-17" cy="13" rx="5.5" ry="7" fill="{NAVY}"></ellipse><ellipse cx="17" cy="13" rx="5.5" ry="7" fill="{NAVY}"></ellipse>
<circle cx="-15" cy="10" r="2.2" fill="#FFFFFF"></circle><circle cx="19" cy="10" r="2.2" fill="#FFFFFF"></circle>
<ellipse cx="-31" cy="34" rx="8" ry="5" fill="#FD8CA7"></ellipse><ellipse cx="31" cy="34" rx="8" ry="5" fill="#FD8CA7"></ellipse>
<path d="M-13 30 Q0 31 13 30 Q11 48 0 48 Q-11 48 -13 30Z" fill="#B23A5A" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"></path>
<path d="M-6 42 Q0 36 6 42 Q3 47 0 47 Q-3 47 -6 42Z" fill="#FD8CA7"></path>
<path d="M-40 -30 Q-28 -46 -10 -50" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"></path>
'''


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


def _cover(tpl):
    tpl = _swap(tpl, '<g transform="translate(880 700)" class="ol">', '<g transform="translate(880 700)">' + MOON + '</g>')
    tpl = _swap(tpl, '<g transform="translate(1010 380) rotate(-18) scale(.95)" class="ol">',
                '<g transform="translate(1010 380) rotate(-18) scale(1.05)">' + ASTRONAUT + '</g>')
    tpl = _swap(tpl, '<g transform="translate(300 830) rotate(22) scale(1)" class="ol">',
                '<g transform="translate(300 812) rotate(22) scale(.98)"><g class="rk">' + rocket('flk', 'rkC') + '</g></g>')
    return tpl


def _countdown(tpl):
    tpl = _swap(tpl, '<g transform="translate(300 726) scale(1.45)" class="ol">',
                '<g transform="translate(300 726) scale(1.3)">' + rocket('flick', 'rkC') + '</g>')
    # Countdown planet and launch clamps get outlines; the numbers a navy edge.
    tpl = tpl.replace('<circle cx="880" cy="480" r="175" fill="#FF9F45"></circle>',
                      '<circle cx="880" cy="480" r="175" fill="#FF9F45" stroke="%s" stroke-width="8"></circle>' % NAVY)
    tpl = tpl.replace('<g fill="#FF6B6B">\n<g class="clL">', '<g fill="#FF6B6B" %s>\n<g class="clL">' % OUTLINE)
    tpl = tpl.replace('<g fill="#FFF7E8">\n<circle class="smoke"', '<g fill="#FFF8EC" %s>\n<circle class="smoke"' % OUTLINE)
    return tpl


PAGES = {'p01-cover': _cover, 'p07-countdown': _countdown}


def apply(tpl, page):
    tpl = _global(tpl)
    if page in PAGES:
        tpl = PAGES[page](tpl)
    return tpl
