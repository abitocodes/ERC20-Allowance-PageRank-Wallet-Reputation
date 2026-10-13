#!/usr/bin/env node
/* video/extract.mjs — what the narration writers need, one entry per build step (304 per language):
   slide id, step, titles, the speaker note of that step, the visible elements of the settled step with
   their boxes in stage coordinates (1920x1080; the "anchors" that the narration points the camera at),
   and two reference images (clean, and with the anchors outlined and numbered).

   Usage (from video/, after `npm install` in ../tools):
     node extract.mjs --lang ko --out DIR          # index.html
     node extract.mjs --lang en --out DIR          # index.en.html
     node extract.mjs --lang ko --out DIR --only s04-pagerank
   Writes DIR/steps.json and DIR/img/<slide>-<step>.jpg, DIR/img/<slide>-<step>-a.jpg (1280x720). */
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const require = createRequire(path.join(ROOT, 'tools', 'package.json'));
const { chromium } = require('playwright-core');

const args = { lang: 'ko', out: null, only: null };
for (let i = 2; i < process.argv.length; i++) {
  const k = process.argv[i];
  if (k === '--lang') args.lang = process.argv[++i];
  else if (k === '--out') args.out = path.resolve(process.argv[++i]);
  else if (k === '--only') args.only = process.argv[++i].split(',');
  else { console.error('unknown argument ' + k); process.exit(2); }
}
if (!args.out) { console.error('--out DIR is required'); process.exit(2); }
fs.mkdirSync(path.join(args.out, 'img'), { recursive: true });

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  for (const d of fs.readdirSync('/opt/pw-browsers')) if (/^chromium-\d+$/.test(d)) {
    const p = path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome');
    if (fs.existsSync(p)) return p;
  }
  throw new Error('no chromium');
}

