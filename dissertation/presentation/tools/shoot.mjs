#!/usr/bin/env node
/* tools/shoot.mjs — walk every slide and build step of the deck and save PNGs.

   Usage (from this folder, after `npm install`):
     node shoot.mjs                        # index.html via file://, 1920x1080, every slide and step
     node shoot.mjs --only s04-pagerank    # one section (or a slide id / id prefix; comma-separated)
     node shoot.mjs --size 1280x720        # other stage size (PNGs go to shots/1280x720/)
     node shoot.mjs --http                 # serve the folder over http://127.0.0.1 instead of file://
     node shoot.mjs --reduced              # emulate prefers-reduced-motion: reduce
     node shoot.mjs --page tools/gallery.html   # another page (PNGs go to shots/<page-name>/)
     node shoot.mjs --first                # only step 0 of each slide
     node shoot.mjs --memcheck 3           # afterwards walk the deck back and forth 3 times, report heap
   Output: tools/shots/<slide>-<step>.png. Prints console errors, page errors and window.__deckErrors;
   exits 1 if any occurred.
   Browser: the preinstalled Chromium (CHROME_PATH, else /opt/pw-browsers/chromium-NNNN/chrome-linux/chrome);
   never runs `playwright install`. */
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');

function parseArgs(argv) {
  const a = { only: null, size: '1920x1080', http: false, reduced: false, page: 'index.html', first: false, memcheck: 0, timeout: 12000, out: null };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--only') a.only = argv[++i].split(',').map(s => s.trim()).filter(Boolean);
    else if (k === '--size') a.size = argv[++i];
    else if (k === '--http') a.http = true;
    else if (k === '--reduced') a.reduced = true;
    else if (k === '--page') a.page = argv[++i];
    else if (k === '--first') a.first = true;
    else if (k === '--memcheck') a.memcheck = parseInt(argv[++i], 10) || 2;
    else if (k === '--timeout') a.timeout = parseInt(argv[++i], 10) || 12000;
    else if (k === '--out') a.out = argv[++i];
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

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.png': 'image/png', '.svg': 'image/svg+xml', '.md': 'text/markdown; charset=utf-8' };
function serve(root) {
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      const f = path.normalize(path.join(root, u === '/' ? '/index.html' : u));
      if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end('not found'); return; }
      res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

const args = parseArgs(process.argv.slice(2));
const [W, H] = args.size.split('x').map(n => parseInt(n, 10));
const pageName = path.basename(args.page, '.html');
let outDir = args.out ? path.resolve(args.out) : path.join(HERE, 'shots');
if (pageName !== 'index') outDir = path.join(outDir, pageName);
if (args.size !== '1920x1080') outDir = path.join(outDir, args.size);
if (args.reduced) outDir = path.join(outDir, 'reduced');
fs.mkdirSync(outDir, { recursive: true });

const exe = findChrome();
let server = null, url;
if (args.http) {
  server = await serve(ROOT);
  url = `http://127.0.0.1:${server.address().port}/${args.page}`;
} else {
  url = pathToFileURL(path.join(ROOT, args.page)).href;
}

const browser = await chromium.launch({
  executablePath: exe,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl', '--font-render-hinting=none']
});
const context = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, reducedMotion: args.reduced ? 'reduce' : 'no-preference' });
const page = await context.newPage();
const consoleMsgs = [], pageErrors = [];
page.on('console', m => {
  const t = m.type();
  if (t === 'error' || t === 'warning') {
    const text = m.text();
    if (/build\/three(\.min)?\.js.*deprecated/i.test(text)) return; /* r158 classic build notice */
    if (/GPU stall due to ReadPixels|Automatic fallback to software WebGL/i.test(text)) return; /* headless SwiftShader noise */
    consoleMsgs.push(`[${t}] ${text}`);
  }
});
page.on('pageerror', e => pageErrors.push(String(e && e.stack || e)));
const badResponses = [];
page.on('response', r => { if (r.status() >= 400) badResponses.push(`${r.status()} ${r.url()}`); });
page.on('requestfailed', r => badResponses.push(`failed ${r.url()} ${r.failure() ? r.failure().errorText : ''}`));

console.log(`chrome  ${exe}`);
console.log(`open    ${url}  (${W}x${H}${args.reduced ? ', reduced motion' : ''})`);
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.Deck && window.Deck.current && window.Deck.current(), null, { timeout: 15000 });

