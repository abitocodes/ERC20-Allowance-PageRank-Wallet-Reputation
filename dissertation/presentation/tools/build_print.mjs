#!/usr/bin/env node
/* tools/build_print.mjs — print edition of the Korean deck: a PDF with one page per build step
   (59 slides, 304 pages). Each page is landscape with the proportions of A4 (297 x 210 mm): the
   slide as it stands after that step, 16:9 at the full page width in a light print palette, and
   under it the speaker-note paragraph of that step (the paragraph the N panel marks with ▶), with
   the slide number, the step, the slide title and what comes next. Printed two pages per A4 sheet
   (portrait), the two pages fill the sheet; one page per sheet fills A4 landscape.

   Usage (from this folder, after `npm install`):
     node build_print.mjs                         # → ../dist/presentation-ko-print.pdf
     node build_print.mjs --only s04-pagerank     # some slides only (section, slide id or id prefix; comma-separated)
     node build_print.mjs --out /tmp/test.pdf     # another output file
     node build_print.mjs --dark                  # keep the screen colours (dark background)
     node build_print.mjs --quality 0.9           # JPEG quality of the slide images (default 0.85)
     node build_print.mjs --keep DIR              # keep the page images, entries.json and print.html in DIR
     node build_print.mjs --from DIR              # lay out the PDF again from a --keep DIR (no new screenshots)
   How it works:
     1. index.html in Chromium with reduced motion, so every step is shot in its settled end state
        (1920x1080, the same walk as shoot.mjs). Notes and titles are read from the slide definitions.
     2. Light palette: each pixel colour is mapped in OKLab. Neutral colours get their lightness turned
        round (the near-black background becomes white, light text becomes dark grey); coloured pixels
        are darkened only as far as a white page needs and keep their hue and chroma (ambers lean a
        little towards orange so they stay warm), so every colour keeps its meaning and legend.
     3. One HTML page per step, printed to PDF by Chromium (the notes stay real, searchable text).
        A long note is set a little smaller (down to 8.5 pt) so it always fits under its slide.
   Exits 1 if the deck reported any error. Browser: as shoot.mjs (CHROME_PATH, else
   /opt/pw-browsers/chromium-NNNN/chrome-linux/chrome); never runs `playwright install`. */
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');

function parseArgs(argv) {
  const a = { only: null, out: path.join(ROOT, 'dist', 'presentation-ko-print.pdf'), dark: false, quality: 0.85, keep: null, from: null, page: 'index.html', timeout: 12000 };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--only') a.only = argv[++i].split(',').map(s => s.trim()).filter(Boolean);
    else if (k === '--out') a.out = path.resolve(argv[++i]);
    else if (k === '--dark') a.dark = true;
    else if (k === '--quality') a.quality = Math.min(1, Math.max(0.3, parseFloat(argv[++i]) || 0.85));
    else if (k === '--keep') a.keep = path.resolve(argv[++i]);
    else if (k === '--from') a.from = path.resolve(argv[++i]);
    else if (k === '--page') a.page = argv[++i];
    else if (k === '--timeout') a.timeout = parseInt(argv[++i], 10) || 12000;
    else if (k === '-h' || k === '--help') { console.log(fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('*/')[0]); process.exit(0); }
    else { console.error('unknown argument ' + k); process.exit(2); }
  }
  return a;
}

