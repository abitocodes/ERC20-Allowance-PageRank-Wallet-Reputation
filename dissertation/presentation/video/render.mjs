#!/usr/bin/env node
/* video/render.mjs — render the narrated video, one chunk (H.264, no sound) per slide.
   The deck runs in Chromium on the virtual clock of vtime.js; every frame is the exact state at its time.
   Frames that cannot have changed (nothing animating, camera at rest) reuse the last capture.

   Usage (from video/, after `npm install` in ../tools):
     node render.mjs --plan PLAN.json --out DIR [--workers 3] [--only 0,1,38] [--crf 20] [--preset faster]
   PLAN.json (written by plan.py):
     { lang, fps, gap, meta: {...card texts...}, intro: [{id, dur}], outro: [{id, dur}],
       slides: [{ index, id, lastStep, chapter: [{id, dur}] | null,
                  steps: [{ step, avoid: [[x,y,w,h]...],
                            lines: [{ id, dur, boxes: [[x,y,w,h]...], zoom, mark, card: {title, body} | null }] }] }] }
     (avoid: the other text on screen at that step, which marks keep clear of)
   Writes DIR/chunk-NN.mp4 and DIR/chunk-NN.json ({ frames, lines: [{ id, frame, dur }] }) per slide.
   A chunk is skipped when its .json exists and --force is not given. */
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const require = createRequire(path.join(ROOT, 'tools', 'package.json'));
const { chromium } = require('playwright-core');

const A = { plan: null, out: null, workers: 3, only: null, crf: 20, preset: 'faster', force: false, quality: 92 };
for (let i = 2; i < process.argv.length; i++) {
  const k = process.argv[i];
  if (k === '--plan') A.plan = path.resolve(process.argv[++i]);
  else if (k === '--out') A.out = path.resolve(process.argv[++i]);
  else if (k === '--workers') A.workers = parseInt(process.argv[++i], 10);
  else if (k === '--only') A.only = process.argv[++i].split(',').map(Number);
  else if (k === '--crf') A.crf = parseInt(process.argv[++i], 10);
  else if (k === '--preset') A.preset = process.argv[++i];
  else if (k === '--quality') A.quality = parseInt(process.argv[++i], 10);
  else if (k === '--force') A.force = true;
  else { console.error('unknown argument ' + k); process.exit(2); }
}
const plan = JSON.parse(fs.readFileSync(A.plan, 'utf8'));
const FPS = plan.fps || 30, DT = 1000 / FPS;
const GAP = Math.round((plan.gap || 0.35) * FPS);
fs.mkdirSync(A.out, { recursive: true });
/* slides whose scene keeps moving although nothing is tweening (three.js orbit with autoRotate) */
const ALWAYS = new Set(['s03-06']);

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  for (const d of fs.readdirSync('/opt/pw-browsers')) if (/^chromium-\d+$/.test(d)) {
    const p = path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome');
    if (fs.existsSync(p)) return p;
  }
  throw new Error('no chromium');
}
const pad2 = n => String(n).padStart(2, '0');