const env = await page.evaluate(async () => {
  await document.fonts.ready;
  const gl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; } })();
  return {
    pretendard: document.fonts.check('700 64px "Pretendard Variable"', '가나다'),
    fontsLoaded: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v, i, a) => a.indexOf(v) === i),
    katex: !!window.katex, three: window.THREE ? window.THREE.REVISION : null, gsap: window.gsap ? window.gsap.version : null, d3: window.d3 ? window.d3.version : null,
    webgl: gl, slides: window.Deck.list().length, data: Object.keys(window.DECK_DATA || {})
  };
});
console.log('env    ', JSON.stringify(env));

async function waitIdle(label) {
  try {
    await page.waitForFunction(() => window.Deck.idle(), null, { timeout: args.timeout, polling: 100 });
  } catch {
    console.log(`  ! ${label}: still animating after ${args.timeout} ms (shot taken anyway)`);
  }
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.waitForTimeout(120);
}

const list = await page.evaluate(() => window.Deck.list());
const pick = list.filter(s => !args.only || args.only.some(o => s.section === o || s.id === o || s.id.startsWith(o)));
if (!pick.length) { console.error('nothing matches --only ' + args.only); process.exit(2); }

let shots = 0;
const t0 = Date.now();
for (const s of pick) {
  await page.evaluate(([i]) => window.Deck.goto(i, 0), [s.index]);
  await waitIdle(`${s.id}/0`);
  await page.screenshot({ path: path.join(outDir, `${s.id}-0.png`) }); shots++;
  if (args.first) continue;
  for (let k = 1; k <= s.steps; k++) {
    await page.evaluate(([i, st]) => window.Deck.goto(i, st), [s.index, k]);
    await waitIdle(`${s.id}/${k}`);
    await page.screenshot({ path: path.join(outDir, `${s.id}-${k}.png`) }); shots++;
  }
  process.stdout.write(`  ${s.id} (${s.steps + 1})\n`);
}

let mem = null;
if (args.memcheck) {
  const cdp = await context.newCDPSession(page);
  await cdp.send('Performance.enable');
  const metrics = async () => {
    await cdp.send('HeapProfiler.collectGarbage');
    const m = await cdp.send('Performance.getMetrics');
    const g = k => (m.metrics.find(x => x.name === k) || {}).value;
    return { heapMB: +(g('JSHeapUsedSize') / 1048576).toFixed(1), nodes: g('Nodes'), listeners: g('JSEventListeners') };
  };
  const rounds = [];
  await page.evaluate(() => window.Deck.goto(0, 0, { instant: true }));
  rounds.push(await metrics());
  for (let r = 0; r < args.memcheck; r++) {
    for (const s of list) {
      await page.evaluate(([i, st]) => { window.Deck.goto(i, st); window.Deck.settle(); }, [s.index, s.steps]);
    }
    const back = list.reduce((n, s) => n + s.steps + 1, 0) - 1;
    for (let i = 0; i < back; i++) {
      await page.evaluate(() => { window.Deck.prev(); window.Deck.settle(); });
    }
    await page.evaluate(() => window.Deck.goto(0, 0, { instant: true }));
    await page.waitForTimeout(300);
    rounds.push(await metrics());
  }
  mem = { rounds, debug: await page.evaluate(() => window.Deck._debug()) };
  console.log('memory ', JSON.stringify(mem));
}

const deckErrors = await page.evaluate(() => window.__deckErrors || []);
const debug = await page.evaluate(() => window.Deck._debug());
await browser.close();
if (server) server.close();

console.log(`\n${shots} screenshots -> ${path.relative(process.cwd(), outDir) || '.'}  (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
console.log('engine ', JSON.stringify(debug));
const report = (title, arr) => { console.log(`${title}: ${arr.length}`); arr.slice(0, 40).forEach(x => console.log('   ' + (typeof x === 'string' ? x : JSON.stringify(x)))); };
report('console errors/warnings', consoleMsgs);
report('page errors', pageErrors);
report('failed requests', badResponses);
report('window.__deckErrors', deckErrors);
process.exit(consoleMsgs.some(m => m.startsWith('[error]')) || pageErrors.length || deckErrors.length || badResponses.length ? 1 : 0);
