#!/usr/bin/env python3
"""tools/build_single.py -- bundle the deck into one self-contained HTML file per language.

Usage (Python 3.8+, standard library only):
    python3 tools/build_single.py              # dist/presentation-ko.html and dist/presentation-en.html
    python3 tools/build_single.py --lang en    # only the English file (ko | en | all)
    python3 tools/build_single.py --out DIR    # write somewhere else

Input: index.html (Korean) and index.en.html (English). The page keeps the same <head> and
the same order of classic scripts, so the single file behaves exactly like the folder:
  - every <link rel="stylesheet"> becomes a <style>; fonts referenced by url(...) become
    data: URIs (KaTeX keeps only its .woff2 entries, which every supported browser loads);
  - every <script src> becomes an inline <script> (same order, same globals);
  - Pretendard (about 2 MB) is embedded once, as base64 in a small loader that registers it
    with the FontFace API for each @font-face rule that pointed to it (the main family and
    the Hangul-only faces of the KaTeX families), instead of repeating it in four rules;
  - the licence table and texts of lib/ travel with the file in <script type="text/plain"
    id="deck-licenses">.
The output has no timestamps, so rebuilding unchanged sources gives the same bytes.
The presenter window (P) opens the same file with #presenter, so it works as before.
"""
import argparse
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PAGES = {'ko': 'index.html', 'en': 'index.en.html'}
OUT_NAMES = {'ko': 'presentation-ko.html', 'en': 'presentation-en.html'}
SHARED_FONT = 'PretendardVariable.woff2'
MIME = {'.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf',
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
        '.svg': 'image/svg+xml', '.webp': 'image/webp'}
FORMAT_RANK = {'.woff2': 0, '.woff': 1, '.otf': 2, '.ttf': 3}

