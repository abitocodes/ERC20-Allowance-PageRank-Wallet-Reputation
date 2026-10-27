/* =========================================================================
   s01-opening — Opening question (STORYBOARD.md §2, s01-01 … s01-03), English edition
   s01-01  The question before signing → title   (wallet window ignites from a dot; the
           allowance arrow it draws becomes the underline of the title)
   s01-02  Research questions          (three players, five RQ chips, links to the progress bar)
   s01-03  Today's road                (a road drawn by the light dot; it flattens into the HUD bar)

   Sources: title, author, supervisors, university and date from DECK_DATA.meta
   (= the thesis title page, 01-Intro/01-Title.tex). RQ wording: Chapter 1,
   Section "Research questions". No result numbers on these slides.

   Shared with later sections (exposed on window.DeckParts):
     DeckParts.wallet.html(opts) / DeckParts.wallet.GEOM  — the brandless wallet
     window of s01-01, so s11-04 can bring it back at the same place and size.
   ========================================================================= */
(function () {
  'use strict';
  var C = Deck.COLORS, esc = Deck.util.esc;
  var DATA = window.DECK_DATA || {};
  var META = DATA.meta || {};
  var NS = 'http://www.w3.org/2000/svg';
  /* title page geometry: top of the title, its line height, top of the author block */
  var TTL = { top: 200, lh: 94, who: 580 };

  /* ------------------------------------------------------------ section styles */
  var CSS = [
    /* wallet window (generic, no brand) */
    '.s01-win{position:absolute;width:820px;height:520px;background:#121826;border:1px solid #2A3345;border-radius:24px;',
    '  box-shadow:0 40px 90px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.02) inset;overflow:hidden}',
    '.s01-win .bar{height:60px;display:flex;align-items:center;justify-content:space-between;padding:0 26px;border-bottom:1px solid var(--line)}',
    '.s01-win .bar .ttl{display:flex;align-items:center;gap:12px;font-size:22px;line-height:1;color:var(--ink-2);font-weight:600}',
    '.s01-win .bar .ttl svg{width:22px;height:22px}',
    '.s01-win .bar .chip{font-family:var(--font-mono);font-size:20px;line-height:1;color:var(--ink-3);border:1px solid var(--line);border-radius:16px;padding:6px 14px;letter-spacing:0}',
    '.s01-win svg.fig{position:absolute;left:0;top:60px;overflow:visible}',
    '.s01-win .q{position:absolute;left:40px;right:40px;top:262px;text-align:center;font-size:30px;line-height:42px;font-weight:600;color:var(--ink)}',
    '.s01-win .cd{position:absolute;left:0;right:0;top:316px;text-align:center;font-family:var(--font-mono);font-size:21px;line-height:28px;color:var(--ink-3);letter-spacing:0}',
    '.s01-win .btns{position:absolute;left:0;right:0;top:396px;display:flex;justify-content:center;gap:20px}',
    '.s01-win .btn{width:190px;height:66px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;letter-spacing:-.01em}',
    '.s01-win .btn.no{border:1.5px solid #3A4458;color:var(--ink-2)}',
    '.s01-win .btn.yes{background:var(--c-allow);color:#1B1305}',
    '.s01-spark{position:absolute;left:0;top:0;width:14px;height:14px;border-radius:8px;background:#fff;',
    '  box-shadow:0 0 14px 3px rgba(255,255,255,.75),0 0 44px 10px rgba(255,255,255,.18);pointer-events:none}',
    '.s01-layer{position:absolute;left:0;top:0;overflow:visible;pointer-events:none}',
    '.s01-qa{position:absolute;left:96px;right:96px;text-align:center}',
    /* title page */
    /* the English title takes three lines where the Korean deck had two lines plus an italic English line;
       #ko / .s01-ko keep the Korean deck's id and class */
    '.s01-ko{position:absolute;left:96px;top:' + TTL.top + 'px;width:1728px;font-size:76px;line-height:' + TTL.lh + 'px;font-weight:800;letter-spacing:-.025em;color:var(--ink)}',
    '.s01-ko .ln{display:block;white-space:nowrap}',
    '.s01-who{position:absolute;left:96px;top:' + TTL.who + 'px;width:1728px}',
    '.s01-who .name{font-size:36px;line-height:50px;font-weight:700}',
    '.s01-who .name .deg{font-weight:500;color:var(--ink-2)}',
    '.s01-who .line{font-size:26px;line-height:40px;color:var(--ink-2)}',
    '.s01-who .line b{color:var(--ink);font-weight:600}',
    /* s01-02 */
    '.s01-rq-sub{position:absolute;left:96px;top:252px;width:960px;font-size:28px;line-height:42px;color:var(--ink-2)}',
    '.s01-players{position:absolute;left:96px;top:420px;display:flex;gap:24px}',
    '.s01-player{width:228px;height:330px;border-radius:20px;background:var(--bg-2);border:1px solid var(--line);position:relative;overflow:hidden}',
    '.s01-player.cpr{border:1.5px solid var(--c-cpr);background:var(--c-cpr-soft)}',
    '.s01-player svg{position:absolute;left:0;top:30px}',
    '.s01-player .nm{position:absolute;left:20px;right:14px;top:190px;font-size:25px;line-height:33px;font-weight:700}',
    '.s01-player .sb{position:absolute;left:20px;right:14px;top:258px;font-size:19px;line-height:27px;color:var(--ink-3)}',
    '.s01-rqs{position:absolute;left:1112px;top:276px;width:712px}',
    '.s01-rq{position:relative;display:flex;align-items:center;gap:20px;min-height:92px;padding:12px 22px 12px 18px;margin-bottom:14px;',
    '  border:1.5px solid var(--line);border-radius:18px;background:rgba(16,21,31,.85)}',
    '.s01-rq .k{flex:0 0 auto;width:74px;height:40px;border-radius:10px;background:var(--bg-3);display:flex;align-items:center;justify-content:center;',
    '  font-family:var(--font-mono);font-size:20px;color:var(--ink);letter-spacing:0}',
    '.s01-rq .t{flex:1 1 auto;font-size:25px;line-height:34px;color:var(--ink);text-wrap:balance}',
    '.s01-rq .s{flex:0 0 auto;font-family:var(--font-mono);font-size:20px;color:var(--ink-3);letter-spacing:0;white-space:nowrap}',
    '.s01-rq.test{border-color:var(--ink)}',
    '.s01-rq-note{position:absolute;left:96px;top:858px;width:1728px;font-size:28px;line-height:42px;color:var(--ink-2)}',
    '.s01-rq-note b{color:var(--ink);font-weight:700}',
    '.s01-rq-note .obj{display:block;margin-top:6px;font-size:24px;line-height:36px;color:var(--ink-3)}',
    '.s01-rq-note .obj b{color:var(--ink-2);font-weight:600}',
    /* s01-03 */
    '.s01-road-lbl{position:absolute;width:300px;margin-left:-150px;text-align:center;pointer-events:none}',
    '.s01-road-lbl .n{display:block;font-family:var(--font-mono);font-size:20px;line-height:26px;color:var(--ink-3);letter-spacing:0}',
    '.s01-road-lbl .t{display:block;font-size:28px;line-height:36px;font-weight:600;color:var(--ink)}',
    '.s01-road-lbl .ic{display:block;margin:4px auto 2px;overflow:visible}',
    '.s01-next{position:absolute;font-size:24px;line-height:34px;color:var(--ink-2);white-space:nowrap}',
    '.s01-next b{color:var(--ink);font-weight:700}'
  ].join('\n');
  (function inject() {
    if (document.getElementById('s01-style')) return;
    var st = document.createElement('style'); st.id = 's01-style'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* ------------------------------------------------------------ the wallet window (shared with s11-04) */
  var WALLET = { left: 550, top: 150, w: 820, h: 520, owner: [150, 92], spender: [670, 92], yes: [1065, 579], no: [855, 579] };
  /* owner / spender: centres inside the window's figure strip (which starts 60 px below the window top);
     yes / no: button centres in stage coordinates */
  var SHIELD = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 2.8l7.5 3v5.6c0 4.6-3.2 8.2-7.5 9.8-4.3-1.6-7.5-5.2-7.5-9.8V5.8z"/><path d="M8.8 12.2l2.2 2.2 4.4-4.6"/></svg>';
  function walletHTML(o) {
    o = o || {};
    var left = o.left != null ? o.left : WALLET.left, top = o.top != null ? o.top : WALLET.top;
    return '<div class="s01-win" id="' + (o.id || 'win') + '" data-in="none" style="left:' + left + 'px;top:' + top + 'px">' +
      '<div class="bar"><span class="ttl">' + SHIELD + 'Signature request</span><span class="chip">Token approval</span></div>' +
      '<svg class="fig" width="820" height="200" viewBox="0 0 820 200"></svg>' +
      '<div class="q">' + (o.question || 'Allow this contract to spend your USDC?') + '</div>' +
      '<div class="cd">' + (o.code || 'approve(spender, amount)') + '</div>' +
      '<div class="btns"><div class="btn no">Reject</div><div class="btn yes">Approve</div></div>' +
      '</div>';
  }
  /* draws the owner (G5) and the spender contract (G4) into the window's figure strip */
  function walletFigure(ctx, winEl) {
    var svg = winEl.querySelector('svg.fig');
    var owner = Comp.eoa(ctx, svg, { x: WALLET.owner[0], y: WALLET.owner[1], r: 22, label: 'Me (owner)' });
    var spender = Comp.contract(ctx, svg, { x: WALLET.spender[0], y: WALLET.spender[1], size: 78, label: 'Spender contract' });
    /* the gap the allowance will fill: a faint dashed placeholder */
    var gap = svgEl('line', { x1: WALLET.owner[0] + 34, y1: WALLET.owner[1], x2: WALLET.spender[0] - 54, y2: WALLET.spender[1],
      stroke: C.ink3, 'stroke-width': 2, 'stroke-dasharray': '5 9', opacity: 0.55 }, svg);
    return { svg: svg, owner: owner, spender: spender, gap: gap };
  }
  window.DeckParts = window.DeckParts || {};
  window.DeckParts.wallet = { GEOM: WALLET, html: walletHTML, figure: walletFigure, css: 's01-win' };

  /* ------------------------------------------------------------ a re-shapeable allowance arrow (G1) */
  function makeAllowArrow(svg) {
    var g = svgEl('g', { 'class': 'glow-allow' }, svg);
    var line = svgEl('path', { fill: 'none', stroke: C.allow, 'stroke-width': 5, 'stroke-linecap': 'round' }, g);
    var head = svgEl('path', { fill: C.allow }, g);
    var key = svgEl('circle', { r: 9, fill: C.bg, stroke: C.allow, 'stroke-width': 3 }, g);
    var A = { g: g, line: line, head: head, key: key, geo: { x0: 0, y0: 0, x1: 0, y1: 0 } };
    A.set = function (x0, y0, x1, y1) {
      var geo = A.geo; if (x0 != null) { geo.x0 = x0; geo.y0 = y0; geo.x1 = x1; geo.y1 = y1; }
      var ang = Math.atan2(geo.y1 - geo.y0, geo.x1 - geo.x0), hs = 20;
      var ex = geo.x1 - Math.cos(ang) * hs * 0.7, ey = geo.y1 - Math.sin(ang) * hs * 0.7;
      line.setAttribute('d', 'M' + geo.x0.toFixed(1) + ',' + geo.y0.toFixed(1) + ' L' + ex.toFixed(1) + ',' + ey.toFixed(1));
      var a1 = ang + Math.PI * 0.84, a2 = ang - Math.PI * 0.84;
      head.setAttribute('d', 'M' + geo.x1 + ',' + geo.y1 + ' L' + (geo.x1 + Math.cos(a1) * hs) + ',' + (geo.y1 + Math.sin(a1) * hs) +
        ' L' + (geo.x1 + Math.cos(a2) * hs) + ',' + (geo.y1 + Math.sin(a2) * hs) + 'Z');
      key.setAttribute('cx', geo.x0); key.setAttribute('cy', geo.y0);
    };
    A.len = function () { try { return line.getTotalLength(); } catch (e) { return 400; } };
    return A;
  }

  /* ------------------------------------------------------------ s01-01 */
  /* the thesis title (= META.title.en), split into lines that fit the 1728 px box; the Korean deck's
     italic second-title line is dropped, so the title page shows the English title only */
  var TITLE_LINES = ['Integrating ERC-20 <span class="c-allow">Allowance Edges</span>', 'into PageRank for Enhanced On-Chain', 'Wallet Reputation Scoring'];
  var author = META.author || {}, date = META.date || {};
  var slide1 = {
    id: 's01-01', title: 'The question before signing → title', time: 45, steps: 2,
    hud: false, ritual: false, autoIn: false,
    notes: [
      '(wallet window) If you have used DeFi, you have probably seen a window like this one. It asks whether a contract may spend your tokens. The window carries no brand. Any wallet software asks a similar question.',
      '(press Approve) The moment I press this button, an allowance edge appears from the owner to the contract. At this point we have to judge whether we can trust that contract, but there is very little to look at. Today\'s talk is about which public signals we can use before signing, and whether smoothing those signals with PageRank makes them better.',
      '(title) The allowance edge I just drew is the main character of this thesis. The title is "Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring". I am Taehong Kwon. My supervisor is Prof. Mnkandla, and my co-supervisors are Prof. Moulla and Dr. Attipoe.'
    ],
    html: function () {
      var who = '<div class="name">' + esc(author.en || 'Taehong Kwon') + ' <span class="deg">· PhD thesis in Computer Science</span></div>' +
        '<div class="line">Supervisor <b>' + esc(META.supervisor || 'Prof. Ernest Mnkandla') + '</b></div>' +
        '<div class="line">Co-supervisors <b>' + esc((META.co_supervisors || ['Prof. Donatien Koulla Moulla', 'Dr. David Sena Attipoe']).join(', ')) + '</b></div>' +
        '<div class="line">' + esc(META.university || 'University of South Africa') + ' (UNISA) · ' + esc(date.en || 'October 2026') + '</div>';
      return walletHTML() +
        '<div class="s01-spark" id="sparkA" data-in="none"></div><div class="s01-spark" id="sparkB" data-in="none"></div>' +
        '<h1 class="s01-qa t-h1" id="q1" data-in="none" style="top:728px">Can I [[trust]] this contract?</h1>' +
        '<p class="s01-qa t-body-l ink-2" id="q2" data-in="none" style="top:822px">What public signals can I see before I sign?</p>' +
        '<div class="s01-ko" id="ko" data-in="none">' + TITLE_LINES.map(function (ln) { return '<div class="ln">' + ln + '</div>'; }).join('') + '</div>' +
        '<div class="s01-who" id="who" data-in="none">' + who + '</div>' +
        '<svg class="s01-layer" id="layer" width="1920" height="1080" viewBox="0 0 1920 1080" data-in="none"></svg>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.win = el.querySelector('#win');
      g.fig = walletFigure(ctx, g.win);
      g.layer = el.querySelector('#layer');
      g.arrow = makeAllowArrow(g.layer);
      var oy = WALLET.top + 60 + WALLET.owner[1];
      g.arrowFrom = [WALLET.left + WALLET.owner[0] + 34, oy, WALLET.left + WALLET.spender[0] - 54, oy];
      g.arrow.set(g.arrowFrom[0], g.arrowFrom[1], g.arrowFrom[2], g.arrowFrom[3]);
      gsap.set(g.arrow.g, { autoAlpha: 0 });
      /* the cursor (G6): a light dot living in the stage layer */
      g.cursor = Comp.walker(ctx, g.layer, { x: 690, y: 560, r: 9, hidden: true });
      g.cursorPath = svgEl('path', { d: 'M690,560 C790,470 980,660 ' + (WALLET.yes[0] + 46) + ',' + (WALLET.yes[1] + 18), fill: 'none', stroke: 'none' }, g.layer);
      g.ripple = svgEl('circle', { cx: WALLET.yes[0], cy: WALLET.yes[1], r: 20, fill: 'none', stroke: C.allow, 'stroke-width': 3, opacity: 0 }, g.layer);
      /* title page parts start hidden */
      ['#q1', '#q2', '#ko', '#who'].forEach(function (s) { gsap.set(el.querySelector(s), { autoAlpha: 0 }); });
      gsap.set([el.querySelector('#sparkA'), el.querySelector('#sparkB')], { autoAlpha: 0 });
      g.yes = g.win.querySelector('.btn.yes');
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl();
      var A = el.querySelector('#sparkA'), B = el.querySelector('#sparkB');
      var cx = WALLET.left + WALLET.w / 2, cy = WALLET.top + WALLET.h / 2;
      /* point -> line -> the line opens up and down into the window (§s01-01, 0.9 s) */
      gsap.set(g.win, { clipPath: 'inset(50% 0% 50% 0% round 24px)' });
      tl.fromTo([A, B], { x: cx - 7, y: cy - 7, width: 14, height: 14, scale: 0, autoAlpha: 1 }, { scale: 1, duration: 0.32, ease: 'back.out(2)' }, 0.1);
      tl.to([A, B], { x: WALLET.left, width: WALLET.w, height: 2, y: cy - 1, duration: 0.36, ease: 'power3.inOut' }, 0.48);
      tl.to(g.win, { clipPath: 'inset(0% 0% 0% 0% round 24px)', duration: 0.55, ease: 'power3.out' }, 0.86);
      tl.to(A, { y: WALLET.top - 1, duration: 0.55, ease: 'power3.out' }, 0.86);
      tl.to(B, { y: WALLET.top + WALLET.h - 1, duration: 0.55, ease: 'power3.out' }, 0.86);
      tl.to(A, { autoAlpha: 0, duration: 0.35 }, 1.3);
      /* the bottom glint shrinks back into the dot: the cursor of the next click */
      tl.to(B, { x: 690 - 7, width: 14, height: 14, y: 560 - 7, duration: 0.5, ease: 'power3.inOut' }, 1.35);
      tl.set(B, { autoAlpha: 0 }, 1.85);
      tl.add(g.cursor.show({ duration: 0.01 }), 1.84);
      tl.call(function () { g.cursor.set(690, 560); }, null, 1.83);
      tl.add(g.fig.owner.pop(), 1.0);
      tl.add(g.fig.spender.pop(), 1.1);
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        /* the cursor glides to Approve, decelerating; press; the allowance is drawn */
        g.cursor.set(690, 560);
        gsap.set(g.cursor.g, { autoAlpha: 1 });
        tl.add(g.cursor.along(g.cursorPath, { duration: 0.85, ease: 'power3.out' }), 0);
        tl.call(function () { var e = g.cursorPath.getPointAtLength(g.cursorPath.getTotalLength()); g.cursor.set(e.x, e.y); }, null, 0.86);
        tl.to(g.yes, { scale: 0.93, duration: 0.09, ease: 'power2.in' }, 0.86);
        tl.to(g.yes, { scale: 1, duration: 0.3, ease: 'back.out(3)' }, 0.95);
        tl.fromTo(g.ripple, { attr: { r: 18 }, opacity: 0.9 }, { attr: { r: 64 }, opacity: 0, duration: 0.6, ease: 'power2.out', immediateRender: false }, 0.9);
        tl.to(g.fig.gap, { opacity: 0, duration: 0.2 }, 1.0);
        tl.set(g.arrow.g, { autoAlpha: 1 }, 1.0);
        var L = g.arrow.len();
        tl.fromTo(g.arrow.key, { scale: 0.2, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.3, ease: 'back.out(2)' }, 1.0);
        tl.fromTo(g.arrow.line, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' }, 1.05);
        tl.fromTo(g.arrow.head, { autoAlpha: 0, scale: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.25, ease: 'power3.out' }, 1.55);
        tl.call(function () { g.arrow.line.style.strokeDasharray = ''; g.arrow.line.style.strokeDashoffset = ''; }, null, 1.7);
        /* the question rises, one word at a time; then the accent underline */
        var q1 = el.querySelector('#q1'), q2 = el.querySelector('#q2');
        tl.add(ctx.rise(q1, { stagger: 0.08 }), 1.75);
        tl.add(ctx.rise(q2, { stagger: 0.06 }), 2.2);
        var hl = q1.querySelector('.hl');
        if (hl) tl.fromTo(hl, { '--hl-x': 0 }, { '--hl-x': 1, duration: 0.5, ease: 'power2.inOut' }, 2.35);
      }
      if (i === 2) {
        /* shared-element move: the window leaves to the upper left, only the arrow stays and
           stretches into the underline of the title */
        var q = [el.querySelector('#q1'), el.querySelector('#q2')];
        tl.to(g.cursor.g, { autoAlpha: 0, duration: 0.2 }, 0);
        tl.to(q, { y: -36, autoAlpha: 0, duration: 0.45, ease: 'power2.in', stagger: 0.05 }, 0);
        tl.to(g.win, { x: -(WALLET.left - 96), y: -(WALLET.top - 40), scale: 0.18, transformOrigin: '0% 0%', autoAlpha: 0, duration: 0.85, ease: 'power2.inOut' }, 0.1);
        var lines = el.querySelectorAll('#ko .ln'), wmax = 0;
        Array.prototype.forEach.call(lines, function (ln) {
          var rg = document.createRange(); rg.selectNodeContents(ln);
          wmax = Math.max(wmax, rg.getBoundingClientRect().width / (Deck.scale || 1));
        });
        /* the underline sits 32 px below the last title line (Korean deck: 2 lines from 208 -> y 428) */
        var x1 = Math.min(1824, 96 + Math.max(900, wmax) + 8), y = TTL.top + lines.length * TTL.lh + 32;
        var geo = g.arrow.geo;
        tl.to(geo, { x0: 106, y0: y, x1: x1, y1: y, duration: 1.0, ease: 'power2.inOut', onUpdate: function () { g.arrow.set(); } }, 0.25);
        /* the title rises from the line, then the names */
        var ko = el.querySelector('#ko');
        tl.add(ctx.rise(ko, { stagger: 0.06 }), 1.1);
        var who = el.querySelector('#who');
        gsap.set(who, { autoAlpha: 1 });
        tl.fromTo(who.children, { autoAlpha: 0, y: 22 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.12 }, 2.0);
      }
    }
  };

  /* ------------------------------------------------------------ s01-02 */
  /* RQ wording: English thesis, Chapter 1, "Research questions", shortened as the Korean slide shortens it;
     '\n' forces a line break, other chips wrap balanced */
  var RQS = [
    { k: 'RQ1', t: 'Do the single-edge walks order contracts\ndifferently, each matching its own checks?', sec: 8 },
    { k: 'RQ2', t: 'What does each score cost, and how much\ndoes walking both edge sets add?', sec: 10 },
    { k: 'RQ3', t: 'Do the scores predict what comes later?\nBetter than the raw degree?', sec: 8, test: true },
    { k: 'RQ4', t: 'Does C-PR beat each layer walked alone? (rule A)', sec: 9, test: true },
    { k: 'RQ5', t: 'Does adding allowances improve the transfer walk? (rule B)', sec: 9, test: true }
  ];
  var slide2 = {
    id: 's01-02', title: 'Research questions', time: 45, steps: 3,
    notes: [
      'This is the main question of the thesis: what does a single PageRank walk over both ERC-20 allowance and transfer edges add to ranking smart contracts on Arbitrum One?',
      'The score of this thesis is C-PR, which walks both kinds of edge at once. It is measured against three references: EndorseRank, which walks the allowances alone; AWP, the existing score that walks the transfer records alone; and the material the walks smooth, the plain count of edges, the raw degree.',
      'I split the main question into five research questions. The number at the end of each chip is the section where the answer comes. I will show the answer in that cell of the bar below.',
      'The first two questions carry the hypotheses H1 to H3. A hypothesis is an expected answer set up in advance. These three are checks that hold largely by construction, because of the way the scores are built. The real tests are RQ3 to RQ5, and RQ4 and RQ5 test C-PR under rules fixed in advance. Each question also has one objective, and I call them objectives O1 to O5. O1 is the objective of RQ1, and O5 is the objective of RQ5. I will judge whether each objective was met at the end, in section 11.'
    ],
    html:
      '<h1 class="t-h1">What does one walk over both edge types<br>[[add]]?</h1>' +
      '<p class="s01-rq-sub">As a reputation score for smart contracts on Arbitrum One, compared with walks over either edge type and with the raw degrees they smooth</p>' +
      '<div class="s01-players" id="players" data-in="none">' +
        '<div class="s01-player"><svg width="228" height="135" viewBox="0 0 304 180"></svg><div class="nm c-allow">Allowance walk</div><div class="sb">EndorseRank (reference)</div></div>' +
        '<div class="s01-player"><svg width="228" height="135" viewBox="0 0 304 180"></svg><div class="nm c-xfer">Transfer walk</div><div class="sb">AWP (published method)</div></div>' +
        '<div class="s01-player"><svg width="228" height="135" viewBox="0 0 304 180"></svg><div class="nm c-deg">Just counting</div><div class="sb">Raw degree (reference)</div></div>' +
        '<div class="s01-player cpr"><svg width="228" height="135" viewBox="0 0 304 180"></svg><div class="nm c-cpr">Both at once</div><div class="sb">C-PR (this thesis)</div></div>' +
      '</div>' +
      '<div class="s01-rqs" id="rqs" data-in="none">' + RQS.map(function (r) {
        return '<div class="s01-rq' + '" data-k="' + r.k + '"><span class="k">' + r.k + '</span><span class="t">' + r.t.split('\n').map(esc).join('<br>') + '</span><span class="s">→ ' + Deck.util.pad2(r.sec) + '</span></div>';
      }).join('') + '</div>' +
      '<p class="s01-rq-note" id="rqnote" data-in="none">Hypotheses H1–H3 (= the expected answers to RQ1–RQ2) hold largely by construction. The real tests are <b>RQ3–RQ5</b>; <b>RQ4</b> and <b>RQ5</b> test C-PR under rules fixed in advance.' +
        '<span class="obj">One objective per question: <b>objectives O1–O5</b> (O1 = the objective of RQ1 …) · whether each was met is judged in → 11</span></p>',
    build: function (el, ctx) {
      var g = ctx.g = {};
      var cards = el.querySelectorAll('.s01-player');
      var s1 = cards[0].querySelector('svg'), s2 = cards[1].querySelector('svg'), s3 = cards[2].querySelector('svg');
      g.e1 = Comp.eoa(ctx, s1, { x: 52, y: 92, r: 16 });
      g.c1 = Comp.contract(ctx, s1, { x: 238, y: 92, size: 64 });
      g.a1 = Comp.arrow(ctx, s1, { from: [52, 92], to: [238, 92], kind: 'allow', width: 4, shorten: [24, 44], hidden: true });
      g.e2 = Comp.eoa(ctx, s2, { x: 52, y: 92, r: 16 });
      g.c2 = Comp.contract(ctx, s2, { x: 238, y: 92, size: 64 });
      g.a2 = Comp.arrow(ctx, s2, { from: [52, 92], to: [238, 92], kind: 'xfer', width: 4, shorten: [24, 44], hidden: true });
      g.tally = Comp.tally(ctx, s3, { x: 116, y: 50, size: 72 });
      var s4 = cards[3].querySelector('svg');
      g.e4a = Comp.eoa(ctx, s4, { x: 52, y: 62, r: 14 });
      g.e4b = Comp.eoa(ctx, s4, { x: 52, y: 122, r: 14 });
      g.c4 = Comp.contract(ctx, s4, { x: 238, y: 92, size: 64 });
      g.a4a = Comp.arrow(ctx, s4, { from: [52, 62], to: [238, 80], kind: 'allow', width: 4, shorten: [20, 40], hidden: true });
      g.a4b = Comp.arrow(ctx, s4, { from: [52, 122], to: [238, 104], kind: 'xfer', width: 4, shorten: [20, 40], hidden: true });
      g.cards = cards;
      gsap.set(cards, { autoAlpha: 0 });
      g.rqs = el.querySelectorAll('.s01-rq');
      gsap.set(g.rqs, { autoAlpha: 0 });
      gsap.set(el.querySelector('#rqnote'), { autoAlpha: 0 });
    },
    step: function (el, i, ctx) {
      var g = ctx.g, tl = ctx.tl();
      if (i === 1) {
        tl.fromTo(g.cards, { autoAlpha: 0, y: 40, scale: 0.9, transformOrigin: '50% 100%' }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.5, ease: 'back.out(1.2)', stagger: 0.12 }, 0);
        tl.add(g.a1.draw(), 0.35);
        tl.add(g.a2.draw(), 0.47);
        tl.add(g.tally.add(5, { stagger: 0.16 }), 0.6);
        tl.add(g.a4a.draw(), 0.75);
        tl.add(g.a4b.draw(), 0.87);
      }
      if (i === 2) {
        tl.fromTo(g.rqs, { autoAlpha: 0, x: 80 }, { autoAlpha: 1, x: 0, duration: 0.55, ease: 'power3.out', stagger: 0.08 }, 0);
        /* each chip's section number reaches for its cell of the progress bar along the right
           margin (never across the chips), then lets go */
        if (!ctx.reduced) {
          var ov = ctx.overlay();
          Array.prototype.forEach.call(g.rqs, function (chip, k) {
            var cell = ctx.hud.rect('cell:' + RQS[k].sec);
            if (!cell || !(cell.w > 0)) return;
            var a = ctx.rect(chip.querySelector('.s'));
            var x0 = a.x + a.w + 8, y0 = a.cy, xb = 1846 + k * 8, yb = 996 + k * 6, cx = cell.cx, r = 10;
            var d = 'M' + x0 + ',' + y0 + ' H' + (xb - r) + ' Q' + xb + ',' + y0 + ' ' + xb + ',' + (y0 + r) +
              ' V' + (yb - r) + ' Q' + xb + ',' + yb + ' ' + (xb - r) + ',' + yb + ' H' + (cx + r) + ' Q' + cx + ',' + yb + ' ' + cx + ',' + (yb + r) + ' V' + (cell.y + 4);
            var path = svgEl('path', { d: d, fill: 'none', stroke: C.ink3, 'stroke-width': 1.5, opacity: 0.9 }, ov);
            var end = svgEl('circle', { cx: cx, cy: cell.y + cell.h / 2, r: 5, fill: C.ink, opacity: 0 }, ov);
            var Lp = path.getTotalLength();
            gsap.set(path, { strokeDasharray: Lp + ' ' + Lp, strokeDashoffset: Lp });
            var t0 = 0.75 + k * 0.1;
            tl.to(path, { strokeDashoffset: 0, duration: 0.7, ease: 'power2.inOut' }, t0);
            tl.fromTo(end, { opacity: 0, attr: { r: 12 } }, { opacity: 1, attr: { r: 5 }, duration: 0.35, ease: 'power3.out' }, t0 + 0.62);
            tl.to([path, end], { opacity: 0, duration: 0.4 }, t0 + 1.6);
            tl.call(function () { path.remove(); end.remove(); }, null, t0 + 2.05);
          });
        }
      }
      if (i === 3) {
        tl.fromTo(el.querySelector('#rqnote'), { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0);
        Array.prototype.forEach.call(g.rqs, function (chip, k) {
          if (RQS[k].test) tl.to(chip, { borderColor: C.ink, duration: 0.45, ease: 'power2.out' }, 0.5);
        });
      }
    }
  };

  /* ------------------------------------------------------------ s01-03 */
  /* '\n' breaks a stop name that is wider than its 300 px label or would cross the 96 px side margin;
     a label above the road grows upwards, so its last line keeps its place */
  var STOPS = [
    ['01', 'Opening\nquestion'], ['02', 'Allowances\nand transfers'], ['03', 'The data'], ['04', 'Deriving PageRank'], ['05', 'Edge weights'],
    ['06', 'Four scores'], ['07', 'How we measure'], ['08', 'Results'], ['09', 'Rules fixed in advance'], ['10', 'Attack cost and speed'], ['11', 'Conclusion']
  ];
  /* tiny icons beside some stops (G7 small world, G9 interval bar, G10 stamp, G14 farm) */
  function stopIcon(svg, kind, x, y) {
    var g = svgEl('g', { transform: 'translate(' + x + ',' + y + ')', opacity: 0.95 }, svg);
    if (kind === 'world') {
      var P = [[-22, 0], [0, -14], [0, 14], [22, 0]];
      [[0, 1], [0, 2], [1, 3], [2, 3]].forEach(function (e) {
        svgEl('line', { x1: P[e[0]][0], y1: P[e[0]][1], x2: P[e[1]][0], y2: P[e[1]][1], stroke: C.allow, 'stroke-width': 2 }, g);
      });
      svgEl('circle', { cx: -22, cy: 0, r: 5, fill: C.bg, stroke: C.ink3, 'stroke-width': 2 }, g);
      [[0, -14], [0, 14], [22, 0]].forEach(function (p) { svgEl('rect', { x: p[0] - 5, y: p[1] - 5, width: 10, height: 10, rx: 2.5, fill: C.bg2, stroke: C.ink2, 'stroke-width': 1.6 }, g); });
    } else if (kind === 'forest') {
      svgEl('line', { x1: 0, y1: -16, x2: 0, y2: 16, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '3 3' }, g);
      svgEl('line', { x1: -6, y1: -6, x2: 22, y2: -6, stroke: C.ink, 'stroke-width': 3, 'stroke-linecap': 'round' }, g);
      svgEl('circle', { cx: 9, cy: -6, r: 4.5, fill: C.ink }, g);
      svgEl('line', { x1: -22, y1: 8, x2: 4, y2: 8, stroke: C.ink2, 'stroke-width': 3, 'stroke-linecap': 'round' }, g);
      svgEl('circle', { cx: -9, cy: 8, r: 4.5, fill: C.ink2 }, g);
    } else if (kind === 'stamp') {
      svgEl('rect', { x: -22, y: -13, width: 44, height: 26, rx: 6, fill: 'none', stroke: C.ink, 'stroke-width': 2.2, transform: 'rotate(-8)' }, g);
      svgEl('path', { d: 'M-8,0 l5,5 l11,-10', fill: 'none', stroke: C.ink, 'stroke-width': 2.4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', transform: 'rotate(-8)' }, g);
    } else if (kind === 'farm') {
      [[-16, -6], [-4, -14], [10, -10], [18, 4], [4, 6], [-12, 10], [-2, 18]].forEach(function (p) {
        svgEl('circle', { cx: p[0], cy: p[1], r: 4.5, fill: 'none', stroke: C.hi, 'stroke-width': 1.6, 'stroke-dasharray': '2 2' }, g);
      });
    }
    return g;
  }
  /* smooth road through the stops: cubic segments with horizontal tangents */
  function roadD(pts) {
    var d = 'M' + pts[0][0].toFixed(1) + ',' + pts[0][1].toFixed(1);
    for (var i = 1; i < pts.length; i++) {
      var a = pts[i - 1], b = pts[i], h = (b[0] - a[0]) / 2;
      d += ' C' + (a[0] + h).toFixed(1) + ',' + a[1].toFixed(1) + ' ' + (b[0] - h).toFixed(1) + ',' + b[1].toFixed(1) + ' ' + b[0].toFixed(1) + ',' + b[1].toFixed(1);
    }
    return d;
  }
  function inOutInv(p) { p = Math.max(0, Math.min(1, p)); return p < 0.5 ? Math.sqrt(p / 2) : 1 - Math.sqrt((1 - p) / 2); } /* inverse of power1.inOut */
  var slide3 = {
    id: 's01-03', title: 'Today\'s road', time: 30, steps: 1, progress: false,
    notes: [
      'Today we will follow this road. First we look at how allowances differ from transfers, and then at the data collected from Arbitrum One. Next I derive the PageRank formula from scratch, then explain how each edge gets its weight and what the four scores are. After we see how to measure whether a score got it right, I show the results and the verdicts of the rules fixed in advance. Finally we look at the cost of an attack and the speed of computation, and then I sum up.',
      'This road now becomes the bar at the bottom of the screen. Until the end of the talk, it will keep showing where we are.'
    ],
    html: '<h1 class="t-h1">Today\'s [[road]]</h1>' +
      '<svg class="s01-layer" id="road" width="1920" height="1080" viewBox="0 0 1920 1080" data-in="none"></svg>' +
      '<div id="lbls" data-in="none"></div>' +
      '<div class="s01-next" id="next" data-in="none">Next stop <b>02 Allowances and transfers</b> · this bar shows where we are</div>',
    build: function (el, ctx) {
      var g = ctx.g = { stops: [] };
      var svg = el.querySelector('#road'), lbls = el.querySelector('#lbls');
      /* stops sit exactly above the HUD cells, so flattening is a pure vertical fall */
      var xs = STOPS.map(function (s, k) {
        var r = ctx.hud.rect('cell:' + (k + 1));
        return r && r.w > 0 ? r.cx : 96 + 74 + k * 158;
      });
      var cell1 = ctx.hud.rect('cell:1');
      g.barY = cell1 && cell1.h > 0 ? cell1.y + cell1.h / 2 : 1040;
      g.up = STOPS.map(function (s, k) { return k % 2 === 0; });
      g.pts = xs.map(function (x, k) { return [x, g.up[k] ? 470 : 650]; });
      g.road = svgEl('path', { d: roadD(g.pts), fill: 'none', stroke: C.ink2, 'stroke-width': 3, 'stroke-linecap': 'round', opacity: 0.85 }, svg);
      g.L = g.road.getTotalLength();
      /* path fraction of each stop */
      var acc = 0; g.frac = [0];
      for (var k = 1; k < g.pts.length; k++) {
        var tmp = svgEl('path', { d: roadD([g.pts[k - 1], g.pts[k]]), fill: 'none' }, svg);
        acc += tmp.getTotalLength(); tmp.parentNode.removeChild(tmp);
        g.frac.push(acc / g.L);
      }
      var icons = { 3: 'world', 7: 'forest', 8: 'stamp', 9: 'farm' };
      STOPS.forEach(function (s, k) {
        var p = g.pts[k];
        var dot = svgEl('circle', { cx: p[0], cy: p[1], r: 10, fill: C.bg, stroke: C.ink3, 'stroke-width': 2.5 }, svg);
        var lab = document.createElement('div');
        lab.className = 's01-road-lbl';
        lab.style.left = p[0] + 'px';
        var extra = (s[1].split('\n').length - 1) * 36;   /* line height of .t */
        lab.style.top = (g.up[k] ? p[1] - 96 - (icons[k] ? 50 : 0) - extra : p[1] + 30) + 'px';
        lab.innerHTML = '<span class="n">' + s[0] + '</span><span class="t">' + s[1].split('\n').map(esc).join('<br>') + '</span>';
        lbls.appendChild(lab);
        var ic = null;
        if (icons[k]) {
          /* the icon sits on the far side of the label, away from the road */
          var isv = document.createElementNS(NS, 'svg');
          isv.setAttribute('width', 60); isv.setAttribute('height', 44); isv.setAttribute('viewBox', '-30 -22 60 44');
          isv.setAttribute('class', 'ic');
          stopIcon(isv, icons[k], 0, 0);
          if (g.up[k]) lab.insertBefore(isv, lab.firstChild); else lab.appendChild(isv);
          ic = isv;
        }
        g.stops.push({ dot: dot, lab: lab, icon: ic });
        gsap.set(lab, { autoAlpha: 0 });
        if (ic) gsap.set(ic, { autoAlpha: 0 });
      });
      g.walker = Comp.walker(ctx, svg, { x: g.pts[0][0], y: g.pts[0][1], r: 8, hidden: true });
      g.next = el.querySelector('#next');
      g.next.style.left = (g.pts[1][0] - 20) + 'px'; g.next.style.top = (g.barY - 74) + 'px';
      gsap.set(g.next, { autoAlpha: 0 });
      gsap.set(g.road, { strokeDasharray: g.L + ' ' + g.L, strokeDashoffset: g.L });
    },
    enter: function (el, ctx) {
      var g = ctx.g, tl = ctx.tl(), D0 = 2.0;
      /* the stops appear first, left to right, as small rings */
      tl.fromTo(g.stops.map(function (st) { return st.dot; }), { attr: { r: 0 } }, { attr: { r: 10 }, duration: 0.35, ease: 'back.out(2)', stagger: 0.035 }, 0);
      /* the light dot runs ahead of the road it draws; each stop lights up as it passes */
      tl.set(g.walker.g, { autoAlpha: 1 }, 0.2);
      tl.to(g.road, { strokeDashoffset: 0, duration: D0, ease: 'power1.inOut' }, 0.2);
      tl.add(g.walker.along(g.road, { duration: D0, ease: 'power1.inOut' }), 0.2);
      g.stops.forEach(function (st, k) {
        var t = 0.2 + D0 * inOutInv(g.frac[k]);
        tl.to(st.dot, { attr: { fill: C.ink }, stroke: C.ink, duration: 0.25 }, t);
        tl.fromTo(st.dot, { attr: { r: 16 } }, { attr: { r: 10 }, duration: 0.45, ease: 'power3.out', immediateRender: false }, t);
        tl.fromTo(st.lab, { autoAlpha: 0, y: g.up[k] ? 14 : -14 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: 'power3.out' }, t + 0.02);
        if (st.icon) tl.fromTo(st.icon, { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: 'back.out(1.6)' }, t + 0.12);
      });
      tl.to(g.walker.g, { autoAlpha: 0.0, duration: 0.4 }, 0.2 + D0 + 0.2);
      tl.call(function () { g.road.style.strokeDasharray = ''; g.road.style.strokeDashoffset = ''; }, null, 0.2 + D0 + 0.05);
    },
    step: function (el, i, ctx) {
      if (i !== 1) return;
      var g = ctx.g, tl = ctx.tl();
      /* shared-element move: the whole road lies down and falls into the progress bar (HUD) */
      var labs = g.stops.map(function (s) { return s.lab; }), icons = g.stops.map(function (s) { return s.icon; }).filter(Boolean);
      tl.to(labs.concat(icons), { autoAlpha: 0, y: 18, duration: 0.3, ease: 'power2.in', stagger: 0.015 }, 0);
      var st = { p: 0 };
      tl.to(st, { p: 1, duration: 0.85, ease: 'power2.inOut', onUpdate: function () {
        var pts = g.pts.map(function (q) { return [q[0], lerp(q[1], g.barY, st.p)]; });
        g.road.setAttribute('d', roadD(pts));
        g.stops.forEach(function (s, k) { s.dot.setAttribute('cy', pts[k][1]); s.dot.setAttribute('r', lerp(10, 3, st.p)); });
      } }, 0.25);
      tl.to(g.road, { attr: { 'stroke-width': 2 }, stroke: '#4B5468', opacity: 1, duration: 0.85, ease: 'power2.inOut' }, 0.25);
      tl.to(g.stops.map(function (s) { return s.dot; }), { attr: { fill: C.ink3 }, stroke: C.ink3, duration: 0.6 }, 0.4);
      /* the real HUD bar takes over in place */
      tl.call(function () { ctx.hud.showProgress(true); }, null, 1.1);
      tl.to([g.road].concat(g.stops.map(function (s) { return s.dot; })), { autoAlpha: 0, duration: 0.25 }, 1.12);
      /* the light dot steps from 01 to 02: that is where we go next */
      tl.call(function () { g.walker.set(g.pts[0][0], g.barY); }, null, 1.15);
      tl.to(g.walker.g, { autoAlpha: 1, duration: 0.2 }, 1.2);
      tl.add(g.walker.moveTo(g.pts[1][0], g.barY, { duration: 0.6, ease: 'power3.inOut' }), 1.4);
      tl.add(g.walker.pulse(), 2.0);
      tl.fromTo(g.next, { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power3.out' }, 2.05);
    }
  };

  Deck.section({ id: 's01-opening', title: 'Opening question', slides: [slide1, slide2, slide3] });
})();
