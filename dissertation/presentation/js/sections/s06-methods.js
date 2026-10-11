/* =========================================================================
   s06-methods — 네 가지 점수 (STORYBOARD.md §2, s06-01 … s06-05)
   s06-01  엔도스랭크                  (small world turns amber, 4-line summary, powers-of-ten
                                        pull-back: the small world becomes one dot of the real graph)
   s06-02  AWP와 원시 차수 기준선       (transfer graph with activeness halos; tallies 正 count
                                        distinct owners / senders; "can PageRank clear the bar?")
   s06-03  C-PR: 두 갈림길 표를 섞어요  (two 100 % row bars squash by λ and 1−λ into one mixed row;
                                        dial sweep; one-layer node renormalised by D_λ; final formula)
   s06-04  λ를 돌리면 (대표 장면)       (three.js: 15,107 contracts, height = C-PR percentile,
                                        five λ values, HUD τ counters, draggable snapping dial)
   s06-05  S-PR                         (teleport rain follows the allowance halos; two post hoc
                                        interval bars)

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
   today, 300 USD 180 days ago, σ(0) = 0.8581) and s06-05 graph are 예시.
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
    '.s6-defs .d .k{flex:0 0 150px;font-size:22px;line-height:32px;color:var(--c-deg);font-weight:600}',
    '.s6-defs .d .katex{font-size:27px}',
    '.s6-defs .mi{font-size:18px;line-height:26px;color:var(--ink-3);margin-top:4px}',
    '.s6-bottom{font-size:30px;line-height:44px;font-weight:600}',
    '.s6-chip{position:absolute;padding:6px 16px;border-radius:18px;font-size:22px;line-height:30px;font-weight:700;background:var(--bg-3);border:2px solid currentColor;white-space:nowrap}',
    /* s06-03 */
    '.s6-lbl{position:absolute;white-space:nowrap;font-size:24px;line-height:32px;font-weight:600}',
    '.s6-lbl .katex{font-size:26px}',
    '.s6-callout{position:absolute;font-size:28px;line-height:40px;font-weight:600;white-space:nowrap}',
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
    '.s6-hudp{padding:16px 22px;border-radius:18px;background:rgba(10,13,20,.78);border:1px solid var(--line);pointer-events:none}',
    '.s6-hudp .r{display:flex;align-items:baseline;gap:14px;margin:4px 0;white-space:nowrap}',
    '.s6-hudp .k{flex:0 0 auto;font-size:22px;line-height:30px;width:230px}',
    '.s6-hudp .v{font-size:40px;line-height:48px;font-weight:700;font-variant-numeric:tabular-nums;width:110px}',
    '.s6-hudp .ci{font-family:var(--font-mono);font-size:18px;color:var(--ink-3);letter-spacing:0}',
    '.s6-hudp .z{margin-top:6px;padding-top:8px;border-top:1px solid var(--line);font-size:20px;line-height:28px;color:var(--ink-2)}',
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
    id: 's06-01', title: '엔도스랭크 (EndorseRank)', time: 40, steps: 3,
    tags: function (step) { return step >= 2 ? ['thesis-example', 'example'] : ['thesis-example']; },
    notes: [
      '이제 네 가지 점수를 소개할게요. 첫째가 이 논문이 제안한 엔도스랭크예요. 04에서 만든 작은 세계를 다시 가져왔어요. 이번에는 화살표가 모두 허락 화살표라서 호박색이에요. 걷는 사람은 100번 중 85번은 화살표를 따라가고, 15번은 아무 점으로나 순간 이동해요.',
      '엔도스랭크는 허락 그래프 위에서 지금까지 만든 페이지랭크를 그대로 돌린 거예요. 화살표는 주인에서 스펜더 계약으로 가고, 토큰마다 마지막 허락 하나만 써요. 무게는 AWP와 같은 시간 무게 곱하기 금액 무게이고, 다시 출발은 모든 점에서 똑같이 해요. 점수를 받는 쪽은 허락을 받은 계약이에요. 주인 A는 화살표의 출발점일 뿐 점수를 받지 않아요. B, C, D 위의 숫자는 논문 2장의 예에서 나온 값이에요.',
      '이제 작은 세계에서 실제 허락 그래프로 물러나 볼게요. 점 네 개짜리 세계가 점점 작아져서, 수많은 점 가운데 하나가 돼요. 실제 허락 그래프에는 점이 6,221,665개, 화살표가 11,210,114개 있어요. 여기 보이는 별자리 모양은 설명을 위한 그림이고, 개수만 실제 값이에요.',
      '한 가지 조심할 점이 있어요. 화살표가 담는 것은 마지막 허락의 금액과 시점이에요. 그 뒤에 계약이 토큰을 꺼내 써서 줄어든 허락 액수나, 2023년 10월 전에 한 허락은 보이지 않아요.'
    ],
    html:
      '<h1 class="t-h1">엔도스랭크 = [[허락]] 그래프 위의 페이지랭크</h1>' +
      '<div class="abs s6-zoom" id="zoom" data-in="none" style="left:' + ZW.x + 'px;top:' + ZW.y + 'px;width:' + ZW.w + 'px;height:' + ZW.h + 'px"></div>' +
      '<div class="abs s6-readout" id="readout" data-in="none" style="left:' + (ZW.x + 28) + 'px;top:' + (ZW.y + ZW.h - 128) + 'px">' +
        '<span class="k">점</span><span class="a">4 →</span><span class="v" id="rn">4</span>' +
        '<span class="k">화살표</span><span class="a">4 →</span><span class="v" id="re">4</span></div>' +
      '<div class="abs s6-fcard" id="fcard" style="left:1080px;top:190px;width:744px">' +
        '<div class="hd">정의 · 논문 3장</div><div id="fhost"></div>' +
        '<div class="nt">04의 페이지랭크 식에 허락 무게 $\\ca{w_A}$와 고른 $\\boldsymbol\\pi$를 넣어요</div></div>' +
      '<div class="abs s6-sum" id="sum" data-in="none" style="left:1080px;top:436px;width:744px">' +
        '<div class="ln"><span class="no">1</span><span class="tx">화살표: 주인 → 스펜더 계약<small>토큰마다 마지막 허락 · 다섯 토큰 · 달러</small></span></div>' +
        '<div class="ln"><span class="no">2</span><span class="tx">무게: AWP와 같은 σ × V<small>시간 무게 × 금액 무게 (05에서 만든 식)</small></span></div>' +
        '<div class="ln"><span class="no">3</span><span class="tx">다시 출발: 모든 점에 똑같이<small>$\\boldsymbol\\pi = 1/|V|$, 감쇠 계수 $d = ' + DAMP + '$</small></span></div>' +
        '<div class="ln"><span class="no">4</span><span class="tx">점수를 받는 쪽: 허락을 받은 계약<small>주인(EOA)은 화살표의 끝점일 뿐이에요</small></span></div>' +
      '</div>' +
      '<div class="abs s6-caution" data-step="3" style="left:1080px;top:842px;width:744px">' + ICON_WARN +
        '<span>화살표는 ‘마지막 허락의 금액과 시점’이에요 — 지금 남은 허락 액수가 아니에요</span></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var zoom = q(el, '#zoom');
      g.K = Comp.canvas(ctx, zoom, { w: ZW.w, h: ZW.h, x: 0, y: 0, onResize: function (K) { drawStars(K, g.Z || Z0); } });
      gsap.set(g.K.canvas, { autoAlpha: 0 });
      g.W = Comp.smallWorld(ctx, zoom, { x: WX, y: WY, hidden: true, shared: 'small-world',
        labels: { A: '주인 A', B: '금고 B', C: '금고 C', D: '대출 풀 D' } });
      g.W.wrap.style.transformOrigin = '380px 250px';
      g.dot = document.createElement('div'); g.dot.className = 's6-swdot'; g.dot.style.left = CX + 'px'; g.dot.style.top = CY + 'px';
      g.lab = document.createElement('div'); g.lab.className = 's6-swlab'; g.lab.style.left = (CX + 28) + 'px'; g.lab.style.top = (CY - 40) + 'px';
      g.lab.innerHTML = '작은 세계 (점 4개)<small>예시 별자리 · 개수만 실제 값</small>';
      zoom.appendChild(g.dot); zoom.appendChild(g.lab);
      gsap.set([g.dot, g.lab], { autoAlpha: 0 });
      g.F = Comp.formula(ctx, q(el, '#fhost'), '\\mathbf s_{\\mathrm{ER}}=\\mathrm{PageRank}\\bigl(\\part{g}{\\ca{G_{\\mathrm{approve}}}},\\ \\part{pi}{\\boldsymbol\\pi=\\tfrac{1}{|V|}\\mathbf 1},\\ \\part{d}{d=' + DAMP + '}\\bigr)', { display: true });
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
        /* 4: who gets a score: contracts B, C, D (thesis Ch. 2 example values), never the owner A */
        var WE = ((DATA.params || {}).worked_example || {}).thesis_values || {};
        var st = WE.stationary || [0.1375, 0.2154, 0.1765, 0.4706];
        tl.add(g.F.unmark('pi'), T0 + 2.85);
        ['B', 'C', 'D'].forEach(function (id, k) {
          tl.add(g.W.node(id).badge(fmt(st[k + 1], 4), { color: C.allow }), T0 + 2.95 + k * 0.12);
        });
        tl.add(g.W.node('A').tag('점수 안 받음'), T0 + 3.3);
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
    id: 's06-02', title: 'AWP와 원시 차수 기준선', time: 40, steps: 3,
    tags: function (step) { return step >= 1 ? ['example'] : []; },
    notes: [
      '둘째는 비교 대상인 AWP와, 그냥 센 수예요.',
      'AWP는 송금 그래프 위의 페이지랭크예요. Do와 동료들이 2023년에 만든 점수이고, 화살표는 송금이라서 동전이 흘러가요. 다시 출발하는 곳이 엔도스랭크와 달라요. 최근에 여러 상대에게 송금한 활발한 주소일수록 후광이 크고, 그만큼 더 자주 다시 출발해요. 그래프는 설명용 예시예요.',
      '그리고 이 연구에서 아주 중요한 비교 상대가 하나 더 있어요. 바로 화살표를 그냥 센 수예요. 허락 쪽은 그 계약에 마지막 허락이 0보다 큰 서로 다른 주인 수예요. 같은 주인이 두 번 허락해도 한 번만 세요. 송금 쪽은 송금을 보내온 서로 다른 주소 수예요. 시험 기간의 기준선은 자기 자신이 보낸 송금을 빼고 세요.',
      '페이지랭크는 결국 이 수를 매끄럽게 다듬은 값이라서, 그냥 센 수보다 나은 무엇을 주는지를 꼭 따져 봐야 해요. 이 질문은 결과 장에서 그대로 답할게요.'
    ],
    html:
      '<h1 class="t-h1">AWP = [[송금]] 그래프 위의 페이지랭크</h1>' +
      '<div class="abs s6-panel" id="pl" data-in="none" style="left:' + S2.L.x + 'px;top:' + S2.L.y + 'px;width:' + S2.L.w + 'px;height:' + S2.L.h + 'px">' +
        '<div class="hd c-xfer">AWP<small>Do 외, 2023</small></div>' +
        '<div class="sb">다시 출발: 활발함 $X_u$에 비례</div>' +
        '<svg id="gl" width="' + S2.L.w + '" height="420" style="left:0;top:140px"></svg>' +
        '<div class="s6-legend" id="lgl" style="top:560px">후광이 클수록 최근에 여러 상대에게 송금했어요<br>→ 그만큼 더 자주 다시 출발해요 &nbsp;&nbsp;$\\pi_u = X_u \\big/ \\textstyle\\sum_v X_v$</div>' +
      '</div>' +
      '<div class="abs s6-panel" id="pr" data-in="none" style="left:' + S2.R.x + 'px;top:' + S2.R.y + 'px;width:' + S2.R.w + 'px;height:' + S2.R.h + 'px">' +
        '<div class="hd">기준선 = 그냥 센 수<small>원시 차수</small></div>' +
        '<svg id="gr" width="' + S2.R.w + '" height="430" style="left:0;top:96px"></svg>' +
        '<div class="s6-defs" id="defs" style="top:506px">' +
          '<div class="d"><span class="k">받은 허락 수</span>$\\mathrm{in\\_approve\\_degree}(w)=\\bigl|\\{\\,u : a^{\\star}(u,w,\\cdot)>0\\,\\}\\bigr|$</div>' +
          '<div class="d"><span class="k">송금 입차수</span>$\\mathrm{in\\_degree}(w)=\\bigl|\\{\\,u_e : e\\in\\mathcal T_{\\mathrm{in}}(w)\\,\\}\\bigr|$</div>' +
          '<div class="mi">시험 기간(W0·W1)의 기준선은 자기 자신이 보낸 송금을 빼고 세요 · 논문 3장</div>' +
        '</div>' +
      '</div>' +
      '<p class="abs s6-bottom" data-step="3" data-in="words" style="left:96px;top:892px;width:1180px">페이지랭크는 이 수를 매끄럽게 다듬은 것이에요.<br>다듬는 것 이상을 하는지가 질문이에요.</p>' +
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
      g.W = Comp.contract(ctx, gr, { x: W.x, y: W.y, size: 84, label: '계약 w' });
      var ow = [30, 86, 142, 198], se = [266, 322, 378];
      svgEl('text', { x: 36, y: 122, fill: C.allow, 'font-size': 22, 'font-weight': 600 }, gr).textContent = '주인';
      svgEl('text', { x: 36, y: 330, fill: C.xfer, 'font-size': 22, 'font-weight': 600 }, gr).textContent = '보낸 주소';
      g.own = ow.map(function (y) { return Comp.eoa(ctx, gr, { x: 170, y: y, r: 13 }); });
      g.snd = se.map(function (y) { return Comp.eoa(ctx, gr, { x: 170, y: y, r: 13 }); });
      g.aA = ow.map(function (y) { return Comp.arrow(ctx, gr, { from: [170, y], to: [W.x, W.y], kind: 'allow', width: 3, shorten: [18, 52], hidden: true }); });
      g.aT = se.map(function (y) { return Comp.arrow(ctx, gr, { from: [170, y], to: [W.x, W.y], kind: 'xfer', width: 3, shorten: [18, 52], hidden: true, flow: false }); });
      g.again = svgEl('circle', { r: 8, fill: C.allow, 'fill-opacity': 0.9 }, gr); gsap.set(g.again, { autoAlpha: 0 });
      g.sameTag = svgEl('text', { x: 300, y: 70, 'text-anchor': 'middle', fill: C.ink, 'font-size': 21, 'font-weight': 600 }, gr);
      g.sameTag.textContent = '같은 주인 → 한 번만 세요'; gsap.set(g.sameTag, { autoAlpha: 0 });
      svgEl('text', { x: 620, y: 40, fill: C.ink2, 'font-size': 21 }, gr).textContent = '받은 허락 수';
      svgEl('text', { x: 620, y: 290, fill: C.ink2, 'font-size': 21 }, gr).textContent = '송금 입차수';
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
      g.barLbl = svgEl('text', { x: 10, y: 104, fill: C.deg, 'font-size': 20, 'font-weight': 600 }, js); g.barLbl.textContent = '기준선 = 그냥 센 수';
      g.q = svgEl('text', { x: 484, y: 104, 'text-anchor': 'end', fill: C.ink2, 'font-size': 20 }, js); g.q.textContent = '넘을 수 있을까?';
      g.chipER = document.createElement('div'); g.chipER.className = 's6-chip c-allow'; g.chipER.textContent = '엔도스랭크 ↑';
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
     is renormalised by D_λ(u). Bars: 예시 (s05-06 cap example; σ(0) = 0.8581). */
  var ROWA = { S1: 20000 / 20500, S2: 500 / 20500 };                 /* 0.9756 / 0.0244 */
  var XT = [1000 * 0.8581, 300 * 0.5];                                /* 858.1 / 150 */
  var ROWT = { S2: XT[1] / (XT[0] + XT[1]), R: XT[0] / (XT[0] + XT[1]) }; /* 0.1488 / 0.8512 */
  var R4 = function (v) { return Math.round(v * 1e4) / 1e4; };
  ROWA = { S1: R4(ROWA.S1), S2: R4(ROWA.S2) }; ROWT = { S2: R4(ROWT.S2), R: R4(ROWT.R) };
  var B3 = { x: 576, y: 196, L: 400, x0: 26, h: 44, rows: [52, 226, 400] };   /* bar figure */
  var SHADE = { S1: C.allow, S2a: '#C98F2A', S2b: '#2A93C2', R: C.xfer };
  var slide3 = {
    id: 's06-03', title: 'C-PR: 두 갈림길 표를 섞어요', time: 60, steps: 6,
    tags: function (step) { return step >= 4 && step < 6 ? ['example', 'plan'] : ['example']; },
    notes: [
      '셋째 점수는 두 화살표를 한 번에 걷는 결합 점수 C-PR이에요. 주인 u 하나를 볼게요. u에서는 허락 화살표 둘과 송금 화살표 둘이 나가요.',
      '먼저 허락 쪽 갈림길 표의 줄이에요. 05에서 본 상한 예 그대로, 무제한 허락은 2만 달러, 다른 하나는 500달러라서 0.9756과 0.0244로 나뉘어요. 합은 1이에요.',
      '송금 쪽 줄도 만들어요. 오늘 보낸 1,000달러는 시간 무게 0.858을 곱해 858, 180일 전 300달러는 0.5를 곱해 150이에요. 그래서 0.8512와 0.1488이에요. 이것도 합이 1이에요. 금액은 모두 설명용 예시예요.',
      '이 두 줄을 섞어요. 다이얼 람다가 0.5면 허락 줄을 반으로, 송금 줄도 반으로 줄여서 이어 붙여요. S1은 0.4878, S2는 두 조각을 더해 0.0866, R은 0.4256이에요. 람다 곱하기 1 더하기 1 빼기 람다 곱하기 1은 언제나 1이라서, 섞은 줄의 합도 1이에요.',
      '다이얼을 돌려 볼게요. 람다가 1이면 허락 줄과 똑같아지고, 0이면 송금 줄과 똑같아져요. 주된 값 0.5와 민감도 값 0.25, 0.75는 데이터를 꺼내기 전에 분석 계획에 적어 두었어요.',
      '그런데 u에게 송금 화살표가 없으면 어떻게 될까요? 섞은 줄의 합이 람다, 곧 0.5밖에 안 돼요. 그래서 람다로 나눠 다시 1로 맞춰요. 이 나눗수를 D 람다라고 써요. 결국 그 점은 허락 길을 100% 따라가요.',
      '이것이 논문 3장의 결합 식이에요. 스위치 1은 그 층에 나가는 화살표가 있으면 1, 없으면 0이에요. 표로 정리하면, 둘 다 있으면 람다와 1 빼기 람다, 한쪽만 있으면 그쪽이 1, 둘 다 없으면 매달린 점이라 다시 출발로 가요. 람다가 1이면 허락 층만, 0이면 송금 층만 걷는 것과 같아요. 다시 출발은 고르게, d는 0.85예요.'
    ],
    html:
      '<h1 class="t-h1" style="font-size:58px;line-height:70px">한 점의 줄 = λ × 허락 줄 + (1 − λ) × 송금 줄</h1>' +
      '<svg class="abs" id="g3" width="470" height="520" style="left:96px;top:196px;overflow:visible" data-in="none"></svg>' +
      '<svg class="abs" id="b3" width="520" height="560" style="left:' + B3.x + 'px;top:' + B3.y + 'px;overflow:visible" data-in="none"></svg>' +
      '<div class="abs s6-lbl c-allow" id="tA" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + B3.rows[0] - 44) + 'px">허락 줄 $\\ca{P_{A,u,\\cdot}}$</div>' +
      '<div class="abs s6-lbl c-xfer" id="tT" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + B3.rows[1] - 44) + 'px">송금 줄 $\\ct{P_{T,u,\\cdot}}$</div>' +
      '<div class="abs s6-lbl c-cpr" id="tM" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + B3.rows[2] - 44) + 'px">섞은 줄 $\\cc{P^{(\\lambda)}_{u,\\cdot}}$</div>' +
      '<div class="abs s6-callout" id="call" data-in="none" style="left:' + (B3.x + B3.x0) + 'px;top:' + (B3.y + 534) + 'px">한쪽 길만 있으면 그 길을 [[100%]]</div>' +
      '<div class="abs" id="dialbox" data-shared="lambda-dial" data-in="none" style="left:96px;top:742px;width:240px;height:180px"></div>' +
      '<div class="abs" id="lcard" data-in="none" style="left:372px;top:756px"></div>' +
      '<p class="abs s6-cap" id="lcap" data-in="none" style="left:372px;top:900px;width:700px">λ = 0.5 (주) · 0.25 · 0.75 (민감도) — 분석 계획이 데이터를 꺼내기 전에 정했어요</p>' +
      '<div class="abs s6-d3" id="d3" data-in="none" style="left:1104px;top:186px;width:720px"></div>' +
      '<div class="abs s6-final" id="fin" data-in="none" style="left:1104px;top:186px;width:720px"><div class="hd"><span>완성 식 · 논문 3장 식 coupled-transition</span></div>' +
        '$$\\begin{aligned}\\cc{P^{(\\lambda)}_{u,\\cdot}}&=\\alpha_A(u)\\,\\ca{P_{A,u,\\cdot}}+\\alpha_T(u)\\,\\ct{P_{T,u,\\cdot}}\\\\[4pt] \\alpha_A(u)&=\\frac{\\lambda\\,\\mathbf 1[o_A(u)>0]}{D_{\\lambda}(u)},\\qquad \\alpha_T(u)=\\frac{(1-\\lambda)\\,\\mathbf 1[o_T(u)>0]}{D_{\\lambda}(u)}\\\\[4pt] D_{\\lambda}(u)&=\\lambda\\,\\mathbf 1[o_A(u)>0]+(1-\\lambda)\\,\\mathbf 1[o_T(u)>0]\\end{aligned}$$' +
        '<div class="lg">$\\mathbf 1[\\text{조건}]$ 조건이 맞으면 1, 아니면 0 — 스위치<br>$D_\\lambda(u)$ 섞은 줄의 합을 다시 1로 맞추는 나눗수 · $o_A, o_T$ 나가는 무게의 합</div></div>' +
      '<div class="abs" id="cases" data-in="none" style="left:1104px;top:556px;width:720px">' +
        '<table class="s6-cases" style="width:720px"><tr><th>u에서 나가는 화살표</th><th style="text-align:center">$\\alpha_A$</th><th style="text-align:center">$\\alpha_T$</th></tr>' +
        '<tr><td>허락·송금 둘 다</td><td class="c">$\\lambda$</td><td class="c">$1-\\lambda$</td></tr>' +
        '<tr><td>허락만</td><td class="c">$\\lambda/\\lambda=1$</td><td class="c">0</td></tr>' +
        '<tr><td>송금만</td><td class="c">0</td><td class="c">$(1-\\lambda)/(1-\\lambda)=1$</td></tr>' +
        '<tr><td>둘 다 없음</td><td class="c" colspan="2">매달린 점 → 다시 출발로</td></tr></table>' +
        '<p class="s6-cap" style="margin-top:14px">λ = 1이면 허락 층만, λ = 0이면 송금 층만 걸어요 · 다시 출발은 고르게, $d = ' + DAMP + '$</p></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* graph: owner u with two allowance and two transfer arrows */
      var gs = q(el, '#g3');
      var U = { x: 70, y: 262 }, S1 = { x: 380, y: 82 }, S2n = { x: 380, y: 262 }, Rn = { x: 380, y: 442 };
      g.u = Comp.eoa(ctx, gs, { x: U.x, y: U.y, r: 18, label: 'u (주인)' });
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
      g.lS1 = tag(S1.x - 40, S1.y - 34, '무제한 → 상한 20,000달러', C.allow);
      g.lS2a = tag(S2n.x - 46, S2n.y - 40, '500달러', C.allow);
      g.lS2b = tag(S2n.x - 30, S2n.y + 46, '300달러 · 180일 전', C.xfer);
      g.lR = tag(Rn.x - 40, Rn.y + 52, '1,000달러 · 오늘', C.xfer);
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
      g.lcard = Comp.symbolCard(ctx, q(el, '#lcard'), { tex: '\\lambda', desc: '섞는 비율 — 다이얼', hidden: true });
      g.lcap = q(el, '#lcap'); gsap.set(g.lcap, { autoAlpha: 0 });
      /* derivation */
      g.D = Comp.derive(ctx, q(el, '#d3'), { head: '유도', lines: [
        { tex: '\\ca{0.9756}+\\ca{0.0244}=1', note: '허락 줄: 05의 상한 예 (20,000달러와 500달러)' },
        { tex: '\\ct{0.1488}+\\ct{0.8512}=1', note: '송금 줄: 300×0.5 = 150 · 1,000×0.858 = 858' },
        { tex: '\\begin{aligned}\\text{S1}&=0.5\\times\\ca{0.9756}=0.4878\\\\ \\text{S2}&=0.5\\times\\ca{0.0244}+0.5\\times\\ct{0.1488}=0.0866\\\\ \\text{R}&=0.5\\times\\ct{0.8512}=0.4256\\end{aligned}', note: 'λ = 0.5로 섞기: 줄마다 반씩' },
        { tex: '\\part{s}{\\lambda\\times1+(1-\\lambda)\\times1}=1', note: '그래서 섞은 줄의 합도 언제나 1', mark: 's' },
        { tex: '\\frac{\\lambda\\times1+0}{\\part{dl}{\\lambda}}=1', note: '송금 화살표가 없으면 합이 λ뿐 → λ로 나눠요. 이 나눗수가 $D_\\lambda(u)$', mark: 'dl' }
      ] });
      Deck.renderMath(g.D.el);
      gsap.set(g.D.el, { autoAlpha: 0 });
      g.fin = q(el, '#fin'); g.cases = q(el, '#cases');
      gsap.set([g.fin, g.cases], { autoAlpha: 0 });
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
    id: 's06-04', title: 'λ를 돌리면: 15,107개 계약이 움직여요', time: 70, steps: 6,
    tags: ['construct'],
    notes: [
      '이 장면이 이 발표의 대표 그림이에요. 실제 계약 15,107개를 모두 올렸어요. 가로는 허락한 주인 수, 깊이는 송금을 보낸 주소 수, 높이는 C-PR 점수의 순위예요. 순위를 백분위로 바꿔서, 람다마다 점수의 크기가 달라도 같은 눈금으로 비교할 수 있게 했어요. 지금 다이얼은 1, 곧 허락 층만 걷는 점수예요.',
      '람다를 0에 두면 송금 층만 걸어요. 점수는 송금 쪽 수를 따라 서고, 송금 그래프에 없는 2,670개는 바닥으로 떨어져요. 위의 숫자를 보면 송금 입차수와의 타우가 0.689, 받은 허락 수와는 0.262예요.',
      '람다를 0.25로 올리면 크게 바뀌어요. 바닥에 있던 계약 대부분이 솟아오르고, 두 그래프 어디에도 없는 80개만 남아요. 능선이 두 축 사이로 비스듬해져요.',
      '0.5에서는 거의 움직이지 않아요. 0.25와 비슷해요.',
      '0.75에서도 조금만 움직여요.',
      '1에서 다시 크게 뛰어 허락 쪽 수를 따라 서요. 받은 허락 수와의 타우는 0.654예요. 허락 그래프에 없는 523개가 바닥으로 가요.',
      '끝에서 크게 뛰는 이유는, 람다가 정확히 0이나 1이면 한 층만 걸어서 점의 모임 자체가 달라지기 때문이에요. 0과 1 사이에서는 한쪽 화살표만 가진 점도 그 길을 100% 따라가니까요. 그래서 이 식은 끝에서 연속이 아니에요. 그리고 이 숫자들은 같은 기간의 점검이라서, 만든 방식 때문에 어느 정도는 저절로 맞는다는 점도 기억해 주세요. 다이얼을 끌면 계산된 다섯 값 사이를 오갈 수 있고, 구름은 끌어서 돌려 볼 수 있어요.'
    ],
    html:
      '<h1 class="t-h1">λ를 돌리면, 점수가 [[어느 쪽 수]]를 따라가는지가 바뀌어요</h1>' +
      '<div class="abs" id="three" data-in="none" style="left:0;top:' + V4.top + 'px;width:1920px;height:' + V4.h + 'px"></div>' +
      '<div class="abs" id="dialbox" data-shared="lambda-dial" data-in="none" style="left:96px;top:176px;width:240px;height:180px"></div>' +
      '<div class="abs s6-cap" id="dialcap" style="left:96px;top:366px;width:300px">λ = 0 송금 층만 · λ = 1 허락 층만<br><span class="ink-3" style="font-size:18px">다이얼을 끌어 보세요 (다섯 값만)</span></div>' +
      '<div class="abs s6-hudp" id="hudp" style="left:1384px;top:176px;width:440px">' +
        '<div class="r"><span class="k c-xfer">τ(송금 입차수)</span><span class="v c-xfer" id="vd">0.183</span></div>' +
        '<div class="r" style="margin-top:-6px"><span class="k"></span><span class="ci" id="cd">[0.171, 0.195]</span></div>' +
        '<div class="r"><span class="k c-allow">τ(받은 허락 수)</span><span class="v c-allow" id="va">0.654</span></div>' +
        '<div class="r" style="margin-top:-6px"><span class="k"></span><span class="ci" id="ca">[0.647, 0.660]</span></div>' +
        '<div class="z">0점이라 바닥판에 있는 계약 <b id="vz">523</b>개</div></div>' +
      '<p class="abs s6-capline" id="cap0" style="left:96px;top:930px;width:1180px">점 하나 = 계약 하나 · 가로 <b class="c-allow">받은 허락 수</b> · 깊이 <b class="c-xfer">송금 입차수</b> (둘 다 로그) · 높이 <b class="c-cpr">C-PR 점수의 백분위</b></p>' +
      '<p class="abs s6-capline" id="cap6" data-in="none" style="left:96px;top:912px;width:1240px;color:var(--ink)">끝에서 크게 뛰어요: λ = 0과 1은 ‘한 층만 걷기’라서 점의 모임이 달라져요 — 연속이 아니에요</p>' +
      '<div class="abs s6-mini ink-2" id="mini" style="left:1384px;top:902px;width:440px;text-align:right">$P^{(\\lambda)}_{u,\\cdot}=\\alpha_A(u)\\,\\ca{P_{A,u,\\cdot}}+\\alpha_T(u)\\,\\ct{P_{T,u,\\cdot}}$</div>',
    build: function (el, ctx) {
      var g = ctx.g = { j: 4 };
      g.dialbox = q(el, '#dialbox');
      g.fromDial = !!(ctx.prev && ctx.prev.rect && ctx.prev.rect('lambda-dial'));
      g.dial = Comp.dial(ctx, g.dialbox, { value: g.fromDial ? 0.5 : 1, size: 240, interactive: true, onChange: function (v) {
        var j = Comp.data.lambdas.indexOf(v); if (j < 0) return;
        ctx.add(function () { setLambda(ctx, j, false); });
      } });
      g.vd = q(el, '#vd'); g.va = q(el, '#va'); g.cd = q(el, '#cd'); g.ca = q(el, '#ca'); g.vz = q(el, '#vz');
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
        T.label('받은 허락 수 (로그)', [O[0] + SPAN + 1.0, O[1], O[2]], { className: 's6-ax3d', anchor: 'left', dx: 14 }),
        T.label('C-PR 백분위', [O[0], O[1] + HY + 0.9, O[2]], { className: 's6-ax3d', anchor: 'left', dx: 18, dy: 6 }),
        T.label('송금 입차수 (로그)', [O[0], O[1], O[2] + SPAN + 1.0], { className: 's6-ax3d', anchor: 'right', dx: -14 })
      ];
      g.labs[0].el.style.color = C.allow; g.labs[1].el.style.color = C.cpr; g.labs[2].el.style.color = C.xfer;
      [[10, '10'], [100, '100'], [1000, '1천'], [10000, '1만']].forEach(function (tv) {
        var lx = Math.log10(1 + tv[0]) * SX - SPAN / 2, lz = Math.log10(1 + tv[0]) * SZ - SPAN / 2;
        if (lx <= SPAN / 2) g.labs.push(T.label(tv[1], [lx, FLOOR, O[2] - 0.4], { className: 's6-tick3d' }));
        if (lz <= SPAN / 2) g.labs.push(T.label(tv[1], [O[0] - 0.4, FLOOR, lz], { className: 's6-tick3d' }));
      });
      [[0, '0'], [0.5, '0.5'], [1, '1']].forEach(function (tv) { g.labs.push(T.label(tv[1], [O[0] - 0.3, tv[0] * HY, O[2]], { className: 's6-tick3d', anchor: 'right' })); });
      g.labs.push(T.label('0점 = 바닥판', [SPAN / 2 + 0.2, FLOOR, SPAN / 2 + 0.6], { className: 's6-tick3d', anchor: 'left' }));
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
      g.cloud = Comp.cloud(ctx, T, { positions: g.emit, colors: g.sets[4].c, size: 3, opacity: 0.62 });
      if (g.cloud.points) g.cloud.points.visible = false;   /* shown when the burst from the needle tip starts */
      g.labs.forEach(function (L) { L.el.innerHTML = '<span class="s6-lin">' + L.el.innerHTML + '</span>'; L.el.style.opacity = '0'; });
      /* labels that project into the caption band fade out (the view turns and can be dragged) */
      T.onFrame(function () {
        var lim = T.height - 96;
        for (var k = 0; k < g.labs.length; k++) {
          var pr = T.project(g.labs[k].pos), o = Math.max(0, Math.min(1, (lim - pr.y) / 50)), inn = g.labs[k].el.firstChild;
          if ((pr.x > T.width - 560 || pr.x < 430) && pr.y < 300) o = 0;   /* under the HUD panel or the dial */
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
  var CAM4 = [
    { theta: 1.40, phi: 1.16, radius: 19.4, target: [0.0, 1.45, 0.2] },   /* λ = 0: look along x, the sky axis runs across */
    { theta: 0.78, phi: 1.12, radius: 18.2, target: [0.3, 1.7, 0] },
    { theta: 0.78, phi: 1.12, radius: 18.2, target: [0.3, 1.7, 0] },
    { theta: 0.78, phi: 1.12, radius: 18.2, target: [0.3, 1.7, 0] },
    { theta: 0.16, phi: 1.16, radius: 19.4, target: [0.2, 1.45, 0] }      /* λ = 1: look along z, the amber axis runs across */
  ];
  function setLambda(ctx, j, fromStep) {
    var g = ctx.g, tl = ctx.tl(), prev = g.j == null ? 4 : g.j;
    var Lp = LAM[prev], Ln = LAM[j];
    g.j = j;
    if (fromStep) tl.add(g.dial.set(Ln.v, { duration: 0.9 }), 0);
    if (g.cloud) {
      tl.add(g.cloud.morph(g.sets[j].p, { duration: 1.4, delays: g.delays, spread: 0.7, ease: E.io }), 0.1);
      tl.add(g.cloud.recolor(g.sets[j].c, { duration: 1.0, delays: g.delays, spread: 0.5 }), 0.1);
      if (fromStep && (prev !== j)) tl.add(g.T.cameraTo(CAM4[j], { duration: 1.8 }), 0.15);
    }
    var a0 = nums(Lp.d), a1 = nums(Ln.d), b0 = nums(Lp.a), b1 = nums(Ln.a);
    tl.add(ctx.count(g.vd, a0[0], a1[0], { decimals: 3, final: fmt(a1[0], 3), duration: 1.2 }), 0.3);
    tl.add(ctx.count(g.va, b0[0], b1[0], { decimals: 3, final: fmt(b1[0], 3), duration: 1.2 }), 0.3);
    tl.add(ctx.count(g.vz, Lp.zeros, Ln.zeros, { decimals: 0, final: fmt(Ln.zeros, 0), duration: 1.2 }), 0.3);
    tl.call(function () { g.cd.textContent = '[' + Ln.d.split('[')[1]; g.ca.textContent = '[' + Ln.a.split('[')[1]; }, null, 0.9);
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
    id: 's06-05', title: 'S-PR: 허락은 \'출발점\'만 정해요', time: 45, steps: 4,
    tags: function (step) { return step >= 3 ? ['example', 'posthoc'] : ['example']; },
    notes: [
      '넷째는 빼 보기 실험인 S-PR이에요. 송금 그래프를 걷는 점수인데, 순간 이동하는 곳이 달라요. 지금은 다시 출발하는 비가 모든 점에 고르게 내려요.',
      '이제 비가 허락 점수가 있는 곳, 곧 호박색 후광이 있는 점에만 몰려 내려요. 후광이 클수록 비도 굵어요. 허락 점수가 없는 점에는 비가 내리지 않아요. 웹 스팸을 막는 TrustRank와 같은 꼴인데, 사람이 고른 씨앗 대신 허락 점수를 씨앗으로 써요.',
      '식으로 쓰면, 송금 그래프의 점마다 허락 층만 걸은 점수를 합이 1이 되게 다시 나눈 것이 다시 출발 비율이에요.',
      '결과를 조금 미리 보면, W0에서 S-PR은 새 송금자는 송금 층만 걸을 때와 거의 같게 맞혔지만, 새 허락 쌍은 허락 층만 걸을 때보다 못 맞혔어요. 이 두 비교는 라벨을 본 뒤에 계산한 사후 비교예요.',
      '그러니까 허락 화살표는 실제로 그 위를 걸을 때 도움이 되고, 출발점만 정할 때는 별 도움이 안 된다는 뜻이에요.'
    ],
    html:
      '<h1 class="t-h1">허락은 [[씨앗]], 송금은 퍼지는 길</h1>' +
      '<svg class="abs" id="g5" data-in="none" width="' + G5.w + '" height="' + G5.h + '" style="left:' + G5.x + 'px;top:' + G5.y + 'px;overflow:visible"></svg>' +
      '<div class="abs s6-lines" style="left:1060px;top:196px;width:764px">' +
        '<p class="l">송금 층을 걷되, 다시 출발할 곳은 허락 점수가 정해요</p>' +
        '<p class="l" data-step="1">TrustRank와 같은 꼴<small>사람이 고른 씨앗 대신 허락 층만 걸은 점수를 씨앗으로 써요</small></p></div>' +
      '<div class="abs s6-eq5" data-step="2" style="left:1060px;top:400px;width:764px">' +
        '$$\\cc{\\pi_u}=\\frac{\\ca{r_{A,u}}}{\\sum_{v\\in V_T}\\ca{r_{A,v}}}\\qquad(u\\in V_T)$$' +
        '<div class="nt">송금 그래프의 점들에서, 허락 점수 $\\ca{\\mathbf r_A}$를 합이 1이 되게 다시 나눈 것 · 허락 그래프에 없는 점은 0</div></div>' +
      '<div class="abs" id="fp5" data-in="none" style="left:1060px;top:640px;width:764px">' +
        '<div class="s6-fhead"><span>미리 보기 · W0 · 짝지은 차이 Δτ</span>' + Deck.tagHTML('posthoc') + '</div><div id="fhost5"></div></div>' +
      '<p class="abs s6-concl" data-step="4" style="left:96px;top:922px;width:1220px">허락 화살표는 ‘걸을 때’ 도움이 되고, ‘출발점만 정할 때’는 별 도움이 안 돼요</p>',
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
      g.ex = svgEl('text', { x: 0, y: G5.h - 30, fill: C.ink2, 'font-size': 20 }, svg); g.ex.textContent = '호박 후광 = 허락 층만 걸은 점수 (예시)';
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
      /* forest: two post hoc contrasts (R§6 contrasts_after[2], [1]) */
      var a = nums(SPR_SEND), b = nums(SPR_APPR);
      g.F = Comp.forest(ctx, q(el, '#fhost5'), { w: 764, rowH: 82, labelWidth: 210, valueWidth: 290, domain: [-0.08, 0.02], ticks: [-0.08, -0.06, -0.04, -0.02, 0, 0.02],
        tickFormat: function (t) { return mfmt(t, 2); }, hidden: true, top: 12,
        rows: [
          { label: '새 송금자', sub: 'S-PR − 송금 층만 (λ = 0)', est: a[0], lo: a[1], hi: a[2], color: 'cpr', text: SPR_SEND },
          { label: '새 허락 쌍', sub: 'S-PR − 허락 층만 (λ = 1)', est: b[0], lo: b[1], hi: b[2], color: 'cpr', text: SPR_APPR }
        ] });
      g.fp = q(el, '#fp5'); gsap.set(g.fp, { autoAlpha: 0 });
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
        tl.add(g.F.show(0), 0.3);
        tl.add(g.F.show(1), 0.75);
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

  Deck.section({ id: 's06-methods', title: '네 가지 점수', slides: [slide1, slide2, slide3, slide4, slide5] });
})();
