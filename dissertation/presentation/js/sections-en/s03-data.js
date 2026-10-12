/* =========================================================================
   s03-data — The data (STORYBOARD.md §2, s03-01 … s03-06), English edition

   Every number on screen is read from window.DECK_DATA (built from the two
   results digests and experiments/data/) with the digest value as fallback:
     revised digest (R) = the thesis's main analysis; registered digest (G) is
     labeled "registered analysis" wherever it appears (s03-02 plan-stage rows, s03-04 the
     first two funnel stages).
   Pictures that are only illustrations (s03-05 galaxies) carry the Example tag.
   No address or contract name is ever drawn (honesty rule 8).
   Styles are injected once with the prefix .s3- so they cannot leak into
   other sections.
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, U = Deck.util, fmt = U.fmt, E = Deck.E;
  var DD = window.DECK_DATA || {};
  var SC = DD.scale || {}, REV = SC.revised || {}, REG = SC.registered || {};
  var TLD = DD.timeline || {}, PR = DD.prices || {}, RES = DD.results || {}, BM = DD.benchmark || {};

  /* ---------------------------------------------------------------- helpers */
  function get(o, path, fb) {
    var cur = o, parts = path.split('.');
    for (var i = 0; i < parts.length; i++) { if (cur == null) return fb; cur = cur[parts[i]]; }
    return cur == null ? fb : cur;
  }
  function S(tag, attrs, parent) { return Comp.svgEl(tag, attrs, parent); }
  function H(tag, cls, parent, html) {
    var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e;
  }
  function T(parent, x, y, text, attrs) {
    var a = { x: x, y: y, fill: C.ink2, 'font-size': 20 };
    if (attrs) for (var k in attrs) a[k] = attrs[k];
    var t = S('text', a, parent); t.textContent = text; return t;
  }
  /* SVG text with "T_obs"-style subscripts: parts = ['Allowance: price on the anchor day (t₁, T', ['obs'], ')'] */
  function TS(parent, x, y, parts, attrs) {
    var t = T(parent, x, y, '', attrs);
    var shift = 0;
    parts.forEach(function (pt) {
      var sub = Array.isArray(pt), sp = S('tspan', sub ? { 'font-size': Math.round((+(attrs && attrs['font-size']) || 20) * 0.7), dy: 5 - shift } : { dy: -shift }, t);
      sp.textContent = sub ? pt[0] : pt; shift = sub ? 5 : 0;
    });
    return t;
  }
  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function easeIO(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
  function easeOut3(t) { return 1 - Math.pow(1 - t, 3); }
  function backOut(t) { var c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); }
  function rgba(hex, a) { var c = Comp.rgb(hex); return 'rgba(' + Math.round(c[0] * 255) + ',' + Math.round(c[1] * 255) + ',' + Math.round(c[2] * 255) + ',' + a + ')'; }
  function n0(v) { return fmt(v, 0); }
  var LOCK_SVG = (Deck.ICONS && Deck.ICONS.lock) || '';

  /* numbers (digest value as fallback; see STORYBOARD §0.2 for the keys) */
  var N = {
    appr: get(REV, 'rows.revised_ego.approvals', 224954202),
    xfer: get(REV, 'rows.revised_ego.transfers', 1149168538),
    regAppr: get(REV, 'rows.registered_ego.approvals', 389866882),
    regXfer: get(REV, 'rows.registered_ego.transfers', 1538404067),
    w1Appr: get(REV, 'rows.revised_ego.approvals_w1', 12209894),
    w1Xfer: get(REV, 'rows.revised_ego.transfers_w1', 60182192),
    bqUsd: get(TLD, 'bigquery.total_usd', 34.8),
    budget: get(TLD, 'bigquery.budget_usd', 50),
    cand: get(REG, 'candidates', 29022),
    codeContract: get(REG, 'by_code_kind.contract', 27844),
    codeNone: get(REG, 'by_code_kind.none', 1121),
    code7702: get(REG, 'by_code_kind.eip7702', 57),
    matched: get(REV, 'cohort', 15107),
    leftOut: get(REV, 'left_out_of_registered', 12737),
    outA: get(REV, 'graph_tobs.cohort_outside_allowance', 523),
    outT: get(REV, 'graph_tobs.cohort_outside_transfer', 2670),
    outBoth: get(REV, 'graph_tobs.cohort_outside_both', 80),
    gAn: get(REV, 'graph_tobs.allowance.nodes', 6221665),
    gAe: get(REV, 'graph_tobs.allowance.edges', 11210114),
    gTn: get(REV, 'graph_tobs.transfer.nodes', 7884602),
    gTe: get(REV, 'graph_tobs.transfer.edges', 25001216),
    owners: get(REV, 'amounts.owners', 6208769),
    maxAge: get(TLD, 'anchors.max_age_days_tobs', 1004)
  };
  /* R§10 "AWP/EndorseRank edge ratio (derived)": edges of the two solver graphs */
  N.edgeRatio = (get(BM, 'revised.main.awp.edges', 25001216) / get(BM, 'revised.main.endorserank.edges', 11210114));
  var TIES = get(RES, 'revised.same_window.ties.endorserank', { distinct: 13625, zeros: 535 });
  var TIES_AWP = get(RES, 'revised.same_window.ties.awp', { distinct: 12435, zeros: 2672 });
  /* zero scores = contracts outside that graph + contracts whose only pairs carry amounts too small
     for the value weight to differ from zero (thesis Ch. 4: 535 = 523 + 12, 2,672 = 2,670 + 2) */
  N.tinyA = TIES.zeros - N.outA;
  N.tinyT = TIES_AWP.zeros - N.outT;

  /* ---------------------------------------------------------------- styles */
  (function injectStyle() {
    if (document.getElementById('s3-style')) return;
    var st = document.createElement('style'); st.id = 's3-style';
    st.textContent = [
      '.s3-wm{position:absolute;right:96px;top:62px;font-family:var(--font-mono);font-size:88px;line-height:96px;font-weight:700;color:rgba(233,237,245,.13);letter-spacing:-.02em;font-variant-numeric:tabular-nums;white-space:nowrap}',
      '.s3-axis-shared{background:var(--ink-2);border-radius:1px;transform-origin:0 50%}',
      '.s3-caps{display:flex;gap:32px}',
      '.s3-cap{position:relative;padding-left:20px}',
      '.s3-cap::before{content:"";position:absolute;left:0;top:8px;bottom:6px;width:3px;border-radius:2px;background:var(--line)}',
      '.s3-cap b{display:block;font-size:28px;line-height:40px;font-weight:700;color:var(--ink);white-space:nowrap}',
      '.s3-cap span{display:block;font-size:22px;line-height:32px;color:var(--ink-2)}',
      '.s3-lockcard{display:flex;flex-direction:column;align-items:center;gap:4px;padding:12px 6px;border-radius:12px;background:rgba(10,13,20,.9);border:1px solid var(--line);text-align:center;font-size:17px;line-height:22px;color:var(--ink-2)}',
      '.s3-lockcard svg{width:30px;height:30px;color:var(--ink)}',
      '.s3-lockcard .mono{color:var(--ink);font-size:16px}',
      /* s03-02 */
      '.s3-numcol{position:absolute}',
      '.s3-numcol .s3-growth{position:absolute;left:0;top:30px;overflow:visible;z-index:0}',
      '.s3-numcol .s3-numlab{position:relative;z-index:1}',
      '.s3-big{position:relative;z-index:1;display:flex;align-items:baseline;gap:14px;font-size:104px;line-height:112px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums;white-space:nowrap;margin-top:6px}',
      '.s3-big .s3-unit{font-size:40px;line-height:48px;font-weight:600;color:var(--ink-2)}',
      '.s3-slot{position:absolute;left:0;top:64px;height:104px;border:2px dashed rgba(103,112,131,.55);border-radius:16px;z-index:1}',
      '.s3-cards{display:flex;gap:32px}',
      '.s3-card{flex:1 1 0;min-width:0;background:var(--bg-2);border-radius:16px;padding:24px 28px;position:relative}',
      '.s3-card .s3-card-h{display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:24px;line-height:34px;font-weight:700;color:var(--ink)}',
      '.s3-card .s3-row{display:flex;justify-content:space-between;font-size:28px;line-height:42px;font-variant-numeric:tabular-nums;margin-top:6px}',
      '.s3-card .s3-row .k{color:var(--ink-2)}',
      '.s3-card .s3-usd{font-size:48px;line-height:58px;font-weight:700;font-variant-numeric:tabular-nums;margin-top:8px}',
      '.s3-meter{position:relative;height:10px;border-radius:5px;background:var(--bg-3);margin-top:14px}',
      '.s3-meter .fill{position:absolute;left:0;top:0;bottom:0;border-radius:5px;background:var(--ink-2);transform-origin:0 50%}',
      '.s3-meter .tick{position:absolute;right:0;top:-8px;bottom:-8px;width:2px;background:var(--ink)}',
      '.s3-meter-l{display:flex;justify-content:space-between;font-size:17px;line-height:24px;color:var(--ink-3);margin-top:8px;font-family:var(--font-mono);letter-spacing:0}',
      '.s3-barlab{font-size:24px;line-height:32px;font-weight:700}',
      '.s3-barval{font-size:24px;line-height:32px;color:var(--ink-2);font-variant-numeric:tabular-nums;white-space:nowrap}',
      /* s03-03 */
      '.s3-fx .s3-fx-eq{font-size:34px;line-height:52px;margin:6px 0 4px}',
      '.s3-fx .s3-fx-leg{display:grid;grid-template-columns:auto 1fr;column-gap:14px;row-gap:2px;font-size:20px;line-height:30px;color:var(--ink-2)}',
      '.s3-fx .s3-fx-leg .katex{font-size:1.1em;color:var(--ink)}',
      '.s3-check{display:flex;gap:16px;align-items:flex-start;background:var(--bg-2);border:1px solid var(--line);border-radius:16px;padding:14px 22px}',
      '.s3-check svg{width:30px;height:30px;flex:0 0 auto;margin-top:4px;color:var(--ink)}',
      '.s3-check b{display:block;font-size:22px;line-height:32px;font-weight:700}',
      '.s3-check span{display:block;font-size:20px;line-height:30px;color:var(--ink-2)}',
      /* s03-04 */
      '.s3-fl-cap{font-size:24px;line-height:34px;color:var(--ink-2)}',
      '.s3-fl-num{font-size:64px;line-height:72px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums;white-space:nowrap;display:flex;align-items:baseline;gap:14px}',
      '.s3-fl-num .eq{font-size:24px;line-height:34px;font-weight:600;color:var(--ink);letter-spacing:-.01em}',
      '.s3-fl-small{font-size:20px;line-height:28px;color:var(--ink-3)}',
      /* s03-05 */
      '.s3-gname{font-size:36px;line-height:46px;font-weight:700}',
      '.s3-gnums{display:flex;gap:28px;font-size:28px;line-height:40px;color:var(--ink-2);font-variant-numeric:tabular-nums;white-space:nowrap}',
      '.s3-gnums b{color:var(--ink);font-weight:700}',
      '.s3-rrow{position:relative;height:56px}',
      '.s3-rlab{position:absolute;left:0;top:10px;font-size:24px;line-height:34px;font-weight:700}',
      '.s3-rbar{position:absolute;left:200px;top:12px;height:30px;border-radius:6px;transform-origin:0 50%}',
      '.s3-rval{position:absolute;top:10px;font-size:24px;line-height:34px;color:var(--ink);font-variant-numeric:tabular-nums;white-space:nowrap}',
      '.s3-rtick{position:absolute;top:4px;width:2px;height:46px;background:var(--ink)}',
      '.s3-rtickl{position:absolute;top:52px;font-size:17px;line-height:22px;color:var(--ink-2);font-family:var(--font-mono);letter-spacing:0;transform:translateX(-50%)}',
      '.s3-ghostbar{position:absolute;height:10px;border-radius:5px;background:var(--c-allow);box-shadow:0 0 0 2px #0A0D14}',
      '.s3-ratio{position:absolute;font-size:30px;line-height:40px;font-weight:700;white-space:nowrap}',
      /* s03-06 */
      '.s3-tick3d{font-size:18px;line-height:24px;color:var(--ink-3);font-variant-numeric:tabular-nums;text-shadow:0 0 6px #0A0D14}',
      '.s3-three-fade{-webkit-mask-image:linear-gradient(to bottom,#000 0,#000 82%,transparent 100%);mask-image:linear-gradient(to bottom,#000 0,#000 82%,transparent 100%)}',
      '.s3-ax3d{font-size:22px;line-height:30px;font-weight:700;text-shadow:0 0 8px #0A0D14,0 0 3px #0A0D14}',
      '.s3-cap3d{position:absolute}',
      '.s3-cap3d p{position:absolute;left:0;top:0;white-space:nowrap}',
      '.s3-legend3d{display:flex;gap:36px;align-items:center;font-size:24px;line-height:34px;color:var(--ink-2)}',
      '.s3-legend3d i{display:inline-block;width:28px;height:3px;border-radius:2px;margin-right:10px;vertical-align:middle}',
      '.s3-colleg{position:absolute}',
      '.s3-colleg span{position:absolute;right:0;top:0;white-space:nowrap;font-size:24px;line-height:34px;color:var(--ink-2)}',
      '.s3-colleg i{display:inline-block;width:56px;height:10px;border-radius:5px;margin-right:12px;vertical-align:middle}',
      '.s3-zero{position:absolute}',
      '.s3-zero div{position:absolute;right:0;top:0;text-align:right;white-space:nowrap}',
      '.s3-zero b{color:var(--ink-2);font-weight:700}'
    ].join('\n');
    document.head.appendChild(st);
  })();

  /* =================================================================== s03-01
     Three-year calendar: time axis 2023-10 … 2026-09, monthly ego counts (two streams,
     each scaled to its own maximum), freeze pins t1 / T_obs, label windows
     W0 / W1 (hatched), lock on W1, age ruler from T_obs (0 … 1,004 days). */
  var MC = get(TLD, 'monthly_counts.revised', {});
  var monA = (MC.approval_ego || []).map(function (r) { return r[1]; });
  var monT = (MC.transfer_ego || []).map(function (r) { return r[1]; });
  var AX = { left: 96, top: 196, w: 1728, h: 660, axisY: 520 };
  var T0 = Comp.parseDate('2023-10-01'), T1 = Comp.parseDate('2026-09-30'), TOBS = Comp.parseDate('2026-07-01');
  function monthLabel(ms) { var d = new Date(ms); return d.getUTCFullYear() + '-' + U.pad2(d.getUTCMonth() + 1); }

  var slide1 = {
    id: 's03-01', title: 'Three-year calendar', time: 40, steps: 4,
    notes: [
      'The data are the public records of Arbitrum One. Let me spread three years out on this time axis.',
      'The observation window runs from 1 October 2023 to 30 June 2026, 33 months. The amber band on top is the approval records created each month, and the sky-blue band below is the transfer records. Each band is scaled to its own height, so please compare only their shapes. Add the three months of the label window W1 and it is exactly three years.',
      'We tested twice. In W0 the scores were frozen on 31 March 2026 and graded on what happened from April to June.',
      'In W1 the scores were frozen on 30 June and graded on what happened from July to September. This study extracted the records of these three months only after commit 0d3a057, which committed the grading rules to the public repository as the registration. That is why there is a lock on it.',
      'Last is the age ruler. The time weight is measured backward from T_obs, that is, 30 June 2026. The oldest record is 1,004 days old. This ruler comes back later when I explain the time weight.'
    ],
    html:
      '<h1 class="t-h1">[[Three years]] of records, two tests</h1>' +
      '<div class="s3-wm" id="wm" data-in="none"></div>' +
      '<div class="abs" id="chart" data-in="none" style="left:' + AX.left + 'px;top:' + AX.top + 'px;width:' + AX.w + 'px;height:' + AX.h + 'px"></div>' +
      '<div class="abs s3-axis-shared" data-shared="time-axis" style="left:' + AX.left + 'px;top:' + (AX.top + AX.axisY - 1) + 'px;width:' + AX.w + 'px;height:2px"></div>' +
      '<div class="abs" id="w1note" data-in="none"></div>' +
      '<div class="abs s3-caps" style="left:96px;top:890px;width:1728px">' +
        '<div class="s3-cap" data-step="1" style="width:620px"><b>Observation window · 33 months</b><span>1 Oct 2023 – 30 Jun 2026</span></div>' +
        '<div class="s3-cap" data-step="2" style="width:520px"><b>W0 · frozen 31 Mar 2026</b><span>graded on Apr–Jun events</span></div>' +
        '<div class="s3-cap" data-step="3" style="width:520px"><b>W1 · frozen 30 Jun 2026</b><span>graded on Jul–Sep · extracted after registration</span></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var TL = g.TL = Comp.timeline(ctx, el.querySelector('#chart'), { w: AX.w, h: AX.h, axisY: AX.axisY, padL: 0, padR: 0 });
      var kids = Array.prototype.slice.call(TL.axis.childNodes);
      g.line = kids[0]; g.ticks = kids.slice(1);
      gsap.set(g.line, { visibility: 'hidden' });
      gsap.set(g.ticks, { autoAlpha: 0 });
      /* streams: approvals above, transfers just above the axis; each scaled to its own max */
      g.sA = TL.stream(monA, { color: 'allow', height: 170, base: 250, opacity: 0.26 });
      g.sT = TL.stream(monT, { color: 'xfer', height: 200, base: AX.axisY - 14, opacity: 0.26 });
      gsap.set([g.sA.g, g.sT.g], { autoAlpha: 0 });
      var lab = g.labels = S('g', {}, TL.svg);
      /* English: the "per month" note follows its label as a tspan (no fixed x offset to measure) */
      [[62, 'Approval records', C.allow], [330, 'Transfer records', C.xfer]].forEach(function (r) {
        var lt = T(lab, 0, r[0], r[1], { fill: r[2], 'font-size': 24, 'font-weight': 700 });
        var sp = S('tspan', { dx: 14, fill: C.ink2, 'font-size': 20, 'font-weight': 500 }, lt); sp.textContent = 'per month';
      });
      T(lab, 0, 360, 'Bands scaled separately', { fill: C.ink3, 'font-size': 18 });
      gsap.set(lab, { autoAlpha: 0 });
      /* freeze pins and label windows */
      g.p1 = TL.pin('2026-04-01', { label: 't₁', y0: 40 });
      g.p2 = TL.pin('2026-07-01', { label: 'T', y0: 40 });
      if (g.p2.label) { var ts = S('tspan', { 'font-size': 15, dy: 5 }, g.p2.label); ts.textContent = 'obs'; }
      g.b0 = TL.band('2026-04-01', '2026-07-01', { label: 'W0', y0: 64 });
      g.b1 = TL.band('2026-07-01', '2026-10-01', { label: 'W1', y0: 64 });
      /* W1 lock card, inside the (empty) W1 band */
      var x1 = TL.x('2026-07-01'), x2 = TL.x('2026-10-01');
      var note = el.querySelector('#w1note');
      note.style.left = (AX.left + x1 + 6) + 'px'; note.style.top = (AX.top + 150) + 'px'; note.style.width = (x2 - x1 - 12) + 'px';
      note.innerHTML = '<div class="s3-lockcard">' + LOCK_SVG + '<span>Extracted after registration commit</span><span class="mono">0d3a057</span></div>';
      gsap.set(note, { autoAlpha: 0 });
      /* age ruler (step 4): from T_obs back to the first day */
      var R = g.ruler = S('g', {}, TL.svg), ry = 590, xo = TL.x(TOBS);
      var dayPx = (TL.x(T1) - TL.x(T0)) / ((T1 - T0) / 864e5);
      g.rLine = S('line', { x1: xo, x2: xo, y1: ry, y2: ry, stroke: C.ink2, 'stroke-width': 2 }, R);
      g.rTicks = [];
      [0, 180, 365, 730, N.maxAge].forEach(function (age, k, arr) {
        var x = xo - age * dayPx, last = k === arr.length - 1;
        var tk = S('line', { x1: x, x2: x, y1: ry - 9, y2: ry + 9, stroke: C.ink, 'stroke-width': 2 }, R);
        var tx = T(R, x, ry + 34, '0', { fill: last ? C.ink : C.ink2, 'font-size': 20, 'text-anchor': last ? 'start' : 'middle', 'class': 'tnum', 'font-weight': last ? 700 : 500 });
        g.rTicks.push({ age: age, x: x, tick: tk, text: tx, last: last });
      });
      g.rCap = TS(R, 0, ry + 66, ['Age = days counted back from T', ['obs'], ' (30 Jun 2026), the anchor of the time weight · the oldest record is ' + n0(N.maxAge) + ' days old'], { fill: C.ink3, 'font-size': 18 });
      g.rArrow = S('path', { d: 'M' + (TL.x(T0) + 12) + ',' + (ry - 7) + ' L' + TL.x(T0) + ',' + ry + ' L' + (TL.x(T0) + 12) + ',' + (ry + 7), fill: 'none', stroke: C.ink2, 'stroke-width': 2 }, R);
      gsap.set(R, { autoAlpha: 0 });
      g.wm = el.querySelector('#wm');
      gsap.set(g.wm, { autoAlpha: 0 });
      /* the shared axis line: flies in from the previous slide's plate edge (s02-05) when that slide
         carries data-shared="time-axis"; otherwise it is drawn in by enter() */
      g.shared = el.querySelector('[data-shared="time-axis"]');
      g.flew = !!(ctx.prev && ctx.prev.rect && ctx.prev.rect('time-axis')) && !ctx.reduced;
      if (!g.flew) gsap.set(g.shared, { scaleX: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (!g.flew) tl.to(g.shared, { scaleX: 1, duration: 0.9, ease: E.io }, 0.05);
      /* hand over from the shared div to the real SVG axis line (same place, same look) */
      tl.call(function () { g.shared.style.visibility = 'hidden'; g.line.style.visibility = 'visible'; }, null, g.flew ? 0.02 : 1.0);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl(), TL = g.TL;
      if (i === 1) {
        var D1 = 2.0, ease = 'power1.inOut';
        tl.set([g.sA.g, g.sT.g], { autoAlpha: 1 }, 0);
        tl.add(g.sA.reveal({ duration: D1, ease: ease }), 0);
        tl.add(g.sT.reveal({ duration: D1, ease: ease }), 0);
        /* ticks and year labels appear as the reveal passes them */
        g.ticks.forEach(function (tk) {
          var x = +(tk.getAttribute('x1') || tk.getAttribute('x') || 0);
          var p = x / AX.w, t = invEase(p) * D1;
          tl.fromTo(tk, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, Math.max(0, t - 0.05));
        });
        var wm = { p: 0 }, cap = Comp.parseDate('2026-06-15');
        tl.call(function () { g.wm.textContent = '2023-10'; }, null, 0);
        tl.set(g.wm, { autoAlpha: 1 }, 0);
        tl.to(wm, { p: 1, duration: D1, ease: ease, onUpdate: function () {
          g.wm.textContent = monthLabel(Math.min(cap, T0 + wm.p * (T1 - T0)));
        }, onComplete: function () { g.wm.textContent = '2026-06'; } }, 0);
        tl.fromTo(g.labels, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, D1 * 0.45);
      }
      if (i === 2) {
        tl.add(g.p1.drop(), 0);
        tl.add(g.b0.show(), 0.45);
      }
      if (i === 3) {
        tl.add(g.p2.drop(), 0);
        tl.add(g.b1.show(), 0.45);
        var note = el.querySelector('#w1note');
        tl.fromTo(note, { autoAlpha: 0, y: 16, scale: 0.92 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.45, ease: E.stamp }, 0.9);
      }
      if (i === 4) {
        var xo = TL.x(TOBS), x0 = TL.x(T0);
        tl.set(g.ruler, { autoAlpha: 1 }, 0);
        tl.fromTo(g.rLine, { attr: { x2: xo } }, { attr: { x2: x0 }, duration: 1.4, ease: 'power2.inOut' }, 0);
        tl.fromTo(g.rArrow, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 1.3);
        g.rTicks.forEach(function (r) {
          var frac = (xo - r.x) / (xo - x0), t = 1.4 * invEase(frac);
          tl.fromTo([r.tick, r.text], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, t);
          var o = { v: 0 };
          tl.to(o, { v: r.age, duration: 0.5, ease: 'power2.out', onUpdate: function () { r.text.textContent = n0(o.v) + (r.last || r.age === 0 ? ' days' : ''); },
            onComplete: function () { r.text.textContent = n0(r.age) + (r.last || r.age === 0 ? ' days' : ''); } }, t);
        });
        tl.fromTo(g.rCap, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.5 }, 1.5);
      }
    }
  };
  /* inverse of power1.inOut (2t² / 1-2(1-t)²): time at which the reveal reaches fraction p */
  function invEase(p) { p = clamp01(p); return p < 0.5 ? Math.sqrt(p / 2) : 1 - Math.sqrt((1 - p) / 2); }

  /* =================================================================== s03-02
     How many records: two odometers with cumulative growth lines behind
     them, a waffle (one dot = 1,000,000 records) that reflows into two bars,
     then three small cards (registered-analysis rows, W1 rows, BigQuery cost). */
  var DOT = 1e6;
  var nDotA = Math.round(N.appr / DOT), nDotT = Math.round(N.xfer / DOT);
  function cumulative(arr) { var s = 0, out = [0]; arr.forEach(function (v) { s += v; out.push(s); }); return out; }

  function numCol(id, x, w, label, cls) {
    return '<div class="s3-numcol" id="col' + id + '" style="left:' + x + 'px;top:226px;width:' + w + 'px;height:200px">' +
      '<div class="t-body-l s3-numlab ' + cls + '" style="font-weight:700">' + label + '</div>' +
      '<div class="s3-slot" id="slot' + id + '"></div>' +
      '<div class="s3-big"><span id="n' + id + '"></span><span class="s3-unit" id="u' + id + '"></span></div>' +
    '</div>';
  }

  var slide2 = {
    id: 's03-02', title: 'How many records', time: 35, steps: 3,
    notes: [
      'Let me start with the volume of records. Across the five tokens, I counted only the records that have a contract under study at one end. The period is the 33-month observation window.',
      'There are more than 220 million approval records and more than 1.1 billion transfer records. The line behind each number is the records piling up month by month. Below, one dot is one million records, so approvals make 225 dots and transfers 1,149 dots.',
      'If I stack the same dots again as bars, the difference in length is easy to see. There are about five times as many transfers as approvals. Approvals happen much more rarely than transfers.',
      'When all tokens were extracted, as first planned, there were 390 million approval records and 1.5 billion transfer records. These are the numbers of the registered analysis. The W1 records from July to September were extracted by this study separately, after the registration. The cloud cost of all these queries was 34.80 dollars, within the budget of 50 dollars set at the start.'
    ],
    html:
      '<h1 class="t-h1">How many records are there?</h1>' +
      '<p class="abs t-body ink-2" style="left:96px;top:162px">Five tokens · only records with a cohort contract at one end · observation window of 33 months</p>' +
      numCol('A', 96, 820, 'Approval records', 'c-allow') + numCol('T', 1000, 824, 'Transfer records', 'c-xfer') +
      '<p class="abs t-caption ink-2" style="left:96px;top:436px" data-step="1">One dot = [[1 million records]] <span class="ink-3">· divided by 1 million and rounded</span></p>' +
      '<div class="abs" id="cv" data-in="none" style="left:96px;top:480px;width:1728px;height:450px"></div>' +
      '<div class="abs" id="barlabs" data-in="none" style="left:96px;top:480px;width:1728px;height:200px">' +
        '<div class="abs s3-barlab c-allow" style="left:0;top:24px">Approvals</div>' +
        '<div class="abs s3-barlab c-xfer" style="left:0;top:104px">Transfers</div>' +
        '<div class="abs s3-barval" id="bvA" style="top:24px"></div>' +
        '<div class="abs s3-barval" id="bvT" style="top:104px"></div>' +
      '</div>' +
      '<div class="abs s3-cards" style="left:96px;top:700px;width:1728px" data-step="3" data-stagger="0.12">' +
        '<div class="s3-card"><div class="s3-card-h"><span>Plan stage · all tokens</span>' + Deck.tagHTML('registered-analysis') + '</div>' +
          '<div class="s3-row"><span class="k">Approvals</span><span>' + n0(N.regAppr) + '</span></div>' +
          '<div class="s3-row"><span class="k">Transfers</span><span>' + n0(N.regXfer) + '</span></div></div>' +
        '<div class="s3-card"><div class="s3-card-h"><span style="white-space:nowrap">W1 · Jul–Sep 2026</span><span class="t-caption ink-3" style="white-space:nowrap;font-size:22px">extracted after registration</span></div>' +
          '<div class="s3-row"><span class="k">Approvals</span><span>' + n0(N.w1Appr) + '</span></div>' +
          '<div class="s3-row"><span class="k">Transfers</span><span>' + n0(N.w1Xfer) + '</span></div></div>' +
        '<div class="s3-card"><div class="s3-card-h"><span>Total BigQuery cost</span></div>' +
          '<div class="s3-usd"><span>$</span><span id="usd">' + fmt(N.bqUsd, 2) + '</span></div>' +
          '<div class="s3-meter"><div class="fill" id="mfill" style="width:' + (N.bqUsd / N.budget * 100).toFixed(1) + '%"></div><div class="tick"></div></div>' +
          '<div class="s3-meter-l"><span>0</span><span>budget $' + n0(N.budget) + '</span></div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = { p1: 0, p2: 0 };
      /* growth lines: cumulative monthly ego counts (sum = the odometer total) */
      [['A', monA, C.allow, 820, N.appr], ['T', monT, C.xfer, 824, N.xfer]].forEach(function (row) {
        var col = el.querySelector('#col' + row[0]), w = row[3], hgt = 150;
        var cum = cumulative(row[1]), tot = cum[cum.length - 1] || 1;
        var svg = Comp.svg(ctx, null, { w: w, h: hgt, className: 's3-growth' });
        col.insertBefore(svg, col.firstChild);
        var pts = cum.map(function (v, k) { return [k / (cum.length - 1) * w, hgt - v / tot * (hgt - 8)]; });
        var d = 'M' + pts.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' L');
        var area = S('path', { d: d + ' L' + w + ',' + hgt + ' L0,' + hgt + ' Z', fill: row[2], 'fill-opacity': 0.07 }, svg);
        var path = S('path', { d: d, fill: 'none', stroke: row[2], 'stroke-width': 3, 'stroke-opacity': 0.55, 'stroke-linecap': 'round' }, svg);
        var dot = S('circle', { cx: 0, cy: hgt, r: 7, fill: row[2] }, svg);
        gsap.set(path, { autoAlpha: 0 });
        var L = path.getTotalLength ? path.getTotalLength() : 1000;
        gsap.set(path, { strokeDasharray: L + ' ' + L, strokeDashoffset: L });
        gsap.set([area, dot], { autoAlpha: 0 });
        g['gl' + row[0]] = { path: path, area: area, dot: dot, L: L };
        /* the empty slot shows the final width of the number */
        var slot = el.querySelector('#slot' + row[0]);
        slot.style.width = (row[0] === 'A' ? 640 : 735) + 'px';
      });
      gsap.set([el.querySelector('#uA'), el.querySelector('#uT')], { autoAlpha: 0 });
      /* waffle + bars on one canvas */
      var W = 1728, Hc = 450;
      var dots = g.dots = [];
      function addDots(n, wx, wy, by, color, group) {
        for (var i = 0; i < n; i++) {
          var wc = i % 45, wr = Math.floor(i / 45);
          var bc = Math.floor(i / 5), br = i % 5;
          dots.push({ x0: wx + 9 + wc * 17, y0: wy + 9 + wr * 17, r0: 6.2, x1: 150 + bc * 6.2 + 3, y1: by + br * 6.2 + 3, r1: 2.5, c: color, i: i, n: n, g: group });
        }
      }
      addDots(nDotA, 0, 0, 30, C.allow, 0);
      addDots(nDotT, 904, 0, 110, C.xfer, 1);
      function draw() {
        var K = g.K; if (!K) return;
        var c = K.g; K.clear();
        for (var k = 0; k < dots.length; k++) {
          var d = dots[k];
          var shown = g.p1 * (d.n + 6) - d.i;         /* reading-order reveal; every dot is full size at p1 = 1 */
          if (shown <= 0) continue;
          var pop = shown >= 6 ? 1 : backOut(clamp01(shown / 6));
          var q = d.i / d.n * 0.55 + d.g * 0.08;       /* reflow wave, left to right */
          var t = clamp01((g.p2 * 1.63 - q) / 1.0);
          var e = easeIO(t);
          var x = lerp(d.x0, d.x1, e), y = lerp(d.y0, d.y1, e) - Math.sin(Math.PI * e) * 26;
          var r = lerp(d.r0, d.r1, e) * pop;
          c.fillStyle = d.c; c.globalAlpha = 0.92;
          c.beginPath(); c.arc(x, y, Math.max(0.1, r), 0, Math.PI * 2); c.fill();
        }
        c.globalAlpha = 1;
      }
      g.draw = draw;
      g.K = Comp.canvas(ctx, el.querySelector('#cv'), { w: W, h: Hc, onResize: draw });
      draw();
      /* bar end labels */
      var bvA = el.querySelector('#bvA'), bvT = el.querySelector('#bvT');
      bvA.style.left = (150 + Math.ceil(nDotA / 5) * 6.2 + 22) + 'px'; bvA.textContent = n0(nDotA) + ' dots';
      bvT.style.left = (150 + Math.ceil(nDotT / 5) * 6.2 + 22) + 'px'; bvT.textContent = n0(nDotT) + ' dots';
      gsap.set(el.querySelector('#barlabs'), { autoAlpha: 0 });
      gsap.set(el.querySelector('#mfill'), { scaleX: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        var D1 = 2.2;
        tl.to([el.querySelector('#slotA'), el.querySelector('#slotT')], { autoAlpha: 0, duration: 0.3 }, 0);
        tl.add(Comp.odometer(ctx, el.querySelector('#nA'), n0(N.appr), { duration: D1 }), 0);
        tl.add(Comp.odometer(ctx, el.querySelector('#nT'), n0(N.xfer), { duration: D1 }), 0);
        tl.fromTo([el.querySelector('#uA'), el.querySelector('#uT')], { autoAlpha: 0, x: -10 }, { autoAlpha: 1, x: 0, duration: 0.4 }, D1 * 0.8);
        ['A', 'T'].forEach(function (k) {
          var gl = g['gl' + k], o = { p: 0 };
          tl.set([gl.dot, gl.area, gl.path], { autoAlpha: 1 }, 0);
          tl.fromTo(gl.area, { autoAlpha: 0 }, { autoAlpha: 1, duration: D1 }, 0);
          tl.to(o, { p: 1, duration: D1, ease: 'power2.out', onUpdate: function () {
            gl.path.style.strokeDashoffset = (gl.L * (1 - o.p)).toFixed(1);
            var pt = gl.path.getPointAtLength(gl.L * o.p); gl.dot.setAttribute('cx', pt.x); gl.dot.setAttribute('cy', pt.y);
          } }, 0);
        });
        tl.to(g, { p1: 1, duration: D1, ease: 'power2.out', onUpdate: g.draw, onComplete: g.draw }, 0);
      }
      if (i === 2) {
        tl.to(g, { p2: 1, duration: 1.6, ease: 'none', onUpdate: g.draw, onComplete: g.draw }, 0);
        tl.fromTo(el.querySelector('#barlabs'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.2);
      }
      if (i === 3) {
        var usd = el.querySelector('#usd');
        tl.add(ctx.count(usd, 0, N.bqUsd, { decimals: 2, final: fmt(N.bqUsd, 2), duration: 1.4 }), 0.5);
        tl.fromTo(el.querySelector('#mfill'), { scaleX: 0 }, { scaleX: 1, duration: 1.4, ease: 'power2.out' }, 0.5);
      }
    },
    tags: function (step) { return step >= 1 ? ['calc'] : []; }
  };

  /* =================================================================== s03-03
     Five tokens and USD prices: daily USD close of the five tokens on a log scale,
     all in ink-3; the token being discussed is lit. Freeze-date markers; a
     digit ruler (powers of ten) for base units; the conversion formula of
     Chapter 3 (x_e = v 10^{-q} p) as a preview; the Chainlink comparison. */
  var TOK = ['WBTC', 'WETH', 'ARB', 'USDC', 'USDT0'];
  var TOK_LABEL = { WBTC: 'WBTC', WETH: 'WETH', ARB: 'ARB', USDC: 'USDC', USDT0: 'USDT0' };
  var PC = { x0: 96, x1: 1500, y0: 24, y1: 484, lmin: Math.log10(0.05), lmax: Math.log10(200000) };
  var CHECK_SVG = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="10" cy="10" r="7.6"/><path d="M6.6 10.2l2.3 2.3 4.6-4.9"/></svg>';
  var CL = get(DD, 'params.chainlink', null);

  var slide3 = {
    id: 's03-03', title: 'Five tokens and USD prices', time: 40, steps: 5,
    notes: [
      'Each token has its own unit and its own value, so amounts cannot simply be added together. That is why the revised analysis converted every amount to US dollars. The prices are DefiLlama daily closes, that is, the last price of each day.',
      'Five tokens remain: WETH, USDC, USDT0, ARB and WBTC. Among the ' + n0(get(SC, 'tokens.priced', 46)) + ' tokens whose Chainlink price feed is rated low or medium risk and that have a daily price, these are the five with the most records. All five are priced by feeds rated low risk. The vertical axis is a log scale, so everything from 0.1 dollars to 100,000 dollars fits in one picture.',
      'WETH and WBTC swing up and down a lot. USDC and USDT0, on the other hand, stay almost fixed at one dollar. So the same single token can be worth a different number of dollars from day to day.',
      'A transfer is converted at the price of the day it happened. An allowance is converted at the price of the anchor day, the day the scores are frozen: t₁, 31 March, and T_obs, 30 June. That is because an allowance is a promise that is still alive on that day.',
      'The units must match too. One USDC is a million in base units, that is, six zeros. One WETH has eighteen zeros. That is twelve digits apart. So we multiply the number of base units v by ten to the power minus q to get the number of tokens, and then by that day\'s price p to get dollars. We will see this formula again when we come to the value weight.',
      'I also checked whether these prices can be trusted. Compared with the Chainlink prices on the chain on 38 days for each token, the median difference was 0.01 to 0.08 percent, and the largest difference was 0.72 percent.'
    ],
    html:
      '<h1 class="t-h1">Every amount in [[US dollars]]</h1>' +
      '<p class="abs t-body ink-2" style="left:96px;top:162px">Converted at that day\'s daily close (DefiLlama)</p>' +
      '<div class="abs" id="pc" data-in="none" style="left:96px;top:222px;width:1728px;height:540px"></div>' +
      '<div class="abs s3-check" id="chk" style="left:1150px;top:70px;width:674px" data-step="5" data-in="pop">' + CHECK_SVG +
        '<div><b>Compared with Chainlink feeds · 38 days per token</b><span>Median difference 0.01–0.08% · largest 0.72%</span></div></div>' +
      '<p class="abs t-caption ink-2" id="rcap" data-in="none" style="left:96px;top:784px">Written in base units</p>' +
      '<div class="abs" id="ruler" data-in="none" style="left:96px;top:816px;width:1240px;height:170px"></div>' +
      '<div class="abs s3-fx" id="fx" data-in="none" style="left:1384px;top:784px;width:440px">' +
        '<div class="t-caption ink-2">Conversion to USD · preview</div>' +
        '<div class="s3-fx-eq">$x_e = v \\cdot 10^{-q} \\cdot p$</div>' +
        '<div class="s3-fx-leg"><span>$v$</span><span>number of base units</span><span>$q$</span><span>decimals (USDC 6 · WETH 18)</span><span>$p$</span><span>price that day (USD)</span></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var svg = g.svg = Comp.svg(ctx, el.querySelector('#pc'), { w: 1728, h: 540 });
      var days = PR.days || 1096;
      function X(i) { return PC.x0 + i / (days - 1) * (PC.x1 - PC.x0); }
      function Y(v) { return PC.y0 + (PC.lmax - Math.log10(Math.max(1e-9, v))) / (PC.lmax - PC.lmin) * (PC.y1 - PC.y0); }
      g.X = X; g.Y = Y;
      /* grid + y labels (decades) */
      var grid = S('g', {}, svg);
      [[0.1, '0.1'], [1, '1'], [10, '10'], [100, '100'], [1000, '1,000'], [10000, '10,000'], [100000, '100,000']].forEach(function (d) {
        var y = Y(d[0]);
        S('line', { x1: PC.x0, x2: PC.x1, y1: y, y2: y, stroke: 'rgba(233,237,245,0.07)', 'stroke-width': 1 }, grid);
        T(grid, PC.x0 - 14, y + 6, d[1], { fill: C.ink3, 'font-size': 18, 'text-anchor': 'end', 'class': 'tnum' });
      });
      T(grid, 0, 8, 'Daily price (USD, log scale)', { fill: C.ink3, 'font-size': 18 });
      /* x: years */
      var start = Comp.parseDate(PR.start || '2023-10-01');
      [2024, 2025, 2026].forEach(function (yr) {
        var i = Math.round((Date.UTC(yr, 0, 1) - start) / 864e5), x = X(i);
        S('line', { x1: x, x2: x, y1: PC.y1, y2: PC.y1 + 10, stroke: C.ink3, 'stroke-width': 1.5 }, grid);
        T(grid, x + 6, PC.y1 + 30, String(yr), { fill: C.ink2, 'font-size': 20, 'class': 'tnum' });
      });
      S('line', { x1: PC.x0, x2: PC.x1, y1: PC.y1, y2: PC.y1, stroke: C.line, 'stroke-width': 1.5 }, grid);
      /* watermark date, in the empty band between $10 and $600 */
      g.wm = T(svg, PC.x0 + 40, Y(60) + 24, '', { fill: 'rgba(233,237,245,0.12)', 'font-size': 72, 'font-weight': 700, 'class': 'svg-mono' });
      /* lines, clipped for a synchronous reveal */
      var cid = 's3-pclip-' + Math.floor(Math.random() * 1e9);
      g.clip = S('rect', { x: 0, y: -10, width: 0, height: 560 }, S('clipPath', { id: cid }, S('defs', {}, svg)));
      var lines = S('g', { 'clip-path': 'url(#' + cid + ')' }, svg);
      g.tok = {};
      var close = PR.close || {};
      TOK.forEach(function (k) {
        var arr = close[k] || [];
        if (!arr.length) return;
        var d = 'M' + arr.map(function (v, i) { return X(i).toFixed(1) + ',' + Y(v).toFixed(1); }).join(' L');
        var p = S('path', { d: d, fill: 'none', stroke: C.ink3, 'stroke-width': 1.6, 'stroke-linejoin': 'round' }, lines);
        var last = arr[arr.length - 1], dy = k === 'USDC' ? -10 : k === 'USDT0' ? 14 : 6;
        var lab = T(svg, PC.x1 + 14, Y(last) + dy, TOK_LABEL[k], { fill: C.ink3, 'font-size': 22, 'font-weight': 700 });
        gsap.set(lab, { autoAlpha: 0 });
        g.tok[k] = { path: p, label: lab, arr: arr };
      });
      /* step-2 annotations */
      var ann = g.ann = {};
      function arrowPath(x, y0, y1) { var dn = y1 > y0 ? 1 : -1; return 'M' + x + ',' + y0 + ' L' + x + ',' + y1 + ' M' + (x - 7) + ',' + (y1 - dn * 9) + ' L' + x + ',' + y1 + ' L' + (x + 7) + ',' + (y1 - dn * 9); }
      var ia = Math.round(days * 0.62), ax = X(ia), wethY = g.tok.WETH ? Y(g.tok.WETH.arr[ia]) : Y(2500);
      ann.a = S('g', {}, svg);
      T(ann.a, ax, Y(150), 'Swings widely', { fill: C.ink, 'font-size': 24, 'font-weight': 700, 'text-anchor': 'middle' });
      S('path', { d: arrowPath(ax, Y(150) - 30, wethY + 10), fill: 'none', stroke: C.ink, 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, ann.a);
      var ib = Math.round(days * 0.3), bx = X(ib);
      ann.b = S('g', {}, svg);
      T(ann.b, bx, Y(14), 'Stays close to $1', { fill: C.ink, 'font-size': 24, 'font-weight': 700, 'text-anchor': 'middle' });
      S('path', { d: arrowPath(bx, Y(14) + 10, Y(1) - 8), fill: 'none', stroke: C.ink, 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, ann.b);
      gsap.set([ann.a, ann.b], { autoAlpha: 0 });
      /* step 3: freeze-date markers + dots + caption */
      var idx = PR.index || { t1: 912, t_obs: 1003 };
      g.pins = [];
      [[idx.t1, 't₁'], [idx.t_obs, 'T']].forEach(function (pp, k) {
        var P = Comp.pin(ctx, svg, { x: X(pp[0]), y0: PC.y0 - 4, y1: PC.y1, label: pp[1], labelSize: 20 });
        if (k === 1 && P.label) { var ts = S('tspan', { 'font-size': 15, dy: 5 }, P.label); ts.textContent = 'obs'; }
        var dg = S('g', {}, svg);
        TOK.forEach(function (tk) {
          var t = g.tok[tk]; if (!t) return;
          S('circle', { cx: X(pp[0]), cy: Y(t.arr[pp[0]]), r: 5.5, fill: C.ink, stroke: C.bg, 'stroke-width': 2 }, dg);
        });
        gsap.set(dg, { autoAlpha: 0 });
        g.pins.push({ P: P, dots: dg });
      });
      g.fcap = S('g', {}, svg);
      var fx = X(idx.t1) - 22;
      TS(g.fcap, fx, Y(120), ['Allowance: price on the anchor day (t₁, T', ['obs'], ')'], { fill: C.ink, 'font-size': 22, 'font-weight': 700, 'text-anchor': 'end' });
      T(g.fcap, fx, Y(120) + 32, 'Transfer: price on the day it happened', { fill: C.ink2, 'font-size': 22, 'text-anchor': 'end' });
      gsap.set(g.fcap, { autoAlpha: 0 });
      /* step 4: digit ruler (powers of ten) */
      buildDigitRuler(ctx, g, el.querySelector('#ruler'));
      gsap.set([el.querySelector('#rcap'), el.querySelector('#ruler'), el.querySelector('#fx')], { autoAlpha: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        var D1 = 1.8, o = { p: 0 }, start = Comp.parseDate(PR.start || '2023-10-01'), days = PR.days || 1096;
        tl.to(o, { p: 1, duration: D1, ease: 'power1.inOut', onUpdate: function () {
          g.clip.setAttribute('width', (PC.x0 + o.p * (PC.x1 - PC.x0) + 4).toFixed(1));
          var d = new Date(start + Math.round(o.p * (days - 1)) * 864e5);
          g.wm.textContent = d.getUTCFullYear() + '-' + U.pad2(d.getUTCMonth() + 1) + '-' + U.pad2(d.getUTCDate());
        }, onComplete: function () { g.clip.setAttribute('width', 1728); g.wm.textContent = (PR.end || '2026-09-30'); } }, 0);
        tl.fromTo(TOK.map(function (k) { return g.tok[k] && g.tok[k].label; }).filter(Boolean), { autoAlpha: 0, x: -8 }, { autoAlpha: 1, x: 0, duration: 0.4, stagger: 0.06 }, D1 - 0.1);
        tl.to(g.wm, { attr: { fill: 'rgba(233,237,245,0.07)' }, duration: 0.6 }, D1 + 0.2);
      }
      if (i === 2) {
        var lit = function (keys, col, w) {
          var paths = [], labs = [];
          keys.forEach(function (k) { if (g.tok[k]) { paths.push(g.tok[k].path); labs.push(g.tok[k].label); } });
          return [paths, labs, col, w];
        };
        var A = lit(['WETH', 'WBTC']), B = lit(['USDC', 'USDT0']);
        tl.to(g.wm, { autoAlpha: 0, duration: 0.4 }, 0);
        tl.to(A[0], { attr: { stroke: C.ink, 'stroke-width': 2.6 }, duration: 0.5 }, 0);
        tl.to(A[1], { attr: { fill: C.ink }, duration: 0.5 }, 0);
        tl.fromTo(g.ann.a, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.3);
        tl.to(A[0], { attr: { stroke: C.ink2, 'stroke-width': 1.8 }, duration: 0.5 }, 2.2);
        tl.to(A[1], { attr: { fill: C.ink2 }, duration: 0.5 }, 2.2);
        tl.to(B[0], { attr: { stroke: C.ink, 'stroke-width': 2.6 }, duration: 0.5 }, 2.2);
        tl.to(B[1], { attr: { fill: C.ink }, duration: 0.5 }, 2.2);
        tl.fromTo(g.ann.b, { autoAlpha: 0, y: -10 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 2.5);
      }
      if (i === 3) {
        tl.to([g.ann.a, g.ann.b], { autoAlpha: 0, duration: 0.35 }, 0);
        g.pins.forEach(function (p, k) {
          tl.add(p.P.drop(), 0.2 + k * 0.35);
          tl.fromTo(p.dots.childNodes, { attr: { r: 0 } }, { attr: { r: 5.5 }, duration: 0.35, ease: E.stamp, stagger: 0.05 }, 0.75 + k * 0.35);
          tl.set(p.dots, { autoAlpha: 1 }, 0.75 + k * 0.35);
        });
        tl.fromTo(g.fcap, { autoAlpha: 0, x: 12 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: E.out }, 1.4);
      }
      if (i === 4) {
        tl.fromTo([el.querySelector('#rcap'), el.querySelector('#ruler')], { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 0);
        tl.add(g.ruler.play(ctx), 0.3);
        tl.fromTo(el.querySelector('#fx'), { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, '>-0.2');
      }
    }
  };

  /* digit ruler: rung k = the k-th zero; "1" sits on rung 0. Zoom (rung spacing) goes from 120 px
     (rungs 0–8 visible, enough for 1 USDC = 10^6) to 52 px (rungs 0–18, 1 WETH = 10^18). */
  function buildDigitRuler(ctx, g, host) {
    var W = 1240, Hh = 170, X0 = 250, AXY = 132;
    var svg = Comp.svg(ctx, host, { w: W, h: Hh });
    var cid = 's3-rclip-' + Math.floor(Math.random() * 1e9);
    S('rect', { x: X0 - 40, y: -20, width: W - X0 + 40, height: Hh + 40 }, S('clipPath', { id: cid }, S('defs', {}, svg)));
    var inner = S('g', { 'clip-path': 'url(#' + cid + ')' }, svg);
    var R = g.ruler = { s: 120, rows: [] };
    T(svg, 0, 46, '1 USDC =', { fill: C.ink, 'font-size': 30, 'font-weight': 700 });
    var wethLab = T(svg, 0, 108, '1 WETH =', { fill: C.ink, 'font-size': 30, 'font-weight': 700 });
    /* highlight band for WETH's extra twelve zeros */
    R.band = S('rect', { x: 0, y: 70, width: 10, height: 50, rx: 8, fill: 'rgba(233,237,245,0.07)' }, inner);
    R.axis = S('line', { x1: X0 - 20, x2: W, y1: AXY, y2: AXY, stroke: C.line, 'stroke-width': 1.5 }, inner);
    R.ticks = [];
    for (var k = 0; k <= 18; k++) {
      var tk = S('line', { x1: 0, x2: 0, y1: AXY - 6, y2: AXY + 6, stroke: k % 3 === 0 ? C.ink2 : C.ink3, 'stroke-width': k % 3 === 0 ? 2 : 1 }, inner);
      var tl = null;
      if (k > 0 && k % 3 === 0) { tl = T(inner, 0, AXY + 30, '10', { fill: C.ink3, 'font-size': 18, 'text-anchor': 'middle', 'class': 'tnum' }); var sp = S('tspan', { dy: -8, 'font-size': 13 }, tl); sp.textContent = String(k); }
      R.ticks.push({ k: k, line: tk, label: tl });
    }
    function row(nZeros, y, keyRow) {
      var digits = [];
      for (var j = 0; j <= nZeros; j++) {
        var t = T(inner, 0, y, j === 0 ? '1' : '0', { fill: keyRow && j > 6 ? C.ink : C.ink2, 'font-size': 40, 'font-weight': keyRow && j > 6 ? 700 : 500, 'text-anchor': 'middle', 'class': 'svg-mono' });
        digits.push(t);
      }
      var commas = [];
      for (var c = 0; c < nZeros; c += 3) commas.push({ after: c, el: T(inner, 0, y + 4, ',', { fill: C.ink3, 'font-size': 34, 'text-anchor': 'middle', 'class': 'svg-mono' }) });
      return { digits: digits, commas: commas };
    }
    R.usdc = row(6, 46, false);
    R.weth = row(18, 108, true);
    /* bracket over WETH zeros 7..18 */
    R.br = S('path', { d: '', fill: 'none', stroke: C.ink, 'stroke-width': 2, 'stroke-linecap': 'round' }, inner);
    R.brLabel = T(inner, 0, 44, '12 more zeros', { fill: C.ink, 'font-size': 26, 'font-weight': 700, 'text-anchor': 'middle' });
    R.readout = T(svg, W - 4, 20, '×10', { fill: C.ink, 'font-size': 28, 'font-weight': 700, 'text-anchor': 'end', 'class': 'svg-mono' });
    R.readSup = S('tspan', { dy: -12, 'font-size': 18 }, R.readout); R.readSup.textContent = '0';
    function xr(k) { return X0 + k * R.s; }
    R.layout = function () {
      R.ticks.forEach(function (t) { var x = xr(t.k); t.line.setAttribute('x1', x); t.line.setAttribute('x2', x); if (t.label) t.label.setAttribute('x', x); });
      [R.usdc, R.weth].forEach(function (rw) {
        rw.digits.forEach(function (d, j) { d.setAttribute('x', xr(j)); });
        rw.commas.forEach(function (c) { c.el.setAttribute('x', xr(c.after + 0.5)); });
      });
      R.band.setAttribute('x', xr(6.5)); R.band.setAttribute('width', Math.max(1, xr(18.5) - xr(6.5)));
      var a = xr(6.6), b = xr(18.4), yb = 64;
      R.br.setAttribute('d', 'M' + a + ',' + (yb + 8) + ' L' + a + ',' + yb + ' L' + b + ',' + yb + ' L' + b + ',' + (yb + 8));
      R.brLabel.setAttribute('x', (a + b) / 2);
    };
    R.layout();
    /* initial state (hidden digits) */
    gsap.set(R.usdc.digits.concat(R.weth.digits).concat(R.usdc.commas.map(function (c) { return c.el; })).concat(R.weth.commas.map(function (c) { return c.el; })), { autoAlpha: 0 });
    gsap.set([R.band, R.br, R.brLabel, wethLab], { autoAlpha: 0 });
    R.play = function (cx) {
      var tl = gsap.timeline();
      var z = { s: 120 };
      tl.call(function () { R.s = 120; R.layout(); R.readSup.textContent = '0'; }, null, 0);
      R.usdc.digits.forEach(function (d, j) {
        tl.fromTo(d, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.25, ease: E.out }, 0.1 + j * 0.11);
        if (j > 0) tl.call(function () { R.readSup.textContent = String(j); }, null, 0.1 + j * 0.11);
      });
      tl.to(R.usdc.commas.map(function (c) { return c.el; }), { autoAlpha: 1, duration: 0.25 }, 0.9);
      /* "camera rises": the rungs compress until 10^18 fits */
      tl.to(z, { s: 52, duration: 1.3, ease: 'power2.inOut', onUpdate: function () { R.s = z.s; R.layout(); } }, 1.4);
      tl.fromTo(wethLab, { autoAlpha: 0, x: -10 }, { autoAlpha: 1, x: 0, duration: 0.3 }, 2.7);
      R.weth.digits.forEach(function (d, j) {
        tl.fromTo(d, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.2, ease: E.out }, 2.8 + j * 0.06);
        if (j > 6) tl.call(function () { R.readSup.textContent = String(j); }, null, 2.8 + j * 0.06);
      });
      tl.to(R.weth.commas.map(function (c) { return c.el; }), { autoAlpha: 1, duration: 0.25 }, 3.9);
      tl.fromTo(R.band, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 4.0);
      tl.fromTo(R.br, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 4.1);
      tl.fromTo(R.brLabel, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: E.out }, 4.2);
      tl.call(function () { R.s = 52; R.layout(); R.readSup.textContent = '18'; }, null, 4.6);
      void cx;
      return tl;
    };
  }

  /* =================================================================== s03-04
     Cohort funnel: ~2,900 particles (one ≈ 10 contracts) pour into a funnel;
     EOAs (no code, EIP-7702) leave as hollow grey circles, the contracts that
     miss the rule on five tokens leave as dim boxes, the matched cohort
     remains; contracts outside a graph settle on the floor trays (score 0). */
  var FX = 50;   /* horizontal offset of the funnel inside its canvas */
  var FUN = {
    cx: 640 + FX,
    c1: { y0: 40, y1: 196, t: [150 + FX, 1130 + FX], b: [220 + FX, 1060 + FX] },
    n1: [640 + FX, 218],
    c2: { y0: 240, y1: 380, t: [230 + FX, 1050 + FX], b: [300 + FX, 980 + FX] },
    n2: [640 + FX, 402],
    c3: { y0: 424, y1: 552, t: [310 + FX, 970 + FX], b: [370 + FX, 910 + FX] },
    eoa: { x0: 8, x1: 190, y0: 262, y1: 372 },
    drop: { x0: 8, x1: 268, y0: 440, y1: 690 },
    trayA: { x0: 380 + FX, x1: 560 + FX, y0: 612, y1: 680 },
    trayT: { x0: 500 + FX, x1: 900 + FX, y0: 612, y1: 680 }
  };
  function trapContains(c, x, y) {
    if (y < c.y0 || y > c.y1) return false;
    var f = (y - c.y0) / (c.y1 - c.y0), l = lerp(c.t[0], c.b[0], f), r = lerp(c.t[1], c.b[1], f);
    return x >= l && x <= r;
  }
  function rectContains(r, x, y) { return x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1; }
  /* n jittered-grid points inside a shape (seeded) */
  function fillShape(n, bbox, inside, rng, pad) {
    pad = pad || 6;
    var area = 0, probe = 0, i, x, y;
    for (i = 0; i < 4000; i++) { x = lerp(bbox[0], bbox[2], rng()); y = lerp(bbox[1], bbox[3], rng()); probe++; if (inside(x, y)) area++; }
    var A = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) * area / probe;
    var s = Math.sqrt(A / n) * 0.96, pts = [];
    for (var tries = 0; tries < 30; tries++) {
      pts = [];
      for (y = bbox[1] + pad; y <= bbox[3] - pad; y += s) {
        for (x = bbox[0] + pad + ((Math.round((y - bbox[1]) / s) % 2) ? s / 2 : 0); x <= bbox[2] - pad; x += s) {
          var jx = x + (rng() - 0.5) * s * 0.5, jy = y + (rng() - 0.5) * s * 0.5;
          if (inside(jx, jy) && inside(jx - pad * 0.6, jy) && inside(jx + pad * 0.6, jy)) pts.push([jx, jy]);
        }
      }
      if (pts.length >= n) break;
      s *= 0.95;
    }
    /* drop extras at random (seeded) */
    while (pts.length > n) pts.splice(Math.floor(rng() * pts.length), 1);
    while (pts.length < n) pts.push([lerp(bbox[0], bbox[2], rng()), lerp(bbox[1], bbox[3], rng())]);
    return pts;
  }
  function shuffle(arr, rng) { for (var i = arr.length - 1; i > 0; i--) { var j = Math.floor(rng() * (i + 1)), t = arr[i]; arr[i] = arr[j]; arr[j] = t; } return arr; }

  var PER = 10;
  var P_ALL = Math.round(N.cand / PER), P_EOA = Math.round((N.codeNone + N.code7702) / PER), P_MATCH = Math.round(N.matched / PER);
  var P_DROP = P_ALL - P_EOA - P_MATCH;
  var P_OA = Math.round(N.outA / PER), P_OT = Math.round(N.outT / PER), P_OB = Math.round(N.outBoth / PER);

  var slide4 = {
    id: 's03-04', title: 'Cohort funnel', time: 35, steps: 4,
    notes: [
      'This is how the contracts to be scored were chosen. One particle is about ten contracts.',
      'First I collected the spenders that received approvals from at least three distinct owners in the observation window. There were 29,022. This number comes from the registered analysis, counted on all tokens as the analysis plan said.',
      'Reading the code at each address, 1,121 had no code and 57 carried an EIP-7702 delegation designator. Both are EOAs, moved by a private key, so they were taken out. The remaining 27,844 are the cohort of the analysis plan.',
      'The revised analysis kept the 15,107 that meet this rule on the five tokens alone. We call this the matched cohort. The other 12,737 cannot reach three owners on the five tokens. Because every score is given to these same contracts, differences between the scores do not come from differences in the sample.',
      'Still, some contracts are missing from one of the graphs altogether. 523 are outside the allowance graph and 2,670 are outside the transfer graph, and 80 of them are outside both. Such a contract gets 0 under the score of that graph.'
    ],
    html:
      '<h1 class="t-h1">Cohort funnel</h1>' +
      '<p class="abs t-caption ink-3" style="left:96px;top:160px">One particle ≈ ' + PER + ' contracts</p>' +
      '<div class="abs" id="fun" data-in="none" style="left:96px;top:176px;width:1210px;height:790px"></div>' +
      '<div class="abs" id="eoalab" data-in="none" style="left:104px;top:338px;width:200px">' +
        '<div class="t-caption ink-2" style="font-weight:700">EOAs, removed</div>' +
        '<div class="s3-fl-small">no code ' + n0(N.codeNone) + '</div><div class="s3-fl-small">EIP-7702 ' + n0(N.code7702) + '</div></div>' +
      '<div class="abs" id="droplab" data-in="none" style="left:96px;top:876px;width:330px">' +
        '<div class="t-caption ink-2" style="font-weight:700">' + n0(N.leftOut) + ' left out</div>' +
        '<div class="s3-fl-small" style="font-family:var(--font-sans)">rule not met on the five tokens</div></div>' +
      '<div class="abs" style="left:1340px;top:200px;width:484px" data-step="1">' +
        '<div class="s3-fl-cap">Spenders approved by 3 or more distinct owners</div>' +
        '<div class="s3-fl-num"><span id="f1"></span>' + Deck.tagHTML('registered-analysis') + '</div></div>' +
      '<div class="abs" style="left:1340px;top:404px;width:484px" data-step="2">' +
        '<div class="s3-fl-cap">Has contract code</div>' +
        '<div class="s3-fl-num"><span id="f2"></span><span class="eq">= the plan\'s cohort</span></div>' +
        '<div class="s3-fl-small" style="margin-top:2px">' + Deck.tagHTML('registered-analysis') + '</div></div>' +
      '<div class="abs" style="left:1340px;top:592px;width:484px" data-step="3">' +
        '<div class="s3-fl-cap">3 or more owners on the five tokens alone</div>' +
        '<div class="s3-fl-num"><span class="hl" id="f3"></span></div>' +
        '<div class="s3-fl-cap" style="color:var(--ink)">= matched cohort (revised analysis)</div></div>' +
      '<div class="abs" style="left:1340px;top:780px;width:484px" data-step="4">' +
        '<div class="s3-fl-cap">Of these, missing from one graph:</div>' +
        '<div class="s3-fl-cap"><span class="c-allow">outside the allowance graph</span> <b class="ink tnum">' + n0(N.outA) + '</b></div>' +
        '<div class="s3-fl-cap"><span class="c-xfer">outside the transfer graph</span> <b class="ink tnum">' + n0(N.outT) + '</b> · both <b class="ink tnum">' + n0(N.outBoth) + '</b></div>' +
        '<div class="s3-fl-cap" style="color:var(--ink);font-weight:700;margin-top:4px">→ that score is 0</div></div>',
    build: function (el, ctx) {
      var g = ctx.g = { s: 0, q: 1 };
      var rng = ctx.rng(42);
      var host = el.querySelector('#fun');
      /* outline (svg under the canvas) */
      var svg = g.svg = Comp.svg(ctx, host, { w: 1210, h: 790, style: 'position:absolute;left:0;top:0' });
      function trapPath(c) { return 'M' + c.t[0] + ',' + c.y0 + ' L' + c.t[1] + ',' + c.y0 + ' L' + c.b[1] + ',' + c.y1 + ' L' + c.b[0] + ',' + c.y1 + ' Z'; }
      var outl = g.outline = S('g', {}, svg);
      [FUN.c1, FUN.c2, FUN.c3].forEach(function (c) {
        S('path', { d: trapPath(c), fill: 'rgba(233,237,245,0.025)', stroke: C.ink3, 'stroke-width': 1.5, 'stroke-linejoin': 'round' }, outl);
      });
      [[FUN.c1, FUN.c2], [FUN.c2, FUN.c3]].forEach(function (pr) {
        var a = pr[0], b = pr[1], cx = FUN.cx;
        S('path', { d: 'M' + (cx - 56) + ',' + a.y1 + ' L' + (cx - 26) + ',' + (a.y1 + 12) + ' L' + (cx - 26) + ',' + (b.y0 - 10) + ' L' + (cx - 56) + ',' + b.y0 +
          ' M' + (cx + 56) + ',' + a.y1 + ' L' + (cx + 26) + ',' + (a.y1 + 12) + ' L' + (cx + 26) + ',' + (b.y0 - 10) + ' L' + (cx + 56) + ',' + b.y0, fill: 'none', stroke: C.ink3, 'stroke-width': 1.5 }, outl);
      });
      /* bins and floor trays */
      var bins = g.bins = S('g', {}, svg);
      S('rect', { x: FUN.eoa.x0 - 6, y: FUN.eoa.y0 - 6, width: FUN.eoa.x1 - FUN.eoa.x0 + 12, height: FUN.eoa.y1 - FUN.eoa.y0 + 12, rx: 14, fill: 'none', stroke: C.line, 'stroke-width': 1.5, 'stroke-dasharray': '5 6' }, bins);
      S('rect', { x: FUN.drop.x0 - 6, y: FUN.drop.y0 - 6, width: FUN.drop.x1 - FUN.drop.x0 + 12, height: FUN.drop.y1 - FUN.drop.y0 + 12, rx: 14, fill: 'none', stroke: C.line, 'stroke-width': 1.5, 'stroke-dasharray': '5 6' }, bins);
      gsap.set(bins.childNodes, { autoAlpha: 0 });
      var trays = g.trays = S('g', {}, svg);
      var tA = FUN.trayA, tT = FUN.trayT;
      S('rect', { x: tT.x0, y: tT.y0, width: tT.x1 - tT.x0, height: tT.y1 - tT.y0, rx: 12, fill: rgba(C.xfer, 0.06), stroke: C.xfer, 'stroke-width': 2, 'stroke-dasharray': '6 6' }, trays);
      S('rect', { x: tA.x0, y: tA.y0 - 6, width: tA.x1 - tA.x0, height: tA.y1 - tA.y0 + 12, rx: 12, fill: rgba(C.allow, 0.06), stroke: C.allow, 'stroke-width': 2, 'stroke-dasharray': '6 6' }, trays);
      /* English labels are wider than the Korean ones: the two tray labels sit on two rows */
      T(trays, tA.x0, tA.y1 + 36, 'Outside allowance graph ' + n0(N.outA), { fill: C.allow, 'font-size': 20, 'font-weight': 700 });
      T(trays, tT.x1, tT.y1 + 64, 'Outside transfer graph ' + n0(N.outT), { fill: C.xfer, 'font-size': 20, 'font-weight': 700, 'text-anchor': 'end' });
      T(trays, (tT.x0 + tA.x1) / 2, tA.y0 - 16, 'Both ' + n0(N.outBoth), { fill: C.ink, 'font-size': 18, 'font-weight': 700, 'text-anchor': 'middle' });
      S('path', { d: 'M' + FUN.c3.b[0] + ',' + (FUN.c3.y1 + 22) + ' L' + FUN.c3.b[1] + ',' + (FUN.c3.y1 + 22), stroke: C.ink3, 'stroke-width': 1.5, 'stroke-dasharray': '3 6' }, trays);
      T(trays, FUN.c3.b[1] + 10, FUN.c3.y1 + 28, 'Floor · score 0', { fill: C.ink3, 'font-size': 17 });
      gsap.set(trays, { autoAlpha: 0 });

      /* particles */
      var cont = function (c) { return function (x, y) { return trapContains(c, x, y); }; };
      var bb = function (c) { return [Math.min(c.t[0], c.b[0]), c.y0, Math.max(c.t[1], c.b[1]), c.y1]; };
      var pC1 = fillShape(P_ALL, bb(FUN.c1), cont(FUN.c1), rng, 5);
      var pC2 = fillShape(P_ALL - P_EOA, bb(FUN.c2), cont(FUN.c2), rng, 5);
      var pC3 = fillShape(P_MATCH, bb(FUN.c3), cont(FUN.c3), rng, 5);
      var pEoa = fillShape(P_EOA, [FUN.eoa.x0, FUN.eoa.y0, FUN.eoa.x1, FUN.eoa.y1], function (x, y) { return rectContains(FUN.eoa, x, y); }, rng, 4);
      var pDrop = fillShape(P_DROP, [FUN.drop.x0, FUN.drop.y0, FUN.drop.x1, FUN.drop.y1], function (x, y) { return rectContains(FUN.drop, x, y); }, rng, 3);
      /* floor: A-only, both, T-only */
      var nAonly = P_OA - P_OB, nTonly = P_OT - P_OB;
      var rA = { x0: tA.x0, x1: tT.x0, y0: tA.y0, y1: tA.y1 }, rB = { x0: tT.x0, x1: tA.x1, y0: tA.y0, y1: tA.y1 }, rT = { x0: tA.x1, x1: tT.x1, y0: tT.y0, y1: tT.y1 };
      function inR(r) { return function (x, y) { return rectContains(r, x, y); }; }
      var pFA = fillShape(nAonly, [rA.x0, rA.y0, rA.x1, rA.y1], inR(rA), rng, 6);
      var pFB = fillShape(P_OB, [rB.x0, rB.y0, rB.x1, rB.y1], inR(rB), rng, 8);
      var pFT = fillShape(nTonly, [rT.x0, rT.y0, rT.x1, rT.y1], inR(rT), rng, 5);
      /* fates (seeded shuffle): 0 EOA, 1 dropped, 2 matched (stays), 3 matched floor-A, 4 floor-both, 5 floor-T */
      var fates = [], k;
      for (k = 0; k < P_EOA; k++) fates.push(0);
      for (k = 0; k < P_DROP; k++) fates.push(1);
      for (k = 0; k < P_MATCH - (nAonly + P_OB + nTonly); k++) fates.push(2);
      for (k = 0; k < nAonly; k++) fates.push(3);
      for (k = 0; k < P_OB; k++) fates.push(4);
      for (k = 0; k < nTonly; k++) fates.push(5);
      shuffle(fates, rng);
      var parts = g.parts = [];
      var iC2 = 0, iC3 = 0, iE = 0, iD = 0, iFA = 0, iFB = 0, iFT = 0;
      /* order chamber slots by y so that particles low in C1 also land low (fewer crossings) */
      var c1Order = pC1.map(function (p, j) { return j; });
      for (k = 0; k < P_ALL; k++) {
        var f = fates[k], p1 = pC1[c1Order[k]];
        var P = { fate: f, pos: [] };
        P.pos[0] = [FUN.cx + (rng() - 0.5) * 180, -30 - rng() * 220];
        P.pos[1] = p1;
        P.pos[2] = f === 0 ? pEoa[iE++] : pC2[iC2++];
        P.pos[3] = f === 0 ? P.pos[2] : f === 1 ? pDrop[iD++] : pC3[iC3++];
        P.pos[4] = f === 3 ? pFA[iFA++] : f === 4 ? pFB[iFB++] : f === 5 ? pFT[iFT++] : P.pos[3];
        P.jit = (rng() - 0.5);
        P.r = rng();
        parts.push(P);
      }
      /* per-transition delays: bottom of the source chamber first, plus a little noise */
      parts.forEach(function (P) {
        P.d = [];
        P.d[1] = clamp01(1 - (P.pos[1][1] - FUN.c1.y0) / (FUN.c1.y1 - FUN.c1.y0)) * 0.85 + P.r * 0.15;
        P.d[2] = clamp01(1 - (P.pos[1][1] - FUN.c1.y0) / (FUN.c1.y1 - FUN.c1.y0)) * 0.8 + P.r * 0.2;
        P.d[3] = clamp01(1 - (P.pos[2][1] - FUN.c2.y0) / (FUN.c2.y1 - FUN.c2.y0)) * 0.8 + P.r * 0.2;
        P.d[4] = P.r;
      });
      var K = g.K = Comp.canvas(ctx, host, { w: 1210, h: 790, x: 0, y: 0, onResize: function () { draw(); } });
      function styleOf(P, s) {
        /* s = state the particle is drawn in (after the midpoint of a move) */
        if (P.fate === 0 && s >= 2) return 1;          /* EOA: hollow grey circle */
        if (P.fate === 1 && s >= 3) return 2;          /* dropped: dim box */
        if (P.fate >= 3 && s >= 4) return 4;           /* floor: dim, tinted later by tray */
        if (s >= 3) return 3;                          /* matched: bright */
        return 0;                                      /* contract candidate */
      }
      function draw() {
        var c = K.g; K.clear();
        var s = g.s, q = g.q, spread = 0.75;
        for (var j = 0; j < parts.length; j++) {
          var P = parts[j];
          if (s === 0) continue;
          var A = P.pos[s - 1], B = P.pos[s], x, y, st;
          if (A === B || (A[0] === B[0] && A[1] === B[1])) { x = B[0]; y = B[1]; st = styleOf(P, s); }
          else {
            var lt = clamp01((q * (1 + spread) - P.d[s] * spread));
            var e = s === 1 ? lt * lt : easeIO(lt);
            var ctl;
            if (s === 1) ctl = [A[0], (A[1] + B[1]) / 2];
            else if (s === 2) ctl = [FUN.n1[0] + P.jit * 30, FUN.n1[1]];
            else if (s === 3) ctl = [FUN.n2[0] + P.jit * 30, FUN.n2[1]];
            else ctl = [B[0], A[1] + 10];
            var u = 1 - e;
            x = u * u * A[0] + 2 * u * e * ctl[0] + e * e * B[0];
            y = u * u * A[1] + 2 * u * e * ctl[1] + e * e * B[1];
            st = styleOf(P, lt > 0.5 ? s : s - 1);
            if (s === 1 && lt <= 0) continue;
          }
          if (st === 1) { c.strokeStyle = C.ink3; c.lineWidth = 1.3; c.beginPath(); c.arc(x, y, 3, 0, 6.2832); c.stroke(); }
          else if (st === 2) { c.fillStyle = 'rgba(103,112,131,0.5)'; c.fillRect(x - 1.6, y - 1.6, 3.2, 3.2); }
          else if (st === 3) { c.fillStyle = C.ink; c.fillRect(x - 1.8, y - 1.8, 3.6, 3.6); }
          else if (st === 4) { c.fillStyle = P.fate === 3 ? C.allow : P.fate === 5 ? C.xfer : C.ink; c.globalAlpha = 0.75; c.fillRect(x - 1.8, y - 1.8, 3.6, 3.6); c.globalAlpha = 1; }
          else { c.fillStyle = C.ink2; c.globalAlpha = 0.85; c.fillRect(x - 1.6, y - 1.6, 3.2, 3.2); c.globalAlpha = 1; }
        }
      }
      g.draw = draw;
      draw();
      gsap.set([el.querySelector('#eoalab'), el.querySelector('#droplab')], { autoAlpha: 0 });
      gsap.set(outl, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo(g.outline.childNodes, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.08, ease: E.out }, 0.15);
      tl.set(g.outline, { autoAlpha: 1 }, 0.15);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      var durs = [0, 2.0, 2.4, 2.6, 1.3];
      g.s = i; g.q = 0; g.draw();
      tl.to(g, { q: 1, duration: durs[i], ease: 'none', onUpdate: g.draw, onComplete: g.draw }, 0);
      if (i === 1) tl.add(Comp.odometer(ctx, el.querySelector('#f1'), n0(N.cand), { duration: 2.0 }), 0.2);
      if (i === 2) {
        tl.to(g.bins.childNodes[0], { autoAlpha: 1, duration: 0.4 }, 0.6);
        tl.fromTo(el.querySelector('#eoalab'), { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: E.out }, 1.0);
        tl.add(Comp.odometer(ctx, el.querySelector('#f2'), n0(N.codeContract), { duration: 2.0 }), 0.3);
      }
      if (i === 3) {
        tl.to(g.bins.childNodes[1], { autoAlpha: 1, duration: 0.4 }, 0.6);
        tl.fromTo(el.querySelector('#droplab'), { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: E.out }, 1.4);
        tl.add(Comp.odometer(ctx, el.querySelector('#f3'), n0(N.matched), { duration: 2.2 }), 0.3);
      }
      if (i === 4) {
        tl.fromTo(g.trays, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 0);
      }
    },
    tags: function (step) { return step >= 1 && step <= 2 ? ['registered-analysis'] : []; }
  };

  /* =================================================================== s03-05
     Size of the two graphs: two illustrative "galaxies" (shapes are illustrations;
     only the ratio of dots and lines matches the real graphs, 1 : 7,800),
     odometers for nodes/edges, a race of the two edge counts, and the ratio
     measured by laying the allowance bar along the transfer bar. */
  var GAL_DIV = 7800;
  function buildGalaxy(kind, w, h, rng) {
    var nodes = [], edges = [], i, j;
    var nN = Math.round((kind === 'A' ? N.gAn : N.gTn) / GAL_DIV), nE = Math.round((kind === 'A' ? N.gAe : N.gTe) / GAL_DIV);
    var cx = w / 2, cy = h / 2;
    if (kind === 'A') {
      /* a few spender hubs, many owners around them (radial bursts) */
      var H = 14, hubs = [], wsum = 0;
      for (i = 0; i < H; i++) {
        var ang = i * 2.39996 + 0.4, rad = 30 + 165 * Math.sqrt((i + 0.5) / H);
        var wgt = 1 / Math.pow(i + 1, 1.05); wsum += wgt;
        hubs.push({ x: cx + Math.cos(ang) * rad * 1.75, y: cy + Math.sin(ang) * rad * 0.92, w: wgt });
      }
      hubs.forEach(function (hb, k) { nodes.push({ x: hb.x, y: hb.y, hub: true, r: 3 + 7 * Math.sqrt(hb.w), id: k }); });
      var pick = function () { var u = rng() * wsum; for (var k = 0; k < H; k++) { u -= hubs[k].w; if (u <= 0) return k; } return H - 1; };
      for (i = H; i < nN; i++) {
        var hk = pick(), hb2 = hubs[hk];
        var R0 = 22 + 120 * Math.sqrt(hb2.w), a2 = rng() * Math.PI * 2, rr = R0 * Math.sqrt(rng()) + 8;
        nodes.push({ x: hb2.x + Math.cos(a2) * rr * 1.3, y: hb2.y + Math.sin(a2) * rr, hub: false, r: 1.7, home: hk });
        edges.push([i, hk]);
      }
      while (edges.length < nE) {
        var o = H + Math.floor(rng() * (nN - H)), hk2 = pick();
        if (hk2 !== nodes[o].home) edges.push([o, hk2]);
      }
    } else {
      /* a denser mesh: jittered points in an ellipse, k-nearest links plus a few long links to busy nodes */
      var pts = fillShape(nN, [20, 20, w - 20, h - 20], function (x, y) { var dx = (x - cx) / (w / 2 - 20), dy = (y - cy) / (h / 2 - 20); return dx * dx + dy * dy <= 1; }, rng, 6);
      pts.forEach(function (p, k) { nodes.push({ x: p[0], y: p[1], hub: false, r: 1.7, id: k }); });
      var busy = [];
      for (i = 0; i < 18; i++) { var b = Math.floor(rng() * nN); busy.push(b); nodes[b].hub = true; nodes[b].r = 3.2 + rng() * 2.5; }
      var seen = {};
      var addE = function (a, b) { if (a === b) return; var key = a < b ? a + '_' + b : b + '_' + a; if (seen[key]) return; seen[key] = 1; edges.push([a, b]); };
      for (i = 0; i < nN; i++) {
        var best = [];
        for (j = 0; j < nN; j++) {
          if (i === j) continue;
          var dx2 = nodes[i].x - nodes[j].x, dy2 = nodes[i].y - nodes[j].y, d2 = dx2 * dx2 + dy2 * dy2;
          if (best.length < 3) { best.push([d2, j]); best.sort(function (p, q) { return p[0] - q[0]; }); }
          else if (d2 < best[2][0]) { best[2] = [d2, j]; best.sort(function (p, q) { return p[0] - q[0]; }); }
        }
        best.forEach(function (bq) { addE(i, bq[1]); });
      }
      var guard = 0;
      while (edges.length < nE && guard++ < 50000) addE(Math.floor(rng() * nN), busy[Math.floor(rng() * busy.length)]);
      if (edges.length > nE) edges.length = nE;
    }
    /* scattered start positions */
    /* scattered start positions: a soft gaussian nebula (no hard rectangular edge) */
    var gauss = function () { var u = Math.max(1e-9, rng()), v = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
    nodes.forEach(function (nd) {
      var sx, sy, guard2 = 0;
      do { sx = cx + gauss() * w * 0.19; sy = cy + gauss() * h * 0.2; } while ((sx < 8 || sx > w - 8 || sy < 8 || sy > h - 8) && guard2++ < 20);
      nd.sx = Math.max(8, Math.min(w - 8, sx)); nd.sy = Math.max(8, Math.min(h - 8, sy));
      nd.dl = rng() * 0.45;
    });
    return { nodes: nodes, edges: edges, nN: nN, nE: nE };
  }

  var slide5 = {
    id: 's03-05', title: 'Size of the two graphs', time: 35, steps: 4,
    notes: [
      'From these records I built two graphs. A node is an address, and an edge is an allowance or a transfer. For now the nodes are scattered.',
      'In the allowance graph on the left, a great many owners point to a few spender contracts. The transfer graph on the right is a denser mesh. The shapes are only illustrations; just the ratio between the numbers of nodes and edges matches the real graphs.',
      'Here are the real sizes. The allowance graph has about 6.22 million nodes and 11.21 million edges. The transfer graph has about 7.88 million nodes and 25 million edges.',
      'Let me put the edge counts side by side. Laying the allowance bar along the transfer bar twice still leaves a little over. There are 2.23 times as many transfer edges as allowance edges. The time it takes to compute a score follows the number of edges, so later this difference by itself explains the difference in computing speed.',
      'Almost every node in the allowance graph is an owner who granted an allowance. It looks like a constellation of 6,208,769 owners pointing to far fewer spenders.'
    ],
    html:
      '<h1 class="t-h1">Size of the two graphs</h1>' +
      '<p class="abs t-caption ink-3" style="left:96px;top:156px">Illustration · the shapes only explain · the ratio of node and edge counts is real (one ≈ ' + n0(GAL_DIV) + ')</p>' +
      '<div class="abs" id="galA" data-in="none" style="left:96px;top:194px;width:800px;height:400px"></div>' +
      '<div class="abs" id="galT" data-in="none" style="left:1024px;top:194px;width:800px;height:400px"></div>' +
      '<div class="abs" style="left:96px;top:606px;width:800px">' +
        '<div class="s3-gname c-allow">Allowance graph</div>' +
        '<div class="s3-gnums" data-step="2" data-in="fade"><span>nodes <b id="gAn"></b></span><span>edges <b id="gAe"></b></span></div></div>' +
      '<div class="abs" style="left:1024px;top:606px;width:800px">' +
        '<div class="s3-gname c-xfer">Transfer graph</div>' +
        '<div class="s3-gnums" data-step="2" data-in="fade"><span>nodes <b id="gTn"></b></span><span>edges <b id="gTe"></b></span></div></div>' +
      '<div class="abs" id="race" data-in="none" style="left:96px;top:742px;width:1728px;height:150px">' +
        '<div class="s3-rrow"><span class="s3-rlab c-allow">Allowance edges</span><div class="s3-rbar" id="rbA" style="background:var(--c-allow)"></div><span class="s3-rval" id="rvA"></span></div>' +
        '<div class="s3-rrow" style="margin-top:22px"><span class="s3-rlab c-xfer">Transfer edges</span><div class="s3-rbar" id="rbT" style="background:var(--c-xfer)"></div><span class="s3-rval" id="rvT"></span></div>' +
        '<div class="s3-ghostbar" id="gh1"></div><div class="s3-ghostbar" id="gh2"></div>' +
        '<div class="s3-rtick" id="tk1"></div><div class="s3-rtickl" id="tl1">1×</div>' +
        '<div class="s3-rtick" id="tk2"></div><div class="s3-rtickl" id="tl2">2×</div>' +
        '<div class="s3-ratio" id="ratio">Transfer edges are [[' + N.edgeRatio.toFixed(2) + '×]]</div>' +
      '</div>' +
      '<p class="abs t-body-l" style="left:96px;top:924px" data-step="4" data-in="words">Allowance graph = a constellation of ' + n0(N.owners) + ' owners pointing to far fewer spenders</p>',
    build: function (el, ctx) {
      var g = ctx.g = { p: 0, tw: -1 };
      var rng = ctx.rng(42);
      g.A = buildGalaxy('A', 800, 400, rng);
      g.T = buildGalaxy('T', 800, 400, rng);
      /* edges in chunks of 150 segments (many small paths rasterise much faster than one huge one) */
      function strokeEdges(c, G, col, alpha, final) {
        var nodes = G.nodes, E2 = G.edges;
        c.strokeStyle = col; c.globalAlpha = alpha; c.lineWidth = 1;
        for (var s0 = 0; s0 < E2.length; s0 += 150) {
          c.beginPath();
          for (var k = s0, kk = Math.min(E2.length, s0 + 150); k < kk; k++) {
            var a = nodes[E2[k][0]], b = nodes[E2[k][1]];
            if (final) { c.moveTo(a.x, a.y); c.lineTo(b.x, b.y); } else { c.moveTo(a.cx, a.cy); c.lineTo(b.cx, b.cy); }
          }
          c.stroke();
        }
        c.globalAlpha = 1;
      }
      function drawGal(K, G, col, p, twinkle) {
        var c = K.g; K.clear();
        var nodes = G.nodes, i;
        for (i = 0; i < nodes.length; i++) {
          var nd = nodes[i], lt = clamp01((p * 1.45 - nd.dl) / 1.0), e = easeIO(lt);
          nd.cx = lerp(nd.sx, nd.x, e); nd.cy = lerp(nd.sy, nd.y, e);
        }
        var la = Math.pow(clamp01((p - 0.55) / 0.45), 2);
        if (p >= 1) {
          /* settled: the edge layer is drawn once into an offscreen canvas and reused (twinkle frames,
             resizes); stroking ~4,600 segments every frame is slow in software-rendered canvases */
          if (!G.cache || G.cacheRatio !== K.ratio) {
            var cv = document.createElement('canvas');
            cv.width = Math.round(800 * K.ratio); cv.height = Math.round(400 * K.ratio);
            var cc = cv.getContext('2d'); cc.setTransform(K.ratio, 0, 0, K.ratio, 0, 0);
            strokeEdges(cc, G, col, 0.085, true);
            G.cache = cv; G.cacheRatio = K.ratio;
          }
          c.drawImage(G.cache, 0, 0, 800, 400);
        } else if (la > 0) strokeEdges(c, G, col, 0.085 * la, false);
        for (i = 0; i < nodes.length; i++) {
          var n2 = nodes[i], al = n2.hub ? 0.95 : 0.55 + 0.3 * clamp01(p);
          if (twinkle >= 0 && !n2.hub) {
            var wf = twinkle * 1.3 - 0.15, dxw = n2.x / 800 - wf;
            al = Math.min(1, al + 0.9 * Math.exp(-dxw * dxw / 0.004));
          }
          c.globalAlpha = al; c.fillStyle = col;
          if (n2.hub && p > 0.5) { c.globalAlpha = 0.18 * clamp01((p - 0.5) * 2); c.beginPath(); c.arc(n2.cx, n2.cy, n2.r * 2.6, 0, 6.2832); c.fill(); c.globalAlpha = al; }
          c.beginPath(); c.arc(n2.cx, n2.cy, n2.hub ? lerp(1.7, n2.r, clamp01(p)) : n2.r, 0, 6.2832); c.fill();
        }
        c.globalAlpha = 1;
      }
      g.draw = function () { drawGal(g.KA, g.A, C.allow, g.p, g.tw); drawGal(g.KT, g.T, C.xfer, g.p, -1); };
      g.KA = Comp.canvas(ctx, el.querySelector('#galA'), { w: 800, h: 400, onResize: function () { g.draw(); } });
      g.KT = Comp.canvas(ctx, el.querySelector('#galT'), { w: 800, h: 400, onResize: function () { g.draw(); } });
      g.draw();
      /* race geometry */
      var W0 = 200, WMAX = 1180, fA = N.gAe / N.gTe;
      g.race = { W0: W0, WMAX: WMAX, fA: fA, wA: WMAX * fA };
      var q = function (s) { return el.querySelector(s); };
      q('#rbA').style.width = g.race.wA + 'px'; q('#rbT').style.width = WMAX + 'px';
      q('#rvA').style.left = (W0 + g.race.wA + 18) + 'px'; q('#rvT').style.left = (W0 + WMAX + 18) + 'px';
      ['#gh1', '#gh2'].forEach(function (s, k) { var e = q(s); e.style.width = (g.race.wA - 4) + 'px'; e.style.left = (W0 + k * g.race.wA + 2) + 'px'; e.style.top = (56 + 22 + 2) + 'px'; });
      ['1', '2'].forEach(function (k) {
        var x = W0 + (+k) * g.race.wA;
        q('#tk' + k).style.left = (x - 1) + 'px'; q('#tk' + k).style.top = (56 + 22) + 'px';
        q('#tl' + k).style.left = x + 'px'; q('#tl' + k).style.top = (56 + 22 + 52) + 'px';
      });
      var ratio = q('#ratio'); ratio.style.right = (1728 - (W0 + WMAX)) + 'px'; ratio.style.top = '4px';
      gsap.set(q('#race'), { autoAlpha: 0 });
      gsap.set([q('#rbA'), q('#rbT')], { scaleX: 0 });
      gsap.set(['#gh1', '#gh2', '#tk1', '#tk2', '#tl1', '#tl2', '#ratio'].map(q), { autoAlpha: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) tl.to(g, { p: 1, duration: 1.6, ease: 'none', onUpdate: g.draw, onComplete: g.draw }, 0);
      if (i === 2) {
        tl.add(Comp.odometer(ctx, el.querySelector('#gAn'), n0(N.gAn), { duration: 1.8 }), 0.1);
        tl.add(Comp.odometer(ctx, el.querySelector('#gAe'), n0(N.gAe), { duration: 1.8 }), 0.25);
        tl.add(Comp.odometer(ctx, el.querySelector('#gTn'), n0(N.gTn), { duration: 1.8 }), 0.4);
        tl.add(Comp.odometer(ctx, el.querySelector('#gTe'), n0(N.gTe), { duration: 1.8 }), 0.55);
      }
      if (i === 3) {
        var R = g.race, q = function (s) { return el.querySelector(s); }, vA = q('#rvA'), vT = q('#rvT');
        var DT = 2.4, DA = DT * R.fA;         /* same speed: the shorter bar stops first */
        tl.set(q('#race'), { autoAlpha: 1 }, 0);
        tl.fromTo(q('#rbT'), { scaleX: 0 }, { scaleX: 1, duration: DT, ease: 'none' }, 0);
        tl.fromTo(q('#rbA'), { scaleX: 0 }, { scaleX: 1, duration: DA, ease: 'none' }, 0);
        tl.add(ctx.count(vA, 0, N.gAe, { duration: DA, ease: 'none', final: n0(N.gAe) }), 0);
        tl.add(ctx.count(vT, 0, N.gTe, { duration: DT, ease: 'none', final: n0(N.gTe) }), 0);
        /* measure: lay the allowance bar along the transfer bar, twice */
        tl.fromTo(q('#gh1'), { autoAlpha: 0, y: -70 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.io }, DT + 0.3);
        tl.fromTo([q('#tk1'), q('#tl1')], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, DT + 0.85);
        tl.fromTo(q('#gh2'), { autoAlpha: 0, x: -R.wA }, { autoAlpha: 1, x: 0, duration: 0.6, ease: E.io }, DT + 1.1);
        tl.fromTo([q('#tk2'), q('#tl2')], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, DT + 1.65);
        tl.fromTo(q('#ratio'), { autoAlpha: 0, y: -24 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.stamp }, DT + 2.0);
        var hl = q('#ratio .hl');
        if (hl) tl.fromTo(hl, { '--hl-x': 0 }, { '--hl-x': 1, duration: 0.5, ease: 'power2.inOut' }, DT + 2.3);
      }
      if (i === 4) {
        g.tw = 0;
        tl.to(g, { tw: 1, duration: 1.6, ease: 'none', onUpdate: g.draw, onComplete: function () { g.tw = -1; g.draw(); } }, 0.6);
      }
    },
    tags: ['example']
  };

  /* =================================================================== s03-06
     15,107 contracts in 3D: x = log10(1 + in-approve degree), z = log10(1 +
     transfer in-degree), y = log10(EndorseRank); zero scores rest on the floor
     plate. Colour = a two-stop ramp dark slate → amber on the EndorseRank
     percentile, then dark slate → sky on the AWP percentile, drawn with normal
     (not additive) blending so the mixed brightness along the ridge stays
     visible in the dense core. No address is shown anywhere. Kendall's τ is
     only named here (it is taught in s07); no interval is shown. */
  var slide6 = {
    id: 's03-06', title: '15,107 contracts in 3D', time: 45, steps: 3,
    notes: [
      'Now let me put all 15,107 contracts of the matched cohort on one screen. One dot is one contract. Right now every dot is lying on the floor.',
      'Across is the number of distinct owners that approved the contract, depth is the number of distinct addresses that sent it transfers, and height is the EndorseRank score. EndorseRank is the "score that walks along allowances" I mentioned in section 01. We will build it step by step in sections 04 to 06. All three axes are on log scales, so very large and very small values can be seen together. One tick up the height means the score is 100 times larger. The contracts with the fewest approvals rise to their height first, and the rest follow in order. The color of a dot is its EndorseRank rank: grey when the rank is low, bright amber when it is high. The 535 contracts with an EndorseRank of 0 stay on the floor plate. That is the 523 outside the allowance graph plus 12 whose amounts are so small that their weight becomes 0.',
      'Seen from the side, EndorseRank rises almost in a single line with the number of approving owners. The color also changes evenly, from grey at the bottom to bright amber at the top. There is a number that measures how close this is to a single line, called Kendall\'s tau. We will learn it in section 07 by counting pairs. This is an intended-construct check, which asks whether the score measures what it was meant to measure. It is not a validation.',
      'Now I color the same dots by the rank of AWP, the transfer-side score: grey when the rank is low, bright sky blue when it is high. If the two scores ordered the contracts the same way, the color would brighten evenly from bottom to top. Instead, bright and dark dots are mixed at every height of the ridge. This means the two scores order the contracts differently. 2,672 contracts have an AWP of 0. That is the 2,670 outside the transfer graph plus 2 whose amounts are so small that their weight becomes 0. These two scenes are a preview of today\'s results. You can also drag the scene to rotate it.'
    ],
    html:
      '<h1 class="t-h1">One dot = one [[contract]]</h1>' +
      '<div class="abs s3-legend3d" style="left:96px;top:162px">' +
        '<span><i style="background:var(--c-allow)"></i>across · approving owners</span>' +
        '<span><i style="background:var(--c-xfer)"></i>depth · transfer senders</span>' +
        '<span><i style="background:var(--ink)"></i>height · EndorseRank score</span>' +
        '<span class="ink-3">all log scales</span></div>' +
      '<div class="abs s3-colleg" style="left:1180px;top:162px;width:644px;height:34px">' +
        '<span data-step-out="3"><i style="background:linear-gradient(90deg,#363D4B,var(--c-allow))"></i>color · EndorseRank rank (low → high)</span>' +
        '<span data-step="3" data-in="fade"><i style="background:linear-gradient(90deg,#363D4B,var(--c-xfer))"></i>color · AWP rank (low → high)</span></div>' +
      '<div class="abs s3-three-fade" id="three" data-in="none" style="left:0;top:204px;width:1920px;height:676px"></div>' +
      '<div class="abs s3-cap3d" style="left:96px;top:872px;width:1300px;height:52px">' +
        '<p class="t-body-l" data-step="2" data-step-out="3" data-in="words">EndorseRank rises almost in one line with the approving owners</p>' +
        '<p class="t-body-l" data-step="3" data-in="words">Colored by AWP, the line breaks up: the two orders differ</p></div>' +
      '<div class="abs" style="left:96px;top:930px;display:flex;gap:16px;align-items:center" data-step="2" data-step-out="3">' +
        '<span class="t-caption ink-2">The number that measures how close to one line (tau) comes in 07</span>' + Deck.tagHTML('construct') + '</div>' +
      '<div class="abs t-caption ink-2" style="left:96px;top:930px" data-step="3">More in the results (08) · drag to rotate</div>' +
      '<div class="abs s3-zero t-caption ink-3 tnum" style="left:1100px;top:898px;width:724px;height:64px">' +
        '<div data-step="1" data-step-out="3">EndorseRank: <b>' + n0(TIES.zeros) + ' zero scores</b> on the floor · ' + n0(TIES.distinct) + ' distinct scores<br>' +
          n0(TIES.zeros) + ' = ' + n0(N.outA) + ' outside the allowance graph + ' + n0(N.tinyA) + ' with amounts too small to weigh</div>' +
        '<div data-step="3">AWP: <b>' + n0(TIES_AWP.zeros) + ' zero scores</b> · ' + n0(TIES_AWP.distinct) + ' distinct scores<br>' +
          n0(TIES_AWP.zeros) + ' = ' + n0(N.outT) + ' outside the transfer graph + ' + n0(N.tinyT) + ' with amounts too small to weigh</div></div>',
    build: function (el, ctx) {
      var K = Comp.data.contracts(); if (!K) return;
      var n = K.n, i;
      var appr = K.raw.in_approve_degree, deg = K.raw.in_degree, ler = K.log10.endorserank;
      var pER = K.pct.endorserank, pAWP = K.pct.awp;
      var mxA = 0, mxZ = 0, lmin = Infinity, lmax = -Infinity;
      var xa = new Float32Array(n), zt = new Float32Array(n);
      for (i = 0; i < n; i++) {
        xa[i] = Math.log10(1 + appr[i]); zt[i] = Math.log10(1 + deg[i]);
        if (xa[i] > mxA) mxA = xa[i]; if (zt[i] > mxZ) mxZ = zt[i];
        var l = ler[i]; if (l === l) { if (l < lmin) lmin = l; if (l > lmax) lmax = l; }
      }
      var SPAN = 7, SX = SPAN / mxA, SZ = SPAN / mxZ, HY = 4.6, FLOOR = -0.42;
      var LY0 = Math.floor(lmin), LY1 = Math.ceil(lmax);          /* -8 … -1 */
      function yOf(l) { return (l - LY0) / (LY1 - LY0) * HY; }
      var flat = new Float32Array(n * 3), up = new Float32Array(n * 3), cER = new Float32Array(n * 3), cAWP = new Float32Array(n * 3);
      /* low end of both ramps: a dark slate, so low and high ranks differ clearly in brightness */
      var ca = Comp.rgb(C.allow), cx = Comp.rgb(C.xfer), grey = Comp.rgb('#363D4B');
      for (i = 0; i < n; i++) {
        var X = xa[i] * SX - SPAN / 2, Z = zt[i] * SZ - SPAN / 2, l2 = ler[i];
        flat[i * 3] = X; flat[i * 3 + 1] = FLOOR + 0.03; flat[i * 3 + 2] = Z;
        up[i * 3] = X; up[i * 3 + 1] = l2 === l2 ? yOf(l2) : FLOOR + 0.03; up[i * 3 + 2] = Z;
        /* two-stop ramps: dark slate (low rank) → full hue (high rank); zero scores darker still */
        var zero1 = !(l2 === l2), zero2 = K.log10.awp ? !(K.log10.awp[i] === K.log10.awp[i]) : false;
        for (var c3 = 0; c3 < 3; c3++) {
          cER[i * 3 + c3] = zero1 ? grey[c3] * 0.8 : lerp(grey[c3], ca[c3], pER[i]);
          cAWP[i * 3 + c3] = zero2 ? grey[c3] * 0.8 : lerp(grey[c3], cx[c3], pAWP[i]);
        }
      }
      /* rising order: by in-approve degree (value order stagger) */
      var order = new Array(n); for (i = 0; i < n; i++) order[i] = i;
      order.sort(function (a, b) { return xa[a] - xa[b]; });
      var delays = new Float32Array(n); for (i = 0; i < n; i++) delays[order[i]] = i / (n - 1);
      var Tz = ctx.three(el.querySelector('#three'), { fov: 30, camera: { theta: 0.72, phi: 1.12, radius: 46, target: [0.5, 1.75, 0] }, autoRotate: 0.05, minRadius: 8, maxRadius: 80 });
      var g = ctx.g = { T: Tz, up: up, flat: flat, cER: cER, cAWP: cAWP, delays: delays };
      if (Tz.failed) return;
      Comp.floor(ctx, Tz, { size: 8, y: FLOOR, divisions: 8, opacity: 0.22 });
      var O = [-SPAN / 2 - 0.3, FLOOR, -SPAN / 2 - 0.3];
      Comp.axes3d(ctx, Tz, { origin: O, length: [SPAN + 0.9, HY + 0.9, SPAN + 0.9], colors: [C.allow, C.ink, C.xfer], headRadius: 0.07, headLength: 0.24 });
      g.axLab = [
        Tz.label('Approving owners (log)', [O[0] + SPAN + 1.0, O[1], O[2]], { className: 's3-ax3d', anchor: 'left', dx: 14 }),
        Tz.label('EndorseRank score (log · one tick = 100×)', [O[0], O[1] + HY + 0.9, O[2]], { className: 's3-ax3d', anchor: 'left', dx: 18, dy: 6 }),
        Tz.label('Transfer senders (log)', [O[0], O[1], O[2] + SPAN + 1.0], { className: 's3-ax3d', anchor: 'right', dx: -14 })
      ];
      g.axLab[0].el.style.color = C.allow; g.axLab[1].el.style.color = C.ink; g.axLab[2].el.style.color = C.xfer;
      /* tick labels (values, never addresses) */
      g.ticks = []; g.zTicks = [];
      [[10, '10'], [100, '100'], [1000, '1,000'], [10000, '10,000'], [100000, '100,000']].forEach(function (tv) {
        var lx = Math.log10(1 + tv[0]) * SX - SPAN / 2, lz = Math.log10(1 + tv[0]) * SZ - SPAN / 2;
        if (lx <= SPAN / 2) g.ticks.push(Tz.label(tv[1], [lx, FLOOR, O[2] - 0.35], { className: 's3-tick3d' }));
        if (lz <= SPAN / 2) { var zl = Tz.label(tv[1], [O[0] - 0.35, FLOOR, lz], { className: 's3-tick3d' }); g.ticks.push(zl); g.zTicks.push(zl); }
      });
      /* height ticks as plain fractions, not negative powers of ten (10^-7 = 1/10,000,000); one tick = 100x */
      var FRAC = { '-1': '1/10', '-2': '1/100', '-3': '1/1,000', '-4': '1/10,000', '-5': '1/100,000', '-6': '1/1,000,000', '-7': '1/10,000,000', '-8': '1/100,000,000', '-9': '1/1,000,000,000' };
      for (var e = LY0 + 1; e <= LY1; e += 2) g.ticks.push(Tz.label(FRAC[String(e)] || ('10^' + e), [O[0] - 0.25, yOf(e), O[2]], { className: 's3-tick3d', anchor: 'right' }));
      g.cloud = Comp.cloud(ctx, Tz, { positions: flat, colors: cER, size: 3, opacity: 0.85, additive: false });
      /* labels that project into the caption band at the bottom of the viewport fade out (the view
         auto-rotates and can be dragged, so this is checked every frame) */
      var allLabs = g.axLab.concat(g.ticks);
      allLabs.forEach(function (L) { L.el.innerHTML = '<span class="s3-lin">' + L.el.innerHTML + '</span>'; });
      Tz.onFrame(function () {
        var lim = Tz.height - 70;
        for (var k = 0; k < allLabs.length; k++) {
          var pr = Tz.project(allLabs[k].pos), o = clamp01((lim - pr.y) / 60), inn = allLabs[k].el.firstChild;
          if (inn && inn.__o !== o) { inn.style.opacity = o.toFixed(2); inn.__o = o; }
        }
      });
      g.axLab.concat(g.ticks).forEach(function (L) { L.el.style.opacity = '0'; });
    },
    enter: function (el, ctx) {
      var g = ctx.g; if (!g || !g.T || g.T.failed) return;
      var tl = ctx.tl();
      tl.add(g.T.cameraTo({ radius: 17.6 }, { duration: 1.8, ease: E.io }), 0);
      var labs = g.axLab.concat(g.ticks).map(function (L) { return L.el; });
      tl.to(labs, { opacity: 1, duration: 0.6, stagger: 0.02 }, 1.2);
    },
    step: function (el, i, ctx) {
      var g = ctx.g; if (!g || !g.T || g.T.failed) return;
      var tl = ctx.tl(), Tz = g.T;
      if (i === 1) tl.add(g.cloud.morph(g.up, { duration: 1.6, delays: g.delays, spread: 1.0, ease: 'power3.out' }), 0);
      if (i === 2) {
        Tz.orbit.autoRotate = 0;
        tl.add(Tz.cameraTo({ theta: 0, phi: Math.PI / 2 - 0.06, radius: 14.2, target: [0.3, 2.05, 0] }, { duration: 1.8 }), 0);
        tl.to([g.axLab[2].el].concat(g.zTicks.map(function (L) { return L.el; })), { opacity: 0, duration: 0.4 }, 0);
      }
      if (i === 3) {
        tl.add(g.cloud.recolor(g.cAWP, { duration: 0.9, delays: g.delays, spread: 0.6 }), 0);
        tl.call(function () { if (!ctx.reduced) Tz.orbit.autoRotate = 0.05; }, null, 1.6);
        tl.to([g.axLab[2].el].concat(g.zTicks.map(function (L) { return L.el; })), { opacity: 1, duration: 0.5 }, 1.6);
      }
    },
    tags: function (step) { return step >= 2 ? ['construct'] : []; }
  };

  Deck.section({ id: 's03-data', title: 'The data', slides: [slide1, slide2, slide3, slide4, slide5, slide6] });
})();