function findChrome() {
  const cands = [];
  if (process.env.CHROME_PATH) cands.push(process.env.CHROME_PATH);
  cands.push('/opt/pw-browsers/chromium-1194/chrome-linux/chrome');
  try {
    for (const d of fs.readdirSync('/opt/pw-browsers')) {
      if (/^chromium-\d+$/.test(d)) cands.push(path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome'));
    }
  } catch { /* none */ }
  for (const c of cands) if (c && fs.existsSync(c)) return c;
  throw new Error('No Chromium found. Set CHROME_PATH to a chrome binary.');
}

/* ---------------------------------------------------------------- light palette (runs in the browser) */
function installMapper() {
  const NP = [[0, 1.0], [0.17, 1.0], [0.21, 0.965], [0.30, 0.885], [0.50, 0.68], [0.66, 0.50], [0.75, 0.40], [0.95, 0.17], [1.0, 0.12]];
  const lin = new Float64Array(256);
  for (let i = 0; i < 256; i++) { const c = i / 255; lin[i] = c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  const enc = c => { c = c < 0 ? 0 : c > 1 ? 1 : c; return c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055; };
  const neutral = L => { for (let i = 1; i < NP.length; i++) if (L <= NP[i][0]) { const [x0, y0] = NP[i - 1], [x1, y1] = NP[i]; return y0 + (y1 - y0) * (L - x0) / (x1 - x0); } return NP[NP.length - 1][1]; };
  const smooth = (e0, e1, x) => { const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t); };
  function labToLinear(L, a, b) {
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b, m_ = L - 0.1055613458 * a - 0.0638541728 * b, s_ = L - 0.0894841775 * a - 1.2914855480 * b;
    const l = l_ * l_ * l_, m = m_ * m_ * m_, s = s_ * s_ * s_;
    return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s];
  }
  function mapColor(r, g, b) {
    const R = lin[r], G = lin[g], B = lin[b];
    const l_ = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B);
    const m_ = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B);
    const s_ = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B);
    const L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_;
    const A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_;
    const Bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_;
    const C = Math.hypot(A, Bb), h = Math.atan2(Bb, A) * 180 / Math.PI;
    const w = smooth(0.025, 0.10, C);                       /* 0 = neutral, 1 = clearly coloured */
    const y = Math.exp(-Math.pow((h - 80) / 28, 2));         /* yellows and ambers */
    const accent = Math.min(0.97, Math.max(0.42, 0.97 - 0.52 * L)) + 0.10 * y;
    const L2 = (1 - w) * neutral(L) + w * accent;
    const hr = (h - 14 * y * w) * Math.PI / 180;
    let k = 1, rgb = labToLinear(L2, C * Math.cos(hr), C * Math.sin(hr));
    for (let i = 0; i < 12 && rgb.some(v => v < -1e-4 || v > 1 + 1e-4); i++) { k *= 0.9; rgb = labToLinear(L2, k * C * Math.cos(hr), k * C * Math.sin(hr)); }
    return (Math.round(enc(rgb[0]) * 255) << 16) | (Math.round(enc(rgb[1]) * 255) << 8) | Math.round(enc(rgb[2]) * 255);
  }
  window.toPrint = async function (pngBase64, quality, dark) {
    const img = new Image();
    img.src = 'data:image/png;base64,' + pngBase64;
    await img.decode();
    const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
    const g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0);
    if (!dark) {
      const d = g.getImageData(0, 0, c.width, c.height), px = d.data, cache = new Map();
      for (let i = 0; i < px.length; i += 4) {
        const key = (px[i] << 16) | (px[i + 1] << 8) | px[i + 2];
        let v = cache.get(key);
        if (v === undefined) { v = mapColor(px[i], px[i + 1], px[i + 2]); cache.set(key, v); }
        px[i] = v >> 16; px[i + 1] = (v >> 8) & 255; px[i + 2] = v & 255;
      }
      g.putImageData(d, 0, 0);
    }
    const url = c.toDataURL('image/jpeg', quality);
    return url.slice(url.indexOf(',') + 1);
  };
}

