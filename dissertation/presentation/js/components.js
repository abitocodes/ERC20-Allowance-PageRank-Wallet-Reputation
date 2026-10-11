/* =========================================================================
   components.js — reusable visual pieces of the deck (window.Comp).
   Loaded after js/deck.js and data/*.js, before js/sections/*.js.
   Every component is exercised in tools/gallery.html (see tools/gallery-sections.js).

   Conventions
   - Every constructor takes the slide ctx first: Comp.x(ctx, parent, opts).
     Call them from build/enter/step so their tweens are recorded by the slide
     (killed on leave, completed by ctx.settle(), honoured by Deck.idle()).
   - Methods that animate return a GSAP tween/timeline you can place in your
     own timeline (tl.add(A.draw(), 0.4)). In reduced motion they snap.
   - Coordinates are design pixels of the 1920x1080 stage (or of the SVG you
     pass). Colours follow meaning (STORYBOARD §1.1): kind = 'allow' | 'xfer' |
     'cpr' | 'deg' | 'hi' | 'ink' | 'ink2' | 'ink3' or any CSS colour.
   - Nothing here ever prints an address or a contract name.

   API
   Comp.svg(ctx, parent, {w, h, className, style})            -> <svg> (viewBox 0 0 w h)
   Comp.color(kind) / Comp.lambdaColor(λ) / Comp.rgb(hex) -> [r,g,b] 0..1 (sRGB)
   Comp.tag(key) -> <span class="pill">   (status tag G11; keys: plan, registered, reanalysis,
                    posthoc, exploratory, construct, registered-analysis, example, calc, thesis-example)
   Comp.example(text='예시') -> small grey label element
   Comp.canvas(ctx, parent, {w, h, x, y, onResize}) -> {canvas, g (2D context in design px), w, h, clear(), resize()}
                    backing store follows the stage scale (sharp at any window size); redraw in onResize

   Glyphs (SVG, G1–G15)
   Comp.arrow(ctx, svg, {from:[x,y], to:[x,y], kind:'allow'|'xfer'|'cpr'|'plain'|'deg'|'hi', width:3,
              bend:0, shorten:[0,0], head:14, label, labelOffset:-18, lambda:.5, dashed, hidden:true})
       -> A {g, path, length, pointAt(t), draw({duration,delay}), cut(), flow(on) (G2 coins),
             setLabel(text), setWidth(w), setLambda(λ), glow(on), show(), hide()}
       allow = G1 (keyring at the owner end, steady glow), xfer = G2 (coins flow), cpr = G3 (two strands)
   Comp.contract(ctx, svg, {x, y, size:56, label, sub, hidden})  -> G4 {g, pop(), badge(text), flash()}
   Comp.eoa(ctx, svg, {x, y, r:14, label, hidden})               -> G5 {g, pop(), tag(text)}
   Comp.walker(ctx, svg, {x, y, r:7, trail:5})                   -> G6 {g, moveTo(x,y,opts), along(pathEl,opts), pulse(), hide(), show()}
   Comp.tally(ctx, svg, {x, y, size:44, count:0})                -> G8 {g, add(k,opts), set(n)}
   Comp.stamp(ctx, parent, {ok:true, text, x, y})                -> G10 {el, slam()}
   Comp.pin(ctx, svg, {x, y0, y1, label, color})                 -> G12 {g, drop()}
   Comp.dial(ctx, parent, {value:1, size:260, snap:[0,.25,.5,.75,1], interactive, onChange})
                                                                 -> G13 {el, value, set(v,opts), arc(v0,v1,color)}
   Comp.farm(ctx, svg, {cx, cy, n:20, radius:120, dotR:9, layout:'ring'|'cloud', seed:42})
                                                                 -> G14 {g, dots, grow({from,to,duration})}
   Comp.cup(ctx, svg, {x, y, w:56, h:66, value:0, max:1, decimals:4, color, label:true})
                                                                 -> G15 {g, set(v,opts), value}
   Widgets
   Comp.graph(ctx, svgOrParent, {w, h, nodes:[{id,x,y,kind:'eoa'|'contract'|'farm'|'dot',label,size}],
              edges:[{from,to,w,kind,bend,label}], showWeights, weightWidth:fn, cups:{dy,w,h,max}, hidden})
       -> G {svg, node(id), edge(from,to), nodes, edges, cups, drawIn(opts), setCups(values,opts),
             walker (G6 on the graph: place(id), hop(id,opts), walk(n,{seed,d,duration}))}
   Comp.smallWorld(ctx, parent, opts)  the four-node world of Chapter 2 (G7), always the same
       geometry: A(EOA)->B(2), A->C(1), B->D(3), C->D(1); opts {x, y, scale, cups, hidden, kind,
       labels:{A:'A 토큰 주인',…}, subs:{…}, shared:'small-world'} (the wrapper carries data-shared, so
       consecutive slides that place it at the same x/y keep it still while the rest changes)
   Comp.forest(ctx, parent, {w, rows:[{label, sub, est, lo, hi, outer:[lo,hi], color, ghost:{est,lo,hi},
              hollow, text}], domain:[a,b], ticks, zero:true, labelWidth, valueWidth, rowH, hidden})
       -> F {svg, x(v), rows, grow(opts), show(i,opts), dim(keep), highlight(i)}   (G9 interval bars)
   Comp.odometer(ctx, el, text, {duration, delay})               -> timeline; ends on `text` exactly
   Comp.timeline(ctx, parent, {w, h, from:'2023-10-01', to:'2026-09-30', axisY, years:true})
       -> TL {svg, x(date), drawAxis(opts), pin(date,opts) -> G12, band(from,to,opts), stream(values,opts), ruler(...)}
   Comp.formula(ctx, parent, tex, {display:true, className})     KaTeX with named parts \part{name}{…}
       -> F {el, parts(name), mark(name,opts), unmark(name), dim(keep), undim(), show(name), hide(name), color(name,c), rect(name)}
   Comp.derive(ctx, parent, {lines:[{tex, note, mark}], head:'유도', counter:true})
       -> D {el, show(k,opts), total}   one line per step, "단계 k / N", changed part highlighted
   Comp.symbolCard(ctx, parent, {tex, desc, art, x, y, hidden:true}) -> {el, pop()}   (기호 카드)
   Comp.leader(ctx, from, to, {fromSide, toSide, color, bend, width, dashed}) -> {path, draw(), remove()}
   Comp.swap(ctx, el, html) / Comp.strike(ctx, el, html) / Comp.hilite(ctx, el, {color}) / Comp.scramble(ctx, el, text)
   3D (three.js, with T = ctx.three(container, opts))
   Comp.cloud(ctx, T, {positions:Float32Array(3n), colors:Float32Array(3n) sRGB 0..1, size:3, opacity:.55, additive:true})
       -> C {points, n, positions, colors, setPositions(a), setColors(a), morph(target,{duration,ease,delays,spread}),
             recolor(target,{duration,delays,spread})}
   Comp.floor(ctx, T, {size, y, divisions, color, opacity})      -> THREE.Group (grid + translucent plate)
   Comp.axes3d(ctx, T, {origin, length:[x,y,z], colors:[…], labels:[html,html,html]}) -> {group, labels}
   Data
   Comp.data.contracts()  -> cached typed arrays of DECK_DATA.contracts:
       {n, pct:{key:Float32Array}, raw:{key:Float32Array}, log10:{key:Float32Array, NaN for null}, flags:Uint8Array}
   ========================================================================= */
