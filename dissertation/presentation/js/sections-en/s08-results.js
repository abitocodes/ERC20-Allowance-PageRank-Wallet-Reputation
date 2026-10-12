/* =========================================================================
   s08-results — Results, English edition (STORYBOARD.md §2, s08-01 … s08-08)

   s08-01  Same window (RQ2)        3 × 3 board (score × family); own-family cells light up with a
                                    mirror; swapped cells and their paired differences; C-PR slides into
                                    the empty middle row; an expandable popover for λ = 1, λ = 0, S-PR
   s08-02  Two different orders     the two rows of s08-01 burst into 15,107 particles (three.js) that
           (RQ1)                    gather into the λ = 1 cloud of s06-04; the camera rises and the points
                                    slide into a rank–rank scatter (EndorseRank × AWP percentile); diagonal,
                                    τ_b count-up, 30 flashed pairs (illustration) and a gauge stopping at
                                    41.2 %; the two zero blocks
   s08-03  Out-of-window test       the calendar of s03-01 returns; freeze pin + frost; label window
           (RQ4 design)             plays (month watermark), sparse new arrows into spender boxes; waffle
                                    (one dot = 10 spenders) with the gained-approval share; W1 with a lock
   s08-04  Transfer side            locked board (data-shared "s8-board", same axes on s08-04 … s08-06):
   s08-05  Allowance side           left τ panel, right paired-difference panel with a dashed zero line;
   s08-06  Restart rule only        ghost markers = registered analysis; "rich get richer" loop; restart
                                    rain; a hollow "Hypothesis" tag drawn slowly (not a verdict stamp)
   s08-07  Closed form              small world (thesis Ch. 2) + 6-line derivation of
                                    r_v = c(1 + d δ(v)); pie example δ = 1 + ½ + ¼ = 1.75 vs count 3
   s08-08  How well it fits         waffle of 14,406 spenders (one dot = 10), counters, then the summary
                                    board of the four raw-degree contrasts with registered ghosts

   Numbers and sources (R = revised digest experiments/data/3-published-results-for-thesis/
   revised-usd/results_digest.md = the thesis's main analysis; G = registered digest results_digest.md)
     s08-01  families τ_b [95%]           R§2 families.{endorserank,awp,cpr_l50,cpr_l100,cpr_l0,spr}.*
             +0.392 [0.380, 0.405]         R§3 contrasts[14] (EndorseRank − AWP, allowance family)
             +0.414 [0.401, 0.427]         R§3 contrasts[13] (AWP − EndorseRank, transfer family)
     s08-02  0.174 [0.163, 0.185]          R§3 inter_method.endorserank_vs_awp; isolated 0.174 (…isolated)
             114,103,171 · 96.7 % · 41.2 % R§3 concordance.pairs / share_ordered_by_both / discordant_share
             535 · 2,672                   R§4 ties.endorserank.zeros / ties.awp.zeros
             0.217 [0.209, 0.225]          G§3 inter_method.endorserank_vs_awp (registered analysis)
             points: DECK_DATA.contracts pct.endorserank / pct.awp (mid-rank percentiles, all 15,107)
     s08-03  17,050 · 2,070 · 1,695        R§6 spenders / gained_new_approvals / gained_new_senders
             both labels 1,173 (W0) / 1,023 (W1): counted from revised-usd/{holdout-w0,window-w1}/spender_scores.part000.parquet
             (12.1 %, 9.9 % = quotients, as in thesis Ch. 4); 18,152 · 1,616 · 1,533  R§7
     s08-04  0.346 · 0.303 · +0.043        R§6 taus.awp / taus.t1_in_degree (new senders) / contrasts_after[4]
             0.330 · 0.308 · +0.022        R§7 spender_taus.awp / .in_degree / endorserank_results.awp_minus_degree_send
             14,094 · +0.056               R§6 receiving.n / receiving.contrasts[1]
             ghosts +0.038, +0.020         G§6 contrasts_after[4], G§7 endorserank_results.awp_minus_degree_send
     s08-05  0.250 · 0.231 · −0.019        R§6 taus.t1_in_approve_degree / taus.endorserank / contrasts_after[3]
             0.268 · 0.234 · −0.034        R§7 spender_taus.* / endorserank_results.endorserank_minus_degree_appr
             +0.035, +0.065                R§7 supplementary w0/w1.er_minus_awp_appr
             −0.013                        R§6 receiving.contrasts[0];  ghosts −0.011, −0.029 (G)
     s08-06  0.308 · 0.295                 R§6 / R§7 taus.endorserank_activity (new approval pairs)
             +0.059, +0.027                R§7 supplementary w0/w1.er_activity_minus_degree_appr
             0.585 → 0.426 [0.418, 0.435]  R§2 families.endorserank(.allowance) / endorserank_activity
     s08-07  0.1375, 0.2154, 0.1765, 0.4706  thesis Ch. 2 worked example (DECK_DATA.params.worked_example),
             re-derived with the closed form (Ch. 5, Eq. closed-form); c = 7.64 × 10⁻⁸  R§5 common_value_c
             pie 1, ½, ¼ → 1.75 = example
     s08-08  14,406 · 12,039 · 100 % · 26.4 % · 87.9 %   R§5 closed_form.* (same window)
             2,367 = 14,406 − 12,039 (calculated); W0 17,032 · 73.7 %  R§5 W0 closed_form.*
   Status tags: construct (s08-01), post hoc (every raw-degree / variant contrast), registered-analysis
   (grey hollow ghosts), example / thesis-example where a value is illustrative.
   No address or contract name is ever shown.
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt;
  var DATA = window.DECK_DATA || {};
  var NS = 'http://www.w3.org/2000/svg';
  var PRM = DATA.params || {};
  var DAMP = ((PRM.pagerank || {}).d) || 0.85;

  /* ------------------------------------------------------------ helpers */
  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function txt(parent, x, y, s, attrs) {
    var a = { x: x, y: y }; for (var k in attrs) a[k] = attrs[k];
    var t = svgEl('text', a, parent); t.textContent = s; return t;
  }
  function h(tag, cls, parent, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; }
  function q(el, sel) { return el.querySelector(sel); }
  function qa(el, sel) { return Array.prototype.slice.call(el.querySelectorAll(sel)); }
  function nums(s) { return String(s).replace(/−/g, '-').match(/-?\d+(?:\.\d+)?/g).map(Number); }
  function iv(s) { var n = nums(s); return { est: n[0], lo: n[1], hi: n[2], s: s }; }
  function estOf(s) { var i = s.indexOf(' ['); return i < 0 ? s : s.slice(0, i); }
  function ciOf(s) { var i = s.indexOf('['); return i < 0 ? '' : s.slice(i); }
  function mfmt(v, d) { return fmt(v, d).replace(/^-/, '−'); }
  function sfmt(v, d) { return (v > 0 ? '+' : '') + mfmt(v, d); }
  function dur(ctx, d) { return ctx.reduced ? 0.01 : d; }
  function pill(t) { return Deck.tagHTML(t); }
  function settleShared(ctx, el, key, delay) {
    var had = !!(ctx.prev && ctx.prev.rect && ctx.prev.rect(key));
    if (!had && !ctx.instant && !ctx.reduced) ctx.gsap.fromTo(el, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: delay != null ? delay : 0.15 });
    return had;
  }
  function rgba(hex, a) { var c = Comp.rgb(hex); return 'rgba(' + Math.round(c[0] * 255) + ',' + Math.round(c[1] * 255) + ',' + Math.round(c[2] * 255) + ',' + a + ')'; }
  function toLin(c) { return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  var NOT_PLANNED = { key: 'not-planned', en: 'Not fixed in advance', icon: 'eye' };
  var H1TAG = { key: 'h1', en: 'Largely expected by construction (H1)', icon: 'mirror' };
  var LOCK_SVG = '<svg viewBox="0 0 20 20" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="9" width="12" height="8.5" rx="2"/><path d="M7 9V6.5a3 3 0 0 1 6 0V9"/></svg>';

  /* ------------------------------------------------------------ styles */
  var CSS = [
    /* s08-01 */
    '.s8-colhd{position:absolute;top:184px;width:460px}',
    '.s8-colhd .k{font-size:30px;line-height:38px;font-weight:700}',
    '.s8-colhd .v{font-size:19px;line-height:26px;color:var(--ink-3)}',
    '.s8-row{position:absolute;left:96px;width:1724px;height:150px}',
    '.s8-rl{position:absolute;left:0;top:0;width:290px;height:150px;display:flex;flex-direction:column;justify-content:center}',
    '.s8-rl .k{font-size:32px;line-height:40px;font-weight:800;letter-spacing:-.02em}',
    '.s8-rl .v{font-size:20px;line-height:28px;color:var(--ink-3);margin-top:4px}',
    '.s8-cell{position:absolute;top:0;width:460px;height:150px;border-radius:18px;border:1.5px solid var(--line);background:var(--bg-2);overflow:hidden}',
    '.s8-cell .tint{position:absolute;inset:0;opacity:0}',
    '.s8-cell .num{position:absolute;left:24px;top:12px;font-size:48px;line-height:56px;font-weight:800;letter-spacing:-.02em;color:var(--ink-2)}',
    '.s8-cell .ci{position:absolute;left:26px;top:70px;font-size:20px;line-height:26px;color:var(--ink-3)}',
    '.s8-cell svg.mini{position:absolute;left:0;top:94px;overflow:visible}',
    '.s8-cell .mir{position:absolute;right:16px;top:14px;width:40px;height:40px}',
    '.s8-cell .mir svg{width:40px;height:40px}',
    '.s8-slot{position:absolute;left:400px;top:440px;width:1420px;height:150px;border-radius:18px;border:1.5px dashed #2C3547;display:flex;align-items:center;justify-content:center;color:var(--ink-3);font-size:24px}',
    '.s8-diff{position:absolute;top:426px;width:300px;height:178px}',
    '.s8-diff svg{position:absolute;left:0;top:0;overflow:visible}',
    '.s8-diff .lab{position:absolute;left:150px;top:62px;transform:translateX(-50%);white-space:nowrap;padding:6px 14px;border-radius:14px;background:var(--bg-3);border:1px solid #39435A;font-size:24px;line-height:30px;font-weight:700;color:var(--ink)}',
    '.s8-diff .lab small{font-size:18px;font-weight:500;color:var(--ink-3);margin-left:6px}',
    '.s8-cap{font-size:30px;line-height:42px;font-weight:600;color:var(--ink)}',
    '.s8-cap .pill{vertical-align:4px;margin-left:12px}',
    '.s8-small{font-size:21px;line-height:30px;color:var(--ink-2)}',
    '.s8-small .katex{font-size:24px}',
    '.s8-note{font-size:24px;line-height:34px;color:var(--ink-2);display:flex;gap:14px;align-items:center}',
    '.s8-more{position:absolute;left:1520px;top:802px;width:300px;height:44px;border-radius:22px;border:1px solid #39435A;background:var(--bg-2);color:var(--ink-2);font:600 19px/42px var(--font-sans);cursor:pointer;text-align:center;padding:0}',
    '.s8-more:hover{border-color:var(--ink-2);color:var(--ink)}',
    '.s8-pop{position:absolute;left:880px;top:612px;width:940px;padding:18px 24px;border-radius:20px;background:rgba(16,21,31,.98);border:1px solid #39435A;box-shadow:0 20px 60px rgba(0,0,0,.55);z-index:5}',
    '.s8-pop table{border-collapse:collapse;width:100%;font-size:22px;line-height:30px}',
    '.s8-pop th{font-size:18px;font-weight:600;color:var(--ink-3);text-align:right;padding:4px 10px;border-bottom:1px solid var(--line)}',
    '.s8-pop th:first-child,.s8-pop td:first-child{text-align:left}',
    '.s8-pop td{padding:6px 10px;text-align:right;font-variant-numeric:tabular-nums;border-bottom:1px solid rgba(35,43,59,.8)}',
    '.s8-pop .hd{font-size:18px;color:var(--ink-3);margin-bottom:6px}',
    /* s08-02 */
    '.s8-ov{pointer-events:none;overflow:visible}',
    '.s8-ov text{font-family:var(--font-sans)}',
    '.s8-p2 .lg{font-size:21px;line-height:31px;color:var(--ink-2)}',
    '.s8-p2 .lg i{display:inline-block;width:14px;height:14px;border-radius:7px;margin-right:10px;vertical-align:-1px}',
    '.s8-p2 .k{font-size:22px;line-height:30px;color:var(--ink-2)}',
    '.s8-p2 .tau{font-size:84px;line-height:88px;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums}',
    '.s8-p2 .ci{font-size:26px;line-height:34px;color:var(--ink-2);font-variant-numeric:tabular-nums}',
    '.s8-p2 .ln{font-size:24px;line-height:36px;color:var(--ink-2)}',
    '.s8-p2 .ln b{color:var(--ink);font-variant-numeric:tabular-nums;font-weight:700}',
    '.s8-p2 .big{font-size:52px;line-height:60px;font-weight:800;color:var(--c-hi);font-variant-numeric:tabular-nums}',
    '.s8-gauge{position:relative;height:16px;border-radius:8px;background:var(--line);overflow:hidden;margin-top:8px}',
    '.s8-gauge b{position:absolute;left:0;top:0;bottom:0;width:0;border-radius:8px;background:var(--c-hi)}',
    '.s8-p2 .concl{font-size:32px;line-height:44px;font-weight:700;color:var(--ink)}',
    '.s8-p2 .gh{display:flex;gap:12px;align-items:center;font-size:21px;color:var(--ink-3)}',
    /* s08-03 */
    '.s8-info{font-size:26px;line-height:40px;font-weight:600;color:var(--ink);display:flex;gap:12px;align-items:center;white-space:nowrap}',
    '.s8-info .mono{font-size:24px;color:var(--ink-2)}',
    '.s8-defs .lk{display:inline-block;vertical-align:-4px;margin-right:8px;color:var(--ink-2)}',
    '.s8-info svg{color:var(--ink-2)}',
    '.s8-wt{font-size:24px;line-height:34px;font-weight:600;color:var(--ink)}',
    '.s8-wt small{font-size:19px;font-weight:500;color:var(--ink-3);margin-left:10px}',
    '.s8-wc{font-size:22px;line-height:32px;color:var(--ink-2);display:flex;gap:26px}',
    '.s8-wc b{font-variant-numeric:tabular-nums;color:var(--ink)}',
    '.s8-wc i{display:inline-block;width:14px;height:14px;border-radius:7px;margin-right:8px;vertical-align:-1px}',
    '.s8-defs{font-size:22px;line-height:34px;color:var(--ink-2)}',
    '.s8-defs b{color:var(--ink);font-weight:700}',
    '.s8-month{position:absolute;font-family:var(--font-mono);font-size:64px;line-height:64px;font-weight:700;color:var(--ink);opacity:.22;letter-spacing:0}',
    /* board s08-04 … s08-06 */
    '.s8-board text,.s8-bars text,.s8-ex text{font-family:var(--font-sans)}',
    '.s8-concl{font-size:32px;line-height:44px;font-weight:700;color:var(--ink)}',
    '.s8-reason{font-size:26px;line-height:38px;color:var(--ink-2)}',
    '.s8-reason b{color:var(--ink)}',
    '.s8-tiny{font-size:20px;line-height:30px;color:var(--ink-3);display:flex;gap:12px;align-items:center;flex-wrap:wrap}',
    '.s8-tiny .pill{flex:0 0 auto}',
    '.s8-tiny b{color:var(--ink-2);font-variant-numeric:tabular-nums;font-weight:600}',
    '.s8-fig{position:absolute;border-radius:20px;background:var(--bg-2);border:1px solid var(--line)}',
    '.s8-fig .cap{position:absolute;left:20px;top:12px;font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s8-fig .ex{position:absolute;right:18px;top:14px}',
    '.s8-fig svg{position:absolute;left:0;top:0;overflow:visible}',
    '.s8-fig .katex{font-size:24px}',
    '.s8-hyp{position:absolute}',
    '.s8-hyp svg{overflow:visible}',
    /* s08-07 */
    '.s8-sub{font-size:28px;line-height:40px;color:var(--ink-2)}',
    '.s8-d .eq-panel{padding:20px 28px 12px}',
    '.s8-d .derive-line{padding:5px 0}',
    '.s8-d .derive-tex .katex{font-size:27px}',
    '.s8-d .derive-note{font-size:20px;line-height:29px}',
    '.s8-d .derive-note .katex{font-size:22px}',
    '.s8-chip{position:absolute;transform:translate(-50%,-50%);white-space:nowrap;padding:3px 12px;border-radius:13px;font-size:19px;line-height:24px;font-weight:700;background:var(--bg-3);border:1px solid #39435A;color:var(--ink)}',
    '.s8-symrow{position:absolute;display:flex;gap:18px}',
    '.s8-symrow .sym-card{min-width:0;padding:12px 18px}',
    '.s8-symrow .sym-card .sym{font-size:36px}',
    '.s8-symrow .sym-card .sym-desc{font-size:19px;line-height:27px;max-width:330px}',
    '.s8-pie text{font-family:var(--font-sans)}',
    '.s8-hero{font-size:28px;line-height:40px;color:var(--ink)}',
    '.s8-hero .katex{font-size:34px}',
    /* s08-08 */
    '.s8-cnt{font-size:24px;line-height:34px;color:var(--ink-2)}',
    '.s8-cnt b{font-variant-numeric:tabular-nums;color:var(--ink);font-weight:700}',
    '.s8-cnt .pc{font-size:44px;line-height:52px;font-weight:800;color:var(--c-allow);font-variant-numeric:tabular-nums}',
    '.s8-cnt .row{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:6px 0;border-bottom:1px solid var(--line)}',
    '.s8-leg{font-size:20px;line-height:28px;color:var(--ink-2);display:flex;gap:26px}',
    '.s8-leg i{display:inline-block;width:14px;height:14px;border-radius:7px;margin-right:8px;vertical-align:-1px}',
    '.s8-sumhd{font-size:28px;line-height:38px;font-weight:700;color:var(--ink)}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s08-style')) return;
    var st = document.createElement('style'); st.id = 's08-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  /* ------------------------------------------------------------ small shared drawing pieces */
  /* an interval bar (G9) on any linear scale; grows from `from` (a value) */
  function ivBar(svg, o) {
    var g = svgEl('g', {}, svg), x0 = o.scale(o.from != null ? o.from : 0);
    var bar = svgEl('line', { x1: x0, x2: x0, y1: o.y, y2: o.y, stroke: o.color, 'stroke-width': o.width || 6, 'stroke-linecap': 'round', opacity: o.opacity != null ? o.opacity : 1 }, g);
    var dot = svgEl('circle', { cx: x0, cy: o.y, r: o.r || 11, fill: o.hollow ? C.bg : o.color, stroke: o.color, 'stroke-width': o.dashed ? 2.5 : 3, 'stroke-dasharray': o.dashed ? '4 3.2' : null }, g);
    var inner = o.dashed && !o.hollow ? null : null;
    if (o.dashed) { dot.setAttribute('fill', C.bg); inner = svgEl('circle', { cx: x0, cy: o.y, r: (o.r || 11) * 0.42, fill: o.color }, g); }
    gsap.set(g, { autoAlpha: 0 });
    var B = { g: g, bar: bar, dot: dot, inner: inner, o: o };
    B.grow = function (ctx, opt) {
      opt = opt || {};
      var tl = gsap.timeline({ delay: opt.delay || 0 }), d = dur(ctx, opt.duration != null ? opt.duration : 0.7);
      var xs = o.scale(o.est), xl = o.scale(o.lo), xh = o.scale(o.hi);
      tl.set(g, { autoAlpha: 1 }, 0);
      tl.fromTo(bar, { attr: { x1: x0, x2: x0 } }, { attr: { x1: xl, x2: xh }, duration: d, ease: E.out }, 0);
      tl.fromTo([dot, inner].filter(Boolean), { attr: { cx: x0 } }, { attr: { cx: xs }, duration: d, ease: E.out }, 0);
      return tl;
    };
    B.showNow = function () { gsap.set(g, { autoAlpha: 1 }); bar.setAttribute('x1', o.scale(o.lo)); bar.setAttribute('x2', o.scale(o.hi)); dot.setAttribute('cx', o.scale(o.est)); if (inner) inner.setAttribute('cx', o.scale(o.est)); };
    return B;
  }
  /* a "pop" that reads well: scale from 0.6 with the stamp ease */
  function popIn(tl, els, at, d) { tl.fromTo(els, { autoAlpha: 0, scale: 0.6, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: d || 0.35, ease: E.stamp, stagger: 0.06 }, at); }
  function fadeUp(tl, els, at, d, stagger) { tl.fromTo(els, { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: d || 0.5, ease: E.out, stagger: stagger || 0 }, at); }

  /* canvas waffle: n dots, cols per row, gap px; style(i) -> {fill, stroke, ring}; p = dots shown, q = highlight wave */
  function waffle(ctx, host, o) {
    var rows = Math.ceil(o.max / o.cols), W = o.cols * o.gap, H = rows * o.gap;
    var Wf = { n: o.n, st: { p: 0, q: 0 }, style: o.style };
    var K = Comp.canvas(ctx, host, { w: W, h: H, x: o.x, y: o.y, onResize: function () { Wf.draw(); } });
    Wf.K = K;
    Wf.draw = function () {
      var g = K.g, p = Wf.st.p, qq = Wf.st.q, r0 = o.r || o.gap * 0.36;
      K.clear();
      for (var i = 0; i < Wf.n; i++) {
        var a = Math.max(0, Math.min(1, (p - i) / 40));
        if (a <= 0) break;
        var cx = (i % o.cols) * o.gap + o.gap / 2, cy = Math.floor(i / o.cols) * o.gap + o.gap / 2;
        var s = Wf.style(i, Math.max(0, Math.min(1, (qq - i) / 60)));
        var r = r0 * (0.55 + 0.45 * a) * (s.scale || 1);
        g.globalAlpha = a * (s.alpha != null ? s.alpha : 1);
        g.beginPath(); g.arc(cx, cy, r, 0, Math.PI * 2);
        if (s.fill) { g.fillStyle = s.fill; g.fill(); }
        if (s.stroke) { g.lineWidth = s.lw || 1.6; g.strokeStyle = s.stroke; g.stroke(); }
      }
      g.globalAlpha = 1;
    };
    Wf.fill = function (opt) {
      opt = opt || {};
      return gsap.to(Wf.st, { p: Wf.n + 40, duration: dur(ctx, opt.duration || 1.2), ease: opt.ease || 'power1.inOut', delay: opt.delay || 0, onUpdate: Wf.draw, onComplete: Wf.draw });
    };
    Wf.wave = function (opt) {
      opt = opt || {};
      return gsap.to(Wf.st, { q: Wf.n + 60, duration: dur(ctx, opt.duration || 1.0), ease: 'power1.inOut', delay: opt.delay || 0, onUpdate: Wf.draw, onComplete: Wf.draw });
    };
    Wf.draw();
    return Wf;
  }

  /* ================================================================ s08-01
     3 × 3 board: rows = scores, columns = check families. EndorseRank row (top) and AWP row
     (bottom) carry data-shared keys: s08-02 bursts them into particles. */
  var G1 = { colX: [400, 880, 1360], yER: 270, yMid: 440, yAWP: 610 };
  var FAMK = ['t', 'a', 's'];
  var FAMHD = [
    { k: 'Transfer family', v: 'Transfer in-degree · in-value', col: C.xfer },
    { k: 'Allowance family', v: 'In-approve degree · in-approve value', col: C.allow },
    { k: 'Sybil-stability family', v: 'Counterparty ratio · tenure · active months', col: C.ink }
  ];
  var ROWS1 = {
    er:  { name: 'EndorseRank', sub: 'Walks the allowance edges', col: C.allow, own: 'a', y: G1.yER,
           v: { t: '0.158 [0.147, 0.169]', a: '0.585 [0.578, 0.592]', s: '0.007 [−0.001, 0.015]' } },
    cpr: { name: 'C-PR (λ = 0.5)', sub: 'Walks both edge types, mixed', col: C.cpr, own: null, y: G1.yMid,
           v: { t: '0.365 [0.355, 0.375]', a: '0.477 [0.469, 0.485]', s: '0.142 [0.134, 0.151]' } },
    awp: { name: 'AWP', sub: 'Walks the transfer edges', col: C.xfer, own: 't', y: G1.yAWP,
           v: { t: '0.572 [0.564, 0.580]', a: '0.193 [0.182, 0.203]', s: '0.395 [0.387, 0.403]' } }
  };
  var EXTRA1 = [
    ['C-PR (λ = 1) · allowance layer', '0.162 [0.151, 0.173]', '0.597 [0.590, 0.604]', '0.011 [0.002, 0.019]'],
    ['C-PR (λ = 0) · transfer layer', '0.659 [0.653, 0.666]', '0.225 [0.214, 0.235]', '0.404 [0.396, 0.413]'],
    ['S-PR', '0.629 [0.621, 0.636]', '0.323 [0.313, 0.333]', '0.398 [0.390, 0.406]']
  ];
  var DIFF1 = { t: '+0.414 [0.401, 0.427]', a: '+0.392 [0.380, 0.405]' };
  var MINI = { x0: 26, x1: 434, d0: -0.05, d1: 0.70, y: 22 };
  function mx(v) { return MINI.x0 + (v - MINI.d0) / (MINI.d1 - MINI.d0) * (MINI.x1 - MINI.x0); }
  function row1Html(key) {
    var R = ROWS1[key];
    var s = '<div class="s8-row" id="row-' + key + '" data-in="none"' + (key !== 'cpr' ? ' data-shared="s8-row-' + key + '"' : '') + ' style="top:' + R.y + 'px">' +
      '<div class="s8-rl"><div class="k" style="color:' + R.col + '">' + R.name + '</div><div class="v">' + R.sub + '</div></div>';
    FAMK.forEach(function (f, j) {
      s += '<div class="s8-cell" data-f="' + f + '" style="left:' + (G1.colX[j] - 96) + 'px"><div class="tint"></div><div class="num tnum">&nbsp;</div><div class="ci tnum"></div></div>';
    });
    return s + '</div>';
  }
  function diff1Html(f, j) {
    return '<div class="s8-diff" id="diff-' + f + '" data-in="none" style="left:' + (G1.colX[j] + 80) + 'px"><svg width="300" height="178"></svg>' +
      '<div class="lab tnum">Difference ' + estOf(DIFF1[f]) + '<small>' + ciOf(DIFF1[f]) + '</small></div></div>';
  }
  var slide1 = {
    id: 's08-01', title: 'Same window: each score fits its own edges', time: 45, steps: 4,
    tags: ['construct'],
    notes: [
      'Now the results. First, the same-window check. The rows are scores and the columns are proxy families. The darker a cell, the larger Kendall’s tau. I will leave the middle row empty for a moment.',
      'EndorseRank agrees best with the allowance proxies, at 0.585, and AWP with the transfer proxies, at 0.572. The two cells with the mirror mark are each score’s own family.',
      'Swap them and the values drop sharply, to 0.158 and 0.193. If we pair the two scores on the same proxies and subtract, the difference is about 0.4, with a narrow interval. This difference was not a comparison fixed in advance.',
      'C-PR, which mixes the two edge types, lies between the two rows on every family at λ = 0.5: 0.365 on transfer, 0.477 on allowance and 0.142 on Sybil stability. The small markers under the cells show where EndorseRank and AWP sit. The button at the bottom right also shows the values for λ = 1, λ = 0 and S-PR.',
      'But the proxies here were built from the same records as the scores, so part of this agreement comes about by itself. That makes it a check that each score measures what it was built to measure, an intended-construct check. It is not an external test.'
    ],
    html: function () {
      var s = '<h1 class="t-h1">Each score agrees most with proxies from [[its own edges]]</h1>';
      FAMHD.forEach(function (F, j) {
        s += '<div class="s8-colhd" style="left:' + G1.colX[j] + 'px"><div class="k" style="color:' + F.col + '">' + F.k + '</div><div class="v">' + F.v + '</div></div>';
      });
      s += '<div class="s8-slot" id="slot" data-in="none">Where does a mix of both edge types stand?</div>';
      s += row1Html('er') + row1Html('awp') + row1Html('cpr');
      s += diff1Html('t', 0) + diff1Html('a', 1);
      s += '<p class="abs s8-cap" id="cap" data-in="none" style="left:96px;top:796px;width:1400px">&nbsp;</p>';
      s += '<p class="abs s8-small" id="fam" data-in="none" style="left:96px;top:850px;width:1728px">Kendall’s τ<sub>b</sub> · family mean = mean τ of the family’s proxies, e.g. transfer family $=\\tfrac12\\bigl(\\tau_{\\text{in-degree}}+\\tau_{\\text{in-value}}\\bigr)$ · 95% interval · matched cohort of 15,107 contracts</p>';
      s += '<div class="abs s8-note" id="note" data-in="none" style="left:96px;top:900px;width:1400px">' + pill('construct') + '<span>Partly by construction: the proxies come from the same records as the scores</span></div>';
      s += '<button class="s8-more" id="more" data-in="none" type="button">Show λ = 1 · λ = 0 · S-PR</button>';
      s += '<div class="s8-pop" id="pop" data-in="none"><div class="hd">Same-window family mean τ<sub>b</sub> [95% interval] · intended-construct check</div><table><tr><th></th><th style="color:#3CC4FF">Transfer</th><th style="color:#F5B43C">Allowance</th><th>Sybil stability</th></tr>' +
        EXTRA1.map(function (r) { return '<tr><td>' + r[0] + '</td><td>' + r[1] + '</td><td>' + r[2] + '</td><td>' + r[3].replace(/^-/, '−') + '</td></tr>'; }).join('') + '</table></div>';
      return s;
    },
    build: function (el, ctx) {
      var g = ctx.g = { cells: {} };
      ['er', 'cpr', 'awp'].forEach(function (key) {
        var R = ROWS1[key], rowEl = q(el, '#row-' + key);
        g.cells[key] = qa(rowEl, '.s8-cell').map(function (cell, j) {
          var f = FAMK[j], d = iv(R.v[f]), own = R.own === f;
          var tint = q(cell, '.tint'); tint.style.background = rgba(R.col, Math.max(0.04, 0.05 + 0.34 * d.est));
          var svg = svgEl('svg', { width: 460, height: 44, 'class': 'mini', viewBox: '0 0 460 44' }, cell);
          svgEl('line', { x1: MINI.x0, x2: MINI.x1, y1: MINI.y, y2: MINI.y, stroke: '#2C3547', 'stroke-width': 2 }, svg);
          svgEl('line', { x1: mx(0), x2: mx(0), y1: MINI.y - 9, y2: MINI.y + 9, stroke: C.ink3, 'stroke-width': 1.5, 'stroke-dasharray': '3 3' }, svg);
          txt(svg, mx(0), MINI.y + 24, '0', { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 15 });
          txt(svg, mx(0.5), MINI.y + 24, '0.5', { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 15 });
          svgEl('line', { x1: mx(0.5), x2: mx(0.5), y1: MINI.y - 5, y2: MINI.y + 5, stroke: '#2C3547', 'stroke-width': 1.5 }, svg);
          var refs = [];
          if (key === 'cpr') {
            [['er', C.allow], ['awp', C.xfer]].forEach(function (rc) {
              var v = iv(ROWS1[rc[0]].v[f]).est, x = mx(v);
              refs.push(svgEl('path', { d: 'M' + (x - 6) + ',' + (MINI.y - 18) + ' L' + (x + 6) + ',' + (MINI.y - 18) + ' L' + x + ',' + (MINI.y - 8) + 'Z', fill: rc[1], opacity: 0.95 }, svg));
            });
            gsap.set(refs, { autoAlpha: 0 });
          }
          var B = ivBar(svg, { scale: mx, y: MINI.y, est: d.est, lo: d.lo, hi: d.hi, color: R.col, width: 5, r: 8, from: 0 });
          var mir = null;
          if (own) { mir = h('div', 'mir', cell, Deck.ICONS.mirror); mir.style.color = R.col; gsap.set(mir, { autoAlpha: 0 }); }
          var ciEl = q(cell, '.ci'); ciEl.textContent = ciOf(R.v[f]); gsap.set(ciEl, { autoAlpha: 0 });
          return { el: cell, f: f, d: d, own: own, tint: tint, num: q(cell, '.num'), ci: ciEl, bar: B, mir: mir, refs: refs, col: R.col };
        });
      });
      g.rowER = q(el, '#row-er'); g.rowAWP = q(el, '#row-awp'); g.rowCPR = q(el, '#row-cpr');
      g.slot = q(el, '#slot'); g.cap = q(el, '#cap'); g.fam = q(el, '#fam'); g.note = q(el, '#note');
      g.more = q(el, '#more'); g.pop = q(el, '#pop');
      g.diffs = ['t', 'a'].map(function (f) {
        var wrap = q(el, '#diff-' + f), svg = q(wrap, 'svg');
        var p = svgEl('path', { d: 'M150,8 L150,170', stroke: C.ink, 'stroke-width': 2.5, fill: 'none' }, svg);
        var h1 = svgEl('path', { d: 'M140,20 L150,6 L160,20', stroke: C.ink, 'stroke-width': 2.5, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, svg);
        var h2 = svgEl('path', { d: 'M140,158 L150,172 L160,158', stroke: C.ink, 'stroke-width': 2.5, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, svg);
        return { wrap: wrap, line: p, heads: [h1, h2], lab: q(wrap, '.lab') };
      });
      gsap.set([g.rowCPR, g.cap, g.fam, g.note, g.more, g.pop].concat(g.diffs.map(function (d) { return d.wrap; })), { autoAlpha: 0 });
      ctx.on(g.more, 'click', function (e) {
        e.stopPropagation();
        g.popOpen = !g.popOpen;
        ctx.add(function () { gsap.to(g.pop, { autoAlpha: g.popOpen ? 1 : 0, y: g.popOpen ? 0 : 10, duration: ctx.reduced ? 0.01 : 0.3, ease: E.out }); });
        g.more.textContent = g.popOpen ? 'Close' : 'Show λ = 1 · λ = 0 · S-PR';
      });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      [g.rowER, g.rowAWP].forEach(function (r, i) {
        var had = ctx.prev && ctx.prev.rect && ctx.prev.rect(r.getAttribute('data-shared'));
        if (!had) tl.fromTo(r, { autoAlpha: 0, y: 28 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out }, 0.3 + i * 0.14);
      });
      tl.fromTo(g.slot, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 0.6);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        var k = 0;
        ['er', 'awp'].forEach(function (key) {
          g.cells[key].forEach(function (c) {
            var at = 0.1 + k * 0.12; k++;
            tl.add(c.bar.grow(ctx, { duration: 0.7 }), at);
            tl.to(c.tint, { opacity: c.own ? 1 : 0.7, duration: 0.6 }, at);
            tl.add(ctx.count(c.num, 0, c.d.est, { decimals: 3, final: estOf(c.d.s), duration: 0.9 }), at);
            tl.fromTo(c.ci, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, at + 0.5);
          });
        });
        ['er', 'awp'].forEach(function (key) {
          g.cells[key].forEach(function (c) {
            if (!c.own) return;
            tl.to(c.el, { borderColor: c.col, boxShadow: '0 0 30px ' + rgba(c.col, 0.28), duration: 0.5 }, 1.0);
            tl.to(c.num, { color: c.col, duration: 0.5 }, 1.0);
            popIn(tl, c.mir, 1.15);
          });
        });
        tl.call(function () { g.cap.innerHTML = 'EndorseRank × allowance family <b class="tnum c-allow">0.585</b> · AWP × transfer family <b class="tnum c-xfer">0.572</b>: highest on their own family'; }, null, 1.2);
        fadeUp(tl, [g.cap, g.fam], 1.25, 0.5, 0.15);
      }
      if (i === 2) {
        var swapped = [g.cells.er[0], g.cells.awp[1]];
        swapped.forEach(function (c, j) {
          tl.fromTo(c.el, { boxShadow: '0 0 0 rgba(233,237,245,0)' }, { boxShadow: '0 0 34px rgba(233,237,245,.30)', duration: 0.3, yoyo: true, repeat: 3, ease: 'sine.inOut' }, j * 0.15);
          tl.to(c.el, { borderColor: '#A3ADBF', duration: 0.3 }, j * 0.15);
        });
        tl.to(g.slot, { color: 'rgba(103,112,131,0)', borderColor: '#202838', duration: 0.3 }, 0);
        g.diffs.forEach(function (D, j) {
          var at = 0.5 + j * 0.3;
          tl.set(D.wrap, { autoAlpha: 1 }, at);
          tl.fromTo(D.line, { strokeDasharray: '170 170', strokeDashoffset: 170 }, { strokeDashoffset: 0, duration: dur(ctx, 0.5), ease: E.io }, at);
          popIn(tl, D.heads, at + 0.35, 0.25);
          popIn(tl, D.lab, at + 0.45);
        });
        tl.add(Comp.swap(ctx, g.cap, 'Swapped, they are much lower: <b class="tnum">0.158</b> · <b class="tnum">0.193</b> · difference about 0.4' + pill(NOT_PLANNED)), 0.3);
      }
      if (i === 3) {
        tl.to(g.diffs.map(function (D) { return D.wrap; }), { autoAlpha: 0, duration: 0.3 }, 0);
        tl.to(g.slot, { autoAlpha: 0, duration: 0.3 }, 0.1);
        tl.fromTo(g.rowCPR, { autoAlpha: 0, x: -80 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.8), ease: E.out }, 0.3);
        g.cells.cpr.forEach(function (c, j) {
          var at = 0.8 + j * 0.12;
          tl.to(c.refs, { autoAlpha: 1, duration: 0.3 }, at - 0.2);
          tl.add(c.bar.grow(ctx, { duration: 0.7 }), at);
          tl.to(c.tint, { opacity: 0.8, duration: 0.6 }, at);
          tl.add(ctx.count(c.num, 0, c.d.est, { decimals: 3, final: estOf(c.d.s), duration: 0.9 }), at);
          tl.fromTo(c.ci, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, at + 0.5);
          tl.to(c.num, { color: C.cpr, duration: 0.4 }, at + 0.6);
        });
        tl.add(Comp.swap(ctx, g.cap, 'C-PR (λ = 0.5) lies <b>between the two rows</b> on every family: transfer <b class="tnum">0.365</b> · allowance <b class="tnum">0.477</b> · Sybil <b class="tnum">0.142</b>'), 0.4);
        tl.fromTo(g.more, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.4);
      }
      if (i === 4) {
        fadeUp(tl, g.note, 0.1, 0.5);
        tl.to(g.cells.er.concat(g.cells.awp).filter(function (c) { return c.own; }).map(function (c) { return c.mir; }), { scale: 1.25, duration: 0.2, yoyo: true, repeat: 1, transformOrigin: '50% 50%' }, 0.5);
      }
    }
  };

  /* ================================================================ s08-02
     three.js: rows of s08-01 → particles → the λ = 1 cloud (geometry of s06-04) → camera rises →
     rank–rank scatter on the floor plate (x = EndorseRank percentile, depth = AWP percentile). */
  var P2 = { top: 150, w: 1260, h: 830, L: 8, FLOOR: -0.42 };
  var CAM_CLOUD = { theta: 0.16, phi: 1.16, radius: 21, target: [0.2, 1.45, 0] };
  var CAM_TOP = { theta: 0, phi: 0.05, radius: 17.4, target: [0, -0.42, 0] };
  var ER_ZERO = { pct: 0.0177, n: 535 }, AWP_ZERO = { pct: 0.0884, n: 2672 };
  function blendLazy(ctx, Cl, which, target, o) {
    o = o || {};
    var n = Cl.n, arr = which === 'position' ? Cl.positions : Cl.colors, attr = Cl.geometry.attributes[which];
    var from = null, ease = gsap.parseEase(o.ease || E.io), dl = o.delays, spread = o.spread || 0, st = { p: 0 };
    function cap() { if (!from) from = new Float32Array(arr); }
    return gsap.to(st, { p: 1, duration: dur(ctx, o.duration || 1.2), ease: 'none', delay: o.delay || 0,
      onStart: cap,
      onUpdate: function () {
        cap();
        var p = st.p;
        for (var i = 0; i < n; i++) {
          var lp = dl ? (p * (1 + spread) - dl[i] * spread) : p;
          lp = lp <= 0 ? 0 : lp >= 1 ? 1 : ease(lp);
          var j = i * 3;
          arr[j] = from[j] + (target[j] - from[j]) * lp; arr[j + 1] = from[j + 1] + (target[j + 1] - from[j + 1]) * lp; arr[j + 2] = from[j + 2] + (target[j + 2] - from[j + 2]) * lp;
        }
        attr.needsUpdate = true;
      },
      onComplete: function () { arr.set(target); attr.needsUpdate = true; if (which === 'position') Cl.geometry.computeBoundingSphere(); from = null; } });
  }
  function p2pt(g, e, a) { var L = P2.L; return g.T.project([(e - 0.5) * L, P2.FLOOR + 0.02, -(a - 0.5) * L]); }
  var slide2 = {
    id: 's08-02', title: 'The two scores give different orders', time: 45, steps: 3,
    tags: [H1TAG],
    notes: [
      'Do the two scores put the same contracts in the same order? The two rows of the previous slide break into points and become a cloud of 15,107 contracts. Seen from above, the cloud becomes a flat picture. Across is the rank by EndorseRank and up is the rank by AWP, both turned into percentiles. Amber points are contracts that EndorseRank ranks higher, sky-blue points contracts that AWP ranks higher.',
      'If the two ranks were the same, the points would gather on this diagonal. But they are spread widely. Kendall’s tau is 0.174. That is clearly above 0 and far from 1. The two orders are related, but they are not the same order.',
      'There are more than 110 million contract pairs. 96.7% of them are ordered by both scores, and of those, 41.2% are in the opposite order. The thirty pairs flashing now are only an illustration; the value where it stops is the result over all pairs. Related, but not interchangeable.',
      'The column at the left edge is the 535 contracts with an EndorseRank of zero, and the row at the bottom is the 2,672 contracts with an AWP of zero. All zero-score contracts are tied, so they share the lowest ranks and sit in the middle of them. That is why the AWP zero row is at about 9, not at 0, and the EndorseRank zero column at about 2. With the rule that keeps contracts outside a graph as isolated nodes, tau stayed at 0.174. The two graphs are built differently, so different orders are partly expected. In the registered analysis it was 0.217.'
    ],
    html:
      '<h1 class="t-h1">EndorseRank and AWP put contracts in [[different orders]]</h1>' +
      '<div class="abs" data-shared="s8-row-er" data-shared-mode="manual" style="left:96px;top:' + G1.yER + 'px;width:1724px;height:150px;visibility:hidden"></div>' +
      '<div class="abs" data-shared="s8-row-awp" data-shared-mode="manual" style="left:96px;top:' + G1.yAWP + 'px;width:1724px;height:150px;visibility:hidden"></div>' +
      '<div class="abs" id="p3" data-in="none" style="left:0;top:' + P2.top + 'px;width:' + P2.w + 'px;height:' + P2.h + 'px"></div>' +
      '<svg class="abs s8-ov" id="ov" data-in="none" width="' + P2.w + '" height="' + P2.h + '" viewBox="0 0 ' + P2.w + ' ' + P2.h + '" style="left:0;top:' + P2.top + 'px"></svg>' +
      '<div class="abs s8-p2" id="panel" data-in="none" style="left:1300px;top:186px;width:524px;height:780px">' +
        '<div class="abs lg" id="lg" style="left:0;top:0;width:524px"><div>One point = one contract · <b class="tnum ink">15,107</b> contracts</div>' +
          '<div><i style="background:#F5B43C"></i>Ranked higher by EndorseRank</div><div><i style="background:#3CC4FF"></i>Ranked higher by AWP</div></div>' +
        '<div class="abs" id="b1" style="left:0;top:126px;width:524px">' +
          '<div class="k">Kendall’s τ<sub>b</sub> (EndorseRank vs AWP)</div>' +
          '<div style="display:flex;align-items:baseline;gap:16px"><span class="tau" id="tau">0.000</span><span class="ci" id="tauci">[0.163, 0.185]</span></div>' +
          '<svg id="rul" width="500" height="72" style="overflow:visible;display:block;margin-top:2px"></svg>' +
          '<div class="ln" id="tauln">Neither 0 nor 1</div>' +
          '<div class="gh" id="ghost" style="margin-top:6px">' + pill('registered-analysis') + '<span class="tnum">0.217 [0.209, 0.225]</span></div>' +
                  '</div>' +
        '<div class="abs" id="b2" style="left:0;top:418px;width:524px">' +
          '<div class="ln">Contract pairs <b id="pairs">114,103,171</b></div>' +
          '<div class="ln">Pairs ordered by both scores <b id="both">96.7%</b></div>' +
          '<div class="ln" style="margin-top:6px">Of these, in opposite order</div>' +
          '<div style="display:flex;align-items:baseline;gap:14px"><span class="big" id="disc">0.0%</span><span class="ln" id="discnote" style="font-size:19px;color:var(--ink-3)">Flashing pairs 0 / 30</span></div>' +
          '<div class="s8-gauge"><b id="gfill"></b></div>' +
        '</div>' +
        '<div class="abs concl" id="b3" style="left:0;top:660px;width:524px">Related, but not interchangeable</div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.ov = q(el, '#ov'); g.panel = q(el, '#panel');
      g.lg = q(el, '#lg'); g.b1 = q(el, '#b1'); g.b2 = q(el, '#b2'); g.b3 = q(el, '#b3');
      g.tau = q(el, '#tau'); g.tauci = q(el, '#tauci'); g.tauln = q(el, '#tauln'); g.ghost = q(el, '#ghost');
      g.pairs = q(el, '#pairs'); g.both = q(el, '#both'); g.disc = q(el, '#disc'); g.discnote = q(el, '#discnote'); g.gfill = q(el, '#gfill');
      gsap.set([g.lg, g.b1, g.b2, g.b3, g.ghost, g.tauci, g.tauln], { autoAlpha: 0 });
      gsap.set(g.panel, { autoAlpha: 1 });
      /* −1 … +1 ruler */
      var rul = q(el, '#rul'), RX = function (v) { return 20 + (v + 1) / 2 * 460; };
      svgEl('line', { x1: RX(-1), x2: RX(1), y1: 24, y2: 24, stroke: C.ink3, 'stroke-width': 2 }, rul);
      [[-1, '−1'], [0, '0'], [1, '+1']].forEach(function (t) {
        svgEl('line', { x1: RX(t[0]), x2: RX(t[0]), y1: 15, y2: 33, stroke: C.ink3, 'stroke-width': 2 }, rul);
        txt(rul, RX(t[0]), 58, t[1], { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18, 'class': 'tnum' });
      });
      g.rmark = svgEl('path', { d: 'M-9,0 L9,0 L0,15 Z', fill: C.ink, transform: 'translate(' + RX(0) + ',4)' }, rul);
      g.RX = RX; g.rst = { v: 0 };
      gsap.set(g.rmark, { autoAlpha: 0 });

      var K = Comp.data.contracts(); if (!K) return;
      var n = K.n, i, er = K.pct.endorserank, aw = K.pct.awp, cl = K.pct.cpr_l100, fl = K.flags;
      g.er = er; g.aw = aw; g.n = n;
      var xa = new Float32Array(n), zt = new Float32Array(n), mxA = 0, mxZ = 0;
      for (i = 0; i < n; i++) {
        xa[i] = Math.log10(1 + K.raw.in_approve_degree[i]); zt[i] = Math.log10(1 + K.raw.in_degree[i]);
        if (xa[i] > mxA) mxA = xa[i]; if (zt[i] > mxZ) mxZ = zt[i];
      }
      var SPAN = 7, SX = SPAN / mxA, SZ = SPAN / mxZ, HY = 4.6, FLOOR = P2.FLOOR, L = P2.L;
      var amb = Comp.rgb(C.allow), sky = Comp.rgb(C.xfer), grey = Comp.rgb(C.ink3), base = Comp.rgb('#8C96A8');
      g.cloudP = new Float32Array(n * 3); g.flatP = new Float32Array(n * 3);
      var cloudC = new Float32Array(n * 3); g.flatC = new Float32Array(n * 3);
      for (i = 0; i < n; i++) {
        var j = i * 3, zero = fl[i] & 1;
        g.cloudP[j] = xa[i] * SX - SPAN / 2; g.cloudP[j + 1] = zero ? FLOOR + 0.03 : cl[i] * HY; g.cloudP[j + 2] = zt[i] * SZ - SPAN / 2;
        var b = 0.3 + 0.7 * cl[i];
        cloudC[j] = zero ? grey[0] * 0.55 : amb[0] * b; cloudC[j + 1] = zero ? grey[1] * 0.55 : amb[1] * b; cloudC[j + 2] = zero ? grey[2] * 0.55 : amb[2] * b;
        g.flatP[j] = (er[i] - 0.5) * L; g.flatP[j + 1] = FLOOR + 0.02; g.flatP[j + 2] = -(aw[i] - 0.5) * L;
        var dlt = aw[i] - er[i], tgt = dlt > 0 ? sky : amb, m = Math.min(1, Math.abs(dlt) * 2.4);
        for (var c3 = 0; c3 < 3; c3++) g.flatC[j + c3] = toLin((base[c3] * (1 - m) + tgt[c3] * m) * 0.92);
      }
      var rnd = Deck.util.rng(42);
      g.rdel = new Float32Array(n); g.rdel2 = new Float32Array(n);
      for (i = 0; i < n; i++) { g.rdel[i] = rnd(); g.rdel2[i] = 0.5 * rnd() + 0.5 * (1 - er[i]); }
      /* 30 illustrative pairs (seeded), no ties on either score */
      g.pairsIdx = [];
      var guard = 0;
      while (g.pairsIdx.length < 30 && guard++ < 5000) {
        var a = Math.floor(rnd() * n), bb = Math.floor(rnd() * n);
        if (a === bb || er[a] === er[bb] || aw[a] === aw[bb]) continue;
        if (Math.abs(er[a] - er[bb]) < 0.15 && Math.abs(aw[a] - aw[bb]) < 0.15) continue;   /* long enough to see */
        g.pairsIdx.push([a, bb, Math.sign(er[a] - er[bb]) * Math.sign(aw[a] - aw[bb]) > 0]);
      }
      var T = ctx.three(q(el, '#p3'), { fov: 30, orbit: false, camera: CAM_CLOUD, autoRotate: 0 });
      g.T = T;
      if (T.failed) return;
      Comp.floor(ctx, T, { size: L, y: FLOOR, divisions: 8, opacity: 0.2 });
      /* start positions: inside the boxes of the two rows of s08-01 (particles), else a small burst */
      var cam = T.camera, THREE = T.THREE;
      cam.updateMatrixWorld(); cam.updateProjectionMatrix();
      var rE = ctx.prev && ctx.prev.rect ? ctx.prev.rect('s8-row-er') : null, rA = ctx.prev && ctx.prev.rect ? ctx.prev.rect('s8-row-awp') : null;
      var emit = new Float32Array(n * 3), dist = CAM_CLOUD.radius, v3 = new THREE.Vector3();
      for (i = 0; i < n; i++) {
        var R = (i % 2 ? rA : rE) || rE || rA;
        if (R) {
          var sx = R.x + 300 + rnd() * (R.w - 300), sy = R.y + rnd() * R.h - P2.top;
          v3.set(sx / T.width * 2 - 1, -(sy / T.height * 2 - 1), 0.5).unproject(cam).sub(cam.position).normalize();
          emit[i * 3] = cam.position.x + v3.x * dist; emit[i * 3 + 1] = cam.position.y + v3.y * dist; emit[i * 3 + 2] = cam.position.z + v3.z * dist;
        } else {
          var u = rnd() * Math.PI * 2, w = rnd() * 2 - 1, rr = 0.25 * Math.cbrt(rnd());
          emit[i * 3] = CAM_CLOUD.target[0] + rr * Math.sqrt(1 - w * w) * Math.cos(u); emit[i * 3 + 1] = CAM_CLOUD.target[1] + rr * w; emit[i * 3 + 2] = CAM_CLOUD.target[2] + rr * Math.sqrt(1 - w * w) * Math.sin(u);
        }
      }
      g.fromRows = !!(rE || rA);
      g.cloud = Comp.cloud(ctx, T, { positions: emit, colors: cloudC, size: 3, opacity: 0.6 });
      if (g.cloud.points) g.cloud.points.visible = false;
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (ctx.prev && ctx.prev.el) {
        ['s8-row-er', 's8-row-awp'].forEach(function (k) { var o = ctx.prev.el.querySelector('[data-shared="' + k + '"]'); if (o && o.style.visibility !== 'hidden') tl.to(o, { autoAlpha: 0, duration: 0.35 }, 0.05); });
      }
      if (!g.cloud || !g.cloud.points) { tl.call(function () { ctx.add(function () { drawAxes2(ctx); }); }, null, 0.4); return; }
      tl.call(function () { g.cloud.points.visible = true; }, null, 0);
      tl.add(blendLazy(ctx, g.cloud, 'position', g.cloudP, { duration: g.fromRows ? 1.1 : 1.3, delays: g.rdel, spread: 1.0, ease: 'power3.out' }), 0);
      tl.add(g.T.cameraTo(CAM_TOP, { duration: 1.5 }), 1.55);
      tl.add(blendLazy(ctx, g.cloud, 'position', g.flatP, { duration: 1.6, delays: g.rdel2, spread: 0.6, ease: E.io }), 1.85);
      tl.add(blendLazy(ctx, g.cloud, 'color', g.flatC, { duration: 1.2, delays: g.rdel2, spread: 0.4 }), 2.0);
      tl.call(function () { ctx.add(function () { drawAxes2(ctx); }); }, null, 3.5);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        if (g.T && !g.T.failed) {
          g.T.render();
          var a = p2pt(g, 0, 0), b = p2pt(g, 1, 1);
          var dg = svgEl('line', { x1: a.x, y1: a.y, x2: b.x, y2: b.y, stroke: C.ink, 'stroke-width': 2.5, 'stroke-dasharray': '8 8', opacity: 0.9 }, g.ov);
          var L = Math.hypot(b.x - a.x, b.y - a.y);
          tl.fromTo(dg, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur(ctx, 0.9), ease: E.io, onComplete: function () { dg.style.strokeDasharray = '8 8'; dg.style.strokeDashoffset = '0'; } }, 0);
          var lab = txt(g.ov, b.x - 12, b.y - 14, 'Same rank', { 'text-anchor': 'end', fill: C.ink, 'font-size': 21, 'font-weight': 700 });
          tl.fromTo(lab, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.8);
        }
        fadeUp(tl, g.b1, 0.3, 0.5);
        tl.add(ctx.count(g.tau, 0, 0.174, { decimals: 3, final: '0.174', duration: 1.2 }), 0.5);
        tl.fromTo(g.tauci, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.4);
        tl.set(g.rmark, { autoAlpha: 1 }, 0.5);
        tl.to(g.rst, { v: 0.174, duration: dur(ctx, 1.2), ease: 'power3.out', onUpdate: function () { g.rmark.setAttribute('transform', 'translate(' + g.RX(g.rst.v).toFixed(1) + ',4)'); } }, 0.5);
        tl.fromTo(g.tauln, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4 }, 1.6);
      }
      if (i === 2) {
        fadeUp(tl, g.b2, 0, 0.5);
        tl.add(Comp.odometer(ctx, g.pairs, '114,103,171', { duration: 1.6 }), 0.1);
        tl.add(ctx.count(g.both, 0, 96.7, { decimals: 1, suffix: '%', final: '96.7%', duration: 1.2 }), 0.4);
        var t0 = 1.7, per = 0.13, st = { c: 0, d: 0 };
        if (g.T && !g.T.failed && g.pairsIdx) {
          g.T.render();
          var lay = g.pairLay = svgEl('g', {}, g.ov);
          g.pairsIdx.forEach(function (pr, k) {
            var A = p2pt(g, g.er[pr[0]], g.aw[pr[0]]), B = p2pt(g, g.er[pr[1]], g.aw[pr[1]]);
            var col = pr[2] ? C.ink : C.hi;
            var ln = svgEl('line', { x1: A.x, y1: A.y, x2: B.x, y2: B.y, stroke: col, 'stroke-width': 2.4, 'stroke-linecap': 'round' }, lay);
            var d1 = svgEl('circle', { cx: A.x, cy: A.y, r: 5, fill: col }, lay), d2 = svgEl('circle', { cx: B.x, cy: B.y, r: 5, fill: col }, lay);
            var L = Math.hypot(B.x - A.x, B.y - A.y) || 1, at = t0 + k * per;
            tl.fromTo(ln, { strokeDasharray: L + ' ' + L, strokeDashoffset: L, autoAlpha: 1 }, { strokeDashoffset: 0, duration: dur(ctx, 0.22), ease: 'power2.out' }, at);
            tl.fromTo([d1, d2], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.1 }, at);
            tl.to([ln, d1, d2], { autoAlpha: 0.22, duration: 0.5 }, at + 0.5);
            tl.call(function () {
              if (pr[2]) st.c++; else st.d++;
              var r = st.d / (st.c + st.d);
              g.disc.textContent = fmt(r * 100, 1) + '%';
              g.discnote.textContent = 'Flashing pairs ' + (st.c + st.d) + ' / 30 · illustration';
              ctx.add(function () { gsap.to(g.gfill, { width: (r * 100).toFixed(1) + '%', duration: ctx.reduced ? 0.01 : 0.12 }); });
            }, null, at + 0.05);
          });
        }
        var tEnd = t0 + 30 * per + 0.3;
        tl.call(function () {
          g.discnote.textContent = 'Final value = all 110 million pairs';
          ctx.add(function () { gsap.to(g.gfill, { width: '41.2%', duration: ctx.reduced ? 0.01 : 0.8, ease: E.io }); });
        }, null, tEnd);
        tl.add(ctx.count(g.disc, 40, 41.2, { decimals: 1, suffix: '%', final: '41.2%', duration: 0.8 }), tEnd + 0.01);
        tl.fromTo(g.b3, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, tEnd + 0.9);
      }
      if (i === 3) {
        if (g.T && !g.T.failed) {
          g.T.render();
          var lay3 = svgEl('g', {}, g.ov);
          var c0 = p2pt(g, ER_ZERO.pct, 0.0884), c1 = p2pt(g, ER_ZERO.pct, 0.9823);
          var b0 = p2pt(g, 0.0177, AWP_ZERO.pct), b1 = p2pt(g, 0.9993, AWP_ZERO.pct);
          var colR = svgEl('rect', { x: c0.x - 11, y: c1.y - 10, width: 22, height: c0.y - c1.y + 20, rx: 11, fill: 'rgba(233,237,245,.08)', stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '6 5' }, lay3);
          var bandR = svgEl('rect', { x: b0.x - 10, y: b0.y - 11, width: b1.x - b0.x + 20, height: 22, rx: 11, fill: 'rgba(233,237,245,.08)', stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '6 5' }, lay3);
          var pl = p2pt(g, ER_ZERO.pct, 0.74);
          var t1a = txt(lay3, pl.x - 64, pl.y - 12, 'EndorseRank', { 'text-anchor': 'end', fill: C.ink, 'font-size': 21, 'font-weight': 700 });
          var t1b = txt(lay3, pl.x - 64, pl.y + 18, '535 at zero', { 'text-anchor': 'end', fill: C.ink, 'font-size': 21, 'font-weight': 700, 'class': 'tnum' });
          var t1l = svgEl('line', { x1: pl.x - 58, x2: pl.x - 16, y1: pl.y + 2, y2: pl.y + 2, stroke: C.ink2, 'stroke-width': 1.5 }, lay3);
          var t1c = txt(lay3, pl.x - 64, pl.y + 46, '→ middle ≈ 2', { 'text-anchor': 'end', fill: C.ink2, 'font-size': 18, 'class': 'tnum' });
          /* ties: every zero shares the bottom ranks, so the block sits at its mid-rank percentile
             (AWP (2,672 + 1)/2 − 1 over 15,106 ≈ 8.8; EndorseRank ≈ 1.8), not at 0 */
          var ya = p2pt(g, 0, AWP_ZERO.pct);
          var tk = svgEl('line', { x1: ya.x - 24, x2: ya.x - 12, y1: ya.y, y2: ya.y, stroke: C.ink, 'stroke-width': 2 }, lay3);
          var tkt = txt(lay3, ya.x - 30, ya.y + 6, '≈ 9', { 'text-anchor': 'end', fill: C.ink, 'font-size': 18, 'font-weight': 700, 'class': 'tnum' });
          var tc = p2pt(g, 0.17, 0.133);
          var tie = txt(lay3, tc.x, tc.y + 6, 'All tied → they share the lowest ranks and sit at their middle (≈ 9)', { 'text-anchor': 'start', fill: C.ink, 'font-size': 18, 'font-weight': 600, stroke: '#0E1119', 'stroke-width': 6, 'stroke-linejoin': 'round', 'paint-order': 'stroke' });
          var t2 = txt(lay3, b1.x + 22, b0.y + 7, 'AWP: 2,672 at zero', { 'text-anchor': 'start', fill: C.ink, 'font-size': 21, 'font-weight': 700, 'class': 'tnum' });
          var t3 = txt(lay3, b1.x + 22, b0.y + 40, 'Isolated-node rule:', { 'text-anchor': 'start', fill: C.ink2, 'font-size': 19 });
          var t4 = txt(lay3, b1.x + 22, b0.y + 66, 'τ still 0.174', { 'text-anchor': 'start', fill: C.ink2, 'font-size': 19, 'class': 'tnum' });
          if (g.pairLay) tl.to(g.pairLay, { opacity: 0.25, duration: 0.4 }, 0);
          tl.fromTo(colR, { autoAlpha: 0, scaleY: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scaleY: 1, duration: dur(ctx, 0.5), ease: E.out }, 0.1);
          tl.fromTo(bandR, { autoAlpha: 0, scaleX: 0.3, transformOrigin: '0% 50%' }, { autoAlpha: 1, scaleX: 1, duration: dur(ctx, 0.5), ease: E.out }, 0.35);
          tl.fromTo([t1a, t1b, t1l, t2], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, stagger: 0.1 }, 0.6);
          tl.fromTo([t3, t4], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, stagger: 0.1 }, 1.1);
          tl.fromTo([tk, tkt, tie, t1c], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, stagger: 0.12 }, 1.5);
        }
        fadeUp(tl, g.ghost, 1.4, 0.5);
      }
    }
  };
  /* axes of the flat scatter, drawn once the camera has settled (positions from T.project) */
  function drawAxes2(ctx) {
    var g = ctx.g; if (g.axesDone) return; g.axesDone = true;
    var tl = gsap.timeline();
    if (g.T && !g.T.failed) {
      g.T.render();
      var ax = svgEl('g', {}, g.ov), P = function (e, a) { return p2pt(g, e, a); };
      var o = P(0, 0), xr = P(1, 0), yt = P(0, 1), off = 18;
      svgEl('line', { x1: o.x - off, y1: o.y + off, x2: xr.x + 6, y2: xr.y + off, stroke: C.ink3, 'stroke-width': 1.5 }, ax);
      svgEl('line', { x1: o.x - off, y1: o.y + off, x2: yt.x - off, y2: yt.y - 6, stroke: C.ink3, 'stroke-width': 1.5 }, ax);
      [[0, '0'], [0.5, '50'], [1, '100']].forEach(function (t) {
        var px = P(t[0], 0), py = P(0, t[0]);
        svgEl('line', { x1: px.x, x2: px.x, y1: px.y + off - 6, y2: px.y + off + 6, stroke: C.ink3, 'stroke-width': 1.5 }, ax);
        txt(ax, px.x, px.y + off + 30, t[1], { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18, 'class': 'tnum' });
        svgEl('line', { x1: py.x - off - 6, x2: py.x - off + 6, y1: py.y, y2: py.y, stroke: C.ink3, 'stroke-width': 1.5 }, ax);
        txt(ax, py.x - off - 12, py.y + 6, t[1], { 'text-anchor': 'end', fill: C.ink2, 'font-size': 18, 'class': 'tnum' });
      });
      txt(ax, (o.x + xr.x) / 2, o.y + off + 58, 'EndorseRank percentile →', { 'text-anchor': 'middle', fill: C.allow, 'font-size': 22, 'font-weight': 700 });
      txt(ax, yt.x - off, yt.y - 24, '↑ AWP percentile', { 'text-anchor': 'start', fill: C.xfer, 'font-size': 22, 'font-weight': 700 });
      tl.fromTo(ax, { autoAlpha: 0 }, { autoAlpha: 1, duration: dur(ctx, 0.6) }, 0);
    }
    tl.fromTo(g.lg, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.5), ease: E.out }, 0.2);
    return tl;
  }

  /* ================================================================ s08-03
     The calendar of s03-01 (same axis span), the freeze pin and the label window. */
  var AX3 = { left: 96, top: 176, w: 1728, h: 250, axisY: 196 };
  var STRIP = [{ x: 180, h: 52 }, { x: 340, h: 30, a: 1 }, { x: 500, h: 68 }, { x: 660, h: 44, a: 2, s: 1 }, { x: 820, h: 22, s: 1 }];
  var slide3 = {
    id: 's08-03', title: 'Out-of-window test (temporal holdout): freeze and wait', time: 40, steps: 3,
    tags: [],
    notes: [
      'Now the real test, the out-of-window test. The thesis calls it a temporal holdout. The three-year calendar is back. The amber stream is the allowance records of each month, and the sky-blue stream the transfer records.',
      'On 31 March we freeze the scores. We build them only from the records up to that day and do not touch them afterwards. This first temporal holdout, which sets a later period aside and checks the scores against it, is holdout W0. This test has 17,050 spender contracts.',
      'Then we grade each spender contract by what newly happened to it from April to June. There are two labels. One is the number of new allowances between an owner and the spender that did not exist on the freeze date; the other is the number of addresses that sent it a transfer for the first time. 2,070 contracts, 12.1%, gained new approval pairs: the amber dots. 1,695 contracts, 9.9%, gained new transfer senders: the sky-blue rings. Many contracts, 1,173, gained both labels, so many amber dots wear a ring. Only about one contract in ten has a label, so the results depend heavily on how well a score ranks these few contracts near the top.',
      'We ran the same test once more, freezing on 30 June and labeling July to September. This is the registered window W1. This study extracted the logs of these three months only after it had registered the rules. There are 18,152 spender contracts.'
    ],
    html:
      '<h1 class="t-h1">[[Freeze]] the scores, then grade them on what comes next</h1>' +
      '<p class="abs s8-small" style="left:96px;top:154px;color:var(--ink-3)">Out-of-window test = temporal holdout · set a later period aside and predict it</p>' +
      '<div class="abs" id="cal" data-in="none" style="left:' + AX3.left + 'px;top:' + AX3.top + 'px;width:' + AX3.w + 'px;height:' + AX3.h + 'px"></div>' +
      '<div class="abs s8-info" id="i0" data-in="none" style="left:96px;top:470px"><span class="mono">W0</span><span>Holdout · freeze 31 Mar → Apr–Jun · <b class="tnum">17,050</b> spenders</span></div>' +
      '<div class="abs s8-info" id="i1" data-in="none" style="left:96px;top:516px"><span class="mono">W1</span><span>Registered window · freeze 30 Jun → Jul–Sep · <b class="tnum">18,152</b> spenders</span>' + LOCK_SVG + '</div>' +
      '<p class="abs s8-small" id="stripcap" data-in="none" style="left:96px;top:566px;color:var(--ink-3)">Spender contracts · scores stay frozen · example</p>' +
      '<svg class="abs" id="strip" data-in="none" width="960" height="280" viewBox="0 0 960 280" style="left:0;top:600px;overflow:visible"></svg>' +
      '<div class="s8-month" id="mon" data-in="none" style="left:868px;top:566px">Apr</div>' +
      '<div class="abs s8-defs" id="defs" data-in="none" style="left:96px;top:872px;width:880px">' +
        '<div><b class="c-allow">New approval pairs</b>: owner–spender allowances that did not exist at the freeze</div>' +
        '<div><b class="c-xfer">New transfer senders</b>: addresses that sent a transfer for the first time</div>' +
        '<div data-step="3"><span class="lk">' + LOCK_SVG + '</span><b>W1</b>: logs extracted after the registration</div></div>' +
      '<div class="abs" id="wbox" data-in="none" style="left:1040px;top:466px;width:784px;height:480px">' +
        '<div class="s8-wt" id="wt">W0 spender contracts <span class="tnum">17,050</span><small>one dot = 10 contracts</small></div>' +
        '<div class="s8-wc" id="wc"><span><i style="background:#F5B43C"></i>New approval pairs <b id="wa">0</b> <span id="wap">(12.1%)</span></span><span><i style="background:transparent;box-shadow:inset 0 0 0 2.5px #3CC4FF"></i>New senders <b id="ws">0</b> <span id="wsp">(9.9%)</span></span><span><i style="background:#F5B43C;box-shadow:0 0 0 2.5px #3CC4FF"></i>Both</span></div>' +
        '<div id="wf" style="position:absolute;left:0;top:92px"></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var TL = g.TL = Comp.timeline(ctx, q(el, '#cal'), { w: AX3.w, h: AX3.h, axisY: AX3.axisY, padL: 0, padR: 0 });
      var MC = (((DATA.timeline || {}).monthly_counts || {}).revised) || {};
      var monA = (MC.approval_ego || []).map(function (p) { return p[1]; }), monT = (MC.transfer_ego || []).map(function (p) { return p[1]; });
      if (monA.length) g.sA = TL.stream(monA, { color: 'allow', height: 70, base: 92, opacity: 0.24 });
      if (monT.length) g.sT = TL.stream(monT, { color: 'xfer', height: 80, base: AX3.axisY - 6, opacity: 0.24 });
      gsap.set([g.sA && g.sA.g, g.sT && g.sT.g].filter(Boolean), { autoAlpha: 0 });
      /* frost over everything recorded up to t1 */
      var svg = TL.svg, xs = TL.x('2023-10-01'), x1 = TL.x('2026-03-31') + 1.5;
      var defs = svgEl('defs', {}, svg), gr = svgEl('linearGradient', { id: 's8-frost', x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
      svgEl('stop', { offset: '0', 'stop-color': '#E9EDF5', 'stop-opacity': 0.16 }, gr); svgEl('stop', { offset: '1', 'stop-color': '#E9EDF5', 'stop-opacity': 0.06 }, gr);
      g.frost = svgEl('g', {}, svg);
      svgEl('rect', { x: xs, y: 14, width: x1 - xs, height: AX3.axisY - 16, fill: 'url(#s8-frost)', rx: 6 }, g.frost);
      svgEl('line', { x1: x1, x2: x1, y1: 14, y2: AX3.axisY - 2, stroke: '#E9EDF5', 'stroke-width': 2, opacity: 0.7 }, g.frost);
      gsap.set(g.frost, { autoAlpha: 0 });
      g.pin0 = TL.pin('2026-03-31', { y0: 8, label: 't₁ · freeze 31 Mar', color: 'ink', labelSize: 19 });
      g.pin1 = TL.pin('2026-06-30', { y0: 8, label: 'T_obs · 30 Jun', color: 'ink', labelSize: 19 });
      g.pin0.label.setAttribute('text-anchor', 'end'); g.pin0.label.setAttribute('x', TL.x('2026-03-31') - 22); g.pin0.label.setAttribute('y', 14);
      g.pin1.label.setAttribute('text-anchor', 'start'); g.pin1.label.setAttribute('x', TL.x('2026-06-30') + 22); g.pin1.label.setAttribute('y', 14);
      g.band0 = TL.band('2026-04-01', '2026-06-30', { label: 'W0 labels', y0: 40, color: 'ink2' });
      g.band1 = TL.band('2026-07-01', '2026-09-30', { label: 'W1 labels', y0: 40, color: 'ink2' });
      [g.band0, g.band1].forEach(function (B) { if (B.label) { B.label.setAttribute('y', 66); B.label.setAttribute('font-size', 18); } });
      var kids = Array.prototype.slice.call(TL.axis.childNodes);
      g.axisLine = kids[0]; g.ticks = kids.slice(1);
      /* spender strip (illustration): frozen score bars, boxes, sparse new arrivals */
      var sv = q(el, '#strip');
      g.boxes = []; g.bars = []; g.arr = []; g.chips = [];
      var frostS = svgEl('g', {}, sv);
      STRIP.forEach(function (s, k) {
        var bar = svgEl('rect', { x: s.x - 9, y: 90 - s.h, width: 18, height: s.h, rx: 4, fill: C.ink2, opacity: 0.85 }, sv);
        g.bars.push(bar);
        var N = Comp.contract(ctx, sv, { x: s.x, y: 140, size: 56, hidden: true });
        g.boxes.push(N);
      });
      svgEl('rect', { x: 140, y: 10, width: 720, height: 86, rx: 10, fill: 'url(#s8-frost)' }, frostS);
      var sf = svgEl('g', { transform: 'translate(846,24)' }, frostS);
      for (var a = 0; a < 3; a++) { var an = a * Math.PI / 3; svgEl('line', { x1: -Math.cos(an) * 9, y1: -Math.sin(an) * 9, x2: Math.cos(an) * 9, y2: Math.sin(an) * 9, stroke: C.ink, 'stroke-width': 2, 'stroke-linecap': 'round' }, sf); }
      g.frostS = frostS; gsap.set(frostS, { autoAlpha: 0 });
      g.stripLab = q(el, '#stripcap');
      gsap.set(g.bars.concat([g.stripLab]), { autoAlpha: 0 });
      STRIP.forEach(function (s, k) {
        var list = [];
        for (var u = 0; u < (s.a || 0); u++) list.push({ kind: 'allow', from: [s.x - 40 + u * 34, 238], to: [s.x - 12 + u * 18, 176] });
        for (var w = 0; w < (s.s || 0); w++) list.push({ kind: 'xfer', from: [s.x + 64, 232], to: [s.x + 22, 174] });
        list.forEach(function (L) {
          var E0 = Comp.eoa(ctx, sv, { x: L.from[0], y: L.from[1] + 12, r: 9, hidden: true });
          var A = Comp.arrow(ctx, sv, { from: L.from, to: L.to, kind: L.kind, width: 3, head: 12, hidden: true, flow: false });
          g.arr.push({ A: A, N: E0, k: k, kind: L.kind });
        });
        if (s.a || s.s) {
          var chipW = svgEl('g', { transform: 'translate(' + (s.x + 36) + ',' + 128 + ')' }, sv), chip = svgEl('g', {}, chipW);
          var lab = (s.a ? '+' + s.a : '') + (s.a && s.s ? ' ' : '') + (s.s ? '+' + s.s : '');
          var cw = lab.length * 12 + 20;
          svgEl('rect', { x: 0, y: -14, width: cw, height: 28, rx: 14, fill: C.bg3, stroke: '#39435A' }, chip);
          var tt = svgEl('text', { x: cw / 2, y: 7, 'text-anchor': 'middle', 'font-size': 18, 'font-weight': 700, 'class': 'tnum' }, chip);
          if (s.a) { var t1s = svgEl('tspan', { fill: C.allow }, tt); t1s.textContent = '+' + s.a; }
          if (s.s) { var t2s = svgEl('tspan', { fill: C.xfer, dx: s.a ? 6 : 0 }, tt); t2s.textContent = '+' + s.s; }
          gsap.set(chip, { autoAlpha: 0 });
          g.chips.push(chip);
        }
      });
      g.mon = q(el, '#mon'); g.defs = q(el, '#defs'); g.i0 = q(el, '#i0'); g.i1 = q(el, '#i1');
      g.wbox = q(el, '#wbox'); g.wt = q(el, '#wt'); g.wa = q(el, '#wa'); g.ws = q(el, '#ws'); g.wap = q(el, '#wap'); g.wsp = q(el, '#wsp');
      gsap.set([g.mon, g.defs, g.i0, g.i1, g.wbox], { autoAlpha: 0 });
      /* waffle: one dot = 10 spenders; mark 1 = new approval pair only (amber dot), 2 = new sender only
         (sky ring), 3 = both (amber dot with a sky ring). Positions are seeded; the counts are not:
         W0 1,705 dots: both 1,173 → 117, approval only 897 → 90 (amber 207 = 2,070 / 10), sender only 522 → 53 (sky 170 ≈ 1,695 / 10)
         W1 1,815 dots: both 1,023 → 102, approval only 593 → 60 (amber 162 ≈ 1,616 / 10), sender only 510 → 51 (sky 153 = 1,533 / 10)
         overlap = spenders with future_new_approvers > 0 and future_new_transfer_senders > 0 in
         experiments/data/2-processed-tables-and-evaluations/revised-usd/{holdout-w0,window-w1}/spender_scores.part000.parquet */
      var rnd = Deck.util.rng(7);
      function pick(n, both, aOnly, sOnly) {
        var idx = [], i, mark = new Uint8Array(n);
        for (i = 0; i < n; i++) idx.push(i);
        for (i = n - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
        for (i = 0; i < both + aOnly + sOnly; i++) mark[idx[i]] = i < both ? 3 : i < both + aOnly ? 1 : 2;
        return mark;
      }
      g.mark0 = pick(1705, 117, 90, 53); g.mark1 = pick(1815, 102, 60, 51);
      g.wmark = g.mark0;
      g.W = waffle(ctx, q(el, '#wf'), { n: 1705, max: 1860, cols: 62, gap: 12.6, r: 4.3, style: function (i, hq) {
        var m = g.wmark[i];
        if (!m || hq <= 0) return { fill: '#3A4458' };
        var sc = 1 + 0.25 * hq;
        if (m === 1) return { fill: C.allow, scale: sc };
        if (m === 2) return { fill: '#3A4458', stroke: C.xfer, lw: 2, scale: sc };
        return { fill: C.allow, stroke: C.xfer, lw: 2, scale: sc };
      } });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo(g.axisLine, { attr: { x2: g.TL.x('2023-10-01') } }, { attr: { x2: g.TL.x('2026-09-30') }, duration: dur(ctx, 1.0), ease: E.io }, 0.2);
      tl.fromTo(g.ticks, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, stagger: 0.012 }, 0.2);
      if (g.sA) tl.add(function () { ctx.add(function () { g.sA.reveal({ duration: 1.0 }); }); }, 0.6);
      if (g.sT) tl.add(function () { ctx.add(function () { g.sT.reveal({ duration: 1.0 }); }); }, 0.75);
      tl.set([g.sA && g.sA.g, g.sT && g.sT.g].filter(Boolean), { autoAlpha: 1 }, 0.6);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.add(g.pin0.drop(), 0);
        tl.fromTo(g.frost, { autoAlpha: 0, scaleX: 0, transformOrigin: '100% 50%' }, { autoAlpha: 1, scaleX: 1, duration: dur(ctx, 0.9), ease: E.io }, 0.45);
        fadeUp(tl, g.i0, 0.6, 0.5);
        tl.fromTo(g.bars, { autoAlpha: 0, scaleY: 0, transformOrigin: '50% 100%' }, { autoAlpha: 0.85, scaleY: 1, duration: dur(ctx, 0.5), ease: E.out, stagger: 0.07 }, 0.9);
        g.boxes.forEach(function (N, k) { tl.add(N.pop(), 0.95 + k * 0.07); });
        tl.fromTo(g.frostS, { autoAlpha: 0, scaleX: 0, transformOrigin: '100% 50%' }, { autoAlpha: 1, scaleX: 1, duration: dur(ctx, 0.7), ease: E.io }, 1.4);
        tl.fromTo(g.stripLab, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.6);
      }
      if (i === 2) {
        tl.add(g.band0.show(), 0);
        tl.set(g.mon, { autoAlpha: 0.22 }, 0.2);
        tl.call(function () { g.mon.textContent = 'Apr'; }, null, 0.2);
        tl.call(function () { g.mon.textContent = 'May'; }, null, 0.95);
        tl.call(function () { g.mon.textContent = 'Jun'; }, null, 1.7);
        g.arr.forEach(function (R, k) {
          var at = 0.35 + k * 0.32;
          tl.add(R.N.pop(), at);
          tl.add(R.A.draw({ duration: 0.45 }), at + 0.1);
        });
        tl.fromTo(g.chips, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: E.stamp, stagger: 0.25 }, 1.0);
        fadeUp(tl, g.defs, 1.2, 0.5);
        tl.fromTo(g.wbox, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.4);
        tl.add(g.W.fill({ duration: 1.3 }), 0.5);
        tl.add(g.W.wave({ duration: 1.2 }), 1.6);
        tl.add(ctx.count(g.wa, 0, 2070, { decimals: 0, final: '2,070', duration: 1.2 }), 1.6);
        tl.add(ctx.count(g.ws, 0, 1695, { decimals: 0, final: '1,695', duration: 1.2 }), 1.6);
      }
      if (i === 3) {
        tl.add(g.pin1.drop(), 0);
        tl.add(g.band1.show(), 0.4);
        fadeUp(tl, g.i1, 0.6, 0.5);
        tl.call(function () { g.mon.textContent = 'Jul'; }, null, 0.6);
        tl.call(function () { g.mon.textContent = 'Aug'; }, null, 1.1);
        tl.call(function () { g.mon.textContent = 'Sep'; }, null, 1.6);
        tl.add(Comp.swap(ctx, g.wt, 'W1 spender contracts <span class="tnum">18,152</span><small>one dot ≈ 10 contracts</small>'), 0.5);
        tl.call(function () {
          g.wap.textContent = ''; g.wsp.textContent = '';
          g.wmark = g.mark1; g.W.n = 1815; g.W.st.p = 0; g.W.st.q = 0; g.W.draw();
        }, null, 0.9);
        tl.add(function () { ctx.add(function () { g.W.fill({ duration: 1.2 }); g.W.wave({ duration: 1.1, delay: 1.0 }); }); }, 0.95);
        tl.add(ctx.count(g.wa, 2070, 1616, { decimals: 0, final: '1,616', duration: 1.0 }), 1.9);
        tl.add(ctx.count(g.ws, 1695, 1533, { decimals: 0, final: '1,533', duration: 1.0 }), 1.9);
      }
    }
  };

  /* ================================================================ locked board (s08-04 … s08-06) */
  var BD = { tx0: 540, tx1: 1040, td: [0.15, 0.40], tticks: [0.15, 0.2, 0.25, 0.3, 0.35, 0.4], vX: 1062,
    dx0: 1344, dx1: 1800, dd: [-0.06, 0.09], dticks: [-0.05, 0, 0.05],
    groups: [{ top: 252, name: 'W0', s1: 'freeze 31 Mar', s2: 'Apr–Jun labels' }, { top: 400, name: 'W1', s1: 'freeze 30 Jun', s2: 'Jul–Sep labels' }],
    gh: 128, rowOff: [34, 94], gridTop: 246, gridBot: 538, tickY: 566 };
  function bx(v) { return BD.tx0 + (v - BD.td[0]) / (BD.td[1] - BD.td[0]) * (BD.tx1 - BD.tx0); }
  function dxs(v) { return BD.dx0 + (v - BD.dd[0]) / (BD.dd[1] - BD.dd[0]) * (BD.dx1 - BD.dx0); }
  var BOARD_HTML = '<svg class="abs s8-board" id="board" data-shared="s8-board" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0"></svg>' +
    '<svg class="abs s8-bars" id="bars" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible"></svg>';
  function drawBoard(svg) {
    var hd = { fill: C.ink2, 'font-size': 22, 'font-weight': 700 };
    txt(svg, BD.tx0, 214, 'τ: how well it predicted what came later', hd);
    txt(svg, BD.dx0, 214, 'Paired difference Δτ', hd);
    txt(svg, dxs(0) - 10, 240, '← raw count better', { 'text-anchor': 'end', fill: C.ink3, 'font-size': 17 });
    txt(svg, dxs(0) + 10, 240, 'walk score better →', { 'text-anchor': 'start', fill: C.ink3, 'font-size': 17 });
    BD.groups.forEach(function (G) {
      svgEl('rect', { x: 96, y: G.top, width: 1728, height: BD.gh, rx: 16, fill: 'rgba(233,237,245,.028)', stroke: 'rgba(233,237,245,.05)' }, svg);
      txt(svg, 120, G.top + 50, G.name, { fill: C.ink, 'font-size': 30, 'font-weight': 800, 'class': 'svg-mono' });
      txt(svg, 120, G.top + 82, G.s1, { fill: C.ink3, 'font-size': 16 });
      txt(svg, 120, G.top + 106, G.s2, { fill: C.ink3, 'font-size': 16 });
    });
    BD.tticks.forEach(function (t) {
      svgEl('line', { x1: bx(t), x2: bx(t), y1: BD.gridTop, y2: BD.gridBot, stroke: 'rgba(233,237,245,.07)', 'stroke-width': 1 }, svg);
      txt(svg, bx(t), BD.tickY, fmt(t, 2), { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'tnum' });
    });
    svgEl('line', { x1: BD.tx0, x2: BD.tx1, y1: BD.gridBot, y2: BD.gridBot, stroke: C.line, 'stroke-width': 1.5 }, svg);
    BD.dticks.forEach(function (t) {
      if (t !== 0) svgEl('line', { x1: dxs(t), x2: dxs(t), y1: BD.gridTop, y2: BD.gridBot, stroke: 'rgba(233,237,245,.07)', 'stroke-width': 1 }, svg);
      txt(svg, dxs(t), BD.tickY, t === 0 ? '0' : sfmt(t, 2), { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'tnum' });
    });
    svgEl('line', { x1: dxs(0), x2: dxs(0), y1: BD.gridTop - 4, y2: BD.gridBot, stroke: C.ink2, 'stroke-width': 1.6, 'stroke-dasharray': '5 6' }, svg);
    svgEl('line', { x1: BD.dx0, x2: BD.dx1, y1: BD.gridBot, y2: BD.gridBot, stroke: C.line, 'stroke-width': 1.5 }, svg);
  }
  /* rows of one window: rows = [{label, color, dashed, val, from}], diff = {val, ghost} */
  function boardGroup(svg, gi, rows, diff) {
    var G = BD.groups[gi], out = { rows: [], diff: null, ghost: null };
    rows.forEach(function (r, k) {
      var y = G.top + BD.rowOff[k], d = iv(r.val);
      var lab = svgEl('g', {}, svg);
      svgEl('line', { x1: 240, x2: 270, y1: y, y2: y, stroke: r.color, 'stroke-width': 5, 'stroke-linecap': 'round' }, lab);
      var sw = svgEl('circle', { cx: 255, cy: y, r: 8, fill: r.dashed ? C.bg : r.color, stroke: r.color, 'stroke-width': 2.5, 'stroke-dasharray': r.dashed ? '3.5 3' : null }, lab);
      if (r.dashed) svgEl('circle', { cx: 255, cy: y, r: 3.4, fill: r.color }, lab);
      void sw;
      txt(lab, 286, y + 8, r.label, { fill: C.ink, 'font-size': 24, 'font-weight': 600 });
      var B = ivBar(svg, { scale: bx, y: y, est: d.est, lo: d.lo, hi: d.hi, color: r.color, dashed: r.dashed, from: r.from != null ? r.from : BD.td[0], width: 6, r: 11 });
      var vt = svgEl('text', { x: BD.vX, y: y + 8, 'font-size': 24, 'class': 'tnum' }, svg);
      var e1 = svgEl('tspan', { fill: r.color, 'font-weight': 800 }, vt); e1.textContent = estOf(r.val);
      var e2 = svgEl('tspan', { fill: C.ink3, 'font-size': 19, dx: 8 }, vt); e2.textContent = ciOf(r.val);
      gsap.set([lab, vt], { autoAlpha: 0 });
      out.rows.push({ lab: lab, B: B, vt: vt, est: e1, ci: e2, d: d });
    });
    if (diff) {
      var y = G.top + 64, d = iv(diff.val);
      out.diff = { B: ivBar(svg, { scale: dxs, y: diff.ghost ? y - 6 : y, est: d.est, lo: d.lo, hi: d.hi, color: diff.color || C.ink, width: 7, r: 12, from: 0 }), d: d };
      var x = d.est < 0 ? dxs(0) - 14 : dxs(0) + 14;
      var vt = svgEl('text', { x: x, y: y - 26, 'text-anchor': d.est < 0 ? 'end' : 'start', 'font-size': 24, 'class': 'tnum', stroke: '#0E1119', 'stroke-width': 8, 'stroke-linejoin': 'round', 'paint-order': 'stroke' }, svg);
      var e1 = svgEl('tspan', { fill: C.ink, 'font-weight': 800 }, vt); e1.textContent = estOf(diff.val);
      var e2 = svgEl('tspan', { fill: C.ink3, 'font-size': 18, dx: 8 }, vt); e2.textContent = ciOf(diff.val);
      gsap.set(vt, { autoAlpha: 0 });
      out.diff.vt = vt; out.diff.est = e1;
      if (diff.ghost) {
        var gd = iv(diff.ghost);
        out.ghost = ivBar(svg, { scale: dxs, y: y + 16, est: gd.est, lo: gd.lo, hi: gd.hi, color: C.ink3, hollow: true, width: 3, r: 7, from: gd.est, opacity: 0.85 });
      }
    }
    return out;
  }
  function growGroup(ctx, tl, Gr, at, opt) {
    opt = opt || {};
    Gr.rows.forEach(function (R, k) {
      var t = at + k * (opt.stagger != null ? opt.stagger : 0.18);
      tl.fromTo(R.lab, { autoAlpha: 0, x: -14 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.35), ease: E.out }, t);
      tl.add(R.B.grow(ctx, { duration: opt.duration || 0.8 }), t + 0.05);
      tl.set(R.vt, { autoAlpha: 1 }, t + 0.1);
      tl.add(ctx.count(R.est, BD.td[0], R.d.est, { decimals: 3, final: estOf(R.est.textContent), duration: opt.duration || 0.8 }), t + 0.1);
    });
  }
  function growDiff(ctx, tl, Gr, at, opt) {
    opt = opt || {};
    var D = Gr.diff; if (!D) return;
    tl.add(D.B.grow(ctx, { duration: opt.duration || 0.9 }), at);
    tl.set(D.vt, { autoAlpha: 1 }, at + 0.1);
    var fin = D.est.textContent;
    tl.add(ctx.count(D.est, 0, D.d.est, { decimals: 3, final: fin, format: function (v) { return sfmt(v, 3); }, duration: opt.duration || 0.9 }), at + 0.1);
  }
  function showGhost(ctx, tl, Gr, at) {
    if (!Gr.ghost) return;
    tl.set(Gr.ghost.g, { autoAlpha: 1 }, at);
    Gr.ghost.showNow(); gsap.set(Gr.ghost.g, { autoAlpha: 0 });
    tl.fromTo(Gr.ghost.g, { autoAlpha: 0, scale: 0.6, svgOrigin: dxs(Gr.ghost.o.est) + ' ' + Gr.ghost.o.y }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.35), ease: E.stamp }, at);
  }
  /* an extra contrast row below the board, on the Δ scale */
  function extraRow(svg, y, label, val, color, sub) {
    var g = svgEl('g', {}, svg), d = iv(val);
    svgEl('rect', { x: 700, y: y - 26, width: 1124, height: 52, rx: 14, fill: 'rgba(233,237,245,.028)', stroke: 'rgba(233,237,245,.05)' }, g);
    svgEl('line', { x1: dxs(0), x2: dxs(0), y1: y - 20, y2: y + 20, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, g);
    txt(g, 724, sub ? y - 2 : y + 8, label, { fill: C.ink, 'font-size': 21, 'font-weight': 600 });
    if (sub) txt(g, 724, y + 19, sub, { fill: C.ink3, 'font-size': 16 });
    var vt = svgEl('text', { x: BD.dx0 - 22, y: y + 8, 'text-anchor': 'end', 'font-size': 23, 'class': 'tnum' }, g);
    var e1 = svgEl('tspan', { fill: C.ink, 'font-weight': 800 }, vt); e1.textContent = estOf(val);
    var e2 = svgEl('tspan', { fill: C.ink3, 'font-size': 18, dx: 8 }, vt); e2.textContent = ciOf(val);
    var B = ivBar(g, { scale: dxs, y: y, est: d.est, lo: d.lo, hi: d.hi, color: color || C.ink, width: 6, r: 10, from: 0 });
    gsap.set(g, { autoAlpha: 0 });
    return { g: g, B: B, show: function (ctx, tl, at) { tl.fromTo(g, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.4), ease: E.out }, at); tl.add(B.grow(ctx, { duration: 0.8 }), at + 0.15); } };
  }
  function boardBuild(el, ctx) {
    var g = ctx.g = {};
    g.board = q(el, '#board'); g.bars = q(el, '#bars');
    drawBoard(g.board);
    return g;
  }
  function boardEnter(el, ctx) { settleShared(ctx, ctx.g.board, 's8-board', 0.2); }

  /* ================================================================ s08-04 transfer side */
  var slide4 = {
    id: 's08-04', title: 'Transfer side: AWP beats the raw count', time: 40, steps: 4,
    tags: function (s) { return s >= 4 ? ['posthoc', 'registered-analysis'] : ['posthoc']; },
    notes: [
      'First, the transfer side. The left panel shows how well each score predicted what happened later. The right panel shows the difference between the two scores, paired on the same contracts. If the difference lies right of 0, the walk score is better; if it lies left of 0, the plain count is better.',
      'In predicting the addresses that will newly send transfers, AWP reaches 0.346 in W0, and the transfer in-degree, which simply counts the addresses that sent transfers, reaches 0.303.',
      'The paired difference is 0.043, and the whole interval lies right of 0.',
      'In W1, AWP was again 0.022 higher, and again the interval lies above 0. On the transfer side, the time and value weights and a walk that restarts at active senders added information that the plain count does not have.',
      'Looking only at the 14,094 contracts that had received a transfer, the difference held, at 0.056. The gray hollow dots are the values of the registered analysis, and they point the same way. But these comparisons were in neither the plan nor the registration; they were computed after the labels were known.'
    ],
    html:
      '<h1 class="t-h1">Predicting new senders: AWP beats [[the count]]</h1>' + BOARD_HTML +
      '<p class="abs s8-concl" id="concl" data-in="none" style="left:96px;top:720px;width:1728px">On the transfer side, the walk (time and value weights, activity restarts) added information to the count</p>' +
      '<div class="abs s8-tiny" id="tiny" data-in="none" style="left:96px;top:800px;width:1728px">' + pill('posthoc') + '<span>In neither the plan nor the registration: computed after the labels were known · new-sender label · spenders W0 17,050, W1 18,152</span></div>' +
      '<div class="abs s8-tiny" id="gleg" data-in="none" style="left:96px;top:850px;width:1728px">' + pill('registered-analysis') + '<span>Gray hollow dots = registered analysis (raw base units, all tokens): <b>+0.038 [0.035, 0.042]</b> · <b>+0.020 [0.016, 0.023]</b>: same direction</span></div>',
    build: function (el, ctx) {
      var g = boardBuild(el, ctx), svg = g.bars;
      var rowsW0 = [{ label: 'AWP', color: C.xfer, val: '0.346 [0.336, 0.356]' }, { label: 'Transfer in-degree', color: C.deg, dashed: true, val: '0.303 [0.292, 0.315]' }];
      var rowsW1 = [{ label: 'AWP', color: C.xfer, val: '0.330 [0.321, 0.340]' }, { label: 'Transfer in-degree', color: C.deg, dashed: true, val: '0.308 [0.299, 0.319]' }];
      g.G0 = boardGroup(svg, 0, rowsW0, { val: '+0.043 [0.038, 0.048]', ghost: '+0.038 [0.035, 0.042]' });
      g.G1 = boardGroup(svg, 1, rowsW1, { val: '+0.022 [0.017, 0.027]', ghost: '+0.020 [0.016, 0.023]' });
      g.ex = extraRow(svg, 640, 'Only prior transfer recipients', '+0.056 [0.049, 0.064]', C.ink, 'W0 · 14,094 contracts · new senders');
      g.concl = q(el, '#concl'); g.tiny = q(el, '#tiny'); g.gleg = q(el, '#gleg');
      gsap.set([g.concl, g.tiny, g.gleg], { autoAlpha: 0 });
    },
    enter: boardEnter,
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) growGroup(ctx, tl, g.G0, 0.1);
      if (i === 2) growDiff(ctx, tl, g.G0, 0.1);
      if (i === 3) { growGroup(ctx, tl, g.G1, 0, { duration: 0.6, stagger: 0.12 }); growDiff(ctx, tl, g.G1, 0.55, { duration: 0.6 }); fadeUp(tl, g.concl, 1.3, 0.5); }
      if (i === 4) {
        g.ex.show(ctx, tl, 0);
        showGhost(ctx, tl, g.G0, 0.8); showGhost(ctx, tl, g.G1, 0.95);
        fadeUp(tl, [g.tiny, g.gleg], 0.9, 0.5, 0.15);
      }
    }
  };

  /* ================================================================ s08-05 allowance side */
  var slide5 = {
    id: 's08-05', title: 'Allowance side: the raw count wins', time: 50, steps: 5,
    tags: function (s) { return s >= 5 ? ['posthoc', 'registered-analysis'] : s >= 4 ? ['posthoc', 'example'] : ['posthoc']; },
    notes: [
      'Now the allowance side. Here I will report the result just as it is. The panels are the same as on the previous slide.',
      'In predicting which contracts will gain new approval pairs, the in-approve degree reaches 0.250 in W0, and EndorseRank 0.231.',
      'The paired difference is −0.019, and the whole interval lies left of 0. EndorseRank did worse than simply counting the owners that approved the contract.',
      'In W1 it was also lower, by 0.034, and again below 0. In both windows the plain count won.',
      'Contracts that already have many owners also gain more new owners, and the plain count captures this most directly. The picture on the left is an illustrative example.',
      'Still, the allowance-side score predicted new approval pairs better than AWP, the transfer-side score: 0.035 higher in W0 and 0.065 higher in W1. These comparisons, too, were all computed after the labels were known, and the registered analysis points the same way.'
    ],
    html:
      '<h1 class="t-h1">Predicting new approval pairs: <span class="s8-hl" id="hl">the count</span> won</h1>' + BOARD_HTML +
      '<div class="s8-fig" id="rich" data-in="none" style="left:96px;top:612px;width:560px;height:330px"><div class="cap">Rich get richer: owners attract owners</div><span class="ex example-mark">Example</span><svg id="richsv" width="560" height="330" viewBox="0 0 560 330"></svg></div>' +
      '<p class="abs s8-concl" id="concl" data-in="none" style="left:700px;top:716px;width:1124px">EndorseRank with uniform restarts did not beat the owner count</p>' +
      '<p class="abs s8-reason" id="reason" data-in="none" style="left:700px;top:796px;width:1124px">Contracts with many owners gain more new owners: <b>the count captures this directly</b></p>' +
      '<div class="abs s8-tiny" id="tiny" data-in="none" style="left:700px;top:870px;width:1124px">' + pill('posthoc') + '<span>Transfer recipients: <b>−0.013 [−0.020, −0.006]</b> · registered analysis <b>−0.011</b>, <b>−0.029</b> (gray)</span></div>',
    build: function (el, ctx) {
      var g = boardBuild(el, ctx), svg = g.bars;
      var rowsW0 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: '0.250 [0.237, 0.262]' }, { label: 'EndorseRank', color: C.allow, val: '0.231 [0.220, 0.242]' }];
      var rowsW1 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: '0.268 [0.257, 0.279]' }, { label: 'EndorseRank', color: C.allow, val: '0.234 [0.222, 0.244]' }];
      g.G0 = boardGroup(svg, 0, rowsW0, { val: '−0.019 [−0.026, −0.011]', ghost: '−0.011 [−0.016, −0.006]' });
      g.G1 = boardGroup(svg, 1, rowsW1, { val: '−0.034 [−0.038, −0.029]', ghost: '−0.029 [−0.032, −0.025]' });
      g.ex0 = extraRow(svg, 606, 'EndorseRank − AWP', '+0.035 [0.019, 0.051]', C.allow, 'W0 · new approval pairs');
      g.ex1 = extraRow(svg, 662, 'EndorseRank − AWP', '+0.065 [0.051, 0.081]', C.allow, 'W1 · new approval pairs');
      g.hl = q(el, '#hl'); g.rich = q(el, '#rich'); g.concl = q(el, '#concl'); g.reason = q(el, '#reason'); g.tiny = q(el, '#tiny');
      gsap.set([g.rich, g.concl, g.reason, g.tiny], { autoAlpha: 0 });
      /* rich-get-richer: two spenders, owners around them, new owners drift in (3 : 1) */
      var rs = q(el, '#richsv');
      g.rA = Comp.contract(ctx, rs, { x: 160, y: 196, size: 58 }); g.rB = Comp.contract(ctx, rs, { x: 410, y: 196, size: 58 });
      var own = [];
      function ring(cx, cy, k, R) { for (var i = 0; i < k; i++) { var a = -Math.PI / 2 + i / k * Math.PI * 2; own.push(Comp.eoa(ctx, rs, { x: cx + Math.cos(a) * R, y: cy + Math.sin(a) * R, r: 9 })); } }
      ring(160, 196, 7, 92); ring(410, 196, 2, 92);
      g.own = own;
      g.cnt = [txt(rs, 160, 316, '7 owners', { 'text-anchor': 'middle', fill: C.deg, 'font-size': 20, 'font-weight': 700 }), txt(rs, 410, 316, '2 owners', { 'text-anchor': 'middle', fill: C.deg, 'font-size': 20, 'font-weight': 700 })];
      g.news = [];
      [[160, 196, -150], [160, 196, -30], [160, 196, 160], [410, 196, 20]].forEach(function (p, k) {
        var a = p[2] * Math.PI / 180, R = 60;
        var n = svgEl('circle', { cx: p[0] + Math.cos(a) * 260, cy: p[1] + Math.sin(a) * 140, r: 9, fill: C.bg, stroke: C.allow, 'stroke-width': 2.5 }, rs);
        gsap.set(n, { autoAlpha: 0 });
        g.news.push({ el: n, tx: p[0] + Math.cos(a) * R, ty: p[1] + Math.sin(a) * R, tgt: k < 3 ? 0 : 1 });
      });
    },
    enter: boardEnter,
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) growGroup(ctx, tl, g.G0, 0.1);
      if (i === 2) {
        growDiff(ctx, tl, g.G0, 0.1);
        tl.call(function () { g.hl.classList.add('hl'); g.hl.style.setProperty('--hl-x', ctx.reduced ? '1' : '0'); }, null, 0.6);
        tl.fromTo(g.hl, { color: C.ink }, { color: C.hi, duration: dur(ctx, 0.4) }, 0.6);
        tl.fromTo(g.hl, { '--hl-x': 0 }, { '--hl-x': 1, duration: dur(ctx, 0.55), ease: 'power2.inOut' }, 0.75);
      }
      if (i === 3) { growGroup(ctx, tl, g.G1, 0, { duration: 0.6, stagger: 0.12 }); growDiff(ctx, tl, g.G1, 0.55, { duration: 0.6 }); fadeUp(tl, g.concl, 1.3, 0.5); }
      if (i === 4) {
        fadeUp(tl, g.rich, 0, 0.5);
        g.news.forEach(function (N, k) {
          var at = 0.6 + k * 0.32;
          tl.fromTo(N.el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, at);
          tl.to(N.el, { attr: { cx: N.tx, cy: N.ty }, duration: dur(ctx, 0.7), ease: 'power2.inOut' }, at + 0.1);
        });
        tl.add(ctx.count(g.cnt[0], 7, 10, { decimals: 0, format: function (v) { return Math.round(v) + ' owners'; }, final: '10 owners (+3)', duration: 1.0 }), 1.0);
        tl.add(ctx.count(g.cnt[1], 2, 3, { decimals: 0, format: function (v) { return Math.round(v) + ' owners'; }, final: '3 owners (+1)', duration: 0.6 }), 1.7);
        fadeUp(tl, g.reason, 0.4, 0.5);
      }
      if (i === 5) {
        g.ex0.show(ctx, tl, 0); g.ex1.show(ctx, tl, 0.25);
        showGhost(ctx, tl, g.G0, 0.9); showGhost(ctx, tl, g.G1, 1.05);
        fadeUp(tl, g.tiny, 1.0, 0.5);
      }
    }
  };

  /* ================================================================ s08-06 restart rule only (post hoc hypothesis) */
  var slide6 = {
    id: 's08-06', title: 'Change only the restart rule? (post hoc, hypothesis)', time: 45, steps: 5,
    tags: function (s) { return s >= 1 ? ['posthoc', 'example'] : ['posthoc']; },
    notes: [
      'So what would we have to change to beat the count?',
      'We changed only the restart rule, to AWP’s. The walk now restarts more often at owners that approve actively. An owner’s activity X_u is the sum, over the spenders that owner approved, of the time weight of the latest approval. It is the activity that AWP measures on transfers, applied in the same way to allowances. The paths of the walk stay the same; only the shares of the starting points change. The rain in the picture on the left is the teleportation. It falls more heavily on active owners.',
      'In W0 this variant reaches 0.308, above the in-approve degree at 0.250. The difference is 0.059. The dashed outline marks the variant, and the small hollow ring is where the original EndorseRank sat.',
      'In W1 it was also ahead, by 0.027.',
      'But we chose this comparison after we had seen the labels, so it cannot count as a finding. That is why it gets a hypothesis tag, not a verdict stamp. It is the first candidate to register and test on a new window in the next study.',
      'The analysis plan only said to report this variant alongside; it did not fix a comparison with the count. This variant also agrees less with the same-window allowance proxies: it drops from 0.585 to 0.426. And on the AWP side, we did not test a change of restart rule.'
    ],
    html:
      '<h1 class="t-h1">With AWP’s restarts it beat the count, but it is a [[hypothesis]]</h1>' + BOARD_HTML +
      '<div class="s8-fig" id="rain" data-in="none" style="left:96px;top:612px;width:560px;height:330px"><div class="cap">Teleport rain: heavier on active owners</div><span class="ex example-mark">Example</span><svg id="rainsv" width="560" height="330" viewBox="0 0 560 330"></svg></div>' +
      '<div class="abs s8-reason" id="def" data-in="none" style="left:700px;top:612px;width:1124px"><b class="c-allow">EndorseRank (activity restarts)</b>: restarts more often at active owners · $\\pi_u=X_u\\big/\\sum_v X_v$<br><span style="font-size:21px;line-height:30px;color:var(--ink-3)">$X_u$ = sum of the time weights of u’s latest approvals, one per spender (AWP’s activity, applied to allowances)</span></div>' +
      '<div class="s8-hyp" id="hyp" data-in="none" style="left:700px;top:706px"><svg width="240" height="84" viewBox="0 0 240 84"></svg></div>' +
      '<div class="abs s8-reason" id="hyptx" data-in="none" style="left:964px;top:710px;width:860px">Chosen after seeing the labels: a hypothesis, not a finding<br><span style="font-size:22px;color:var(--ink-3)">→ to be checked in the next registered test</span></div>' +
      '<div class="abs s8-tiny" id="tiny" data-in="none" style="left:700px;top:818px;width:1124px;flex-direction:column;align-items:flex-start;gap:2px">' +
        '<div>In exchange, same-window agreement with the allowance family drops: <b>0.585 → 0.426 [0.418, 0.435]</b></div>' +
        '<div>The analysis plan only said to ‘report’ this variant alongside; it fixed no comparison with the count</div>' +
        '<div>On the AWP side, no change of restart rule was tested</div></div>',
    build: function (el, ctx) {
      var g = boardBuild(el, ctx), svg = g.bars;
      var rowsW0 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: '0.250 [0.237, 0.262]' }, { label: 'EndorseRank variant', color: C.allow, dashed: true, val: '0.308 [0.299, 0.319]', from: 0.231 }];
      var rowsW1 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: '0.268 [0.257, 0.279]' }, { label: 'EndorseRank variant', color: C.allow, dashed: true, val: '0.295 [0.285, 0.304]', from: 0.234 }];
      g.G0 = boardGroup(svg, 0, rowsW0, { val: '+0.059 [0.050, 0.067]', color: C.ink });
      g.G1 = boardGroup(svg, 1, rowsW1, { val: '+0.027 [0.021, 0.034]', color: C.ink });
      /* where the uniform-restart EndorseRank sat (0.231 / 0.234): small hollow amber ring */
      g.orig = [[0, 0.231], [1, 0.234]].map(function (p) {
        var y = BD.groups[p[0]].top + BD.rowOff[1];
        var gg = svgEl('g', {}, svg);
        svgEl('circle', { cx: bx(p[1]), cy: y, r: 7, fill: 'none', stroke: C.allow, 'stroke-width': 2, opacity: 0.8 }, gg);
        txt(gg, bx(p[1]), y + 30, 'original ' + fmt(p[1], 3), { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 16, 'class': 'tnum' });
        gsap.set(gg, { autoAlpha: 0 });
        return gg;
      });
      g.rain = q(el, '#rain'); g.def = q(el, '#def'); g.hyp = q(el, '#hyp'); g.hyptx = q(el, '#hyptx'); g.tiny = q(el, '#tiny');
      gsap.set([g.rain, g.def, g.hyp, g.hyptx, g.tiny], { autoAlpha: 0 });
      /* hypothesis tag: hollow outline, drawn slowly (not a stamp) */
      var hs = q(g.hyp, 'svg');
      g.hypRect = svgEl('rect', { x: 3, y: 3, width: 234, height: 78, rx: 16, fill: 'none', stroke: C.hi, 'stroke-width': 3, 'stroke-dasharray': '10 7' }, hs);
      g.hypText = txt(hs, 142, 53, 'Hypothesis', { 'text-anchor': 'middle', fill: C.hi, 'font-size': 30, 'font-weight': 800 });
      var eye = svgEl('g', { transform: 'translate(14,27) scale(1.5)', fill: 'none', stroke: C.hi, 'stroke-width': 1.6 }, hs);
      eye.innerHTML = '<path d="M1.8 10S5 4.6 10 4.6 18.2 10 18.2 10 15 15.4 10 15.4 1.8 10 1.8 10z"/><circle cx="10" cy="10" r="2.6"/>';
      /* restart rain: six owners, rain proportional to activeness X_u */
      var rs = q(el, '#rainsv');
      var OW = [{ x: 70, X: 1 }, { x: 150, X: 6 }, { x: 230, X: 1 }, { x: 310, X: 2 }, { x: 390, X: 7 }, { x: 470, X: 1 }];
      var sum = OW.reduce(function (a, o) { return a + o.X; }, 0);
      g.drops = []; g.owners = [];
      var rnd = Deck.util.rng(11);
      OW.forEach(function (o, k) {
        var N = Comp.eoa(ctx, rs, { x: o.x, y: 270, r: 12 });
        var halo = svgEl('circle', { cx: o.x, cy: 270, r: 12 + 16 * o.X / 7, fill: C.allow, opacity: 0.0 }, rs);
        rs.insertBefore(halo, rs.firstChild);
        g.owners.push({ N: N, halo: halo, X: o.X });
        var nd = Math.max(1, Math.round(18 * o.X / sum * 6 / 2));
        for (var d = 0; d < nd; d++) {
          var dx = o.x + (rnd() - 0.5) * 26, delay = rnd();
          var dr = svgEl('line', { x1: dx, x2: dx, y1: 60, y2: 74, stroke: C.ink, 'stroke-width': 2.2, 'stroke-linecap': 'round', opacity: 0 }, rs);
          g.drops.push({ el: dr, d: delay, k: k });
        }
      });
      g.pin = txt(rs, 280, 318, 'Thick ring = active owner = more teleport rain', { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17 });
      ctx.katex(g.def);
    },
    enter: boardEnter,
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        fadeUp(tl, g.rain, 0, 0.5);
        fadeUp(tl, g.def, 0.2, 0.5);
        g.owners.forEach(function (O, k) { tl.to(O.halo, { opacity: 0.12 + 0.36 * O.X / 7, duration: 0.6 }, 0.4 + k * 0.05); });
        g.drops.forEach(function (D) {
          for (var c = 0; c < 2; c++) {
            var at = 0.6 + c * 0.9 + D.d * 0.8;
            tl.fromTo(D.el, { attr: { y1: 50, y2: 64 }, opacity: 0 }, { attr: { y1: c ? 214 : 236, y2: c ? 228 : 250 }, opacity: c ? 0.55 : 0.75, duration: dur(ctx, 0.55), ease: 'power1.in' }, at);
            if (!c) tl.to(D.el, { opacity: 0, duration: 0.12 }, at + 0.55);
          }
        });
      }
      if (i === 2) {
        growGroup(ctx, tl, g.G0, 0.1);
        tl.fromTo(g.orig[0], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.3);
        growDiff(ctx, tl, g.G0, 1.0);
      }
      if (i === 3) {
        growGroup(ctx, tl, g.G1, 0, { duration: 0.6, stagger: 0.12 });
        tl.fromTo(g.orig[1], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.15);
        growDiff(ctx, tl, g.G1, 0.6, { duration: 0.6 });
      }
      if (i === 4) {
        tl.set(g.hyp, { autoAlpha: 1 }, 0);
        var L = 2 * (234 + 78);
        tl.fromTo(g.hypRect, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur(ctx, 1.4), ease: 'power1.inOut', onComplete: function () { g.hypRect.style.strokeDasharray = '10 7'; g.hypRect.style.strokeDashoffset = '0'; } }, 0.1);
        tl.fromTo([g.hypText, q(g.hyp, 'g')], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.6 }, 1.0);
        fadeUp(tl, g.hyptx, 1.1, 0.6);
      }
      if (i === 5) fadeUp(tl, g.tiny, 0.1, 0.5);
    }
  };

  /* ================================================================ s08-07 closed form */
  var SWX = 96, SWY = 236;
  var SWV = (PRM.worked_example || {}).stationary || [0.1375, 0.2154, 0.1765, 0.4706];
  var slide7 = {
    id: 's08-07', title: '닫힌 식: 엔도스랭크는 사실 무엇을 계산할까', time: 60, steps: 6,
    tags: function (s) { return s === 5 ? ['example'] : s >= 6 ? ['thesis-example', 'example'] : ['thesis-example']; },
    notes: [
      '왜 엔도스랭크가 그냥 센 수를 못 이겼는지, 식으로 들여다볼게요. 다시 작은 세계예요. 컵의 물은 오래 걸었을 때 각 점에 머무는 몫이에요.',
      '먼저 c부터 정할게요. c는 모든 점이 매번 똑같이 받는 몫이에요. 다시 출발 몫과 매달린 점 몫을 더한 거예요. A처럼 들어오는 화살표가 없는 점은 이것만 받으니까 점수가 바로 c예요. 작은 세계에서 c는 0.15 더하기 0.85 곱하기 0.4706을 4로 나눈 0.1375이고, A의 컵과 같아요.',
      '모든 점의 균형식은 c에서 시작하고, 화살표로 들어온 몫을 더해요. 대부분의 스펜더는 허락을 받지 않는 주인들에게서만 허락을 받아요. 그런 주인의 점수는 c니까, 스펜더의 균형식에서 주인 u의 몫 r_u 자리에 c를 넣어요.',
      'c는 모든 주인에게 같으니까 합 밖으로 꺼낼 수 있어요. 그러면 c 더하기 c 곱하기 d 곱하기 델타가 되고, c로 묶으면 c 곱하기 괄호 1 더하기 d 곱하기 델타라는 짧은 식이 돼요. 델타는 주인마다 자기 허락 무게 가운데 이 스펜더에게 간 조각을 더한 것이에요. B로 확인해 볼게요. A는 무게 3 가운데 2를 B에 줬으니 3분의 2, 그래서 0.2154가 나와요.',
      'C도 0.1765로 맞아요. 그런데 D는 이 식이 안 맞아요. D의 주인 B와 C가 허락을 받으니까, 한 단계 더 퍼진 몫이 들어와요. 그래서 D는 균형식 그대로 계산해서 0.4706이에요.',
      '델타를 예로 볼게요. 주인 셋이 각각 스펜더 1곳, 2곳, 4곳을 허락했다면, 그냥 센 수는 3이지만 델타는 1 더하기 2분의 1 더하기 4분의 1, 1.75예요.',
      'c와 d는 모든 한 단계 스펜더에 같으니까, 점수의 순서는 델타의 순서와 같아요. d가 얼마든 상관없어요. 그러니까 엔도스랭크는 사실상 주인 수를, 주인이 허락한 곳의 무게로 나눠 센 값이에요. 그런 스펜더에게는 나이와 금액 무게, 그리고 이 나눗셈 말고는 센 수와 다를 것이 거의 없어요. 퍼뜨려서 더할 정보가 없는 셈이에요. 실제 같은 기간 그래프에서 c는 7.64 곱하기 10의 마이너스 8제곱이에요.'
    ],
    html:
      '<h1 class="t-h1">엔도스랭크 ≈ [[나눠 센]] 허락 수</h1>' +
      '<p class="abs s8-sub" style="left:96px;top:156px">주인들이 허락을 받지 않는 스펜더(한 단계 스펜더)라면</p>' +
      '<div class="abs" id="swhost" data-in="none" style="left:0;top:0;width:1px;height:1px"></div>' +
      '<svg class="abs" id="swov" data-in="none" width="900" height="760" viewBox="0 0 900 760" style="left:0;top:200px;overflow:visible"></svg>' +
      '<div class="abs s8-d" id="eq" data-in="none" style="left:980px;top:204px;width:844px"></div>' +
      '<div class="s8-symrow" id="syms" data-in="none" style="left:96px;top:832px"></div>' +
      '<svg class="abs s8-pie" id="pie" data-in="none" width="880" height="620" viewBox="0 0 880 620" style="left:96px;top:226px;overflow:visible"></svg>' +
      '<div class="abs s8-hero" id="concl" data-in="none" style="left:96px;top:856px;width:860px">주인이 여러 곳을 허락할수록 한 곳에 가는 몫이 작아져요<br><span style="font-size:22px;color:var(--ink-3)">→ 센 수와 순서가 달라져요 · 실제 같은 기간 그래프: c = 7.64 × 10<sup>−8</sup></span></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = Comp.smallWorld(ctx, q(el, '#swhost'), { x: SWX, y: SWY, cups: { dy: 92, w: 50, h: 60, max: 0.8, decimals: 4, color: C.ink }, shared: 's8-sw' });
      g.W.wrap.setAttribute('data-in', 'none');
      ['A', 'B', 'C', 'D'].forEach(function (id, k) { g.W.cups[id].set(SWV[k], { duration: 0 }); });
      /* overlay chips (stage coords → overlay at top 200) */
      var ov = q(el, '#swov'), OY = 200;
      function nodeXY(id) { var n = Comp.SMALL_WORLD.nodes.filter(function (m) { return m.id === id; })[0]; return { x: SWX + n.x, y: SWY + n.y - OY }; }
      g.nodeXY = nodeXY;
      var A = nodeXY('A');
      g.ringA = svgEl('circle', { cx: A.x, cy: A.y, r: 34, fill: 'none', stroke: C.ink, 'stroke-width': 2.5, 'stroke-dasharray': '6 6' }, ov);
      g.ringTx = txt(ov, A.x, A.y - 48, '들어오는 화살표 없음', { 'text-anchor': 'middle', fill: C.ink, 'font-size': 19, 'font-weight': 700 });
      gsap.set([g.ringA, g.ringTx], { autoAlpha: 0 });
      function chip(id, label, dy, col) {
        var p = nodeXY(id), gw = svgEl('g', { transform: 'translate(' + p.x + ',' + (p.y + dy) + ')' }, ov), gg = svgEl('g', {}, gw);
        var w = label.length * 19 + 26;
        svgEl('rect', { x: -w / 2, y: -15, width: w, height: 30, rx: 15, fill: C.bg3, stroke: col || '#39435A', 'stroke-width': 1.5 }, gg);
        txt(gg, 0, 7, label, { 'text-anchor': 'middle', fill: col || C.ink, 'font-size': 19, 'font-weight': 700 });
        gsap.set(gg, { autoAlpha: 0 });
        return gg;
      }
      g.chipB = chip('B', '한 단계', -62, C.allow); g.chipC = chip('C', '한 단계', -62, C.allow); g.chipD = chip('D', '더 깊음', -62, C.ink2);
      g.chipA = chip('A', 'c', 0, C.ink); g.chipA.parentNode.setAttribute('transform', 'translate(' + (A.x - 66) + ',' + A.y + ')');
      /* derivation panel */
      g.D = Comp.derive(ctx, q(el, '#eq'), { head: '닫힌 식 만들기 · 논문 5장', lines: [
        { tex: 'c=\\dfrac{1-d+d\\,r_D}{|V|}', note: 'c = 모든 점이 매번 똑같이 받는 몫(다시 출발 몫 + 매달린 점 몫)<br>들어오는 화살표가 없는 점은 이것만 받아요 → 점수 = c<br>작은 세계: $c=\\tfrac{0.15+0.85\\times0.4706}{4}=0.1375=r_A$ ✓' },
        { tex: 'r_v=c+d\\sum_{u}\\part{rc}{c}\\,\\dfrac{w(u,v)}{o(u)}', note: '모든 점: c + 화살표로 들어온 몫 · 주인 u가 모두 그런 점이면 $r_u$ 자리에 c를 넣어요', mark: 'rc' },
        { tex: 'r_v=c+c\\,d\\,\\part{dl}{\\delta(v)}=c\\,\\bigl(1+d\\,\\delta(v)\\bigr)', note: 'c는 모든 u에 같아서 합 밖으로 → 남은 합 $\\delta(v)=\\sum_u w(u,v)/o(u)$ → c로 묶어요', mark: 'dl' },
        { tex: 'r_B=0.1375\\times\\bigl(1+0.85\\times\\part{f}{\\tfrac23}\\bigr)=0.2154\\ \\checkmark', note: 'B의 주인은 A 하나: A의 무게 3 가운데 2가 B로', mark: 'f' },
        { tex: '\\begin{aligned}r_C&=0.1375\\times\\bigl(1+0.85\\times\\tfrac13\\bigr)=0.1765\\ \\checkmark\\\\ r_D&=c+d\\,(r_B+r_C)=0.4706\\end{aligned}', note: 'D는 식이 안 맞아요: 주인 B, C가 허락을 받으니까 → 한 단계 더 퍼진 몫' },
        { tex: '\\text{점수 순서}=\\delta(v)\\ \\text{순서}', note: 'c와 d는 모든 한 단계 스펜더에 같아요 → d가 얼마든 순서는 δ가 정해요', mark: null }
      ] });
      ctx.katex(q(el, '#eq'));
      /* symbol cards */
      var syms = q(el, '#syms');
      g.symC = Comp.symbolCard(ctx, syms, { tex: 'c', desc: '모든 점이 매번 똑같이 받는 몫 · 화살표가 안 들어오는 점의 점수' });
      g.symD = Comp.symbolCard(ctx, syms, { tex: '\\delta(v)', desc: '주인마다 나눠 준 조각의 합' });
      g.syms = syms;
      /* pie example (step 5) */
      var pie = q(el, '#pie');
      g.pie = pie; gsap.set(pie, { autoAlpha: 0 });
      txt(pie, 0, 18, '예시 · 주인 셋, 스펜더 v', { fill: C.ink3, 'font-size': 18, 'class': 'svg-mono' });
      var V = { x: 560, y: 300 };
      g.vBox = Comp.contract(ctx, pie, { x: V.x, y: V.y, size: 64, label: 'v' });
      var OWN = [{ y: 120, k: 1 }, { y: 300, k: 2 }, { y: 480, k: 4 }];
      g.pies = [];
      OWN.forEach(function (o, j) {
        var gg = svgEl('g', {}, pie), cx = 230, cy = o.y, R = 46;
        Comp.eoa(ctx, gg, { x: 70, y: cy, r: 14 });
        svgEl('line', { x1: 86, x2: cx - R - 10, y1: cy, y2: cy, stroke: C.ink3, 'stroke-width': 1.5, 'stroke-dasharray': '3 4' }, gg);
        for (var s = 0; s < o.k; s++) {
          var a0 = -Math.PI / 2 + s / o.k * Math.PI * 2, a1 = -Math.PI / 2 + (s + 1) / o.k * Math.PI * 2;
          var d = o.k === 1 ? 'M' + (cx - R) + ',' + cy + ' a' + R + ',' + R + ' 0 1,0 ' + (2 * R) + ',0 a' + R + ',' + R + ' 0 1,0 ' + (-2 * R) + ',0' :
            'M' + cx + ',' + cy + ' L' + (cx + Math.cos(a0) * R) + ',' + (cy + Math.sin(a0) * R) + ' A' + R + ',' + R + ' 0 ' + (a1 - a0 > Math.PI ? 1 : 0) + ',1 ' + (cx + Math.cos(a1) * R) + ',' + (cy + Math.sin(a1) * R) + ' Z';
          svgEl('path', { d: d, fill: s === 0 ? C.allow : '#2A3242', stroke: C.bg, 'stroke-width': 2, opacity: s === 0 ? 0.95 : 1 }, gg);
        }
        txt(gg, cx, cy + R + 28, o.k === 1 ? '스펜더 1곳 허락' : '스펜더 ' + o.k + '곳 허락', { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18 });
        var frac = o.k === 1 ? '1' : '1/' + o.k;
        var A = Comp.arrow(ctx, gg, { from: [cx + R + 12, cy], to: [V.x - 40, V.y + (cy - V.y) * 0.18], kind: 'allow', width: 3, head: 12, label: frac, labelOffset: 18, labelSize: 22, hidden: true });
        var fly = svgEl('rect', { x: cx - 18, y: cy - 10, width: 36, height: 20, rx: 4, fill: C.allow, opacity: 0 }, pie);
        g.pies.push({ g: gg, A: A, fly: fly, k: o.k });
        gsap.set(gg, { autoAlpha: 0 });
      });
      /* δ gauge and tally */
      var GX = 680, G0 = 520, U = 200;
      svgEl('rect', { x: GX - 22, y: G0 - 2 * U, width: 44, height: 2 * U, rx: 8, fill: 'none', stroke: '#39435A', 'stroke-width': 1.5 }, pie);
      [0, 1, 2].forEach(function (t) { svgEl('line', { x1: GX - 30, x2: GX - 22, y1: G0 - t * U, y2: G0 - t * U, stroke: C.ink3, 'stroke-width': 1.5 }, pie); txt(pie, GX - 36, G0 - t * U + 6, String(t), { 'text-anchor': 'end', fill: C.ink3, 'font-size': 16, 'class': 'tnum' }); });
      g.segLab = [];
      g.seg = [1, 0.5, 0.25].map(function (v, j) {
        var top = G0 - U * [1, 1.5, 1.75][j];
        var r = svgEl('rect', { x: GX - 20, y: top, width: 40, height: v * U - 3, rx: 5, fill: C.allow, opacity: [0.95, 0.75, 0.55][j] }, pie);
        var lb = txt(pie, GX + 32, top + v * U / 2 + 7, ['1', '½', '¼'][j], { fill: C.allow, 'font-size': 21, 'font-weight': 700 });
        gsap.set([r, lb], { autoAlpha: 0 });
        g.segLab.push(lb);
        return r;
      });
      g.gT = txt(pie, GX, G0 + 36, 'δ = 0', { 'text-anchor': 'middle', fill: C.allow, 'font-size': 24, 'font-weight': 800, 'class': 'tnum' });
      g.gT2 = txt(pie, GX, G0 + 64, '나눠 센 수', { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18 });
      g.tal = Comp.tally(ctx, pie, { x: 800, y: G0 - 46, size: 40 });
      g.talT = txt(pie, 820, G0 + 36, '센 수 3', { 'text-anchor': 'middle', fill: C.deg, 'font-size': 24, 'font-weight': 800 });
      g.talT2 = txt(pie, 820, G0 + 64, '그냥 센 수', { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18 });
      gsap.set([g.gT, g.gT2, g.tal.g, g.talT, g.talT2], { autoAlpha: 0 });
      g.GX = GX; g.G0 = G0; g.U = U;
      g.concl = q(el, '#concl'); gsap.set(g.concl, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo(g.W.wrap, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.6), ease: E.out }, 0.2);
      tl.fromTo(g.D.el, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.6), ease: E.out }, 0.35);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      function edge(a, b) { return g.W.edge(a, b); }
      function glowEdges(list, at) {
        list.forEach(function (E2) { var A = edge(E2[0], E2[1]); if (A) tl.fromTo(A.strands, { attr: { 'stroke-width': 9 } }, { attr: { 'stroke-width': +A.strands[0].getAttribute('stroke-width') || 4 }, duration: dur(ctx, 1.0), ease: 'power2.out' }, at); });
      }
      function pulseCup(id, at) { var cu = g.W.cups[id]; tl.fromTo(cu.g, { scale: 1.25, transformOrigin: '50% 50%' }, { scale: 1, duration: dur(ctx, 0.6), ease: E.out }, at); }
      if (i === 1) {
        tl.fromTo(g.ringA, { autoAlpha: 0, scale: 0.6, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.4), ease: E.stamp }, 0);
        tl.fromTo(g.ringTx, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.2);
        tl.add(g.D.show(1), 0.2);
        tl.fromTo(g.chipA, { autoAlpha: 0, scale: 0.6, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.35), ease: E.stamp }, 1.0);
        pulseCup('A', 1.1);
        tl.add(g.symC.pop(), 1.3);
      }
      if (i === 2) {
        tl.to([g.ringA, g.ringTx], { autoAlpha: 0.35, duration: 0.3 }, 0);
        glowEdges([['A', 'B'], ['A', 'C']], 0.1);
        tl.add(g.D.show(2), 0.2);
        tl.fromTo([g.chipB, g.chipC], { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.35), ease: E.stamp, stagger: 0.1 }, 0.8);
      }
      if (i === 3) {
        tl.add(g.D.show(3), 0);
        tl.add(g.symD.pop(), 0.8);
        tl.add(function () { ctx.add(function () { g.D.show(4); }); }, 1.6);
        glowEdges([['A', 'B']], 1.7);
        pulseCup('B', 2.0);
      }
      if (i === 4) {
        tl.add(g.D.show(5), 0);
        pulseCup('C', 0.4);
        glowEdges([['B', 'D'], ['C', 'D']], 0.9);
        tl.fromTo(g.chipD, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.35), ease: E.stamp }, 1.0);
        pulseCup('D', 1.2);
      }
      if (i === 5) {
        tl.to([g.W.wrap, q(el, '#swov')], { autoAlpha: 0, duration: dur(ctx, 0.5) }, 0);
        tl.to(g.syms, { autoAlpha: 0, duration: dur(ctx, 0.4) }, 0);
        tl.set(g.pie, { autoAlpha: 1 }, 0.3);
        g.pies.forEach(function (P, j) {
          var at = 0.4 + j * 0.2;
          tl.fromTo(P.g, { autoAlpha: 0, x: -20 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.4), ease: E.out }, at);
          tl.add(P.A.draw({ duration: 0.5 }), at + 0.3);
        });
        tl.add(g.vBox.pop(), 0.5);
        var vals = [1, 1.5, 1.75];
        g.pies.forEach(function (P, j) {
          var at = 1.6 + j * 0.55, seg = g.seg[j];
          var sb = seg.getBBox ? null : null; void sb;
          tl.set(P.fly, { opacity: 1 }, at);
          tl.fromTo(P.fly, { x: 0, y: 0 }, { x: (g.GX - 20) - (+P.fly.getAttribute('x')), y: (+seg.getAttribute('y')) - (+P.fly.getAttribute('y')), duration: dur(ctx, 0.5), ease: 'power2.inOut' }, at);
          tl.set(P.fly, { opacity: 0 }, at + 0.5);
          tl.fromTo(seg, { autoAlpha: 0, scaleY: 0, transformOrigin: '50% 100%' }, { autoAlpha: 1, scaleY: 1, duration: dur(ctx, 0.3), ease: E.out }, at + 0.45);
          tl.fromTo(g.segLab[j], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, at + 0.5);
          tl.call(function () { g.gT.textContent = 'δ = ' + ['1', '1.5', '1.75'][j]; }, null, at + 0.5);
          void vals;
        });
        tl.set(g.gT, { autoAlpha: 1 }, 1.6);
        tl.fromTo(g.gT2, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 2.2);
        tl.set(g.tal.g, { autoAlpha: 1 }, 3.4);
        tl.add(g.tal.add(3, { stagger: 0.2 }), 3.4);
        tl.fromTo([g.talT, g.talT2], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 4.0);
      }
      if (i === 6) {
        tl.add(g.D.show(6), 0);
        fadeUp(tl, g.concl, 0.6, 0.5);
      }
    }
  };

  /* ================================================================ s08-08 how well the closed form fits + one-page summary */
  var CF = { spenders: 14406, d1: 12039, deeper: 2367 };
  var slide8 = {
    id: 's08-08', title: '닫힌 식은 얼마나 맞을까, 그리고 결과 한 장', time: 45, steps: 4,
    tags: function (s) { return s >= 4 ? ['posthoc', 'registered-analysis'] : []; },
    notes: [
      '이 식이 실제 그래프에서 얼마나 맞는지 확인했어요. 점 하나가 같은 기간 스펜더 10개예요.',
      '같은 기간의 스펜더 14,406개 가운데 12,039개가 한 단계 스펜더였어요. 진한 호박색이 한 단계, 옅은 색과 장미색 테두리가 더 깊은 스펜더예요.',
      '한 단계 스펜더는 하나도 빠짐없이 식과 1% 안으로 맞았어요. 나머지 더 깊은 스펜더 2,367개는 26.4%만 맞았는데, 이것은 여러 단계로 퍼지는 몫이 실제로 있다는 뜻이에요. 모두 합치면 87.9%, W0에서는 73.7%예요.',
      '그런데 그 퍼짐이 있는데도 엔도스랭크는 그냥 센 수를 넘지 못했어요.',
      '아래는 원시 차수와의 비교 네 개를 한 장에 모은 거예요. 송금 쪽은 걷기가 이기고 허락 쪽은 센 수가 이겨요. 처음 등록한 분석의 회색 표식도 네 방향이 모두 같아요. 네 비교 모두 라벨을 본 뒤에 계산했어요.'
    ],
    html:
      '<h1 class="t-h1">한 단계 스펜더는 [[모두]] 식대로예요</h1>' +
      '<div class="abs" id="top" data-in="none" style="left:0;top:0;width:1920px;height:820px">' +
        '<div class="abs s8-leg" id="leg" style="left:96px;top:186px"><span><i style="background:#F5B43C"></i>한 단계 · 1% 안</span><span><i style="background:rgba(245,180,60,.42)"></i>더 깊음 · 1% 안</span><span><i style="background:transparent;border:2px solid #FF6B8A;width:12px;height:12px"></i>더 깊음 · 1% 밖</span><span class="ink-3">점 하나 = 스펜더 10개 · 같은 기간</span></div>' +
        '<div id="wf8" style="position:absolute;left:96px;top:232px"></div>' +
        '<div class="abs s8-cnt" id="cnt" style="left:1330px;top:226px;width:494px">' +
          '<div class="row"><span>같은 기간 스펜더</span><b>14,406</b></div>' +
          '<div class="row"><span>한 단계 <b>12,039</b>개 → 1% 안</span><span class="pc" id="c1">0%</span></div>' +
          '<div class="row"><span>더 깊은 <b>2,367</b>개 → 1% 안</span><span class="pc" id="c2" style="color:rgba(245,180,60,.75)">0%</span></div>' +
          '<div class="row" style="border-bottom:0"><span>모두</span><span class="pc" id="c3" style="color:var(--ink)">0%</span></div>' +
          '<div id="w0l" style="font-size:21px;color:var(--ink-3);margin-top:6px">W0: 스펜더 <b>17,032</b>개 · 모두 <b>73.7%</b></div>' +
        '</div>' +
        '<p class="abs s8-concl" id="concl" style="left:96px;top:700px;width:1700px">퍼짐은 있었지만, 엔도스랭크가 센 수를 넘게 해 주지는 못했어요</p>' +
      '</div>' +
      '<div class="abs s8-reason" id="mini" data-in="none" style="left:720px;top:214px;width:1100px">식과 1% 안으로 맞은 스펜더(같은 기간)<br><b class="c-allow tnum">한 단계 100%</b> · <b class="tnum" style="color:rgba(245,180,60,.8)">더 깊음 26.4%</b> · <b class="tnum">모두 87.9%</b><br><span style="font-size:22px;color:var(--ink-3)">퍼짐은 있었지만, 센 수를 넘게 해 주지는 못했어요</span></div>' +
      '<div class="abs" id="sum" data-in="none" style="left:96px;top:478px;width:1728px">' +
        '<div class="s8-sumhd">원시 차수와의 비교 넷 — 수정 분석과 등록 분석의 방향이 모두 같아요</div>' +
        '<div class="s8-tiny" style="margin:4px 0 0">' + pill('posthoc') + '<span>모두 라벨을 본 뒤 계산 · 색 점 = 수정 분석(본 결과) · 회색 빈 점 = 등록 분석</span></div>' +
        '<div id="fp" style="margin-top:6px"></div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.top = q(el, '#top'); g.leg = q(el, '#leg'); g.mini = q(el, '#mini'); g.cnt = q(el, '#cnt'); g.concl = q(el, '#concl'); g.sum = q(el, '#sum'); g.w0l = q(el, '#w0l');
      g.c1 = q(el, '#c1'); g.c2 = q(el, '#c2'); g.c3 = q(el, '#c3');
      gsap.set([g.cnt, g.concl, g.sum, g.w0l, g.mini], { autoAlpha: 0 });
      /* 1,441 dots: 1,204 depth-one (12,039/10), 63 deeper within 1 % (2,367 × 0.2645 / 10), 174 deeper outside */
      var N1 = Math.round(CF.d1 / 10), NIN = Math.round(CF.deeper * 0.26447 / 10), NT = Math.round(CF.spenders / 10), NOUT = NT - N1 - NIN;
      g.N1 = N1; g.NIN = NIN; g.NOUT = NOUT;
      g.WF = waffle(ctx, q(el, '#wf8'), { n: NT, max: NT, cols: 64, gap: 18.2, r: 6.2, style: function (i, hq) {
        if (i < N1) return { fill: C.allow };
        if (i < N1 + NIN) return { fill: 'rgba(245,180,60,.42)' };
        return { fill: C.bg2, stroke: C.hi, lw: 1.8 };
      } });
      g.F = Comp.forest(ctx, q(el, '#fp'), { w: 1728, rowH: 86, labelWidth: 470, valueWidth: 300, domain: [-0.05, 0.06], ticks: [-0.04, -0.02, 0, 0.02, 0.04, 0.06], hidden: true,
        tickFormat: function (t) { return t === 0 ? '0' : sfmt(t, 2); }, axisLabel: '짝지은 차이 Δτ (← 그냥 센 수가 나음 · 걷는 점수가 나음 →)',
        rows: [
          { label: 'AWP − 송금 입차수', sub: 'W0 · 새 송금자', est: 0.043, lo: 0.038, hi: 0.048, color: 'xfer', text: '+0.043 [0.038, 0.048]', ghost: { est: 0.038, lo: 0.035, hi: 0.042 } },
          { label: 'AWP − 송금 입차수', sub: 'W1 · 새 송금자', est: 0.022, lo: 0.017, hi: 0.027, color: 'xfer', text: '+0.022 [0.017, 0.027]', ghost: { est: 0.020, lo: 0.016, hi: 0.023 } },
          { label: '엔도스랭크 − 받은 허락 수', sub: 'W0 · 새 허락 쌍', est: -0.019, lo: -0.026, hi: -0.011, color: 'allow', text: '−0.019 [−0.026, −0.011]', ghost: { est: -0.011, lo: -0.016, hi: -0.006 } },
          { label: '엔도스랭크 − 받은 허락 수', sub: 'W1 · 새 허락 쌍', est: -0.034, lo: -0.038, hi: -0.029, color: 'allow', text: '−0.034 [−0.038, −0.029]', ghost: { est: -0.029, lo: -0.032, hi: -0.025 } }
        ] });
    },
    enter: function (el, ctx) {
      var tl = ctx.tl(), g = ctx.g;
      tl.fromTo(g.leg, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.3);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.add(g.WF.fill({ duration: 1.4 }), 0);
        fadeUp(tl, g.cnt, 0.3, 0.5);
      }
      if (i === 2) {
        tl.add(ctx.count(g.c1, 0, 100, { decimals: 0, suffix: '%', final: '100%', duration: 1.0 }), 0);
        tl.add(ctx.count(g.c2, 0, 26.4, { decimals: 1, suffix: '%', final: '26.4%', duration: 1.0 }), 0.35);
        tl.add(ctx.count(g.c3, 0, 87.9, { decimals: 1, suffix: '%', final: '87.9%', duration: 1.0 }), 0.7);
        fadeUp(tl, g.w0l, 1.4, 0.4);
      }
      if (i === 3) fadeUp(tl, g.concl, 0.1, 0.5);
      if (i === 4) {
        tl.to([g.cnt, g.concl], { autoAlpha: 0, duration: 0.3 }, 0);
        tl.to(g.top, { scale: 0.5, transformOrigin: '96px 186px', duration: dur(ctx, 0.9), ease: E.io }, 0.1);
        tl.to(g.leg, { autoAlpha: 0, duration: 0.3 }, 0.1);
        fadeUp(tl, g.mini, 0.8, 0.5);
        tl.fromTo(g.sum, { autoAlpha: 0, y: 60 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.7), ease: E.out }, 0.5);
        tl.add(g.F.grow({ stagger: 0.22 }), 1.0);
      }
    }
  };

  Deck.section({
    id: 's08-results',
    title: '결과',
    slides: [slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8]
  });
})();
