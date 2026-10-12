/* =========================================================================
   s05-weights — 화살표의 무게 (STORYBOARD.md §2, s05-01 … s05-06)

   s05-01  왜 화살표마다 무게가 다를까   the small world flies over from s04-07 (shared element);
                                         its arrows act out "old" / "small" / "big"; σ × V chips meet
   s05-02  시간 무게 σ(Δt)              the age ruler of s03-01 rises and turns into the x-axis;
                                         a straight line fails (negative after 360 days); penalty s → e^s
                                         (table of e^−2 … e^2) → σ, a draggable Δt handle, ratio bars ÷e
                                         per 100 days (z is kept for the dollar amount only)
   s05-03  금액 무게 V(z)               y = e^{−bz} ball; curve stops under a glass ceiling at 1;
                                         morph into the registered setting (raw units, b = 1)
   s05-04  b = ln 3 / m                 coins sorted to the median; nine-step derivation that folds
                                         itself up; transfer and allowance curves; a dollar slider
   s05-05  두 그래프의 무게와 다시 출발   AWP: every transfer adds σ·V; EndorseRank: latest approval per
                                         token; restart halos (activeness vs uniform)
   s05-06  달러로 바꾸기와 상한 U        base units → dollars; one owner's row swallowed by an unlimited
                                         approval; the cap U cuts it to 97.6 % / 2.4 %

   Numbers and sources
     k = 0.01, t0 = 180 days, m_T = 200, m_A = 62, raw medians 203.7129 / 61.5102, b_T, b_A, U = 20,000,
     raw p99 of transfers 20,266.4, first cap definition ≈ 1e47 — DECK_DATA.params (decay, value, cap) =
       revised digest R§D constants.*
     σ(0) = 0.8581 — R§8 sigma0; σ table 0.711 / 0.5 / 0.136 / 0.004 / 0.0003 — computed from k, t0 (계산)
     transfers 1,073,838,657 and finite allowances 6,491,970 up to t1 — R§D constants.raw.n_transfers,
       constants.raw.n_finite_allowances (digest values, written here)
     99.52 %, 99.78 % (≥ 10 base units) — registered digest G§D amounts.*_ge10_share
       = DECK_DATA.scale.registered.amounts, status tag 등록 분석
     45.8 %, 53.8 %, 797,852 — R§D amounts.* = DECK_DATA.scale.revised.amounts
     2705b28 — revised digest header (code revision of the amended cap)
     every dollar amount, date and token on s05-01, s05-04 (coins), s05-05 and s05-06 is 예시;
       their weights are computed with the formulas above (계산)
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt;
  var NS = 'http://www.w3.org/2000/svg';
  var DATA = window.DECK_DATA || {};
  var PRM = DATA.params || {}, DEC = PRM.decay || {}, VAL = PRM.value || {}, CAP = PRM.cap || {};
  var K = DEC.k != null ? DEC.k : 0.01, T0 = DEC.t0_days != null ? DEC.t0_days : 180;
  var MT = VAL.m_T || 200, MA = VAL.m_A || 62, MT_RAW = VAL.m_T_raw || 203.7129, MA_RAW = VAL.m_A_raw || 61.5102;
  var LN3 = Math.log(3), BT = LN3 / MT, BA = LN3 / MA;
  var U = CAP.U_usd || 20000, P99T = CAP.p99_transfer_usd_raw || 20266.3877;
  var AMR = (((DATA.scale || {}).revised || {}).amounts) || {};
  var AMG = (((DATA.scale || {}).registered || {}).amounts) || {};
  var UNL = AMR.unlimited_share != null ? AMR.unlimited_share : 0.4578;
  var ATCAP = AMR.allowances_at_or_above_cap_share != null ? AMR.allowances_at_or_above_cap_share : 0.5382;
  var BOTH = AMR.owners_with_both_kinds != null ? AMR.owners_with_both_kinds : 797852;
  var GE10T = AMG.transfers_ge10_share != null ? AMG.transfers_ge10_share : 0.9952;
  var GE10A = AMG.allowances_ge10_share != null ? AMG.allowances_ge10_share : 0.9978;
  var N_TRANSFERS = 1073838657, N_FINITE_ALLOW = 6491970;          /* R§D constants.raw.* */
  var MAX_AGE = 1004;                                              /* oldest event at T_obs (thesis Ch. 3) */

  function sigma(dt) { return 1 / (1 + Math.exp(K * (dt - T0))); }
  function V(z, b) { return 2 / (1 + Math.exp(-b * z)) - 1; }
  function f4(v) { return fmt(v, 4); }
  var UID = 0;
  function uid(p) { UID += 1; return 's5-' + p + '-' + UID; }
  function sup(n) { return String(n).replace(/-/g, '⁻').replace(/\d/g, function (c) { return '⁰¹²³⁴⁵⁶⁷⁸⁹'.charAt(+c); }); }
  function n0(v) { return fmt(v, 0); }
  function pct(v) { return fmt(v * 100, 1) + '%'; }
  function pct2(v) { return fmt(v * 100, 2) + '%'; }

  /* ------------------------------------------------------------ section styles */
  var CSS = [
    '.s5-sub{position:absolute;left:96px;top:164px;width:1728px;font-size:30px;line-height:44px;color:var(--ink-2)}',
    '.s5-panel{position:absolute;left:1040px;top:196px;width:784px;height:794px;border-radius:24px;background:var(--bg-2);padding:30px 40px}',
    '.s5-panel > * + *{margin-top:14px}',
    '.s5-k{font-family:var(--font-mono);font-size:17px;line-height:24px;color:var(--ink-3);letter-spacing:0}',
    '.s5-L{font-size:34px;line-height:48px;font-weight:700;letter-spacing:-.01em}',
    '.s5-l{font-size:28px;line-height:42px;color:var(--ink-2)}',
    '.s5-l b,.s5-L b{color:var(--ink);font-weight:700}',
    '.s5-note{font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s5-note b{color:var(--ink)}',
    '.s5-tx{font-size:30px;line-height:44px}',
    '.s5-tx .katex-display{margin:0;text-align:left}.s5-tx .katex-display>.katex{text-align:left}',
    '.s5-read{font-family:var(--font-mono);font-size:22px;line-height:32px;color:var(--ink-2);letter-spacing:0;padding:10px 14px;border-radius:12px;background:var(--bg-3);white-space:nowrap}',
    '.s5-read b{color:var(--ink);font-weight:700}',
    '.s5-read .hl2{color:var(--c-hi)}',
    /* custom derivation list that can fold finished steps */
    '.s5-dv .hd{display:flex;justify-content:space-between;font-family:var(--font-mono);font-size:17px;line-height:24px;color:var(--ink-3);letter-spacing:0;margin-bottom:4px}',
    '.s5-dl{display:flex;gap:18px;align-items:baseline;padding:7px 0;overflow:hidden}',
    '.s5-dl .no{flex:0 0 auto;width:34px;font-family:var(--font-mono);font-size:17px;color:var(--ink-3);letter-spacing:0}',
    '.s5-dl .b{flex:1 1 auto;min-width:0}',
    '.s5-dl .tx{font-size:30px;line-height:42px}',
    '.s5-dl .tx .formula.display{text-align:left}',
    '.s5-dl .tx .katex-display{margin:0;text-align:left}.s5-dl .tx .katex-display>.katex{text-align:left}',
    '.s5-dl .nt{font-size:21px;line-height:30px;color:var(--ink-2)}',
    '.s5-dl.sum{padding:4px 0}',
    '.s5-dl.sum .b{font-size:21px;line-height:30px;color:var(--ink-3);border-left:3px solid var(--line);padding-left:14px}',
    '.s5-dl.sum .b .katex{font-size:1.05em}',
    /* checklist */
    '.s5-check{position:absolute;padding:16px 20px;border-radius:16px;background:rgba(16,21,31,.9);border:1px solid var(--line)}',
    '.s5-check .t{font-family:var(--font-mono);font-size:17px;color:var(--ink-3);letter-spacing:0;margin-bottom:6px}',
    '.s5-check .it{display:flex;align-items:center;gap:12px;font-size:24px;line-height:38px;color:var(--ink-2)}',
    '.s5-check .bx{position:relative;flex:0 0 auto;width:24px;height:24px;border-radius:6px;border:2px solid var(--ink-3)}',
    '.s5-check .bx svg{position:absolute;left:-2px;top:-4px;overflow:visible}',
    '.s5-check .it.on{color:var(--ink)}',
    '.s5-check .it.bad{color:var(--c-hi)}',
    /* dark halo behind chart labels so curves and guides never strike them through */
    '.s5-halo{paint-order:stroke;stroke:#0A0D14;stroke-width:5px;stroke-linejoin:round}',
    /* compact symbol cards */
    '.sym-card.s5-sc{display:grid;grid-template-columns:auto auto;column-gap:14px;row-gap:2px;align-items:center;min-width:0;max-width:300px;padding:10px 16px}',
    '.sym-card.s5-sc .sym{grid-row:1 / span 2;font-size:32px}',
    '.sym-card.s5-sc .sym-desc{grid-column:2;font-size:19px;line-height:26px}',
    '.sym-card.s5-sc .sym-art{grid-column:2}',
    /* s05-01 */
    '.s5-row{position:absolute;left:96px;width:930px;display:flex;gap:26px;align-items:flex-start}',
    '.s5-row .ic{flex:0 0 auto;width:72px;height:72px}',
    '.s5-row .tt{flex:1 1 auto}',
    '.s5-row .h{font-size:34px;line-height:46px;font-weight:700;letter-spacing:-.01em}',
    '.s5-row .s{font-size:26px;line-height:38px;color:var(--ink-2);margin-top:4px}',
    '.s5-row .s b{color:var(--ink)}',
    '.s5-row .mini{flex:0 0 auto}',
    '.s5-chip{display:inline-flex;align-items:center;justify-content:center;min-width:76px;height:64px;padding:0 14px;border-radius:16px;border:2px solid var(--ink-2);font-size:36px;background:var(--bg-3)}',
    '.s5-chip .katex{font-size:1em}',
    '.s5-times{display:inline-block;font-size:40px;color:var(--ink-2);margin:0 16px}',
    '.s5-hero .katex{font-size:46px}',
    /* s05-05 */
    '.s5-two{position:absolute;top:196px;width:840px;height:676px;border-radius:24px;background:var(--bg-2);padding:26px 34px}',
    '.s5-two > * + *{margin-top:10px}',
    '.s5-kind{display:inline-flex;align-items:center;gap:10px;font-size:26px;line-height:36px;font-weight:700}',
    '.s5-kind i{display:inline-block;width:26px;height:4px;border-radius:2px}',
    '.s5-sym{display:flex;gap:18px;flex-wrap:wrap;font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s5-sym > span{display:inline-block;margin-right:6px}',
    '.s5-sym .katex{font-size:1.15em;color:var(--ink)}',
    '.s5-wbar{font-family:var(--font-mono);font-size:26px;letter-spacing:0}',
    '.s5-bottom{position:absolute;left:96px;top:892px;width:1728px;font-size:32px;line-height:46px;font-weight:600}',
    /* s05-06 */
    '.s5-amt{position:absolute;left:96px;top:196px;width:900px}',
    '.s5-slots{display:flex;align-items:center;gap:12px;font-size:28px;line-height:44px;font-variant-numeric:tabular-nums;margin-top:10px}',
    '.s5-slots .sl{padding:2px 12px;border-radius:10px;background:var(--bg-3);font-weight:700}',
    '.s5-slots .op{color:var(--ink-3)}',
    '.s5-flt{position:absolute;font-family:var(--font-mono);font-size:22px;letter-spacing:0;color:var(--ink);white-space:nowrap}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s05-style')) return;
    var st = document.createElement('style'); st.id = 's05-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  /* ------------------------------------------------------------ helpers */
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
  function txt(svg, x, y, s, a) {
    var t = S('text', { x: x, y: y, fill: (a && a.fill) || C.ink3, 'font-size': (a && a.size) || 18, 'text-anchor': (a && a.anchor) || 'start', 'font-weight': (a && a.weight) || null, 'class': (a && a.cls) || null }, svg);
    t.textContent = s; return t;
  }
  function card(ctx, el, o) { o.className = 's5-sc'; return Comp.symbolCard(ctx, el, o); }
  function drawPath(p, o) {
    o = o || {};
    var L = 1; try { L = p.getTotalLength(); } catch (e) { /* ignore */ }
    return gsap.fromTo(p, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: o.duration || 1.2, ease: o.ease || 'power2.inOut', delay: o.delay || 0,
      onComplete: function () { p.style.strokeDasharray = o.dash || ''; p.style.strokeDashoffset = ''; } });
  }
  /* a plot area: host div at stage (x, y), SVG w × h; inner box l..r × t..b */
  function plot(ctx, el, o) {
    var host = H('div', '', el); host.setAttribute('data-in', 'none');
    host.style.cssText = 'position:absolute;left:' + o.x + 'px;top:' + o.y + 'px;width:' + o.w + 'px;height:' + o.h + 'px';
    var svg = Comp.svg(ctx, host, { w: o.w, h: o.h });
    var P = { host: host, svg: svg, l: o.l, r: o.r, t: o.t, b: o.b, xd: o.xd, yd: o.yd || [0, 1] };
    P.px = function (v) { return P.l + (v - P.xd[0]) / (P.xd[1] - P.xd[0]) * (P.r - P.l); };
    P.py = function (v) { return P.b - (v - P.yd[0]) / (P.yd[1] - P.yd[0]) * (P.b - P.t); };
    P.grid = S('g', {}, svg); P.under = S('g', {}, svg); P.main = S('g', {}, svg); P.over = S('g', {}, svg);
    return P;
  }
  function yAxis(P, ticks, title) {
    var g = S('g', {}, P.grid);
    ticks.forEach(function (t) {
      S('line', { x1: P.l, x2: P.r, y1: P.py(t[0]), y2: P.py(t[0]), 'class': 'gridline' }, g);
      txt(g, P.l - 14, P.py(t[0]) + 6, t[1], { anchor: 'end', size: 18, cls: 'svg-mono' });
    });
    S('line', { x1: P.l, x2: P.l, y1: P.t - 6, y2: P.b, stroke: C.line, 'stroke-width': 1.5 }, g);
    if (title) txt(g, P.l, P.t - 18, title, { size: 20, fill: C.ink2 });
    return g;
  }
  function xAxis(P, ticks, title) {
    var g = S('g', {}, P.grid);
    S('line', { x1: P.l, x2: P.r, y1: P.b, y2: P.b, stroke: C.ink3, 'stroke-width': 1.5 }, g);
    ticks.forEach(function (t) {
      S('line', { x1: P.px(t[0]), x2: P.px(t[0]), y1: P.b, y2: P.b + 8, stroke: C.ink3, 'stroke-width': 1.5 }, g);
      txt(g, P.px(t[0]), P.b + 32, t[1], { anchor: 'middle', size: 19, cls: 'svg-mono' });
    });
    if (title) txt(g, P.r, P.b + 62, title, { anchor: 'end', size: 20, fill: C.ink2 });
    return g;
  }
  function curvePath(P, f, a, b, n, scale) {
    var d = '';
    for (var i = 0; i <= n; i++) {
      var v = scale === 'log' ? Math.pow(10, Math.log10(a) + (Math.log10(b) - Math.log10(a)) * i / n) : a + (b - a) * i / n;
      d += (i ? 'L' : 'M') + P.px(scale === 'log' ? Math.log10(v) : v).toFixed(1) + ',' + P.py(f(v)).toFixed(1);
    }
    return d;
  }
  /* custom derivation list: rows appear one by one; finished groups fold into one summary row */
  function Deriv(ctx, parent, o) {
    var el = H('div', 's5-dv', parent);
    var hd = H('div', 'hd', el, '<span>' + (o.head || '유도') + '</span><span class="cnt"></span>');
    var cnt = q(hd, '.cnt');
    var D = { el: el, rows: [], sums: [], k: 0, total: o.lines.length };
    o.lines.forEach(function (ln, i) {
      var row = H('div', 's5-dl', el);
      H('div', 'no', row, String(i + 1));
      var b = H('div', 'b', row);
      var F = null;
      if (ln.tex) { var tx = H('div', 'tx', b); F = Comp.formula(ctx, tx, ln.tex, { display: ln.display !== false }); }
      if (ln.tex2) { var tx2 = H('div', 'tx', b); var F2 = Comp.formula(ctx, tx2, ln.tex2, { display: ln.display !== false }); if (ln.markOn2) F = F2; }
      if (ln.note) H('div', 'nt', b, ln.note);
      if (ln.html) H('div', 'hx', b, ln.html);
      row.style.display = 'none';
      D.rows.push({ el: row, F: F, data: ln, state: 'hidden' });
    });
    (o.groups || []).forEach(function (gp) {
      var row = H('div', 's5-dl sum', null);
      H('div', 'no', row, gp.from === gp.to ? String(gp.from) : gp.from + '–' + gp.to);
      H('div', 'b', row, gp.summary);
      el.insertBefore(row, D.rows[gp.from - 1].el);
      row.style.display = 'none';
      D.sums.push({ el: row, g: gp, state: 'hidden' });
    });
    ctx.katex(el);
    function setCount(k) { cnt.textContent = '단계 ' + k + ' / ' + D.total; }
    setCount(0);
    function folded(i, k) { return (o.groups || []).some(function (gp) { return k >= gp.at && i + 1 >= gp.from && i + 1 <= gp.to; }); }
    D.show = function (k) {
      var tl = gsap.timeline();
      D.rows.forEach(function (R, i) {
        var want = i < k ? (folded(i, k) ? 'folded' : 'shown') : 'hidden';
        if (want === R.state) return;
        if (want === 'shown') {
          R.el.style.display = '';
          gsap.set(R.el, { height: 'auto', paddingTop: 7, paddingBottom: 7 });
          if (i === k - 1) {
            tl.fromTo(R.el, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.55, ease: E.out }, 0.05);
            if (R.F && R.data.mark) tl.call(function () { ctx.add(function () { R.F.mark(R.data.mark); }); }, null, 0.5);
          } else gsap.set(R.el, { autoAlpha: 1, y: 0 });
        } else if (want === 'folded') {
          tl.to(R.el, { height: 0, paddingTop: 0, paddingBottom: 0, autoAlpha: 0, duration: 0.45, ease: E.io, onComplete: function () { R.el.style.display = 'none'; } }, 0);
        } else { R.el.style.display = 'none'; gsap.set(R.el, { autoAlpha: 0 }); }
        R.state = want;
      });
      D.sums.forEach(function (Sm) {
        var want = k >= Sm.g.at ? 'shown' : 'hidden';
        if (want === Sm.state) return;
        if (want === 'shown') { Sm.el.style.display = ''; tl.fromTo(Sm.el, { autoAlpha: 0, height: 0 }, { autoAlpha: 1, height: 'auto', duration: 0.45, ease: E.io }, 0.2); }
        else { Sm.el.style.display = 'none'; }
        Sm.state = want;
      });
      var prev = D.rows[D.k - 1];
      if (prev && prev.F && k !== D.k) tl.add(prev.F.unmark(), 0);
      tl.call(setCount, [k], 0);
      D.k = k;
      return tl;
    };
    return D;
  }
  function hold(ctx, sec) { return ctx.timeout(function () { /* wait for fragment reveals */ }, sec * 1000); }
  function slideIn(ctx, els, o) { /* small helper: rise a list of elements */
    o = o || {};
    return gsap.fromTo(els, { autoAlpha: 0, y: o.y != null ? o.y : 18 }, { autoAlpha: 1, y: 0, duration: o.duration || 0.5, ease: E.out, stagger: o.stagger || 0.1, delay: o.delay || 0 });
  }

  /* ================================================================ s05-01 */
  var SWX = 1064, SWY = 250;
  function clockIcon() {
    return '<svg class="ic" viewBox="0 0 72 72"><circle cx="36" cy="36" r="30" fill="none" stroke="' + C.ink2 + '" stroke-width="3"/>' +
      '<g class="hand-m"><line x1="36" y1="36" x2="36" y2="14" stroke="' + C.ink + '" stroke-width="3.5" stroke-linecap="round"/></g>' +
      '<g class="hand-h"><line x1="36" y1="36" x2="50" y2="36" stroke="' + C.ink2 + '" stroke-width="4" stroke-linecap="round"/></g>' +
      '<circle cx="36" cy="36" r="3.5" fill="' + C.ink + '"/></svg>';
  }
  function coinIcon() {
    var s = '<svg class="ic" viewBox="0 0 72 72">';
    for (var i = 0; i < 4; i++) s += '<ellipse cx="36" cy="' + (56 - i * 11) + '" rx="22" ry="8" fill="' + C.bg3 + '" stroke="' + C.ink2 + '" stroke-width="2.5"/>';
    return s + '</svg>';
  }
  function miniSigma() {
    var w = 250, h = 120, s = '<svg class="mini" width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '">', d = '';
    for (var i = 0; i <= 60; i++) { var dt = i / 60 * 800, x = 10 + dt / 800 * 230, y = 104 - sigma(dt) * 86; d += (i ? 'L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1); }
    s += '<line x1="10" x2="240" y1="104" y2="104" stroke="' + C.line + '" stroke-width="1.5"/>';
    s += '<path d="' + d + '" fill="none" stroke="' + C.ink2 + '" stroke-width="2.5"/>';
    var x1 = 10 + 1 / 800 * 230, y1 = 104 - sigma(1) * 86, x2 = 10 + 730 / 800 * 230, y2 = 104 - sigma(730) * 86;
    s += '<circle cx="' + x1 + '" cy="' + y1 + '" r="6" fill="' + C.ink + '"/><text x="' + (x1 + 12) + '" y="' + (y1 + 4) + '" fill="' + C.ink2 + '" font-size="16">어제</text>';
    s += '<circle class="old" cx="' + x2 + '" cy="' + y2 + '" r="6" fill="' + C.ink + '"/><text class="old" x="' + (x2 - 4) + '" y="' + (y2 - 14) + '" fill="' + C.ink2 + '" font-size="16" text-anchor="end">2년 전</text>';
    return s + '</svg>';
  }
  function miniV() {
    var w = 250, h = 120, s = '<svg class="mini" width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '">', d = '';
    function X(z) { return 10 + (Math.log10(z) - 0) / 4 * 230; }
    for (var i = 0; i <= 60; i++) { var z = Math.pow(10, i / 60 * 4), y = 104 - V(z, BA) * 78; d += (i ? 'L' : 'M') + X(z).toFixed(1) + ',' + y.toFixed(1); }
    s += '<line x1="10" x2="240" y1="104" y2="104" stroke="' + C.line + '" stroke-width="1.5"/>';
    s += '<rect x="10" y="12" width="230" height="14" fill="rgba(233,237,245,.08)"/><line x1="10" x2="240" y1="26" y2="26" stroke="' + C.ink2 + '" stroke-width="1.5" stroke-dasharray="5 5"/>';
    s += '<text x="244" y="31" fill="' + C.ink2 + '" font-size="16">1</text>';
    s += '<path d="' + d + '" fill="none" stroke="' + C.ink2 + '" stroke-width="2.5"/>';
    s += '<circle cx="' + X(5) + '" cy="' + (104 - V(5, BA) * 78) + '" r="6" fill="' + C.ink + '"/><text x="' + (X(5) - 2) + '" y="' + (104 - V(5, BA) * 78 - 14) + '" fill="' + C.ink2 + '" font-size="16" text-anchor="end">5달러</text>';
    s += '<circle cx="' + X(5000) + '" cy="' + (104 - V(5000, BA) * 78) + '" r="6" fill="' + C.ink + '"/><text x="' + (X(5000) - 8) + '" y="' + (104 - V(5000, BA) * 78 + 26) + '" fill="' + C.ink2 + '" font-size="16" text-anchor="end">5,000달러</text>';
    return s + '</svg>';
  }
  var s1 = {
    id: 's05-01', title: '왜 화살표마다 무게가 다를까', time: 30, steps: 3,
    notes: [
      '앞에서는 화살표의 무게를 2, 1, 3, 1로 그냥 정해 두었어요. 실제 데이터에서는 이 무게를 어떻게 정할까요? 같은 허락이라도 무게가 달라야 해요.',
      '어제 한 허락과 2년 전에 한 허락은 지금 뜻하는 바가 달라요. 오래된 허락일수록 가볍게 세요. 이것이 시간 무게 시그마예요.',
      '5달러 허락과 5,000달러 허락도 달라요. 큰 허락일수록 무겁게 세되, 아무리 커도 끝이 있게 만들어요. 이것이 금액 무게 V예요.',
      '그래서 한 사건의 무게는 시간 무게와 금액 무게를 곱한 값이에요. 이 방식은 송금 그래프로 점수를 매기는 AWP가 처음 쓴 것이고, 이 연구는 같은 무게를 허락 그래프에도 그대로 가져왔어요. 다음 두 장에서 두 무게를 하나씩 끌어낼게요.'
    ],
    html: '<h1 class="t-h1">같은 허락이라도 [[무게]]가 달라요</h1>' +
      '<p class="s5-sub">앞에서는 무게를 2, 1, 3, 1로 정해 두었어요 · 실제로는 어떻게 정할까요?</p>' +
      '<div class="s5-row" id="r1" data-step="1" style="top:258px">' + clockIcon() + '<div class="tt"><div class="h">어제 한 허락 vs <span id="old">2년 전</span> 허락</div>' +
        '<div class="s">오래될수록 가볍게 → <b>시간 무게 σ</b></div></div>' + miniSigma() + '</div>' +
      '<div class="s5-row" id="r2" data-step="2" style="top:452px">' + coinIcon() + '<div class="tt"><div class="h">5달러 허락 vs 5,000달러 허락</div>' +
        '<div class="s">클수록 무겁게 · 1을 넘지 않게 → <b>금액 무게 V</b></div></div>' + miniV() + '</div>' +
      '<div class="abs" id="r3" data-in="none" style="left:96px;top:650px;width:900px">' +
        '<div class="s5-l" style="color:var(--ink)">한 사건의 무게 = 시간 무게 σ × 금액 무게 V</div>' +
        '<div style="display:flex;align-items:center;margin-top:16px"><span class="s5-chip" id="cs">$\\sigma(\\Delta t)$</span><span class="s5-times" id="cx">×</span><span class="s5-chip" id="cv">$V(z)$</span>' +
        '<span class="s5-hero" id="hero" style="margin-left:34px">$=\\;w$</span></div>' +
        '<div class="s5-note" style="margin-top:22px">AWP (Do 외, 2023)가 송금에 쓴 무게를 두 그래프에 똑같이 써요</div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.W = Comp.smallWorld(ctx, el, { x: SWX, y: SWY });
      var dimmed = [g.W.edge('B', 'D'), g.W.edge('C', 'D')];
      dimmed.forEach(function (A) { gsap.set(A.g, { opacity: 0.22 }); });
      gsap.set(g.W.node('D').g, { opacity: 0.3 });
      g.AB = g.W.edge('A', 'B'); g.AC = g.W.edge('A', 'C');
      g.r3 = q(el, '#r3');
      gsap.set(g.r3, { autoAlpha: 0 });
      g.example = H('div', 'example-mark abs', el, '예시 · 금액과 날짜는 설명용'); g.example.setAttribute('data-in', 'none');
      g.example.style.cssText += ';left:' + (SWX + 30) + 'px;top:' + (SWY + 600) + 'px';
      gsap.set(g.example, { autoAlpha: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.add(g.AB.setLabel('어제'), 0.1);
        tl.add(g.AC.setLabel('2년 전'), 0.1);
        tl.to(g.example, { autoAlpha: 1, duration: 0.3 }, 0.3);
        var r1 = q(el, '#r1');
        tl.fromTo(q(r1, '.hand-m'), { rotation: 0, svgOrigin: '36 36' }, { rotation: 720, svgOrigin: '36 36', duration: 1.6, ease: 'power2.inOut' }, 0.5);
        tl.fromTo(q(r1, '.hand-h'), { rotation: 0, svgOrigin: '36 36' }, { rotation: 60, svgOrigin: '36 36', duration: 1.6, ease: 'power2.inOut' }, 0.5);
        tl.to([q(el, '#old')].concat(qa(r1, '.old')), { opacity: 0.25, duration: 1.4, ease: 'power1.in' }, 0.6);
        tl.to(g.AC.g, { opacity: 0.3, duration: 1.4, ease: 'power1.in' }, 0.6);
        tl.add(g.AC.setWidth(2, { duration: 1.4 }), 0.6);
      }
      if (i === 2) {
        tl.to(g.AC.g, { opacity: 1, duration: 0.4 }, 0);
        tl.add(g.AB.setLabel('5,000달러'), 0.1);
        tl.add(g.AC.setLabel('5달러'), 0.1);
        tl.add(g.AC.setWidth(2.5, { duration: 0.6 }), 0.5);
        tl.to(g.AB.strands, { attr: { 'stroke-width': 15 }, duration: 0.7, ease: 'power2.in' }, 0.6);
        tl.to(g.AB.strands, { attr: { 'stroke-width': 11 }, duration: 0.5, ease: 'back.out(3)' }, 1.3);
      }
      if (i === 3) {
        tl.set(g.r3, { autoAlpha: 1 }, 0);
        tl.fromTo(q(g.r3, '.s5-l'), { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
        var r1b = ctx.rect(q(el, '#r1 .h')), r2b = ctx.rect(q(el, '#r2 .h')), cs = ctx.rect(q(el, '#cs')), cv = ctx.rect(q(el, '#cv'));
        tl.fromTo(q(el, '#cs'), { autoAlpha: 0, x: r1b.x + 300 - cs.x, y: r1b.cy - cs.cy, scale: 0.6 }, { autoAlpha: 1, x: 0, y: 0, scale: 1, duration: 0.9, ease: 'power3.inOut' }, 0.3);
        tl.fromTo(q(el, '#cv'), { autoAlpha: 0, x: r2b.x + 300 - cv.x, y: r2b.cy - cv.cy, scale: 0.6 }, { autoAlpha: 1, x: 0, y: 0, scale: 1, duration: 0.9, ease: 'power3.inOut' }, 0.45);
        tl.fromTo(q(el, '#cx'), { autoAlpha: 0, scale: 2.4 }, { autoAlpha: 1, scale: 1, duration: 0.45, ease: E.stamp }, 1.3);
        tl.fromTo(q(el, '#hero'), { autoAlpha: 0, x: -20 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: E.out }, 1.6);
        tl.fromTo(q(g.r3, '.s5-note'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 2.0);
        tl.add(g.AB.setLabel('σ × V'), 1.6);
        tl.add(g.AC.setLabel('σ × V'), 1.7);
        tl.add(g.AB.setWidth(6.4, { duration: 0.6 }), 1.6);
        tl.add(g.AC.setWidth(4.2, { duration: 0.6 }), 1.6);
      }
    },
    tags: function (st) { return st >= 1 ? ['example'] : []; }
  };

  /* ================================================================ s05-02 */
  var P2 = { x: 96, y: 236, w: 920, h: 600, l: 80, r: 890, t: 52, b: 520, xd: [0, 1100] };
  var AGES = [0, 180, 365, 730, MAX_AGE];
  var LIN_END = 400;                                               /* the straight line 1 − Δt/360, drawn to 400 days */
  var EXP_S = [-2, -1, 0, 1, 2];                                   /* e^s table: 0.14, 0.37, 1, 2.7, 7.4 (계산) */
  function sx(s) { return 20 + (s + 2) / 4 * 600; }                /* s-axis of the derivation pictures */
  var s2 = {
    id: 's05-02', title: '시간 무게 σ(Δt): 180일이면 반', time: 60, steps: 6,
    notes: [
      '시간 무게부터 만들어 볼게요. 가로축은 사건이 기준일보다 며칠 전에 일어났는지예요. 데이터 부분에서 본 나이 자가 돌아서 가로축이 됐어요. 가장 오래된 기록은 1,004일 전이에요.',
      '바라는 것은 네 가지예요. 0과 1 사이일 것, 새것은 크게, 오래될수록 부드럽게 작아질 것, 그리고 180일에 딱 절반일 것.',
      '가장 쉬운 방법은 직선이에요. 1에서 시작해서 하루에 360분의 1씩 빼면, 180일에 딱 절반이에요. 그런데 360일이 지나면 0보다 작아져요. 400일 전 일은 마이너스 0.11이 돼요. 무게가 음수일 수는 없으니까 직선은 안 돼요.',
      '그래서 다른 길로 가요. 먼저 180일보다 얼마나 오래됐는지를 벌점 s로 재요. s는 k 곱하기, 델타 t 빼기 180이에요. k는 0.01이에요. 오늘 일어난 일은 s가 마이너스 1.8, 180일 전 일은 0, 1년 전 일은 1.85예요.',
      '이 벌점을 e의 지수에 올려요. e는 약 2.718인 자연 상수예요. e의 1제곱은 약 2.7, 2제곱은 약 7.4이고, 0제곱은 1이에요. 지수가 음수면 뒤집어서 나눠요. e의 마이너스 1제곱은 1 나누기 e라서 약 0.37, 마이너스 2제곱은 약 0.14예요. 그래서 e의 s제곱은 s가 무엇이든 언제나 0보다 커요. 오늘 일어난 일이면 e의 마이너스 1.8제곱, 곧 1 나누기 6.05, 약 0.165예요.',
      '이제 1을, 1 더하기 e의 s제곱으로 나눠요. 분모는 언제나 1보다 크니까 결과는 언제나 0과 1 사이예요. s가 0이면 1 나누기 2라서 딱 절반이고, s가 크면 0에 가까워져요. s가 아주 큰 음수면 1에 가까워져요. 예를 들어 s가 마이너스 5면 e의 마이너스 5제곱은 0.007이라서 시그마는 0.993이에요. 네 가지가 모두 맞아요. 그래서 오늘 일어난 일은 0.858, 1년 전 일은 0.136, 2년 전 일은 0.004만큼만 세요. 논문은 e의 무엇 제곱을 exp라고도 써요. 같은 뜻이에요. 이것이 논문 3장의 로지스틱 감쇠 식이에요.',
      '덧붙이면, 1 빼기 시그마는 e의 s제곱을, 1 더하기 e의 s제곱으로 나눈 값이에요. 그래서 남은 무게를 사라진 무게로 나누면 1 나누기 e의 s제곱, 곧 e의 마이너스 s제곱이에요. k 곱하기 100이 1이라서, 100일이 지날 때마다 이 비가 e배, 약 2.7배씩 줄어요. 아래 손잡이를 끌면 그날의 무게를 바로 볼 수 있어요.'
    ],
    html: '<h1 class="t-h1">[[180일]]이 지나면 무게가 반</h1>' +
      '<div class="s5-panel" id="pn" data-in="none">' +
        '<div class="s5-read" id="rd"><span id="rd1">Δt = <b>0</b>일 → s = <b>−1.80</b></span><span id="rd2"> → eˢ = <b>0.165</b></span><span id="rd3"> → σ = <b class="hl2">0.858</b></span></div>' +
        '<div id="dv"></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var P = g.P = plot(ctx, el, P2);
      g.yax = yAxis(P, [[0, '0'], [0.5, '0.5'], [1, '1']], '시간 무게 σ');
      /* band of ages that occur at T_obs */
      g.band = S('rect', { x: P.px(0), y: P.t, width: P.px(MAX_AGE) - P.px(0), height: P.b - P.t, fill: 'rgba(233,237,245,.035)' }, P.grid);
      g.bandL = txt(P.grid, P.px(MAX_AGE) - 6, P.t + 22, '', { anchor: 'end', size: 17 });
      g.bandL.innerHTML = 'T<tspan baseline-shift="sub" font-size="12">obs</tspan><tspan>에 있는 나이: 0–1,004일</tspan>';
      /* the straight-line attempt 1 − Δt/360: behind the ruler labels (which carry a halo) */
      g.lin = S('g', {}, P.grid);
      g.lin1 = S('path', { d: 'M' + P.px(0) + ',' + P.py(1) + 'L' + P.px(360) + ',' + P.py(0), fill: 'none', stroke: C.ink2, 'stroke-width': 3, 'stroke-dasharray': '9 7', 'stroke-linecap': 'round' }, g.lin);
      g.lin2 = S('path', { d: 'M' + P.px(360) + ',' + P.py(0) + 'L' + P.px(LIN_END) + ',' + P.py(1 - LIN_END / 360), fill: 'none', stroke: C.hi, 'stroke-width': 3.5, 'stroke-linecap': 'round' }, g.lin);
      g.linMid = S('g', {}, g.lin);
      S('circle', { cx: P.px(180), cy: P.py(0.5), r: 6, fill: C.ink2, stroke: C.bg, 'stroke-width': 2 }, g.linMid);
      txt(g.linMid, P.px(180) + 14, P.py(0.5) - 10, '180일 → 1/2 ✓', { size: 19, fill: C.ink2, weight: 600, cls: 's5-halo' });
      g.linX = S('g', {}, g.lin);
      var xe = P.px(LIN_END), ye = P.py(1 - LIN_END / 360);
      S('path', { d: 'M' + (xe - 8) + ',' + (ye - 8) + 'L' + (xe + 8) + ',' + (ye + 8) + 'M' + (xe + 8) + ',' + (ye - 8) + 'L' + (xe - 8) + ',' + (ye + 8), stroke: C.hi, 'stroke-width': 3.5, 'stroke-linecap': 'round' }, g.linX);
      txt(g.linX, xe + 16, ye + 7, '400일 → −0.11 · 음수!', { size: 19, fill: C.hi, weight: 700, cls: 's5-halo' });
      gsap.set([g.lin1, g.lin2, g.linMid, g.linX], { autoAlpha: 0 });
      /* the age ruler (s03-01): reversed at first (1,004 left, 0 right), then turns into the axis */
      g.ruler = S('g', {}, P.grid);
      g.rLine = S('line', { x1: P.px(0), x2: P.px(MAX_AGE), y1: 0, y2: 0, stroke: C.ink2, 'stroke-width': 2 }, g.ruler);
      g.rTicks = AGES.map(function (a) {
        var tg = S('g', {}, g.ruler);
        S('line', { x1: 0, x2: 0, y1: -9, y2: 9, stroke: C.ink2, 'stroke-width': 2 }, tg);
        txt(tg, 0, 34, a === MAX_AGE ? '1,004일' : a === 0 ? '0일' : String(a), { anchor: 'middle', size: 20, fill: C.ink2, cls: 'svg-mono s5-halo' });
        return { g: tg, a: a };
      });
      g.xTitle = txt(P.grid, P.r, P.b + 64, 'Δt = 기준일보다 며칠 전 (일)', { anchor: 'end', size: 20, fill: C.ink2 });
      /* σ curve, points, ratio bars */
      var d = curvePath(P, sigma, 0, 1100, 220);
      g.curve = S('path', { d: d, fill: 'none', stroke: C.ink, 'stroke-width': 4, 'stroke-linecap': 'round' }, P.main);
      gsap.set(g.curve, { autoAlpha: 0 });
      g.cross = S('g', {}, P.under);
      S('line', { x1: P.l, x2: P.px(T0), y1: P.py(0.5), y2: P.py(0.5), stroke: C.hi, 'stroke-width': 1.5, 'stroke-dasharray': '5 6' }, g.cross);
      S('line', { x1: P.px(T0), x2: P.px(T0), y1: P.py(0.5), y2: P.b, stroke: C.hi, 'stroke-width': 1.5, 'stroke-dasharray': '5 6' }, g.cross);
      gsap.set(g.cross, { autoAlpha: 0 });
      var PTS = [[0, '오늘', 'r'], [90, '90일', 'r'], [180, '180일', 'r'], [365, '1년', 'r'], [730, '2년', 'u'], [MAX_AGE, '1,004일', 'u']];
      g.pts = PTS.map(function (p) {
        var x = P.px(p[0]), y = P.py(sigma(p[0])), pg = S('g', {}, P.over);
        S('circle', { cx: x, cy: y, r: 7, fill: C.ink, stroke: C.bg, 'stroke-width': 2 }, pg);
        var v = p[0] === 180 ? '0.5' : p[0] === MAX_AGE ? fmt(sigma(p[0]), 4) : fmt(sigma(p[0]), 3);
        var lab = p[1] + ' ' + v;
        if (p[2] === 'r') txt(pg, x + 14, y - 10, lab, { size: 19, fill: p[0] === 180 ? C.hi : C.ink, weight: 600, cls: 's5-halo' });
        else txt(pg, x, y - 18, lab, { anchor: p[0] === MAX_AGE ? 'end' : 'middle', size: 19, fill: C.ink, weight: 600, cls: 's5-halo' });
        gsap.set(pg, { autoAlpha: 0 });
        return pg;
      });
      g.ratio = S('g', {}, P.under);
      [0, 100, 200, 300].forEach(function (a) {
        var x = P.px(a) + (a === 0 ? 20 : 0), s = sigma(a), w = 14;             /* the bar at 0 sits right of the Δt handle */
        S('rect', { x: x - w / 2, y: P.py(1), width: w, height: P.py(s) - P.py(1), fill: 'none', stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '3 3' }, g.ratio);
        S('rect', { x: x - w / 2, y: P.py(s), width: w, height: P.b - P.py(s), fill: C.ink, 'fill-opacity': 0.3 }, g.ratio);
      });
      gsap.set(g.ratio, { autoAlpha: 0 });
      /* draggable Δt handle: a pin above the axis, clear of the tick labels */
      g.hd = S('g', { 'class': 'no-advance', style: 'cursor:ew-resize' }, P.over);
      g.hdGuide = S('line', { x1: 0, x2: 0, y1: P.b, y2: P.b, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, g.hd);
      g.hdDot = S('circle', { cx: 0, cy: P.b, r: 7, fill: C.hi }, g.hd);
      g.hdKnob = S('path', { d: 'M0,0 l-11,-18 h22 z', fill: C.bg3, stroke: C.ink, 'stroke-width': 2.5, 'stroke-linejoin': 'round' }, g.hd);
      g.hit = S('rect', { x: P.l - 10, y: P.b - 30, width: P.r - P.l + 20, height: 64, fill: 'transparent', 'class': 'no-advance', style: 'cursor:ew-resize' }, P.over);
      gsap.set([g.hd, g.hit], { autoAlpha: 0 });
      g.state = { dt: 0, curve: false };
      /* checklist (upper right of the plot) */
      var ck = g.check = H('div', 's5-check', el); ck.setAttribute('data-in', 'none');
      ck.style.left = (P2.x + P.px(500)) + 'px'; ck.style.top = (P2.y + P.t + 30) + 'px';
      H('div', 't', ck, '원하는 성질');
      g.items = ['0과 1 사이', '새것은 크게', '오래될수록 작게, 부드럽게', '180일에 딱 1/2'].map(function (t, k) {
        var cross = k === 0 ? '<path class="xx" d="M5,5 L25,25 M25,5 L5,25" fill="none" stroke="' + C.hi + '" stroke-width="3.5" stroke-linecap="round"/>' : '';
        var it = H('div', 'it', ck, '<span class="bx"><svg width="30" height="30" viewBox="0 0 30 30"><path class="ok" d="M4,14 L11,22 L27,2" fill="none" stroke="' + C.ink + '" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>' + cross + '</svg></span><span>' + t + '</span>');
        gsap.set(qa(it, 'path'), { autoAlpha: 0 });
        return it;
      });
      gsap.set(ck, { autoAlpha: 0 });
      /* derivation pictures: the s-ball line and the e^s bars, on the same s-axis */
      var sline = '<svg width="640" height="64" viewBox="0 0 640 64" style="display:block;margin-top:4px;overflow:visible"><line x1="20" x2="620" y1="26" y2="26" stroke="' + C.ink3 + '" stroke-width="2"/>' +
        EXP_S.map(function (s) { var x = sx(s); return '<line x1="' + x + '" x2="' + x + '" y1="18" y2="34" stroke="' + C.ink3 + '" stroke-width="2"/><text x="' + x + '" y="58" text-anchor="middle" fill="' + C.ink3 + '" font-size="17" class="svg-mono">' + (s < 0 ? '−' + (-s) : s) + '</text>'; }).join('') +
        '<text x="0" y="31" text-anchor="end" fill="' + C.ink3 + '" font-size="18">s</text><circle class="sball" cx="20" cy="26" r="10" fill="' + C.ink + '"/></svg>';
      var EB = 92, EH = 70, EMAX = Math.exp(2);
      var etab = '<svg class="etab" width="640" height="122" viewBox="0 0 640 122" style="display:block;margin-top:6px;overflow:visible">' +
        '<line x1="0" x2="640" y1="' + EB + '" y2="' + EB + '" stroke="' + C.ink3 + '" stroke-width="1.5"/>' +
        EXP_S.map(function (s) {
          var v = Math.exp(s), x = sx(s), h = v / EMAX * EH, lab = s === 0 ? '1' : fmt(v, s < 0 ? 2 : 1);
          return '<rect class="eb" data-h="' + h.toFixed(2) + '" x="' + (x - 22) + '" y="' + (EB - h).toFixed(2) + '" width="44" height="' + h.toFixed(2) + '" rx="3" fill="' + C.ink + '" fill-opacity="' + (s === 0 ? 0.75 : 0.45) + '"/>' +
            '<text x="' + x + '" y="' + (EB - h - 8).toFixed(1) + '" text-anchor="middle" fill="' + C.ink + '" font-size="18" font-weight="700" class="svg-mono ev">' + lab + '</text>' +
            '<text x="' + x + '" y="' + (EB + 24) + '" text-anchor="middle" fill="' + C.ink3 + '" font-size="18">e' + sup(s) + '</text>';
        }).join('') +
        '<text x="0" y="14" fill="' + C.ink3 + '" font-size="16">← 0에 가까워져도 0은 안 돼요 · 오른쪽으로는 빠르게 커져요 →</text></svg>';
      g.dv = Deriv(ctx, q(el, '#dv'), { head: '유도', lines: [
        { tex: '1-\\frac{\\Delta t}{360}', display: false, note: '직선으로 해 보면 · 180일 → 1 − 1/2 = 1/2 ✓ · 그런데 400일 → 1 − 400/360 ≈ −0.11 <b style="color:var(--c-hi)">✕ 음수!</b>' },
        { tex: 's=k\\,(\\Delta t-t_0)', display: false, note: '벌점 s: 180일보다 얼마나 오래됐나 · 예: Δt = 0이면 s = 0.01 × (0 − 180) = −1.8', html: sline },
        { tex: 'e^{-1.8}=\\frac{1}{e^{1.8}}=\\frac{1}{6.05}\\approx0.165', display: false, note: '지수가 음수면 1 ÷ (양수 지수) · 그래서 eˢ는 언제나 0보다 커요', html: etab },
        { tex: '\\sigma=\\frac{1}{1+e^{s}}', note: '분모 1 + eˢ는 언제나 1보다 커요 → σ는 0과 1 사이 ✓ · s = 0 → 1/(1+1) = 1/2 ✓ · s가 크면 → 0 ✓ · s가 아주 큰 음수면 → 1 ✓ (s = −5 → e⁻⁵ = 0.007 → σ = 0.993) · Δt = 0 → 1/(1+0.165) = 0.858' },
        { tex: '\\part{f}{\\sigma(\\Delta t)=\\frac{1}{1+\\exp\\bigl(k(\\Delta t-t_0)\\bigr)}}', note: 'exp(□) = e<sup>□</sup> (같은 뜻 · 지수가 길 때 쓰는 표기) · k = 0.01, t₀ = 180일 · 논문 식 (3.3)', mark: 'f' },
        { tex: '1-\\sigma=\\frac{1+e^{s}-1}{1+e^{s}}=\\frac{e^{s}}{1+e^{s}}', tex2: '\\frac{\\sigma}{1-\\sigma}=\\frac{1}{e^{s}}=e^{-s}=e^{-k(\\Delta t-t_0)}', note: 'k × 100 = 1 → 100일마다 \'남은 : 사라진\' 비가 e ≈ 2.7배씩 줄어요<br>0, 100, 200, 300일: ' + [0, 100, 200, 300].map(function (a) { return fmt(sigma(a) / (1 - sigma(a)), 2); }).join(' → ') + ' (막대: 채운 칸 = 남은, 점선 칸 = 사라진)' }
      ], groups: [
        { from: 1, to: 3, at: 4, summary: '직선은 음수 ✕ → 벌점 $s$ → $e^{s}>0$ (음수 지수 = 1 ÷ 양수 지수)' },
        { from: 4, to: 4, at: 6, summary: '$\\sigma=\\frac{1}{1+e^{s}}$ · 네 가지 성질 모두 ✓' }
      ] });
      gsap.set(q(el, '#dv'), { autoAlpha: 0 });
      gsap.set([q(el, '#rd'), q(el, '#rd2'), q(el, '#rd3')], { autoAlpha: 0 });
      /* symbol cards */
      g.cards = [
        card(ctx, el, { tex: '\\Delta t', desc: '며칠 전 일인지', x: 96, y: 884 }),
        card(ctx, el, { tex: 'k', desc: '0.01<br>가파른 정도', x: 330, y: 884 }),
        card(ctx, el, { tex: 't_0', desc: '180일<br>반이 되는 날', x: 560, y: 884 }),
        card(ctx, el, { tex: 'e', desc: '≈ 2.718<br>자연 상수', x: 800, y: 884 })
      ];
      setHandle(ctx, 0);
      /* drag */
      var drag = false;
      function pick(e) { var p = ctx.toStage(e); var dt = (p.x - P2.x - P.l) / (P.r - P.l) * 1100; dt = Math.max(0, Math.min(1100, Math.round(dt))); setHandle(ctx, dt); }
      [g.hd, g.hit].forEach(function (n) {
        ctx.on(n, 'pointerdown', function (e) { if (+gsap.getProperty(g.hd, 'opacity') < 0.5) return; drag = true; try { n.setPointerCapture(e.pointerId); } catch (er) { /* ignore */ } pick(e); e.stopPropagation(); });
        ctx.on(n, 'pointermove', function (e) { if (drag) pick(e); });
        ctx.on(n, 'pointerup', function () { drag = false; });
        ctx.on(n, 'click', function (e) { e.stopPropagation(); });
      });
    },
    enter: function (el, ctx) {
      var g = ctx.g, P = g.P, tl = ctx.tl();
      /* the ruler rises from below (where s03-01 left it) and its ticks swap ends */
      g.rTicks.forEach(function (t) { gsap.set(t.g, { x: P.px(MAX_AGE - t.a) }); });
      gsap.set(g.ruler, { y: P.b + 140 });
      gsap.set([g.yax, g.band, g.bandL, g.xTitle], { autoAlpha: 0 });
      tl.fromTo(g.ruler, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0);
      tl.to(g.ruler, { y: P.b, duration: 0.8, ease: E.io }, 0.1);
      g.rTicks.forEach(function (t, k) { tl.to(t.g, { x: P.px(t.a), duration: 0.9, ease: 'power3.inOut' }, 0.9 + k * 0.05); });
      tl.to([g.yax, g.band, g.bandL, g.xTitle], { autoAlpha: 1, duration: 0.5, stagger: 0.1 }, 1.6);
      gsap.set(q(el, '#pn'), { autoAlpha: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(g.check, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
        tl.add(slideIn(ctx, g.items, { stagger: 0.18 }), 0.2);
      }
      if (i === 2) {                                                  /* the straight line: ½ at 180 days, negative after 360 */
        tl.fromTo(q(el, '#pn'), { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
        tl.set(q(el, '#dv'), { autoAlpha: 1 }, 0);
        tl.add(g.dv.show(1), 0.1);
        tl.set(g.lin1, { autoAlpha: 1 }, 0.3);
        tl.add(drawPath(g.lin1, { duration: 1.1, ease: 'none', dash: '9 7' }), 0.3);
        tl.fromTo(g.linMid, { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp }, 0.85);
        tl.set(g.lin2, { autoAlpha: 1 }, 1.4);
        tl.add(drawPath(g.lin2, { duration: 0.45, ease: 'power1.in' }), 1.4);
        tl.fromTo(g.linX, { autoAlpha: 0, scale: 1.8, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: E.stamp }, 1.85);
        var xx = q(g.items[0], '.xx'), L = 60;
        tl.set(xx, { autoAlpha: 1 }, 2.0);
        tl.fromTo(xx, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.35, ease: 'power2.out' }, 2.0);
        tl.call(function () { g.items[0].classList.add('bad'); }, null, 2.0);
      }
      if (i === 3) {                                                  /* penalty s */
        tl.add(g.dv.show(2), 0);
        tl.to(g.lin, { opacity: 0.3, duration: 0.5 }, 0);
        tl.fromTo(q(el, '#rd'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.3);
        tl.fromTo([g.hd, g.hit], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.3);
        tl.add(g.cards[0].pop(), 0.4); tl.add(g.cards[1].pop(), 0.55); tl.add(g.cards[2].pop(), 0.7);
        tl.add(moveHandle(ctx, 180, 1.0), 1.2);
        tl.add(moveHandle(ctx, 365, 1.0), 2.5);
      }
      if (i === 4) {                                                  /* e^s: table of e^−2 … e^2 */
        tl.add(g.dv.show(3), 0);
        var bars = qa(el, '.etab .eb'), vals = qa(el, '.etab .ev');
        bars.forEach(function (b, k) {
          var h = +b.getAttribute('data-h');
          tl.fromTo(b, { attr: { y: 92, height: 0 } }, { attr: { y: 92 - h, height: h }, duration: 0.5, ease: E.out }, 0.4 + k * 0.14);
          tl.fromTo(vals[k], { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: E.out }, 0.6 + k * 0.14);
        });
        tl.add(moveHandle(ctx, 0, 1.0), 0.2);
        tl.fromTo(q(el, '#rd2'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.3);
        tl.add(g.cards[3].pop(), 0.6);
      }
      if (i === 5) {                                                  /* σ = 1 / (1 + e^s): all four wishes */
        tl.add(g.dv.show(4), 0);
        tl.add(g.dv.show(5), 1.9);
        tl.to(g.lin, { autoAlpha: 0, duration: 0.4 }, 0);
        tl.set(g.curve, { autoAlpha: 1 }, 0.4);
        tl.add(drawPath(g.curve, { duration: 1.4 }), 0.4);
        tl.call(function () { g.state.curve = true; setHandle(ctx, g.state.dt); }, null, 0.4);
        tl.fromTo(q(el, '#rd3'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.6);
        g.pts.forEach(function (p, k) { tl.fromTo(p, { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: E.stamp }, 0.6 + k * 0.2); });
        tl.fromTo(g.cross, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.1);
        tl.to(q(g.items[0], '.xx'), { autoAlpha: 0, duration: 0.3 }, 1.6);
        tl.call(function () { g.items[0].classList.remove('bad'); }, null, 1.6);
        g.items.forEach(function (it, k) {
          var p = q(it, '.ok'), L = 40;
          tl.set(p, { autoAlpha: 1 }, 1.9 + k * 0.25);
          tl.fromTo(p, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.3, ease: 'power2.out' }, 1.9 + k * 0.25);
          tl.add(function () { it.classList.add('on'); }, 1.9 + k * 0.25);
        });
      }
      if (i === 6) {                                                  /* 1 − σ and the ratio σ / (1 − σ) = e^−s */
        g.state.curve = true;
        tl.add(g.dv.show(6), 0);
        tl.fromTo(g.ratio, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 0.5);
        tl.fromTo(qa(g.ratio, 'rect'), { scaleY: 0, transformOrigin: '50% 100%' }, { scaleY: 1, duration: 0.6, ease: E.out, stagger: 0.08 }, 0.5);
      }
    },
    tags: ['calc']
  };
  function setHandle(ctx, dt) {
    var g = ctx.g, P = g.P;
    g.state.dt = dt;
    var x = P.px(dt), sg = sigma(dt), s = K * (dt - T0), y = g.state.curve ? P.py(sg) : P.b;
    g.hdKnob.setAttribute('transform', 'translate(' + x + ',' + (P.b - 3) + ')');
    g.hdDot.setAttribute('cx', x); g.hdDot.setAttribute('cy', y);
    g.hdGuide.setAttribute('x1', x); g.hdGuide.setAttribute('x2', x); g.hdGuide.setAttribute('y1', y);
    var el = g.P.host.parentNode;
    var r1 = q(el, '#rd1'), r2 = q(el, '#rd2'), r3 = q(el, '#rd3');
    var ss = (s < 0 ? '−' : '') + fmt(Math.abs(s), 2);
    if (r1) r1.innerHTML = 'Δt = <b>' + n0(dt) + '</b>일 → s = <b>' + ss + '</b>';
    var es = Math.exp(s);
    if (r2) r2.innerHTML = ' → eˢ = <b>' + (es >= 100 ? fmt(es, 0) : es >= 10 ? fmt(es, 2) : fmt(es, 3)) + '</b>';
    if (r3) r3.innerHTML = ' → σ = <b class="hl2">' + (sg < 0.001 ? fmt(sg, 4) : fmt(sg, 3)) + '</b>';
    var ball = q(el, '.sball');
    if (ball) ball.setAttribute('cx', sx(Math.max(-2, Math.min(2, s))));
  }
  function moveHandle(ctx, to, dur) {
    var st = { v: ctx.g.state.dt };
    return gsap.to(st, { v: to, duration: dur, ease: 'power2.inOut', onStart: function () { st.v = ctx.g.state.dt; }, onUpdate: function () { setHandle(ctx, st.v); }, onComplete: function () { setHandle(ctx, to); } });
  }

  /* ================================================================ s05-03 */
  var P3 = { x: 96, y: 236, w: 920, h: 600, l: 80, r: 820, t: 90, b: 520, xd: [0, 500] };
  var s3 = {
    id: 's05-03', title: '금액 무게 V(z): 커져도 1을 넘지 않아요', time: 40, steps: 3,
    notes: [
      '이제 금액 무게예요. 금액이 클수록 무게가 커지되, 아무리 커도 1을 넘지 않게 만든 식이에요. z는 달러 금액이에요.',
      '식을 정리해 볼게요. e의 마이너스 b z 제곱을 y라고 두면, z가 0일 때 y는 1이고, z가 커질수록 y는 0에 가까워져요. 그러면 V는 2 나누기 1 더하기 y, 빼기 1이고, 분수를 정리하면 1 빼기 y를 1 더하기 y로 나눈 꼴이 돼요.',
      '0달러면 y가 1이라서 0, 금액이 아주 크면 y가 0에 가까워서 1에 가까워져요. 그래서 V는 0 이상이고 1을 넘지 않아요. 무제한 허락은 금액이 너무 커서 컴퓨터 계산으로는 딱 1이 돼요. 곡선이 천장에 닿을 듯 멈춰요.',
      '그런데 분석 계획은 기울기 b를 1로, 금액을 토큰의 원래 단위로 정해 두었어요. 기본 단위는 토큰의 가장 작은 조각이에요. 1 USDC는 기본 단위 100만 개예요. 그러면 10 기본 단위만 넘어도 V가 0.99991보다 커서, 1에서 1만분의 1도 떨어지지 않아요. 등록 분석에서는 송금의 99.52%, 마지막 허락의 99.78%가 그랬어요. 금액이 아무 역할도 하지 못했고, 이것이 나중에 금액을 고친 이유 가운데 하나예요.'
    ],
    html: '<h1 class="t-h1">아무리 커도 [[1]]을 넘지 않아요</h1>' +
      '<div class="s5-panel" id="pn" data-in="none">' +
        '<div id="dv"></div>' +
        '<div id="vs" data-step="3" style="margin-top:14px;padding:14px 20px;border-radius:16px;border:1px dashed var(--ink-3)">' +
          '<div class="s5-note" style="display:flex;align-items:center;gap:12px"><span id="ptag"></span><span>계획대로 (원래 단위, b = 1)였다면</span></div>' +
          '<div class="s5-l" style="margin-top:6px">송금의 <b>' + pct2(GE10T) + '</b>, 마지막 허락의 <b>' + pct2(GE10A) + '</b>가 10 기본 단위 이상</div>' +
          '<div class="s5-note">기본 단위 = 토큰의 가장 작은 조각 (1 USDC = 1,000,000개)</div>' +
          '<div class="s5-note">→ $V(10)\\approx0.99991$: 1에서 1만분의 1도 안 떨어져요 → 금액이 아무 역할도 못 했어요</div>' +
        '</div>' +
      '</div>' +
      '<div class="abs s5-note" style="left:470px;top:884px;width:540px"><b>z</b> = 달러 금액 · 0달러 → 0 · 아주 큰 금액 → 1에 가까이 · 무제한 허락 → 1</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var P = g.P = plot(ctx, el, P3);
      yAxis(P, [[0, '0'], [0.5, '0.5'], [1, '1']], '');
      txt(P.grid, P.l, P.t - 60, '금액 무게 V', { size: 20, fill: C.ink2 });
      xAxis(P, [[0, '0'], [100, '100'], [200, '200'], [300, '300'], [400, '400'], [500, '500']], 'z = 달러 금액 (그림의 b = ln 3 / 62, 다음 장)');
      /* glass ceiling at V = 1 */
      var gl = S('g', {}, P.under);
      var gid = uid('glass');
      var grad = S('linearGradient', { id: gid, x1: 0, y1: 0, x2: 0, y2: 1 }, S('defs', {}, gl));
      S('stop', { offset: '0', 'stop-color': '#E9EDF5', 'stop-opacity': 0.02 }, grad);
      S('stop', { offset: '1', 'stop-color': '#E9EDF5', 'stop-opacity': 0.16 }, grad);
      S('rect', { x: P.l, y: P.py(1) - 34, width: P.r - P.l, height: 34, fill: 'url(#' + gid + ')' }, gl);
      S('line', { x1: P.l, x2: P.r, y1: P.py(1), y2: P.py(1), stroke: C.ink, 'stroke-width': 2, 'stroke-dasharray': '7 6' }, gl);
      g.one = txt(P.over, P.r + 14, P.py(1) + 7, '1', { size: 26, fill: C.hi, weight: 800 });
      txt(gl, P.r - 10, P.py(1) - 12, '천장 · 아무리 커도 1을 넘지 않아요', { anchor: 'end', size: 17, fill: C.ink2 });
      /* coin stacks along the axis and the unlimited stack */
      g.coins = S('g', {}, P.under);
      [[50, 1], [150, 2], [300, 3], [450, 4]].forEach(function (c) {
        for (var k = 0; k < c[1]; k++) S('ellipse', { cx: P.px(c[0]), cy: P.b - 10 - k * 9, rx: 14, ry: 5, fill: C.bg3, stroke: C.ink2, 'stroke-width': 1.5 }, g.coins);
      });
      gsap.set(g.coins, { autoAlpha: 0 });
      g.unl = S('g', {}, P.over);
      var UX = P.r + 64;                                             /* clear of the '500' tick label */
      for (var k2 = 0; k2 < 9; k2++) S('ellipse', { cx: UX, cy: P.b - 10 - k2 * 9, rx: 16, ry: 5.5, fill: C.bg3, stroke: C.ink2, 'stroke-width': 1.5 }, g.unl);
      txt(g.unl, UX, P.b + 32, '무제한', { anchor: 'middle', size: 18, fill: C.ink2 });
      S('circle', { cx: UX, cy: P.py(1) + 10, r: 7, fill: C.ink }, g.unl);
      S('line', { x1: UX, x2: UX, y1: P.b - 92, y2: P.py(1) + 20, stroke: C.ink3, 'stroke-width': 1.5, 'stroke-dasharray': '3 5' }, g.unl);
      gsap.set(g.unl, { autoAlpha: 0 });
      /* main curve and the morphing grey curve (registered setting) */
      g.curve = S('path', { d: curvePath(P, function (z) { return V(z, BA); }, 0, 500, 200), fill: 'none', stroke: C.ink, 'stroke-width': 4, 'stroke-linecap': 'round' }, P.main);
      gsap.set(g.curve, { autoAlpha: 0 });
      g.grey = S('path', { d: '', fill: 'none', stroke: C.ink2, 'stroke-width': 5, 'stroke-linecap': 'round', 'stroke-dasharray': '1 10' }, P.main);
      gsap.set(g.grey, { autoAlpha: 0 });
      g.greyL = txt(P.over, P.px(14), P.py(0.93), '계획대로: 원래 단위, b = 1', { size: 20, fill: C.ink2, weight: 600 });
      gsap.set(g.greyL, { autoAlpha: 0 });
      /* derivation with a y-ball */
      var xline = '<svg width="620" height="70" viewBox="0 0 620 70" style="display:block;overflow:visible">' +
        '<line x1="30" x2="590" y1="30" y2="30" stroke="' + C.ink3 + '" stroke-width="2"/>' +
        '<text x="30" y="62" text-anchor="middle" fill="' + C.ink3 + '" font-size="17" class="svg-mono">0</text><text x="590" y="62" text-anchor="middle" fill="' + C.ink3 + '" font-size="17" class="svg-mono">1</text>' +
        '<text x="310" y="62" text-anchor="middle" fill="' + C.ink3 + '" font-size="17">y = e^(−bz)</text>' +
        '<circle class="xball" cx="590" cy="30" r="11" fill="' + C.ink + '"/><text class="xz svg-mono" x="608" y="22" fill="' + C.ink2 + '" font-size="17">z = 0</text></svg>';
      g.dv = Deriv(ctx, q(el, '#dv'), { head: '정리하기', lines: [
        { tex: 'V(z)=\\frac{2}{1+e^{-bz}}-1', note: '논문 식 (3.4)' },
        { tex: 'y=e^{-bz}\\;\\Rightarrow\\;V=\\frac{2}{1+y}-1', tex2: '=\\frac{2-(1+y)}{1+y}=\\part{f}{\\frac{1-y}{1+y}}', markOn2: true, note: 'z = 0이면 y = 1, z가 커지면 y → 0', html: xline, mark: 'f' },
        { tex: 'z=0:\\ \\tfrac{1-1}{1+1}=0,\\qquad z\\to\\infty:\\ \\tfrac{1-0}{1+0}=1', display: false, note: '그래서 V는 0 이상이고 1을 넘지 않아요 · 무제한 허락은 금액이 너무 커서 컴퓨터 계산으로 딱 1' }
      ] });
      gsap.set(q(el, '#dv'), { autoAlpha: 0 });
      var pt = q(el, '#ptag'); pt.appendChild(Comp.tag('registered-analysis'));
      g.bCard = card(ctx, el, { tex: 'b', desc: '기울기 — 얼마나 빨리 1로 올라가는지', x: 96, y: 880 });
    },
    enter: function (el, ctx) {
      ctx.gsap.fromTo(q(el, '#pn'), { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: 0.2 });
      ctx.gsap.fromTo(ctx.g.P.host, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: 0.1 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, P = g.P, tl = ctx.tl();
      if (i === 1) {
        tl.set(q(el, '#dv'), { autoAlpha: 1 }, 0);
        tl.add(g.dv.show(1), 0);
        tl.add(g.bCard.pop(), 0.4);
        tl.add(g.dv.show(2), 1.6);
        var ball = q(el, '.xball'), xz = q(el, '.xz'), st = { z: 0 };
        tl.to(st, { z: 300, duration: 2.0, ease: 'power1.inOut', onUpdate: function () {
          var x = Math.exp(-BA * st.z), cx = 30 + x * 560;
          ball.setAttribute('cx', cx); xz.setAttribute('x', cx + 18); xz.textContent = 'z = ' + n0(st.z) + '달러';
        } }, 2.3);
      }
      if (i === 2) {
        tl.add(g.dv.show(3), 0);
        tl.fromTo(g.coins, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.2);
        tl.fromTo(qa(g.coins, 'ellipse'), { autoAlpha: 0, y: -20 }, { autoAlpha: 1, y: 0, duration: 0.3, stagger: 0.05, ease: 'power2.out' }, 0.2);
        tl.set(g.curve, { autoAlpha: 1 }, 0.5);
        tl.add(drawPath(g.curve, { duration: 1.6, ease: 'power2.out' }), 0.5);
        tl.fromTo(g.one, { y: -22 }, { y: 0, duration: 0.7, ease: 'bounce.out' }, 1.5);
        tl.fromTo(g.unl, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 2.0);
      }
      if (i === 3) {
        var st2 = { m: 0 }, N = 160;
        var zs = []; for (var k = 0; k <= N; k++) zs.push(k === 1 ? 0.0001 : k === 0 ? 0 : (k - 1) / (N - 1) * 500);
        var draw = function () {
          var d = '';
          zs.forEach(function (z, j) { var vm = V(z, BA), vg = j === 0 ? 0 : 1, v = vm + (vg - vm) * st2.m; d += (j ? 'L' : 'M') + P.px(z).toFixed(1) + ',' + P.py(v).toFixed(1); });
          g.grey.setAttribute('d', d);
        };
        draw();
        tl.set(g.grey, { autoAlpha: 1 }, 0);
        tl.to(g.curve, { opacity: 0.35, duration: 0.4 }, 0);
        /* the y-ball picture has done its job: fold it so the registered-analysis box fits the panel */
        var hx = q(el, '#dv .hx');
        if (hx) { gsap.set(hx, { overflow: 'hidden' }); tl.to(hx, { height: 0, autoAlpha: 0, duration: 0.4, ease: E.io }, 0); }
        tl.to(st2, { m: 1, duration: 1.0, ease: E.io, onUpdate: draw, onComplete: function () { st2.m = 1; draw(); } }, 0.2);
        tl.fromTo(g.greyL, { autoAlpha: 0, x: -10 }, { autoAlpha: 1, x: 0, duration: 0.4 }, 1.1);
      }
    },
    tags: function (st) { return st >= 3 ? ['calc', 'registered-analysis'] : ['calc']; }
  };

  /* ================================================================ s05-04 */
  var COINS = [3, 12, 25, 48, 62, 90, 150, 400, 2000];               /* 예시 amounts; the 5th of 9 is the median */
  var SHUF = [6, 0, 7, 4, 8, 2, 5, 1, 3];                            /* initial (unsorted) order, indices into COINS */
  var P4 = { x: 96, y: 418, w: 920, h: 460, l: 80, r: 880, t: 40, b: 352, xd: [0, 600] };
  var s4 = {
    id: 's05-04', title: 'b = ln 3 / m: 중앙값이 반이 되게', time: 55, steps: 9,
    notes: [
      '그러면 기울기 b는 어떻게 정할까요? 수정 분석에서는 금액의 한가운데 값, 곧 중앙값이 딱 절반의 무게를 갖도록 정했어요.',
      '중앙값은 금액을 작은 것부터 줄 세웠을 때 한가운데 있는 값이에요. 이 예에서는 아홉 개 가운데 다섯 번째예요. 그래서 바라는 것은 V(m)이 2분의 1인 거예요.',
      '앞 장에서 V를 1 빼기 y를, 1 더하기 y로 나눈 꼴로 바꿔 두었어요. y는 e의 마이너스 b m 제곱이에요. 이 분수가 2분의 1이라는 식을 풀면 돼요.',
      '양변에 2 곱하기, 1 더하기 y를 곱해서 분모를 없애요.',
      '괄호를 풀면 2 빼기 2y는 1 더하기 y예요.',
      'y를 한쪽으로 모으면 1은 3y, 그래서 y는 3분의 1이에요.',
      'y를 원래대로 되돌리면 e의 마이너스 b m 제곱이 3분의 1이에요. 지수가 음수면 1 나누기 양수 지수라서, 1 나누기 e의 b m 제곱이 3분의 1이에요. 그러니 e의 b m 제곱은 3이에요. 끝난 단계는 한 줄로 접어 둘게요.',
      'e를 몇 제곱해야 3이 될까요? e는 약 2.7이고 e의 제곱은 약 7.4니까, 답은 1과 2 사이, 약 1.0986이에요. 이 답을 ln 3이라고 써요. 그래서 b 곱하기 m은 ln 3이에요.',
      '양변을 m으로 나누면, b는 ln 3을 m으로 나눈 값이에요.',
      '확인해 볼게요. 중앙값의 두 배면 e의 2bm제곱은 3을 두 번 곱한 9라서 y는 9분의 1이고, V는 9분의 8을 9분의 10으로 나눈 0.8이에요. 절반이면 e의 bm/2 제곱을 두 번 곱해야 3이니까 그 값은 루트 3, 약 1.732예요. 그래서 y는 약 0.577, V는 약 0.27이에요. 금액 차이가 무게에 고르게 드러나요. 송금은 중앙값이 200달러, 허락은 62달러였어요. 이 값은 3월 31일까지의 기록만으로 구해서, 시험 기간의 정보가 섞이지 않았어요. 아래 손잡이로 금액을 바꿔 볼 수 있어요.'
    ],
    html: '<h1 class="t-h1">[[중앙값]]의 무게를 1/2로</h1>' +
      '<div class="abs s5-note" id="cap1" style="left:96px;top:356px;width:880px"></div>' +
      '<div class="s5-panel" id="pn" data-in="none"><div id="dv"></div></div>' +
      '<div class="abs no-advance" id="zs" data-in="none" style="left:96px;top:892px;width:900px;height:96px"></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* coins */
      var host = H('div', '', el); host.setAttribute('data-in', 'none');
      host.style.cssText = 'position:absolute;left:96px;top:186px;width:900px;height:170px';
      var csvg = Comp.svg(ctx, host, { w: 900, h: 170 });
      g.coinPos = function (slot) { return 50 + slot * 100; };
      g.coins = COINS.map(function (amt, ci) {
        var r = 13 + 7 * Math.log10(amt), cg = S('g', {}, csvg);
        S('circle', { cx: 0, cy: 0, r: r, fill: C.bg3, stroke: C.ink2, 'stroke-width': 2.5 }, cg);
        S('circle', { cx: 0, cy: 0, r: r * 0.62, fill: 'none', stroke: C.ink3, 'stroke-width': 1.5 }, cg);
        txt(cg, 0, r + 28, n0(amt) + '달러', { anchor: 'middle', size: 18, fill: C.ink2, cls: 'svg-mono' });
        var slot = SHUF.indexOf(ci);
        gsap.set(cg, { x: g.coinPos(slot), y: 74 });
        return { g: cg, amt: amt, ci: ci, r: r };
      });
      g.mLab = txt(csvg, g.coinPos(4), 22, 'm = 62달러 (한가운데)', { anchor: 'middle', size: 21, fill: C.hi, weight: 700 });
      gsap.set(g.mLab, { autoAlpha: 0 });
      g.cap1 = q(el, '#cap1');
      g.cap1.innerHTML = '중앙값 m = 금액을 줄 세웠을 때 한가운데 값 <span class="example-mark" style="margin-left:8px">예시 · 아홉 개 중 다섯 번째</span>';
      gsap.set(g.cap1, { autoAlpha: 0 });
      /* plot with two curves */
      var P = g.P = plot(ctx, el, P4);
      yAxis(P, [[0, '0'], [0.27, '0.27'], [0.5, '0.5'], [0.8, '0.8'], [1, '1']], '금액 무게 V');
      xAxis(P, [[0, '0'], [100, '100'], [200, '200'], [300, '300'], [400, '400'], [500, '500'], [600, '600달러']], '');
      g.half = S('line', { x1: P.l, x2: P.r, y1: P.py(0.5), y2: P.py(0.5), stroke: C.hi, 'stroke-width': 1.5, 'stroke-dasharray': '6 6' }, P.under);
      g.halfL = txt(P.under, P.r - 4, P.py(0.5) - 10, '목표: 중앙값 m에서 V = 1/2', { anchor: 'end', size: 18, fill: C.hi, cls: 's5-halo' });
      g.cT = S('path', { d: curvePath(P, function (z) { return V(z, BT); }, 0, 600, 200), fill: 'none', stroke: C.xfer, 'stroke-width': 4, 'stroke-linecap': 'round' }, P.main);
      g.cA = S('path', { d: curvePath(P, function (z) { return V(z, BA); }, 0, 600, 200), fill: 'none', stroke: C.allow, 'stroke-width': 4, 'stroke-linecap': 'round' }, P.main);
      gsap.set([g.cT, g.cA], { autoAlpha: 0 });
      g.mk = [];
      [[MA, C.allow, BA], [MT, C.xfer, BT]].forEach(function (s0) {
        var m = s0[0], col = s0[1], b = s0[2], grp = S('g', {}, P.over);
        [[m / 2, '0.27'], [m, '0.5'], [2 * m, '0.8']].forEach(function (pp) {
          var x = P.px(pp[0]), y = P.py(V(pp[0], b));
          S('circle', { cx: x, cy: y, r: 7, fill: col, stroke: C.bg, 'stroke-width': 2 }, grp);
          if (col === C.allow) txt(grp, x - 12, y - (pp[1] === '0.27' ? 14 : 8), pp[1], { anchor: 'end', size: 17, fill: col, weight: 700, cls: 'svg-mono s5-halo' });
          else txt(grp, x + 10, y + 24, pp[1], { size: 17, fill: col, weight: 700, cls: 'svg-mono s5-halo' });
        });
        S('line', { x1: P.px(m), x2: P.px(m), y1: P.py(0.5), y2: P.b, stroke: col, 'stroke-width': 1.5, 'stroke-dasharray': '3 5' }, grp);
        txt(grp, P.px(m), P.b - 8, String(m), { anchor: 'middle', size: 18, fill: col, weight: 700, cls: 'svg-mono s5-halo' });
        gsap.set(grp, { autoAlpha: 0 });
        g.mk.push(grp);
      });
      /* legend (lower right of the plot, where both curves are high) */
      var lg = g.leg = S('g', {}, P.over);
      var lx = P.px(250), ly = P.py(0.32);
      S('line', { x1: lx, x2: lx + 30, y1: ly - 6, y2: ly - 6, stroke: C.xfer, 'stroke-width': 4 }, lg);
      txt(lg, lx + 42, ly, '송금 m_T = 200달러 → b_T = ln 3 / 200', { size: 20, fill: C.ink });
      S('line', { x1: lx, x2: lx + 30, y1: ly + 26, y2: ly + 26, stroke: C.allow, 'stroke-width': 4 }, lg);
      txt(lg, lx + 42, ly + 32, '허락 m_A = 62달러 → b_A = ln 3 / 62', { size: 20, fill: C.ink });
      txt(lg, lx, ly + 66, 't₁(3월 31일)까지 기록만 · 두 자리로 반올림', { size: 17, fill: C.ink2 });
      txt(lg, lx, ly + 90, '송금 ' + n0(N_TRANSFERS) + '건 ' + fmt(MT_RAW, 2) + ' → ' + MT + ' · 허락 ' + n0(N_FINITE_ALLOW) + '건 ' + fmt(MA_RAW, 2) + ' → ' + MA, { size: 17, fill: C.ink2 });
      gsap.set(lg, { autoAlpha: 0 });
      /* derivation */
      var ePic = (function () {
        var w = 600, s = '<svg width="' + w + '" height="96" viewBox="0 0 ' + w + ' 96" style="display:block;overflow:visible;margin-top:2px">';
        /* the curve y = e^x for x in [0, 2.2]: where does it reach height 3? */
        function X(e) { return 40 + e / 2.2 * 380; }
        function Y(v) { return 78 - v / 9 * 72; }
        var d = ''; for (var i = 0; i <= 44; i++) { var xx = i / 44 * 2.2; d += (i ? 'L' : 'M') + X(xx).toFixed(1) + ',' + Y(Math.exp(xx)).toFixed(1); }
        s += '<line x1="40" x2="430" y1="78" y2="78" stroke="' + C.ink3 + '" stroke-width="1.5"/>';
        s += '<path d="' + d + '" fill="none" stroke="' + C.ink2 + '" stroke-width="2.5"/>';
        s += '<line x1="40" x2="' + X(LN3) + '" y1="' + Y(3) + '" y2="' + Y(3) + '" stroke="' + C.hi + '" stroke-width="1.5" stroke-dasharray="4 4"/>';
        s += '<line x1="' + X(LN3) + '" x2="' + X(LN3) + '" y1="' + Y(3) + '" y2="78" stroke="' + C.hi + '" stroke-width="1.5" stroke-dasharray="4 4"/>';
        s += '<circle cx="' + X(1) + '" cy="' + Y(Math.E) + '" r="4.5" fill="' + C.ink2 + '"/><circle cx="' + X(2) + '" cy="' + Y(Math.E * Math.E) + '" r="4.5" fill="' + C.ink2 + '"/><circle cx="' + X(LN3) + '" cy="' + Y(3) + '" r="6" fill="' + C.hi + '"/>';
        s += '<text x="' + (X(2) + 12) + '" y="' + (Y(Math.E * Math.E) + 6) + '" fill="' + C.ink2 + '" font-size="16">e² ≈ 7.39</text>';
        s += '<text x="' + (X(1) - 8) + '" y="' + (Y(Math.E) + 18) + '" text-anchor="end" fill="' + C.ink2 + '" font-size="16">e¹ ≈ 2.72</text>';
        s += '<text x="30" y="' + (Y(3) + 5) + '" text-anchor="end" fill="' + C.hi + '" font-size="16">3</text>';
        s += '<text x="' + X(LN3) + '" y="96" text-anchor="middle" fill="' + C.hi + '" font-size="16" class="svg-mono">1.0986</text>';
        s += '<text x="' + X(2) + '" y="96" text-anchor="middle" fill="' + C.ink3 + '" font-size="15" class="svg-mono">2</text><text x="440" y="83" fill="' + C.ink3 + '" font-size="15">몇 제곱?</text>';
        return s + '</svg>';
      })();
      g.dv = Deriv(ctx, q(el, '#dv'), { head: 'b 구하기', lines: [
        { tex: 'V(m)=\\tfrac12', display: false, note: '바라는 것: 중앙값 m의 무게가 딱 반' },
        { tex: 'y=e^{-bm}\\;\\Rightarrow\\;\\frac{1-y}{1+y}=\\frac12', note: '앞 장에서 바꾼 꼴 V = (1 − y)/(1 + y)' },
        { tex: '\\part{a}{2(1-y)}=\\part{b}{1+y}', display: false, note: '양변에 2(1 + y)를 곱해요', mark: 'a' },
        { tex: '2-2y=1+y', display: false, note: '괄호를 풀어요' },
        { tex: '1=3y\\;\\Rightarrow\\;\\part{y}{y=\\tfrac13}', display: false, note: 'y를 한쪽으로 모아요', mark: 'y' },
        { tex: 'e^{-bm}=\\tfrac13\\;\\Leftrightarrow\\;\\part{e}{e^{bm}=3}', display: false, note: 'y를 원래대로 되돌려요 · $e^{-a}=1\\div e^{a}$ → $1\\div e^{bm}=\\tfrac13$ → $e^{bm}=3$', mark: 'e' },
        { tex: 'bm=\\ln 3\\approx1.0986', display: false, note: 'e를 몇 제곱해야 3이 될까? 그 답을 ln 3이라고 써요', html: ePic },
        { tex: '\\boxed{\\,b=\\dfrac{\\ln 3}{m}\\,}', note: '양변을 m으로 나눠요' },
        { tex: '\\begin{aligned} z=2m:&\\;\\; e^{b\\cdot 2m}=(e^{bm})^2=3^2=9\\\\ &\\Rightarrow\\; y=\\tfrac19,\\;\\; V=\\tfrac{1-1/9}{1+1/9}=0.8 \\end{aligned}', tex2: '\\begin{aligned} z=\\tfrac m2:&\\;\\; e^{bm/2}=\\sqrt3\\approx1.732\\\\ &\\Rightarrow\\; y\\approx0.577,\\;\\; V\\approx0.27 \\end{aligned}', display: false, note: '$e^{bm/2}$를 두 번 곱하면 $e^{bm}=3$ → 그래서 $\\sqrt3$ · $y=1\\div\\sqrt3$ · 확인: 중앙값 0.5, 두 배 0.8, 절반 0.27' }
      ], groups: [
        { from: 2, to: 4, at: 6, summary: '분모를 없애고 정리하면 → $y=\\tfrac13$' },
        { from: 5, to: 7, at: 9, summary: '$y=\\tfrac13\\;\\to\\;e^{bm}=3\\;\\to\\;bm=\\ln 3$' }
      ] });
      g.lnCard = card(ctx, el, { tex: '\\ln 3', desc: 'e를 몇 제곱해야 3이 되는가 ≈ 1.0986', x: 96, y: 892 });
      /* slider */
      var zs = q(el, '#zs');
      var ssvg = Comp.svg(ctx, zs, { w: 900, h: 96 });
      var X0 = P.l, X1 = P.r;
      g.zx = function (z) { return X0 + z / 600 * (X1 - X0); };
      S('line', { x1: X0, x2: X1, y1: 24, y2: 24, stroke: C.line, 'stroke-width': 6, 'stroke-linecap': 'round' }, ssvg);
      g.zKnob = S('circle', { cx: g.zx(MT), cy: 24, r: 14, fill: C.bg, stroke: C.ink, 'stroke-width': 3, style: 'cursor:ew-resize' }, ssvg);
      g.zText = S('text', { x: X0, y: 76, fill: C.ink, 'font-size': 22, 'class': 'svg-mono' }, ssvg);
      g.zGuide = S('line', { x1: 0, x2: 0, y1: P.t, y2: P.b, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, P.over);
      var drag = false;
      function pick(e) { var p = ctx.toStage(e), r = ctx.rect(ssvg); var z = (p.x - r.x - X0) / (X1 - X0) * 600; setZ(ctx, Math.max(0, Math.min(600, Math.round(z)))); }
      ctx.on(ssvg, 'pointerdown', function (e) { drag = true; try { ssvg.setPointerCapture(e.pointerId); } catch (er) { /* ignore */ } pick(e); e.stopPropagation(); });
      ctx.on(ssvg, 'pointermove', function (e) { if (drag) pick(e); });
      ctx.on(ssvg, 'pointerup', function () { drag = false; });
      ctx.on(zs, 'click', function (e) { e.stopPropagation(); });
      gsap.set([zs, g.zGuide], { autoAlpha: 0 });
      setZ(ctx, MT);
    },
    enter: function (el, ctx) {
      ctx.gsap.fromTo(q(el, '#pn'), { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: 0.2 });
      ctx.gsap.fromTo(ctx.g.P.host, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: 0.1 });
      ctx.gsap.fromTo(ctx.g.coins.map(function (c) { return c.g; }), { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: E.stamp, stagger: 0.06, delay: 0.3 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        g.coins.forEach(function (c) { tl.to(c.g, { x: g.coinPos(c.ci), duration: 0.9, ease: 'power3.inOut' }, 0.1); });
        var mid = g.coins[4];
        tl.to(mid.g, { y: 58, duration: 0.4, ease: E.out }, 1.1);
        tl.to(q(mid.g, 'circle'), { stroke: C.hi, duration: 0.3 }, 1.1);
        tl.fromTo(g.mLab, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4 }, 1.3);
        tl.fromTo(g.cap1, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.4);
        tl.add(g.dv.show(1), 1.7);
      }
      if (i >= 2 && i <= 8) {
        tl.add(g.dv.show(i), 0);
        if (i === 7) tl.add(g.lnCard.pop(), 0.6);
      }
      if (i === 9) {
        tl.add(g.dv.show(9), 0);
        tl.to(g.lnCard.el, { autoAlpha: 0, duration: 0.3 }, 0);
        tl.set(g.cT, { autoAlpha: 1 }, 0.3);
        tl.add(drawPath(g.cT, { duration: 1.2 }), 0.3);
        tl.fromTo(g.mk[1], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 1.4);
        tl.set(g.cA, { autoAlpha: 1 }, 1.6);
        tl.add(drawPath(g.cA, { duration: 1.0 }), 1.6);
        tl.fromTo(g.mk[0], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 2.5);
        tl.fromTo(g.leg, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 2.7);
        tl.to([g.half, g.halfL], { opacity: 0.45, duration: 0.4 }, 2.7);
        tl.fromTo([q(el, '#zs'), g.zGuide], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 3.0);
      }
    },
    tags: ['calc', 'example']
  };
  function setZ(ctx, z) {
    var g = ctx.g, P = g.P;
    g.zKnob.setAttribute('cx', g.zx(z));
    g.zGuide.setAttribute('x1', P.px(z)); g.zGuide.setAttribute('x2', P.px(z));
    g.zText.textContent = 'z = ' + n0(z) + '달러 → 송금 V = ' + fmt(V(z, BT), 3) + ' · 허락 V = ' + fmt(V(z, BA), 3) + '  (계산)';
  }

  /* ================================================================ s05-05 */
  var EV_T = [[0, 400, '오늘'], [180, 200, '180일 전'], [365, 100, '1년 전']];      /* 예시: (age, dollars) */
  var EV_A = [['USDC', 30, Infinity, '무제한 · 30일 전'], ['WETH', 400, MA, '62달러 · 400일 전']];
  function w4(v) { return f4(v); }
  var s5 = {
    id: 's05-05', title: '두 그래프의 무게와 다시 출발', time: 55, steps: 4,
    notes: [
      '두 그래프는 같은 무게 식을 쓰지만, 쌓는 방법과 다시 출발하는 곳이 조금 달라요.',
      '송금 그래프는 u가 v에게 보낸 모든 송금마다 시간 무게와 금액 무게를 곱해 더해요. 예를 들어 오늘 400달러, 180일 전 200달러, 1년 전 100달러를 보냈다면 0.6865, 0.25, 0.0364를 더해 약 0.973이에요.',
      '허락 그래프는 토큰마다 가장 최근 허락 하나만 써요. 허락은 새로 하면 앞의 것을 덮어쓰기 때문이에요. USDC 무제한 허락을 30일 전에 했다면 0.8176, WETH 62달러 허락을 400일 전에 했다면 0.0499, 더해서 약 0.867이에요.',
      '다시 출발하는 곳도 달라요. AWP는 최근에 여러 상대에게 송금한 활발한 주소에서 더 자주 다시 출발해요. 받는 상대마다 가장 최근 송금의 시간 무게를 더한 것을 활발함 X라고 해요. 같은 상대에게 여러 번 보내도 가장 최근 한 번만 세요. 이 예에서 u는 v 한 곳에만 세 번 보냈으니, 오늘 보낸 송금의 0.8581 하나만 세요. 그래서 X_u는 0.8581이에요. 엔도스랭크는 모든 점에서 똑같이 다시 출발해요.',
      '왜 똑같이 했을까요? 허락을 많이 해 준 주인을 높이는 것이 아니라, 허락을 받은 계약을 재려는 것이기 때문이에요. 이 선택은 이 연구가 데이터를 꺼내기 전에 분석 계획에 적어 두었고, AWP식 다시 출발을 쓴 변형도 함께 보고하기로 했어요.'
    ],
    html: '<h1 class="t-h1">같은 무게 식, 쌓는 법과 다시 출발은 달라요</h1>' +
      '<div class="s5-two" id="pl" style="left:96px">' +
        '<div class="s5-kind c-xfer"><i style="background:var(--c-xfer)"></i>송금 · AWP</div>' +
        '<div class="s5-l">송금마다 <b>σ × V</b>를 모두 더해요</div>' +
        '<div class="s5-tx">$w_T(u,v)=\\sum_{e:\\,u\\to v}\\sigma(\\Delta t_e)\\,V(x_e)$</div>' +
        '<div class="s5-sym"><span>$x_e$ 송금 e의 달러 금액</span></div>' +
        '<div id="figT" style="position:relative;height:250px"></div>' +
        '<div id="rsT" data-in="none"><div class="s5-l">다시 출발: <b>활발한</b> 송신자일수록 자주 ($\\pi_u\\propto X_u$)</div>' +
          '<div class="s5-tx" style="font-size:24px">$X_u=\\sum_{v\\neq u}\\max_{e:\\,u\\to v}\\sigma(\\Delta t_e)$ · 받는 상대마다 <b>가장 최근 한 번만</b></div>' +
          '<div class="s5-note" id="xmax">예: v 한 곳에만 세 번 → $X_u=\\max(0.8581,\\,0.5,\\,0.1359)=0.8581$</div></div>' +
      '</div>' +
      '<div class="s5-two" id="pr" style="left:984px">' +
        '<div class="s5-kind c-allow"><i style="background:var(--c-allow)"></i>허락 · 엔도스랭크</div>' +
        '<div class="s5-l">토큰마다 <b>마지막 허락 하나만</b>, σ × V</div>' +
        '<div class="s5-tx">$w_A(u,v)=\\sum_{\\mathrm{token}}\\sigma\\bigl(\\Delta t^{\\star}\\bigr)\\,V\\bigl(a^{\\star}\\bigr)$</div>' +
        '<div class="s5-sym"><span>$a^{\\star}$ 마지막 허락의 달러 금액</span><span>$\\Delta t^{\\star}$ 그 허락이 며칠 전인지</span></div>' +
        '<div id="figA" style="position:relative;height:250px"></div>' +
        '<div id="rsA" data-in="none"><div class="s5-l">다시 출발: 모든 점에 [[똑같이]] ($\\pi_u=1/|V|$)</div>' +
          '<div class="s5-note">허락을 많이 해 준 주인에게 몫을 더 주지 않아요</div></div>' +
      '</div>' +
      '<div class="s5-bottom" data-step="4" data-in="words">왜 똑같이? 허락을 많이 <span class="ink-2">‘해 준’</span> 주인보다, 허락을 <span class="c-allow">‘받은’</span> 계약을 재고 싶어서요</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* transfer figure */
      var fT = Comp.svg(ctx, q(el, '#figT'), { w: 772, h: 250 });
      var uT = Comp.eoa(ctx, fT, { x: 50, y: 70, r: 16, label: 'u' }), vT = Comp.contract(ctx, fT, { x: 700, y: 70, size: 54, label: 'v' });
      g.aT = Comp.arrow(ctx, fT, { from: [50, 70], to: [700, 70], kind: 'xfer', width: 4, shorten: [24, 36], flow: false });
      void uT; void vT;
      g.evT = EV_T.map(function (ev, k) {
        var s0 = sigma(ev[0]), v0 = V(ev[1], BT), eg = S('g', {}, fT);
        var x = 150 + k * 190;
        var dot = S('circle', { cx: x, cy: 70, r: 15, fill: C.bg3, stroke: C.xfer, 'stroke-width': 2.5 }, eg);
        txt(eg, x, 36, ev[2] + ' · ' + ev[1] + '달러', { anchor: 'middle', size: 18, fill: C.ink2 });
        txt(eg, x, 116, fmt(s0, 4) + ' × ' + (ev[1] === 400 ? '0.8' : ev[1] === 200 ? '0.5' : fmt(v0, 4)), { anchor: 'middle', size: 18, fill: C.ink, cls: 'svg-mono' });
        txt(eg, x, 140, '= ' + w4(s0 * v0), { anchor: 'middle', size: 18, fill: C.xfer, cls: 'svg-mono', weight: 700 });
        gsap.set(eg, { autoAlpha: 0 });
        return { g: eg, dot: dot, x: x, w: s0 * v0 };
      });
      g.barT = mkBar(fT, 170, C.xfer, 1.0, 'w_T');
      /* restart halos (transfer: ∝ activeness; example values) */
      g.haloT = halos(fT, 216, [0.858, 0.35, 0.12, 0.6, 0.05], C.xfer);   /* first halo = u, X_u = σ(0) = 0.858 */
      /* allowance figure */
      var fA = Comp.svg(ctx, q(el, '#figA'), { w: 772, h: 250 });
      Comp.eoa(ctx, fA, { x: 50, y: 70, r: 16, label: 'u' }); Comp.contract(ctx, fA, { x: 700, y: 70, size: 54, label: 'v' });
      g.aA = Comp.arrow(ctx, fA, { from: [50, 70], to: [700, 70], kind: 'allow', width: 4, shorten: [24, 36] });
      g.evA = EV_A.map(function (ev, k) {
        var dt = ev[1], s0 = sigma(dt), v0 = ev[2] === Infinity ? 1 : V(ev[2], BA), eg = S('g', {}, fA), x = 230 + k * 250;
        /* older approvals of the same token, struck out */
        var old = S('g', {}, eg);
        S('rect', { x: x - 58, y: 8, width: 116, height: 30, rx: 8, fill: C.bg3, stroke: C.ink3, 'stroke-width': 1.5, 'stroke-dasharray': '4 4' }, old);
        txt(old, x, 29, '예전 허락', { anchor: 'middle', size: 16, fill: C.ink3 });
        var strike = S('line', { x1: x - 62, x2: x + 62, y1: 23, y2: 23, stroke: C.hi, 'stroke-width': 3, 'stroke-linecap': 'round' }, old);
        var chip = S('g', {}, eg);
        S('rect', { x: x - 58, y: 52, width: 116, height: 36, rx: 10, fill: C.bg3, stroke: C.allow, 'stroke-width': 2 }, chip);
        txt(chip, x, 77, ev[0] + ' 마지막', { anchor: 'middle', size: 18, fill: C.ink, weight: 700 });
        txt(eg, x, 112, ev[3], { anchor: 'middle', size: 17, fill: C.ink2 });
        txt(eg, x, 136, fmt(s0, 4) + ' × ' + (ev[2] === Infinity ? '1' : '0.5') + ' = ' + w4(s0 * v0), { anchor: 'middle', size: 18, fill: C.allow, cls: 'svg-mono', weight: 700 });
        gsap.set(eg, { autoAlpha: 0 });
        return { g: eg, old: old, strike: strike, w: s0 * v0 };
      });
      g.barA = mkBar(fA, 170, C.allow, 1.0, 'w_A');
      g.haloA = halos(fA, 216, [0.5, 0.5, 0.5, 0.5, 0.5], C.allow);
      gsap.set([g.haloT.g, g.haloA.g, q(el, '#rsT'), q(el, '#rsA')], { autoAlpha: 0 });
      g.ex = H('div', 'example-mark abs', el, '예시 · 금액·날짜·토큰은 설명용, 무게는 계산'); g.ex.setAttribute('data-in', 'none');
      g.ex.style.cssText += ';left:130px;top:836px';
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        var acc = 0;
        g.evT.forEach(function (ev, k) {
          var t0 = 0.2 + k * 1.0;
          tl.fromTo(ev.g, { autoAlpha: 0, y: -26 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'back.out(1.6)' }, t0);
          var from = acc; acc += ev.w;
          tl.add(g.barT.set(from, acc, 0.6), t0 + 0.45);
        });
        tl.call(function () { ctx.add(function () { g.aT.flow(true); }); }, null, 3.2);
      }
      if (i === 2) {
        var acc2 = 0;
        g.evA.forEach(function (ev, k) {
          var t0 = 0.2 + k * 1.2;
          tl.fromTo(ev.g, { autoAlpha: 0, y: -26 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'back.out(1.6)' }, t0);
          var L = 120;
          tl.fromTo(ev.strike, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.35, ease: 'power2.in' }, t0 + 0.5);
          tl.to(ev.old, { opacity: 0.25, duration: 0.3 }, t0 + 0.85);
          var from = acc2; acc2 += ev.w;
          tl.add(g.barA.set(from, acc2, 0.6), t0 + 0.8);
        });
      }
      if (i === 4) hold(ctx, 2.2);
      if (i === 3) {
        /* activeness: the same receiver v counts once, by its latest transfer — the two older ones step back */
        var newest = g.evT[0];
        tl.to([g.evT[1].g, g.evT[2].g], { opacity: 0.28, duration: 0.5, ease: E.io }, 0.2);
        tl.fromTo(newest.dot, { attr: { r: 15 } }, { attr: { r: 21 }, duration: 0.3, ease: 'power2.out', yoyo: true, repeat: 1 }, 0.3);
        tl.to(newest.dot, { attr: { 'stroke-width': 4 }, duration: 0.3 }, 0.3);
        tl.fromTo([q(el, '#rsT'), q(el, '#rsA')], { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out, stagger: 0.2 }, 0);
        tl.fromTo(q(el, '#xmax'), { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: E.out }, 0.7);
        tl.fromTo([g.haloT.g, g.haloA.g], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.4);
        tl.add(g.haloT.grow(), 0.6);
        tl.add(g.haloA.grow(), 0.6);
      }
    },
    tags: ['example', 'calc']
  };
  /* weight bar: grows from a to b (bar scale: 1.0 = 560 px) */
  function mkBar(svg, y, col, maxV, name) {
    var X = 110, W = 560;
    txt(svg, 40, y + 20, name, { size: 20, fill: C.ink2, cls: 'svg-mono' });
    S('rect', { x: X, y: y, width: W, height: 26, rx: 6, fill: 'rgba(233,237,245,.04)' }, svg);
    var bar = S('rect', { x: X, y: y, width: 0, height: 26, rx: 6, fill: col, 'fill-opacity': 0.75 }, svg);
    var tv = txt(svg, X + W + 14, y + 21, '0', { size: 24, fill: C.ink, weight: 700, cls: 'svg-mono' });
    return {
      set: function (a, b, dur) {
        var st = { v: a };
        return gsap.to(st, { v: b, duration: dur || 0.6, ease: 'power2.out',
          onUpdate: function () { bar.setAttribute('width', st.v / maxV * W); tv.textContent = fmt(st.v, 4); },
          onComplete: function () { bar.setAttribute('width', b / maxV * W); tv.textContent = fmt(b, 4); } });
      }
    };
  }
  /* restart halos: five points; halo radius ∝ restart share (예시 shares) */
  function halos(svg, y, shares, col) {
    var g = S('g', {}, svg), hs = [];
    var tot = shares.reduce(function (a, b) { return a + b; }, 0);
    txt(g, 40, y + 6, '다시 출발', { size: 18, fill: C.ink2 });
    shares.forEach(function (s, k) {
      var x = 210 + k * 110, r = 6 + 28 * Math.sqrt(s / tot * shares.length / 2.2);
      var h = S('circle', { cx: x, cy: y, r: r, fill: col, 'fill-opacity': 0.18, stroke: col, 'stroke-width': 1.5, 'stroke-opacity': 0.6 }, g);
      S('circle', { cx: x, cy: y, r: 6, fill: C.ink }, g);
      hs.push(h);
    });
    return { g: g, grow: function () { return gsap.fromTo(hs, { scale: 0, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.6, ease: E.stamp, stagger: 0.08 }); } };
  }

  /* ================================================================ s05-06 */
  var S1 = U, S2 = 500;                                              /* 예시: one owner, two spenders */
  var s6 = {
    id: 's05-06', title: '달러로 바꾸기와 상한 U (C-PR용)', time: 45, steps: 4,
    notes: [
      '결합 점수 C-PR에 쓰는 무게는 조금 달라요. C-PR은 금액에 V를 씌우지 않고 달러를 그대로 더해요.',
      '먼저 금액을 달러로 바꿔요. 기본 단위는 토큰의 가장 작은 조각이고, 그 개수를 n이라고 써요. n에 10의 마이너스 소수 자릿수 제곱을 곱하고, 그날 가격을 곱해요. 10의 마이너스 6제곱을 곱한다는 것은 1,000,000으로 나눈다는 뜻이에요. USDC는 소수 자릿수가 6이라서 1,000,000 기본 단위가 1 USDC, 약 1달러예요.',
      '그런데 무제한 허락은 기본 단위로 2의 256제곱에 가까운 엄청난 수라서, 그대로 두면 한 주인의 허락 줄 전체를 혼자 차지해 버려요. 같은 주인의 500달러짜리 허락은 보이지도 않아요.',
      '그래서 허락 하나는 최대 2만 달러까지만 세도록 상한 U를 두었어요. 둘 중 작은 값을 쓰는 거예요. 그러면 무제한 허락은 2만 달러, 500달러 허락은 500달러로 세서, 줄을 97.6%와 2.4%로 나눠요. 2만 달러는 3월 31일까지 송금 한 건 금액의 99번째 백분위, 20,266달러를 두 자리로 반올림한 값이에요.',
      '실제로 마지막 허락의 45.8%가 무제한이고, 53.8%가 상한 이상이에요. 무제한과 유한한 허락을 함께 가진 주인도 79만 7,852명이에요. 처음에는 상한을 유한한 허락의 99번째 백분위로 정했는데, 그 값이 10의 47제곱 달러쯤이라 상한 구실을 못 했어요. 그래서 수정 점수를 하나도 계산하기 전에 이 정의를 고쳐서 커밋했어요.'
    ],
    html: '<h1 class="t-h1">무제한 허락이 줄 전체를 [[삼키지]] 않게</h1>' +
      '<div class="s5-amt" data-step="1">' +
        '<div class="s5-l"><b>달러 금액</b> = 기본 단위 × 10<sup>−소수 자릿수</sup> × 그날 가격 &nbsp; $x_e=n\\cdot10^{-q}\\cdot p$</div>' +
        '<div class="s5-slots" id="slots"><span class="ink-2">예: 1 USDC</span><span class="sl">1,000,000</span><span class="op">×</span><span class="sl">10⁻⁶</span><span class="op">×</span><span class="sl">1</span><span class="op">=</span><span class="sl" style="color:var(--ink)">1달러</span><span class="example-mark">예시 · 가격 1달러로 둠</span></div>' +
        '<div class="s5-note" style="margin-top:8px">$n$ = 기본 단위의 개수 · $q$ = 소수 자릿수 (USDC는 6) · $p$ = 그날 가격 · $10^{-6}$ = ÷ 1,000,000</div>' +
      '</div>' +
      '<div class="s5-panel" id="pn" data-in="none">' +
        '<div class="s5-l">C-PR의 두 층은 <b>V 없이</b> 달러 그대로 더해요</div>' +
        '<div class="s5-tx" style="font-size:26px">$$\\tilde w_A(u,v)=\\sum_{\\mathrm{token}}\\min\\bigl(a^{\\star},\\,\\ch{U}\\bigr),\\qquad \\tilde w_T(u,v)=\\sum_{e:\\,u\\to v}x_e\\,\\sigma(\\Delta t_e)$$</div>' +
        '<div class="s5-note">논문 식 (3.8) · min(a, U) = 둘 중 작은 것: 무제한이면 U, 500달러면 500</div>' +
        '<div data-step="3"><div class="s5-L">허락 하나는 최대 <span class="c-hi">U = ' + n0(U) + '달러</span>로 세요</div>' +
          '<div class="s5-note">U = t₁(3월 31일)까지 송금 한 건 금액의 99번째 백분위 (' + n0(P99T) + '달러)를 두 자리로 반올림</div>' +
          '<div class="s5-tx" style="font-size:26px;margin-top:6px">$\\frac{20{,}000}{20{,}000+500}=0.976,\\qquad \\frac{500}{20{,}500}=0.024$</div></div>' +
        '<div data-step="4" style="margin-top:22px;padding-top:16px;border-top:1px solid var(--line)">' +
          '<div class="s5-note">마지막 허락 중 무제한 <b>' + pct(UNL) + '</b> · 상한 이상 <b>' + pct(ATCAP) + '</b> · 무제한과 유한을 함께 가진 주인 <b>' + n0(BOTH) + '명</b></div>' +
          '<div class="s5-note" style="margin-top:8px">처음 정의 (유한 허락의 99번째 백분위)는 약 <b>10⁴⁷달러</b> → 상한 구실을 못 해서, 수정 점수를 계산하기 전에 고쳤어요 <span class="mono ink-3">(2705b28)</span></div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* bar chart: two spenders, linear dollars 0 … 25,000; S1 runs off the top */
      var P = g.P = plot(ctx, el, { x: 96, y: 380, w: 380, h: 560, l: 92, r: 360, t: 70, b: 440, xd: [0, 1], yd: [0, 25000] });
      yAxis(P, [[0, '0'], [10000, '10,000'], [20000, '20,000']], '');
      txt(P.grid, P.l - 86, P.t + 6, '달러', { size: 18, fill: C.ink2 });
      S('line', { x1: P.l, x2: P.r, y1: P.b, y2: P.b, stroke: C.ink3, 'stroke-width': 1.5 }, P.grid);
      var bw = 70, x1 = P.px(0.3), x2 = P.px(0.75);
      g.clipId = uid('cut');
      var defs = S('defs', {}, P.svg), cp = S('clipPath', { id: g.clipId }, defs);
      g.clipRect = S('rect', { x: 0, y: -400, width: 600, height: 1200 }, cp);
      g.s1 = S('rect', { x: x1 - bw / 2, y: P.t - 60, width: bw, height: P.b - P.t + 60, fill: C.allow, 'fill-opacity': 0.8, 'clip-path': 'url(#' + g.clipId + ')' }, P.main);
      g.s1top = S('path', { d: 'M' + (x1 - bw / 2) + ',' + (P.t - 60) + ' l12,-14 l12,14 l12,-14 l12,14 l12,-14 l10,14', fill: 'none', stroke: C.allow, 'stroke-width': 2.5 }, P.main);
      g.s1lab = txt(P.main, x1 + bw / 2 + 10, P.t - 40, '↑ 약 10⁷¹달러', { size: 18, fill: C.allow, weight: 700 });
      g.s2 = S('rect', { x: x2 - bw / 2, y: P.py(S2), width: bw, height: P.b - P.py(S2), fill: C.allow, 'fill-opacity': 0.8 }, P.main);
      txt(P.main, x2, P.py(S2) - 12, '500', { anchor: 'middle', size: 18, fill: C.allow, weight: 700, cls: 'svg-mono' });
      txt(P.grid, x1, P.b + 30, 'S1 무제한', { anchor: 'middle', size: 19, fill: C.ink2 });
      txt(P.grid, x2, P.b + 30, 'S2', { anchor: 'middle', size: 19, fill: C.ink2 });
      txt(P.grid, (x1 + x2) / 2, P.b + 58, '한 주인의 두 허락 · 예시', { anchor: 'middle', size: 17, fill: C.ink3 });
      /* the cap line U, the falling cut-off piece, the zigzag */
      g.uLine = S('g', {}, P.over);
      S('line', { x1: P.l - 10, x2: P.r + 6, y1: 0, y2: 0, stroke: C.hi, 'stroke-width': 2.5, 'stroke-dasharray': '8 6' }, g.uLine);
      txt(g.uLine, P.r + 6, -10, 'U', { anchor: 'end', size: 22, fill: C.hi, weight: 800 });
      gsap.set(g.uLine, { y: P.t - 120, autoAlpha: 0 });
      g.zig = S('path', { d: 'M' + (x1 - bw / 2) + ',' + P.py(U) + ' l12,-8 l12,8 l12,-8 l12,8 l12,-8 l10,8', fill: 'none', stroke: C.bg, 'stroke-width': 3 }, P.over);
      gsap.set(g.zig, { autoAlpha: 0 });
      g.piece = S('rect', { x: x1 - bw / 2, y: P.t - 60, width: bw, height: P.py(U) - P.t + 60, fill: C.allow, 'fill-opacity': 0.5 }, P.over);
      gsap.set(g.piece, { autoAlpha: 0 });
      /* exponent ladder for 1e47 (step 4) */
      g.ladder = S('text', { x: P.px(0.75), y: P.t + 30, 'text-anchor': 'middle', fill: C.hi, 'font-size': 20, 'font-weight': 800 }, P.over);
      gsap.set(g.ladder, { autoAlpha: 0 });
      /* one owner's row as a 100 % bar */
      var host = H('div', '', el); host.setAttribute('data-in', 'none');
      host.style.cssText = 'position:absolute;left:530px;top:470px;width:480px;height:360px';
      var rs = g.rs = Comp.svg(ctx, host, { w: 480, h: 360 });
      g.rowHost = host;
      txt(rs, 0, 24, '한 주인의 허락 줄 = 100%', { size: 22, fill: C.ink, weight: 700 });
      g.rowLab = txt(rs, 0, 56, '(가) 원래 단위 그대로', { size: 20, fill: C.ink2 });
      var RX = 0, RW = 470, RY = 86, RH = 64;
      S('rect', { x: RX, y: RY, width: RW, height: RH, rx: 10, fill: 'none', stroke: C.ink3, 'stroke-width': 1.5 }, rs);
      g.segA = S('rect', { x: RX, y: RY, width: RW, height: RH, rx: 10, fill: C.allow, 'fill-opacity': 0.85 }, rs);
      g.segB = S('rect', { x: RX + RW, y: RY, width: 0, height: RH, fill: '#FFD48A', 'fill-opacity': 0.95 }, rs);
      g.tA = txt(rs, RX + 16, RY + 41, 'S1  100%', { size: 22, fill: C.bg, weight: 800, cls: 'svg-mono' });
      g.tB = txt(rs, RX + RW, RY + RH + 34, 'S2  0.000…%', { anchor: 'end', size: 20, fill: C.ink2, cls: 'svg-mono' });
      g.RW = RW; g.RX = RX;
      txt(rs, 0, 268, '걷는 사람이 이 주인에게서 S2로 갈 확률 = S2의 몫', { size: 18, fill: C.ink3 });
      gsap.set([P.host, host], { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      ctx.gsap.fromTo(q(el, '#pn'), { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: E.out, delay: 0.2 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, P = g.P, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(qa(el, '#slots .sl'), { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.35, stagger: 0.25, ease: E.out }, 0.4);
      }
      if (i === 2) {
        tl.fromTo([P.host, g.rowHost], { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out, stagger: 0.15 }, 0);
        tl.fromTo(g.segA, { attr: { width: 0 } }, { attr: { width: g.RW }, duration: 1.0, ease: 'power2.inOut' }, 0.5);
        tl.fromTo(g.s1, { attr: { height: 0, y: P.b } }, { attr: { height: P.b - P.t + 60, y: P.t - 60 }, duration: 1.0, ease: 'power2.in' }, 0.3);
      }
      if (i === 3) {
        var frac = S2 / (S1 + S2);                              /* 0.0244 */
        tl.set(g.uLine, { autoAlpha: 1 }, 0);
        tl.to(g.uLine, { y: P.py(U), duration: 0.6, ease: 'power2.in' }, 0);
        tl.set(g.piece, { autoAlpha: 1 }, 0.6);
        tl.call(function () { g.clipRect.setAttribute('y', P.py(U)); }, null, 0.6);
        tl.set(g.zig, { autoAlpha: 1 }, 0.6);
        tl.to([g.s1top, g.s1lab], { autoAlpha: 0, duration: 0.3 }, 0.6);
        tl.to(g.piece, { y: 260, rotation: 14, svgOrigin: (P.px(0.3)) + ' ' + P.py(U), autoAlpha: 0, duration: 0.9, ease: 'power2.in' }, 0.65);
        tl.add(Comp.swap(ctx, g.rowLab, '(나) 달러 + 상한 U'), 1.0);
        tl.to(g.segA, { attr: { width: g.RW * (1 - frac) }, duration: 1.0, ease: E.io }, 1.2);
        tl.to(g.segB, { attr: { x: g.RX + g.RW * (1 - frac), width: g.RW * frac }, duration: 1.0, ease: E.io }, 1.2);
        tl.call(function () { g.tA.textContent = 'S1  ' + fmt((1 - frac) * 100, 1) + '%'; g.tB.textContent = 'S2  ' + fmt(frac * 100, 1) + '%'; }, null, 1.6);
      }
      if (i === 4) {
        var st = { e: 4 };
        tl.set(g.ladder, { autoAlpha: 1 }, 0.2);
        tl.to(st, { e: 47, duration: 1.4, ease: 'power2.in', onUpdate: function () { g.ladder.textContent = '10' + sup(Math.round(st.e)) + '달러'; } }, 0.2);
        tl.to(g.ladder, { y: -16, duration: 0.15, yoyo: true, repeat: 1 }, 1.6);
        tl.call(function () { g.ladder.textContent = '처음 정의: 약 10' + sup(47) + '달러'; g.ladder.setAttribute('font-size', 18); }, null, 1.9);
      }
    },
    tags: ['example']
  };

  Deck.section({ id: 's05-weights', title: '화살표의 무게', slides: [s1, s2, s3, s4, s5, s6] });
})();
