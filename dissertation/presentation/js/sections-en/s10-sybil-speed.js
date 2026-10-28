/* =========================================================================
   s10-sybil-speed — Attack cost and speed (English edition; STORYBOARD.md §2, s10-01 … s10-04)

   s10-01  Sybil farm         the trap of s04-05 (two points that only point at each other) grows
                              into a ring of 20 fake addresses; rain = restart + dangling share;
                              derivation of the closed-cluster equation (thesis Ch. 5); a gauge
                              rises 1 → 3.23× and d buttons 0.75 / 0.85 / 0.95 switch it
   s10-02  star-shaped farm   ten fake addresses pop around one target and approve it both ways;
                              derivation of r_t = c(1 + d f)/(1 − d²); a log bar compares f = 10
                              with the cohort's median, 90th percentile and top
   s10-03  to the top         3D tower of the 6,483 matched-cohort contracts on a log EndorseRank
                              axis (real data); the target climbs: one partner (the pair, 2 approvals)
                              → about 25 → 2,292 → 47,073 fake addresses (one pink point per 5
                              addresses, 9,415 points at the top); approvals must be renewed in
                              every twelve-month score window
   s10-04  speed, iterations  small world: one iteration = one multiplication per edge; edge piles;
                              a 2× race 2.66 s vs 8.53 s; 3.21 > 2.21, = 1.65 (iterations 94/57)
                              × 1.95 (per iteration); C-PR and S-PR; then, as its own last step with
                              the rest dimmed, the subsample stage chart (the time ratio follows the
                              edge ratio at no stage)

   Numbers and sources (R = revised analysis, revised-usd-12m = the thesis's main analysis;
   all read from DECK_DATA, the literals are fallbacks)
     |V| 2,513,982, |E| 3,808,949 (EndorseRank solver graph at T_obs) sybil.revised.json.graph
     2,514,846 / 3,603,300 (graphs as counted in s03)                 results.revised.same_window.graph
     864 = 2,514,846 − 2,513,982 and 1,573 = 3,603,300 − 3,601,727: addresses whose pairs all
       carry a value weight of zero (left out of the solver graphs)    calc; thesis Ch. 4 §dataset
     r_dang (the thesis's r_D: the total share of all dangling nodes) 0.3939 → 0.394 (0.365, 0.419
       at d = 0.75, 0.95); farm factor 2.0956 / 3.232 / 8.9626 → 2.10 / 3.23 / 8.96
                                                                       sybil.revised.json.damping.*
     ring of 20: 3.2317                                                ring20_collects_times_share
     c = 1.928e-7                                                      b_common
     star: f = 10, r_t 6.601e-6 (closed form 6.602e-6), 20 approvals, top 0.02781, ratio 2.374e-4
       (about 1/4,200)                                                 star.*
     cohort quantiles p50 5.817e-7, p90 1.557e-5, p99 1.354e-3, top 0.02781 and farm sizes
       0 / 25.19 (about 25) / 2,291.7 (about 2,292) / 47,072.6 (about 47,073), rounded as in the
       thesis (Ch. 5 and abstract: "about 25 … about 2,292 … about 47,073")
                                                                       farm_size_to_reach_cohort_quantile
     median: the formula gives f ≤ 0 ("no farm"), but the target still needs one partner that it
       approves and that approves it → shown as 1 fake address and 2 approvals; f = 1 in the star
       formula gives c/(1−d) = 1.29e-6 (pair_score)
     2f approvals per window 2 (the pair) / 50 / 4,584 / 94,146 (thesis: about 94,000); box heights
       r_t(f); 1 − d² = 0.2775; 0.0278 / c > 140,000 (highest_over_c 144,200)   calc
     renewal: the score window keeps the approvals of the twelve months before each freeze, so a
       farm emits its approvals again in every window                  thesis Ch. 5 §sybil-cost
     tower points: log10 EndorseRank of the 6,483 contracts            contracts.log10.endorserank
     benchmark: EndorseRank 2.657 s (SD 0.109), 325.3 MB, 57 it., |V| 2,513,982, |E| 3,808,949;
       AWP 8.530 s, 663.7 MB, 94 it., 3,601,727, 8,426,124; C-PR (λ=0.5) 11.563 s, 4,111,490,
       10,562,390, 82 it. (1.36 × AWP); S-PR 10.883 s, 3,603,300, 8,432,635, 151 it. = 56 (the
       allowance layer, same_window.iterations.cpr_l100) + 95; ratios 3.21 (time) and 2.21
       (edges), 1.43 (nodes), 1.65 (iterations), 1.95 (per iteration); 3.00 and 2.56 at d = 0.75,
       0.95; 1 warm-up + 5 timed runs                                  benchmark.revised
     stage ratios 2.85 2.95 2.73 2.21 (edges), 2.63 7.49 3.96 3.21 (time) at n = 1,000 … 6,483
                                                                       calc from benchmark.revised.scaling
   Status tags: s10-01 … s10-03 'calc' (model values evaluated on the revised graph; no label,
   no rule). s10-04 carries no tag (H3 / RQ2 hold largely by construction); every number on it is
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
  function sciH(s) { return s[0] + ' × 10' + sup(s[1]); }               /* ['6.60', -6] -> HTML */
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
  var NODES = pick(SY, ['graph', 'nodes'], 2513982), NEDGES = pick(SY, ['graph', 'edges'], 3808949);
  var RD = pick(SY, ['r_D'], 0.3939);
  var RDD = { '0.75': pick(SY, ['damping', '0.75', 'r_D'], 0.3652), '0.95': pick(SY, ['damping', '0.95', 'r_D'], 0.4191) };
  var FF = { '0.75': pick(SY, ['damping', '0.75', 'farm_factor'], 2.0956), '0.85': pick(SY, ['damping', '0.85', 'farm_factor'], 3.232),
    '0.95': pick(SY, ['damping', '0.95', 'farm_factor'], 8.9626) };
  var RING20 = pick(SY, ['ring20_collects_times_share'], 3.2317);
  var CC = pick(SY, ['b_common'], 1.928e-7);
  var STAR = SY.star || {};
  var STAR_M = STAR.m || 10, STAR_R = STAR.target_score || 6.601e-6, TOP = STAR.highest_cohort_endorserank || 0.02781;
  var STAR_APPR = STAR.approvals_per_window || 20;
  var STAR_RATIO = STAR.ratio_to_highest || STAR_R / TOP;
  var QS = SY.farm_size_to_reach_cohort_quantile || {};
  /* farm sizes: f solved from the closed form and rounded as the thesis rounds them ("about 25, 2,292, 47,073");
     two approvals per farm address and score window */
  var Q = ['p50', 'p90', 'p99', 'p100'].map(function (k, i) {
    var dflt = [[5.817e-7, 0], [1.557e-5, 25.1891], [1.354e-3, 2291.74952], [0.02781, 47072.6474]][i];
    var f = pick(QS, [k, 'farm_addresses'], dflt[1]), n = Math.round(f);
    return { key: k, score: pick(QS, [k, 'score'], dflt[0]), f: f, n: n, appr: 2 * n };
  });
  var PAIR = SYR.pair_score || CC / (1 - DAMP);
  var TOP_C = pick(SYR, ['highest_over_c'], TOP / CC);                  /* the top score in units of c */
  /* graph sizes as s03 counts them; the solver graphs leave out the zero-value-weight addresses */
  var G_ALLOW_V = pick(DATA, ['results', 'revised', 'same_window', 'graph', 'allowance', 'nodes'], 2514846);
  var G_XFER_V = pick(DATA, ['results', 'revised', 'same_window', 'graph', 'transfer', 'nodes'], 3603300);
  /* display strings, written as in the thesis (Ch. 5; checked against the data below) */
  var S = {
    rD: '0.394', rDd: { '0.75': '0.365', '0.95': '0.419' }, ff: { '0.75': '2.10', '0.85': '3.23', '0.95': '8.96' }, ring20: '3.23',
    c: ['1.93', -7], star: ['6.60', -6], p50: ['5.82', -7], p90: ['1.56', -5], p99: ['1.35', -3], top: '0.0278',
    pair: ['1.29', -6], ratio: ['2.4', -4], nodes: fmt(NODES, 0), edges: fmt(NEDGES, 0)
  };
  var INV_RATIO = fmt(Math.round(1 / STAR_RATIO / 100) * 100, 0);        /* 1 / 2.374e-4 ≈ 4,200 */
  var TOP_C_K = fmt(Math.floor(TOP_C / 1e4) * 1e4, 0);                  /* "more than 140,000 times c" */
  (function check() {
    function near(v, s, e) { var x = parseFloat(s) * Math.pow(10, e || 0); return Math.abs(v - x) <= Math.abs(x) * 0.006 + 1e-15; }
    var bad = [];
    if (!near(RD, S.rD)) bad.push('r_D');
    ['0.75', '0.95'].forEach(function (k) { if (!near(RDD[k], S.rDd[k])) bad.push('r_D ' + k); });
    if (Math.abs(STAR_RATIO - parseFloat(S.ratio[0]) * Math.pow(10, S.ratio[1])) > 0.06e-4) bad.push('star ratio');
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
  var B_ER = bm('endorserank', [2.6569, 325.3234, 57, 2513982, 3808949]);
  var B_AWP = bm('awp', [8.5296, 663.6928, 94, 3601727, 8426124]);
  var B_CPR = bm('cpr_l50', [11.5635, 719.06, 82, 4111490, 10562390]);
  var B_SPR = bm('spr', [10.8831, 509.4488, 151, 3603300, 8432635]);
  var R_TIME = pick(BMR, ['derived', 'time_ratio_awp_over_er'], B_AWP.s / B_ER.s);
  var R_EDGE = pick(BMR, ['derived', 'edge_ratio_awp_over_er'], B_AWP.e / B_ER.e);
  /* the time ratio is the iteration ratio times the per-iteration ratio; the latter lies between the node and edge ratios */
  var R_IT = B_AWP.it / B_ER.it, R_PER = (B_AWP.s / B_AWP.it) / (B_ER.s / B_ER.it), R_NODE = B_AWP.v / B_ER.v;
  var R_CPR_AWP = B_CPR.s / B_AWP.s;
  function dampRatio(k, dflt) { var e = pick(BMR, ['damping', k, 'endorserank', 'mean_s'], null), a = pick(BMR, ['damping', k, 'awp', 'mean_s'], null); return e && a ? a / e : dflt; }
  var R_D75 = dampRatio('0.75', 2.998), R_D95 = dampRatio('0.95', 2.564);
  /* S-PR's iterations include the allowance-layer solve that supplies its restart vector */
  var IT_ALLOW = pick(DATA, ['results', 'revised', 'same_window', 'iterations', 'cpr_l100'], 56);
  var PROT = BMR.protocol || { warmup_runs: 1, timed_runs: 5 };
  var STAGES = (BMR.scaling || []).map(function (st) {
    return { n: st.n, er: st.endorserank.mean_s, awp: st.awp.mean_s, eE: st.endorserank.edges, eA: st.awp.edges };
  });
  if (STAGES.length < 2) STAGES = [[1000, 0.498, 1.3073, 485077, 1382177], [2000, 0.3183, 2.3829, 897812, 2647854], [5000, 1.6717, 6.6199, 2577926, 7035600],
    [6483, 2.6569, 8.5296, 3808949, 8426124]].map(function (a) { return { n: a[0], er: a[1], awp: a[2], eE: a[3], eA: a[4] }; });
  STAGES.forEach(function (st) { st.rt = st.awp / st.er; st.re = st.eA / st.eE; });
  var N_MAX = STAGES[STAGES.length - 1].n;
  var K_PEAK = 0; STAGES.forEach(function (st, k) { if (st.rt > STAGES[K_PEAK].rt) K_PEAK = k; });
  var SMALL_NS = STAGES.slice(0, -1).map(function (st) { return fmt(st.n, 0); });   /* the subsamples (the last stage is the full cohort) */

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
    '.s10-frac b{color:var(--ink);font-weight:700}',
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
    var dv = Comp.derive(ctx, host, { lines: lines, head: head || 'Derivation' });
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
    id: 's10-01', title: 'Sybil farm: three times its fair share', time: 50, steps: 6,
    className: 's10',
    tags: ['calc'],
    notes: [
      'Now let us see what it costs to fool this score. Creating many fake addresses to inflate a reputation is called a Sybil attack. An approval can be made without holding any of the token, so the cost is almost only the fees. The trap we saw in section 04, Deriving PageRank, the \'two nodes that point only at each other\', is the seed of this farm. Here 20 fake addresses each approve the next one and form a ring. The numbers come from the allowance graph of EndorseRank, but the same bound holds for C-PR, which also restarts uniformly.',
      'Rain falls on the farm. Every node gets the same restart share and the same share spread evenly from the dangling nodes, every time. The share that enters the farm only goes round the ring along the edges. No edge leads out, so nothing leaks out along the edges. We call this a closed farm.',
      'Let us follow it with a formula. Call c the share that every node gets each time. It is the restart share, 1 minus d, plus d times r_dang, the sum of the shares held by all dangling nodes, divided by the number of nodes |V|. r_dang is the water we collected from the dangling nodes and handed out again in the third piece of section 04. In that small world D was the only dangling node, so it was the same as r_D, but the real graph has very many dangling nodes, so we add up all their shares. Think of c as one raindrop.',
      'Call M the share held by the whole farm. In one sweep, two things come into the farm: the rain on each address, that is |S| times c, and d times M, which stays in the ring along the edges. No share leaves along an edge. So where does the rest, 1 minus d times M, go? It is the share with which the walker teleports, so it spreads evenly over every node of the graph. Teleportation is the only way out of the farm. The share that comes back to the farm is already in the rain.',
      'When the values stop changing, what goes out equals what comes in. The 1 minus d times M that leaves by teleportation equals the new rain, |S| times c. As a formula, M equals d M plus |S| c, and taking d M from both sides gives 1 minus d times M equals |S| c.',
      'Divide both sides by 1 minus d, write c out in full, and we get the equation of Chapter 5 of the thesis. The first fraction, |S| over |V|, is the farm\'s population share, the share it would get if everything were split fairly. The second fraction says how many times that share the farm collects. Without dangling nodes the second fraction is 1.',
      'In the real allowance graph, r_dang, the sum of the shares held by the dangling nodes, is ' + S.rD + '. Putting it in, 0.15 plus 0.85 times ' + S.rD + ', divided by 0.15, gives ' + S.ff['0.85'] + ' times. With d at 0.75 it is ' + S.ff['0.75'] + ' times, and at 0.95 it is ' + S.ff['0.95'] + ' times; r_dang itself moves a little with d, to ' + S.rDd['0.75'] + ' and ' + S.rDd['0.95'] + '. The buttons below switch the gauge. When we added a ring of 20 addresses to the real graph and computed with the same code, we also got ' + S.ring20 + ' times. All of these values were computed on the graph of the revised analysis, built from the approvals of the twelve months before T_obs. The solver graph used here has ' + S.nodes + ' nodes, ' + fmt(G_ALLOW_V - NODES, 0) + ' fewer than the ' + fmt(G_ALLOW_V, 0) + ' of the allowance graph we saw in section 03. That is because addresses whose pairs all carry amounts so small that their value weight is zero are left out of the solver graph.'
    ],
    html: function () {
      var chips = ['0.75', '0.85', '0.95'].map(function (k) {
        return '<button type="button" class="s10-chip' + (k === '0.85' ? ' on' : '') + '" data-d="' + k + '">d = ' + k + ' →<b>' + S.ff[k] + '×</b></button>';
      }).join('');
      return '<h1 class="t-h1">A closed farm collects [[' + S.ff['0.85'] + '×]] its fair share</h1>' +
        '<div class="s10-lead"><p><b>Sybil attack</b>: inflating a reputation with many fake addresses</p>' +
        '<p>An approval needs no balance → the cost is almost only <b>gas (fees)</b></p></div>' +
        '<svg class="abs" id="fig" data-in="none" width="1000" height="600" viewBox="0 0 1000 600" style="left:' + F1.x + 'px;top:' + F1.y + 'px;overflow:visible"></svg>' +
        '<div class="s10-lbl" id="pairlbl" data-in="none" style="left:' + (F1.x + RING.cx - 290) + 'px;top:' + (F1.y + RING.cy + 64) + 'px;width:580px;text-align:center">The trap from 04 (Deriving PageRank):<br>two nodes that point only at each other</div>' +
        '<div class="s10-lbl" id="outlbl" data-in="none" style="left:' + (F1.x + OUTL.x) + 'px;top:' + (F1.y + OUTL.y) + 'px;color:#BFE8FF;white-space:normal;width:124px;padding:2px 10px;border-radius:10px;background:rgba(10,13,20,.82)">$(1-d)\\,M$<br>teleport</div>' +
        '<div class="s10-lbl" id="walllbl" data-in="none" style="left:' + (F1.x + RING.cx - RING.wall + 10) + 'px;top:' + (F1.y + RING.cy - RING.wall - 36) + 'px">Closed farm $\\mathcal S$ · edges leading out: <b class="ink">0</b></div>' +
        '<div class="s10-gh" id="gh" data-in="none" style="left:' + (F1.x + TANK.x + TANK.w / 2 - 120) + 'px;top:' + (F1.y + 40) + 'px">Times its fair share?</div>' +
        '<div class="s10-gv" id="gv" data-in="none" style="left:' + (F1.x + TANK.x + TANK.w / 2 - 120) + 'px;top:' + (F1.y + 70) + 'px">?</div>' +
        '<p class="abs s10-cap" id="cap" data-in="none" style="left:96px;top:834px;width:1000px"><b>Closed farm</b>: restart and dangling shares keep flowing in; no edge leads out</p>' +
        '<div class="abs s10-chips" id="chips" data-in="none" style="left:96px;top:880px">' + chips + '</div>' +
        '<p class="abs s10-foot" id="foot" data-in="none" style="left:96px;top:938px;width:1000px">A ring of 20 addresses added to the real graph also gives <b>' + S.ring20 + '×</b><br>EndorseRank solver graph of the revised analysis · ' + S.nodes + ' nodes · ' + S.edges + ' edges</p>' +
        '<p class="abs s10-foot" id="vnote" data-in="none" style="left:1124px;top:902px;width:700px">' + S.nodes + ' nodes: the allowance graph of 03 (' + fmt(G_ALLOW_V, 0) + ') minus <b>' + fmt(G_ALLOW_V - NODES, 0) + '</b> addresses whose tiny amounts all have value weight 0</p>' +
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
        if (x > 722 && y > 450 && y < 500) continue;   /* … and the gauge's "1 = fair share" label */
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
      bgT.textContent = 'Gray nodes: the rest of the graph (|V| = ' + S.nodes + ' nodes in all)';
      g.bgL = bgL;
      /* pooled water inside the ring */
      var defs = svgEl('defs', {}, svg);
      var cid = uid('pool');
      var cp = svgEl('clipPath', { id: cid }, defs);
      svgEl('circle', { cx: RING.cx, cy: RING.cy, r: RING.r - 34 }, cp);
      g.pool = svgEl('rect', { x: RING.cx - RING.r, y: RING.cy + RING.r, width: 2 * RING.r, height: 2 * RING.r, fill: C.hi, 'fill-opacity': 0.13, 'clip-path': 'url(#' + cid + ')' }, svg);
      g.poolTop = svgEl('line', { x1: RING.cx - RING.r, x2: RING.cx + RING.r, y1: RING.cy + RING.r, y2: RING.cy + RING.r, stroke: C.hi, 'stroke-width': 2, opacity: 0.6, 'clip-path': 'url(#' + cid + ')' }, svg);
      g.poolLbl = svgEl('text', { x: RING.cx, y: RING.cy + 70, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 22, 'font-weight': 600 }, svg);
      g.poolLbl.textContent = 'share M held by the farm';
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
      var t1 = svgEl('text', { x: TANK.x - 14, y: tankY(1) + 6, 'text-anchor': 'end', fill: C.ink, 'font-size': 19, 'font-weight': 600 }, gL); t1.textContent = '1 = fair share';
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
          ctx.add(function () { setTank(ctx, g, FF[k], S.ff[k] + '×', 0.8); });
        });
      });
      /* derivation */
      g.dv = derivePanel(ctx, q(el, '#dv'), [
        { tex: 'c=\\dfrac{1-d+d\\,r_{\\mathrm{dang}}}{|V|}', note: 'One raindrop: the share every node gets each time<br>$r_{\\mathrm{dang}}=\\sum_{\\text{dangling }u} r_u$: total share of the dangling nodes<br>(the water collected in piece ③ of 04)' },
        { tex: '\\text{in}=\\underbrace{|\\mathcal S|\\,c}_{\\text{new rain}}+\\underbrace{d\\,M}_{\\text{share kept in the ring}}', note: '$M=\\sum_{i\\in\\mathcal S} r_i$: share of the whole farm · share leaving along edges: 0<br>The rest, $(1-d)\\,M$, leaves by teleportation' },
        { tex: 'M=d\\,M+|\\mathcal S|\\,c\\;\\Rightarrow\\;\\underbrace{(1-d)\\,M}_{\\text{out}}=\\underbrace{|\\mathcal S|\\,c}_{\\text{in}}', note: 'Steady state: share leaving by teleportation = new rain' },
        { tex: '\\sum_{i\\in\\mathcal S} r_i=\\part{share}{\\frac{|\\mathcal S|}{|V|}}\\cdot\\part{factor}{\\frac{1-d+d\\,r_{\\mathrm{dang}}}{1-d}}', note: 'population share × how many times · thesis Eq. (5.6)', mark: 'factor' },
        { tex: '\\frac{0.15+0.85\\times' + S.rD + '}{0.15}=' + S.ff['0.85'], note: '$d=0.85$, $r_{\\mathrm{dang}}=' + S.rD + '$ (sum over the real graph’s dangling nodes)' }
      ], 'Derivation · closed farm');
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
        tl.add(setTank(ctx, g, FF['0.85'], S.ff['0.85'] + '×', 1.6, 1), 0.5);
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
      g.gv.textContent = fmt(st.v, 2) + '×';
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
    id: 's10-02', title: 'Star-shaped farm: all on one contract', time: 50, steps: 7,
    className: 's10',
    tags: ['calc'],
    notes: [
      'The farm can also pour its share into one contract. The one in the middle is the target contract, whose score the attacker wants to raise. f fake addresses approve only the target, and the target approves these addresses back, so they form a star.',
      'The fake addresses appear one by one. Each address means two approvals: the fake address approves the target, and the target approves the fake address. With ten of them, that is eleven addresses and twenty approvals.',
      'Fake address a approves only the target t. It has only one way out, so a walker who follows an edge from a always goes to t. So P_{a,t} is 1.',
      'The share of a is the sum of two things: the rain c that falls on everyone, and the share the target hands to a, d times r_t times P_{t,a}.',
      'The target\'s share works the same way. Take the rain c, and add d times the sum of the shares sent by the fake addresses. Since P_{a,t} is 1, we just add each r_a as it is.',
      'Put the second equation into the third. Expanding the brackets, c is added f times, and d squared times r_t times the sum of P_{t,a} is left. Everything the target hands out goes to the fake addresses, so that sum is 1.',
      'Collect r_t on the left: r_t times 1 minus d squared equals c times 1 plus d f. Divide, and we get the main formula. Each extra fake address raises the score by the same amount, d c over 1 minus d squared, and it takes two approvals. Because the score keeps only the approvals of the twelve months before each freeze, the farm has to make these approvals again in every score window.',
      'Let us put in numbers. 1 minus 0.85 squared is 0.2775. With c at 1.93 times 10 to the minus 7 and f equal to 10, the target\'s score is 6.60 times 10 to the minus 6. Adding the star to the real graph and computing gave the same value. On the scale below, it passes the cohort\'s median but stays below half of the 90th percentile, and it reaches only 2.4 times 10 to the minus 4 of the top, roughly 1 part in ' + INV_RATIO + '.'
    ],
    html: function () {
      return '<h1 class="t-h1">f fake addresses feed [[one]] target contract</h1>' +
        '<p class="s10-lead" style="top:170px">The fake addresses approve only the target, and the target approves them back</p>' +
        '<div class="abs s10-fc" id="fc" style="left:96px;top:236px">f =<b id="fn">0</b><span class="ink-3"> · </span><b id="an" style="font-size:30px">0</b><span class="ink-3">approvals / window</span></div>' +
        '<svg class="abs" id="fig" data-in="none" width="1000" height="520" viewBox="0 0 1000 520" style="left:' + F2.x + 'px;top:' + F2.y + 'px;overflow:visible"></svg>' +
        '<p class="abs s10-cap" id="leg" style="left:96px;top:744px;width:1000px">$c$: the rain on every address (previous slide) · $d = 0.85$ · every arrow is an approval</p>' +
        '<p class="abs s10-sum" id="sum" data-in="none" style="left:96px;top:796px;width:1040px"><span class="r">f = ' + STAR_M + ' → ' + sciH(S.star) + '</span> : above the median, below half the 90th percentile, ≈ 1/' + INV_RATIO + ' of the top</p>' +
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
      tlt.textContent = 'target contract t';
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
      g.fLbl.textContent = 'f fake addresses';
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
        { v: Q[0].score, name: 'median', s: S.p50 },
        { v: Q[1].score, name: '90th', s: S.p90 },
        { v: TOP, name: 'top', s: null, txt: S.top }
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
      g.brT = svgEl('text', { x: (fx + tx) / 2, y: ay - 56, 'text-anchor': 'middle', fill: C.ink, 'font-size': 20, 'font-weight': 600 }, lb); g.brT.textContent = 'about 1/' + INV_RATIO;
      gsap.set([lb], { autoAlpha: 0 });
      g.dv = derivePanel(ctx, q(el, '#dv'), [
        { tex: 'P_{a,t}=1', note: 'Fake address $a$ approves only target $t$ → only one way out' },
        { tex: 'r_a=c+d\\,r_t\\,P_{t,a}', note: 'share of $a$ = rain + share the target hands to $a$' },
        { tex: 'r_t=c+d\\sum_{a} r_a', note: 'share of the target = rain + shares sent by the $f$ fake addresses' },
        { tex: '\\begin{aligned}r_t&=c+d\\sum_a\\bigl(c+d\\,r_t P_{t,a}\\bigr)\\\\&=c+d\\,f\\,c+d^2 r_t\\part{sum}{\\textstyle\\sum_a P_{t,a}}\\end{aligned}', note: 'Put 2 into 3 · the target’s row sums to one: $\\sum_a P_{t,a}=1$', mark: 'sum' },
        { tex: '\\begin{aligned}r_t-d^2r_t&=c\\,(1+d f)\\\\ \\Rightarrow\\ r_t&=\\part{hero}{\\dfrac{c\\,(1+d f)}{1-d^2}}\\end{aligned}', note: 'each extra address adds $+\\,\\dfrac{d\\,c}{1-d^2}$ · 2 approvals', mark: 'hero' },
        { tex: '\\begin{aligned}1-d^2&=1-0.7225=0.2775\\\\ r_t&=\\frac{' + sciT(S.c) + '\\times(1+8.5)}{0.2775}=' + sciT(S.star) + '\\end{aligned}', note: '$f=' + STAR_M + '$ · same value when the star is added to the real graph' }
      ], 'Derivation · star-shaped farm');
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
  var FARM_N = Q[3].n || 47073;
  var FARM_PER = 5, FARM_PTS = Math.ceil(FARM_N / FARM_PER);   /* one pink point = 5 fake addresses (9,415 points) */
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
    id: 's10-03', title: 'How many fake addresses to reach the top?', time: 45, steps: 5,
    className: 's10',
    tags: ['calc'],
    notes: [
      'So how many fake addresses does it take to climb this ladder? Each point of the tower on the left is one contract of the matched cohort. The height is the EndorseRank score on a log scale, so each level up means a score ten times larger. Most contracts sit close to the floor. The box in the middle is the target contract whose score the attacker wants to raise. It starts at c, the score of an address that nobody approves.',
      'The median is very cheap. It is enough for two addresses, the target contract and one fake address, to approve each other. The pink dashed circle in the picture is that partner, and it takes two approvals. Putting f = 1 into the star formula gives c times 1 plus d, divided by 1 minus d squared. Since 1 minus d squared is 1 minus d times 1 plus d, this cancels to c over 1 minus d, that is ' + S.pair[0] + ' times 10 to the minus ' + (-S.pair[1]) + '. That is above the median. Solving the formula for f gives f of 0 or less, so the thesis says that no farm is needed. But there has to be one partner to approve each other, so in practice the attacker creates 1 fake address.',
      'About ' + fmt(Q[1].n, 0) + ' fake addresses reach the 90th percentile. That is about ' + fmt(Q[1].appr, 0) + ' approvals per score window.',
      'The 99th percentile takes about ' + fmt(Q[2].n, 0) + '. The numbers start to grow fast.',
      'Reaching the top takes about ' + fmt(Q[3].n, 0) + ', that is about ' + fmt(Math.round(Q[3].appr / 1000) * 1000, 0) + ' approvals per score window. Each point of the pink haze covering the tower stands for five fake addresses. Note that this calculation leaves out one effect: a farm this large would also raise the total number of nodes and so lower c.',
      'The top is this expensive because endorsement is concentrated. The top contract holds about 3% of the whole graph\'s share, more than ' + TOP_C_K + ' times c. In short, looking ordinary is cheap and the top is expensive. And because the scores keep only the approvals of the twelve months before each freeze, a farm has to renew its approvals in every score window, at least once a year, to keep the target\'s rank. This study did not measure the gas price, so these counts are not turned into money. The same bound holds for C-PR, so no score should decide rewards without Sybil controls. Keeping only five tokens does not change the attack cost, because approving one of those tokens costs the attacker no more than approving any other token. If you drag the slider on the right, the box height and the number of pink points change with f, as the formula says.'
    ],
    html: function () {
      var rungs = [
        { r: 4, q: 'top', n: 'about ' + fmt(Q[3].n, 0) },
        { r: 3, q: '99th percentile', n: 'about ' + fmt(Q[2].n, 0) },
        { r: 2, q: '90th percentile', n: 'about ' + fmt(Q[1].n, 0) },
        { r: 1, q: 'median', n: '1 partner', d: 'target and 1 partner approve each other (2 approvals)<br>the formula gives $f\\le 0$, i.e. no farm<br>$f=1$: $c(1+d)/(1-d^2)=c/(1-d)=$ ' + sciH(S.pair) }
      ];
      return '<h1 class="t-h1">Looking ordinary is [[cheap]]; the top is expensive</h1>' +
        '<div class="s10-3d" id="tw" data-in="none" style="left:96px;top:196px;width:1084px;height:764px"></div>' +
        '<p class="abs s10-leg" id="leg" style="left:96px;top:166px;width:1100px"><i style="background:#F5B43C"></i>one contract (matched cohort, ' + fmt(pick(DATA, ['contracts', 'meta', 'n'], 6483), 0) + ') &nbsp; <i style="background:#FF6B8A"></i>' + FARM_PER + ' fake addresses &nbsp; · height = EndorseRank (log scale, one level up = 10×)</p>' +
        '<p class="abs s10-foot" id="foot" style="left:110px;top:966px;width:1040px">box height = thesis formula $r_t=c\\,(1+d f)/(1-d^2)$ · leaves out that a bigger farm also enlarges $|V|$ and so lowers $c$</p>' +
        '<div class="abs s10-cnt" id="cnt" style="left:1196px;top:176px;width:640px">' +
          '<div class="k">Fake addresses needed <span class="ink-3">(f rounded · median: 1 partner)</span></div>' +
          '<div class="v"><span class="pre" id="pre" style="display:none">about</span><span id="fN">0</span></div>' +
          '<div class="s"><b id="aN">0</b> approvals per window <span class="ink-3">(2 per address)</span></div></div>' +
        '<div class="abs s10-rungs" id="rungs" style="left:1196px;top:440px;width:628px">' + rungs.map(function (r) {
          return '<div class="s10-rung" data-r="' + r.r + '"><span class="ck">' + CHECK + '</span><span class="q">' + r.q + '</span><span class="n">' + r.n + '</span>' +
            (r.d ? '<span class="dd">' + r.d + '</span>' : '') + '</div>';
        }).join('') + '</div>' +
        '<div class="abs s10-con" id="con" data-in="none" style="left:1196px;top:800px;width:628px">' +
          '<p>The top holds <b>about 3%</b> of all share, over <b>' + TOP_C_K + '×</b> $c$</p>' +
          '<p class="big" style="font-size:25px">So no score should decide rewards without Sybil controls</p>' +
          '<p style="font-size:21px;line-height:30px">Approvals must be renewed in every twelve-month window · five tokens leave the cost unchanged</p></div>' +
        '<div class="abs s10-range no-advance" id="rng" data-in="none" style="left:1196px;top:384px;width:628px">' +
          '<span>Try it: f</span><input type="range" min="0" max="1000" step="1" value="1000" aria-label="number of fake addresses f"><span class="tnum" id="rv"></span></div>';
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
      /* cohort points: real log10 EndorseRank of the matched-cohort contracts (zero scores on the floor) */
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
        { l: lg(CC), html: '<b>c</b>' + sciH(S.c) + ' · 0 approvals' },
        { l: lg(Q[0].score), html: '<b>median</b>' + sciH(S.p50) },
        { l: lg(Q[1].score), html: '<b>90th</b>' + sciH(S.p90) },
        { l: lg(Q[2].score), html: '<b>99th</b>' + sciH(S.p99) },
        { l: lg(Q[3].score), html: '<b>top</b>' + S.top }
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
      g.pairTxt = T.label('<span class="s10-rl on">one partner: $c/(1-d)$ = ' + sciH(S.pair) + '</span>', [0, ty(lg(PAIR)), 0], { anchor: 'right', dx: -46 });
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
        tl.call(function () { g.fN.textContent = '1'; g.aN.textContent = '2'; g.pre.style.display = 'none'; }, null, 0.6);
      }
      if (i >= 2 && i <= 4) {
        var tgt = Q[i - 1].n, f0 = i === 2 ? 1 : Q[i - 2].n;
        if (i === 2) { tl.to(g.pair, { attr: { opacity: 0 }, duration: 0.3 }, 0.1); tl.to(g.pairTxt.el.firstChild, { autoAlpha: 0, duration: 0.3 }, 0.1); }
        var st = { f: f0 }, dd = i === 4 ? 3.0 : i === 3 ? 2.2 : 1.6;
        tl.to(st, { f: tgt, duration: dd, ease: i === 2 ? 'power1.inOut' : 'power2.in', onUpdate: function () {
          setF(g, st.f, false);
          g.fN.textContent = fmt(Math.round(st.f), 0); g.aN.textContent = fmt(2 * Math.round(st.f), 0);
        }, onComplete: function () {
          setF(g, tgt, false);
          g.fN.textContent = fmt(tgt, 0); g.aN.textContent = fmt(Q[i - 1].appr, 0);
          g.pre.style.display = '';   /* every rung is "about": f solved from the formula, rounded */
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

  /* ================================================================ s10-04 speed follows graph size and iterations */
  var PILE = { x: 96, y: 236, w: 330, h: 440, base: 420, cw: 110, xs: [36, 186], per: 20000, cols: 10, cell: 11, row: 7 };
  var RACE = { x: 480, y: 236, w: 700, h: 470, x0: 0, sps: 48, tmax: 12, tick: 3, rows: [58, 164, 270, 376], axis: 446, bh: 32 };
  function rx(s) { return RACE.x0 + s * RACE.sps; }
  var SWX = 1206, SWY = 180, SWS = 0.5;
  var RACE_SP = 2, RACE_SP2 = 4;   /* the races play 2× and 4× faster than real time */

  var slide4 = {
    id: 's10-04', title: 'Speed follows graph size and iterations (RQ2)', time: 45, steps: 5,
    className: 's10',
    notes: [
      'We also measured how fast the scores compute. As I said in section 04, one PageRank iteration does one multiplication per edge. This small world has four edges, so that is multiplications 1 to 4, four in all. The circled numbers are the order of the multiplications, not edge weights. Each iteration also does a few additions per node.',
      'So first, the edge counts of the two graphs. On the same contracts, the allowance graph has ' + fmt(B_ER.e, 0) + ' edges and the transfer graph has ' + fmt(B_AWP.e, 0) + '. The transfer side has ' + fmt(R_EDGE, 2) + ' times as many edges and ' + fmt(R_NODE, 2) + ' times as many nodes. The work of one iteration grows with the edges and the nodes, and the whole time is that work times the number of iterations. As the small print below says, the solver graphs have slightly fewer nodes than the graph sizes we saw in section 03. The solver leaves out addresses whose amounts are all so small that their value weight is zero: ' + fmt(G_ALLOW_V - B_ER.v, 0) + ' on the allowance side and ' + fmt(G_XFER_V - B_AWP.v, 0) + ' on the transfer side.',
      'Now we start both computations at the same time, with the same solver. The screen runs ' + RACE_SP + ' times faster than real time, and the clock shows real seconds. Each time is the mean of five timed runs after one warm-up run. EndorseRank finished in ' + fmt(B_ER.s, 2) + ' seconds and AWP in ' + fmt(B_AWP.s, 2) + ' seconds.',
      'AWP took ' + fmt(R_TIME, 2) + ' times as long, although it has only ' + fmt(R_EDGE, 2) + ' times as many edges. The time ratio is larger than the edge ratio, because AWP also needs more iterations: ' + B_AWP.it + ' against ' + B_ER.it + ', ' + fmt(R_IT, 2) + ' times as many. One iteration of AWP takes ' + fmt(R_PER, 2) + ' times as long, between the node ratio of ' + fmt(R_NODE, 2) + ' and the edge ratio of ' + fmt(R_EDGE, 2) + '. Multiply the two and you get ' + fmt(R_TIME, 2) + '. With d at 0.75 or 0.95 the ratio becomes ' + fmt(R_D75, 2) + ' or ' + fmt(R_D95, 2) + ', so it does not follow the edge ratio. Both scores use the same solver, so the difference in speed comes from the size of each graph and from the iterations its walk needs there, which this benchmark does not separate. It is no advantage of the EndorseRank algorithm.',
      'C-PR and S-PR, which also walk the transfer layer, took even longer than AWP. C-PR multiplies the matrices of both layers in every iteration, so although it needs fewer iterations, ' + B_CPR.it + ', it takes ' + fmt(B_CPR.s, 2) + ' seconds, ' + fmt(R_CPR_AWP, 2) + ' times as long as AWP. S-PR takes ' + fmt(B_SPR.s, 2) + ' seconds. It first sets its restart points with the allowance walk and then walks the transfer graph, so its ' + B_SPR.it + ' iterations are ' + IT_ALLOW + ' for the allowance layer and ' + (B_SPR.it - IT_ALLOW) + ' for the transfer walk.',
      'Finally, I also want to state a limitation. We also timed subsamples drawn from the cohort: ' + SMALL_NS.slice(0, -1).join(', ') + (SMALL_NS.length > 1 ? ' and ' : '') + SMALL_NS[SMALL_NS.length - 1] + ' contracts. The solid line is the time ratio and the dashed line is the edge ratio. EndorseRank was faster at every stage, but at no stage did the time ratio follow the edge ratio. At ' + fmt(STAGES[K_PEAK].n, 0) + ' contracts the time ratio even reached ' + fmt(STAGES[K_PEAK].rt, 2) + '. The iterations each walk needs differ from stage to stage. These stages are subsamples of one cohort, so they say nothing about graphs larger than that.'
    ],
    html: function () {
      function detail(b) { return fmt(b.v, 0) + ' nodes · ' + b.it + ' iterations · memory ' + fmt(b.mb, 1) + ' MB'; }
      var fracTeX = '\\frac{' + fmt(B_AWP.s, 2) + '\\text{ s}}{' + fmt(B_ER.s, 2) + '\\text{ s}}=' + fmt(R_TIME, 2) + '=' + fmt(R_IT, 2) + '\\times' + fmt(R_PER, 2);
      return '<h1 class="t-h1">Speed comes from [[graph size and iterations]]</h1>' +
        '<p class="s10-lead" style="top:168px;width:1080px;font-size:24px">Revised analysis · same contracts · same solver · mean of ' + (PROT.timed_runs || 5) + ' timed runs after ' + (PROT.warmup_runs || 1) + ' warm-up run</p>' +
        /* piles */
        '<div class="abs" id="pile" data-in="none" style="left:' + PILE.x + 'px;top:' + PILE.y + 'px;width:' + PILE.w + 'px;height:' + PILE.h + 'px"></div>' +
        '<div class="abs s10-pn ink-2" id="ph" style="left:' + PILE.x + 'px;top:' + (PILE.y - 4) + 'px;width:' + PILE.w + 'px;font-weight:600">number of edges $|E|$</div>' +
        '<div class="s10-pk c-allow" id="pkE" data-in="none" style="left:' + (PILE.x + PILE.xs[0] + PILE.cw / 2 - 90) + 'px;width:180px">0</div>' +
        '<div class="s10-pk c-xfer" id="pkA" data-in="none" style="left:' + (PILE.x + PILE.xs[1] + PILE.cw / 2 - 90) + 'px;width:180px">0</div>' +
        '<div class="s10-pn c-allow" style="left:' + (PILE.x + PILE.xs[0] + PILE.cw / 2 - 90) + 'px;top:' + (PILE.y + PILE.base + 10) + 'px;width:180px" id="pnE">EndorseRank</div>' +
        '<div class="s10-pn c-xfer" style="left:' + (PILE.x + PILE.xs[1] + PILE.cw / 2 - 90) + 'px;top:' + (PILE.y + PILE.base + 10) + 'px;width:180px" id="pnA">AWP</div>' +
        '<p class="abs s10-foot" id="pleg" style="left:' + PILE.x + 'px;top:' + (PILE.y + PILE.base + 46) + 'px;width:' + (PILE.w + 40) + 'px">1 small arrow = ' + fmt(PILE.per, 0) + ' edges</p>' +
        /* race */
        '<svg class="abs" id="race" width="' + RACE.w + '" height="' + RACE.h + '" viewBox="0 0 ' + RACE.w + ' ' + RACE.h + '" style="left:' + RACE.x + 'px;top:' + RACE.y + 'px;overflow:visible"></svg>' +
        '<div class="abs s10-clock" id="clock" style="left:' + (RACE.x + 300) + 'px;top:' + (RACE.y - 8) + 'px;width:400px">real time<b id="clk">0.00</b>s</div>' +
        /* ratios */
        '<div class="abs s10-ratio" id="ratio" data-in="none" style="left:96px;top:744px;width:1100px"><span class="k">time </span><span class="num" id="rt">' + fmt(R_TIME, 2) + '×</span>' +
          '<span class="ap" id="ap">&gt;</span><span class="k">edges </span><span class="num" id="re">' + fmt(R_EDGE, 2) + '×</span></div>' +
        '<p class="abs s10-frac" id="frac" data-in="none" style="left:96px;top:812px;width:1100px">$' + fracTeX + '$ &nbsp;← iterations <b>' + fmt(R_IT, 2) + '×</b> (' + B_AWP.it + ' ÷ ' + B_ER.it + ') × one iteration <b>' + fmt(R_PER, 2) + '×</b></p>' +
        '<p class="abs s10-foot" id="vfoot" style="left:96px;top:946px;width:1100px;font-size:19px;line-height:26px">Nodes: the solver graphs leave out addresses whose amounts are all so small that their value weight is 0 (allowance ' + fmt(G_ALLOW_V - B_ER.v, 0) + ', transfer ' + fmt(G_XFER_V - B_AWP.v, 0) + '), so they have ' + fmt(B_ER.v, 0) + ' / ' + fmt(B_AWP.v, 0) + ' nodes <span class="ink-3">(the gap to ' + fmt(G_ALLOW_V, 0) + ' / ' + fmt(G_XFER_V, 0) + ' in 03)</span></p>' +
        '<p class="abs s10-cap" id="small" data-in="none" style="left:96px;top:892px;width:1100px;font-size:23px;line-height:34px">C-PR ' + fmt(B_CPR.s, 2) + ' s = ' + fmt(R_CPR_AWP, 2) + ' × AWP · S-PR ' + fmt(B_SPR.s, 2) + ' s · walking the transfer layer means paying for its size</p>' +
        /* right column */
        '<div class="abs s10-swc" id="swc" style="left:1600px;top:' + (SWY + 52) + 'px;width:230px;white-space:normal">one iteration =<br>one multiplication<br>per edge<br><span class="ink-3">this small world:</span> <b id="mulN">0</b><br><span class="ink-3" style="font-size:18px"><span class="s10-cn">1</span>–<span class="s10-cn">4</span> = their order,<br>not edge weights</span></div>' +
        '<div class="abs s10-d" id="dv" style="left:1214px;top:446px;width:610px"></div>' +
        '<div class="abs s10-ct" id="ctt" data-in="none" style="left:1214px;top:806px;width:610px">At no stage does the time ratio follow the edge ratio<small>EndorseRank faster at every stage · ratios computed</small></div>' +
        '<svg class="abs" id="chart" data-in="none" width="610" height="140" viewBox="0 0 610 140" style="left:1214px;top:862px;overflow:visible"></svg>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* small world: one iteration multiplies along each of its 4 arrows */
      g.sw = Comp.smallWorld(ctx, el, { x: SWX, y: SWY, scale: SWS, shared: 's10-sw' });
      g.sw.wrap.setAttribute('data-in', 'none');
      g.mul = g.sw.edges.map(function (A, k) {
        var p = A.pointAt(0.5);
        var m = h('div', 's10-mul', el, 'mult.<span class="s10-cn">' + (k + 1) + '</span>');
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
      for (var s = 0; s <= RACE.tmax; s += RACE.tick) {
        svgEl('line', { x1: rx(s), x2: rx(s), y1: 30, y2: RACE.axis, stroke: 'rgba(233,237,245,.06)', 'stroke-width': 1 }, ax);
        var tt = svgEl('text', { x: rx(s), y: RACE.axis + 28, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'tnum' }, ax); tt.textContent = s + ' s';
      }
      svgEl('line', { x1: rx(0), x2: rx(RACE.tmax), y1: RACE.axis, y2: RACE.axis, stroke: C.line, 'stroke-width': 1.5 }, ax);
      function row(k, name, b, col, dashed) {
        var y = RACE.rows[k], gg = svgEl('g', {}, svg);
        var nm = svgEl('text', { x: rx(0), y: y - 12, fill: col, 'font-size': 22, 'font-weight': 700 }, gg); nm.textContent = name;
        svgEl('rect', { x: rx(0), y: y, width: rx(RACE.tmax) - rx(0), height: RACE.bh, rx: 8, fill: 'rgba(233,237,245,.03)' }, gg);
        var bar = svgEl('rect', { x: rx(0), y: y, width: 0, height: RACE.bh, rx: 8, fill: col, 'fill-opacity': dashed ? 0.18 : 0.85,
          stroke: dashed ? col : 'none', 'stroke-width': 2, 'stroke-dasharray': dashed ? '6 5' : null }, gg);
        var val = svgEl('text', { x: rx(b.s) + 12, y: y + RACE.bh / 2 + 8, fill: C.ink, 'font-size': 24, 'font-weight': 800, 'class': 'tnum' }, gg); val.textContent = fmt(b.s, 2) + ' s';
        var dt = svgEl('text', { x: rx(0), y: y + RACE.bh + 22, fill: C.ink3, 'font-size': 17, 'class': 'tnum' }, gg);
        dt.textContent = b === B_CPR ? fmt(b.v, 0) + ' nodes · ' + fmt(b.e, 0) + ' edges · ' + b.it + ' iterations' :
          b === B_SPR ? fmt(b.v, 0) + ' nodes · ' + fmt(b.e, 0) + ' edges · ' + b.it + ' iterations = ' + IT_ALLOW + ' + ' + (b.it - IT_ALLOW) :
          fmt(b.v, 0) + ' nodes · ' + b.it + ' iterations · memory ' + fmt(b.mb, 1) + ' MB';
        gsap.set(val, { autoAlpha: 0 });
        return { g: gg, bar: bar, val: val, b: b, nm: nm, dt: dt };
      }
      g.rows = [row(0, 'EndorseRank', B_ER, C.allow), row(1, 'AWP', B_AWP, C.xfer), row(2, 'C-PR (λ = 0.5)', B_CPR, C.cpr), row(3, 'S-PR', B_SPR, C.cpr, true)];
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
        { tex: 'r^{\\text{new}}_v\\;\\leftarrow\\;r^{\\text{new}}_v+d\\,r_u\\,P_{u,v}', note: 'one multiplication per edge $(u\\to v)$ → $|E|$ per sweep' },
        { tex: 'T\\;\\approx\\;\\text{build the matrix}+\\;I\\times\\underbrace{\\text{one sweep}}_{\\text{grows with }|E|\\text{ and }|V|}', note: '$I$: number of iterations · each walk needs its own $I$' },
        { tex: '\\frac{T_{\\text{AWP}}}{T_{\\text{ER}}}=\\frac{I_{\\text{AWP}}}{I_{\\text{ER}}}\\cdot\\frac{t_{\\text{AWP}}}{t_{\\text{ER}}}=' + fmt(R_IT, 2) + '\\cdot' + fmt(R_PER, 2), note: '$t$: time of one iteration · same solver for both' }
      ], 'Derivation · time and iterations');
      /* stage chart */
      var ch = g.chart = q(el, '#chart');
      var cx0 = 60, cx1 = 540, cy0 = 104, cy1 = 6, rmin = 1, rmax = 9;
      function cX(n) { return cx0 + (lg(n) - 3) / (lg(N_MAX) - 3) * (cx1 - cx0); }
      function cY(r) { return cy0 - (r - rmin) / (rmax - rmin) * (cy0 - cy1); }
      [2, 4, 6, 8].forEach(function (r) {
        svgEl('line', { x1: cx0, x2: cx1, y1: cY(r), y2: cY(r), stroke: 'rgba(233,237,245,.07)', 'stroke-width': 1 }, ch);
        var t = svgEl('text', { x: cx0 - 10, y: cY(r) + 6, 'text-anchor': 'end', fill: C.ink3, 'font-size': 16, 'class': 'tnum' }, ch); t.textContent = '×' + r;
      });
      STAGES.forEach(function (st) {
        var t = svgEl('text', { x: cX(st.n), y: cy0 + 26, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 15, 'class': 'tnum' }, ch); t.textContent = fmt(st.n, 0);
      });
      var tN = svgEl('text', { x: cX(N_MAX), y: cy0 + 46, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 15 }, ch); tN.textContent = 'contracts';   /* under the last stage: the English word is too wide to sit after it */
      function line(key, col, dash) {
        var d = STAGES.map(function (st, k) { return (k ? 'L' : 'M') + cX(st.n).toFixed(1) + ',' + cY(st[key]).toFixed(1); }).join(' ');
        var p = svgEl('path', { d: d, fill: 'none', stroke: col, 'stroke-width': 3, 'stroke-dasharray': dash || null, 'stroke-linejoin': 'round' }, ch);
        var dots = STAGES.map(function (st) { return svgEl('circle', { cx: cX(st.n), cy: cY(st[key]), r: 5, fill: dash ? C.bg : col, stroke: col, 'stroke-width': 2.5 }, ch); });
        return { p: p, dots: dots };
      }
      g.lE = line('re', C.ink2, '7 6');
      g.lT = line('rt', C.ink);
      /* label both lines at the stage where the time ratio peaks (n = 2,000) */
      var SP = STAGES[K_PEAK];
      var la = svgEl('text', { x: cX(SP.n), y: cY(SP.re) + 26, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 17, 'font-weight': 600 }, ch); la.textContent = 'edge ratio ' + fmt(SP.re, 2);
      var lb2 = svgEl('text', { x: cX(SP.n), y: cY(SP.rt) - 12, 'text-anchor': 'middle', fill: C.ink, 'font-size': 17, 'font-weight': 600 }, ch); lb2.textContent = 'time ratio ' + fmt(SP.rt, 2);
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
        var st = { t: 0 }, sp = RACE_SP, rows = g.rows.slice(0, 2);
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
        var rows2 = g.rows.slice(2), st2 = { t: 0 }, sp2 = RACE_SP2;
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

  Deck.section({ id: 's10-sybil-speed', title: 'Attack cost and speed', slides: [slide1, slide2, slide3, slide4] });
})();