LINK_RE = re.compile(r'<link\b[^>]*(?<![\w-])rel="stylesheet"[^>]*(?<![\w-])href="([^"]+)"[^>]*>\s*\n?', re.I)
SCRIPT_RE = re.compile(r'<script\b[^>]*(?<![\w-])src="([^"]+)"[^>]*>\s*</script>\s*\n?', re.I)
FONT_FACE_RE = re.compile(r'@font-face\s*\{[^}]*\}', re.I)
URL_RE = re.compile(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)(\s*format\(\s*[\'"]?([^\'")]+)[\'"]?\s*\))?', re.I)


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'rb') as f:
        return 'data:%s;base64,%s' % (MIME.get(ext, 'application/octet-stream'), base64.b64encode(f.read()).decode('ascii'))


def descriptor(block, name):
    m = re.search(r'(?:^|[;{\s])' + re.escape(name) + r'\s*:\s*([^;}]+)', block, re.I)
    return ' '.join(m.group(1).split()) if m else None


def inline_css(css_path, shared_faces):
    """Return the CSS with its fonts inlined; @font-face rules of the shared font are
    removed and their descriptors appended to shared_faces (in source order)."""
    css = read_text(css_path)
    base = os.path.dirname(css_path)

    def resolve(u):
        return os.path.normpath(os.path.join(base, u.split('?')[0].split('#')[0]))

    def face(m):
        block = m.group(0)
        urls = [(resolve(u.group(2)), u.group(4)) for u in URL_RE.finditer(block) if not u.group(2).startswith('data:')]
        if not urls:
            return block
        if any(os.path.basename(p) == SHARED_FONT for p, _ in urls):
            shared_faces.append({
                'family': descriptor(block, 'font-family').strip('"\''),
                'weight': descriptor(block, 'font-weight'),
                'style': descriptor(block, 'font-style'),
                'display': descriptor(block, 'font-display'),
                'unicodeRange': descriptor(block, 'unicode-range'),
            })
            return '/* (%s: registered by the font loader below) */' % descriptor(block, 'font-family')
        found = [(p, f) for p, f in urls if os.path.isfile(p)]
        if not found:
            sys.exit('missing font file for %s: %s' % (css_path, ', '.join(p for p, _ in urls)))
        path, fmt = sorted(found, key=lambda x: FORMAT_RANK.get(os.path.splitext(x[0])[1].lower(), 9))[0]
        fmt = fmt or os.path.splitext(path)[1].lstrip('.')
        src = 'src:url(%s) format("%s")' % (data_uri(path), fmt)
        return re.sub(r'src\s*:[^;}]+', lambda _: src, block, count=1)

    css = FONT_FACE_RE.sub(face, css)

    def other_url(m):   # images or other files referenced outside @font-face
        u = m.group(2)
        if u.startswith('data:') or re.match(r'^[a-z]+:', u, re.I):
            return m.group(0)
        p = resolve(u)
        return 'url(%s)' % data_uri(p) + (m.group(3) or '') if os.path.isfile(p) else m.group(0)

    return URL_RE.sub(other_url, css)


def script_safe(js):
    """Make a script body safe to sit inside <script>…</script>."""
    js = re.sub(r'</(script)', r'<\\/\1', js, flags=re.I)
    js = js.replace('<!--', '<\\!--')
    return re.sub(r'^\s*//# sourceMappingURL=.*$', '', js, flags=re.M)


def font_loader(shared_faces):
    font_path = os.path.join(ROOT, 'lib', 'fonts', SHARED_FONT)
    with open(font_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    faces = []
    for fc in shared_faces:
        desc = {k: fc[k] for k in ('weight', 'style', 'display', 'unicodeRange') if fc.get(k)}
        faces.append('{family:%s,desc:{%s}}' % (js_str(fc['family']), ','.join('%s:%s' % (k, js_str(v)) for k, v in desc.items())))
    return ('<script>\n'
            '/* Pretendard Variable 1.3.9 (SIL Open Font License 1.1, text in #deck-licenses), embedded once and\n'
            '   registered for every @font-face rule of the stylesheets that pointed to lib/fonts/%s */\n'
            '(function () {\n'
            '  var faces = [%s];\n'
            '  try {\n'
            '    var bin = atob(%s), buf = new Uint8Array(bin.length);\n'
            '    for (var i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);\n'
            '    faces.forEach(function (f) { var ff = new FontFace(f.family, buf, f.desc); document.fonts.add(ff); ff.load(); });\n'
            '  } catch (e) { (window.__deckErrors = window.__deckErrors || []).push({ type: \'font\', message: String(e && e.message || e) }); }\n'
            '})();\n'
            '</script>\n') % (SHARED_FONT, ', '.join(faces), "'" + b64 + "'")


def js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def licenses_block():
    parts = [read_text(os.path.join(ROOT, 'lib', 'LICENSES.md'))]
    lic_dir = os.path.join(ROOT, 'lib', 'licenses')
    for name in sorted(os.listdir(lic_dir)):
        parts.append('=' * 72 + '\n' + name + '\n' + '=' * 72 + '\n' + read_text(os.path.join(lic_dir, name)))
    return '<script type="text/plain" id="deck-licenses">\n' + script_safe('\n\n'.join(parts)) + '\n</script>\n'


def build(lang, out_dir):
    page = PAGES[lang]
    html = read_text(os.path.join(ROOT, page))
    shared_faces = []

    def link(m):
        href = m.group(1)
        css = inline_css(os.path.join(ROOT, href), shared_faces)
        return '<style data-src="%s">\n%s\n</style>\n' % (href, css.strip())

    def script(m):
        src = m.group(1)
        js = read_text(os.path.join(ROOT, src))
        return '<script data-src="%s">\n%s\n</script>\n' % (src, script_safe(js).strip())

    html = LINK_RE.sub(link, html)
    if shared_faces:   # right after the last stylesheet, before any script runs
        last = html.rfind('</style>\n') + len('</style>\n')
        html = html[:last] + font_loader(shared_faces) + html[last:]
    html = SCRIPT_RE.sub(script, html)
    if re.search(r'<(script|link)\b[^>]*(?<![\w-])(src|href)="(?!data:)[^"]+\.(js|css)"', html, re.I):
        sys.exit('%s: an external script or stylesheet was not inlined' % page)
    note = ('<!-- Single-file build of %s (made by tools/build_single.py; do not edit by hand:\n'
            '     edit the sources and run python3 tools/build_single.py). Libraries and fonts are\n'
            '     third-party; licences in <script id="deck-licenses"> at the end of this file. -->\n') % page
    html = re.sub(r'(<!doctype html>\s*\n)', lambda m: m.group(1) + note, html, count=1, flags=re.I)
    html = html.replace('</body>', licenses_block() + '</body>', 1)

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, OUT_NAMES[lang])
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('%-3s %s -> %s (%.1f MB)' % (lang, page, os.path.relpath(out, ROOT), os.path.getsize(out) / 1e6))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--lang', choices=['ko', 'en', 'all'], default='all')
    ap.add_argument('--out', default=os.path.join(ROOT, 'dist'))
    a = ap.parse_args()
    for lang in (['ko', 'en'] if a.lang == 'all' else [a.lang]):
        build(lang, os.path.abspath(a.out))


if __name__ == '__main__':
    main()
