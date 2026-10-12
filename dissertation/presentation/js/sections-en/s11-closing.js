/* =========================================================================
   s11-closing — Conclusion (English edition; STORYBOARD.md §2, s11-01 … s11-05)

   s11-01  Answers to the RQs    five RQ cards; on entry the representative pictures of the talk fly
                                 back in as dim thumbnails (rank scatter of the real 15,107 contracts,
                                 family bars, race bars, interval bars, verdict stamps); each click
                                 brings one card forward with its answer and status; then the
                                 out-of-both-edges line and the five objective chips
   s11-02  Five contributions    bento of five tiles, each with one small motion (G1, G8, closed form,
                                 G13 dial, a waffle of the W1 traders)
   s11-03  Limitations           eight lines with icons, four per click
   s11-04  Wallet window, next   the brandless wallet window of s01-01 opens again (DeckParts.wallet; 46 px
                                 lower than in s01-01 so it clears the title), now with "owner addresses: N"
                                 (owners are addresses, not people); the cursor rests on Approve without
                                 pressing; two lines; four next steps, the first tagged hypothesis
   s11-05  Thank you             the small world as a constellation; the allowance arrow underlines
                                 the thanks; then everything stops for the questions

   Numbers and sources (R = revised digest = the thesis's main analysis)
     τ 0.174 [0.163, 0.185]                    R§3 inter_method.endorserank_vs_awp
     0.585 (EndorseRank × allowance), 0.572 (AWP × transfer)        R§2 families
     2.17, 2.23                                R§10 derived ratios
     W1 contrasts in the RQ4 thumbnail: AWP − transfer in-degree +0.022 [0.017, 0.027],
       EndorseRank − in-approve degree −0.034 [−0.038, −0.029]       R§7 (after the labels)
     objectives O1–O5: thesis Ch. 5, Table objectives-achievement (Outcome column)
     70 / 88 traders (W1 / W0)                 R§7 neutral_w1.n / neutral_w0.n
     "N": a placeholder, no contract is meant; "October–December 2026": thesis Ch. 6, future work
     repository: thesis Ch. 3, Reproducibility
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, E = Deck.E, fmt = Deck.util.fmt, esc = Deck.util.esc;
  var NS = 'http://www.w3.org/2000/svg';
  var DATA = window.DECK_DATA || {};
  var META = DATA.meta || {};

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
  function qa(el, sel) { return Array.prototype.slice.call(el.querySelectorAll(sel)); }
  function plainPill(text) { return '<span class="pill pill-plain">' + esc(text) + '</span>'; }

  /* ------------------------------------------------------------ data */
  var RV = pick(DATA, ['results', 'revised'], {});
  var TAU = pick(RV, ['same_window', 'inter_method', 'endorserank_vs_awp'], [0.1738, 0.1632, 0.1848]);
  var FAM = pick(RV, ['same_window', 'families'], {});
  var F_ER_A = pick(FAM, ['endorserank', 'allowance', 0], 0.5849), F_ER_T = pick(FAM, ['endorserank', 'transfer', 0], 0.1579);
  var F_AWP_T = pick(FAM, ['awp', 'transfer', 0], 0.5723), F_AWP_A = pick(FAM, ['awp', 'allowance', 0], 0.193);
  var BM = pick(DATA, ['benchmark', 'revised', 'main'], {});
  var T_ER = pick(BM, ['endorserank', 'mean_s'], 10.2942), T_AWP = pick(BM, ['awp', 'mean_s'], 22.3674);
  var R_TIME = pick(DATA, ['benchmark', 'revised', 'derived', 'time_ratio_awp_over_er'], 2.1728);
  var R_EDGE = pick(DATA, ['benchmark', 'revised', 'derived', 'edge_ratio_awp_over_er'], 2.2302);
  var W1C_AWP = pick(RV, ['w1', 'endorserank_results', 'awp_minus_degree_send', 'd'], [0.02186, 0.01694, 0.02708]);
  var W1C_ER = pick(RV, ['w1', 'endorserank_results', 'endorserank_minus_degree_appr', 'd'], [-0.03377, -0.03802, -0.02901]);
  var N_W1 = pick(RV, ['w1', 'neutral_w1', 'n'], 70), N_W0 = pick(RV, ['w1', 'neutral_w0', 'n'], 88);

  /* ------------------------------------------------------------ styles */
  var CSS = [
    /* s11-01 */
    '.s11-card{position:absolute;top:186px;width:326px;height:560px;border-radius:20px;background:var(--bg-2);border:1.5px solid var(--line);padding:16px 18px}',
    '.s11-card.on{border-color:#3A4458}',
    '.s11-card .th{position:relative;height:128px;border-radius:12px;background:var(--bg-3);overflow:hidden}',
    '.s11-card .th svg,.s11-card .th canvas{position:absolute;left:0;top:0}',
    '.s11-card .bd{position:absolute;left:18px;right:18px;top:162px;bottom:16px}',
    '.s11-card .rq{display:flex;gap:10px;align-items:flex-start}',
    '.s11-card .rq .k{flex:0 0 auto;height:32px;padding:0 10px;border-radius:9px;background:var(--bg-3);font-family:var(--font-mono);font-size:18px;line-height:32px;color:var(--ink);letter-spacing:0}',
    '.s11-card .rq .qq{font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s11-card .an{margin-top:16px;font-size:30px;line-height:40px;font-weight:800;letter-spacing:-.02em;color:var(--ink)}',
    '.s11-card .sb{margin-top:10px;font-size:22px;line-height:32px;color:var(--ink-2)}',
    '.s11-card .sb b{color:var(--ink);font-weight:700;font-variant-numeric:tabular-nums}',
    '.s11-card .sb .em{color:var(--ink);font-weight:700;background-image:linear-gradient(rgba(233,237,245,.16),rgba(233,237,245,.16));background-repeat:no-repeat;background-size:0% 100%;-webkit-box-decoration-break:clone;box-decoration-break:clone;border-radius:4px;padding:0 3px}',
    '.s11-card .tg{position:absolute;left:0;bottom:0;display:flex;flex-wrap:wrap;gap:8px}',
    '.s11-card .tg .pill{height:30px;font-size:16px}',
    '.s11-oc{position:absolute;top:762px;width:326px;padding:8px 14px;border-radius:14px;border:1.5px solid var(--line);background:rgba(16,21,31,.9);font-size:19px;line-height:26px;color:var(--ink-2)}',
    '.s11-oc b{color:var(--ink);font-weight:800;margin-right:6px}',
    '.s11-oc.part{border-color:var(--ink-3)}',
    '.s11-oc.fail{border-color:var(--ink-2);border-style:dashed}',
    '.s11-brk{position:absolute;top:812px;height:30px;border:1.5px solid var(--ink-3);border-top:none;border-radius:0 0 10px 10px}',
    '.s11-brk span{position:absolute;left:50%;top:14px;transform:translateX(-50%);white-space:nowrap;padding:0 12px;background:var(--bg);font-size:19px;line-height:26px;color:var(--ink-2)}',
    '.s11-add{font-size:24px;line-height:36px;color:var(--ink-2);display:flex;align-items:center;gap:14px}',
    '.s11-add b{color:var(--ink);font-weight:700}',
    /* s11-02 */
    '.s11-tile{position:absolute;border-radius:22px;background:var(--bg-2);border:1.5px solid var(--line);overflow:hidden}',
    '.s11-tile .no{position:absolute;left:24px;top:18px;font-family:var(--font-mono);font-size:20px;line-height:26px;color:var(--ink-3);letter-spacing:0}',
    '.s11-tile .vis{position:absolute;left:0;right:0}',
    '.s11-tile .tx{position:absolute;left:28px;right:28px;bottom:24px;font-size:26px;line-height:36px;font-weight:600;color:var(--ink)}',
    '.s11-tile .tx small{display:block;margin-top:4px;font-size:20px;line-height:28px;font-weight:500;color:var(--ink-2)}',
    '.s11-tile .big{font-size:52px;line-height:60px;font-weight:800;letter-spacing:-.02em}',
    '.s11-tile .fx .katex{font-size:46px}',
    '.s11-note{font-size:26px;line-height:38px;color:var(--ink-2)}',
    '.s11-note b{color:var(--ink);font-weight:700}',
    /* s11-03 */
    '.s11-lim{display:flex;flex-direction:column;gap:14px}',
    '.s11-lim .r{display:flex;align-items:center;gap:24px;min-height:68px}',
    '.s11-lim .ic{flex:0 0 auto;width:64px;height:64px;border-radius:16px;background:var(--bg-2);border:1px solid var(--line);display:flex;align-items:center;justify-content:center}',
    '.s11-lim .ic svg{width:38px;height:38px}',
    '.s11-lim .t{font-size:29px;line-height:40px;color:var(--ink)}',
    '.s11-lim .t span{color:var(--ink-2)}',
    /* s11-04 */
    '.s11-nl{font-family:var(--font-sans);font-size:23px;line-height:26px;color:var(--ink);font-weight:600;letter-spacing:-.01em}',
    '.s11-nl b{font-family:var(--font-mono);font-size:24px;color:var(--ink);padding:0 4px;border-bottom:2px dashed var(--ink-2)}',
    '.s11-ns{position:absolute;left:0;right:0;top:352px;text-align:center;font-size:18px;line-height:24px;color:var(--ink-3)}',
    '.s11-caret{display:inline-block;width:2px;height:22px;margin-left:2px;vertical-align:-3px;background:var(--ink)}',
    '.s11-two{font-size:40px;line-height:58px;font-weight:700;letter-spacing:-.02em}',
    '.s11-two .ne{display:inline-block;margin:0 8px;color:var(--ink);font-weight:800}',
    '.s11-two .ink-2{font-weight:600}',
    '.s11-nx h2{margin-bottom:18px}',
    '.s11-nc{position:relative;display:flex;gap:20px;align-items:flex-start;padding:18px 22px;margin-bottom:14px;border-radius:18px;background:var(--bg-2);border:1.5px solid var(--line)}',
    '.s11-nc .n{flex:0 0 auto;width:40px;height:40px;border-radius:12px;background:var(--bg-3);font-family:var(--font-mono);font-size:20px;line-height:40px;text-align:center;color:var(--ink)}',
    '.s11-nc .t{font-size:26px;line-height:38px;color:var(--ink)}',
    '.s11-nc .t small{display:block;font-size:21px;line-height:30px;color:var(--ink-2)}',
    '.s11-hyp{position:absolute;right:18px;top:-16px}',
    '.s11-nnote{font-size:18px;line-height:26px;color:var(--ink-3)}',
    /* s11-05 */
    '.s11-thx{position:absolute;left:0;right:0;text-align:center}',
    '.s11-small{position:absolute;left:96px;right:96px;text-align:center;font-size:22px;line-height:34px;color:var(--ink-2)}',
    '.s11-small b{color:var(--ink);font-weight:600}',
    '.s11-mono{position:absolute;left:96px;right:96px;text-align:center;font-family:var(--font-mono);font-size:18px;line-height:28px;color:var(--ink-3);letter-spacing:0}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s11-style')) return;
    var st = document.createElement('style'); st.id = 's11-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  /* ================================================================ s11-01 answers */
  var CX = [96, 446, 796, 1146, 1496];
  var CARDS = [
    { k: 'RQ1', q: 'Do the two scores order contracts differently?', a: 'Yes: τ = ' + fmt(TAU[0], 3), sb: 'They order the same contracts quite differently (neither 0 nor 1)', tags: [plainPill('Largely by construction')] },
    { k: 'RQ2', q: 'What does each score agree with?', a: 'The proxies of its own edges', sb: '<span style="font-size:20px;letter-spacing:-.01em;white-space:nowrap">EndorseRank × allowance <b>' + fmt(F_ER_A, 3) + '</b><br>AWP × transfer <b>' + fmt(F_AWP_T, 3) + '</b></span>', tags: [Deck.tagHTML('construct')] },
    { k: 'RQ3', q: 'How long does each take?', a: 'Time follows the edge count', sb: 'Time <b>' + fmt(R_TIME, 2) + '×</b> ≈ edges <b>' + fmt(R_EDGE, 2) + '×</b><br>Same solver', tags: [] },
    { k: 'RQ4', q: 'Do they predict later events? Better than the count?', a: 'Every score predicts', sb: 'On transfers AWP beats the count; on allowances <span class="em" id="em4">the count beats EndorseRank</span>', tags: [Deck.tagHTML('posthoc')] },
    { k: 'RQ5', q: 'Does mixing both edge types help?', a: 'No', sb: 'Rules A and B both not met<br>Same in the registered analysis', tags: [Deck.tagHTML('reanalysis')] }
  ];
  var OCH = [
    { cls: '', html: '<b>O1</b>Met' }, { cls: '', html: '<b>O2</b>Met' }, { cls: '', html: '<b>O3</b>Met' },
    { cls: 'part', html: '<b>O4 partly met</b>Prediction met; beating the count: AWP only' },
    { cls: 'fail', html: '<b>O5 not met</b>Rules A and B, also in the registered analysis' }
  ];
  var slide1 = {
    id: 's11-01', title: 'Answers to the research questions', time: 40, steps: 7,
    notes: [
      'Let me answer the five questions. The key pictures of the talk have come back as small tiles. Each question is paired with the objective of the same number.',
      'First, EndorseRank and AWP order the contracts differently. Kendall\'s tau is 0.174, neither 0 nor 1. But the two scores walk different graphs in different ways, so to some degree this result follows by construction.',
      'Second, each score agrees most with the proxies built from its own edges. EndorseRank reaches 0.585 with the allowance proxies, and AWP 0.572 with the transfer proxies. This is an intended-construct check. The proxies come from the same records, so part of the agreement is built in.',
      'Third, computing time follows the number of edges. The time is 2.17 times, the edges 2.23 times. It is the same solver, so the speed comes from the graph.',
      'Fourth, every score predicted later events to some degree. But on the transfer side the walk, that is AWP, beat the plain count, and on the allowance side the plain count beat EndorseRank. These are post hoc comparisons, made after seeing the labels.',
      'Fifth, C-PR, which mixes the two edge types, met neither of the two rules fixed in advance, A and B. This is a re-analysis that applies the rules to the revised scores, and the registered analysis gave the same verdicts.',
      'In addition, on an outcome found in neither edge type, such as avoiding liquidation, there was no evidence that the allowance side leads, and the comparison between the PageRank versions was not resolved. This too is a re-analysis that applies the registered rules to the revised scores.',
      'As for the objectives, the first three were met, but all three largely by construction. The fourth was only partly met: prediction was met, but only AWP did better than the count. The fifth was not met, and the same holds in the registered analysis.'
    ],
    html: function () {
      var cards = CARDS.map(function (c, i) {
        return '<div class="s11-card" data-in="none" data-k="' + i + '" style="left:' + CX[i] + 'px"><div class="th"></div><div class="bd">' +
          '<div class="rq"><span class="k">' + c.k + '</span><span class="qq">' + esc(c.q) + '</span></div>' +
          '<div class="an">' + esc(c.a) + '</div><div class="sb">' + c.sb + '</div>' +
          '<div class="tg">' + c.tags.join('') + '</div></div></div>';
      }).join('');
      var och = OCH.map(function (o, i) { return '<div class="s11-oc ' + o.cls + '" data-in="none" style="left:' + CX[i] + 'px">' + o.html + '</div>'; }).join('');
      return '<h1 class="t-h1">Five questions, [[five answers]]</h1>' + cards + och +
        '<div class="s11-brk" id="brk" data-in="none" style="left:' + (CX[0] + 20) + 'px;width:' + (CX[2] + 326 - CX[0] - 40) + 'px"><span>All three largely by construction</span></div>' +
        '<div class="abs s11-add" id="add" data-in="none" style="left:96px;top:880px;width:1728px"><span><b>Outcome in neither edge type</b> (liquidation avoidance): no evidence that the allowance side leads · PageRank versions not resolved</span>' + Deck.tagHTML('reanalysis') + '</div>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.cards = qa(el, '.s11-card');
      g.ths = g.cards.map(function (c) { return q(c, '.th'); });
      g.bds = g.cards.map(function (c) { return q(c, '.bd'); });
      g.ocs = qa(el, '.s11-oc'); g.brk = q(el, '#brk'); g.add = q(el, '#add');
      gsap.set(g.bds, { autoAlpha: 0 });
      gsap.set([g.brk, g.add].concat(g.ocs), { autoAlpha: 0 });
      drawThumbs(ctx, g);
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl(), rnd = ctx.rng(11);
      /* the pictures of the talk fly back in and settle, dim, as the grid of the answers */
      tl.fromTo(g.cards, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, stagger: 0.06 }, 0);
      g.ths.forEach(function (t, i) {
        var dx = (rnd() - 0.5) * 900, dy = 300 + rnd() * 300;
        tl.fromTo(t, { x: dx, y: dy, scale: 1.7, rotation: (rnd() - 0.5) * 12, opacity: 0 },
          { x: 0, y: 0, scale: 1, rotation: 0, opacity: 0.38, duration: 0.95, ease: 'power3.out' }, 0.1 + i * 0.12);
      });
      /* the section's ghost numeral would only peek through the gaps between the cards */
      var gh = ctx.root.querySelector('.ritual-ghost');
      if (gh) tl.to(gh, { autoAlpha: 0, duration: 0.6 }, 1.2);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i >= 1 && i <= 5) {
        var k = i - 1, card = g.cards[k], bd = g.bds[k];
        tl.call(function () { card.classList.add('on'); }, null, 0);
        tl.to(g.ths[k], { opacity: 1, duration: 0.4 }, 0);
        tl.fromTo(card, { y: 0 }, { y: -10, duration: 0.25, ease: 'power2.out', yoyo: true, repeat: 1 }, 0);
        tl.set(bd, { autoAlpha: 1 }, 0.1);
        tl.fromTo(bd.children, { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.1, ease: E.out }, 0.1);
        if (k === 3) tl.fromTo(q(el, '#em4'), { backgroundSize: '0% 100%' }, { backgroundSize: '100% 100%', duration: 0.6, ease: E.out }, 0.9);
      }
      if (i === 6) tl.fromTo(g.add, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 0);
      if (i === 7) {
        tl.fromTo(g.ocs, { autoAlpha: 0, y: -16, scale: 0.9 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.08, ease: E.stamp }, 0);
        tl.fromTo(g.brk, { autoAlpha: 0, scaleX: 0.3 }, { autoAlpha: 1, scaleX: 1, duration: 0.5, ease: E.out }, 0.45);
      }
    }
  };
  /* the five thumbnails: real data where the picture is data */
  function drawThumbs(ctx, g) {
    var W = 290, H = 128;
    /* RQ1: rank scatter, EndorseRank percentile × AWP percentile, all 15,107 contracts;
       amber where EndorseRank ranks the contract higher, sky where AWP does (as in s08-02) */
    var K = Comp.canvas(ctx, g.ths[0], { w: W, h: H, onResize: function (k) { scatter(k); } });
    function scatter(k) {
      var c = k.g; k.clear();
      var cd = Comp.data.contracts();
      if (!cd) return;
      var a = cd.pct.endorserank, b = cd.pct.awp;
      var AMB = 'rgba(245,180,60,.35)', SKY = 'rgba(60,196,255,.35)';
      for (var i = 0; i < a.length; i++) {
        c.fillStyle = b[i] > a[i] ? SKY : AMB;
        c.fillRect(14 + a[i] * (W - 28), H - 12 - b[i] * (H - 24), 1.4, 1.4);
      }
      c.strokeStyle = 'rgba(233,237,245,.25)'; c.lineWidth = 1;
      c.strokeRect(13.5, 11.5, W - 27, H - 23);
    }
    scatter(K);
    /* RQ2: family bars */
    var s2 = Comp.svg(ctx, g.ths[1], { w: W, h: H });
    function bar(x, v, col) { var hh = v * 150; svgEl('rect', { x: x, y: H - 22 - hh, width: 30, height: hh, rx: 4, fill: col }, s2); }
    bar(40, F_ER_A, C.allow); bar(74, F_ER_T, C.xfer); bar(186, F_AWP_A, C.allow); bar(220, F_AWP_T, C.xfer);
    svgEl('line', { x1: 20, x2: W - 20, y1: H - 22, y2: H - 22, stroke: C.line, 'stroke-width': 1.5 }, s2);
    [['EndorseRank', 72], ['AWP', 218]].forEach(function (t) { var x = svgEl('text', { x: t[1], y: H - 5, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 13 }, s2); x.textContent = t[0]; });
    /* RQ3: race bars */
    var s3 = Comp.svg(ctx, g.ths[2], { w: W, h: H });
    var sc = 10;
    svgEl('rect', { x: 20, y: 34, width: T_ER * sc, height: 22, rx: 6, fill: C.allow }, s3);
    svgEl('rect', { x: 20, y: 74, width: T_AWP * sc, height: 22, rx: 6, fill: C.xfer }, s3);
    svgEl('line', { x1: 20, x2: 20, y1: 24, y2: 106, stroke: C.ink3, 'stroke-width': 1.5 }, s3);
    /* RQ4: interval bars around zero (W1, after the labels) */
    var s4 = Comp.svg(ctx, g.ths[3], { w: W, h: H });
    function X(v) { return 145 + v * 2400; }
    svgEl('line', { x1: X(0), x2: X(0), y1: 14, y2: H - 14, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 4' }, s4);
    [[W1C_AWP, 44, C.xfer], [W1C_ER, 86, C.allow]].forEach(function (r) {
      svgEl('line', { x1: X(r[0][1]), x2: X(r[0][2]), y1: r[1], y2: r[1], stroke: r[2], 'stroke-width': 5, 'stroke-linecap': 'round' }, s4);
      svgEl('circle', { cx: X(r[0][0]), cy: r[1], r: 7, fill: r[2] }, s4);
    });
    /* RQ5: two verdict stamps */
    var s5 = h('div', '', g.ths[4]);
    s5.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:12px';
    s5.innerHTML = '<span class="stamp fail" style="font-size:18px;padding:6px 10px;border-width:2.5px;transform:rotate(-6deg)">A not met ✕</span>' +
      '<span class="stamp fail" style="font-size:18px;padding:6px 10px;border-width:2.5px;transform:rotate(4deg)">B not met ✕</span>';
  }

  /* ================================================================ s11-02 contributions */
  var TILES = [
    { n: '①', x: 96, y: 196, w: 600, h: 640 },
    { n: '②', x: 728, y: 196, w: 532, h: 304 },
    { n: '③', x: 1292, y: 196, w: 532, h: 304 },
    { n: '④', x: 728, y: 532, w: 532, h: 304 },
    { n: '⑤', x: 1292, y: 532, w: 532, h: 304 }
  ];
  var slide2 = {
    id: 's11-02', title: 'What this study adds', time: 30, steps: 2,
    notes: [
      'This study adds five things.',
      'First, it uses the allowance as an edge of contract reputation: that is EndorseRank. Second, an evaluation design that sets every score against the raw count before smoothing, in the same window and in two windows outside it. Third, a closed form that shows what EndorseRank actually computes at a depth-one spender. Fourth, C-PR, which mixes the two edge types, and its test by rules fixed in advance; the result was not met. Fifth, a comparison registered in advance on an outcome found in neither edge type.',
      'The PageRank algorithm and AWP\'s weights are borrowed. What is new is the kind of edge and the way it was tested.'
    ],
    html: function () {
      var t = TILES;
      function tile(i, inner) { var T = t[i]; return '<div class="s11-tile" data-in="none" data-i="' + i + '" style="left:' + T.x + 'px;top:' + T.y + 'px;width:' + T.w + 'px;height:' + T.h + 'px"><span class="no">' + T.n + '</span>' + inner + '</div>'; }
      return '<h1 class="t-h1">[[Five]] contributions</h1>' +
        tile(0, '<svg class="vis" id="v1" width="600" height="380" viewBox="0 0 600 380" style="top:70px"></svg>' +
          '<div class="tx"><span class="big c-allow">EndorseRank</span><br>Allowances as reputation edges for contracts<small>The allowance an owner gives a contract is an endorsement</small></div>') +
        tile(1, '<svg class="vis" id="v2" width="532" height="150" viewBox="0 0 532 150" style="top:44px"></svg>' +
          '<div class="tx">Every score set against the raw count<small>Same window · two holdouts (W0, W1)</small></div>') +
        tile(2, '<div class="vis fx" id="v3" style="top:62px;text-align:center">$r_v=c\\,\\bigl(1+d\\,\\delta(v)\\bigr)$</div>' +
          '<div class="tx">Closed form at a depth-one spender:<br>EndorseRank = split approval count</div>') +
        tile(3, '<div class="vis" id="v4" style="top:28px;height:170px"></div>' +
          '<div class="tx">C-PR mixes both edge types, tested<br>by rules fixed in advance <span class="ink-2">(not met)</span></div>') +
        tile(4, '<svg class="vis" id="v5" width="532" height="150" viewBox="0 0 532 150" style="top:44px"></svg>' +
          '<div class="tx">A registered comparison on<br>an outcome in neither edge type<small>Liquidation avoidance of GMX V2 contract traders</small></div>') +
        '<p class="abs s11-note" data-step="2" style="left:96px;top:870px;width:1728px">The algorithm (PageRank) and the weights (AWP) are <b>borrowed</b>. What is new is the <b>edge</b> and the <b>way it was tested</b>.</p>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.tiles = qa(el, '.s11-tile');
      gsap.set(g.tiles, { autoAlpha: 0 });
      /* ① owner → spender, the G1 arrow */
      var v1 = q(el, '#v1');
      g.o1s = [[110, 60], [110, 170], [110, 280]].map(function (p, k) { return Comp.eoa(ctx, v1, { x: p[0], y: p[1], r: 24, label: k === 2 ? 'owners' : null }); });
      g.c1 = Comp.contract(ctx, v1, { x: 470, y: 170, size: 104, label: 'spender contract' });
      g.c1.label.setAttribute('y', 92); g.c1.label.setAttribute('font-size', 24);
      g.a1s = [[110, 60], [110, 170], [110, 280]].map(function (p, k) {
        return Comp.arrow(ctx, v1, { from: p, to: [470, 170], kind: 'allow', width: k === 1 ? 6 : 4, head: k === 1 ? 22 : 17, shorten: [38, 70], label: k === 1 ? 'allowance' : null, labelOffset: 22, labelSize: 24, hidden: true });
      });
      /* ② the count beside the walk: tally + three windows */
      var v2 = q(el, '#v2');
      g.tally = Comp.tally(ctx, v2, { x: 36, y: 34, size: 56 });
      [['same window', 212], ['W0', 364], ['W1', 448]].forEach(function (b, k) {
        var w = k ? 70 : 140;
        var r = svgEl('rect', { x: b[1], y: 52, width: w, height: 40, rx: 10, fill: 'none', stroke: k ? C.ink2 : C.ink3, 'stroke-width': 2, 'stroke-dasharray': k ? null : '5 5' }, v2);
        var t = svgEl('text', { x: b[1] + w / 2, y: 78, 'text-anchor': 'middle', fill: C.ink, 'font-size': 19, 'font-weight': 600 }, v2); t.textContent = b[0];
        void r;
      });
      g.v2bands = qa(v2, 'rect, text');
      gsap.set(g.v2bands, { autoAlpha: 0 });
      /* ③ formula */
      g.v3 = q(el, '#v3');
      /* ④ λ dial */
      var v4 = q(el, '#v4');
      g.dial = Comp.dial(ctx, v4, { value: 1, size: 220 });
      g.dial.el.style.position = 'absolute'; g.dial.el.style.left = '60px'; g.dial.el.style.top = '0px';
      g.stamp = Comp.stamp(ctx, v4, { ok: false, text: 'Rules A · B\nnot met', x: 300, y: 50 });
      g.stamp.el.style.fontSize = '24px';
      g.stamp.el.style.whiteSpace = 'pre-line'; g.stamp.el.style.textAlign = 'center'; g.stamp.el.style.lineHeight = '1.15';
      /* ⑤ waffle: one dot per W1 trader contract */
      var v5 = q(el, '#v5');
      g.waf = [];
      for (var i = 0; i < N_W1; i++) {
        var cx = 40 + (i % 18) * 25, cy = 22 + Math.floor(i / 18) * 24;
        g.waf.push(svgEl('circle', { cx: cx, cy: cy, r: 8.5, fill: C.ink2, 'fill-opacity': 0.75 }, v5));
      }
      var wt = svgEl('text', { x: 31, y: 22 + 3 * 24 + 32, fill: C.ink3, 'font-size': 17 }, v5);
      wt.textContent = 'One dot = one W1 trader contract (' + N_W1 + ')';
      g.wt = wt;
      gsap.set(g.waf.concat([wt]), { autoAlpha: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(g.tiles, { autoAlpha: 0, y: 40, scale: 0.96, transformOrigin: '50% 100%' }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.55, stagger: 0.12, ease: E.out }, 0);
        /* one small motion per tile, once */
        g.o1s.forEach(function (o, k) { tl.add(o.pop(), 0.3 + k * 0.08); });
        tl.add(g.c1.pop(), 0.45);
        g.a1s.forEach(function (A, k) { tl.add(A.draw({ duration: 0.7 }), 0.6 + k * 0.15); });
        tl.add(g.tally.add(10, { stagger: 0.07 }), 0.5);
        tl.fromTo(g.v2bands, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.3, stagger: 0.05 }, 0.9);
        tl.fromTo(g.v3, { autoAlpha: 0, scale: 0.8, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: E.stamp }, 0.7);
        tl.add(g.dial.set(0.5, { duration: 1.0 }), 0.75);
        tl.add(g.stamp.slam(), 1.7);
        tl.fromTo(g.waf, { autoAlpha: 0, scale: 0.2, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.25, stagger: 0.012, ease: E.stamp }, 0.8);
        tl.fromTo(g.wt, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 1.8);
      }
    }
  };

  /* ================================================================ s11-03 limits */
  function ico(body) { return '<svg viewBox="0 0 40 40" fill="none" stroke="#A3ADBF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>'; }
  var LIMITS = [
    { i: ico('<circle cx="13" cy="20" r="7"/><path d="M20 20h16M30 20v6M35 20v4"/>'), t: 'No off-chain information besides prices and the token list: <span>it cannot tell whether approving owners are different people</span>' },
    { i: ico('<path d="M14 11l-9 9 9 9M26 11l9 9-9 9M23 8l-6 24"/>'), t: 'A reputation of contracts only: <span>it says nothing about whether the code is safe</span>' },
    { i: '<svg viewBox="0 0 40 40" fill="none"><rect x="5" y="5" width="30" height="30" rx="8" stroke="#A3ADBF" stroke-width="2.4"/><text x="20" y="21" text-anchor="middle" dominant-baseline="middle" fill="#A3ADBF" font-size="13" class="svg-mono">{ }</text></svg>', t: 'Only contracts were scored: <span>it says nothing about EOAs</span>' },
    { i: Deck.ICONS.loop, t: 'The revised analysis was set after the registered results were known → <span>its verdicts are a re-analysis</span>' },
    { i: Deck.ICONS.eye, t: 'The comparisons with the raw count and the activity-restart variant are <span>post hoc</span>' },
    { i: ico('<circle cx="8" cy="10" r="3"/><circle cx="32" cy="9" r="3"/><circle cx="20" cy="22" r="3.5"/><circle cx="9" cy="32" r="3"/><circle cx="33" cy="31" r="3"/><path d="M10.5 12l7 8M29.5 11l-7 9M11 30l7-6M31 29l-8.5-5"/>'), t: 'Ego network (only edges that touch the cohort) · five tokens · Arbitrum One · <span>these months only</span>' },
    { i: ico('<circle cx="10" cy="10" r="3"/><circle cx="20" cy="10" r="3"/><circle cx="30" cy="10" r="3"/><circle cx="10" cy="20" r="3"/><circle cx="20" cy="20" r="3"/><circle cx="10" cy="30" r="3"/>'), t: 'The trader samples are small <span>(W1: ' + N_W1 + ' · W0: ' + N_W0 + ')</span>' },
    { i: '<svg viewBox="0 0 40 40" fill="none" stroke="#A3ADBF" stroke-width="2.2" stroke-dasharray="3 3"><circle cx="20" cy="8" r="4.5"/><circle cx="31" cy="16" r="4.5"/><circle cx="28" cy="30" r="4.5"/><circle cx="12" cy="30" r="4.5"/><circle cx="9" cy="16" r="4.5"/></svg>', t: 'With uniform restarts the score is <span>weak against closed farms</span>' }
  ];
  var slide3 = {
    id: 's11-03', title: 'Limitations', time: 35, steps: 2,
    notes: [
      'Let me also be clear about the limitations.',
      'These scores use no off-chain information except daily prices and the token list, so we cannot tell whether the owners who approve a contract are really different people. It is only a reputation of contracts; it says nothing about whether the code is safe. Only contracts received scores, so it says nothing at all about EOAs. The revised analysis in the main text was set after the registered results were known, so its verdicts are a re-analysis.',
      'The comparisons with the raw count and the activity-restart variant were made after seeing the labels. And the results come from an ego network that keeps only the edges touching the cohort, from five tokens, from one chain, Arbitrum One, and from these months only. The trader samples are small, 70 in W1 and 88 in W0, and the score with uniform restarts is weak against closed farms.'
    ],
    html: function () {
      function rows(a, step) {
        return '<div class="s11-lim" data-in="none" data-k="' + step + '" data-stagger="0.08">' + a.map(function (l) {
          return '<div class="r"><span class="ic">' + l.i + '</span><span class="t">' + l.t + '</span></div>';
        }).join('') + '</div>';
      }
      return '<h1 class="t-h1">What this study does [[not say]]</h1>' +
        '<div class="abs" style="left:96px;top:206px;width:1728px">' + rows(LIMITS.slice(0, 4), 1) + '<div style="height:14px"></div>' + rows(LIMITS.slice(4), 2) + '</div>';
    },
    build: function (el, ctx) { ctx.g = { groups: qa(el, '.s11-lim') }; gsap.set(ctx.g.groups, { autoAlpha: 0 }); },
    step: function (el, i, ctx) { var tl = ctx.tl(); tl.add(ctx.reveal(ctx.g.groups[i - 1], 'rise'), 0); }
  };

  /* ================================================================ s11-04 the wallet window again */
  var WP = (window.DeckParts || {}).wallet || null;
  var WG = WP ? WP.GEOM : { left: 550, top: 150, w: 820, h: 520, yes: [1065, 579] };
  var WS = 0.78, WX = 96, WY = 196;                    /* window after it steps aside */
  var WT = Math.max(WG.top, 196), WDY = WT - WG.top;    /* opens at the content top, clear of the title */
  function fallbackWallet() {
    return '<div class="s01-win" id="win" data-in="none" style="left:' + WG.left + 'px;top:' + WT + 'px;position:absolute;width:820px;height:520px;background:#121826;border:1px solid #2A3345;border-radius:24px;overflow:hidden">' +
      '<div class="q" style="position:absolute;left:40px;right:40px;top:262px;text-align:center;font-size:30px;line-height:42px;font-weight:600">' + WQ + '</div>' +
      '<div class="cd" style="position:absolute;left:0;right:0;top:318px;text-align:center"></div>' +
      '<div class="btns" style="position:absolute;left:0;right:0;top:396px;display:flex;justify-content:center;gap:20px"><div class="btn no">Reject</div><div class="btn yes">Approve</div></div></div>';
  }
  var WQ = 'Allow this contract to spend your USDC?';
  var NEXT = [
    { t: 'Register the activity-restart variant on a new window and test it against the count', s: 'Depth-one and deeper spenders reported separately', hyp: true },
    { t: 'A registered test of the revised analysis itself', s: 'e.g. registered before the October–December 2026 logs are extracted' },
    { t: 'Restart only from trusted seeds to block farms', s: 'Under uniform restarts a closed farm collects share' },
    { t: 'Compare with contract-risk labels (drainers, rug pulls)', s: 'See whether the score says anything about risk beyond activity' }
  ];
  var slide4 = {
    id: 's11-04', title: 'What wallet software could show, and next steps', time: 40, steps: 3,
    carrier: false,
    notes: [
      'So what could that first window show?',
      'The window from the start opens again. This time it has one more line: the number of distinct owner addresses that approved this contract. Owners are addresses, not people, so the line counts addresses, not persons. By the results of this study, this number is a public signal that any service can compute without PageRank, and EndorseRank did not beat it out of window either. The N on the screen is a placeholder and does not point to any particular contract.',
      'But this number only says how widely the contract is approved. A low number is a reason to look closer, but a high number is no reason to sign. That is why the cursor only rests on the Approve button.',
      'For further research I have four things in mind. First, register the activity-restart variant in advance on a new window and test it against the count; for now this is only a hypothesis. Second, redo the revised analysis itself as a registered test. Third, restart only from trusted seeds, to block farms. And fourth, compare the scores with real contract-risk labels.'
    ],
    html: function () {
      var win = WP ? WP.html({ id: 'win', top: WT, question: WQ, code: '' }) : fallbackWallet();
      return '<h1 class="t-h1">What that window could show</h1>' + win +
        '<div class="s01-spark" id="sp1" data-in="none" style="position:absolute;left:0;top:0;width:14px;height:14px;border-radius:8px;background:#fff;box-shadow:0 0 14px 3px rgba(255,255,255,.75)"></div>' +
        '<div class="s01-spark" id="sp2" data-in="none" style="position:absolute;left:0;top:0;width:14px;height:14px;border-radius:8px;background:#fff;box-shadow:0 0 14px 3px rgba(255,255,255,.75)"></div>' +
        '<p class="abs s11-nnote" id="nnote" data-in="none" style="left:' + WX + 'px;top:' + (WY + WG.h * WS + 14) + 'px;width:' + (WG.w * WS) + 'px">N is a placeholder: it does not point to any particular contract</p>' +
        '<div class="abs s11-two" id="two" data-in="none" style="left:' + WX + 'px;top:' + (WY + WG.h * WS + 74) + 'px;width:700px">' +
          '<div>Low count <span class="ne">=</span> <span class="ink-2">reason to look closer</span></div>' +
          '<div>High count <span class="ne" id="ne">≠</span> [[reason to sign]]</div></div>' +
        '<div class="abs s11-nx" id="nx" data-in="none" style="left:820px;top:196px;width:1004px"><h2 class="t-h2">Next steps</h2>' +
          NEXT.map(function (n, i) {
            return '<div class="s11-nc"><span class="n">' + (i + 1) + '</span><span class="t"' + (n.hyp ? ' style="padding-right:260px"' : '') + '>' + esc(n.t) + '<small>' + esc(n.s) + '</small></span>' +
              (n.hyp ? '<span class="s11-hyp" id="hyp">' + Deck.tagHTML({ en: 'Hypothesis · post hoc', icon: 'eye', key: 'hypothesis' }) + '</span>' : '') + '</div>';
          }).join('') + '</div>' +
        '<svg class="abs" id="lay" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible;pointer-events:none"></svg>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.win = q(el, '#win');
      if (WP) WP.figure(ctx, g.win);
      /* the new line in the window: distinct approving owners, N (placeholder) */
      var cd = q(g.win, '.cd');
      cd.innerHTML = '<span class="s11-nl" id="nl"></span>';
      g.nl = q(cd, '#nl');
      g.nlText = 'Distinct owner addresses that approved this contract: ';
      var ns = h('div', 's11-ns', g.win, 'Only how widely it is approved, not a sign that it is safe');
      g.ns = ns;
      gsap.set([g.win, ns, q(el, '#sp1'), q(el, '#sp2'), q(el, '#nnote'), q(el, '#two'), q(el, '#nx')], { autoAlpha: 0 });
      g.cards = qa(el, '.s11-nc'); g.hyp = q(el, '#hyp');
      g.cursor = Comp.walker(ctx, q(el, '#lay'), { x: 760, y: 760, r: 9, hidden: true });
      g.yes = q(g.win, '.btn.yes');
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        /* the same window, opened the same way (46 px lower, clear of the title): point → line → window */
        var A = q(el, '#sp1'), B = q(el, '#sp2');
        var cx = WG.left + WG.w / 2, cy = WT + WG.h / 2;
        tl.set(g.win, { autoAlpha: 1, clipPath: 'inset(50% 0% 50% 0% round 24px)' }, 0);
        tl.fromTo([A, B], { x: cx - 7, y: cy - 7, width: 14, height: 14, scale: 0, autoAlpha: 1 }, { scale: 1, duration: 0.3, ease: 'back.out(2)' }, 0.05);
        tl.to([A, B], { x: WG.left, width: WG.w, height: 2, y: cy - 1, duration: 0.36, ease: 'power3.inOut' }, 0.4);
        tl.to(g.win, { clipPath: 'inset(0% 0% 0% 0% round 24px)', duration: 0.55, ease: 'power3.out' }, 0.78);
        tl.to(A, { y: WT - 1, duration: 0.55, ease: 'power3.out' }, 0.78);
        tl.to(B, { y: WT + WG.h - 1, duration: 0.55, ease: 'power3.out' }, 0.78);
        tl.to([A, B], { autoAlpha: 0, duration: 0.35 }, 1.25);
        /* typewriter: the new line */
        var st = { n: 0 }, full = g.nlText;
        tl.to(st, { n: full.length, duration: 1.1, ease: 'none', onUpdate: function () {
          g.nl.innerHTML = esc(full.slice(0, Math.round(st.n))) + '<span class="s11-caret"></span>';
        }, onComplete: function () { g.nl.innerHTML = esc(full) + '<b>N</b>'; } }, 1.45);
        tl.fromTo(g.ns, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 2.65);
        /* the cursor comes to rest on Approve, and does not press */
        tl.set(g.cursor.g, { autoAlpha: 1 }, 2.7);
        tl.call(function () { g.cursor.set(760, 760); }, null, 2.69);
        tl.add(g.cursor.moveTo(WG.yes[0] + 30, WG.yes[1] + WDY + 14, { duration: 0.9, ease: 'power3.out' }), 2.7);
      }
      if (i === 2) {
        var yx = WX + (WG.yes[0] - WG.left) * WS, yy = WY + (WG.yes[1] - WG.top) * WS;
        tl.to(g.win, { x: WX - WG.left, y: WY - WT, scale: WS, transformOrigin: '0 0', duration: 1.0, ease: E.io }, 0);
        tl.add(g.cursor.moveTo(yx + 24, yy + 12, { duration: 1.0, ease: E.io }), 0);
        tl.fromTo(q(el, '#nnote'), { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 0.9);
        var two = q(el, '#two');
        tl.set(two, { autoAlpha: 1 }, 1.0);
        tl.fromTo(two.children, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.35, ease: E.out }, 1.0);
        tl.fromTo(q(el, '#ne'), { scale: 2.2, rotation: -10 }, { scale: 1, rotation: 0, duration: 0.45, ease: E.stamp }, 1.4);
        var hl = two.querySelector('.hl');
        if (hl) tl.fromTo(hl, { '--hl-x': 0 }, { '--hl-x': 1, duration: 0.5, ease: 'power2.inOut' }, 1.75);
      }
      if (i === 3) {
        var nx = q(el, '#nx');
        tl.set(nx, { autoAlpha: 1 }, 0);
        tl.fromTo(nx.firstChild, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: E.out }, 0);
        tl.fromTo(g.cards, { autoAlpha: 0, x: 60 }, { autoAlpha: 1, x: 0, duration: 0.5, stagger: 0.12, ease: E.out }, 0.15);
        if (g.hyp) tl.fromTo(g.hyp, { autoAlpha: 0, x: -520, y: -150, rotation: -12 }, { autoAlpha: 1, x: 0, y: 0, rotation: 0, duration: 0.9, ease: 'power3.inOut' }, 0.9);
      }
    }
  };

  /* ================================================================ s11-05 thanks */
  var SWT = { x: 704, y: 128, s: 0.68 };   /* constellation: the small world, scaled */
  var slide5 = {
    id: 's11-05', title: 'Thank you', time: 20, steps: 2,
    hud: false,
    notes: [
      '(The four nodes of the small world rise like a constellation.)',
      'Thank you for listening. I am happy to take your questions now.',
      'I thank my supervisors, Professor Mnkandla, Professor Moulla and Dr. Attipoe. The code and every result number of this study are in the public repository, and for every number in this talk I have noted which value in which file it comes from.'
    ],
    html: function () {
      var sup = esc(META.supervisor || 'Prof. Ernest Mnkandla'), co = esc((META.co_supervisors || ['Prof. Donatien Koulla Moulla', 'Dr. David Sena Attipoe']).join(', '));
      return '<svg class="abs" id="sky" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible;pointer-events:none"></svg>' +
        '<div class="s11-thx" id="thx" data-in="none" style="top:500px"><div class="t-display" id="ty">Thank you</div></div>' +
        '<svg class="abs" id="ul" data-in="none" width="1920" height="60" viewBox="0 0 1920 60" style="left:0;top:628px;overflow:visible"></svg>' +
        '<p class="s11-thx t-body-l ink-2" id="qa" data-in="none" style="top:690px">Questions are welcome</p>' +
        '<p class="s11-small" id="sm1" data-in="none" style="top:846px">Supervisor <b>' + sup + '</b> · Co-supervisors <b>' + co + '</b> · ' + esc(META.university || 'University of South Africa') + ' (UNISA)</p>' +
        '<p class="s11-mono" id="sm2" data-in="none" style="top:892px">Code and results: github.com/abitocodes/phd_works · results digest: experiments/data/3-published-results-for-thesis/revised-usd/</p>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      var sky = q(el, '#sky');
      var SW = Comp.SMALL_WORLD, P = {};
      SW.nodes.forEach(function (n) { P[n.id] = [SWT.x + n.x * SWT.s, SWT.y + n.y * SWT.s]; });
      var arL = svgEl('g', {}, sky);
      g.arrows = SW.edges.map(function (e) {
        return Comp.arrow(ctx, arL, { from: P[e.from], to: P[e.to], kind: 'allow', width: 2, head: 11, shorten: [16, 18], hidden: true });
      });
      g.stars = SW.nodes.map(function (n) {
        var p = P[n.id], gg = svgEl('g', {}, sky);
        svgEl('circle', { cx: p[0], cy: p[1], r: 16, fill: '#fff', 'fill-opacity': 0.08 }, gg);
        svgEl('circle', { cx: p[0], cy: p[1], r: n.kind === 'eoa' ? 5 : 7, fill: '#fff', 'class': 'glow-white' }, gg);
        gsap.set(gg, { autoAlpha: 0 });
        return gg;
      });
      /* the G1 underline under the thanks */
      var ul = q(el, '#ul');
      g.ula = Comp.arrow(ctx, ul, { from: [700, 24], to: [1220, 24], kind: 'allow', width: 5, head: 20, hidden: true });
      g.ty = q(el, '#ty');
      gsap.set([g.ty, q(el, '#qa'), q(el, '#sm1'), q(el, '#sm2')], { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      g.stars.forEach(function (s, k) {
        tl.fromTo(s, { autoAlpha: 0, scale: 0.2, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: 'back.out(2)' }, 0.2 + k * 0.12);
      });
      g.arrows.forEach(function (A, k) { tl.add(A.draw({ duration: 0.6 }), 0.8 + k * 0.12); });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.add(ctx.rise(g.ty, { stagger: 0.08 }), 0);
        tl.add(g.ula.draw({ duration: 0.8 }), 0.5);
        tl.fromTo(q(el, '#qa'), { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: E.out }, 1.0);
      }
      if (i === 2) tl.fromTo([q(el, '#sm1'), q(el, '#sm2')], { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.15, ease: E.out }, 0);
    }
  };

  Deck.section({ id: 's11-closing', title: 'Conclusion', slides: [slide1, slide2, slide3, slide4, slide5] });
})();