async function openDeck(browser) {
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e && e.message || e)));
  page.on('console', m => { if (m.type() === 'error' && !/three|GPU stall|WebGL/i.test(m.text())) errors.push(m.text()); });
  await page.addInitScript({ path: path.join(HERE, 'vtime.js') });
  await page.goto(pathToFileURL(path.join(ROOT, plan.lang === 'en' ? 'index.en.html' : 'index.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  for (let i = 0; i < 600; i++) {
    const ok = await page.evaluate(dt => { __vt.advance(dt); return !!(window.Deck && Deck.current && Deck.current()); }, DT);
    if (ok) break;
  }
  await page.addScriptTag({ path: path.join(HERE, 'overlay.js') });
  const cdp = await ctx.newCDPSession(page);
  return { page, cdp, errors };
}

async function renderChunk(D, si) {
  const S = plan.slides[si];
  const base = path.join(A.out, 'chunk-' + pad2(si));
  if (!A.force && fs.existsSync(base + '.json')) return 'skipped';
  const { page, cdp } = D;
  const always = ALWAYS.has(S.id);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', A.preset, '-crf', String(A.crf), '-pix_fmt', 'yuv420p', '-r', String(FPS), '-g', String(FPS * 10),
    '-movflags', '+faststart', base + '.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  const ffDone = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  ffDone.catch(() => {});
  try {
  let frame = 0, last = null, wasDyn = true, force = 2;
  const log = [];
  const shot = async () => Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: A.quality, optimizeForSpeed: true })).data, 'base64');
  const write = buf => new Promise(res => { if (ff.stdin.write(buf)) res(); else ff.stdin.once('drain', res); });
  const ev = (fn, arg) => page.evaluate(fn, arg);
  async function F(n, until) {
    for (let i = 0; i < n; i++) {
      const r = await ev(([dt, al]) => { __vt.advance(dt); return { dyn: al || __vx.dynamic(), idle: Deck.idle() }; }, [DT, always]);
      if (r.dyn || wasDyn || force > 0 || !last) last = await shot();
      wasDyn = r.dyn; if (force > 0) force--;
      await write(last);
      frame++;
      if (until && until(r)) return r;
    }
    return null;
  }
  const act = async (fn, arg) => { await ev(fn, arg); force = 2; };
  const idle = () => ev(() => Deck.idle());

  /* start: the previous slide's last step, settled, so this slide's entrance plays as in the deck */
  await act(() => __vx.reset());
  if (si > 0) await act(([i, k]) => Deck.goto(i, k, { instant: true }), [si - 1, plan.slides[si - 1].lastStep]);
  else await act(() => Deck.goto(0, 0, { instant: true }));
  for (let i = 0; i < 40; i++) await ev(dt => __vt.advance(dt), DT);   /* settle, not recorded */
  last = null;

  if (si === 0 && plan.intro && plan.intro.length) {
    await act(m => __vx.intro(m), plan.meta.intro);
    await F(Math.round(1.6 * FPS));
    for (const L of plan.intro) { log.push({ id: L.id, frame, dur: L.dur }); await F(Math.ceil(L.dur * FPS) + GAP); }
    await F(Math.round(0.6 * FPS));
    await act(() => __vx.introOut(1.0));
    await F(Math.round(0.5 * FPS));
  }

  let curKey = '', curBoxes = null, hadCard = false;
  /* does the next line look at (nearly) the same place as the camera does now? */
  const near = (a, b) => {
    if (!a || !a.length || !b || !b.length) return false;
    const u = bs => bs.reduce((r, x) => [Math.min(r[0], x[0]), Math.min(r[1], x[1]), Math.max(r[2], x[0] + x[2]), Math.max(r[3], x[1] + x[3])], [1e9, 1e9, -1e9, -1e9]);
    const p = u(a), q = u(b);
    return Math.hypot((p[0] + p[2] - q[0] - q[2]) / 2, (p[1] + p[3] - q[1] - q[3]) / 2) < 320;
  };
  async function motion(L, next, avoid, end) {
    const key = L.boxes && L.boxes.length ? JSON.stringify([L.boxes, L.zoom, L.mark]) : '';
    if (L.card) {
      await act(c => { __vx.clearMarks(0.25); __vx.card(c.title, c.body, 0.7); }, L.card);
      hadCard = true; curKey = 'card'; curBoxes = null;
      /* the line's own mark goes on the shrunken slide too, once the card has settled */
      if (key && L.mark && L.mark !== 'none' && end - frame > 36) {
        await F(24);
        await act(([b, m, a]) => __vx.marks(b, m, a), [L.boxes, L.mark, avoid]);
      }
      return;
    }
    if (hadCard) {
      /* the card leaves; the shrunken slide comes back to full size unless the camera moves on anyway */
      await act(k => { __vx.cardOut(0.35); if (!k) __vx.camHome(0.7); }, key);
      hadCard = false; curKey = '';
      if (!key) return;
    }
    if (key === curKey) return;
    if (!key) {
      /* nothing to point at: drop the highlight and pull the camera back, except for a short aside
         between two close-ups of the same place, which would only pump the camera out and in again */
      if (curKey === '' || curKey === 'marks-only') return;
      const hold = L.dur < 4.0 && next && next.zoom && next.zoom !== 'none' && near(next.boxes, curBoxes);
      await act(h => { __vx.clearMarks(0.3); if (!h) __vx.camHome(0.7); }, hold);
      curKey = hold ? 'marks-only' : '';
      return;
    }
    curKey = key; curBoxes = L.boxes;
    await act(L => { __vx.clearMarks(0.25); __vx.camTo(L.boxes, L.zoom || 'none', 0.8); }, L);
    await F(9);
    await act(([b, m, a]) => __vx.marks(b, m, a), [L.boxes, L.mark || 'ring', avoid]);
  }

  for (const st of S.steps) {
    if (st.step > 0 || si > 0) await act(() => Deck.next());
    const click = frame;
    /* speech starts when the entrance settles, but not before 0.4 s nor after 1.5 s */
    await F(Math.round(1.5 * FPS), r => r.idle && frame - click >= Math.round(0.4 * FPS));
    const lines = (st.step === 0 && S.chapter ? S.chapter.map(l => Object.assign({ boxes: [], zoom: 'none', mark: 'none' }, l)) : []).concat(st.lines);
    for (const [li, L] of lines.entries()) {
      const start = frame, end = start + Math.ceil(L.dur * FPS);
      log.push({ id: L.id, frame: start, dur: L.dur });
      const wantsMotion = (L.boxes && L.boxes.length) || L.card || curKey;
      if (wantsMotion) {
        /* the deck may still be animating (long entrances): move the camera only once it is idle */
        if (!(await idle())) await F(Math.max(0, end - frame - 24), r => r.idle);
        if (frame < end - 12) await motion(L, lines[li + 1], st.avoid, end);
      }
      if (frame < end) await F(end - frame);
      await F(GAP);
    }
    await F(Math.round(0.4 * FPS));
    if (!(await idle())) await F(Math.round(6 * FPS), r => r.idle);
    if (curKey || hadCard || !(await ev(() => __vx.isHome()))) {
      await act(() => { __vx.clearMarks(0.3); __vx.cardOut(0.35); __vx.camHome(0.6); });
      curKey = ''; curBoxes = null; hadCard = false;
      await F(Math.round(0.7 * FPS));
    }
  }

  if (si === plan.slides.length - 1 && plan.outro && plan.outro.length) {
    await act(m => __vx.outro(m), plan.meta.outro);
    await F(Math.round(2.0 * FPS));
    for (const L of plan.outro) { log.push({ id: L.id, frame, dur: L.dur }); await F(Math.ceil(L.dur * FPS) + GAP); }
    await F(Math.round(2.5 * FPS));
    await act(() => __vx.fadeBlack(1.6));
    await F(Math.round(2.2 * FPS));
  }

  ff.stdin.end();
  await ffDone;
  fs.writeFileSync(base + '.json', JSON.stringify({ slide: S.id, frames: frame, fps: FPS, lines: log }));
  return frame;
  } catch (e) {
    /* a dead page: stop the encoder and drop its half-written file, so the chunk is rendered again */
    try { ff.stdin.destroy(); } catch { /* closed */ }
    ff.kill('SIGKILL');
    try { fs.unlinkSync(base + '.mp4'); } catch { /* none */ }
    throw e;
  }
}

