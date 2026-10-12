/* =========================================================================
   s04-pagerank — Deriving PageRank, English edition (STORYBOARD.md §2, s04-01 … s04-07)

   One locked stage for the whole section: the four-node world of thesis
   Chapter 2 (Comp.smallWorld, G7) stays at the same place on all seven slides
   (data-shared="small-world"), and so does the background of the right-hand
   panel (data-shared="s04-panel", with the section counter "Step n / 7").
   Only the panel contents and the overlays change.

   s04-01  A small world                weights count up; o(u) — numbers fly from the arrows into the sums
   s04-02  The random walker            spinners next to A, B, C; P_{u,v} = w/o
   s04-03  A long walk: balance eq.     walker bursts into water; one pour; r_v = Σ r_u P_{u,v}
   s04-04  One table: transition matrix 4×4 table; arrows fly into cells; 3D flip about the diagonal = Pᵀ
   s04-05  Two problems                 leak at the dangling node (1 → 0.75 → 0.25 → 0); D ⇄ E trap
   s04-06  The fix: damping d, restarts three pieces of Eq. pagerank fill r^(1) = (0.0906, 0.2323, 0.1615, 0.5156)
   s04-07  Power iteration              23 iterations to ε = 1e-8; 69 / 92 on the real graphs; live d slider

   Numbers and sources
     weights 2, 1, 3, 1; o = 3, 3, 1, 0; d = 0.85; 0.0375 = 0.15/4; r^(1) = (0.0906, 0.2323, 0.1615, 0.5156);
     r = (0.1375, 0.2154, 0.1765, 0.4706); d·r_D/4 = 0.1000
       — thesis Ch. 2 "Worked example" (DECK_DATA.params.worked_example), status tag 'thesis-example'
     leak totals 1, 0.75, 0.25, 0; trap (D, E) values; fixed trap D 0.4619, E 0.4226; 23 iterations;
     change values 0.531, 0.135, …; slider values — computed here in the browser (power iteration
       of Eq. pagerank on the toy graph), status tags 'calc' / 'example'
     d = 0.85, ε = 1e-8, I_max = 300 — DECK_DATA.params.pagerank (R§10 Protocol)
     69 (EndorseRank), 92 (AWP) iterations at T_obs — DECK_DATA.scale.revised.iterations_tobs (R§1)
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt;
  var NS = 'http://www.w3.org/2000/svg';
  var DATA = window.DECK_DATA || {};
  var PRM = DATA.params || {};
  var PRP = PRM.pagerank || {};
  var DAMP = PRP.d != null ? PRP.d : 0.85;
  var TOL = PRP.tol != null ? PRP.tol : 1e-8;
  var IMAX = PRP.max_iter != null ? PRP.max_iter : 300;
  var ITS = (((DATA.scale || {}).revised || {}).iterations_tobs) || {};
  var IT_ER = ITS.endorserank != null ? ITS.endorserank : 69;
  var IT_AWP = ITS.awp != null ? ITS.awp : 92;

  /* ------------------------------------------------------------ geometry of the locked stage */
  var WX = 96, WY = 236;                       /* small-world wrapper (stage px) */
  var SW = Comp.SMALL_WORLD;
  var NODE = {}; SW.nodes.forEach(function (n) { NODE[n.id] = { x: n.x, y: n.y }; });
  var IDS = ['A', 'B', 'C', 'D'];
  var EDGES = SW.edges.map(function (e) { return [e.from, e.to, e.w]; });
  var CUP_DY = 92, CUP_H = 60, CUP_MAX = 0.8;
  var WATER = C.ink;
  var STEP_NAMES = ['Small world', 'Walker', 'Balance', 'Transition matrix', 'Two problems', 'The fix', 'Iteration'];

  /* ------------------------------------------------------------ math: power iteration on a toy graph */
  /* mode 'full' = Eq. pagerank with uniform restarts; mode 'plain' = r(t+1) = Pᵀ r(t) (no fix) */
  function iterate(ids, edges, o) {
    o = o || {};
    var n = ids.length, idx = {}, i, t;
    ids.forEach(function (k, j) { idx[k] = j; });
    var out = []; for (i = 0; i < n; i++) out.push(0);
    edges.forEach(function (e) { out[idx[e[0]]] += e[2]; });
    var d = o.d != null ? o.d : DAMP, r = [];
    for (i = 0; i < n; i++) r.push(1 / n);
    var hist = [r.slice()], deltas = [], max = o.steps || IMAX;
    for (t = 0; t < max; t++) {
      var nr = [], dang = 0;
      for (i = 0; i < n; i++) { nr.push(0); if (out[i] === 0) dang += r[i]; }
      if (o.mode === 'plain') {
        edges.forEach(function (e) { var a = idx[e[0]]; nr[idx[e[1]]] += r[a] * e[2] / out[a]; });
      } else {
        edges.forEach(function (e) { var a = idx[e[0]]; nr[idx[e[1]]] += d * r[a] * e[2] / out[a]; });
        for (i = 0; i < n; i++) nr[i] += (1 - d) / n + d * dang / n;
      }
      var dl = 0; for (i = 0; i < n; i++) dl += Math.abs(nr[i] - r[i]);
      deltas.push(dl); r = nr; hist.push(r.slice());
      if (o.mode !== 'plain' && dl < (o.tol || TOL)) break;
    }
    return { r: r, hist: hist, deltas: deltas, iters: deltas.length };
  }
  var PR = iterate(IDS, EDGES, { d: DAMP });                                   /* 23 iterations */
  var LEAK = iterate(IDS, EDGES, { mode: 'plain', steps: 3 });                  /* 1 → 0.75 → 0.25 → 0 */
  var TIDS = ['A', 'B', 'C', 'D', 'E'];
  var TEDGES = EDGES.concat([['D', 'E', 1], ['E', 'D', 1]]);
  var TRAP = iterate(TIDS, TEDGES, { mode: 'plain', steps: 6 });                /* (D,E) seesaw */
  var TRAPFIX = iterate(TIDS, TEDGES, { d: DAMP });                            /* D 0.4619, E 0.4226 */
  function sum(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return s; }
  function f4(v) { return fmt(v, 4); }

  /* ------------------------------------------------------------ section styles */
  var CSS = [
    '.s4-pbg{position:absolute;left:940px;top:196px;width:884px;height:794px;border-radius:24px;background:var(--bg-2)}',
    '.s4-ph{position:absolute;left:44px;right:44px;top:22px;height:28px;display:flex;align-items:center;gap:14px;font-family:var(--font-mono);font-size:17px;line-height:24px;color:var(--ink-3);letter-spacing:0}',
    '.s4-ph .nm{color:var(--ink-2);font-family:var(--font-sans);font-weight:600}',
    '.s4-ph .segs{display:flex;gap:6px;margin-left:auto}',
    '.s4-ph .segs i{display:block;position:relative;width:30px;height:4px;border-radius:2px;background:var(--line);overflow:hidden}',
    '.s4-ph .segs i.done{background:var(--ink-3)}',
    '.s4-ph .segs i b{position:absolute;inset:0;background:var(--ink);transform-origin:0 50%}',
    '.s4-pn{position:absolute;left:984px;top:262px;width:796px;height:716px}',
    '.s4-pn > * + *{margin-top:18px}',
    '.s4-k{font-family:var(--font-mono);font-size:17px;line-height:24px;color:var(--ink-3);letter-spacing:0}',
    '.s4-L{font-size:34px;line-height:48px;font-weight:600;color:var(--ink);letter-spacing:-.01em}',
    '.s4-l{font-size:28px;line-height:42px;color:var(--ink-2)}',
    '.s4-l b,.s4-L b{color:var(--ink);font-weight:700}',
    '.s4-note{font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s4-tx{font-size:30px;line-height:44px}',
    '.s4-tx .katex-display{margin:0;text-align:left}.s4-tx .katex-display>.katex{text-align:left}',
    '.s4-tx.c .katex-display{text-align:center}.s4-tx.c .katex-display>.katex{text-align:center}',
    '.s4-q{font-size:30px;line-height:44px;font-weight:700;color:var(--c-hi)}',
    '.s4-key{font-size:30px;line-height:44px;font-weight:700;color:var(--ink);padding-left:18px;border-left:4px solid var(--ink-2)}',
    '.s4-cast{display:flex;flex-direction:column;gap:12px}',
    '.s4-cast .row{display:flex;align-items:center;gap:18px;font-size:30px;line-height:44px}',
    '.s4-cast .row svg{flex:0 0 auto}',
    '.s4-cast .row b{width:84px;font-weight:700}',
    '.s4-cast .row span{color:var(--ink-2)}',
    '.s4-otab{display:grid;grid-template-columns:1fr 1fr;column-gap:30px;row-gap:12px;margin-top:8px}',
    '.s4-orow{display:flex;align-items:center;gap:12px;font-size:34px;line-height:52px;font-variant-numeric:tabular-nums;padding:6px 16px;border-radius:14px;background:var(--bg-3)}',
    '.s4-orow .ok .katex{font-size:1em}',
    '.s4-orow .os,.s4-orow .or{display:inline-block;min-width:26px;text-align:center;font-weight:700}',
    '.s4-orow .os{color:var(--c-allow)}',
    '.s4-orow .oo{color:var(--ink-3)}',
    '.s4-orow .or.zero{color:var(--c-hi);border:2px dashed var(--c-hi);border-radius:10px;padding:0 10px}',
    '.s4-fly{position:absolute;left:0;top:0;z-index:30;pointer-events:none;white-space:nowrap;font-size:30px;line-height:40px;font-weight:700;',
    '  color:var(--c-allow);padding:2px 10px;border-radius:10px;background:rgba(10,13,20,.88);border:1px solid rgba(245,180,60,.55);font-variant-numeric:tabular-nums}',
    '.s4-fly .katex{font-size:1em}',
    '.s4-bubble{position:absolute;width:76px;height:76px;margin:-38px 0 0 -38px;border-radius:38px;border:3px solid var(--c-hi);color:var(--c-hi);background:rgba(10,13,20,.85);',
    '  display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:800;line-height:1}',
    '.s4-gauge{position:absolute;width:40px}',
    '.s4-gauge .lb{position:absolute;left:50%;top:-68px;transform:translateX(-50%);white-space:nowrap;text-align:center;font-size:22px;line-height:28px;color:var(--ink-2)}',
    '.s4-gauge .fr{position:absolute;left:0;top:0;width:40px;border:2px solid var(--ink-3);border-radius:10px;overflow:hidden}',
    '.s4-gauge .fl{position:absolute;left:0;right:0;bottom:0;background:rgba(233,237,245,.55)}',
    '.s4-gauge .vl{position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;font-family:var(--font-mono);font-size:24px;line-height:32px;color:var(--ink);letter-spacing:0}',
    '.s4-chain{display:flex;align-items:center;gap:14px;font-size:30px;line-height:44px;font-variant-numeric:tabular-nums}',
    '.s4-chain .v{font-weight:700;padding:0 6px}',
    '.s4-chain .ar{color:var(--ink-3)}',
    '.s4-chain .v.zero{color:var(--c-hi)}',
    /* matrix (s04-04) */
    '.s4-mxw{position:absolute;perspective:1700px}',
    '.s4-flip{position:absolute;left:0;top:0;width:100%;height:100%;transform-style:preserve-3d;transform-origin:50% 50%}',
    '.s4-face{position:absolute;left:0;top:0;width:100%;height:100%;backface-visibility:hidden;-webkit-backface-visibility:hidden}',
    '.s4-face.back{transform:rotate3d(1,1,0,180deg)}',
    '.s4-cell{position:absolute;display:flex;align-items:center;justify-content:center;border:1px solid var(--line);font-size:30px;line-height:1;font-variant-numeric:tabular-nums;color:var(--ink)}',
    '.s4-cell .katex{font-size:1.05em}',
    '.s4-cell .bgf{position:absolute;inset:0;background:var(--c-allow);opacity:0}',
    '.s4-cell .val{position:relative}',
    '.s4-cell .val.z{color:var(--ink-3)}',
    '.s4-hcell{position:absolute;display:flex;align-items:center;justify-content:center;font-family:var(--font-mono);font-size:24px;color:var(--ink-2);letter-spacing:0}',
    '.s4-rowmark{position:absolute;border:2px dashed var(--c-hi);border-radius:6px;background:var(--c-hi-soft);pointer-events:none}',
    '.s4-vec{position:absolute}',
    '.s4-vec .vc{position:absolute;left:0;width:100%;display:flex;align-items:center;justify-content:center;border:1px solid var(--ink-3);font-size:30px;background:rgba(233,237,245,.04)}',
    '.s4-vec .vh{position:absolute;left:0;width:100%;top:0;height:44px;display:flex;align-items:center;justify-content:center;font-size:28px;color:var(--ink-2)}',
    '.s4-vec .vc.on{border-color:var(--c-hi);background:var(--c-hi-soft)}',
    '.s4-cap{position:absolute;font-size:24px;line-height:34px;color:var(--ink-2)}',
    '.s4-cap b{color:var(--ink);font-weight:700}',
    '.s4-pill{display:inline-flex;align-items:center;gap:8px;padding:4px 14px;border-radius:18px;border:2px dashed var(--c-hi);color:var(--c-hi);font-size:22px;line-height:30px;font-weight:600;background:rgba(10,13,20,.85)}',
    /* s04-06 */
    '.s4-rules{display:flex;flex-direction:column;gap:6px}',
    '.s4-rule{display:flex;align-items:baseline;gap:18px}',
    '.s4-rule .n{width:96px;text-align:right;font-size:60px;line-height:64px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.02em}',
    '.s4-rule .t{font-size:28px;line-height:40px;color:var(--ink-2)}',
    '.s4-rule .t b{color:var(--ink)}',
    '.s4-hero{position:relative;font-size:34px;line-height:48px}',
    '.s4-hero .katex-display{margin:0}',
    '.s4-plabels{position:relative;height:36px}',
    '.s4-plabels .pl{position:absolute;top:0;transform:translateX(-50%);white-space:nowrap;font-size:20px;line-height:28px;color:var(--ink-3)}',
    '.s4-plabels .pl i{font-style:normal;display:inline-block;width:26px;height:26px;border-radius:13px;border:1.5px solid currentColor;text-align:center;line-height:23px;font-size:16px;margin-right:6px;font-family:var(--font-mono)}',
    '.s4-plabels .pl.on{color:var(--ink)}',
    '.s4-slot{position:relative;min-height:330px}',
    '.s4-slot > div{position:absolute;left:0;top:0;width:100%}',
    '.s4-slot > div > * + *{margin-top:14px}',
    /* s04-07 */
    '.s4-iter{display:flex;align-items:baseline;gap:22px}',
    '.s4-iter .t{font-size:60px;line-height:64px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.02em}',
    '.s4-iter .k{font-size:24px;color:var(--ink-2)}',
    '.s4-iter .dl{margin-left:auto;font-family:var(--font-mono);font-size:22px;color:var(--ink-2);letter-spacing:0}',
    '.s4-real{display:flex;gap:40px;align-items:baseline}',
    '.s4-real .it{display:flex;flex-direction:column}',
    '.s4-real .it .n{font-size:72px;line-height:76px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.02em}',
    '.s4-real .it .k{font-size:24px;line-height:32px;color:var(--ink-2)}',
    '.s4-slider{position:absolute;left:96px;top:858px;width:760px;height:120px}',
    '.s4-slider .lb{font-size:24px;line-height:32px;color:var(--ink-2)}',
    '.s4-slider .lb b{color:var(--ink);font-family:var(--font-mono);letter-spacing:0;font-weight:700}',
    '.s4-slider svg{position:absolute;left:0;top:44px;overflow:visible;cursor:pointer;touch-action:none}',
    /* derivation panel inside the section panel: no second card */
    '.s4-pn .derive.eq-panel{padding:0;background:none;border-radius:0}',
    '.s4-pn .derive .eq-head{margin-bottom:6px}',
    '.s4-pn .derive .derive-line{padding:6px 0}',
    '.s4-pn .derive .katex{font-size:1.12em}',
    /* compact symbol card: symbol on the left, picture and meaning on the right */
    '.sym-card.s4-sc{display:grid;grid-template-columns:auto auto;column-gap:22px;row-gap:4px;align-items:center;max-width:560px;padding:14px 22px}',
    '.sym-card.s4-sc .sym{grid-row:1 / span 2;font-size:42px}',
    '.sym-card.s4-sc .sym-art,.sym-card.s4-sc .sym-desc{grid-column:2}',
    '.s4-circ{display:inline-block;width:34px;height:34px;border-radius:17px;border:2px solid currentColor;text-align:center;line-height:30px;font-size:20px;font-weight:700;font-family:var(--font-mono);margin-right:10px;vertical-align:middle}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s04-style')) return;
    var st = document.createElement('style'); st.id = 's04-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  /* ------------------------------------------------------------ small DOM helpers */
  function S(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function H(tag, cls, parent, html) {
    var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e;
  }
  function q(el, sel) { return el.querySelector(sel); }
  function qa(el, sel) { return Array.prototype.slice.call(el.querySelectorAll(sel)); }
  function tex(src) { return Deck.tex(src, false); }

  /* shared panel background with the section counter (stays put between the seven slides) */
  function panelBg(k) {
    var segs = '';
    for (var i = 1; i <= 7; i++) segs += '<i class="' + (i < k ? 'done' : '') + '">' + (i === k ? '<b></b>' : '') + '</i>';
    return '<div class="s4-pbg" data-shared="s04-panel"><div class="s4-ph"><span>Building PageRank · Step ' + k + ' / 7</span>' +
      '<span class="nm">' + STEP_NAMES[k - 1] + '</span><span class="segs">' + segs + '</span></div></div>';
  }
  function panelEnter(el, ctx, first) {
    var b = q(el, '.s4-pbg .segs b');
    if (b) ctx.gsap.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: E.io, delay: first ? 0.5 : 0.2 });
    if (first) ctx.gsap.fromTo(q(el, '.s4-pbg'), { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out });
  }

  /* the locked world */
  function makeWorld(ctx, el, o) {
    o = o || {};
    var W = Comp.smallWorld(ctx, el, { x: WX, y: WY, hidden: !!o.hidden,
      cups: { dy: CUP_DY, w: 50, h: CUP_H, max: CUP_MAX, decimals: 4, color: WATER } });
    W.cupG = IDS.map(function (id) { return W.cups[id].g; });
    W.cupL = IDS.map(function (id) { return W.cups[id].label; });
    if (o.cupAlpha != null) gsap.set(W.cupG, { autoAlpha: o.cupAlpha });
    if (o.cupLabels === false) gsap.set(W.cupL, { autoAlpha: 0 });
    if (o.cups) IDS.forEach(function (id, k) { W.cups[id].set(o.cups[k], { duration: 0 }); });
    if (o.dangling) dangling(W, true);
    return W;
  }
  function dangling(W, on) {
    var r = W.node('D').rect;
    r.setAttribute('stroke', on ? C.hi : C.ink2);
    if (on) r.setAttribute('stroke-dasharray', '6 5'); else r.removeAttribute('stroke-dasharray');
  }
  function setCups(W, vals, opt) {
    var tl = gsap.timeline();
    IDS.forEach(function (id, k) { if (vals[k] != null) tl.add(W.cups[id].set(vals[k], opt), 0); });
    return tl;
  }
  function stageOf(id) { return { x: WX + NODE[id].x, y: WY + NODE[id].y }; }
  function arrowWidth(A) { if (A.w0 == null) A.w0 = +A.strands[0].getAttribute('stroke-width') || 4; return A.w0; }
  function pulseArrow(A, delay) {
    var w = arrowWidth(A);
    return gsap.fromTo(A.strands, { attr: { 'stroke-width': w * 2.1 } }, { attr: { 'stroke-width': w }, duration: 0.9, ease: 'power2.out', delay: delay || 0 });
  }
  function pulseNode(N, delay) {
    return gsap.fromTo(N.g, { scale: 1.3, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.6, ease: 'power3.out', delay: delay || 0 });
  }
  /* an overlay SVG in world coordinates (spinners, fans, cloud) */
  function fxSvg(ctx, el) {
    var host = H('div', '', el); host.setAttribute('data-in', 'none');
    host.style.cssText = 'position:absolute;left:' + WX + 'px;top:' + WY + 'px;width:760px;height:560px;pointer-events:none';
    return Comp.svg(ctx, host, { w: 760, h: 560 });
  }

  /* particles (water) on a canvas in world coordinates */
  function Particles(ctx, el) {
    var OX = 60, OY = 110, streams = [];
    var host = H('div', '', el); host.setAttribute('data-in', 'none');
    host.style.cssText = 'position:absolute;left:0;top:0;pointer-events:none';
    var K = Comp.canvas(ctx, host, { w: 900, h: 840, x: WX - OX, y: WY - OY, onResize: function () { draw(); } });
    K.canvas.style.pointerEvents = 'none';
    function draw() {
      K.clear();
      if (!streams.length) return;
      var g = K.g; g.save(); g.translate(OX, OY);
      for (var s = 0; s < streams.length; s++) streams[s].paint(g);
      g.restore();
    }
    function emit(o) {
      var n = Math.round(o.n || 0);
      if (n <= 0 || ctx.instant || ctx.reduced) return gsap.to({}, { duration: 0.01, delay: o.delay || 0 });
      var rnd = Deck.util.rng(o.seed || 11), spread = o.spread != null ? o.spread : 0.45, life = 1 - spread, J = o.jitter != null ? o.jitter : 8;
      var offs = [], jit = [];
      for (var i = 0; i < n; i++) { offs.push(rnd() * spread); jit.push([(rnd() - 0.5) * J, (rnd() - 0.5) * J]); }
      var st = { p: 0 };
      st.paint = function (g) {
        g.fillStyle = o.color || WATER;
        for (var i2 = 0; i2 < n; i2++) {
          var t = (st.p - offs[i2]) / life; if (t <= 0 || t >= 1) continue;
          var e = t * t * (3 - 2 * t);
          var qq = o.path(e, i2);
          g.globalAlpha = (o.fade === false ? 1 : Math.min(1, Math.min(t, 1 - t) * 6)) * (o.alpha || 0.9);
          g.beginPath(); g.arc(qq[0] + jit[i2][0], qq[1] + jit[i2][1], o.r || 3, 0, 6.2832); g.fill();
        }
        g.globalAlpha = 1;
      };
      streams.push(st);
      return gsap.to(st, { p: 1, duration: o.duration || 1, delay: o.delay || 0, ease: 'none', onUpdate: draw,
        onComplete: function () { var k = streams.indexOf(st); if (k >= 0) streams.splice(k, 1); draw(); } });
    }
    return { K: K, emit: emit, draw: draw };
  }
  function seg(a, b) { return function (t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; }; }
  function chain(parts, ws) {
    var tot = sum(ws);
    return function (t) {
      var x = t * tot;
      for (var i = 0; i < parts.length; i++) { if (x <= ws[i] || i === parts.length - 1) return parts[i](Math.min(1, x / ws[i])); x -= ws[i]; }
      return parts[parts.length - 1](1);
    };
  }
  function cupMid(id, dy) { return [NODE[id].x, NODE[id].y + CUP_DY + (dy != null ? dy : 32)]; }
  /* water poured from the cup of `from`, along the arrow, into the cup of `to` */
  function pourPath(W, from, to, nodeOrigin) {
    var A = W.edge(from, to), p0 = A.pointAt(0), p1 = A.pointAt(1);
    var along = function (t) { var p = A.pointAt(t); return [p.x, p.y]; };
    var start = nodeOrigin ? [NODE[from].x, NODE[from].y] : cupMid(from);
    return chain([seg(start, [p0.x, p0.y]), along, seg([p1.x, p1.y], cupMid(to))], [nodeOrigin ? 0.08 : 0.22, 0.56, 0.22]);
  }
  function spillPath(id) { var a = cupMid(id, CUP_H + 2); return seg(a, [a[0], a[1] + 150]); }

  /* a chip that flies from one stage point to the centre of an element (results fly into place) */
  function flyer(ctx, el, html, from, toEl, o) {
    o = o || {};
    var f = H('div', 's4-fly' + (o.cls ? ' ' + o.cls : ''), el, html);
    var fr = ctx.rect(f), tr = ctx.rect(toEl);
    var x0 = from.x - fr.w / 2, y0 = from.y - fr.h / 2, x1 = tr.cx - fr.w / 2, y1 = tr.cy - fr.h / 2;
    gsap.set(f, { x: x0, y: y0, autoAlpha: 0 });
    var tl = gsap.timeline({ delay: o.delay || 0 });
    tl.to(f, { autoAlpha: 1, scale: 1.12, duration: 0.18, ease: 'power2.out' });
    tl.to(f, { x: x1, y: y1, scale: o.scale || 1, duration: o.duration || 0.75, ease: 'power3.inOut' });
    if (o.swap != null) tl.call(function () { f.innerHTML = o.swap; }, null, 0.18 + (o.duration || 0.75) * 0.55);
    if (o.reveal !== false) tl.set(toEl, { autoAlpha: 1 });
    tl.to(f, { autoAlpha: 0, duration: 0.18 });
    tl.call(function () { if (f.parentNode) f.parentNode.removeChild(f); });
    return tl;
  }

  /* compact symbol card at the bottom-left of the stage */
  function card(ctx, el, o) {
    o.className = 's4-sc'; if (o.y == null || o.y >= 836) o.y = 866;
    return Comp.symbolCard(ctx, el, o);
  }
  /* symbol-card art */
  function artArrow(label, kind) {
    var col = kind === 'p' ? C.ink2 : C.allow;
    return '<svg width="190" height="40" viewBox="0 0 190 40"><circle cx="16" cy="22" r="9" fill="none" stroke="' + C.ink3 + '" stroke-width="2.5"/>' +
      '<line x1="30" y1="22" x2="148" y2="22" stroke="' + col + '" stroke-width="4" stroke-linecap="round"/><path d="M160,22 L146,15 L146,29Z" fill="' + col + '"/>' +
      '<rect x="164" y="10" width="24" height="24" rx="6" fill="none" stroke="' + C.ink2 + '" stroke-width="2"/>' +
      '<text x="90" y="13" text-anchor="middle" fill="' + col + '" font-size="18" font-weight="700">' + label + '</text>' +
      '<text x="16" y="27" text-anchor="middle" fill="' + C.ink3 + '" font-size="12">u</text><text x="176" y="27" text-anchor="middle" fill="' + C.ink2 + '" font-size="12">v</text></svg>';
  }
  function artOut() {
    return '<svg width="222" height="60" viewBox="0 0 222 60"><circle cx="20" cy="30" r="9" fill="none" stroke="' + C.ink3 + '" stroke-width="2.5"/>' +
      '<path d="M32,26 L128,8" stroke="' + C.allow + '" stroke-width="5" stroke-linecap="round"/><path d="M32,34 L128,52" stroke="' + C.allow + '" stroke-width="3" stroke-linecap="round"/>' +
      '<text x="84" y="10" fill="' + C.allow + '" font-size="16" font-weight="700">2</text><text x="84" y="60" fill="' + C.allow + '" font-size="16" font-weight="700">1</text>' +
      '<text x="140" y="36" fill="' + C.ink + '" font-size="18" font-weight="700">2 + 1 = 3</text></svg>';
  }
  function artCups() {
    var s = '<svg width="200" height="54" viewBox="0 0 200 54">';
    [0.1375, 0.2154, 0.1765, 0.4706].forEach(function (v, i) {
      var x = 12 + i * 48, h = Math.round(v / 0.6 * 40);
      s += '<path d="M' + x + ',8 L' + (x + 4) + ',48 L' + (x + 28) + ',48 L' + (x + 32) + ',8" fill="none" stroke="' + C.ink2 + '" stroke-width="1.6"/>' +
        '<rect x="' + (x + 3) + '" y="' + (48 - h) + '" width="26" height="' + h + '" fill="' + C.ink + '" fill-opacity=".45"/>';
    });
    return s + '</svg>';
  }
  function artVec() {
    var s = '<svg width="50" height="58" viewBox="0 0 50 58">';
    ['A', 'B', 'C', 'D'].forEach(function (k, i) { s += '<rect x="4" y="' + (2 + i * 13.5) + '" width="40" height="13" fill="none" stroke="' + C.ink3 + '" stroke-width="1.2"/><text x="24" y="' + (12.5 + i * 13.5) + '" text-anchor="middle" fill="' + C.ink2 + '" font-size="10">r' + k + '</text>'; });
    return s + '</svg>';
  }
  function castIcon(kind) {
    if (kind === 'eoa') return '<svg width="44" height="44" viewBox="0 0 44 44"><circle cx="22" cy="22" r="13" fill="none" stroke="' + C.ink3 + '" stroke-width="2.5"/></svg>';
    return '<svg width="44" height="44" viewBox="0 0 44 44"><rect x="5" y="5" width="34" height="34" rx="8" fill="' + C.bg2 + '" stroke="' + C.ink2 + '" stroke-width="2"/>' +
      '<text x="22" y="27" text-anchor="middle" fill="' + C.ink2 + '" font-size="14" class="svg-mono">{ }</text></svg>';
  }

  /* spinner: slices [{n (equal parts), label, fill, ink}] + optional outer 85/15 ring */
  function spinner(svg, cx, cy, r, slices) {
    var g = S('g', { transform: 'translate(' + cx + ',' + cy + ')' }, svg);
    var disc = S('g', {}, g);
    var parts = []; slices.forEach(function (sl) { for (var k = 0; k < (sl.n || 1); k++) parts.push(sl); });
    var n = parts.length, mids = [];
    parts.forEach(function (sl, i) {
      var a0 = -Math.PI / 2 + i / n * Math.PI * 2, a1 = -Math.PI / 2 + (i + 1) / n * Math.PI * 2, am = (a0 + a1) / 2;
      mids.push(n === 1 ? 0 : (i + 0.5) / n * 360);
      if (n === 1) S('circle', { r: r, fill: sl.fill, stroke: C.bg, 'stroke-width': 2 }, disc);
      else S('path', { d: 'M0,0 L' + Math.cos(a0) * r + ',' + Math.sin(a0) * r + ' A' + r + ',' + r + ' 0 0 1 ' + Math.cos(a1) * r + ',' + Math.sin(a1) * r + 'Z',
        fill: sl.fill, stroke: C.bg, 'stroke-width': 2 }, disc);
      var tx = S('text', { x: n === 1 ? 0 : Math.cos(am) * r * 0.58, y: (n === 1 ? 0 : Math.sin(am) * r * 0.58) + 6, 'text-anchor': 'middle', fill: sl.ink || C.bg, 'font-size': Math.round(r * 0.48), 'font-weight': 800 }, disc);
      tx.textContent = sl.label;
    });
    S('circle', { r: r, fill: 'none', stroke: C.ink2, 'stroke-width': 1.5 }, g);
    var ptr = S('path', { d: 'M0,' + (-r + 6) + ' L-8,' + (-r - 10) + ' L8,' + (-r - 10) + 'Z', fill: C.ink }, g);
    var SP = { g: g, disc: disc, r: r, mids: mids, ptr: ptr, rot: 0 };
    SP.spin = function (slot, turns, o) {
      o = o || {};
      var target = -mids[slot] + 360 * (turns || 2);
      SP.rot = target;
      return gsap.fromTo(disc, { rotation: 0, svgOrigin: '0 0' }, { rotation: target, svgOrigin: '0 0', duration: o.duration || 1.4, ease: 'power3.out', delay: o.delay || 0 });
    };
    SP.ring = function (frac) { /* outer ring: frac follows the arrows (ink), 1 - frac teleports (rose) */
      var R = r + 9, rg = S('g', {}, g), segs = [];
      [[0, frac, C.ink2], [frac, 1, C.hi]].forEach(function (p) {
        if (p[1] - p[0] <= 0) return;
        var a0 = -Math.PI / 2 + p[0] * Math.PI * 2, a1 = -Math.PI / 2 + p[1] * Math.PI * 2, big = p[1] - p[0] > 0.5 ? 1 : 0;
        var d = (p[1] - p[0] >= 0.999) ? 'M0,' + (-R) + ' A' + R + ',' + R + ' 0 1 1 -0.01,' + (-R) :
          'M' + Math.cos(a0) * R + ',' + Math.sin(a0) * R + ' A' + R + ',' + R + ' 0 ' + big + ' 1 ' + Math.cos(a1) * R + ',' + Math.sin(a1) * R;
        segs.push(S('path', { d: d, fill: 'none', stroke: p[2], 'stroke-width': 7, 'stroke-linecap': 'butt' }, rg));
      });
      SP.ringSegs = segs;
      return segs;
    };
    return SP;
  }
  function drawSegs(segs, delay) {
    var tl = gsap.timeline({ delay: delay || 0 });
    segs.forEach(function (p, i) {
      var L = 1; try { L = p.getTotalLength(); } catch (e) { /* ignore */ }
      tl.fromTo(p, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.5, ease: 'power2.inOut' }, i * 0.45);
    });
    return tl;
  }

  /* vertical "Total water" gauge (HTML) */
  function gauge(ctx, el, o) {
    var wrap = H('div', 's4-gauge', el); wrap.setAttribute('data-in', 'none');
    wrap.style.left = o.x + 'px'; wrap.style.top = o.y + 'px'; wrap.style.height = o.h + 'px';
    H('div', 'lb', wrap, 'Total<br>water');
    var fr = H('div', 'fr', wrap); fr.style.height = o.h + 'px';
    var fl = H('div', 'fl', fr);
    var vl = H('div', 'vl', wrap); vl.style.top = (o.h + 10) + 'px';
    var G = { el: wrap, v: o.value != null ? o.value : 1 };
    fl.style.height = (G.v * o.h) + 'px'; vl.textContent = fmt(G.v, 2);
    G.set = function (v, opt) {
      opt = opt || {};
      var st = { v: G.v }; G.v = v;
      return gsap.to(st, { v: v, duration: opt.duration != null ? opt.duration : 0.6, delay: opt.delay || 0, ease: 'power2.inOut',
        onUpdate: function () { fl.style.height = (st.v * o.h) + 'px'; vl.textContent = fmt(st.v, 2); },
        onComplete: function () { fl.style.height = (v * o.h) + 'px'; vl.textContent = opt.text || fmt(v, 2); } });
    };
    return G;
  }

  /* ================================================================ s04-01 */
  function castRow(kind, k, txt) { return '<div class="row">' + castIcon(kind) + '<b>' + k + '</b><span>' + txt + '</span></div>'; }
  function orow(id, terms, res) {
    var h = '<div class="s4-orow" data-id="' + id + '"><span class="ok">$o(' + id + ')$</span><span class="oo">=</span>';
    terms.forEach(function (t, i) { if (i) h += '<span class="oo plus">+</span>'; h += '<span class="os" data-k="' + i + '">' + t + '</span>'; });
    if (terms.length > 1) h += '<span class="oo ores">=</span><span class="or">' + res + '</span>';
    if (!terms.length) h += '<span class="or zero">' + res + '</span>';
    return h + '</div>';
  }
  var s1 = {
    id: 's04-01', title: 'A small world', time: 40, steps: 2,
    notes: [
      'I will build PageRank from scratch in a very small world. There are four nodes. A is a token owner, that is, a person\'s wallet address (an EOA). B and C are vault contracts that A has approved, and D is a lending pool contract that both vaults approve in turn. This is the same as the worked example in Chapter 2 of the thesis.',
      'The number on each arrow is its weight. The bigger the weight, the thicker the arrow. I write the weight of the arrow from u to v as w(u, v). A to B is 2, A to C is 1, B to D is 3, and C to D is 1.',
      'I call the sum of all the weights leaving a node o. The sigma in the formula is the symbol for "add them all up". The small v underneath means we add while v runs over the nodes. So A is 2 plus 1, which is 3, B is 3, and C is 1. D has no outgoing arrow at all, so it is 0. This 0 is about to cause trouble.'
    ],
    html: '<h1 class="t-h1">We [[start]] with 4 nodes and 4 allowance edges</h1>' + panelBg(1) +
      '<div class="s4-pn">' +
        '<div class="s4-k">The cast</div>' +
        '<div class="s4-cast" data-in="rise" data-stagger="0.12">' + castRow('eoa', 'A', 'token owner (EOA)') + castRow('box', 'B, C', 'vault contracts') + castRow('box', 'D', 'lending pool contract') + '</div>' +
        '<div class="s4-l" data-step="1" style="margin-top:34px">Number on an arrow = its <b>weight</b> (thickness)</div>' +
        '<div class="s4-tx" data-step="1" style="font-size:28px">$w(A,B)=2,\\;\\; w(A,C)=1,\\;\\; w(B,D)=3,\\;\\; w(C,D)=1$</div>' +
        '<div id="og" data-in="none" style="margin-top:30px">' +
          '<div class="s4-tx" id="ofx"></div>' +
          '<div class="s4-note">Add the weights of all arrows leaving u · <b class="ink">Σ</b> (sigma) = add them all up</div>' +
          '<div class="s4-otab">' + orow('A', [2, 1], 3) + orow('B', [3]) + orow('C', [1]) + orow('D', [], 0) + '</div>' +
        '</div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { hidden: true, cupLabels: false });
      g.W.edges.forEach(function (A) { A.lbl = A.label; A.label = null; gsap.set(A.lbl, { autoAlpha: 0 }); });
      g.wCard = card(ctx, el, { tex: 'w(u,v)', desc: 'weight of the arrow u → v', art: artArrow('2'), x: 96, y: 840 });
      g.oCard = card(ctx, el, { tex: 'o(u)', desc: 'total weight leaving u', art: artOut(), x: 562, y: 840 });
      g.of = Comp.formula(ctx, q(el, '#ofx'), 'o(u)=\\part{s}{\\sum_{v}} w(u,v)', { display: false });
      /* Σ card inside the panel, under the o-table */
      g.sCard = Comp.symbolCard(ctx, el, { className: 's4-sc', tex: '\\sum_{v}', x: 984, y: 878,
        desc: 'sigma = <b class="ink">add them all up</b><br>v below: over every v · e.g. o(A) = 2 + 1 = 3' });
      g.og = q(el, '#og');
      gsap.set(g.og, { autoAlpha: 0 });
      gsap.set(qa(g.og, '.os, .or, .ores, .plus'), { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, W = g.W, tl = ctx.tl();
      panelEnter(el, ctx, true);
      IDS.forEach(function (id, i) { tl.add(W.node(id).pop(), 0.1 + i * 0.12); });
      W.edges.forEach(function (A, j) { tl.add(A.draw(), 0.7 + j * 0.14); });
      tl.to(W.cupG, { autoAlpha: 0.35, duration: 0.5, stagger: 0.06 }, 1.5);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, W = g.W, tl = ctx.tl();
      if (i === 1) {
        W.edges.forEach(function (A, k) {
          A.label = A.lbl;
          A.lbl.textContent = '0';
          tl.fromTo(A.lbl, { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: E.stamp }, k * 0.15);
          tl.add(ctx.count(A.lbl, 0, A.w, { decimals: 0, duration: 0.7 }), k * 0.15 + 0.05);
          tl.add(pulseArrow(A), k * 0.15);
        });
        tl.add(g.wCard.pop(), 1.0);
        tl.call(function () {
          ctx.add(function () {
            var cr = ctx.rect(g.wCard.el), lr = ctx.rect(W.edge('A', 'B').lbl);
            Comp.leader(ctx, [cr.x + 70, cr.y - 2], [lr.x - 4, lr.cy], { fromSide: 'top', toSide: 'left', color: 'ink2', bend: 0.45 }).draw();
          });
        }, null, 1.45);
      }
      if (i === 2) {
        var og = g.og;
        gsap.set(og, { autoAlpha: 1, y: 0 });                    /* measure the final boxes first */
        var rows = {}; qa(og, '.s4-orow').forEach(function (r) { rows[r.getAttribute('data-id')] = r; });
        var lbl = function (a, b) { return W.edge(a, b).lbl; };
        var from = function (n) { var r = ctx.rect(n); return { x: r.cx, y: r.cy }; };
        var sr = g.of.rect('s');                                  /* before the panel's rise offsets it */
        tl.fromTo(og, { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
        tl.add(g.sCard.pop(), 0.35);
        tl.add(flyer(ctx, el, '2', from(lbl('A', 'B')), q(rows.A, '.os[data-k="0"]')), 0.45);
        tl.add(flyer(ctx, el, '1', from(lbl('A', 'C')), q(rows.A, '.os[data-k="1"]')), 0.6);
        /* Σ leaves the formula and becomes the + between 2 and 1 */
        tl.call(function () { ctx.add(function () { g.of.mark('s', { pad: 4 }); }); }, null, 1.0);
        tl.add(flyer(ctx, el, 'Σ', { x: sr.cx, y: sr.cy }, q(rows.A, '.plus'), { swap: '+', duration: 0.9 }), 1.2);
        tl.call(function () { ctx.add(function () { g.of.unmark('s'); }); }, null, 2.4);
        tl.fromTo(qa(rows.A, '.ores, .or'), { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp, stagger: 0.1 }, 2.45);
        tl.add(pulseNode(W.node('A')), 2.45);
        tl.add(flyer(ctx, el, '3', from(lbl('B', 'D')), q(rows.B, '.os')), 2.8);
        tl.add(flyer(ctx, el, '1', from(lbl('C', 'D')), q(rows.C, '.os')), 3.1);
        var zero = q(rows.D, '.or');
        tl.fromTo(zero, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.12, repeat: 3, yoyo: true }, 4.1);
        tl.set(zero, { autoAlpha: 1 }, 4.6);
        tl.call(function () { dangling(W, true); }, null, 4.2);
        tl.add(pulseNode(W.node('D')), 4.2);
        tl.add(g.oCard.pop(), 4.7);
        tl.call(function () {
          ctx.add(function () {
            var cr = ctx.rect(g.oCard.el), fr = ctx.rect(q(og, '.s4-tx'));
            Comp.leader(ctx, [cr.x + cr.w + 4, cr.cy], [fr.x - 6, fr.cy], { fromSide: 'right', toSide: 'left', color: 'ink2', bend: 0.3 }).draw();
          });
        }, null, 5.1);
      }
    },
    tags: ['thesis-example']
  };

  /* ================================================================ s04-02 */
  var SPIN = {
    A: { x: 50, y: 150, r: 40, slices: [{ n: 2, label: 'B', fill: C.allow }, { n: 1, label: 'C', fill: 'rgba(245,180,60,.32)', ink: C.ink }] },
    B: { x: 470, y: 40, r: 30, slices: [{ n: 1, label: 'D', fill: C.allow }] },
    C: { x: 470, y: 455, r: 30, slices: [{ n: 1, label: 'D', fill: C.allow }] }
  };
  function makeSpinners(svg, ring) {
    var out = {};
    Object.keys(SPIN).forEach(function (id) {
      var s = SPIN[id];
      out[id] = spinner(svg, s.x, s.y, s.r, s.slices);
      if (ring) out[id].ring(DAMP);
    });
    return out;
  }
  var s2 = {
    id: 's04-02', title: 'The random walker', time: 40, steps: 4,
    notes: [
      'Now I let one person loose in this world, someone who wanders around without any plan. There is one rule. From the node where they stand, they pick one outgoing arrow, and they pick heavier arrows more often.',
      'I spin the spinner next to A. Of its three slices, two are B and one is C. The weights 2 and 1 have simply become the numbers of slices. This time it lands on B, so the walker crosses to B.',
      'Of A\'s total weight 3, 2 points toward B, so two times out of three the walker goes to B. I write this probability as P. In general, we divide the weight of an arrow by the sum of the weights leaving its node.',
      'In the same way, A to C is one third. From B and from C there is only one way out, so the walker always goes to D. The probabilities leaving a node always add up to 1. D is the only exception, because there is nothing to add.',
      'Spinning at B can only give D. So the walker moves on to D, but D has no arrow to leave by, so the walk gets stuck. Also, B to D is the only way out of B, so even with weight 3 the probability is 1. Weights only matter where the path forks.'
    ],
    html: '<h1 class="t-h1">One rule: pick one [[outgoing arrow]] of the current node</h1>' + panelBg(2) +
      '<div class="s4-pn">' +
        '<div class="s4-L" data-in="words">Thicker arrows are picked more often</div>' +
        '<div class="s4-l" data-step="1">From A: to B <b>2 times in 3</b>, to C <b>1 time in 3</b></div>' +
        '<div id="dv" data-in="none" style="margin-top:22px"></div>' +
        '<div data-step="4" style="margin-top:22px"><div class="s4-q">D has no arrow to leave by!</div>' +
        '<div class="s4-note">B → D is the only way out of B, so its weight 3 does not change the probability</div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 0.35, cupLabels: false, dangling: true });
      g.fx = fxSvg(ctx, el);
      g.sp = makeSpinners(g.fx);
      gsap.set([g.sp.A.g, g.sp.B.g, g.sp.C.g], { autoAlpha: 0 });
      gsap.set(q(el, '#dv'), { autoAlpha: 0 });
      g.dv = Comp.derive(ctx, q(el, '#dv'), { head: 'Probability', lines: [
        { tex: 'P_{A,B}=\\frac{w(A,B)}{o(A)}=\\part{f}{\\frac{2}{3}}', note: 'Of A\'s total weight 3, 2 points to B → to B 2 times in 3', mark: 'f' },
        { tex: '\\part{g}{P_{u,v}=\\dfrac{w(u,v)}{o(u)}}', note: 'General form · weight of the arrow ÷ sum of the weights leaving u', mark: 'g' },
        { tex: 'P_{A,C}=\\tfrac{1}{3},\\quad P_{B,D}=\\tfrac{3}{3}=1,\\quad P_{C,D}=\\tfrac{1}{1}=1' },
        { tex: '\\tfrac{2}{3}+\\tfrac{1}{3}=1', note: 'Probabilities leaving a node sum to 1 · except D (nothing to add)' }
      ] });
      g.pCard = card(ctx, el, { tex: 'P_{u,v}', desc: 'probability of going from u to v', art: artArrow('2/3', 'p'), x: 96, y: 840 });
      g.bub = H('div', 's4-bubble', el, '?'); g.bub.setAttribute('data-in', 'none');
      var d = stageOf('D'); g.bub.style.left = (d.x + 64) + 'px'; g.bub.style.top = (d.y - 78) + 'px';
      gsap.set(g.bub, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      panelEnter(el, ctx);
      tl.call(function () { dangling(g.W, false); }, null, 0.4);
      ['A', 'B', 'C'].forEach(function (id, k) {
        tl.fromTo(g.sp[id].g, { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: E.stamp }, 0.5 + k * 0.12);
      });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, W = g.W, tl = ctx.tl();
      if (i === 1) {
        W.walker.place('A');
        tl.add(W.walker.pulse(), 0);
        tl.add(g.sp.A.spin(0, 2), 0.2);
        tl.add(W.walker.hop('B', { duration: 0.6 }), 1.75);
      }
      if (i === 2) {
        W.walker.place('B');
        tl.set(q(el, '#dv'), { autoAlpha: 1 }, 0);
        tl.add(g.dv.show(1), 0);
        tl.add(g.pCard.pop(), 0.3);
        var fpart = g.dv.lines[0].F.parts('f')[0];
        gsap.set(fpart, { autoAlpha: 0 });
        tl.call(function () {
          ctx.add(function () {
            var sr = ctx.rect(g.sp.A.g);
            flyer(ctx, el, tex('\\tfrac{2}{3}'), { x: sr.cx, y: sr.cy }, fpart, { duration: 0.9 });
          });
        }, null, 0.75);
        tl.add(g.dv.show(2), 2.2);
      }
      if (i === 3) {
        W.walker.place('B');
        tl.add(g.dv.show(3), 0);
        tl.add(g.dv.show(4), 1.6);
      }
      if (i === 4) {
        W.walker.place('B');
        tl.add(g.sp.B.spin(0, 1, { duration: 0.9 }), 0);
        tl.add(W.walker.hop('D', { duration: 0.6 }), 0.95);
        tl.add(W.walker.pulse(), 1.6);
        tl.fromTo(g.bub, { autoAlpha: 0, scale: 0.3, rotation: -12 }, { autoAlpha: 1, scale: 1, rotation: 0, duration: 0.45, ease: E.stamp }, 1.7);
        tl.call(function () { dangling(W, true); }, null, 1.7);
        var L = W.edge('B', 'D').lbl || W.edge('B', 'D').label;
        tl.fromTo(L, { scale: 1.8, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.6, ease: 'power2.out', repeat: 1, repeatDelay: 0.2 }, 2.4);
      }
    },
    tags: ['thesis-example']
  };

  /* ================================================================ s04-03 */
  var s3 = {
    id: 's04-03', title: 'A long walk: share of time → balance equation', time: 50, steps: 5,
    notes: [
      'If this person walks for a very long time, the fraction of time spent at each node settles down. PageRank uses exactly this fraction as the node\'s score.',
      'Instead of one person, think of 1 liter of water. You can also picture the person split into very many droplets. At first I put a quarter, 0.25, into each of the four cups. I write the water in the cup of node v as r_v. This is the node\'s share, that is, its score.',
      'Now I pour once. The water in each cup is split along the outgoing arrows in proportion to their probabilities. A\'s water goes to B and C at 2 to 1, and all of B\'s and C\'s water goes to D. But D\'s water has no way out, so it spills away. We come back to this problem two slides from now.',
      'If we keep pouring like this, there comes a point where the amount in each cup no longer changes. We call this balance. The water has not stopped. It keeps flowing, but as much comes in as goes out, so the amount stays the same. So at balance, the water in my cup equals the water flowing into me. B gets two thirds of A, C gets one third of A, and D gets all of B\'s and C\'s water. Nobody points to A, so A is 0.',
      'Written in one line, it looks like this. My share is the sum of the shares passed to me by the nodes that point to me. The u, arrow, v under the sigma means we add only the nodes u that point to v. This is called the balance equation.',
      'But if we solve this equation all the way through, something odd happens. A is 0, so B is 0 times two thirds, which is 0, and C is 0 too. Then D is 0 plus 0, which is 0. The only solution of the balance equation is "all zero". It means all the water leaks out at D. The next two slides fix this problem.'
    ],
    html: '<h1 class="t-h1">Walk long enough and each node gets a fixed [[share of time]]</h1>' + panelBg(3) +
      '<div class="s4-pn">' +
        '<div class="s4-L" data-in="words">That share is the node\'s score <b>r</b></div>' +
        '<div class="s4-l" data-step="1">New picture: one walker → <b>1 liter of water</b>, poured in parts</div>' +
        '<div id="dv" data-in="none" style="margin-top:20px"></div>' +
        '<div data-step="4" style="margin-top:18px"><div class="s4-key">My share = the sum of the shares passed to me</div><div id="gen" class="s4-tx" style="margin-top:10px"></div></div>' +
        '<div data-step="5" style="margin-top:12px"><div class="s4-q">But solve it: <span id="zch">$r_A=0\\;\\Rightarrow\\;r_B=r_C=0\\;\\Rightarrow\\;r_D=0+0=0$</span></div>' +
          '<div class="s4-note">The only solution is <b class="ink">‘all zero’</b>: all the water leaks out at D</div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 0.35, cupLabels: false, dangling: true });
      g.PL = Particles(ctx, el);
      g.dv = Comp.derive(ctx, q(el, '#dv'), { head: 'Balance: water flows, levels hold → cup = inflow', lines: [
        { tex: 'r_B=r_A\\cdot\\tfrac{2}{3}', display: false, note: 'inflow to B: 2/3 of A\'s share' },
        { tex: 'r_C=r_A\\cdot\\tfrac{1}{3}', display: false },
        { tex: 'r_D=r_B\\cdot 1+r_C\\cdot 1', display: false },
        { tex: 'r_A=0', display: false, note: 'nobody points to A' }
      ] });
      g.gen = Comp.formula(ctx, q(el, '#gen'), 'r_v=\\sum_{\\part{s}{u:\\,u\\to v}} r_u\\,\\frac{w(u,v)}{o(u)}=\\sum_{u} r_u\\,P_{u,v}');
      g.rCard = card(ctx, el, { tex: 'r_v', desc: 'share (score) of node v = water in its cup', art: artCups(), x: 96, y: 840 });
      gsap.set(q(el, '#dv'), { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      panelEnter(el, ctx);
      ctx.g.W.walker.place('D');
      ctx.timeout(function () { dangling(ctx.g.W, false); }, 400);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, W = g.W, PL = g.PL, tl = ctx.tl();
      if (i === 1) {
        W.walker.place('D');
        tl.add(W.walker.pulse(), 0);
        tl.to(W.walker.g, { autoAlpha: 0, duration: 0.2 }, 0.45);
        IDS.forEach(function (id, k) {
          var a = [NODE.D.x, NODE.D.y], b = cupMid(id, 26), mid = [(a[0] + b[0]) / 2, Math.min(a[1], b[1]) - 120 - k * 10];
          tl.add(PL.emit({ n: 60, duration: 1.2, spread: 0.4, jitter: 14, seed: 3 + k, path: function (t) {
            var u = 1 - t; return [u * u * a[0] + 2 * u * t * mid[0] + t * t * b[0], u * u * a[1] + 2 * u * t * mid[1] + t * t * b[1]];
          } }), 0.45);
        });
        tl.to(W.cupG, { autoAlpha: 1, duration: 0.4 }, 0.5);
        tl.to(W.cupL, { autoAlpha: 1, duration: 0.4 }, 1.2);
        tl.add(setCups(W, [0.25, 0.25, 0.25, 0.25], { duration: 0.8 }), 1.0);
        tl.add(g.rCard.pop(), 1.9);
      }
      if (i === 2) {
        var r0 = LEAK.hist[0], r1 = LEAK.hist[1];
        tl.add(setCups(W, [0, 0, 0, 0], { duration: 0.5, ease: 'power2.in' }), 0);
        tl.add(PL.emit({ n: 40, duration: 1.4, path: pourPath(W, 'A', 'B'), seed: 5 }), 0.1);
        tl.add(PL.emit({ n: 20, duration: 1.4, path: pourPath(W, 'A', 'C'), seed: 6 }), 0.1);
        tl.add(PL.emit({ n: 60, duration: 1.4, path: pourPath(W, 'B', 'D'), seed: 7 }), 0.1);
        tl.add(PL.emit({ n: 60, duration: 1.4, path: pourPath(W, 'C', 'D'), seed: 8 }), 0.1);
        tl.add(PL.emit({ n: 60, duration: 1.2, path: spillPath('D'), seed: 9, color: C.hi, jitter: 10 }), 0.2);
        tl.call(function () { dangling(W, true); }, null, 0.3);
        tl.add(pulseNode(W.node('D')), 0.3);
        tl.add(setCups(W, r1, { duration: 0.7 }), 1.25);
        void r0;
      }
      if (i === 3) {
        tl.set(q(el, '#dv'), { autoAlpha: 1 }, 0);
        tl.add(g.dv.show(1), 0);
        tl.add(pulseArrow(W.edge('A', 'B')), 0.2);
        tl.add(g.dv.show(2), 0.9);
        tl.add(pulseArrow(W.edge('A', 'C')), 1.1);
        tl.add(g.dv.show(3), 1.8);
        tl.add(pulseArrow(W.edge('B', 'D')), 2.0);
        tl.add(pulseArrow(W.edge('C', 'D')), 2.0);
        tl.add(g.dv.show(4), 2.7);
        tl.add(pulseNode(W.node('A')), 2.9);
      }
      if (i === 4) {
        tl.call(function () { ctx.add(function () { var t2 = gsap.timeline(); t2.add(g.gen.mark('s')); t2.add(g.gen.unmark('s'), 2.2); }); }, null, 0.8);
      }
      if (i === 5) {                                                  /* the balance equations only solve to "all zero": the cups drain */
        /* two more pours of the same rule (computed): 0.75 → 0.25 → 0 */
        tl.add(pulseNode(W.node('A')), 0.2);
        tl.call(function () { dangling(W, true); }, null, 0.4);
        tl.add(PL.emit({ n: 40, duration: 1.1, path: pourPath(W, 'B', 'D'), seed: 13 }), 0.4);
        tl.add(PL.emit({ n: 20, duration: 1.1, path: pourPath(W, 'C', 'D'), seed: 14 }), 0.4);
        tl.add(PL.emit({ n: 120, duration: 1.1, path: spillPath('D'), seed: 15, color: C.hi, jitter: 10 }), 0.5);
        tl.add(setCups(W, LEAK.hist[2], { duration: 0.6 }), 1.2);
        tl.add(PL.emit({ n: 60, duration: 1.1, path: spillPath('D'), seed: 16, color: C.hi, jitter: 10 }), 1.9);
        tl.add(setCups(W, LEAK.hist[3], { duration: 0.6 }), 2.4);
        tl.add(pulseNode(W.node('D')), 2.4);
      }
    },
    tags: ['thesis-example']
  };

  /* ================================================================ s04-04 */
  var MX = { x: 984, y: 330, H: 44, c: 86 };
  MX.S = MX.H + 4 * MX.c;
  var PT = { A: { B: '\\tfrac{2}{3}', C: '\\tfrac{1}{3}' }, B: { D: '1' }, C: { D: '1' }, D: {} };
  var PV = { A: { B: 2 / 3, C: 1 / 3 }, B: { D: 1 }, C: { D: 1 }, D: {} };
  function buildFace(face, transposed) {
    var H0 = MX.H, c = MX.c, cells = {};
    IDS.forEach(function (k, j) {
      var hc = H('div', 's4-hcell', face, k); hc.style.cssText = 'left:' + (H0 + j * c) + 'px;top:0;width:' + c + 'px;height:' + H0 + 'px';
      var hr = H('div', 's4-hcell', face, k); hr.style.cssText = 'left:0;top:' + (H0 + j * c) + 'px;width:' + H0 + 'px;height:' + c + 'px';
    });
    IDS.forEach(function (ri, i) {
      IDS.forEach(function (cj, j) {
        var from = transposed ? cj : ri, to = transposed ? ri : cj;   /* Pᵀ[i][j] = P[j][i] */
        var v = PV[from][to] || 0;
        var cell = H('div', 's4-cell', face);
        cell.style.cssText = 'left:' + (H0 + j * c) + 'px;top:' + (H0 + i * c) + 'px;width:' + (c + 1) + 'px;height:' + (c + 1) + 'px';
        var bg = H('div', 'bgf', cell);
        var val = H('span', 'val' + (v ? '' : ' z'), cell, v ? tex(PT[from][to]) : '0');
        cells[ri + cj] = { el: cell, bg: bg, val: val, v: v };
      });
    });
    return cells;
  }
  var s4 = {
    id: 's04-04', title: 'One table: the transition matrix', time: 45, steps: 4,
    notes: [
      'With millions of nodes we cannot write the equations one by one, so we collect all the forks in one table. The rows are the nodes we leave from, and the columns are the nodes we arrive at.',
      'In each cell we write the probability of taking that arrow. Row A has two thirds in column B and one third in column C. Rows B and C have 1 in column D. Cells without an arrow are 0. This table is the transition matrix P.',
      'Row D is empty. That is because D has no outgoing arrow. A node like this is called a dangling node.',
      'Now I flip this table about its diagonal. The flipped table is called P transpose, written as P with a T on top. Now each row collects everything that flows into that node.',
      'I call the list of the four shares, stacked in a column, r. Multiplying r by the flipped table adds up, for every arrival node at once, all the shares that flow in. Look at row D: 0 times r_A, plus 1 times r_B, plus 1 times r_C, plus 0 times r_D, gives r_B plus r_C. That is exactly the balance equation I wrote by hand on the last slide. So one pour is one multiplication by the table.'
    ],
    html: '<h1 class="t-h1">One [[table]] for all the forks: P</h1>' + panelBg(4) +
      '<div class="s4-cap" id="cap" style="left:984px;top:268px;width:800px"><span id="capt">Row = node we <b>leave</b> · column = node we <b>reach</b> · cell = probability</span></div>' +
      '<div class="s4-mxw" id="mxw" data-in="none"><div class="s4-flip" id="flip"><div class="s4-face front" id="ff"></div><div class="s4-face back" id="fb"></div></div></div>' +
      '<div class="abs" data-step="2" data-step-out="3" data-in="left" style="left:1404px;top:' + (330 + 44 + 3 * 86 + 26) + 'px"><span class="s4-pill">dangling node · no outgoing arrow</span></div>' +
      '<div class="s4-vec" id="vec" data-in="none"></div>' +
      '<div class="s4-vec" id="res" data-in="none"></div>' +
      '<div class="abs" id="eqs" style="left:984px;top:742px;width:800px">' +
        '<div class="s4-tx" data-step="1" data-in="fade">$P_{u,v}=\\begin{cases} w(u,v)/o(u) & \\text{if } o(u)>0\\\\ 0 & \\text{otherwise}\\end{cases}$ <span class="source" style="margin-left:14px">Thesis Eq. (3.2)</span></div>' +
        '<div data-step="4" style="margin-top:6px"><div class="s4-tx">$\\mathbf r^{(t+1)}=P^{\\top}\\mathbf r^{(t)}$ <span class="s4-note" style="margin-left:12px">(t) = after the t-th pour</span></div>' +
        '<div class="s4-tx" id="dline">$(P^{\\top}\\mathbf r)_D=0\\cdot r_A+1\\cdot r_B+1\\cdot r_C+0\\cdot r_D=r_B+r_C$</div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cups: LEAK.hist[1], dangling: true });
      var mxw = q(el, '#mxw');
      mxw.style.cssText = 'left:' + MX.x + 'px;top:' + MX.y + 'px;width:' + MX.S + 'px;height:' + MX.S + 'px';
      g.front = buildFace(q(el, '#ff'), false);
      g.back = buildFace(q(el, '#fb'), true);
      g.flip = q(el, '#flip');
      /* front starts empty: grid lines appear in step 1, values fly in */
      g.frontCells = Object.keys(g.front).map(function (k) { return g.front[k]; });
      gsap.set(qa(q(el, '#ff'), '.s4-cell, .s4-hcell'), { autoAlpha: 0 });
      gsap.set(g.frontCells.map(function (c) { return c.val; }), { autoAlpha: 0 });
      Object.keys(g.back).forEach(function (k) { var c = g.back[k]; if (c.v) gsap.set(c.bg, { opacity: 0.12 + 0.3 * c.v }); });
      /* D-row mark (front) and D-column mark (back) */
      g.rowMark = H('div', 's4-rowmark', q(el, '#ff'));
      g.rowMark.style.cssText = 'left:' + MX.H + 'px;top:' + (MX.H + 3 * MX.c) + 'px;width:' + (4 * MX.c + 1) + 'px;height:' + (MX.c + 1) + 'px';
      gsap.set(g.rowMark, { autoAlpha: 0 });
      /* vector r and the product Pᵀr */
      var vx = MX.x + MX.S + 44, vy = MX.y;
      var vec = q(el, '#vec'), res = q(el, '#res');
      vec.style.cssText = 'left:' + vx + 'px;top:' + vy + 'px;width:96px;height:' + MX.S + 'px';
      res.style.cssText = 'left:' + (vx + 160) + 'px;top:' + vy + 'px;width:200px;height:' + MX.S + 'px';
      H('div', 'vh', vec, tex('\\mathbf r'));
      H('div', 'vh', res, tex('P^{\\top}\\mathbf r'));
      var eq = H('div', 'vh', vec, '='); eq.style.cssText = 'left:118px;width:30px;top:' + (MX.H + 1.5 * MX.c) + 'px;height:' + MX.c + 'px';
      g.vc = []; g.rc = [];
      var RES = ['0', '\\tfrac{2}{3}\\,r_A', '\\tfrac{1}{3}\\,r_A', 'r_B+r_C'];
      IDS.forEach(function (k, i) {
        var c1 = H('div', 'vc', vec, tex('r_' + k)); c1.style.top = (MX.H + i * MX.c) + 'px'; c1.style.height = (MX.c + 1) + 'px';
        var c2 = H('div', 'vc', res, tex(RES[i])); c2.style.top = (MX.H + i * MX.c) + 'px'; c2.style.height = (MX.c + 1) + 'px';
        g.vc.push(c1); g.rc.push(c2);
      });
      g.eqSign = eq;
      gsap.set([vec, res], { autoAlpha: 0 });
      gsap.set(g.rc, { autoAlpha: 0 });
      g.vecEl = vec; g.resEl = res;
      g.rCard = card(ctx, el, { tex: '\\mathbf r', desc: 'the four shares stacked in a column (a vector)', art: artVec(), x: 96, y: 836 });
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      panelEnter(el, ctx);
      /* drain the cups of s04-03 and dim them: this slide is about the table */
      ctx.gsap.to(g.W.cupG, { autoAlpha: 0.35, duration: 0.5, delay: 0.5 });
      ctx.gsap.to(g.W.cupL, { autoAlpha: 0, duration: 0.4, delay: 0.5 });
      setCups(g.W, [0, 0, 0, 0], { duration: 0.6, ease: 'power2.inOut', delay: 0.2 });
      ctx.timeout(function () { dangling(g.W, false); }, 400);
      var ff = q(el, '#ff');
      ctx.gsap.fromTo(qa(ff, '.s4-hcell'), { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4, stagger: 0.04, delay: 0.3 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, W = g.W, tl = ctx.tl();
      if (i === 1) {
        var ff = q(el, '#ff');
        tl.fromTo(qa(ff, '.s4-cell'), { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: E.out, stagger: { each: 0.03, grid: [4, 4], from: 'start' } }, 0);
        W.edges.forEach(function (A, k) {
          var cell = g.front[A.fromId + A.toId], p = A.pointAt(0.5);
          var from = { x: WX + p.x, y: WY + p.y };
          tl.add(pulseArrow(A), 0.6 + k * 0.3);
          tl.add(flyer(ctx, el, tex(PT[A.fromId][A.toId]), from, cell.val, { duration: 0.8 }), 0.6 + k * 0.3);
          tl.to(cell.bg, { opacity: 0.12 + 0.3 * cell.v, duration: 0.4 }, 1.55 + k * 0.3);
        });
        var zeros = g.frontCells.filter(function (c) { return !c.v; }).map(function (c) { return c.val; });
        tl.fromTo(zeros, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, stagger: 0.03 }, 2.8);
      }
      if (i === 2) {
        tl.fromTo(g.rowMark, { autoAlpha: 0, scaleX: 0.2, transformOrigin: '0% 50%' }, { autoAlpha: 1, scaleX: 1, duration: 0.5, ease: E.out }, 0);
        tl.fromTo(g.rowMark, { backgroundColor: 'rgba(255,107,138,.45)' }, { backgroundColor: 'rgba(255,107,138,.16)', duration: 0.25, repeat: 3, yoyo: true }, 0.5);
        tl.call(function () { dangling(W, true); }, null, 0.4);
        tl.add(pulseNode(W.node('D')), 0.4);
      }
      if (i === 3) {
        var st = { a: 0 };
        tl.to(g.rowMark, { autoAlpha: 0, duration: 0.2 }, 0);
        tl.to(st, { a: 180, duration: ctx.reduced ? 0.01 : 1.3, ease: 'power2.inOut', onUpdate: function () { g.flip.style.transform = 'rotate3d(1,1,0,' + st.a + 'deg)'; },
          onComplete: function () { g.flip.style.transform = 'rotate3d(1,1,0,180deg)'; } }, 0.15);
        tl.add(Comp.swap(ctx, q(el, '#capt'), 'P<sup>T</sup> · row = node we <b>reach</b> = what <b>flows in</b> · column = node we leave'), 0.4);
      }
      if (i === 4) {
        g.flip.style.transform = 'rotate3d(1,1,0,180deg)';
        tl.set(g.vecEl, { autoAlpha: 1 }, 0);
        tl.fromTo(g.vc, { autoAlpha: 0, rotationX: -90, transformOrigin: '50% 100%' }, { autoAlpha: 1, rotationX: 0, duration: 0.5, ease: E.out, stagger: 0.08 }, 0);
        tl.fromTo(q(g.vecEl, '.vh'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0);
        tl.add(g.rCard.pop(), 0.4);
        /* walk the D row of Pᵀ against r */
        IDS.forEach(function (k, j) {
          var cell = g.back['D' + k].el, t0 = 0.9 + j * 0.45;
          tl.fromTo(cell, { boxShadow: 'inset 0 0 0 0 rgba(255,107,138,0)' }, { boxShadow: 'inset 0 0 0 3px rgba(255,107,138,1)', duration: 0.2 }, t0);
          tl.add(function () { g.vc[j].classList.add('on'); }, t0);
          tl.to(cell, { boxShadow: 'inset 0 0 0 0 rgba(255,107,138,0)', duration: 0.25 }, t0 + 0.38);
          tl.add(function () { g.vc[j].classList.remove('on'); }, t0 + 0.4);
        });
        tl.set(g.resEl, { autoAlpha: 1 }, 0.9);
        tl.fromTo(q(g.resEl, '.vh'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.9);
        tl.fromTo(g.rc[3], { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: E.stamp }, 2.8);
        tl.fromTo([g.rc[0], g.rc[1], g.rc[2]], { autoAlpha: 0, x: -20 }, { autoAlpha: 1, x: 0, duration: 0.4, stagger: 0.12 }, 3.4);
        tl.add(pulseArrow(W.edge('B', 'D')), 2.8);
        tl.add(pulseArrow(W.edge('C', 'D')), 2.8);
      }
    },
    tags: ['thesis-example']
  };

  /* ================================================================ s04-05 */
  var TW = { x: 984, y: 410, w: 796, h: 340 };
  var TNODES = [
    { id: 'A', x: 46, y: 140, kind: 'eoa', size: 13, label: 'A' },
    { id: 'B', x: 196, y: 56, kind: 'contract', size: 46, label: 'B' },
    { id: 'C', x: 196, y: 224, kind: 'contract', size: 46, label: 'C' },
    { id: 'D', x: 430, y: 140, kind: 'contract', size: 46, label: 'D' },
    { id: 'E', x: 660, y: 140, kind: 'contract', size: 46, label: 'E', dashed: true, stroke: C.hi }
  ];
  function trapGraph(ctx, el, o) {
    var host = H('div', '', el); host.setAttribute('data-in', 'none');
    host.style.cssText = 'position:absolute;left:' + TW.x + 'px;top:' + TW.y + 'px;width:' + TW.w + 'px;height:' + TW.h + 'px';
    var G = Comp.graph(ctx, host, { w: TW.w, h: TW.h, nodes: TNODES,
      edges: [{ from: 'A', to: 'B', w: 2 }, { from: 'A', to: 'C', w: 1 }, { from: 'B', to: 'D', w: 3 }, { from: 'C', to: 'D', w: 1 },
        { from: 'D', to: 'E', w: 1, bend: -34 }, { from: 'E', to: 'D', w: 1, bend: -34 }],
      showWeights: false, weightWidth: function (w) { return 2 + 1.4 * w; },
      cups: { dy: 52, w: 40, h: 46, max: CUP_MAX, decimals: 4, color: WATER, value: 0.2 }, hidden: !!o.hidden });
    G.host = host;
    G.cupG = TIDS.map(function (id) { return G.cups[id].g; });
    return G;
  }
  var s5 = {
    id: 's04-05', title: 'Two problems: leaking water and traps', time: 45, steps: 3,
    notes: [
      'If we just apply the balance equation over and over, two problems appear. Let me start again with 0.25 in each of the four cups.',
      'First, water that goes into the dangling node D has nowhere to go, so it disappears. If we actually compute it, the total water shrinks from 1 to 0.75, then 0.25, then 0. After three pours no water is left at all.',
      'Second, if two nodes point only at each other, the water that goes in is trapped forever. To show this, I added one more node, E. D and E approve each other. With five nodes we start with 0.2 each. After two pours all the water is in D and E, and from then on it sloshes back and forth between 0.4 and 0.6. The values never stop changing. We say it does not converge.',
      'E is a node I added for this explanation. This shape, addresses that approve each other, comes back in section 10, where we talk about the cost of attacks.'
    ],
    html: '<h1 class="t-h1">Problem 1 · water [[leaks]] at the dangling node</h1>' + panelBg(5) +
      '<div class="s4-pn">' +
        '<div class="t-h2">Problem 2 · a trap</div>' +
        '<div class="s4-l" data-step="2">D ⇄ E point only at each other and trap all the water</div>' +
      '</div>' +
      '<div class="abs" data-step="2" data-in="fade" style="left:984px;top:790px;width:800px">' +
        '<div class="s4-chain"><span class="ink-2" style="font-size:24px">(D, E)</span><span class="v" id="tv">(0.2, 0.2)</span></div>' +
        '<div class="s4-q" style="margin-top:6px">The values never settle (no convergence)</div>' +
      '</div>' +
      '<div class="abs s4-note" data-step="3" style="left:984px;top:920px;width:800px">E is only for illustration · mutual approvals return in <b class="ink">10 · Attack cost and speed</b></div>' +
      '<div class="abs" style="left:96px;top:846px;width:800px">' +
        '<div class="s4-tx" style="font-size:26px">$\\mathbf r^{(t+1)}=P^{\\top}\\mathbf r^{(t)},\\quad \\mathbf r^{(0)}=(0.25,\\,0.25,\\,0.25,\\,0.25)$</div>' +
        '<div class="s4-chain" id="tot" style="margin-top:6px"><span class="ink-2" style="font-size:24px">Total water $\\textstyle\\sum_v r^{(t)}_v$</span>' +
          '<span class="v" data-t="0">1</span><span class="ar" data-t="1">→</span><span class="v" data-t="1">0.75</span><span class="ar" data-t="2">→</span><span class="v" data-t="2">0.25</span><span class="ar" data-t="3">→</span><span class="v zero" data-t="3">0</span></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 0.35, cupLabels: false, dangling: true });
      g.PL = Particles(ctx, el);
      g.ga = gauge(ctx, el, { x: 872, y: 330, h: 360, value: 1 });
      var tot = q(el, '#tot');
      g.tot = qa(tot, '[data-t]');
      gsap.set(g.tot.filter(function (n) { return n.getAttribute('data-t') !== '0'; }), { autoAlpha: 0 });
      g.T = trapGraph(ctx, el, { hidden: true });
      g.T.edges.forEach(function (A) { if (A.label) gsap.set(A.label, { autoAlpha: 0 }); });
      g.tv = q(el, '#tv');
      g.tag10 = H('div', '', el, '<span class="s4-pill" style="font-size:18px;padding:2px 10px">→ 10</span>');
      g.tag10.setAttribute('data-in', 'none');
      g.tag10.style.cssText = 'position:absolute;left:' + (TW.x + 660 + 34) + 'px;top:' + (TW.y + 140 - 70) + 'px';
      gsap.set(g.tag10, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      panelEnter(el, ctx);
      ctx.gsap.to(g.W.cupG, { autoAlpha: 1, duration: 0.4, delay: 0.2 });
      ctx.gsap.to(g.W.cupL, { autoAlpha: 1, duration: 0.4, delay: 0.4 });
      setCups(g.W, [0.25, 0.25, 0.25, 0.25], { duration: 0.8, delay: 0.3 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, W = g.W, PL = g.PL, tl = ctx.tl();
      if (i === 1) {
        for (var t = 1; t <= 3; t++) {
          var t0 = (t - 1) * 1.6, prev = LEAK.hist[t - 1], next = LEAK.hist[t];
          var amt = { AB: prev[0] * 2 / 3, AC: prev[0] / 3, BD: prev[1], CD: prev[2], D: prev[3] };
          tl.add(setCups(W, [0, 0, 0, 0], { duration: 0.4, ease: 'power2.in' }), t0);
          tl.add(PL.emit({ n: amt.AB * 240, duration: 1.1, path: pourPath(W, 'A', 'B'), seed: 10 + t }), t0 + 0.05);
          tl.add(PL.emit({ n: amt.AC * 240, duration: 1.1, path: pourPath(W, 'A', 'C'), seed: 20 + t }), t0 + 0.05);
          tl.add(PL.emit({ n: amt.BD * 240, duration: 1.1, path: pourPath(W, 'B', 'D'), seed: 30 + t }), t0 + 0.05);
          tl.add(PL.emit({ n: amt.CD * 240, duration: 1.1, path: pourPath(W, 'C', 'D'), seed: 40 + t }), t0 + 0.05);
          tl.add(PL.emit({ n: amt.D * 240, duration: 1.0, path: spillPath('D'), seed: 50 + t, color: C.hi }), t0 + 0.1);
          tl.add(setCups(W, next, { duration: 0.5 }), t0 + 0.95);
          tl.add(g.ga.set(sum(next), { duration: 0.6 }), t0 + 0.9);
          tl.fromTo(g.tot.filter(function (n) { return +n.getAttribute('data-t') === t; }), { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.35, stagger: 0.1 }, t0 + 1.05);
        }
      }
      if (i === 2) {
        var T = g.T;
        TIDS.forEach(function (id, k) { tl.add(T.node(id).pop(), k * 0.08); });
        T.edges.forEach(function (A, k) { tl.add(A.draw({ duration: 0.45 }), 0.4 + k * 0.08); });
        tl.fromTo(T.cupG, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, stagger: 0.05 }, 0.8);
        for (var p = 1; p <= 6; p++) {
          var vals = TRAP.hist[p], at = 1.3 + (p - 1) * 0.75;
          TIDS.forEach(function (id, k) { tl.add(T.cups[id].set(vals[k], { duration: 0.45, ease: 'power2.inOut' }), at); });
          (function (v) {
            tl.call(function () { g.tv.textContent = '(' + fmt(v[3], 1) + ', ' + fmt(v[4], 1) + ')'; }, null, at + 0.3);
          })(vals);
          tl.add(pulseArrow(p % 2 ? T.edge('D', 'E') : T.edge('E', 'D')), at);
        }
        tl.call(function () { var h = TRAP.hist; g.tv.textContent = [2, 3, 4].map(function (k) { return '(' + fmt(h[k][3], 1) + ', ' + fmt(h[k][4], 1) + ')'; }).join(' → ') + ' → …'; }, null, 1.3 + 6 * 0.75);
      }
      if (i === 3) {
        tl.fromTo(g.tag10, { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: E.stamp }, 0.3);
        tl.add(pulseNode(g.T.node('E')), 0.3);
      }
    },
    tags: function (st) { return st >= 2 ? ['calc', 'example'] : ['calc']; }
  };

  /* ================================================================ s04-06 */
  /* the three pieces of one step from r(t) = 1/4: rain, flow, dangling cloud */
  var R0 = [0.25, 0.25, 0.25, 0.25];
  var TELE = (1 - DAMP) / 4;                                                       /* 0.0375 */
  var FLOW = { AB: DAMP * R0[0] * 2 / 3, AC: DAMP * R0[0] / 3, BD: DAMP * R0[1], CD: DAMP * R0[2] };
  var DANG = DAMP * R0[3] / 4;                                                     /* 0.0531 each */
  var P1 = [TELE, TELE + FLOW.AB, TELE + FLOW.AC, TELE + FLOW.BD + FLOW.CD];
  var P2 = P1.map(function (v) { return v + DANG; });                              /* = r(1) */
  var CLOUD = [330, -24];
  var s6 = {
    id: 's04-06', title: 'The fix: damping factor d and restarts', time: 60, steps: 7,
    notes: [
      'The way to fix both problems at once is the damping factor d together with restarts.',
      'The walker follows an arrow 85 times out of 100, and 15 times teleports to any node at all. This 0.85 is called the damping factor d. The outer ring of each spinner shows that ratio. When the walker reaches the dangling node D, it always teleports. So from D, dashed lines spread to all four nodes, D itself included.',
      'Say the current shares are all 0.25, and let us fill in the new shares in three pieces. The first piece is the restart share. Every time, it falls evenly on every node: 0.15 divided by 4, which is 0.0375 each. I write how the restarts are spread over the nodes as π. For EndorseRank it is the same quarter for every node. |V| is the number of nodes.',
      'The second piece is the share that comes along the arrows. It is the same as the balance equation we built earlier, but multiplied by 0.85, so the streams are a little thinner.',
      'The third piece is the share collected from the dangling nodes and handed out again. We gather D\'s water like a cloud and let it fall evenly on every node. 1_dang is a list that is 1 for a dangling node and 0 otherwise. The T on r means we lay the column list down as a row, and multiplying a row list by a column list means multiplying cell by cell and adding it all up. That is 0 times 0.25 three times and 1 times 0.25 once, so the sum is 0.25, which is r_D. Only the share of the dangling node is left. Multiplying by 0.85 and by one quarter gives 0.0531. With all three pieces filled in, we get exactly the r(1) of Chapter 2 of the thesis.',
      'Written node by node, this becomes the equation in Chapter 2 of the thesis. I kept the letters u and v from before. The thesis writes the same equation with i and j, and E means the set of all edges. No arrow points to A, so A\'s share is only the share collected from D plus the restart share. That is 0.2125 times r_D plus 0.0375.',
      'When we add the three pieces, the total water always stays at 1. The restart share takes 1 minus d, and the other two pieces split d between them. In this example 0.15, 0.6375 and 0.2125 add up to exactly 1. No water leaks.',
      'Let me also run the trap from the last slide again with the fixed rule. The trapped water slowly gets out, the sloshing dies down, and the values settle. D is 0.4619 and E is 0.4226. The equation we have built is exactly the PageRank equation of Chapter 3 of the thesis.'
    ],
    html: '<h1 class="t-h1">85 times in 100 along an arrow, 15 times [[anywhere]]</h1>' + panelBg(6) +
      '<div class="s4-pn">' +
        '<div class="s4-rules" id="rules" data-in="none">' +
          '<div class="s4-rule"><span class="n" id="n85">85</span><span class="t">damping factor <b>d = 0.85</b> · follow an arrow</span></div>' +
          '<div class="s4-rule"><span class="n c-hi" id="n15">15</span><span class="t"><b>1 − d = 0.15</b> · teleport to any node (restart)</span></div>' +
          '<div class="s4-l" style="padding-left:114px">At a dangling node: always teleport</div>' +
        '</div>' +
        '<div class="s4-hero" id="hero" data-step="2" data-in="fade" style="margin-top:30px"></div>' +
        '<div class="s4-plabels" id="pls" data-step="2" data-in="fade"></div>' +
        '<div class="s4-slot" id="slot" style="margin-top:20px">' +
          '<div data-step="2" data-step-out="3"><div class="s4-l">Current shares = all 0.25 → fill the new share in <b>three pieces</b></div>' +
            '<div class="s4-tx"><span class="s4-circ">1</span>$(1-d)\\,\\pi_v=0.15\\times\\tfrac14=0.0375$</div><div class="s4-note">restart share, falling equally on every node</div></div>' +
          '<div data-step="3" data-step-out="4"><div class="s4-tx"><span class="s4-circ">2</span>$d\\,P^{\\top}\\mathbf r^{(t)}$</div><div class="s4-note">share that came along the arrows · the balance equation times 0.85, a little thinner</div>' +
            '<div class="s4-tx" style="font-size:26px">$\\text{e.g. } 0.85\\times0.25\\times\\tfrac23=0.1417\\;(A\\to B)$</div></div>' +
          '<div data-step="4" data-step-out="5"><div class="s4-tx"><span class="s4-circ">3</span>$d\\,\\bigl(\\mathbf r^{(t)\\top}\\mathbf 1_{\\mathrm{dang}}\\bigr)\\,\\boldsymbol\\pi=d\\,r_D\\,\\tfrac14$</div>' +
            '<div class="s4-note">shares of the dangling nodes, pooled and spread evenly · here only $r_D$</div>' +
            '<div class="s4-note" style="margin-top:10px">$\\mathbf r^{(t)\\top}\\mathbf 1_{\\mathrm{dang}}$ = <b class="ink">multiply cell by cell, then add</b> (only dangling shares remain)</div>' +
            '<div class="s4-tx" id="dotp" style="font-size:24px;line-height:36px;margin-top:4px"></div>' +
            '<div class="s4-tx" style="font-size:24px">$0.85\\times0.25\\times\\tfrac14=0.0531$ · new shares = $(0.0906,\\,0.2323,\\,0.1615,\\,0.5156)$</div></div>' +
          '<div data-step="5" data-step-out="6"><div class="s4-note">Node by node · Thesis Eq. (2.3)</div>' +
            '<div class="s4-tx" style="font-size:28px">$$r_v=d\\!\\!\\sum_{u:\\,u\\to v}\\! r_u\\,\\frac{w(u,v)}{o(u)}+\\frac{d}{|V|}\\sum_{u:\\,o(u)=0}\\! r_u+\\frac{1-d}{|V|}$$</div>' +
            '<div class="s4-note">The thesis writes it with $i\\to j$, $w_{ij}$, $o_i$ ($i, j$ = $u, v$ · $E$ = all edges)</div>' +
            '<div class="s4-note">Row of A: nobody points to A, so the first term is 0</div>' +
            '<div class="s4-tx">$r_A=\\tfrac{0.85}{4}\\,r_D+\\tfrac{0.15}{4}=0.2125\\,r_D+0.0375$</div></div>' +
          '<div data-step="6" data-step-out="7"><div class="s4-L">No water leaks</div>' +
            '<div class="s4-tx" style="font-size:26px">$$\\sum_j r^{(t+1)}_j=(1-d)+d\\!\\!\\sum_{\\text{non-dangling }i}\\!\\! r^{(t)}_i+d\\!\\!\\sum_{\\text{dangling }i}\\!\\! r^{(t)}_i=(1-d)+d=1$$</div>' +
            '<div class="s4-tx" style="font-size:28px">$\\text{This example: } 0.15+0.6375+0.2125=1$</div></div>' +
          '<div data-step="7"><div class="s4-L">The trap is fixed too</div><div class="s4-note" id="trapv">The D ⇄ E sloshing dies down and the values settle</div></div>' +
        '</div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 1, cups: [0, 0, 0, 0], dangling: true });
      g.fx = fxSvg(ctx, el);
      g.sp = makeSpinners(g.fx, true);
      /* D: dangling — full teleport ring and a dashed fan to every node (itself included) */
      var dS = spinner(g.fx, 720, 160, 26, [{ n: 1, label: '', fill: 'rgba(255,107,138,.25)', ink: C.hi }]);
      dS.ring(0); g.sp.D = dS;
      g.rings = [].concat(g.sp.A.ringSegs, g.sp.B.ringSegs, g.sp.C.ringSegs, g.sp.D.ringSegs);
      gsap.set(g.rings, { autoAlpha: 0 });
      var D0 = NODE.D;
      g.fan = [
        Comp.arrow(ctx, g.fx, { from: [D0.x, D0.y], to: [NODE.A.x, NODE.A.y], kind: 'hi', color: C.hi, dashed: true, width: 2, head: 11, bend: 0, shorten: [34, 24], hidden: true }),
        Comp.arrow(ctx, g.fx, { from: [D0.x, D0.y], to: [NODE.B.x, NODE.B.y], kind: 'hi', color: C.hi, dashed: true, width: 2, head: 11, bend: -46, shorten: [34, 36], hidden: true }),
        Comp.arrow(ctx, g.fx, { from: [D0.x, D0.y], to: [NODE.C.x, NODE.C.y], kind: 'hi', color: C.hi, dashed: true, width: 2, head: 11, bend: 46, shorten: [34, 36], hidden: true })
      ];
      g.loop = S('path', { d: 'M' + (D0.x + 30) + ',' + (D0.y + 12) + ' C' + (D0.x + 92) + ',' + (D0.y + 40) + ' ' + (D0.x + 92) + ',' + (D0.y - 40) + ' ' + (D0.x + 34) + ',' + (D0.y - 12),
        fill: 'none', stroke: C.hi, 'stroke-width': 2, 'stroke-dasharray': '6 7' }, g.fx);
      gsap.set(g.loop, { autoAlpha: 0 });
      /* cloud for piece ③ */
      g.cloud = S('g', { transform: 'translate(' + CLOUD[0] + ',' + CLOUD[1] + ')' }, g.fx);
      [[-34, 6, 22], [-8, -6, 28], [22, 4, 22], [44, 10, 15]].forEach(function (c) { S('circle', { cx: c[0], cy: c[1], r: c[2], fill: 'rgba(233,237,245,.10)', stroke: C.ink3, 'stroke-width': 1.5 }, g.cloud); });
      gsap.set(g.cloud, { autoAlpha: 0 });
      g.PL = Particles(ctx, el);
      g.ga = gauge(ctx, el, { x: 872, y: 330, h: 360, value: 0 });
      gsap.set(g.ga.el, { autoAlpha: 0 });
      /* hero formula with the three named parts */
      g.hero = Comp.formula(ctx, q(el, '#hero'), '\\mathbf r^{(t+1)}=\\part{a}{(1-d)\\,\\boldsymbol\\pi}+\\part{b}{d\\,P^{\\top}\\mathbf r^{(t)}}+\\part{c}{d\\,\\bigl(\\mathbf r^{(t)\\top}\\mathbf 1_{\\mathrm{dang}}\\bigr)\\,\\boldsymbol\\pi}');
      /* piece ③ worked: a row times a column = multiply cell by cell and add */
      var dotp = q(el, '#dotp');
      Comp.formula(ctx, H('div', '', dotp), '(0.25,\\,0.25,\\,0.25,\\,0.25)\\cdot(0,\\,0,\\,0,\\,1)', { display: false });
      g.dot = Comp.formula(ctx, H('div', '', dotp),
        '=\\part{p0}{0\\times0.25}+\\part{p1}{0\\times0.25}+\\part{p2}{0\\times0.25}+\\part{p3}{1\\times0.25}\\part{res}{\\,=0.25=r_D}', { display: false });
      g.dotParts = ['p0', 'p1', 'p2', 'p3', 'res'].map(function (nm) { return g.dot.parts(nm); });
      var pls = q(el, '#pls');
      g.pl = [['1', 'restart share'], ['2', 'arrow share'], ['3', 'dangling share']].map(function (p) { return H('span', 'pl', pls, '<i>' + p[0] + '</i>' + p[1]); });
      g.cards = [
        card(ctx, el, { tex: '\\boldsymbol\\pi', desc: 'how restarts are spread<br>EndorseRank: all 1/|V|', x: 96 }),
        card(ctx, el, { tex: '|V|', desc: 'number of nodes<br>(here 4)', x: 520 }),
        card(ctx, el, { tex: '\\mathbf 1_{\\mathrm{dang}}', desc: '1 for a dangling node, else 0<br>here (0, 0, 0, 1)', x: 96 })
      ];
      /* trap window (step 7) */
      g.T = trapGraph(ctx, el, { hidden: true });
      g.T.host.style.top = '706px';
      g.T.host.style.transformOrigin = '0 0'; g.T.host.style.transform = 'scale(.74)';
      g.T.host.style.left = '1040px';
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      panelEnter(el, ctx);
      ctx.gsap.fromTo(q(el, '#rules'), { autoAlpha: 0 }, { autoAlpha: 0.22, duration: 0.5, delay: 0.3 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, W = g.W, PL = g.PL, tl = ctx.tl(), pls = g.pl;
      function partLabels(k) {
        /* place the ① ② ③ labels under their parts of the hero formula */
        var base = ctx.rect(q(el, '#pls'));
        ['a', 'b', 'c'].forEach(function (nm, j) { var r = g.hero.rect(nm); if (r) pls[j].style.left = (r.cx - base.x) + 'px'; pls[j].classList.toggle('on', j === k); });
      }
      if (i === 1) {
        tl.to(q(el, '#rules'), { autoAlpha: 1, duration: 0.4 }, 0);
        tl.add(ctx.count(q(el, '#n85'), 0, 85, { decimals: 0, duration: 1.0 }), 0.1);
        tl.add(ctx.count(q(el, '#n15'), 0, 15, { decimals: 0, duration: 1.0 }), 0.1);
        tl.set(g.rings, { autoAlpha: 1 }, 0.1);
        tl.add(drawSegs(g.rings, 0.1), 0.1);
        g.fan.forEach(function (A, k) { tl.add(A.draw({ duration: 0.5 }), 1.1 + k * 0.15); });
        tl.fromTo(g.loop, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.6);
      }
      if (i === 2) {
        gsap.set(q(el, '#rules'), { autoAlpha: 1 });
        tl.call(function () { partLabels(0); }, null, 0);
        tl.call(function () { ctx.add(function () { g.hero.mark('a', { delay: 0.1 }); }); }, null, 0.3);
        IDS.forEach(function (id, k) {
          var x = NODE[id].x, y0 = NODE[id].y + CUP_DY - 70, y1 = NODE[id].y + CUP_DY + 40;
          tl.add(PL.emit({ n: 18, duration: 1.1, spread: 0.6, jitter: 30, seed: 60 + k, alpha: 0.7, r: 2.4, path: function (t) { return [x, y0 + (y1 - y0) * t]; } }), 0.4);
        });
        tl.add(setCups(W, [TELE, TELE, TELE, TELE], { duration: 0.6 }), 1.2);
        tl.add(g.cards[0].pop(), 1.0);
        tl.add(g.cards[1].pop(), 1.2);
      }
      if (i === 3) {
        tl.call(function () { partLabels(1); ctx.add(function () { g.hero.unmark('a'); g.hero.mark('b', { delay: 0.1 }); }); }, null, 0);
        tl.to(g.cards[0].el, { autoAlpha: 0, duration: 0.3 }, 0); tl.to(g.cards[1].el, { autoAlpha: 0, duration: 0.3 }, 0);
        tl.add(PL.emit({ n: FLOW.AB * 200, r: 2.4, duration: 1.3, path: pourPath(W, 'A', 'B', true), seed: 71 }), 0.3);
        tl.add(PL.emit({ n: FLOW.AC * 200, r: 2.4, duration: 1.3, path: pourPath(W, 'A', 'C', true), seed: 72 }), 0.3);
        tl.add(PL.emit({ n: FLOW.BD * 200, r: 2.4, duration: 1.3, path: pourPath(W, 'B', 'D', true), seed: 73 }), 0.3);
        tl.add(PL.emit({ n: FLOW.CD * 200, r: 2.4, duration: 1.3, path: pourPath(W, 'C', 'D', true), seed: 74 }), 0.3);
        tl.add(setCups(W, P1, { duration: 0.6 }), 1.3);
      }
      if (i === 4) {
        tl.call(function () { partLabels(2); ctx.add(function () { g.hero.unmark('b'); g.hero.mark('c', { delay: 0.1 }); }); }, null, 0);
        tl.fromTo(g.cloud, { autoAlpha: 0, scale: 0.6, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: E.out }, 0.2);
        var dpt = [NODE.D.x, NODE.D.y];
        tl.add(PL.emit({ n: 50, duration: 1.0, spread: 0.4, jitter: 16, seed: 81, path: seg(dpt, CLOUD) }), 0.4);
        IDS.forEach(function (id, k) {
          tl.add(PL.emit({ n: 14, duration: 1.0, spread: 0.5, jitter: 18, seed: 90 + k, r: 2.4, path: seg([CLOUD[0] + (k - 1.5) * 20, CLOUD[1] + 20], cupMid(id, 10)) }), 1.3);
        });
        tl.add(setCups(W, P2, { duration: 0.6 }), 2.1);
        tl.add(g.cards[2].pop(), 1.0);
        tl.to(g.cloud, { autoAlpha: 0.35, duration: 0.5 }, 2.4);
        /* the four cell products drop in one by one; only D's (1 × 0.25) survives */
        g.dotParts.forEach(function (ps, k) {
          tl.fromTo(ps, { autoAlpha: 0, y: -18 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: E.out }, 0.7 + k * 0.28);
          if (k < 3) tl.to(ps, { opacity: 0.4, duration: 0.3 }, 1.0 + k * 0.28);
        });
        tl.call(function () { ctx.add(function () { g.dot.mark('p3', { pad: 4 }); }); }, null, 2.0);
        tl.add(pulseNode(W.node('D')), 2.0);
      }
      if (i === 5) {
        tl.call(function () { pls.forEach(function (p) { p.classList.remove('on'); }); ctx.add(function () { g.hero.unmark(); }); }, null, 0);
        tl.to(g.cards[2].el, { autoAlpha: 0, duration: 0.3 }, 0);
        tl.add(pulseNode(W.node('A')), 0.6);
        tl.add(pulseNode(W.node('D')), 0.6);
      }
      if (i === 6) {
        tl.fromTo(g.ga.el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0);
        tl.add(g.ga.set(1 - DAMP, { duration: 0.5, text: '0.15' }), 0.4);
        tl.add(g.ga.set(1 - DAMP + DAMP * 0.75, { duration: 0.5, text: '0.79' }), 1.1);
        tl.add(g.ga.set(1, { duration: 0.5, text: '1.00' }), 1.8);
        tl.call(function () { pls.forEach(function (p) { p.classList.add('on'); }); }, null, 0.4);
      }
      if (i === 7) {
        var T = g.T;
        gsap.set(g.ga.el, { autoAlpha: 1 });
        tl.set(T.host, { autoAlpha: 1 }, 0);
        TIDS.forEach(function (id, k) { tl.add(T.node(id).pop(), k * 0.06); });
        T.edges.forEach(function (A, k) { tl.add(A.draw({ duration: 0.4 }), 0.3 + k * 0.06); });
        tl.fromTo(T.cupG, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, stagger: 0.05 }, 0.6);
        var frames = [1, 2, 3, 4, 6, 9, 14, 22, 40, TRAPFIX.iters];
        frames.forEach(function (fi, k) {
          var v = TRAPFIX.hist[Math.min(fi, TRAPFIX.hist.length - 1)];
          TIDS.forEach(function (id, j) { tl.add(T.cups[id].set(v[j], { duration: 0.32, ease: 'power2.inOut' }), 1.0 + k * 0.36); });
        });
        var fin = TRAPFIX.r;
        tl.call(function () { q(el, '#trapv').innerHTML = 'The sloshing dies down and the values settle · D <b class="ink">' + f4(fin[3]) + '</b>, E <b class="ink">' + f4(fin[4]) + '</b>'; }, null, 1.0 + frames.length * 0.36);
      }
    },
    tags: function (st) { return st >= 7 ? ['thesis-example', 'calc', 'example'] : ['thesis-example']; }
  };

  /* ================================================================ s04-07 */
  var CH = { x: 0, y: 0, w: 796, h: 200 };                                   /* change chart (panel-local) */
  var s7 = {
    id: 's04-07', title: 'Repeat until it settles: power iteration', time: 60, steps: 4,
    notes: [
      'In practice we do not solve this equation in one go. We repeat the same calculation. This is called power iteration. At the start every node gets a quarter.',
      'Applying the equation once tilts the shares toward D. A becomes 0.0375 plus 0.2125 times 0.25, which is 0.0906. To measure how much changed, we add up the size of the difference in every cell. We drop the minus signs and add only the sizes. We write this with a double-bar symbol. The first time it is 0.531. The dots in the chart on the right are these changes. On the vertical scale, each grid line down is a hundred times smaller: 1, 0.01, 0.0001, one millionth, one hundred-millionth.',
      'With every repetition the change gets smaller, and at the 23rd iteration it falls below one hundred-millionth, so we stop. This threshold is written as epsilon. We also fixed a cap: however long it takes, we stop at 300 iterations. The final order is D, B, C, A. That is because D is endorsed by two vaults, and those vaults are in turn endorsed by A. A\'s share of 0.1375 is the restart share 0.0375 plus the 0.1000 collected from D.',
      'On the real allowance graph it stopped after 69 iterations, and on the transfer graph after 92. Each iteration does one multiplication per edge, so the time it takes follows the number of edges. This comes back in section 10.',
      'Let me change d directly. When d is 0, the walker never follows an arrow, so every node gets a quarter. As d grows, the arrows matter more: D grows, A shrinks, and it takes more iterations to settle. The browser computes these values on the spot.'
    ],
    html: '<h1 class="t-h1">[[Repeat]] the same calculation and the values settle</h1>' + panelBg(7) +
      '<div class="s4-pn" style="height:auto">' +
        '<div class="s4-iter"><span class="k">Power iteration:</span><span class="t" id="it">0</span><span class="k">iterations</span><span class="dl" id="dl">start: all 1/4</span></div>' +
        '<div id="bars" data-in="none" style="position:relative;height:196px;margin-top:8px"></div>' +
        '<div id="chart" data-in="none" style="position:relative;height:210px;margin-top:6px"></div>' +
        '<div class="s4-slot" id="slot" style="min-height:220px;margin-top:6px">' +
          '<div data-step="1" data-step-out="2"><div class="s4-tx" style="font-size:26px">$r^{(1)}_A=0.0375+0.2125\\times0.25=0.0906$</div>' +
            '<div class="s4-tx" style="font-size:26px">$\\lVert\\mathbf r^{(1)}-\\mathbf r^{(0)}\\rVert_1=0.1594+0.0177+0.0885+0.2656=0.531$</div>' +
            '<div class="s4-note">change = sum of the cell differences, signs dropped · symbol $\\lVert\\;\\rVert_1$</div></div>' +
          '<div data-step="2" data-step-out="3"><div class="s4-l"><b>After 23</b>: (0.1375, 0.2154, 0.1765, 0.4706) · order <b>D, B, C, A</b></div>' +
            '<div class="s4-l">Stop when $\\lVert\\mathbf r^{(t+1)}-\\mathbf r^{(t)}\\rVert_1<\\varepsilon$ · at most $I_{\\max}=300$ iterations</div>' +
            '<div class="s4-note">$\\varepsilon$ = one hundred-millionth ($10^{-8}$) · below that, almost nothing changes</div>' +
            '<div class="s4-note">A\'s share = restart 0.0375 + $d\\,r_D/4=0.1000$ collected from D</div></div>' +
          '<div data-step="3" data-step-out="4"><div class="s4-note">On the real graphs (revised analysis, T<sub>obs</sub>)</div><div class="s4-real">' +
            '<div class="it"><span class="n c-allow" id="r1">' + IT_ER + '</span><span class="k">EndorseRank · allowance graph</span></div>' +
            '<div class="it"><span class="n c-xfer" id="r2">' + IT_AWP + '</span><span class="k">AWP · transfer graph</span></div></div>' +
            '<div class="s4-note">One iteration = one multiplication per edge → time follows the <b class="ink">number of edges</b></div></div>' +
          '<div data-step="4"><div class="s4-l">Try changing d (bottom left)</div><div class="s4-note" id="dnote">The browser computes the values on the spot · d = 0 gives 0.25 for all</div></div>' +
        '</div>' +
      '</div>' +
      '<div class="s4-slider no-advance" id="sl" data-step="4" data-in="fade"><div class="lb">d = <b id="dv">0.85</b> <span class="ink-3" style="font-size:20px;margin-left:10px">drag to change · computed</span></div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 1, cups: P2, dangling: true });
      g.nCard = card(ctx, el, { tex: '\\lVert\\,\\square\\,\\rVert_1', desc: 'add up all sizes (signs dropped)<br>e.g. |−0.1594| = 0.1594', x: 96 });
      /* bars A..D */
      var bars = q(el, '#bars');
      var bsvg = Comp.svg(ctx, bars, { w: 796, h: 196 });
      g.bar = []; g.barT = [];
      var BX = 70, BW = 560, scale = BW / 0.6;
      IDS.forEach(function (k, i) {
        var y = 8 + i * 47;
        var lt = S('text', { x: 20, y: y + 26, fill: C.ink2, 'font-size': 24, 'font-weight': 700 }, bsvg); lt.textContent = k;
        S('rect', { x: BX, y: y + 4, width: BW, height: 30, rx: 6, fill: 'rgba(233,237,245,.04)' }, bsvg);
        g.bar.push(S('rect', { x: BX, y: y + 4, width: 0, height: 30, rx: 6, fill: C.ink, 'fill-opacity': 0.55 }, bsvg));
        var vt = S('text', { x: BX + BW + 18, y: y + 27, fill: C.ink, 'font-size': 24, 'class': 'svg-mono tnum' }, bsvg); g.barT.push(vt);
      });
      g.barScale = scale;
      /* change chart (log10 scale) */
      var chart = q(el, '#chart');
      var csvg = Comp.svg(ctx, chart, { w: 796, h: 210 });
      var X0 = 132, X1 = 770, Y0 = 14, Y1 = 176, NMAX = 30;
      var TICK = { '0': '1', '-2': '0.01', '-4': '0.0001', '-6': '10⁻⁶', '-8': '10⁻⁸' };
      g.cx = function (t) { return X0 + (t - 1) / (NMAX - 1) * (X1 - X0); };
      g.cy = function (v) { var L = Math.log(Math.max(v, 1e-10)) / Math.LN10; return Y0 + (0 - L) / 10 * (Y1 - Y0); };
      [0, -2, -4, -6, -8].forEach(function (L) {
        var y = g.cy(Math.pow(10, L));
        S('line', { x1: X0, x2: X1, y1: y, y2: y, 'class': 'gridline' }, csvg);
        var tt = S('text', { x: X0 - 12, y: y + 6, 'text-anchor': 'end', fill: C.ink3, 'font-size': 17, 'class': L >= -4 ? 'svg-mono' : null }, csvg);
        tt.textContent = TICK[String(L)];
      });
      [1, 10, 20, 30].forEach(function (t) {
        var tx = S('text', { x: g.cx(t), y: Y1 + 26, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'svg-mono' }, csvg); tx.textContent = t;
      });
      var yl = S('text', { x: X1, y: Y0 + 6, 'text-anchor': 'end', fill: C.ink3, 'font-size': 18 }, csvg); yl.textContent = 'change per iteration · one grid step = ×100';
      g.thr = S('line', { x1: X0, x2: X1, y1: g.cy(TOL), y2: g.cy(TOL), stroke: C.ink2, 'stroke-width': 2, 'stroke-dasharray': '7 6' }, csvg);
      var thl = S('text', { x: X0 + 10, y: g.cy(TOL) + 24, fill: C.ink2, 'font-size': 18 }, csvg); thl.textContent = 'ε = one hundred-millionth (10⁻⁸) · below this line we stop';
      g.thrL = thl;
      g.line = S('path', { d: '', fill: 'none', stroke: C.ink2, 'stroke-width': 1.5, 'stroke-opacity': 0.6 }, csvg);
      g.dots = S('g', {}, csvg);
      g.csvg = csvg;
      g.state = { k: 0, d: DAMP, run: PR };
      /* slider */
      var sl = q(el, '#sl');
      var ssvg = Comp.svg(ctx, sl, { w: 760, h: 70 });
      var SX0 = 20, SX1 = 740;
      g.sx = function (d) { return SX0 + d / 0.99 * (SX1 - SX0); };
      S('line', { x1: SX0, x2: SX1, y1: 20, y2: 20, stroke: C.line, 'stroke-width': 6, 'stroke-linecap': 'round' }, ssvg);
      g.sFill = S('line', { x1: SX0, x2: g.sx(DAMP), y1: 20, y2: 20, stroke: C.ink2, 'stroke-width': 6, 'stroke-linecap': 'round' }, ssvg);
      [0, 0.5, 0.85, 0.99].forEach(function (d) {
        S('line', { x1: g.sx(d), x2: g.sx(d), y1: 30, y2: 40, stroke: C.ink3, 'stroke-width': 2 }, ssvg);
        var t = S('text', { x: g.sx(d), y: 62, 'text-anchor': 'middle', fill: d === DAMP ? C.ink : C.ink3, 'font-size': 18, 'class': 'svg-mono' }, ssvg);
        t.textContent = String(d);
      });
      g.knob = S('circle', { cx: g.sx(DAMP), cy: 20, r: 14, fill: C.bg, stroke: C.ink, 'stroke-width': 3 }, ssvg);
      g.ssvg = ssvg; g.dv = q(el, '#dv'); g.it = q(el, '#it'); g.dl = q(el, '#dl'); g.dnote = q(el, '#dnote');
      var drag = false;
      function pick(e) {
        var p = ctx.toStage(e), r = ctx.rect(ssvg), d = (p.x - r.x - SX0) / (SX1 - SX0) * 0.99;
        d = Math.max(0, Math.min(0.99, Math.round(d * 100) / 100));
        ctx.add(function () { setD(ctx, d, true); });
      }
      ctx.on(ssvg, 'pointerdown', function (e) { drag = true; try { ssvg.setPointerCapture(e.pointerId); } catch (er) { /* ignore */ } pick(e); e.stopPropagation(); });
      ctx.on(ssvg, 'pointermove', function (e) { if (drag) pick(e); });
      ctx.on(ssvg, 'pointerup', function () { drag = false; });
      ctx.on(sl, 'click', function (e) { e.stopPropagation(); });
      renderIter(ctx, PR, 0, true);
      IDS.forEach(function (id, j) { g.W.cups[id].set(P2[j], { duration: 0 }); });   /* cups keep r(1) of s04-06 until enter() */
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      panelEnter(el, ctx);
      setCups(g.W, PR.hist[0], { duration: 0.8, delay: 0.3 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.add(g.nCard.pop(), 0.9);
        for (var k = 1; k <= 7; k++) (function (kk) { tl.call(function () { ctx.add(function () { renderIter(ctx, PR, kk); }); }, null, 0.1 + (kk - 1) * 0.42); })(k);
      }
      if (i === 2) {
        renderIter(ctx, PR, 7, true);
        for (var k2 = 8; k2 <= PR.iters; k2++) (function (kk) { tl.call(function () { ctx.add(function () { renderIter(ctx, PR, kk, false, 0.12); }); }, null, (kk - 8) * 0.1); })(k2);
        var tEnd = (PR.iters - 8) * 0.1 + 0.15;
        tl.fromTo(g.thr, { attr: { 'stroke-width': 6 }, stroke: C.ink }, { attr: { 'stroke-width': 2 }, stroke: C.ink2, duration: 0.8, ease: 'power2.out' }, tEnd);
        tl.fromTo(q(el, '#it'), { scale: 1.25, transformOrigin: '0% 70%' }, { scale: 1, duration: 0.5, ease: E.stamp }, tEnd);
      }
      if (i === 3) {
        tl.to(g.nCard.el, { autoAlpha: 0, duration: 0.3 }, 0);
        renderIter(ctx, PR, PR.iters, true);
        tl.add(ctx.count(q(el, '#r1'), 0, IT_ER, { decimals: 0, duration: 1.2 }), 0.3);
        tl.add(ctx.count(q(el, '#r2'), 0, IT_AWP, { decimals: 0, duration: 1.4 }), 0.45);
      }
      if (i === 4) {
        renderIter(ctx, PR, PR.iters, true);
        var demo = [0, 0.5, 0.99, DAMP];
        demo.forEach(function (d, k) { tl.call(function () { ctx.add(function () { setD(ctx, d, false); }); }, null, 0.5 + k * 1.1); });
      }
    },
    tags: ['thesis-example', 'calc']
  };
  /* show iteration k of a run on cups, bars, chart and counter */
  function renderIter(ctx, run, k, instant, dur) {
    var g = ctx.g, v = run.hist[Math.min(k, run.hist.length - 1)], d = dur != null ? dur : 0.32;
    IDS.forEach(function (id, j) {
      if (instant) { g.W.cups[id].set(v[j], { duration: 0 }); g.bar[j].setAttribute('width', v[j] * g.barScale); g.barT[j].textContent = f4(v[j]); }
      else {
        g.W.cups[id].set(v[j], { duration: d, ease: 'power2.inOut' });
        gsap.to(g.bar[j], { attr: { width: v[j] * g.barScale }, duration: d, ease: 'power2.inOut' });
        g.barT[j].textContent = f4(v[j]);
      }
    });
    if (g.it) g.it.textContent = String(k);
    if (g.dl) g.dl.textContent = k === 0 ? 'start: all 1/4' : 'change ' + fmtDelta(run.deltas[k - 1]);
    /* chart: points 1..k */
    var dots = g.dots; while (dots.firstChild) dots.removeChild(dots.firstChild);
    var dd = '';
    for (var t = 1; t <= k && t <= run.deltas.length; t++) {
      var x = g.cx(t), y = g.cy(run.deltas[t - 1]);
      dd += (t === 1 ? 'M' : 'L') + x.toFixed(1) + ',' + y.toFixed(1);
      var below = run.deltas[t - 1] < TOL;
      var c = S('circle', { cx: x, cy: y, r: t === k ? 6 : 4, fill: below ? C.hi : C.ink, 'fill-opacity': t === k ? 1 : 0.75 }, dots);
      if (t === k && !instant) gsap.fromTo(c, { attr: { r: 11 } }, { attr: { r: 6 }, duration: 0.3 });
    }
    g.line.setAttribute('d', dd);
  }
  function fmtDelta(v) {
    if (!(v > 0)) return '0';
    if (v >= 0.001) return fmt(v, v >= 0.1 ? 3 : 4);
    var e = Math.floor(Math.log(v) / Math.LN10), m = v / Math.pow(10, e);
    var sup = String(e).replace(/-/g, '⁻').replace(/\d/g, function (c) { return '⁰¹²³⁴⁵⁶⁷⁸⁹'.charAt(+c); });
    return fmt(m, 2) + '×10' + sup;
  }
  function setD(ctx, d, fromUser) {
    var g = ctx.g;
    var run = Math.abs(d - DAMP) < 1e-9 ? PR : iterate(IDS, EDGES, { d: d });
    g.state.d = d; g.state.run = run;
    g.dv.textContent = String(d);
    var sx = g.sx(d);
    if (fromUser) { g.knob.setAttribute('cx', sx); g.sFill.setAttribute('x2', sx); }
    else { gsap.to(g.knob, { attr: { cx: sx }, duration: 0.6, ease: E.io }); gsap.to(g.sFill, { attr: { x2: sx }, duration: 0.6, ease: E.io }); }
    renderIter(ctx, run, run.iters, !!fromUser, 0.5);                 /* dragging: follow the pointer directly */
    var nt = g.dnote;
    if (nt) nt.innerHTML = 'd = ' + d + ' → (' + run.r.map(f4).join(', ') + ') · stops after ' + run.iters + ' iterations';
  }

  Deck.section({ id: 's04-pagerank', title: 'Deriving PageRank', slides: [s1, s2, s3, s4, s5, s6, s7] });
})();
