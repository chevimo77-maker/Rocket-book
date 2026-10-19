#!/usr/bin/env python3
"""Unpack tools/source-book.html (the exported single-file bundle) into 14 plain,
standalone HTML pages plus shared assets.

Usage: python3 -I tools/build.py        (run from the repo root)

Why: the exported pages each carried their own gzipped copy of React, ReactDOM, the
runtime and the font, and rebuilt the whole document in JS on every load. Here the
shared files live once in assets/ (cached across pages) and each page is plain HTML.
"""
import base64, gzip, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restyle  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'source-book.html')
NAMES = ['p01-cover', 'p02-training', 'p03-suit-up', 'p04-rollout', 'p05-fuel', 'p06-board',
         'p07-countdown', 'p08-liftoff', 'p09-booster', 'p10-refuel', 'p11-journey',
         'p12-landing', 'p13-moonwalk', 'p14-home']
# Pages switched to the SeaBeans redesign (tools/restyle.py). `--preview` also writes
# preview-<page>.html for the redesigned pages that are not switched yet.
RESTYLED = set(NAMES)
PREVIEW = '--preview' in sys.argv
REACT_URL = 'https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js'
SHADE = (
    '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="a"></feColorMatrix>'
    '<feOffset in="a" dx="-9" dy="-7" result="o1"></feOffset>'
    '<feComposite in="a" in2="o1" operator="out" result="rimD"></feComposite>'
    '<feOffset in="a" dx="7" dy="7" result="o2"></feOffset>'
    '<feComposite in="a" in2="o2" operator="out" result="rimL"></feComposite>'
    '<feFlood flood-color="#24125E" flood-opacity=".14"></feFlood>'
    '<feComposite in2="rimD" operator="in" result="sh"></feComposite>'
    '<feFlood flood-color="#FFFFFF" flood-opacity=".15"></feFlood>'
    '<feComposite in2="rimL" operator="in" result="hl"></feComposite>'
    '<feMerge><feMergeNode in="SourceGraphic"></feMergeNode><feMergeNode in="hl"></feMergeNode><feMergeNode in="sh"></feMergeNode></feMerge>')
REACT_DOM_URL = 'https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js'


def tag(s, name):
    m = re.search(r'<script type="__bundler/%s">\s*(.*?)\s*</script>' % name, s, re.S)
    return json.loads(m.group(1))


def blob(entry):
    d = base64.b64decode(entry['data'])
    return gzip.decompress(d) if entry.get('compressed') else d