let browser = await chromium.launch({ executablePath: findChrome() });
const queue = plan.slides.map((s, i) => i).filter(i => !A.only || A.only.includes(i));
const t0 = Date.now();
let failed = 0;
/* every chunk gets a fresh page (a long-lived page slowly fills up with dead slides and three.js
   renderers, and a crashed one would fail every later chunk); a failed chunk is tried twice more */
async function worker(w) {
  for (;;) {
    const si = queue.shift();
    if (si === undefined) break;
    for (let attempt = 1; attempt <= 3; attempt++) {
      const t = Date.now();
      let D = null;
      try {
        if (!browser.isConnected()) browser = await chromium.launch({ executablePath: findChrome() });
        D = await openDeck(browser);
        const r = await renderChunk(D, si);
        console.log(`[w${w}] chunk ${pad2(si)} ${plan.slides[si].id}: ${r === 'skipped' ? 'skipped' : r + ' frames (' + (r / FPS).toFixed(1) + ' s video) in ' + ((Date.now() - t) / 1000).toFixed(0) + ' s'}` +
          (D.errors.length ? `, page errors ${D.errors.length}: ${D.errors[0]}` : ''));
        await D.page.context().close().catch(() => {});
        break;
      } catch (e) {
        console.error(`[w${w}] chunk ${pad2(si)} attempt ${attempt} failed: ${e && e.message || e}`);
        if (D) await D.page.context().close().catch(() => {});
        if (attempt === 3) failed++;
      }
    }
  }
}
await Promise.all(Array.from({ length: Math.max(1, A.workers) }, (_, w) => worker(w)));
await browser.close();
console.log(`done in ${((Date.now() - t0) / 60000).toFixed(1)} min${failed ? ', ' + failed + ' failed' : ''}`);
process.exit(failed ? 1 : 0);
