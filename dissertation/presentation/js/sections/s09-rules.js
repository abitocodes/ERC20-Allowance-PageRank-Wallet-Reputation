/* =========================================================================
   s09-rules — 미리 정한 규칙 (STORYBOARD.md §2, s09-01 … s09-05)

   s09-01  언제, 무엇을 정했나       vertical commit stem (git-graph look, folded time axis); locks
                                     click shut; "seconds zoom" panel counts 13:41:27 → 37 (10 s) and
                                     16:49:32 → 33 → 40 (8 s); the "results known from here" line;
                                     three revision commits with hollow locks, each followed by its query
   s09-02  규칙 A                     checklist cards + paired-difference bars (W0) + same-window part
                                     (C-PR outside the better layer's band) → stamp "미충족" + 재분석
   s09-03  규칙 B                     one number line −0.11 … +0.13, rose hatched margin [−δ, 0];
                                     F1 ✓, F2 ✕, F3 ✕ with a ×10 zoom on the lower end (−0.014 vs −0.010)
   s09-04  등록 분석과 수정 분석       three reasons (flat V curve, 12-digit ladder, spam token) +
                                     two-column table, "=" between the verdicts
   s09-05  R1–R3                      70 W1 traders as a dot grid (37 recipients, 9 liquidated); outcome
                                     definition; P and Q with 95 % bars and 97.5 % brackets; the
                                     registered sentences typed out; R3 profit-share bars

   Numbers and sources (R = revised digest, the thesis's main analysis; G = registered digest)
     13:41:27 / 13:41:37            G§D timing.plan_commit_43d8045_utc / timing.scan_a created
     16:49:32 / 16:49:40            G§D timing.registration_commit_0d3a057_utc / timing.scan_b created
     16:49:33 · override "no" · SHA-256   R§1 W1 extraction: started at / override used / SHA-256
     07:54:35 (a897475)             R§D timing.revision_commit_utc
     08:12:44 (09dfc32), 11:24:01 (2705b28)   git log (DECK_DATA.timeline.commits; thesis Ch. 3 gives 08:12, 11:24)
     08:16:11, 11:24:57 (56 s)      D:bq_ledger.json jobs[].at (DECK_DATA.timeline.ledger_jobs, gaps)
     rule A  +0.029 [0.022, 0.036], −0.034 [−0.040, −0.029]   R§6 contrasts_prefixed[0], [1]
             0.365 vs [0.653, 0.666]; 0.477 vs [0.590, 0.604]; 0.142 vs 0.011 / 0.404   R§3 rule_a_secondary
             registered +0.008 [0.003, 0.013], −0.030 [−0.034, −0.026]   G§6 contrasts_prefixed
     rule B  F1 +0.110 [0.098, 0.122], F2 −0.028 [−0.033, −0.023], F3 +0.000 [−0.014, 0.010]   R§7 rule_b
             δ = 0.010 R§7 delta; half-width 0.0040 = calc from G§6 contrasts_prefixed[1] (thesis Ch. 3/4)
             traders 70 R§7; F3 τ 0.350 [0.236, 0.461] R§7 trader_taus.cpr_l50 / cpr_l0
             AWP F2 −0.067 [−0.072, −0.061] R§7 sensitivity_awp.F2
             registered F1 +0.101 [0.092, 0.111], F2 −0.025 [−0.029, −0.021], F3 −0.044 [−0.100, −0.002]  G§7
     table   27,844/15,107 · 33,101/17,050 · 34,587/18,152 · 0.217/0.174 · verdicts   G / R (thesis table
             registered-vs-revised); 0.9978 / 0.9952 G§D allowances_ge10_share / transfers_ge10_share
     R1–R3   70 / 88 R§7 neutral_w1.n / neutral_w0.n; 9 liquidated R§7 traders_liquidated
             P W1 +0.084 [−0.013, 0.176], 97.5 % [−0.026, 0.188]; P W0 +0.182, 97.5 % [0.032, 0.338]
             Q W1 −0.041 [−0.135, 0.050], 97.5 % [−0.148, 0.064]; Q W0 −0.014, 97.5 % [−0.161, 0.151]
             R3: −0.196 [−0.364, −0.046] (profitable share), −0.252 [−0.391, −0.120] (non-loss share)
             37/37, 40/40, 72.7 %, 75.0 % neutral_w1/w0.recipients; 0.310 [0.184, 0.425] neutral_w1.taus.in_degree
             verdicts R§7 neutral_rules (G§7: same)
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt;
  var DATA = window.DECK_DATA || {};
  var NS = 'http://www.w3.org/2000/svg';

  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function txt(parent, x, y, s, attrs) { var a = { x: x, y: y }; for (var k in attrs) a[k] = attrs[k]; var t = svgEl('text', a, parent); t.textContent = s; return t; }
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
  function fadeUp(tl, els, at, d, stagger) { tl.fromTo(els, { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: d || 0.5, ease: E.out, stagger: stagger || 0 }, at); }
  function popIn(tl, els, at, d) { tl.fromTo(els, { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: d || 0.35, ease: E.stamp }, at); }
  /* typewriter: the registered sentence appears letter by letter (fixed in advance) */
  function typeIn(ctx, el, text, opt) {
    opt = opt || {};
    var st = { n: 0 }, L = text.length;
    el.textContent = '';
    return gsap.to(st, { n: L, duration: dur(ctx, opt.duration || Math.min(1.6, 0.035 * L)), ease: 'none', delay: opt.delay || 0,
      onUpdate: function () { el.textContent = text.slice(0, Math.round(st.n)); }, onComplete: function () { el.textContent = text; } });
  }
  var LOCK = function (cls) {
    return '<svg class="lk ' + (cls || '') + '" viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      '<rect x="4.5" y="10.5" width="15" height="10.5" rx="2.4"/><path class="sh" d="M8 10.5V7.4a4 4 0 0 1 8 0v3.1"/></svg>';
  };
  var LOOP_SVG = '<svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15.6 8.4A6 6 0 1 0 16 12"/><path d="M16.2 4.3v4.2H12"/></svg>';

  /* ------------------------------------------------------------ styles */
  var CSS = [
    /* s09-01 */
    '.s9-node{position:absolute;left:360px;display:flex;align-items:center;gap:14px;white-space:nowrap;transform:translateY(-50%)}',
    '.s9-node .k{font-size:26px;line-height:34px;font-weight:600;color:var(--ink)}',
    '.s9-node .code{font-family:var(--font-mono);font-size:21px;color:var(--ink);background:var(--bg-3);border:1px solid var(--line);border-radius:8px;padding:1px 9px;letter-spacing:0}',
    '.s9-node .sub{font-size:20px;line-height:28px;color:var(--ink-3)}',
    '.s9-node .chip{font-size:20px;line-height:26px;font-weight:800;color:var(--bg);background:var(--ink);border-radius:13px;padding:1px 12px}',
    '.s9-node.small .k{font-size:22px;color:var(--ink-2);font-weight:500}',
    '.s9-node .note{font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s9-node .note b{color:var(--ink);font-variant-numeric:tabular-nums}',
    '.s9-time{position:absolute;width:210px;left:96px;text-align:right;font-family:var(--font-mono);font-size:21px;line-height:28px;color:var(--ink-2);letter-spacing:0;transform:translateY(-50%)}',
    '.s9-date{position:absolute;left:96px;font-size:19px;line-height:26px;color:var(--ink-3);font-weight:600}',
    '.s9-lockw{position:absolute;left:308px;width:44px;height:44px;margin-top:-22px;border-radius:22px;background:var(--bg);display:flex;align-items:center;justify-content:center;color:var(--ink)}',
    '.s9-lockw.hollow{color:var(--ink-2)}',
    '.s9-lockw.hollow .lk rect,.s9-lockw.hollow .lk path{stroke-dasharray:3 3}',
    '.s9-node .re{display:inline-flex;color:var(--ink-2);margin-left:-6px}',
    '.s9-zoom{position:absolute;left:1240px;top:204px;width:584px;height:380px;border-radius:24px;background:var(--bg-2);border:1px solid var(--line);transform-origin:0% 50%}',
    '.s9-zoom .hd{position:absolute;left:28px;top:20px;font-family:var(--font-mono);font-size:17px;color:var(--ink-3);letter-spacing:0}',
    '.s9-zoom .clk{position:absolute;left:28px;top:54px;font-family:var(--font-mono);font-size:64px;line-height:72px;font-weight:700;color:var(--ink);letter-spacing:0;font-variant-numeric:tabular-nums}',
    '.s9-zoom .gap{position:absolute;right:28px;top:62px;font-size:44px;line-height:56px;font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums}',
    '.s9-zoom svg{position:absolute;left:0;top:150px;overflow:visible}',
    '.s9-zoom .cap{position:absolute;left:28px;right:28px;bottom:18px;font-size:20px;line-height:28px;color:var(--ink-2)}',
    '.s9-sep{position:absolute;left:200px;width:1000px;height:0;border-top:2px dashed var(--ink-2);transform-origin:0 50%}',
    '.s9-septx{position:absolute;font-size:22px;line-height:30px;font-weight:700;color:var(--ink);background:var(--bg);padding:0 10px}',
    '.s9-bot{font-size:27px;line-height:38px;color:var(--ink)}',
    '.s9-bot b{font-weight:800}',
    '.s9-small{font-size:19px;line-height:27px;color:var(--ink-3)}',
    /* s09-02 / s09-03 */
    '.s9-card{position:absolute;left:96px;width:660px;border-radius:20px;background:var(--bg-2);border:1.5px solid var(--line);padding:16px 22px 14px 24px}',
    '.s9-card .hd{font-size:26px;line-height:34px;font-weight:800;color:var(--ink)}',
    '.s9-card .ds{font-size:23px;line-height:33px;color:var(--ink-2)}',
    '.s9-card .fx{font-size:19px;line-height:28px;color:var(--ink-3)}',
    '.s9-card .fx .katex{font-size:22px}',
    '.s9-mark{position:absolute;right:20px;top:18px;width:46px;height:46px;border-radius:23px;border:2.5px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;line-height:1}',
    '.s9-mark.ok{border-color:var(--ink);color:var(--ink)}',
    '.s9-mark.no{border-color:var(--c-hi);color:var(--c-hi)}',
    '.s9-ax text{font-family:var(--font-sans)}',
    '.s9-cell{position:absolute;width:330px;height:132px;border-radius:16px;background:var(--bg-2);border:1px solid var(--line)}',
    '.s9-cell .hd{position:absolute;left:16px;top:8px;font-size:20px;line-height:28px;font-weight:700}',
    '.s9-cell .v{position:absolute;left:16px;top:34px;font-size:17px;line-height:24px;color:var(--ink-2);font-variant-numeric:tabular-nums;white-space:nowrap}',
    '.s9-cell svg{position:absolute;left:0;top:52px;overflow:visible}',
    '.s9-verd{display:flex;align-items:center;gap:16px}',
    '.s9-line{font-size:24px;line-height:34px;color:var(--ink-2)}',
    '.s9-line b{color:var(--ink);font-variant-numeric:tabular-nums}',
    '.s9-tiny{font-size:20px;line-height:30px;color:var(--ink-3)}',
    '.s9-tiny b{color:var(--ink-2);font-variant-numeric:tabular-nums;font-weight:600}',
    '.s9-tiny .pill{vertical-align:-2px;margin-right:8px}',
    '.s9-fl{position:absolute;left:96px;width:470px}',
    '.s9-fl .hd{font-size:28px;line-height:36px;font-weight:800;color:var(--ink)}',
    '.s9-fl .ds{font-size:20px;line-height:28px;color:var(--ink-3)}',
    '.s9-fx{font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s9-fx .katex{font-size:24px}',
    '.s9-inset{position:absolute;left:1180px;top:660px;width:644px;height:200px;border-radius:20px;background:rgba(16,21,31,.97);border:1px solid #39435A;box-shadow:0 18px 50px rgba(0,0,0,.5)}',
    '.s9-inset .hd{position:absolute;left:20px;top:12px;font-size:18px;line-height:24px;color:var(--ink-3);font-family:var(--font-mono);letter-spacing:0}',
    '.s9-inset svg{position:absolute;left:0;top:0;overflow:visible}',
    /* s09-04 */
    '.s9-rs{position:absolute;left:96px;width:660px;display:flex;gap:18px;align-items:flex-start;padding:14px 18px;border-radius:18px;background:var(--bg-2);border:1px solid var(--line)}',
    '.s9-rs svg{flex:0 0 auto}',
    '.s9-rs .t{font-size:22px;line-height:32px;color:var(--ink)}',
    '.s9-rs .t small{display:block;font-size:18px;line-height:26px;color:var(--ink-3)}',
    '.s9-th{position:absolute;top:196px;width:300px}',
    '.s9-th .nm{font-size:30px;line-height:40px;font-weight:800}',
    '.s9-th .ds{font-size:18px;line-height:26px;color:var(--ink-3);margin-top:4px}',
    '.s9-tr{position:absolute;left:800px;width:1024px;height:46px;display:flex;align-items:center;border-bottom:1px solid var(--line);font-size:23px}',
    '.s9-tr .l{width:400px;color:var(--ink-2)}',
    '.s9-tr .a{width:250px;text-align:right;color:var(--ink-3);font-variant-numeric:tabular-nums}',
    '.s9-tr .eq{width:90px;text-align:center;color:var(--ink-3);font-weight:700}',
    '.s9-tr .b{width:280px;text-align:left;color:var(--ink);font-weight:700;font-variant-numeric:tabular-nums}',
    '.s9-tr.vd .a,.s9-tr.vd .b{font-weight:800}',
    '.s9-tr.vd .eq{color:var(--ink);font-size:30px}',
    '.s9-bold{font-size:28px;line-height:40px;font-weight:800;color:var(--ink)}',
    /* s09-05 */
    '.s9-wl{font-size:20px;line-height:30px;color:var(--ink-2)}',
    '.s9-wl i{display:inline-block;width:14px;height:14px;border-radius:7px;margin-right:8px;vertical-align:-1px}',
    '.s9-def{position:absolute;left:760px;top:192px;width:1064px;border-radius:20px;background:var(--bg-2);border:1px solid var(--line);padding:14px 24px;display:flex;align-items:center;gap:24px}',
    '.s9-def .k{font-size:24px;line-height:32px;font-weight:700;color:var(--ink);white-space:nowrap}',
    '.s9-def .katex{font-size:30px}',
    '.s9-rule{font-size:22px;line-height:30px;color:var(--ink);white-space:nowrap;background:var(--bg);padding:2px 10px 2px 0;border-radius:8px}',
    '.s9-rule .typed{color:var(--ink-2)}',
    '.s9-score{position:absolute;left:96px;display:flex;flex-direction:column;gap:12px}',
    '.s9-score .r{display:flex;align-items:center;gap:14px;font-size:24px;line-height:32px;color:var(--ink-2)}',
    '.s9-score .r b{font-family:var(--font-mono);font-size:26px;color:var(--ink);width:44px;letter-spacing:0}',
    '.s9-v{display:inline-flex;align-items:center;padding:3px 14px;border-radius:12px;font-size:22px;font-weight:800;border:2.5px solid var(--ink);color:var(--ink)}',
    '.s9-v.no{border-color:var(--c-hi);color:var(--c-hi)}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s09-style')) return;
    var st = document.createElement('style'); st.id = 's09-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  /* interval bar (G9), optional 97.5 % brackets (outer) */
  function ivBar(svg, o) {
    var g = svgEl('g', {}, svg), x0 = o.scale(o.from != null ? o.from : 0);
    var outer = null;
    if (o.outer) {
      var xa = o.scale(o.outer[0]), xb = o.scale(o.outer[1]), y = o.y;
      outer = svgEl('path', { d: 'M' + (xa + 7) + ',' + (y - 15) + ' L' + xa + ',' + (y - 15) + ' L' + xa + ',' + (y + 15) + ' L' + (xa + 7) + ',' + (y + 15) +
        ' M' + (xb - 7) + ',' + (y - 15) + ' L' + xb + ',' + (y - 15) + ' L' + xb + ',' + (y + 15) + ' L' + (xb - 7) + ',' + (y + 15), fill: 'none', stroke: o.color, 'stroke-width': 2.4 }, g);
    }
    var bar = svgEl('line', { x1: x0, x2: x0, y1: o.y, y2: o.y, stroke: o.color, 'stroke-width': o.width || 6, 'stroke-linecap': 'round', opacity: o.opacity != null ? o.opacity : 1 }, g);
    var dot = svgEl('circle', { cx: x0, cy: o.y, r: o.r || 11, fill: o.hollow ? C.bg : o.color, stroke: o.color, 'stroke-width': 3 }, g);
    gsap.set(g, { autoAlpha: 0 });
    if (outer) gsap.set(outer, { autoAlpha: 0 });
    var B = { g: g, bar: bar, dot: dot, outer: outer, o: o };
    B.grow = function (ctx, opt) {
      opt = opt || {};
      var tl = gsap.timeline({ delay: opt.delay || 0 }), d = dur(ctx, opt.duration != null ? opt.duration : 0.8);
      tl.set(g, { autoAlpha: 1 }, 0);
      tl.fromTo(bar, { attr: { x1: x0, x2: x0 } }, { attr: { x1: o.scale(o.lo), x2: o.scale(o.hi) }, duration: d, ease: E.out }, 0);
      tl.fromTo(dot, { attr: { cx: x0 } }, { attr: { cx: o.scale(o.est) }, duration: d, ease: E.out }, 0);
      if (outer) tl.fromTo(outer, { autoAlpha: 0 }, { autoAlpha: 0.9, duration: dur(ctx, 0.4) }, d * 0.9);
      return tl;
    };
    B.showNow = function () { gsap.set(g, { autoAlpha: 1 }); bar.setAttribute('x1', o.scale(o.lo)); bar.setAttribute('x2', o.scale(o.hi)); dot.setAttribute('cx', o.scale(o.est)); if (outer) gsap.set(outer, { autoAlpha: 0.9 }); };
    return B;
  }
  /* linear axis on an svg (stage coords): ticks, gridlines, dashed zero */
  function axis(svg, o) {
    var g = svgEl('g', { 'class': 's9-ax' }, svg);
    o.ticks.forEach(function (t) {
      if (t !== 0 && o.grid !== false) svgEl('line', { x1: o.scale(t), x2: o.scale(t), y1: o.y0, y2: o.y1, stroke: 'rgba(233,237,245,.07)', 'stroke-width': 1 }, g);
      txt(g, o.scale(t), o.y1 + 26, t === 0 ? '0' : (o.signed ? sfmt(t, o.dec || 2) : mfmt(t, o.dec || 2)), { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 17, 'class': 'tnum' });
    });
    svgEl('line', { x1: o.scale(o.domain[0]), x2: o.scale(o.domain[1]), y1: o.y1, y2: o.y1, stroke: C.line, 'stroke-width': 1.5 }, g);
    if (o.zero !== false) svgEl('line', { x1: o.scale(0), x2: o.scale(0), y1: o.y0 - 6, y2: o.y1, stroke: C.ink2, 'stroke-width': 1.6, 'stroke-dasharray': '5 6' }, g);
    return g;
  }
  function lin(d0, d1, x0, x1) { return function (v) { return x0 + (v - d0) / (d1 - d0) * (x1 - x0); }; }

  /* ================================================================ s09-01 timeline of commits */
  var STEM = { x: 330, y0: 206, y1: 820 };
  var N1 = [
    { y: 236, t: '13:41:27', html: '<span class="k">분석 계획 커밋</span><span class="code">43d8045</span><span class="sub">로그를 하나도 꺼내기 전</span>', lock: 'closed', step: 1 },
    { y: 298, t: '13:41:37', html: '<span class="k">1차 추출(scan A) 시작</span><span class="chip">10초 뒤</span>', step: 1, late: 1.9 },
    { y: 364, t: '같은 날', html: '<span class="k">코호트 · 라벨 · 같은 기간과 W0 결과</span><span class="sub">→ 규칙 A 판정</span>', step: 2 },
    { y: 452, t: '16:49:32', html: '<span class="k">W1 등록 커밋</span><span class="code">0d3a057</span><span class="sub">규칙 B · R1–R3 · 허용 폭 · 판정 문장</span>', lock: 'closed', step: 3 },
    { y: 508, t: '16:49:33', html: '<span class="k">추출 기록서 작성</span><span class="sub">두 파일의 SHA-256 · 예외 사용 안 함</span>', step: 3, small: true, late: 1.2 },
    { y: 562, t: '16:49:40', html: '<span class="k">2차 추출(scan B) 시작</span><span class="chip">8초 뒤</span>', step: 3, late: 2.0 },
    { y: 680, t: '07:54:35', html: '<span class="k">금액 수정 문서</span><span class="code">a897475</span>', lock: 'hollow', step: 5 },
    { y: 738, t: '08:12:44', html: '<span class="k">다섯 토큰과 가격</span><span class="code">09dfc32</span><span class="note">→ 08:16 질의: 다섯 토큰 표</span>', lock: 'hollow', step: 5 },
    { y: 796, t: '11:24:01', html: '<span class="k">상한 U 고침</span><span class="code">2705b28</span><span class="note">→ <b>11:24:57</b> 첫 수정 점수 입력</span>', lock: 'hollow', step: 5 }
  ];
  var slide1 = {
    id: 's09-01', title: '언제, 무엇을 정했나', time: 60, steps: 6,
    tags: function (s) { return s >= 5 ? ['plan', 'registered', 'reanalysis'] : s >= 3 ? ['plan', 'registered'] : s >= 1 ? ['plan'] : []; },
    notes: [
      '이 연구에서 가장 신경 쓴 것은 순서예요. 이 줄기는 공개 저장소의 커밋과 데이터 추출을 시간 순서로 놓은 거예요. 물결 표시는 시간을 접은 곳이에요.',
      '10월 9일 13시 41분 27초, 데이터를 하나도 꺼내기 전에 분석 계획을 공개 저장소에 커밋했어요. 자물쇠가 잠기죠. 오른쪽에서 초 단위로 늘려 보면, 정확히 10초 뒤에 첫 추출이 시작됐어요.',
      '같은 날 코호트와 라벨을 만들고, 같은 기간과 W0 결과를 계산해서 규칙 A를 판정했어요.',
      '그 W0 결과를 본 다음, W1에서 무엇을 시험할지를 등록했어요. 16시 49분 32초 커밋이에요. 1초 뒤에 추출 기록서가 쓰이기 시작했고, 8초 뒤에 7월부터 9월까지의 기록을 꺼냈어요. 추출 스크립트는 등록 커밋이 없으면 돌지 않고, 기록서에는 두 파일의 SHA-256과 예외를 쓰지 않았다는 기록이 남아 있어요.',
      '여기까지가 등록 분석이에요. 이 선 아래부터는 등록 분석의 결과를 알고 있었어요.',
      '다음 날 저는 금액 단위에 문제가 있다는 것을 알고 금액을 달러로 고쳤어요. 이것은 등록 결과를 본 뒤의 변경이에요. 그래서 자물쇠가 속이 비어 있어요. 다만 수정 문서, 다섯 토큰, 상한 U를 차례로 커밋한 다음에야 질의와 점수 계산을 돌렸어요. 마지막 커밋 56초 뒤에 첫 수정 점수의 입력이 만들어졌어요.',
      '그래서 계획과 등록은 데이터보다 먼저였고, 이것이 등록 분석이에요. 수정은 등록 결과를 본 뒤였지만 수정 점수를 계산하기 전에 커밋했어요. 이것이 수정 분석이고, 여기에 등록 규칙을 적용한 판정은 모두 재분석이라고 불러요.'
    ],
    html: function () {
      var s = '<h1 class="t-h1">규칙을 먼저 [[잠그고]], 그다음에 데이터를 꺼냈어요</h1>';
      s += '<svg class="abs" id="stem" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible"></svg>';
      s += '<div class="s9-date" id="d1" data-in="none" style="top:180px">2026년 10월 9일 · UTC</div>';
      s += '<div class="s9-date" id="d2" data-in="none" style="top:636px">10월 10일</div>';
      N1.forEach(function (n, i) {
        s += '<div class="s9-time" data-n="' + i + '" data-in="none" style="top:' + n.y + 'px">' + n.t + '</div>';
        if (n.lock) s += '<div class="s9-lockw ' + n.lock + '" data-lk="' + i + '" data-in="none" style="top:' + n.y + 'px">' + LOCK() + '</div>';
        s += '<div class="s9-node' + (n.small ? ' small' : '') + '" data-n="' + i + '" data-in="none" style="top:' + n.y + 'px">' + n.html.replace('</span><span class="note">', '</span><span class="re">' + LOOP_SVG + '</span><span class="note">') + (n.lock === 'hollow' && n.html.indexOf('class="note"') < 0 ? '<span class="re">' + LOOP_SVG + '</span>' : '') + '</div>';
      });
      s += '<div class="s9-sep" id="sep" data-in="none" style="top:616px"></div>';
      s += '<div class="s9-septx" id="septx" data-in="none" style="left:760px;top:600px">여기서부터 등록 분석 결과를 앎</div>';
      s += '<div class="s9-zoom" id="zoom" data-in="none"><div class="hd" id="zhd">초 단위로 늘려 보기</div><div class="clk" id="clk">13:41:27</div><div class="gap" id="zgap">0초</div>' +
        '<svg id="zr" width="584" height="150" viewBox="0 0 584 150"></svg><div class="cap" id="zcap"></div></div>';
      s += '<div class="abs s9-bot" id="bot1" data-in="none" style="left:96px;top:846px;width:1728px"><b>계획과 등록은 데이터보다 먼저</b> → 등록 분석 &nbsp;·&nbsp; <b>수정은 등록 결과를 본 뒤, 하지만 수정 점수 계산 전에 커밋</b> → 수정 분석(재분석)</div>';
      s += '<div class="abs s9-small" id="bot2" data-in="none" style="left:96px;top:894px;width:1728px">추출 스크립트는 등록 커밋이 없으면 돌지 않아요 · 기록서에 두 파일의 SHA-256과 ‘예외 사용 안 함’이 적혀 있어요 · 커밋 시각은 저장소 기록(git log), 질의 시각은 빅쿼리 장부</div>';
      return s;
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      var sv = q(el, '#stem');
      /* stem with two folds (time folded between 13:43 and 16:49, and overnight) */
      var F1 = 408, F2 = 640;
      var d = 'M' + STEM.x + ',' + STEM.y0 + ' L' + STEM.x + ',' + (F1 - 10) + ' M' + STEM.x + ',' + (F1 + 10) + ' L' + STEM.x + ',' + (F2 - 10) + ' M' + STEM.x + ',' + (F2 + 10) + ' L' + STEM.x + ',' + STEM.y1;
      g.stem = svgEl('path', { d: d, stroke: '#3A4458', 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }, sv);
      g.folds = [F1, F2].map(function (fy) {
        return svgEl('path', { d: 'M' + (STEM.x - 16) + ',' + (fy - 6) + ' q 8,-8 16,0 t 16,0 M' + (STEM.x - 16) + ',' + (fy + 6) + ' q 8,-8 16,0 t 16,0', stroke: C.ink3, 'stroke-width': 2, fill: 'none' }, sv);
      });
      g.head = svgEl('circle', { cx: STEM.x, cy: STEM.y0, r: 8, fill: '#fff', 'class': 'glow-white' }, sv);
      g.dots = N1.map(function (n) { return svgEl('circle', { cx: STEM.x, cy: n.y, r: n.lock ? 0 : 7, fill: C.bg, stroke: C.ink3, 'stroke-width': 2.5 }, sv); });
      gsap.set(g.folds.concat([g.head]), { autoAlpha: 0 });
      g.times = qa(el, '.s9-time'); g.nodes = qa(el, '.s9-node'); g.locks = {};
      qa(el, '.s9-lockw').forEach(function (L) { g.locks[+L.getAttribute('data-lk')] = L; });
      gsap.set(g.times.concat(g.nodes), { autoAlpha: 0 });
      Object.keys(g.locks).forEach(function (k) { gsap.set(g.locks[k], { autoAlpha: 0.35 }); gsap.set(q(g.locks[k], '.sh'), { y: -5 }); });
      g.d1 = q(el, '#d1'); g.d2 = q(el, '#d2'); g.sep = q(el, '#sep'); g.septx = q(el, '#septx');
      g.zoom = q(el, '#zoom'); g.clk = q(el, '#clk'); g.zgap = q(el, '#zgap'); g.zr = q(el, '#zr'); g.zcap = q(el, '#zcap'); g.zhd = q(el, '#zhd');
      g.bot1 = q(el, '#bot1'); g.bot2 = q(el, '#bot2');
      gsap.set([g.d2, g.sep, g.septx, g.zoom, g.bot1, g.bot2], { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      var L = STEM.y1 - STEM.y0 + 20;
      tl.fromTo(g.stem, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur(ctx, 1.4), ease: 'power1.inOut' }, 0.2);
      tl.set(g.head, { autoAlpha: 1 }, 0.2);
      tl.fromTo(g.head, { attr: { cy: STEM.y0 } }, { attr: { cy: STEM.y1 }, duration: dur(ctx, 1.4), ease: 'power1.inOut' }, 0.2);
      tl.to(g.head, { autoAlpha: 0, duration: 0.3 }, 1.6);
      tl.fromTo(g.folds, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, stagger: 0.3 }, 0.6);
      tl.fromTo(g.dots, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, stagger: 0.12 }, 0.3);
      tl.fromTo(Object.keys(g.locks).map(function (k) { return g.locks[k]; }), { autoAlpha: 0 }, { autoAlpha: 0.35, duration: 0.3, stagger: 0.1 }, 0.4);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      function showNode(k, at) {
        tl.fromTo([g.times[k], g.nodes[k]], { autoAlpha: 0, x: -14 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.4), ease: E.out }, at);
        tl.to(g.dots[k], { attr: { fill: C.ink, stroke: C.ink }, duration: 0.3 }, at);
      }
      function lockShut(k, at) {
        var L = g.locks[k];
        tl.to(L, { autoAlpha: 1, duration: 0.15 }, at);
        tl.to(q(L, '.sh'), { y: 0, duration: dur(ctx, 0.18), ease: 'power4.in' }, at + 0.1);
        tl.fromTo(L, { scale: 1.25 }, { scale: 1, duration: dur(ctx, 0.3), ease: E.stamp }, at + 0.26);
      }
      function zoom(cfg, at) {
        /* the panel grows out of the node (a "powers of ten" for time) */
        var ny = cfg.y;
        tl.set(g.zoom, { autoAlpha: 1 }, at);
        tl.fromTo(g.zoom, { scaleX: 0.04, scaleY: 0.12, x: 360 - 1240 + 380, y: ny - (204 + 190) }, { scaleX: 1, scaleY: 1, x: 0, y: 0, duration: dur(ctx, 0.7), ease: E.io }, at);
        tl.call(function () {
          g.zhd.textContent = cfg.hd; g.zcap.innerHTML = cfg.cap; g.zgap.textContent = '0초';
          while (g.zr.firstChild) g.zr.removeChild(g.zr.firstChild);
          var X = lin(0, cfg.n, 40, 544);
          svgEl('line', { x1: X(0), x2: X(cfg.n), y1: 60, y2: 60, stroke: C.line, 'stroke-width': 3, 'stroke-linecap': 'round' }, g.zr);
          for (var s = 0; s <= cfg.n; s++) {
            var major = cfg.n <= 12 || s % 10 === 0 || s === cfg.n;
            svgEl('line', { x1: X(s), x2: X(s), y1: major ? 50 : 55, y2: major ? 70 : 65, stroke: C.ink3, 'stroke-width': s === 0 || s === cfg.n ? 2.5 : major ? 1.5 : 1 }, g.zr);
            if (major && !(cfg.n > 12 && s === 50)) txt(g.zr, X(s), 96, String(s), { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 16, 'class': 'tnum' });
          }
          g.sweep = svgEl('line', { x1: X(0), x2: X(0), y1: 60, y2: 60, stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round', 'class': 'glow-white' }, g.zr);
          g.zmarks = cfg.marks.map(function (m) {
            var gg = svgEl('g', {}, g.zr);
            svgEl('circle', { cx: X(m.s), cy: 60, r: 10, fill: m.fill || C.ink, stroke: C.bg, 'stroke-width': 3 }, gg);
            var mid = m.s !== 0 && m.s !== cfg.n;
            txt(gg, mid ? X(m.s) - 4 : X(m.s), mid ? 128 : 30, m.label, { 'text-anchor': m.s === 0 ? 'start' : m.s === cfg.n ? 'end' : 'start', fill: mid ? C.ink2 : C.ink, 'font-size': 19, 'font-weight': 700 });
            gsap.set(gg, { autoAlpha: 0 });
            return { g: gg, s: m.s };
          });
          g.X = X;
        }, null, at + 0.05);
        var st = { s: 0 };
        tl.fromTo(st, { s: 0 }, { s: cfg.n, duration: dur(ctx, Math.min(2.0, 0.2 * cfg.n + 0.4)), ease: 'none',
          onUpdate: function () {
            var s = st.s, sec = cfg.start[2] + Math.floor(s + 1e-6);
            g.clk.textContent = cfg.start[0] + ':' + cfg.start[1] + ':' + (sec < 10 ? '0' : '') + sec;
            g.zgap.textContent = Math.floor(s + 1e-6) + '초';
            if (g.sweep) g.sweep.setAttribute('x2', g.X(s));
            if (g.zmarks) g.zmarks.forEach(function (m) { if (s >= m.s - 1e-6 && !m.on) { m.on = true; ctx.add(function () { gsap.fromTo(m.g, { autoAlpha: 0, scale: 0.5, svgOrigin: g.X(m.s) + ' 60' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.3), ease: E.stamp }); }); } });
          },
          onComplete: function () {
            var sec = cfg.start[2] + cfg.n;
            g.clk.textContent = cfg.start[0] + ':' + cfg.start[1] + ':' + (sec < 10 ? '0' : '') + sec;
            g.zgap.textContent = cfg.n + '초'; if (g.sweep) g.sweep.setAttribute('x2', g.X(cfg.n));
            if (g.zmarks) g.zmarks.forEach(function (m) { m.on = true; gsap.set(m.g, { autoAlpha: 1, scale: 1 }); });
          } }, at + 0.75);
      }
      if (i === 1) {
        showNode(0, 0); lockShut(0, 0.15);
        zoom({ y: 236, n: 10, start: ['13', '41', 27], hd: '10월 9일 · 초 단위로 늘려 보기', cap: '계획 커밋 → 첫 추출: <b class="ink">10초</b>',
          marks: [{ s: 0, label: '계획 커밋' }, { s: 10, label: 'scan A 시작' }] }, 0.5);
        showNode(1, 3.1);
      }
      if (i === 2) {
        showNode(2, 0);
      }
      if (i === 3) {
        showNode(3, 0); lockShut(3, 0.15);
        zoom({ y: 452, n: 8, start: ['16', '49', 32], hd: '10월 9일 · 초 단위로 늘려 보기', cap: '등록 커밋 → 기록서 <b class="ink">1초</b> → W1 추출 <b class="ink">8초</b>',
          marks: [{ s: 0, label: '등록 커밋' }, { s: 1, label: '기록서', fill: C.ink2 }, { s: 8, label: 'scan B 시작' }] }, 0.5);
        showNode(4, 1.7); showNode(5, 2.7);
      }
      if (i === 4) {
        tl.fromTo(g.sep, { autoAlpha: 1, scaleX: 0 }, { autoAlpha: 1, scaleX: 1, duration: dur(ctx, 0.9), ease: E.io }, 0);
        tl.fromTo(g.septx, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: E.out }, 0.7);
        tl.to(g.zoom, { autoAlpha: 0, duration: 0.4 }, 0);
      }
      if (i === 5) {
        fadeUp(tl, g.d2, 0, 0.4);
        [6, 7, 8].forEach(function (k, j) {
          var at = 0.2 + j * 0.55;
          showNode(k, at);
          tl.to(g.locks[k], { autoAlpha: 1, duration: 0.3 }, at);
          var re = q(g.nodes[k], '.re'); if (re) popIn(tl, re, at + 0.25);
        });
        zoom({ y: 796, n: 56, start: ['11', '24', 1], hd: '10월 10일 · 마지막 수정 커밋 → 첫 수정 점수 입력', cap: '수정은 등록 결과를 본 뒤였지만, <b class="ink">수정 점수를 계산하기 전에</b> 커밋했어요',
          marks: [{ s: 0, label: '2705b28 커밋' }, { s: 56, label: '첫 쌍 표 완료' }] }, 1.9);
      }
      if (i === 6) {
        fadeUp(tl, [g.bot1, g.bot2], 0.1, 0.5, 0.2);
      }
    }
  };

  /* ================================================================ s09-02 rule A */
  var A2 = { x0: 900, x1: 1560, d: [-0.05, 0.05], rows: [{ y: 262, v: '+0.029 [0.022, 0.036]', g: '+0.008 [0.003, 0.013]', ok: true }, { y: 408, v: '−0.034 [−0.040, −0.029]', g: '−0.030 [−0.034, −0.026]', ok: false }] };
  var SW2 = [
    { hd: '송금 가족', col: C.xfer, cpr: 0.365, band: [0.653, 0.666], bandCol: C.xfer, v: 'C-PR 0.365 · λ = 0 구간 [0.653, 0.666]' },
    { hd: '허락 가족', col: C.allow, cpr: 0.477, band: [0.590, 0.604], bandCol: C.allow, v: 'C-PR 0.477 · λ = 1 구간 [0.590, 0.604]' },
    { hd: '시빌 안정성', col: C.ink, cpr: 0.142, ticks: [[0.011, C.allow, 'λ=1 0.011'], [0.404, C.xfer, 'λ=0 0.404']], v: 'C-PR 0.142 · λ = 1 0.011 · λ = 0 0.404' }
  ];
  var slide2 = {
    id: 's09-02', title: '규칙 A (분석 계획, 추출 전에 정함)', time: 45, steps: 5,
    tags: function (s) { return s >= 5 ? ['plan', 'reanalysis', 'registered-analysis'] : s >= 4 ? ['plan', 'reanalysis'] : ['plan']; },
    notes: [
      '규칙 A는 데이터를 꺼내기 전에 분석 계획에 적어 둔 규칙이에요. 두 화살표를 섞은 C-PR이 W0에서 허락 층만 걷는 것보다 나쁘지 않고, 동시에 송금 층만 걷는 것보다 나아야 해요. 같은 기간 부분도 있어요.',
      '첫째 조건이에요. 새 허락 쌍에서 C-PR에서 허락 층만 걷기를 짝지어 빼면 0.029, 구간이 0보다 위라서 맞았어요.',
      '둘째 조건에서는 C-PR이 송금 층보다 오히려 0.034 낮았어요. 구간 전체가 0 왼쪽이라서 맞지 않아요.',
      '같은 기간 부분도 세 가지 모두 맞지 않았어요. 송금 가족과 허락 가족에서 C-PR은 더 나은 층의 구간 안에 들지 못했고, 시빌 안정성에서는 두 층보다 위에 있어야 하는데 송금 층보다 낮았어요.',
      '그래서 규칙 A는 미충족이에요. 이 판정은 수정 점수에 미리 정한 규칙을 적용한 재분석이에요.',
      '처음 등록한 분석에서도 똑같이 미충족이었어요. 회색 빈 점이 그 값이에요.'
    ],
    html:
      '<h1 class="t-h1">규칙 A: C-PR(λ = 0.5)이 두 층을 [[모두]] 넘을까?</h1>' +
      '<div class="s9-card" id="ca1" data-in="none" style="top:196px;height:132px"><div class="hd">① W0 · 새 허락 쌍</div><div class="ds">허락 층만 걷기(λ = 1)보다 나쁘지 않을 것</div><div class="fx">$\\Delta\\tau=\\tau_{\\mathrm{CPR}}-\\tau_{\\lambda=1}$의 95% 구간이 0을 품거나 0보다 위</div><div class="s9-mark" id="m1"></div></div>' +
      '<div class="s9-card" id="ca2" data-in="none" style="top:342px;height:132px"><div class="hd">② W0 · 새 송금자</div><div class="ds">송금 층만 걷기(λ = 0)보다 나을 것</div><div class="fx">$\\Delta\\tau=\\tau_{\\mathrm{CPR}}-\\tau_{\\lambda=0}$의 95% 구간이 0보다 위</div><div class="s9-mark" id="m2"></div></div>' +
      '<div class="s9-card" id="ca3" data-in="none" style="top:530px;height:132px"><div class="hd">③ 같은 기간 부분</div><div class="ds">송금·허락: 더 나은 층의 95% 구간 안에</div><div class="ds">시빌 안정성: 두 층보다 위</div><div class="s9-mark" id="m3"></div></div>' +
      '<svg class="abs" id="ax2" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible"></svg>' +
      '<div class="abs" id="sw2" data-in="none" style="left:800px;top:530px;width:1024px;height:132px"></div>' +
      '<div class="abs s9-verd" id="verd" data-in="none" style="left:96px;top:712px"><span id="stampHost"></span><span id="reTag">' + pill('reanalysis') + '</span><span class="s9-line" id="reTx">수정 점수에 미리 정한 규칙을 적용한 판정이에요 — 등록 시험이 아니에요</span></div>' +
      '<div class="abs s9-tiny" id="gl" data-in="none" style="left:96px;top:806px;width:1728px">' + pill('registered-analysis') + '등록 분석에서도 미충족: ① <b>+0.008 [0.003, 0.013]</b> · ② <b>−0.030 [−0.034, −0.026]</b> · 같은 기간 부분도 미충족 (회색 빈 점)</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var sv = q(el, '#ax2'), X = lin(A2.d[0], A2.d[1], A2.x0, A2.x1);
      txt(sv, A2.x0, 214, '짝지은 차이 Δτ (W0)', { fill: C.ink2, 'font-size': 22, 'font-weight': 700 });
      txt(sv, X(0) - 10, 240, '← 층만 걷기가 나음', { 'text-anchor': 'end', fill: C.ink3, 'font-size': 17 });
      txt(sv, X(0) + 10, 240, 'C-PR이 나음 →', { 'text-anchor': 'start', fill: C.ink3, 'font-size': 17 });
      axis(sv, { scale: X, domain: A2.d, ticks: [-0.04, -0.02, 0, 0.02, 0.04], y0: 250, y1: 470, signed: true });
      g.rows = A2.rows.map(function (r) {
        var d = iv(r.v), gd = iv(r.g);
        var B = ivBar(sv, { scale: X, y: r.y, est: d.est, lo: d.lo, hi: d.hi, color: C.cpr, width: 7, r: 12 });
        var G = ivBar(sv, { scale: X, y: r.y + 22, est: gd.est, lo: gd.lo, hi: gd.hi, color: C.ink3, hollow: true, width: 3, r: 7, from: gd.est, opacity: 0.85 });
        var vt = svgEl('text', { x: A2.x1 + 30, y: r.y + 8, 'font-size': 24, 'class': 'tnum' }, sv);
        var e1 = svgEl('tspan', { fill: C.ink, 'font-weight': 800 }, vt); e1.textContent = estOf(r.v);
        var e2 = svgEl('tspan', { fill: C.ink3, 'font-size': 19, dx: 8 }, vt); e2.textContent = ciOf(r.v);
        gsap.set(vt, { autoAlpha: 0 });
        return { B: B, G: G, vt: vt, est: e1, d: d };
      });
      /* same-window part: three small τ axes */
      var host = q(el, '#sw2');
      g.cells = SW2.map(function (c, j) {
        var cell = document.createElement('div'); cell.className = 's9-cell'; cell.style.left = (j * 347) + 'px'; cell.style.top = '0px';
        cell.innerHTML = '<div class="hd" style="color:' + c.col + '">' + c.hd + '</div><div class="v tnum">' + c.v + '</div>';
        host.appendChild(cell);
        var sv2 = svgEl('svg', { width: 330, height: 80, viewBox: '0 0 330 80' }, cell);
        var x = lin(0, 0.7, 20, 310);
        svgEl('line', { x1: x(0), x2: x(0.7), y1: 44, y2: 44, stroke: '#2C3547', 'stroke-width': 2 }, sv2);
        [0, 0.35, 0.7].forEach(function (t) { txt(sv2, x(t), 70, fmt(t, t === 0 ? 0 : 2), { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 14, 'class': 'tnum' }); });
        var parts = [];
        if (c.band) parts.push(svgEl('rect', { x: x(c.band[0]) - 3, y: 32, width: x(c.band[1]) - x(c.band[0]) + 6, height: 24, rx: 5, fill: c.bandCol, opacity: 0.45 }, sv2));
        (c.ticks || []).forEach(function (t) { parts.push(svgEl('line', { x1: x(t[0]), x2: x(t[0]), y1: 30, y2: 58, stroke: t[1], 'stroke-width': 4, 'stroke-linecap': 'round' }, sv2)); });
        var dot = svgEl('circle', { cx: x(c.cpr), cy: 44, r: 10, fill: C.cpr, stroke: C.bg, 'stroke-width': 2.5 }, sv2);
        var cross = txt(sv2, x(c.cpr) + 16, 26, '밖', { 'text-anchor': 'start', fill: C.hi, 'font-size': 16, 'font-weight': 800 });
        if (j === 2) cross.textContent = '아래';
        gsap.set(cell, { autoAlpha: 0 }); gsap.set([dot, cross].concat(parts), { autoAlpha: 0 });
        return { el: cell, dot: dot, parts: parts, cross: cross, x: x, c: c };
      });
      g.ca = ['#ca1', '#ca2', '#ca3'].map(function (s) { return q(el, s); });
      g.m = ['#m1', '#m2', '#m3'].map(function (s) { return q(el, s); });
      g.verd = q(el, '#verd'); g.reTag = q(el, '#reTag'); g.reTx = q(el, '#reTx'); g.gl = q(el, '#gl');
      g.stamp = Comp.stamp(ctx, q(el, '#stampHost'), { ok: false, text: '규칙 A 미충족 ✕' });
      gsap.set([g.verd, g.gl, g.reTag, g.reTx], { autoAlpha: 0 });
      gsap.set(g.m, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      tl.fromTo(g.ca, { autoAlpha: 0, x: -30 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.5), ease: E.out, stagger: 0.12 }, 0.3);
      tl.fromTo(q(el, '#ax2'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 0.5);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      function verdict(k, ok, at) {
        tl.call(function () { g.m[k].className = 's9-mark ' + (ok ? 'ok' : 'no'); g.m[k].textContent = ok ? '✓' : '✕'; }, null, at);
        popIn(tl, g.m[k], at, 0.35);
        tl.to(g.ca[k], { borderColor: ok ? '#A3ADBF' : 'rgba(255,107,138,.7)', duration: 0.3 }, at);
      }
      function rowGrow(k, at) {
        var R = g.rows[k];
        tl.add(R.B.grow(ctx, { duration: 0.8 }), at);
        tl.set(R.vt, { autoAlpha: 1 }, at + 0.1);
        tl.add(ctx.count(R.est, 0, R.d.est, { decimals: 3, final: estOf(A2.rows[k].v), format: function (v) { return sfmt(v, 3); }, duration: 0.8 }), at + 0.1);
      }
      if (i === 1) { rowGrow(0, 0.1); verdict(0, true, 1.0); }
      if (i === 2) { rowGrow(1, 0.1); verdict(1, false, 1.0); }
      if (i === 3) {
        g.cells.forEach(function (c, j) {
          var at = 0.1 + j * 0.45;
          tl.fromTo(c.el, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.4), ease: E.out }, at);
          tl.fromTo(c.parts, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, at + 0.2);
          tl.fromTo(c.dot, { autoAlpha: 0, attr: { cx: c.x(0) } }, { autoAlpha: 1, attr: { cx: c.x(c.c.cpr) }, duration: dur(ctx, 0.6), ease: E.out }, at + 0.3);
          tl.fromTo(c.cross, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, at + 0.8);
        });
        verdict(2, false, 1.6);
      }
      if (i === 4) {
        tl.set(g.verd, { autoAlpha: 1 }, 0);
        tl.add(g.stamp.slam(), 0.05);
        tl.fromTo(g.reTag, { autoAlpha: 0, x: -40 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.45), ease: E.out }, 0.55);
        tl.fromTo(g.reTx, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.8);
      }
      if (i === 5) {
        g.rows.forEach(function (R, k) { R.G.showNow(); gsap.set(R.G.g, { autoAlpha: 0 }); popIn(tl, R.G.g, 0.1 + k * 0.15, 0.35); });
        fadeUp(tl, g.gl, 0.4, 0.5);
      }
    }
  };

  /* ================================================================ s09-03 rule B */
  var B3 = { x0: 620, x1: 1470, d: [-0.11, 0.13], vX: 1500, rows: [
    { y: 276, k: 'F1 · 새 허락 쌍', ds: '스펜더 18,152개 · 구간이 0보다 위(우월성)', v: '+0.110 [0.098, 0.122]', g: '+0.101 [0.092, 0.111]', ok: true },
    { y: 404, k: 'F2 · 새 송금자', ds: '스펜더 · 아래 끝 > −0.01(비열등성)', v: '−0.028 [−0.033, −0.023]', g: '−0.025 [−0.029, −0.021]', ok: false },
    { y: 532, k: 'F3 · 청산 없이 닫은 비율', ds: '계약 트레이더 70개 · 아래 끝 > −0.01', v: '+0.000 [−0.014, 0.010]', g: '−0.044 [−0.100, −0.002]', ok: false }
  ] };
  var slide3 = {
    id: 's09-03', title: '규칙 B (W1, 추출 전에 등록)', time: 50, steps: 5,
    tags: function (s) { return s >= 5 ? ['registered', 'reanalysis', 'registered-analysis'] : s >= 4 ? ['registered', 'reanalysis'] : ['registered']; },
    notes: [
      '규칙 B는 W0 결과를 본 뒤, W1 기록을 꺼내기 전에 등록한 규칙이에요. C-PR이 송금 층만 걷는 것을 개선했다고 말하려면 세 가지가 모두 맞아야 해요. 세 줄 모두 C-PR에서 송금 층만 걷기를 짝지어 뺀 값이에요. 장미색 빗금이 허용 폭 0.01이에요.',
      '새 허락 쌍에서는 분명히 나았어요. 0.110이고 구간이 0보다 훨씬 위예요. W0에서 본 이득이 새 기간에서도 다시 나타난 거예요.',
      '새 송금자에서는 −0.028로, 허용 폭 0.01보다 더 많이 뒤졌어요. 구간 전체가 빗금보다 왼쪽이에요.',
      '트레이더의 청산 없이 닫은 비율에서는 두 점수가 똑같았어요. 가운데 값이 0이에요. 그런데 구간의 아래 끝을 크게 늘려 보면 −0.014로, 허용 폭 −0.010을 0.004만큼 넘었어요. 아슬아슬하게 미충족이에요.',
      '그래서 규칙 B도 미충족이에요. 이 역시 수정 점수에 등록 규칙을 적용한 재분석이에요.',
      '허용 폭 0.01은 등록 분석 W0의 같은 비교 구간의 반폭 0.0040을 두 자리로 올린 값이에요. 비교 대상을 AWP로 바꾼 민감도 분석에서도 F2는 −0.067로 미충족이었고, F3에서 두 점수는 모두 0.350이었어요. 처음 등록한 분석에서도 규칙 B는 미충족이었어요.'
    ],
    html:
      '<h1 class="t-h1">규칙 B: C-PR이 송금 층만 걷기를 [[개선]]할까?</h1>' +
      '<p class="abs s9-fx" style="left:96px;top:160px;width:1728px">세 줄 모두 $\\Delta\\tau=\\tau_{\\mathrm{CPR}}-\\tau_{\\lambda=0}$ · F1 우월성: 95% 구간 &gt; 0 · F2·F3 비열등성: 아래 끝 &gt; $-\\delta$, $\\delta=0.01$ · 셋 다 맞아야 해요</p>' +
      B3.rows.map(function (r, k) { return '<div class="s9-fl" data-r="' + k + '" data-in="none" style="top:' + (r.y - 34) + 'px"><div class="hd">' + r.k + '</div><div class="ds">' + r.ds + '</div></div>'; }).join('') +
      '<svg class="abs" id="ax3" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible"></svg>' +
      '<div class="s9-inset" id="ins" data-in="none"><div class="hd">F3 아래 끝 · 10배 확대</div><svg id="inssv" width="644" height="200" viewBox="0 0 644 200"></svg></div>' +
      '<div class="abs s9-verd" id="verd" data-in="none" style="left:96px;top:676px"><span id="stampHost"></span><span id="reTag">' + pill('reanalysis') + '</span></div>' +
      '<div class="abs s9-tiny" id="sm" data-in="none" style="left:96px;top:770px;width:1060px">' +
        '<div>허용 폭 0.01 = 등록 분석 W0의 같은 비교 구간 반폭(<b>0.0040</b>)을 두 자리로 올린 값</div>' +
        '<div>AWP와 비교하면(민감도 분석) F2 <b>−0.067 [−0.072, −0.061]</b> · 미충족</div>' +
        '<div>F3: 두 점수 모두 <b>0.350 [0.236, 0.461]</b></div>' +
        '<div style="margin-top:6px">' + pill('registered-analysis') + '등록 분석에서도 미충족: F1 <b>+0.101</b> · F2 <b>−0.025</b> · F3 <b>−0.044</b> (회색 빈 점)</div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var sv = q(el, '#ax3'), X = lin(B3.d[0], B3.d[1], B3.x0, B3.x1);
      g.X = X;
      /* margin band [−δ, 0] (hatched rose) */
      var defs = svgEl('defs', {}, sv), pat = svgEl('pattern', { id: 's9-hatch', width: 10, height: 10, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, defs);
      svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 10, stroke: C.hi, 'stroke-width': 3, 'stroke-opacity': 0.45 }, pat);
      g.band = svgEl('rect', { x: X(-0.01), y: 232, width: X(0) - X(-0.01), height: 352, fill: 'url(#s9-hatch)' }, sv);
      g.bandL = svgEl('line', { x1: X(-0.01), x2: X(-0.01), y1: 228, y2: 584, stroke: C.hi, 'stroke-width': 2 }, sv);
      g.bandT = txt(sv, X(-0.01) - 8, 226, '−δ = −0.01', { 'text-anchor': 'end', fill: C.hi, 'font-size': 18, 'font-weight': 700 });
      axis(sv, { scale: X, domain: B3.d, ticks: [-0.1, -0.05, 0, 0.05, 0.1], y0: 232, y1: 584, signed: true });
      g.rows = B3.rows.map(function (r) {
        var d = iv(r.v), gd = iv(r.g);
        var B = ivBar(sv, { scale: X, y: r.y, est: d.est, lo: d.lo, hi: d.hi, color: C.cpr, width: 7, r: 12 });
        var G = ivBar(sv, { scale: X, y: r.y + 24, est: gd.est, lo: gd.lo, hi: gd.hi, color: C.ink3, hollow: true, width: 3, r: 7, from: gd.est, opacity: 0.85 });
        var vt = svgEl('text', { x: B3.vX, y: r.y + 8, 'font-size': 24, 'class': 'tnum' }, sv);
        var e1 = svgEl('tspan', { fill: C.ink, 'font-weight': 800 }, vt); e1.textContent = estOf(r.v);
        var e2 = svgEl('tspan', { fill: C.ink3, 'font-size': 19, dx: 8 }, vt); e2.textContent = ciOf(r.v);
        var mk = svgEl('g', { transform: 'translate(1792,' + r.y + ')' }, sv), mki = svgEl('g', {}, mk);
        svgEl('circle', { r: 22, fill: 'none', stroke: r.ok ? C.ink : C.hi, 'stroke-width': 2.5 }, mki);
        txt(mki, 0, 10, r.ok ? '✓' : '✕', { 'text-anchor': 'middle', fill: r.ok ? C.ink : C.hi, 'font-size': 26, 'font-weight': 900 });
        gsap.set([vt, mki], { autoAlpha: 0 });
        return { B: B, G: G, vt: vt, est: e1, d: d, mk: mki };
      });
      g.fl = qa(el, '.s9-fl');
      /* ×10 inset around the F3 lower end: domain [−0.022, 0.004] */
      var ins = q(el, '#inssv'), Z = lin(-0.022, 0.004, 40, 604);
      g.Z = Z;
      svgEl('rect', { x: Z(-0.01), y: 46, width: Z(0) - Z(-0.01), height: 100, fill: 'url(#s9-hatch)' }, ins);
      svgEl('line', { x1: Z(-0.01), x2: Z(-0.01), y1: 42, y2: 150, stroke: C.hi, 'stroke-width': 2.5 }, ins);
      svgEl('line', { x1: Z(0), x2: Z(0), y1: 42, y2: 150, stroke: C.ink2, 'stroke-width': 1.6, 'stroke-dasharray': '5 6' }, ins);
      svgEl('line', { x1: Z(-0.022), x2: Z(0.004), y1: 150, y2: 150, stroke: C.line, 'stroke-width': 1.5 }, ins);
      [-0.02, -0.015, -0.01, -0.005, 0].forEach(function (t) { txt(ins, Z(t), 174, t === 0 ? '0' : mfmt(t, 3), { 'text-anchor': 'middle', fill: C.ink3, 'font-size': 16, 'class': 'tnum' }); });
      g.zbar = svgEl('line', { x1: Z(-0.014), x2: Z(0.004) + 20, y1: 96, y2: 96, stroke: C.cpr, 'stroke-width': 9, 'stroke-linecap': 'round' }, ins);
      g.zend = svgEl('circle', { cx: Z(-0.014), cy: 96, r: 7, fill: C.cpr, stroke: C.bg, 'stroke-width': 2 }, ins);
      g.zgapL = svgEl('path', { d: 'M' + Z(-0.014) + ',70 L' + Z(-0.014) + ',62 L' + Z(-0.01) + ',62 L' + Z(-0.01) + ',70', fill: 'none', stroke: C.ink, 'stroke-width': 2 }, ins);
      g.zgapT = txt(ins, (Z(-0.014) + Z(-0.01)) / 2, 54, '0.004', { 'text-anchor': 'middle', fill: C.ink, 'font-size': 20, 'font-weight': 800, 'class': 'tnum' });
      g.zlab = txt(ins, Z(-0.014), 128, '아래 끝 −0.014', { 'text-anchor': 'middle', fill: C.cpr, 'font-size': 18, 'font-weight': 700, 'class': 'tnum' });
      g.zv = txt(ins, 604, 54, '아슬아슬하게 미충족', { 'text-anchor': 'end', fill: C.hi, 'font-size': 20, 'font-weight': 800 });
      gsap.set([g.zgapL, g.zgapT, g.zv], { autoAlpha: 0 });
      g.ins = q(el, '#ins'); g.verd = q(el, '#verd'); g.reTag = q(el, '#reTag'); g.sm = q(el, '#sm');
      g.stamp = Comp.stamp(ctx, q(el, '#stampHost'), { ok: false, text: '규칙 B 미충족 ✕' });
      gsap.set([g.ins, g.verd, g.reTag, g.sm], { autoAlpha: 0 });
      gsap.set(g.fl, { autoAlpha: 0.35 });
    },
    enter: function (el, ctx) {
      var tl = ctx.tl();
      tl.fromTo(q(el, '#ax3'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 0.4);
      tl.fromTo(ctx.g.fl, { autoAlpha: 0, x: -24 }, { autoAlpha: 0.35, x: 0, duration: dur(ctx, 0.5), ease: E.out, stagger: 0.1 }, 0.3);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      function row(k, at, d) {
        var R = g.rows[k];
        tl.to(g.fl[k], { autoAlpha: 1, duration: 0.3 }, at);
        tl.add(R.B.grow(ctx, { duration: d || 0.8 }), at + 0.05);
        tl.set(R.vt, { autoAlpha: 1 }, at + 0.1);
        tl.add(ctx.count(R.est, 0, R.d.est, { decimals: 3, final: estOf(B3.rows[k].v), format: function (v) { return sfmt(v, 3); }, duration: d || 0.8 }), at + 0.1);
        popIn(tl, R.mk, at + (d || 0.8) + 0.1, 0.35);
      }
      if (i === 1) row(0, 0.05);
      if (i === 2) row(1, 0.05);
      if (i === 3) {
        row(2, 0.05, 0.8);
        /* lens from the lower end of F3 into the inset */
        var ov = ctx.overlay(), xa = g.X(-0.022), xb = g.X(0.004), yr = B3.rows[2].y;
        var mag = svgEl('rect', { x: xa, y: yr - 22, width: xb - xa, height: 44, rx: 8, fill: 'none', stroke: C.ink2, 'stroke-width': 1.6, 'stroke-dasharray': '5 5' }, ov);
        var lp = svgEl('path', { d: 'M' + xa + ',' + (yr + 22) + ' L' + xa + ',640 Q' + xa + ',760 1180,760', fill: 'none', stroke: C.ink2, 'stroke-width': 1.6, 'stroke-dasharray': '5 5' }, ov);
        var LL = lp.getTotalLength ? lp.getTotalLength() : 600;
        gsap.set([mag, lp], { autoAlpha: 0 });
        tl.fromTo(mag, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 1.0);
        tl.fromTo(lp, { autoAlpha: 1, strokeDasharray: LL + ' ' + LL, strokeDashoffset: LL }, { strokeDashoffset: 0, duration: dur(ctx, 0.5), ease: E.io, onComplete: function () { lp.style.strokeDasharray = '5 5'; lp.style.strokeDashoffset = '0'; } }, 1.2);
        tl.fromTo(g.ins, { autoAlpha: 0, scale: 0.3, transformOrigin: '20% 0%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.9), ease: E.io }, 1.4);
        tl.fromTo(g.zbar, { attr: { x1: g.Z(0.004) + 20 } }, { attr: { x1: g.Z(-0.014) }, duration: dur(ctx, 0.7), ease: E.out }, 2.1);
        tl.fromTo(g.zend, { attr: { cx: g.Z(0.004) + 20 } }, { attr: { cx: g.Z(-0.014) }, duration: dur(ctx, 0.7), ease: E.out }, 2.1);
        tl.fromTo([g.zgapL, g.zgapT], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 2.8);
        tl.fromTo(g.zv, { autoAlpha: 0, x: 10 }, { autoAlpha: 1, x: 0, duration: 0.4 }, 3.1);
      }
      if (i === 4) {
        tl.set(g.verd, { autoAlpha: 1 }, 0);
        tl.add(g.stamp.slam(), 0.05);
        tl.fromTo(g.reTag, { autoAlpha: 0, x: -40 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.45), ease: E.out }, 0.55);
      }
      if (i === 5) {
        g.rows.forEach(function (R, k) { R.G.showNow(); gsap.set(R.G.g, { autoAlpha: 0 }); popIn(tl, R.G.g, 0.1 + k * 0.12, 0.35); });
        fadeUp(tl, g.sm, 0.3, 0.5);
      }
    }
  };

  /* ================================================================ s09-04 registered vs revised */
  var TR4 = [
    ['매칭 코호트(계약)', '27,844', '15,107'],
    ['W0 스펜더 코호트', '33,101', '17,050'],
    ['W1 스펜더 코호트', '34,587', '18,152'],
    ['엔도스랭크 vs AWP τ', '0.217', '0.174'],
    ['규칙 A', '미충족', '미충족', 1],
    ['규칙 B', '미충족', '미충족', 1],
    ['R1 (개수 수준 우위)', '미충족', '미충족', 1],
    ['R2 (페이지랭크 수준 우위)', '미충족', '미충족', 1],
    ['R3 (특정성)', '해당', '해당', 1]
  ];
  var ICO4 = {
    flat: '<svg width="88" height="70" viewBox="0 0 88 70" fill="none"><path d="M8 62H84M8 62V6" stroke="#677083" stroke-width="2"/><path d="M8 62 C10 20 12 14 18 12 L84 12" stroke="#F5B43C" stroke-width="3"/><text x="70" y="30" fill="#A3ADBF" font-size="13" font-family="sans-serif">1</text><path d="M8 12h76" stroke="#677083" stroke-width="1" stroke-dasharray="3 3"/></svg>',
    ladder: '<svg width="88" height="70" viewBox="0 0 88 70" fill="none"><rect x="10" y="50" width="22" height="12" rx="2" fill="#3CC4FF" opacity=".8"/><rect x="50" y="8" width="22" height="54" rx="2" fill="#A3ADBF" opacity=".8"/><text x="21" y="44" text-anchor="middle" fill="#A3ADBF" font-size="13" font-family="sans-serif">10⁶</text><text x="44" y="16" text-anchor="end" fill="#A3ADBF" font-size="13" font-family="sans-serif">10¹⁸</text><path d="M4 62H84" stroke="#677083" stroke-width="2"/></svg>',
    spam: '<svg width="88" height="70" viewBox="0 0 88 70" fill="none"><rect x="6" y="10" width="54" height="40" rx="6" stroke="#A3ADBF" stroke-width="2"/><path d="M14 22h36M14 30h28M14 38h32" stroke="#677083" stroke-width="2"/><circle cx="66" cy="50" r="14" fill="#10151F" stroke="#FF6B8A" stroke-width="2.5"/><path d="M60 44l12 12M72 44L60 56" stroke="#FF6B8A" stroke-width="2.5" stroke-linecap="round"/></svg>'
  };
  var slide4 = {
    id: 's09-04', title: '등록 분석과 수정 분석', time: 50, steps: 4,
    tags: ['registered-analysis', 'reanalysis'],
    notes: [
      '그래서 이 논문에는 분석이 두 개 있어요.',
      '등록 분석은 미리 정한 그대로, 토큰의 원래 단위와 모든 토큰을 쓴 분석이에요. 수정 분석은 등록 결과를 본 뒤에 금액을 달러로, 토큰을 다섯 개로 고친 분석이고, 논문 본문의 결과는 이쪽이에요.',
      '고친 이유는 세 가지였어요. 원래 단위에서는 금액 무게가 거의 다 1이었어요. 결합 점수는 USDC 1개가 10의 6제곱 단위, WETH 1개가 10의 18제곱 단위인데도 그냥 더했고, 무제한 허락이 줄을 통째로 차지했어요. 그리고 스팸 토큰은 아무 주소의 이름으로나 기록을 남길 수 있었어요.',
      '중요한 것은 두 분석의 판정이 모두 같았다는 점이에요. 코호트의 크기는 거의 절반으로 줄었지만, 규칙 A, 규칙 B, R1부터 R3까지 판정은 하나도 바뀌지 않았어요.',
      '그래도 수정 분석의 판정은 재분석이지 등록 시험이 아니라는 점은 분명히 해 둘게요.'
    ],
    html:
      '<h1 class="t-h1">두 분석, [[같은 판정]]</h1>' +
      '<p class="abs s9-line" id="rhd" data-in="none" style="left:96px;top:196px;color:var(--ink);font-weight:700">고친 이유 셋 <span class="s9-tiny">(등록 결과를 본 뒤 알게 됨)</span></p>' +
      '<div class="s9-rs" id="r1" data-in="none" style="top:244px">' + ICO4.flat + '<div class="t">① 원래 단위에서는 거의 모든 금액의 무게가 1 → 금액이 역할을 못 했어요<small>등록 분석: 허락 99.78% · 송금 99.52%가 10단위 이상 → 무게 ≈ 1</small></div></div>' +
      '<div class="s9-rs" id="r2" data-in="none" style="top:404px">' + ICO4.ladder + '<div class="t">② C-PR이 단위가 12자리 다른 토큰을 그냥 더했고, 무제한 허락이 줄을 통째로 차지했어요<small>USDC 1개 = 10⁶ 단위 · WETH 1개 = 10¹⁸ 단위 · 무제한 = 2²⁵⁶ − 1</small></div></div>' +
      '<div class="s9-rs" id="r3" data-in="none" style="top:552px">' + ICO4.spam + '<div class="t">③ 아무 토큰이나 다른 주소 이름으로 기록을 남길 수 있었어요<small>스팸 토큰의 기록은 그 주인이 허락했다는 증거가 아니에요</small></div></div>' +
      '<div class="s9-th" id="th1" data-in="none" style="left:1180px;width:280px;text-align:right"><div class="nm" style="color:var(--ink-3)">등록 분석</div><div class="ds">미리 정한 그대로 · 원래 단위 · 모든 토큰 · b = 1</div></div>' +
      '<div class="s9-th" id="th2" data-in="none" style="left:1550px;width:274px"><div class="nm">수정 분석</div><div class="ds">등록 결과를 본 뒤 정함 · 달러 · 다섯 토큰 · b = ln 3 / m · 상한 U</div></div>' +
      TR4.map(function (r, k) {
        return '<div class="s9-tr' + (r[3] ? ' vd' : '') + '" data-r="' + k + '" data-in="none" style="top:' + (330 + k * 48) + 'px"><span class="l">' + r[0] + '</span><span class="a">' + r[1] + '</span><span class="eq">' + (r[3] ? '=' : '→') + '</span><span class="b">' + r[2] + '</span></div>';
      }).join('') +
      '<p class="abs s9-bold" id="bold" data-in="none" style="left:96px;top:810px;width:1728px">논문 본문 = 수정 분석 · 수정 분석의 판정은 재분석이에요 — 등록 시험이 아니에요</p>' +
      '<p class="abs s9-tiny" id="bsrc" data-in="none" style="left:96px;top:860px;width:1728px">두 분석은 같은 규칙과 같은 기준값을 썼어요 · 등록 분석의 결과는 그대로 공개해 두었어요</p>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.rs = ['#r1', '#r2', '#r3'].map(function (s) { return q(el, s); });
      g.rhd = q(el, '#rhd'); g.th = [q(el, '#th1'), q(el, '#th2')]; g.tr = qa(el, '.s9-tr'); g.bold = q(el, '#bold'); g.bsrc = q(el, '#bsrc');
      g.eq = g.tr.map(function (r) { return q(r, '.eq'); });
      gsap.set([g.rhd, g.bold, g.bsrc].concat(g.rs, g.th, g.tr), { autoAlpha: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(g.th, { autoAlpha: 0, y: -14 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.5), ease: E.out, stagger: 0.2 }, 0);
      }
      if (i === 2) {
        fadeUp(tl, g.rhd, 0, 0.4);
        g.rs.forEach(function (r, k) {
          var at = 0.2 + k * 0.5;
          tl.fromTo(r, { autoAlpha: 0, x: -40 }, { autoAlpha: 1, x: 0, duration: dur(ctx, 0.55), ease: E.out }, at);
          tl.fromTo(q(r, 'svg'), { scale: 0.6, transformOrigin: '50% 50%' }, { scale: 1, duration: dur(ctx, 0.45), ease: E.stamp }, at + 0.15);
        });
      }
      if (i === 3) {
        g.tr.forEach(function (r, k) {
          var at = k * 0.08;
          tl.fromTo(r, { autoAlpha: 0, y: -10 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.35), ease: E.out }, at);
          if (TR4[k][3]) popIn(tl, g.eq[k], 0.9 + (k - 4) * 0.15, 0.35);
        });
      }
      if (i === 4) fadeUp(tl, [g.bold, g.bsrc], 0, 0.5, 0.15);
    }
  };

  /* ================================================================ s09-05 R1–R3 on trader outcomes */
  var P5 = { x0: 1150, x1: 1560, d: [-0.45, 0.4], vX: 1586 };
  var ROW5 = {
    P: { y: 436, w0y: 474, k: 'P = 받은 허락 수 − 송금 입차수', s: 'W1 · 개수 수준', v: '+0.084 [−0.013, 0.176]', outer: [-0.026, 0.188], vt: '+0.084', vo: '97.5% [−0.026, 0.188]',
         w0: { est: 0.182, lo: 0.052, hi: 0.314, outer: [0.032, 0.338], t: 'W0 +0.182 [0.032, 0.338]' } },
    Q: { y: 588, w0y: 626, k: 'Q = 엔도스랭크(활동 재시작) − AWP', s: 'W1 · 페이지랭크 수준', v: '−0.041 [−0.135, 0.050]', outer: [-0.148, 0.064], vt: '−0.041', vo: '97.5% [−0.148, 0.064]',
         w0: { est: -0.014, lo: -0.147, hi: 0.130, outer: [-0.161, 0.151], t: 'W0 −0.014 [−0.161, 0.151]' } }
  };
  var R3ROWS = [
    { y: 744, k: 'P · 이익 낸 닫기 비율', v: '−0.196 [−0.364, −0.046]' },
    { y: 790, k: 'P · 손실 아닌 닫기 비율', v: '−0.252 [−0.391, −0.120]' }
  ];
  var slide5 = {
    id: 's09-05', title: '두 화살표 어디에도 없는 결과: R1–R3', time: 55, steps: 6,
    tags: function (s) { return s >= 6 ? ['registered', 'reanalysis', 'registered-analysis'] : s >= 3 ? ['registered', 'reanalysis'] : ['registered']; },
    notes: [
      '마지막 규칙은 두 화살표 어디에도 담기지 않은 결과에서의 비교예요. GMX V2에서 거래하는 계약 트레이더가 다음 석 달 동안 어떻게 포지션을 닫았는지 봤어요.',
      'W1의 트레이더는 70개예요. 호박색 고리는 동결일까지 허락을 받은 37개이고, 장미색은 석 달 동안 한 번이라도 청산된 9개예요.',
      '결과는 청산 없이 닫은 비율이에요. 1에서 청산으로 끝난 닫기의 비율을 뺀 값이라서, 많이 거래한다고 저절로 높아지지 않아요.',
      '허락한 주인 수에서 송금 입차수를 뺀 차이 P는 0.084였지만, 97.5% 구간이 0을 품어요. 그래서 미리 등록한 문장 그대로, 개수 수준에서 허락이 송금보다 앞선다는 증거는 없다는 결론이 나와요.',
      '페이지랭크끼리의 비교 Q도 −0.041로 구간이 0을 품어서 가려지지 않았어요.',
      'R3은 해당해요. 이익을 낸 비율이나 손실이 아닌 비율에서는 허락 쪽이 오히려 낮았어요. 그러니 신호가 있다면 그것은 강제 청산을 피하는 것에 관한 것이지 거래 실력이 아니에요.',
      '허락을 받은 트레이더가 두 기간 모두 한 번도 청산되지 않은 것은 눈에 띄지만, 표본이 70개와 88개뿐이고 송금 쪽 수도 이 결과를 0.310으로 꽤 맞혀서, 여기서 더 말할 수는 없어요. 이 판정들도 재분석이고, 처음 등록한 분석에서도 같았어요.'
    ],
    html:
      '<h1 class="t-h1">청산에서는 허락 쪽이 [[앞선다는 증거가 없어요]]</h1>' +
      '<p class="abs s9-line" id="wcap" data-in="none" style="left:96px;top:192px;width:620px">GMX V2에서 거래하는 계약 트레이더 · W1 <b>70</b>개 (W0 <b>88</b>개)</p>' +
      '<svg class="abs" id="wf5" data-in="none" width="620" height="400" viewBox="0 0 620 400" style="left:96px;top:240px;overflow:visible"></svg>' +
      '<div class="abs s9-wl" id="wleg" data-in="none" style="left:96px;top:640px;width:640px">' +
        '<div><i style="background:#E9EDF5;box-shadow:0 0 0 3px #F5B43C"></i>허락을 받은 트레이더 <b class="ink">37</b> · 모두 청산 없음</div>' +
        '<div><i style="background:#E9EDF5"></i>나머지 33 · 청산 없음 <b class="ink">24</b> <i style="background:#FF6B8A;margin-left:14px"></i>청산 있음 <b class="ink">9</b></div></div>' +
      '<div class="s9-def" id="def" data-in="none"><span class="k">결과 · 청산 없이 닫은 비율</span><span>$=1-\\dfrac{\\text{청산으로 끝난 닫기 수}}{\\text{모든 닫기 수}}$</span><span class="s9-tiny">거래를 많이 해도 저절로 높아지지 않아요</span></div>' +
      '<svg class="abs" id="ax5" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible"></svg>' +
      '<div class="abs s9-rule" id="r1t" data-in="none" style="left:760px;top:494px"><span class="s9-v no">R1 미충족</span> <span class="typed" id="r1s"></span></div>' +
      '<div class="abs s9-rule" id="r2t" data-in="none" style="left:760px;top:646px"><span class="s9-v no">R2 미충족</span> <span class="typed" id="r2s"></span></div>' +
      '<div class="abs s9-rule" id="r3t" data-in="none" style="left:760px;top:868px"><span class="s9-v">R3 해당</span> <span class="typed" id="r3s"></span></div>' +
      '<div class="abs s9-tiny" id="sm5" data-in="none" style="left:96px;top:742px;width:620px">허락을 받은 트레이더는 <b>37개 중 37개</b>(W1), <b>40개 중 40개</b>(W0)가 청산 없음 — 나머지는 <b>72.7%</b>, <b>75.0%</b>. 하지만 표본이 작고, 송금 입차수도 이 결과를 <b>0.310 [0.184, 0.425]</b>로 맞혀요.<div style="margin-top:8px">' + pill('registered-analysis') + '등록 분석에서도 같은 판정이에요</div></div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      /* 70 W1 traders from DECK_DATA.traders (37 recipients, 9 liquidated); fall back to the digest counts */
      var T = ((DATA.traders || {}).w1 || {}).raw || null, list = [];
      if (T && T.in_approve_degree) {
        for (var i = 0; i < T.in_approve_degree.length; i++) list.push({ rec: T.in_approve_degree[i] > 0, liq: !T.no_liquidation[i] });
      } else {
        for (var a = 0; a < 70; a++) list.push({ rec: a < 37, liq: a >= 61 });
      }
      list.sort(function (x, y) { return (y.rec - x.rec) || (x.liq - y.liq); });
      var sv = q(el, '#wf5');
      g.dots = list.map(function (t, k) {
        var cx = 30 + (k % 10) * 58, cy = 30 + Math.floor(k / 10) * 56;
        var gg = svgEl('g', {}, sv);
        var c = svgEl('circle', { cx: cx, cy: cy, r: 17, fill: '#3A4458' }, gg);
        var ring = t.rec ? svgEl('circle', { cx: cx, cy: cy, r: 22, fill: 'none', stroke: C.allow, 'stroke-width': 3.5 }, gg) : null;
        gsap.set(gg, { autoAlpha: 0 }); if (ring) gsap.set(ring, { autoAlpha: 0 });
        return { g: gg, c: c, ring: ring, t: t, cx: cx, cy: cy };
      });
      /* axes for P, Q and R3 */
      var ax = q(el, '#ax5'), X = lin(P5.d[0], P5.d[1], P5.x0, P5.x1);
      g.X = X;
      txt(ax, P5.x0, 340, '짝지은 차이 Δτ · 95% 막대, 97.5% 괄호 (본페로니)', { fill: C.ink2, 'font-size': 20, 'font-weight': 700 });
      txt(ax, X(0) - 8, 364, '← 송금 쪽이 나음', { 'text-anchor': 'end', fill: C.ink3, 'font-size': 16 });
      txt(ax, X(0) + 8, 364, '허락 쪽이 나음 →', { 'text-anchor': 'start', fill: C.ink3, 'font-size': 16 });
      g.axis = axis(ax, { scale: X, domain: P5.d, ticks: [-0.4, -0.2, 0, 0.2, 0.4], y0: 376, y1: 812, signed: true, dec: 1 });
      g.rows = {};
      ['P', 'Q'].forEach(function (k) {
        var R = ROW5[k], d = iv(R.v), gl = svgEl('g', {}, ax);
        txt(gl, 760, R.y - 2, R.k, { fill: C.ink, 'font-size': 23, 'font-weight': 700 });
        txt(gl, 760, R.y + 24, R.s, { fill: C.ink3, 'font-size': 17 });
        var B = ivBar(ax, { scale: X, y: R.y, est: d.est, lo: d.lo, hi: d.hi, outer: R.outer, color: C.ink, width: 7, r: 12 });
        var W = ivBar(ax, { scale: X, y: R.w0y, est: R.w0.est, lo: R.w0.lo, hi: R.w0.hi, outer: R.w0.outer, color: C.ink2, width: 3, r: 6, opacity: 0.8 });
        var vt = svgEl('text', { x: P5.vX, y: R.y + 2, 'font-size': 24, 'class': 'tnum' }, ax);
        var e1 = svgEl('tspan', { fill: C.ink, 'font-weight': 800 }, vt); e1.textContent = R.vt;
        var vt2 = txt(ax, P5.vX, R.y + 26, R.vo, { fill: C.ink3, 'font-size': 17, 'class': 'tnum' });
        var w0t = txt(ax, P5.vX, R.w0y + 6, R.w0.t, { fill: C.ink3, 'font-size': 16, 'class': 'tnum' });
        gsap.set([gl, vt, vt2, w0t], { autoAlpha: 0 });
        g.rows[k] = { gl: gl, B: B, W: W, vt: vt, vt2: vt2, w0t: w0t, est: e1, d: d };
      });
      g.r3 = R3ROWS.map(function (r) {
        var d = iv(r.v), gl = svgEl('g', {}, ax);
        txt(gl, 760, r.y + 7, r.k, { fill: C.ink2, 'font-size': 20, 'font-weight': 600 });
        var B = ivBar(ax, { scale: X, y: r.y, est: d.est, lo: d.lo, hi: d.hi, color: C.ink2, width: 5, r: 9 });
        var vt = txt(ax, P5.vX, r.y + 7, r.v, { fill: C.ink2, 'font-size': 19, 'class': 'tnum' });
        gsap.set([gl, vt], { autoAlpha: 0 });
        return { gl: gl, B: B, vt: vt };
      });
      g.wcap = q(el, '#wcap'); g.wleg = q(el, '#wleg'); g.def = q(el, '#def'); g.sm = q(el, '#sm5');
      g.r1t = q(el, '#r1t'); g.r2t = q(el, '#r2t'); g.r3t = q(el, '#r3t');
      g.r1s = q(el, '#r1s'); g.r2s = q(el, '#r2s'); g.r3s = q(el, '#r3s');
      gsap.set([g.wleg, g.def, g.sm, g.r1t, g.r2t, g.r3t, ax], { autoAlpha: 0 });
      g.ax = ax;
    },
    enter: function (el, ctx) {
      var tl = ctx.tl();
      tl.fromTo(ctx.g.wcap, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0.3);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        g.dots.forEach(function (D, k) {
          var at = 0.05 + k * 0.022;
          tl.fromTo(D.g, { autoAlpha: 0, scale: 0.2, svgOrigin: D.cx + ' ' + D.cy }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.3), ease: E.stamp }, at);
        });
        g.dots.forEach(function (D, k) {
          var at = 1.8 + k * 0.012;
          if (D.ring) tl.fromTo(D.ring, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.25 }, at);
          tl.to(D.c, { attr: { fill: D.t.liq ? C.hi : C.ink }, duration: 0.3 }, D.t.liq ? 2.8 + k * 0.02 : at);
        });
        fadeUp(tl, g.wleg, 2.4, 0.5);
      }
      if (i === 2) {
        tl.fromTo(g.def, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: dur(ctx, 0.5), ease: E.out }, 0);
      }
      if (i === 3) {
        tl.fromTo(g.ax, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0);
        var R = g.rows.P;
        tl.fromTo(R.gl, { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.35 }, 0.2);
        tl.add(R.B.grow(ctx, { duration: 0.8 }), 0.3);
        tl.set([R.vt, R.vt2], { autoAlpha: 1 }, 0.35);
        tl.add(ctx.count(R.est, 0, R.d.est, { decimals: 3, final: ROW5.P.vt, format: function (v) { return sfmt(v, 3); }, duration: 0.8 }), 0.35);
        tl.add(R.W.grow(ctx, { duration: 0.6 }), 1.0);
        tl.set(R.w0t, { autoAlpha: 1 }, 1.2);
        tl.set(g.r1t, { autoAlpha: 1 }, 1.5);
        tl.fromTo(q(g.r1t, '.s9-v'), { autoAlpha: 0, scale: 1.3 }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.35), ease: E.stamp }, 1.5);
        tl.add(typeIn(ctx, g.r1s, '‘개수 수준에서 허락이 송금보다 앞선다는 증거는 없어요’'), 1.8);
      }
      if (i === 4) {
        var Rq = g.rows.Q;
        tl.fromTo(Rq.gl, { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.35 }, 0);
        tl.add(Rq.B.grow(ctx, { duration: 0.8 }), 0.1);
        tl.set([Rq.vt, Rq.vt2], { autoAlpha: 1 }, 0.15);
        tl.add(ctx.count(Rq.est, 0, Rq.d.est, { decimals: 3, final: ROW5.Q.vt, format: function (v) { return sfmt(v, 3); }, duration: 0.8 }), 0.15);
        tl.add(Rq.W.grow(ctx, { duration: 0.6 }), 0.8);
        tl.set(Rq.w0t, { autoAlpha: 1 }, 1.0);
        tl.set(g.r2t, { autoAlpha: 1 }, 1.3);
        tl.fromTo(q(g.r2t, '.s9-v'), { autoAlpha: 0, scale: 1.3 }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.35), ease: E.stamp }, 1.3);
        tl.add(typeIn(ctx, g.r2s, '‘페이지랭크끼리는 가려지지 않아요’'), 1.6);
      }
      if (i === 5) {
        g.r3.forEach(function (R, k) {
          var at = k * 0.3;
          tl.fromTo(R.gl, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, at);
          tl.add(R.B.grow(ctx, { duration: 0.7 }), at + 0.05);
          tl.fromTo(R.vt, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, at + 0.4);
        });
        tl.set(g.r3t, { autoAlpha: 1 }, 0.9);
        tl.fromTo(q(g.r3t, '.s9-v'), { autoAlpha: 0, scale: 1.3 }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.35), ease: E.stamp }, 0.9);
        tl.add(typeIn(ctx, g.r3s, '‘신호가 있다면 강제 청산 피하기에 관한 것이지, 거래 실력이 아니에요’'), 1.2);
      }
      if (i === 6) fadeUp(tl, g.sm, 0.1, 0.5);
    }
  };

  Deck.section({
    id: 's09-rules',
    title: '미리 정한 규칙',
    slides: [slide1, slide2, slide3, slide4, slide5]
  });
})();
