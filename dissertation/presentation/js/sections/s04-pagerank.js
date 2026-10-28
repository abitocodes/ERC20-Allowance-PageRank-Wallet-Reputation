/* =========================================================================
   s04-pagerank — 페이지랭크 유도 (STORYBOARD.md §2, s04-01 … s04-07)

   One locked stage for the whole section: the four-node world of thesis
   Chapter 2 (Comp.smallWorld, G7) stays at the same place on all seven slides
   (data-shared="small-world"), and so does the background of the right-hand
   panel (data-shared="s04-panel", with the section counter "단계 n / 7").
   Only the panel contents and the overlays change.

   s04-01  작은 세계                    weights count up; o(u) — numbers fly from the arrows into the sums
   s04-02  무작위로 돌아다니는 사람        spinners (돌림판) next to A, B, C; P_{u,v} = w/o
   s04-03  오래 걸으면: 균형식            walker bursts into water; one pour; r_v = Σ r_u P_{u,v}
   s04-04  표로 한 번에: 이동 행렬         4×4 table; arrows fly into cells; 3D flip about the diagonal = Pᵀ
   s04-05  두 가지 문제                  leak at the dangling node (1 → 0.75 → 0.25 → 0); D ⇄ E trap
   s04-06  고치기: 감쇠 계수 d와 다시 출발  three pieces of Eq. pagerank fill r^(1) = (0.0906, 0.2323, 0.1615, 0.5156)
   s04-07  거듭제곱 반복                 23 iterations to ε = 1e-8; 57 / 94 on the real graphs; live d slider

   Numbers and sources
     weights 2, 1, 3, 1; o = 3, 3, 1, 0; d = 0.85; 0.0375 = 0.15/4; r^(1) = (0.0906, 0.2323, 0.1615, 0.5156);
     r = (0.1375, 0.2154, 0.1765, 0.4706); d·r_D/4 = 0.1000
       — thesis Ch. 2 "Worked example" (DECK_DATA.params.worked_example), status tag 논문 2장 예시
     leak totals 1, 0.75, 0.25, 0; trap (D, E) values; fixed trap D 0.4619, E 0.4226; 23 iterations;
     change values 0.531, 0.135, …; slider values — computed here in the browser (power iteration
       of Eq. pagerank on the toy graph), status tags 계산 / 예시
     d = 0.85, ε = 1e-8, I_max = 300 — DECK_DATA.params.pagerank (R§10 Protocol)
     57 (EndorseRank), 94 (AWP) iterations at T_obs — DECK_DATA.scale.revised.iterations_tobs (R§1);
       solve time = graph size (|E|, |V|) per iteration × iterations (thesis Ch. 4 benchmark), notes only
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
  var IT_ER = ITS.endorserank != null ? ITS.endorserank : 57;
  var IT_AWP = ITS.awp != null ? ITS.awp : 94;

  /* ------------------------------------------------------------ geometry of the locked stage */
  var WX = 96, WY = 236;                       /* small-world wrapper (stage px) */
  var SW = Comp.SMALL_WORLD;
  var NODE = {}; SW.nodes.forEach(function (n) { NODE[n.id] = { x: n.x, y: n.y }; });
  var IDS = ['A', 'B', 'C', 'D'];
  var EDGES = SW.edges.map(function (e) { return [e.from, e.to, e.w]; });
  var CUP_DY = 92, CUP_H = 60, CUP_MAX = 0.8;
  var WATER = C.ink;
  var STEP_NAMES = ['작은 세계', '걷는 사람', '균형식', '이동 행렬', '두 가지 문제', '고치기', '되풀이'];

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
    '.s4-gauge .lb{position:absolute;left:50%;top:-40px;transform:translateX(-50%);white-space:nowrap;font-size:22px;line-height:30px;color:var(--ink-2)}',
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
    return '<div class="s4-pbg" data-shared="s04-panel"><div class="s4-ph"><span>페이지랭크 만들기 · 단계 ' + k + ' / 7</span>' +
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

  /* spinner (돌림판): slices [{n (equal parts), label, fill, ink}] + optional outer 85/15 ring */
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

  /* vertical "전체 물" gauge (HTML) */
  function gauge(ctx, el, o) {
    var wrap = H('div', 's4-gauge', el); wrap.setAttribute('data-in', 'none');
    wrap.style.left = o.x + 'px'; wrap.style.top = o.y + 'px'; wrap.style.height = o.h + 'px';
    H('div', 'lb', wrap, '전체 물');
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
    id: 's04-01', title: '작은 세계', time: 40, steps: 2,
    notes: [
      '페이지랭크를 아주 작은 세계에서 처음부터 만들어 볼게요. 점이 네 개 있어요. A는 토큰 주인, 곧 사람의 지갑 주소(EOA)예요. B와 C는 A가 허락한 금고 계약이고, D는 두 금고가 다시 허락한 대출 풀 계약이에요. 이 예는 논문 2장의 예시와 같아요.',
      '화살표 위의 숫자는 무게예요. 무게가 클수록 화살표가 굵어요. u에서 v로 가는 화살표의 무게를 w(u, v)라고 써요. A에서 B는 2, A에서 C는 1, B에서 D는 3, C에서 D는 1이에요.',
      '한 점에서 나가는 무게를 모두 더한 값을 o라고 쓸게요. 식의 시그마는 "모두 더하기"라는 기호예요. 아래 작은 v는 v를 바꿔 가며 더한다는 뜻이에요. 그래서 A는 2와 1을 더해 3, B는 3, C는 1이에요. D는 나가는 화살표가 하나도 없어서 0이에요. 이 0이 곧 문제를 일으킬 거예요.'
    ],
    html: '<h1 class="t-h1">점 4개, 허락 화살표 4개로 [[시작]]해요</h1>' + panelBg(1) +
      '<div class="s4-pn">' +
        '<div class="s4-k">등장인물</div>' +
        '<div class="s4-cast" data-in="rise" data-stagger="0.12">' + castRow('eoa', 'A', '토큰 주인 (EOA)') + castRow('box', 'B, C', '금고 계약') + castRow('box', 'D', '대출 풀 계약') + '</div>' +
        '<div class="s4-l" data-step="1" style="margin-top:34px">화살표 위 숫자 = 화살표의 <b>무게</b> (굵기)</div>' +
        '<div class="s4-tx" data-step="1" style="font-size:28px">$w(A,B)=2,\\;\\; w(A,C)=1,\\;\\; w(B,D)=3,\\;\\; w(C,D)=1$</div>' +
        '<div id="og" data-in="none" style="margin-top:30px">' +
          '<div class="s4-tx" id="ofx"></div>' +
          '<div class="s4-note">u에서 나가는 화살표 무게를 모두 더해요 · <b class="ink">Σ</b> (시그마) = 모두 더하기</div>' +
          '<div class="s4-otab">' + orow('A', [2, 1], 3) + orow('B', [3]) + orow('C', [1]) + orow('D', [], 0) + '</div>' +
        '</div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { hidden: true, cupLabels: false });
      g.W.edges.forEach(function (A) { A.lbl = A.label; A.label = null; gsap.set(A.lbl, { autoAlpha: 0 }); });
      g.wCard = card(ctx, el, { tex: 'w(u,v)', desc: 'u에서 v로 가는 화살표의 무게', art: artArrow('2'), x: 96, y: 840 });
      g.oCard = card(ctx, el, { tex: 'o(u)', desc: 'u에서 나가는 무게의 합', art: artOut(), x: 562, y: 840 });
      g.of = Comp.formula(ctx, q(el, '#ofx'), 'o(u)=\\part{s}{\\sum_{v}} w(u,v)', { display: false });
      /* Σ card inside the panel, under the o-table */
      g.sCard = Comp.symbolCard(ctx, el, { className: 's4-sc', tex: '\\sum_{v}', x: 984, y: 878,
        desc: '시그마 = <b class="ink">모두 더하기</b><br>아래 글자 v = v를 바꿔 가며 · 예: o(A) = 2 + 1 = 3' });
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
    id: 's04-02', title: '무작위로 돌아다니는 사람', time: 40, steps: 4,
    notes: [
      '이 세계에 아무 생각 없이 돌아다니는 사람을 한 명 풀어 놓을게요. 규칙은 하나예요. 지금 서 있는 점에서 나가는 화살표 하나를 고르되, 무게가 큰 화살표를 더 자주 골라요.',
      'A 옆의 돌림판을 돌려요. 세 칸 가운데 두 칸이 B, 한 칸이 C예요. 무게 2와 1이 그대로 칸 수가 됐어요. 이번에는 B가 나와서 B로 건너가요.',
      'A의 무게 합 3 가운데 2가 B 쪽이니까, 세 번 중 두 번은 B로 가요. 이 확률을 P라고 써요. 일반적으로는 화살표의 무게를 그 점에서 나가는 무게의 합으로 나눠요.',
      '같은 방법으로 A에서 C는 3분의 1이에요. B와 C에서는 길이 하나뿐이라 무조건 D로 가요. 한 점에서 나가는 확률을 모두 더하면 언제나 1이에요. D만 예외예요. 더할 것이 없거든요.',
      'B에서 돌림판을 돌리면 D밖에 없어요. 그래서 D로 넘어왔는데, D에는 나갈 화살표가 없어서 멈춰 버려요. 그리고 B에서 D로 가는 길은 하나뿐이라, 무게가 3이어도 확률은 1이에요. 무게는 갈림길에서만 뜻이 있어요.'
    ],
    html: '<h1 class="t-h1">규칙 하나: 지금 점에서 [[나가는 화살표]] 하나를 골라요</h1>' + panelBg(2) +
      '<div class="s4-pn">' +
        '<div class="s4-L" data-in="words">굵은 화살표일수록 더 자주 골라요</div>' +
        '<div class="s4-l" data-step="1">A에서: B로 <b>3번 중 2번</b>, C로 <b>3번 중 1번</b></div>' +
        '<div id="dv" data-in="none" style="margin-top:22px"></div>' +
        '<div data-step="4" style="margin-top:22px"><div class="s4-q">D에서는 나갈 화살표가 없어요!</div>' +
        '<div class="s4-note">B → D는 하나뿐인 길이라 무게 3은 확률에 영향이 없어요</div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 0.35, cupLabels: false, dangling: true });
      g.fx = fxSvg(ctx, el);
      g.sp = makeSpinners(g.fx);
      gsap.set([g.sp.A.g, g.sp.B.g, g.sp.C.g], { autoAlpha: 0 });
      gsap.set(q(el, '#dv'), { autoAlpha: 0 });
      g.dv = Comp.derive(ctx, q(el, '#dv'), { head: '확률', lines: [
        { tex: 'P_{A,B}=\\frac{w(A,B)}{o(A)}=\\part{f}{\\frac{2}{3}}', note: 'A의 무게 합 3 가운데 2가 B 쪽 → 3번 중 2번 B로 가요', mark: 'f' },
        { tex: '\\part{g}{P_{u,v}=\\dfrac{w(u,v)}{o(u)}}', note: '일반식 · 화살표의 무게 ÷ 나가는 무게의 합', mark: 'g' },
        { tex: 'P_{A,C}=\\tfrac{1}{3},\\quad P_{B,D}=\\tfrac{3}{3}=1,\\quad P_{C,D}=\\tfrac{1}{1}=1' },
        { tex: '\\tfrac{2}{3}+\\tfrac{1}{3}=1', note: '한 점에서 나가는 확률을 모두 더하면 1 · D만 예외 (더할 것이 없어요)' }
      ] });
      g.pCard = card(ctx, el, { tex: 'P_{u,v}', desc: 'u에서 v로 갈 확률', art: artArrow('2/3', 'p'), x: 96, y: 840 });
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
    id: 's04-03', title: '오래 걸으면: 머무는 비율 → 균형식', time: 50, steps: 5,
    notes: [
      '이 사람이 아주 오래 걸으면, 각 점에 머문 시간의 비율이 일정해져요. 페이지랭크는 바로 이 비율을 그 점의 점수로 써요.',
      '사람 한 명 대신 물 1리터를 생각해 볼게요. 사람이 아주 많이 쪼개져 물방울이 됐다고 생각해도 돼요. 처음에는 네 컵에 4분의 1씩, 0.25씩 나눠 담아요. 점 v의 컵에 든 물을 r_v라고 쓰고, 이것이 그 점의 몫, 곧 점수예요.',
      '이제 한 번 부어요. 각 컵의 물을 나가는 화살표의 확률만큼 나눠 부어요. A의 물은 2대 1로 B와 C에, B와 C의 물은 모두 D로 가요. 그런데 D의 물은 나갈 길이 없어서 흘러 버려요. 이 문제는 두 장 뒤에 다시 봐요.',
      '이렇게 계속 부으면 언젠가 컵마다 물의 양이 더는 바뀌지 않는 때가 와요. 이것을 균형이라고 해요. 물이 멈춘 게 아니에요. 물은 계속 흐르지만, 나가는 만큼 다시 들어와서 양이 그대로예요. 그래서 균형에서는 내 컵의 물이 나에게 들어오는 물과 같아요. B에는 A의 3분의 2, C에는 A의 3분의 1, D에는 B와 C의 물이 모두 들어와요. 아무도 A를 가리키지 않으니 A는 0이에요.',
      '한 줄로 쓰면 이래요. 내 몫은 나를 가리키는 점들이 나눠 주는 몫의 합이에요. 시그마 아래의 u 화살표 v는 v를 가리키는 점 u만 더한다는 뜻이에요. 이것을 균형식이라고 해요.',
      '그런데 이 식을 끝까지 풀어 보면 이상해요. A가 0이니까 B는 0 곱하기 3분의 2라서 0, C도 0이에요. 그러면 D는 0 더하기 0이라서 0이에요. 균형식의 답은 "모두 0"뿐이에요. 물이 D에서 전부 새어 버린다는 뜻이에요. 다음 두 장에서 이 문제를 고쳐요.'
    ],
    html: '<h1 class="t-h1">오래 걸으면, 점마다 [[머무는 비율]]이 정해져요</h1>' + panelBg(3) +
      '<div class="s4-pn">' +
        '<div class="s4-L" data-in="words">그 비율이 그 점의 점수 <b>r</b>이에요</div>' +
        '<div class="s4-l" data-step="1">생각을 바꿔요: 사람 한 명 → <b>물 1리터</b>를 나눠 붓기</div>' +
        '<div id="dv" data-in="none" style="margin-top:20px"></div>' +
        '<div data-step="4" style="margin-top:18px"><div class="s4-key">내 몫 = 나를 가리키는 점들이 나눠 주는 몫의 합</div><div id="gen" class="s4-tx" style="margin-top:10px"></div></div>' +
        '<div data-step="5" style="margin-top:12px"><div class="s4-q">그런데 풀어 보면: <span id="zch">$r_A=0\\;\\Rightarrow\\;r_B=r_C=0\\;\\Rightarrow\\;r_D=0+0=0$</span></div>' +
          '<div class="s4-note">균형식의 답은 <b class="ink">‘모두 0’</b>뿐 — 물이 D에서 전부 새어 버려요</div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 0.35, cupLabels: false, dangling: true });
      g.PL = Particles(ctx, el);
      g.dv = Comp.derive(ctx, q(el, '#dv'), { head: '균형: 물은 계속 흘러도 컵마다 양은 그대로 → 컵의 물 = 들어오는 물', lines: [
        { tex: 'r_B=r_A\\cdot\\tfrac{2}{3}', display: false, note: 'B로 들어오는 물: A의 몫 중 2/3' },
        { tex: 'r_C=r_A\\cdot\\tfrac{1}{3}', display: false },
        { tex: 'r_D=r_B\\cdot 1+r_C\\cdot 1', display: false },
        { tex: 'r_A=0', display: false, note: '아무도 A를 가리키지 않아요' }
      ] });
      g.gen = Comp.formula(ctx, q(el, '#gen'), 'r_v=\\sum_{\\part{s}{u:\\,u\\to v}} r_u\\,\\frac{w(u,v)}{o(u)}=\\sum_{u} r_u\\,P_{u,v}');
      g.rCard = card(ctx, el, { tex: 'r_v', desc: '점 v의 몫 (점수) = 컵의 물', art: artCups(), x: 96, y: 840 });
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
    id: 's04-04', title: '표로 한 번에: 이동 행렬', time: 45, steps: 4,
    notes: [
      '점이 수백만 개가 되면 식을 하나하나 쓸 수 없으니, 갈림길을 표 하나에 모아요. 가로줄은 출발하는 점, 세로칸은 도착하는 점이에요.',
      '칸 안에는 그 화살표를 탈 확률을 적어요. A 줄에는 B 칸에 3분의 2, C 칸에 3분의 1. B와 C 줄에는 D 칸에 1. 화살표가 없는 칸은 0이에요. 이 표가 이동 행렬 P예요.',
      'D의 줄은 비어 있어요. 나가는 화살표가 없는 점이라서 그래요. 이런 점을 매달린 점이라고 불러요.',
      '이 표를 대각선을 축으로 뒤집을게요. 뒤집은 표를 P 전치, 기호로 P 위에 T를 붙여 써요. 이제 가로줄 하나가 그 점으로 들어오는 쪽을 모아 보여 줘요.',
      '몫 네 개를 세로로 세운 목록을 r이라고 해요. 뒤집은 표를 r에 곱하면, 도착점마다 들어오는 몫을 한꺼번에 더한 것이 돼요. D 줄을 보면 0 곱하기 r_A, 1 곱하기 r_B, 1 곱하기 r_C, 0 곱하기 r_D를 더해서 r_B 더하기 r_C예요. 앞 장에서 손으로 쓴 균형식과 똑같아요. 그래서 한 번 붓기가 곧 표 곱하기 한 번이에요.'
    ],
    html: '<h1 class="t-h1">갈림길 [[표]] P</h1>' + panelBg(4) +
      '<div class="s4-cap" id="cap" style="left:984px;top:268px;width:800px"><span id="capt">가로줄 = <b>출발</b>하는 점 · 세로칸 = <b>도착</b>하는 점 · 칸 안 = 탈 확률</span></div>' +
      '<div class="s4-mxw" id="mxw" data-in="none"><div class="s4-flip" id="flip"><div class="s4-face front" id="ff"></div><div class="s4-face back" id="fb"></div></div></div>' +
      '<div class="abs" data-step="2" data-step-out="3" data-in="left" style="left:1404px;top:' + (330 + 44 + 3 * 86 + 26) + 'px"><span class="s4-pill">매달린 점 · 나가는 화살표가 없어요</span></div>' +
      '<div class="s4-vec" id="vec" data-in="none"></div>' +
      '<div class="s4-vec" id="res" data-in="none"></div>' +
      '<div class="abs" id="eqs" style="left:984px;top:742px;width:800px">' +
        '<div class="s4-tx" data-step="1" data-in="fade">$P_{u,v}=\\begin{cases} w(u,v)/o(u) & o(u)>0\\text{ 이면}\\\\ 0 & \\text{그 밖에는}\\end{cases}$ <span class="source" style="margin-left:14px">논문 식 (3.2)</span></div>' +
        '<div data-step="4" style="margin-top:6px"><div class="s4-tx">$\\mathbf r^{(t+1)}=P^{\\top}\\mathbf r^{(t)}$ <span class="s4-note" style="margin-left:12px">(t) = t번째 붓기 뒤</span></div>' +
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
      g.rCard = card(ctx, el, { tex: '\\mathbf r', desc: '몫 네 개를 세로로 세운 목록 (벡터)', art: artVec(), x: 96, y: 836 });
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
        tl.add(Comp.swap(ctx, q(el, '#capt'), 'P<sup>T</sup> · 가로줄 = <b>도착</b>하는 점 = 그 점으로 <b>들어오는 쪽</b> · 세로칸 = 출발'), 0.4);
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
    id: 's04-05', title: '두 가지 문제: 새는 물과 함정', time: 45, steps: 3,
    notes: [
      '균형식을 그대로 되풀이해서 돌리면 문제가 두 가지 생겨요. 다시 네 컵에 0.25씩 담고 시작해 볼게요.',
      '첫째, 매달린 점 D에 들어간 물은 나갈 곳이 없어서 사라져요. 실제로 계산해 보면 전체 물이 1에서 0.75, 0.25, 0으로 줄어요. 세 번 붓고 나면 물이 하나도 남지 않아요.',
      '둘째, 서로만 가리키는 두 점이 있으면, 거기로 들어간 물이 영원히 갇혀요. 설명을 위해 D와 서로 허락하는 점 E를 하나 더했어요. 점이 다섯이니 처음에는 0.2씩이에요. 두 번 부으면 물이 모두 D와 E로 들어가고, 그 뒤로는 0.4와 0.6을 오가며 출렁여요. 값이 멈추지 않아요. 수렴하지 않는다고 해요.',
      'E는 설명을 위해 더한 점이에요. 이렇게 서로 허락하는 주소 모양은 10번째 부분, 공격 비용 이야기에서 다시 나와요.'
    ],
    html: '<h1 class="t-h1">문제 1 · 매달린 점에서 물이 [[새요]]</h1>' + panelBg(5) +
      '<div class="s4-pn">' +
        '<div class="t-h2">문제 2 · 함정</div>' +
        '<div class="s4-l" data-step="2">서로만 가리키는 두 점 (D ⇄ E)이 물을 모두 가둬요</div>' +
      '</div>' +
      '<div class="abs" data-step="2" data-in="fade" style="left:984px;top:790px;width:800px">' +
        '<div class="s4-chain"><span class="ink-2" style="font-size:24px">(D, E)</span><span class="v" id="tv">(0.2, 0.2)</span></div>' +
        '<div class="s4-q" style="margin-top:6px">멈추지 않아요 (수렴하지 않음)</div>' +
      '</div>' +
      '<div class="abs s4-note" data-step="3" style="left:984px;top:920px;width:800px">E는 설명용으로 더한 점이에요 · 서로 허락하는 두 주소 — <b class="ink">10 · 공격 비용</b>에서 다시 만나요</div>' +
      '<div class="abs" style="left:96px;top:846px;width:800px">' +
        '<div class="s4-tx" style="font-size:26px">$\\mathbf r^{(t+1)}=P^{\\top}\\mathbf r^{(t)},\\quad \\mathbf r^{(0)}=(0.25,\\,0.25,\\,0.25,\\,0.25)$</div>' +
        '<div class="s4-chain" id="tot" style="margin-top:6px"><span class="ink-2" style="font-size:24px">전체 물 $\\textstyle\\sum_v r^{(t)}_v$</span>' +
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
    id: 's04-06', title: '고치기: 감쇠 계수 d와 다시 출발', time: 60, steps: 7,
    notes: [
      '두 문제를 한꺼번에 고치는 방법이 감쇠 계수 d와 다시 출발이에요.',
      '걷는 사람은 100번 중 85번은 화살표를 따라가고, 15번은 아무 점으로나 순간 이동해요. 이 0.85를 감쇠 계수 d라고 해요. 돌림판 바깥 고리가 그 비율이에요. 매달린 점 D에 도착하면 언제나 순간 이동해요. 그래서 D에서는 네 점 모두로, D 자신까지 점선이 퍼져요.',
      '지금 몫이 모두 0.25라고 하고, 새 몫을 세 조각으로 채워 볼게요. 첫째 조각은 다시 출발 몫이에요. 매번 모든 점에 고르게, 0.15를 4로 나눈 0.0375씩 내려요. 다시 출발할 곳의 비율을 π라고 쓰는데, 엔도스랭크는 모든 점에 똑같이 4분의 1이에요. |V|는 점의 개수예요.',
      '둘째 조각은 화살표를 따라 온 몫이에요. 앞에서 만든 균형식과 같지만 0.85를 곱해서 물줄기가 조금 가늘어요.',
      '셋째 조각은 매달린 점에서 모아 다시 나눠 주는 몫이에요. D의 물을 구름처럼 모아서 모든 점에 고르게 내려요. 1_dang은 매달린 점이면 1, 아니면 0인 목록이에요. r 위에 붙은 T는 세로 목록을 가로로 눕힌다는 뜻이고, 가로 목록과 세로 목록을 곱하면 칸끼리 곱해서 모두 더해요. 0 곱하기 0.25가 세 번, 1 곱하기 0.25가 한 번이라서 합은 0.25, 곧 r_D예요. 매달린 점의 몫만 남는 거예요. 여기에 0.85와 4분의 1을 곱하면 0.0531이에요. 세 조각을 다 채우면 논문 2장의 r(1)과 똑같은 값이 돼요.',
      '점 하나씩 쓰면 논문 2장의 식이 돼요. 앞에서 쓴 글자 u, v 그대로 썼어요. 논문은 같은 식을 i, j로 쓰고, E는 화살표 전체를 뜻해요. A를 가리키는 화살표는 없으니까 A의 몫은 D에서 모아 온 몫과 다시 출발 몫뿐이에요. 0.2125 곱하기 r_D 더하기 0.0375예요.',
      '세 조각을 더하면 전체 물이 언제나 1로 유지돼요. 다시 출발 몫이 1 빼기 d를 가져가고, 나머지 두 조각이 d를 나눠 갖기 때문이에요. 지금 예에서는 0.15, 0.6375, 0.2125를 더해 딱 1이에요. 물이 새지 않아요.',
      '앞 장의 함정도 고친 규칙으로 다시 돌려 볼게요. 갇혔던 물이 조금씩 빠져나와 출렁임이 잦아들고 값이 멈춰요. D는 0.4619, E는 0.4226이에요. 지금까지 만든 식이 논문 3장의 페이지랭크 식 그대로예요.'
    ],
    html: '<h1 class="t-h1">100번 중 85번은 화살표를, 15번은 [[아무 데로나]]</h1>' + panelBg(6) +
      '<div class="s4-pn">' +
        '<div class="s4-rules" id="rules" data-in="none">' +
          '<div class="s4-rule"><span class="n" id="n85">85</span><span class="t">감쇠 계수 <b>d = 0.85</b> · 화살표를 따라갈 확률</span></div>' +
          '<div class="s4-rule"><span class="n c-hi" id="n15">15</span><span class="t"><b>1 − d = 0.15</b> · 아무 점으로나 순간 이동 (다시 출발)</span></div>' +
          '<div class="s4-l" style="padding-left:114px">매달린 점에서는: 언제나 순간 이동</div>' +
        '</div>' +
        '<div class="s4-hero" id="hero" data-step="2" data-in="fade" style="margin-top:30px"></div>' +
        '<div class="s4-plabels" id="pls" data-step="2" data-in="fade"></div>' +
        '<div class="s4-slot" id="slot" style="margin-top:20px">' +
          '<div data-step="2" data-step-out="3"><div class="s4-l">지금 몫 = 모두 0.25 → 새 몫을 <b>세 조각</b>으로 채워요</div>' +
            '<div class="s4-tx"><span class="s4-circ">1</span>$(1-d)\\,\\pi_v=0.15\\times\\tfrac14=0.0375$</div><div class="s4-note">모든 점에 똑같이 내리는 다시 출발 몫</div></div>' +
          '<div data-step="3" data-step-out="4"><div class="s4-tx"><span class="s4-circ">2</span>$d\\,P^{\\top}\\mathbf r^{(t)}$</div><div class="s4-note">화살표를 따라 온 몫 · 균형식에 0.85를 곱해 조금 가늘어요</div>' +
            '<div class="s4-tx" style="font-size:26px">$\\text{예: } 0.85\\times0.25\\times\\tfrac23=0.1417\\;(A\\to B)$</div></div>' +
          '<div data-step="4" data-step-out="5"><div class="s4-tx"><span class="s4-circ">3</span>$d\\,\\bigl(\\mathbf r^{(t)\\top}\\mathbf 1_{\\mathrm{dang}}\\bigr)\\,\\boldsymbol\\pi=d\\,r_D\\,\\tfrac14$</div>' +
            '<div class="s4-note">매달린 점들이 가진 몫의 합을 모아 다시 고르게 나눠요 · 여기서는 $r_D$ 하나</div>' +
            '<div class="s4-note" style="margin-top:10px">$\\mathbf r^{(t)\\top}\\mathbf 1_{\\mathrm{dang}}$ = <b class="ink">칸끼리 곱해 더하기</b> (매달린 점 몫만 남아요)</div>' +
            '<div class="s4-tx" id="dotp" style="font-size:24px;line-height:36px;margin-top:4px"></div>' +
            '<div class="s4-tx" style="font-size:26px">$0.85\\times0.25\\times\\tfrac14=0.0531$ · 새 몫 = $(0.0906,\\,0.2323,\\,0.1615,\\,0.5156)$</div></div>' +
          '<div data-step="5" data-step-out="6"><div class="s4-note">점 하나씩 쓰면 · 논문 식 (2.3)</div>' +
            '<div class="s4-tx" style="font-size:28px">$$r_v=d\\!\\!\\sum_{u:\\,u\\to v}\\! r_u\\,\\frac{w(u,v)}{o(u)}+\\frac{d}{|V|}\\sum_{u:\\,o(u)=0}\\! r_u+\\frac{1-d}{|V|}$$</div>' +
            '<div class="s4-note">논문은 같은 식을 $i\\to j$, $w_{ij}$, $o_i$로 써요 ($i, j$ = $u, v$ · $E$ = 화살표 전체)</div>' +
            '<div class="s4-note">A의 줄: 아무도 A를 가리키지 않아서 첫 항은 0</div>' +
            '<div class="s4-tx">$r_A=\\tfrac{0.85}{4}\\,r_D+\\tfrac{0.15}{4}=0.2125\\,r_D+0.0375$</div></div>' +
          '<div data-step="6" data-step-out="7"><div class="s4-L">물이 새지 않아요</div>' +
            '<div class="s4-tx" style="font-size:26px">$$\\sum_j r^{(t+1)}_j=(1-d)+d\\!\\!\\sum_{\\text{안 매달린 }i}\\!\\! r^{(t)}_i+d\\!\\!\\sum_{\\text{매달린 }i}\\!\\! r^{(t)}_i=(1-d)+d=1$$</div>' +
            '<div class="s4-tx" style="font-size:28px">$\\text{지금 예: } 0.15+0.6375+0.2125=1$</div></div>' +
          '<div data-step="7"><div class="s4-L">함정도 풀려요</div><div class="s4-note" id="trapv">D ⇄ E의 출렁임이 잦아들고 값이 멈춰요</div></div>' +
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
      g.pl = [['1', '다시 출발 몫'], ['2', '화살표를 따라 온 몫'], ['3', '매달린 점 몫']].map(function (p) { return H('span', 'pl', pls, '<i>' + p[0] + '</i>' + p[1]); });
      g.cards = [
        card(ctx, el, { tex: '\\boldsymbol\\pi', desc: '다시 출발할 곳의 비율<br>엔도스랭크는 모두 1/|V|', x: 96 }),
        card(ctx, el, { tex: '|V|', desc: '점의 개수<br>(여기서는 4)', x: 520 }),
        card(ctx, el, { tex: '\\mathbf 1_{\\mathrm{dang}}', desc: '매달린 점이면 1, 아니면 0<br>여기서는 (0, 0, 0, 1)', x: 96 })
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
        tl.call(function () { q(el, '#trapv').innerHTML = '출렁임이 잦아들고 값이 멈춰요 · D <b class="ink">' + f4(fin[3]) + '</b>, E <b class="ink">' + f4(fin[4]) + '</b>'; }, null, 1.0 + frames.length * 0.36);
      }
    },
    tags: function (st) { return st >= 7 ? ['thesis-example', 'calc', 'example'] : ['thesis-example']; }
  };

  /* ================================================================ s04-07 */
  var CH = { x: 0, y: 0, w: 796, h: 200 };                                   /* change chart (panel-local) */
  var s7 = {
    id: 's04-07', title: '되풀이하면 멈춰요: 거듭제곱 반복', time: 60, steps: 4,
    notes: [
      '실제로는 이 식을 한 번에 풀지 않고, 같은 계산을 되풀이해요. 이것을 거듭제곱 반복이라고 해요. 처음에는 모든 점에 4분의 1씩 줘요.',
      '식을 한 번 적용하면 D 쪽으로 몫이 기울어요. A는 0.0375에 0.2125 곱하기 0.25를 더해서 0.0906이 돼요. 얼마나 바뀌었는지는 칸마다 차이의 크기를 모두 더해서 재요. 빼기 표시는 떼고 크기만 더해요. 이것을 두 줄 막대 기호로 써요. 첫 번에는 0.531이에요. 오른쪽 그래프의 점이 그 변화량이에요. 세로 눈금은 한 칸 내려갈 때마다 100분의 1로 작아져요. 1, 0.01, 0.0001, 100만분의 1, 1억분의 1이에요.',
      '되풀이할수록 바뀌는 양이 줄어들고, 23번째에 변화량이 1억분의 1보다 작아져서 멈춰요. 이 기준을 엡실론이라고 써요. 아무리 길어도 300번에서는 멈추게 정해 두었어요. 최종 순서는 D, B, C, A예요. D는 두 금고에게서 보증을 받고, 그 금고들도 A에게서 보증을 받았기 때문이에요. A의 몫 0.1375는 다시 출발 몫 0.0375와 D에서 모아 온 0.1000을 더한 값이에요.',
      '실제 허락 그래프에서는 ' + IT_ER + '번, 송금 그래프에서는 ' + IT_AWP + '번 만에 멈췄어요. 한 번 되풀이할 때 화살표 하나마다 곱셈 한 번을 하니까, 화살표가 많은 그래프일수록 한 번에 걸리는 시간이 길어요. 그래서 전체 시간은 그래프의 크기와 되풀이 횟수가 함께 정해요. 이것은 10번째 부분에서 다시 나와요.',
      'd를 직접 바꿔 볼게요. d가 0이면 화살표를 전혀 따라가지 않아서 모두 4분의 1이에요. d가 커질수록 화살표가 중요해져서 D가 커지고 A가 작아지고, 멈추기까지 되풀이도 많아져요. 이 값들은 브라우저가 그 자리에서 계산한 거예요.'
    ],
    html: '<h1 class="t-h1">같은 계산을 [[되풀이]]하면 값이 멈춰요</h1>' + panelBg(7) +
      '<div class="s4-pn" style="height:auto">' +
        '<div class="s4-iter"><span class="k">거듭제곱 반복</span><span class="t" id="it">0</span><span class="k">번</span><span class="dl" id="dl">시작: 모두 1/4</span></div>' +
        '<div id="bars" data-in="none" style="position:relative;height:196px;margin-top:8px"></div>' +
        '<div id="chart" data-in="none" style="position:relative;height:210px;margin-top:6px"></div>' +
        '<div class="s4-slot" id="slot" style="min-height:220px;margin-top:6px">' +
          '<div data-step="1" data-step-out="2"><div class="s4-tx" style="font-size:26px">$r^{(1)}_A=0.0375+0.2125\\times0.25=0.0906$</div>' +
            '<div class="s4-tx" style="font-size:26px">$\\lVert\\mathbf r^{(1)}-\\mathbf r^{(0)}\\rVert_1=0.1594+0.0177+0.0885+0.2656=0.531$</div>' +
            '<div class="s4-note">변화량 = 칸마다 차이의 크기(부호 떼기)를 모두 더한 값 · 기호 $\\lVert\\;\\rVert_1$</div></div>' +
          '<div data-step="2" data-step-out="3"><div class="s4-l"><b>23번 뒤</b>: (0.1375, 0.2154, 0.1765, 0.4706) — <b>D, B, C, A</b> 순</div>' +
            '<div class="s4-l">$\\lVert\\mathbf r^{(t+1)}-\\mathbf r^{(t)}\\rVert_1<\\varepsilon$이면 멈춰요 · 최대 $I_{\\max}=300$번</div>' +
            '<div class="s4-note">$\\varepsilon$ = 1억분의 1 ($10^{-8}$) · 변화량이 이보다 작으면 거의 안 바뀐 거예요</div>' +
            '<div class="s4-note">A의 몫 = 다시 출발 0.0375 + D에서 모아 온 $d\\,r_D/4=0.1000$</div></div>' +
          '<div data-step="3" data-step-out="4"><div class="s4-note">실제 그래프에서는 (수정 분석, T<sub>obs</sub>)</div><div class="s4-real">' +
            '<div class="it"><span class="n c-allow" id="r1">' + IT_ER + '</span><span class="k">엔도스랭크 · 허락 그래프</span></div>' +
            '<div class="it"><span class="n c-xfer" id="r2">' + IT_AWP + '</span><span class="k">AWP · 송금 그래프</span></div></div>' +
            '<div class="s4-note">한 번 = 화살표마다 곱셈 한 번 → 시간은 <b class="ink">그래프 크기와 되풀이 횟수</b>로 정해져요</div></div>' +
          '<div data-step="4"><div class="s4-l">d를 바꿔 보세요 (왼쪽 아래)</div><div class="s4-note" id="dnote">값은 브라우저가 그 자리에서 계산해요 · d = 0이면 모두 0.25</div></div>' +
        '</div>' +
      '</div>' +
      '<div class="s4-slider no-advance" id="sl" data-step="4" data-in="fade"><div class="lb">d = <b id="dv">0.85</b> <span class="ink-3" style="font-size:20px;margin-left:10px">끌어서 바꾸기 · 계산</span></div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = makeWorld(ctx, el, { cupAlpha: 1, cups: P2, dangling: true });
      g.nCard = card(ctx, el, { tex: '\\lVert\\,\\square\\,\\rVert_1', desc: '칸마다 크기(부호 떼기)를 모두 더하기<br>예: |−0.1594| = 0.1594', x: 96 });
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
      var TICK = { '0': '1', '-2': '0.01', '-4': '0.0001', '-6': '100만분의 1', '-8': '1억분의 1' };
      g.cx = function (t) { return X0 + (t - 1) / (NMAX - 1) * (X1 - X0); };
      g.cy = function (v) { var L = Math.log(Math.max(v, 1e-10)) / Math.LN10; return Y0 + (0 - L) / 10 * (Y1 - Y0); };
      [0, -2, -4, -6, -8].forEach(function (L) {
        var y = g.cy(Math.pow(10, L));
        S('line', { x1: X0, x2: X1, y1: y, y2: y, 'class': 'gridline' }, csvg);
        var tt = S('text', { x: X0 - 12, y: y + 6, 'text-anchor': 'end', fill: C.ink3, 'font-size': 17, 'class': L >= -4 ? 'svg-mono' : null }, csvg);
        tt.textContent = TICK[String(L)];
      });
      [1, 10, 20, 30].forEach(function (t) {
        var tx = S('text', { x: g.cx(t), y: Y1 + 26, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'svg-mono' }, csvg); tx.textContent = t === 30 ? '30번' : t;
      });
      var yl = S('text', { x: X1, y: Y0 + 6, 'text-anchor': 'end', fill: C.ink3, 'font-size': 18 }, csvg); yl.textContent = '변화량 · 눈금 한 칸 = 100배';
      g.thr = S('line', { x1: X0, x2: X1, y1: g.cy(TOL), y2: g.cy(TOL), stroke: C.ink2, 'stroke-width': 2, 'stroke-dasharray': '7 6' }, csvg);
      var thl = S('text', { x: X0 + 10, y: g.cy(TOL) + 24, fill: C.ink2, 'font-size': 18 }, csvg); thl.textContent = 'ε = 1억분의 1 (10⁻⁸) · 이 선 아래로 내려가면 멈춰요';
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
    if (g.dl) g.dl.textContent = k === 0 ? '시작: 모두 1/4' : '변화량 ' + fmtDelta(run.deltas[k - 1]);
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
    if (nt) nt.innerHTML = 'd = ' + d + ' → (' + run.r.map(f4).join(', ') + ') · ' + run.iters + '번 만에 멈춰요';
  }

  Deck.section({ id: 's04-pagerank', title: '페이지랭크 유도', slides: [s1, s2, s3, s4, s5, s6, s7] });
})();
