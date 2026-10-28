/* =========================================================================
   s08-results — Results, English edition (STORYBOARD.md §2, s08-01 … s08-08)

   s08-01  Same window (RQ2)        3 × 3 board (score × family); own-family cells light up with a
                                    mirror; swapped cells and their paired differences; C-PR slides into
                                    the empty middle row; an expandable popover for λ = 1, λ = 0, S-PR
   s08-02  Two different orders     the two rows of s08-01 burst into 6,483 particles (three.js) that
           (RQ1)                    gather into the λ = 1 cloud of s06-04; the camera rises and the points
                                    slide into a rank–rank scatter (EndorseRank × AWP percentile); diagonal,
                                    τ_b count-up, 30 flashed pairs (illustration) and a gauge stopping at
                                    39.8 %; the two zero blocks
   s08-03  Out-of-window test       the calendar of s03-01 returns with the monthly streams of the score
           (RQ4 design)             window; freeze pin + frost over the 12-month score window; label window
                                    plays (month watermark), sparse new arrows into spender boxes; waffle
                                    (one dot = 10 spenders) with the gained-label shares; W1 with a lock,
                                    frost and streams move to the T_obs score window
   s08-04  Transfer side            locked board (data-shared "s8-board", same axes on s08-04 … s08-06):
   s08-05  Allowance side           left τ panel, right paired-difference panel with a dashed zero line;
   s08-06  Restart rule only        ghost markers = registered analysis; "rich get richer" loop; restart
                                    rain; hollow rings where uniform EndorseRank sat; a hollow "Still below"
                                    tag drawn slowly (not a verdict stamp)
   s08-07  Closed form              small world (thesis Ch. 2) + 6-line derivation of
                                    r_v = c(1 + d δ(v)); pie example δ = 1 + ½ + ¼ = 1.75 vs count 3
   s08-08  How well it fits         waffle of 6,224 spenders (one dot = 10), counters, then the summary
                                    board of the four raw-degree contrasts with registered ghosts

   Numbers and sources (R = revised digest experiments/data/3-published-results-for-thesis/
   revised-usd-12m/results_digest.md = the thesis's main analysis; G = registered digest results_digest.md).
   Every number below is read from DECK_DATA.results (R → .revised, G → .registered) with the value as
   fallback, and rounded with toFixed, as the thesis tables are.
     s08-01  families τ_b [95%]           R same_window.families.{endorserank,awp,cpr_l50,cpr_l100,cpr_l0,spr}
             +0.333 [0.311, 0.354]         R same_window contrast EndorseRank − AWP, allowance family
             +0.539 [0.518, 0.560]         R same_window contrast AWP − EndorseRank, transfer family
             6,483                         R same_window.cohort
     s08-02  0.199 [0.181, 0.221]          R inter_method.endorserank_vs_awp; isolated 0.199 (…isolated)
             21,011,403 · 96.4 % · 39.8 %  R concordance.pairs / share_ordered_by_both / discordant_share
             197 · 1,192                   R ties.endorserank.zeros / ties.awp.zeros (thesis Ch. 4)
             0.217 [0.209, 0.225]          G inter_method.endorserank_vs_awp (registered analysis)
             points: DECK_DATA.contracts pct.endorserank / pct.awp (mid-rank percentiles, all 6,483);
             zero blocks at the lowest percentile of each score (≈ 1.5 and ≈ 9.2), from the same arrays
     s08-03  7,914 · 1,732 · 1,422         R w0.spenders / gained_new_approvals / gained_new_senders
             (21.9 %, 18.0 % = DECK_DATA.holdout.w0 base rates, as in thesis Ch. 4); 7,960 · 1,495 · 1,371  R w1
             both labels 1,044 (W0) / 967 (W1): counted from
             revised-usd-12m/{holdout-w0,window-w1}/spender_scores.part000.parquet
             score windows DECK_DATA.timeline.anchors.score_window_t1 / score_window_tobs;
             streams timeline.monthly_counts.revised.{approval,transfer}_ego_t1 (W0) and _ego (W1)
     s08-04  0.409 · 0.447 · −0.038        R w0.taus.awp / taus.t1_in_degree (new senders) / AWP minus t1 in-degree
             0.398 · 0.439 · −0.041        R w1.spender_taus.awp / .in_degree / endorserank_results.awp_minus_degree_send
             6,489 · −0.051                R w0.receiving.n / receiving AWP minus t1 in-degree
             ghosts +0.038, +0.020         G w0 AWP minus t1 in-degree, G w1 endorserank_results.awp_minus_degree_send
     s08-05  0.392 · 0.303 · −0.090        R w0.taus.t1_in_approve_degree / taus.endorserank / EndorseRank minus t1 in-approve degree
             0.381 · 0.299 · −0.082        R w1.spender_taus.* / endorserank_results.endorserank_minus_degree_appr
             +0.107, +0.142                R supplementary w0/w1.er_minus_awp_appr
             −0.087 · 0.299 / 0.328        R w0.receiving contrast and taus (EndorseRank / AWP, new approval pairs)
             1,342 · 1,425                 R w0.coverage.spenders_without_transfer_edge; 7,914 − 6,489 (calculated)
             ghosts −0.011, −0.029         G w0 / w1 EndorseRank minus in-approve degree
     s08-06  0.332 · 0.335                 R w0.taus / w1.spender_taus .endorserank_activity (new approval pairs)
             −0.060, −0.046                R supplementary w0/w1.er_activity_minus_degree_appr
             rings 0.303 / 0.299, −0.090 / −0.082   uniform EndorseRank (s08-05)
             0.560 → 0.601 [0.590, 0.613]  R same_window.families.endorserank / endorserank_activity (.allowance)
             0.366 · 0.409 · 0.447         R w0.taus.cpr_l0 / awp / t1_in_degree (new senders)
     s08-07  0.1375, 0.2154, 0.1765, 0.4706  thesis Ch. 2 worked example (DECK_DATA.params.worked_example),
             re-derived with the closed form (Ch. 5, Eq. closed-form); c = 1.93 × 10⁻⁷  R same_window.closed_form.common_value_c
             pie 1, ½, ¼ → 1.75 = example
     s08-08  6,224 · 5,232 · 100 % · 21.9 % · 87.5 % · τ 0.908   R same_window.closed_form.*
             992 = 6,224 − 5,232 (calculated); W0 7,905 · 70.8 %  R w0.closed_form.*
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

  /* ------------------------------------------------------------ numbers (DECK_DATA.results)
     toFixed rounds the stored binary value exactly, as the thesis tables do; Intl rounding of a
     four-digit half such as 0.2135 would drift by 0.001. Each fallback is the same value as text. */
  var RES = DATA.results || {}, RV = RES.revised || {}, RG = RES.registered || {};
  var SW = RV.same_window || {}, W0 = RV.w0 || {}, W1 = RV.w1 || {}, SUP = RV.supplementary || {};
  function get(o, path, dflt) {
    var v = o, p = path.split('.');
    for (var i = 0; i < p.length; i++) { if (v == null) return dflt; v = v[p[i]]; }
    return v == null ? dflt : v;
  }
  function fx(v, d) { var s = (+v).toFixed(d); return /^-0(\.0+)?$/.test(s) ? s.slice(1) : s; }
  function m3(v) { return fx(v, 3).replace(/^-/, '−'); }
  function s3(v) { return (v > 0 ? '+' : '') + m3(v); }
  function pc1(v) { return fx(Number(fx(v, 3)) * 100, 1); }
  function ivx(a, signed) {
    if (a && a.d) a = a.d;
    if (!a || a.length < 3 || a[0] == null) return null;
    return (signed ? s3(a[0]) : m3(a[0])) + ' [' + m3(a[1]) + ', ' + m3(a[2]) + ']';
  }
  function IV(o, path, fb, signed) { return ivx(get(o, path), signed) || fb; }
  function findC(list, a, b, outcome) {
    list = list || [];
    for (var i = 0; i < list.length; i++) {
      var c = list[i];
      if (String(c.a) === String(a) && String(c.b) === String(b) && (!outcome || c.outcome === outcome)) return c;
    }
    return null;
  }
  function CV(list, a, b, outcome, fb) { return ivx(findC(list, a, b, outcome), true) || fb; }
  function n0(v) { return fmt(v, 0); }
  var NUM = {
    cohort: get(SW, 'cohort', 6483),
    sp0: get(W0, 'spenders', 7914), sp1: get(W1, 'spenders', 7960),
    ga0: get(W0, 'gained_new_approvals', 1732), gs0: get(W0, 'gained_new_senders', 1422),
    ga1: get(W1, 'gained_new_approvals', 1495), gs1: get(W1, 'gained_new_senders', 1371),
    recv0: get(W0, 'receiving.n', 6489),
    noXfer0: get(W0, 'coverage.spenders_without_transfer_edge', 1342)
  };
  NUM.notRecv0 = NUM.sp0 - NUM.recv0;

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
    '.s8-cap{font-size:28px;line-height:42px;font-weight:600;color:var(--ink)}',
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
    '.s8-symrow .sym-card .sym-desc{font-size:19px;line-height:27px;max-width:400px}',
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
  function fam1(m, fb) {
    var F = 'families.' + m + '.';
    return { t: IV(SW, F + 'transfer', fb[0]), a: IV(SW, F + 'allowance', fb[1]), s: IV(SW, F + 'sybil_stability', fb[2]) };
  }
  var ROWS1 = {
    er:  { name: 'EndorseRank', sub: 'Walks the allowance edges', col: C.allow, own: 'a', y: G1.yER,
           v: fam1('endorserank', ['0.196 [0.180, 0.216]', '0.560 [0.548, 0.571]', '0.026 [0.012, 0.041]']) },
    cpr: { name: 'C-PR (λ = 0.5)', sub: 'Walks both edge types, mixed', col: C.cpr, own: null, y: G1.yMid,
           v: fam1('cpr_l50', ['0.400 [0.385, 0.416]', '0.449 [0.437, 0.463]', '0.142 [0.128, 0.156]']) },
    awp: { name: 'AWP', sub: 'Walks the transfer edges', col: C.xfer, own: 't', y: G1.yAWP,
           v: fam1('awp', ['0.736 [0.728, 0.744]', '0.226 [0.210, 0.245]', '0.419 [0.408, 0.434]']) }
  };
  var EXTRA1 = [
    ['C-PR (λ = 1) · allowance layer', fam1('cpr_l100', ['0.196 [0.180, 0.216]', '0.561 [0.550, 0.572]', '0.028 [0.014, 0.042]'])],
    ['C-PR (λ = 0) · transfer layer', fam1('cpr_l0', ['0.700 [0.691, 0.709]', '0.194 [0.178, 0.213]', '0.402 [0.389, 0.417]'])],
    ['S-PR', fam1('spr', ['0.671 [0.661, 0.681]', '0.289 [0.272, 0.308]', '0.398 [0.386, 0.414]'])]
  ].map(function (r) { return [r[0], r[1].t, r[1].a, r[1].s]; });
  var DIFF1 = { t: CV(SW.contrasts, ['awp', 'transfer'], ['endorserank', 'transfer'], null, '+0.539 [0.518, 0.560]'),
                a: CV(SW.contrasts, ['endorserank', 'allowance'], ['awp', 'allowance'], null, '+0.333 [0.311, 0.354]') };
  function e1(key, f) { return estOf(ROWS1[key].v[f]); }
  var MINI = { x0: 26, x1: 434, d0: -0.05, d1: 0.80, y: 22 };
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
      'Now the results. First, the same-window check. The scores and the proxies all come from the twelve months up to 30 June 2026. The rows are scores and the columns are proxy families. The darker a cell, the larger Kendall’s tau. I will leave the middle row empty for a moment.',
      'EndorseRank agrees best with the allowance proxies, at ' + e1('er', 'a') + ', and AWP with the transfer proxies, at ' + e1('awp', 't') + '. The two cells with the mirror mark are each score’s own family.',
      'Swap them and the values drop sharply, to ' + e1('er', 't') + ' and ' + e1('awp', 'a') + '. If we pair the two scores on the same proxies and subtract, the difference is ' + estOf(DIFF1.t).replace('+', '') + ' on the transfer side and ' + estOf(DIFF1.a).replace('+', '') + ' on the allowance side, with narrow intervals. These differences were not comparisons fixed in advance.',
      'C-PR, which mixes the two edge types, lies between the two rows on every family at λ = 0.5: ' + e1('cpr', 't') + ' on transfer, ' + e1('cpr', 'a') + ' on allowance and ' + e1('cpr', 's') + ' on Sybil stability. The small markers under the cells show where EndorseRank and AWP sit. The button at the bottom right also shows the values for λ = 1, λ = 0 and S-PR.',
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
      s += '<p class="abs s8-small" id="fam" data-in="none" style="left:96px;top:850px;width:1728px">Kendall’s τ<sub>b</sub> · family mean = mean τ of the family’s proxies, e.g. transfer family $=\\tfrac12\\bigl(\\tau_{\\text{in-degree}}+\\tau_{\\text{in-value}}\\bigr)$ · 95% interval · matched cohort of ' + n0(NUM.cohort) + ' contracts</p>';
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
        tl.call(function () { g.cap.innerHTML = 'EndorseRank × allowance family <b class="tnum c-allow">' + e1('er', 'a') + '</b> · AWP × transfer family <b class="tnum c-xfer">' + e1('awp', 't') + '</b>: highest on their own family'; }, null, 1.2);
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
        tl.add(Comp.swap(ctx, g.cap, 'Swapped, they are much lower: <b class="tnum">' + e1('er', 't') + '</b> · <b class="tnum">' + e1('awp', 'a') + '</b> · differences about ' + fx(iv(DIFF1.t).est, 1) + ' and ' + fx(iv(DIFF1.a).est, 1) + pill(NOT_PLANNED)), 0.3);
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
        tl.add(Comp.swap(ctx, g.cap, 'C-PR (λ = 0.5) lies <b>between the two rows</b> on every family: transfer <b class="tnum">' + e1('cpr', 't') + '</b> · allowance <b class="tnum">' + e1('cpr', 'a') + '</b> · Sybil <b class="tnum">' + e1('cpr', 's') + '</b>'), 0.4);
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
  /* the zero blocks: n from the thesis tie counts; their mid-rank percentiles and extents are
     recomputed from DECK_DATA.contracts below (fallbacks = the values of the 6,483-contract cohort) */
  var ER_ZERO = { pct: 0.0151, n: get(SW, 'ties.endorserank.zeros', 197), lo: 0.0919, hi: 0.9645 };
  var AWP_ZERO = { pct: 0.0919, n: get(SW, 'ties.awp.zeros', 1192), lo: 0.0151, hi: 0.9995 };
  var CONC = get(SW, 'inter_method.concordance', {});
  var T2 = {
    tau: IV(SW, 'inter_method.endorserank_vs_awp', '0.199 [0.181, 0.221]'),
    iso: IV(SW, 'inter_method.isolated', '0.199 [0.181, 0.221]'),
    reg: IV(RG, 'same_window.inter_method.endorserank_vs_awp', '0.217 [0.209, 0.225]'),
    pairs: CONC.pairs || 21011403,
    both: pc1(CONC.share_ordered_by_both != null ? CONC.share_ordered_by_both : 0.9644),
    disc: pc1(CONC.discordant_share_of_ordered != null ? CONC.discordant_share_of_ordered : 0.3984),
    n: get(DATA, 'contracts.meta.n', NUM.cohort)
  };
  T2.est = iv(T2.tau).est;
  function pctTxt(p) { var v = p * 100; return v < 5 ? fx(v, 1) : fx(v, 0); }
  (function zeroBlocks() {
    var K = DATA.contracts, er = K && K.pct && K.pct.endorserank, aw = K && K.pct && K.pct.awp;
    if (!er || !aw || !er.length || er.length !== aw.length) return;
    var n = er.length, i, eMin = Infinity, aMin = Infinity, aLo = 1, aHi = 0, eLo = 1, eHi = 0;
    for (i = 0; i < n; i++) { if (er[i] < eMin) eMin = er[i]; if (aw[i] < aMin) aMin = aw[i]; }
    for (i = 0; i < n; i++) {
      if (er[i] === eMin) { if (aw[i] < aLo) aLo = aw[i]; if (aw[i] > aHi) aHi = aw[i]; }
      if (aw[i] === aMin) { if (er[i] < eLo) eLo = er[i]; if (er[i] > eHi) eHi = er[i]; }
    }
    ER_ZERO.pct = eMin; ER_ZERO.lo = aLo; ER_ZERO.hi = aHi;
    AWP_ZERO.pct = aMin; AWP_ZERO.lo = eLo; AWP_ZERO.hi = eHi;
  })();
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
      'Do the two scores put the same contracts in the same order? The two rows of the previous slide break into points and become a cloud of ' + n0(T2.n) + ' contracts. Seen from above, the cloud becomes a flat picture. Across is the rank by EndorseRank and up is the rank by AWP, both turned into percentiles. Amber points are contracts that EndorseRank ranks higher, sky-blue points contracts that AWP ranks higher.',
      'If the two ranks were the same, the points would gather on this diagonal. But they are spread widely. Kendall’s tau is ' + estOf(T2.tau) + '. That is clearly above 0 and far from 1. The two orders are related, but they are not the same order.',
      'There are more than ' + Math.floor(T2.pairs / 1e6) + ' million contract pairs. ' + T2.both + '% of them are ordered by both scores, and of those, ' + T2.disc + '% are in the opposite order. The thirty pairs flashing now are only an illustration; the value where it stops is the result over all pairs. Related, but not interchangeable.',
      'The column at the left edge is the ' + n0(ER_ZERO.n) + ' contracts with an EndorseRank of zero, and the row at the bottom is the ' + n0(AWP_ZERO.n) + ' contracts with an AWP of zero. All zero-score contracts are tied, so they share the lowest ranks and sit in the middle of them. That is why the AWP zero row is at about ' + pctTxt(AWP_ZERO.pct) + ', not at 0, and the EndorseRank zero column at about ' + pctTxt(ER_ZERO.pct) + '. With the rule that keeps contracts outside a graph as isolated nodes, tau stayed at ' + estOf(T2.iso) + '. The two graphs are built differently, so different orders are partly expected. In the registered analysis it was ' + estOf(T2.reg) + '.'
    ],
    html:
      '<h1 class="t-h1">EndorseRank and AWP put contracts in [[different orders]]</h1>' +
      '<div class="abs" data-shared="s8-row-er" data-shared-mode="manual" style="left:96px;top:' + G1.yER + 'px;width:1724px;height:150px;visibility:hidden"></div>' +
      '<div class="abs" data-shared="s8-row-awp" data-shared-mode="manual" style="left:96px;top:' + G1.yAWP + 'px;width:1724px;height:150px;visibility:hidden"></div>' +
      '<div class="abs" id="p3" data-in="none" style="left:0;top:' + P2.top + 'px;width:' + P2.w + 'px;height:' + P2.h + 'px"></div>' +
      '<svg class="abs s8-ov" id="ov" data-in="none" width="' + P2.w + '" height="' + P2.h + '" viewBox="0 0 ' + P2.w + ' ' + P2.h + '" style="left:0;top:' + P2.top + 'px"></svg>' +
      '<div class="abs s8-p2" id="panel" data-in="none" style="left:1300px;top:186px;width:524px;height:780px">' +
        '<div class="abs lg" id="lg" style="left:0;top:0;width:524px"><div>One point = one contract · <b class="tnum ink">' + n0(T2.n) + '</b> contracts</div>' +
          '<div><i style="background:#F5B43C"></i>Ranked higher by EndorseRank</div><div><i style="background:#3CC4FF"></i>Ranked higher by AWP</div></div>' +
        '<div class="abs" id="b1" style="left:0;top:126px;width:524px">' +
          '<div class="k">Kendall’s τ<sub>b</sub> (EndorseRank vs AWP)</div>' +
          '<div style="display:flex;align-items:baseline;gap:16px"><span class="tau" id="tau">0.000</span><span class="ci" id="tauci">' + ciOf(T2.tau) + '</span></div>' +
          '<svg id="rul" width="500" height="72" style="overflow:visible;display:block;margin-top:2px"></svg>' +
          '<div class="ln" id="tauln">Neither 0 nor 1</div>' +
          '<div class="gh" id="ghost" style="margin-top:6px">' + pill('registered-analysis') + '<span class="tnum">' + T2.reg + '</span></div>' +
                  '</div>' +
        '<div class="abs" id="b2" style="left:0;top:418px;width:524px">' +
          '<div class="ln">Contract pairs <b id="pairs">' + n0(T2.pairs) + '</b></div>' +
          '<div class="ln">Pairs ordered by both scores <b id="both">' + T2.both + '%</b></div>' +
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
        tl.add(ctx.count(g.tau, 0, T2.est, { decimals: 3, final: estOf(T2.tau), duration: 1.2 }), 0.5);
        tl.fromTo(g.tauci, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.4);
        tl.set(g.rmark, { autoAlpha: 1 }, 0.5);
        tl.to(g.rst, { v: T2.est, duration: dur(ctx, 1.2), ease: 'power3.out', onUpdate: function () { g.rmark.setAttribute('transform', 'translate(' + g.RX(g.rst.v).toFixed(1) + ',4)'); } }, 0.5);
        tl.fromTo(g.tauln, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4 }, 1.6);
      }
      if (i === 2) {
        fadeUp(tl, g.b2, 0, 0.5);
        tl.add(Comp.odometer(ctx, g.pairs, n0(T2.pairs), { duration: 1.6 }), 0.1);
        tl.add(ctx.count(g.both, 0, +T2.both, { decimals: 1, suffix: '%', final: T2.both + '%', duration: 1.2 }), 0.4);
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
          g.discnote.textContent = 'Final value = all ' + Math.round(T2.pairs / 1e6) + ' million pairs';
          ctx.add(function () { gsap.to(g.gfill, { width: T2.disc + '%', duration: ctx.reduced ? 0.01 : 0.8, ease: E.io }); });
        }, null, tEnd);
        tl.add(ctx.count(g.disc, Math.max(0, T2.disc - 1.2), +T2.disc, { decimals: 1, suffix: '%', final: T2.disc + '%', duration: 0.8 }), tEnd + 0.01);
        tl.fromTo(g.b3, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, tEnd + 0.9);
      }
      if (i === 3) {
        if (g.T && !g.T.failed) {
          g.T.render();
          var lay3 = svgEl('g', {}, g.ov);
          var c0 = p2pt(g, ER_ZERO.pct, ER_ZERO.lo), c1 = p2pt(g, ER_ZERO.pct, ER_ZERO.hi);
          var b0 = p2pt(g, AWP_ZERO.lo, AWP_ZERO.pct), b1 = p2pt(g, AWP_ZERO.hi, AWP_ZERO.pct);
          var colR = svgEl('rect', { x: c0.x - 11, y: c1.y - 10, width: 22, height: c0.y - c1.y + 20, rx: 11, fill: 'rgba(233,237,245,.08)', stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '6 5' }, lay3);
          var bandR = svgEl('rect', { x: b0.x - 10, y: b0.y - 11, width: b1.x - b0.x + 20, height: 22, rx: 11, fill: 'rgba(233,237,245,.08)', stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '6 5' }, lay3);
          var pl = p2pt(g, ER_ZERO.pct, 0.74);
          var t1a = txt(lay3, pl.x - 64, pl.y - 12, 'EndorseRank', { 'text-anchor': 'end', fill: C.ink, 'font-size': 21, 'font-weight': 700 });
          var t1b = txt(lay3, pl.x - 64, pl.y + 18, n0(ER_ZERO.n) + ' at zero', { 'text-anchor': 'end', fill: C.ink, 'font-size': 21, 'font-weight': 700, 'class': 'tnum' });
          var t1l = svgEl('line', { x1: pl.x - 58, x2: pl.x - 16, y1: pl.y + 2, y2: pl.y + 2, stroke: C.ink2, 'stroke-width': 1.5 }, lay3);
          var t1c = txt(lay3, pl.x - 64, pl.y + 46, '→ middle ≈ ' + pctTxt(ER_ZERO.pct), { 'text-anchor': 'end', fill: C.ink2, 'font-size': 18, 'class': 'tnum' });
          /* ties: every zero shares the bottom ranks, so the block sits at its mid-rank percentile
             (AWP ((1,192 + 1)/2 − 1)/6,482 ≈ 9.2; EndorseRank ((197 + 1)/2 − 1)/6,482 ≈ 1.5), not at 0 */
          var ya = p2pt(g, 0, AWP_ZERO.pct);
          var tk = svgEl('line', { x1: ya.x - 24, x2: ya.x - 12, y1: ya.y, y2: ya.y, stroke: C.ink, 'stroke-width': 2 }, lay3);
          var tkt = txt(lay3, ya.x - 30, ya.y + 6, '≈ ' + pctTxt(AWP_ZERO.pct), { 'text-anchor': 'end', fill: C.ink, 'font-size': 18, 'font-weight': 700, 'class': 'tnum' });
          var tc = p2pt(g, 0.17, AWP_ZERO.pct + 0.045);
          var tie = txt(lay3, tc.x, tc.y + 6, 'All tied → they share the lowest ranks and sit at their middle (≈ ' + pctTxt(AWP_ZERO.pct) + ')', { 'text-anchor': 'start', fill: C.ink, 'font-size': 18, 'font-weight': 600, stroke: '#0E1119', 'stroke-width': 6, 'stroke-linejoin': 'round', 'paint-order': 'stroke' });
          var t2 = txt(lay3, b1.x + 22, b0.y + 7, 'AWP: ' + n0(AWP_ZERO.n) + ' at zero', { 'text-anchor': 'start', fill: C.ink, 'font-size': 21, 'font-weight': 700, 'class': 'tnum' });
          var t3 = txt(lay3, b1.x + 22, b0.y + 40, 'Isolated-node rule:', { 'text-anchor': 'start', fill: C.ink2, 'font-size': 19 });
          var t4 = txt(lay3, b1.x + 22, b0.y + 66, 'τ still ' + estOf(T2.iso), { 'text-anchor': 'start', fill: C.ink2, 'font-size': 19, 'class': 'tnum' });
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
  /* holdout counts (R w0 / w1), label shares (DECK_DATA.holdout base rates) and the 12-month score
     windows (DECK_DATA.timeline.anchors); spenders with both labels are counted from
     revised-usd-12m/{holdout-w0,window-w1}/spender_scores.part000.parquet (not in DECK_DATA) */
  var HO = DATA.holdout || {}, AN3 = (DATA.timeline || {}).anchors || {};
  var H3 = {
    pa0: pc1(get(HO, 'w0.base_rate_new_approvals', NUM.ga0 / NUM.sp0)), ps0: pc1(get(HO, 'w0.base_rate_new_senders', NUM.gs0 / NUM.sp0)),
    both0: 1044, both1: 967,
    win0: AN3.score_window_t1 || ['2025-04-01T00:00:00Z', '2026-03-31T23:59:59Z'],
    win1: AN3.score_window_tobs || ['2025-07-01T00:00:00Z', '2026-06-30T23:59:59Z']
  };
  var MON_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  function ymEn(s) { return MON_EN[+String(s).slice(5, 7) - 1] + ' ' + String(s).slice(0, 4); }
  var slide3 = {
    id: 's08-03', title: 'Out-of-window test (temporal holdout): freeze and wait', time: 40, steps: 3,
    tags: [],
    notes: [
      'Now the real test, the out-of-window test. The thesis calls it a temporal holdout. The three-year calendar is back. The amber stream is the allowance records of each month, and the sky-blue stream the transfer records; only the twelve months that the first test scores from are drawn.',
      'On 31 March we freeze the scores. We build them only from the records of the twelve months before, ' + ymEn(H3.win0[0]) + ' to ' + ymEn(H3.win0[1]) + ', and do not touch them afterwards. Allowances, too, count only if they were set inside these twelve months. This first temporal holdout, which sets a later period aside and checks the scores against it, is holdout W0. This test has ' + n0(NUM.sp0) + ' spender contracts.',
      'Then we grade each spender contract by what newly happened to it from April to June. There are two labels. One is the number of new allowances between an owner and the spender that did not exist on the freeze date; the other is the number of addresses that sent it a transfer for the first time. ' + n0(NUM.ga0) + ' contracts, ' + H3.pa0 + '%, gained new approval pairs: the amber dots. ' + n0(NUM.gs0) + ' contracts, ' + H3.ps0 + '%, gained new transfer senders: the sky-blue rings. Many contracts, ' + n0(H3.both0) + ', gained both labels, so many amber dots wear a ring. Only about one contract in five has a label, so the results depend heavily on how well a score ranks these few contracts near the top.',
      'We ran the same test once more, freezing on 30 June and labeling July to September. Here the scores come from the twelve months ' + ymEn(H3.win1[0]) + ' to ' + ymEn(H3.win1[1]) + '. This is the registered window W1. This study extracted the logs of these three months only after it had registered the rules. There are ' + n0(NUM.sp1) + ' spender contracts; ' + n0(NUM.ga1) + ' gained new approval pairs and ' + n0(NUM.gs1) + ' new transfer senders.'
    ],
    html:
      '<h1 class="t-h1">[[Freeze]] the scores, then grade them on what comes next</h1>' +
      '<p class="abs s8-small" style="left:96px;top:154px;color:var(--ink-3)">Out-of-window test = temporal holdout · set a later period aside and predict it</p>' +
      '<div class="abs" id="cal" data-in="none" style="left:' + AX3.left + 'px;top:' + AX3.top + 'px;width:' + AX3.w + 'px;height:' + AX3.h + 'px"></div>' +
      '<div class="abs s8-info" id="i0" data-in="none" style="left:96px;top:470px"><span class="mono">W0</span><span>Holdout · freeze 31 Mar → Apr–Jun · <b class="tnum">' + n0(NUM.sp0) + '</b> spenders</span></div>' +
      '<div class="abs s8-info" id="i1" data-in="none" style="left:96px;top:516px"><span class="mono">W1</span><span>Registered window · freeze 30 Jun → Jul–Sep · <b class="tnum">' + n0(NUM.sp1) + '</b> spenders</span>' + LOCK_SVG + '</div>' +
      '<p class="abs s8-small" id="stripcap" data-in="none" style="left:96px;top:566px;color:var(--ink-3)">Spender contracts · scores stay frozen · example</p>' +
      '<svg class="abs" id="strip" data-in="none" width="960" height="280" viewBox="0 0 960 280" style="left:0;top:600px;overflow:visible"></svg>' +
      '<div class="s8-month" id="mon" data-in="none" style="left:868px;top:566px">Apr</div>' +
      '<div class="abs s8-defs" id="defs" data-in="none" style="left:96px;top:872px;width:880px">' +
        '<div><b class="c-allow">New approval pairs</b>: owner–spender allowances that did not exist at the freeze</div>' +
        '<div><b class="c-xfer">New transfer senders</b>: addresses that sent a transfer for the first time</div>' +
        '<div data-step="3"><span class="lk">' + LOCK_SVG + '</span><b>W1</b>: logs extracted after the registration</div></div>' +
      '<div class="abs" id="wbox" data-in="none" style="left:1040px;top:466px;width:784px;height:480px">' +
        '<div class="s8-wt" id="wt">W0 spender contracts <span class="tnum">' + n0(NUM.sp0) + '</span><small>one dot ' + (NUM.sp0 % 10 ? '≈' : '=') + ' 10 contracts</small></div>' +
        '<div class="s8-wc" id="wc"><span><i style="background:#F5B43C"></i>New approval pairs <b id="wa">0</b> <span id="wap">(' + H3.pa0 + '%)</span></span><span><i style="background:transparent;box-shadow:inset 0 0 0 2.5px #3CC4FF"></i>New senders <b id="ws">0</b> <span id="wsp">(' + H3.ps0 + '%)</span></span><span><i style="background:#F5B43C;box-shadow:0 0 0 2.5px #3CC4FF"></i>Both</span></div>' +
        '<div id="wf" style="position:absolute;left:0;top:92px"></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var TL = g.TL = Comp.timeline(ctx, q(el, '#cal'), { w: AX3.w, h: AX3.h, axisY: AX3.axisY, padL: 0, padR: 0 });
      /* monthly streams of each score window: W0 (12 months before t1) first, T_obs (W1) at step 3 */
      var MC = (((DATA.timeline || {}).monthly_counts || {}).revised) || {};
      function ser(k) { var a = MC[k] || []; return { v: a.map(function (p) { return p[1]; }), start: a.length ? a[0][0] : null }; }
      var A0 = ser('approval_ego_t1'), T0 = ser('transfer_ego_t1'), A1 = ser('approval_ego'), T1s = ser('transfer_ego');
      var mxA = Math.max.apply(null, A0.v.concat(A1.v, [1])), mxT = Math.max.apply(null, T0.v.concat(T1s.v, [1]));
      function mk(S, color, hgt, base, mx) { return S.v.length ? TL.stream(S.v, { color: color, height: hgt, base: base, opacity: 0.24, start: S.start, max: mx }) : null; }
      g.sA = mk(A0, 'allow', 70, 92, mxA); g.sT = mk(T0, 'xfer', 80, AX3.axisY - 6, mxT);
      g.sA1 = mk(A1, 'allow', 70, 92, mxA); g.sT1 = mk(T1s, 'xfer', 80, AX3.axisY - 6, mxT);
      g.S0 = [g.sA, g.sT].filter(Boolean).map(function (S) { return S.g; });
      g.S1 = [g.sA1, g.sT1].filter(Boolean).map(function (S) { return S.g; });
      gsap.set(g.S0.concat(g.S1), { autoAlpha: 0 });
      /* frost over the 12-month score window of each freeze (only these records make the score) */
      var svg = TL.svg;
      var defs = svgEl('defs', {}, svg), gr = svgEl('linearGradient', { id: 's8-frost', x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
      svgEl('stop', { offset: '0', 'stop-color': '#E9EDF5', 'stop-opacity': 0.16 }, gr); svgEl('stop', { offset: '1', 'stop-color': '#E9EDF5', 'stop-opacity': 0.06 }, gr);
      function frost(win, label) {
        var xs = TL.x(win[0]), x1 = TL.x(win[1]) + 1.5, G = svgEl('g', {}, svg);
        svgEl('rect', { x: xs, y: 14, width: x1 - xs, height: AX3.axisY - 16, fill: 'url(#s8-frost)', rx: 6 }, G);
        svgEl('line', { x1: x1, x2: x1, y1: 14, y2: AX3.axisY - 2, stroke: '#E9EDF5', 'stroke-width': 2, opacity: 0.7 }, G);
        txt(G, xs - 10, 40, label + ' →', { 'text-anchor': 'end', fill: C.ink, 'font-size': 17, 'font-weight': 600 });
        gsap.set(G, { autoAlpha: 0 });
        return G;
      }
      g.frost = frost(H3.win0, 'W0 score window · 12 months');
      g.frost1 = frost(H3.win1, 'W1 score window · 12 months');
      g.pin0 = TL.pin('2026-03-31', { y0: 8, label: 't₁ · freeze 31 Mar', color: 'ink', labelSize: 19 });
      g.pin1 = TL.pin('2026-06-30', { y0: 8, label: 'T_obs · 30 Jun', color: 'ink', labelSize: 19 });
      g.pin0.label.setAttribute('text-anchor', 'end'); g.pin0.label.setAttribute('x', TL.x('2026-03-31') - 22); g.pin0.label.setAttribute('y', 14);
      g.pin1.label.setAttribute('text-anchor', 'start'); g.pin1.label.setAttribute('x', TL.x('2026-06-30') + 22); g.pin1.label.setAttribute('y', 14);
      g.band0 = TL.band('2026-04-01', '2026-06-30', { label: 'W0 labels', y0: 40, color: 'ink2' });
      g.band1 = TL.band('2026-07-01', '2026-09-30', { label: 'W1 labels', y0: 40, color: 'ink2' });
      [g.band0, g.band1].forEach(function (B) {
        if (!B.label) return;
        B.label.setAttribute('y', 66); B.label.setAttribute('font-size', 18);
        /* above the streams, with a dark outline: the W1 streams reach into the W0 label window */
        B.label.setAttribute('stroke', '#0E1119'); B.label.setAttribute('stroke-width', 5); B.label.setAttribute('stroke-linejoin', 'round'); B.label.setAttribute('paint-order', 'stroke');
        TL.svg.appendChild(B.label); gsap.set(B.label, { autoAlpha: 0 });
      });
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
         W0 791 dots: both 1,044 → 104, approval only → 69 (amber 173 ≈ 1,732 / 10), sender only → 38 (sky 142 ≈ 1,422 / 10)
         W1 796 dots: both 967 → 97, approval only → 53 (amber 150 ≈ 1,495 / 10), sender only → 40 (sky 137 ≈ 1,371 / 10)
         overlap = spenders with future_new_approvers > 0 and future_new_transfer_senders > 0 in
         experiments/data/2-processed-tables-and-evaluations/revised-usd-12m/{holdout-w0,window-w1}/spender_scores.part000.parquet */
      var rnd = Deck.util.rng(7);
      function pick(n, both, aOnly, sOnly) {
        var idx = [], i, mark = new Uint8Array(n);
        for (i = 0; i < n; i++) idx.push(i);
        for (i = n - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
        for (i = 0; i < both + aOnly + sOnly; i++) mark[idx[i]] = i < both ? 3 : i < both + aOnly ? 1 : 2;
        return mark;
      }
      function dots(sp, ga, gs, both) { var b = Math.round(both / 10); return [Math.round(sp / 10), b, Math.round(ga / 10) - b, Math.round(gs / 10) - b]; }
      var D0 = dots(NUM.sp0, NUM.ga0, NUM.gs0, H3.both0), D1 = dots(NUM.sp1, NUM.ga1, NUM.gs1, H3.both1);
      g.n0 = D0[0]; g.n1 = D1[0];
      g.mark0 = pick.apply(null, D0); g.mark1 = pick.apply(null, D1);
      g.wmark = g.mark0;
      g.W = waffle(ctx, q(el, '#wf'), { n: g.n0, max: Math.max(g.n0, g.n1), cols: 40, gap: 19.4, r: 6.6, style: function (i, hq) {
        var m = g.wmark[i];
        if (!m || hq <= 0) return { fill: '#3A4458' };
        var sc = 1 + 0.25 * hq;
        if (m === 1) return { fill: C.allow, scale: sc };
        if (m === 2) return { fill: '#3A4458', stroke: C.xfer, lw: 2.6, scale: sc };
        return { fill: C.allow, stroke: C.xfer, lw: 2.6, scale: sc };
      } });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo(g.axisLine, { attr: { x2: g.TL.x('2023-10-01') } }, { attr: { x2: g.TL.x('2026-09-30') }, duration: dur(ctx, 1.0), ease: E.io }, 0.2);
      tl.fromTo(g.ticks, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, stagger: 0.012 }, 0.2);
      if (g.sA) tl.add(function () { ctx.add(function () { g.sA.reveal({ duration: 1.0 }); }); }, 0.6);
      if (g.sT) tl.add(function () { ctx.add(function () { g.sT.reveal({ duration: 1.0 }); }); }, 0.75);
      if (g.S0.length) tl.set(g.S0, { autoAlpha: 1 }, 0.6);
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
        tl.add(ctx.count(g.wa, 0, NUM.ga0, { decimals: 0, final: n0(NUM.ga0), duration: 1.2 }), 1.6);
        tl.add(ctx.count(g.ws, 0, NUM.gs0, { decimals: 0, final: n0(NUM.gs0), duration: 1.2 }), 1.6);
      }
      if (i === 3) {
        tl.add(g.pin1.drop(), 0);
        tl.to(g.frost, { autoAlpha: 0, duration: dur(ctx, 0.4) }, 0.2);
        tl.fromTo(g.frost1, { autoAlpha: 0, scaleX: 0, transformOrigin: '100% 50%' }, { autoAlpha: 1, scaleX: 1, duration: dur(ctx, 0.9), ease: E.io }, 0.3);
        if (g.S1.length) { tl.to(g.S0, { autoAlpha: 0, duration: dur(ctx, 0.5) }, 0.2); tl.fromTo(g.S1, { autoAlpha: 0 }, { autoAlpha: 1, duration: dur(ctx, 0.6) }, 0.45); }
        tl.add(g.band1.show(), 0.4);
        fadeUp(tl, g.i1, 0.6, 0.5);
        tl.call(function () { g.mon.textContent = 'Jul'; }, null, 0.6);
        tl.call(function () { g.mon.textContent = 'Aug'; }, null, 1.1);
        tl.call(function () { g.mon.textContent = 'Sep'; }, null, 1.6);
        tl.add(Comp.swap(ctx, g.wt, 'W1 spender contracts <span class="tnum">' + n0(NUM.sp1) + '</span><small>one dot ' + (NUM.sp1 % 10 ? '≈' : '=') + ' 10 contracts</small>'), 0.5);
        tl.call(function () {
          g.wap.textContent = ''; g.wsp.textContent = '';
          g.wmark = g.mark1; g.W.n = g.n1; g.W.st.p = 0; g.W.st.q = 0; g.W.draw();
        }, null, 0.9);
        tl.add(function () { ctx.add(function () { g.W.fill({ duration: 1.2 }); g.W.wave({ duration: 1.1, delay: 1.0 }); }); }, 0.95);
        tl.add(ctx.count(g.wa, NUM.ga0, NUM.ga1, { decimals: 0, final: n0(NUM.ga1), duration: 1.0 }), 1.9);
        tl.add(ctx.count(g.ws, NUM.gs0, NUM.gs1, { decimals: 0, final: n0(NUM.gs1), duration: 1.0 }), 1.9);
      }
    }
  };

  /* ================================================================ locked board (s08-04 … s08-06) */
  var BD = { tx0: 540, tx1: 1040, td: [0.25, 0.50], tticks: [0.25, 0.3, 0.35, 0.4, 0.45, 0.5], vX: 1062,
    dx0: 1344, dx1: 1800, dd: [-0.11, 0.17], dticks: [-0.1, -0.05, 0, 0.05, 0.1, 0.15],
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
      txt(svg, 120, G.top + 82, G.s1, { fill: C.ink3, 'font-size': 15 });
      txt(svg, 120, G.top + 106, G.s2, { fill: C.ink3, 'font-size': 15 });
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

  /* values of s08-04 … s08-08 (R = DECK_DATA.results.revised, G = .registered) */
  var NA = 'future_new_approvers', NS8 = 'future_new_transfer_senders';
  var T4 = {
    awp0: IV(W0, 'taus.awp.' + NS8, '0.409 [0.396, 0.421]'), deg0: IV(W0, 'taus.t1_in_degree.' + NS8, '0.447 [0.435, 0.459]'),
    d0: CV(W0.contrasts_after, 'awp', 't1_in_degree', NS8, '−0.038 [−0.043, −0.032]'),
    g0: CV(get(RG, 'w0.contrasts_after'), 'awp', 't1_in_degree', NS8, '+0.038 [0.035, 0.042]'),
    awp1: IV(W1, 'spender_taus.awp.' + NS8, '0.398 [0.386, 0.412]'), deg1: IV(W1, 'spender_taus.in_degree.' + NS8, '0.439 [0.426, 0.454]'),
    d1: IV(W1, 'endorserank_results.awp_minus_degree_send', '−0.041 [−0.047, −0.034]', true),
    g1: IV(RG, 'w1.endorserank_results.awp_minus_degree_send', '+0.020 [0.016, 0.023]', true),
    recv: CV(get(W0, 'receiving.contrasts'), 'awp', 't1_in_degree', NS8, '−0.051 [−0.059, −0.043]')
  };
  var T5 = {
    deg0: IV(W0, 'taus.t1_in_approve_degree.' + NA, '0.392 [0.377, 0.406]'), er0: IV(W0, 'taus.endorserank.' + NA, '0.303 [0.287, 0.319]'),
    d0: CV(W0.contrasts_after, 'endorserank', 't1_in_approve_degree', NA, '−0.090 [−0.100, −0.079]'),
    g0: CV(get(RG, 'w0.contrasts_after'), 'endorserank', 't1_in_approve_degree', NA, '−0.011 [−0.016, −0.006]'),
    deg1: IV(W1, 'spender_taus.in_approve_degree.' + NA, '0.381 [0.365, 0.396]'), er1: IV(W1, 'spender_taus.endorserank.' + NA, '0.299 [0.284, 0.314]'),
    d1: IV(W1, 'endorserank_results.endorserank_minus_degree_appr', '−0.082 [−0.090, −0.073]', true),
    g1: IV(RG, 'w1.endorserank_results.endorserank_minus_degree_appr', '−0.029 [−0.032, −0.025]', true),
    ea0: IV(SUP, 'w0.er_minus_awp_appr', '+0.107 [0.086, 0.130]', true), ea1: IV(SUP, 'w1.er_minus_awp_appr', '+0.142 [0.119, 0.164]', true),
    recv: CV(get(W0, 'receiving.contrasts'), 'endorserank', 't1_in_approve_degree', NA, '−0.087 [−0.096, −0.078]'),
    rEr: estOf(IV(W0, 'receiving.taus.endorserank.' + NA, '0.299 [0.283, 0.315]')), rAwp: estOf(IV(W0, 'receiving.taus.awp.' + NA, '0.328 [0.312, 0.343]')),
    cvW: pc1(get(W0, 'coverage.share_gaining_approvals_without', 0.2668)), cvO: pc1(get(W0, 'coverage.share_gaining_approvals_with', 0.2091))
  };
  var T6 = {
    act0: IV(W0, 'taus.endorserank_activity.' + NA, '0.332 [0.315, 0.347]'), act1: IV(W1, 'spender_taus.endorserank_activity.' + NA, '0.335 [0.319, 0.349]'),
    d0: IV(SUP, 'w0.er_activity_minus_degree_appr', '−0.060 [−0.070, −0.052]', true), d1: IV(SUP, 'w1.er_activity_minus_degree_appr', '−0.046 [−0.055, −0.038]', true),
    famEr: estOf(IV(SW, 'families.endorserank.allowance', '0.560 [0.548, 0.571]')), famAct: IV(SW, 'families.endorserank_activity.allowance', '0.601 [0.590, 0.613]'),
    cpr0: estOf(IV(W0, 'taus.cpr_l0.' + NS8, '0.366 [0.351, 0.378]'))
  };
  function E8(s) { return estOf(s); }
  function A8(s) { return estOf(s).replace(/^[+−]/, ''); }   /* size of a difference, without its sign */
  var slide4 = {
    id: 's08-04', title: 'Transfer side: the raw count beats AWP', time: 40, steps: 4,
    tags: function (s) { return s >= 4 ? ['posthoc', 'registered-analysis'] : ['posthoc']; },
    notes: [
      'First, the transfer side. The left panel shows how well each score predicted what happened later. The right panel shows the difference between the two scores, paired on the same contracts. If the difference lies right of 0, the walk score is better; if it lies left of 0, the plain count is better.',
      'In predicting the addresses that will newly send transfers, AWP reaches ' + E8(T4.awp0) + ' in W0, and the transfer in-degree, which simply counts the addresses that sent transfers, reaches ' + E8(T4.deg0) + '.',
      'The paired difference is ' + E8(T4.d0) + ', and the whole interval lies left of 0. AWP did worse than simply counting the addresses that sent transfers.',
      'In W1, AWP was again ' + A8(T4.d1) + ' lower, and again the interval lies below 0. So on the transfer side, too, the time and value weights and a walk that restarts at active senders did not beat the plain count.',
      'Looking only at the ' + n0(NUM.recv0) + ' contracts that had received a transfer, the difference is ' + E8(T4.recv) + ', still below 0, so the contracts that AWP scores zero do not explain the gap. The gray hollow dots are the values of the registered analysis. That analysis, with raw base units, every token and scores from all records since October 2023, had AWP slightly above the count: the opposite direction. These comparisons were in neither the plan nor the registration; they were computed after the labels were known.'
    ],
    html:
      '<h1 class="t-h1">Predicting new senders: [[the count]] beats AWP</h1>' + BOARD_HTML +
      '<p class="abs s8-concl" id="concl" data-in="none" style="left:96px;top:720px;width:1728px">On the transfer side, too, the walk (time and value weights, activity restarts) did not beat the count</p>' +
      '<div class="abs s8-tiny" id="tiny" data-in="none" style="left:96px;top:800px;width:1728px">' + pill('posthoc') + '<span>In neither the plan nor the registration: computed after the labels were known · new-sender label · spenders W0 ' + n0(NUM.sp0) + ', W1 ' + n0(NUM.sp1) + '</span></div>' +
      '<div class="abs s8-tiny" id="gleg" data-in="none" style="left:96px;top:850px;width:1728px">' + pill('registered-analysis') + '<span>Gray hollow = registered analysis (raw units, all tokens, since Oct 2023): <b>' + T4.g0 + '</b> · <b>' + T4.g1 + '</b>: AWP above the count</span></div>',
    build: function (el, ctx) {
      var g = boardBuild(el, ctx), svg = g.bars;
      var rowsW0 = [{ label: 'AWP', color: C.xfer, val: T4.awp0 }, { label: 'Transfer in-degree', color: C.deg, dashed: true, val: T4.deg0 }];
      var rowsW1 = [{ label: 'AWP', color: C.xfer, val: T4.awp1 }, { label: 'Transfer in-degree', color: C.deg, dashed: true, val: T4.deg1 }];
      g.G0 = boardGroup(svg, 0, rowsW0, { val: T4.d0, ghost: T4.g0 });
      g.G1 = boardGroup(svg, 1, rowsW1, { val: T4.d1, ghost: T4.g1 });
      g.ex = extraRow(svg, 640, 'Only prior transfer recipients', T4.recv, C.ink, 'W0 · ' + n0(NUM.recv0) + ' contracts · new senders');
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
      'In predicting which contracts will gain new approval pairs, the in-approve degree reaches ' + E8(T5.deg0) + ' in W0, and EndorseRank ' + E8(T5.er0) + '.',
      'The paired difference is ' + E8(T5.d0) + ', and the whole interval lies left of 0. EndorseRank did worse than simply counting the owners that approved the contract.',
      'In W1 it was also lower, by ' + A8(T5.d1) + ', and again below 0. In both windows the plain count won, just as on the transfer side.',
      'Contracts that already have many owners also gain more new owners, and the plain count captures this most directly. The picture on the left is an illustrative example.',
      'Over all spenders, the allowance-side score predicted new approval pairs better than AWP, the transfer-side score: ' + A8(T5.ea0) + ' higher in W0 and ' + A8(T5.ea1) + ' higher in W1. But this lead rests on the ' + n0(NUM.notRecv0) + ' spenders that had never received a transfer, the ' + n0(NUM.noXfer0) + ' that AWP scores zero among them. Those spenders without a transfer edge, about one in six, gained new approval pairs more often than the rest, ' + T5.cvW + '% against ' + T5.cvO + '%. Among the ' + n0(NUM.recv0) + ' that had received one, AWP is in fact higher, at ' + T5.rAwp + ' against ' + T5.rEr + ' for EndorseRank; no paired difference was computed for these two. On those ' + n0(NUM.recv0) + ' contracts, too, EndorseRank stays ' + A8(T5.recv) + ' below the in-approve degree. These comparisons, too, were all computed after the labels were known. The gray hollow dots are the registered analysis, where EndorseRank was also below the count.'
    ],
    html:
      '<h1 class="t-h1">Predicting new approval pairs: <span class="s8-hl" id="hl">the count</span> won</h1>' + BOARD_HTML +
      '<div class="s8-fig" id="rich" data-in="none" style="left:96px;top:612px;width:560px;height:330px"><div class="cap">Rich get richer: owners attract owners</div><span class="ex example-mark">Example</span><svg id="richsv" width="560" height="330" viewBox="0 0 560 330"></svg></div>' +
      '<p class="abs s8-concl" id="concl" data-in="none" style="left:700px;top:716px;width:1124px">EndorseRank with uniform restarts did not beat the owner count</p>' +
      '<p class="abs s8-reason" id="reason" data-in="none" style="left:700px;top:796px;width:1124px">Contracts with many owners gain more new owners: <b>the count captures this directly</b></p>' +
      '<div class="abs s8-tiny" id="tiny" data-in="none" style="left:700px;top:858px;width:1124px;flex-direction:column;align-items:flex-start;gap:2px">' +
        '<div>' + pill('posthoc') + ' <span>The lead rests on <b>' + n0(NUM.notRecv0) + '</b> spenders with no inbound transfer (<b>' + n0(NUM.noXfer0) + '</b> AWP zeros)</span></div>' +
        '<div>The <b>' + n0(NUM.recv0) + '</b> prior transfer recipients alone: AWP <b>' + T5.rAwp + '</b> · EndorseRank <b>' + T5.rEr + '</b> (not paired)</div>' +
        '<div>On them, EndorseRank − in-approve degree <b>' + T5.recv + '</b> · registered analysis <b>' + E8(T5.g0) + '</b>, <b>' + E8(T5.g1) + '</b> (gray)</div></div>',
    build: function (el, ctx) {
      var g = boardBuild(el, ctx), svg = g.bars;
      var rowsW0 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: T5.deg0 }, { label: 'EndorseRank', color: C.allow, val: T5.er0 }];
      var rowsW1 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: T5.deg1 }, { label: 'EndorseRank', color: C.allow, val: T5.er1 }];
      g.G0 = boardGroup(svg, 0, rowsW0, { val: T5.d0, ghost: T5.g0 });
      g.G1 = boardGroup(svg, 1, rowsW1, { val: T5.d1, ghost: T5.g1 });
      g.ex0 = extraRow(svg, 606, 'EndorseRank − AWP', T5.ea0, C.allow, 'W0 · new approval pairs · all spenders');
      g.ex1 = extraRow(svg, 662, 'EndorseRank − AWP', T5.ea1, C.allow, 'W1 · new approval pairs · all spenders');
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

  /* ================================================================ s08-06 restart rule only (post hoc) */
  var slide6 = {
    id: 's08-06', title: 'Change only the restart rule? (post hoc)', time: 45, steps: 5,
    tags: function (s) { return s >= 1 ? ['posthoc', 'example'] : ['posthoc']; },
    notes: [
      'So would a different restart rule beat the count?',
      'We changed only the restart rule, to AWP’s. The walk now restarts more often at owners that approve actively. An owner’s activity X_u is the sum, over the spenders that owner approved, of the time weight of the latest approval. It is the activity that AWP measures on transfers, applied in the same way to allowances. The paths of the walk stay the same; only the shares of the starting points change. The rain in the picture on the left is the teleportation. It falls more heavily on active owners.',
      'In W0 this variant reaches ' + E8(T6.act0) + ', up from ' + E8(T5.er0) + ' for the original EndorseRank. But it stays below the in-approve degree at ' + E8(T5.deg0) + '. The difference is ' + E8(T6.d0) + '. The dashed outline marks the variant, and the small hollow ring is where the original EndorseRank sat. On the right, too, the difference moved from the original ' + E8(T5.d0) + ' toward 0, but its interval still lies left of 0.',
      'W1 shows the same. The variant rises to ' + E8(T6.act1) + ' but stays ' + A8(T6.d1) + ' below the count; the original was ' + A8(T5.d1) + ' below.',
      'So the restart rule changes how far the walk falls short of the count, not whether it does. This comparison, too, was computed after we had seen the labels, so it gets a tag, not a verdict stamp. The closed form on the next slide shows why.',
      'The analysis plan only said to report this variant alongside; it did not fix a comparison with the count. This variant agrees more with the same-window allowance proxies: it rises from ' + T6.famEr + ' to ' + E8(T6.famAct) + '. The transfer side shows the same picture. The transfer layer of C-PR, which restarts uniformly, reaches ' + T6.cpr0 + ' in W0, further below the transfer in-degree at ' + E8(T4.deg0) + ' than AWP at ' + E8(T4.awp0) + '. No paired difference was computed for that layer, though.'
    ],
    html:
      '<h1 class="t-h1">With AWP’s restarts it still did not beat [[the count]]</h1>' + BOARD_HTML +
      '<div class="s8-fig" id="rain" data-in="none" style="left:96px;top:612px;width:560px;height:330px"><div class="cap">Teleport rain: heavier on active owners</div><span class="ex example-mark">Example</span><svg id="rainsv" width="560" height="330" viewBox="0 0 560 330"></svg></div>' +
      '<div class="abs s8-reason" id="def" data-in="none" style="left:700px;top:612px;width:1124px"><b class="c-allow">EndorseRank (activity restarts)</b>: restarts more often at active owners · $\\pi_u=X_u\\big/\\sum_v X_v$<br><span style="font-size:21px;line-height:30px;color:var(--ink-3)">$X_u$ = sum of the time weights of u’s latest approvals, one per spender (AWP’s activity, applied to allowances)</span></div>' +
      '<div class="s8-hyp" id="hyp" data-in="none" style="left:700px;top:706px"><svg width="280" height="84" viewBox="0 0 280 84"></svg></div>' +
      '<div class="abs s8-reason" id="hyptx" data-in="none" style="left:1004px;top:710px;width:820px">The restart rule changed only how far it falls short<br><span style="font-size:22px;color:var(--ink-3)">→ not whether it does · why: the closed form on the next slide</span></div>' +
      '<div class="abs s8-tiny" id="tiny" data-in="none" style="left:700px;top:818px;width:1124px;flex-direction:column;align-items:flex-start;gap:2px">' +
        '<div>Same-window agreement with the allowance family rises: <b>' + T6.famEr + ' → ' + T6.famAct + '</b></div>' +
        '<div>The analysis plan only said to ‘report’ this variant alongside; it fixed no comparison with the count</div>' +
        '<div>The transfer side agrees: C-PR’s transfer layer, with uniform restarts (W0 <b>' + T6.cpr0 + '</b>), lies further below the in-degree (<b>' + E8(T4.deg0) + '</b>) than AWP (<b>' + E8(T4.awp0) + '</b>) · not paired</div></div>',
    build: function (el, ctx) {
      var g = boardBuild(el, ctx), svg = g.bars;
      var er0 = iv(T5.er0).est, er1 = iv(T5.er1).est;
      var rowsW0 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: T5.deg0 }, { label: 'EndorseRank variant', color: C.allow, dashed: true, val: T6.act0, from: er0 }];
      var rowsW1 = [{ label: 'In-approve degree', color: C.deg, dashed: true, val: T5.deg1 }, { label: 'EndorseRank variant', color: C.allow, dashed: true, val: T6.act1, from: er1 }];
      g.G0 = boardGroup(svg, 0, rowsW0, { val: T6.d0, color: C.ink });
      g.G1 = boardGroup(svg, 1, rowsW1, { val: T6.d1, color: C.ink });
      /* where the uniform-restart EndorseRank sat (τ and its difference to the count, s08-05): small hollow amber rings */
      function ring(gi, x, y, label) {
        var gg = svgEl('g', {}, svg);
        svgEl('circle', { cx: x, cy: y, r: 7, fill: 'none', stroke: C.allow, 'stroke-width': 2, opacity: 0.8 }, gg);
        txt(gg, x, y + 30, label, { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 16, 'class': 'tnum' });
        gsap.set(gg, { autoAlpha: 0 });
        return gg;
      }
      g.orig = [[0, er0], [1, er1]].map(function (p) { return ring(p[0], bx(p[1]), BD.groups[p[0]].top + BD.rowOff[1], 'original ' + fx(p[1], 3)); });
      g.origD = [[0, iv(T5.d0).est], [1, iv(T5.d1).est]].map(function (p) { return ring(p[0], dxs(p[1]), BD.groups[p[0]].top + 64, 'original ' + m3(p[1])); });
      g.rain = q(el, '#rain'); g.def = q(el, '#def'); g.hyp = q(el, '#hyp'); g.hyptx = q(el, '#hyptx'); g.tiny = q(el, '#tiny');
      gsap.set([g.rain, g.def, g.hyp, g.hyptx, g.tiny], { autoAlpha: 0 });
      /* result tag: hollow outline, drawn slowly (not a verdict stamp) */
      var hs = q(g.hyp, 'svg');
      g.hypRect = svgEl('rect', { x: 3, y: 3, width: 274, height: 78, rx: 16, fill: 'none', stroke: C.hi, 'stroke-width': 3, 'stroke-dasharray': '10 7' }, hs);
      g.hypText = txt(hs, 160, 53, 'Still below', { 'text-anchor': 'middle', fill: C.hi, 'font-size': 30, 'font-weight': 800 });
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
        tl.fromTo(g.origD[0], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.8);
        growDiff(ctx, tl, g.G0, 1.0);
      }
      if (i === 3) {
        growGroup(ctx, tl, g.G1, 0, { duration: 0.6, stagger: 0.12 });
        tl.fromTo(g.orig[1], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.15);
        tl.fromTo(g.origD[1], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.45);
        growDiff(ctx, tl, g.G1, 0.6, { duration: 0.6 });
      }
      if (i === 4) {
        tl.set(g.hyp, { autoAlpha: 1 }, 0);
        var L = 2 * (274 + 78);
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
  /* c of the real same-window graph (R same_window.closed_form.common_value_c; thesis: 1.93 × 10⁻⁷) */
  var CC = (function () {
    var c = get(SW, 'closed_form.common_value_c', 1.928e-7), e = Math.floor(Math.log10(c)), m = fx(c / Math.pow(10, e), 2);
    if (m === '10.00') { m = '1.00'; e += 1; }
    return { m: m, e: e, html: m + ' × 10<sup>' + (e < 0 ? '−' + (-e) : e) + '</sup>' };
  })();
  var slide7 = {
    id: 's08-07', title: 'Closed form: what EndorseRank really computes', time: 60, steps: 6,
    tags: function (s) { return s === 5 ? ['example'] : s >= 6 ? ['thesis-example', 'example'] : ['thesis-example']; },
    notes: [
      'Let us look with a formula at why EndorseRank did not beat the plain count. Back to the small world. The water in each cup is the share of a long walk that stays at each node.',
      'First, c. c is the share that every node receives equally at every step: the restart share plus the dangling-node share. A node with no incoming edge, like A, receives only this, so its score is exactly c. In the small world, c is 0.15 plus 0.85 times 0.4706, divided by 4, which gives 0.1375, the same as A’s cup.',
      'The balance equation of every node starts at c and adds the shares that come in along edges. Most spenders receive approvals only from owners that receive no approvals themselves. Such an owner’s score is c, so in the spender’s balance equation we put c in place of the owner’s share r_u.',
      'Because c is the same for every owner, it comes out of the sum. That gives c plus c times d times delta, and factoring out c gives a short formula: c times, in brackets, 1 plus d times delta. Delta adds up, over the owners, the piece of each owner’s allowance weight that went to this spender. Let us check with B. A gave 2 of its weight 3 to B, so two thirds, and that gives 0.2154.',
      'C also matches, at 0.1765. But for D this formula does not hold. D’s owners, B and C, receive approvals themselves, so shares that spread one more step come in. So D is computed from the full balance equation: 0.4706.',
      'Here is delta in an example. If three owners approved 1, 2 and 4 spenders respectively, the plain count is 3, but delta is 1 plus one half plus one quarter, 1.75.',
      'c and d are the same for every depth-one spender, so the order of the scores is the order of delta, whatever d is. So EndorseRank in effect counts the owners, each divided by the weight of everything that owner approved. For such spenders, apart from the age and value weights and this division, little differs from the count. There is no information for the walk to add by spreading. In the real same-window graph, c is ' + CC.m + ' times 10 to the minus ' + (-CC.e) + '.'
    ],
    html:
      '<h1 class="t-h1">EndorseRank ≈ a [[divided]] count of approvals</h1>' +
      '<p class="abs s8-sub" style="left:96px;top:156px">For a spender whose owners receive no approvals (a depth-one spender)</p>' +
      '<div class="abs" id="swhost" data-in="none" style="left:0;top:0;width:1px;height:1px"></div>' +
      '<svg class="abs" id="swov" data-in="none" width="900" height="760" viewBox="0 0 900 760" style="left:0;top:200px;overflow:visible"></svg>' +
      '<div class="abs s8-d" id="eq" data-in="none" style="left:980px;top:204px;width:844px"></div>' +
      '<div class="s8-symrow" id="syms" data-in="none" style="left:96px;top:832px"></div>' +
      '<svg class="abs s8-pie" id="pie" data-in="none" width="880" height="620" viewBox="0 0 880 620" style="left:96px;top:226px;overflow:visible"></svg>' +
      '<div class="abs s8-hero" id="concl" data-in="none" style="left:96px;top:856px;width:860px">The more spenders an owner approves, the smaller each share<br><span style="font-size:22px;color:var(--ink-3)">→ the order differs from the count · real same-window graph: c = ' + CC.html + '</span></div>',
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
      g.ringTx = txt(ov, A.x, A.y - 48, 'No incoming edges', { 'text-anchor': 'middle', fill: C.ink, 'font-size': 19, 'font-weight': 700 });
      gsap.set([g.ringA, g.ringTx], { autoAlpha: 0 });
      function chip(id, label, dy, col) {
        var p = nodeXY(id), gw = svgEl('g', { transform: 'translate(' + p.x + ',' + (p.y + dy) + ')' }, ov), gg = svgEl('g', {}, gw);
        var w = label.length * 11 + 28;
        svgEl('rect', { x: -w / 2, y: -15, width: w, height: 30, rx: 15, fill: C.bg3, stroke: col || '#39435A', 'stroke-width': 1.5 }, gg);
        txt(gg, 0, 7, label, { 'text-anchor': 'middle', fill: col || C.ink, 'font-size': 19, 'font-weight': 700 });
        gsap.set(gg, { autoAlpha: 0 });
        return gg;
      }
      g.chipB = chip('B', 'depth one', -62, C.allow); g.chipC = chip('C', 'depth one', -62, C.allow); g.chipD = chip('D', 'deeper', -62, C.ink2);
      g.chipA = chip('A', 'c', 0, C.ink); g.chipA.parentNode.setAttribute('transform', 'translate(' + (A.x - 66) + ',' + A.y + ')');
      /* derivation panel */
      g.D = Comp.derive(ctx, q(el, '#eq'), { head: 'Building the closed form · thesis Ch. 5', lines: [
        { tex: 'c=\\dfrac{1-d+d\\,r_D}{|V|}', note: 'c = the equal share every node gets each step (restart share + dangling share)<br>A node with no incoming edge gets only this → score = c<br>Small world: $c=\\tfrac{0.15+0.85\\times0.4706}{4}=0.1375=r_A$ ✓' },
        { tex: 'r_v=c+d\\sum_{u}\\part{rc}{c}\\,\\dfrac{w(u,v)}{o(u)}', note: 'Every node: c + shares along in-edges · owners u without in-edges: put c for $r_u$', mark: 'rc' },
        { tex: 'r_v=c+c\\,d\\,\\part{dl}{\\delta(v)}=c\\,\\bigl(1+d\\,\\delta(v)\\bigr)', note: 'Same c for all u → out of the sum → rest $\\delta(v)=\\sum_u w(u,v)/o(u)$ → factor out c', mark: 'dl' },
        { tex: 'r_B=0.1375\\times\\bigl(1+0.85\\times\\part{f}{\\tfrac23}\\bigr)=0.2154\\ \\checkmark', note: 'B’s only owner is A: 2 of A’s weight 3 goes to B', mark: 'f' },
        { tex: '\\begin{aligned}r_C&=0.1375\\times\\bigl(1+0.85\\times\\tfrac13\\bigr)=0.1765\\ \\checkmark\\\\ r_D&=c+d\\,(r_B+r_C)=0.4706\\end{aligned}', note: 'Not for D: its owners B and C receive approvals → shares spread one more step' },
        { tex: '\\text{score order}=\\delta(v)\\ \\text{order}', note: 'c and d are equal for all depth-one spenders → for any d, δ sets the order', mark: null }
      ] });
      ctx.katex(q(el, '#eq'));
      /* symbol cards */
      var syms = q(el, '#syms');
      g.symC = Comp.symbolCard(ctx, syms, { tex: 'c', desc: 'Equal share for every node at each step · score of a node with no incoming edge' });
      g.symD = Comp.symbolCard(ctx, syms, { tex: '\\delta(v)', desc: 'Sum of the pieces each owner gives' });
      g.syms = syms;
      /* pie example (step 5) */
      var pie = q(el, '#pie');
      g.pie = pie; gsap.set(pie, { autoAlpha: 0 });
      txt(pie, 0, 18, 'Example · three owners, spender v', { fill: C.ink3, 'font-size': 18, 'class': 'svg-mono' });
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
        txt(gg, cx, cy + R + 28, o.k === 1 ? 'approves 1 spender' : 'approves ' + o.k + ' spenders', { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18 });
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
      g.gT2 = txt(pie, GX, G0 + 64, 'divided count', { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18 });
      g.tal = Comp.tally(ctx, pie, { x: 800, y: G0 - 46, size: 40 });
      g.talT = txt(pie, 820, G0 + 36, 'count 3', { 'text-anchor': 'middle', fill: C.deg, 'font-size': 24, 'font-weight': 800 });
      g.talT2 = txt(pie, 820, G0 + 64, 'plain count', { 'text-anchor': 'middle', fill: C.ink2, 'font-size': 18 });
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
  var CFR = get(SW, 'closed_form', {}), CF0 = get(W0, 'closed_form', {});
  var CF = { spenders: CFR.spenders || 6224, d1: CFR.depth_one_spenders || 5232,
    inDeep: CFR.within_1pct_deeper != null ? CFR.within_1pct_deeper : 0.2188,
    pD1: pc1(CFR.within_1pct_depth_one != null ? CFR.within_1pct_depth_one : 1),
    pDeep: pc1(CFR.within_1pct_deeper != null ? CFR.within_1pct_deeper : 0.2188),
    pAll: pc1(CFR.within_1pct_all != null ? CFR.within_1pct_all : 0.8755),
    tau: fx(CFR.tau_score_vs_delta != null ? CFR.tau_score_vs_delta : 0.9085, 3),
    w0n: CF0.spenders || 7905, w0All: pc1(CF0.within_1pct_all != null ? CF0.within_1pct_all : 0.7075) };
  CF.deeper = CF.spenders - CF.d1;
  CF.pD1 = CF.pD1.replace(/\.0$/, '');
  function frow(label, sub, s, color, ghost) {
    var d = iv(s), gd = ghost ? iv(ghost) : null;
    return { label: label, sub: sub, est: d.est, lo: d.lo, hi: d.hi, color: color, text: s, ghost: gd ? { est: gd.est, lo: gd.lo, hi: gd.hi } : null };
  }
  var slide8 = {
    id: 's08-08', title: 'How well the closed form fits · results on one page', time: 45, steps: 4,
    tags: function (s) { return s >= 4 ? ['posthoc', 'registered-analysis'] : []; },
    notes: [
      'We checked how well this formula fits on the real graph. One dot is 10 same-window spenders.',
      'Of the ' + n0(CF.spenders) + ' same-window spenders, ' + n0(CF.d1) + ' were depth-one spenders. Dark amber is depth one; the pale dots and the dots with a rose outline are deeper spenders.',
      'Every single depth-one spender matched the formula to within 1%. Of the remaining ' + n0(CF.deeper) + ' deeper spenders, only ' + CF.pDeep + '% matched, which means that shares spreading over several steps really exist. Over all spenders it is ' + CF.pAll + '%, and in W0 ' + CF.w0All + '%. Kendall’s tau between the EndorseRank score and delta is ' + CF.tau + '.',
      'Yet even with that spreading, EndorseRank did not beat the plain count. The deeper spenders were not tested on their own. Whether spreading adds anything to the count would need a deeper sample, reaching two or more steps out, tested separately.',
      'Below, the four comparisons with the raw degree are gathered on one page. All four lie left of 0: on the transfer side and on the allowance side alike, the plain count wins. Add the restart variant, and still no walk score beat the count it smooths. The gray markers are the registered analysis: on the allowance side they point the same way, while on the transfer side that analysis had AWP slightly above the count. All four comparisons were computed after the labels were known.'
    ],
    html:
      '<h1 class="t-h1">[[Every]] depth-one spender follows the formula</h1>' +
      '<div class="abs" id="top" data-in="none" style="left:0;top:0;width:1920px;height:820px">' +
        '<div class="abs s8-leg" id="leg" style="left:96px;top:186px"><span><i style="background:#F5B43C"></i>Depth one · within 1%</span><span><i style="background:rgba(245,180,60,.42)"></i>Deeper · within 1%</span><span><i style="background:transparent;border:2px solid #FF6B8A;width:12px;height:12px"></i>Deeper · outside 1%</span><span class="ink-3">One dot = 10 spenders · same window</span></div>' +
        '<div id="wf8" style="position:absolute;left:96px;top:232px"></div>' +
        '<div class="abs s8-cnt" id="cnt" style="left:1330px;top:226px;width:494px">' +
          '<div class="row"><span>Same-window spenders</span><b>' + n0(CF.spenders) + '</b></div>' +
          '<div class="row"><span>Depth one <b>' + n0(CF.d1) + '</b> → within 1%</span><span class="pc" id="c1">0%</span></div>' +
          '<div class="row"><span>Deeper <b>' + n0(CF.deeper) + '</b> → within 1%</span><span class="pc" id="c2" style="color:rgba(245,180,60,.75)">0%</span></div>' +
          '<div class="row" style="border-bottom:0"><span>All</span><span class="pc" id="c3" style="color:var(--ink)">0%</span></div>' +
          '<div id="w0l" style="font-size:21px;color:var(--ink-3);margin-top:6px">W0: <b>' + n0(CF.w0n) + '</b> spenders · all <b>' + CF.w0All + '%</b><br>Kendall’s τ of score and δ <b>' + CF.tau + '</b> (same window)</div>' +
        '</div>' +
        '<p class="abs s8-concl" id="concl" style="left:96px;top:700px;width:1700px">The spreading was there, but it did not lift EndorseRank above the count</p>' +
      '</div>' +
      '<div class="abs s8-reason" id="mini" data-in="none" style="left:720px;top:214px;width:1100px">Spenders within 1% of the formula (same window)<br><b class="c-allow tnum">depth one ' + CF.pD1 + '%</b> · <b class="tnum" style="color:rgba(245,180,60,.8)">deeper ' + CF.pDeep + '%</b> · <b class="tnum">all ' + CF.pAll + '%</b><br><span style="font-size:22px;color:var(--ink-3)">The spreading was there, but it did not lift the score above the count</span></div>' +
      '<div class="abs" id="sum" data-in="none" style="left:96px;top:478px;width:1728px">' +
        '<div class="s8-sumhd">Four comparisons with the raw degree: the plain count wins all four</div>' +
        '<div class="s8-tiny" style="margin:4px 0 0">' + pill('posthoc') + '<span>All computed after the labels were known · colored dots = revised analysis (main result) · gray hollow dots = registered analysis (AWP slightly above on the transfer side)</span></div>' +
        '<div id="fp" style="margin-top:6px"></div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.top = q(el, '#top'); g.leg = q(el, '#leg'); g.mini = q(el, '#mini'); g.cnt = q(el, '#cnt'); g.concl = q(el, '#concl'); g.sum = q(el, '#sum'); g.w0l = q(el, '#w0l');
      g.c1 = q(el, '#c1'); g.c2 = q(el, '#c2'); g.c3 = q(el, '#c3');
      gsap.set([g.cnt, g.concl, g.sum, g.w0l, g.mini], { autoAlpha: 0 });
      /* 622 dots: 523 depth-one (5,232 / 10), 22 deeper within 1 % (992 × 0.2188 / 10), 77 deeper outside */
      var N1 = Math.round(CF.d1 / 10), NIN = Math.round(CF.deeper * CF.inDeep / 10), NT = Math.round(CF.spenders / 10), NOUT = NT - N1 - NIN;
      g.N1 = N1; g.NIN = NIN; g.NOUT = NOUT;
      g.WF = waffle(ctx, q(el, '#wf8'), { n: NT, max: NT, cols: 44, gap: 26.4, r: 9, style: function (i, hq) {
        if (i < N1) return { fill: C.allow };
        if (i < N1 + NIN) return { fill: 'rgba(245,180,60,.42)' };
        return { fill: C.bg2, stroke: C.hi, lw: 2.2 };
      } });
      g.F = Comp.forest(ctx, q(el, '#fp'), { w: 1728, rowH: 86, labelWidth: 470, valueWidth: 300, domain: [-0.11, 0.05], ticks: [-0.1, -0.08, -0.06, -0.04, -0.02, 0, 0.02, 0.04], hidden: true,
        tickFormat: function (t) { return t === 0 ? '0' : sfmt(t, 2); }, axisLabel: 'Δτ (← raw count better · walk score better →)',
        rows: [
          frow('AWP − transfer in-degree', 'W0 · new senders', T4.d0, 'xfer', T4.g0),
          frow('AWP − transfer in-degree', 'W1 · new senders', T4.d1, 'xfer', T4.g1),
          frow('EndorseRank − in-approve degree', 'W0 · new approval pairs', T5.d0, 'allow', T5.g0),
          frow('EndorseRank − in-approve degree', 'W1 · new approval pairs', T5.d1, 'allow', T5.g1)
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
        tl.add(ctx.count(g.c1, 0, +CF.pD1, { decimals: 0, suffix: '%', final: CF.pD1 + '%', duration: 1.0 }), 0);
        tl.add(ctx.count(g.c2, 0, +CF.pDeep, { decimals: 1, suffix: '%', final: CF.pDeep + '%', duration: 1.0 }), 0.35);
        tl.add(ctx.count(g.c3, 0, +CF.pAll, { decimals: 1, suffix: '%', final: CF.pAll + '%', duration: 1.0 }), 0.7);
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
    title: 'Results',
    slides: [slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8]
  });
})();
