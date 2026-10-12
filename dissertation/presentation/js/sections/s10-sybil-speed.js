/* =========================================================================
   s10-sybil-speed — 공격 비용과 속도 (STORYBOARD.md §2, s10-01 … s10-04)

   s10-01  가짜 주소 농장     the trap of s04-05 (two points that only point at each other) grows
                              into a ring of 20 fake addresses; rain = restart + dangling share;
                              derivation of the closed-cluster equation (thesis Ch. 5); a gauge
                              rises 1 → 3.17× and d buttons 0.75 / 0.85 / 0.95 switch it
   s10-02  별 모양 농장       ten fake addresses pop around one target and approve it both ways;
                              derivation of r_t = c(1 + d f)/(1 − d²); a log bar compares f = 10
                              with the cohort's median, 90th percentile and top
   s10-03  꼭대기까지         3D tower of the 15,107 matched-cohort contracts on a log EndorseRank
                              axis (real data); the target climbs: one partner (the pair, 2 approvals)
                              → 22 → 2,074 → ≈135,895 fake addresses (one pink point per 5 addresses,
                              27,179 points at the top, so the scene stays light)
   s10-04  속도와 |E|         small world: one iteration = one multiplication per edge; edge piles;
                              a 4× race 10.29 s vs 22.37 s; 2.17 ≈ 2.23; C-PR and S-PR; then, as its
                              own last step with the rest dimmed, the small-sample stage chart

   Numbers and sources (R = revised digest = the thesis's main analysis)
     |V| 6,219,063, |E| 11,210,114 (EndorseRank solver graph at T_obs) R§8 graph.nodes / graph.edges
     6,221,665 / 7,884,602 (graphs as counted in s03)                 R§1 graph.allowance/transfer.nodes
     2,602 = 6,221,665 − 6,219,063 and 2,246 = 7,884,602 − 7,882,356: addresses touched only by
       pairs whose value weight is zero (left out of the solver graphs)  calc; thesis Ch. 4 §dataset
     r_dang (the thesis's r_D: the total share of all dangling nodes) 0.3824 → 0.382;
       farm factor 2.0648 / 3.1671 / 8.6819 at d = 0.75 / 0.85 / 0.95
                                                                       R§8 damping.*.farm_factor
     ring of 20: 3.1671                                                R§8 ring20 collects times share
     c = 7.639e-8                                                      R§8 b common
     star: f = 10, r_t 2.615e-6 (= closed form), 20 approvals, top 0.0318, ratio 8.224e-5
                                                                       R§8 star.*
     cohort quantiles p50 1.881e-7, p90 5.278e-6, p99 4.855e-4, top 0.0318 and farm sizes
       0 / 21.38 (→ 22) / 2,073.9 (→ 2,074) / 135,894.8 (→ about 135,895)
                                                                       R§8 farm size to reach cohort quantile
     median: the formula gives f ≤ 0 ("no farm"), but the target still needs one partner that it
       approves and that approves it (thesis Ch. 5: "two addresses that approve each other already
       score c/(1−d)") → shown as 1 fake address and 2 approvals; f = 1 in the star formula
     2f approvals per window 2 (the pair) / 44 / 4,148 / 271,790; pair score c/(1−d) = 5.09e-7;
       box heights r_t(f); 1 − d² = 0.2775; 0.0318 / c > 400,000      calc (DECK_DATA.sybil.revised)
     tower points: log10 EndorseRank of the 15,107 contracts           D: cohort_scores.part000.parquet
     benchmark: EndorseRank 10.294 s (SD 0.601), 879.7 MB, 69 it., |V| 6,219,063, |E| 11,210,114;
       AWP 22.367 s, 1,712.6 MB, 92 it., 7,882,356, 25,001,216; C-PR (λ=0.5) 36.162 s, 9,151,010,
       31,552,359, 79 it.; S-PR 34.422 s, 7,884,602, 25,018,892; ratios 2.17 and 2.23;
       1 warm-up + 5 timed runs                                        R§10
     stage ratios 3.98 2.49 2.60 2.57 2.23 (edges), 2.89 4.55 3.60 2.70 2.17 (time)
                                                                       calc from R§10 scaling[0–4]
   Status tags: s10-01 … s10-03 '계산' (model values evaluated on the revised graph; no label,
   no rule). s10-04 carries no tag (RQ3 is met largely by construction); every number on it is
   a benchmark measurement of the revised analysis, named as such on the slide.
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt;
  var NS = 'http://www.w3.org/2000/svg';
  var DATA = window.DECK_DATA || {};

  function pick(o, keys, dflt) {
    for (var i = 0; i < keys.length; i++) { if (o == null) return dflt; o = o[keys[i]]; }
    return o == null ? dflt : o;
  }
  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, cls, parent, html) {
    var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e); return e;
  }
  function q(el, sel) { return el.querySelector(sel); }
  var uidN = 0;
  function uid(p) { uidN += 1; return 's10-' + p + '-' + uidN; }
  function sup(e) { return '<sup>' + (e < 0 ? '−' : '') + Math.abs(e) + '</sup>'; }
  function sciH(s) { return s[0] + ' × 10' + sup(s[1]); }               /* ['2.62', -6] -> HTML */
  function sciT(s) { return s[0] + '\\times10^{' + s[1] + '}'; }        /* -> TeX */
  function sciSvg(t, s, pre, post) {                                    /* -> SVG <text> */
    t.textContent = '';
    t.appendChild(document.createTextNode((pre || '') + s[0] + ' × 10'));
    var ts = svgEl('tspan', { 'baseline-shift': 'super', 'font-size': '64%' }, t);
    ts.textContent = (s[1] < 0 ? '−' : '') + Math.abs(s[1]);
    if (post) { var t2 = svgEl('tspan', {}, t); t2.textContent = post; }
    return t;
  }
  function lg(v) { return Math.log(v) / Math.LN10; }

  /* ------------------------------------------------------------ data (digest values as fallbacks) */
  var SYR = pick(DATA, ['sybil', 'revised'], {});
  var SY = SYR.json || {};
  var DAMP = pick(DATA, ['params', 'pagerank', 'd'], 0.85);
  var NODES = pick(SY, ['graph', 'nodes'], 6219063), NEDGES = pick(SY, ['graph', 'edges'], 11210114);
  var RD = pick(SY, ['r_D'], 0.3824);
  var FF = { '0.75': pick(SY, ['damping', '0.75', 'farm_factor'], 2.0648), '0.85': pick(SY, ['damping', '0.85', 'farm_factor'], 3.1671),
    '0.95': pick(SY, ['damping', '0.95', 'farm_factor'], 8.6819) };
  var RING20 = pick(SY, ['ring20_collects_times_share'], 3.1671);
  var CC = pick(SY, ['b_common'], 7.639e-8);
  var STAR = SY.star || {};
  var STAR_M = STAR.m || 10, STAR_R = STAR.target_score || 2.615e-6, TOP = STAR.highest_cohort_endorserank || 0.0318;
  var STAR_APPR = STAR.approvals_per_window || 20;
  var QS = SY.farm_size_to_reach_cohort_quantile || {};
  var KP = SYR.key_points || {};
  var Q = ['p50', 'p90', 'p99', 'p100'].map(function (k, i) {
    var dflt = [[1.881e-7, 0, 0, 0], [5.278e-6, 21.3797, 22, 44], [4.855e-4, 2073.9281, 2074, 4148], [0.0318, 135894.8004, 135895, 271790]][i];
    return { key: k, score: pick(QS, [k, 'score'], dflt[0]), f: pick(QS, [k, 'farm_addresses'], dflt[1]),
      ceil: pick(KP, [k, 'farm_addresses_ceil'], dflt[2]), appr: pick(KP, [k, 'approvals_per_window'], dflt[3]) };
  });
  var PAIR = SYR.pair_score || CC / (1 - DAMP);
  /* graph sizes as s03 counts them (R§1); the solver graphs leave out the zero-value-weight addresses */
  var G_ALLOW_V = pick(DATA, ['results', 'revised', 'same_window', 'graph', 'allowance', 'nodes'], 6221665);
  var G_XFER_V = pick(DATA, ['results', 'revised', 'same_window', 'graph', 'transfer', 'nodes'], 7884602);
  /* display strings, written as in the digest / thesis (checked against the data below) */
  var S = {
    rD: '0.382', ff: { '0.75': '2.06', '0.85': '3.17', '0.95': '8.68' }, ring20: '3.17',
    c: ['7.64', -8], star: ['2.62', -6], p50: ['1.88', -7], p90: ['5.28', -6], p99: ['4.86', -4], top: '0.0318',
    pair: ['5.09', -7], nodes: fmt(NODES, 0), edges: fmt(NEDGES, 0)
  };
  (function check() {
    function near(v, s, e) { var x = parseFloat(s) * Math.pow(10, e || 0); return Math.abs(v - x) <= Math.abs(x) * 0.006 + 1e-15; }
    var bad = [];
    if (!near(RD, S.rD)) bad.push('r_D');
    ['0.75', '0.85', '0.95'].forEach(function (k) { if (!near(FF[k], S.ff[k])) bad.push('farm factor ' + k); });
    if (!near(RING20, S.ring20)) bad.push('ring20');
    if (!near(CC, S.c[0], S.c[1])) bad.push('c');
    if (!near(STAR_R, S.star[0], S.star[1])) bad.push('star');
    if (!near(Q[0].score, S.p50[0], S.p50[1]) || !near(Q[1].score, S.p90[0], S.p90[1]) || !near(Q[2].score, S.p99[0], S.p99[1]) || !near(Q[3].score, S.top)) bad.push('quantiles');
    if (!near(PAIR, S.pair[0], S.pair[1])) bad.push('pair');
    if (bad.length) { try { console.warn('[s10] DECK_DATA differs from the digest strings: ' + bad.join(', ')); } catch (e) { /* ignore */ } }
  })();
  function rStar(f) { return CC * (1 + DAMP * f) / (1 - DAMP * DAMP); }   /* r_t = c(1 + d f)/(1 − d²) */

  var BMR = pick(DATA, ['benchmark', 'revised'], {});
  function bm(k, dflt) {
    var m = pick(BMR, ['main', k], null) || {};
    return { s: m.mean_s || dflt[0], mb: m.peak_mb || dflt[1], it: m.iterations || dflt[2], v: m.nodes || dflt[3], e: m.edges || dflt[4] };
  }
  var B_ER = bm('endorserank', [10.2942, 879.7489, 69, 6219063, 11210114]);
  var B_AWP = bm('awp', [22.3674, 1712.5831, 92, 7882356, 25001216]);
  var B_CPR = bm('cpr_l50', [36.1616, 1768.0676, 79, 9151010, 31552359]);
  var B_SPR = bm('spr', [34.4221, 1235.78846, 158, 7884602, 25018892]);
  var R_TIME = pick(BMR, ['derived', 'time_ratio_awp_over_er'], B_AWP.s / B_ER.s);
  var R_EDGE = pick(BMR, ['derived', 'edge_ratio_awp_over_er'], B_AWP.e / B_ER.e);
  var PROT = BMR.protocol || { warmup_runs: 1, timed_runs: 5 };
  var STAGES = (BMR.scaling || []).map(function (st) {
    return { n: st.n, er: st.endorserank.mean_s, awp: st.awp.mean_s, eE: st.endorserank.edges, eA: st.awp.edges };
  });
  if (STAGES.length !== 5) STAGES = [[1000, 0.5802, 1.6774, 424888, 1692513], [2000, 0.9388, 4.272, 1263471, 3148826], [5000, 2.4959, 8.9948, 2988450, 7769268],
    [10000, 6.2196, 16.82053, 6673167, 17180184], [15107, 10.2942, 22.3674, 11210114, 25001216]].map(function (a) { return { n: a[0], er: a[1], awp: a[2], eE: a[3], eA: a[4] }; });
  STAGES.forEach(function (st) { st.rt = st.awp / st.er; st.re = st.eA / st.eE; });

  /* ------------------------------------------------------------ section styles */
  var CSS = [
    '.s10 sup{font-size:.6em;vertical-align:.62em;line-height:0;letter-spacing:0}',
    '.s10-lead{position:absolute;left:96px;top:170px;width:1000px;font-size:26px;line-height:40px;color:var(--ink-2)}',
    '.s10-lead b{color:var(--ink);font-weight:700}',
    '.s10-d .eq-panel{padding:20px 28px 14px}',
    '.s10-d .eq-head{margin-bottom:6px}',
    '.s10-d .derive-line{padding:6px 0;gap:14px}',
    '.s10-d .derive-no{width:22px}',
    '.s10-d .derive-tex .katex{font-size:25px}',
    '.s10-d .derive-note{font-size:20px;line-height:28px}',
    '.s10-d .derive-note .katex{font-size:21px}',
    '.s10-d .fx-mark{background:rgba(255,107,138,.22)}',
    '.s10-cap{font-size:25px;line-height:36px;color:var(--ink-2)}',
    '.s10-cap b{color:var(--ink);font-weight:700}',
    '.s10-cap .katex{font-size:25px}',
    '.s10-foot{font-size:20px;line-height:28px;color:var(--ink-3)}',
    '.s10-foot b{color:var(--ink-2);font-weight:600}',
    '.s10-lbl{position:absolute;white-space:nowrap;font-size:21px;line-height:28px;color:var(--ink-2)}',
    '.s10-lbl .katex{font-size:22px}',
    '.s10-chips{display:flex;gap:14px}',
    '.s10-chip{appearance:none;border:1.5px solid var(--line);background:var(--bg-2);color:var(--ink-2);border-radius:14px;padding:8px 18px;',
    '  font-family:var(--font-sans);font-size:22px;line-height:30px;font-weight:600;cursor:pointer;font-variant-numeric:tabular-nums}',
    '.s10-chip b{color:var(--ink);font-weight:800;margin-left:6px}',
    '.s10-chip.on{border-color:var(--c-hi);color:var(--ink);background:var(--c-hi-soft)}',
    '.s10-chip:focus-visible{outline:2px solid var(--ink);outline-offset:2px}',
    '.s10-gh{position:absolute;width:240px;text-align:center;font-size:21px;line-height:28px;color:var(--ink-2)}',
    '.s10-gv{position:absolute;width:240px;text-align:center;font-size:44px;line-height:52px;font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums}',
    /* s10-02 */
    '.s10-fc{font-size:26px;line-height:36px;color:var(--ink-2)}',
    '.s10-fc b{font-size:40px;color:var(--ink);font-weight:800;font-variant-numeric:tabular-nums;margin:0 4px}',
    '.s10-sum{font-size:24px;line-height:34px;color:var(--ink)}',
    '.s10-sum .r{color:var(--c-hi);font-weight:700}',
    /* s10-03 */
    '.s10-3d{position:absolute;overflow:hidden;-webkit-mask-image:linear-gradient(#000 88%,transparent);mask-image:linear-gradient(#000 88%,transparent)}',
    '.s10-cnt .k{font-size:24px;line-height:32px;color:var(--ink-2)}',
    '.s10-cnt .v{font-size:112px;line-height:118px;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:var(--ink);white-space:nowrap}',
    '.s10-cnt .v .u{font-size:44px;font-weight:700;margin-left:10px;color:var(--ink-2)}',
    '.s10-cnt .v .pre{font-size:44px;font-weight:700;margin-right:12px;color:var(--ink-2)}',
    '.s10-cnt .s{font-size:24px;line-height:34px;color:var(--ink-2)}',
    '.s10-cnt .s b{color:var(--ink);font-variant-numeric:tabular-nums}',
    '.s10-rungs{display:flex;flex-direction:column;gap:10px}',
    '.s10-rung{position:relative;display:grid;grid-template-columns:34px 1fr auto;column-gap:14px;align-items:center;padding:10px 18px;border-radius:14px;',
    '  border:1.5px solid var(--line);background:rgba(16,21,31,.85);opacity:.32}',
    '.s10-rung .ck{width:26px;height:26px;border-radius:13px;border:2px solid var(--ink-3);display:flex;align-items:center;justify-content:center}',
    '.s10-rung .ck svg{width:16px;height:16px;opacity:0}',
    '.s10-rung .q{font-size:26px;line-height:34px;font-weight:700}',
    '.s10-rung .n{font-size:28px;line-height:34px;font-weight:800;font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}',
    '.s10-rung .dd{grid-column:2 / span 2;font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s10-rung.on{opacity:1;border-color:#3A4458}',
    '.s10-rung.on .ck{border-color:var(--ink)}',
    '.s10-rung.on .ck svg{opacity:1}',
    '.s10-con{font-size:23px;line-height:34px;color:var(--ink-2)}',
    '.s10-con p + p{margin-top:8px}',
    '.s10-con b{color:var(--ink);font-weight:700}',
    '.s10-con .big{font-size:27px;line-height:38px;color:var(--ink);font-weight:700;padding-left:16px;border-left:4px solid var(--ink-2)}',
    '.s10-rl{font-size:20px;line-height:26px;color:var(--ink-2);white-space:nowrap;padding:2px 8px;border-radius:8px;background:rgba(10,13,20,.72)}',
    '.s10-rl b{color:var(--ink);font-weight:700;margin-right:6px}',
    '.s10-rl.on{color:var(--ink);box-shadow:0 0 0 1.5px var(--ink-2) inset}',
    '.s10-box{pointer-events:none}',
    '.s10-box svg{display:block;overflow:visible}',
    '.s10-leg{font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s10-leg i{display:inline-block;width:12px;height:12px;border-radius:6px;margin:0 8px 0 0;vertical-align:0}',
    '.s10-range{display:flex;align-items:center;gap:14px;font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s10-range input{width:300px;accent-color:#FF6B8A}',
    /* s10-04 */
    '.s10-pk{position:absolute;text-align:center;font-weight:800;font-size:24px;line-height:30px;font-variant-numeric:tabular-nums;white-space:nowrap}',
    '.s10-pn{position:absolute;text-align:center;font-size:22px;line-height:28px;font-weight:700;white-space:nowrap}',
    '.s10-clock{font-size:22px;line-height:30px;color:var(--ink-2);white-space:nowrap;text-align:right}',
    '.s10-clock b{font-family:var(--font-mono);font-size:36px;color:var(--ink);font-weight:700;letter-spacing:0;margin:0 6px}',
    '.s10-ratio{font-size:44px;line-height:56px;font-weight:700;letter-spacing:-.02em;white-space:nowrap}',
    '.s10-ratio .k{font-size:30px;font-weight:600;color:var(--ink-2)}',
    '.s10-ratio .ap{display:inline-block;margin:0 22px;color:var(--ink)}',
    '.s10-ratio .num{display:inline-block;font-variant-numeric:tabular-nums}',
    '.s10-frac{font-size:24px;line-height:34px;color:var(--ink-2)}',
    '.s10-frac .katex{font-size:26px}',
    '.s10-mul{position:absolute;padding:1px 9px;border-radius:10px;background:var(--bg-3);border:1px solid var(--c-allow);color:var(--ink);',
    '  font-size:17px;line-height:24px;font-weight:700;white-space:nowrap;font-variant-numeric:tabular-nums;pointer-events:none}',
    '.s10-swc{font-size:22px;line-height:30px;color:var(--ink-2);white-space:nowrap}',
    '.s10-cn{display:inline-block;min-width:21px;height:21px;padding:0 3px;border-radius:11px;border:1.5px solid currentColor;text-align:center;line-height:18px;',
    '  font-size:14px;font-weight:700;font-family:var(--font-mono);letter-spacing:0;vertical-align:1px;margin-left:3px}',
    '.s10-swc b{color:var(--ink);font-weight:700;font-variant-numeric:tabular-nums}',
    '.s10-ct{font-size:20px;line-height:26px;color:var(--ink);font-weight:600}',
    '.s10-ct small{display:block;font-size:18px;line-height:24px;color:var(--ink-2);font-weight:500}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s10-style')) return;
    var st = document.createElement('style'); st.id = 's10-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  /* a derivation panel whose notes may carry $…$ */
  function derivePanel(ctx, host, lines, head) {
    var dv = Comp.derive(ctx, host, { lines: lines, head: head || '유도' });
    ctx.katex(dv.el);
    return dv;
  }
  var CHECK = '<svg viewBox="0 0 16 16" fill="none" stroke="#E9EDF5" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.4l3.2 3.1L13 4.6"/></svg>';

  /* ================================================================ s10-01 the closed farm */
  var F1 = { x: 96, y: 262 };                                  /* figure svg origin (stage px) */
  var RING = { cx: 380, cy: 318, r: 200, dot: 15, wall: 250 }; /* svg px */
  var TANK = { x: 862, y: 132, w: 60, h: 392, max: 9 };        /* svg px */
  var OUTA = [-42, -24, -6];                                   /* the teleport outflow: three arrows (deg) */
  var OUTL = { x: 704, y: 196 };                               /* … and their label (svg px), clear of the gauge */
  function tankY(v) { return TANK.y + TANK.h - Math.max(0, Math.min(TANK.max, v)) / TANK.max * TANK.h; }

  var slide1 = {
    id: 's10-01', title: '가짜 주소 농장: 제 몫의 3배를 모아요', time: 50, steps: 6,
    className: 's10',
    tags: ['calc'],
    notes: [
      '이제 이 점수를 속이는 데 얼마가 드는지 볼게요. 가짜 주소를 많이 만들어 평판을 부풀리는 것을 시빌 공격이라고 해요. 허락은 그 토큰을 하나도 갖고 있지 않아도 할 수 있어서, 드는 돈은 거의 수수료뿐이에요. 앞의 04, 페이지랭크 유도에서 본 \'서로만 가리키는 두 점\'의 함정이 바로 이 농장의 씨앗이에요. 가짜 주소 20개가 다음 주소를 하나씩 허락해서 고리를 만들었어요.',
      '농장 위로 비가 내려요. 모든 점은 매번 다시 출발 몫과, 매달린 점에서 고르게 나눠 주는 몫을 똑같이 받아요. 농장에 들어온 몫은 화살표를 따라 고리를 돌기만 하고, 밖으로 나가는 화살표가 없어서 화살표로는 새지 않아요. 이것을 닫힌 농장이라고 불러요.',
      '식으로 따라가 볼게요. 점 하나가 매번 똑같이 받는 몫을 c라고 해요. 다시 출발 몫 1 빼기 d에, 매달린 점들이 가진 몫을 모두 더한 값 r_dang을 d만큼 곱해 더하고, 점의 개수 |V|로 나눈 값이에요. r_dang은 04의 셋째 조각에서 매달린 점들에게서 모아 다시 나눠 준 물이에요. 그 작은 세계에서는 매달린 점이 D 하나뿐이라 r_D와 같았지만, 실제 그래프에는 매달린 점이 아주 많아서 그 몫을 모두 더해요. 비 한 방울이라고 생각하면 돼요.',
      '농장 전체가 가진 몫을 M이라고 해요. 한 번 돌 때 농장에 들어오는 것은 두 가지예요. 주소마다 내리는 비, 곧 |S| 곱하기 c, 그리고 화살표를 따라 고리 안에 남은 d 곱하기 M이에요. 화살표로 밖에 나가는 몫은 없어요. 그러면 나머지 1 빼기 d 곱하기 M은 어디로 갈까요? 걷는 사람이 순간 이동하는 몫이라서, 그래프의 모든 점으로 고르게 흩어져요. 농장에서 나가는 길은 이 순간 이동 하나뿐이에요. 농장으로 되돌아오는 몫은 비에 이미 들어 있어요.',
      '값이 멈춘 상태에서는 나가는 만큼 들어와요. 순간 이동으로 나가는 1 빼기 d 곱하기 M이, 새로 내리는 비 |S| 곱하기 c와 같아요. 식으로 쓰면 M은 d M 더하기 |S| c이고, 양쪽에서 d M을 빼면 1 빼기 d 곱하기 M이 |S| c가 돼요.',
      '양쪽을 1 빼기 d로 나누고 c를 풀어 쓰면 논문 5장의 식이 나와요. 앞의 분수 |S| 나누기 |V|는 농장의 인구 비율, 곧 공평하게 나누면 받을 몫이고, 뒤의 분수는 농장이 그 몇 배를 모으는지예요. 매달린 점이 없으면 뒤의 분수는 1이에요.',
      '실제 허락 그래프에서 매달린 점들이 가진 몫을 모두 더한 r_dang은 0.382예요. 넣어 보면 0.15 더하기 0.85 곱하기 0.382를 0.15로 나눠서 3.17배가 나와요. d가 0.75면 2.06배, 0.95면 8.68배예요. 아래 단추를 누르면 계기가 바뀌어요. 주소 20개짜리 고리를 실제 그래프에 넣고 같은 코드로 계산해도 3.17배였어요. 모두 수정 분석의 그래프에서 계산한 값이에요. 이 계산에 쓴 풀이 그래프의 점은 6,219,063개로, 03에서 본 허락 그래프의 6,221,665개보다 2,602개 적어요. 금액이 아주 작아서 금액 무게가 0이 되는 쌍만 가진 주소는 풀이 그래프에서 빼기 때문이에요.'
    ],
    html: function () {
      var chips = ['0.75', '0.85', '0.95'].map(function (k) {
        return '<button type="button" class="s10-chip' + (k === '0.85' ? ' on' : '') + '" data-d="' + k + '">d = ' + k + ' →<b>' + S.ff[k] + '배</b></button>';
      }).join('');
      return '<h1 class="t-h1">서로만 허락하는 가짜 주소는 몫을 [[' + S.ff['0.85'] + '배]] 모아요</h1>' +
        '<div class="s10-lead"><p><b>시빌 공격</b>: 가짜 주소를 많이 만들어 평판을 부풀리기</p>' +
        '<p>허락은 잔고가 없어도 할 수 있어요 → 드는 돈은 거의 <b>가스(수수료)</b>뿐</p></div>' +
        '<svg class="abs" id="fig" data-in="none" width="1000" height="600" viewBox="0 0 1000 600" style="left:' + F1.x + 'px;top:' + F1.y + 'px;overflow:visible"></svg>' +
        '<div class="s10-lbl" id="pairlbl" data-in="none" style="left:' + (F1.x + RING.cx - 290) + 'px;top:' + (F1.y + RING.cy + 64) + 'px;width:580px;text-align:center">04(페이지랭크 유도)에서 본 함정: 서로만 가리키는 두 점</div>' +
        '<div class="s10-lbl" id="outlbl" data-in="none" style="left:' + (F1.x + OUTL.x) + 'px;top:' + (F1.y + OUTL.y) + 'px;color:#BFE8FF;white-space:normal;width:124px;padding:2px 10px;border-radius:10px;background:rgba(10,13,20,.82)">$(1-d)\\,M$<br>순간 이동</div>' +
        '<div class="s10-lbl" id="walllbl" data-in="none" style="left:' + (F1.x + RING.cx - RING.wall + 10) + 'px;top:' + (F1.y + RING.cy - RING.wall - 36) + 'px">닫힌 농장 $\\mathcal S$ · 밖으로 나가는 화살표 <b class="ink">0개</b></div>' +
        '<div class="s10-gh" id="gh" data-in="none" style="left:' + (F1.x + TANK.x + TANK.w / 2 - 120) + 'px;top:' + (F1.y + 40) + 'px">인구 비율의 몇 배?</div>' +
        '<div class="s10-gv" id="gv" data-in="none" style="left:' + (F1.x + TANK.x + TANK.w / 2 - 120) + 'px;top:' + (F1.y + 70) + 'px">?</div>' +
        '<p class="abs s10-cap" id="cap" data-in="none" style="left:96px;top:834px;width:1000px"><b>닫힌 농장</b>: 다시 출발 몫과 매달린 점 몫이 계속 들어오고, 화살표로는 나가지 않아요</p>' +
        '<div class="abs s10-chips" id="chips" data-in="none" style="left:96px;top:880px">' + chips + '</div>' +
        '<p class="abs s10-foot" id="foot" data-in="none" style="left:96px;top:938px;width:1000px">실제 그래프에 주소 20개짜리 고리를 넣어 확인해도 <b>' + S.ring20 + '배</b><br>수정 분석의 엔도스랭크 풀이 그래프 · 점 ' + S.nodes + '개 · 화살표 ' + S.edges + '개</p>' +
        '<p class="abs s10-foot" id="vnote" data-in="none" style="left:1124px;top:902px;width:700px">점 ' + S.nodes + '개: 03의 허락 그래프(' + fmt(G_ALLOW_V, 0) + '개)에서 금액 무게가 0인 아주 작은 금액만 가진 주소 <b>' + fmt(G_ALLOW_V - NODES, 0) + '개</b>를 뺀 풀이 그래프예요</p>' +
        '<div class="abs s10-d" id="dv" style="left:1124px;top:168px;width:700px"></div>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      var svg = g.svg = q(el, '#fig');
      var rnd = ctx.rng(1001);
      /* the rest of the graph: faint grey points (and a few grey arrows) */
      var bgL = svgEl('g', { 'class': 'bg' }, svg);
      g.bg = [];
      var tries = 0;
      while (g.bg.length < 54 && tries++ < 4000) {
        var x = 26 + rnd() * 760, y = 26 + rnd() * 516;
        if (Math.hypot(x - RING.cx, y - RING.cy) < RING.wall + 34) continue;
        if (y < 64 && x < 640) continue;   /* keep the two labels of the top band clear */
        if (g.bg.some(function (p) { return Math.hypot(p[0] - x, p[1] - y) < 50; })) continue;
        g.bg.push([x, y]);
      }
      g.bg.forEach(function (p, i) {
        var nb = null, best = 1e9;
        g.bg.forEach(function (o, j) { var dd = Math.hypot(o[0] - p[0], o[1] - p[1]); if (j !== i && dd < best) { best = dd; nb = o; } });
        if (nb && i % 3 === 0 && best < 120) {
          var dx = nb[0] - p[0], dy = nb[1] - p[1], L = Math.hypot(dx, dy);
          svgEl('line', { x1: p[0] + dx / L * 10, y1: p[1] + dy / L * 10, x2: nb[0] - dx / L * 12, y2: nb[1] - dy / L * 12, stroke: C.ink3, 'stroke-width': 1.5, opacity: 0.35 }, bgL);
        }
      });
      g.bgDots = g.bg.map(function (p) { return svgEl('circle', { cx: p[0], cy: p[1], r: 6, fill: C.bg, stroke: C.ink3, 'stroke-width': 2, opacity: 0.75 }, bgL); });
      var bgT = svgEl('text', { x: 6, y: 18, fill: C.ink3, 'font-size': 18 }, bgL);
      bgT.textContent = '회색 점: 나머지 그래프 (전체 점 |V| = ' + S.nodes + '개)';
      g.bgL = bgL;
      /* pooled water inside the ring */
      var defs = svgEl('defs', {}, svg);
      var cid = uid('pool');
      var cp = svgEl('clipPath', { id: cid }, defs);
      svgEl('circle', { cx: RING.cx, cy: RING.cy, r: RING.r - 34 }, cp);
      g.pool = svgEl('rect', { x: RING.cx - RING.r, y: RING.cy + RING.r, width: 2 * RING.r, height: 2 * RING.r, fill: C.hi, 'fill-opacity': 0.13, 'clip-path': 'url(#' + cid + ')' }, svg);
      g.poolTop = svgEl('line', { x1: RING.cx - RING.r, x2: RING.cx + RING.r, y1: RING.cy + RING.r, y2: RING.cy + RING.r, stroke: C.hi, 'stroke-width': 2, opacity: 0.6, 'clip-path': 'url(#' + cid + ')' }, svg);
      g.poolLbl = svgEl('text', { x: RING.cx, y: RING.cy + 70, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 22, 'font-weight': 600 }, svg);
      g.poolLbl.textContent = '농장이 모은 몫 M';
      gsap.set([g.poolLbl], { autoAlpha: 0 });
      /* the wall of the closed farm */
      g.wall = svgEl('circle', { cx: RING.cx, cy: RING.cy, r: RING.wall, fill: 'none', stroke: C.hi, 'stroke-width': 2, 'stroke-dasharray': '7 9', opacity: 0.85 }, svg);
      gsap.set(g.wall, { autoAlpha: 0 });
      /* circulation along the ring (one quiet loop, after step 1) */
      var R = RING.r;
      g.flow = svgEl('path', { d: 'M' + RING.cx + ',' + (RING.cy - R) + ' a' + R + ',' + R + ' 0 1,1 0,' + (2 * R) + ' a' + R + ',' + R + ' 0 1,1 0,' + (-2 * R),
        fill: 'none', stroke: C.allow, 'stroke-width': 3, 'stroke-dasharray': '6 26', 'stroke-linecap': 'round', opacity: 0.5 }, svg);
      gsap.set(g.flow, { autoAlpha: 0 });
      /* ring arrows (each fake address approves the next), then the farm points on top */
      var arL = svgEl('g', {}, svg);
      g.farm = Comp.farm(ctx, svg, { cx: RING.cx, cy: RING.cy, n: 20, radius: RING.r, dotR: RING.dot });
      g.ring = [];
      for (var i = 0; i < 20; i++) {
        var a = g.farm.positions[i], b = g.farm.positions[(i + 1) % 20];
        g.ring.push(Comp.arrow(ctx, arL, { from: a, to: b, kind: 'allow', width: 2.5, head: 10, bend: -5, shorten: [RING.dot + 4, RING.dot + 5], hidden: true }));
      }
      /* the seed: two points that only point at each other (s04-05) */
      var pL = svgEl('g', {}, svg);
      g.pd = [[RING.cx - 80, RING.cy], [RING.cx + 80, RING.cy]];
      g.pairA = Comp.arrow(ctx, pL, { from: g.pd[0], to: g.pd[1], kind: 'allow', width: 3, head: 13, bend: 30, shorten: [28, 30], hidden: true });
      g.pairB = Comp.arrow(ctx, pL, { from: g.pd[1], to: g.pd[0], kind: 'allow', width: 3, head: 13, bend: 30, shorten: [28, 30], hidden: true });
      g.pc = g.pd.map(function (p, k) {
        var gg = svgEl('g', {}, pL);
        var c = svgEl('circle', { cx: p[0], cy: p[1], r: 24, fill: C.bg, stroke: C.hi, 'stroke-width': 2.5, 'stroke-dasharray': '4 4' }, gg);
        var t = svgEl('text', { x: p[0], y: p[1] + 1, 'text-anchor': 'middle', 'dominant-baseline': 'middle', fill: C.ink, 'font-size': 22, 'font-weight': 700 }, gg);
        t.textContent = k ? 'E' : 'D';
        gsap.set(gg, { autoAlpha: 0 });
        return { g: gg, c: c, t: t };
      });
      g.pairLbl = q(el, '#pairlbl');
      gsap.set(g.pairLbl, { autoAlpha: 0 });
      /* the only way out: (1 − d) M leaves by teleport (dashed, the colour of the rain it becomes) */
      var outL = svgEl('g', {}, svg);
      g.out = OUTA.map(function (deg) {
        var a = deg * Math.PI / 180, r0 = RING.r + RING.dot + 6, r1 = RING.wall + 62;
        return Comp.arrow(ctx, outL, { from: [RING.cx + Math.cos(a) * r0, RING.cy + Math.sin(a) * r0], to: [RING.cx + Math.cos(a) * r1, RING.cy + Math.sin(a) * r1],
          kind: 'plain', color: '#BFE8FF', dashed: true, width: 2.5, head: 11, hidden: true });
      });
      g.outLbl = q(el, '#outlbl');
      gsap.set(g.outLbl, { autoAlpha: 0 });
      /* rain drops */
      var targets = g.farm.positions.map(function (p) { return [p[0], p[1] - RING.dot]; }).concat(g.bg.map(function (p) { return [p[0], p[1] - 7]; }));
      var dropL = svgEl('g', {}, svg);
      g.drops = [];
      for (var k2 = 0; k2 < 84; k2++) {
        var tg = k2 < 40 ? targets[k2 % 20] : targets[Math.floor(rnd() * targets.length)];
        var dr = svgEl('line', { x1: tg[0], x2: tg[0], y1: -14, y2: 0, stroke: '#BFE8FF', 'stroke-width': 2, 'stroke-linecap': 'round' }, dropL);
        gsap.set(dr, { autoAlpha: 0 });
        g.drops.push({ el: dr, y: tg[1], x: tg[0], at: rnd() });
      }
      /* gauge (tank) */
      var gL = g.gauge = svgEl('g', {}, svg);
      var tcid = uid('tank');
      svgEl('rect', { x: TANK.x, y: TANK.y, width: TANK.w, height: TANK.h, rx: 16 }, svgEl('clipPath', { id: tcid }, svgEl('defs', {}, gL)));
      svgEl('rect', { x: TANK.x, y: TANK.y, width: TANK.w, height: TANK.h, rx: 16, fill: C.bg2, stroke: C.ink3, 'stroke-width': 2 }, gL);
      g.tfill = svgEl('rect', { x: TANK.x - 2, y: tankY(0), width: TANK.w + 4, height: TANK.h, fill: C.hi, 'fill-opacity': 0.42, 'clip-path': 'url(#' + tcid + ')' }, gL);
      g.ttop = svgEl('line', { x1: TANK.x, x2: TANK.x + TANK.w, y1: tankY(0), y2: tankY(0), stroke: C.hi, 'stroke-width': 3, 'clip-path': 'url(#' + tcid + ')' }, gL);
      [0, 3, 6, 9].forEach(function (v) {
        svgEl('line', { x1: TANK.x + TANK.w, x2: TANK.x + TANK.w + 8, y1: tankY(v), y2: tankY(v), stroke: C.ink3, 'stroke-width': 1.5 }, gL);
        var t = svgEl('text', { x: TANK.x + TANK.w + 14, y: tankY(v) + 6, fill: C.ink3, 'font-size': 18, 'class': 'tnum' }, gL); t.textContent = String(v);
      });
      svgEl('line', { x1: TANK.x - 10, x2: TANK.x + TANK.w + 8, y1: tankY(1), y2: tankY(1), stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '5 5' }, gL);
      var t1 = svgEl('text', { x: TANK.x - 14, y: tankY(1) + 6, 'text-anchor': 'end', fill: C.ink, 'font-size': 19, 'font-weight': 600 }, gL); t1.textContent = '1 = 제 몫';
      g.tankSt = { v: 0 };
      g.gh = q(el, '#gh'); g.gv = q(el, '#gv');
      gsap.set([gL, g.gh, g.gv], { autoAlpha: 0 });
      g.cap = q(el, '#cap'); g.chips = q(el, '#chips'); g.foot = q(el, '#foot'); g.walllbl = q(el, '#walllbl'); g.vnote = q(el, '#vnote');
      gsap.set([g.cap, g.chips, g.foot, g.walllbl, g.vnote], { autoAlpha: 0 });
      /* the d buttons */
      Array.prototype.forEach.call(g.chips.querySelectorAll('.s10-chip'), function (b) {
        ctx.on(b, 'click', function (e) {
          e.stopPropagation();
          var k = b.getAttribute('data-d');
          Array.prototype.forEach.call(g.chips.querySelectorAll('.s10-chip'), function (o) { o.classList.toggle('on', o === b); });
          ctx.add(function () { setTank(ctx, g, FF[k], S.ff[k] + '배', 0.8); });
        });
      });
      /* derivation */
      g.dv = derivePanel(ctx, q(el, '#dv'), [
        { tex: 'c=\\dfrac{1-d+d\\,r_{\\mathrm{dang}}}{|V|}', note: '비 한 방울: 모든 점이 매번 똑같이 받는 몫<br>$r_{\\mathrm{dang}}=\\sum_{\\text{매달린 }u} r_u$: 매달린 점들의 몫의 합 (04의 조각 ③에서 모은 물)' },
        { tex: '\\text{들어옴}=\\underbrace{|\\mathcal S|\\,c}_{\\text{새 비}}+\\underbrace{d\\,M}_{\\text{고리에 남은 몫}}', note: '$M=\\sum_{i\\in\\mathcal S} r_i$: 농장 전체의 몫 · 화살표로 나가는 몫은 0<br>나머지 $(1-d)\\,M$은 순간 이동으로 밖에 나가요' },
        { tex: 'M=d\\,M+|\\mathcal S|\\,c\\;\\Rightarrow\\;\\underbrace{(1-d)\\,M}_{\\text{나감}}=\\underbrace{|\\mathcal S|\\,c}_{\\text{들어옴}}', note: '멈춘 상태: 순간 이동으로 나가는 몫 = 새로 내리는 비' },
        { tex: '\\sum_{i\\in\\mathcal S} r_i=\\part{share}{\\frac{|\\mathcal S|}{|V|}}\\cdot\\part{factor}{\\frac{1-d+d\\,r_{\\mathrm{dang}}}{1-d}}', note: '인구 비율 × 몇 배 · 논문 식 (5.6)', mark: 'factor' },
        { tex: '\\frac{0.15+0.85\\times' + S.rD + '}{0.15}=' + S.ff['0.85'], note: '$d=0.85$, $r_{\\mathrm{dang}}=' + S.rD + '$ (실제 그래프의 매달린 점들이 가진 몫의 합)' }
      ], '유도 · 닫힌 농장');
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      /* the trap returns: D ⇄ E */
      tl.fromTo(g.bgL, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.6 }, 0);
      g.pc.forEach(function (p, k) {
        tl.fromTo(p.g, { autoAlpha: 0, scale: 0.4, svgOrigin: g.pd[k][0] + ' ' + g.pd[k][1] }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp }, 0.1 + k * 0.12);
      });
      tl.add(g.pairA.draw({ duration: 0.5 }), 0.4);
      tl.add(g.pairB.draw({ duration: 0.5 }), 0.55);
      tl.fromTo(g.pairLbl, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: E.out }, 0.7);
      /* … and grows into a ring of 20 */
      var t = 2.0;
      tl.to(g.pairLbl, { autoAlpha: 0, duration: 0.3 }, t);
      tl.to([g.pairA.g, g.pairB.g], { autoAlpha: 0, duration: 0.3 }, t);
      [0, 1].forEach(function (k) {
        var tp = g.farm.positions[k];
        tl.to(g.pc[k].c, { attr: { cx: tp[0], cy: tp[1], r: RING.dot }, duration: 0.7, ease: E.io }, t + 0.1);
        tl.to(g.pc[k].t, { attr: { x: tp[0], y: tp[1] + 1 }, autoAlpha: 0, duration: 0.5, ease: E.io }, t + 0.1);
      });
      tl.set(g.farm.dots.slice(0, 2), { autoAlpha: 1, scale: 1 }, t + 0.8);
      tl.set(g.pc.map(function (p) { return p.g; }), { autoAlpha: 0 }, t + 0.8);
      tl.add(g.farm.grow({ from: 2, to: 20, duration: 1.0 }), t + 0.75);
      g.ring.forEach(function (A, i) { tl.add(A.draw({ duration: 0.35 }), t + 1.0 + i * 0.05); });
      /* the section's ghost numeral would only peek out beside the derivation panel */
      var gh = ctx.root.querySelector('.ritual-ghost');
      if (gh) tl.to(gh, { autoAlpha: 0, duration: 0.6 }, 2.0);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(g.wall, { autoAlpha: 0, scale: 0.94, svgOrigin: RING.cx + ' ' + RING.cy }, { autoAlpha: 0.85, scale: 1, duration: 0.6, ease: E.out }, 0);
        tl.fromTo(g.walllbl, { autoAlpha: 0, x: -10 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: E.out }, 0.3);
        /* rain: two showers over everything; every point gets the same */
        g.drops.forEach(function (d) {
          var at = 0.2 + d.at * 1.9;
          tl.fromTo(d.el, { autoAlpha: 0, y: -30 }, { autoAlpha: 0.75, y: d.y - 2, duration: 0.55, ease: 'power1.in' }, at);
          tl.to(d.el, { autoAlpha: 0, duration: 0.12 }, at + 0.55);
        });
        tl.to(g.pool, { attr: { y: RING.cy + 6 }, duration: 2.4, ease: 'power2.out' }, 0.5);
        tl.to(g.poolTop, { attr: { y1: RING.cy + 6, y2: RING.cy + 6 }, duration: 2.4, ease: 'power2.out' }, 0.5);
        tl.to(g.poolLbl, { autoAlpha: 1, duration: 0.4 }, 1.8);
        tl.fromTo(g.cap, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.9);
        /* the gauge waits at "?" */
        tl.fromTo([g.gauge, g.gh, g.gv], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 1.2);
        tl.call(function () { ctx.add(function () { startFlow(ctx, g); }); }, null, 2.7);
      }
      if (i >= 2 && i <= 5) tl.add(g.dv.show(i - 1), 0);
      if (i === 3) {
        /* (1 − d) M: the only way out of the closed farm is the teleport */
        g.out.forEach(function (A, k) { tl.add(A.draw({ duration: 0.6 }), 0.5 + k * 0.12); });
        tl.fromTo(g.outLbl, { autoAlpha: 0, x: -8 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: E.out }, 1.0);
      }
      if (i === 6) {
        tl.add(g.dv.show(5), 0);
        tl.add(setTank(ctx, g, FF['0.85'], S.ff['0.85'] + '배', 1.6, 1), 0.5);
        tl.fromTo(g.chips, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 1.6);
        tl.fromTo(g.foot, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 2.0);
        tl.fromTo(g.vnote, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 2.2);
      }
    }
  };
  function startFlow(ctx, g) {
    if (g.flowOn) return;
    g.flowOn = true;
    gsap.set(g.flow, { autoAlpha: 0.5 });
    if (!ctx.reduced) gsap.fromTo(g.flow, { strokeDashoffset: 0 }, { strokeDashoffset: -64, duration: 1.6, ease: 'none', repeat: -1 });
  }
  /* gauge to value v (×), readout ends on `text` */
  function setTank(ctx, g, v, text, dur, from) {
    var tl = gsap.timeline(), st = g.tankSt;
    if (from != null) st.v = from;
    var v0 = st.v;
    tl.to(st, { v: v, duration: ctx.reduced ? 0.01 : dur, ease: 'power2.inOut', onUpdate: function () {
      var y = tankY(st.v);
      g.tfill.setAttribute('y', y); g.ttop.setAttribute('y1', y); g.ttop.setAttribute('y2', y);
      g.gv.textContent = fmt(st.v, 2) + '배';
    }, onComplete: function () { g.gv.textContent = text; } }, 0);
    void v0;
    return tl;
  }

  /* ================================================================ s10-02 the star */
  var F2 = { x: 96, y: 236 };
  var STARG = { cx: 430, cy: 254, r: 192, dot: 18, box: 84 };
  var LOGB = { x: 96, y: 840, w: 1000, x0: 44, x1: 960, lmin: -8, lmax: -1, ay: 70 };
  function lx(v) { return LOGB.x0 + (lg(v) - LOGB.lmin) / (LOGB.lmax - LOGB.lmin) * (LOGB.x1 - LOGB.x0); }

  var slide2 = {
    id: 's10-02', title: '별 모양 농장: 한 계약에 몰아주기', time: 50, steps: 7,
    className: 's10',
    tags: ['calc'],
    notes: [
      '농장의 몫을 한 계약에 몰아줄 수도 있어요. 가운데가 점수를 올리고 싶은 목표 계약이에요. 가짜 주소 f개가 목표 계약만 허락하고, 목표도 이 주소들을 허락하는 별 모양을 만들어요.',
      '가짜 주소가 하나씩 생겨요. 주소마다 허락이 두 번이에요. 가짜 주소가 목표를 허락하고, 목표가 가짜 주소를 허락해요. 열 개면 주소 열한 개에 허락 스무 번이에요.',
      '가짜 주소 a는 목표 t 하나만 허락해요. 나가는 길이 하나뿐이니까, 걷는 사람이 a에서 화살표를 따라가면 언제나 t로 가요. 그래서 P_{a,t}는 1이에요.',
      'a의 몫은 두 가지를 더한 거예요. 모두에게 내리는 비 c, 그리고 목표가 a에게 나눠 준 몫 d 곱하기 r_t 곱하기 P_{t,a}예요.',
      '목표의 몫도 같아요. 비 c에, 가짜 주소들이 보낸 몫을 모두 더하고 d를 곱해요. P_{a,t}가 1이니까 r_a를 그대로 더하면 돼요.',
      '둘째 식을 셋째 식에 넣어요. 괄호를 풀면 c가 f번 더해지고, d 제곱 곱하기 r_t 곱하기 P_{t,a}의 합이 남아요. 목표가 나눠 주는 몫은 가짜 주소들에게 모두 가니까, 그 합은 1이에요.',
      'r_t를 왼쪽으로 모으면 r_t 곱하기 1 빼기 d 제곱이 c 곱하기 1 더하기 d f예요. 나누면 주인공 식이 나와요. 가짜 주소를 하나 늘릴 때마다 점수가 d c 나누기 1 빼기 d 제곱만큼 일정하게 늘고, 한 기간에 허락 두 번이면 돼요.',
      '숫자를 넣어 볼게요. 1 빼기 0.85의 제곱은 0.2775예요. c가 7.64 곱하기 10의 마이너스 8제곱이고 f가 10이면, 목표의 점수는 2.62 곱하기 10의 마이너스 6제곱이에요. 실제 그래프에 별을 넣고 계산해도 같은 값이었어요. 아래 눈금에서 보면 코호트의 중앙값을 넘고, 90번째 백분위의 절반쯤에 이르지만, 꼭대기에 비하면 1만 2천분의 1 정도예요.'
    ],
    html: function () {
      return '<h1 class="t-h1">가짜 주소 f개가 목표 계약 [[하나]]에 몰아줘요</h1>' +
        '<p class="s10-lead" style="top:170px">가짜 주소는 목표만 허락하고, 목표도 가짜 주소들을 허락해요</p>' +
        '<div class="abs s10-fc" id="fc" style="left:96px;top:236px">f =<b id="fn">0</b><span class="ink-3"> · 허락</span><b id="an" style="font-size:30px">0</b><span class="ink-3">번 / 기간</span></div>' +
        '<svg class="abs" id="fig" data-in="none" width="1000" height="520" viewBox="0 0 1000 520" style="left:' + F2.x + 'px;top:' + F2.y + 'px;overflow:visible"></svg>' +
        '<p class="abs s10-cap" id="leg" style="left:96px;top:744px;width:1000px">$c$: 모든 주소에 내리는 비 (앞 장) · $d = 0.85$ · 화살표는 모두 허락</p>' +
        '<p class="abs s10-sum" id="sum" data-in="none" style="left:96px;top:796px;width:1040px"><span class="r">f = ' + STAR_M + ' → ' + sciH(S.star) + '</span> : 중앙값보다 높고, 90번째 백분위의 절반쯤, 꼭대기의 약 1만 2천분의 1</p>' +
        '<svg class="abs" id="logb" data-in="none" width="' + LOGB.w + '" height="150" viewBox="0 0 ' + LOGB.w + ' 150" style="left:' + LOGB.x + 'px;top:' + LOGB.y + 'px;overflow:visible"></svg>' +
        '<div class="abs s10-d" id="dv" style="left:1124px;top:166px;width:700px"></div>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      var svg = q(el, '#fig');
      var arL = svgEl('g', {}, svg);
      g.target = Comp.contract(ctx, svg, { x: STARG.cx, y: STARG.cy, size: STARG.box });
      g.tl = svgEl('g', {}, svg);
      svgEl('line', { x1: STARG.cx + STARG.box / 2 + 10, x2: STARG.cx + STARG.r + 30, y1: STARG.cy, y2: STARG.cy, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, g.tl);
      var tlt = svgEl('text', { x: STARG.cx + STARG.r + 40, y: STARG.cy + 9, fill: C.ink, 'font-size': 26, 'font-weight': 700 }, g.tl);
      tlt.textContent = '목표 계약 t';
      g.farm = Comp.farm(ctx, svg, { cx: STARG.cx, cy: STARG.cy, n: STAR_M, radius: STARG.r, dotR: STARG.dot });
      g.arr = g.farm.positions.map(function (p) {
        var tp = [STARG.cx, STARG.cy];
        return [
          Comp.arrow(ctx, arL, { from: p, to: tp, kind: 'allow', width: 2.5, head: 11, bend: 13, shorten: [STARG.dot + 5, STARG.box * 0.62], hidden: true }),
          Comp.arrow(ctx, arL, { from: tp, to: p, kind: 'allow', width: 2.5, head: 11, bend: 13, shorten: [STARG.box * 0.62, STARG.dot + 5], hidden: true })
        ];
      });
      /* name one fake address */
      var p2 = g.farm.positions[2];
      g.aLbl = svgEl('text', { x: p2[0] + 28, y: p2[1] - 8, fill: C.ink, 'font-size': 26, 'font-weight': 700 }, svg);
      g.aLbl.textContent = 'a';
      g.fLbl = svgEl('text', { x: STARG.cx + STARG.r + 46, y: STARG.cy - 150, fill: C.hi, 'font-size': 22, 'font-weight': 600 }, svg);
      g.fLbl.textContent = '가짜 주소 f개';
      gsap.set([g.aLbl, g.fLbl], { autoAlpha: 0 });
      g.fn = q(el, '#fn'); g.an = q(el, '#an'); g.fc = q(el, '#fc');
      g.leg = q(el, '#leg'); g.sum = q(el, '#sum');
      gsap.set([g.sum], { autoAlpha: 0 });
      /* log bar: f = 10 against the cohort */
      var lb = g.lb = q(el, '#logb');
      var ay = LOGB.ay;
      svgEl('line', { x1: LOGB.x0, x2: LOGB.x1, y1: ay, y2: ay, stroke: C.ink2, 'stroke-width': 2 }, lb);
      for (var e = LOGB.lmin; e <= LOGB.lmax; e++) {
        var x = lx(Math.pow(10, e));
        svgEl('line', { x1: x, x2: x, y1: ay - 6, y2: ay + 6, stroke: C.ink3, 'stroke-width': 1.5 }, lb);
        if (e === LOGB.lmin || e === LOGB.lmax) sciSvg(svgEl('text', { x: x + (e === LOGB.lmin ? -8 : 8), y: ay + 6, 'text-anchor': e === LOGB.lmin ? 'end' : 'start', fill: C.ink3, 'font-size': 16, 'class': 'tnum' }, lb), ['1', e]).firstChild.nodeValue = '10';
      }
      var marks = [
        { v: CC, name: 'c', s: null, dy: 0, col: C.ink3 },
        { v: Q[0].score, name: '중앙값', s: S.p50 },
        { v: Q[1].score, name: '90번째', s: S.p90 },
        { v: TOP, name: '꼭대기', s: null, txt: S.top }
      ];
      g.marks = marks.map(function (m) {
        var x = lx(m.v), gg = svgEl('g', {}, lb);
        svgEl('line', { x1: x, x2: x, y1: ay - 12, y2: ay + 12, stroke: m.col || C.ink, 'stroke-width': 3 }, gg);
        var t1 = svgEl('text', { x: x, y: ay + 34, 'text-anchor': 'middle', fill: m.col || C.ink, 'font-size': 19, 'font-weight': 700 }, gg); t1.textContent = m.name;
        if (m.s) sciSvg(svgEl('text', { x: x, y: ay + 56, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 17, 'class': 'tnum' }, gg), m.s);
        else if (m.txt) { var t2 = svgEl('text', { x: x, y: ay + 56, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 17, 'class': 'tnum' }, gg); t2.textContent = m.txt; }
        return gg;
      });
      var fx = lx(STAR_R);
      g.fm = svgEl('g', {}, lb);
      svgEl('circle', { cx: fx, cy: ay, r: 11, fill: C.hi, stroke: C.bg, 'stroke-width': 2 }, g.fm);
      var ft = svgEl('text', { x: fx, y: ay - 44, 'text-anchor': 'middle', fill: C.hi, 'font-size': 20, 'font-weight': 700 }, g.fm); ft.textContent = 'f = ' + STAR_M;
      /* bracket f=10 … top */
      var tx = lx(TOP);
      g.br = svgEl('path', { d: 'M' + (fx + 16) + ',' + (ay - 30) + ' Q' + ((fx + tx) / 2) + ',' + (ay - 64) + ' ' + (tx - 6) + ',' + (ay - 22), fill: 'none', stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, lb);
      g.brT = svgEl('text', { x: (fx + tx) / 2, y: ay - 56, 'text-anchor': 'middle', fill: C.ink, 'font-size': 20, 'font-weight': 600 }, lb); g.brT.textContent = '약 1만 2천분의 1';
      gsap.set([lb], { autoAlpha: 0 });
      g.dv = derivePanel(ctx, q(el, '#dv'), [
        { tex: 'P_{a,t}=1', note: '가짜 주소 $a$는 목표 $t$만 허락 → 나가는 길이 하나뿐' },
        { tex: 'r_a=c+d\\,r_t\\,P_{t,a}', note: '$a$의 몫 = 비 + 목표가 $a$에게 나눠 준 몫' },
        { tex: 'r_t=c+d\\sum_{a} r_a', note: '목표의 몫 = 비 + 가짜 주소 $f$개가 보낸 몫' },
        { tex: '\\begin{aligned}r_t&=c+d\\sum_a\\bigl(c+d\\,r_t P_{t,a}\\bigr)\\\\&=c+d\\,f\\,c+d^2 r_t\\part{sum}{\\textstyle\\sum_a P_{t,a}}\\end{aligned}', note: '2를 3에 넣어요 · 목표의 줄 합 $\\sum_a P_{t,a}=1$', mark: 'sum' },
        { tex: '\\begin{aligned}r_t-d^2r_t&=c\\,(1+d f)\\\\ \\Rightarrow\\ r_t&=\\part{hero}{\\dfrac{c\\,(1+d f)}{1-d^2}}\\end{aligned}', note: '하나 더할 때마다 $+\\,\\dfrac{d\\,c}{1-d^2}$ · 허락 2번', mark: 'hero' },
        { tex: '\\begin{aligned}1-d^2&=1-0.7225=0.2775\\\\ r_t&=\\frac{' + sciT(S.c) + '\\times(1+8.5)}{0.2775}=' + sciT(S.star) + '\\end{aligned}', note: '$f=' + STAR_M + '$ · 실제 그래프에 별을 넣어 계산한 값과 같아요' }
      ], '유도 · 별 모양 농장');
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.add(g.target.pop(), 0.2);
      tl.fromTo(g.tl, { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.45, ease: E.out }, 0.45);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        var per = 0.17, st = { f: 0 };
        g.farm.dots.forEach(function (d, k) {
          var t = 0.1 + k * per;
          tl.fromTo(d, { autoAlpha: 0, scale: 0, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: E.stamp }, t);
          tl.add(g.arr[k][0].draw({ duration: 0.35 }), t + 0.05);
          tl.add(g.arr[k][1].draw({ duration: 0.35 }), t + 0.13);
          tl.call(function (n) { g.fn.textContent = String(n); g.an.textContent = String(2 * n); }, [k + 1], t + 0.1);
        });
        tl.call(function () { g.fn.textContent = String(STAR_M); g.an.textContent = String(STAR_APPR); }, null, 0.1 + STAR_M * per + 0.3);
        tl.fromTo([g.aLbl, g.fLbl], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, stagger: 0.1 }, 0.1 + STAR_M * per);
        void st;
      }
      if (i >= 2 && i <= 6) tl.add(g.dv.show(i - 1), 0);
      if (i === 7) {
        tl.add(g.dv.show(6), 0);
        tl.fromTo(g.sum, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.4);
        tl.set(g.lb, { autoAlpha: 1 }, 0.6);
        tl.fromTo(g.lb.firstChild, { attr: { x2: LOGB.x0 } }, { attr: { x2: LOGB.x1 }, duration: 0.7, ease: E.io }, 0.6);
        tl.fromTo(g.marks, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4, stagger: 0.12, ease: E.out }, 0.9);
        tl.fromTo(g.fm, { autoAlpha: 0, scale: 0.3, svgOrigin: lx(STAR_R) + ' ' + LOGB.ay }, { autoAlpha: 1, scale: 1, duration: 0.45, ease: E.stamp }, 1.5);
        var L = 0; try { L = g.br.getTotalLength(); } catch (e2) { L = 600; }
        tl.fromTo(g.br, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.7, ease: E.io,
          onComplete: function () { g.br.style.strokeDasharray = '4 5'; g.br.style.strokeDashoffset = '0'; } }, 1.9);
        tl.fromTo(g.brT, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 2.4);
      }
    }
  };

  /* ================================================================ s10-03 the 3D ladder */
  var TW = { lmin: -7.35, lmax: -1.25, H: 10, R: 1.7, ringR: 2.05 };
  function ty(l) { return (l - TW.lmin) / (TW.lmax - TW.lmin) * TW.H; }
  var FARM_N = Q[3].ceil || 135895;
  var FARM_PER = 5, FARM_PTS = Math.ceil(FARM_N / FARM_PER);   /* one pink point = 5 fake addresses (27,179 points) */
  function farmPts(f) { return Math.max(0, Math.min(FARM_PTS, Math.ceil(f / FARM_PER - 1e-9))); }
  var CAMS = [
    { theta: 0.62, phi: 1.40, radius: 9.6, target: [0, 1.75, 0] },
    { theta: 0.66, phi: 1.40, radius: 9.6, target: [0, 1.85, 0] },
    { theta: 0.78, phi: 1.38, radius: 10.4, target: [0, 3.0, 0] },
    { theta: 0.92, phi: 1.36, radius: 15.5, target: [0, 4.3, 0] },
    { theta: 1.08, phi: 1.34, radius: 21.5, target: [0, 5.9, 0] },
    { theta: 1.08, phi: 1.34, radius: 21.5, target: [0, 5.9, 0] }
  ];
  var BOX_SVG = '<svg width="260" height="150" viewBox="-130 -75 260 150">' +
    '<g class="pair" opacity="0"><path d="M38,-12 Q66,-30 92,-12" fill="none" stroke="#F5B43C" stroke-width="3.5"/><path d="M87,-20 L95,-10 L83,-8Z" fill="#F5B43C"/>' +
    '<path d="M92,12 Q66,30 38,12" fill="none" stroke="#F5B43C" stroke-width="3.5"/><path d="M43,20 L35,10 L47,8Z" fill="#F5B43C"/>' +
    '<circle cx="112" cy="0" r="16" fill="#0A0D14" stroke="#FF6B8A" stroke-width="3" stroke-dasharray="4 3"/></g>' +
    '<rect x="-30" y="-30" width="60" height="60" rx="13" fill="#10151F" stroke="#E9EDF5" stroke-width="2.5"/>' +
    '<text x="0" y="2" text-anchor="middle" dominant-baseline="middle" fill="#E9EDF5" font-size="22" class="svg-mono">{ }</text></svg>';

  var slide3 = {
    id: 's10-03', title: '꼭대기까지 가짜 주소가 몇 개 필요할까', time: 45, steps: 5,
    className: 's10',
    tags: ['calc'],
    notes: [
      '그러면 이 사다리를 오르는 데 가짜 주소가 몇 개 필요할까요? 왼쪽 탑의 점 하나하나가 매칭 코호트의 계약 하나예요. 높이는 엔도스랭크 점수이고, 로그 눈금이라 한 칸 오를 때마다 점수가 열 배씩 커져요. 대부분의 계약이 바닥 가까이에 몰려 있어요. 가운데 상자가 점수를 올리려는 목표 계약이에요. 처음에는 아무도 허락하지 않은 주소의 점수 c에 있어요.',
      '중앙값은 아주 싸요. 목표 계약과 가짜 주소 하나, 이렇게 두 주소가 서로 허락하기만 하면 돼요. 그림의 분홍 점선 동그라미가 그 짝이고, 허락은 두 번이에요. 별 모양 식에 f = 1을 넣으면 c 곱하기 1 더하기 d를 1 빼기 d 제곱으로 나눈 값이에요. 1 빼기 d 제곱은 1 빼기 d 곱하기 1 더하기 d라서, 약분하면 c 나누기 1 빼기 d, 곧 5.09 곱하기 10의 마이너스 7제곱이에요. 중앙값보다 높아요. 식을 f에 대해 풀면 f가 0 이하로 나와서, 논문은 농장이 없어도 된다고 써요. 하지만 서로 허락할 짝은 하나 있어야 하니까, 실제로 만드는 가짜 주소는 1개예요.',
      '90번째 백분위는 가짜 주소 22개면 넘어요. 한 기간에 허락 44번이에요.',
      '99번째 백분위는 2,074개예요. 숫자가 빨리 커지기 시작해요.',
      '꼭대기까지 가려면 13만 개가 넘게, 약 135,895개가 필요해요. 한 기간에 허락이 27만 번이 넘어요. 탑을 덮은 분홍 안개의 점 하나가 가짜 주소 다섯 개예요. 다만 이 계산은 농장이 이만큼 커지면 전체 점 수도 커져서 c가 줄어드는 효과를 빼고 한 거예요.',
      '꼭대기가 이렇게 비싼 까닭은 보증이 몰려 있기 때문이에요. 꼭대기 계약이 그래프 전체 몫의 3% 정도를 가지는데, 이것은 c의 40만 배가 넘어요. 정리하면, 평범해 보이기는 싸고 꼭대기는 비싸요. 그래서 이 연구의 어떤 점수도 혼자서 경고를 띄우거나 보상을 정하는 데 쓰면 안 된다고 결론지었어요. 토큰을 다섯 개로 줄였어도, 공격하는 쪽은 그 토큰을 허락하는 데 돈이 더 들지 않으니 공격 비용은 그대로예요. 오른쪽의 막대를 끌면 f에 따라 상자 높이와 분홍 점의 수가 식대로 바뀌어요.'
    ],
    html: function () {
      var rungs = [
        { r: 4, q: '꼭대기', n: '약 ' + fmt(Q[3].ceil, 0) + '개' },
        { r: 3, q: '99번째 백분위', n: fmt(Q[2].ceil, 0) + '개' },
        { r: 2, q: '90번째 백분위', n: fmt(Q[1].ceil, 0) + '개' },
        { r: 1, q: '중앙값', n: '짝 1개', d: '목표와 짝 1개가 서로 허락 (허락 2번) · 식의 답은 $f\\le 0$, 곧 농장 없이<br>$f=1$: $c(1+d)/(1-d^2)=c/(1-d)=$ ' + sciH(S.pair) }
      ];
      return '<h1 class="t-h1">평범해 보이기는 [[싸고]], 꼭대기는 비싸요</h1>' +
        '<div class="s10-3d" id="tw" data-in="none" style="left:96px;top:196px;width:1084px;height:764px"></div>' +
        '<p class="abs s10-leg" id="leg" style="left:96px;top:166px;width:1100px"><i style="background:#F5B43C"></i>계약 하나 (매칭 코호트 ' + fmt(pick(DATA, ['contracts', 'meta', 'n'], 15107), 0) + '개) &nbsp; <i style="background:#FF6B8A"></i>가짜 주소 ' + FARM_PER + '개 &nbsp; · 높이 = 엔도스랭크 (로그 눈금, 한 칸 위 = 10배)</p>' +
        '<p class="abs s10-foot" id="foot" style="left:110px;top:966px;width:1040px">상자 높이 = 논문 식 $r_t=c\\,(1+d f)/(1-d^2)$ · 농장이 커지면 $|V|$도 커져 $c$가 줄어드는 효과는 빼고 계산</p>' +
        '<div class="abs s10-cnt" id="cnt" style="left:1196px;top:176px;width:640px">' +
          '<div class="k">필요한 가짜 주소 <span class="ink-3">(식으로 푼 f를 올림 · 중앙값은 짝 1개)</span></div>' +
          '<div class="v"><span class="pre" id="pre" style="display:none">약</span><span id="fN">0</span><span class="u">개</span></div>' +
          '<div class="s">기간마다 허락 <b id="aN">0</b>번 <span class="ink-3">(주소마다 2번)</span></div></div>' +
        '<div class="abs s10-rungs" id="rungs" style="left:1196px;top:440px;width:628px">' + rungs.map(function (r) {
          return '<div class="s10-rung" data-r="' + r.r + '"><span class="ck">' + CHECK + '</span><span class="q">' + r.q + '</span><span class="n">' + r.n + '</span>' +
            (r.d ? '<span class="dd">' + r.d + '</span>' : '') + '</div>';
        }).join('') + '</div>' +
        '<div class="abs s10-con" id="con" data-in="none" style="left:1196px;top:790px;width:628px">' +
          '<p>꼭대기 계약은 전체 몫의 <b>약 3%</b>를 가져요 — $c$의 <b>40만 배</b>가 넘어요</p>' +
          '<p class="big">그래서 어떤 점수도 혼자서 경고나 보상을 정하면 안 돼요</p>' +
          '<p style="font-size:21px;line-height:30px">다섯 토큰으로 줄여도 공격 비용은 그대로예요</p></div>' +
        '<div class="abs s10-range no-advance" id="rng" data-in="none" style="left:1196px;top:384px;width:628px">' +
          '<span>직접 해 보기: f</span><input type="range" min="0" max="1000" step="1" value="1000" aria-label="가짜 주소 수 f"><span class="tnum" id="rv"></span></div>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.cnt = q(el, '#cnt'); g.fN = q(el, '#fN'); g.aN = q(el, '#aN'); g.pre = q(el, '#pre');
      g.rungs = {}; Array.prototype.forEach.call(el.querySelectorAll('.s10-rung'), function (r) { g.rungs[r.getAttribute('data-r')] = r; });
      g.con = q(el, '#con'); g.rng = q(el, '#rng'); g.leg = q(el, '#leg'); g.foot = q(el, '#foot');
      gsap.set([g.con, g.rng], { autoAlpha: 0 });
      var host = q(el, '#tw');
      var T = g.T = ctx.three(host, { fov: 35, camera: CAMS[0], autoRotate: 0, minRadius: 5, maxRadius: 40 });
      g.f = 1; g.st = { f: 0 };
      if (T.failed) return;
      var THREE = T.THREE;
      /* the heaviest scene of the deck: at most one backing pixel per stage pixel … */
      function capPR() {
        if (T.disposed) return;
        var pr = Math.min(1, Deck.pixelRatio());
        if (T.renderer.getPixelRatio() !== pr) { T.renderer.setPixelRatio(pr); T.renderer.setSize(T.width, T.height, false); }
      }
      var resize0 = T._resize;
      T._resize = function () { resize0(); capPR(); T.render(); };
      capPR();
      /* … and once this instance is leaving (next slide, or a step back), stop drawing it every frame:
         the last frame stays on the canvas while the exit fades it out */
      var tick0 = T._tick, frozen = false;
      T._tick = function (dt) {
        if (frozen) return;
        var cur = Deck._cur && Deck._cur();
        if (cur && cur.ctx !== ctx) { frozen = true; T.frameFns.length = 0; return; }
        tick0(dt);
      };
      /* cohort points: real log10 EndorseRank of the 15,107 contracts (zero scores on the floor) */
      var cd = Comp.data.contracts();
      var L = cd && cd.log10.endorserank, n = L ? L.length : 0;
      var pos = new Float32Array(n * 3), col = new Float32Array(n * 3), rnd = ctx.rng(31);
      var amb = Comp.rgb(C.allow), gry = Comp.rgb(C.ink3);
      for (var i = 0; i < n; i++) {
        var a = rnd() * Math.PI * 2, rr = TW.R * Math.sqrt(rnd()), v = L[i];
        var y = isNaN(v) ? -0.55 : ty(v) + (rnd() - 0.5) * 0.02;
        pos[i * 3] = Math.cos(a) * rr; pos[i * 3 + 1] = y; pos[i * 3 + 2] = Math.sin(a) * rr;
        var cc = isNaN(v) ? gry : amb;
        col[i * 3] = cc[0]; col[i * 3 + 1] = cc[1]; col[i * 3 + 2] = cc[2];
      }
      g.cohort = Comp.cloud(ctx, T, { positions: pos, colors: col, size: 3, opacity: 0.5 });
      /* the axis and the quantile rings */
      var axG = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, -0.55, 0), new THREE.Vector3(0, TW.H + 0.4, 0)]);
      T.scene.add(new THREE.Line(axG, new THREE.LineBasicMaterial({ color: new THREE.Color(C.ink3), transparent: true, opacity: 0.6 })));
      function ring(y, color, op) {
        var pts = []; for (var k = 0; k <= 96; k++) { var aa = k / 96 * Math.PI * 2; pts.push(new THREE.Vector3(Math.cos(aa) * TW.ringR, y, Math.sin(aa) * TW.ringR)); }
        var m = new THREE.LineBasicMaterial({ color: new THREE.Color(color), transparent: true, opacity: op });
        var ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), m);
        T.scene.add(ln); return ln;
      }
      g.rings = [];
      var defs = [
        { l: lg(CC), html: '<b>c</b>' + sciH(S.c) + ' · 허락 0개' },
        { l: lg(Q[0].score), html: '<b>중앙값</b>' + sciH(S.p50) },
        { l: lg(Q[1].score), html: '<b>90번째</b>' + sciH(S.p90) },
        { l: lg(Q[2].score), html: '<b>99번째</b>' + sciH(S.p99) },
        { l: lg(Q[3].score), html: '<b>꼭대기</b>' + S.top }
      ];
      defs.forEach(function (d, k) {
        var y = ty(d.l), ln = ring(y, k ? C.ink2 : C.ink3, k ? 0.55 : 0.35);
        var lab = T.label('<span class="s10-rl">' + d.html + '</span>', [TW.ringR + 0.2, y, 0], { anchor: 'left', dx: 10 });
        g.rings.push({ y: y, line: ln, lab: lab });
      });
      /* the farm: one point per FARM_PER fake addresses, filling a growing ball around the target */
      var N = FARM_PTS, fp = new Float32Array(N * 3), fc = new Float32Array(N * 3), rose = Comp.rgb(C.hi), r2 = ctx.rng(77);
      var r0 = 0.5, rm = 3.5;     /* r0: the first points sit just outside the target box */
      for (var j = 0; j < N; j++) {
        var u = r2() * 2 - 1, ph = r2() * Math.PI * 2, s = Math.sqrt(1 - u * u);
        var rad = (r0 + (rm - r0) * Math.pow((j + 1) / N, 1 / 3)) * (0.86 + 0.28 * r2());
        fp[j * 3] = s * Math.cos(ph) * rad; fp[j * 3 + 1] = u * rad * 0.55; fp[j * 3 + 2] = s * Math.sin(ph) * rad;
        fc[j * 3] = rose[0]; fc[j * 3 + 1] = rose[1]; fc[j * 3 + 2] = rose[2];
      }
      g.farm = Comp.cloud(ctx, T, { positions: fp, colors: fc, size: 5.5, opacity: 0.85 });   /* few points: large; smaller as the farm grows */
      g.farmG = new THREE.Group();
      g.farmG.add(g.farm.points);
      T.scene.add(g.farmG);
      g.farm.geometry.setDrawRange(0, 0);
      /* the target box (HTML overlay at the axis) */
      g.boxY = ty(lg(CC));
      g.box = T.label('<div class="s10-box">' + BOX_SVG + '</div>', [0, g.boxY, 0], { anchor: 'center' });
      g.pair = g.box.el.querySelector('.pair');
      g.pairTxt = T.label('<span class="s10-rl on">짝 하나: $c/(1-d)$ = ' + sciH(S.pair) + '</span>', [0, ty(lg(PAIR)), 0], { anchor: 'right', dx: -46 });
      ctx.katex(g.pairTxt.el);
      gsap.set(g.pairTxt.el.firstChild, { autoAlpha: 0 });
      g.farmG.position.y = g.boxY;
      /* keep the ring labels on the right-hand side of the screen whatever the camera angle */
      T.onFrame(function () {
        var th = T.orbit.theta, cx = Math.cos(th), sz = -Math.sin(th);
        g.rings.forEach(function (rg) { rg.lab.pos.set(cx * (TW.ringR + 0.15), rg.y, sz * (TW.ringR + 0.15)); });
      });
      /* the f slider (after the last step): r_t(f) by the closed form */
      var inp = g.rng.querySelector('input'), rv = g.rng.querySelector('#rv');
      g.inp = inp; g.rv = rv;
      function fromSlider(x) { return Math.round(Math.pow(10, x / 1000 * lg(FARM_N + 1)) - 1); }
      ctx.on(inp, 'input', function () {
        var f = fromSlider(+inp.value);
        rv.textContent = 'f = ' + fmt(f, 0);
        setF(g, f, true);
      });
      ['pointerdown', 'click', 'keydown'].forEach(function (t) { ctx.on(inp, t, function (e) { e.stopPropagation(); }); });
      rv.textContent = 'f = ' + fmt(FARM_N, 0);
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (!g.T || g.T.failed) return;
      setF(g, 0, false);
      tl.fromTo(g.T.wrap, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.8 }, 0.1);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (!g.T || g.T.failed) return;
      tl.add(g.T.cameraTo(CAMS[i], { duration: i === 4 ? 3.2 : 1.6 }), 0);
      if (i === 1) {
        /* two addresses approve each other: c/(1−d) > median */
        tl.to(g.pair, { attr: { opacity: 1 }, duration: 0.4 }, 0.2);
        tl.fromTo(g.pairTxt.el.firstChild, { autoAlpha: 0, x: -10 }, { autoAlpha: 1, x: 0, duration: 0.4 }, 1.2);
        tl.add(moveBox(g, ty(lg(PAIR)), 0.9), 0.5);
        tl.call(function () { lightRing(g, 1); lightRung(g, 1); }, null, 1.0);
        /* count what is drawn: one partner, two approvals (the formula's f is ≤ 0: "no farm") */
        tl.call(function () { g.fN.textContent = '1'; g.aN.textContent = '2'; }, null, 0.6);
      }
      if (i >= 2 && i <= 4) {
        var tgt = Q[i - 1].ceil, f0 = i === 2 ? 1 : Q[i - 2].ceil;
        if (i === 2) { tl.to(g.pair, { attr: { opacity: 0 }, duration: 0.3 }, 0.1); tl.to(g.pairTxt.el.firstChild, { autoAlpha: 0, duration: 0.3 }, 0.1); }
        var st = { f: f0 }, dd = i === 4 ? 3.0 : i === 3 ? 2.2 : 1.6;
        tl.to(st, { f: tgt, duration: dd, ease: i === 2 ? 'power1.inOut' : 'power2.in', onUpdate: function () {
          setF(g, st.f, false);
          g.fN.textContent = fmt(Math.round(st.f), 0); g.aN.textContent = fmt(2 * Math.round(st.f), 0);
        }, onComplete: function () {
          setF(g, tgt, false);
          g.fN.textContent = fmt(tgt, 0); g.aN.textContent = fmt(Q[i - 1].appr, 0);
          if (i === 4) g.pre.style.display = '';
        } }, 0.3);
        tl.call(function () { lightRing(g, i); lightRung(g, i); }, null, 0.3 + dd);
        if (i === 3) tl.to(g.farm.material, { size: 4, duration: 1.0 }, 0.3 + dd * 0.5);
        if (i === 4) tl.to(g.farm.material, { opacity: 0.5, size: 2.2, duration: 1.0 }, 0.3 + dd * 0.6);
      }
      if (i === 5) {
        tl.fromTo(g.con.children, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.25, ease: E.out }, 0.2);
        tl.set(g.con, { autoAlpha: 1 }, 0.2);
        tl.fromTo(g.rng, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.2);
      }
    }
  };
  function setF(g, f, fromUser) {
    g.f = f;
    var r = f >= 1 ? rStar(f) : (f > 0 ? CC + (PAIR - CC) * f : CC);
    g.boxY = ty(lg(r));
    if (g.box) g.box.pos.y = g.boxY;
    if (g.farmG) g.farmG.position.y = g.boxY;
    if (g.farm && g.farm.geometry) g.farm.geometry.setDrawRange(0, farmPts(f));
    if (fromUser) {
      for (var k = 1; k <= 4; k++) {
        lightRing(g, k, r >= Q[k - 1].score);
        if (g.rungs[String(k)]) g.rungs[String(k)].classList.toggle('on', r >= Q[k - 1].score);
      }
      g.fN.textContent = fmt(Math.round(f), 0); g.aN.textContent = fmt(2 * Math.round(f), 0);
      g.pre.style.display = 'none';
      if (g.pair) g.pair.setAttribute('opacity', f >= 1 && f < 2 ? 1 : 0);
    }
  }
  function moveBox(g, y, dur) {
    var st = { y: g.boxY };
    return gsap.to(st, { y: y, duration: dur, ease: E.stamp, onUpdate: function () { g.boxY = st.y; g.box.pos.y = st.y; g.farmG.position.y = st.y; } });
  }
  function lightRing(g, k, on) {
    var rg = g.rings[k]; if (!rg) return;
    on = on !== false;
    rg.line.material.color.set(on ? C.ink : C.ink2); rg.line.material.opacity = on ? 0.95 : 0.55;
    rg.lab.el.firstChild.classList.toggle('on', on);
  }
  function lightRung(g, k) { var r = g.rungs[String(k)]; if (r) r.classList.add('on'); }

  /* ================================================================ s10-04 speed follows |E| */
  var PILE = { x: 96, y: 236, w: 330, h: 440, base: 420, cw: 110, xs: [36, 186], per: 50000, cols: 10, cell: 11, row: 7 };
  var RACE = { x: 480, y: 236, w: 700, h: 470, x0: 0, sps: 15, rows: [58, 164, 270, 376], axis: 446, bh: 32 };
  function rx(s) { return RACE.x0 + s * RACE.sps; }
  var SWX = 1206, SWY = 180, SWS = 0.5;

  var slide4 = {
    id: 's10-04', title: '속도는 화살표 수에서 와요 (RQ3)', time: 45, steps: 5,
    className: 's10',
    notes: [
      '계산 속도도 봤어요. 앞의 04에서 말씀드린 것처럼, 페이지랭크를 한 번 되풀이할 때는 화살표 하나마다 곱하기를 한 번 해요. 이 작은 세계라면 화살표가 네 개니까 곱셈 1번부터 4번까지, 네 번이에요. 동그라미 숫자는 곱셈의 차례이고, 화살표의 무게가 아니에요.',
      '그러면 두 그래프의 화살표 수부터 볼게요. 같은 계약을 두고 허락 그래프에는 화살표가 11,210,114개, 송금 그래프에는 25,001,216개 있어요. 송금 쪽이 2.23배 많아요. 행렬을 만드는 일도 화살표마다 한 번씩이라, 일의 양은 화살표 수에 비례해요. 비례한다는 것은 화살표가 두 배면 일도 두 배라는 뜻이에요. 아래 작은 글씨처럼, 풀이 그래프의 점 수는 03에서 본 그래프 크기보다 조금 적어요. 금액 무게가 0이 되는 아주 작은 금액만 가진 주소, 허락 쪽 2,602개와 송금 쪽 2,246개를 풀이 프로그램이 빼기 때문이에요.',
      '이제 두 계산을 같은 풀이 프로그램으로 동시에 출발시켜요. 화면은 실제보다 4배 빠르게 보여 드리고, 시계는 실제 초를 보여 줘요. 준비 실행을 한 번 하고, 시간을 잰 실행 다섯 번의 평균이에요. 엔도스랭크는 10.29초, AWP는 22.37초에 끝났어요.',
      'AWP가 2.17배 오래 걸렸는데, 화살표는 2.23배 많아요. 반복 횟수는 69번과 92번으로 조금 다르지만, 시간 비가 화살표 비에 거의 붙어 있어요. 그러니 엔도스랭크가 빠른 것은 알고리즘이 좋아서가 아니라 허락 그래프가 듬성듬성하기 때문이에요.',
      '송금 층도 함께 걷는 C-PR과 S-PR은 AWP보다도 오래 걸렸어요. C-PR은 두 그래프를 합친 화살표 31,552,359개를 걷고, S-PR은 허락 걷기로 출발점을 정한 뒤 송금 그래프를 다시 걸어요.',
      '마지막으로 한계도 함께 말씀드려요. 코호트에서 계약을 1,000개, 2,000개, 5,000개, 1만 개만 뽑은 작은 표본에서도 시간을 쟀어요. 실선이 시간 비, 점선이 화살표 비예요. 작은 표본에서는 두 선이 꽤 떨어져 있어서, 시간 비가 화살표 비를 잘 따르지 않았어요. 계약 1만 개 이상의 큰 두 단계, 곧 상자 안에서만 두 선이 가까웠어요. 이 단계들은 한 코호트의 부분 표본이라, 그보다 큰 그래프에 대해서는 말하지 않아요.'
    ],
    html: function () {
      function detail(b) { return '점 ' + fmt(b.v, 0) + ' · 반복 ' + b.it + '번 · 메모리 ' + fmt(b.mb, 1) + ' MB'; }
      var fracTeX = '\\frac{' + fmt(B_AWP.s, 2) + '\\text{초}}{' + fmt(B_ER.s, 2) + '\\text{초}}=' + fmt(R_TIME, 2) +
        '\\quad\\approx\\quad\\frac{' + fmt(B_AWP.e, 0).replace(/,/g, '{,}') + '}{' + fmt(B_ER.e, 0).replace(/,/g, '{,}') + '}=' + fmt(R_EDGE, 2);
      return '<h1 class="t-h1">빠른 건 알고리즘이 아니라 [[화살표 수]] 덕분이에요</h1>' +
        '<p class="s10-lead" style="top:168px;width:1080px;font-size:24px">수정 분석 · 같은 계약 · 같은 풀이 프로그램 · 준비 실행 ' + (PROT.warmup_runs || 1) + '번 뒤 시간 잰 실행 ' + (PROT.timed_runs || 5) + '번의 평균</p>' +
        /* piles */
        '<div class="abs" id="pile" data-in="none" style="left:' + PILE.x + 'px;top:' + PILE.y + 'px;width:' + PILE.w + 'px;height:' + PILE.h + 'px"></div>' +
        '<div class="abs s10-pn ink-2" id="ph" style="left:' + PILE.x + 'px;top:' + (PILE.y - 4) + 'px;width:' + PILE.w + 'px;font-weight:600">화살표 수 $|E|$</div>' +
        '<div class="s10-pk c-allow" id="pkE" data-in="none" style="left:' + (PILE.x + PILE.xs[0] + PILE.cw / 2 - 90) + 'px;width:180px">0</div>' +
        '<div class="s10-pk c-xfer" id="pkA" data-in="none" style="left:' + (PILE.x + PILE.xs[1] + PILE.cw / 2 - 90) + 'px;width:180px">0</div>' +
        '<div class="s10-pn c-allow" style="left:' + (PILE.x + PILE.xs[0] + PILE.cw / 2 - 90) + 'px;top:' + (PILE.y + PILE.base + 10) + 'px;width:180px" id="pnE">엔도스랭크</div>' +
        '<div class="s10-pn c-xfer" style="left:' + (PILE.x + PILE.xs[1] + PILE.cw / 2 - 90) + 'px;top:' + (PILE.y + PILE.base + 10) + 'px;width:180px" id="pnA">AWP</div>' +
        '<p class="abs s10-foot" id="pleg" style="left:' + PILE.x + 'px;top:' + (PILE.y + PILE.base + 46) + 'px;width:' + (PILE.w + 40) + 'px">작은 화살표 1개 = 화살표 5만 개</p>' +
        /* race */
        '<svg class="abs" id="race" width="' + RACE.w + '" height="' + RACE.h + '" viewBox="0 0 ' + RACE.w + ' ' + RACE.h + '" style="left:' + RACE.x + 'px;top:' + RACE.y + 'px;overflow:visible"></svg>' +
        '<div class="abs s10-clock" id="clock" style="left:' + (RACE.x + 300) + 'px;top:' + (RACE.y - 8) + 'px;width:400px">실제 시간<b id="clk">0.00</b>초</div>' +
        /* ratios */
        '<div class="abs s10-ratio" id="ratio" data-in="none" style="left:96px;top:744px;width:1100px"><span class="k">시간 </span><span class="num" id="rt">' + fmt(R_TIME, 2) + '배</span>' +
          '<span class="ap" id="ap">≈</span><span class="k">화살표 </span><span class="num" id="re">' + fmt(R_EDGE, 2) + '배</span></div>' +
        '<p class="abs s10-frac" id="frac" data-in="none" style="left:96px;top:812px;width:1100px">$' + fracTeX + '$</p>' +
        '<p class="abs s10-foot" id="vfoot" style="left:96px;top:946px;width:1100px;font-size:19px;line-height:26px">점 수: 풀이 그래프는 금액 무게가 0인 아주 작은 금액만 가진 주소(허락 ' + fmt(G_ALLOW_V - B_ER.v, 0) + '개, 송금 ' + fmt(G_XFER_V - B_AWP.v, 0) + '개)를 빼서 ' + fmt(B_ER.v, 0) + '개 / ' + fmt(B_AWP.v, 0) + '개예요 <span class="ink-3">(03의 ' + fmt(G_ALLOW_V, 0) + '개 / ' + fmt(G_XFER_V, 0) + '개와의 차이)</span></p>' +
        '<p class="abs s10-cap" id="small" data-in="none" style="left:96px;top:892px;width:1100px;font-size:23px;line-height:34px">C-PR ' + fmt(B_CPR.s, 2) + '초 (화살표 ' + fmt(B_CPR.e, 0) + '개) · S-PR ' + fmt(B_SPR.s, 2) + '초 — 송금 층을 걸으면 그 화살표 값을 치러요</p>' +
        /* right column */
        '<div class="abs s10-swc" id="swc" style="left:1600px;top:' + (SWY + 52) + 'px;width:230px;white-space:normal">반복 한 번 =<br>화살표마다<br>곱하기 한 번<br><span class="ink-3">이 작은 세계:</span> <b id="mulN">0</b>번<br><span class="ink-3" style="font-size:18px"><span class="s10-cn">1</span>–<span class="s10-cn">4</span>는 곱셈 차례예요<br>(화살표 무게가 아니에요)</span></div>' +
        '<div class="abs s10-d" id="dv" style="left:1214px;top:446px;width:610px"></div>' +
        '<div class="abs s10-ct" id="ctt" data-in="none" style="left:1214px;top:806px;width:610px">작은 표본에서는 시간 비가 화살표 비를 잘 안 따라요<small>큰 두 단계(계약 1만 개 이상)에서만 가까워요 · 단계별 비는 계산</small></div>' +
        '<svg class="abs" id="chart" data-in="none" width="610" height="140" viewBox="0 0 610 140" style="left:1214px;top:862px;overflow:visible"></svg>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* small world: one iteration multiplies along each of its 4 arrows */
      g.sw = Comp.smallWorld(ctx, el, { x: SWX, y: SWY, scale: SWS, shared: 's10-sw' });
      g.sw.wrap.setAttribute('data-in', 'none');
      g.mul = g.sw.edges.map(function (A, k) {
        var p = A.pointAt(0.5);
        var m = h('div', 's10-mul', el, '곱셈<span class="s10-cn">' + (k + 1) + '</span>');
        m.style.left = (SWX + p.x * SWS) + 'px'; m.style.top = (SWY + p.y * SWS - 30) + 'px';
        gsap.set(m, { xPercent: -50, autoAlpha: 0 });
        return m;
      });
      g.mulN = q(el, '#mulN');
      /* edge piles (canvas) */
      g.pileSt = { p: 0 };
      g.K = Comp.canvas(ctx, q(el, '#pile'), { w: PILE.w, h: PILE.h, onResize: function () { drawPiles(g); } });
      g.nE = Math.round(B_ER.e / PILE.per); g.nA = Math.round(B_AWP.e / PILE.per);
      g.pkE = q(el, '#pkE'); g.pkA = q(el, '#pkA');
      var hE = Math.ceil(g.nE / PILE.cols) * PILE.row, hA = Math.ceil(g.nA / PILE.cols) * PILE.row;
      g.pkE.style.top = (PILE.y + PILE.base - hE - 40) + 'px';
      g.pkA.style.top = (PILE.y + PILE.base - hA - 40) + 'px';
      g.hE = hE; g.hA = hA;
      drawPiles(g);
      gsap.set([g.pkE, g.pkA], { autoAlpha: 0 });
      /* race bars */
      var svg = g.race = q(el, '#race');
      var ax = svgEl('g', {}, svg);
      for (var s = 0; s <= 40; s += 10) {
        svgEl('line', { x1: rx(s), x2: rx(s), y1: 30, y2: RACE.axis, stroke: 'rgba(233,237,245,.06)', 'stroke-width': 1 }, ax);
        var tt = svgEl('text', { x: rx(s), y: RACE.axis + 28, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'tnum' }, ax); tt.textContent = s + '초';
      }
      svgEl('line', { x1: rx(0), x2: rx(40), y1: RACE.axis, y2: RACE.axis, stroke: C.line, 'stroke-width': 1.5 }, ax);
      function row(k, name, b, col, dashed) {
        var y = RACE.rows[k], gg = svgEl('g', {}, svg);
        var nm = svgEl('text', { x: rx(0), y: y - 12, fill: col, 'font-size': 22, 'font-weight': 700 }, gg); nm.textContent = name;
        svgEl('rect', { x: rx(0), y: y, width: rx(40) - rx(0), height: RACE.bh, rx: 8, fill: 'rgba(233,237,245,.03)' }, gg);
        var bar = svgEl('rect', { x: rx(0), y: y, width: 0, height: RACE.bh, rx: 8, fill: col, 'fill-opacity': dashed ? 0.18 : 0.85,
          stroke: dashed ? col : 'none', 'stroke-width': 2, 'stroke-dasharray': dashed ? '6 5' : null }, gg);
        var val = svgEl('text', { x: rx(b.s) + 12, y: y + RACE.bh / 2 + 8, fill: C.ink, 'font-size': 24, 'font-weight': 800, 'class': 'tnum' }, gg); val.textContent = fmt(b.s, 2) + '초';
        var dt = svgEl('text', { x: rx(0), y: y + RACE.bh + 22, fill: C.ink3, 'font-size': 17, 'class': 'tnum' }, gg);
        dt.textContent = b === B_CPR ? '점 ' + fmt(b.v, 0) + ' · 화살표 ' + fmt(b.e, 0) + ' · 반복 ' + b.it + '번' :
          b === B_SPR ? '점 ' + fmt(b.v, 0) + ' · 화살표 ' + fmt(b.e, 0) + ' · 두 번 걸어요' :
          '점 ' + fmt(b.v, 0) + ' · 반복 ' + b.it + '번 · 메모리 ' + fmt(b.mb, 1) + ' MB';
        gsap.set(val, { autoAlpha: 0 });
        return { g: gg, bar: bar, val: val, b: b, nm: nm, dt: dt };
      }
      g.rows = [row(0, '엔도스랭크', B_ER, C.allow), row(1, 'AWP', B_AWP, C.xfer), row(2, 'C-PR (λ = 0.5)', B_CPR, C.cpr), row(3, 'S-PR', B_SPR, C.cpr, true)];
      gsap.set([g.rows[2].g, g.rows[3].g], { autoAlpha: 0 });
      /* ER's finish line across both rows, and the two ratios as chips */
      var xE = rx(B_ER.s);
      g.rbr = svgEl('g', {}, svg);
      svgEl('line', { x1: xE, x2: xE, y1: RACE.rows[1] - 8, y2: RACE.rows[1] + RACE.bh + 8, stroke: C.allow, 'stroke-width': 3 }, g.rbr);
      var rbt = svgEl('text', { x: rx(B_AWP.s) + 112, y: RACE.rows[1] + RACE.bh / 2 + 8, fill: C.ink, 'font-size': 24, 'font-weight': 800, 'class': 'tnum' }, g.rbr);
      rbt.textContent = '× ' + fmt(R_TIME, 2);
      gsap.set(g.rbr, { autoAlpha: 0 });
      g.pbr = h('div', 's10-pk', el, '× ' + fmt(R_EDGE, 2));
      g.pbr.style.left = (PILE.x + PILE.w - 30) + 'px'; g.pbr.style.top = (PILE.y + PILE.base - g.hA + 14) + 'px'; g.pbr.style.color = C.ink;
      gsap.set(g.pbr, { autoAlpha: 0 });
      g.clk = q(el, '#clk'); g.clock = q(el, '#clock');
      g.ratio = q(el, '#ratio'); g.frac = q(el, '#frac'); g.small = q(el, '#small');
      gsap.set([g.ratio, g.frac, g.small], { autoAlpha: 0 });
      /* derivation */
      g.dv = derivePanel(ctx, q(el, '#dv'), [
        { tex: 'r^{\\text{새}}_v\\;\\leftarrow\\;r^{\\text{새}}_v+d\\,r_u\\,P_{u,v}', note: '화살표 $(u\\to v)$마다 곱하기 한 번 → 한 번 돌 때 $|E|$번' },
        { tex: 'T\\;\\approx\\;\\underbrace{\\text{행렬 만들기}}_{\\text{화살표 수에 비례}}+\\;I\\times\\underbrace{\\text{한 번 돌기}}_{\\text{화살표 수에 비례}}', note: '$I$: 반복 횟수 · 비례 = 화살표가 두 배면 일도 두 배' },
        { tex: '\\frac{T_{\\text{AWP}}}{T_{\\text{ER}}}\\;\\approx\\;\\frac{|E|_{\\text{AWP}}}{|E|_{\\text{ER}}}', note: '같은 풀이 프로그램이니까 · 측정: ' + fmt(R_TIME, 2) + ' ≈ ' + fmt(R_EDGE, 2) }
      ], '유도 · 시간과 화살표 수');
      /* stage chart */
      var ch = g.chart = q(el, '#chart');
      var cx0 = 60, cx1 = 540, cy0 = 104, cy1 = 6, rmin = 1.5, rmax = 5;
      function cX(n) { return cx0 + (lg(n) - 3) / (lg(15107) - 3) * (cx1 - cx0); }
      function cY(r) { return cy0 - (r - rmin) / (rmax - rmin) * (cy0 - cy1); }
      [2, 3, 4, 5].forEach(function (r) {
        svgEl('line', { x1: cx0, x2: cx1, y1: cY(r), y2: cY(r), stroke: 'rgba(233,237,245,.07)', 'stroke-width': 1 }, ch);
        var t = svgEl('text', { x: cx0 - 10, y: cY(r) + 6, 'text-anchor': 'end', fill: C.ink3, 'font-size': 16, 'class': 'tnum' }, ch); t.textContent = '×' + r;
      });
      g.band = svgEl('rect', { x: cX(10000) - 18, y: cy1 - 4, width: cX(15107) - cX(10000) + 36, height: cy0 - cy1 + 8, rx: 10, fill: 'rgba(233,237,245,.07)', stroke: 'rgba(233,237,245,.25)', 'stroke-width': 1 }, ch);
      STAGES.forEach(function (st) {
        var t = svgEl('text', { x: cX(st.n), y: cy0 + 26, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 15, 'class': 'tnum' }, ch); t.textContent = fmt(st.n, 0);
      });
      var tN = svgEl('text', { x: cx1 + 30, y: cy0 + 26, fill: C.ink3, 'font-size': 15 }, ch); tN.textContent = '계약';
      function line(key, col, dash) {
        var d = STAGES.map(function (st, k) { return (k ? 'L' : 'M') + cX(st.n).toFixed(1) + ',' + cY(st[key]).toFixed(1); }).join(' ');
        var p = svgEl('path', { d: d, fill: 'none', stroke: col, 'stroke-width': 3, 'stroke-dasharray': dash || null, 'stroke-linejoin': 'round' }, ch);
        var dots = STAGES.map(function (st) { return svgEl('circle', { cx: cX(st.n), cy: cY(st[key]), r: 5, fill: dash ? C.bg : col, stroke: col, 'stroke-width': 2.5 }, ch); });
        return { p: p, dots: dots };
      }
      g.lE = line('re', C.ink2, '7 6');
      g.lT = line('rt', C.ink);
      var la = svgEl('text', { x: cX(STAGES[2].n), y: cY(STAGES[2].re) + 26, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 17, 'font-weight': 600 }, ch); la.textContent = '화살표 비 ' + fmt(STAGES[2].re, 2);
      var lb2 = svgEl('text', { x: cX(STAGES[2].n), y: cY(STAGES[2].rt) - 12, 'text-anchor': 'middle', fill: C.ink, 'font-size': 17, 'font-weight': 600 }, ch); lb2.textContent = '시간 비 ' + fmt(STAGES[2].rt, 2);
      g.chLbl = [la, lb2];
      g.ctt = q(el, '#ctt');
      gsap.set([ch, g.ctt], { autoAlpha: 0 });
      /* what steps back for the last step */
      g.dimmable = ['.s10-lead', '#pile', '#ph', '#pkE', '#pkA', '#pnE', '#pnA', '#pleg', '#race', '#clock', '#ratio', '#frac', '#small', '#vfoot', '#swc', '#dv']
        .map(function (sel) { return q(el, sel); }).concat([g.pbr, g.sw.wrap], g.mul).filter(Boolean);
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo(g.sw.wrap, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out }, 0.1);
      tl.add(g.sw.drawIn({ stagger: 0.08 }), 0.2);
      /* one iteration: the four arrows light in turn, one multiplication each */
      var t0 = 1.4;
      g.sw.edges.forEach(function (A, k) {
        tl.fromTo(A.g, { opacity: 1 }, { opacity: 0.35, duration: 0.18, yoyo: true, repeat: 1 }, t0 + k * 0.45);
        tl.fromTo(g.mul[k], { autoAlpha: 0, y: 8, scale: 0.6 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.3, ease: E.stamp }, t0 + k * 0.45);
        tl.call(function (n) { g.mulN.textContent = String(n); }, [k + 1], t0 + k * 0.45);
      });
      tl.add(g.dv.show(1), t0 + 2.0);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.to(g.pileSt, { p: 1, duration: 1.8, ease: 'power1.inOut', onUpdate: function () { drawPiles(g); } }, 0.1);
        tl.set([g.pkE, g.pkA], { autoAlpha: 1 }, 0.1);
        tl.add(ctx.count(g.pkE, 0, B_ER.e, { decimals: 0, duration: 1.8, final: fmt(B_ER.e, 0) }), 0.1);
        tl.add(ctx.count(g.pkA, 0, B_AWP.e, { decimals: 0, duration: 1.8, final: fmt(B_AWP.e, 0) }), 0.1);
        tl.add(g.dv.show(2), 1.4);
      }
      if (i === 2) {
        /* the race, 4× real time; the clock shows real seconds */
        var st = { t: 0 }, sp = 4, rows = g.rows.slice(0, 2);
        tl.to(st, { t: B_AWP.s, duration: B_AWP.s / sp, ease: 'none', onUpdate: function () {
          rows.forEach(function (r) { r.bar.setAttribute('width', rx(Math.min(st.t, r.b.s)) - rx(0)); });
          g.clk.textContent = fmt(st.t, 2);
        }, onComplete: function () { rows.forEach(function (r) { r.bar.setAttribute('width', rx(r.b.s) - rx(0)); }); g.clk.textContent = fmt(B_AWP.s, 2); } }, 0.2);
        rows.forEach(function (r) {
          tl.fromTo(r.val, { autoAlpha: 0, x: -8 }, { autoAlpha: 1, x: 0, duration: 0.3 }, 0.2 + r.b.s / sp);
          tl.fromTo(r.bar, { attr: { 'fill-opacity': 1 } }, { attr: { 'fill-opacity': 0.85 }, duration: 0.5 }, 0.2 + r.b.s / sp);
        });
      }
      if (i === 3) {
        tl.fromTo(g.rbr, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.45 }, 0);
        tl.fromTo(g.pbr, { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: E.stamp }, 0.3);
        tl.set(g.ratio, { autoAlpha: 1 }, 0.7);
        tl.fromTo(g.ratio.children, { autoAlpha: 0, y: -40 }, { autoAlpha: 1, y: 0, duration: 0.55, ease: 'power3.out', stagger: 0.1 }, 0.7);
        tl.fromTo(q(g.ratio, '#ap'), { scale: 0.3 }, { scale: 1, duration: 0.4, ease: E.stamp }, 1.1);
        tl.fromTo(g.frac, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 1.4);
        tl.add(g.dv.show(3), 1.2);
      }
      if (i === 4) {
        var rows2 = g.rows.slice(2), st2 = { t: 0 }, sp2 = 8;
        tl.fromTo(rows2.map(function (r) { return r.g; }), { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.45, stagger: 0.1, ease: E.out }, 0);
        tl.to(st2, { t: B_CPR.s, duration: B_CPR.s / sp2, ease: 'none', onUpdate: function () {
          rows2.forEach(function (r) { r.bar.setAttribute('width', rx(Math.min(st2.t, r.b.s)) - rx(0)); });
          g.clk.textContent = fmt(st2.t, 2);
        }, onComplete: function () { rows2.forEach(function (r) { r.bar.setAttribute('width', rx(r.b.s) - rx(0)); }); g.clk.textContent = fmt(B_CPR.s, 2); } }, 0.4);
        rows2.forEach(function (r) { tl.fromTo(r.val, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.4 + r.b.s / sp2); });
        tl.fromTo(g.small, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 1.0);
      }
      if (i === 5) {
        /* the small-sample stage chart, on its own: everything else steps back */
        tl.to(g.dimmable, { opacity: 0.16, duration: 0.6, ease: E.io }, 0);
        tl.fromTo(g.ctt, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 0.3);
        tl.set(g.chart, { autoAlpha: 1 }, 0.5);
        [g.lE, g.lT].forEach(function (Ln, k) {
          var L = 0; try { L = Ln.p.getTotalLength(); } catch (e) { L = 600; }
          var dash = k === 0 ? '7 6' : null;
          tl.fromTo(Ln.p, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 1.1, ease: E.io,
            onComplete: function () { Ln.p.style.strokeDasharray = dash || ''; Ln.p.style.strokeDashoffset = ''; } }, 0.6 + k * 0.3);
          tl.fromTo(Ln.dots, { autoAlpha: 0, scale: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.25, stagger: 0.2, ease: E.stamp }, 0.6 + k * 0.3);
        });
        tl.fromTo(g.chLbl, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.5);
        tl.fromTo(g.band, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 1.8);
      }
    }
  };
  /* stacked arrow glyphs; pileSt.p (0 → 1) = how far the stacking has got */
  function drawPiles(g) {
    var K = g.K, c = K.g; K.clear();
    var p = g.pileSt.p;
    [[g.nE, PILE.xs[0], C.allow], [g.nA, PILE.xs[1], C.xfer]].forEach(function (col) {
      var n = col[0], x0 = col[1], shown = Math.round(Math.min(n, n * p));
      c.strokeStyle = col[2]; c.fillStyle = col[2]; c.lineWidth = 1.6;
      for (var k = 0; k < shown; k++) {
        var r = Math.floor(k / PILE.cols), cc = k % PILE.cols;
        var x = x0 + cc * PILE.cell + 1, y = PILE.base - r * PILE.row - 4;
        var fall = (shown - k) < 12 && p < 1 ? (12 - (shown - k)) * -6 : 0;
        y += fall;
        c.globalAlpha = 0.85;
        c.beginPath(); c.moveTo(x, y); c.lineTo(x + 6, y); c.stroke();
        c.beginPath(); c.moveTo(x + 9, y); c.lineTo(x + 5, y - 2.6); c.lineTo(x + 5, y + 2.6); c.closePath(); c.fill();
      }
      c.globalAlpha = 1;
      c.strokeStyle = 'rgba(233,237,245,.25)'; c.lineWidth = 1;
      c.beginPath(); c.moveTo(x0 - 6, PILE.base + 2); c.lineTo(x0 + PILE.cw + 2, PILE.base + 2); c.stroke();
    });
  }

  Deck.section({ id: 's10-sybil-speed', title: '공격 비용과 속도', slides: [slide1, slide2, slide3, slide4] });
})();