(function (global) {
  'use strict';
  var gsap = global.gsap, Deck = global.Deck;
  if (!gsap || !Deck) { (global.__deckErrors = global.__deckErrors || []).push({ type: 'components', message: 'gsap/Deck missing' }); return; }
  var NS = 'http://www.w3.org/2000/svg';
  var COL = Deck.COLORS, D = Deck.D, E = Deck.E, fmt = Deck.util.fmt;
  var KIND = { allow: COL.allow, xfer: COL.xfer, cpr: COL.cpr, deg: COL.deg, hi: COL.hi, ink: COL.ink, ink2: COL.ink2, ink3: COL.ink3, line: COL.line, plain: COL.ink2 };
  function color(k) { return KIND[k] || k || COL.ink; }
  function red(ctx) { return !!(ctx && ctx.reduced); }
  /* reduced motion: near-instant, never exactly 0 (zero-length tweens nested in timelines can
     render their start state when the parent is jumped to its end inside a gsap.context) */
  function dur(ctx, d) { return red(ctx) ? 0.01 : d; }

  function s(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, cls, parent, html) {
    var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e;
  }
  function rgb(hex) { hex = String(hex).replace('#', ''); return [parseInt(hex.slice(0, 2), 16) / 255, parseInt(hex.slice(2, 4), 16) / 255, parseInt(hex.slice(4, 6), 16) / 255]; }
  function toLin(c) { return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  var uidN = 0;
  function uid(p) { uidN += 1; return 'deck-' + p + '-' + uidN; }
  function pathLen(p) { try { return p.getTotalLength(); } catch (e) { return 0; } }
  function localRect(elm, container) {
    var sc = Deck.util.stageRect(elm), cc = Deck.util.stageRect(container);
    return { x: sc.x - cc.x, y: sc.y - cc.y, w: sc.w, h: sc.h };
  }

  var Comp = {};
  Comp.color = color;
  Comp.lambdaColor = Deck.util.lambdaColor;
  Comp.rgb = rgb;
  Comp.svgEl = s;
  Comp.tag = function (key) { var w = h('span'); w.innerHTML = Deck.tagHTML(key); return w.firstChild; };
  Comp.example = function (text) { return h('span', 'example-mark', null, text || '예시'); };

  Comp.svg = function (ctx, parent, o) {
    o = o || {};
    var w = o.w || 800, hh = o.h || 600;
    var el = s('svg', { width: w, height: hh, viewBox: o.viewBox || ('0 0 ' + w + ' ' + hh), 'class': o.className || '', overflow: 'visible' }, parent);
    if (o.style) el.setAttribute('style', o.style);
    return el;
  };

  /* -------------------------------------------------------------- 2D canvas (particles, waffles, funnels) */
  Comp.canvas = function (ctx, parent, o) {
    o = o || {};
    var w = o.w || 800, hh = o.h || 600;
    var cv = h('canvas', o.className || '', parent);
    cv.style.width = w + 'px'; cv.style.height = hh + 'px'; cv.style.display = 'block';
    if (o.x != null) { cv.style.position = 'absolute'; cv.style.left = o.x + 'px'; cv.style.top = o.y + 'px'; }
    var K = { canvas: cv, w: w, h: hh, g: cv.getContext('2d'), ratio: 1 };
    K.resize = function (initial) {
      var r = Deck.pixelRatio();
      if (initial !== true && r === K.ratio && cv.width === Math.round(w * r)) return;
      K.ratio = r;
      cv.width = Math.round(w * r); cv.height = Math.round(hh * r);
      K.g.setTransform(r, 0, 0, r, 0, 0);
      if (initial !== true && o.onResize) o.onResize(K);   /* redraw after a size change */
    };
    K.clear = function () { K.g.clearRect(0, 0, w, hh); };
    K.resize(true);
    ctx.on(window, 'deck:resize', function () { K.resize(); });
    return K;
  };

  /* -------------------------------------------------------------- G1/G2/G3 arrows */
  Comp.arrow = function (ctx, svg, o) {
    o = o || {};
    var kind = o.kind || 'allow', col = o.color || color(kind === 'plain' ? 'ink2' : kind === 'dashed' ? 'ink3' : kind);
    var width = o.width != null ? o.width : 3, headS = o.head != null ? o.head : 14;
    var p0 = o.from.slice(), p1 = o.to.slice();
    var dx = p1[0] - p0[0], dy = p1[1] - p0[1], L0 = Math.hypot(dx, dy) || 1;
    var nx = -dy / L0, ny = dx / L0, bend = o.bend || 0;
    var c = [(p0[0] + p1[0]) / 2 + nx * bend, (p0[1] + p1[1]) / 2 + ny * bend];
    var sh = o.shorten || [0, 0];
    function toward(a, b, d) { var vx = b[0] - a[0], vy = b[1] - a[1], l = Math.hypot(vx, vy) || 1; return [a[0] + vx / l * d, a[1] + vy / l * d]; }
    if (sh[0]) p0 = toward(p0, c, sh[0]);
    if (sh[1]) p1 = toward(p1, c, sh[1]);
    var tang = Math.atan2(p1[1] - c[1], p1[0] - c[0]);
    var lineEnd = [p1[0] - Math.cos(tang) * headS * 0.7, p1[1] - Math.sin(tang) * headS * 0.7];
    var d = bend ? 'M' + p0[0] + ',' + p0[1] + ' Q' + c[0] + ',' + c[1] + ' ' + lineEnd[0] + ',' + lineEnd[1]
                 : 'M' + p0[0] + ',' + p0[1] + ' L' + lineEnd[0] + ',' + lineEnd[1];
    var g = s('g', { 'class': 'arrow arrow-' + kind }, svg);
    var A = { g: g, kind: kind, from: p0, to: p1, ctrl: c };
    var strands = [];
    if (kind === 'cpr') {
      var lam = o.lambda != null ? o.lambda : 0.5;
      strands.push(s('path', { d: d, fill: 'none', stroke: col, 'stroke-width': 1 + 4 * lam, 'stroke-linecap': 'round', transform: 'translate(' + (nx * 3) + ',' + (ny * 3) + ')' }, g));
      strands.push(s('path', { d: d, fill: 'none', stroke: col, 'stroke-width': 1 + 4 * (1 - lam), 'stroke-linecap': 'round', 'stroke-opacity': 0.8, transform: 'translate(' + (-nx * 3) + ',' + (-ny * 3) + ')' }, g));
    } else {
      strands.push(s('path', { d: d, fill: 'none', stroke: col, 'stroke-width': width, 'stroke-linecap': 'round', 'stroke-dasharray': (o.dashed || kind === 'dashed') ? '6 7' : null }, g));
    }
    A.path = strands[0]; A.strands = strands;
    var hx = p1[0], hy = p1[1], a1 = tang + Math.PI * 0.84, a2 = tang - Math.PI * 0.84;
    A.head = s('path', { d: 'M' + hx + ',' + hy + ' L' + (hx + Math.cos(a1) * headS) + ',' + (hy + Math.sin(a1) * headS) +
      ' L' + (hx + Math.cos(a2) * headS) + ',' + (hy + Math.sin(a2) * headS) + 'Z', fill: col }, g);
    if (kind === 'allow') {
      A.key = s('circle', { cx: p0[0], cy: p0[1], r: Math.max(4.5, width + 2), fill: COL.bg, stroke: col, 'stroke-width': 2 }, g);
      if (o.glow !== false) g.setAttribute('class', g.getAttribute('class') + ' glow-allow');
    }
    if (o.label != null) {
      /* labelOffset > 0 puts the label on the upper side of the arrow, < 0 below */
      var k = (o.labelOffset != null ? o.labelOffset : 20) * (ny > 0 ? -1 : 1);
      var mx = 0.25 * p0[0] + 0.5 * c[0] + 0.25 * p1[0], my = 0.25 * p0[1] + 0.5 * c[1] + 0.25 * p1[1];
      A.label = s('text', { x: mx + nx * k, y: my + ny * k, 'text-anchor': 'middle', 'dominant-baseline': 'middle',
        fill: o.labelColor || col, 'font-size': o.labelSize || 24, 'font-weight': 700, 'class': 'tnum' }, g);
      A.label.textContent = o.label;
    }
    A.length = pathLen(A.path);
    A.pointAt = function (t) {
      var L = pathLen(A.path) || 1, p = A.path.getPointAtLength(Math.max(0, Math.min(1, t)) * L);
      return { x: p.x, y: p.y };
    };
    function setHidden() {
      var L = pathLen(A.path) || 1;
      strands.forEach(function (p) { gsap.set(p, { strokeDasharray: L + ' ' + L, strokeDashoffset: L, autoAlpha: 0 }); });
      gsap.set([A.head, A.key, A.label].filter(Boolean), { autoAlpha: 0 });
    }
    function clearDash() { strands.forEach(function (p) { p.style.strokeDasharray = (o.dashed || kind === 'dashed') ? '6 7' : ''; p.style.strokeDashoffset = ''; }); }
    if (o.hidden) setHidden();
    A.draw = function (opt) {
      opt = opt || {};
      var L = pathLen(A.path) || 1, tl = gsap.timeline({ delay: opt.delay || 0 });
      var dd = dur(ctx, opt.duration != null ? opt.duration : D.m);
      if (A.key) tl.fromTo(A.key, { autoAlpha: 0, scale: 0.3, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.25), ease: E.stamp }, 0);
      tl.set(strands, { autoAlpha: 1 }, 0);
      tl.fromTo(strands, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: dd, ease: 'power2.inOut', onComplete: clearDash }, 0);
      tl.fromTo(A.head, { autoAlpha: 0, scale: 0.4, transformOrigin: p1[0] + 'px ' + p1[1] + 'px' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.25), ease: E.out }, dd * 0.85);
      if (A.label) tl.fromTo(A.label, { autoAlpha: 0, y: 6 }, { autoAlpha: 1, y: 0, duration: dur(ctx, D.s), ease: E.out }, dd * 0.8);
      if (kind === 'xfer' && o.flow !== false) tl.call(function () { A.flow(true); }, null, dd);
      return tl;
    };
    A.show = function () { clearDash(); gsap.set(strands.concat([A.head, A.key, A.label].filter(Boolean)), { autoAlpha: 1 }); gsap.set(A.g, { autoAlpha: 1 }); return A; };
    A.hide = function () { setHidden(); return A; };
    A.cut = function (opt) { /* revoke: breaks off from the spender end */
      opt = opt || {};
      var L = pathLen(A.path) || 1, tl = gsap.timeline({ delay: opt.delay || 0 });
      A.flow(false);
      tl.to(A.head, { autoAlpha: 0, scale: 0.4, transformOrigin: p1[0] + 'px ' + p1[1] + 'px', duration: dur(ctx, 0.15) }, 0);
      tl.fromTo(strands, { strokeDasharray: L + ' ' + L, strokeDashoffset: 0 }, { strokeDashoffset: L, duration: dur(ctx, opt.duration != null ? opt.duration : 0.4), ease: 'power2.in' }, 0.05);
      tl.to([A.key, A.label].filter(Boolean), { autoAlpha: 0, duration: dur(ctx, 0.2) }, '>-0.1');
      tl.set(strands, { autoAlpha: 0 });
      return tl;
    };
    var coins = null, coinTw = null;
    A.flow = function (on) {
      if (on === false) { if (coinTw) { coinTw.kill(); coinTw = null; } if (coins) coins.forEach(function (c2) { c2.remove(); }); coins = null; return A; }
      if (coins || red(ctx)) return A;
      coins = [0, 1, 2].map(function () { return s('circle', { r: Math.max(4, width + 1.5), fill: col, 'fill-opacity': 0.6, stroke: COL.bg, 'stroke-width': 1.5 }, g); });
      var st = { t: 0 }, L = pathLen(A.path) || 1;
      coinTw = gsap.to(st, { t: 1, duration: o.flowPeriod || 2.4, ease: 'none', repeat: -1, onUpdate: function () {
        for (var i = 0; i < 3; i++) {
          var tt = (st.t + i / 3) % 1, p = A.path.getPointAtLength(tt * L);
          coins[i].setAttribute('cx', p.x); coins[i].setAttribute('cy', p.y);
          coins[i].setAttribute('opacity', Math.min(1, Math.min(tt, 1 - tt) * 8));
        }
      } });
      return A;
    };
    A.setLabel = function (text, opt) { if (!A.label) return null; return Comp.swap(ctx, A.label, text, opt); };
    A.setWidth = function (w, opt) { return gsap.to(strands, { attr: { 'stroke-width': w }, duration: dur(ctx, (opt && opt.duration) || D.m), ease: E.io }); };
    A.setLambda = function (lam, opt) {
      if (kind !== 'cpr') return null;
      var dd = dur(ctx, (opt && opt.duration) || D.m), tl = gsap.timeline();
      tl.to(strands[0], { attr: { 'stroke-width': 1 + 4 * lam }, duration: dd, ease: E.io }, 0);
      tl.to(strands[1], { attr: { 'stroke-width': 1 + 4 * (1 - lam) }, duration: dd, ease: E.io }, 0);
      return tl;
    };
    A.glow = function (on) { g.classList.toggle('glow-allow', on !== false && kind === 'allow'); g.classList.toggle('glow-xfer', on !== false && kind === 'xfer'); return A; };
    A.remove = function () { A.flow(false); if (g.parentNode) g.parentNode.removeChild(g); };
    if (!o.hidden && kind === 'xfer' && o.flow) A.flow(true);
    return A;
  };

  /* -------------------------------------------------------------- G4 contract box, G5 EOA dot */
  Comp.contract = function (ctx, svg, o) {
    o = o || {};
    var sz = o.size || 56, x = o.x, y = o.y;
    var g = s('g', { 'class': 'node node-contract', transform: 'translate(' + x + ',' + y + ')' }, svg);
    var r = s('rect', { x: -sz / 2, y: -sz / 2, width: sz, height: sz, rx: Math.round(sz * 0.22), fill: COL.bg2, stroke: o.stroke || COL.ink2, 'stroke-width': 2,
      'stroke-dasharray': o.dashed ? '5 5' : null }, g);
    var t = s('text', { x: 0, y: 1, 'text-anchor': 'middle', 'dominant-baseline': 'middle', fill: o.stroke || COL.ink2, 'font-size': Math.round(sz * 0.4), 'class': 'svg-mono' }, g);
    t.textContent = '{ }';
    var N = { g: g, rect: r, x: x, y: y, size: sz };
    if (o.label != null) {
      N.label = s('text', { x: 0, y: sz / 2 + 30, 'text-anchor': 'middle', fill: COL.ink2, 'font-size': o.labelSize || 22, 'font-weight': 600 }, g);
      N.label.textContent = o.label;
    }
    if (o.sub != null) {
      N.sub = s('text', { x: 0, y: sz / 2 + 56, 'text-anchor': 'middle', fill: COL.ink3, 'font-size': 18 }, g);
      N.sub.textContent = o.sub;
    }
    if (o.hidden) gsap.set(g, { autoAlpha: 0 });
    N.pop = function (opt) {
      opt = opt || {};
      return gsap.fromTo(g, { autoAlpha: 0, scale: 0.5, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, D.s), ease: E.stamp, delay: opt.delay || 0 });
    };
    N.badge = function (text, opt) {
      opt = opt || {};
      if (!N.badgeG) {
        N.badgeG = s('g', { transform: 'translate(0,' + (-sz / 2 - 22) + ')' }, g);
        N.badgeR = s('rect', { x: -40, y: -16, width: 80, height: 32, rx: 16, fill: COL.bg3, stroke: opt.color || COL.ink, 'stroke-width': 1.5 }, N.badgeG);
        N.badgeT = s('text', { x: 0, y: 1, 'text-anchor': 'middle', 'dominant-baseline': 'middle', fill: opt.color || COL.ink, 'font-size': 18, 'font-weight': 700, 'class': 'tnum' }, N.badgeG);
      }
      N.badgeT.textContent = text;
      var w = Math.max(56, String(text).length * 11 + 26);
      N.badgeR.setAttribute('x', -w / 2); N.badgeR.setAttribute('width', w);
      return gsap.fromTo(N.badgeG, { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, D.s), ease: E.stamp, delay: opt.delay || 0 });
    };
    N.flash = function () { return gsap.fromTo(t, { fill: COL.ink }, { fill: o.stroke || COL.ink2, duration: dur(ctx, 0.6), ease: 'power2.out' }); };
    return N;
  };
  Comp.eoa = function (ctx, svg, o) {
    o = o || {};
    var r = o.r || 14;
    var g = s('g', { 'class': 'node node-eoa', transform: 'translate(' + o.x + ',' + o.y + ')' }, svg);
    var c = s('circle', { cx: 0, cy: 0, r: r, fill: 'none', stroke: COL.ink3, 'stroke-width': 2.5 }, g);
    var N = { g: g, circle: c, x: o.x, y: o.y, r: r };
    if (o.label != null) {
      N.label = s('text', { x: 0, y: r + 30, 'text-anchor': 'middle', fill: COL.ink2, 'font-size': o.labelSize || 22, 'font-weight': 600 }, g);
      N.label.textContent = o.label;
    }
    if (o.hidden) gsap.set(g, { autoAlpha: 0 });
    N.pop = function (opt) {
      opt = opt || {};
      return gsap.fromTo(g, { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, D.s), ease: E.stamp, delay: opt.delay || 0 });
    };
    N.tag = function (text) {
      if (!N.tagT) N.tagT = s('text', { x: 0, y: -r - 14, 'text-anchor': 'middle', fill: COL.ink3, 'font-size': 18 }, g);
      N.tagT.textContent = text;
      return gsap.fromTo(N.tagT, { autoAlpha: 0, y: 6 }, { autoAlpha: 1, y: 0, duration: dur(ctx, D.s) });
    };
    return N;
  };

  /* -------------------------------------------------------------- G6 walker (light dot) */
  Comp.walker = function (ctx, svg, o) {
    o = o || {};
    var r = o.r || 7, nTrail = o.trail != null ? o.trail : 5;
    var g = s('g', { 'class': 'walker', 'pointer-events': 'none' }, svg);
    var trail = [];
    for (var i = nTrail; i >= 1; i--) trail.unshift(s('circle', { r: r * (1 - i * 0.12), fill: '#fff', 'fill-opacity': 0.22 - i * 0.03 }, g));
    var dot = s('circle', { r: r, fill: '#fff', 'class': 'glow-white' }, g);
    var W = { g: g, dot: dot, x: o.x || 0, y: o.y || 0, hist: [] };
    function place(x, y) { W.x = x; W.y = y; dot.setAttribute('cx', x); dot.setAttribute('cy', y); }
    place(W.x, W.y);
    for (var k = 0; k < nTrail; k++) { trail[k].setAttribute('cx', W.x); trail[k].setAttribute('cy', W.y); }
    var tp = trail.map(function () { return { x: W.x, y: W.y }; });
    ctx.raf(function () {
      var tx = W.x, ty = W.y;
      for (var i2 = 0; i2 < tp.length; i2++) {
        tp[i2].x += (tx - tp[i2].x) * 0.35; tp[i2].y += (ty - tp[i2].y) * 0.35;
        trail[i2].setAttribute('cx', tp[i2].x.toFixed(1)); trail[i2].setAttribute('cy', tp[i2].y.toFixed(1));
        tx = tp[i2].x; ty = tp[i2].y;
      }
    });
    if (o.hidden) gsap.set(g, { autoAlpha: 0 });
    W.set = function (x, y) { place(x, y); tp.forEach(function (p) { p.x = x; p.y = y; }); return W; };
    W.moveTo = function (x, y, opt) {
      opt = opt || {};
      var st = { x: W.x, y: W.y };
      return gsap.to(st, { x: x, y: y, duration: dur(ctx, opt.duration != null ? opt.duration : 0.5), ease: opt.ease || 'power2.inOut', delay: opt.delay || 0,
        onUpdate: function () { place(st.x, st.y); } });
    };
    W.along = function (pathEl, opt) {
      opt = opt || {};
      var L = pathLen(pathEl), st = { t: opt.from || 0 };
      return gsap.to(st, { t: opt.to != null ? opt.to : 1, duration: dur(ctx, opt.duration != null ? opt.duration : 0.5), ease: opt.ease || 'power1.inOut', delay: opt.delay || 0,
        onUpdate: function () { var p = pathEl.getPointAtLength(st.t * L); place(p.x, p.y); } });
    };
    W.pulse = function () { return gsap.fromTo(dot, { attr: { r: r * 2 } }, { attr: { r: r }, duration: dur(ctx, 0.5), ease: 'power3.out' }); };
    W.show = function (opt) { return gsap.to(g, { autoAlpha: 1, duration: dur(ctx, (opt && opt.duration) || 0.3) }); };
    W.hide = function (opt) { return gsap.to(g, { autoAlpha: 0, duration: dur(ctx, (opt && opt.duration) || 0.3) }); };
    return W;
  };

  /* -------------------------------------------------------------- G8 tally (正) */
  Comp.tally = function (ctx, svg, o) {
    o = o || {};
    var S = o.size || 44, x0 = o.x || 0, y0 = o.y || 0;
    var g = s('g', { 'class': 'tally', transform: 'translate(' + x0 + ',' + y0 + ')' }, svg);
    var border = s('rect', { x: -10, y: -10, width: S + 20, height: S + 20, rx: 10, fill: 'none', stroke: COL.deg, 'stroke-width': 1.5, 'stroke-dasharray': '4 5', opacity: 0.7 }, g);
    var strokes = [];
    var T = { g: g, count: 0, border: border, strokes: strokes };
    /* stroke order of 正: top bar, centre stem, middle right bar, left stem, base */
    function glyph(ix) {
      var ox = ix * (S + 18), u = S / 40;
      return [[ox + 4 * u, 4 * u, ox + 36 * u, 4 * u], [ox + 20 * u, 4 * u, ox + 20 * u, 37 * u], [ox + 20 * u, 20 * u, ox + 33 * u, 20 * u],
              [ox + 8 * u, 18 * u, ox + 8 * u, 37 * u], [ox + 2 * u, 37 * u, ox + 38 * u, 37 * u]];
    }
    function ensure(n) {
      while (strokes.length < n) {
        var gi = Math.floor(strokes.length / 5), seg = glyph(gi)[strokes.length % 5];
        var ln = s('line', { x1: seg[0], y1: seg[1], x2: seg[2], y2: seg[3], stroke: COL.deg, 'stroke-width': 4, 'stroke-linecap': 'round' }, g);
        var L = Math.hypot(seg[2] - seg[0], seg[3] - seg[1]);
        gsap.set(ln, { strokeDasharray: L + ' ' + L, strokeDashoffset: L, autoAlpha: 0 });
        strokes.push(ln);
        border.setAttribute('width', (gi + 1) * (S + 18) + 2);
      }
    }
    T.add = function (k, opt) {
      opt = opt || {};
      k = k == null ? 1 : k;
      var from = T.count; ensure(from + k); T.count = from + k;
      var tl = gsap.timeline({ delay: opt.delay || 0 });
      for (var i = from; i < from + k; i++) {
        var at = (i - from) * (opt.stagger != null ? opt.stagger : 0.18);
        tl.set(strokes[i], { autoAlpha: 1 }, at);
        tl.to(strokes[i], { strokeDashoffset: 0, duration: dur(ctx, 0.22), ease: 'power2.out' }, at);
      }
      return tl;
    };
    T.set = function (n) { ensure(n); strokes.forEach(function (l, i) { gsap.set(l, { strokeDashoffset: i < n ? 0 : pathLen(l) || 40, autoAlpha: i < n ? 1 : 0 }); }); T.count = n; return T; };
    if (o.count) T.set(o.count);
    return T;
  };

  /* -------------------------------------------------------------- G10 stamp */
  Comp.stamp = function (ctx, parent, o) {
    o = o || {};
    var ok = o.ok !== false;
    var el = h('div', 'stamp' + (ok ? '' : ' fail'), parent, Deck.util.esc(o.text || (ok ? '충족 ✓' : '미충족 ✕')));
    if (o.x != null) { el.style.position = 'absolute'; el.style.left = o.x + 'px'; el.style.top = o.y + 'px'; }
    gsap.set(el, { autoAlpha: 0 });
    return {
      el: el,
      slam: function (opt) {
        opt = opt || {};
        var tl = gsap.timeline({ delay: opt.delay || 0 });
        if (red(ctx)) { tl.to(el, { autoAlpha: 1, duration: 0.2 }); return tl; }
        tl.fromTo(el, { autoAlpha: 0, scale: 1.4, rotation: -8 }, { autoAlpha: 1, scale: 1, rotation: 0, duration: D.s, ease: E.stamp });
        tl.to(el, { x: 3, duration: 0.05, yoyo: true, repeat: 3, ease: 'none' }).set(el, { x: 0 });
        return tl;
      }
    };
  };

  /* -------------------------------------------------------------- G12 freeze pin */
  function snowflake(g, cx, cy, r, col) {
    for (var i = 0; i < 3; i++) {
      var a = i * Math.PI / 3;
      s('line', { x1: cx - Math.cos(a) * r, y1: cy - Math.sin(a) * r, x2: cx + Math.cos(a) * r, y2: cy + Math.sin(a) * r, stroke: col, 'stroke-width': 2, 'stroke-linecap': 'round' }, g);
    }
  }
  Comp.pin = function (ctx, svg, o) {
    o = o || {};
    var col = color(o.color || 'ink');
    var g = s('g', { 'class': 'pin' }, svg);
    var line = s('line', { x1: o.x, y1: o.y0, x2: o.x, y2: o.y1, stroke: col, 'stroke-width': 1.5, 'stroke-dasharray': '5 6', opacity: 0.85 }, g);
    var head = s('g', {}, g);
    s('circle', { cx: o.x, cy: o.y0, r: 15, fill: COL.bg, stroke: col, 'stroke-width': 2 }, head);
    snowflake(head, o.x, o.y0, 8, col);
    var P = { g: g, line: line, head: head };
    if (o.label != null) {
      P.label = s('text', { x: o.x, y: o.y0 - 28, 'text-anchor': 'middle', fill: col, 'font-size': o.labelSize || 20, 'font-weight': 600 }, g);
      P.label.textContent = o.label;
    }
    if (o.hidden !== false) gsap.set(g, { autoAlpha: 0 });
    P.drop = function (opt) {
      opt = opt || {};
      var L = Math.abs(o.y1 - o.y0), tl = gsap.timeline({ delay: opt.delay || 0 });
      tl.set(g, { autoAlpha: 1 });
      if (red(ctx)) return tl;
      tl.fromTo(head, { y: -70, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5, ease: 'bounce.out' }, 0);
      tl.fromTo(line, { attr: { y2: o.y0 } }, { attr: { y2: o.y1 }, duration: 0.5, ease: 'power2.out' }, 0.35);
      if (P.label) tl.fromTo(P.label, { autoAlpha: 0, y: 8 }, { autoAlpha: 1, y: 0, duration: D.s }, 0.45);
      tl.to(head, { rotation: 6, transformOrigin: o.x + 'px ' + o.y0 + 'px', duration: 0.08, yoyo: true, repeat: 1 }, 0.5);
      void L;
      return tl;
    };
    return P;
  };

  /* -------------------------------------------------------------- G13 lambda dial */
  Comp.dial = function (ctx, parent, o) {
    o = o || {};
    var size = o.size || 260, R = size / 2 - 22, cx = size / 2, cy = size / 2 + 6;
    var snap = o.snap || [0, 0.25, 0.5, 0.75, 1];
    var wrap = h('div', 'dial' + (o.interactive ? ' interactive' : ''), parent);
    if (o.x != null) { wrap.style.position = 'absolute'; wrap.style.left = o.x + 'px'; wrap.style.top = o.y + 'px'; }
    var svg = s('svg', { width: size, height: size / 2 + 60, viewBox: '0 0 ' + size + ' ' + (size / 2 + 60) }, wrap);
    function ang(v) { return Math.PI - v * Math.PI; } /* v=0 left, v=1 right */
    function pt(v, rr) { var a = ang(v); return [cx + Math.cos(a) * rr, cy - Math.sin(a) * rr]; }
    var segs = 48;
    for (var i = 0; i < segs; i++) {
      var a0 = pt(i / segs, R), a1 = pt((i + 1) / segs, R);
      s('path', { d: 'M' + a0[0] + ',' + a0[1] + ' A' + R + ',' + R + ' 0 0 1 ' + a1[0] + ',' + a1[1], stroke: Deck.util.lambdaColor((i + 0.5) / segs), 'stroke-width': 10, fill: 'none', 'stroke-linecap': 'butt' }, svg);
    }
    snap.forEach(function (v) {
      var p0 = pt(v, R - 12), p1 = pt(v, R + 12), pl = pt(v, R + 30);
      s('line', { x1: p0[0], y1: p0[1], x2: p1[0], y2: p1[1], stroke: COL.ink2, 'stroke-width': 2 }, svg);
      var t = s('text', { x: pl[0], y: pl[1] + 6, 'text-anchor': 'middle', fill: COL.ink2, 'font-size': 17, 'class': 'svg-mono' }, svg);
      t.textContent = v === 0 ? '0' : v === 1 ? '1' : String(v).replace(/^0/, '');
    });
    var needle = s('g', {}, svg);
    var nl = s('line', { x1: cx, y1: cy, x2: cx - (R - 20), y2: cy, stroke: COL.ink, 'stroke-width': 4, 'stroke-linecap': 'round' }, needle);
    var tip = s('circle', { cx: cx - (R - 20), cy: cy, r: 8, fill: COL.ink }, needle);
    s('circle', { cx: cx, cy: cy, r: 10, fill: COL.bg3, stroke: COL.ink, 'stroke-width': 2 }, svg);
    var readout = s('text', { x: cx, y: cy + 44, 'text-anchor': 'middle', fill: COL.ink, 'font-size': 26, 'font-weight': 700, 'class': 'tnum' }, svg);
    var Dl = { el: wrap, svg: svg, value: o.value != null ? o.value : 1 };
    var st = { v: Dl.value };
    function render() {
      var deg = st.v * 180; /* clockwise from the λ=0 (left) position */
      needle.setAttribute('transform', 'rotate(' + deg + ' ' + cx + ' ' + cy + ')');
      var c = Deck.util.lambdaColor(st.v);
      nl.setAttribute('stroke', c); tip.setAttribute('fill', c);
      readout.textContent = 'λ = ' + (Math.abs(st.v - Math.round(st.v * 100) / 100) < 1e-9 ? String(Math.round(st.v * 100) / 100) : st.v.toFixed(2));
    }
    render();
    Dl.set = function (v, opt) {
      opt = opt || {};
      Dl.value = v;
      return gsap.to(st, { v: v, duration: dur(ctx, opt.duration != null ? opt.duration : D.l), ease: opt.ease || E.io, onUpdate: render, onComplete: function () { st.v = v; render(); } });
    };
    Dl.arc = function (v0, v1, col) {
      var p0 = pt(v0, R + 20), p1 = pt(v1, R + 20);
      var p = s('path', { d: 'M' + p0[0] + ',' + p0[1] + ' A' + (R + 20) + ',' + (R + 20) + ' 0 0 1 ' + p1[0] + ',' + p1[1], stroke: color(col || 'hi'), 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }, svg);
      var L = pathLen(p);
      return gsap.fromTo(p, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur(ctx, D.m), ease: 'power2.inOut' });
    };
    if (o.interactive) {
      var dragging = false;
      var pick = function (e) {
        var r = svg.getBoundingClientRect(), sc = r.width / size;
        var x = (e.clientX - r.left) / sc - cx, y = cy - (e.clientY - r.top) / sc;
        var a = Math.atan2(Math.max(0, y), x), v = 1 - a / Math.PI;
        var best = snap[0];
        snap.forEach(function (sv) { if (Math.abs(sv - v) < Math.abs(best - v)) best = sv; });
        if (best !== Dl.value) { Dl.set(best, { duration: 0.35 }); if (o.onChange) o.onChange(best); }
      };
      ctx.on(wrap, 'pointerdown', function (e) { dragging = true; try { wrap.setPointerCapture(e.pointerId); } catch (er) { /* ignore */ } pick(e); e.stopPropagation(); });
      ctx.on(wrap, 'pointermove', function (e) { if (dragging) pick(e); });
      ctx.on(wrap, 'pointerup', function () { dragging = false; });
      ctx.on(wrap, 'click', function (e) { e.stopPropagation(); });
    }
    return Dl;
  };

  /* -------------------------------------------------------------- G14 farm */
  Comp.farm = function (ctx, svg, o) {
    o = o || {};
    var n = o.n || 20, R = o.radius || 120, dr = o.dotR || 9, rnd = Deck.util.rng(o.seed == null ? 42 : o.seed);
    var g = s('g', { 'class': 'farm' }, svg);
    var dots = [];
    for (var i = 0; i < n; i++) {
      var x, y;
      if (o.layout === 'cloud') { var a = rnd() * Math.PI * 2, rr = Math.sqrt(rnd()) * R; x = o.cx + Math.cos(a) * rr; y = o.cy + Math.sin(a) * rr; }
      else { var a2 = -Math.PI / 2 + i / n * Math.PI * 2; x = o.cx + Math.cos(a2) * R; y = o.cy + Math.sin(a2) * R; }
      var c = s('circle', { cx: x, cy: y, r: dr, fill: COL.bg, stroke: COL.hi, 'stroke-width': 2, 'stroke-dasharray': '3 3' }, g);
      gsap.set(c, { autoAlpha: 0 });
      dots.push(c);
    }
    var F = { g: g, dots: dots, positions: dots.map(function (d) { return [+d.getAttribute('cx'), +d.getAttribute('cy')]; }) };
    F.grow = function (opt) {
      opt = opt || {};
      var a = opt.from || 0, b = opt.to != null ? opt.to : n, tl = gsap.timeline({ delay: opt.delay || 0 });
      var total = dur(ctx, opt.duration != null ? opt.duration : Math.min(1.6, 0.06 * (b - a)));
      var sub = dots.slice(a, b);
      tl.fromTo(sub, { autoAlpha: 0, scale: 0, transformOrigin: '50% 50%' }, { autoAlpha: 1, scale: 1, duration: dur(ctx, 0.3), ease: E.stamp, stagger: sub.length > 1 ? total / sub.length : 0 });
      return tl;
    };
    return F;
  };

  /* -------------------------------------------------------------- G15 water cup */
  Comp.cup = function (ctx, svg, o) {
    o = o || {};
    var w = o.w || 56, hh = o.h || 66, x = o.x - w / 2, y = o.y, max = o.max || 1, dec = o.decimals != null ? o.decimals : 4;
    var col = color(o.color || 'xfer');
    var g = s('g', { 'class': 'cup' }, svg);
    var clipId = uid('cupclip');
    var defs = s('defs', {}, g);
    var cp = s('clipPath', { id: clipId }, defs);
    s('path', { d: 'M' + x + ',' + y + ' L' + (x + w) + ',' + y + ' L' + (x + w - 6) + ',' + (y + hh) + ' L' + (x + 6) + ',' + (y + hh) + 'Z' }, cp);
    var water = s('rect', { x: x - 2, y: y + hh, width: w + 4, height: 0, fill: col, 'fill-opacity': 0.55, 'clip-path': 'url(#' + clipId + ')' }, g);
    var surf = s('line', { x1: x, x2: x + w, y1: y + hh, y2: y + hh, stroke: col, 'stroke-width': 2, 'clip-path': 'url(#' + clipId + ')' }, g);
    s('path', { d: 'M' + x + ',' + y + ' L' + (x + 6) + ',' + (y + hh) + ' L' + (x + w - 6) + ',' + (y + hh) + ' L' + (x + w) + ',' + y, fill: 'none', stroke: COL.ink2, 'stroke-width': 2, 'stroke-linejoin': 'round' }, g);
    var U = { g: g, value: 0 };
    if (o.label !== false) {
      U.label = s('text', { x: x + w / 2, y: y + hh + 28, 'text-anchor': 'middle', fill: COL.ink2, 'font-size': 18, 'class': 'tnum svg-mono' }, g);
    }
    var st = { v: 0 };
    function render() {
      var f = Math.max(0, Math.min(1, st.v / max)), wy = y + hh - f * hh;
      water.setAttribute('y', wy); water.setAttribute('height', f * hh + 1);
      surf.setAttribute('y1', wy); surf.setAttribute('y2', wy);
      if (U.label) U.label.textContent = fmt(st.v, dec);
    }
    U.set = function (v, opt) {
      opt = opt || {};
      U.value = v;
      if (opt.duration === 0) { st.v = v; render(); return gsap.to({}, { duration: 0 }); }
      return gsap.to(st, { v: v, duration: dur(ctx, opt.duration != null ? opt.duration : D.m), ease: opt.ease || 'back.out(1.6)', delay: opt.delay || 0, onUpdate: render, onComplete: function () { st.v = v; render(); } });
    };
    st.v = o.value || 0; U.value = st.v; render();
    return U;
  };

  /* -------------------------------------------------------------- graph widget (+ G7 small world) */
  Comp.graph = function (ctx, target, o) {
    o = o || {};
    var svg = target && target.namespaceURI === NS && target.tagName.toLowerCase() === 'svg' ? target : Comp.svg(ctx, target, { w: o.w || 900, h: o.h || 600 });
    var G = { svg: svg, nodes: {}, edges: [], cups: {} };
    var ew = o.weightWidth || function (w) { return 2 + 2.2 * (w || 1); };
    var edgeLayer = s('g', { 'class': 'edges' }, svg), nodeLayer = s('g', { 'class': 'nodes' }, svg), cupLayer = s('g', { 'class': 'cups' }, svg);
    (o.nodes || []).forEach(function (n) {
      var N;
      if (n.kind === 'eoa') N = Comp.eoa(ctx, nodeLayer, { x: n.x, y: n.y, r: n.size || 16, label: n.label, hidden: o.hidden });
      else if (n.kind === 'farm') { N = Comp.eoa(ctx, nodeLayer, { x: n.x, y: n.y, r: n.size || 12, label: n.label, hidden: o.hidden }); N.circle.setAttribute('stroke', COL.hi); N.circle.setAttribute('stroke-dasharray', '3 3'); }
      else if (n.kind === 'dot') N = Comp.eoa(ctx, nodeLayer, { x: n.x, y: n.y, r: n.size || 6, label: n.label, hidden: o.hidden });
      else N = Comp.contract(ctx, nodeLayer, { x: n.x, y: n.y, size: n.size || 60, label: n.label, sub: n.sub, hidden: o.hidden, dashed: n.dashed, stroke: n.stroke });
      N.id = n.id; N.kind = n.kind || 'contract'; N.radius = n.kind === 'eoa' || n.kind === 'farm' || n.kind === 'dot' ? (n.size || 16) : (n.size || 60) * 0.62;
      G.nodes[n.id] = N;
    });
    (o.edges || []).forEach(function (e) {
      var a = G.nodes[e.from], b = G.nodes[e.to];
      if (!a || !b) return;
      var A = Comp.arrow(ctx, edgeLayer, { from: [a.x, a.y], to: [b.x, b.y], kind: e.kind || 'allow', width: e.width || ew(e.w), bend: e.bend || 0,
        shorten: [a.radius + 6, b.radius + 8], label: o.showWeights === false || e.w == null ? e.label : (e.label != null ? e.label : String(e.w)),
        labelOffset: e.labelOffset, hidden: o.hidden, head: e.head || 16, dashed: e.dashed, flow: e.flow });
      A.fromId = e.from; A.toId = e.to; A.w = e.w == null ? 1 : e.w;
      G.edges.push(A);
    });
    if (o.cups) {
      var cu = o.cups === true ? {} : o.cups;
      Object.keys(G.nodes).forEach(function (id) {
        var N = G.nodes[id];
        G.cups[id] = Comp.cup(ctx, cupLayer, { x: N.x, y: N.y + (cu.dy || 92), w: cu.w || 50, h: cu.h || 60, max: cu.max || 1, value: cu.value || 0, decimals: cu.decimals, color: cu.color || 'xfer', label: cu.label });
        if (o.hidden) gsap.set(G.cups[id].g, { autoAlpha: 0 });
      });
    }
    G.node = function (id) { return G.nodes[id]; };
    G.edge = function (from, to) { for (var i = 0; i < G.edges.length; i++) if (G.edges[i].fromId === from && G.edges[i].toId === to) return G.edges[i]; return null; };
    G.out = function (id) { return G.edges.filter(function (e) { return e.fromId === id; }); };
    G.drawIn = function (opt) {
      opt = opt || {};
      var tl = gsap.timeline({ delay: opt.delay || 0 }), st = opt.stagger != null ? opt.stagger : 0.12, i = 0;
      Object.keys(G.nodes).forEach(function (id) { tl.add(G.nodes[id].pop(), i++ * st); });
      var t0 = i * st + 0.1;
      G.edges.forEach(function (A, j) { tl.add(A.draw(), t0 + j * st); });
      if (o.cups) tl.to(Object.keys(G.cups).map(function (k) { return G.cups[k].g; }), { autoAlpha: 1, duration: dur(ctx, D.s), stagger: 0.06 }, t0 + G.edges.length * st);
      return tl;
    };
    G.setCups = function (values, opt) {
      var tl = gsap.timeline();
      var ids = Object.keys(G.nodes);
      ids.forEach(function (id, k) {
        var v = Array.isArray(values) ? values[k] : values[id];
        if (v != null && G.cups[id]) tl.add(G.cups[id].set(v, opt), 0);
      });
      return tl;
    };
    /* G6 walker living on the graph */
    var W = Comp.walker(ctx, svg, { hidden: true });
    W.at = null;
    W.place = function (id) { var N = G.nodes[id]; W.at = id; W.set(N.x, N.y); gsap.set(W.g, { autoAlpha: 1 }); return W; };
    W.hop = function (id, opt) {
      opt = opt || {};
      var from = W.at, A = G.edge(from, id), tl = gsap.timeline({ delay: opt.delay || 0 });
      var N = G.nodes[id];
      if (A) {
        tl.add(W.along(A.path, { duration: opt.duration || 0.5 }));
        tl.add(W.moveTo(N.x, N.y, { duration: dur(ctx, 0.12) }));
      } else { /* teleport: blink out and in */
        tl.to(W.g, { autoAlpha: 0, duration: dur(ctx, 0.12) });
        tl.call(function () { W.set(N.x, N.y); });
        tl.to(W.g, { autoAlpha: 1, duration: dur(ctx, 0.12) });
      }
      tl.call(function () { W.at = id; });
      W.at = id;
      return tl;
    };
    W.walk = function (n, opt) {
      opt = opt || {};
      var rnd = Deck.util.rng(opt.seed == null ? 42 : opt.seed), d = opt.d == null ? 1 : opt.d;
      var ids = Object.keys(G.nodes), at = W.at || ids[0], tl = gsap.timeline({ delay: opt.delay || 0 }), path = [];
      for (var i = 0; i < n; i++) {
        var outs = G.out(at), nxt;
        if (!outs.length || rnd() > d) nxt = ids[Math.floor(rnd() * ids.length)];
        else {
          var tot = outs.reduce(function (acc, e) { return acc + e.w; }, 0), r = rnd() * tot;
          nxt = outs[outs.length - 1].toId;
          for (var k = 0; k < outs.length; k++) { r -= outs[k].w; if (r <= 0) { nxt = outs[k].toId; break; } }
        }
        tl.add(W.hop(nxt, { duration: opt.duration || 0.45 }));
        path.push(nxt); at = nxt;
      }
      tl.path = path;
      return tl;
    };
    G.walker = W;
    return G;
  };
  /* the four-node world of Chapter 2 (G7). Same geometry everywhere it appears. */
  Comp.SMALL_WORLD = {
    nodes: [
      { id: 'A', x: 110, y: 250, kind: 'eoa', label: 'A' },
      { id: 'B', x: 380, y: 110, kind: 'contract', label: 'B' },
      { id: 'C', x: 380, y: 390, kind: 'contract', label: 'C' },
      { id: 'D', x: 650, y: 250, kind: 'contract', label: 'D' }
    ],
    edges: [{ from: 'A', to: 'B', w: 2 }, { from: 'A', to: 'C', w: 1 }, { from: 'B', to: 'D', w: 3 }, { from: 'C', to: 'D', w: 1 }],
    w: 760, h: 560
  };
  Comp.smallWorld = function (ctx, parent, o) {
    o = o || {};
    var SW = Comp.SMALL_WORLD;
    var wrap = h('div', 'small-world', parent);
    wrap.setAttribute('data-shared', o.shared || 'small-world');
    wrap.style.position = 'absolute';
    wrap.style.left = (o.x != null ? o.x : 0) + 'px'; wrap.style.top = (o.y != null ? o.y : 0) + 'px';
    wrap.style.width = SW.w + 'px'; wrap.style.height = SW.h + 'px';
    if (o.scale) { wrap.style.transformOrigin = '0 0'; wrap.style.scale = String(o.scale); }
    var svg = Comp.svg(ctx, wrap, { w: SW.w, h: SW.h });
    var nodes = SW.nodes.map(function (n) { var m = {}; for (var k in n) m[k] = n[k]; if (o.labels && o.labels[n.id] != null) m.label = o.labels[n.id]; if (o.subs && o.subs[n.id] != null) m.sub = o.subs[n.id]; return m; });
    var G = Comp.graph(ctx, svg, { nodes: nodes, edges: SW.edges.map(function (e) { return { from: e.from, to: e.to, w: e.w, kind: o.kind || 'allow' }; }),
      cups: o.cups, hidden: o.hidden, showWeights: o.showWeights });
    G.wrap = wrap;
    return G;
  };

  /* -------------------------------------------------------------- G9 forest plot */
  Comp.forest = function (ctx, parent, o) {
    o = o || {};
    var rows = o.rows || [], rowH = o.rowH || 64, lw = o.labelWidth != null ? o.labelWidth : 380, vw = o.valueWidth != null ? o.valueWidth : 280;
    var W = o.w || 1500, top = o.top != null ? o.top : 20, axisH = 56;
    var H = o.h || (top + rows.length * rowH + axisH);
    var svg = Comp.svg(ctx, parent, { w: W, h: H, className: 'forest' });
    var dom = o.domain || [Math.min(0, d3min(rows)), Math.max(0, d3max(rows))];
    var x0 = lw, x1 = W - vw;
    function x(v) { return x0 + (v - dom[0]) / (dom[1] - dom[0]) * (x1 - x0); }
    var F = { svg: svg, x: x, rows: [] };
    var ticks = o.ticks || niceTicks(dom[0], dom[1], 5);
    var axis = s('g', { 'class': 'axis' }, svg), yAxis = top + rows.length * rowH + 8;
    ticks.forEach(function (t) {
      s('line', { x1: x(t), x2: x(t), y1: top - 6, y2: yAxis, 'class': 'gridline' }, axis);
      var tt = s('text', { x: x(t), y: yAxis + 28, 'text-anchor': 'middle', 'class': 'tnum' }, axis);
      tt.textContent = o.tickFormat ? o.tickFormat(t) : fmt(t, Deck.util.decimalsOf(t) > 2 ? 2 : Deck.util.decimalsOf(t));
    });
    s('line', { x1: x0, x2: x1, y1: yAxis, y2: yAxis }, axis);
    if (o.zero !== false && dom[0] <= 0 && dom[1] >= 0) s('line', { x1: x(0), x2: x(0), y1: top - 10, y2: yAxis, stroke: COL.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, svg);
    if (o.axisLabel) { var al = s('text', { x: (x0 + x1) / 2, y: yAxis + 52, 'text-anchor': 'middle', fill: COL.ink3, 'font-size': 18 }, svg); al.textContent = o.axisLabel; }
    var fm = o.format || function (v) { return fmt(v, 3); };
    rows.forEach(function (r, i) {
      var cy = top + i * rowH + rowH / 2, col = color(r.color || 'ink');
      var g = s('g', { 'class': 'forest-row' }, svg);
      var R = { g: g, data: r, cy: cy };
      R.label = s('text', { x: 0, y: cy + (r.sub ? -4 : 8), fill: COL.ink, 'font-size': 26, 'font-weight': 600 }, g); R.label.textContent = r.label || '';
      if (r.sub) { R.sub = s('text', { x: 0, y: cy + 22, fill: COL.ink3, 'font-size': 18 }, g); R.sub.textContent = r.sub; }
      if (r.ghost) {
        R.gbar = s('line', { x1: x(r.ghost.lo), x2: x(r.ghost.hi), y1: cy + 14, y2: cy + 14, stroke: COL.ink3, 'stroke-width': 3, 'stroke-linecap': 'round', opacity: 0.8 }, g);
        R.gdot = s('circle', { cx: x(r.ghost.est), cy: cy + 14, r: 7, fill: COL.bg, stroke: COL.ink3, 'stroke-width': 2 }, g);
      }
      var by = r.ghost ? cy - 6 : cy;
      if (r.outer) {
        R.outer = s('path', { d: bracket(x(r.outer[0]), by, -1) + ' ' + bracket(x(r.outer[1]), by, 1), fill: 'none', stroke: col, 'stroke-width': 2, opacity: 0.85 }, g);
      }
      R.bar = s('line', { x1: x(r.lo), x2: x(r.hi), y1: by, y2: by, stroke: col, 'stroke-width': 5, 'stroke-linecap': 'round' }, g);
      R.dot = s('circle', { cx: x(r.est), cy: by, r: 10, fill: r.hollow ? COL.bg : col, stroke: col, 'stroke-width': 3 }, g);
      R.value = s('text', { x: W - vw + 28, y: by + 8, fill: COL.ink2, 'font-size': 22, 'class': 'tnum' }, g);
      R.value.textContent = r.text != null ? r.text : fm(r.est) + ' [' + fm(r.lo) + ', ' + fm(r.hi) + ']';
      if (o.hidden) gsap.set(g, { autoAlpha: 0 });
      F.rows.push(R);
    });
    function bracket(px, y, side) { return 'M' + (px - side * 6) + ',' + (y - 13) + ' L' + px + ',' + (y - 13) + ' L' + px + ',' + (y + 13) + ' L' + (px - side * 6) + ',' + (y + 13); }
    F.show = function (i, opt) {
      opt = opt || {};
      var R = F.rows[i], r = R.data, tl = gsap.timeline({ delay: opt.delay || 0 }), z = x(Math.max(dom[0], Math.min(dom[1], 0)));
      var dd = dur(ctx, opt.duration != null ? opt.duration : D.m);
      tl.set(R.g, { autoAlpha: 1 }, 0);
      tl.fromTo([R.label, R.sub].filter(Boolean), { autoAlpha: 0, x: -16 }, { autoAlpha: 1, x: 0, duration: dur(ctx, D.s), ease: E.out }, 0);
      tl.fromTo(R.bar, { attr: { x1: z, x2: z } }, { attr: { x1: x(r.lo), x2: x(r.hi) }, duration: dd, ease: E.out }, 0.1);
      tl.fromTo(R.dot, { attr: { cx: z }, autoAlpha: 0 }, { attr: { cx: x(r.est) }, autoAlpha: 1, duration: dd, ease: E.out }, 0.1);
      if (R.outer) tl.fromTo(R.outer, { autoAlpha: 0 }, { autoAlpha: 0.85, duration: dur(ctx, D.s) }, 0.1 + dd);
      if (R.gbar) tl.fromTo([R.gbar, R.gdot], { autoAlpha: 0 }, { autoAlpha: 0.8, duration: dur(ctx, D.s) }, 0.1 + dd * 0.6);
      tl.fromTo(R.value, { autoAlpha: 0 }, { autoAlpha: 1, duration: dur(ctx, D.s) }, 0.1 + dd * 0.7);
      return tl;
    };
    F.grow = function (opt) {
      opt = opt || {};
      var tl = gsap.timeline({ delay: opt.delay || 0 });
      F.rows.forEach(function (R, i) { tl.add(F.show(i, opt), i * (opt.stagger != null ? opt.stagger : 0.12)); });
      return tl;
    };
    F.dim = function (keep, opt) {
      keep = [].concat(keep);
      return gsap.to(F.rows.map(function (R) { return R.g; }), { opacity: function (i) { return keep.indexOf(i) >= 0 ? 1 : (opt && opt.opacity != null ? opt.opacity : 0.25); }, duration: dur(ctx, D.s) });
    };
    F.undim = function () { return gsap.to(F.rows.map(function (R) { return R.g; }), { opacity: 1, duration: dur(ctx, D.s) }); };
    F.highlight = function (i, opt) {
      var R = F.rows[i], col = color((opt && opt.color) || 'hi');
      var y = R.cy - rowH / 2 + 4;
      var bg = s('rect', { x: -12, y: y, width: W + 12, height: rowH - 8, rx: 10, fill: col, 'fill-opacity': 0.12 }, svg);
      svg.insertBefore(bg, svg.firstChild);
      return gsap.fromTo(bg, { scaleX: 0, transformOrigin: '0 50%' }, { scaleX: 1, duration: dur(ctx, D.s), ease: E.out });
    };
    return F;
  };
  function d3min(rows) { var m = Infinity; rows.forEach(function (r) { m = Math.min(m, r.lo, r.outer ? r.outer[0] : Infinity, r.ghost ? r.ghost.lo : Infinity); }); return m; }
  function d3max(rows) { var m = -Infinity; rows.forEach(function (r) { m = Math.max(m, r.hi, r.outer ? r.outer[1] : -Infinity, r.ghost ? r.ghost.hi : -Infinity); }); return m; }
  function niceTicks(a, b, n) {
    var span = b - a, step = Math.pow(10, Math.floor(Math.log10(span / n))), err = n / span * step;
    if (err <= 0.15) step *= 10; else if (err <= 0.35) step *= 5; else if (err <= 0.75) step *= 2;
    var out = [], t = Math.ceil(a / step) * step;
    for (; t <= b + 1e-12; t += step) out.push(Math.round(t / step) * step);
    return out.map(function (v) { return +v.toFixed(10); });
  }
  Comp.niceTicks = niceTicks;

  /* -------------------------------------------------------------- odometer */
  Comp.odometer = function (ctx, el, text, o) {
    o = o || {};
    text = String(text);
    var tl = gsap.timeline({ delay: o.delay || 0, onComplete: function () { el.textContent = text; } });
    if (red(ctx)) { tl.call(function () { el.textContent = text; }); return tl; }
    el.textContent = '';
    el.classList.add('odo');
    var cols = [], digitsSeen = 0, nDigits = (text.match(/\d/g) || []).length;
    for (var i = 0; i < text.length; i++) {
      var ch = text.charAt(i);
      if (!/\d/.test(ch)) { h('span', '', el, Deck.util.esc(ch)); continue; }
      var col = h('span', 'odo-col', el), strip = h('span', 'odo-strip', col);
      var target = +ch, cycles = 1 + Math.floor((nDigits - digitsSeen) / 3), total = cycles * 10 + target, html = '';
      for (var k = 0; k <= total; k++) html += '<span>' + (k % 10) + '</span>';
      strip.innerHTML = html;
      cols.push({ strip: strip, total: total, idx: digitsSeen });
      digitsSeen++;
    }
    var d0 = o.duration || 2.2;
    cols.forEach(function (c) {
      tl.fromTo(c.strip, { yPercent: 0 }, { yPercent: -100 * c.total / (c.total + 1), duration: d0 * (0.65 + 0.35 * (c.idx / Math.max(1, nDigits - 1))), ease: 'power2.out' }, 0);
    });
    return tl;
  };

  /* -------------------------------------------------------------- time axis */
  function parseDate(d) {
    if (d instanceof Date) return d.getTime();
    if (typeof d === 'number') return d;
    var m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(d);
    return Date.UTC(+m[1], +m[2] - 1, m[3] ? +m[3] : 1);
  }
  Comp.parseDate = parseDate;
  Comp.timeline = function (ctx, parent, o) {
    o = o || {};
    var W = o.w || 1700, H = o.h || 420, axisY = o.axisY != null ? o.axisY : H - 60, padL = o.padL || 20, padR = o.padR || 20;
    var svg = Comp.svg(ctx, parent, { w: W, h: H, className: 'timeline' });
    var t0 = parseDate(o.from || '2023-10-01'), t1 = parseDate(o.to || '2026-09-30');
    function x(d) { return padL + (parseDate(d) - t0) / (t1 - t0) * (W - padL - padR); }
    var TL = { svg: svg, x: x, axisY: axisY };
    var ax = s('g', { 'class': 'axis' }, svg);
    var line = s('line', { x1: x(t0), x2: x(t1), y1: axisY, y2: axisY, stroke: COL.ink2, 'stroke-width': 2 }, ax);
    var ticks = [], dt = new Date(t0);
    var y = dt.getUTCFullYear(), mo = dt.getUTCMonth();
    while (true) {
      var t = Date.UTC(y, mo, 1);
      if (t > t1) break;
      if (t >= t0) {
        var major = mo === 0;
        ticks.push(s('line', { x1: x(t), x2: x(t), y1: axisY, y2: axisY + (major ? 16 : 7), stroke: major ? COL.ink2 : COL.ink3, 'stroke-width': major ? 2 : 1 }, ax));
        if (major && o.years !== false) { var lt = s('text', { x: x(t) + 6, y: axisY + 36, fill: COL.ink2, 'font-size': 20, 'class': 'tnum' }, ax); lt.textContent = String(y); ticks.push(lt); }
      }
      mo++; if (mo > 11) { mo = 0; y++; }
    }
    TL.axis = ax;
    TL.drawAxis = function (opt) {
      opt = opt || {};
      var tl = gsap.timeline({ delay: opt.delay || 0 }), L = x(t1) - x(t0), dd = dur(ctx, opt.duration != null ? opt.duration : 1.6);
      tl.fromTo(line, { attr: { x2: x(t0) } }, { attr: { x2: x(t1) }, duration: dd, ease: 'power2.inOut' }, 0);
      tl.fromTo(ticks, { autoAlpha: 0 }, { autoAlpha: 1, duration: dur(ctx, 0.2), stagger: dd / Math.max(1, ticks.length) }, 0);
      void L;
      return tl;
    };
    TL.pin = function (date, opt) {
      opt = opt || {};
      return Comp.pin(ctx, svg, { x: x(date), y0: opt.y0 != null ? opt.y0 : 40, y1: axisY, label: opt.label, color: opt.color, labelSize: opt.labelSize });
    };
    TL.band = function (from, to, opt) {
      opt = opt || {};
      var col = color(opt.color || 'ink2'), y0 = opt.y0 != null ? opt.y0 : 40, y1 = axisY;
      var g = s('g', { 'class': 'band' }, svg);
      svg.insertBefore(g, svg.firstChild);
      var pid = uid('hatch');
      var defs = s('defs', {}, g), pat = s('pattern', { id: pid, width: 12, height: 12, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, defs);
      s('line', { x1: 0, y1: 0, x2: 0, y2: 12, stroke: col, 'stroke-width': 3, 'stroke-opacity': 0.35 }, pat);
      var rect = s('rect', { x: x(from), y: y0, width: Math.max(1, x(to) - x(from)), height: y1 - y0, fill: opt.hatch === false ? col : 'url(#' + pid + ')', 'fill-opacity': opt.hatch === false ? 0.12 : 1 }, g);
      var B = { g: g, rect: rect };
      if (opt.label) { B.label = s('text', { x: (x(from) + x(to)) / 2, y: y0 - 12, 'text-anchor': 'middle', fill: col, 'font-size': 20, 'font-weight': 600 }, g); B.label.textContent = opt.label; }
      gsap.set(g, { autoAlpha: 0 });
      B.show = function (o2) {
        o2 = o2 || {};
        var tl = gsap.timeline({ delay: o2.delay || 0 });
        tl.set(g, { autoAlpha: 1 });
        tl.fromTo(rect, { scaleX: 0, transformOrigin: '0% 50%' }, { scaleX: 1, duration: dur(ctx, D.m), ease: E.out }, 0);
        if (B.label) tl.fromTo(B.label, { autoAlpha: 0 }, { autoAlpha: 1, duration: dur(ctx, D.s) }, 0.3);
        return tl;
      };
      return B;
    };
    /* values: one number per month starting at `from`; drawn as a filled stream above the axis */
    TL.stream = function (values, opt) {
      opt = opt || {};
      var col = color(opt.color || 'allow'), hgt = opt.height || 200, base = opt.base != null ? opt.base : axisY - 4;
      var start = parseDate(opt.start || o.from || '2023-10-01'), max = opt.max || Math.max.apply(null, values) || 1;
      var pts = values.map(function (v, i) {
        var d = new Date(start); var t = Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + i, 15);
        return [x(t), base - v / max * hgt];
      });
      var dpath = 'M' + pts[0][0] + ',' + base + ' L' + pts.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' L') + ' L' + pts[pts.length - 1][0] + ',' + base + 'Z';
      var g = s('g', { 'class': 'stream' }, svg);
      var cid = uid('clip');
      var cr = s('rect', { x: 0, y: 0, width: W, height: H }, s('clipPath', { id: cid }, s('defs', {}, g)));
      var area = s('path', { d: dpath, fill: col, 'fill-opacity': opt.opacity || 0.28, stroke: col, 'stroke-width': 2, 'clip-path': 'url(#' + cid + ')' }, g);
      return { g: g, path: area, reveal: function (o2) {
        o2 = o2 || {};
        return gsap.fromTo(cr, { attr: { width: 0 } }, { attr: { width: W }, duration: dur(ctx, o2.duration || 2), ease: o2.ease || 'none', delay: o2.delay || 0 });
      } };
    };
    return TL;
  };

  /* -------------------------------------------------------------- formula with named parts */
  Comp.formula = function (ctx, parent, src, o) {
    o = o || {};
    var display = o.display !== false;
    var el = h(display ? 'div' : 'span', 'formula' + (display ? ' display' : '') + (o.className ? ' ' + o.className : ''), parent);
    el.innerHTML = Deck.tex(src, display);
    var marks = {};
    var F = { el: el };
    F.parts = function (name) { return Array.prototype.slice.call(el.querySelectorAll('.fx-' + name)); };
    F.rect = function (name) {
      var ps = F.parts(name); if (!ps.length) return null;
      var r = null;
      ps.forEach(function (p) {
        var q = Deck.util.stageRect(p);
        r = r ? { x: Math.min(r.x, q.x), y: Math.min(r.y, q.y), r: Math.max(r.r, q.x + q.w), b: Math.max(r.b, q.y + q.h) } : { x: q.x, y: q.y, r: q.x + q.w, b: q.y + q.h };
      });
      return { x: r.x, y: r.y, w: r.r - r.x, h: r.b - r.y, cx: (r.x + r.r) / 2, cy: (r.y + r.b) / 2 };
    };
    F.mark = function (name, opt) {
      opt = opt || {};
      var r = F.rect(name); if (!r) return gsap.to({}, { duration: 0 });
      var base = Deck.util.stageRect(el), pad = opt.pad != null ? opt.pad : 6;
      var m = marks[name] || (marks[name] = h('div', 'fx-mark', el));
      m.style.left = (r.x - base.x - pad) + 'px'; m.style.top = (r.y - base.y - pad / 2) + 'px';
      m.style.width = (r.w + pad * 2) + 'px'; m.style.height = (r.h + pad) + 'px';
      if (opt.color) m.style.background = opt.color;
      return gsap.fromTo(m, { scaleX: 0, autoAlpha: 1 }, { scaleX: 1, duration: dur(ctx, opt.duration != null ? opt.duration : D.s), ease: E.out, delay: opt.delay || 0 });
    };
    F.unmark = function (name, opt) {
      var ms = name ? [marks[name]] : Object.keys(marks).map(function (k) { return marks[k]; });
      ms = ms.filter(Boolean);
      if (!ms.length) return gsap.to({}, { duration: 0 });
      return gsap.to(ms, { autoAlpha: 0, duration: dur(ctx, (opt && opt.duration) || 0.3) });
    };
    function leaves() {
      return Array.prototype.slice.call(el.querySelectorAll('.katex-html *')).filter(function (n) {
        if (n.closest('svg') && n.tagName.toLowerCase() !== 'svg') return false;
        return !n.firstElementChild || n.tagName.toLowerCase() === 'svg';
      });
    }
    F.dim = function (keep, opt) {
      keep = [].concat(keep || []);
      var keepEls = []; keep.forEach(function (k) { keepEls = keepEls.concat(F.parts(k)); });
      var targets = leaves().filter(function (n) { return !keepEls.some(function (k) { return k.contains(n); }); });
      return gsap.to(targets, { opacity: opt && opt.opacity != null ? opt.opacity : 0.28, duration: dur(ctx, D.s) });
    };
    F.undim = function () { return gsap.to(leaves(), { opacity: 1, duration: dur(ctx, D.s) }); };
    F.show = function (name, opt) { return gsap.to(F.parts(name), { autoAlpha: 1, y: 0, duration: dur(ctx, (opt && opt.duration) || D.s), ease: E.out }); };
    F.hide = function (name, opt) { return gsap.to(F.parts(name), { autoAlpha: 0, duration: opt && opt.duration === 0 ? 0 : dur(ctx, (opt && opt.duration) || 0.25) }); };
    F.color = function (name, c, opt) { return gsap.to(F.parts(name), { color: color(c), duration: dur(ctx, (opt && opt.duration) || D.s) }); };
    if (o.hideParts) o.hideParts.forEach(function (p) { gsap.set(F.parts(p), { autoAlpha: 0 }); });
    return F;
  };

  /* -------------------------------------------------------------- derivation panel */
  Comp.derive = function (ctx, parent, o) {
    o = o || {};
    var lines = o.lines || [];
    var el = h('div', 'derive eq-panel' + (o.className ? ' ' + o.className : ''), parent);
    var head = h('div', 'eq-head', el, '<span>' + Deck.util.esc(o.head || '유도') + '</span><span class="derive-count tnum"></span>');
    var count = head.querySelector('.derive-count');
    var Dv = { el: el, total: lines.length, k: 0, lines: [] };
    lines.forEach(function (ln, i) {
      var row = h('div', 'derive-line', el);
      h('div', 'derive-no', row, String(i + 1));
      var body = h('div', 'derive-body', row);
      var F = null;
      if (ln.tex) { var tx = h('div', 'derive-tex', body); F = Comp.formula(ctx, tx, ln.tex, { display: ln.display !== false }); }
      if (ln.note) h('span', 'derive-note', body, ln.note);
      if (ln.html) h('div', 'derive-html', body, ln.html);
      gsap.set(row, { autoAlpha: 0 });
      Dv.lines.push({ row: row, F: F, data: ln });
    });
    function setCount(k) { if (o.counter !== false) count.textContent = '단계 ' + k + ' / ' + lines.length; }
    setCount(0);
    Dv.show = function (k, opt) {
      opt = opt || {};
      k = Math.max(0, Math.min(lines.length, k));
      var tl = gsap.timeline({ delay: opt.delay || 0 });
      Dv.lines.forEach(function (L, i) {
        if (i < k - 1 || (i === k - 1 && opt.animate === false)) tl.set(L.row, { autoAlpha: 1, y: 0 }, 0);
        else if (i >= k) tl.set(L.row, { autoAlpha: 0 }, 0);
      });
      var prev = Dv.lines[Dv.k - 1];
      if (prev && prev.F && k !== Dv.k) tl.add(prev.F.unmark(), 0);
      var L = Dv.lines[k - 1];
      if (L && opt.animate !== false) {
        tl.fromTo(L.row, { autoAlpha: 0, y: 22 }, { autoAlpha: 1, y: 0, duration: dur(ctx, D.m), ease: E.out }, 0.05);
        if (L.F && L.data.mark) tl.add(function () { ctx.add(function () { L.F.mark(L.data.mark); }); }, 0.45);
      } else if (L && L.F && L.data.mark) tl.add(function () { ctx.add(function () { L.F.mark(L.data.mark, { duration: 0 }); }); }, 0);
      tl.call(setCount, [k], 0);
      Dv.k = k;
      return tl;
    };
    return Dv;
  };

  /* -------------------------------------------------------------- symbol card (기호 카드) */
  Comp.symbolCard = function (ctx, parent, o) {
    o = o || {};
    var el = h('div', 'sym-card' + (o.className ? ' ' + o.className : ''), parent);
    if (o.x != null) { el.style.position = 'absolute'; el.style.left = o.x + 'px'; el.style.top = o.y + 'px'; }
    h('div', 'sym', el, o.tex ? Deck.tex(o.tex, false) : Deck.util.esc(o.sym || ''));
    if (o.art) h('div', 'sym-art', el, o.art);
    if (o.desc) h('div', 'sym-desc', el, o.desc);
    if (o.hidden !== false) gsap.set(el, { autoAlpha: 0 });
    return {
      el: el,
      pop: function (opt) {
        opt = opt || {};
        if (red(ctx)) return gsap.to(el, { autoAlpha: 1, duration: 0.2 });
        return gsap.fromTo(el, { autoAlpha: 0, scale: 0.7, y: 12, transformOrigin: '50% 100%' }, { autoAlpha: 1, scale: 1, y: 0, duration: D.s, ease: E.stamp, delay: opt.delay || 0 });
      }
    };
  };

  /* -------------------------------------------------------------- leader line (지시선) */
  function anchor(r, side, other) {
    if (side === 'auto' || !side) {
      var dx = other.cx - r.cx, dy = other.cy - r.cy;
      side = Math.abs(dx) * 0.6 > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'bottom' : 'top');
    }
    if (side === 'left') return { x: r.x - 6, y: r.cy, side: side };
    if (side === 'right') return { x: r.x + r.w + 6, y: r.cy, side: side };
    if (side === 'top') return { x: r.cx, y: r.y - 6, side: side };
    return { x: r.cx, y: r.y + r.h + 6, side: 'bottom' };
  }
  function asRect(t) {
    if (Array.isArray(t)) return { x: t[0], y: t[1], w: 0, h: 0, cx: t[0], cy: t[1] };
    if (t && t.nodeType) return Deck.util.stageRect(t);
    return t;
  }
  Comp.leader = function (ctx, from, to, o) {
    o = o || {};
    var svg = ctx.overlay();
    var a = asRect(from), b = asRect(to);
    var p = anchor(a, o.fromSide, b), q = anchor(b, o.toSide, a);
    var k = o.bend != null ? o.bend : 0.35, dx = q.x - p.x, dy = q.y - p.y;
    function ctrl(pt, side, sgn) {
      var L = Math.hypot(dx, dy) * k;
      if (side === 'left') return [pt.x - L, pt.y]; if (side === 'right') return [pt.x + L, pt.y];
      if (side === 'top') return [pt.x, pt.y - L]; return [pt.x, pt.y + L * (sgn || 1)];
    }
    var c1 = ctrl(p, p.side), c2 = ctrl(q, q.side);
    var path = s('path', { d: 'M' + p.x + ',' + p.y + ' C' + c1[0] + ',' + c1[1] + ' ' + c2[0] + ',' + c2[1] + ' ' + q.x + ',' + q.y,
      fill: 'none', stroke: color(o.color || 'ink2'), 'stroke-width': o.width || 1.5, 'stroke-dasharray': o.dashed ? '4 5' : null, opacity: 0.9 }, svg);
    var dotA = s('circle', { cx: p.x, cy: p.y, r: 3.5, fill: color(o.color || 'ink2') }, svg);
    var dotB = s('circle', { cx: q.x, cy: q.y, r: 3.5, fill: color(o.color || 'ink2') }, svg);
    var L = pathLen(path);
    gsap.set(path, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }); gsap.set([dotA, dotB], { autoAlpha: 0 });
    return {
      path: path,
      draw: function (opt) {
        opt = opt || {};
        var tl = gsap.timeline({ delay: opt.delay || 0 });
        tl.set(dotA, { autoAlpha: 1 });
        tl.to(path, { strokeDashoffset: 0, duration: dur(ctx, opt.duration || D.m), ease: 'power2.inOut', onComplete: function () { if (o.dashed) { path.style.strokeDasharray = '4 5'; path.style.strokeDashoffset = '0'; } } });
        tl.set(dotB, { autoAlpha: 1 });
        return tl;
      },
      undraw: function () { return gsap.to([path, dotA, dotB], { autoAlpha: 0, duration: dur(ctx, 0.3) }); },
      remove: function () { [path, dotA, dotB].forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); }); }
    };
  };

  /* -------------------------------------------------------------- typography moves */
  Comp.swap = function (ctx, el, html, o) {
    o = o || {};
    var tl = gsap.timeline({ delay: o.delay || 0 });
    var isSvg = el.namespaceURI === NS;
    if (red(ctx)) { tl.call(function () { if (isSvg) el.textContent = html; else el.innerHTML = html; }); return tl; }
    tl.to(el, { autoAlpha: 0, y: -6, filter: isSvg ? 'none' : 'blur(8px)', duration: 0.28, ease: E['in'] });
    tl.call(function () { if (isSvg) el.textContent = html; else el.innerHTML = html; });
    tl.fromTo(el, { autoAlpha: 0, y: 6, filter: isSvg ? 'none' : 'blur(8px)' }, { autoAlpha: 1, y: 0, filter: isSvg ? 'none' : 'blur(0px)', duration: 0.32, ease: E.out });
    return tl;
  };
  Comp.strike = function (ctx, el, html, o) {
    o = o || {};
    var tl = gsap.timeline({ delay: o.delay || 0 });
    var cs = getComputedStyle(el);
    if (cs.position === 'static') el.style.position = 'relative';
    var line = h('span', '', el);
    line.style.cssText = 'position:absolute;left:-4px;right:-4px;top:52%;height:4px;border-radius:2px;background:' + color(o.color || 'hi') + ';transform-origin:left center;';
    tl.fromTo(line, { scaleX: 0 }, { scaleX: 1, duration: dur(ctx, 0.45), ease: 'power2.inOut' });
    if (html != null) {
      tl.to(el, { autoAlpha: 0, duration: dur(ctx, 0.25) }, '+=0.35');
      tl.call(function () { el.innerHTML = html; });
      tl.set(el, { autoAlpha: 1 });
      tl.call(function () { ctx.add(function () { ctx.rise(el); }); });
    }
    return tl;
  };
  Comp.hilite = function (ctx, el, o) {
    o = o || {};
    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
    el.style.isolation = 'isolate';
    var b = h('span', '', el);
    b.style.cssText = 'position:absolute;left:-6px;right:-6px;top:6%;bottom:2%;z-index:-1;border-radius:6px;transform-origin:left center;background:' + (o.color || 'var(--c-hi-soft)') + ';';
    return gsap.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: dur(ctx, D.s), ease: E.out, delay: o.delay || 0 });
  };
  Comp.scramble = function (ctx, el, text, o) {
    o = o || {};
    if (red(ctx) || !global.ScrambleTextPlugin) return gsap.set(el, { textContent: text });
    return gsap.to(el, { duration: o.duration || 0.8, scrambleText: { text: text, chars: o.chars || '0123456789', speed: 0.6 }, delay: o.delay || 0 });
  };

  /* -------------------------------------------------------------- 3D: point cloud, floor, axes */
  var dotTexture = null;
  function dotTex(THREE) {
    /* a fresh texture per cloud (disposed with the scene); the canvas is shared */
    if (!dotTexture) {
      var c = document.createElement('canvas'); c.width = c.height = 64;
      var g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.55, 'rgba(255,255,255,0.95)'); gr.addColorStop(0.8, 'rgba(255,255,255,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
      dotTexture = c;
    }
    var t = new THREE.CanvasTexture(dotTexture);
    return t;
  }
  Comp.cloud = function (ctx, T, o) {
    o = o || {};
    var THREE = T.THREE;
    if (!THREE || T.failed) return { failed: true, morph: function () { return gsap.to({}, { duration: 0 }); }, recolor: function () { return gsap.to({}, { duration: 0 }); }, setPositions: function () {}, setColors: function () {} };
    var n = o.n || (o.positions ? o.positions.length / 3 : 0);
    var pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    if (o.positions) pos.set(o.positions);
    function srgbToLinArr(src, dst) { for (var i = 0; i < src.length; i++) dst[i] = toLin(src[i]); }
    if (o.colors) srgbToLinArr(o.colors, col);
    else { var c0 = rgb(color(o.color || 'allow')).map(toLin); for (var i = 0; i < n; i++) { col[i * 3] = c0[0]; col[i * 3 + 1] = c0[1]; col[i * 3 + 2] = c0[2]; } }
    var geo = new THREE.BufferGeometry();
    var pAttr = new THREE.BufferAttribute(pos, 3), cAttr = new THREE.BufferAttribute(col, 3);
    pAttr.setUsage(THREE.DynamicDrawUsage); cAttr.setUsage(THREE.DynamicDrawUsage);
    geo.setAttribute('position', pAttr); geo.setAttribute('color', cAttr);
    geo.computeBoundingSphere();
    var mat = new THREE.PointsMaterial({ size: o.size || 3, sizeAttenuation: !!o.sizeAttenuation, vertexColors: true, map: dotTex(THREE), transparent: true,
      opacity: o.opacity != null ? o.opacity : 0.55, depthWrite: false, blending: o.additive === false ? THREE.NormalBlending : THREE.AdditiveBlending, alphaTest: 0.01 });
    var pts = new THREE.Points(geo, mat);
    pts.frustumCulled = false;
    T.scene.add(pts);
    var C = { points: pts, geometry: geo, material: mat, n: n, positions: pos, colors: col };
    C.setPositions = function (a) { pos.set(a); pAttr.needsUpdate = true; geo.computeBoundingSphere(); };
    C.setColors = function (a) { srgbToLinArr(a, col); cAttr.needsUpdate = true; };
    function blend(src, dst, out, attr, opt) {
      opt = opt || {};
      var delays = opt.delays, spread = opt.spread != null ? opt.spread : (delays ? 0.5 : 0);
      var ease = gsap.parseEase(opt.ease || E.io), st = { p: 0 }, from = new Float32Array(src);
      return gsap.to(st, { p: 1, duration: dur(ctx, opt.duration != null ? opt.duration : 1.4), ease: 'none', delay: opt.delay || 0,
        onUpdate: function () {
          var p = st.p;
          for (var i = 0; i < n; i++) {
            var lp = delays ? (p * (1 + spread) - delays[i] * spread) : p;
            lp = lp <= 0 ? 0 : lp >= 1 ? 1 : ease(lp);
            var j = i * 3;
            out[j] = from[j] + (dst[j] - from[j]) * lp; out[j + 1] = from[j + 1] + (dst[j + 1] - from[j + 1]) * lp; out[j + 2] = from[j + 2] + (dst[j + 2] - from[j + 2]) * lp;
          }
          attr.needsUpdate = true;
        },
        onComplete: function () { out.set(dst); attr.needsUpdate = true; if (attr === pAttr) geo.computeBoundingSphere(); } });
    }
    C.morph = function (target, opt) { return blend(pos, target, pos, pAttr, opt); };
    C.recolor = function (target, opt) { var lin = new Float32Array(target.length); srgbToLinArr(target, lin); return blend(col, lin, col, cAttr, opt); };
    return C;
  };
  Comp.floor = function (ctx, T, o) {
    o = o || {};
    var THREE = T.THREE; if (!THREE || T.failed) return null;
    var size = o.size || 10, y = o.y || 0;
    var grp = new THREE.Group();
    var grid = new THREE.GridHelper(size, o.divisions || 10, new THREE.Color(o.color || COL.ink3), new THREE.Color(o.color || COL.ink3));
    grid.material.transparent = true; grid.material.opacity = o.opacity != null ? o.opacity : 0.25; grid.material.depthWrite = false;
    grp.add(grid);
    var plate = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshBasicMaterial({ color: new THREE.Color(COL.bg3), transparent: true, opacity: 0.35, depthWrite: false, side: THREE.DoubleSide }));
    plate.rotation.x = -Math.PI / 2; plate.position.y = -0.001;
    grp.add(plate);
    grp.position.set(o.x || 0, y, o.z || 0);
    T.scene.add(grp);
    return grp;
  };
  Comp.axes3d = function (ctx, T, o) {
    o = o || {};
    var THREE = T.THREE; if (!THREE || T.failed) return { group: null, labels: [] };
    var org = o.origin || [0, 0, 0], len = o.length || [5, 5, 5];
    var cols = o.colors || [COL.allow, COL.ink, COL.xfer];
    var grp = new THREE.Group(), labels = [];
    var dirs = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    dirs.forEach(function (dv, i) {
      var end = [org[0] + dv[0] * len[i], org[1] + dv[1] * len[i], org[2] + dv[2] * len[i]];
      var g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(org[0], org[1], org[2]), new THREE.Vector3(end[0], end[1], end[2])]);
      var line = new THREE.Line(g, new THREE.LineBasicMaterial({ color: new THREE.Color(cols[i]), transparent: true, opacity: 0.9 }));
      grp.add(line);
      var cone = new THREE.Mesh(new THREE.ConeGeometry(o.headRadius || 0.07, o.headLength || 0.24, 12), new THREE.MeshBasicMaterial({ color: new THREE.Color(cols[i]) }));
      cone.position.set(end[0], end[1], end[2]);
      if (i === 0) cone.rotation.z = -Math.PI / 2; else if (i === 2) cone.rotation.x = Math.PI / 2;
      grp.add(cone);
      if (o.labels && o.labels[i]) {
        var off = o.labelOffset || 0.35;
        labels.push(T.label(o.labels[i], [end[0] + dv[0] * off, end[1] + dv[1] * off, end[2] + dv[2] * off], { className: 'axis3d-label' }));
        labels[labels.length - 1].el.style.color = cols[i];
      }
    });
    T.scene.add(grp);
    return { group: grp, labels: labels };
  };

  /* -------------------------------------------------------------- data helpers */
  var cache = {};
  Comp.data = {
    contracts: function () {
      if (cache.contracts) return cache.contracts;
      var c = (global.DECK_DATA || {}).contracts;
      if (!c) return null;
      var out = { n: c.meta ? c.meta.n : (c.pct.endorserank || []).length, pct: {}, raw: {}, log10: {}, flags: null, zeros: c.zeros, flag_counts: c.flag_counts };
      Object.keys(c.pct || {}).forEach(function (k) { out.pct[k] = Float32Array.from(c.pct[k]); });
      Object.keys(c.raw || {}).forEach(function (k) { out.raw[k] = Float32Array.from(c.raw[k]); });
      Object.keys(c.log10 || {}).forEach(function (k) { out.log10[k] = Float32Array.from(c.log10[k], function (v) { return v == null ? NaN : v; }); });
      out.flags = Uint8Array.from(c.flags || []);
      cache.contracts = out;
      return out;
    },
    lambdaKeys: ['cpr_l0', 'cpr_l25', 'cpr_l50', 'cpr_l75', 'cpr_l100'],
    lambdas: [0, 0.25, 0.5, 0.75, 1]
  };

  global.Comp = Comp;
})(window);