/* runs in the page: visible elements of the current slide, in stage coordinates */
function collectAnchors() {
  const cur = Deck.current();
  const slides = document.querySelectorAll('#deck-slides .slide[data-id="' + cur.id + '"]');
  const root = slides[slides.length - 1];
  const stage = document.getElementById('deck-stage').getBoundingClientRect();
  const s = Deck.scale || 1;
  const box = el => { const r = el.getBoundingClientRect(); return [(r.left - stage.left) / s, (r.top - stage.top) / s, r.width / s, r.height / s]; };
  /* text: the box of the glyphs, not of the (often full-width) block */
  const tbox = el => { const rg = document.createRange(); rg.selectNodeContents(el); const r = rg.getBoundingClientRect();
    return r.width > 0 ? [(r.left - stage.left) / s, (r.top - stage.top) / s, r.width / s, r.height / s] : box(el); };
  const opacity = el => { let o = 1; for (let e = el; e && e !== root.parentNode; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= parseFloat(cs.opacity); } return o; };
  const ownText = el => Array.from(el.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join('').replace(/\s+/g, ' ').trim();
  const out = [];
  const seen = new Set();
  const push = (el, kind, text) => {
    if (seen.has(el)) return;
    const b = kind === 'text' ? tbox(el) : box(el);
    if (b[2] < 6 || b[3] < 6 || b[0] > 1920 || b[1] > 1080 || b[0] + b[2] < 0 || b[1] + b[3] < 0) return;
    if (opacity(el) < 0.08) return;
    seen.add(el);
    out.push({ kind, box: b.map(v => Math.round(v)), text: (text || '').slice(0, 90) });
  };
  root.querySelectorAll('*').forEach(el => {
    if (el.closest('.katex') && !el.classList.contains('katex')) return;
    const tag = el.tagName.toLowerCase();
    if (el.classList.contains('katex')) {
      const ann = el.querySelector('annotation');
      push(el, 'formula', ann ? ann.textContent : el.textContent);
      return;
    }
    if (tag === 'canvas') { push(el, '3d', ''); return; }
    if (tag === 'img') { push(el, 'image', el.alt || ''); return; }
    if (tag === 'text' || (el.namespaceURI !== 'http://www.w3.org/2000/svg' && ownText(el))) {
      const t = tag === 'text' ? el.textContent.replace(/\s+/g, ' ').trim() : el.textContent.replace(/\s+/g, ' ').trim();
      if (t) { push(el, 'text', t); return; }
    }
    if (tag === 'svg') { const b = box(el); if (b[2] > 120 && b[3] > 80) push(el, 'figure', ''); return; }
    if (el.namespaceURI !== 'http://www.w3.org/2000/svg') {
      const cs = getComputedStyle(el), b = box(el);
      const filled = (cs.backgroundColor && !/rgba\(0, 0, 0, 0\)|transparent/.test(cs.backgroundColor)) || parseFloat(cs.borderTopWidth) > 0;
      if (filled && b[2] >= 80 && b[3] >= 50) push(el, 'box', el.textContent.replace(/\s+/g, ' ').trim());
    }
  });
  /* reading order, then ids */
  out.sort((a, b) => (Math.round(a.box[1] / 24) - Math.round(b.box[1] / 24)) || (a.box[0] - b.box[0]));
  out.forEach((a, i) => { a.id = 'a' + (i + 1); });
  return out;
}

function drawAnchors(list) {
  const stage = document.getElementById('deck-stage');
  const layer = document.createElement('div');
  layer.id = '__anchors';
  layer.style.cssText = 'position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;z-index:99999';
  list.forEach(a => {
    const d = document.createElement('div');
    const [x, y, w, h] = a.box;
    const col = a.kind === 'box' ? '#ff4fd8' : a.kind === 'formula' ? '#ffd23f' : a.kind === 'figure' || a.kind === '3d' ? '#3fe0ff' : '#7CFF6B';
    d.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;outline:2px solid ${col};outline-offset:1px`;
    const t = document.createElement('span');
    t.textContent = a.id;
    t.style.cssText = `position:absolute;left:-2px;top:-24px;font:700 18px/22px monospace;color:#000;background:${col};padding:0 4px;border-radius:3px`;
    d.appendChild(t);
    layer.appendChild(d);
  });
  stage.appendChild(layer);
}

const browser = await chromium.launch({ executablePath: findChrome()});
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, reducedMotion: 'reduce' });
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', e => errors.push(String(e && e.message || e)));
await page.addInitScript(() => {
  let D; window.__defs = [];
  Object.defineProperty(window, 'Deck', {
    configurable: true, get() { return D; },
    set(v) { D = v; const orig = v.section; v.section = function (def) { window.__defs.push(def); return orig.apply(this, arguments); }; }
  });
});
const pageFile = args.lang === 'en' ? 'index.en.html' : 'index.html';
await page.goto(pathToFileURL(path.join(ROOT, pageFile)).href, { waitUntil: 'load' });
await page.waitForFunction(() => window.Deck && window.Deck.current && window.Deck.current(), null, { timeout: 30000 });
await page.evaluate(() => document.fonts.ready);
const meta = await page.evaluate(() => {
  const list = window.Deck.list();
  const sections = window.__defs.map(s => ({ id: s.id, title: s.title }));
  const slides = [];
  window.__defs.forEach(sec => sec.slides.forEach(s => {
    const L = list.find(x => x.id === s.id);
    slides.push({ id: s.id, index: L.index, steps: L.steps, title: s.title || '', time: s.time || 0, section: sec.id,
      notes: Array.isArray(s.notes) ? s.notes.slice() : [s.notes || ''] });
  }));
  return { sections, slides: slides.sort((a, b) => a.index - b.index) };
});
const cdp = await ctx.newCDPSession(page);
const shot = async file => {
  const r = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 82, clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 2 / 3 } });
  fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
};
const steps = [];
const pick = meta.slides.filter(s => !args.only || args.only.some(o => s.section === o || s.id.startsWith(o)));
for (const s of pick) {
  for (let k = 0; k <= s.steps; k++) {
    await page.evaluate(([i, st]) => window.Deck.goto(i, st), [s.index, k]);
    try { await page.waitForFunction(() => window.Deck.idle(), null, { timeout: 12000, polling: 100 }); } catch { console.log(`  ! ${s.id}/${k} not idle`); }
    await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    await page.waitForTimeout(150);
    const anchors = await page.evaluate(collectAnchors);
    const base = `${s.id}-${k}`;
    await shot(path.join(args.out, 'img', base + '.jpg'));
    await page.evaluate(drawAnchors, anchors);
    await shot(path.join(args.out, 'img', base + '-a.jpg'));
    await page.evaluate(() => document.getElementById('__anchors').remove());
    const sec = meta.sections.find(x => x.id === s.section);
    steps.push({ slide: s.id, index: s.index, step: k, steps: s.steps, title: s.title, section: s.section, sectionTitle: sec ? sec.title : '',
      plannedSeconds: k === 0 ? s.time : undefined,
      note: s.notes[k] != null ? s.notes[k] : null, anchors, img: 'img/' + base + '.jpg', imgAnchors: 'img/' + base + '-a.jpg' });
  }
  process.stdout.write(`  ${s.id} (${s.steps + 1})\n`);
}
fs.writeFileSync(path.join(args.out, 'steps.json'), JSON.stringify({ lang: args.lang, sections: meta.sections, slides: meta.slides.map(({ notes, ...r }) => r), steps }, null, 1));
console.log(`${steps.length} steps, page errors: ${errors.length}${errors.length ? ' e.g. ' + errors[0] : ''}`);
await browser.close();
