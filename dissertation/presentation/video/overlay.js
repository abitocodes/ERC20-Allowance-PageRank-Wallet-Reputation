/* video/overlay.js — motion graphics drawn over the deck for the video (injected after the deck boots).
   Everything animates with the page's GSAP, so it runs on the virtual clock of vtime.js.

   window.__vx
     camTo(boxes, zoom, dur)   camera onto the union of boxes (stage px [x,y,w,h]); zoom 'none'|'soft'|'close'
     camHome(dur)              camera back to the whole slide
     marks(boxes, kind)        'ring' | 'underline' | 'spot' around each box (or their union when far apart)
     clearMarks(dur)
     card(title, body, dur)    term card under a shrunken slide;  cardOut(dur)
     intro(o) / introOut(dur)  opening title card;  outro(o) / fadeBlack(dur)  closing card
     reset()                   everything off at once (between chunks)
     dynamic()                 true while anything on screen can still change (capture this frame)
     state()                   { cam, marks, card } for the renderer */
(function () {
  'use strict';
  var STAGE_W = 1920, STAGE_H = 1080;
  var stage = document.getElementById('deck-stage');
  var slides = document.getElementById('deck-slides');
  var lang = document.documentElement.lang === 'en' ? 'en' : 'ko';

  var css = document.createElement('style');
  css.textContent = [
    '#vx-cam{position:absolute;left:0;top:0;width:1920px;height:1080px;z-index:6;pointer-events:none;transform-origin:0 0}',
    '#vx-screen{position:absolute;left:0;top:0;width:1920px;height:1080px;z-index:60;pointer-events:none;font-family:var(--font-sans)}',
    '.vx-ring{position:absolute;overflow:visible}',
    '.vx-ring rect{fill:none;stroke:#FFFFFF;stroke-width:4.5;filter:drop-shadow(0 0 12px rgba(255,255,255,.6))}',
    '.vx-under{position:absolute;height:6px;border-radius:3px;background:#FFFFFF;box-shadow:0 0 14px rgba(255,255,255,.6);transform-origin:0 50%}',
    '.vx-spot{position:absolute;border-radius:18px;box-shadow:0 0 0 4000px rgba(4,6,10,.58)}',
    '.vx-card{position:absolute;left:50%;bottom:26px;max-width:1560px;min-width:760px;padding:22px 40px 24px 44px;border-radius:22px;',
    '  background:rgba(16,21,31,.97);border:1px solid #2E3850;box-shadow:0 18px 50px rgba(0,0,0,.55);color:#E9EDF5}',
    '.vx-card:before{content:"";position:absolute;left:0;top:18px;bottom:18px;width:6px;border-radius:0 4px 4px 0;background:#FF6B8A}',
    '.vx-card .k{font-size:20px;line-height:26px;letter-spacing:.08em;color:#8790A3;font-weight:600;text-transform:uppercase}',
    '.vx-card .t{margin-top:2px;font-size:36px;line-height:46px;font-weight:700;letter-spacing:-.01em}',
    '.vx-card .b{margin-top:4px;font-size:28px;line-height:40px;color:#C3CBDA}',
    '.vx-full{position:absolute;inset:0;background:#0A0D14;overflow:hidden}',
    '.vx-full svg.net{position:absolute;left:0;top:0}',
    '.vx-full .eyebrow{position:absolute;left:120px;top:250px;font-size:30px;line-height:40px;color:#A3ADBF;font-weight:600;letter-spacing:.02em}',
    '.vx-full .title{position:absolute;left:120px;top:310px;width:1100px;font-size:72px;line-height:92px;font-weight:800;letter-spacing:-.025em;color:#E9EDF5}',
    '.vx-full .title .w{display:inline-block;margin-right:.24em}',
    '.vx-full .title .m{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:6px}',
    '.vx-full .rule{position:absolute;left:120px;height:4px;width:180px;border-radius:2px;background:linear-gradient(90deg,#3CC4FF,#A78BFA,#F5B43C);transform-origin:0 50%}',
    '.vx-full .who{position:absolute;left:120px;font-size:32px;line-height:44px;color:#E9EDF5;font-weight:600}',
    '.vx-full .who small{display:block;font-size:26px;line-height:38px;color:#A3ADBF;font-weight:500}',
    '.vx-full .legend{position:absolute;left:120px;bottom:96px;display:flex;gap:36px;font-size:24px;color:#A3ADBF}',
    '.vx-full .legend span{display:inline-flex;align-items:center;gap:12px}',
    '.vx-full .legend i{display:inline-block;width:42px;height:4px;border-radius:2px}',
    '.vx-full .credits{position:absolute;left:120px;bottom:90px;width:1300px;font-size:22px;line-height:34px;color:#8790A3}',
    '.vx-black{position:absolute;inset:0;background:#000}'
  ].join('\n');
  document.head.appendChild(css);

  var cam = document.createElement('div'); cam.id = 'vx-cam'; stage.appendChild(cam);
  var scr = document.createElement('div'); scr.id = 'vx-screen'; stage.appendChild(scr);

  /* ------------------------------------------------------------ camera */
  var C = { s: 1, tx: 0, ty: 0 };
  var camTween = null;
  function applyCam() {
    var t = C.s === 1 && C.tx === 0 && C.ty === 0 ? '' : 'translate(' + C.tx.toFixed(2) + 'px,' + C.ty.toFixed(2) + 'px) scale(' + C.s.toFixed(4) + ')';
    slides.style.transformOrigin = '0 0';
    slides.style.transform = t;
    cam.style.transform = t;
  }
  function union(boxes) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    boxes.forEach(function (b) { x0 = Math.min(x0, b[0]); y0 = Math.min(y0, b[1]); x1 = Math.max(x1, b[0] + b[2]); y1 = Math.max(y1, b[1] + b[3]); });
    return [x0, y0, x1 - x0, y1 - y0];
  }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function targetFor(boxes, zoom) {
    if (!boxes || !boxes.length || zoom === 'none' || !zoom) return { s: 1, tx: 0, ty: 0 };
    var u = union(boxes), pad = 48;
    var w = u[2] + 2 * pad, h = u[3] + 2 * pad;
    var s = zoom === 'close' ? 1.6 : 1.25;
    s = Math.min(s, STAGE_W * 0.9 / w, STAGE_H * 0.84 / h);
    if (s < 1.06) return { s: 1, tx: 0, ty: 0 };
    var cx = u[0] + u[2] / 2, cy = u[1] + u[3] / 2;
    return { s: s, tx: clamp(STAGE_W / 2 - s * cx, STAGE_W - STAGE_W * s, 0), ty: clamp(STAGE_H / 2 - s * cy, STAGE_H - STAGE_H * s, 0) };
  }
  function camTarget(t, dur) {
    if (camTween) camTween.kill();
    if (Math.abs(t.s - C.s) < 1e-3 && Math.abs(t.tx - C.tx) < 0.5 && Math.abs(t.ty - C.ty) < 0.5) { camTween = null; return 0; }
    camTween = gsap.to(C, { s: t.s, tx: t.tx, ty: t.ty, duration: dur, ease: 'power2.inOut', onUpdate: applyCam });
    return dur;
  }

  /* ------------------------------------------------------------ marks */
  var marks = [];
  function groupBoxes(boxes) {
    if (boxes.length <= 1) return boxes.slice();
    var u = union(boxes);
    /* far-apart pieces get their own mark; close ones one mark around them all */
    var spread = u[2] * u[3], sum = boxes.reduce(function (a, b) { return a + b[2] * b[3]; }, 0);
    return (boxes.length > 3 || spread < 3.2 * sum) ? [u] : boxes.slice();
  }
  function ring(b) {
    var p = 16, x = b[0] - p, y = b[1] - p, w = b[2] + 2 * p, h = b[3] + 2 * p;
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'vx-ring');
    svg.setAttribute('width', w + 20); svg.setAttribute('height', h + 20);
    svg.style.left = (x - 10) + 'px'; svg.style.top = (y - 10) + 'px';
    var r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    r.setAttribute('x', 10); r.setAttribute('y', 10); r.setAttribute('width', w); r.setAttribute('height', h);
    r.setAttribute('rx', Math.min(18, h / 2)); r.setAttribute('pathLength', '1');
    r.style.strokeDasharray = '1'; r.style.strokeDashoffset = '1';
    svg.appendChild(r);
    cam.appendChild(svg);
    var tl = gsap.timeline();
    tl.to(r.style, { strokeDashoffset: 0, duration: 0.7, ease: 'power2.inOut' }, 0);
    tl.fromTo(svg, { opacity: 0 }, { opacity: 1, duration: 0.25 }, 0);
    return { el: svg, tl: tl };
  }
  function underline(b) {
    var d = document.createElement('div'); d.className = 'vx-under';
    d.style.left = b[0] + 'px'; d.style.top = (b[1] + b[3] + 6) + 'px'; d.style.width = b[2] + 'px';
    cam.appendChild(d);
    var tl = gsap.timeline();
    tl.fromTo(d, { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.6, ease: 'power3.out' });
    return { el: d, tl: tl };
  }
  function spot(b) {
    var p = 18, d = document.createElement('div'); d.className = 'vx-spot';
    d.style.left = (b[0] - p) + 'px'; d.style.top = (b[1] - p) + 'px';
    d.style.width = (b[2] + 2 * p) + 'px'; d.style.height = (b[3] + 2 * p) + 'px';
    cam.appendChild(d);
    var tl = gsap.timeline();
    tl.fromTo(d, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power1.out' });
    return { el: d, tl: tl };
  }
  function addMarks(boxes, kind) {
    if (!boxes || !boxes.length || !kind || kind === 'none') return;
    var groups = kind === 'spot' ? [union(boxes)] : groupBoxes(boxes);
    groups.forEach(function (b, i) {
      var m = kind === 'underline' ? underline(b) : kind === 'spot' ? spot(b) : ring(b);
      m.tl.delay(0.12 * i);
      marks.push(m);
    });
  }
  function clearMarks(dur) {
    var old = marks; marks = [];
    old.forEach(function (m) {
      m.tl.kill();
      gsap.to(m.el, { opacity: 0, duration: dur == null ? 0.3 : dur, onComplete: function () { if (m.el.parentNode) m.el.parentNode.removeChild(m.el); } });
    });
  }

  /* ------------------------------------------------------------ term card */
  var card = null;
  var CARD_CAM = { s: 0.82, tx: (STAGE_W - STAGE_W * 0.82) / 2, ty: 16 };
  function showCard(title, body, dur) {
    hideCard(0.2);
    var d = document.createElement('div'); d.className = 'vx-card';
    d.innerHTML = '<div class="k">' + (lang === 'ko' ? '용어 한 줄' : 'In one line') + '</div><div class="t"></div><div class="b"></div>';
    d.querySelector('.t').textContent = title; d.querySelector('.b').textContent = body;
    scr.appendChild(d);
    gsap.set(d, { xPercent: -50 });
    camTarget(CARD_CAM, dur || 0.7);
    gsap.fromTo(d, { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, delay: 0.25, ease: 'power3.out' });
    card = d;
  }
  function hideCard(dur) {
    if (!card) return;
    var d = card; card = null;
    gsap.to(d, { y: 50, opacity: 0, duration: dur == null ? 0.4 : dur, ease: 'power2.in', onComplete: function () { if (d.parentNode) d.parentNode.removeChild(d); } });
  }

  /* ------------------------------------------------------------ opening and closing cards */
  function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  /* a small owner/contract network on the right: amber approvals, sky transfers, dots that travel */
  function network(host, seed) {
    var R = rng(seed), NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'net');
    svg.setAttribute('width', 1920); svg.setAttribute('height', 1080);
    var defs = document.createElementNS(NS, 'defs');
    defs.innerHTML = '<marker id="vxa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#F5B43C"/></marker>' +
      '<marker id="vxt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#3CC4FF"/></marker>';
    svg.appendChild(defs);
    var contracts = [[1420, 330], [1650, 560], [1380, 760], [1720, 250]];
    var owners = [];
    for (var i = 0; i < 26; i++) {
      var a = R() * Math.PI * 2, rr = 180 + R() * 380;
      var c = contracts[i % contracts.length];
      owners.push([clamp(c[0] + Math.cos(a) * rr, 1080, 1860), clamp(c[1] + Math.sin(a) * rr * 0.8, 110, 980), i % contracts.length]);
    }
    var gE = document.createElementNS(NS, 'g'), gN = document.createElementNS(NS, 'g'), gD = document.createElementNS(NS, 'g');
    svg.appendChild(gE); svg.appendChild(gN); svg.appendChild(gD);
    var edges = [], dots = [];
    owners.forEach(function (o, i) {
      var c = contracts[o[2]], allow = i % 3 !== 2;
      var dx = c[0] - o[0], dy = c[1] - o[1], L = Math.hypot(dx, dy), k = (L - 34) / L;
      var p = document.createElementNS(NS, 'path');
      p.setAttribute('d', 'M' + o[0] + ' ' + o[1] + 'L' + (o[0] + dx * k).toFixed(1) + ' ' + (o[1] + dy * k).toFixed(1));
      p.setAttribute('stroke', allow ? '#F5B43C' : '#3CC4FF'); p.setAttribute('stroke-width', allow ? 2.4 : 2);
      p.setAttribute('stroke-opacity', allow ? 0.75 : 0.55); p.setAttribute('fill', 'none');
      p.setAttribute('marker-end', allow ? 'url(#vxa)' : 'url(#vxt)');
      if (!allow) p.setAttribute('stroke-dasharray', '8 8');
      p.setAttribute('pathLength', '1');
      gE.appendChild(p); edges.push({ p: p, allow: allow, o: o, c: c, k: k });
      var n = document.createElementNS(NS, 'circle');
      n.setAttribute('cx', o[0]); n.setAttribute('cy', o[1]); n.setAttribute('r', 9);
      n.setAttribute('fill', '#10151F'); n.setAttribute('stroke', '#8790A3'); n.setAttribute('stroke-width', 2);
      gN.appendChild(n); edges[edges.length - 1].n = n;
    });
    var cNodes = contracts.map(function (c) {
      var g = document.createElementNS(NS, 'g');
      g.innerHTML = '<rect x="' + (c[0] - 30) + '" y="' + (c[1] - 30) + '" width="60" height="60" rx="14" fill="#161C29" stroke="#E9EDF5" stroke-width="2.5"/>' +
        '<text x="' + c[0] + '" y="' + (c[1] + 9) + '" text-anchor="middle" font-size="26" fill="#E9EDF5" font-family="ui-monospace,monospace">{ }</text>';
      gN.appendChild(g); return g;
    });
    edges.forEach(function (e) {
      if (!e.allow) return;
      var d = document.createElementNS(NS, 'circle'); d.setAttribute('r', 4.5); d.setAttribute('fill', '#FFD27A'); d.setAttribute('opacity', 0);
      gD.appendChild(d); dots.push({ d: d, e: e });
    });
    host.appendChild(svg);
    var tl = gsap.timeline();
    tl.fromTo(cNodes, { opacity: 0, scale: 0.6, transformOrigin: '50% 50%' }, { opacity: 1, scale: 1, duration: 0.6, stagger: 0.12, ease: 'back.out(1.6)' }, 0.2);
    edges.forEach(function (e, i) {
      tl.fromTo(e.n, { opacity: 0 }, { opacity: 1, duration: 0.3 }, 0.5 + i * 0.07);
      e.p.style.strokeDasharray = e.allow ? '1' : '0.02 0.02';
      if (e.allow) tl.fromTo(e.p.style, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.8, ease: 'power2.out' }, 0.6 + i * 0.07);
      else tl.fromTo(e.p, { opacity: 0 }, { opacity: 1, duration: 0.6 }, 0.6 + i * 0.07);
    });
    /* dots keep travelling along the approval arrows: the endorsement that PageRank passes on */
    dots.forEach(function (o, i) {
      var st = { t: 0 }, e = o.e;
      var tw = gsap.to(st, { t: 1, duration: 2.6 + (i % 5) * 0.35, ease: 'none', repeat: -1, delay: 2.2 + (i % 7) * 0.3,
        onUpdate: function () {
          var x = e.o[0] + (e.c[0] - e.o[0]) * e.k * st.t, y = e.o[1] + (e.c[1] - e.o[1]) * e.k * st.t;
          o.d.setAttribute('cx', x.toFixed(1)); o.d.setAttribute('cy', y.toFixed(1));
          o.d.setAttribute('opacity', (Math.sin(Math.PI * st.t) * 0.9).toFixed(2));
        } });
      tl.add(tw, 0);
    });
    return { svg: svg, tl: tl };
  }
  function words(el, text) {
    el.innerHTML = '';
    text.split(/\s+/).forEach(function (w) {
      var m = document.createElement('span'); m.className = 'm';
      var s = document.createElement('span'); s.className = 'w'; s.textContent = w;
      m.appendChild(s); el.appendChild(m);
    });
    return el.querySelectorAll('.w');
  }
  var full = null;
  function intro(o) {
    if (full) full.el.remove();
    var el = document.createElement('div'); el.className = 'vx-full';
    scr.appendChild(el);
    var net = network(el, 7);
    var eb = document.createElement('div'); eb.className = 'eyebrow'; eb.textContent = o.eyebrow; el.appendChild(eb);
    var ti = document.createElement('div'); ti.className = 'title'; el.appendChild(ti);
    var ws = words(ti, o.title);
    var rule = document.createElement('div'); rule.className = 'rule'; el.appendChild(rule);
    var who = document.createElement('div'); who.className = 'who'; who.innerHTML = '<span></span><small></small>'; el.appendChild(who);
    who.firstChild.textContent = o.author; who.lastChild.textContent = o.affiliation;
    var lg = document.createElement('div'); lg.className = 'legend';
    lg.innerHTML = '<span><i style="background:#F5B43C"></i></span><span><i style="background:repeating-linear-gradient(90deg,#3CC4FF 0 8px,transparent 8px 16px)"></i></span>';
    lg.children[0].appendChild(document.createTextNode(o.legendAllow)); lg.children[1].appendChild(document.createTextNode(o.legendTransfer));
    el.appendChild(lg);
    /* layout: rule and author under the title, whatever its line count */
    var th = ti.getBoundingClientRect().height / (Deck.scale || 1);
    rule.style.top = (310 + th + 34) + 'px'; who.style.top = (310 + th + 66) + 'px';
    var tl = gsap.timeline();
    tl.add(net.tl, 0);
    tl.fromTo(eb, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, 0.3);
    tl.fromTo(ws, { yPercent: 110 }, { yPercent: 0, duration: 0.8, ease: 'power3.out', stagger: 0.06 }, 0.5);
    tl.fromTo(rule, { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: 'power3.inOut' }, 1.3);
    tl.fromTo(who, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' }, 1.6);
    tl.fromTo(lg, { opacity: 0 }, { opacity: 1, duration: 0.8 }, 2.4);
    full = { el: el, tl: tl, net: net };
  }
  function outro(o) {
    if (full) full.el.remove();
    var el = document.createElement('div'); el.className = 'vx-full';
    scr.appendChild(el);
    var net = network(el, 11);
    var eb = document.createElement('div'); eb.className = 'eyebrow'; eb.textContent = o.eyebrow; el.appendChild(eb);
    var ti = document.createElement('div'); ti.className = 'title'; el.appendChild(ti);
    var ws = words(ti, o.title);
    var rule = document.createElement('div'); rule.className = 'rule'; el.appendChild(rule);
    var who = document.createElement('div'); who.className = 'who'; who.innerHTML = '<span></span><small></small>'; el.appendChild(who);
    who.firstChild.textContent = o.author; who.lastChild.textContent = o.affiliation;
    var cr = document.createElement('div'); cr.className = 'credits'; cr.textContent = o.credits; el.appendChild(cr);
    var th = ti.getBoundingClientRect().height / (Deck.scale || 1);
    rule.style.top = (310 + th + 34) + 'px'; who.style.top = (310 + th + 66) + 'px';
    var tl = gsap.timeline();
    tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 1.0, ease: 'power1.inOut' }, 0);
    tl.add(net.tl, 0.4);
    tl.fromTo(eb, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.6 }, 0.8);
    tl.fromTo(ws, { yPercent: 110 }, { yPercent: 0, duration: 0.8, ease: 'power3.out', stagger: 0.06 }, 1.0);
    tl.fromTo(rule, { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: 'power3.inOut' }, 1.6);
    tl.fromTo(who, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.7 }, 1.9);
    tl.fromTo(cr, { opacity: 0 }, { opacity: 1, duration: 0.8 }, 2.6);
    full = { el: el, tl: tl, net: net };
  }
  function introOut(dur) {
    if (!full) return;
    var f = full; full = null;
    gsap.to(f.el, { opacity: 0, duration: dur || 1.0, ease: 'power1.inOut', onComplete: function () { f.tl.kill(); f.el.remove(); } });
  }
  function fadeBlack(dur) {
    var b = document.createElement('div'); b.className = 'vx-black'; scr.appendChild(b);
    gsap.fromTo(b, { opacity: 0 }, { opacity: 1, duration: dur || 1.5, ease: 'power1.in' });
  }

  function reset() {
    if (camTween) camTween.kill();
    C.s = 1; C.tx = 0; C.ty = 0; applyCam();
    marks.forEach(function (m) { m.tl.kill(); if (m.el.parentNode) m.el.parentNode.removeChild(m.el); }); marks = [];
    if (card && card.parentNode) card.parentNode.removeChild(card); card = null;
    if (full) { full.tl.kill(); full.el.remove(); full = null; }
    scr.innerHTML = ''; cam.innerHTML = '';
  }

  function anyActive() {
    var list = gsap.globalTimeline.getChildren(true, true, true);
    for (var i = 0; i < list.length; i++) if (list[i].isActive()) return true;
    return false;
  }
  function cssRunning() {
    if (!document.getAnimations) return false;
    var a = document.getAnimations(), now = window.__vt ? window.__vt.now() : 0;
    for (var i = 0; i < a.length; i++) {
      var t = a[i].effect && a[i].effect.getComputedTiming ? a[i].effect.getComputedTiming() : null;
      if (t && a[i].__vt0 !== undefined && now - a[i].__vt0 < t.endTime + 34) return true;
    }
    return false;
  }

  window.__vx = {
    camTo: function (boxes, zoom, dur) { return camTarget(targetFor(boxes, zoom), dur == null ? 0.8 : dur); },
    camHome: function (dur) { return camTarget({ s: 1, tx: 0, ty: 0 }, dur == null ? 0.6 : dur); },
    marks: addMarks, clearMarks: clearMarks,
    card: showCard, cardOut: function (dur) { hideCard(dur); },
    intro: intro, introOut: introOut, outro: outro, fadeBlack: fadeBlack,
    reset: reset,
    isHome: function () { return C.s === 1 && C.tx === 0 && C.ty === 0; },
    hasMarks: function () { return marks.length > 0; },
    hasCard: function () { return !!card; },
    dynamic: function () { return anyActive() || cssRunning() || !Deck.idle(); },
    target: targetFor
  };
})();