def main():
    outer = open(SRC, encoding='utf-8').read()
    order = tag(outer, 'page_order')
    pages = tag(outer, 'manifest')
    assert len(order) == 14, len(order)
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)

    shared = {}  # content-hash -> asset path, so identical files are written once
    out = {}
    for i, uuid in enumerate(order):
        page = blob(pages[uuid]).decode('utf-8')
        manifest = tag(page, 'manifest')
        ext = {e['uuid']: e['id'] for e in tag(page, 'ext_resources')}
        tpl = tag(page, 'template')
        title = re.search(r'<title>(.*?)</title>', tpl).group(1)

        # Replace asset uuids with shared files.
        for u, entry in manifest.items():
            data = blob(entry)
            if u in ext:
                path = 'assets/react.production.min.js' if ext[u] == REACT_URL else 'assets/react-dom.production.min.js'
            elif entry['mime'] == 'font/woff2':
                path = 'assets/baloo2-latin.woff2'
            else:
                path = 'assets/dc-runtime.js'
            key = (path, data)
            if path in shared and shared[path] != data:
                raise SystemExit('asset %s differs between pages' % path)
            shared[path] = data
            tpl = tpl.replace(u, path)

        # Links: sibling .dc.html files -> plain pages.
        tpl = tpl.replace('Main.dc.html', 'p01-cover.html')
        tpl = re.sub(r'(p\d\d-[a-z0-9-]+)\.dc\.html', r'\1.html', tpl)
        assert '.dc.html' not in tpl

        # Four full-screen feTurbulence overlays -> pre-rendered textures.
        def noise(m):
            # Normal blending only: mix-blend-mode forced a full-screen blend pass every frame.
            # The textures in assets/noise are pre-converted to look the same with normal blending.
            return '<div class="nz nz-%s" aria-hidden="true" style="opacity: %s"></div>' % (m.group(3), m.group(2))
        tpl, n = re.subn(
            r'<svg width="1194" height="834" aria-hidden="true" style="position: absolute; left: 0; top: 0; pointer-events: none; mix-blend-mode: ([\w-]+); opacity: ([\d.]+)"><filter id="(\w+)">.*?</svg>',
            noise, tpl, flags=re.S)
        assert n == 4, (NAMES[i], n)

        # The "shade" filter (rim light/shadow + noise grit) sits on characters that animate, so it
        # is re-run every frame. Its feTurbulence/feDisplacementMap steps made animations drop to
        # ~16 fps on slower devices; keep the rim shading, drop the per-frame noise and blur.
        tpl, n = re.subn(r'(<filter id="shade"[^>]*>).*?</filter>', lambda m: m.group(1) + SHADE + '</filter>', tpl, flags=re.S)
        assert n == 1, (NAMES[i], n)
        assert 'feTurbulence' not in tpl and 'feDisplacementMap' not in tpl, NAMES[i]

        tpl = tpl.replace('<link rel="preconnect" href="https://fonts.googleapis.com">\n', '')

        # Redesigned pages: restyled for real once approved; otherwise only as preview-<name>.html.
        if NAMES[i] in RESTYLED:
            out[NAMES[i]] = page_html(restyle.apply(tpl, NAMES[i]), i, title)
        else:
            out[NAMES[i]] = page_html(tpl, i, title)
            if PREVIEW and NAMES[i] in restyle.PAGES:
                out['preview-' + NAMES[i]] = page_html(restyle.apply(tpl, NAMES[i]), i, title, preview=True)

    for path, data in shared.items():
        with open(os.path.join(ROOT, path), 'wb') as f:
            f.write(data)
    for name, html in out.items():
        with open(os.path.join(ROOT, name + '.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        print('%-26s %6d bytes' % (name + '.html', len(html.encode('utf-8'))))
    print('assets:', {p: len(d) for p, d in shared.items()})


def page_html(tpl, i, title, preview=False):
    body = tpl[tpl.index('<body>') + len('<body>'):tpl.rindex('</body>')]
    if preview:
        # Preview pages link to each other so the two redesigned pages can be compared in a row.
        body = body.replace('href="p02-training.html"', 'href="preview-p07-countdown.html"')
        body = body.replace('href="p06-board.html"', 'href="preview-p01-cover.html"')
    prev = NAMES[i - 1] + '.html' if i > 0 else None
    nxt = NAMES[i + 1] + '.html' if i < 13 else None
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, viewport-fit=cover">',
        '<meta name="theme-color" content="#0b1030">',
        '<title>%s</title>' % title,
        '<link rel="stylesheet" href="assets/book.css">',
        '<link rel="preload" href="assets/baloo2-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="assets/react.production.min.js" as="script">',
        '<link rel="preload" href="assets/react-dom.production.min.js" as="script">',
        '<script>window.__resources=%s;</script>' % json.dumps({REACT_URL: 'assets/react.production.min.js', REACT_DOM_URL: 'assets/react-dom.production.min.js'}),
        '<script src="assets/dc-runtime.js"></script>',
    ]
    for p in (nxt, prev):
        if p:
            head.append('<link rel="prefetch" href="%s">' % p)
    html = ('<!DOCTYPE html>\n<html lang="es-CO"><head>\n' + '\n'.join(head) + '\n</head>\n<body>'
            + body + '\n<noscript>Esta página necesita JavaScript.</noscript>\n<script src="assets/book.js"></script>\n</body></html>\n')
    return html


if __name__ == '__main__':
    main()
