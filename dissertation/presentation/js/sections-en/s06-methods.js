/* =========================================================================
   s06-methods — Four scores (STORYBOARD.md §2, s06-01 … s06-05)
   s06-01  EndorseRank                  (small world turns amber, 4-line summary, powers-of-ten
                                        pull-back: the small world becomes one dot of the real graph)
   s06-02  AWP and raw-degree baselines (transfer graph with activeness halos; tally bars count
                                        distinct owners / senders; "can PageRank clear the bar?")
   s06-03  C-PR: mixing the two rows    (two 100 % row bars squash by λ and 1−λ into one mixed row;
                                        dial sweep; one-layer node renormalized by D_λ; final formula)
   s06-04  Turning λ (key scene)        (three.js: 15,107 contracts, height = C-PR percentile, shadows on
                                        the two back walls, five λ values, plain τ meters, draggable dial)
   s06-05  S-PR                         (teleport rain follows the allowance halos; two post hoc
                                        verdicts in words — the numbers wait for s07/s08)

   Numbers and sources (revised digest = R, experiments/data/3-published-results-for-thesis/revised-usd/results_digest.md)
     6,221,665 nodes / 11,210,114 edges   R§1 graph.allowance.nodes / .edges  (DECK_DATA.results.revised.same_window.graph)
     d = 0.85                              params.pagerank.d; R§10 protocol
     λ table (s06-04), τ_b [95% CI]        R§2 per_proxy.cpr_l{0,25,50,75,100}.in_degree / .in_approve_degree
     zeros 2,670 / 80 / 80 / 80 / 523      R§4 ties.cpr_l*.zeros (= graph.cohort_outside_transfer / _both / _allowance)
     S-PR −0.001 [−0.004, 0.002]           R§6 contrasts_after[2] (S-PR − C-PR(λ=0), new transfer senders)
     S-PR −0.051 [−0.066, −0.038]          R§6 contrasts_after[1] (S-PR − C-PR(λ=1), new approval pairs)
     λ = 0.5 primary, 0.25 / 0.75          params.coupled (configuration of 9 Oct 2026 = analysis plan)
   The τ strings are copied from the digest: DECK_DATA keeps 4 significant digits, and a
   value such as 0.2615 would round to 0.261 in JavaScript while the digest prints 0.262.
   Point positions in s06-04 come from DECK_DATA.contracts (cohort_scores parquet).
   Illustrations: s06-01 B/C/D badges = thesis Ch. 2 worked example (stationary vector);
   s06-01 constellation, s06-02 graphs, s06-03 row bars (20,000/500 USD allowances; 1,000 USD
   today, 300 USD 180 days ago, σ(0) = 0.8581) and s06-05 graph are examples.
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt;
  var DATA = window.DECK_DATA || {};
  var NS = 'http://www.w3.org/2000/svg';

  /* ------------------------------------------------------------ data (with digest fallbacks) */
  var GA = { nodes: 6221665, edges: 11210114 };
  try {
    var ga = DATA.results.revised.same_window.graph.allowance;
    if (ga.nodes) GA.nodes = ga.nodes; if (ga.edges) GA.edges = ga.edges;
  } catch (e) { /* digest values above */ }
  var DAMP = ((DATA.params || {}).pagerank || {}).d || 0.85;
  /* s06-04: τ_b with the transfer in-degree and the in-approve degree, per λ (R§2 per_proxy) */
  var LAM = [
    { v: 0,    key: 'cpr_l0',   d: '0.689 [0.682, 0.697]', a: '0.262 [0.250, 0.273]', zeros: 2670 },
    { v: 0.25, key: 'cpr_l25',  d: '0.390 [0.379, 0.402]', a: '0.495 [0.486, 0.504]', zeros: 80 },
    { v: 0.5,  key: 'cpr_l50',  d: '0.369 [0.358, 0.381]', a: '0.511 [0.503, 0.520]', zeros: 80 },
    { v: 0.75, key: 'cpr_l75',  d: '0.347 [0.336, 0.359]', a: '0.523 [0.515, 0.532]', zeros: 80 },
    { v: 1,    key: 'cpr_l100', d: '0.183 [0.171, 0.195]', a: '0.654 [0.647, 0.660]', zeros: 523 }
  ];
  /* s06-05: W0 post hoc contrasts (R§6 contrasts_after[2], [1]) */
  var SPR_SEND = '−0.001 [−0.004, 0.002]', SPR_APPR = '−0.051 [−0.066, −0.038]';

  function nums(s) { return String(s).replace(/−/g, '-').match(/-?\d+(?:\.\d+)?/g).map(Number); }
  function mfmt(v, d) { return fmt(v, d).replace(/^-/, '−'); }
  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function q(el, sel) { return el.querySelector(sel); }
  /* A data-shared element is skipped by the generic entry: when there is no flight from the
     previous slide (deep link, coming back from a slide without it), bring it in here. */
  function settleShared(ctx, el, key) {
    var hadPrev = !!(ctx.prev && ctx.prev.rect && ctx.prev.rect(key));
    if (!hadPrev) {
      if (!ctx.instant && !ctx.reduced) ctx.gsap.fromTo(el, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: 0.15 });
    }
    return hadPrev;
  }

  /* ------------------------------------------------------------ section styles */
  var CSS = [
    /* s06-01 */
    '.s6-zoom{overflow:hidden;border-radius:24px}',
    '.s6-zoom canvas{-webkit-mask-image:radial-gradient(ellipse 72% 72% at 50% 46%,#000 62%,transparent 100%);mask-image:radial-gradient(ellipse 72% 72% at 50% 46%,#000 62%,transparent 100%)}',
    '.s6-zoom .small-world{z-index:2}',
    '.s6-swdot{position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:2.5px solid var(--c-allow);box-shadow:0 0 18px rgba(245,180,60,.75);z-index:3}',
    '.s6-swlab{position:absolute;white-space:nowrap;font-size:22px;line-height:30px;color:var(--ink);z-index:3;background:rgba(10,13,20,.82);padding:6px 14px 6px 12px;border-radius:12px;border:1px solid var(--line)}',
    '.s6-swlab small{display:block;font-size:17px;line-height:24px;color:var(--ink-3)}',
    '.s6-readout{display:grid;grid-template-columns:auto auto auto;column-gap:14px;row-gap:2px;align-items:baseline;padding:14px 20px;border-radius:16px;background:rgba(10,13,20,.78);border:1px solid var(--line);z-index:4}',
    '.s6-readout .k{font-size:20px;color:var(--ink-3)}',
    '.s6-readout .a{font-family:var(--font-mono);font-size:22px;color:var(--ink-3);letter-spacing:0}',
    '.s6-readout .v{font-size:34px;line-height:44px;font-weight:700;color:var(--c-allow);font-variant-numeric:tabular-nums;min-width:200px}',
    '.s6-fcard{background:var(--bg-2);border-radius:24px;padding:24px 30px 22px;border:1px solid var(--line)}',
    '.s6-fcard .hd{font-size:18px;line-height:24px;color:var(--ink-3);margin-bottom:6px}',
    '.s6-fcard .formula .katex{font-size:34px}',
    '.s6-fcard .nt{margin-top:8px;font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s6-sum .ln{display:flex;gap:20px;align-items:flex-start;margin-bottom:26px}',
    '.s6-sum .no{flex:0 0 auto;width:40px;height:40px;border-radius:20px;border:2px solid var(--c-allow);color:var(--c-allow);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:22px;margin-top:2px}',
    '.s6-sum .tx{font-size:30px;line-height:42px;font-weight:600}',
    '.s6-sum .tx small{display:block;font-size:22px;line-height:32px;font-weight:500;color:var(--ink-2)}',
    '.s6-caution{display:flex;gap:16px;align-items:flex-start;padding:16px 22px;border-radius:16px;background:var(--c-allow-soft);font-size:24px;line-height:36px;color:var(--ink)}',
    '.s6-caution svg{flex:0 0 auto;width:30px;height:30px;margin-top:3px}',
    /* s06-02 */
    '.s6-panel{border-radius:24px;background:rgba(16,21,31,.6);border:1px solid #2C3546}',
    '.s6-panel > .hd{position:absolute;left:36px;top:26px;font-size:40px;line-height:52px;font-weight:700;letter-spacing:-.02em}',
    '.s6-panel > .hd small{font-size:22px;font-weight:500;color:var(--ink-3);margin-left:12px;letter-spacing:0}',
    '.s6-panel > .sb{position:absolute;left:36px;top:84px;font-size:26px;line-height:38px;color:var(--ink-2)}',
    '.s6-panel > svg{position:absolute;overflow:visible}',
    '.s6-legend{position:absolute;left:36px;right:30px;font-size:22px;line-height:34px;color:var(--ink-2)}',
    '.s6-defs{position:absolute;left:36px;right:30px}',
    '.s6-defs .d{display:flex;align-items:baseline;gap:18px;margin-bottom:10px}',
    '.s6-defs .d .k{flex:0 0 206px;font-size:22px;line-height:32px;color:var(--c-deg);font-weight:600}',
    '.s6-defs .d .katex{font-size:27px}',
    '.s6-defs .d .w{font-size:25px;line-height:32px;color:var(--ink)}',
    '.s6-defs .d .w b{font-weight:700;color:var(--ink)}',
    '.s6-defs .d .w .katex{font-size:26px}',
    '.s6-defs .mi{font-size:18px;line-height:26px;color:var(--ink-3);margin-top:4px}',
    '.s6-bottom{font-size:30px;line-height:44px;font-weight:600}',
    '.s6-chip{position:absolute;padding:6px 16px;border-radius:18px;font-size:22px;line-height:30px;font-weight:700;background:var(--bg-3);border:2px solid currentColor;white-space:nowrap}',
    /* s06-03 */
    '.s6-lbl{position:absolute;white-space:nowrap;font-size:24px;line-height:32px;font-weight:600}',
    '.s6-lbl .katex{font-size:26px}',
    '.s6-callout{position:absolute;font-size:28px;line-height:40px;font-weight:600;white-space:nowrap}',
    '.s6-kick{font-size:24px;line-height:32px;color:var(--ink-2);white-space:nowrap}',
    '.s6-kick b{font-weight:700}',
    '.s6-dotnote{font-size:18px;font-weight:500;color:var(--ink-3);margin-left:6px}',
    '.s6-xnote{position:absolute;white-space:nowrap;font-size:22px;line-height:30px;font-weight:600;color:var(--c-xfer)}',
    '.s6-d3 .eq-panel{padding:26px 30px 18px}',
    '.s6-d3 .derive-line{padding:7px 0}',
    '.s6-d3 .derive-tex .katex{font-size:27px}',
    '.s6-d3 .derive-note{font-size:20px;line-height:28px}',
    '.s6-final{background:var(--bg-2);border:1px solid var(--line);border-radius:24px;padding:16px 26px 12px}',
    '.s6-final .hd{font-size:18px;line-height:24px;color:var(--ink-3);display:flex;justify-content:space-between}',
    '.s6-final .katex{font-size:26px}',
    '.s6-final .katex-display{margin:10px 0 4px;text-align:left}',
    '.s6-final .katex-display > .katex{text-align:left}',
    '.s6-final .lg{margin-top:8px;font-size:20px;line-height:30px;color:var(--ink-2)}',
    '.s6-final .lg .katex{font-size:20px}',
    '.s6-cases{border-collapse:collapse;font-size:22px;line-height:30px}',
    '.s6-cases th{font-weight:600;color:var(--ink-3);font-size:18px;text-align:left;padding:6px 12px;border-bottom:1px solid var(--line)}',
    '.s6-cases td{padding:8px 12px;border-bottom:1px solid rgba(35,43,59,.9);color:var(--ink)}',
    '.s6-cases td.c{text-align:center}',
    '.s6-cases .katex{font-size:23px}',
    '.s6-halo{paint-order:stroke;stroke:#0A0D14;stroke-width:6px;stroke-linejoin:round}',
    '.s6-cap{font-size:22px;line-height:32px;color:var(--ink-2)}',
    /* s06-04 */
    '.s6-hudp{padding:16px 22px;border-radius:18px;background:rgba(10,13,20,.82);border:1px solid var(--line);pointer-events:none}',
    '.s6-hudp .q{font-size:22px;line-height:30px;font-weight:600;color:var(--ink);margin-bottom:8px}',
    '.s6-hudp .m{display:flex;align-items:center;gap:12px;margin:8px 0;white-space:nowrap}',
    '.s6-hudp .k{flex:0 0 auto;font-size:21px;line-height:24px;width:122px;font-weight:600}',
    '.s6-hudp .bar{position:relative;flex:0 0 auto;width:170px;height:22px;background:repeating-linear-gradient(90deg,rgba(233,237,245,.12) 0 15px,transparent 15px 17px)}',
    '.s6-hudp .bar i{position:absolute;left:0;top:0;bottom:0;width:0;background:repeating-linear-gradient(90deg,currentColor 0 15px,transparent 15px 17px)}',
    '.s6-hudp .v{font-size:28px;line-height:34px;font-weight:700;font-variant-numeric:tabular-nums}',
    '.s6-hudp .sc{display:flex;justify-content:space-between;margin-left:134px;width:170px;font-size:16px;line-height:22px;color:var(--ink-3)}',
    '.s6-hudp .nt{margin-top:6px;font-size:18px;line-height:26px;color:var(--ink-3)}',
    '.s6-hudp .z{margin-top:8px;padding-top:8px;border-top:1px solid var(--line);font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s6-read{padding:14px 18px;border-radius:16px;background:rgba(10,13,20,.82);border:1px solid var(--line);pointer-events:none}',
    '.s6-read .hd{font-size:18px;line-height:24px;color:var(--ink-3);margin-bottom:4px}',
    '.s6-read .r{display:grid;grid-template-columns:112px 1fr;font-size:18px;line-height:25px;color:var(--ink-2);margin-top:5px;white-space:nowrap}',
    '.s6-read .r b{color:var(--ink);font-weight:700}',
    '.s6-wall3d{font-size:19px;line-height:26px;font-weight:600;white-space:nowrap;padding:2px 10px;border-radius:10px;background:rgba(10,13,20,.7)}',
    '.s6-hudp .z b{font-variant-numeric:tabular-nums;color:var(--ink)}',
    '.s6-ax3d{font-size:22px;line-height:30px;font-weight:600}',
    '.s6-tick3d{font-size:17px;line-height:22px;color:var(--ink-3);font-family:var(--font-mono);letter-spacing:0}',
    '.s6-capline{font-size:24px;line-height:36px;color:var(--ink-2)}',
    '.s6-capline b{color:var(--ink);font-weight:600}',
    '.s6-mini .katex{font-size:24px}',
    /* s06-05 */
    '.s6-lines .l{font-size:30px;line-height:44px;margin-bottom:14px}',
    '.s6-lines .l small{display:block;font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s6-eq5{background:var(--bg-2);border:1px solid var(--line);border-radius:24px;padding:18px 28px}',
    '.s6-eq5 .katex{font-size:34px}',
    '.s6-eq5 .nt{font-size:21px;line-height:30px;color:var(--ink-2);margin-top:4px}',
    '.s6-fhead{display:flex;align-items:center;gap:14px;font-size:22px;line-height:30px;color:var(--ink-2);margin-bottom:6px}',
    '.s6-verd{display:flex;align-items:center;gap:18px;margin-top:12px;padding:12px 20px;border-radius:16px;background:var(--bg-2);border:1px solid var(--line);font-size:24px;line-height:38px;font-weight:600}',
    '.s6-verd b{font-weight:700;margin-right:12px}',
    '.s6-verd .ic{flex:0 0 auto;width:44px;height:44px;border-radius:22px;border:2px solid currentColor;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700}',
    '.s6-fnote{margin-top:10px;font-size:20px;line-height:28px;color:var(--ink-3)}',
    '.s6-concl{font-size:30px;line-height:44px;font-weight:600;padding:14px 22px;border-left:4px solid var(--c-cpr);background:var(--c-cpr-soft);border-radius:0 14px 14px 0}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s06-style')) return;
    var st = document.createElement('style'); st.id = 's06-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  var ICON_WARN = '<svg viewBox="0 0 30 30" fill="none" stroke="#F5B43C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3.5 28 26.5H2z"/><path d="M15 12v7"/><circle cx="15" cy="22.6" r="0.9" fill="#F5B43C"/></svg>';

  /* ================================================================ s06-01
     EndorseRank = PageRank on the allowance graph. The small world (G7) turns amber, the
     four-line summary lights its parts, then a powers-of-ten pull-back: the small world
     shrinks into one dot of an (illustrative) constellation while the readout counts
     4 → 6,221,665 nodes in log space. */
  var ZW = { x: 96, y: 190, w: 940, h: 720 }, WX = 90, WY = 96, Z0 = 140;
  var CX = WX + 380, CY = WY + 250;   /* the small world's centre in the zoom box */
  function genStars() {
    var rnd = Deck.util.rng(61), P = [], H = [], Ed = [], i;
    var hubs = [[150, 140], [330, 520], [610, 120], [800, 470], [210, 330], [700, 640], [880, 220], [470, 610], [90, 600], [560, 330]];
    hubs.forEach(function (h) { H.push({ x: h[0], y: h[1], r: 3.6 + rnd() * 2.2, a: 0.95 }); });
    function gauss() { var u = 1 - rnd(), v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
    for (i = 0; i < 2300; i++) {
      var p, hub = -1;
      if (rnd() < 0.62) { hub = Math.floor(rnd() * hubs.length); var sd = 46 + rnd() * 70; p = { x: hubs[hub][0] + gauss() * sd, y: hubs[hub][1] + gauss() * sd }; }
      else p = { x: rnd() * ZW.w, y: rnd() * ZW.h };
      if (Math.hypot(p.x - CX, p.y - CY) < 36) continue;
      p.r = 0.8 + rnd() * 1.3; p.a = 0.22 + rnd() * 0.55; p.b = rnd() < 0.33 ? 0 : rnd() < 0.5 ? 1 : 2;
      P.push(p);
      if (hub >= 0 && rnd() < 0.45) Ed.push([P.length - 1, -1 - hub]);
    }
    for (i = 0; i < 420; i++) {
      var a = Math.floor(rnd() * P.length), b = Math.floor(rnd() * P.length);
      if (Math.hypot(P[a].x - P[b].x, P[a].y - P[b].y) < 90) Ed.push([a, b]);
    }
    return { P: P, H: H, E: Ed };
  }
  var STARS = null;
  function drawStars(K, Z) {
    if (!K) return;
    var S = STARS || (STARS = genStars()), g = K.g;
    K.clear();
    var lz = Math.log10(Math.max(1, Z)), grow = 1 + 0.55 * lz;
    function px(p) { return CX + (p.x - CX) * Z; }
    function py(p) { return CY + (p.y - CY) * Z; }
    function node(id) { return id < 0 ? S.H[-1 - id] : S.P[id]; }
    g.lineWidth = 1;
    g.strokeStyle = 'rgba(245,180,60,0.13)';
    g.beginPath();
    for (var e = 0; e < S.E.length; e++) {
      var A = node(S.E[e][0]), B = node(S.E[e][1]);
      var ax = px(A), ay = py(A), bx = px(B), by = py(B);
      if ((ax < -50 && bx < -50) || (ax > ZW.w + 50 && bx > ZW.w + 50) || (ay < -50 && by < -50) || (ay > ZW.h + 50 && by > ZW.h + 50)) continue;
      g.moveTo(ax, ay); g.lineTo(bx, by);
    }
    g.stroke();
    var shades = ['rgba(245,180,60,', 'rgba(250,206,120,', 'rgba(233,237,245,'];
    for (var s = 0; s < 3; s++) {
      for (var i = 0; i < S.P.length; i++) {
        var p = S.P[i]; if (p.b !== s) continue;
        var x = px(p), y = py(p);
        if (x < -10 || y < -10 || x > ZW.w + 10 || y > ZW.h + 10) continue;
        g.fillStyle = shades[s] + p.a.toFixed(2) + ')';
        g.beginPath(); g.arc(x, y, p.r * grow, 0, Math.PI * 2); g.fill();
      }
    }
    g.fillStyle = 'rgba(245,180,60,0.95)';
    S.H.forEach(function (h) {
      var x = px(h), y = py(h);
      if (x < -20 || y < -20 || x > ZW.w + 20 || y > ZW.h + 20) return;
      g.beginPath(); g.arc(x, y, h.r * grow, 0, Math.PI * 2); g.fill();
    });
  }
  function logCount(a, b, p) { return Math.round(Math.pow(10, Math.log10(a) + p * (Math.log10(b) - Math.log10(a)))); }

  var slide1 = {
    id: 's06-01', title: 'EndorseRank', time: 40, steps: 3,
    tags: function (step) { return step >= 2 ? ['thesis-example', 'example'] : ['thesis-example']; },
    notes: [
      'Now I will introduce the four scores. The first is EndorseRank, the score this thesis proposes. I have brought back the small world we built in 04. This time every edge is an allowance edge, so they are all amber. The walker follows an edge 85 times out of 100 and teleports to any node the other 15 times.',
      'EndorseRank runs the PageRank we have built so far on the allowance graph. Edges go from an owner to a spender contract, and only the latest allowance per token is used. The weight is the same as in AWP, time weight times value weight, and restarts are the same at every node v, 1/|V| each. What we evaluate are the contracts that received approvals. Owner A also holds a share in the walk (0.1375), but this study evaluates and reports only the scores of contracts. The numbers above B, C and D and the share of A come from the example in Chapter 2 of the thesis.',
      'Now let us pull back from the small world to the real allowance graph. The four-node world gets smaller and smaller until it is one node among a great many. The real allowance graph has 6,221,665 nodes and 11,210,114 edges. The constellation you see here is a picture for explanation; only the counts are real.',
      'One point needs care. An edge holds the amount and the time of the latest allowance. It does not show an allowance that has shrunk since then because the contract spent tokens from it, and it does not show approvals made before October 2023.'
    ],
    html:
      '<h1 class="t-h1">EndorseRank = PageRank on the [[allowance]] graph</h1>' +
      '<div class="abs s6-zoom" id="zoom" data-in="none" style="left:' + ZW.x + 'px;top:' + ZW.y + 'px;width:' + ZW.w + 'px;height:' + ZW.h + 'px"></div>' +
      '<div class="abs s6-readout" id="readout" data-in="none" style="left:' + (ZW.x + 28) + 'px;top:' + (ZW.y + ZW.h - 128) + 'px">' +
        '<span class="k">Nodes</span><span class="a">4 →</span><span class="v" id="rn">4</span>' +
        '<span class="k">Edges</span><span class="a">4 →</span><span class="v" id="re">4</span></div>' +
      '<div class="abs s6-fcard" id="fcard" style="left:1080px;top:190px;width:744px">' +
        '<div class="hd">Definition · thesis Ch. 3</div><div id="fhost"></div>' +
        '<div class="nt">The formula from 04, with allowance weights $\\ca{w_A}$ and uniform restarts</div></div>' +
      '<div class="abs s6-sum" id="sum" data-in="none" style="left:1080px;top:436px;width:744px">' +
        '<div class="ln"><span class="no">1</span><span class="tx">Edges: owner → spender contract<small>latest allowance per token · five tokens · USD</small></span></div>' +
        '<div class="ln"><span class="no">2</span><span class="tx">Weights: σ × V, as in AWP<small>time weight × value weight (the formula from 05)</small></span></div>' +
        '<div class="ln"><span class="no">3</span><span class="tx">Restarts: the same at every node<small>every node $v$ gets $\\pi_v = 1/|V|$ · damping factor $d = ' + DAMP + '$</small></span></div>' +
        '<div class="ln"><span class="no">4</span><span class="tx">Evaluated: contracts that receive approvals<small>Owners (EOAs) hold a share too, but are not evaluated or reported</small></span></div>' +
      '</div>' +
      '<div class="abs s6-caution" data-step="3" style="left:1080px;top:842px;width:744px">' + ICON_WARN +
        '<span>An edge holds the amount and time of the latest allowance, not the allowance left today</span></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var zoom = q(el, '#zoom');
      g.K = Comp.canvas(ctx, zoom, { w: ZW.w, h: ZW.h, x: 0, y: 0, onResize: function (K) { drawStars(K, g.Z || Z0); } });
      gsap.set(g.K.canvas, { autoAlpha: 0 });
      g.W = Comp.smallWorld(ctx, zoom, { x: WX, y: WY, hidden: true, shared: 'small-world',
        labels: { A: 'Owner A', B: 'Vault B', C: 'Vault C', D: 'Lending pool D' } });
      g.W.wrap.style.transformOrigin = '380px 250px';
      g.dot = document.createElement('div'); g.dot.className = 's6-swdot'; g.dot.style.left = CX + 'px'; g.dot.style.top = CY + 'px';
      g.lab = document.createElement('div'); g.lab.className = 's6-swlab'; g.lab.style.left = (CX + 28) + 'px'; g.lab.style.top = (CY - 40) + 'px';
      g.lab.innerHTML = 'Small world (4 nodes)<small>example constellation · only the counts are real</small>';
      zoom.appendChild(g.dot); zoom.appendChild(g.lab);
      gsap.set([g.dot, g.lab], { autoAlpha: 0 });
      g.F = Comp.formula(ctx, q(el, '#fhost'), '\\mathbf s_{\\mathrm{ER}}=\\mathrm{PageRank}\\bigl(\\part{g}{\\ca{G_{\\mathrm{approve}}}},\\ \\part{pi}{\\pi_v=\\tfrac{1}{|V|}},\\ \\part{d}{d=' + DAMP + '}\\bigr)', { display: true });
      g.F.el.style.textAlign = 'left';
      g.lines = Array.prototype.slice.call(el.querySelectorAll('.s6-sum .ln'));
      gsap.set(g.lines, { autoAlpha: 0 });
      g.readout = q(el, '#readout'); gsap.set(g.readout, { autoAlpha: 0 });
      g.rn = q(el, '#rn'); g.re = q(el, '#re');
      /* teleport drops (one per node and column) */
      g.drops = [];
      g.W.svg.setAttribute('overflow', 'visible');
      ['A', 'B', 'C', 'D'].forEach(function (id) {
        var N = g.W.node(id);
        for (var k = 0; k < 3; k++) {
          var c = svgEl('circle', { cx: N.x + (k - 1) * 12, cy: N.y - 80, r: 4.5, fill: '#fff', 'fill-opacity': 0.85 }, g.W.svg);
          gsap.set(c, { autoAlpha: 0 });
          g.drops.push({ c: c, y0: N.y - 92 - k * 16, y1: N.y - (N.kind === 'eoa' ? 20 : 36) });
        }
      });
      g.Z = Z0;
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      settleShared(ctx, g.W.wrap, 'small-world');
      tl.add(g.W.drawIn({ stagger: 0.1 }), 0.2);
      tl.call(function () { ctx.add(function () { g.W.walker.place('A'); g.W.walker.walk(7, { seed: 11, d: DAMP, duration: 0.42 }); }); }, null, 1.6);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        var T0 = 0;
        g.lines.forEach(function (ln, k) {
          var t = T0 + k * 0.95;
          tl.fromTo(ln, { autoAlpha: 0, x: 40 }, { autoAlpha: 1, x: 0, duration: 0.55, ease: E.out }, t);
          tl.fromTo(ln.querySelector('.no'), { scale: 0.4 }, { scale: 1, duration: 0.4, ease: E.stamp }, t + 0.1);
        });
        /* 1: the arrows (keyrings pulse, strokes brighten) */
        tl.add(g.F.mark('g', { duration: 0.35 }), T0 + 0.2);
        g.W.edges.forEach(function (A, k) {
          if (A.key) tl.fromTo(A.key, { scale: 2.0, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.5, ease: 'power3.out', immediateRender: false }, T0 + 0.25 + k * 0.06);
          tl.fromTo(A.strands, { stroke: '#FFE2A8' }, { stroke: C.allow, duration: 0.7, ease: 'power2.out', immediateRender: false }, T0 + 0.25 + k * 0.06);
        });
        /* 2: the weights (widths swell and settle) */
        g.W.edges.forEach(function (A) {
          var w0 = 2 + 2.2 * A.w;
          tl.to(A.strands, { attr: { 'stroke-width': w0 * 1.7 }, duration: 0.3, ease: 'power2.out' }, T0 + 0.95 + 0.1);
          tl.to(A.strands, { attr: { 'stroke-width': w0 }, duration: 0.45, ease: 'power2.inOut' }, T0 + 0.95 + 0.45);
          if (A.label) tl.fromTo(A.label, { scale: 1.5, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.5, ease: 'power3.out', immediateRender: false }, T0 + 1.0);
        });
        /* 3: restarts: the same small rain falls on every node */
        tl.add(g.F.unmark('g'), T0 + 1.9);
        tl.add(g.F.mark('pi', { duration: 0.35 }), T0 + 1.95);
        g.drops.forEach(function (d, k) {
          var t = T0 + 2.0 + (k % 3) * 0.12;
          tl.fromTo(d.c, { autoAlpha: 0, attr: { cy: d.y0 } }, { autoAlpha: 0.85, attr: { cy: d.y1 }, duration: 0.5, ease: 'power2.in' }, t);
          tl.to(d.c, { autoAlpha: 0, duration: 0.2 }, t + 0.5);
        });
        /* 4: who is evaluated: contracts B, C, D (thesis Ch. 2 example values). The owner A also holds a
              stationary share (0.1375) but the study neither evaluates nor reports EOA scores. */
        var WE = ((DATA.params || {}).worked_example || {}).thesis_values || {};
        var st = WE.stationary || [0.1375, 0.2154, 0.1765, 0.4706];
        tl.add(g.F.unmark('pi'), T0 + 2.85);
        ['B', 'C', 'D'].forEach(function (id, k) {
          tl.add(g.W.node(id).badge(fmt(st[k + 1], 4), { color: C.allow }), T0 + 2.95 + k * 0.12);
        });
        var NA = g.W.node('A');
        tl.add(NA.tag('not evaluated'), T0 + 3.3);
        NA.tagT.setAttribute('text-anchor', 'end'); NA.tagT.setAttribute('x', NA.r + 6);
        if (!g.aShare) {
          g.aShare = svgEl('text', { x: NA.r + 6, y: -NA.r - 38, 'text-anchor': 'end', fill: C.ink3, 'font-size': 20, 'font-weight': 700, 'class': 'tnum' }, NA.g);
          g.aShare.textContent = 'share ' + fmt(st[0], 4);
        }
        tl.fromTo(g.aShare, { autoAlpha: 0, y: 6 }, { autoAlpha: 1, y: 0, duration: 0.4 }, T0 + 3.3);
      }
      if (i === 2) {
        /* powers-of-ten pull-back */
        tl.to(g.W.walker.g, { autoAlpha: 0, duration: 0.3 }, 0);
        tl.set(g.K.canvas, { autoAlpha: 1 }, 0.15);
        tl.fromTo(g.readout, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: E.out }, 0.1);
        var st2 = { p: 0 }, LZ = Math.log(Z0);
        var apply = function () {
          var Z = Math.exp(LZ * (1 - st2.p));
          g.Z = Z;
          gsap.set(g.W.wrap, { scale: Z / Z0 });
          drawStars(g.K, Z);
          g.rn.textContent = fmt(logCount(4, GA.nodes, st2.p), 0);
          g.re.textContent = fmt(logCount(4, GA.edges, st2.p), 0);
        };
        apply();
        tl.to(st2, { p: 1, duration: 2.1, ease: 'power2.inOut', onUpdate: apply,
          onComplete: function () { st2.p = 1; apply(); g.rn.textContent = fmt(GA.nodes, 0); g.re.textContent = fmt(GA.edges, 0); } }, 0.25);
        tl.to(g.W.wrap, { autoAlpha: 0, duration: 0.35 }, 2.0);
        tl.fromTo(g.dot, { autoAlpha: 0, scale: 2.6 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: E.out }, 2.05);
        tl.fromTo(g.lab, { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.45, ease: E.out }, 2.35);
      }
    }
  };

  /* ================================================================ s06-02
     AWP (transfer graph, activeness restarts) and the raw-degree baselines. */
  var S2 = { L: { x: 96, y: 196, w: 820, h: 664 }, R: { x: 956, y: 196, w: 868, h: 664 } };
  var slide2 = {
    id: 's06-02', title: 'AWP and raw-degree baselines', time: 40, steps: 3,
    tags: function (step) { return step >= 1 ? ['example'] : []; },
    notes: [
      'The second is AWP, the score we compare against, together with the plain counts.',
      'AWP is PageRank on the transfer graph. Do and colleagues proposed it in 2023. Its edges are transfers, so coins flow along them. Where it restarts is different from EndorseRank. An active address, one that sent to many counterparties recently, has a bigger halo, and the walk restarts there more often. The graph is an illustrative example.',
      'And there is one more comparator that matters a great deal in this study: simply counting the edges. Let me call the contract v. On the allowance side, it is the number of distinct owners whose latest allowance to v is above zero. If the same owner approves twice, it still counts once. On the transfer side, it is the number of distinct addresses that sent transfers to v. In the test windows, the baseline leaves out the transfers a contract sent to itself.',
      'PageRank is, in the end, a smoothed version of these counts, so we must ask what it gives beyond the plain count. I will answer exactly this question in the results section.'
    ],
    html:
      '<h1 class="t-h1">AWP = PageRank on the [[transfer]] graph</h1>' +
      '<div class="abs s6-panel" id="pl" data-in="none" style="left:' + S2.L.x + 'px;top:' + S2.L.y + 'px;width:' + S2.L.w + 'px;height:' + S2.L.h + 'px">' +
        '<div class="hd c-xfer">AWP<small>Do et al., 2023</small></div>' +
        '<div class="sb">Restarts: in proportion to activeness $X_u$</div>' +
        '<svg id="gl" width="' + S2.L.w + '" height="420" style="left:0;top:140px"></svg>' +
        '<div class="s6-legend" id="lgl" style="top:560px">Bigger halo = sent to more counterparties recently<br>→ the walk restarts there more often &nbsp;&nbsp;$\\pi_u = X_u \\big/ \\textstyle\\sum_v X_v$</div>' +
      '</div>' +
      '<div class="abs s6-panel" id="pr" data-in="none" style="left:' + S2.R.x + 'px;top:' + S2.R.y + 'px;width:' + S2.R.w + 'px;height:' + S2.R.h + 'px">' +
        '<div class="hd">Baseline = plain count<small>raw degree</small></div>' +
        '<svg id="gr" width="' + S2.R.w + '" height="430" style="left:0;top:96px"></svg>' +
        '<div class="s6-defs" id="defs" style="top:506px">' +
          '<div class="d"><span class="k">In-approve degree</span><span class="w"><b>distinct owners</b> with a latest allowance &gt; 0 to $v$</span></div>' +
          '<div class="d"><span class="k">Transfer in-degree</span><span class="w"><b>distinct addresses</b> that sent $v$ a transfer</span></div>' +
          '<div class="mi">In the test windows (W0, W1) the baseline leaves out self-transfers · thesis Ch. 3</div>' +
        '</div>' +
      '</div>' +
      '<p class="abs s6-bottom" data-step="3" data-in="words" style="left:96px;top:892px;width:1180px">PageRank is a smoothed version of these counts.<br>The question is whether it does more than smooth.</p>' +
      '<div class="abs" id="jump" data-in="none" style="left:1330px;top:866px;width:494px;height:110px"></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.pl = q(el, '#pl'); g.pr = q(el, '#pr');
      var gl = q(el, '#gl'), gr = q(el, '#gr');
      /* left: transfer graph with activeness halos */
      var halos = [[110, 64, 54], [110, 214, 34], [110, 364, 19]];
      g.halos = halos.map(function (h) {
        return svgEl('circle', { cx: h[0], cy: h[1], r: h[2], fill: 'rgba(60,196,255,.13)', stroke: 'rgba(60,196,255,.5)', 'stroke-width': 1.5 }, gl);
      });
      g.GL = Comp.graph(ctx, gl, {
        nodes: [{ id: 'e1', x: 110, y: 64, kind: 'eoa' }, { id: 'e2', x: 110, y: 214, kind: 'eoa' }, { id: 'e3', x: 110, y: 364, kind: 'eoa' },
                { id: 'k1', x: 420, y: 104, kind: 'contract', size: 58 }, { id: 'k2', x: 420, y: 324, kind: 'contract', size: 58 }, { id: 'k3', x: 690, y: 214, kind: 'contract', size: 58 }],
        edges: [{ from: 'e1', to: 'k1', kind: 'xfer', width: 3 }, { from: 'e2', to: 'k1', kind: 'xfer', width: 3 }, { from: 'e2', to: 'k2', kind: 'xfer', width: 3 },
                { from: 'e3', to: 'k2', kind: 'xfer', width: 3 }, { from: 'k1', to: 'k3', kind: 'xfer', width: 3 }, { from: 'k2', to: 'k3', kind: 'xfer', width: 3 }],
        showWeights: false, hidden: true
      });
      gsap.set(g.halos, { autoAlpha: 0 });
      g.lgl = q(el, '#lgl'); gsap.set(g.lgl, { autoAlpha: 0 });
      gsap.set([q(el, '#pl .hd'), q(el, '#pl .sb')], { autoAlpha: 0 });
      /* right: one contract, owners (allowance) and senders (transfer), two tallies */
      var W = { x: 470, y: 200 };
      g.W = Comp.contract(ctx, gr, { x: W.x, y: W.y, size: 84, label: 'contract v' });
      var ow = [30, 86, 142, 198], se = [266, 322, 378];
      svgEl('text', { x: 36, y: 122, fill: C.allow, 'font-size': 22, 'font-weight': 600 }, gr).textContent = 'Owners';
      svgEl('text', { x: 36, y: 330, fill: C.xfer, 'font-size': 22, 'font-weight': 600 }, gr).textContent = 'Senders';
      g.own = ow.map(function (y) { return Comp.eoa(ctx, gr, { x: 170, y: y, r: 13 }); });
      g.snd = se.map(function (y) { return Comp.eoa(ctx, gr, { x: 170, y: y, r: 13 }); });
      g.aA = ow.map(function (y) { return Comp.arrow(ctx, gr, { from: [170, y], to: [W.x, W.y], kind: 'allow', width: 3, shorten: [18, 52], hidden: true }); });
      g.aT = se.map(function (y) { return Comp.arrow(ctx, gr, { from: [170, y], to: [W.x, W.y], kind: 'xfer', width: 3, shorten: [18, 52], hidden: true, flow: false }); });
      g.again = svgEl('circle', { r: 8, fill: C.allow, 'fill-opacity': 0.9 }, gr); gsap.set(g.again, { autoAlpha: 0 });
      g.sameTag = svgEl('text', { x: 300, y: 70, 'text-anchor': 'middle', fill: C.ink, 'font-size': 21, 'font-weight': 600 }, gr);
      g.sameTag.textContent = 'same owner → counted once'; gsap.set(g.sameTag, { autoAlpha: 0 });
      svgEl('text', { x: 620, y: 40, fill: C.ink2, 'font-size': 21 }, gr).textContent = 'In-approve degree';
      svgEl('text', { x: 620, y: 290, fill: C.ink2, 'font-size': 21 }, gr).textContent = 'Transfer in-degree';
      g.tA = Comp.tally(ctx, gr, { x: 630, y: 66, size: 46 });
      g.tT = Comp.tally(ctx, gr, { x: 630, y: 316, size: 46 });
      g.cA = svgEl('text', { x: 800, y: 106, 'text-anchor': 'end', fill: C.deg, 'font-size': 46, 'font-weight': 700, 'class': 'tnum' }, gr); g.cA.textContent = '0';
      g.cT = svgEl('text', { x: 800, y: 356, 'text-anchor': 'end', fill: C.deg, 'font-size': 46, 'font-weight': 700, 'class': 'tnum' }, gr); g.cT.textContent = '0';
      gsap.set([g.tA.border, g.tT.border, g.cA, g.cT], { autoAlpha: 0 });
      g.defs = q(el, '#defs'); gsap.set(g.defs.children, { autoAlpha: 0 });
      /* high-jump bar: baseline = raw count; can the PageRank chips clear it? */
      var jump = q(el, '#jump');
      var js = Comp.svg(ctx, jump, { w: 494, h: 110 });
      g.bar = svgEl('line', { x1: 10, y1: 78, x2: 484, y2: 78, stroke: C.deg, 'stroke-width': 3, 'stroke-dasharray': '10 8' }, js);
      g.barLbl = svgEl('text', { x: 10, y: 104, fill: C.deg, 'font-size': 20, 'font-weight': 600 }, js); g.barLbl.textContent = 'Baseline = plain count';
      g.q = svgEl('text', { x: 484, y: 104, 'text-anchor': 'end', fill: C.ink2, 'font-size': 20 }, js); g.q.textContent = 'Can they clear it?';
      g.chipER = document.createElement('div'); g.chipER.className = 's6-chip c-allow'; g.chipER.textContent = 'EndorseRank ↑';
      g.chipAWP = document.createElement('div'); g.chipAWP.className = 's6-chip c-xfer'; g.chipAWP.textContent = 'AWP ↑';
      g.chipER.style.left = '90px'; g.chipER.style.top = '8px'; g.chipAWP.style.left = '300px'; g.chipAWP.style.top = '8px';
      jump.appendChild(g.chipER); jump.appendChild(g.chipAWP);
      gsap.set([g.bar, g.barLbl, g.q, g.chipER, g.chipAWP], { autoAlpha: 0 });
      gsap.set([g.W.g].concat(g.own.map(function (n) { return n.g; }), g.snd.map(function (n) { return n.g; })), { autoAlpha: 0 });
      g.Wpos = W;
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo([g.pl, g.pr], { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, stagger: 0.12 }, 0.15);
      tl.fromTo([q(el, '#pl .hd'), q(el, '#pl .sb')], { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out, stagger: 0.1 }, 0.5);
      tl.add(g.W.pop(), 0.6);
      tl.fromTo(g.own.map(function (n) { return n.g; }).concat(g.snd.map(function (n) { return n.g; })), { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%' },
        { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp, stagger: 0.05 }, 0.7);
      tl.fromTo([g.tA.border, g.tT.border, g.cA, g.cT], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.0);
      Object.keys(g.GL.nodes).forEach(function (id, k) { tl.add(g.GL.nodes[id].pop(), 0.6 + k * 0.07); });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        g.GL.edges.forEach(function (A, k) { tl.add(A.draw({ duration: 0.55 }), k * 0.1); });
        tl.call(function () { g.GL.edges.forEach(function (A) { A.flow(true); A.g.querySelectorAll('circle').forEach(function (c) { c.setAttribute('fill-opacity', 0.5); }); }); }, null, 1.4);
        tl.fromTo(g.halos, { autoAlpha: 0, scale: 0.2, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.7, ease: E.out, stagger: 0.15 }, 1.0);
        tl.fromTo(g.halos[0], { scale: 1.25, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.6, ease: 'power2.inOut', immediateRender: false }, 1.9);
        tl.fromTo(g.lgl, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 1.9);
      }
      if (i === 2) {
        var t = 0;
        g.aA.forEach(function (A, k) {
          tl.add(A.draw({ duration: 0.45 }), t);
          tl.add(g.tA.add(1), t + 0.42);
          tl.call(function (n) { g.cA.textContent = String(n); }, [k + 1], t + 0.45);
          tl.fromTo(g.cA, { scale: 1.35, transformOrigin: '100% 70%' }, { scale: 1, duration: 0.3, ease: 'power3.out', immediateRender: false }, t + 0.45);
          t += 0.5;
        });
        /* the second owner approves again: a pulse runs along the same arrow, no new stroke */
        var A2 = g.aA[1], st = { p: 0 };
        tl.set(g.again, { autoAlpha: 1 }, t);
        tl.to(st, { p: 1, duration: 0.55, ease: 'power2.inOut', onUpdate: function () { var pt = A2.pointAt(st.p); g.again.setAttribute('cx', pt.x); g.again.setAttribute('cy', pt.y); } }, t);
        tl.to(g.again, { autoAlpha: 0, duration: 0.2 }, t + 0.55);
        tl.fromTo(g.sameTag, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.3 }, t + 0.5);
        tl.to(g.sameTag, { autoAlpha: 0, duration: 0.4 }, t + 1.7);
        t += 1.0;
        g.aT.forEach(function (A, k) {
          tl.add(A.draw({ duration: 0.45 }), t);
          tl.add(g.tT.add(1), t + 0.42);
          tl.call(function (n) { g.cT.textContent = String(n); }, [k + 1], t + 0.45);
          tl.fromTo(g.cT, { scale: 1.35, transformOrigin: '100% 70%' }, { scale: 1, duration: 0.3, ease: 'power3.out', immediateRender: false }, t + 0.45);
          t += 0.5;
        });
        tl.fromTo(g.defs.children, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out, stagger: 0.15 }, t + 0.1);
      }
      if (i === 3) {
        tl.fromTo(g.bar, { autoAlpha: 0, attr: { x2: 10 } }, { autoAlpha: 1, attr: { x2: 484 }, duration: 0.6, ease: E.out }, 0.6);
        tl.fromTo([g.barLbl, g.q], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.9);
        tl.fromTo(g.chipER, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out }, 1.1);
        tl.fromTo(g.chipAWP, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out }, 1.25);
        /* the tallies glow: this is the bar to clear */
        tl.fromTo([g.tA.border, g.tT.border], { opacity: 1 }, { opacity: 0.35, duration: 0.4, yoyo: true, repeat: 1 }, 0.6);
      }
    }
  };

  /* ================================================================ s06-03
     C-PR: two 100 % rows (allowance row, transfer row) are squashed by λ and 1 − λ and
     joined into one mixed row; the dial sweeps λ; then a node with allowance arrows only
     is renormalized by D_λ(u). Bars: example (s05-06 cap example; σ(0) = 0.8581). */
  var ROWA = { S1: 20000 / 20500, S2: 500 / 20500 };                 /* 0.9756 / 0.0244 */
  var XT = [1000 * 0.8581, 300 * 0.5];                                /* 858.1 / 150 */
  var ROWT = { S2: XT[1] / (XT[0] + XT[1]), R: XT[0] / (XT[0] + XT[1]) }; /* 0.1488 / 0.8512 */
  var R4 = function (v) { return Math.round(v * 1e4) / 1e4; };
  ROWA = { S1: R4(ROWA.S1), S2: R4(ROWA.S2) }; ROWT = { S2: R4(ROWT.S2), R: R4(ROWT.R) };
  var B3 = { x: 576, y: 196, L: 400, x0: 26, h: 44, rows: [52, 226, 400] };   /* bar figure */
  var SHADE = { S1: C.allow, S2a: '#C98F2A', S2b: '#2A93C2', R: C.xfer };
  var slide3 = {
    id: 's06-03', title: 'C-PR: mixing the two rows', time: 60, steps: 6,
    tags: function (step) { return step >= 4 && step < 6 ? ['example', 'plan'] : ['example']; },
    notes: [
      'The third score is C-PR, coupled PageRank. It is a score that walks both graphs together. Let us look at one owner, u. Two allowance edges and two transfer edges leave u.',
      'First, the row of u on the allowance side, its row in the transition matrix. The A under P means the allowance layer, u is the starting node, and the last place, the dot, stands for every destination. Just as in the cap example from 05, the unlimited allowance counts as 20,000 dollars and the other one is 500 dollars, so the row splits into 0.9756 and 0.0244. They add up to 1.',
      'We build the transfer row too. The 1,000 dollars sent today is multiplied by the time weight 0.858, giving 858, and the 300 dollars sent 180 days ago is multiplied by 0.5, giving 150. So the row is 0.8512 and 0.1488. This also adds up to 1. All the amounts are illustrative examples.',
      'Now we mix the two rows. With the dial λ at 0.5, we shrink the allowance row to half, shrink the transfer row to half as well, and join them. S1 gets 0.4878, S2 gets the two pieces added together, 0.0866, and R gets 0.4256. λ times 1 plus 1 minus λ times 1 is always 1, so the mixed row also adds up to 1.',
      'Let me turn the dial. At λ = 1 the mixed row is the same as the allowance row, and at 0 it is the same as the transfer row. The primary value 0.5 and the sensitivity values 0.25 and 0.75 were written into the analysis plan before this study extracted any data.',
      'But what if u has no transfer edges? Then the transfer row is empty. The mixed row adds up to only λ, that is 0.5. So we divide by λ to bring it back to 1. We write this divisor as D-lambda. In the end, that node follows its allowance edges 100% of the time.',
      'This is the coupled formula in Chapter 3 of the thesis. The switch, the bold 1, is 1 if the node has outgoing edges in that layer and 0 if not. As a table: if both kinds are there, the weights are λ and 1 minus λ; if only one kind is there, that one gets 1; if neither is there, the node is dangling and its mass goes to the restart. λ = 1 is the same as walking the allowance layer alone, and 0 the same as walking the transfer layer alone. Restarts are uniform, and d is 0.85.'
    ],
    html:
      '<h1 class="t-h1" style="font-size:58px;line-height:70px">A node’s row = λ × allowance row + (1 − λ) × transfer row</h1>' +
      '<p class="abs s6-kick" style="left:96px;top:146px"><b class="c-cpr">C-PR</b> (coupled PageRank) · a score that walks both graphs together</p>' +
      '<svg class="abs" id="g3" width="470" height="520" style="left:96px;top:196px;overflow:visible" data-in="none"></svg>' +
      '<svg class="abs" id="b3" width="520" height="560" style="left:' + B3.x + 'px;top:' + B3.y + 'px;overflow:visible" data-in="none"></svg>' +
      '<div class="abs s6-lbl c-allow" id="tA" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + B3.rows[0] - 44) + 'px">Allowance row $\\ca{P_{A,u,\\cdot}}$ <span class="s6-dotnote">‘·’ = every destination</span></div>' +
      '<div class="abs s6-lbl c-xfer" id="tT" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + B3.rows[1] - 44) + 'px">Transfer row $\\ct{P_{T,u,\\cdot}}$</div>' +
      '<div class="abs s6-lbl c-cpr" id="tM" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + B3.rows[2] - 44) + 'px">Mixed row $\\cc{P^{(\\lambda)}_{u,\\cdot}}$</div>' +
      '<div class="abs s6-callout" id="call" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + 534) + 'px">One path only: take it [[100%]]</div>' +
      '<div class="abs" id="dialbox" data-shared="lambda-dial" data-in="none" style="left:96px;top:742px;width:240px;height:180px"></div>' +
      '<div class="abs" id="lcard" data-in="none" style="left:372px;top:756px"></div>' +
      '<p class="abs s6-cap" id="lcap" data-in="none" style="left:372px;top:900px;width:700px">λ = 0.5 (primary) · 0.25 · 0.75 (sensitivity)<br>fixed in the analysis plan before this study extracted any data</p>' +
      '<div class="abs s6-d3" id="d3" data-in="none" style="left:1104px;top:186px;width:720px"></div>' +
      '<div class="abs s6-final" id="fin" data-in="none" style="left:1104px;top:186px;width:720px"><div class="hd"><span>Full formula · thesis Eq. (3.9)</span></div>' +
        '$$\\begin{aligned}\\cc{P^{(\\lambda)}_{u,\\cdot}}&=\\alpha_A(u)\\,\\ca{P_{A,u,\\cdot}}+\\alpha_T(u)\\,\\ct{P_{T,u,\\cdot}}\\\\[4pt] \\alpha_A(u)&=\\frac{\\lambda\\,\\mathbf 1[o_A(u)>0]}{D_{\\lambda}(u)},\\qquad \\alpha_T(u)=\\frac{(1-\\lambda)\\,\\mathbf 1[o_T(u)>0]}{D_{\\lambda}(u)}\\\\[4pt] D_{\\lambda}(u)&=\\lambda\\,\\mathbf 1[o_A(u)>0]+(1-\\lambda)\\,\\mathbf 1[o_T(u)>0]\\end{aligned}$$' +
        '<div class="lg">$\\mathbf 1[\\text{condition}]$ is 1 if the condition holds, else 0: a switch<br>$D_\\lambda(u)$ makes the mixed row sum to 1 again · $o_A, o_T$ out-strengths</div></div>' +
      '<div class="abs" id="cases" data-in="none" style="left:1104px;top:556px;width:720px">' +
        '<table class="s6-cases" style="width:720px"><tr><th>Edges leaving u</th><th style="text-align:center">$\\alpha_A$</th><th style="text-align:center">$\\alpha_T$</th></tr>' +
        '<tr><td>allowance and transfer</td><td class="c">$\\lambda$</td><td class="c">$1-\\lambda$</td></tr>' +
        '<tr><td>allowance only</td><td class="c">$\\lambda/\\lambda=1$</td><td class="c">0</td></tr>' +
        '<tr><td>transfer only</td><td class="c">0</td><td class="c">$(1-\\lambda)/(1-\\lambda)=1$</td></tr>' +
        '<tr><td>neither</td><td class="c" colspan="2">dangling node → restart</td></tr></table>' +
        '<p class="s6-cap" style="margin-top:14px">λ = 1 walks the allowance layer alone, λ = 0 the transfer layer alone<br>uniform restarts, $d = ' + DAMP + '$</p></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* graph: owner u with two allowance and two transfer arrows */
      var gs = q(el, '#g3');
      var U = { x: 70, y: 262 }, S1 = { x: 380, y: 82 }, S2n = { x: 380, y: 262 }, Rn = { x: 380, y: 442 };
      g.u = Comp.eoa(ctx, gs, { x: U.x, y: U.y, r: 18, label: 'u (owner)' });
      g.s1 = Comp.contract(ctx, gs, { x: S1.x, y: S1.y, size: 58, label: 'S1' });
      g.s2 = Comp.contract(ctx, gs, { x: S2n.x, y: S2n.y, size: 58, label: 'S2' });
      g.r = Comp.contract(ctx, gs, { x: Rn.x, y: Rn.y, size: 58, label: 'R' });
      [g.s1, g.s2, g.r].forEach(function (N) { N.label.setAttribute('x', 44); N.label.setAttribute('y', 8); N.label.setAttribute('text-anchor', 'start'); });
      g.aS1 = Comp.arrow(ctx, gs, { from: [U.x, U.y], to: [S1.x, S1.y], kind: 'allow', width: 5, shorten: [24, 40], hidden: true });
      g.aS2 = Comp.arrow(ctx, gs, { from: [U.x, U.y], to: [S2n.x, S2n.y], kind: 'allow', width: 2.5, bend: -34, shorten: [24, 40], hidden: true });
      g.tS2 = Comp.arrow(ctx, gs, { from: [U.x, U.y], to: [S2n.x, S2n.y], kind: 'xfer', width: 2.5, bend: 34, shorten: [24, 40], hidden: true, flow: false });
      g.tR = Comp.arrow(ctx, gs, { from: [U.x, U.y], to: [Rn.x, Rn.y], kind: 'xfer', width: 5, shorten: [24, 40], hidden: true, flow: false });
      /* amount tags placed by hand next to the targets, with a dark halo so lines never cut them */
      function tag(x, y, text, col) {
        var t = svgEl('text', { x: x, y: y, 'text-anchor': 'end', fill: col, 'font-size': 20, 'font-weight': 700, 'class': 'tnum s6-halo' }, gs);
        t.textContent = text; gsap.set(t, { autoAlpha: 0 }); return t;
      }
      g.lS1 = tag(S1.x - 40, S1.y - 34, 'unlimited → cap 20,000 USD', C.allow);
      g.lS2a = tag(S2n.x - 46, S2n.y - 40, '500 USD', C.allow);
      g.lS2b = tag(S2n.x - 30, S2n.y + 46, '300 USD', C.xfer);
      svgEl('tspan', { x: S2n.x - 30, dy: 23 }, g.lS2b).textContent = '180 days ago';   /* two lines: one line would run into the label of u */
      g.lR = tag(Rn.x - 40, Rn.y + 52, '1,000 USD · today', C.xfer);
      gsap.set([g.u.g, g.s1.g, g.s2.g, g.r.g], { autoAlpha: 0 });
      /* bars */
      var bs = q(el, '#b3'), x0 = B3.x0, L = B3.L, H = B3.h;
      g.bs = bs;
      function seg(parent, y, col) { return svgEl('rect', { x: x0, y: y, width: 0, height: H, fill: col, rx: 0 }, parent); }
      function frame(parent, y, col, dash) { return svgEl('rect', { x: x0 - 3, y: y - 3, width: L + 6, height: H + 6, rx: 8, fill: 'none', stroke: col, 'stroke-width': 2, 'stroke-dasharray': dash || null }, parent); }
      function lab(parent, x, y, name, col, anchor) {
        var t = svgEl('text', { x: x, y: y, 'text-anchor': anchor || 'start', fill: col, 'font-size': 21, 'font-weight': 700, 'class': 'tnum' }, parent);
        var a = svgEl('tspan', {}, t); a.textContent = name + ' ';
        var b = svgEl('tspan', { fill: C.ink, 'font-weight': 500 }, t);
        return { t: t, v: b };
      }
      function leader(parent) { return svgEl('polyline', { points: '0,0 0,0', fill: 'none', stroke: C.ink3, 'stroke-width': 1.2 }, parent); }
      /* row A */
      var yA = B3.rows[0], yT = B3.rows[1], yM = B3.rows[2];
      g.rowA = svgEl('g', {}, bs);
      g.fA = frame(g.rowA, yA, 'rgba(245,180,60,.35)');
      g.aS1r = seg(g.rowA, yA, SHADE.S1); g.aS2r = seg(g.rowA, yA, SHADE.S2a);
      g.aS1r.setAttribute('width', ROWA.S1 * L); g.aS2r.setAttribute('x', x0 + ROWA.S1 * L); g.aS2r.setAttribute('width', ROWA.S2 * L);
      var lA1 = lab(g.rowA, x0, yA + H + 34, 'S1', C.allow); lA1.v.textContent = fmt(ROWA.S1, 4);
      var lA2 = lab(g.rowA, x0 + L, yA + H + 34, 'S2', C.allow, 'end'); lA2.v.textContent = fmt(ROWA.S2, 4);
      var ldA = svgEl('polyline', { points: (x0 + L - ROWA.S2 * L / 2) + ',' + (yA + H + 2) + ' ' + (x0 + L - ROWA.S2 * L / 2) + ',' + (yA + H + 12), stroke: C.ink3, fill: 'none', 'stroke-width': 1.2 }, g.rowA);
      void ldA;
      /* row T (S2 first, so that the two S2 pieces meet in the mixed row) */
      g.rowT = svgEl('g', {}, bs);
      g.fT = frame(g.rowT, yT, 'rgba(60,196,255,.35)');
      g.tS2r = seg(g.rowT, yT, SHADE.S2b); g.tRr = seg(g.rowT, yT, SHADE.R);
      g.tS2r.setAttribute('width', ROWT.S2 * L); g.tRr.setAttribute('x', x0 + ROWT.S2 * L); g.tRr.setAttribute('width', ROWT.R * L);
      var lT1 = lab(g.rowT, x0, yT + H + 34, 'S2', C.xfer); lT1.v.textContent = fmt(ROWT.S2, 4);
      var lT2 = lab(g.rowT, x0 + L, yT + H + 34, 'R', C.xfer, 'end'); lT2.v.textContent = fmt(ROWT.R, 4);
      g.lT1 = lT1; g.lT2 = lT2;
      g.sumA = svgEl('text', { x: x0 + L + 16, y: yA + 30, fill: C.ink2, 'font-size': 21, 'class': 'tnum' }, g.rowA); g.sumA.textContent = '= 1';
      g.sumT = svgEl('text', { x: x0 + L + 16, y: yT + 30, fill: C.ink2, 'font-size': 21, 'class': 'tnum' }, g.rowT); g.sumT.textContent = '= 1';
      /* mixed row */
      g.rowM = svgEl('g', {}, bs);
      g.mS1 = seg(g.rowM, yM, SHADE.S1); g.mS2a = seg(g.rowM, yM, SHADE.S2a); g.mS2b = seg(g.rowM, yM, SHADE.S2b); g.mR = seg(g.rowM, yM, SHADE.R);
      g.fM = svgEl('rect', { x: x0 - 3, y: yM - 3, width: L + 6, height: H + 6, rx: 8, fill: 'none', stroke: C.cpr, 'stroke-width': 3 }, g.rowM);
      g.lM = { S1: lab(g.rowM, x0, yM + H + 40, 'S1', C.allow), S2: lab(g.rowM, x0 + L / 2, yM + H + 40, 'S2', C.cpr, 'middle'), R: lab(g.rowM, x0 + L, yM + H + 40, 'R', C.xfer, 'end') };
      g.ldM = { S1: leader(g.rowM), S2a: leader(g.rowM), S2b: leader(g.rowM), R: leader(g.rowM) };
      g.sumM = svgEl('text', { x: x0 + L + 16, y: yM + 30, fill: C.ink, 'font-size': 23, 'font-weight': 700, 'class': 'tnum' }, g.rowM); g.sumM.textContent = '= 1';
      g.mix = { lam: 0.5, t: 1, norm: 0 };
      g.render = function () { mixRender(g); };
      g.render();
      gsap.set([g.rowA, g.rowT, g.rowM, q(el, '#tA'), q(el, '#tT'), q(el, '#tM'), q(el, '#call')], { autoAlpha: 0 });
      /* clones that fly into the mixed row */
      g.cloneA = g.rowA.cloneNode(true); g.cloneT = g.rowT.cloneNode(true);
      [g.cloneA, g.cloneT].forEach(function (c) {
        Array.prototype.slice.call(c.querySelectorAll('text, polyline')).forEach(function (n) { n.parentNode.removeChild(n); });
        bs.appendChild(c); gsap.set(c, { autoAlpha: 0 });
      });
      /* dial (G13), λ symbol card, caption */
      g.dialbox = q(el, '#dialbox');
      g.dial = Comp.dial(ctx, g.dialbox, { value: 1, size: 240 });
      g.lcard = Comp.symbolCard(ctx, q(el, '#lcard'), { tex: '\\lambda', desc: 'mixing weight', hidden: true });
      g.lcap = q(el, '#lcap'); gsap.set(g.lcap, { autoAlpha: 0 });
      /* derivation */
      g.D = Comp.derive(ctx, q(el, '#d3'), { head: 'Derivation', lines: [
        { tex: '\\ca{0.9756}+\\ca{0.0244}=1', note: 'Allowance row: the cap example from 05 (20,000 and 500 USD)' },
        { tex: '\\ct{0.1488}+\\ct{0.8512}=1', note: 'Transfer row: 300×0.5 = 150 · 1,000×0.858 = 858' },
        { tex: '\\begin{aligned}\\text{S1}&=0.5\\times\\ca{0.9756}=0.4878\\\\ \\text{S2}&=0.5\\times\\ca{0.0244}+0.5\\times\\ct{0.1488}=0.0866\\\\ \\text{R}&=0.5\\times\\ct{0.8512}=0.4256\\end{aligned}', note: 'Mixing at λ = 0.5: half of each row' },
        { tex: '\\part{s}{\\lambda\\times1+(1-\\lambda)\\times1}=1', note: 'so the mixed row always adds up to 1 as well', mark: 's' },
        { tex: '\\frac{\\lambda\\times1+0}{\\part{dl}{\\lambda}}=1', note: 'No transfer edges: the sum is only λ → divide by λ, the divisor $D_\\lambda(u)$', mark: 'dl' }
      ] });
      Deck.renderMath(g.D.el);
      gsap.set(g.D.el, { autoAlpha: 0 });
      g.fin = q(el, '#fin'); g.cases = q(el, '#cases');
      gsap.set([g.fin, g.cases], { autoAlpha: 0 });
      g.xnote = document.createElement('div'); g.xnote.className = 's6-xnote';
      g.xnote.style.left = (B3.x + B3.x0 + 40) + 'px'; g.xnote.style.top = (B3.y + B3.rows[1] + 7) + 'px';
      g.xnote.textContent = 'No transfer edges → empty row';
      el.appendChild(g.xnote); gsap.set(g.xnote, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      settleShared(ctx, g.dialbox, 'lambda-dial');
      tl.fromTo([g.s1.g, g.s2.g, g.r.g], { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp, stagger: 0.08 }, 0.25);
      tl.add(g.u.pop(), 0.2);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.add(g.aS1.draw({ duration: 0.6 }), 0);
        tl.add(g.aS2.draw({ duration: 0.6 }), 0.15);
        tl.fromTo(q(el, '#tA'), { autoAlpha: 0, x: -20 }, { autoAlpha: 1, x: 0, duration: 0.45, ease: E.out }, 0.5);
        tl.set(g.rowA, { autoAlpha: 1 }, 0.6);
        tl.fromTo([g.aS1r, g.aS2r], { scaleX: 0, svgOrigin: B3.x0 + ' ' + B3.rows[0] }, { scaleX: 1, duration: 0.8, ease: E.out }, 0.6);
        tl.fromTo(g.D.el, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.7);
        tl.fromTo([g.lS1, g.lS2a], { autoAlpha: 0, x: 10 }, { autoAlpha: 1, x: 0, duration: 0.4, stagger: 0.12 }, 0.55);
        tl.add(g.D.show(1), 0.9);
      }
      if (i === 2) {
        tl.add(g.tS2.draw({ duration: 0.6 }), 0);
        tl.add(g.tR.draw({ duration: 0.6 }), 0.15);
        tl.fromTo(q(el, '#tT'), { autoAlpha: 0, x: -20 }, { autoAlpha: 1, x: 0, duration: 0.45, ease: E.out }, 0.5);
        tl.set(g.rowT, { autoAlpha: 1 }, 0.6);
        tl.fromTo([g.tS2r, g.tRr], { scaleX: 0, svgOrigin: B3.x0 + ' ' + B3.rows[1] }, { scaleX: 1, duration: 0.8, ease: E.out }, 0.6);
        tl.fromTo([g.lS2b, g.lR], { autoAlpha: 0, x: 10 }, { autoAlpha: 1, x: 0, duration: 0.4, stagger: 0.12 }, 0.55);
        tl.add(g.D.show(2), 0.9);
      }
      if (i === 3) {
        /* λ = 0.5: both rows squash and fly into the mixed row */
        var dy = B3.rows[2] - B3.rows[0], dyT = B3.rows[2] - B3.rows[1];
        tl.add(g.dial.set(0.5, { duration: 0.6 }), 0);
        tl.add(g.lcard.pop(), 0.2);
        tl.fromTo(q(el, '#tM'), { autoAlpha: 0, x: -20 }, { autoAlpha: 1, x: 0, duration: 0.45, ease: E.out }, 0.4);
        tl.set([g.cloneA, g.cloneT], { autoAlpha: 1 }, 0.5);
        tl.fromTo(g.cloneA, { x: 0, y: 0, scaleX: 1 }, { y: dy, scaleX: 0.5, svgOrigin: B3.x0 + ' ' + B3.rows[0], duration: 1.0, ease: E.io }, 0.5);
        tl.fromTo(g.cloneT, { x: 0, y: 0, scaleX: 1 }, { x: B3.L * 0.5, y: dyT, scaleX: 0.5, svgOrigin: B3.x0 + ' ' + B3.rows[1], duration: 1.0, ease: E.io }, 0.62);
        tl.call(function () { g.mix.lam = 0.5; g.mix.t = 1; g.mix.norm = 0; g.render(); }, null, 1.6);
        tl.set(g.rowM, { autoAlpha: 1 }, 1.62);
        tl.set([g.cloneA, g.cloneT], { autoAlpha: 0 }, 1.64);
        tl.fromTo(g.fM, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 1.62);
        tl.fromTo(g.sumM, { scale: 1.6, transformOrigin: '0% 50%' }, { scale: 1, duration: 0.45, ease: E.stamp, immediateRender: false }, 1.8);
        tl.add(g.D.show(3), 1.7);
        tl.add(g.D.show(4), 3.2);
      }
      if (i === 4) {
        /* sweep the dial: the mixed row follows (1 → allowance row, 0 → transfer row) */
        var seq = [0.25, 0.75, 1, 0, 0.5], t = 0.2;
        tl.fromTo(g.lcap, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 0);
        seq.forEach(function (v) {
          tl.add(g.dial.set(v, { duration: 0.8 }), t);
          tl.to(g.mix, { lam: v, duration: 0.8, ease: E.io, onUpdate: g.render }, t);
          t += 1.05;
        });
        tl.call(g.render, null, t);
      }
      if (i === 5) {
        /* u has allowance arrows only: the row shrinks to λ, then D_λ = λ stretches it back to 1 */
        tl.add(g.tS2.cut(), 0);
        tl.add(g.tR.cut(), 0.1);
        tl.to([g.lS2b, g.lR], { autoAlpha: 0, duration: 0.3 }, 0.1);
        /* the transfer row empties with its arrows: o_T(u) = 0, nothing to share out */
        tl.to([g.tS2r, g.tRr], { scaleX: 0, svgOrigin: B3.x0 + ' ' + B3.rows[1], duration: 0.6, ease: E.io }, 0.2);
        tl.call(function () { g.lT1.v.textContent = '0'; g.lT2.v.textContent = '0'; g.sumT.textContent = '= 0'; g.sumT.setAttribute('fill', C.hi); }, null, 0.6);
        tl.set(g.fT, { attr: { 'stroke-dasharray': '7 6' } }, 0.6);
        tl.fromTo(g.xnote, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: E.out }, 0.7);
        tl.to(g.mix, { t: 0, duration: 0.7, ease: E.io, onUpdate: g.render }, 0.5);
        tl.set(g.fM, { attr: { stroke: C.hi, 'stroke-dasharray': '7 6' } }, 1.2);
        tl.fromTo(g.sumM, { scale: 1.5, transformOrigin: '0% 50%' }, { scale: 1, duration: 0.4, ease: E.stamp, immediateRender: false }, 1.2);
        tl.to(g.mix, { norm: 1, duration: 0.7, ease: E.io, onUpdate: g.render }, 2.0);
        tl.set(g.fM, { attr: { stroke: C.cpr, 'stroke-dasharray': 'none' } }, 2.7);
        tl.call(g.render, null, 2.72);
        tl.add(g.D.show(5), 2.1);
        tl.fromTo(q(el, '#call'), { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 2.8);
        tl.call(function () { ctx.add(function () { var h = q(el, '#call .hl'); if (h) gsap.fromTo(h, { '--hl-x': 0 }, { '--hl-x': 1, duration: 0.5, ease: 'power2.inOut' }); }); }, null, 3.1);
      }
      if (i === 6) {
        tl.fromTo(g.fin, { autoAlpha: 0, y: 26 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out }, 0.35);
        tl.fromTo(g.cases, { autoAlpha: 0, y: 26 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out }, 0.55);
        tl.fromTo(g.cases.querySelectorAll('tr'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, stagger: 0.12 }, 0.7);
        tl.to(g.D.el, { autoAlpha: 0, y: -16, duration: 0.4, ease: E['in'] }, 0);
        tl.to([g.rowA, g.rowT, g.rowM, q(el, '#tA'), q(el, '#tT'), q(el, '#tM'), q(el, '#call'), g.xnote, g.lcard.el, g.lcap], { autoAlpha: 0.2, duration: 0.5, ease: E.io }, 0.1);
      }
    }
  };
  function mixRender(g) {
    var s = g.mix, L = B3.L, x0 = B3.x0, yM = B3.rows[2], H = B3.h;
    var A = s.lam, T = (1 - s.lam) * s.t, D = A + T;
    var k = D > 1e-9 ? 1 + (1 / D - 1) * s.norm : 1;
    var w = [A * ROWA.S1 * k * L, A * ROWA.S2 * k * L, T * ROWT.S2 * k * L, T * ROWT.R * k * L];
    var rects = [g.mS1, g.mS2a, g.mS2b, g.mR], x = x0;
    rects.forEach(function (r, j) { r.setAttribute('x', x.toFixed(2)); r.setAttribute('width', Math.max(0, w[j]).toFixed(2)); x += w[j]; });
    var total = x - x0;
    g.fM.setAttribute('width', (total + 6).toFixed(2));
    var vS1 = A * ROWA.S1 * k, vS2 = (A * ROWA.S2 + T * ROWT.S2) * k, vR = T * ROWT.R * k;
    function nice(v) { return v < 5e-5 ? '0' : fmt(v, 4); }
    g.lM.S1.v.textContent = nice(vS1); g.lM.S2.v.textContent = nice(vS2); g.lM.R.v.textContent = nice(vR);
    var sum = (A + T) * k;
    g.sumM.textContent = '= ' + (Math.abs(sum - 1) < 5e-4 ? '1' : fmt(sum, 2));
    g.sumM.setAttribute('x', (x0 + Math.max(total, 0) + 16).toFixed(1));
    g.sumM.setAttribute('fill', Math.abs(sum - 1) < 5e-4 ? C.ink : C.hi);
    /* leaders from segment centres to the fixed label slots */
    var yb = yM + H + 3, yl = yM + H + 18;
    var cS1 = x0 + w[0] / 2, cS2a = x0 + w[0] + w[1] / 2, cS2b = x0 + w[0] + w[1] + w[2] / 2, cR = x0 + w[0] + w[1] + w[2] + w[3] / 2;
    function pl(n, cx, tx) { n.setAttribute('points', cx.toFixed(1) + ',' + yb + ' ' + cx.toFixed(1) + ',' + (yb + 6) + ' ' + tx.toFixed(1) + ',' + yl); }
    pl(g.ldM.S1, cS1, x0 + 22); pl(g.ldM.S2a, cS2a, x0 + L / 2); pl(g.ldM.S2b, cS2b, x0 + L / 2); pl(g.ldM.R, cR, x0 + L - 22);
    g.ldM.S1.style.opacity = w[0] > 0.5 ? 1 : 0; g.ldM.S2a.style.opacity = w[1] > 0.3 ? 1 : 0; g.ldM.S2b.style.opacity = w[2] > 0.3 ? 1 : 0; g.ldM.R.style.opacity = w[3] > 0.5 ? 1 : 0;
  }

  /* ================================================================ s06-04
     The representative scene: 15,107 contracts of the matched cohort. x = log10(1 + in-approve
     degree), z = log10(1 + transfer in-degree), y = percentile of the C-PR(λ) score in the cohort;
     contracts that a layer leaves out (score 0) rest on the floor plate. The dial snaps to the five
     computed values of λ only. No address or contract name is ever shown. */
  var V4 = { top: 150, h: 790 };
  var slide4 = {
    id: 's06-04', title: 'Turning λ: 15,107 contracts move', time: 70, steps: 6,
    tags: ['construct'],
    notes: [
      'This scene is the key picture of this talk. All 15,107 real contracts are in it. Across is the in-approve degree, and depth is the transfer in-degree. Both are on log scales, so each step on the scale is ten times the one before. Height is the percentile of the C-PR score, that is, the score rank turned into 0 to 100, with 100 at the top. With ranks we can compare on the same scale even though the size of the scores differs for each λ. On the two back walls we cast the shadow of the cloud. The right wall shows the in-approve degree against the score, and the left wall the transfer in-degree against the score. If a shadow is a thin band, the score follows that count closely; if it is a spread-out cloud, it does not. Right now the dial is at 1, the score that walks only the allowance layer, so the shadow on the allowance wall is close to a band. The bars at the top right show how far the score order matches each count. 0 means no relation and 1 means the same order. I will explain how this is measured in 07.',
      'If we set λ to 0, the walk uses only the transfer layer. Now the shadow on the left wall, the transfer wall, gets close to a band, and the shadow on the allowance wall spreads out. The 2,670 contracts that are not in the transfer graph fall to the floor. On the bars, it is 0.689 with the transfer in-degree and 0.262 with the in-approve degree.',
      'Raising λ to 0.25 changes a lot. Most of the contracts that were on the floor rise up, and only the 80 that are in neither graph stay there. The shadows on both walls are half spread out, and the two bars meet around the middle.',
      'At 0.5 almost nothing moves. It looks much like 0.25.',
      'At 0.75, too, it moves only a little.',
      'At 1 it jumps a lot again and lines up with the allowance-side count. The shadow on the allowance wall gets close to a band again, and it is 0.654 with the in-approve degree. The 523 contracts that are not in the allowance graph go to the floor.',
      'The big jumps at the ends happen because at exactly 0 or 1 only one layer is walked, so the set of nodes itself changes. Between 0 and 1, a node with only one kind of edge follows that path 100% of the time. So this formula is not continuous at the end points. Please also keep in mind that these numbers are a same-window check, so part of the agreement is built in by the way the scores are made. If you drag the dial you can move between the five computed values, and you can drag the cloud to rotate it.'
    ],
    html:
      '<h1 class="t-h1">Turning λ changes [[which count]] the score follows</h1>' +
      '<div class="abs" id="three" data-in="none" style="left:0;top:' + V4.top + 'px;width:1920px;height:' + V4.h + 'px"></div>' +
      '<div class="abs" id="dialbox" data-shared="lambda-dial" data-in="none" style="left:96px;top:176px;width:240px;height:180px"></div>' +
      '<div class="abs s6-cap" id="dialcap" style="left:96px;top:362px;width:300px;line-height:28px">λ = 0: transfer layer alone<br>λ = 1: allowance layer alone<br><span class="ink-3" style="font-size:18px">drag the dial (five values only)</span></div>' +
      '<div class="abs s6-hudp" id="hudp" style="left:1384px;top:176px;width:440px">' +
        '<div class="q">Agreement of the score order with</div>' +
        '<div class="m"><span class="k c-allow">In-approve<br>degree</span><span class="bar c-allow"><i id="ma"></i></span><span class="v c-allow" id="va">0.654</span></div>' +
        '<div class="m"><span class="k c-xfer">Transfer<br>in-degree</span><span class="bar c-xfer"><i id="md"></i></span><span class="v c-xfer" id="vd">0.183</span></div>' +
        '<div class="sc"><span>0 none</span><span>1 same order</span></div>' +
        '<div class="nt">Kendall’s τ · how it is measured: 07</div>' +
        '<div class="z">On the floor (score 0): <b id="vz">523</b> contracts</div></div>' +
      '<div class="abs s6-read" id="read" style="left:96px;top:456px;width:420px">' +
        '<div class="hd">How to read</div>' +
        '<div class="r"><b>Percentile</b><span>score rank 0–100 (100 at the top)</span></div>' +
        '<div class="r"><b>Log scale</b><span>10 → 100 → 1,000: one step = ×10</span></div>' +
        '<div class="r"><b>Wall shadow</b><span>thin band = follows the count<br>wide cloud = does not follow</span></div></div>' +
      '<p class="abs s6-capline" id="cap0" style="left:96px;top:930px;width:1270px">One dot = one contract · across <b class="c-allow">in-approve degree</b> · depth <b class="c-xfer">transfer in-degree</b> (both log) · height <b class="c-cpr">C-PR percentile</b></p>' +
      '<p class="abs s6-capline" id="cap6" data-in="none" style="left:96px;top:912px;width:1240px;color:var(--ink)">Big jumps at the ends: λ = 0 and 1 walk one layer alone, so the node set changes. Not continuous.</p>' +
      '<div class="abs s6-mini ink-2" id="mini" style="left:1384px;top:902px;width:440px;text-align:right">$P^{(\\lambda)}_{u,\\cdot}=\\alpha_A(u)\\,\\ca{P_{A,u,\\cdot}}+\\alpha_T(u)\\,\\ct{P_{T,u,\\cdot}}$</div>',
    build: function (el, ctx) {
      var g = ctx.g = { j: 4 };
      g.dialbox = q(el, '#dialbox');
      g.fromDial = !!(ctx.prev && ctx.prev.rect && ctx.prev.rect('lambda-dial'));
      g.dial = Comp.dial(ctx, g.dialbox, { value: g.fromDial ? 0.5 : 1, size: 240, interactive: true, onChange: function (v) {
        var j = Comp.data.lambdas.indexOf(v); if (j < 0) return;
        ctx.add(function () { setLambda(ctx, j, false); });
      } });
      g.vd = q(el, '#vd'); g.va = q(el, '#va'); g.vz = q(el, '#vz'); g.md = q(el, '#md'); g.ma = q(el, '#ma');
      var L0 = LAM[4];   /* the cloud and the HUD start at λ = 1 */
      gsap.set(g.ma, { width: nums(L0.a)[0] * 100 + '%' }); gsap.set(g.md, { width: nums(L0.d)[0] * 100 + '%' });
      g.cap6 = q(el, '#cap6'); gsap.set(g.cap6, { autoAlpha: 0 });
      var K = Comp.data.contracts(); if (!K) return;
      var n = K.n, i, keys = Comp.data.lambdaKeys, lams = Comp.data.lambdas;
      var xa = new Float32Array(n), zt = new Float32Array(n), mxA = 0, mxZ = 0;
      for (i = 0; i < n; i++) {
        xa[i] = Math.log10(1 + K.raw.in_approve_degree[i]); zt[i] = Math.log10(1 + K.raw.in_degree[i]);
        if (xa[i] > mxA) mxA = xa[i]; if (zt[i] > mxZ) mxZ = zt[i];
      }
      var SPAN = 7, SX = SPAN / mxA, SZ = SPAN / mxZ, HY = 4.6, FLOOR = -0.42;   /* geometry of s03-06 */
      var grey = Comp.rgb(C.ink3);
      g.sets = keys.map(function (k, j) {
        var p = new Float32Array(n * 3), col = new Float32Array(n * 3), lc = Comp.rgb(Deck.util.lambdaColor(lams[j])), pc = K.pct[k];
        for (var i2 = 0; i2 < n; i2++) {
          var f = K.flags[i2], zero = lams[j] === 1 ? (f & 1) : lams[j] === 0 ? (f & 2) : f === 3;
          p[i2 * 3] = xa[i2] * SX - SPAN / 2; p[i2 * 3 + 1] = zero ? FLOOR + 0.03 : pc[i2] * HY; p[i2 * 3 + 2] = zt[i2] * SZ - SPAN / 2;
          var b = 0.3 + 0.7 * pc[i2];
          col[i2 * 3] = zero ? grey[0] * 0.55 : lc[0] * b; col[i2 * 3 + 1] = zero ? grey[1] * 0.55 : lc[1] * b; col[i2 * 3 + 2] = zero ? grey[2] * 0.55 : lc[2] * b;
        }
        return { p: p, c: col };
      });
      /* shadows on the two back walls: (allowance count, percentile) on the wall z = WZ and
         (transfer count, percentile) on the wall x = WX. A contract with score 0 casts no shadow
         (black under additive blending). */
      var WX = -SPAN / 2 - 0.3, WZ = -SPAN / 2 - 0.3, ca = Comp.rgb(C.allow), cx = Comp.rgb(C.xfer);
      g.shadow = keys.map(function (k, j) {
        var a = new Float32Array(n * 3), t = new Float32Array(n * 3), cA = new Float32Array(n * 3), cT = new Float32Array(n * 3), pc = K.pct[k];
        for (var i3 = 0; i3 < n; i3++) {
          var f = K.flags[i3], zero = lams[j] === 1 ? (f & 1) : lams[j] === 0 ? (f & 2) : f === 3;
          var yy = zero ? FLOOR + 0.03 : pc[i3] * HY, on = zero ? 0 : 1;
          a[i3 * 3] = xa[i3] * SX - SPAN / 2; a[i3 * 3 + 1] = yy; a[i3 * 3 + 2] = WZ + 0.03;
          t[i3 * 3] = WX + 0.03; t[i3 * 3 + 1] = yy; t[i3 * 3 + 2] = zt[i3] * SZ - SPAN / 2;
          cA[i3 * 3] = ca[0] * on; cA[i3 * 3 + 1] = ca[1] * on; cA[i3 * 3 + 2] = ca[2] * on;
          cT[i3 * 3] = cx[0] * on; cT[i3 * 3 + 1] = cx[1] * on; cT[i3 * 3 + 2] = cx[2] * on;
        }
        return { a: a, t: t, ca: cA, ct: cT };
      });
      g.geo = { WX: WX, WZ: WZ, SPAN: SPAN, HY: HY, FLOOR: FLOOR };
      g.delays = new Float32Array(n);
      for (i = 0; i < n; i++) g.delays[i] = xa[i] / mxA;
      var rnd = Deck.util.rng(42);
      g.rdel = new Float32Array(n);
      for (i = 0; i < n; i++) g.rdel[i] = rnd();
      var T = ctx.three(q(el, '#three'), { fov: 30, camera: { theta: 0.72, phi: 1.12, radius: 17.6, target: [0.3, 1.9, 0] }, autoRotate: 0, minRadius: 8, maxRadius: 60 });
      g.T = T;
      if (T.failed) return;
      Comp.floor(ctx, T, { size: 8, y: FLOOR, divisions: 8, opacity: 0.22 });
      var O = [-SPAN / 2 - 0.3, FLOOR, -SPAN / 2 - 0.3];
      Comp.axes3d(ctx, T, { origin: O, length: [SPAN + 0.9, HY + 0.9, SPAN + 0.9], colors: [C.allow, C.cpr, C.xfer], headRadius: 0.07, headLength: 0.24 });
      g.labs = [
        T.label('In-approve degree (log)', [O[0] + SPAN + 1.0, O[1], O[2]], { className: 's6-ax3d', anchor: 'left', dx: 14 }),
        T.label('C-PR percentile', [O[0], O[1] + HY + 0.9, O[2]], { className: 's6-ax3d', anchor: 'left', dx: 18, dy: 6 }),
        T.label('Transfer in-degree (log)', [O[0], O[1], O[2] + SPAN + 1.0], { className: 's6-ax3d', anchor: 'right', dx: -14 })
      ];
      g.labs[0].el.style.color = C.allow; g.labs[1].el.style.color = C.cpr; g.labs[2].el.style.color = C.xfer;
      [[10, '10'], [100, '100'], [1000, '1,000'], [10000, '10,000']].forEach(function (tv) {
        var lx = Math.log10(1 + tv[0]) * SX - SPAN / 2, lz = Math.log10(1 + tv[0]) * SZ - SPAN / 2;
        if (lx <= SPAN / 2) g.labs.push(T.label(tv[1], [lx, FLOOR, O[2] - 0.4], { className: 's6-tick3d' }));
        if (lz <= SPAN / 2) g.labs.push(T.label(tv[1], [O[0] - 0.4, FLOOR, lz], { className: 's6-tick3d' }));
      });
      [[0, '0'], [0.5, '50'], [1, '100']].forEach(function (tv) { g.labs.push(T.label(tv[1], [O[0] - 0.3, tv[0] * HY, O[2]], { className: 's6-tick3d', anchor: 'right' })); });
      g.labs.push(T.label('score 0 = floor plate', [SPAN / 2 + 0.2, FLOOR, SPAN / 2 + 0.6], { className: 's6-tick3d', anchor: 'left' }));
      /* emission point: in front of the camera, under the dial needle tip (λ = 1 points right) */
      var THREE = T.THREE, cam = T.camera;
      cam.updateMatrixWorld(); cam.updateProjectionMatrix();
      var tipX = 96 + 120 + 78, tipY = 176 + 126 - V4.top;
      var v = new THREE.Vector3(tipX / T.width * 2 - 1, -(tipY / T.height * 2 - 1), 0.5).unproject(cam);
      var dir = v.sub(cam.position).normalize();
      var o = cam.position.clone().add(dir.multiplyScalar(9));
      g.emit = new Float32Array(n * 3);
      for (i = 0; i < n; i++) {
        g.emit[i * 3] = o.x + (rnd() - 0.5) * 0.12; g.emit[i * 3 + 1] = o.y + (rnd() - 0.5) * 0.12; g.emit[i * 3 + 2] = o.z + (rnd() - 0.5) * 0.12;
      }
      /* the two back walls (translucent screens) and their shadows */
      var WW = SPAN + 0.3, WH = HY + 0.42 + 0.25, wy = FLOOR + WH / 2;
      g.walls = [];
      [[C.allow, [WX + WW / 2, wy, WZ], 0], [C.xfer, [WX, wy, WZ + WW / 2], Math.PI / 2]].forEach(function (w) {
        var grp = new THREE.Group();
        var pl = new THREE.Mesh(new THREE.PlaneGeometry(WW, WH), new THREE.MeshBasicMaterial({ color: new THREE.Color(C.bg3), transparent: true, opacity: 0.32, depthWrite: false, side: THREE.DoubleSide }));
        var fr = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(WW, WH)), new THREE.LineBasicMaterial({ color: new THREE.Color(w[0]), transparent: true, opacity: 0.35 }));
        grp.add(pl); grp.add(fr);
        grp.position.set(w[1][0], w[1][1], w[1][2]); grp.rotation.y = w[2];
        T.scene.add(grp);
        g.walls.push({ g: grp, mats: [pl.material, fr.material], o: [0.32, 0.35] });
        pl.material.opacity = 0; fr.material.opacity = 0;
      });
      g.shA = Comp.cloud(ctx, T, { positions: g.shadow[4].a, colors: g.shadow[4].ca, size: 2.2, opacity: 0.5 });
      g.shT = Comp.cloud(ctx, T, { positions: g.shadow[4].t, colors: g.shadow[4].ct, size: 2.2, opacity: 0.5 });
      if (g.shA.material) { g.shA.material.opacity = 0; g.shT.material.opacity = 0; }
      g.wallLabs = [
        T.label('Shadow: in-approve degree vs. score', [WX + WW * 0.5, FLOOR + WH + 0.18, WZ], { className: 's6-wall3d' }),   /* 0.5 (Korean 0.62): the longer English label stays clear of the HUD at λ = 0 */
        T.label('Shadow: transfer in-degree vs. score', [WX, FLOOR + WH + 0.18, WZ + WW * 0.62], { className: 's6-wall3d' })
      ];
      g.wallLabs[0].el.style.color = C.allow; g.wallLabs[1].el.style.color = C.xfer;
      g.wallLabs.forEach(function (L) { L.el.style.opacity = '0'; });
      g.cloud = Comp.cloud(ctx, T, { positions: g.emit, colors: g.sets[4].c, size: 3, opacity: 0.62 });
      if (g.cloud.points) g.cloud.points.visible = false;   /* shown when the burst from the needle tip starts */
      g.labs.forEach(function (L) { L.el.innerHTML = '<span class="s6-lin">' + L.el.innerHTML + '</span>'; L.el.style.opacity = '0'; });
      /* labels that project into the caption band fade out (the view turns and can be dragged) */
      T.onFrame(function () {
        var lim = T.height - 96;
        for (var k = 0; k < g.labs.length; k++) {
          var pr = T.project(g.labs[k].pos), o = Math.max(0, Math.min(1, (lim - pr.y) / 50)), inn = g.labs[k].el.firstChild;
          if ((pr.x > T.width - 560 || pr.x < 430) && pr.y < 300) o = 0;   /* under the HUD panel or the dial */
          if (pr.x < 640 && pr.y > 280 && pr.y < 480) o = 0;                 /* under the reading guide */
          if (inn && inn.__o !== o) { inn.style.opacity = o.toFixed(2); inn.__o = o; }
        }
      });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      var shared = settleShared(ctx, g.dialbox, 'lambda-dial');
      if (!g.cloud) return;
      var t0 = shared ? 1.75 : 0.4;
      if (g.fromDial) tl.add(g.dial.set(1, { duration: 0.7 }), t0 - 0.75);
      tl.fromTo(g.dial.el, { scale: 1 }, { scale: 1.06, duration: 0.18, yoyo: true, repeat: 1, transformOrigin: '50% 70%' }, t0 - 0.1);
      tl.call(function () { if (g.cloud.points) g.cloud.points.visible = true; }, null, t0);
      tl.add(g.cloud.morph(g.sets[4].p, { duration: 1.3, delays: g.rdel, spread: 1.2, ease: 'power3.out' }), t0);
      tl.to(g.labs.map(function (L) { return L.el; }), { opacity: 1, duration: 0.6, stagger: 0.02 }, t0 + 1.2);
      g.walls.forEach(function (w) { w.mats.forEach(function (m, k) { tl.to(m, { opacity: w.o[k], duration: 0.7 }, t0 + 1.3); }); });
      if (g.shA.material) tl.to([g.shA.material, g.shT.material], { opacity: 0.5, duration: 0.9 }, t0 + 1.5);
      tl.to(g.wallLabs.map(function (L) { return L.el; }), { opacity: 1, duration: 0.5, stagger: 0.15 }, t0 + 1.8);
    },
    step: function (el, i, ctx) {
      var g = ctx.g;
      if (i >= 1 && i <= 5) setLambda(ctx, i - 1, true);
      if (i === 6) {
        var tl = ctx.tl();
        tl.to(q(el, '#cap0'), { autoAlpha: 0, y: -10, duration: 0.3, ease: E['in'] }, 0);
        tl.fromTo(g.cap6, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.25);
        tl.add(g.dial.arc(0, 0.25, 'hi'), 0.5);
        tl.add(g.dial.arc(0.75, 1, 'hi'), 0.8);
      }
    }
  };
  /* the camera leans towards the wall whose shadow should tighten, but both walls stay in view */
  var CAM4 = [
    { theta: 1.02, phi: 1.14, radius: 18.8, target: [0.1, 1.6, 0.1] },   /* λ = 0: the transfer wall turns towards us */
    { theta: 0.78, phi: 1.12, radius: 18.2, target: [0.3, 1.7, 0] },
    { theta: 0.78, phi: 1.12, radius: 18.2, target: [0.3, 1.7, 0] },
    { theta: 0.78, phi: 1.12, radius: 18.2, target: [0.3, 1.7, 0] },
    { theta: 0.56, phi: 1.14, radius: 18.8, target: [0.2, 1.6, 0.1] }    /* λ = 1: the allowance wall turns towards us */
  ];
  function setLambda(ctx, j, fromStep) {
    var g = ctx.g, tl = ctx.tl(), prev = g.j == null ? 4 : g.j;
    var Lp = LAM[prev], Ln = LAM[j];
    g.j = j;
    if (fromStep) tl.add(g.dial.set(Ln.v, { duration: 0.9 }), 0);
    if (g.cloud) {
      tl.add(g.cloud.morph(g.sets[j].p, { duration: 1.4, delays: g.delays, spread: 0.7, ease: E.io }), 0.1);
      tl.add(g.cloud.recolor(g.sets[j].c, { duration: 1.0, delays: g.delays, spread: 0.5 }), 0.1);
      tl.add(g.shA.morph(g.shadow[j].a, { duration: 1.4, delays: g.delays, spread: 0.7, ease: E.io }), 0.1);
      tl.add(g.shT.morph(g.shadow[j].t, { duration: 1.4, delays: g.delays, spread: 0.7, ease: E.io }), 0.1);
      tl.add(g.shA.recolor(g.shadow[j].ca, { duration: 0.8, delays: g.delays, spread: 0.5 }), 0.1);
      tl.add(g.shT.recolor(g.shadow[j].ct, { duration: 0.8, delays: g.delays, spread: 0.5 }), 0.1);
      if (fromStep && (prev !== j)) tl.add(g.T.cameraTo(CAM4[j], { duration: 1.8 }), 0.15);
    }
    /* τ_b point values only (digest strings); the intervals come in s07 */
    var a0 = nums(Lp.d), a1 = nums(Ln.d), b0 = nums(Lp.a), b1 = nums(Ln.a);
    tl.add(ctx.count(g.vd, a0[0], a1[0], { decimals: 3, final: fmt(a1[0], 3), duration: 1.2 }), 0.3);
    tl.add(ctx.count(g.va, b0[0], b1[0], { decimals: 3, final: fmt(b1[0], 3), duration: 1.2 }), 0.3);
    tl.fromTo(g.md, { width: a0[0] * 100 + '%' }, { width: a1[0] * 100 + '%', duration: 1.2, ease: E.io }, 0.3);
    tl.fromTo(g.ma, { width: b0[0] * 100 + '%' }, { width: b1[0] * 100 + '%', duration: 1.2, ease: E.io }, 0.3);
    tl.add(ctx.count(g.vz, Lp.zeros, Ln.zeros, { decimals: 0, final: fmt(Ln.zeros, 0), duration: 1.2 }), 0.3);
  }

  /* ================================================================ s06-05
     S-PR: walk the transfer layer, restart where the allowance score is. Teleport rain first
     falls evenly, then only on the nodes with an amber (allowance-score) halo. */
  var G5 = { x: 96, y: 190, w: 900, h: 720 };
  var N5 = [
    { id: 'c1', x: 250, y: 330, kind: 'contract', rA: 0.32 }, { id: 'c2', x: 560, y: 300, kind: 'contract', rA: 0.2 },
    { id: 'c3', x: 420, y: 560, kind: 'contract', rA: 0 },    { id: 'c4', x: 760, y: 520, kind: 'contract', rA: 0.13 },
    { id: 'e1', x: 90, y: 470, kind: 'eoa', rA: 0.05 },       { id: 'e2', x: 130, y: 640, kind: 'eoa', rA: 0.04 },
    { id: 'e3', x: 640, y: 660, kind: 'eoa', rA: 0 },         { id: 'e4', x: 820, y: 330, kind: 'eoa', rA: 0.05 },
    { id: 'e5', x: 380, y: 420, kind: 'eoa', rA: 0.03 }
  ];
  var E5 = [['e1', 'c1'], ['e2', 'c1'], ['c1', 'c2'], ['e5', 'c2'], ['e5', 'c3'], ['e2', 'c3'], ['c3', 'c4'], ['e3', 'c4'], ['e4', 'c2'], ['c2', 'c4']];
  var slide5 = {
    id: 's06-05', title: 'S-PR: allowances only set the starting points', time: 45, steps: 4,
    tags: function (step) { return step >= 3 ? ['example', 'posthoc'] : ['example']; },
    notes: [
      'The fourth is S-PR, endorsement-seeded PageRank. S-PR is an ablation experiment. It is a score that walks the transfer graph, but it teleports to different places. For now, the restart rain falls evenly on every node.',
      'Now the rain gathers where there is an allowance score, on the nodes with an amber halo. The bigger the halo, the heavier the rain. No rain falls on nodes without an allowance score. This has the same form as TrustRank, which fights web spam, but instead of seeds picked by people it uses the allowance score as the seed.',
      'As a formula: for each node of the transfer graph, the restart share is the score from walking the allowance layer alone, divided again so that the shares add up to 1.',
      'To preview the results a little: in W0, S-PR did about as well on new transfer senders as walking the transfer layer alone, but it did worse on new approval pairs than walking the allowance layer alone. These two comparisons are post hoc, computed after the labels were seen. We will see how the difference is measured in 07.',
      'So allowance edges help when the walk actually moves along them, and they help little when they only set the starting points.'
    ],
    html:
      '<h1 class="t-h1">Allowances as [[seeds]], transfers as paths</h1>' +
      '<svg class="abs" id="g5" data-in="none" width="' + G5.w + '" height="' + G5.h + '" style="left:' + G5.x + 'px;top:' + G5.y + 'px;overflow:visible"></svg>' +
      '<div class="abs s6-lines" style="left:1060px;top:196px;width:764px">' +
        '<p class="l">Walk the transfer layer, but let the allowance score decide where to restart</p>' +
        '<p class="l" data-step="1">Same form as TrustRank<small>seeds from the allowance layer walked alone, not picked by people</small></p></div>' +
      '<div class="abs s6-eq5" data-step="2" style="left:1060px;top:400px;width:764px">' +
        '$$\\cc{\\pi_u}=\\frac{\\ca{r_{A,u}}}{\\sum_{v\\in V_T}\\ca{r_{A,v}}}\\qquad(u\\in V_T)$$' +
        '<div class="nt">On the nodes of the transfer graph, the allowance score $\\ca{\\mathbf r_A}$ divided again to sum to 1 · 0 for a node not in the allowance graph</div></div>' +
      '<div class="abs" id="fp5" data-in="none" style="left:1060px;top:640px;width:764px">' +
        '<div class="s6-fhead"><span>Preview · W0 · post hoc comparison</span>' + Deck.tagHTML('posthoc') + '</div>' +
        '<div class="s6-verd" id="v5a"><span class="ic c-xfer">≈</span><span><b class="c-xfer">New transfer senders</b>close to the transfer layer alone</span></div>' +
        '<div class="s6-verd" id="v5b"><span class="ic c-hi">↓</span><span><b class="c-allow">New approval pairs</b>worse than the allowance layer alone</span></div>' +
        '<div class="s6-fnote">How the difference is measured: see 07</div></div>' +
      '<p class="abs s6-concl" data-step="4" style="left:96px;top:922px;width:1220px">Allowance edges help as paths to walk, but little as starting points only</p>',
    build: function (el, ctx) {
      var g = ctx.g = { w: N5.map(function () { return 1 / N5.length; }) };
      var svg = q(el, '#g5');
      g.svg = svg;
      /* halos (allowance score) behind the graph */
      g.halo = {};
      N5.forEach(function (n) {
        if (!n.rA) return;
        g.halo[n.id] = svgEl('circle', { cx: n.x, cy: n.y, r: 18 + 120 * n.rA, fill: 'rgba(245,180,60,.14)', stroke: 'rgba(245,180,60,.55)', 'stroke-width': 1.5 }, svg);
      });
      gsap.set(Object.keys(g.halo).map(function (k) { return g.halo[k]; }), { autoAlpha: 0 });
      g.G = Comp.graph(ctx, svg, {
        nodes: N5.map(function (n) { return { id: n.id, x: n.x, y: n.y, kind: n.kind, size: n.kind === 'contract' ? 56 : 13 }; }),
        edges: E5.map(function (e) { return { from: e[0], to: e[1], kind: 'xfer', width: 2.5 }; }),
        showWeights: false, hidden: true
      });
      g.ex = svgEl('text', { x: 0, y: G5.h - 30, fill: C.ink2, 'font-size': 20 }, svg); g.ex.textContent = 'amber halo = score of the allowance layer walked alone (example)';
      gsap.set(g.ex, { autoAlpha: 0 });
      /* rain: a pool of drops and ripples */
      g.rainG = svgEl('g', {}, svg);
      g.drops = [];
      for (var k = 0; k < 34; k++) {
        var ln = svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 16, stroke: '#E3F3FF', 'stroke-width': 2.5, 'stroke-linecap': 'round', opacity: 0 }, g.rainG);
        g.drops.push({ el: ln, t: -((k * 0.379) % 1), node: 0, x: 0, y0: 0, y1: 0, v: 0 });
      }
      g.rip = [];
      for (var r = 0; r < 14; r++) g.rip.push({ el: svgEl('ellipse', { cx: 0, cy: 0, rx: 0, ry: 0, fill: 'none', stroke: '#CFE9FF', 'stroke-width': 1.5, opacity: 0 }, g.rainG), t: 1 });
      g.ripN = 0;
      g.rain = { on: 0 };
      /* two post hoc verdicts in words (R§6 contrasts_after[2]: SPR_SEND, interval covers 0 → 'about the same';
         contrasts_after[1]: SPR_APPR, interval below 0 → 'worse'). Δτ and intervals are taught only in s07. */
      g.fp = q(el, '#fp5'); gsap.set(g.fp, { autoAlpha: 0 });
      g.v5 = [q(el, '#v5a'), q(el, '#v5b')]; gsap.set(g.v5, { autoAlpha: 0 });
      /* static rain for reduced motion */
      g.static = svgEl('g', {}, svg);
      gsap.set(g.static, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.add(g.G.drawIn({ stagger: 0.06 }), 0.2);
      tl.call(function () { g.G.edges.forEach(function (A) { A.flow(true); A.g.querySelectorAll('circle').forEach(function (c) { c.setAttribute('fill-opacity', 0.45); }); }); }, null, 1.4);
      tl.fromTo(g.ex, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 1.0);
      tl.to(g.rain, { on: 1, duration: 0.6 }, 1.2);
      startRain(ctx);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        var hal = Object.keys(g.halo).map(function (k) { return g.halo[k]; });
        tl.fromTo(hal, { autoAlpha: 0, scale: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.7, ease: E.out, stagger: 0.08 }, 0);
        var target = N5.map(function (n) { return n.rA; }), sum = target.reduce(function (s, v) { return s + v; }, 0);
        target = target.map(function (v) { return v / sum; });
        var from = g.w.slice(), st = { p: 0 };
        tl.to(st, { p: 1, duration: 0.8, ease: E.io, onUpdate: function () { g.w = from.map(function (v, k) { return v + (target[k] - v) * st.p; }); }, onComplete: function () { g.w = target.slice(); drawStaticRain(g); } }, 0.6);
      }
      if (i === 3) {
        tl.fromTo(g.fp, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
        tl.fromTo(g.v5, { autoAlpha: 0, x: 30 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: E.out, stagger: 0.45 }, 0.3);
        tl.fromTo(g.v5.map(function (v) { return v.querySelector('.ic'); }), { scale: 0.4 }, { scale: 1, duration: 0.4, ease: E.stamp, stagger: 0.45 }, 0.45);
      }
    }
  };
  function startRain(ctx) {
    var g = ctx.g;
    drawStaticRain(g);
    if (ctx.reduced) { gsap.set(g.static, { autoAlpha: 1 }); return; }
    var rnd = Deck.util.rng(7);
    function pick() {
      var r = rnd(), acc = 0;
      for (var k = 0; k < g.w.length; k++) { acc += g.w[k]; if (r <= acc) return k; }
      return g.w.length - 1;
    }
    ctx.raf(function (t, dt) {
      if (ctx.reduced) { g.rainG.style.opacity = 0; gsap.set(g.static, { autoAlpha: 1 }); return; }
      g.rainG.style.opacity = g.rain.on;
      for (var k = 0; k < g.drops.length; k++) {
        var d = g.drops[k];
        d.t += dt * (d.v || 1);
        if (d.t >= 1) {
          if (d.y1) { var R = g.rip[g.ripN++ % g.rip.length]; R.x = d.x; R.y = d.y1; R.t = 0; }
          var j = pick(), n = N5[j];
          if (g.w[j] < 1e-4) { d.t = -0.3; d.y1 = 0; d.el.setAttribute('opacity', 0); continue; }
          d.node = j; d.x = n.x + (rnd() - 0.5) * 34; d.y0 = 26 + rnd() * 50; d.y1 = n.y - (n.kind === 'contract' ? 34 : 18);
          d.v = 1.05 + rnd() * 0.5; d.t = 0;
        }
        if (d.t < 0 || !d.y1) { d.el.setAttribute('opacity', 0); continue; }
        var y = d.y0 + (d.y1 - d.y0) * d.t * d.t;
        d.el.setAttribute('x1', d.x.toFixed(1)); d.el.setAttribute('x2', d.x.toFixed(1));
        d.el.setAttribute('y1', (y - 16).toFixed(1)); d.el.setAttribute('y2', y.toFixed(1));
        d.el.setAttribute('opacity', (0.55 * Math.min(1, d.t * 4)).toFixed(2));
      }
      for (var r = 0; r < g.rip.length; r++) {
        var Rp = g.rip[r];
        if (Rp.t >= 1) { Rp.el.setAttribute('opacity', 0); continue; }
        Rp.t += dt * 2.2;
        Rp.el.setAttribute('cx', Rp.x); Rp.el.setAttribute('cy', Rp.y);
        Rp.el.setAttribute('rx', (4 + 18 * Rp.t).toFixed(1)); Rp.el.setAttribute('ry', (1.5 + 5 * Rp.t).toFixed(1));
        Rp.el.setAttribute('opacity', (0.5 * (1 - Rp.t)).toFixed(2));
      }
    });
  }
  function drawStaticRain(g) {
    while (g.static.firstChild) g.static.removeChild(g.static.firstChild);
    N5.forEach(function (n, k) {
      var cnt = Math.round(g.w[k] * 30);
      for (var m = 0; m < cnt; m++) {
        var x = n.x + ((m % 5) - 2) * 7, y = n.y - (n.kind === 'contract' ? 44 : 26) - Math.floor(m / 5) * 22 - (m % 2) * 9;
        svgEl('line', { x1: x, y1: y - 14, x2: x, y2: y, stroke: '#CFE9FF', 'stroke-width': 2, 'stroke-linecap': 'round', opacity: 0.45 }, g.static);
      }
    });
  }

  Deck.section({ id: 's06-methods', title: 'Four scores', slides: [slide1, slide2, slide3, slide4, slide5] });
})();