/* ---------------------------------------------------------------- print page */
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function noteHTML(p) {
  const m = /^\(([^()]{1,40})\)\s*/.exec(p || '');   /* a leading stage cue such as "(지갑 창)" */
  return m ? '<span class="cue">(' + esc(m[1]) + ')</span> ' + esc(p.slice(m[0].length)) : esc(p || '(노트 없음)');
}
function pageHTML(e, total) {
  const next = e.step < e.steps ? '다음: <b>단계 ' + (e.step + 1) + ' / ' + e.steps + '</b>'
    : e.nextTitle ? '다음 장: <b>' + esc(e.nextTitle) + '</b>' : '마지막 장이에요';
  return '<section class="page">' +
    '<img class="shot" src="' + esc(e.img) + '" alt="">' +
    '<div class="band">' +
    '<div class="meta"><span><b>' + (e.index + 1) + ' / ' + e.slideCount + '</b> · ' + esc(e.id) +
    (e.steps ? ' · 단계 ' + e.step + ' / ' + e.steps : '') + ' · ' + esc(e.secNum) + ' ' + esc(e.secTitle) + ' · <b>' + esc(e.title || e.id) + '</b>' +
    (e.step === 0 && e.time ? ' · 이 장 ' + e.time + '초' : '') + '</span>' +
    '<span class="right">' + next + ' · ' + e.page + ' / ' + total + '</span></div>' +
    '<p class="notes">' + noteHTML(e.note) + '</p>' +
    '</div></section>';
}
function documentHTML(entries, fontURL) {
  return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>발표 자료 인쇄판</title><style>' +
    '@font-face{font-family:"Pretendard Variable";src:url("' + fontURL + '") format("woff2");font-weight:45 920;font-style:normal}' +
    '@page{size:297mm 210mm;margin:0}' +
    '*{box-sizing:border-box}' +
    'html,body{margin:0;padding:0;background:#fff}' +
    'body{font-family:"Pretendard Variable","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;color:#161a22;-webkit-print-color-adjust:exact;print-color-adjust:exact}' +
    '.page{width:297mm;height:210mm;padding:5mm 6mm 4.5mm;display:flex;flex-direction:column;overflow:hidden;break-after:page}' +
    '.page:last-child{break-after:auto}' +
    '.shot{display:block;flex:none;width:100%;aspect-ratio:16/9;border:.25mm solid #d5d9e1;border-radius:1mm}' +
    '.band{flex:1;min-height:0;display:flex;flex-direction:column;padding-top:2.4mm}' +
    '.meta{flex:none;display:flex;justify-content:space-between;gap:6mm;font-size:8pt;line-height:1.3;color:#6b7280;white-space:nowrap}' +
    '.meta span:first-child{overflow:hidden;text-overflow:ellipsis}' +
    '.meta b{color:#161a22;font-weight:600}' +
    '.notes{flex:1;min-height:0;overflow:hidden;margin:1.3mm 0 0;font-size:11pt;line-height:1.55;word-break:keep-all;overflow-wrap:break-word}' +
    '.cue{color:#6b7280;font-weight:600}' +
    '</style></head><body>' + entries.map(e => pageHTML(e, entries.length)).join('') + '</body></html>';
}
/* in the print page: set a note smaller, a quarter point at a time, until it fits under its slide */
function fitNotes() {
  let shrunk = 0, over = 0;
  document.querySelectorAll('.notes').forEach(n => {
    let pt = 11;
    while (n.scrollHeight > n.clientHeight + 1 && pt > 8.5) { pt -= 0.25; n.style.fontSize = pt + 'pt'; }
    if (pt < 11) shrunk++;
    if (n.scrollHeight > n.clientHeight + 1) over++;
  });
  return { shrunk, over };
}

/* ---------------------------------------------------------------- run */
const args = parseArgs(process.argv.slice(2));
const exe = findChrome();
const work = args.from || args.keep || fs.mkdtempSync(path.join(os.tmpdir(), 'deck-print-'));
fs.mkdirSync(path.join(work, 'img'), { recursive: true });
fs.mkdirSync(path.dirname(args.out), { recursive: true });

const browser = await chromium.launch({
  executablePath: exe,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl', '--font-render-hinting=none']
});
const problems = [];
const t0 = Date.now();
let entries, deckErrors = 0;

