/* =========================================================================
   s07-measure — How we measure (English edition; STORYBOARD.md §2, s07-01 … s07-05)
   s07-01  What to compare with             (a three-rung ladder lights up from the bottom; "validation" is
                                             struck out and becomes "intended-construct check")
   s07-02  Kendall's τ: count the pairs     (five cards, a handshake pentagon of 10 pairs, every pair
                                             judged ✓ / ✕ / =, counters, τ_a = 0.7 on a −1…+1 ruler)
   s07-03  With ties: τ_b                   (same cards and pentagon; tie groups; the 10 × 9 rectangle
                                             morphs into the square of equal area → √90; τ_b = 0.738;
                                             side panel: Spearman's ρ)
   s07-04  Bootstrap: resample 400 times    (a bag of 15,107 dots, the light dot draws with replacement,
                                             a histogram fills, 2.5 % cut on each side, the middle band
                                             squashes into the interval bar G9)
   s07-05  Paired difference, margin,       (two overlapping intervals vs their paired difference;
           Bonferroni                        joint scatter; toy table of three resamples; δ band;
                                             5 % → 2.5 % + 2.5 %)

   Numbers and sources (revised digest = R)
     0.585 [0.578, 0.592]     R§2 families.endorserank.allowance  (construct check)
     0.250 [0.237, 0.262]     R§6 taus.t1_in_approve_degree.future_new_approvers  (W0)
     0.231 [0.220, 0.242]     R§6 taus.endorserank.future_new_approvers  (W0)
     −0.019 [−0.026, −0.011]  R§6 contrasts_after[3]  (post hoc)
     114,103,171 pairs        R§3 inter_method.concordance.pairs
     B = 400, seed 42, B = 2,000, δ = 0.010, 97.5 %   params.stats; R§7 delta; R§7 neutral blocks
     0.13 × bootstrap SE      thesis Ch. 3, Statistical tests (Uncertainty) — notes only
     family τ = mean of its 2 proxies  thesis Ch. 3, Family aggregation
   Illustrations (example, computed here): five cards A–E (score 5…1, label 3,4,1,1,0): n_c 8,
   n_d 1, one label tie, τ_a 0.7, τ_b 7/√90 = 0.738, mid-rank ρ 0.872 (the no-tie formula's
   0.875 is in the notes only); s07-05 toy table (0.27/0.25, 0.23/0.21, 0.25/0.23); the
   histogram shape, the bag of dots and the joint scatter (only the cut points are digest values).
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt;
  var DATA = window.DECK_DATA || {};
  var NS = 'http://www.w3.org/2000/svg';
  var STP = (DATA.params || {}).stats || {};
  var B = STP.B || 400, SEED = STP.seed != null ? STP.seed : 42, B2 = STP.B_neutral || 2000, DELTA = STP.delta || 0.01;
  var PAIRS = 114103171, NCOH = 15107;
  try { PAIRS = DATA.results.revised.same_window.inter_method.concordance.pairs || PAIRS; } catch (e) { /* digest value */ }
  try { NCOH = DATA.results.revised.same_window.cohort || NCOH; } catch (e) { /* digest value */ }
  /* digest strings (copied, so that the printed digits are the digest's) */
  var FAM_ER_A = '0.585 [0.578, 0.592]';
  var W0_DEG = '0.250 [0.237, 0.262]', W0_ER = '0.231 [0.220, 0.242]', W0_DIFF = '−0.019 [−0.026, −0.011]';

  function nums(s) { return String(s).replace(/−/g, '-').match(/-?\d+(?:\.\d+)?/g).map(Number); }
  function mfmt(v, d) { return fmt(v, d).replace(/^-/, '−'); }
  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, cls, parent, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; }
  function q(el, sel) { return el.querySelector(sel); }
  function settleShared(ctx, el, key) {
    var had = !!(ctx.prev && ctx.prev.rect && ctx.prev.rect(key));
    if (!had && !ctx.instant && !ctx.reduced) ctx.gsap.fromTo(el, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: 0.15 });
    return had;
  }

  /* ------------------------------------------------------------ styles */
  var CSS = [
    /* s07-01 */
    '.s7-rung{position:absolute;left:200px;width:900px;height:178px;border-radius:22px;border:2px solid var(--line);background:rgba(16,21,31,.7);display:flex;gap:28px;align-items:center;padding:0 30px}',
    '.s7-rung .ic{flex:0 0 auto;width:96px;height:96px;border-radius:20px;background:var(--bg-3);display:flex;align-items:center;justify-content:center}',
    '.s7-rung .ic svg{width:70px;height:70px}',
    '.s7-rung .no{position:absolute;right:26px;top:18px;font-family:var(--font-mono);font-size:17px;color:var(--ink-3);letter-spacing:0}',
    '.s7-rung .tt{font-size:38px;line-height:48px;font-weight:700;letter-spacing:-.02em}',
    '.s7-rung .ds{font-size:26px;line-height:38px;color:var(--ink-2)}',
    '.s7-rung .vv{font-size:26px;line-height:38px;font-weight:600;margin-top:2px}',
    '.s7-rung .vv small{font-size:21px;font-weight:500;color:var(--ink-2)}',
    '.s7-fam{position:absolute;left:1250px;width:574px;padding:14px 20px;border-radius:16px;background:var(--bg-2);border:1px solid var(--line)}',
    '.s7-fam .k{font-size:24px;line-height:32px;font-weight:700}',
    '.s7-fam .v{font-size:21px;line-height:30px;color:var(--ink-2)}',
    '.s7-fam .gl{margin-top:4px;font-size:18px;line-height:25px;color:var(--ink-3)}',
    '.s7-rung .vv small.gl{display:block;font-size:19px;line-height:26px;font-weight:500;color:var(--ink-3)}',
    '.s7-strict{font-size:22px;line-height:30px;color:var(--ink-2);font-weight:600}',
    /* s07-02 / s07-03 */
    '.s7-card{position:absolute;top:0;width:160px;height:290px;border-radius:18px;background:var(--bg-2);border:2px solid var(--line)}',
    '.s7-card .nm{position:absolute;left:0;right:0;top:12px;text-align:center;font-size:30px;line-height:36px;font-weight:800}',
    '.s7-card svg{position:absolute;left:0;top:60px;overflow:visible}',
    '.s7-legend{font-size:21px;line-height:30px;color:var(--ink-2);display:flex;gap:22px;align-items:center}',
    '.s7-hs .a{font-size:30px;line-height:42px;font-weight:700;color:var(--ink)}',
    '.s7-hs .b{margin-top:10px;font-size:52px;line-height:60px;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:var(--ink)}',
    '.s7-hs .b small{font-size:26px;font-weight:600;color:var(--ink-2);margin-left:10px;letter-spacing:0}',
    '.s7-legend i{display:inline-block;width:16px;height:16px;border-radius:3px;margin-right:8px;vertical-align:-2px}',
    '.s7-cmp{border-radius:22px;background:var(--bg-2);border:1px solid var(--line);padding:22px 28px}',
    '.s7-cmp .pr{font-size:52px;line-height:60px;font-weight:800;letter-spacing:-.02em}',
    '.s7-cmp .row{display:flex;gap:18px;align-items:baseline;margin-top:8px;font-size:30px;line-height:42px}',
    '.s7-cmp .row .k{width:80px;font-size:24px;color:var(--ink-3)}',
    '.s7-cmp .row .v{font-weight:700;font-variant-numeric:tabular-nums}',
    '.s7-cmp .vd{margin-top:16px;font-size:30px;line-height:42px;font-weight:700}',
    '.s7-tiles{display:flex;gap:14px}',
    '.s7-tile{flex:1 1 0;border-radius:16px;background:var(--bg-2);border:1px solid var(--line);padding:10px 16px 10px;display:grid;grid-template-columns:auto 1fr;column-gap:12px;align-items:baseline}',
    '.s7-tile .sy{font-size:30px;line-height:44px}',
    '.s7-tile .sy .katex{font-size:30px}',
    '.s7-tile .ct{font-size:42px;line-height:48px;font-weight:800;font-variant-numeric:tabular-nums;text-align:right}',
    '.s7-tile .ds{grid-column:1 / span 2;font-size:18px;line-height:24px;color:var(--ink-2);white-space:nowrap}',
    '.s7-d .eq-panel{padding:22px 30px 14px}',
    '.s7-d .derive-line{padding:6px 0}',
    '.s7-d .derive-tex .katex{font-size:27px}',
    '.s7-d .derive-note{font-size:20px;line-height:28px}',
    '.s7-ruler text{font-size:18px}',
    '.s7-note{font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s7-note b{color:var(--ink);font-variant-numeric:tabular-nums}',
    '.s7-sp{border-radius:22px;background:#10151F;border:1px solid #39435A;padding:22px 28px;box-shadow:0 20px 60px rgba(0,0,0,.5)}',
    '.s7-sp .rs{font-size:24px;line-height:34px;color:var(--ink-2)}',
    '.s7-sp .rs .big{margin-top:10px;font-size:34px;line-height:42px;font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums}',
    '.s7-sp .hd{font-size:26px;line-height:34px;font-weight:700}',
    '.s7-sp .hd small{font-size:20px;font-weight:500;color:var(--ink-2);margin-left:10px}',
    '.s7-sp table{border-collapse:collapse;font-size:22px;line-height:30px;margin-top:12px}',
    '.s7-sp th{font-weight:600;color:var(--ink-3);font-size:18px;padding:5px 12px;text-align:center;border-bottom:1px solid var(--line)}',
    '.s7-sp td{padding:6px 12px;text-align:center;font-variant-numeric:tabular-nums;border-bottom:1px solid rgba(35,43,59,.9)}',
    '.s7-sp td.l{text-align:left;color:var(--ink-2)}',
    '.s7-sp .katex{font-size:26px}',
    '.s7-sp .nt{font-size:20px;line-height:30px;color:var(--ink-2)}',
    /* s07-04 */
    '.s7-lines .l{font-size:28px;line-height:42px;margin-bottom:6px}',
    '.s7-lines .l b{font-variant-numeric:tabular-nums}',
    '.s7-lines .why{font-size:26px;line-height:38px;color:var(--ink-2);margin-bottom:8px}',
    '.s7-lines .why b{color:var(--c-allow);font-weight:800;margin-right:8px}',
    '.s7-res small{font-size:19px;line-height:26px;color:var(--ink-3);margin-top:4px}',
    '.s7-slotlbl{position:absolute;font-size:20px;line-height:28px;color:var(--ink-2);white-space:nowrap}',
    '.s7-chip{position:absolute;padding:4px 12px;border-radius:14px;background:var(--bg-3);border:1px solid var(--c-allow);color:var(--ink);font-size:20px;line-height:28px;white-space:nowrap;font-variant-numeric:tabular-nums}',
    '.s7-cnt{font-size:24px;line-height:32px;color:var(--ink-2)}',
    '.s7-cnt b{font-size:40px;color:var(--ink);font-variant-numeric:tabular-nums;margin:0 6px}',
    '.s7-res{display:flex;flex-direction:column;gap:2px;font-size:22px;line-height:30px;color:var(--ink-2)}',
    '.s7-res b{font-size:30px;color:var(--c-allow)}',
    '.s7-res b{font-variant-numeric:tabular-nums}',
    '.s7-foot{font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s7-foot .katex{font-size:26px}',
    '.s7-foot small{display:block;font-size:19px;line-height:28px;color:var(--ink-3)}',
    /* s07-05 */
    '.s7-sub{font-size:22px;line-height:30px;color:var(--ink-2)}',
    '.s7-var{border-radius:20px;background:var(--bg-2);border:1px solid var(--line);padding:12px 20px}',
    '.s7-var .hd{font-size:18px;line-height:24px;color:var(--ink-3)}',
    '.s7-var table{border-collapse:collapse;width:100%;margin-top:4px;font-size:21px;line-height:28px;font-variant-numeric:tabular-nums}',
    '.s7-var th{font-size:17px;font-weight:600;color:var(--ink-3);text-align:right;padding:2px 8px;border-bottom:1px solid var(--line)}',
    '.s7-var td{text-align:right;padding:2px 8px;color:var(--ink)}',
    '.s7-var td.l, .s7-var th.l{text-align:left;color:var(--ink-2)}',
    '.s7-var th.c-deg{color:var(--c-deg)}', '.s7-var th.c-allow{color:var(--c-allow)}',
    '.s7-var td.d{font-weight:800}',
    '.s7-var .nt{font-size:19px;line-height:27px;color:var(--ink);margin-top:6px}',
    '.s7-scale{display:flex;gap:16px;align-items:center;font-size:21px;line-height:30px;color:var(--ink-2)}',
    '.s7-scale svg{flex:0 0 auto}',
    '.s7-rule{font-size:22px;line-height:32px;color:var(--ink)}',
    '.s7-rule small{display:block;font-size:19px;line-height:26px;color:var(--ink-2)}',
    '.s7-rule .katex{font-size:24px}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s07-style')) return;
    var st = document.createElement('style'); st.id = 's07-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  /* ================================================================ s07-01
     A three-rung ladder: the higher the rung, the stricter the comparison. */
  var ICO = {
    mirror: '<svg viewBox="0 0 70 70" fill="none" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="35" cy="30" rx="20" ry="24" stroke="#A3ADBF" stroke-width="3"/><path d="M35 54v8M24 64h22" stroke="#A3ADBF" stroke-width="3"/><rect x="25" y="30" width="6" height="12" rx="1.5" fill="#F5B43C"/><rect x="34" y="22" width="6" height="20" rx="1.5" fill="#F5B43C" opacity=".7"/><path d="M27 14l12 12" stroke="#E9EDF5" stroke-width="2" opacity=".5"/></svg>',
    pin: '<svg viewBox="0 0 70 70" fill="none" stroke="#E9EDF5" stroke-width="2.6" stroke-linecap="round"><circle cx="35" cy="20" r="13"/><path d="M27 20h16M31 13l8 14M39 13l-8 14"/><path d="M35 33v30" stroke-dasharray="4 5"/></svg>',
    cross: '<svg viewBox="0 0 70 70" fill="none" stroke-linecap="round" stroke-width="3.2"><path d="M8 24h44" stroke="#F5B43C"/><path d="M46 18l8 6-8 6" stroke="#F5B43C"/><circle cx="8" cy="24" r="4" stroke="#F5B43C" stroke-width="2.4"/><path d="M8 46h44" stroke="#3CC4FF"/><path d="M46 40l8 6-8 6" stroke="#3CC4FF"/><path d="M24 14l14 18M38 14L24 32M24 36l14 18M38 36L24 54" stroke="#E9EDF5" stroke-width="2.6"/></svg>'
  };
  var RUNG_Y = [688, 458, 228];
  var slide1 = {
    id: 's07-01', title: 'What to compare with: checks and tests', time: 40, steps: 4,
    notes: [
      'Before we measure whether a score is right, we have to decide what to compare it with. On this ladder, the higher the rung, the stricter the comparison.',
      'The easiest comparison is with proxies from the same window. But these proxies are computed from the very records the score was built from, so part of the agreement is to be expected. That is why I do not call this validation. I call it an intended-construct check. The construct is what the score set out to measure, and the check asks whether the score really measures it. The score is, in a sense, looking at itself in a mirror.',
      'A stricter test freezes the score and asks whether it predicts what happened afterwards. The labels are the new approval pairs and the new transfer senders.',
      'The strictest is an outcome that neither edge type contains. In this study, that is the liquidation of contract traders on GMX V2.',
      'The same-window check has three proxy families: the transfer family, the allowance family and the Sybil-stability family. A Sybil attack means creating many fake addresses to inflate a reputation. The Sybil-stability family looks at whether a contract traded over a long time, steadily and with many counterparties. It is a weak check, so no hypothesis rests on it.'
    ],
    html:
      '<h1 class="t-h1">A same-window check is not [[validation]]</h1>' +
      '<svg class="abs" id="lad" data-in="none" width="1100" height="760" style="left:96px;top:176px;overflow:visible"></svg>' +
      '<div class="abs s7-strict" id="strict" data-in="none" style="left:96px;top:170px">↑ stricter toward the top</div>' +
      '<div class="s7-rung" id="r1" data-in="none" style="top:' + RUNG_Y[0] + 'px"><span class="no">1</span><div class="ic">' + ICO.mirror + '</div>' +
        '<div><div class="tt">Same-window check</div><div class="ds">Compared with proxies from the score’s own records</div>' +
        '<div class="vv" id="vv">→ <span id="vword">validation?</span></div></div></div>' +
      '<div class="s7-rung" id="r2" data-in="none" style="top:' + RUNG_Y[1] + 'px"><span class="no">2</span><div class="ic">' + ICO.pin + '</div>' +
        '<div><div class="tt">Out-of-window test</div><div class="ds">Scored on what happens after the score is frozen<br>new approval pairs · new transfer senders</div></div></div>' +
      '<div class="s7-rung" id="r3" data-in="none" style="top:' + RUNG_Y[2] + 'px"><span class="no">3</span><div class="ic">' + ICO.cross + '</div>' +
        '<div><div class="tt">Outcome in neither edge type</div><div class="ds">Liquidation of contract traders on GMX V2</div></div></div>' +
      '<p class="abs s7-strict" id="famhd" data-in="none" style="left:1250px;top:566px;color:var(--ink)">Three same-window proxy families</p>' +
      '<div class="s7-fam" data-in="none" style="top:606px"><div class="k c-xfer">Transfer family</div><div class="v">Transfer in-degree · in-value</div></div>' +
      '<div class="s7-fam" data-in="none" style="top:710px"><div class="k c-allow">Allowance family</div><div class="v">In-approve degree · in-approve value (cap U)</div></div>' +
      '<div class="s7-fam" data-in="none" style="top:814px"><div class="k">Sybil-stability family</div><div class="v">Counterparty ratio · tenure · active months</div>' +
        '<div class="gl">Sybil = fake addresses that inflate a reputation · this family looks for long, steady trading with many counterparties</div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var svg = q(el, '#lad');
      /* rails (left one is the "stricter" arrow) and rungs */
      g.railL = svgEl('path', { d: 'M54 728 L54 44', stroke: '#3A4458', 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }, svg);
      g.railR = svgEl('path', { d: 'M1046 728 L1046 44', stroke: '#3A4458', 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }, svg);
      g.head = svgEl('path', { d: 'M40 58 L54 30 L68 58', stroke: C.ink2, 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, svg);
      g.glow = svgEl('path', { d: 'M54 728 L54 728', stroke: C.ink, 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round', 'class': 'glow-white' }, svg);
      g.spark = svgEl('circle', { cx: 54, cy: 728, r: 8, fill: '#fff', 'class': 'glow-white' }, svg);
      gsap.set(g.spark, { autoAlpha: 0 });
      RUNG_Y.forEach(function (ry) {
        var cy = ry - 176 + 89;
        svgEl('line', { x1: 54, x2: 104, y1: cy, y2: cy, stroke: '#3A4458', 'stroke-width': 4, 'stroke-linecap': 'round' }, svg);
        svgEl('line', { x1: 1004, x2: 1046, y1: cy, y2: cy, stroke: '#3A4458', 'stroke-width': 4, 'stroke-linecap': 'round' }, svg);
      });
      g.rungs = ['#r1', '#r2', '#r3'].map(function (s) { return q(el, s); });
      g.icons = g.rungs.map(function (r) { return r.querySelector('.ic svg'); });
      gsap.set(g.rungs, { opacity: 0.3 });
      gsap.set(g.icons, { autoAlpha: 0 });
      g.fams = Array.prototype.slice.call(el.querySelectorAll('.s7-fam'));
      g.famhd = q(el, '#famhd');
      gsap.set(g.fams.concat([g.famhd]), { autoAlpha: 0 });
      /* bracket from rung 1 to the family cards */
      g.br = svgEl('path', { d: 'M1046 601 C1090 601 1100 573 1146 573 M1166 432 Q1150 432 1150 448 L1150 557 Q1150 573 1140 573 Q1150 573 1150 589 L1150 698 Q1150 714 1166 714', stroke: C.ink3, 'stroke-width': 2, fill: 'none' }, svg);
      gsap.set(g.br, { autoAlpha: 0 });
      g.vword = q(el, '#vword');
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo([g.railL, g.railR], { strokeDasharray: '700 700', strokeDashoffset: 700 }, { strokeDashoffset: 0, duration: 0.9, ease: E.io, stagger: 0.08 }, 0.1);
      tl.fromTo(g.head, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: E.out }, 0.8);
      tl.fromTo(g.rungs, { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.55, ease: E.out, stagger: 0.12 }, 0.3);
      tl.fromTo(q(el, '#strict'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.9);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i >= 1 && i <= 3) {
        var k = i - 1, R = g.rungs[k], yTo = RUNG_Y[k] - 176 + 89;
        /* the light climbs the rail to this rung */
        var yFrom = k === 0 ? 728 : RUNG_Y[k - 1] - 176 + 89;
        tl.set(g.spark, { autoAlpha: 1, attr: { cy: yFrom } }, 0);
        tl.to(g.spark, { attr: { cy: yTo }, duration: 0.55, ease: E.io }, 0);
        tl.to(g.glow, { attr: { d: 'M54 728 L54 ' + yTo }, duration: 0.55, ease: E.io }, 0);
        tl.to(g.spark, { autoAlpha: 0, duration: 0.3 }, 0.6);
        tl.to(R, { opacity: 1, borderColor: '#A3ADBF', duration: 0.45, ease: E.out }, 0.45);
        tl.fromTo(R, { boxShadow: '0 0 0 rgba(233,237,245,0)' }, { boxShadow: '0 0 34px rgba(233,237,245,.16)', duration: 0.5 }, 0.45);
        tl.fromTo(g.icons[k], { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: E.stamp }, 0.6);
        if (k > 0) tl.to(g.rungs[k - 1], { boxShadow: '0 0 0 rgba(233,237,245,0)', duration: 0.4 }, 0.45);
        if (k === 0) {
          tl.add(Comp.strike(ctx, g.vword, 'intended-construct check <small>· part of the fit is built in</small>' +
            '<small class="gl">construct = what the score sets out to measure · does it really measure that?</small>'), 1.3);
        }
      }
      if (i === 4) {
        tl.fromTo(g.br, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0);
        tl.fromTo(g.famhd, { autoAlpha: 0, x: -16 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: E.out }, 0.1);
        tl.fromTo(g.fams, { autoAlpha: 0, x: -30 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: E.out, stagger: 0.12 }, 0.2);
        tl.to(g.rungs[0], { boxShadow: '0 0 34px rgba(233,237,245,.16)', duration: 0.4 }, 0);
        tl.to(g.rungs.slice(1), { opacity: 0.55, boxShadow: '0 0 0 rgba(233,237,245,0)', duration: 0.4 }, 0);
      }
    }
  };

  /* ================================================================ s07-02 / s07-03 shared pieces
     Five contract cards (example) and the handshake pentagon of their 10 pairs. */
  var KC = [{ id: 'A', s: 5, l: 3 }, { id: 'B', s: 4, l: 4 }, { id: 'C', s: 3, l: 1 }, { id: 'D', s: 2, l: 1 }, { id: 'E', s: 1, l: 0 }];
  var PAIRS10 = [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]];
  function verdict(a, b) { var v = Math.sign(KC[a].s - KC[b].s) * Math.sign(KC[a].l - KC[b].l); return v > 0 ? 'c' : v < 0 ? 'd' : 't'; }
  var CARDS = { x: 96, y: 186, w: 920, h: 292 }, PENT = { x: 96, y: 548, w: 440, h: 400, cx: 220, cy: 196, r: 150 };
  var UNIT = 30;
  function buildCards(ctx, host) {
    var out = { cards: [], sb: [], lb: [], sv: [], lv: [] };
    KC.forEach(function (k, i) {
      var c = h('div', 's7-card', host);
      c.style.left = (i * 190) + 'px';
      h('div', 'nm', c, k.id);
      var svg = svgEl('svg', { width: 160, height: 220, viewBox: '0 0 160 220' }, c);
      svgEl('line', { x1: 18, x2: 142, y1: 184, y2: 184, stroke: C.line, 'stroke-width': 2 }, svg);
      var sb = svgEl('rect', { x: 34, y: 184 - k.s * UNIT, width: 38, height: k.s * UNIT, rx: 4, fill: C.allow }, svg);
      var lb = svgEl('rect', { x: 90, y: 184 - k.l * UNIT, width: 38, height: Math.max(0.001, k.l * UNIT), rx: 4, fill: C.ink }, svg);
      var sv = svgEl('text', { x: 53, y: 212, 'text-anchor': 'middle', fill: C.allow, 'font-size': 24, 'font-weight': 700, 'class': 'tnum' }, svg); sv.textContent = k.s;
      var lv = svgEl('text', { x: 109, y: 212, 'text-anchor': 'middle', fill: C.ink, 'font-size': 24, 'font-weight': 700, 'class': 'tnum' }, svg); lv.textContent = k.l;
      out.cards.push(c); out.sb.push(sb); out.lb.push(lb); out.sv.push(sv); out.lv.push(lv);
    });
    return out;
  }
  function pentPos(i) { var a = -Math.PI / 2 + i * 2 * Math.PI / 5; return [PENT.cx + Math.cos(a) * PENT.r, PENT.cy + Math.sin(a) * PENT.r]; }
  function buildPent(ctx, svg) {
    var P = { lines: [], nodes: [] };
    var lay = svgEl('g', {}, svg);
    PAIRS10.forEach(function (p) {
      var a = pentPos(p[0]), b = pentPos(p[1]);
      P.lines.push(svgEl('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: C.ink3, 'stroke-width': 2, 'stroke-linecap': 'round', opacity: 0.7 }, lay));
    });
    KC.forEach(function (k, i) {
      var p = pentPos(i), gN = svgEl('g', { transform: 'translate(' + p[0] + ',' + p[1] + ')' }, svg);
      svgEl('circle', { r: 25, fill: C.bg2, stroke: C.ink2, 'stroke-width': 2 }, gN);
      var t = svgEl('text', { y: 1, 'text-anchor': 'middle', 'dominant-baseline': 'middle', fill: C.ink, 'font-size': 24, 'font-weight': 800 }, gN); t.textContent = k.id;
      P.nodes.push(gN);
    });
    return P;
  }
  function lineStyle(v) {
    if (v === 'c') return { attr: { stroke: C.ink, 'stroke-width': 2.6, opacity: 1 }, dash: 'none' };
    if (v === 'd') return { attr: { stroke: C.hi, 'stroke-width': 3.4, opacity: 1 }, dash: 'none' };
    return { attr: { stroke: C.ink3, 'stroke-width': 2.2, opacity: 1 }, dash: '6 7' };
  }
  function applyLine(l, st) { for (var a in st.attr) l.setAttribute(a, st.attr[a]); l.style.strokeDasharray = st.dash; l.style.strokeDashoffset = '0'; }
  /* −1 … +1 ruler with markers */
  function buildRuler(ctx, host) {
    var W = 720, x0 = 30, x1 = 690, y = 46;
    var svg = svgEl('svg', { width: W, height: 120, 'class': 's7-ruler', style: 'overflow:visible' }, host);
    function x(v) { return x0 + (v + 1) / 2 * (x1 - x0); }
    svgEl('line', { x1: x0, x2: x1, y1: y, y2: y, stroke: C.ink2, 'stroke-width': 2 }, svg);
    [[-1, '−1', 'opposite order'], [-0.5, '', ''], [0, '0', 'no relation'], [0.5, '', ''], [1, '+1', 'same order']].forEach(function (t) {
      svgEl('line', { x1: x(t[0]), x2: x(t[0]), y1: y - (t[1] ? 10 : 6), y2: y + (t[1] ? 10 : 6), stroke: C.ink2, 'stroke-width': 2 }, svg);
      if (t[1]) {
        var a = svgEl('text', { x: x(t[0]), y: y + 36, 'text-anchor': 'middle', fill: C.ink, 'font-size': 20, 'font-weight': 700, 'class': 'tnum' }, svg); a.textContent = t[1];
        var b = svgEl('text', { x: x(t[0]), y: y + 60, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 18 }, svg); b.textContent = t[2];
      }
    });
    function marker(col, above) {
      var g = svgEl('g', {}, svg);
      svgEl('path', { d: above ? 'M-9,-22 L9,-22 L0,-6 Z' : 'M-9,22 L9,22 L0,6 Z', fill: col }, g);
      var t = svgEl('text', { x: 0, y: above ? -30 : 44, 'text-anchor': 'middle', fill: col, 'font-size': 22, 'font-weight': 800, 'class': 'tnum' }, g);
      gsap.set(g, { autoAlpha: 0 });
      var M = { g: g, t: t, v: 0 };
      M.place = function (v) { M.v = v; g.setAttribute('transform', 'translate(' + x(v).toFixed(2) + ',' + y + ')'); };
      M.slide = function (v, text, o) {
        o = o || {};
        var st = { v: M.v };
        var tl = gsap.timeline({ delay: o.delay || 0 });
        tl.set(g, { autoAlpha: 1 });
        tl.call(function () { t.textContent = text; });
        tl.to(st, { v: v, duration: ctx.reduced ? 0.01 : (o.duration || 1.0), ease: 'power3.out', onUpdate: function () { M.place(st.v); }, onComplete: function () { M.place(v); } });
        return tl;
      };
      M.place(0);
      return M;
    }
    return { svg: svg, x: x, marker: marker };
  }

  /* ================================================================ s07-02 Kendall's τ */
  var slide2 = {
    id: 's07-02', title: 'Kendall’s τ: count the pairs', time: 50, steps: 4,
    tags: ['example'],
    notes: [
      'How well a score agrees with later outcomes is measured with Kendall’s tau. Let me build a small example with five contracts. The amber bars are the scores, and the white bars are the outcome labels we score them against later.',
      'First, let’s count the pairs. Think of the contracts as people who each shake hands once with everyone else. A shakes hands with the 4 others. All five shake 4 hands each, so 5 times 4 is 20. But A shaking hands with B and B shaking hands with A is the same handshake, so we counted every handshake twice. Dividing by 2 gives 10. As a formula: n times n minus 1, divided by 2.',
      'Now look at each pair. If the contract with the higher score also has the higher label, the pair is concordant; if it is the other way round, it is discordant. For A and B, A has the higher score but B has the higher label, so they are discordant. A with C, A with D and A with E are concordant. Counting the rest, there are eight concordant pairs and one discordant pair. C and D have the same label, so they count as neither.',
      'Take the concordant pairs minus the discordant pairs and divide by all the pairs: that gives 0.7. We write this as tau a. It is the basic tau, which does not treat ties separately. 1 means the order is exactly the same, 0 means no relation, and −1 means exactly the opposite.',
      'When there are no ties, 1 plus tau, divided by 2, is the probability that a randomly chosen pair is in the same order in both rankings. In the actual matched cohort there are more than 110 million contract pairs.'
    ],
    html:
      '<h1 class="t-h1">How closely do two rankings keep the [[same order]]?</h1>' +
      '<div class="abs" id="cards" data-shared="s7-cards" data-in="none" style="left:' + CARDS.x + 'px;top:' + CARDS.y + 'px;width:' + CARDS.w + 'px;height:' + CARDS.h + 'px"></div>' +
      '<div class="abs s7-legend" id="leg" data-in="none" style="left:96px;top:490px"><span><i style="background:var(--c-allow)"></i>Score</span><span><i style="background:var(--ink)"></i>Later outcome label</span><span class="ink-3" style="font-size:18px">five contracts · example</span></div>' +
      '<svg class="abs" id="pent" data-shared="s7-pent" data-in="none" width="' + PENT.w + '" height="' + PENT.h + '" style="left:' + PENT.x + 'px;top:' + PENT.y + 'px;overflow:visible"></svg>' +
      '<div class="abs s7-hs" id="hs" data-in="none" style="left:580px;top:600px;width:436px"><div class="a" id="hsa"></div><div class="b" id="hsb"></div></div>' +
      '<div class="abs s7-cmp" id="cmp" data-in="none" style="left:580px;top:568px;width:436px">' +
        '<div class="pr" id="cp">A – B</div>' +
        '<div class="row"><span class="k">score</span><span class="v c-allow" id="cs">5 &gt; 4</span></div>' +
        '<div class="row"><span class="k">label</span><span class="v" id="cl">3 &lt; 4</span></div>' +
        '<div class="vd" id="cv">Discordant pair ✕</div></div>' +
      '<div class="abs s7-tiles" id="tiles" style="left:1084px;top:186px;width:740px">' +
        '<div class="s7-tile"><div class="sy">$n_0$</div><div class="ct" id="t0">0</div><div class="ds">all pairs</div></div>' +
        '<div class="s7-tile"><div class="sy">$n_c$</div><div class="ct" id="tc">0</div><div class="ds">concordant ✓</div></div>' +
        '<div class="s7-tile"><div class="sy">$\\ch{n_d}$</div><div class="ct c-hi" id="td">0</div><div class="ds">discordant ✕</div></div>' +
        '<div class="s7-tile"><div class="sy ink-3">=</div><div class="ct ink-3" id="tt">0</div><div class="ds">tie · not counted</div></div></div>' +
      '<div class="abs s7-d" id="d2" data-in="none" style="left:1084px;top:316px;width:740px"></div>' +
      '<div class="abs" id="rul" data-in="none" style="left:1094px;top:708px;width:720px;height:120px"></div>' +
      '<div class="abs s7-note" data-step="4" style="left:1084px;top:862px;width:740px">' +
        '<div>Aside: without ties, $\\tfrac{1+\\tau}{2}$ = the chance that a random pair is in the same order in both rankings</div>' +
        '<div style="margin-top:6px">The real matched cohort has <b>' + fmt(PAIRS, 0) + '</b> pairs</div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.cardsEl = q(el, '#cards'); g.pentEl = q(el, '#pent');
      g.K = buildCards(ctx, g.cardsEl);
      g.P = buildPent(ctx, g.pentEl);
      gsap.set(g.K.cards, { autoAlpha: 0 });
      gsap.set(g.P.nodes, { autoAlpha: 0 });
      g.P.lines.forEach(function (l) { var L = Math.hypot(l.x2.baseVal.value - l.x1.baseVal.value, l.y2.baseVal.value - l.y1.baseVal.value); l.__L = L; gsap.set(l, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }); });
      g.leg = q(el, '#leg'); gsap.set(g.leg, { autoAlpha: 0 });
      g.cmp = q(el, '#cmp'); gsap.set(g.cmp, { autoAlpha: 0 });
      g.cp = q(el, '#cp'); g.cs = q(el, '#cs'); g.cl = q(el, '#cl'); g.cv = q(el, '#cv');
      g.ck = Array.prototype.slice.call(el.querySelectorAll('#cmp .row .k'));
      g.hs = q(el, '#hs'); g.hsa = q(el, '#hsa'); g.hsb = q(el, '#hsb'); gsap.set(g.hs, { autoAlpha: 0 });
      g.nodeC = g.P.nodes.map(function (n) { return n.querySelector('circle'); });
      g.t0 = q(el, '#t0'); g.tc = q(el, '#tc'); g.td = q(el, '#td'); g.tt = q(el, '#tt');
      g.D = Comp.derive(ctx, q(el, '#d2'), { head: 'Derivation', lines: [
        { tex: 'n_0=\\frac{n(n-1)}{2}=\\frac{5\\times4}{2}=10', note: '5 people × 4 handshakes = 20 · each one counted twice, so ÷ 2' },
        { tex: 'n_c=8,\\qquad \\ch{n_d}=1', note: 'C and D have the same label (a tie) → counted as neither' },
        { tex: '\\tau_a=\\frac{\\part{num}{n_c-n_d}}{n_0}=\\frac{8-1}{10}=0.7', note: '(concordant − discordant) ÷ all pairs · $\\tau_a$ = the basic τ, with no special handling of ties', mark: 'num' }
      ] });
      gsap.set(g.D.el, { autoAlpha: 0 });
      g.R = buildRuler(ctx, q(el, '#rul'));
      g.m = g.R.marker(C.ink, true);
      gsap.set(q(el, '#rul'), { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      /* cards and pentagon are shared with s07-03: the containers stay, their pieces come in at step 1 */
      void g;
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(g.K.cards, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out, stagger: 0.1 }, 0);
        tl.fromTo(g.K.sb.concat(g.K.lb), { scaleY: 0, transformOrigin: '50% 100%' }, { scaleY: 1, duration: 0.6, ease: E.out, stagger: 0.05 }, 0.35);
        tl.fromTo(g.leg, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.9);
        tl.fromTo(g.P.nodes, { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp, stagger: 0.08 }, 1.0);
        /* handshakes: every card shakes hands with the 4 others (5 × 4 = 20), but each line was
           counted from both ends, so the number of pairs is 20 ÷ 2 = 10 */
        var drawn = {}, T1 = 1.5, hsSet = function (a, b) { tl.call(function () { g.hsa.innerHTML = a; g.hsb.innerHTML = b; }, null, T1); };
        tl.fromTo(g.hs, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: E.out }, T1);
        [0, 1, 2, 3, 4].forEach(function (i, step) {
          var mine = [];
          PAIRS10.forEach(function (p, k) { if (p[0] === i || p[1] === i) mine.push(k); });
          var dt = step === 0 ? 1.15 : 0.55;
          hsSet(KC[i].id + ' shakes hands with 4' + (step === 0 ? ' others' : ' too'), (step === 0 ? '4' : (step + 1) + ' × 4 = ' + (4 * (step + 1))) + (step === 0 ? '<small>handshakes</small>' : ''));
          tl.to(g.nodeC[i], { attr: { stroke: C.allow, 'stroke-width': 4 }, duration: 0.15 }, T1);
          mine.forEach(function (k, m) {
            var l = g.P.lines[k];
            if (!drawn[k]) { drawn[k] = true; tl.to(l, { strokeDashoffset: 0, duration: step === 0 ? 0.3 : 0.18, ease: 'power2.out' }, T1 + m * (step === 0 ? 0.18 : 0.06)); }
            tl.to(l, { attr: { stroke: C.allow, opacity: 1 }, duration: 0.12 }, T1 + m * (step === 0 ? 0.18 : 0.06) + 0.05);
          });
          tl.fromTo(g.hsb, { scale: 1.25, transformOrigin: '0% 60%' }, { scale: 1, duration: 0.3, ease: E.stamp, immediateRender: false }, T1 + 0.05);
          T1 += dt;
          tl.to(g.nodeC[i], { attr: { stroke: C.ink2, 'stroke-width': 2 }, duration: 0.2 }, T1 - 0.2);
          tl.to(mine.map(function (k) { return g.P.lines[k]; }), { attr: { stroke: C.ink3, opacity: 0.7 }, duration: 0.2 }, T1 - 0.2);
        });
        /* every line was counted twice: flash each line twice, count the distinct pairs */
        T1 += 0.2;
        hsSet('A–B and B–A: one handshake', '20 ÷ 2 = 10<small>pairs</small>');
        tl.fromTo(g.hsb, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, immediateRender: false }, T1);
        g.P.lines.forEach(function (l, k) {
          var t = T1 + 0.25 + k * 0.14;
          tl.to(l, { attr: { stroke: C.ink, 'stroke-width': 4, opacity: 1 }, duration: 0.07, yoyo: true, repeat: 3 }, t);
          tl.call(function (n) { g.t0.textContent = String(n); }, [k + 1], t + 0.1);
        });
        T1 += 0.25 + 10 * 0.14 + 0.2;
        tl.fromTo(g.t0, { scale: 1.3, transformOrigin: '0% 70%' }, { scale: 1, duration: 0.35, ease: E.stamp, immediateRender: false }, T1);
        tl.fromTo(g.D.el, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, T1 - 0.2);
        tl.add(g.D.show(1), T1 + 0.1);
      }
      if (i === 2) {
        var t = 0.1, nc = 0, nd = 0, nt = 0;
        tl.to(g.hs, { autoAlpha: 0, y: -10, duration: 0.25, ease: E['in'] }, 0);
        tl.fromTo(g.cmp, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: E.out }, 0.15);
        PAIRS10.forEach(function (p, k) {
          var slow = k < 4, d = slow ? 1.15 : 0.36, v = verdict(p[0], p[1]);
          var A = KC[p[0]], Bk = KC[p[1]];
          var cards = [g.K.cards[p[0]], g.K.cards[p[1]]];
          tl.to(cards, { y: -16, borderColor: '#A3ADBF', duration: slow ? 0.22 : 0.1, ease: E.out }, t);
          tl.call(function () {
            g.cp.textContent = A.id + ' – ' + Bk.id;
            g.cs.innerHTML = A.s + (A.s > Bk.s ? ' &gt; ' : A.s < Bk.s ? ' &lt; ' : ' = ') + Bk.s;
            g.cl.innerHTML = A.l + (A.l > Bk.l ? ' &gt; ' : A.l < Bk.l ? ' &lt; ' : ' = ') + Bk.l;
            g.cv.innerHTML = v === 'c' ? 'Concordant pair ✓' : v === 'd' ? 'Discordant pair ✕' : 'Tie = not counted';
            g.cv.style.color = v === 'c' ? C.ink : v === 'd' ? C.hi : C.ink3;
          }, null, t + 0.02);
          if (slow) tl.fromTo([g.cs, g.cl, g.cv], { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.25, stagger: 0.12 }, t + 0.05);
          var L = g.P.lines[k];
          var lsv = lineStyle(v);
          tl.to(L, { attr: lsv.attr, duration: slow ? 0.3 : 0.12 }, t + (slow ? 0.55 : 0.12));
          tl.set(L, { strokeDasharray: lsv.dash, strokeDashoffset: 0 }, t + (slow ? 0.55 : 0.12));
          if (v === 'c') nc++; else if (v === 'd') nd++; else nt++;
          tl.call(function (a, b, c) { g.tc.textContent = a; g.td.textContent = b; g.tt.textContent = c; }, [nc, nd, nt], t + (slow ? 0.6 : 0.14));
          tl.to(cards, { y: 0, borderColor: '#232B3B', duration: slow ? 0.2 : 0.08 }, t + d - (slow ? 0.22 : 0.1));
          t += d;
        });
        tl.call(function () {
          g.cp.textContent = 'All 10 pairs';
          g.ck[0].textContent = '✓'; g.ck[1].textContent = '✕'; g.ck[1].style.color = C.hi;
          g.cs.innerHTML = 'concordant 8'; g.cs.style.color = C.ink; g.cl.innerHTML = '<span class="c-hi">discordant 1</span>';
          g.cv.innerHTML = '= 1 tie · not counted'; g.cv.style.color = C.ink3;
        }, null, t + 0.2);
        tl.add(g.D.show(2), t + 0.3);
      }
      if (i === 3) {
        tl.add(g.D.show(3), 0);
        tl.fromTo(q(el, '#rul'), { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 0.4);
        tl.add(g.m.slide(0.7, '0.7', { duration: 1.1 }), 0.8);
      }
    }
  };

  /* ================================================================ s07-03 τ_b (and Spearman's ρ) */
  var MID = { x: 580, y: 540, w: 436, h: 420 };
  var slide3 = {
    id: 's07-03', title: 'With ties: τ_b (and Spearman’s ρ)', time: 45, steps: 4,
    tags: ['example'],
    notes: [
      'But a pair with the same label, a tie, is neither right nor wrong. When there are many ties, the formula we just used cannot reach 1, however well the score predicts.',
      'Let’s count the tied pairs first. A tie group of size 2 gives 1 pair, and a group of size 3 gives 3 pairs. So for a group of size t we take t times t minus 1, divided by 2. In this example the scores have no ties, so n1 is 0, and the labels have one group, C and D, so n2 is 1.',
      'So the score ranking puts 10 pairs in order, and the label ranking puts 9 pairs in order. Instead of picking one of the two numbers, we use the side of the square with the same area as a rectangle 10 wide and 9 high. This is called the geometric mean: the square root of 90, about 9.487.',
      'So τ_b is 7 divided by 9.487, which is 0.738. Without ties, n1 and n2 are 0, so τ_b equals the τ_a from before. Every tau in this thesis is τ_b. The correction matters because plain counts and later labels are integers, and many contracts have zero, so there are a great many ties.',
      'We also report Spearman’s rho. Put the ranks from the two rankings side by side: the smaller the rank differences, the closer the value is to 1. In this example it is 0.872. C and D have the same label, so they share rank 2.5, halfway between 2nd and 3rd. It mostly tells the same story as tau. (Advanced) Without ties, the formula is rho = 1 − 6 times the sum of the squared differences, divided by n times n squared minus 1. The 6 is a constant of the formula, and I skip its derivation. In this example the sum of the squared differences is 2.5, so the formula gives 0.875. But there are ties, so the thesis computes the correlation of the mid-ranks, and that value is 0.872.'
    ],
    html:
      '<h1 class="t-h1">A [[tie]] is neither right nor wrong</h1>' +
      '<div class="abs" id="cards" data-shared="s7-cards" data-in="none" style="left:' + CARDS.x + 'px;top:' + CARDS.y + 'px;width:' + CARDS.w + 'px;height:' + CARDS.h + 'px"></div>' +
      '<div class="abs s7-legend" style="left:96px;top:490px"><span><i style="background:var(--c-allow)"></i>Score</span><span><i style="background:var(--ink)"></i>Later outcome label</span><span class="ink-3" style="font-size:18px">five contracts · example</span></div>' +
      '<svg class="abs" id="pent" data-shared="s7-pent" data-in="none" width="' + PENT.w + '" height="' + PENT.h + '" style="left:' + PENT.x + 'px;top:' + PENT.y + 'px;overflow:visible"></svg>' +
      '<svg class="abs" id="mid" data-in="none" width="' + MID.w + '" height="' + MID.h + '" style="left:' + MID.x + 'px;top:' + MID.y + 'px;overflow:visible"></svg>' +
      '<div class="abs" id="midtx" data-in="none" style="left:' + MID.x + 'px;top:' + (MID.y + 250) + 'px;width:' + MID.w + 'px;text-align:center;font-size:24px;line-height:34px;color:var(--ink-2)">A group of size $t$ has $\\dfrac{t(t-1)}{2}$ pairs</div>' +
      '<p class="abs" style="left:1084px;top:180px;width:740px;font-size:26px;line-height:38px">So the divisor keeps only the truly ordered pairs</p>' +
      '<div class="abs s7-tiles" id="tiles" style="left:1084px;top:236px;width:740px">' +
        '<div class="s7-tile"><div class="sy">$n_1$</div><div class="ct" id="t1">0</div><div class="ds">tied pairs in scores</div></div>' +
        '<div class="s7-tile"><div class="sy">$n_2$</div><div class="ct" id="t2">0</div><div class="ds">tied pairs in labels</div></div>' +
        '<div class="s7-tile"><div class="sy">$t_k$</div><div class="ct" style="font-size:30px;line-height:50px">2</div><div class="ds">tie-group size (C·D)</div></div></div>' +
      '<div class="abs s7-d" id="d3" data-in="none" style="left:1084px;top:356px;width:740px"></div>' +
      '<div class="abs" id="rul" data-in="none" style="left:1094px;top:826px;width:720px;height:120px"></div>' +
      '<p class="abs s7-note" data-step="3" style="left:96px;top:956px;width:1728px;color:var(--ink)">Every τ in this thesis is τ<sub>b</sub> · raw degrees and labels have many ties: they are integers, and many contracts have zero</p>' +
      '<div class="abs s7-sp" id="sp" data-in="none" style="left:96px;top:548px;width:920px">' +
        '<div class="hd">Aside · Spearman’s ρ<small>reported alongside τ</small></div>' +
        '<div style="display:flex;gap:40px;align-items:center">' +
        '<table><tr><th></th><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr>' +
        '<tr><td class="l">score rank</td><td>5</td><td>4</td><td>3</td><td>2</td><td>1</td></tr>' +
        '<tr><td class="l">label rank</td><td>4</td><td>5</td><td>2.5</td><td>2.5</td><td>1</td></tr>' +
        '<tr><td class="l">rank difference</td><td>1</td><td>−1</td><td>0.5</td><td>−0.5</td><td>0</td></tr></table>' +
        '<div class="rs">The smaller the rank<br>differences, the closer ρ is to 1<div class="big">Here: ρ ≈ 0.872</div></div></div>' +
        '<div class="nt" style="margin-top:12px">C and D have the same label, so both get rank 2.5, halfway between 2nd and 3rd</div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.cardsEl = q(el, '#cards'); g.pentEl = q(el, '#pent');
      g.K = buildCards(ctx, g.cardsEl);
      g.P = buildPent(ctx, g.pentEl);
      PAIRS10.forEach(function (p, k) { applyLine(g.P.lines[k], lineStyle(verdict(p[0], p[1]))); });
      g.cd = g.P.lines[7];   /* C–D, the tie */
      /* tie groups */
      var mid = q(el, '#mid');
      g.tie = svgEl('g', {}, mid);
      var gp = [[[70, 110], [170, 110]], [[300, 60], [250, 150], [350, 150]]];
      svgEl('line', { x1: 70, y1: 110, x2: 170, y2: 110, stroke: C.ink2, 'stroke-width': 2.5, 'stroke-dasharray': '6 7' }, g.tie);
      [[0, 1], [1, 2], [0, 2]].forEach(function (e) { svgEl('line', { x1: gp[1][e[0]][0], y1: gp[1][e[0]][1], x2: gp[1][e[1]][0], y2: gp[1][e[1]][1], stroke: C.ink2, 'stroke-width': 2.5, 'stroke-dasharray': '6 7' }, g.tie); });
      gp[0].concat(gp[1]).forEach(function (p) { svgEl('circle', { cx: p[0], cy: p[1], r: 13, fill: C.bg3, stroke: C.ink, 'stroke-width': 2 }, g.tie); });
      var t1 = svgEl('text', { x: 120, y: 200, 'text-anchor': 'middle', fill: C.ink, 'font-size': 22, 'font-weight': 600 }, g.tie); t1.textContent = 'size 2 → 1 pair';
      var t2 = svgEl('text', { x: 300, y: 200, 'text-anchor': 'middle', fill: C.ink, 'font-size': 22, 'font-weight': 600 }, g.tie); t2.textContent = 'size 3 → 3 pairs';
      g.midtx = q(el, '#midtx');
      gsap.set([g.tie, g.midtx], { autoAlpha: 0 });
      /* denominator: two bars 10 and 9 → rectangle 10 × 9 → square of the same area */
      var U = 26, base = 330, X0 = 150;
      g.den = svgEl('g', {}, mid);
      g.rect = svgEl('rect', { x: X0, y: base - 9 * U, width: 10 * U, height: 9 * U, fill: 'rgba(233,237,245,.08)', stroke: 'none' }, g.den);
      g.grid = svgEl('g', { opacity: 0.5 }, g.den);
      for (var gx = 1; gx < 10; gx++) svgEl('line', { x1: X0 + gx * U, x2: X0 + gx * U, y1: base - 9 * U, y2: base, stroke: 'rgba(233,237,245,.12)', 'stroke-width': 1 }, g.grid);
      for (var gy = 1; gy < 9; gy++) svgEl('line', { x1: X0, x2: X0 + 10 * U, y1: base - gy * U, y2: base - gy * U, stroke: 'rgba(233,237,245,.12)', 'stroke-width': 1 }, g.grid);
      g.barA = svgEl('rect', { x: 20, y: base - 10 * U, width: 28, height: 10 * U, rx: 4, fill: C.ink }, g.den);
      g.barB = svgEl('rect', { x: 72, y: base - 9 * U, width: 28, height: 9 * U, rx: 4, fill: C.ink2 }, g.den);
      g.lA = svgEl('text', { x: 34, y: base + 30, 'text-anchor': 'middle', fill: C.ink, 'font-size': 22, 'font-weight': 700, 'class': 'tnum' }, g.den); g.lA.textContent = '10';
      g.lB = svgEl('text', { x: 86, y: base + 30, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 22, 'font-weight': 700, 'class': 'tnum' }, g.den); g.lB.textContent = '9';
      g.area = svgEl('text', { x: X0 + 5 * U, y: base - 4.5 * U, 'text-anchor': 'middle', 'dominant-baseline': 'middle', fill: C.ink, 'font-size': 26, 'font-weight': 700, 'class': 'tnum' }, g.den); g.area.textContent = 'area 10 × 9 = 90';
      g.side = svgEl('line', { x1: X0, x2: X0 + Math.sqrt(90) * U, y1: base - Math.sqrt(90) * U, y2: base - Math.sqrt(90) * U, stroke: C.hi, 'stroke-width': 5, 'stroke-linecap': 'round' }, g.den);
      g.sideL = svgEl('text', { x: X0 + Math.sqrt(90) * U / 2, y: base - Math.sqrt(90) * U - 16, 'text-anchor': 'middle', fill: C.hi, 'font-size': 24, 'font-weight': 800, 'class': 'tnum' }, g.den); g.sideL.textContent = 'side = √90 ≈ 9.487';
      g.denCap = svgEl('text', { x: MID.w / 2, y: base + 66, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 21 }, g.den); g.denCap.textContent = 'geometric mean of 10 and 9';
      gsap.set([g.den, g.rect, g.grid, g.area, g.side, g.sideL, g.denCap], { autoAlpha: 0 });
      g.U = U; g.base = base; g.X0 = X0;
      /* counters, derivation, ruler, Spearman side panel */
      g.t1 = q(el, '#t1'); g.t2 = q(el, '#t2');
      g.D = Comp.derive(ctx, q(el, '#d3'), { head: 'Derivation', lines: [
        { tex: 'n_1=\\sum_k\\frac{t_k(t_k-1)}{2}=0,\\qquad n_2=\\frac{2\\times1}{2}=1', note: 'No ties in the scores · in the labels, C and D (one group of size 2)' },
        { tex: 'n_0-n_1=10,\\qquad n_0-n_2=9', note: 'the pairs that each ranking really puts in order' },
        { tex: '\\tau_b=\\frac{n_c-n_d}{\\part{den}{\\sqrt{(n_0-n_1)(n_0-n_2)}}}=\\frac{8-1}{\\sqrt{10\\times9}}=\\frac{7}{9.487}\\approx\\ch{0.738}', note: 'Thesis Eq. (2.6) · without ties $n_1=n_2=0$, so $\\tau_b=\\tau_a$', mark: 'den' }
      ] });
      Deck.renderMath(g.D.el);
      gsap.set(g.D.el, { autoAlpha: 0 });
      g.rul = q(el, '#rul'); gsap.set(g.rul, { autoAlpha: 0 });
      g.R = buildRuler(ctx, g.rul);
      g.ghost = g.R.marker(C.ink3, false); g.ghost.place(0.7); g.ghost.t.textContent = 'τa 0.7';
      g.m = g.R.marker(C.ink, true); g.m.place(0.7);
      g.sp = q(el, '#sp'); gsap.set(g.sp, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      settleShared(ctx, g.cardsEl, 's7-cards');
      settleShared(ctx, g.pentEl, 's7-pent');
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl(), U = g.U, base = g.base, X0 = g.X0, S = Math.sqrt(90) * U;
      if (i === 1) {
        /* the C–D tie line glows; tie groups and their pair counts */
        tl.to(g.cd, { attr: { stroke: C.ink, 'stroke-width': 5 }, duration: 0.3, yoyo: true, repeat: 1 }, 0);
        tl.fromTo([g.K.lv[2], g.K.lv[3]], { scale: 1 }, { scale: 1.5, transformOrigin: '50% 50%', duration: 0.25, yoyo: true, repeat: 1 }, 0);
        tl.call(function () { g.t2.textContent = '1'; }, null, 0.5);
        tl.fromTo(g.t2, { scale: 1.4, transformOrigin: '0% 70%' }, { scale: 1, duration: 0.35, ease: E.stamp, immediateRender: false }, 0.5);
        tl.fromTo(g.tie, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.4);
        tl.fromTo(g.midtx, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.8);
        tl.fromTo(g.D.el, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.6);
        tl.add(g.D.show(1), 0.9);
      }
      if (i === 2) {
        tl.to([g.tie, g.midtx], { autoAlpha: 0, y: -12, duration: 0.3, ease: E['in'] }, 0);
        tl.set(g.den, { autoAlpha: 1 }, 0.3);
        tl.fromTo([g.barA, g.barB], { scaleY: 0, transformOrigin: '50% 100%' }, { scaleY: 1, duration: 0.5, ease: E.out, stagger: 0.1 }, 0.3);
        tl.fromTo([g.lA, g.lB], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.6);
        tl.add(g.D.show(2), 0.4);
        /* the bars become two edges of a 10 × 9 rectangle */
        tl.to(g.barA, { attr: { x: X0, y: base, width: 10 * U, height: 6 }, duration: 0.8, ease: E.io }, 1.4);
        tl.to(g.barB, { attr: { x: X0 - 6, y: base - 9 * U, width: 6, height: 9 * U }, duration: 0.8, ease: E.io }, 1.5);
        tl.to(g.lA, { attr: { x: X0 + 5 * U, y: base + 32 }, duration: 0.8, ease: E.io }, 1.4);
        tl.to(g.lB, { attr: { x: X0 - 24, y: base - 4.5 * U + 8 }, duration: 0.8, ease: E.io }, 1.5);
        tl.fromTo([g.rect, g.grid], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 2.2);
        tl.fromTo(g.area, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 2.4);
        /* … and morph into the square of the same area */
        tl.to([g.grid, g.area, g.lA, g.lB], { autoAlpha: 0, duration: 0.3 }, 3.6);
        tl.to(g.rect, { attr: { width: S, height: S, y: base - S }, duration: 0.9, ease: E.io }, 3.7);
        tl.to(g.barA, { attr: { width: S }, duration: 0.9, ease: E.io }, 3.7);
        tl.to(g.barB, { attr: { height: S, y: base - S }, duration: 0.9, ease: E.io }, 3.7);
        tl.fromTo(g.side, { autoAlpha: 0, attr: { x2: X0 } }, { autoAlpha: 1, attr: { x2: X0 + S }, duration: 0.5, ease: E.out }, 4.6);
        tl.fromTo([g.sideL, g.denCap], { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.4, stagger: 0.15 }, 4.8);
      }
      if (i === 3) {
        tl.add(g.D.show(3), 0);
        tl.fromTo(g.rul, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 0.5);
        tl.fromTo(g.ghost.g, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.6);
        tl.add(g.m.slide(0.7379, 'τb 0.738', { duration: 0.9 }), 0.8);
      }
      if (i === 4) {
        /* the side panel takes the pentagon's place: the pentagon and the tie figure step out */
        tl.to([g.den, g.pentEl], { autoAlpha: 0, duration: 0.3 }, 0);
        tl.fromTo(g.sp, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out }, 0.1);
        tl.fromTo(g.sp.querySelectorAll('tr'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, stagger: 0.12 }, 0.4);
      }
    }
  };

  /* ================================================================ s07-04 bootstrap */
  var BAG = { cx: 330, cy: 572, r: 200 };
  var SLOT = { x: 640, y0: 392, dy: 120, n: 8, w: 40, gap: 12 };
  var HIST = { x: 1270, y: 300, w: 554, h: 400, lo: 0.572, hi: 0.598, base: 340 };
  function bootValues() {
    /* 400 illustrative resample values: seeded normal draws, mapped so that the numpy-style
       2.5th / 97.5th percentiles land exactly on the digest's interval ends */
    var rnd = Deck.util.rng(SEED), v = [];
    for (var i = 0; i < B; i++) { var u = 1 - rnd(), w = rnd(); v.push(Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * w)); }
    var s = v.slice().sort(function (a, b) { return a - b; });
    function pct(p) { var pos = p * (B - 1), i0 = Math.floor(pos), f = pos - i0; return s[i0] + (s[Math.min(B - 1, i0 + 1)] - s[i0]) * f; }
    var lo = nums(FAM_ER_A)[1], hi = nums(FAM_ER_A)[2], q0 = pct(0.025), q1 = pct(0.975);
    return v.map(function (x) { return lo + (x - q0) * (hi - lo) / (q1 - q0); });
  }
  var slide4 = {
    id: 's07-04', title: 'Bootstrap: resample 400 times', time: 45, steps: 4,
    tags: function (step) { return step >= 4 ? ['construct', 'example'] : ['example']; },
    notes: [
      'How far we can trust a number like 0.585 is measured with the bootstrap, that is, by resampling. All we have is one collection of 15,107 contracts. We would like to know how much tau would change if we collected the contracts again. We cannot do that, so we imitate it by drawing again from a bag. The bag on the left holds the 15,107 contracts of the matched cohort.',
      'I draw one contract from the bag, write it down and put it back. Doing this as many times as there are contracts gives a new sample of the same size as the original, but slightly different. Because each contract goes back in, the same contract can be drawn twice. For every new sample I compute tau again and stack it on the right, one by one. The shape of the bars on screen is an illustration.',
      'We do this 400 times. The draws are fixed by seed 42, so anyone who reruns it gets the same result.',
      'We sort those 400 values from smallest to largest and cut off the smallest 2.5% and the largest 2.5%. The middle range that remains is the 95% confidence interval. Out of 400, that is about the 10th and the 390th value. For EndorseRank and the allowance family, it runs from 0.578 to 0.592. The family’s tau is the mean of the taus of its two proxies, the in-approve degree and the in-approve value. 400 resamples are not many, so with another seed the interval ends could move a little. (Advanced) According to Chapter 3 of the thesis, that wobble is about 0.13 times the bootstrap standard error.',
      'If we press this middle band flat, it becomes the interval bar that appears in every result figure from now on. The dot is 0.585, and the bar is the 95% interval. And every score uses the same 400 samples. That is the key to the next slide.'
    ],
    html:
      '<h1 class="t-h1">[[Resample]] from the same bag, 400 times</h1>' +
      '<div class="abs s7-lines" style="left:96px;top:172px;width:1100px">' +
        '<p class="why"><b>Why?</b>How much would τ vary with other contracts? Resampling the bag imitates it</p>' +
        '<p class="l">Draw one of the n contracts and put it back, n times → one new sample</p>' +
        '<p class="l" data-step="2">Recompute τ on each new sample → <b>' + fmt(B, 0) + '</b> times (seed ' + SEED + ')</p></div>' +
      '<div class="abs" id="bag" data-in="none" style="left:' + (BAG.cx - BAG.r - 10) + 'px;top:' + (BAG.cy - BAG.r - 10) + 'px;width:' + (2 * BAG.r + 20) + 'px;height:' + (2 * BAG.r + 20) + 'px"></div>' +
      '<p class="abs s7-note" id="baglbl" style="left:' + (BAG.cx - 220) + 'px;top:' + (BAG.cy + BAG.r + 18) + 'px;width:440px;text-align:center">Bag = <b>' + fmt(NCOH, 0) + '</b> matched-cohort contracts</p>' +
      '<svg class="abs" id="ov" data-in="none" width="1160" height="900" style="left:0;top:0;overflow:visible;pointer-events:none"></svg>' +
      '<div class="abs s7-cnt" id="cnt" data-in="none" style="left:' + HIST.x + 'px;top:' + (HIST.y - 70) + 'px">Sample <b id="cn">0</b>/ ' + fmt(B, 0) + ' · stacking τ values</div>' +
      '<svg class="abs" id="hist" data-in="none" width="' + HIST.w + '" height="' + HIST.h + '" style="left:' + HIST.x + 'px;top:' + HIST.y + 'px;overflow:visible"></svg>' +
      '<div class="abs s7-res" id="res" data-in="none" style="left:' + HIST.x + 'px;top:' + (HIST.y + HIST.base + 190) + 'px;width:' + HIST.w + 'px"><span>EndorseRank × allowance family · 95% interval</span><b>' + FAM_ER_A + '</b><small>family τ = mean τ of its 2 proxies (in-approve degree · in-approve value)</small></div>' +
      '<div class="abs s7-foot" id="foot" data-in="none" style="left:96px;top:868px;width:1040px">' +
        '<div>95% interval = about the 10th to the 390th of the ' + fmt(B, 0) + ' resampled τ values, sorted</div>' +
        '<small>With only ' + fmt(B, 0) + ' resamples, another seed can move the interval ends slightly in the third decimal</small></div>' +
      '<p class="abs s7-note" data-step="4" style="left:96px;top:966px;width:1060px;color:var(--ink)">Every score uses the same 400 samples → the ‘paired difference’ on the next slide</p>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* the bag: 15,107 dots in a disc (illustrative positions) */
      var bagHost = q(el, '#bag'), size = 2 * BAG.r + 20;
      g.Kb = Comp.canvas(ctx, bagHost, { w: size, h: size, onResize: function (K) { drawBag(K); } });
      var rnd = Deck.util.rng(SEED + 1);
      g.dots = [];
      for (var i = 0; i < NCOH; i++) { var a = rnd() * Math.PI * 2, rr = Math.sqrt(rnd()) * (BAG.r - 8); g.dots.push([BAG.r + 10 + Math.cos(a) * rr, BAG.r + 10 + Math.sin(a) * rr]); }
      function drawBag(K) {
        var c = K.g; K.clear();
        c.fillStyle = 'rgba(16,21,31,.9)'; c.strokeStyle = '#3A4458'; c.lineWidth = 2;
        c.beginPath(); c.arc(BAG.r + 10, BAG.r + 10, BAG.r, 0, Math.PI * 2); c.fill(); c.stroke();
        c.fillStyle = 'rgba(245,180,60,.55)';
        for (var k = 0; k < g.dots.length; k++) { c.fillRect(g.dots[k][0] - 0.9, g.dots[k][1] - 0.9, 1.8, 1.8); }
      }
      drawBag(g.Kb);
      /* sample rows: three rows of 8 slots */
      var ov = q(el, '#ov');
      g.ov = ov;
      g.rows = [];
      for (var r = 0; r < 3; r++) {
        var y = SLOT.y0 + r * SLOT.dy, row = { slots: [], fills: [], y: y };
        var lab = h('div', 's7-slotlbl', el, 'New sample ' + (r + 1)); lab.style.left = SLOT.x + 'px'; lab.style.top = (y - 44) + 'px';
        for (var k2 = 0; k2 < SLOT.n; k2++) {
          var sx = SLOT.x + k2 * (SLOT.w + SLOT.gap);
          row.slots.push(svgEl('rect', { x: sx, y: y, width: SLOT.w, height: SLOT.w, rx: 8, fill: 'none', stroke: '#3A4458', 'stroke-width': 1.5 }, ov));
          row.fills.push(svgEl('circle', { cx: sx + SLOT.w / 2, cy: y + SLOT.w / 2, r: 9, fill: C.allow }, ov));
        }
        var dots = h('div', 's7-slotlbl', el, '… to n'); dots.style.left = (SLOT.x + SLOT.n * (SLOT.w + SLOT.gap) + 4) + 'px'; dots.style.top = (y + 6) + 'px';
        var chip = h('div', 's7-chip', el, ''); chip.style.left = (SLOT.x + SLOT.n * (SLOT.w + SLOT.gap) + 76) + 'px'; chip.style.top = (y + 2) + 'px';
        row.lab = lab; row.dots = dots; row.chip = chip;
        gsap.set(row.fills, { autoAlpha: 0 });
        gsap.set([lab, dots, chip].concat(row.slots), { autoAlpha: 0 });
        g.rows.push(row);
      }
      g.badge = svgEl('g', {}, ov);
      svgEl('rect', { x: -24, y: -15, width: 48, height: 28, rx: 14, fill: C.bg3, stroke: C.ink, 'stroke-width': 1.5 }, g.badge);
      var bt = svgEl('text', { x: 0, y: 4, 'text-anchor': 'middle', fill: C.ink, 'font-size': 18, 'font-weight': 800 }, g.badge); bt.textContent = '×2';
      gsap.set(g.badge, { autoAlpha: 0 });
      g.ring = svgEl('circle', { r: 10, fill: 'none', stroke: '#fff', 'stroke-width': 2 }, ov); gsap.set(g.ring, { autoAlpha: 0 });
      g.carry = svgEl('circle', { r: 6, fill: C.allow }, ov); gsap.set(g.carry, { autoAlpha: 0 });
      g.hand = Comp.walker(ctx, ov, { x: BAG.cx, y: BAG.cy - BAG.r - 40, r: 8, hidden: true });
      /* picks (seeded); in sample 1 the 6th pick repeats the 2nd → ×2 */
      var rp = Deck.util.rng(SEED + 2);
      g.picks = [0, 1, 2].map(function () { var a = []; for (var k3 = 0; k3 < SLOT.n; k3++) a.push(Math.floor(rp() * NCOH)); return a; });
      g.picks[0][5] = g.picks[0][1];
      /* histogram */
      g.vals = bootValues();
      g.sampleTau = [g.vals[0], g.vals[1], g.vals[2]];
      var hs = q(el, '#hist');
      function X(v) { return (v - HIST.lo) / (HIST.hi - HIST.lo) * HIST.w; }
      g.X = X;
      svgEl('line', { x1: 0, x2: HIST.w, y1: HIST.base, y2: HIST.base, stroke: C.ink2, 'stroke-width': 1.5 }, hs);
      [0.575, 0.580, 0.585, 0.590, 0.595].forEach(function (t) {
        svgEl('line', { x1: X(t), x2: X(t), y1: HIST.base, y2: HIST.base + 8, stroke: C.ink2, 'stroke-width': 1.5 }, hs);
        var tt = svgEl('text', { x: X(t), y: HIST.base + 30, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'tnum svg-mono' }, hs); tt.textContent = t.toFixed(3);
      });
      var ax = svgEl('text', { x: HIST.w, y: -14, 'text-anchor': 'end', fill: C.ink3, 'font-size': 18 }, hs); ax.textContent = 'τ of each resample · bar shape is an example';
      var BW = 0.001, nb = Math.ceil((HIST.hi - HIST.lo) / BW), cnt = new Array(nb).fill(0);
      g.ticks = g.vals.map(function (v) {
        var b = Math.max(0, Math.min(nb - 1, Math.floor((v - HIST.lo) / BW))), k4 = cnt[b]++;
        var bx = X(HIST.lo + b * BW) + 1.5, bw = X(HIST.lo + BW) - X(HIST.lo) - 3;
        var r2 = svgEl('rect', { x: bx, y: HIST.base - 6 - k4 * 5.4, width: bw, height: 3.8, rx: 1.2, fill: C.allow }, hs);
        r2.__y = HIST.base - 6 - k4 * 5.4;
        return r2;
      });
      gsap.set(g.ticks, { autoAlpha: 0 });
      /* trimming shades and the middle band */
      var lo = nums(FAM_ER_A)[1], hi = nums(FAM_ER_A)[2], est = nums(FAM_ER_A)[0];
      g.shL = svgEl('rect', { x: 0, y: 0, width: X(lo), height: HIST.base, fill: 'rgba(10,13,20,.78)' }, hs);
      g.shR = svgEl('rect', { x: X(hi), y: 0, width: HIST.w - X(hi), height: HIST.base, fill: 'rgba(10,13,20,.78)' }, hs);
      g.cutL = svgEl('line', { x1: X(lo), x2: X(lo), y1: 0, y2: HIST.base + 10, stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '5 5' }, hs);
      g.cutR = svgEl('line', { x1: X(hi), x2: X(hi), y1: 0, y2: HIST.base + 10, stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '5 5' }, hs);
      g.pL = svgEl('text', { x: X(lo) / 2, y: 40, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 22, 'font-weight': 700 }, hs); g.pL.textContent = '2.5%';
      g.pR = svgEl('text', { x: (X(hi) + HIST.w) / 2, y: 40, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 22, 'font-weight': 700 }, hs); g.pR.textContent = '2.5%';
      g.band = svgEl('rect', { x: X(lo), y: 10, width: X(hi) - X(lo), height: HIST.base - 10, fill: 'rgba(245,180,60,.10)', stroke: 'rgba(245,180,60,.5)', 'stroke-width': 1.5 }, hs);
      g.pM = svgEl('text', { x: (X(lo) + X(hi)) / 2, y: 40, 'text-anchor': 'middle', fill: C.ink, 'font-size': 24, 'font-weight': 800 }, hs); g.pM.textContent = '95%';
      g.eL = svgEl('text', { x: X(lo), y: HIST.base + 70, 'text-anchor': 'middle', fill: C.ink, 'font-size': 26, 'font-weight': 800, 'class': 'tnum' }, hs); g.eL.textContent = lo.toFixed(3);
      g.eR = svgEl('text', { x: X(hi), y: HIST.base + 70, 'text-anchor': 'middle', fill: C.ink, 'font-size': 26, 'font-weight': 800, 'class': 'tnum' }, hs); g.eR.textContent = hi.toFixed(3);
      gsap.set([g.shL, g.shR, g.cutL, g.cutR, g.pL, g.pR, g.band, g.pM, g.eL, g.eR], { autoAlpha: 0 });
      /* the G9 interval bar the band turns into */
      var by = HIST.base + 118;
      g.ibar = svgEl('line', { x1: X(lo), x2: X(hi), y1: by, y2: by, stroke: C.allow, 'stroke-width': 6, 'stroke-linecap': 'round' }, hs);
      g.idot = svgEl('circle', { cx: X(est), cy: by, r: 11, fill: C.allow, stroke: C.allow, 'stroke-width': 3 }, hs);
      gsap.set([g.ibar, g.idot], { autoAlpha: 0 });
      g.by = by; g.lo = lo; g.hi = hi;
      g.cnt = q(el, '#cnt'); g.cn = q(el, '#cn'); g.res = q(el, '#res'); g.foot = q(el, '#foot');
      gsap.set([g.cnt, g.res, g.foot], { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo(g.Kb.canvas, { autoAlpha: 0, scale: 0.85, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.7, ease: E.out }, 0.2);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(g.cnt, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0);
        tl.set(g.hand.g, { autoAlpha: 1 }, 0);
        var t = 0.2;
        g.rows.forEach(function (row, r) {
          var per = r === 0 ? 0.42 : 0.17;
          tl.fromTo([row.lab].concat(row.slots), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25, stagger: 0.02 }, t);
          tl.fromTo(row.dots, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, t + 0.1);
          t += 0.3;
          g.picks[r].forEach(function (di, k) {
            var d = g.dots[di], px = BAG.cx - BAG.r - 10 + d[0], py = BAG.cy - BAG.r - 10 + d[1];
            var sx = SLOT.x + k * (SLOT.w + SLOT.gap) + SLOT.w / 2, sy = row.y + SLOT.w / 2;
            tl.add(g.hand.moveTo(px, py, { duration: per * 0.45, ease: 'power2.inOut' }), t);
            tl.set(g.ring, { autoAlpha: 1, attr: { cx: px, cy: py } }, t + per * 0.45);
            tl.fromTo(g.ring, { attr: { r: 4 } }, { attr: { r: 14 }, duration: per * 0.4, ease: 'power2.out' }, t + per * 0.45);
            tl.set(g.carry, { autoAlpha: 1, attr: { cx: px, cy: py } }, t + per * 0.45);
            tl.to(g.carry, { attr: { cx: sx, cy: sy }, duration: per * 0.5, ease: 'power2.inOut' }, t + per * 0.5);
            tl.add(g.hand.moveTo(sx, sy - 26, { duration: per * 0.5, ease: 'power2.inOut' }), t + per * 0.5);
            tl.set(g.carry, { autoAlpha: 0 }, t + per);
            tl.set(g.ring, { autoAlpha: 0 }, t + per);
            tl.fromTo(row.fills[k], { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.18, ease: E.stamp }, t + per);
            if (r === 0 && k === 5) {
              tl.set(g.badge, { x: sx + 20, y: sy - 32 }, t + per);
              tl.fromTo(g.badge, { autoAlpha: 0, scale: 1.5 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp }, t + per);
              tl.fromTo([row.fills[1], row.fills[5]], { attr: { r: 9 } }, { attr: { r: 12 }, duration: 0.2, yoyo: true, repeat: 1 }, t + per + 0.05);
            }
            t += per + 0.02;
          });
          /* τ of this resample (illustrative) → one tick on the histogram */
          var tv = g.sampleTau[r];
          tl.call(function () { row.chip.textContent = 'τ = ' + tv.toFixed(3); }, null, t);
          tl.fromTo(row.chip, { autoAlpha: 0, x: -10 }, { autoAlpha: 1, x: 0, duration: 0.25 }, t);
          tl.fromTo(g.ticks[r], { autoAlpha: 0, attr: { y: g.ticks[r].__y - 120 } }, { autoAlpha: 1, attr: { y: g.ticks[r].__y }, duration: 0.45, ease: 'bounce.out' }, t + 0.2);
          tl.call(function (n) { g.cn.textContent = String(n); }, [r + 1], t + 0.3);
          t += 0.45;
        });
        tl.add(g.hand.hide(), t);
      }
      if (i === 2) {
        var rest = g.ticks.slice(3), st = { n: 3 };
        tl.to(st, { n: B, duration: 1.9, ease: 'power2.in', onUpdate: function () { g.cn.textContent = String(Math.round(st.n)); }, onComplete: function () { g.cn.textContent = String(B); } }, 0.2);
        rest.forEach(function (r, k) {
          var at = 0.2 + 1.9 * Math.pow((k + 1) / rest.length, 0.5);
          tl.fromTo(r, { autoAlpha: 0, attr: { y: r.__y - 160 } }, { autoAlpha: 1, attr: { y: r.__y }, duration: 0.35, ease: 'power2.in' }, at - 0.35);
        });
      }
      if (i === 3) {
        tl.fromTo(g.shL, { autoAlpha: 0, attr: { width: 0 } }, { autoAlpha: 1, attr: { width: g.X(g.lo) }, duration: 0.7, ease: E.out }, 0);
        tl.fromTo(g.shR, { autoAlpha: 0, attr: { x: HIST.w, width: 0 } }, { autoAlpha: 1, attr: { x: g.X(g.hi), width: HIST.w - g.X(g.hi) }, duration: 0.7, ease: E.out }, 0);
        tl.fromTo([g.cutL, g.cutR], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.6);
        tl.fromTo([g.pL, g.pR], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.7);
        tl.fromTo(g.band, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 0.9);
        tl.fromTo(g.pM, { autoAlpha: 0, scale: 0.6, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: E.stamp }, 1.0);
        tl.add(ctx.count(g.eL, 0.570, g.lo, { decimals: 3, final: g.lo.toFixed(3), duration: 0.9 }), 1.0);
        tl.add(ctx.count(g.eR, 0.600, g.hi, { decimals: 3, final: g.hi.toFixed(3), duration: 0.9 }), 1.0);
        tl.fromTo([g.eL, g.eR], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 1.0);
        tl.fromTo(g.foot, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 1.4);
      }
      if (i === 4) {
        /* shared-element hand-over: the band flattens into the interval bar (G9) */
        tl.to([g.pL, g.pR, g.pM, g.shL, g.shR], { autoAlpha: 0, duration: 0.3 }, 0);
        tl.to(g.ticks, { opacity: 0.3, duration: 0.4 }, 0);
        tl.to(g.band, { attr: { y: g.by - 3, height: 6 }, fill: 'rgba(245,180,60,1)', duration: 0.8, ease: E.io }, 0.2);
        tl.to([g.cutL, g.cutR], { attr: { y1: g.by - 14, y2: g.by + 14 }, duration: 0.8, ease: E.io }, 0.2);
        tl.set(g.ibar, { autoAlpha: 1 }, 1.0);
        tl.set(g.band, { autoAlpha: 0 }, 1.02);
        tl.fromTo(g.idot, { autoAlpha: 0, scale: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp }, 1.05);
        tl.to([g.eL, g.eR], { attr: { y: g.by + 44 }, duration: 0.6, ease: E.io }, 0.2);
        tl.fromTo(g.res, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 1.2);
      }
    }
  };

  /* ================================================================ s07-05 paired difference, margin, Bonferroni */
  var slide5 = {
    id: 's07-05', title: 'Paired difference Δτ, margin, Bonferroni', time: 55, steps: 5,
    tags: function (step) { return step >= 4 ? ['posthoc', 'example'] : step >= 2 ? ['posthoc', 'example'] : ['posthoc']; },
    notes: [
      'When we compare two scores, we do not look at their two intervals separately. We compute the difference directly on the same samples. As a real example, let’s compare the in-approve degree and EndorseRank at predicting new approval pairs in W0. This comparison was computed after the labels were seen, so it is post hoc.',
      'The in-approve degree is 0.250 and EndorseRank is 0.231. The two intervals overlap, so looked at separately, it is hard to tell whether there is a difference.',
      'But the two scores are computed together on the same 400 samples. When one comes out high on a sample, the other comes out high too, so they rise and fall together. The dots on the right are an example that shows this pattern. The table below also uses example numbers. Over three samples the two taus move by 0.02 at a time, like 0.27, 0.23, 0.25, but the difference is −0.02 every time. Because they move together, the difference moves less. It is like weighing two people on the same scale: the difference between their weights is less affected by the scale’s error. (Advanced) As a formula, the variance of the difference is the sum of the two variances minus 2 times the covariance, so when they move together it gets smaller by that much.',
      'So when we compute the difference on each of the same 400 samples, its interval runs from −0.026 to −0.011 and stays fully clear of 0. Separately they overlap; paired, they separate. On the allowance side, the plain count predicted a little better than EndorseRank.',
      'There is also a verdict that only asks whether one score is not worse by more than a set margin. This is called non-inferiority. The margin delta is 0.01, and the verdict passes if the lower end of the difference interval lies above −0.01. The two bars in the figure are illustrations.',
      'Finally, Bonferroni. When we make two verdicts together, the chance that one of them is wrong by luck goes up. These two verdicts appear in section 09 under the names P and Q. So the two split the 5% error budget into 2.5% each, and each uses a 97.5% interval. These two verdicts were computed with 2,000 resamples, and we will see their values later, in the section on the rules.'
    ],
    html:
      '<h1 class="t-h1">Separately they overlap, [[paired]] they separate</h1>' +
      '<p class="abs s7-sub" style="left:96px;top:158px">W0 · new approval pairs · the same ' + fmt(B, 0) + ' resamples · Kendall’s τ<sub>b</sub></p>' +
      '<div class="abs" id="f1" data-in="none" style="left:96px;top:214px;width:1100px"></div>' +
      '<div class="abs" id="f2" data-in="none" style="left:96px;top:452px;width:1100px"></div>' +
      '<div class="abs s7-lines" data-step="3" style="left:96px;top:620px;width:1100px">' +
        '<p class="l" style="font-size:26px;line-height:38px">Both scores computed on the same ' + fmt(B, 0) + ' samples → also ' + fmt(B, 0) + ' differences Δτ</p>' +
        '<p class="l" style="font-size:26px;line-height:38px">If the 95% interval of the difference excludes 0, we count it as a difference</p>' +
        '<p class="l" style="font-size:22px;line-height:32px;color:var(--ink-2)">Here the plain count (in-approve degree) predicted a little better than EndorseRank</p></div>' +
      '<svg class="abs" id="sc" data-in="none" width="330" height="330" style="left:1396px;top:196px;overflow:visible"></svg>' +
      '<div class="abs s7-scale" id="scl" data-in="none" style="left:1240px;top:578px;width:584px">' +
        '<svg width="78" height="70" viewBox="0 0 78 70" fill="none" stroke="#A3ADBF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="40" width="66" height="24" rx="6"/><rect x="24" y="46" width="30" height="12" rx="2" stroke="#E9EDF5"/><circle cx="26" cy="14" r="6"/><path d="M26 20v14M18 26h16"/><circle cx="52" cy="10" r="6"/><path d="M52 16v18M44 23h16"/></svg>' +
        '<span>Two people on the same scale: the<br>scale’s error affects their difference less</span></div>' +
      '<div class="abs s7-var" id="var" data-in="none" style="left:1240px;top:656px;width:584px">' +
        '<div class="hd">Example numbers · three resamples</div>' +
        '<table><tr><th class="l"></th><th class="c-deg">in-approve degree τ</th><th class="c-allow">EndorseRank τ</th><th>difference</th></tr>' +
        '<tr><td class="l">sample 1</td><td>0.27</td><td>0.25</td><td class="d">−0.02</td></tr>' +
        '<tr><td class="l">sample 2</td><td>0.23</td><td>0.21</td><td class="d">−0.02</td></tr>' +
        '<tr><td class="l">sample 3</td><td>0.25</td><td>0.23</td><td class="d">−0.02</td></tr></table>' +
        '<div class="nt">τ moves by ±0.02 per sample, the difference is −0.02 every time<br>→ they move together, so the difference moves less</div></div>' +
      '<div class="abs" id="mg" data-in="none" style="left:96px;top:780px;width:1100px;height:210px"></div>' +
      '<div class="abs" id="bf" data-in="none" style="left:1130px;top:806px;width:694px;height:180px"></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var a = nums(W0_DEG), b = nums(W0_ER), d = nums(W0_DIFF);
      var fm3 = function (v) { return mfmt(v, 3); };
      g.F1 = Comp.forest(ctx, q(el, '#f1'), { w: 1100, rowH: 74, labelWidth: 300, valueWidth: 300, domain: [0.2, 0.28], ticks: [0.2, 0.22, 0.24, 0.26, 0.28], zero: false,
        tickFormat: function (t) { return t.toFixed(2); }, hidden: true, top: 14,
        rows: [{ label: 'In-approve degree', sub: 'raw degree · at the freeze date', est: a[0], lo: a[1], hi: a[2], color: 'deg', text: W0_DEG },
               { label: 'EndorseRank', sub: 'uniform restarts', est: b[0], lo: b[1], hi: b[2], color: 'allow', text: W0_ER }] });
      /* overlap band between the two intervals */
      var ox0 = g.F1.x(Math.max(a[1], b[1])), ox1 = g.F1.x(Math.min(a[2], b[2]));
      g.ov = svgEl('rect', { x: ox0, y: 14, width: ox1 - ox0, height: 2 * 74, fill: 'rgba(233,237,245,.10)', stroke: 'rgba(233,237,245,.35)', 'stroke-dasharray': '4 4' }, g.F1.svg);
      g.F1.svg.insertBefore(g.ov, g.F1.svg.firstChild);
      g.ovl = svgEl('text', { x: (ox0 + ox1) / 2, y: 6, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 20, 'font-weight': 700 }, g.F1.svg); g.ovl.textContent = 'overlap';
      gsap.set([g.ov, g.ovl], { autoAlpha: 0 });
      g.F2 = Comp.forest(ctx, q(el, '#f2'), { w: 1100, rowH: 80, labelWidth: 300, valueWidth: 300, domain: [-0.04, 0.02], ticks: [-0.04, -0.03, -0.02, -0.01, 0, 0.01, 0.02],
        tickFormat: function (t) { return mfmt(t, 2); }, hidden: true, top: 14,
        rows: [{ label: 'Paired difference Δτ', sub: 'EndorseRank − in-approve degree', est: d[0], lo: d[1], hi: d[2], color: 'ink', text: W0_DIFF }] });
      gsap.set(g.F2.svg, { autoAlpha: 0 });
      g.gap = svgEl('text', { x: g.F2.x(-0.005), y: 14 + 40 - 22, 'text-anchor': 'middle', fill: C.ink, 'font-size': 22, 'font-weight': 800 }, g.F2.svg); g.gap.textContent = 'separate';
      g.gapA = svgEl('path', { d: 'M' + g.F2.x(d[2]) + ',' + (14 + 40 + 16) + ' L' + g.F2.x(0) + ',' + (14 + 40 + 16), stroke: C.ink, 'stroke-width': 2, fill: 'none', 'marker-end': null }, g.F2.svg);
      gsap.set([g.gap, g.gapA], { autoAlpha: 0 });
      /* joint scatter of 400 illustrative pairs (τ_A, τ_B), one per resample */
      var sc = q(el, '#sc'), W = 300, rnd = Deck.util.rng(SEED + 5);
      g.sc = sc;
      svgEl('rect', { x: 0, y: 0, width: W, height: W, rx: 12, fill: 'rgba(16,21,31,.7)', stroke: C.line }, sc);
      var xl = svgEl('text', { x: W / 2, y: W + 28, 'text-anchor': 'middle', fill: C.deg, 'font-size': 18, 'font-weight': 600 }, sc); xl.textContent = 'τ of in-approve degree';
      var yl = svgEl('text', { x: -14, y: W / 2, 'text-anchor': 'middle', fill: C.allow, 'font-size': 18, 'font-weight': 600, transform: 'rotate(-90 -14 ' + W / 2 + ')' }, sc); yl.textContent = 'τ of EndorseRank';
      var ex = svgEl('text', { x: W - 8, y: 22, 'text-anchor': 'end', fill: C.ink3, 'font-size': 16 }, sc); ex.textContent = '400 dots · example';
      svgEl('line', { x1: 20, y1: W - 20, x2: W - 20, y2: 20, stroke: C.ink3, 'stroke-width': 1.2, 'stroke-dasharray': '4 6' }, sc);
      g.pts = []; var P = [];
      for (var i = 0; i < B; i++) {
        var u1 = 1 - rnd(), u2 = rnd(), z1 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2), z2 = Math.sqrt(-2 * Math.log(u1)) * Math.sin(2 * Math.PI * u2);
        var x = z1, y = 0.9 * z1 + Math.sqrt(1 - 0.81) * z2;
        var px = W / 2 + x * 42, py = W / 2 - y * 42;
        P.push([px, py]);
        g.pts.push(svgEl('circle', { cx: px, cy: py, r: 2.6, fill: C.ink, 'fill-opacity': 0.55 }, sc));
      }
      g.P = P;
      g.cross = svgEl('g', {}, sc);
      g.chx = svgEl('line', { x1: 0, y1: W, x2: 0, y2: 0, stroke: C.deg, 'stroke-width': 1.5, 'stroke-dasharray': '3 4' }, g.cross);
      g.chy = svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 0, stroke: C.allow, 'stroke-width': 1.5, 'stroke-dasharray': '3 4' }, g.cross);
      g.chd = svgEl('circle', { r: 7, fill: 'none', stroke: '#fff', 'stroke-width': 2.5 }, g.cross);
      gsap.set(g.cross, { autoAlpha: 0 });
      gsap.set([sc, q(el, '#scl'), q(el, '#var')], { autoAlpha: 0 });
      g.W = W;
      /* non-inferiority margin: mini axis, δ band, two illustrative intervals */
      var mg = q(el, '#mg'), ms = Comp.svg(ctx, mg, { w: 1100, h: 210 });
      var mx0 = 300, mx1 = 800, dom = [-0.03, 0.01];
      function MX(v) { return mx0 + (v - dom[0]) / (dom[1] - dom[0]) * (mx1 - mx0); }
      g.MX = MX;
      var pid = 's7-hatch-' + Math.floor(MX(0));
      var pat = svgEl('pattern', { id: pid, width: 10, height: 10, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, svgEl('defs', {}, ms));
      svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 10, stroke: C.hi, 'stroke-width': 3, 'stroke-opacity': 0.55 }, pat);
      g.mgG = svgEl('g', {}, ms);
      var ttl = svgEl('text', { x: 0, y: 34, fill: C.ink, 'font-size': 24, 'font-weight': 700 }, g.mgG); ttl.textContent = 'Non-inferiority (margin δ = ' + DELTA.toFixed(2) + ')';
      var tt2 = svgEl('text', { x: 0, y: 66, fill: C.ink2, 'font-size': 20 }, g.mgG); tt2.textContent = 'Lower end above −δ →';
      var tt3 = svgEl('text', { x: 0, y: 94, fill: C.ink2, 'font-size': 20 }, g.mgG); tt3.textContent = '‘not worse by more than δ’';
      svgEl('rect', { x: MX(-DELTA), y: 18, width: MX(0) - MX(-DELTA), height: 140, fill: 'url(#' + pid + ')' }, g.mgG);
      var bl = svgEl('text', { x: (MX(-DELTA) + MX(0)) / 2, y: 12, 'text-anchor': 'middle', fill: C.hi, 'font-size': 18, 'font-weight': 700 }, g.mgG); bl.textContent = 'margin';
      svgEl('line', { x1: mx0, x2: mx1, y1: 158, y2: 158, stroke: C.ink2, 'stroke-width': 1.5 }, g.mgG);
      [-0.03, -0.02, -0.01, 0, 0.01].forEach(function (t) {
        svgEl('line', { x1: MX(t), x2: MX(t), y1: 158, y2: 166, stroke: C.ink2, 'stroke-width': 1.5 }, g.mgG);
        var tt = svgEl('text', { x: MX(t), y: 188, 'text-anchor': 'middle', fill: t === -DELTA ? C.hi : C.ink3, 'font-size': 17, 'class': 'tnum svg-mono' }, g.mgG); tt.textContent = t === 0 ? '0' : mfmt(t, 2);
      });
      svgEl('line', { x1: MX(0), x2: MX(0), y1: 18, y2: 158, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, g.mgG);
      function ex1(y, lo, hi, est, ok, lab) {
        var gg = svgEl('g', {}, g.mgG);
        svgEl('line', { x1: MX(lo), x2: MX(hi), y1: y, y2: y, stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round' }, gg);
        svgEl('circle', { cx: MX(est), cy: y, r: 8, fill: C.ink }, gg);
        var tx = svgEl('text', { x: mx1 + 22, y: y + 7, fill: ok ? C.ink : C.hi, 'font-size': 20, 'font-weight': 700 }, gg); tx.textContent = lab;
        var br = svgEl('path', { d: 'M' + (MX(lo - 0.002) + 6) + ',' + (y - 14) + ' L' + MX(lo - 0.002) + ',' + (y - 14) + ' L' + MX(lo - 0.002) + ',' + (y + 14) + ' L' + (MX(lo - 0.002) + 6) + ',' + (y + 14) +
          ' M' + (MX(hi + 0.002) - 6) + ',' + (y - 14) + ' L' + MX(hi + 0.002) + ',' + (y - 14) + ' L' + MX(hi + 0.002) + ',' + (y + 14) + ' L' + (MX(hi + 0.002) - 6) + ',' + (y + 14), stroke: C.ink, 'stroke-width': 2, fill: 'none' }, gg);
        gsap.set(br, { autoAlpha: 0 });
        return { g: gg, br: br };
      }
      g.exA = ex1(62, -0.006, 0.008, 0.001, true, 'example: passes ✓');
      g.exB = ex1(118, -0.018, -0.002, -0.010, false, 'example: fails ✕');
      gsap.set(mg, { autoAlpha: 0 });
      /* Bonferroni: 5 % → 2.5 % + 2.5 % */
      var bf = q(el, '#bf'), bs = Comp.svg(ctx, bf, { w: 694, h: 180 });
      g.bf = bf;
      var cx = 70, cy = 70, R = 52;
      g.pieBg = svgEl('circle', { cx: cx, cy: cy, r: R, fill: 'rgba(233,237,245,.06)', stroke: C.ink3, 'stroke-width': 1.5 }, bs);
      function wedge(a0, a1) { var p0 = [cx + R * Math.sin(a0), cy - R * Math.cos(a0)], p1 = [cx + R * Math.sin(a1), cy - R * Math.cos(a1)]; return 'M' + cx + ',' + cy + ' L' + p0[0] + ',' + p0[1] + ' A' + R + ',' + R + ' 0 0 1 ' + p1[0] + ',' + p1[1] + ' Z'; }
      var A5 = 2 * Math.PI * 0.05;
      g.wP = svgEl('path', { d: wedge(0, A5 / 2), fill: C.hi, 'fill-opacity': 0.85 }, bs);
      g.wQ = svgEl('path', { d: wedge(A5 / 2, A5), fill: C.hi, 'fill-opacity': 0.6 }, bs);
      var pl = svgEl('text', { x: cx, y: cy + R + 30, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18 }, bs); pl.textContent = '5% error budget';
      g.chP = svgEl('g', {}, bs); gsap.set(g.chP, { x: 176, y: 22 });
      svgEl('rect', { x: 0, y: 0, width: 150, height: 40, rx: 20, fill: C.bg3, stroke: C.ink2 }, g.chP);
      var tP = svgEl('text', { x: 75, y: 27, 'text-anchor': 'middle', fill: C.ink, 'font-size': 20, 'font-weight': 700 }, g.chP); tP.textContent = 'verdict 1 · 2.5%';
      g.chQ = svgEl('g', {}, bs); gsap.set(g.chQ, { x: 176, y: 78 });
      svgEl('rect', { x: 0, y: 0, width: 150, height: 40, rx: 20, fill: C.bg3, stroke: C.ink2 }, g.chQ);
      var tQ = svgEl('text', { x: 75, y: 27, 'text-anchor': 'middle', fill: C.ink, 'font-size': 20, 'font-weight': 700 }, g.chQ); tQ.textContent = 'verdict 2 · 2.5%';
      g.bfTx = h('div', 's7-rule', bf, '$1-\\dfrac{0.05}{2}=0.975$<br>→ a <b>97.5%</b> interval for each<small>Two verdicts share the 5% error budget (they appear as P and Q in 09) · these two use ' + fmt(B2, 0) + ' resamples</small>');
      g.bfTx.style.position = 'absolute'; g.bfTx.style.left = '350px'; g.bfTx.style.top = '0px'; g.bfTx.style.width = '344px';
      Deck.renderMath(g.bfTx);
      gsap.set(bf, { autoAlpha: 0 });
      g.d = d;
    },
    enter: function (el, ctx) { void ctx; },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.add(g.F1.show(0), 0);
        tl.add(g.F1.show(1), 0.35);
        tl.fromTo(g.ov, { autoAlpha: 0, scaleY: 0, transformOrigin: '50% 50%' }, { autoAlpha: 1, scaleY: 1, duration: 0.5, ease: E.out }, 1.2);
        tl.fromTo(g.ovl, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 1.5);
      }
      if (i === 2) {
        tl.fromTo(g.sc, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
        tl.fromTo(g.pts, { autoAlpha: 0, attr: { r: 0 } }, { autoAlpha: 1, attr: { r: 2.6 }, duration: 0.3, stagger: 0.002 }, 0.2);
        /* one resample at a time: both coefficients move up or down together */
        var hops = [17, 203, 88, 311, 145, 260], W = g.W;
        tl.set(g.cross, { autoAlpha: 1 }, 1.2);
        hops.forEach(function (k, j) {
          var p = g.P[k], t = 1.2 + j * 0.55;
          tl.to(g.chd, { attr: { cx: p[0], cy: p[1] }, duration: j ? 0.35 : 0.01, ease: E.io }, t);
          tl.to(g.chx, { attr: { x1: p[0], x2: p[0], y1: W, y2: p[1] }, duration: j ? 0.35 : 0.01, ease: E.io }, t);
          tl.to(g.chy, { attr: { x1: 0, x2: p[0], y1: p[1], y2: p[1] }, duration: j ? 0.35 : 0.01, ease: E.io }, t);
        });
        tl.fromTo(q(el, '#scl'), { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 1.6);
        tl.fromTo(q(el, '#var'), { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 2.2);
      }
      if (i === 3) {
        tl.set(g.F2.svg, { autoAlpha: 1 }, 0);
        tl.add(g.F2.show(0, { duration: 0.8 }), 0);
        tl.fromTo([g.gap, g.gapA], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.1);
        tl.to(g.cross, { autoAlpha: 0, duration: 0.3 }, 0);
      }
      if (i === 4) {
        tl.fromTo(q(el, '#mg'), { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
      }
      if (i === 5) {
        tl.to(q(el, '#var'), { autoAlpha: 0, y: -10, duration: 0.3, ease: E['in'] }, 0);
        tl.fromTo(g.bf, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.15);
        tl.fromTo(g.chP, { autoAlpha: 0, x: 96 }, { autoAlpha: 1, x: 176, duration: 0.6, ease: E.out }, 0.5);
        tl.fromTo(g.chQ, { autoAlpha: 0, x: 96 }, { autoAlpha: 1, x: 176, duration: 0.6, ease: E.out }, 0.65);
        tl.fromTo(g.wP, { x: 0, y: 0 }, { x: 14, y: -6, duration: 0.5, ease: E.out }, 0.4);
        tl.fromTo(g.wQ, { x: 0, y: 0 }, { x: 16, y: 8, duration: 0.5, ease: E.out }, 0.45);
        tl.fromTo([g.exA.br, g.exB.br], { autoAlpha: 0, scaleX: 0.6, transformOrigin: '50% 50%' }, { autoAlpha: 1, scaleX: 1, duration: 0.5, ease: E.out }, 1.0);
      }
    }
  };

  Deck.section({ id: 's07-measure', title: 'How we measure', slides: [slide1, slide2, slide3, slide4, slide5] });
})();
