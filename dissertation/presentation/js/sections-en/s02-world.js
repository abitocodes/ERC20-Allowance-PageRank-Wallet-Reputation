/* =========================================================================
   s02-world — Allowances and transfers, English edition (STORYBOARD.md §2, s02-01 … s02-05)
   s02-01  DeFi in one picture              (three contract cards, each with a one-shot mini animation)
   s02-02  Transfers and allowances differ  (transfer = coins flow; allowance = a standing promise:
                                            transferFrom, overwrite, revoke)
   s02-03  Allowances look like trust, but  (40 + 40 identical arrows; 49.8 % unlimited)
   s02-04  The scored objects are contracts (scan brackets lock onto contracts only)
   s02-05  The setting: Arbitrum One        (CSS-3D plates, falling log particles; the Arbitrum plate
                                            turns edge-on into the time axis of s03-01)

   Numbers and sources
     49.8 % = 2,084,669 / 4,185,287 positive latest allowances at T_obs, set inside the T_obs score
       window (2025-07-01 – 2026-06-30), that are unlimited (revised digest, revised-usd-12m:
       amounts.unlimited_share 0.4981, amounts.unlimited_allowances, amounts.latest_allowances_tobs
       = DECK_DATA.scale.revised.amounts; thesis App. D, table usd-tokens)
     block 513,216,506 = experiments/data/1-raw-blockchain-extracts/cohort/candidate_account_types.json
       block_number (thesis Ch. 3, "Account type"): the eth_getCode block of the cohort candidates only;
       holdout spenders and GMX accounts outside the candidates were read at later blocks within
       three hours. Said in the notes of s02-04 only (the slide keeps the plain idea).
     chain ID 42161 = DECK_DATA.params.chain.id (config/contract_reputation.yaml chain_id)
     1,000 / 500 USDC on s02-02 are examples (made up for the explanation).

   Shared element: s02-05 leaves a horizontal line with data-shared="time-axis" at
   left 96, top 715, width 1728, height 2 (stage px) = the axis line of s03-01, which carries the same
   key, so the FLIP hand-over is in place.
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, esc = Deck.util.esc, fmt = Deck.util.fmt;
  var DATA = window.DECK_DATA || {};
  var NS = 'http://www.w3.org/2000/svg';
  var AMT = (((DATA.scale || {}).revised || {}).amounts) || {};
  var UNL = AMT.unlimited_allowances != null ? AMT.unlimited_allowances : 2084669;
  var LATEST = AMT.latest_allowances_tobs != null ? AMT.latest_allowances_tobs : 4185287;
  var UNL_SHARE = AMT.unlimited_share != null ? AMT.unlimited_share : 0.4981;
  var CHAIN_ID = ((DATA.params || {}).chain || {}).id || 42161;
  var GETCODE_BLOCK = 513216506; /* candidate_account_types.json block_number */
  var CLIP_N = 0;

  /* ------------------------------------------------------------ section styles */
  var CSS = [
    /* s02-01 */
    '.s02-cards{position:absolute;left:96px;top:290px;display:flex;gap:48px}',
    '.s02-card{position:relative;width:544px;height:470px;border-radius:24px;background:var(--bg-2);border:1px solid var(--line);overflow:hidden}',
    '.s02-card svg{position:absolute;left:0;top:14px;overflow:visible}',
    '.s02-card .nm{position:absolute;left:40px;top:300px;font-size:42px;line-height:52px;font-weight:700;letter-spacing:-.02em}',
    '.s02-card .ds{position:absolute;left:40px;right:30px;top:362px;font-size:28px;line-height:40px;color:var(--ink-2)}',
    '.s02-line{position:absolute;left:96px;width:1728px;font-size:34px;line-height:50px;color:var(--ink-2)}',
    '.s02-line b{color:var(--ink);font-weight:700}',
    /* s02-02 */
    '.s02-panel{position:absolute;top:196px;width:840px;height:572px}',
    '.s02-panel > svg.frame{position:absolute;left:0;top:0;overflow:visible}',
    '.s02-panel .hd{position:absolute;left:44px;top:34px;font-size:46px;line-height:56px;font-weight:700;letter-spacing:-.02em}',
    '.s02-panel .hd small{font-size:26px;font-weight:500;color:var(--ink-3);margin-left:12px;letter-spacing:0}',
    '.s02-panel .tx{position:absolute;left:44px;right:40px;top:112px;font-size:28px;line-height:44px;color:var(--ink)}',
    '.s02-panel .tx .sub{display:block;color:var(--ink-2);margin-top:6px}',
    '.s02-panel svg.fig{position:absolute;left:0;top:214px;overflow:visible}',
    '.s02-codes{position:absolute;left:984px;top:788px;display:flex;flex-wrap:wrap;gap:12px 14px;align-items:center;width:860px}',
    '.s02-codes .c{font-family:var(--font-mono);font-size:21px;line-height:30px;padding:6px 14px;border-radius:10px;background:var(--bg-3);color:var(--ink);letter-spacing:0;position:relative}',
    '.s02-codes .c i{font-style:normal;color:var(--ink-3)}',
    '.s02-codes .c .ext{font-family:var(--font-sans);font-size:20px;margin-left:6px}',
    '.s02-codes .lb{font-size:22px;color:var(--ink-3)}',
    '.s02-codes .grp{display:inline-flex;gap:10px;align-items:center;white-space:nowrap}',
    '.s02-bottom{position:absolute;left:96px;top:880px;font-size:36px;line-height:50px;font-weight:600}',
    /* s02-03 */
    '.s02-sub{position:absolute;left:96px;top:164px;width:1728px;font-size:30px;line-height:44px;color:var(--ink-2)}',
    '.s02-claim{position:absolute;left:1180px;top:300px;width:644px;padding:26px 30px;border-radius:20px;background:var(--bg-2);border:1px solid var(--line)}',
    '.s02-claim .k{font-size:24px;line-height:32px;color:var(--ink-3)}',
    '.s02-claim .v{margin-top:8px;font-size:46px;line-height:58px;font-weight:700;letter-spacing:-.02em}',
    '.s02-claim .v small{display:block;font-size:26px;line-height:36px;font-weight:500;color:var(--ink-2);letter-spacing:0;margin-top:4px}',
    '.s02-warn{position:absolute;left:1180px;top:500px;width:644px}',
    '.s02-warn .w{display:flex;gap:18px;align-items:flex-start;margin-bottom:22px}',
    '.s02-warn .w svg{flex:0 0 auto;width:44px;height:44px;margin-top:2px}',
    '.s02-warn .w .t{font-size:28px;line-height:40px}',
    '.s02-warn .big{display:flex;align-items:baseline;gap:16px;margin-top:6px}',
    '.s02-warn .big .n{font-size:84px;line-height:88px;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums}',
    '.s02-warn .big .u{font-size:24px;line-height:32px;color:var(--ink-2)}',
    '.s02-src{font-family:var(--font-mono);font-size:20px;line-height:28px;color:var(--ink-3);letter-spacing:0;margin-top:8px}',
    /* s02-04 */
    '.s02-l{position:absolute;left:96px;width:780px;font-size:30px;line-height:46px}',
    '.s02-l .note{color:var(--ink-2)}',
    '.s02-small{position:absolute;left:96px;top:846px;width:780px;font-size:24px;line-height:36px;color:var(--ink-2)}',
    '.s02-legend{position:absolute;left:964px;top:904px;display:flex;gap:30px;align-items:center;font-size:22px;color:var(--ink-2)}',
    '.s02-legend span{display:inline-flex;align-items:center;gap:10px}',
    /* s02-05 */
    '.s02-scene{position:absolute;left:740px;top:150px;width:1000px;height:760px;perspective:1700px;perspective-origin:50% 40%}',
    '.s02-world{position:absolute;left:500px;top:360px;width:0;height:0;transform-style:preserve-3d}',
    '.s02-plate{position:absolute;left:-250px;top:-250px;width:500px;height:500px;border-radius:26px;border:2px solid #4A5468;',
    '  background-color:rgba(16,21,31,.82);background-image:linear-gradient(rgba(233,237,245,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(233,237,245,.07) 1px,transparent 1px);',
    '  background-size:50px 50px;background-position:-1px -1px}',
    '.s02-plate.arb{border-color:#A3ADBF;background-color:rgba(22,28,41,.9)}',
    '.s02-batch{position:absolute;left:-34px;top:-34px;width:68px;height:68px;border-radius:10px;border:2px solid var(--ink);background:rgba(233,237,245,.12)}',
    '.s02-mark{position:absolute;width:2px;height:2px}',
    '.s02-plbl{position:absolute;font-size:28px;line-height:36px;font-weight:700;white-space:nowrap}',
    '.s02-plbl small{display:block;font-size:20px;line-height:28px;font-weight:500;color:var(--ink-3);font-family:var(--font-mono);letter-spacing:0}',
    '.s02-pts{position:absolute;left:96px;top:236px;width:700px}',
    '.s02-pts .p{display:flex;gap:18px;align-items:flex-start;margin-bottom:30px;font-size:30px;line-height:44px}',
    '.s02-pts .p .ic{flex:0 0 auto;width:12px;height:12px;border-radius:6px;background:var(--ink-2);margin-top:16px}',
    '.s02-pts .p b{font-weight:700}',
    '.s02-pts .p .mono{font-size:26px}',
    '.s02-axis{position:absolute;left:96px;top:715px;width:1728px;height:2px;background:#A3ADBF;border-radius:1px;transform-origin:0 50%}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s02-style')) return;
    var st = document.createElement('style'); st.id = 's02-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  /* a neutral coin (token): filled disc with an inner ring; variant 2 is the "other" token */
  function coin(svg, x, y, variant) {
    var g = svgEl('g', { transform: 'translate(' + x + ',' + y + ')' }, svg);
    var c = svgEl('circle', { r: 15, fill: variant === 2 ? C.bg : C.ink, stroke: variant === 2 ? C.ink : C.ink, 'stroke-width': 2.5 }, g);
    var i = svgEl('circle', { r: 8, fill: 'none', stroke: variant === 2 ? C.ink : C.bg, 'stroke-width': 2 }, g);
    return { g: g, outer: c, inner: i, x: x, y: y };
  }
  function moveCoin(K, x, y, opts) {
    opts = opts || {};
    var st = { x: K.x, y: K.y };
    return gsap.to(st, { x: x, y: y, duration: opts.duration || 0.6, ease: opts.ease || 'power2.inOut', delay: opts.delay || 0,
      onUpdate: function () { K.x = st.x; K.y = st.y; K.g.setAttribute('transform', 'translate(' + st.x.toFixed(1) + ',' + st.y.toFixed(1) + ')'); } });
  }
  var ICON = {
    hand: '<svg viewBox="0 0 44 44" fill="none" stroke="#A3ADBF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 22V9.5a3 3 0 0 1 6 0V20"/><path d="M22 18.5v-2a3 3 0 0 1 6 0V21"/><path d="M28 19.5a3 3 0 0 1 6 0V27c0 6-4 10-10 10h-2c-4 0-6.5-2-8.5-5L9 25.5a2.8 2.8 0 0 1 4.4-3.4L16 25"/></svg>',
    hook: '<svg viewBox="0 0 44 44" fill="none" stroke="#A3ADBF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="26" cy="8.5" r="3.5"/><path d="M26 12v17a8 8 0 0 1-16 0v-3"/><path d="M10 26l-3.5 4"/></svg>',
    inf: '<svg viewBox="0 0 44 44" fill="none" stroke="#A3ADBF" stroke-width="2.4" stroke-linecap="round"><path d="M22 22c-3.5-4.5-6-7-9.5-7a7 7 0 0 0 0 14c3.5 0 6-2.5 9.5-7zm0 0c3.5 4.5 6 7 9.5 7a7 7 0 0 0 0-14c-3.5 0-6 2.5-9.5 7z"/></svg>'
  };

  /* ================================================================ s02-01 */
  var slide1 = {
    id: 's02-01', title: 'DeFi in one picture', time: 30, steps: 2,
    notes: [
      'DeFi means decentralized finance. In place of a clerk at a bank counter, programs exchange money, hold it and put it to work, and lend it.',
      'The routers, vaults and lending pools in today\'s talk are all programs of this kind. A router swaps my tokens for other tokens, a vault puts the tokens I deposit to work, and in a lending pool people lend and borrow.',
      'Such a program is called a smart contract. It runs by itself on the blockchain, following fixed rules. Before these contracts can move a user\'s tokens, they first need the user\'s permission, an allowance. That allowance is what the next slide is about.'
    ],
    html:
      '<h1 class="t-h1">DeFi = [[programs]] instead of a bank counter</h1>' +
      '<div class="s02-cards" id="cards" data-in="none">' +
        '<div class="s02-card"><svg width="544" height="270" viewBox="0 0 544 270"></svg><div class="nm">Router</div><div class="ds">Swaps one token for another</div></div>' +
        '<div class="s02-card"><svg width="544" height="270" viewBox="0 0 544 270"></svg><div class="nm">Vault</div><div class="ds">Puts deposited tokens to work</div></div>' +
        '<div class="s02-card"><svg width="544" height="270" viewBox="0 0 544 270"></svg><div class="nm">Lending pool</div><div class="ds">Lend and borrow</div></div>' +
      '</div>' +
      '<p class="s02-line" style="top:822px" data-step="2">These programs are called <b>smart contracts</b>. They run by themselves on the blockchain.</p>',
    build: function (el, ctx) {
      var g = ctx.g = { cards: el.querySelectorAll('.s02-card'), boxes: [], mini: [] };
      var svgs = Array.prototype.map.call(g.cards, function (c) { return c.querySelector('svg'); });
      var BX = 300, BY = 136;
      svgs.forEach(function (svg, k) {
        /* EOAs around the contract, linked by faint dashed lines */
        var eo = k === 2 ? [[86, 136], [490, 136]] : [[86, 136]];
        if (k === 0) eo.push([480, 56], [486, 214]);
        if (k === 1) eo.push([474, 70], [480, 204]);
        eo.forEach(function (p) {
          svgEl('line', { x1: p[0], y1: p[1], x2: BX, y2: BY, stroke: C.ink3, 'stroke-width': 1.5, 'stroke-dasharray': '4 7', opacity: 0.55 }, svg);
        });
        var box = Comp.contract(ctx, svg, { x: BX, y: BY, size: 104 });
        eo.forEach(function (p) { Comp.eoa(ctx, svg, { x: p[0], y: p[1], r: 15 }); });
        g.boxes.push(box);
      });
      /* router: a coin goes in, a different coin comes back */
      g.r1 = coin(svgs[0], 86, 136, 1); g.r2 = coin(svgs[0], BX, BY, 2);
      gsap.set([g.r1.g, g.r2.g], { autoAlpha: 0 });
      /* vault: a coin sinks in, the level inside the box rises */
      g.v1 = coin(svgs[1], 86, 136, 1);
      var clipId = 's02-vclip-' + (++CLIP_N);
      var cp = svgEl('clipPath', { id: clipId }, svgEl('defs', {}, svgs[1]));
      svgEl('rect', { x: BX - 50, y: BY - 50, width: 100, height: 100, rx: 22 }, cp);
      g.level = svgEl('rect', { x: BX - 52, y: BY + 52, width: 104, height: 0, fill: C.ink, 'fill-opacity': 0.14, 'clip-path': 'url(#' + clipId + ')' }, svgs[1]);
      gsap.set(g.v1.g, { autoAlpha: 0 });
      /* lending pool: a coin leaves for the borrower and comes back */
      g.l1 = coin(svgs[2], BX, BY, 1);
      gsap.set(g.l1.g, { autoAlpha: 0 });
      gsap.set(g.cards, { autoAlpha: 0 });
      g.BX = BX; g.BY = BY;
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        /* bento: cards rise left to right; each mini animation plays once */
        tl.fromTo(g.cards, { autoAlpha: 0, y: 60 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.12 }, 0);
        /* router */
        tl.set(g.r1.g, { autoAlpha: 1 }, 0.7);
        tl.add(moveCoin(g.r1, g.BX, g.BY, { duration: 0.6 }), 0.7);
        tl.to(g.r1.g, { autoAlpha: 0, duration: 0.15 }, 1.25);
        tl.add(g.boxes[0].flash(), 1.25);
        tl.set(g.r2.g, { autoAlpha: 1 }, 1.3);
        tl.add(moveCoin(g.r2, 86, 136, { duration: 0.6, ease: 'power2.out' }), 1.3);
        tl.to(g.r2.g, { autoAlpha: 0, duration: 0.3 }, 2.2);
        /* vault */
        tl.set(g.v1.g, { autoAlpha: 1 }, 0.9);
        tl.add(moveCoin(g.v1, g.BX, g.BY - 96, { duration: 0.55, ease: 'power2.out' }), 0.9);
        tl.add(moveCoin(g.v1, g.BX, g.BY + 10, { duration: 0.45, ease: 'power2.in' }), 1.5);
        tl.to(g.v1.g, { autoAlpha: 0, duration: 0.2 }, 1.85);
        tl.to(g.level, { attr: { y: g.BY + 6, height: 46 }, duration: 0.7, ease: 'power2.out' }, 1.9);
        /* lending pool */
        tl.set(g.l1.g, { autoAlpha: 1 }, 1.1);
        tl.add(moveCoin(g.l1, 490, 136, { duration: 0.6 }), 1.1);
        tl.add(moveCoin(g.l1, g.BX, g.BY, { duration: 0.6 }), 1.95);
        tl.to(g.l1.g, { autoAlpha: 0, duration: 0.2 }, 2.55);
      }
      if (i === 2) {
        /* the three { } flash together: all of them are smart contracts */
        g.boxes.forEach(function (b) { tl.add(b.flash(), 0.35); });
        g.boxes.forEach(function (b) { tl.fromTo(b.rect, { stroke: C.ink }, { stroke: C.ink2, duration: 0.9, ease: 'power2.out' }, 0.35); });
      }
    }
  };

  /* ================================================================ s02-02 */
  var P_L = 96, P_R = 984, P_W = 840, P_H = 572;
  var slide2 = {
    id: 's02-02', title: 'Transfers and allowances differ', time: 45, steps: 5,
    tags: function (step) { return step >= 2 ? ['example'] : []; },
    notes: [
      'Let me put two kinds of record side by side. On the left is a transfer, on the right an allowance.',
      'A transfer means tokens actually move. The coins flow from the sender to the recipient.',
      'An allowance is different. The token owner promises a contract: "you may take up to this much of my tokens." The owner grants it with the approve function of the ERC-20 standard, or with permit, the signature-based approval of its extension EIP-2612, and either way the same record, an Approval event, is left behind. So this arrow does not flow; it just stays in place. The 1,000 USDC is an example for the explanation.',
      'Later, the spender contract can call transferFrom to actually move the owner\'s tokens, up to the approved amount. The value this study uses is the amount written in the latest approval record.',
      'For the same owner, the same contract and the same token, the most recent approval overwrites the earlier one. So for each owner, spender and token, this study uses only the latest allowance as an edge, and it counts only allowances set in the twelve months before the day the scores are frozen.',
      'Approving an amount of zero revokes the allowance. A revoked allowance leaves no edge.'
    ],
    html:
      '<h1 class="t-h1">Transfers and allowances are different</h1>' +
      '<div class="s02-panel" id="pl" data-in="none" style="left:' + P_L + 'px">' +
        '<svg class="frame" width="' + P_W + '" height="' + P_H + '"></svg>' +
        '<div class="hd c-xfer">Transfer<small>Transfer event</small></div>' +
        '<div class="tx">Tokens actually move<span class="sub">sender → recipient</span></div>' +
        '<svg class="fig" width="' + P_W + '" height="300" viewBox="0 0 ' + P_W + ' 300"></svg>' +
      '</div>' +
      '<div class="s02-panel" id="pr" data-in="none" style="left:' + P_R + 'px">' +
        '<svg class="frame" width="' + P_W + '" height="' + P_H + '"></svg>' +
        '<div class="hd c-allow">Allowance<small>Approval event</small></div>' +
        '<div class="tx">A promise: ‘you may spend up to this much of my tokens’<span class="sub">owner → spender contract</span></div>' +
        '<svg class="fig" width="' + P_W + '" height="300" viewBox="0 0 ' + P_W + ' 300"></svg>' +
      '</div>' +
      '<div class="s02-codes" id="codes" data-in="none">' +
        '<span class="c">approve(spender, amount)</span><span class="c">permit(<i>signature</i>)<i class="ext">extension EIP-2612</i></span>' +
        '<span class="grp"><span class="lb">revoke =</span><span class="c" id="revoke">approve(spender, 0)</span></span></div>' +
      '<p class="s02-bottom" data-step="4" data-in="words">The latest approval [[overwrites]] the earlier one</p>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var pl = el.querySelector('#pl'), pr = el.querySelector('#pr');
      g.frames = [pl, pr].map(function (p) {
        return svgEl('rect', { x: 1, y: 1, width: P_W - 2, height: P_H - 2, rx: 24, fill: 'rgba(16,21,31,.55)', stroke: '#3A4458', 'stroke-width': 2 }, p.querySelector('svg.frame'));
      });
      var fl = pl.querySelector('svg.fig'), fr = pr.querySelector('svg.fig');
      var Y = 130, X0 = 130, X1 = 700;
      /* left: sender -> receiving contract, G2 */
      Comp.eoa(ctx, fl, { x: X0, y: Y, r: 20, label: 'sender' });
      Comp.contract(ctx, fl, { x: X1, y: Y, size: 84, label: 'receiving contract' });
      g.xfer = Comp.arrow(ctx, fl, { from: [X0, Y], to: [X1, Y], kind: 'xfer', width: 5, head: 18, shorten: [30, 56], hidden: true });
      /* right: owner -> spender, G1 */
      g.owner = Comp.eoa(ctx, fr, { x: X0, y: Y, r: 20, label: 'owner' });
      g.spender = Comp.contract(ctx, fr, { x: X1, y: Y, size: 84, label: 'spender contract' });
      g.allow = Comp.arrow(ctx, fr, { from: [X0, Y], to: [X1, Y], kind: 'allow', width: 5, head: 18, shorten: [30, 56], hidden: true,
        label: 'up to 1,000 USDC', labelOffset: 30, labelSize: 28 });
      g.ex = svgEl('text', { x: (X0 + X1) / 2, y: Y - 74, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 20, 'class': 'svg-mono' }, fr);
      g.ex.textContent = 'Example';
      gsap.set(g.ex, { autoAlpha: 0 });
      /* transferFrom: a thin dashed sky path under the allowance, one coin pulled along it */
      var mid = (X0 + X1) / 2;
      g.tf = svgEl('path', { d: 'M' + (X0 + 26) + ',' + (Y + 16) + ' Q' + mid + ',' + (Y + 170) + ' ' + (X1 - 52) + ',' + (Y + 24), fill: 'none', stroke: C.xfer, 'stroke-width': 2, 'stroke-dasharray': '6 8', opacity: 0.85 }, fr);
      g.tfLbl = svgEl('text', { x: mid, y: Y + 128, 'text-anchor': 'middle', fill: C.xfer, 'font-size': 20, 'class': 'svg-mono' }, fr);
      g.tfLbl.textContent = 'later: transferFrom';
      g.tfCoin = svgEl('circle', { r: 9, fill: C.xfer, stroke: C.bg, 'stroke-width': 2 }, fr);
      g.tfNote = svgEl('text', { x: mid, y: Y + 174, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 21 }, fr);
      g.tfNote.textContent = 'Tag = amount of the latest approval (the value this study uses)';
      gsap.set([g.tf, g.tfLbl, g.tfCoin, g.tfNote], { autoAlpha: 0 });
      /* after a revoke: a ghost of the arrow */
      g.ghost = svgEl('line', { x1: X0 + 30, y1: Y, x2: X1 - 56, y2: Y, stroke: C.ink3, 'stroke-width': 2, 'stroke-dasharray': '3 9', opacity: 0.6 }, fr);
      g.ghostLbl = svgEl('text', { x: mid, y: Y - 22, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 22 }, fr);
      g.ghostLbl.textContent = 'revoked allowance → no edge';
      gsap.set([g.ghost, g.ghostLbl], { autoAlpha: 0 });
      g.codes = el.querySelector('#codes');
      g.revoke = el.querySelector('#revoke');
      gsap.set(g.codes, { autoAlpha: 0 });
      g.X0 = X0; g.X1 = X1; g.Y = Y;
    },
    enter: function (el, ctx) {
      /* the two panel frames are drawn at the same time */
      var tl = ctx.tl(), g = ctx.g;
      var L = 2 * (P_W + P_H);
      tl.fromTo(g.frames, { strokeDasharray: L + ' ' + L, strokeDashoffset: L, fillOpacity: 0 }, { strokeDashoffset: 0, duration: 0.9, ease: 'power2.inOut' }, 0.1);
      tl.to(g.frames, { fillOpacity: 1, duration: 0.5 }, 0.7);
      tl.call(function () { g.frames.forEach(function (f) { f.style.strokeDasharray = ''; f.style.strokeDashoffset = ''; }); }, null, 1.05);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) tl.add(g.xfer.draw({ duration: 0.7 }), 0);
      if (i === 2) {
        tl.add(g.allow.draw({ duration: 0.7 }), 0);
        tl.fromTo(g.ex, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.7);
        tl.fromTo(g.codes, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power3.out' }, 0.9);
      }
      if (i === 3) {
        /* later: the spender pulls one coin from the owner; the tag keeps the last approval's amount */
        var L = g.tf.getTotalLength();
        tl.set([g.tf, g.tfLbl], { autoAlpha: 1 }, 0);
        tl.fromTo(g.tf, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' }, 0);
        tl.call(function () { g.tf.style.strokeDasharray = ''; g.tf.style.strokeDashoffset = ''; g.tf.setAttribute('stroke-dasharray', '6 8'); }, null, 0.62);
        tl.fromTo(g.tfLbl, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0.3);
        var st = { t: 0 };
        tl.set(g.tfCoin, { autoAlpha: 1 }, 0.65);
        tl.fromTo(st, { t: 0 }, { t: 1, duration: 0.9, ease: 'power2.inOut', onUpdate: function () {
          var p = g.tf.getPointAtLength(st.t * L); g.tfCoin.setAttribute('cx', p.x); g.tfCoin.setAttribute('cy', p.y);
        } }, 0.65);
        tl.to(g.tfCoin, { autoAlpha: 0, duration: 0.2 }, 1.55);
        tl.add(g.spender.flash(), 1.5);
        tl.fromTo(g.tfNote, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.4 }, 1.7);
      }
      if (i === 4) {
        /* a new approval overwrites the old one: only the amount on the tag changes */
        tl.to([g.tf, g.tfLbl, g.tfNote], { autoAlpha: 0.35, duration: 0.3 }, 0);
        tl.fromTo(g.allow.key, { scale: 1.9, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.5, ease: 'power3.out', immediateRender: false }, 0.1);
        tl.add(g.allow.setLabel('up to 500 USDC'), 0.25);
      }
      if (i === 5) {
        /* revoke = approve(spender, 0): the arrow breaks off from the spender end */
        tl.to([g.tf, g.tfLbl, g.tfNote, g.ex], { autoAlpha: 0, duration: 0.3 }, 0);
        tl.add(g.allow.cut({ duration: 0.4 }), 0.1);
        tl.add(Comp.hilite(ctx, g.revoke, { color: 'rgba(245,180,60,.28)' }), 0.15);
        tl.fromTo(g.revoke, { scale: 1.08 }, { scale: 1, duration: 0.5, ease: 'power3.out', immediateRender: false }, 0.15);
        tl.fromTo([g.ghost, g.ghostLbl], { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, 0.7);
      }
    }
  };

  /* ================================================================ s02-03 */
  function ringPoints(rnd, cx, cy, n, r0, r1, a0, a1) {
    var pts = [];
    for (var i = 0; i < n; i++) {
      var a = a0 + (a1 - a0) * (i + 0.5) / n + (rnd() - 0.5) * 0.09;
      var r = r0 + (r1 - r0) * rnd();
      pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]);
    }
    return pts;
  }
  var slide3 = {
    id: 's02-03', title: 'Allowances look like trust, but', time: 40, steps: 3,
    notes: [
      'An approval entrusts my tokens to a contract, so it can be read as trust in the contract that receives it. It is like the way a link on the web can be read as a citation.',
      'When many owners approve one contract, that contract looks as if it has received many endorsements.',
      'But we have to be careful. An approval clicked by someone tricked by a phishing site leaves exactly the same record as an honest one. From the arrows alone, the two boxes cannot be told apart.',
      'People also approve simply because it is convenient. In this study\'s data, too, ' + fmt(UNL_SHARE * 100, 1) + '% of the about ' + fmt(LATEST / 1e6, 2) + ' million latest allowances set in the twelve months up to 30 June 2026 were unlimited approvals. So this thesis treats an allowance not as firm evidence of trust but as a signal that "can be read" as an endorsement.'
    ],
    html:
      '<h1 class="t-h1">Approval = [[entrusting]] my tokens</h1>' +
      '<p class="s02-sub">So it can be read as an edge of endorsement (trust placed in the contract), the way a link on a web page is read as a citation.</p>' +
      '<svg id="fig" class="abs" data-in="none" style="left:96px;top:250px;overflow:visible" width="1040" height="700" viewBox="0 0 1040 700"></svg>' +
      '<div class="s02-claim" id="claim"><div class="k">Allowance edge =</div><div class="v" id="belief">Evidence of trust</div></div>' +
      '<div class="s02-warn" id="warn" data-in="none">' +
        '<div class="w">' + ICON.hand + '<div class="t">Some approve just for convenience</div></div>' +
        '<div class="w">' + ICON.hook + '<div class="t">A tricked approval leaves the same record</div></div>' +
        '<div class="w">' + ICON.inf + '<div><div class="t">Unlimited approvals are common</div>' +
          '<div class="big"><span class="n" id="pct">' + fmt(UNL_SHARE * 100, 1) + '%</span><span class="u">of latest allowances</span></div>' +
          '<div class="s02-src">' + fmt(UNL) + ' / ' + fmt(LATEST) + '<br>positive latest allowances at T_obs, set in the 12-month score window</div></div></div>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var svg = el.querySelector('#fig'), rnd = ctx.rng(42);
      var A = [250, 360], B = [770, 360];
      g.layerA = svgEl('g', {}, svg); g.layerB = svgEl('g', {}, svg);
      function cluster(layer, c, seed, dashed) {
        var r2 = ctx.rng(seed);
        var pts = ringPoints(r2, c[0], c[1], 40, 170, 236, -Math.PI, Math.PI);
        var arrows = [], dots = [];
        pts.forEach(function (p) {
          arrows.push(Comp.arrow(ctx, layer, { from: p, to: c, kind: 'allow', width: 2, head: 10, shorten: [9, 50], hidden: true, glow: false }));
        });
        pts.forEach(function (p) { dots.push(Comp.eoa(ctx, layer, { x: p[0], y: p[1], r: 7 })); });
        var box = Comp.contract(ctx, layer, { x: c[0], y: c[1], size: 76, dashed: dashed, stroke: dashed ? C.hi : null });
        return { arrows: arrows, dots: dots, box: box };
      }
      g.A = cluster(g.layerA, A, 11, false);
      g.B = cluster(g.layerB, B, 23, true);
      gsap.set(g.layerB, { autoAlpha: 0 });
      void rnd;
      /* the two boxes look the same: an arc with a question mark */
      g.q = svgEl('g', {}, svg);
      g.qPath = svgEl('path', { d: 'M' + A[0] + ',' + (A[1] - 70) + ' C' + A[0] + ',' + 40 + ' ' + B[0] + ',' + 40 + ' ' + B[0] + ',' + (B[1] - 70), fill: 'none', stroke: C.ink2, 'stroke-width': 1.8, 'stroke-dasharray': '5 7' }, g.q);
      var qc = svgEl('g', { transform: 'translate(' + ((A[0] + B[0]) / 2) + ',' + 110 + ')' }, g.q);
      svgEl('circle', { r: 24, fill: C.bg2, stroke: C.ink2, 'stroke-width': 2 }, qc);
      var qt = svgEl('text', { x: 0, y: 2, 'text-anchor': 'middle', 'dominant-baseline': 'middle', fill: C.ink, 'font-size': 28, 'font-weight': 800 }, qc);
      qt.textContent = '?';
      g.qText = svgEl('text', { x: (A[0] + B[0]) / 2, y: 62, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 26 }, g.q);
      g.qText.textContent = 'The arrows of the two boxes look the same';
      g.lblA = svgEl('text', { x: A[0], y: A[1] + 290, 'text-anchor': 'middle', fill: C.ink2, 'font-size': 24, 'font-weight': 600 }, svg);
      g.lblA.textContent = 'honest contract';
      g.lblB = svgEl('text', { x: B[0], y: B[1] + 290, 'text-anchor': 'middle', fill: C.hi, 'font-size': 24, 'font-weight': 600 }, svg);
      g.lblB.textContent = 'phishing contract (approved by deception)';
      gsap.set([g.q, g.lblA, g.lblB], { autoAlpha: 0 });
      g.warn = el.querySelectorAll('#warn .w');
      gsap.set(el.querySelector('#warn'), { autoAlpha: 1 });
      gsap.set(g.warn, { autoAlpha: 0 });
      g.belief = el.querySelector('#belief');
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      ctx.tl().add(g.A.box.pop(), 0.4);
      g.A.dots.forEach(function (d, k) { gsap.set(d.g, { autoAlpha: 0 }); });
      ctx.tl().fromTo(g.A.dots.map(function (d) { return d.g; }), { autoAlpha: 0, scale: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: 'back.out(2)', stagger: 0.012 }, 0.5);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        /* 40 owners approve the same contract, one after another; the box grows a little */
        g.A.arrows.forEach(function (A, k) { tl.add(A.draw({ duration: 0.45 }), k * 0.03); });
        tl.to(g.A.box.g, { scale: 1.16, transformOrigin: '50% 50%', duration: 1.4, ease: 'power1.inOut' }, 0.2);
        tl.fromTo(g.lblA, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4 }, 1.4);
      }
      if (i === 2) {
        tl.set(g.layerB, { autoAlpha: 1 }, 0);
        tl.add(g.B.box.pop(), 0);
        tl.fromTo(g.B.dots.map(function (d) { return d.g; }), { autoAlpha: 0, scale: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: 'back.out(2)', stagger: 0.01 }, 0.1);
        g.B.arrows.forEach(function (A, k) { tl.add(A.draw({ duration: 0.45 }), 0.5 + k * 0.03); });
        tl.to(g.B.box.g, { scale: 1.16, transformOrigin: '50% 50%', duration: 1.4, ease: 'power1.inOut' }, 0.6);
        tl.fromTo(g.lblB, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4 }, 1.9);
        var L = g.qPath.getTotalLength();
        tl.set(g.q, { autoAlpha: 1 }, 2.1);
        tl.fromTo(g.qPath, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.7, ease: 'power2.inOut' }, 2.1);
        tl.call(function () { g.qPath.style.strokeDasharray = ''; g.qPath.style.strokeDashoffset = ''; }, null, 2.82);
        tl.fromTo(g.q.children[1], { scale: 0.4, autoAlpha: 0, transformOrigin: '50% 50%' }, { scale: 1, autoAlpha: 1, duration: 0.4, ease: 'back.out(2)' }, 2.5);
        tl.fromTo(g.qText, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: 0.4 }, 2.6);
      }
      if (i === 3) {
        /* evidence of trust -> read as endorsement: strike and rewrite; then the three cautions; the unlimited share counts up */
        tl.add(Comp.strike(ctx, g.belief, '<b>Read</b> as endorsement<small>Not firm evidence</small>'), 0);
        tl.fromTo(g.warn, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.55, ease: 'power3.out', stagger: 0.16 }, 1.2);
        tl.add(ctx.count(el.querySelector('#pct'), 0, UNL_SHARE * 100, { decimals: 1, suffix: '%', final: fmt(UNL_SHARE * 100, 1) + '%', duration: 1.4 }), 1.55);
      }
    }
  };

  /* ================================================================ s02-04 */
  var G4 = {
    nodes: [
      { id: 'E1', x: 90, y: 110, kind: 'eoa' }, { id: 'E2', x: 70, y: 400, kind: 'eoa' }, { id: 'E3', x: 260, y: 640, kind: 'eoa' },
      { id: 'E4', x: 560, y: 70, kind: 'eoa' }, { id: 'E5', x: 800, y: 560, kind: 'eoa' }, { id: 'E6', x: 500, y: 660, kind: 'eoa' },
      { id: 'C1', x: 320, y: 230, kind: 'contract' }, { id: 'C2', x: 600, y: 380, kind: 'contract' },
      { id: 'C3', x: 300, y: 480, kind: 'contract' }, { id: 'C4', x: 790, y: 190, kind: 'contract' }
    ],
    edges: [
      { from: 'E1', to: 'C1', kind: 'allow' }, { from: 'E2', to: 'C1', kind: 'allow' }, { from: 'E2', to: 'C3', kind: 'xfer' },
      { from: 'E3', to: 'C3', kind: 'allow' }, { from: 'C3', to: 'C2', kind: 'xfer' }, { from: 'C1', to: 'C2', kind: 'allow' },
      { from: 'E4', to: 'C4', kind: 'allow' }, { from: 'E4', to: 'C1', kind: 'xfer' }, { from: 'C2', to: 'E5', kind: 'xfer' },
      { from: 'E6', to: 'C2', kind: 'allow' }, { from: 'C4', to: 'C2', kind: 'xfer' }
    ],
    scan: ['E1', 'C1', 'E2', 'C3', 'E4', 'C4', 'E5', 'C2', 'E3', 'E6']
  };
  function bracketD(x, y, h, arm) {
    var a = arm || Math.min(16, h * 0.4);
    return 'M' + (x - h) + ',' + (y - h + a) + ' V' + (y - h) + ' H' + (x - h + a) +
      ' M' + (x + h - a) + ',' + (y - h) + ' H' + (x + h) + ' V' + (y - h + a) +
      ' M' + (x + h) + ',' + (y + h - a) + ' V' + (y + h) + ' H' + (x + h - a) +
      ' M' + (x - h + a) + ',' + (y + h) + ' H' + (x - h) + ' V' + (y + h - a);
  }
  var slide4 = {
    id: 's02-04', title: 'The scored objects are contracts', time: 35, steps: 3,
    notes: [
      'There is one thing I must point out here. The graph mixes two kinds of address. A circle is an externally owned account, an EOA, which a person controls with a private key, and a square is a smart contract.',
      'Every address this study scored and evaluated is a smart contract. EOAs appear in the graph only as owners, senders or recipients, and they receive no score.',
      'Score badges go only on the squares, that is, on contracts. The circles get only the label "endpoint".',
      'We decided whether an address is a contract by checking whether program code sits at that address. With eth_getCode we looked for code at block ' + fmt(GETCODE_BLOCK) + ' for the cohort candidates, and at later blocks within three hours for the remaining holdout spenders and GMX accounts. An address whose code is only an EIP-7702 delegation designator was counted as an EOA.'
    ],
    html:
      '<h1 class="t-h1">What gets scored: [[smart contracts]]</h1>' +
      '<p class="s02-l" style="top:236px" data-step="2">Externally owned accounts (EOAs, accounts controlled by a private key) appear only as endpoints of edges: owners, senders, recipients</p>' +
      '<p class="s02-l note" id="fn" style="top:430px" data-step="2"><span>Score badges go only on squares (<b class="ink">contracts</b>)</span></p>' +
      '<p class="s02-small" data-step="3">Contract check: we looked for program code at the address</p>' +
      '<svg id="g4" class="abs" data-in="none" style="left:964px;top:178px;overflow:visible" width="860" height="720" viewBox="0 0 860 720"></svg>' +
      '<div class="s02-legend" id="leg">' +
        '<span><svg width="24" height="24"><circle cx="12" cy="12" r="9" fill="none" stroke="' + C.ink3 + '" stroke-width="2.5"/></svg>EOA</span>' +
        '<span><svg width="26" height="26"><rect x="2" y="2" width="22" height="22" rx="5" fill="#10151F" stroke="#A3ADBF" stroke-width="2"/></svg>contract</span>' +
        '<span><svg width="44" height="10"><line x1="2" y1="5" x2="42" y2="5" stroke="#F5B43C" stroke-width="3"/></svg>allowance</span>' +
        '<span><svg width="44" height="10"><line x1="2" y1="5" x2="42" y2="5" stroke="#3CC4FF" stroke-width="3"/></svg>transfer</span>' +
      '</div>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var svg = el.querySelector('#g4');
      g.G = Comp.graph(ctx, svg, {
        nodes: G4.nodes.map(function (n) { return { id: n.id, x: n.x, y: n.y, kind: n.kind, size: n.kind === 'eoa' ? 15 : 66 }; }),
        edges: G4.edges.map(function (e) { return { from: e.from, to: e.to, kind: e.kind, width: 3, head: 14, flow: false }; }),
        showWeights: false, hidden: true
      });
      g.G.edges.forEach(function (A) { A.glow(false); });
      /* tags of the EOAs: under the dot for the bottom row (their arrows go up); also under E2,
         whose wider English tag would otherwise cross its arrow up to C1 */
      Object.keys(g.G.nodes).forEach(function (id) {
        var N = g.G.nodes[id]; if (N.kind !== 'eoa') return;
        N.tag('endpoint'); gsap.set(N.tagT, { autoAlpha: 0 });
        if (N.y > 500 || id === 'E2') N.tagT.setAttribute('y', N.r + 30);
      });
      g.shiftEls = [svg, el.querySelector('#leg')];
      g.SHIFT = -420;
      gsap.set(g.shiftEls, { x: g.SHIFT });
      g.scanG = svgEl('path', { d: bracketD(G4.nodes[0].x, G4.nodes[0].y, 30), fill: 'none', stroke: C.ink2, 'stroke-width': 3, 'stroke-linecap': 'round' }, svg);
      g.lockLayer = svgEl('g', {}, svg);
      gsap.set(g.scanG, { autoAlpha: 0 });
    },
    enter: function (el, ctx) {
      var g = ctx.g;
      ctx.tl().add(g.G.drawIn({ stagger: 0.05 }), 0.15);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        /* the scan brackets hop from point to point and lock onto contracts only */
        var st = { x: G4.nodes[0].x, y: G4.nodes[0].y, h: 26 };
        var draw = function () { g.scanG.setAttribute('d', bracketD(st.x, st.y, st.h)); };
        tl.set(g.scanG, { autoAlpha: 1 }, 0);
        var t = 0;
        G4.scan.forEach(function (id) {
          var N = g.G.nodes[id], isC = N.kind === 'contract', h = isC ? 50 : 26;
          tl.to(st, { x: N.x, y: N.y, h: h, duration: 0.22, ease: 'power2.inOut', onUpdate: draw }, t);
          if (isC) {
            var lock = svgEl('path', { d: bracketD(N.x, N.y, 50), fill: 'none', stroke: C.ink, 'stroke-width': 3, 'stroke-linecap': 'round' }, g.lockLayer);
            gsap.set(lock, { autoAlpha: 0 });
            tl.set(lock, { autoAlpha: 1 }, t + 0.22);
            tl.fromTo(lock, { scale: 1.25, svgOrigin: N.x + ' ' + N.y }, { scale: 1, duration: 0.25, ease: 'back.out(2)', immediateRender: false }, t + 0.22);
            tl.add(N.badge('score', { color: C.ink }), t + 0.3);
          } else {
            tl.add(N.tag('endpoint'), t + 0.22);
          }
          t += 0.3;
        });
        tl.to(g.scanG, { autoAlpha: 0, duration: 0.25 }, t);
      }
      if (i === 2) {
        /* the graph glides right to make room for the words */
        tl.to(g.shiftEls, { x: 0, duration: 0.8, ease: 'power2.inOut' }, 0);
        /* the badge line points at a contract's score badge; every badge answers */
        var fn = el.querySelector('#fn span'), N = g.G.nodes.C1;
        tl.add(function () {
          ctx.add(function () {
            if (!N.badgeG) return;
            Comp.leader(ctx, fn, N.badgeG, { color: 'ink3', dashed: true, bend: 0.25, fromSide: 'right', toSide: 'left' }).draw({ duration: 0.8 });
          });
        }, 1.6);
        ['C1', 'C2', 'C3', 'C4'].forEach(function (id, k) {
          var B = g.G.nodes[id].badgeG; if (!B) return;
          tl.fromTo(B, { scale: 1.3, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.45, ease: 'back.out(2)', immediateRender: false }, 2.3 + k * 0.08);
        });
      }
    }
  };

  /* ================================================================ s02-05 */
  var slide5 = {
    id: 's02-05', title: 'The setting: Arbitrum One', time: 30, steps: 3,
    notes: [
      'The study takes place on Arbitrum One.',
      'Arbitrum One is a rollup that runs on top of Ethereum. Because it bundles transactions and posts them to Ethereum together, its fees are low, and people transact often. Its chain ID is 42161.',
      'Every approval and transfer record here can be read by anyone in the public data of Google BigQuery. The amber dots are approval records and the sky-blue dots are transfer records.',
      'There is also a reason for looking at only one chain. If one person holds the same address on several chains, it shows up as separate nodes, so comparing within one chain is cleaner. Now I will lay this plate on its side and turn it into a time axis.'
    ],
    html:
      '<h1 class="t-h1">The setting: Arbitrum One</h1>' +
      '<div class="s02-pts" id="pts">' +
        '<div class="p" data-step="1"><span class="ic"></span><span>A <b>rollup</b> that runs on Ethereum · chain ID <span class="mono">' + CHAIN_ID + '</span></span></div>' +
        '<div class="p" data-step="1"><span class="ic"></span><span>Low fees, so people transact often</span></div>' +
        '<div class="p" data-step="2"><span class="ic"></span><span>All records: public <b>BigQuery</b> logs</span></div>' +
        '<div class="p" data-step="3"><span class="ic"></span><span>One chain only → one owner’s addresses on several chains do not get mixed</span></div>' +
      '</div>' +
      '<div class="s02-scene" id="scene" data-in="none"><div class="s02-world" id="world">' +
        '<div class="s02-plate eth" id="eth"><i class="s02-mark" style="left:0;top:0"></i></div>' +
        '<div class="s02-plate arb" id="arb"><i class="s02-mark" style="right:0;top:0"></i><i class="s02-mark" style="right:0;bottom:0"></i><i class="s02-mark" style="left:0;bottom:0"></i></div>' +
        '<div class="s02-batch" id="batch"></div>' +
      '</div></div>' +
      '<div class="s02-plbl" id="lblArb" data-in="none">Arbitrum One<small>rollup · ' + CHAIN_ID + '</small></div>' +
      '<div class="s02-plbl ink-2" id="lblEth" data-in="none">Ethereum</div>' +
      '<svg id="barrel" class="abs" data-in="none" style="left:1480px;top:650px;overflow:visible" width="240" height="250" viewBox="0 0 240 250"></svg>' +
      '<div id="parts" class="abs" data-in="none" style="left:740px;top:150px"></div>' +
      '<div class="s02-axis" id="axis" data-shared="time-axis" data-in="none"></div>',
    build: function (el, ctx) {
      var g = ctx.g = { rx: 58, rz: -40 };
      g.world = el.querySelector('#world');
      g.eth = el.querySelector('#eth'); g.arb = el.querySelector('#arb'); g.batch = el.querySelector('#batch');
      g.setWorld = function () { g.world.style.transform = 'rotateX(' + g.rx + 'deg) rotateZ(' + g.rz + 'deg)'; };
      g.setWorld();
      gsap.set(g.eth, { z: -420, autoAlpha: 0 });
      gsap.set(g.arb, { z: 620, autoAlpha: 0 });
      gsap.set(g.batch, { z: 170, autoAlpha: 0 });
      /* the public-log barrel */
      var b = el.querySelector('#barrel'), cx = 120, top = 40, H = 150, rx = 96, ry = 24;
      var bg = svgEl('g', {}, b);
      svgEl('path', { d: 'M' + (cx - rx) + ',' + top + ' V' + (top + H) + ' A' + rx + ',' + ry + ' 0 0 0 ' + (cx + rx) + ',' + (top + H) + ' V' + top, fill: C.bg2, stroke: C.ink2, 'stroke-width': 2 }, bg);
      [0.33, 0.66].forEach(function (f) {
        svgEl('path', { d: 'M' + (cx - rx) + ',' + (top + H * f) + ' A' + rx + ',' + ry + ' 0 0 0 ' + (cx + rx) + ',' + (top + H * f), fill: 'none', stroke: C.ink3, 'stroke-width': 1.5 }, bg);
      });
      svgEl('ellipse', { cx: cx, cy: top, rx: rx, ry: ry, fill: C.bg3, stroke: C.ink2, 'stroke-width': 2 }, bg);
      var t1 = svgEl('text', { x: cx, y: top + H + ry + 40, 'text-anchor': 'middle', fill: C.ink, 'font-size': 24, 'font-weight': 700 }, bg);
      t1.textContent = 'Public logs';
      var t2 = svgEl('text', { x: cx, y: top + H + ry + 70, 'text-anchor': 'middle', fill: C.ink3, 'font-size': 20, 'class': 'svg-mono' }, bg);
      t2.textContent = 'BigQuery public data';
      g.barrel = b; g.barrelTop = [1480 + cx, 650 + top];
      gsap.set(b, { autoAlpha: 0 });
      gsap.set([el.querySelector('#lblArb'), el.querySelector('#lblEth')], { autoAlpha: 0 });
      g.axis = el.querySelector('#axis');
      gsap.set(g.axis, { autoAlpha: 0 });
      /* particles: approval logs (amber) and transfer logs (sky), in the ratio of the
         revised ego rows of the T_obs score window (85,986,562 : 442,722,039 ≈ 1 : 5.1) */
      var rows = (((DATA.scale || {}).revised || {}).rows || {}).revised_ego || {};
      g.pA = rows.approvals && rows.transfers ? rows.approvals / (rows.approvals + rows.transfers) : 0.163;
      g.K = Comp.canvas(ctx, el.querySelector('#parts'), { w: 1000, h: 760, onResize: function () { if (g.drawParts) g.drawParts(); } });
      g.parts = []; g.rnd = ctx.rng(7); g.spawn = false;
    },
    enter: function (el, ctx) {
      gsap.set(ctx.g.world, { autoAlpha: 1 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      function place(lbl, mark, dx, dy) {
        var r = ctx.rect(mark); lbl.style.left = (r.x + dx) + 'px'; lbl.style.top = (r.y + dy) + 'px';
      }
      if (i === 1) {
        /* Ethereum rises from below and settles; Arbitrum lands on top of it */
        tl.fromTo(g.eth, { z: -420, autoAlpha: 0 }, { z: 0, autoAlpha: 1, duration: 0.8, ease: 'power3.out' }, 0);
        tl.fromTo(g.arb, { z: 620, autoAlpha: 0 }, { z: 170, autoAlpha: 1, duration: 0.8, ease: 'power3.out' }, 0.45);
        /* a rollup posts a batch down to Ethereum (once) */
        tl.fromTo(g.batch, { z: 172, autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, 1.4);
        tl.to(g.batch, { z: 4, duration: 0.7, ease: 'power2.in' }, 1.6);
        tl.to(g.batch, { autoAlpha: 0, duration: 0.4 }, 2.3);
        tl.call(function () {
          var marks = g.arb.querySelectorAll('.s02-mark');
          place(el.querySelector('#lblArb'), marks[1], 24, -46);
          var lE = el.querySelector('#lblEth'), em = ctx.rect(g.eth.querySelector('.s02-mark'));
          lE.style.left = (em.x - 150) + 'px'; lE.style.top = (em.y + 26) + 'px';
        }, null, 1.3);
        tl.fromTo([el.querySelector('#lblArb'), el.querySelector('#lblEth')], { autoAlpha: 0, x: -12 }, { autoAlpha: 1, x: 0, duration: 0.45, ease: 'power3.out', stagger: 0.1 }, 1.35);
      }
      if (i === 2) {
        /* log particles fall from the Arbitrum plate into the public-log barrel */
        tl.fromTo(g.barrel, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power3.out' }, 0);
        var marks = g.arb.querySelectorAll('.s02-mark');
        var a = ctx.rect(marks[1]), b = ctx.rect(marks[2]);
        var ox = 740, oy = 150;
        /* the lower-right edge of the Arbitrum plate (the half nearest the barrel) */
        g.src = [[a.cx - ox, a.cy - oy], [a.cx + (b.cx - a.cx) * 0.55 - ox, a.cy + (b.cy - a.cy) * 0.55 - oy]];
        g.dst = [g.barrelTop[0] - ox, g.barrelTop[1] - oy];
        var K = g.K;
        g.drawParts = function () {
          K.clear();
          var c = K.g;
          for (var k = 0; k < g.parts.length; k++) {
            var p = g.parts[k];
            c.globalAlpha = p.a * 0.6;
            c.fillStyle = p.amber ? C.allow : C.xfer;
            c.fillRect(p.x - 5, p.y - 2.5, 10, 5);
          }
          c.globalAlpha = 1;
        };
        var spawnOne = function (t) {
          var u = g.rnd(), s = g.src;
          g.parts.push({ x: s[0][0] + (s[1][0] - s[0][0]) * u, y: s[0][1] + (s[1][1] - s[0][1]) * u + 6, t: t == null ? 0 : t,
            T: 1.3 + g.rnd() * 0.5, amber: g.rnd() < g.pA, a: 0, jx: (g.rnd() - 0.5) * 120 });
        };
        var advance = function (p, dt) {
          p.t += dt;
          var f = Math.min(1, p.t / p.T), e = f * f;
          var x0 = p.x0 != null ? p.x0 : (p.x0 = p.x), y0 = p.y0 != null ? p.y0 : (p.y0 = p.y);
          p.x = x0 + (g.dst[0] + p.jx * (1 - f) * 0.4 - x0) * f;
          p.y = y0 + (g.dst[1] - y0) * e;
          p.a = Math.min(1, p.t / 0.25) * (f > 0.86 ? (1 - f) / 0.14 : 1);
          return f < 1;
        };
        if (ctx.reduced) {
          /* still picture: a few dozen logs on their way */
          for (var k = 0; k < 46; k++) { spawnOne(); var p = g.parts[g.parts.length - 1]; advance(p, p.T * (k / 46) * 0.95); }
          g.drawParts();
        } else {
          g.spawn = true;
          var acc = 0;
          ctx.raf(function (t, dt) {
            if (g.spawn) { acc += dt * 34; while (acc >= 1) { spawnOne(); acc -= 1; } }
            g.parts = g.parts.filter(function (p) { return advance(p, dt); });
            g.drawParts();
          });
        }
      }
      if (i === 3) {
        /* the stream stops; Ethereum sinks away; the Arbitrum plate turns edge-on and becomes
           a horizontal line, which stretches into the time axis of the next slide */
        tl.call(function () { g.spawn = false; }, null, 0);
        tl.to([g.barrel, el.querySelector('#lblArb'), el.querySelector('#lblEth')], { autoAlpha: 0, duration: 0.4 }, 0);
        tl.to(g.K.canvas, { autoAlpha: 0, duration: 0.5 }, 0.2);
        tl.to(g.eth, { z: -380, autoAlpha: 0, duration: 0.6, ease: 'power2.in' }, 0.1);
        tl.to(g, { rx: 90, rz: 0, duration: 0.9, ease: 'power2.inOut', onUpdate: g.setWorld }, 0.55);
        tl.to(g.arb, { borderColor: '#A3ADBF', duration: 0.5 }, 0.9);
        tl.call(function () {
          ctx.add(function () {
            var r = ctx.rect(g.arb);
            var y = r.y + r.h / 2;
            gsap.set(g.axis, { autoAlpha: 1, x: r.x - 96, y: y - 716, scaleX: r.w / 1728 });
            gsap.set(g.arb, { autoAlpha: 0 });
            gsap.to(g.axis, { x: 0, y: 0, scaleX: 1, duration: 0.8, ease: 'power2.inOut' });
          });
        }, null, 1.47);
      }
    }
  };

  Deck.section({ id: 's02-world', title: 'Allowances and transfers', slides: [slide1, slide2, slide3, slide4, slide5] });
})();