if (args.from) {
  /* lay out again what an earlier --keep run shot */
  entries = JSON.parse(fs.readFileSync(path.join(args.from, 'entries.json'), 'utf8'));
  const missing = entries.filter(e => !fs.existsSync(path.join(args.from, e.img)));
  if (missing.length) { console.error(`${missing.length} images missing in ${args.from}, e.g. ${missing[0].img}`); process.exit(2); }
  console.log(`from    ${args.from} (${entries.length} pages)`);
} else {
  const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, reducedMotion: 'reduce' })).newPage();
  page.on('pageerror', e => problems.push('page error: ' + String(e && e.message || e)));
  page.on('console', m => {
    if (m.type() !== 'error') return;
    const t = m.text();
    if (/build\/three(\.min)?\.js.*deprecated|GPU stall due to ReadPixels|Automatic fallback to software WebGL/i.test(t)) return;
    problems.push('console: ' + t);
  });
  /* read every slide definition as the sections register (titles, notes, planned time) */
  await page.addInitScript(() => {
    let D; window.__defs = [];
    Object.defineProperty(window, 'Deck', {
      configurable: true, get() { return D; },
      set(v) { D = v; const orig = v.section; v.section = function (def) { window.__defs.push(def); return orig.apply(this, arguments); }; }
    });
  });
  const deckURL = pathToFileURL(path.join(ROOT, args.page)).href;
  console.log(`chrome  ${exe}`);
  console.log(`open    ${deckURL}  (1920x1080, reduced motion${args.dark ? ', screen colours' : ', light print palette'})`);
  await page.goto(deckURL, { waitUntil: 'load' });
  await page.waitForFunction(() => window.Deck && window.Deck.current && window.Deck.current(), null, { timeout: 30000 });
  await page.evaluate(() => document.fonts.ready);
  const meta = await page.evaluate(() => {
    const list = window.Deck.list();
    const sections = window.__defs.map(s => ({ id: s.id, title: s.title, num: s.id.slice(1, 3) }));
    const slides = [];
    window.__defs.forEach(sec => sec.slides.forEach(s => {
      const L = list.find(x => x.id === s.id);
      slides.push({ id: s.id, index: L.index, steps: L.steps, title: s.title || '', time: s.time || 0, section: sec.id,
        notes: Array.isArray(s.notes) ? s.notes.slice() : [s.notes || ''] });
    }));
    return { sections, slides: slides.sort((a, b) => a.index - b.index) };
  });

  const worker = await (await browser.newContext()).newPage();
  await worker.setContent('<!doctype html><html><body></body></html>');
  await worker.evaluate(installMapper);

  const waitIdle = async label => {
    try { await page.waitForFunction(() => window.Deck.idle(), null, { timeout: args.timeout, polling: 100 }); }
    catch { console.log(`  ! ${label}: still animating after ${args.timeout} ms (shot taken anyway)`); }
    await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    await page.waitForTimeout(120);
  };

  const pick = meta.slides.filter(s => !args.only || args.only.some(o => s.section === o || s.id === o || s.id.startsWith(o)));
  if (!pick.length) { console.error('nothing matches --only ' + args.only); process.exit(2); }
  const secOf = id => meta.sections.find(s => s.id === id) || { title: '', num: '' };
  entries = [];
  for (const s of pick) {
    const sec = secOf(s.section), next = meta.slides[s.index + 1];
    for (let k = 0; k <= s.steps; k++) {
      await page.evaluate(([i, st]) => window.Deck.goto(i, st), [s.index, k]);
      await waitIdle(`${s.id}/${k}`);
      const png = await page.screenshot({ type: 'png' });
      const jpg = await worker.evaluate(([b64, q, dark]) => window.toPrint(b64, q, dark), [png.toString('base64'), args.quality, args.dark]);
      const file = `${s.id}-${k}.jpg`;
      fs.writeFileSync(path.join(work, 'img', file), Buffer.from(jpg, 'base64'));
      entries.push({ id: s.id, index: s.index, slideCount: meta.slides.length, step: k, steps: s.steps, title: s.title, time: s.time,
        secNum: sec.num, secTitle: sec.title, note: s.notes[k] != null ? s.notes[k] : s.notes[s.notes.length - 1],
        nextTitle: next ? (next.title || next.id) : null, img: 'img/' + file });
    }
    process.stdout.write(`  ${s.id} (${s.steps + 1})\n`);
  }
  entries.forEach((e, i) => { e.page = i + 1; });
  deckErrors = await page.evaluate(() => (window.__deckErrors || []).length);
  if (args.keep) fs.writeFileSync(path.join(work, 'entries.json'), JSON.stringify(entries, null, 1), 'utf8');
}

const fontURL = pathToFileURL(path.join(ROOT, 'lib', 'fonts', 'PretendardVariable.woff2')).href;
fs.writeFileSync(path.join(work, 'print.html'), documentHTML(entries, fontURL), 'utf8');
const printer = await (await browser.newContext()).newPage();
await printer.goto(pathToFileURL(path.join(work, 'print.html')).href, { waitUntil: 'load' });
await printer.evaluate(() => document.fonts.ready);
const fit = await printer.evaluate(fitNotes);
await printer.pdf({ path: args.out, preferCSSPageSize: true, printBackground: true });
await browser.close();
if (!args.keep && !args.from) fs.rmSync(work, { recursive: true, force: true });

const mb = (fs.statSync(args.out).size / 1e6).toFixed(1);
console.log(`\n${entries.length} pages -> ${path.relative(process.cwd(), args.out)} (${mb} MB, ${((Date.now() - t0) / 1000).toFixed(1)} s)`);
if (args.keep) console.log(`images, entries.json and print.html kept in ${work}`);
console.log(`notes set smaller to fit: ${fit.shrunk} · notes still overflowing: ${fit.over}`);
console.log(`window.__deckErrors: ${deckErrors}`);
problems.forEach(p => console.log('  ' + p));
console.log(`errors: ${problems.length}`);
process.exit(problems.length || deckErrors || fit.over ? 1 : 0);
