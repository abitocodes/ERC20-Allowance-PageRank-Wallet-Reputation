/* =========================================================================
   deck.js — slide engine of the thesis deck (classic script, no modules).
   Works from file:// and over http. Needs lib/gsap.min.js; uses THREE and
   katex when present. Design tokens: css/deck.css, STORYBOARD.md §1.
   Working examples of every feature: tools/gallery.html (+ tools/gallery-sections.js).
   Screenshots of every slide and step: cd tools && npm install && node shoot.mjs [--only s04-pagerank].

   ------------------------------------------------------------------------
   REGISTERING SLIDES (one file per section in js/sections/)
   ------------------------------------------------------------------------
   Deck.section({ id: 's04-pagerank', title: '페이지랭크 유도', slides: [ slide, ... ] })
     The section number (ghost numeral, eyebrow "04 · 페이지랭크 유도", progress
     cell) is read from the id prefix sNN.

   slide = {
     id:     's04-03',                     // unique; used in the URL hash
     title:  '오래 걸으면 …',               // overview + notes panel
     notes:  '해요체 narration …',          // string, or array (one entry per step)
     html:   '<h1 class="t-h1">…[[강조]]…</h1>' | function(ctx) -> string,
     build:  function (el, ctx) {},        // optional: build DOM imperatively (after html)
     steps:  3,                            // build steps after the first view (default:
                                           //   highest data-step / data-step-out in html, else 0)
     enter:  function (el, ctx) { return cleanupFn; },   // slide becomes active (entry animation)
     step:   function (el, i, ctx, dir) {},              // bring the slide to build state i
     leave:  function (el, ctx) {},                      // optional, before teardown
     tl:     function (el, ctx) { return gsapTimeline; }, // optional "timeline mode", see below
     tags:   ['construct'] | function (step) -> [...],   // status pills, bottom right (§0.3)
     time:   45,                           // seconds planned (notes panel)
     ritual: true|false,                   // section-opening ritual (§1.9); default: first slide of a section
     ghost:  true|false,                   // ritual ghost numeral stays at 4 % (true) or fades out (false);
                                           //   default: fades out when slide content reaches into its box
     hud:    false,                        // hide the whole HUD on this slide (title page)
     progress: false,                      // hide only the progress bar
     autoIn: false,                        // switch off the generic entry animation of this slide
     back:   'custom',                     // call step(el, i, ctx, -1) on ← instead of rebuilding
     reducedAuto: false,                   // do not auto-settle animations in reduced motion
     math:   false,                        // do not auto-render $…$ / $$…$$ in the html
     carrier: true,                        // keep the continuity dot (ctx.carrier) from the previous slide
     className: 'my-layout'                // extra class on .slide-inner
   }

   `el` is the slide's .slide-inner element (1920x1080 design pixels, padded by
   the 12-column margins). In html, [[word]] becomes <span class="hl">word</span>
   (the one rose accent; its underline is drawn on entry).

   STEP SEMANTICS
     step(el, i, ctx, dir) brings the slide to build state i.
       dir = +1  advancing from state i-1 (animate)
       dir =  0  catching up instantly (deep link, ← rebuild, reduced motion): the
                 engine completes every finite tween you start, so you may simply
                 run the same code as for +1
       dir = -1  only when slide.back === 'custom': going back from i+1 to i (i may be 0)
     Default ← behaviour: the slide is rebuilt and fast-forwarded to state i
     (enter + step(1..i, dir 0), all tweens completed), so every step is
     reversible without writing backward code.
   FRAGMENTS (no code): any element with data-step="n" is hidden until step n;
     data-step-out="n" hides it again at step n. Their reveal/hide tweens belong to the slide's
     gsap context: a press during a reveal completes it first, and Deck.idle() waits for it. Reveal style: data-in = rise
     (default) | words | pop | draw | left | right | fade | none; data-stagger="0.08"
     staggers its children instead.
   TIMELINE MODE: tl(el, ctx) returns a GSAP timeline with labels 'step0' (end of
     the entry), 'step1', … 'stepN' (end of each build). Forward = tweenFromTo the
     previous label, back = seek. No step() needed.
   GENERIC ENTRY (unless autoIn:false): headings (.t-display, .t-h1, h1,
     [data-in=words]) rise word by word under a mask; other blocks rise 28px. Mark an
     element data-in="none" to animate it yourself in enter(). Exit: content moves up
     and out in 0.45 s, then the next slide rises — never a crossfade.
   SHARED ELEMENTS (FLIP): an element with data-shared="key" on two consecutive
     slides flies from its old box to its new box (1.0 s, power2.inOut) while the old
     copy hides. data-shared-mode="manual": no automatic flight; read the old box
     with ctx.prev.rect('key') and animate it yourself.

   ------------------------------------------------------------------------
   ctx (one per slide instance; everything it creates is cleaned up on leave)
   ------------------------------------------------------------------------
   ctx.el / ctx.root          .slide-inner / the .slide section element
   ctx.slide, ctx.index       slide definition, 0-based index
   ctx.step, ctx.dir          current build state, last direction
   ctx.data                   window.DECK_DATA
   ctx.reduced                prefers-reduced-motion (or M key)
   ctx.instant                true while the engine fast-forwards (deep link / rebuild)
   ctx.prev                   { id, index, rect(key) } of the slide we came from, or null
   ctx.D, ctx.E, ctx.C        duration tokens (s), ease tokens, colour hex tokens
   ctx.gsap                   gsap. Tweens made inside enter/step/build are recorded
                              and killed on leave; selector strings are scoped to the slide.
   ctx.add(fn)                run fn inside the slide's gsap context (use in async callbacks)
   ctx.tl(vars)               new gsap timeline (recorded)
   ctx.settle()               jump every running finite tween of this slide to its end
   ctx.count(el, from, to, opts)   count-up; opts {decimals, duration, delay, ease, prefix,
                              suffix, final (exact final text), format(v)} -> tween.
                              Ends exactly on `final` (or the formatted `to`).
   ctx.katex(el)              render $…$ and $$…$$ inside el (macros \ca \ct \cc \cd \ch
                              colour by meaning; \part{name}{…} marks a part for Comp.formula)
   ctx.tex(src, display)      KaTeX -> HTML string
   ctx.three(el, opts)        three.js stage sized to el (see below)
   ctx.raf(fn)                per-frame callback fn(t, dt) until leave; returns stop()
   ctx.timeout(fn, ms)        gsap.delayedCall (recorded, so settle/idle know about it)
   ctx.interval(fn, ms)       setInterval, cleared on leave
   ctx.on(target, type, fn, opts)  addEventListener, removed on leave
   ctx.cleanup(fn)            run fn on leave
   ctx.overlay()              full-stage SVG above the slide (stage coordinates) for leader lines
   ctx.rect(el)               element box in stage coordinates {x, y, w, h, cx, cy}
   ctx.toStage(evt)           pointer event -> stage coordinates {x, y}
   ctx.split(el)              split an element into masked words -> [word spans]
   ctx.rise(el|words, opts)   words rise from under the mask -> tween
   ctx.reveal(el, kind)       fragment-style reveal of any element -> timeline
   ctx.hud                    { setTags(keys), rect(part), showProgress(bool), el }
                              part: 'eyebrow' | 'id' | 'progress' | 'cell:N' (N = section number)
   ctx.carrier                continuity dot (G6), lives above all slides:
                              show(x, y) / moveTo(x, y, {duration, ease}) / path([[x,y],…], opts)
                              / pulse() / hide(); slides that use it set carrier:true
   ctx.rng(seed)              seeded random (mulberry32); ctx.fmt(n, decimals)

   ctx.three(container, opts) -> T
     opts: { fov:35, near:.1, far:2000, camera:{theta, phi, radius, target:[x,y,z]},
             orbit:true (drag to rotate with 0.95 inertia, wheel to zoom), autoRotate:0.05
             (rad/s; off in reduced motion), minRadius, maxRadius, background (null = transparent) }
     T = { THREE, scene, camera, renderer, wrap, width, height, orbit,
           render(), onFrame(fn(dt)), cameraTo({theta,phi,radius,target}, {duration, ease}) -> tween,
           label(html, [x,y,z], {className, anchor:'center'|'left'|'right'|'top'|'bottom', dx, dy}) -> label,
           project([x,y,z]) -> {x, y, visible}, dispose() }
     Renderers come from a pool of at most two WebGL contexts; scenes are disposed on leave.

   ------------------------------------------------------------------------
   Deck (global)
   ------------------------------------------------------------------------
   Deck.section(def)   register a section            Deck.start()   (automatic on DOMContentLoaded)
   Deck.list()         [{index, id, steps, title, section}]
   Deck.goto(i, step)  i = 0-based slide index (or slide id); same slide & step+1 animates
   Deck.next(), Deck.prev(), Deck.current() -> {index, id, step, steps}
   Deck.idle()         true when no transition or finite slide animation is running
   Deck.setReduced(bool|null)   null = follow the system setting
   Deck.scale, Deck.pixelRatio()   current stage scale and the backing-store ratio for canvases
                       (window event 'deck:resize' {scale, pixelRatio} fires after every re-layout)
   Deck.tex(src, display), Deck.renderMath(el), Deck.tagHTML(key), Deck.TAGS, Deck.COLORS,
   Deck.D, Deck.E, Deck.util { rng, fmt, pad2, splitWords, esc, lambdaColor }
   window.__deckErrors  runtime errors (window errors, rejections, slide callbacks, KaTeX)

   KEYS  → Space PageDown click: next step/slide · ← PageUp: back · ↓/↑ next/previous slide ·
         Home End · digits+Enter: go to slide n (the HUD shows "n / total") · N notes in this window
         (rehearsal) · P presenter window (notes, next, timer; drives this window by postMessage,
         also from file://) · O overview · M reduced motion · F fullscreen · ? help · Esc close panels.
         A focused range slider keeps only its arrows/Home/End; a mouse drag gives the keys back.
         Hash: #<slide-id>[/<step>], #<section-id>[/<step>] (first slide of the section),
         #<n>[/<step>] (1-based), #presenter (the presenter window).
   ========================================================================= */
(function (global) {
  'use strict';

  var STAGE_W = 1920, STAGE_H = 1080;
  var doc = global.document;
  var gsap = global.gsap;
  var errors = global.__deckErrors = global.__deckErrors || [];

  /* identical errors in a row (e.g. thrown every frame by a tween callback) are counted, not repeated */
  function record(rec) {
    var last = errors[errors.length - 1];
    if (last && last.type === rec.type && last.message === rec.message && last.where === rec.where && last.source === rec.source && last.line === rec.line) {
      last.count = (last.count || 1) + 1; return false;
    }
    errors.push(rec); return true;
  }
  function pushError(where, err, extra) {
    var rec = {
      type: 'deck', where: where,
      message: err && err.message ? err.message : String(err),
      stack: err && err.stack ? String(err.stack).split('\n').slice(0, 4).join('\n') : undefined
    };
    if (extra) rec.extra = extra;
    if (record(rec)) { try { console.error('[deck] ' + where + ': ' + rec.message); } catch (e) { /* ignore */ } }
  }
  global.addEventListener('error', function (e) {
    var rec = { type: 'error', message: e.message, source: e.filename, line: e.lineno, col: e.colno };
    if (e.error && e.error.stack) rec.stack = String(e.error.stack).split('\n').slice(0, 4).join('\n');
    /* under file:// Chrome hides details of errors thrown from other files (e.g. inside a
       tween callback): the console and tools/shoot.mjs ("page errors") still show them */
    if (e.message === 'Script error.') rec.hint = 'details hidden under file://; see the console or run tools/shoot.mjs';
    record(rec);
  });
  global.addEventListener('unhandledrejection', function (e) {
    var r = e.reason;
    record({ type: 'unhandledrejection', message: String(r && r.message ? r.message : r) });
  });

  if (!gsap) { pushError('boot', new Error('lib/gsap.min.js is missing')); return; }
  ['Flip', 'MotionPathPlugin', 'DrawSVGPlugin', 'MorphSVGPlugin', 'SplitText', 'ScrambleTextPlugin', 'CustomEase']
    .forEach(function (n) { if (global[n]) { try { gsap.registerPlugin(global[n]); } catch (e) { pushError('plugin ' + n, e); } } });
  var ROOT_TL = gsap.globalTimeline;

  /* ------------------------------------------------------------ tokens */
  var D = { xs: 0.18, s: 0.35, m: 0.6, l: 1.0, xl: 1.8, count: 1.6 };
  var E = { out: 'power3.out', 'in': 'power2.in', io: 'power2.inOut', type: 'expo.out', stamp: 'back.out(1.4)' };
  var COLORS = {
    bg: '#0A0D14', bg2: '#10151F', bg3: '#161C29', line: '#232B3B', ink: '#E9EDF5', ink2: '#A3ADBF', ink3: '#8790A3',
    allow: '#F5B43C', xfer: '#3CC4FF', cpr: '#A78BFA', deg: '#4ADE9B', hi: '#FF6B8A'
  };
  var TEX_MACROS = {
    '\\ca': '\\textcolor{F5B43C}{#1}', '\\ct': '\\textcolor{3CC4FF}{#1}', '\\cc': '\\textcolor{A78BFA}{#1}',
    '\\cd': '\\textcolor{4ADE9B}{#1}', '\\ch': '\\textcolor{FF6B8A}{#1}', '\\ci': '\\textcolor{A3ADBF}{#1}',
    '\\cm': '\\textcolor{8790A3}{#1}', '\\part': '\\htmlClass{fx-part fx-#1}{#2}'
  };

  /* status tags (§0.3, G11): icon + words, never colour */
  var SVG_ICON = function (body) {
    return '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + body + '</svg>';
  };
  var ICONS = {
    lock: SVG_ICON('<rect x="4" y="9" width="12" height="8.5" rx="2"/><path d="M7 9V6.5a3 3 0 0 1 6 0V9"/>'),
    seal: SVG_ICON('<path d="M10 2.4l1.9 1.4 2.3-.2.8 2.2 2 1.2-.6 2.3.6 2.3-2 1.2-.8 2.2-2.3-.2L10 17.6l-1.9-1.4-2.3.2-.8-2.2-2-1.2.6-2.3-.6-2.3 2-1.2.8-2.2 2.3.2z"/><path d="M7.4 10.1l1.8 1.8 3.5-3.7"/>'),
    loop: SVG_ICON('<path d="M15.6 8.4A6 6 0 1 0 16 12"/><path d="M16.2 4.3v4.2H12"/>'),
    eye: SVG_ICON('<path d="M1.8 10S5 4.6 10 4.6 18.2 10 18.2 10 15 15.4 10 15.4 1.8 10 1.8 10z"/><circle cx="10" cy="10" r="2.6"/>'),
    compass: SVG_ICON('<circle cx="10" cy="10" r="7.6"/><path d="M13 7l-1.8 4.2L7 13l1.8-4.2z"/>'),
    mirror: SVG_ICON('<ellipse cx="10" cy="8" rx="5" ry="6"/><path d="M10 14v4M7 18h6M8 5.4l3.2 3.2"/>'),
    hollow: SVG_ICON('<circle cx="10" cy="10" r="6" stroke-dasharray="2.6 2.2"/>'),
    pencil: SVG_ICON('<path d="M4 16l2.6-.6 8.4-8.4a1.5 1.5 0 0 0-2-2L4.6 13.4 4 16z"/>'),
    sigma: SVG_ICON('<path d="M14.5 4.5h-9l5 5.5-5 5.5h9"/>')
  };
  var TAGS = {
    'plan':                { ko: '미리 정함(계획)', icon: 'lock' },
    'registered':          { ko: '등록함(W1)', icon: 'seal' },
    'reanalysis':          { ko: '재분석', icon: 'loop' },
    'posthoc':             { ko: '사후(라벨 본 뒤)', icon: 'eye' },
    'exploratory':         { ko: '탐색적', icon: 'compass' },
    'construct':           { ko: '의도한 구성개념 점검', icon: 'mirror' },
    'registered-analysis': { ko: '등록 분석', icon: 'hollow', ghost: true },
    'example':             { ko: '예시', icon: 'pencil', ghost: true },
    'thesis-example':      { ko: '논문 2장 예시', icon: 'pencil', ghost: true },
    'calc':                { ko: '계산', icon: 'sigma', ghost: true }
  };
  var TAG_ALIASES = { 'w1': 'registered', 'G': 'registered-analysis', 'check': 'construct', 'post-hoc': 'posthoc' };
  function tagHTML(key) {
    var t = typeof key === 'object' ? key : TAGS[TAG_ALIASES[key] || key];
    if (!t) { pushError('tag', new Error('unknown status tag: ' + key)); t = { ko: String(key), icon: 'hollow' }; }
    return '<span class="pill' + (t.ghost ? ' pill-ghost' : '') + '" data-tag="' + esc(String(key.key || key)) + '">' +
      (ICONS[t.icon] || '') + '<span>' + esc(t.ko) + '</span></span>';
  }

  /* ------------------------------------------------------------ utils */
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function mulberry32(a) {
    a = a >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  var fmtCache = {};
  function fmt(v, decimals, opts) {
    decimals = decimals == null ? 0 : decimals;
    var key = decimals + (opts && opts.grouping === false ? 'n' : 'g');
    var f = fmtCache[key] || (fmtCache[key] = new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals, maximumFractionDigits: decimals, useGrouping: !(opts && opts.grouping === false)
    }));
    var s = f.format(v);
    return s === '-0' ? '0' : s.replace(/^-(0(\.0+)?)$/, '$1');
  }
  function decimalsOf(x) { var s = String(x); var i = s.indexOf('.'); return i < 0 || /e/i.test(s) ? 0 : s.length - i - 1; }
  function hexToRgb(h) { h = h.replace('#', ''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; }
  function lambdaColor(l) { /* λ=0 sky -> 0.5 purple -> 1 amber (§1.1) */
    l = Math.max(0, Math.min(1, +l || 0));
    var a = l < 0.5 ? hexToRgb(COLORS.xfer) : hexToRgb(COLORS.cpr), b = l < 0.5 ? hexToRgb(COLORS.cpr) : hexToRgb(COLORS.allow);
    var t = l < 0.5 ? l / 0.5 : (l - 0.5) / 0.5;
    var c = [0, 1, 2].map(function (i) { return Math.round(a[i] + (b[i] - a[i]) * t); });
    return '#' + c.map(function (v) { return (v < 16 ? '0' : '') + v.toString(16); }).join('').toUpperCase();
  }
  function $$(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }
  function preprocess(html) { return String(html).replace(/\[\[([\s\S]+?)\]\]/g, '<span class="hl">$1</span>'); }
  function maxStepIn(html) {
    var m, re = /data-step(?:-out)?\s*=\s*["']?(\d+)/g, max = 0;
    while ((m = re.exec(html))) max = Math.max(max, +m[1]);
    return max;
  }

  /* masked word split (keeps inline elements such as .hl and KaTeX whole) */
  function splitWords(el) {
    if (el.__words) return el.__words;
    var words = [];
    function mask(content) {
      var m = doc.createElement('span'); m.className = 'w-mask';
      var w = doc.createElement('span'); w.className = 'w-word';
      if (typeof content === 'string') w.textContent = content; else w.appendChild(content);
      m.appendChild(w); words.push(w); return m;
    }
    function walk(parent) {
      Array.prototype.slice.call(parent.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var parts = n.nodeValue.split(/(\s+)/), frag = doc.createDocumentFragment();
          parts.forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) frag.appendChild(doc.createTextNode(p)); else frag.appendChild(mask(p));
          });
          parent.replaceChild(frag, n);
        } else if (n.nodeType === 1) {
          if (n.tagName === 'BR' || n.classList.contains('w-mask')) return;
          var disp = global.getComputedStyle(n).display;
          if (disp === 'block' || disp === 'flex' || disp === 'grid' || disp === 'list-item') { walk(n); return; }
          var holder = doc.createElement('span');
          parent.replaceChild(holder, n);
          holder.parentNode.replaceChild(mask(n), holder);
        }
      });
    }
    walk(el);
    el.__words = words;
    return words;
  }

  /* ------------------------------------------------------------ KaTeX */
  function katexOpts(display, throwOnError) {
    var macros = {}; for (var k in TEX_MACROS) macros[k] = TEX_MACROS[k];
    return {
      displayMode: !!display, throwOnError: !!throwOnError, strict: 'ignore', macros: macros,
      trust: function (c) { return c.command === '\\htmlClass' || c.command === '\\htmlData'; }
    };
  }
  function katexInto(node, tex, display) {
    if (!global.katex) { node.textContent = tex; pushError('katex', new Error('lib/katex is missing')); return; }
    try { global.katex.render(tex, node, katexOpts(display, true)); }
    catch (e) { pushError('katex', e, tex); global.katex.render(tex, node, katexOpts(display, false)); }
  }
  function tex(src, display) {
    if (!global.katex) return esc(src);
    try { return global.katex.renderToString(src, katexOpts(display, true)); }
    catch (e) { pushError('katex', e, src); return global.katex.renderToString(src, katexOpts(display, false)); }
  }
  function parseMath(text) {
    var out = [], buf = '', i = 0, n = text.length;
    function flush() { if (buf) { out.push({ t: 0, v: buf }); buf = ''; } }
    while (i < n) {
      var ch = text.charAt(i);
      if (ch === '\\' && text.charAt(i + 1) === '$') { buf += '$'; i += 2; continue; }
      if (ch === '$') {
        var display = text.charAt(i + 1) === '$', open = display ? 2 : 1, j = i + open, found = -1;
        while (j < n) {
          if (text.charAt(j) === '\\') { j += 2; continue; }
          if (text.charAt(j) === '$' && (!display || text.charAt(j + 1) === '$')) { found = j; break; }
          j++;
        }
        if (found < 0) { buf += text.slice(i); break; }
        flush(); out.push({ t: display ? 2 : 1, v: text.slice(i + open, found) });
        i = found + open; continue;
      }
      buf += ch; i++;
    }
    flush();
    return out;
  }
  function renderMath(root) {
    if (!root) return;
    var nodes = [], tw = doc.createTreeWalker(root, 4 /* SHOW_TEXT */, null);
    var n;
    while ((n = tw.nextNode())) {
      if (n.nodeValue.indexOf('$') < 0) continue;
      var p = n.parentNode, skip = false;
      while (p && p !== root.parentNode) {
        if (p.nodeType === 1 && (/^(SCRIPT|STYLE|CODE|PRE|TEXTAREA)$/.test(p.nodeName) || (p.classList && (p.classList.contains('katex') || p.classList.contains('no-math'))))) { skip = true; break; }
        p = p.parentNode;
      }
      if (!skip) nodes.push(n);
    }
    nodes.forEach(function (node) {
      var parts = parseMath(node.nodeValue);
      if (parts.length === 1 && parts[0].t === 0) return;
      var frag = doc.createDocumentFragment();
      parts.forEach(function (p) {
        if (p.t === 0) { frag.appendChild(doc.createTextNode(p.v)); return; }
        var span = doc.createElement('span');
        span.className = p.t === 2 ? 'math-display' : 'math-inline';
        katexInto(span, p.v, p.t === 2);
        frag.appendChild(span);
      });
      node.parentNode.replaceChild(frag, node);
    });
  }

  /* ------------------------------------------------------------ state */
  var sections = [], slides = [];
  var state = {
    started: false, index: -1, scale: 1, notes: false, overview: false, help: false,
    reducedUser: null, reducedSys: false, transition: null, suppressClick: false,
    startTime: 0, jumpBuf: '', jumpTimer: null, pendingGoto: null,
    presenter: /^#presenter\b/.test(global.location.hash || ''), presenterWin: null, lastSync: 0
  };
  var cur = null;                 /* current slide instance */
  var dying = [];                 /* instances leaving (during a transition) */
  var dom = {};
  var mq = global.matchMedia ? global.matchMedia('(prefers-reduced-motion: reduce)') : null;
  state.reducedSys = !!(mq && mq.matches);
  function reduced() { return state.reducedUser == null ? state.reducedSys : !!state.reducedUser; }

  /* ------------------------------------------------------------ registration */
  function section(def) {
    if (!def || !def.id) { pushError('section', new Error('Deck.section needs an id')); return; }
    var m = /^s(\d+)/.exec(def.id);
    var sec = { id: def.id, title: def.title || def.id, num: m ? +m[1] : sections.length + 1, slides: [], order: sections.length };
    var existing = -1;
    sections.forEach(function (s, i) { if (s.id === def.id) existing = i; });
    if (existing >= 0) { pushError('section', new Error('section registered twice: ' + def.id)); return; }
    (def.slides || []).forEach(function (s, i) {
      if (!s) return;
      var sl = s;
      sl.id = sl.id || (def.id.replace(/^(s\d+).*/, '$1') + '-' + pad2(i + 1));
      sl.section = sec; sl.indexInSection = i;
      if (sl.steps == null) sl.steps = typeof sl.html === 'string' ? maxStepIn(sl.html) : 0;
      sl.steps = Math.max(0, sl.steps | 0);
      if (sl.ritual == null) sl.ritual = i === 0;
      sec.slides.push(sl);
    });
    sections.push(sec);
    sections.sort(function (a, b) { return a.num - b.num || a.order - b.order; });
    slides = [];
    sections.forEach(function (s) { s.slides.forEach(function (sl) { sl.index = slides.length; slides.push(sl); }); });
    var seen = {};
    slides.forEach(function (sl) { if (seen[sl.id]) pushError('section', new Error('duplicate slide id ' + sl.id)); seen[sl.id] = 1; });
    if (state.started) buildProgress();
  }

  /* ------------------------------------------------------------ chrome */
  function el(tag, cls, parent, html) {
    var e = doc.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e;
  }
  function buildChrome() {
    var body = doc.body;
    dom.viewport = el('div', '', body); dom.viewport.id = 'deck-viewport';
    dom.stage = el('div', '', dom.viewport); dom.stage.id = 'deck-stage';
    dom.stage.setAttribute('role', 'region'); dom.stage.setAttribute('aria-roledescription', 'slide deck');
    dom.slides = el('div', '', dom.stage); dom.slides.id = 'deck-slides';
    dom.ritual = el('div', '', dom.stage); dom.ritual.id = 'deck-ritual';
    dom.hud = el('div', '', dom.stage); dom.hud.id = 'deck-hud';
    dom.carrier = el('div', '', dom.stage); dom.carrier.id = 'deck-carrier';
    dom.eyebrow = el('div', 'hud-eyebrow', dom.hud, '<span class="hud-num"></span><span class="hud-sep">·</span><span class="hud-name"></span>');
    dom.hudNum = dom.eyebrow.children[0]; dom.hudSep = dom.eyebrow.children[1]; dom.hudName = dom.eyebrow.children[2];
    dom.hudId = el('div', 'hud-id', dom.hud);
    dom.tags = el('div', 'hud-tags', dom.hud);
    dom.progress = el('div', 'hud-progress', dom.hud);
    dom.notes = el('aside', '', body); dom.notes.id = 'deck-notes';
    dom.notes.innerHTML = '<div class="notes-head"><span class="nh-pos"></span><span class="nh-timer">00:00</span></div>' +
      '<div class="notes-title"></div><div class="notes-step"></div><div class="notes-steps"></div><div class="notes-body"></div><div class="notes-next"></div>';
    dom.overview = el('div', '', body); dom.overview.id = 'deck-overview';
    dom.jump = el('div', '', body); dom.jump.id = 'deck-jump';
    dom.toast = el('div', '', body); dom.toast.id = 'deck-toast';
    dom.help = el('div', '', body); dom.help.id = 'deck-help';
    dom.help.innerHTML = '<div class="help-card"><h4>키</h4>' +
      '<div><kbd>→</kbd><kbd>Space</kbd>다음 단계 · 다음 장</div><div><kbd>←</kbd>이전 단계</div>' +
      '<div><kbd>↓</kbd><kbd>↑</kbd>다음 장 · 이전 장</div><div><kbd>Home</kbd><kbd>End</kbd>처음 · 끝</div>' +
      '<div><kbd>12</kbd><kbd>Enter</kbd>12번째 장으로</div><div><kbd>N</kbd>발표 노트 (같은 창, 연습용)</div>' +
      '<div><kbd>P</kbd>발표자 창 (노트·다음·시간, 따로 띄워요)</div><div><kbd>O</kbd>전체 보기</div>' +
      '<div><kbd>M</kbd>움직임 줄이기</div><div><kbd>F</kbd>전체 화면</div><div><kbd>Esc</kbd>닫기</div></div>';
    buildCarrier();
    buildProgress();
  }
  function buildProgress() {
    if (!dom.progress) return;
    dom.progress.innerHTML = '';
    dom.cells = {};
    sections.forEach(function (s) {
      var c = el('div', 'hud-cell', dom.progress, '<span class="hud-fill"></span><span class="hud-dot"></span>');
      c.setAttribute('data-sec', s.num);
      dom.cells[s.num] = c;
    });
    if (cur) updateHUD(cur, false);
  }

  /* ------------------------------------------------------------ layout / scale */
  function layout() {
    if (!dom.stage) return;
    var vw = global.innerWidth, vh = global.innerHeight;
    var notesW = state.notes ? dom.notes.getBoundingClientRect().width : 0;
    var aw = Math.max(160, vw - notesW), ah = Math.max(90, vh);
    var s = Math.min(aw / STAGE_W, ah / STAGE_H);
    var left = Math.round((aw - STAGE_W * s) / 2), top = Math.round((ah - STAGE_H * s) / 2);
    dom.stage.style.transform = 'translate(' + left + 'px,' + top + 'px) scale(' + s + ')';
    state.scale = s;
    allInstances().forEach(function (inst) { inst.threes.forEach(function (T) { T._resize(); }); });
    try { global.dispatchEvent(new CustomEvent('deck:resize', { detail: { scale: s, pixelRatio: pixelRatio() } })); } catch (e) { /* ignore */ }
  }
  function stageRect(elm) {
    var r = elm.getBoundingClientRect(), sr = dom.stage.getBoundingClientRect(), s = state.scale || 1;
    var x = (r.left - sr.left) / s, y = (r.top - sr.top) / s, w = r.width / s, h = r.height / s;
    return { x: x, y: y, w: w, h: h, cx: x + w / 2, cy: y + h / 2, left: x, top: y, right: x + w, bottom: y + h, width: w, height: h };
  }
  function pixelRatio() { return Math.max(0.75, Math.min(2, (global.devicePixelRatio || 1) * (state.scale || 1))); }

  /* ------------------------------------------------------------ carrier (G6) */
  var carrier = { el: null, tails: [], visible: false, ctx: null, x: 0, y: 0 };
  function buildCarrier() {
    var root = dom.carrier;
    for (var i = 0; i < 5; i++) {
      var t = el('div', 'carrier-tail', root);
      t.style.opacity = String(0.28 - i * 0.05); t.style.transform = 'scale(' + (1 - i * 0.14) + ')';
      carrier.tails.push(t);
    }
    carrier.el = el('div', 'carrier-dot', root);
    gsap.set(root, { autoAlpha: 0 });
    carrier.quick = carrier.tails.map(function (t, i) {
      return { x: gsap.quickTo(t, 'x', { duration: 0.08 + i * 0.05, ease: 'power2.out' }), y: gsap.quickTo(t, 'y', { duration: 0.08 + i * 0.05, ease: 'power2.out' }) };
    });
    carrier.ctx = gsap.context(function () {});
    gsap.ticker.add(function () {
      if (!carrier.visible) return;
      var x = gsap.getProperty(carrier.el, 'x'), y = gsap.getProperty(carrier.el, 'y');
      if (x !== carrier.x || y !== carrier.y) {
        carrier.x = x; carrier.y = y;
        carrier.quick.forEach(function (q) { q.x(x); q.y(y); });
      }
    });
  }
  var carrierAPI = {
    get el() { return carrier.el; },
    get position() { return { x: gsap.getProperty(carrier.el, 'x'), y: gsap.getProperty(carrier.el, 'y') }; },
    show: function (x, y, opts) {
      opts = opts || {};
      carrier.visible = true;
      if (x != null) { gsap.set(carrier.el, { x: x, y: y }); carrier.tails.forEach(function (t) { gsap.set(t, { x: x, y: y }); }); }
      return carrier.ctx.add(function () {
        return gsap.to(dom.carrier, { autoAlpha: 1, duration: reduced() || opts.instant ? 0 : (opts.duration != null ? opts.duration : 0.35) });
      });
    },
    moveTo: function (x, y, opts) {
      opts = opts || {}; carrier.visible = true;
      gsap.set(dom.carrier, { autoAlpha: 1 });
      return carrier.ctx.add(function () {
        return gsap.to(carrier.el, { x: x, y: y, duration: reduced() ? 0 : (opts.duration != null ? opts.duration : 0.8), ease: opts.ease || 'power2.inOut', delay: opts.delay || 0 });
      });
    },
    path: function (pts, opts) {
      opts = opts || {}; carrier.visible = true;
      gsap.set(dom.carrier, { autoAlpha: 1 });
      var dur = reduced() ? 0 : (opts.duration != null ? opts.duration : 1.2);
      return carrier.ctx.add(function () {
        var tl = gsap.timeline({ delay: opts.delay || 0 });
        var per = dur / Math.max(1, pts.length);
        pts.forEach(function (p) { tl.to(carrier.el, { x: p[0], y: p[1], duration: per, ease: opts.ease || 'none' }); });
        return tl;
      });
    },
    pulse: function () {
      return carrier.ctx.add(function () { return gsap.fromTo(carrier.el, { scale: 1.8 }, { scale: 1, duration: 0.5, ease: 'power3.out' }); });
    },
    hide: function (opts) {
      opts = opts || {};
      var d = reduced() || opts.instant ? 0 : (opts.duration != null ? opts.duration : 0.3);
      return carrier.ctx.add(function () {
        return gsap.to(dom.carrier, { autoAlpha: 0, duration: d, onComplete: function () { carrier.visible = false; } });
      });
    }
  };

  /* ------------------------------------------------------------ animation bookkeeping */
  function finiteAnim(a) {
    if (!a || !a.totalDuration) return false;
    if (a.repeat && a.repeat() < 0) return false;
    return a.totalDuration() < 3600;
  }
  function topLevel(a) { return a.parent === ROOT_TL; }
  function settleCtx(gctx, except) {
    var data = gctx.data.slice(), changed = true, guard = 0;
    /* settling can create new tweens (callbacks); loop a few times */
    while (changed && guard++ < 6) {
      changed = false;
      data = gctx.data.slice();
      for (var i = 0; i < data.length; i++) {
        var a = data[i];
        if (!a || a === except || !(a instanceof gsap.core.Animation)) continue;
        if (!topLevel(a) || a.paused() || !finiteAnim(a)) continue;
        if (a.totalProgress() < 1) {
          a.totalProgress(1); changed = true;
          /* repair: a zero-length child sitting exactly at its parent's end can be left at
             its start state; push any unfinished descendant to its end (in time order) */
          if (a.getChildren) a.getChildren(true, true, true).forEach(function (ch) {
            if (!ch.paused() && finiteAnim(ch) && ch.totalProgress() < 1) ch.totalProgress(1);
          });
        }
      }
    }
  }
  function pauseLoops(gctx) {
    gctx.data.forEach(function (a) {
      if (a instanceof gsap.core.Animation && topLevel(a) && !finiteAnim(a)) a.pause();
    });
  }
  function ctxBusy(gctx, except) {
    for (var i = 0; i < gctx.data.length; i++) {
      var a = gctx.data[i];
      if (!a || a === except || !(a instanceof gsap.core.Animation)) continue;
      if (topLevel(a) && !a.paused() && finiteAnim(a) && a.totalProgress() < 1) return true;
    }
    return false;
  }

  /* ------------------------------------------------------------ three.js */
  var rendererPool = [], webglFailed = false;
  function acquireRenderer() {
    var r = rendererPool.pop();
    if (r) return r;
    if (webglFailed || !global.THREE) return null;
    try {
      r = new global.THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
      return r;
    } catch (e) { webglFailed = true; pushError('three', e); return null; }
  }
  function releaseRenderer(r) {
    try {
      r.setAnimationLoop(null);
      if (r.renderLists) r.renderLists.dispose();
      if (r.domElement.parentNode) r.domElement.parentNode.removeChild(r.domElement);
      if (rendererPool.length < 2) rendererPool.push(r); else { r.dispose(); r.forceContextLoss(); }
    } catch (e) { pushError('three release', e); }
  }
  function disposeObject(root) {
    root.traverse(function (o) {
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        [].concat(o.material).forEach(function (m) {
          for (var k in m) { if (m[k] && m[k].isTexture) m[k].dispose(); }
          if (m.uniforms) { for (var u in m.uniforms) { var v = m.uniforms[u] && m.uniforms[u].value; if (v && v.isTexture) v.dispose(); } }
          m.dispose();
        });
      }
    });
  }
  function makeThree(inst, container, opts) {
    opts = opts || {};
    var THREE = global.THREE;
    var wrap = el('div', 'three-wrap' + (opts.orbit === false ? '' : ' orbit'), container);
    var renderer = THREE ? acquireRenderer() : null;
    if (!renderer) {
      wrap.innerHTML = '<div class="three-fallback">3D 장면을 그릴 수 없어요 (WebGL 없음)</div>';
      if (!THREE) pushError('three', new Error('lib/three.min.js is missing'));
      var stub = { THREE: THREE, wrap: wrap, failed: true, scene: null, camera: null, render: function () {}, onFrame: function () {},
        cameraTo: function () { return gsap.to({}, { duration: 0 }); }, label: function () { return { el: el('div'), set: function () {}, show: function () {}, hide: function () {} }; },
        project: function () { return { x: 0, y: 0, visible: false }; }, dispose: function () {}, _resize: function () {}, _tick: function () {} };
      return stub;
    }
    var canvas = renderer.domElement;
    wrap.appendChild(canvas);
    var w = Math.max(2, opts.width || container.clientWidth || STAGE_W), h = Math.max(2, opts.height || container.clientHeight || STAGE_H);
    renderer.setPixelRatio(pixelRatio());
    renderer.setSize(w, h, false);
    if (opts.background != null) renderer.setClearColor(new THREE.Color(opts.background), 1); else renderer.setClearColor(0x000000, 0);
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(opts.fov || 35, w / h, opts.near || 0.1, opts.far || 2000);
    var cam = opts.camera || {};
    var tgt = cam.target || [0, 0, 0];
    var orbit = {
      theta: cam.theta != null ? cam.theta : 0.6, phi: cam.phi != null ? cam.phi : 1.1, radius: cam.radius != null ? cam.radius : 10,
      tx: tgt[0], ty: tgt[1], tz: tgt[2],
      vTheta: 0, vPhi: 0, enabled: opts.orbit !== false,
      autoRotate: reduced() ? 0 : (opts.autoRotate || 0), held: false,
      minRadius: opts.minRadius || 0.5, maxRadius: opts.maxRadius || 500, minPhi: 0.05, maxPhi: Math.PI - 0.05
    };
    var labelsEl = el('div', 'three-labels', wrap);
    var T = {
      THREE: THREE, scene: scene, camera: camera, renderer: renderer, canvas: canvas, wrap: wrap,
      width: w, height: h, orbit: orbit, frameFns: [], labels: [], disposed: false, failed: false
    };
    function applyOrbit() {
      orbit.phi = Math.max(orbit.minPhi, Math.min(orbit.maxPhi, orbit.phi));
      orbit.radius = Math.max(orbit.minRadius, Math.min(orbit.maxRadius, orbit.radius));
      var sp = Math.sin(orbit.phi);
      camera.position.set(orbit.tx + orbit.radius * sp * Math.sin(orbit.theta), orbit.ty + orbit.radius * Math.cos(orbit.phi), orbit.tz + orbit.radius * sp * Math.cos(orbit.theta));
      camera.lookAt(orbit.tx, orbit.ty, orbit.tz);
    }
    var v3 = new THREE.Vector3();
    T.project = function (p) {
      if (p.isVector3) v3.copy(p); else v3.set(p[0], p[1], p[2]);
      v3.project(camera);
      return { x: (v3.x + 1) / 2 * T.width, y: (1 - v3.y) / 2 * T.height, visible: v3.z < 1 && v3.z > -1 };
    };
    T.label = function (html, pos, lopts) {
      lopts = lopts || {};
      var lab = el('div', 'three-label' + (lopts.className ? ' ' + lopts.className : ''), labelsEl, html);
      var L = { el: lab, pos: new THREE.Vector3(pos[0], pos[1], pos[2]), anchor: lopts.anchor || 'center', dx: lopts.dx || 0, dy: lopts.dy || 0, hidden: false,
        set: function (h2) { lab.innerHTML = h2; }, show: function () { L.hidden = false; }, hide: function () { L.hidden = true; lab.style.visibility = 'hidden'; } };
      T.labels.push(L);
      return L;
    };
    function updateLabels() {
      for (var i = 0; i < T.labels.length; i++) {
        var L = T.labels[i];
        if (L.hidden) continue;
        var p = T.project(L.pos);
        var ax = L.anchor === 'left' ? '0%' : L.anchor === 'right' ? '-100%' : '-50%';
        var ay = L.anchor === 'top' ? '0%' : L.anchor === 'bottom' ? '-100%' : '-50%';
        L.el.style.visibility = p.visible ? 'visible' : 'hidden';
        L.el.style.transform = 'translate(' + (p.x + L.dx).toFixed(1) + 'px,' + (p.y + L.dy).toFixed(1) + 'px) translate(' + ax + ',' + ay + ')';
      }
    }
    T.render = function () {
      if (T.disposed) return;
      applyOrbit();
      renderer.render(scene, camera);
      updateLabels();
    };
    T.onFrame = function (fn) { T.frameFns.push(fn); return function () { var i = T.frameFns.indexOf(fn); if (i >= 0) T.frameFns.splice(i, 1); }; };
    T.cameraTo = function (c, o) {
      o = o || {};
      var to = {};
      if (c.theta != null) to.theta = c.theta;
      if (c.phi != null) to.phi = c.phi;
      if (c.radius != null) to.radius = c.radius;
      if (c.target) { to.tx = c.target[0]; to.ty = c.target[1]; to.tz = c.target[2]; }
      orbit.vTheta = orbit.vPhi = 0;
      return inst.gctx.add(function () {
        return gsap.to(orbit, Object.assign(to, { duration: reduced() || inst.ctx.instant ? 0 : (o.duration != null ? o.duration : D.xl), ease: o.ease || E.io, delay: o.delay || 0 }));
      });
    };
    T._resize = function () {
      if (T.disposed) return;
      var nw = Math.max(2, opts.width || wrap.clientWidth), nh = Math.max(2, opts.height || wrap.clientHeight);
      renderer.setPixelRatio(pixelRatio());
      if (nw !== T.width || nh !== T.height) { T.width = nw; T.height = nh; camera.aspect = nw / nh; camera.updateProjectionMatrix(); }
      renderer.setSize(T.width, T.height, false);
      T.render();
    };
    T._tick = function (dt) {
      if (T.disposed) return;
      if (!orbit.held) {
        if (orbit.vTheta || orbit.vPhi) {
          orbit.theta += orbit.vTheta; orbit.phi += orbit.vPhi;
          orbit.vTheta *= 0.95; orbit.vPhi *= 0.95;
          if (Math.abs(orbit.vTheta) < 1e-5) orbit.vTheta = 0;
          if (Math.abs(orbit.vPhi) < 1e-5) orbit.vPhi = 0;
        }
        if (orbit.autoRotate && !reduced()) orbit.theta += orbit.autoRotate * dt;
      }
      for (var i = 0; i < T.frameFns.length; i++) { try { T.frameFns[i](dt); } catch (e) { pushError('three onFrame', e); T.frameFns.splice(i--, 1); } }
      T.render();
    };
    T.dispose = function () {
      if (T.disposed) return;
      T.disposed = true;
      try { disposeObject(scene); scene.clear(); } catch (e) { pushError('three dispose', e); }
      releaseRenderer(renderer);
      if (wrap.parentNode) wrap.parentNode.removeChild(wrap);
      T.frameFns.length = 0; T.labels.length = 0;
    };
    /* orbit interaction: drag rotates (inertia 0.95), wheel zooms */
    if (orbit.enabled) {
      var last = null, moved = 0;
      inst.ctx.on(wrap, 'pointerdown', function (e) {
        if (e.button !== 0) return;
        last = { x: e.clientX, y: e.clientY }; moved = 0; orbit.held = true; orbit.vTheta = orbit.vPhi = 0;
        try { wrap.setPointerCapture(e.pointerId); } catch (er) { /* ignore */ }
        wrap.classList.add('dragging');
      });
      inst.ctx.on(wrap, 'pointermove', function (e) {
        if (!last) return;
        var s = state.scale || 1, dx = (e.clientX - last.x) / s, dy = (e.clientY - last.y) / s;
        last = { x: e.clientX, y: e.clientY }; moved += Math.abs(dx) + Math.abs(dy);
        orbit.vTheta = -dx * 0.0055; orbit.vPhi = -dy * 0.0055;
        orbit.theta += orbit.vTheta; orbit.phi += orbit.vPhi;
        orbit.autoRotate = 0;
      });
      var up = function () {
        if (!last) return;
        last = null; orbit.held = false; wrap.classList.remove('dragging');
        if (moved > 6) { state.suppressClick = true; gsap.delayedCall(0.05, function () { state.suppressClick = false; }); }
      };
      inst.ctx.on(wrap, 'pointerup', up); inst.ctx.on(wrap, 'pointercancel', up);
      inst.ctx.on(wrap, 'wheel', function (e) {
        e.preventDefault();
        orbit.radius *= Math.exp(Math.max(-60, Math.min(60, e.deltaY)) * 0.0015);
      }, { passive: false });
    }
    inst.threes.push(T);
    applyOrbit();
    return T;
  }

  /* ------------------------------------------------------------ the shared ticker */
  var lastTick = 0;
  gsap.ticker.add(function (time) {
    var dt = lastTick ? Math.min(0.1, time - lastTick) : 0.016;
    lastTick = time;
    var list = allInstances();
    for (var k = 0; k < list.length; k++) {
      var inst = list[k];
      if (inst.dead) continue;
      for (var i = 0; i < inst.loops.length; i++) {
        var L = inst.loops[i];
        L.t += dt;
        try { L.fn(L.t, dt); } catch (e) { pushError(inst.slide.id + ' raf', e); inst.loops.splice(i--, 1); }
      }
      for (var j = 0; j < inst.threes.length; j++) inst.threes[j]._tick(dt);
    }
  });

  /* ------------------------------------------------------------ slide instances */
  function allInstances() { var a = dying.slice(); if (cur) a.push(cur); return a; }

  function makeCtx(inst) {
    var ctx = {
      el: inst.inner, root: inst.el, slide: inst.slide, index: inst.index, step: 0, dir: 0,
      data: global.DECK_DATA || {}, instant: false, prev: null,
      D: D, E: E, C: COLORS, gsap: gsap,
      get reduced() { return reduced(); },
      add: function (fn) { return inst.gctx.add(fn); },
      tl: function (vars) { return inst.gctx.add(function () { return gsap.timeline(vars); }); },
      settle: function () { settleCtx(inst.gctx, inst.tl); },
      count: function (target, from, to, opts) { return countUp(inst, target, from, to, opts); },
      katex: function (target) { renderMath(target || inst.inner); return target; },
      tex: tex,
      three: function (container, opts) { return makeThree(inst, container, opts); },
      raf: function (fn) {
        var L = { fn: fn, t: 0 }; inst.loops.push(L);
        return function () { var i = inst.loops.indexOf(L); if (i >= 0) inst.loops.splice(i, 1); };
      },
      timeout: function (fn, ms) { return inst.gctx.add(function () { return gsap.delayedCall((ms || 0) / 1000, function () { inst.gctx.add(fn); }); }); },
      interval: function (fn, ms) { var id = setInterval(function () { if (!inst.dead) inst.gctx.add(fn); }, ms); inst.cleanups.push(function () { clearInterval(id); }); return id; },
      on: function (target, type, fn, opts) {
        target.addEventListener(type, fn, opts);
        inst.listeners.push([target, type, fn, opts]);
        return function () { target.removeEventListener(type, fn, opts); };
      },
      cleanup: function (fn) { inst.cleanups.push(fn); },
      overlay: function () {
        if (inst.overlay) return inst.overlay;
        var svg = doc.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'slide-overlay'); svg.setAttribute('viewBox', '0 0 ' + STAGE_W + ' ' + STAGE_H);
        svg.setAttribute('width', STAGE_W); svg.setAttribute('height', STAGE_H);
        inst.el.appendChild(svg); inst.overlay = svg; return svg;
      },
      rect: stageRect,
      toStage: function (e) { var sr = dom.stage.getBoundingClientRect(), s = state.scale || 1; return { x: (e.clientX - sr.left) / s, y: (e.clientY - sr.top) / s }; },
      split: splitWords,
      rise: function (target, opts) { return inst.gctx.add(function () { return riseWords(target, opts); }); },
      reveal: function (target, kind, opts) { return inst.gctx.add(function () { return revealEl(target, kind, opts); }); },
      hud: {
        get el() { return dom.hud; },
        setTags: function (keys) { inst.tagOverride = keys; renderTags(inst, true); },
        rect: function (part) { return hudRect(part); },
        showProgress: function (on) { dom.hud.classList.toggle('hide-progress', !on); }
      },
      carrier: carrierAPI,
      rng: function (seed) { return mulberry32(seed == null ? 42 : seed); },
      fmt: fmt,
      $: function (sel) { return inst.inner.querySelector(sel); },
      $$: function (sel) { return $$(inst.inner, sel); }
    };
    return ctx;
  }

  function createInstance(index) {
    var slide = slides[index];
    var sec = doc.createElement('section');
    sec.className = 'slide'; sec.setAttribute('data-id', slide.id);
    sec.setAttribute('aria-label', slide.title || slide.id);
    var inner = el('div', 'slide-inner' + (slide.className ? ' ' + slide.className : ''), sec);
    var inst = {
      slide: slide, index: index, el: sec, inner: inner, step: 0, entered: false, dead: false,
      cleanups: [], listeners: [], loops: [], threes: [], frags: [], tl: null, tlTween: null,
      overlay: null, tagOverride: null
    };
    inst.gctx = gsap.context(function () {}, inner);
    inst.ctx = makeCtx(inst);
    return inst;
  }
  function call(inst, phase, fn) {
    try { return inst.gctx.add(fn); }
    catch (e) { pushError(inst.slide.id + ' ' + phase, e); return undefined; }
  }
  function mountInstance(inst) {
    var s = inst.slide;
    dom.slides.appendChild(inst.el);
    try {
      if (typeof s.html === 'string') inst.inner.innerHTML = preprocess(s.html);
      else if (typeof s.html === 'function') inst.inner.innerHTML = preprocess(s.html(inst.ctx) || '');
    } catch (e) { pushError(s.id + ' html', e); }
    if (s.math !== false) { try { renderMath(inst.inner); } catch (e) { pushError(s.id + ' math', e); } }
    if (s.build) call(inst, 'build', function () { s.build(inst.inner, inst.ctx); });
    if (s.ritual) {
      var g = el('div', 'ritual-ghost', null, pad2(s.section.num));
      inst.el.insertBefore(g, inst.inner); inst.ghost = g;
      inst.ghostRest = ghostRest(inst);
    }
    inst.frags = $$(inst.inner, '[data-step], [data-step-out]');
    inst.frags.forEach(function (f) { f.__vis = fragVisible(f, 0); if (!f.__vis) gsap.set(f, { autoAlpha: 0 }); });
    $$(inst.inner, '.hl').forEach(function (h) { h.style.setProperty('--hl-x', '0'); });
  }
  /* resting opacity of the ghost numeral after the ritual: 4 % on an empty right side, 0 when
     slide content (text, figures, cards — including fragments still hidden) reaches into its box,
     where it would show through translucent panels. slide.ghost true/false forces it. */
  var GHOST_REST = 0.04;
  function ghostRest(inst) {
    var g = inst.ghost, s = inst.slide;
    if (s.ghost === true) return GHOST_REST;
    if (s.ghost === false) return 0;
    try {
      var gr = g.getBoundingClientRect();
      var ix = gr.width * 0.08, iy = gr.height * 0.12;
      var G = { l: gr.left + ix, r: gr.right - ix, t: gr.top + iy, b: gr.bottom - iy };
      var area = Math.max(1, (G.r - G.l) * (G.b - G.t)), hit = 0;
      var all = inst.inner.querySelectorAll('*');
      for (var i = 0; i < all.length; i++) {
        var n = all[i];
        if (n instanceof global.SVGElement) {
          if (!/^(path|line|polyline|polygon|circle|ellipse|rect|text|image|foreignObject)$/.test(n.tagName)) continue;
          if (n.closest('defs, clipPath, mask, marker, pattern, symbol')) continue;
        } else {
          if (n.closest('.katex-mathml')) continue;
          var leaf = /^(IMG|CANVAS|VIDEO)$/.test(n.nodeName) || n.classList.contains('three-wrap');
          for (var c = n.firstChild; !leaf && c; c = c.nextSibling) if (c.nodeType === 3 && /\S/.test(c.nodeValue)) leaf = true;
          if (!leaf) {
            var cs = global.getComputedStyle(n);
            leaf = (cs.backgroundColor && !/^(transparent|rgba\(0, 0, 0, 0\))$/.test(cs.backgroundColor)) || cs.backgroundImage !== 'none' ||
              (parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none');
          }
          if (!leaf) continue;
        }
        var r = n.getBoundingClientRect();
        if (r.width < 1 || r.height < 1) continue;
        var w = Math.min(G.r, r.right) - Math.max(G.l, r.left), h = Math.min(G.b, r.bottom) - Math.max(G.t, r.top);
        if (w > 0 && h > 0) { hit += w * h; if (hit > area * 0.03) return 0; }
      }
    } catch (e) { pushError(s.id + ' ghost', e); }
    return GHOST_REST;
  }
  function destroyInstance(inst) {
    if (!inst || inst.dead) return;
    inst.dead = true;
    try { if (inst.slide.leave) inst.gctx.add(function () { inst.slide.leave(inst.inner, inst.ctx); }); } catch (e) { pushError(inst.slide.id + ' leave', e); }
    inst.cleanups.forEach(function (fn) { try { fn(); } catch (e) { pushError(inst.slide.id + ' cleanup', e); } });
    inst.cleanups.length = 0;
    try { inst.gctx.kill(); } catch (e) { pushError(inst.slide.id + ' kill', e); }
    if (inst.tl) { inst.tl.kill(); inst.tl = null; }
    inst.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
    inst.listeners.length = 0; inst.loops.length = 0;
    inst.threes.slice().forEach(function (T) { T.dispose(); });
    inst.threes.length = 0;
    var all = inst.el.querySelectorAll('*');
    if (all.length < 6000) gsap.killTweensOf(all); /* safety net for tweens made outside the context */
    if (inst.el.parentNode) inst.el.parentNode.removeChild(inst.el);
    inst.frags = null; inst.overlay = null;
    var di = dying.indexOf(inst); if (di >= 0) dying.splice(di, 1);
  }

  /* ------------------------------------------------------------ reveal helpers */
  function riseWords(target, opts) {
    opts = opts || {};
    var words = Array.isArray(target) ? target : splitWords(target);
    if (!Array.isArray(target)) gsap.set(target, { autoAlpha: 1 });
    if (reduced()) return gsap.fromTo(words, { opacity: 0, yPercent: 0 }, { opacity: 1, duration: 0.2, delay: opts.delay || 0 });
    return gsap.fromTo(words, { yPercent: opts.from != null ? opts.from : 115, opacity: 1 },
      { yPercent: 0, duration: opts.duration || 0.75, ease: opts.ease || E.type, stagger: opts.stagger != null ? opts.stagger : 0.08, delay: opts.delay || 0 });
  }
  function drawHl(scope, delay) {
    var hls = scope.classList && scope.classList.contains('hl') ? [scope] : $$(scope, '.hl');
    if (!hls.length) return null;
    if (reduced()) { hls.forEach(function (h) { h.style.setProperty('--hl-x', '1'); }); return null; }
    return gsap.fromTo(hls, { '--hl-x': 0 }, { '--hl-x': 1, duration: 0.5, ease: 'power2.inOut', delay: delay || 0, stagger: 0.1 });
  }
  function svgLen(node) { try { return node.getTotalLength ? node.getTotalLength() : 0; } catch (e) { return 0; } }
  function revealEl(target, kind, opts) {
    opts = opts || {};
    kind = kind || target.getAttribute('data-in') || 'rise';
    var tl = gsap.timeline({ delay: opts.delay || 0 });
    var stg = target.getAttribute('data-stagger');
    var items = stg != null ? Array.prototype.slice.call(target.children) : [target];
    var st = stg != null ? (+stg || 0.08) : 0;
    if (stg != null) tl.set(target, { autoAlpha: 1 }, 0);
    if (reduced()) {
      tl.fromTo(items, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, stagger: st ? 0.03 : 0 }, 0);
      $$(target, '.hl').forEach(function (h) { h.style.setProperty('--hl-x', '1'); });
      return tl;
    }
    switch (kind) {
      case 'words':
        tl.set(items, { autoAlpha: 1 }, 0);
        items.forEach(function (it, i) { tl.add(riseWords(it), i * Math.max(st, 0.12)); });
        break;
      case 'pop':
        tl.fromTo(items, { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: D.s, ease: E.stamp, stagger: st }, 0);
        break;
      case 'draw':
        tl.set(items, { autoAlpha: 1 }, 0);
        items.forEach(function (it, i) {
          var shapes = it.matches && it.matches('path,line,polyline,polygon,circle,rect,ellipse') ? [it] : $$(it, 'path,line,polyline,polygon,circle,rect,ellipse');
          shapes.forEach(function (sh) {
            var L = svgLen(sh); if (!L) return;
            tl.fromTo(sh, { strokeDasharray: L + ' ' + L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: D.m, ease: 'power2.inOut',
              onComplete: function () { sh.style.strokeDasharray = ''; sh.style.strokeDashoffset = ''; } }, i * st);
          });
        });
        break;
      case 'left': case 'right':
        tl.fromTo(items, { autoAlpha: 0, x: kind === 'left' ? -60 : 60 }, { autoAlpha: 1, x: 0, duration: D.m, ease: E.out, stagger: st }, 0);
        break;
      case 'fade':
        tl.fromTo(items, { autoAlpha: 0 }, { autoAlpha: 1, duration: D.s, stagger: st }, 0);
        break;
      case 'none':
        tl.set(items, { autoAlpha: 1 }, 0);
        break;
      default: /* rise */
        tl.fromTo(items, { autoAlpha: 0, y: 28 }, { autoAlpha: 1, y: 0, duration: D.m, ease: E.out, stagger: st }, 0);
    }
    var h = drawHl(target, 0); if (h) tl.add(h, Math.min(0.5, tl.duration()));
    return tl;
  }
  function fragVisible(f, target) {
    var a = f.getAttribute('data-step'), b = f.getAttribute('data-step-out');
    return (a == null || +a <= target) && (b == null || +b > target);
  }
  /* finish (then drop) the engine's own reveal/hide animation of a fragment, so a later state
     change never races a still-running one (a 0.6 s reveal would otherwise outlive a 0.35 s hide
     and leave the fragment on screen). Tweens a slide made on the element are left alone. */
  function stopFrag(f) {
    var a = f.__fragAnim;
    if (!a) return;
    f.__fragAnim = null;
    try { if (a.totalProgress() < 1) a.totalProgress(1); } catch (e) { pushError('fragment', e); }
    a.kill();
  }
  /* bring every data-step / data-step-out element to its state at build `target`.
     Called inside the slide's gsap context (runStep), so the reveal and hide tweens are
     recorded: a press during a reveal completes it first, and Deck.idle() waits for it. */
  function applyFragments(inst, target, animate) {
    if (!inst.frags) return;
    inst.frags.forEach(function (f) {
      var vis = fragVisible(f, target);
      if (vis === f.__vis) return;
      f.__vis = vis;
      stopFrag(f);
      if (vis) {
        if (animate) f.__fragAnim = revealEl(f);
        else {
          gsap.set(f, { autoAlpha: 1, y: 0, x: 0, scale: 1 });
          if (f.getAttribute('data-stagger') != null) gsap.set(f.children, { autoAlpha: 1, clearProps: 'transform' });
          if (f.__words) gsap.set(f.__words, { yPercent: 0, opacity: 1 });
          $$(f, '.hl').forEach(function (h) { h.style.setProperty('--hl-x', '1'); });
          if (f.classList.contains('hl')) f.style.setProperty('--hl-x', '1');
        }
      } else {
        if (animate && !reduced()) f.__fragAnim = gsap.to(f, { autoAlpha: 0, y: -16, duration: D.s, ease: E['in'], overwrite: 'auto' });
        else gsap.set(f, { autoAlpha: 0 });
      }
    });
  }
  function countUp(inst, target, from, to, opts) {
    opts = opts || {};
    var dec = opts.decimals != null ? opts.decimals : decimalsOf(to);
    var f = opts.format || function (v) { return (opts.prefix || '') + fmt(v, dec, opts) + (opts.suffix || ''); };
    var finalText = opts.final != null ? String(opts.final) : f(to);
    var digits = String(Math.round(Math.abs(to))).length;
    var dur = opts.duration != null ? opts.duration : Math.min(2.2, 1.1 + 0.11 * digits);
    var o = { v: from };
    return inst.gctx.add(function () {
      if (reduced() || inst.ctx.instant) {
        target.textContent = finalText;
        return gsap.delayedCall(0, function () { target.textContent = finalText; });
      }
      target.textContent = f(from);
      return gsap.to(o, { v: to, duration: dur, delay: opts.delay || 0, ease: opts.ease || 'power2.out',
        onUpdate: function () { target.textContent = f(o.v); },
        onComplete: function () { target.textContent = finalText; } });
    });
  }

  /* ------------------------------------------------------------ entry / exit / ritual */
  function isHead(n) { return n.matches && n.matches('.t-display, .t-h1, h1, [data-in="words"]'); }
  function collectEntry(inner) {
    var heads = [], blocks = [];
    function skip(n) {
      if (n.nodeType !== 1 || n.hasAttribute('data-step') || n.hasAttribute('data-step-out') || n.hasAttribute('data-shared') || n.getAttribute('data-in') === 'none' ||
        n.classList.contains('slide-overlay') || n.classList.contains('ritual-ghost') || /^(SCRIPT|STYLE)$/.test(n.nodeName)) return true;
      /* the builder already hid or animates it: leave it alone */
      if (n.style && (n.style.visibility === 'hidden' || n.style.opacity === '0' || n.style.display === 'none')) return true;
      if (gsap.getTweensOf(n).length) return true;
      return false;
    }
    function containsAnimated(n) { return !!n.querySelector('.t-display, .t-h1, h1, [data-in], [data-step], [data-shared]'); }
    function walk(parent) {
      Array.prototype.slice.call(parent.children).forEach(function (c) {
        if (skip(c)) return;
        if (isHead(c)) { heads.push(c); return; }
        if (c.hasAttribute('data-in')) { blocks.push(c); return; }
        if (containsAnimated(c) && !c.classList.contains('katex')) { walk(c); return; }
        blocks.push(c);
      });
    }
    walk(inner);
    return { heads: heads, blocks: blocks };
  }
  /* hidden by the builder (inline visibility on the block or an ancestor inside the slide)?
     The computed visibility cannot be used here: the whole new slide is still hidden while
     its entry timeline is built, so every block would look hidden and never rise. */
  function builderHidden(b, inst) {
    for (var n = b; n && n !== inst.el; n = n.parentNode) { if (n.style && n.style.visibility === 'hidden') return true; }
    return false;
  }
  function entryTimeline(inst, dir) {
    var tl = gsap.timeline();
    if (inst.slide.autoIn === false) return tl;
    var parts = collectEntry(inst.inner);
    if (reduced()) {
      parts.heads.concat(parts.blocks).forEach(function (b) {
        var op = +gsap.getProperty(b, 'opacity');
        if (!(op > 0) || builderHidden(b, inst)) return;
        tl.fromTo(b, { opacity: 0 }, { opacity: op, duration: 0.2 }, 0);
      });
      $$(inst.inner, '.hl').forEach(function (h) { if (!h.closest('[data-step]')) h.style.setProperty('--hl-x', '1'); });
      return tl;
    }
    var t = 0;
    parts.heads.forEach(function (h) {
      var words = splitWords(h);
      tl.fromTo(words, { yPercent: dir < 0 ? -115 : 115 }, { yPercent: 0, duration: 0.75, ease: E.type, stagger: 0.08 }, t);
      t += 0.12 + 0.05 * Math.min(words.length, 8);
    });
    if (parts.blocks.length) {
      parts.blocks.forEach(function (b, i) {
        var kind = b.getAttribute('data-in');
        if ((kind && kind !== 'rise') || b.hasAttribute('data-stagger')) { tl.add(revealEl(b, kind || 'rise'), 0.12 + i * 0.1); return; }
        /* rise back to the opacity the slide gave it (a dimmed block stays dimmed) */
        var op = +gsap.getProperty(b, 'opacity');
        if (!(op > 0) || builderHidden(b, inst)) return;
        tl.fromTo(b, { opacity: 0, y: 28 * (dir < 0 ? -1 : 1) }, { opacity: op, y: 0, duration: D.m, ease: E.out }, 0.12 + i * 0.1);
      });
    }
    var hls = $$(inst.inner, '.hl').filter(function (h) { return !h.closest('[data-step]'); });
    if (hls.length) tl.fromTo(hls, { '--hl-x': 0 }, { '--hl-x': 1, duration: 0.5, ease: 'power2.inOut', stagger: 0.1 }, Math.max(0.5, t));
    return tl;
  }
  /* keep (optional): the data-shared keys of the incoming slide. A shared element whose key the
     incoming slide does not have exits with the rest (otherwise it would stay on screen, fully
     visible, until the transition ends). Without keep every shared element is held back. */
  function exitItems(inner, keep) {
    var out = [];
    function held(n) { var k = n.getAttribute('data-shared'); return k != null && (!keep || !!keep[k]); }
    (function walk(parent) {
      Array.prototype.slice.call(parent.children).forEach(function (c) {
        if (held(c)) return;
        if ($$(c, '[data-shared]').some(held)) walk(c); else out.push(c);
      });
    })(inner);
    return out;
  }
  function exitTimeline(inst, dir, keep) {
    var tl = gsap.timeline();
    var items = exitItems(inst.inner, keep);
    var extra = [];
    if (inst.overlay) extra.push(inst.overlay);
    if (inst.ghost) extra.push(inst.ghost);
    if (reduced()) { tl.to(items.concat(extra), { autoAlpha: 0, duration: 0.2 }, 0); return tl; }
    tl.to(items, { y: -44 * (dir < 0 ? -1 : 1), autoAlpha: 0, duration: 0.45, ease: E['in'], stagger: Math.min(0.035, 0.18 / Math.max(1, items.length)) }, 0);
    if (extra.length) tl.to(extra, { autoAlpha: 0, duration: 0.35, ease: E['in'] }, 0);
    return tl;
  }
  function hudRect(part) {
    if (!dom.hud) return null;
    if (part === 'eyebrow') return stageRect(dom.eyebrow);
    if (part === 'name') return stageRect(dom.hudName);
    if (part === 'id') return stageRect(dom.hudId);
    if (part === 'progress') return stageRect(dom.progress);
    if (part === 'tags') return stageRect(dom.tags);
    var m = /^cell:(\d+)$/.exec(part || '');
    if (m && dom.cells[+m[1]]) return stageRect(dom.cells[+m[1]]);
    return null;
  }
  function ritualTimeline(inst) {
    var sec = inst.slide.section, tl = gsap.timeline();
    var title = el('div', 'ritual-title t-display', dom.ritual);
    title.textContent = sec.title;
    inst.ritualTitle = title;
    var words = splitWords(title);
    var ghost = inst.ghost;
    var num = pad2(sec.num);
    /* land position: the eyebrow name (text set now, invisible until landing) */
    dom.hudName.textContent = sec.title;
    gsap.set(dom.hudName, { opacity: 0 });
    gsap.set(dom.hudSep, { opacity: 1 });
    var nameR = stageRect(dom.hudName), titleR = stageRect(title);
    /* land exactly on the eyebrow: scale = eyebrow font size / display font size (read from CSS) */
    var ecs = global.getComputedStyle(dom.eyebrow), tcs = global.getComputedStyle(title);
    var efs = parseFloat(ecs.fontSize) || 20, elh = parseFloat(ecs.lineHeight) || 28;
    var tfs = parseFloat(tcs.fontSize) || 104, tlh = parseFloat(tcs.lineHeight) || 112;
    var k = efs / tfs;
    var dx = nameR.x - titleR.x, dy = nameR.y - titleR.y - (tlh * k - elh) / 2;
    if (ghost) tl.fromTo(ghost, { x: 420, opacity: 0 }, { x: 0, opacity: 0.16, duration: 0.7, ease: E.out }, 0);
    tl.fromTo(words, { yPercent: 115 }, { yPercent: 0, duration: 0.7, ease: E.type, stagger: 0.08 }, 0.15);
    var hold = 0.15 + 0.7 + 0.08 * (words.length - 1) + 0.45;   /* §1.9: ~0.9 s in, then a short hold */
    if (ghost) tl.to(ghost, { opacity: inst.ghostRest, duration: 0.6, ease: E.io }, hold);
    tl.to(title, { x: dx, y: dy, scale: k, duration: 0.6, ease: E.io }, hold);
    tl.to(title, { opacity: 0, duration: 0.15 }, hold + 0.48);
    tl.to(dom.hudName, { opacity: 1, duration: 0.15 }, hold + 0.48);
    if (dom.hudNum.textContent !== num) {
      if (global.ScrambleTextPlugin) tl.to(dom.hudNum, { duration: 0.6, scrambleText: { text: num, chars: '0123456789', speed: 0.6 } }, hold + 0.1);
      else tl.set(dom.hudNum, { textContent: num }, hold + 0.3);
    }
    tl.call(function () { if (title.parentNode) title.parentNode.removeChild(title); inst.ritualTitle = null; }, null, hold + 0.65);
    tl.contentAt = hold + 0.2;
    return tl;
  }

  /* ------------------------------------------------------------ HUD */
  function slideTags(inst) {
    if (inst.tagOverride) return inst.tagOverride;
    var t = inst.slide.tags;
    if (typeof t === 'function') { try { t = t(inst.step); } catch (e) { pushError(inst.slide.id + ' tags', e); t = null; } }
    return t || [];
  }
  function renderTags(inst, animate) {
    var keys = slideTags(inst), sig = JSON.stringify(keys);
    if (dom.tags.__sig === sig) return;
    dom.tags.__sig = sig;
    dom.tags.innerHTML = keys.map(tagHTML).join('');
    if (animate && !reduced() && keys.length) gsap.fromTo(dom.tags.children, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: D.s, ease: E.out, stagger: 0.06 });
  }
  function updateHUD(inst, animate, ritualRunning) {
    var s = inst.slide, sec = s.section;
    dom.hud.classList.toggle('hidden', s.hud === false);
    dom.hud.classList.toggle('hide-progress', s.progress === false);
    /* slide number (pairs with "digits + Enter"); the internal id is shown in the notes panel */
    dom.hudId.textContent = (s.index + 1) + ' / ' + slides.length;
    var num = pad2(sec.num);
    if (!ritualRunning) {
      if (dom.hudNum.textContent !== num) {
        if (animate && !reduced() && global.ScrambleTextPlugin && dom.hudNum.textContent) gsap.to(dom.hudNum, { duration: 0.6, scrambleText: { text: num, chars: '0123456789', speed: 0.6 } });
        else dom.hudNum.textContent = num;
      }
      if (dom.hudName.textContent !== sec.title) {
        dom.hudName.textContent = sec.title;
        if (animate && !reduced()) gsap.fromTo(dom.hudName, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: D.s, ease: E.out });
      }
      gsap.set([dom.hudName, dom.hudSep], { opacity: 1 });
    }
    sections.forEach(function (x) {
      var c = dom.cells && dom.cells[x.num]; if (!c) return;
      c.classList.toggle('past', x.num < sec.num);
      c.classList.toggle('current', x === sec);
      c.firstChild.style.width = x === sec ? ((s.indexInSection + 1) / sec.slides.length * 100).toFixed(1) + '%' : '0%';
    });
    renderTags(inst, animate);
    updateNotes();
  }
  /* notes: one paragraph per build step; the current one is marked (▶), bright, and kept in view */
  function renderNotesBody(body, inst) {
    var n = inst.slide.notes, arr = Array.isArray(n), paras = arr ? n : [n || '(노트 없음)'];
    body.innerHTML = paras.map(function (p, i) {
      var on = arr && i === inst.step;
      return '<p class="np' + (on ? ' on' : '') + (arr ? '' : ' single') + '">' + (on ? '▶ ' : '') + esc(p) + '</p>';
    }).join('');
    var on = body.querySelector('.np.on');
    if (on && body.clientHeight) {   /* scroll only the panel, never the page */
      var top = on.offsetTop - body.offsetTop, bottom = top + on.offsetHeight;
      if (top < body.scrollTop + 8 || bottom > body.scrollTop + body.clientHeight - 8) body.scrollTop = Math.max(0, top - 16);
    }
  }
  function updateNotes() {
    if (!dom.notes || !cur) return;
    var s = cur.slide, nxt = slides[cur.index + 1];
    dom.notes.querySelector('.nh-pos').textContent = (cur.index + 1) + ' / ' + slides.length + ' · ' + s.id + (s.time ? ' · ' + s.time + '초' : '');
    dom.notes.querySelector('.notes-title').textContent = s.title || s.id;
    dom.notes.querySelector('.notes-step').textContent = s.steps ? '단계 ' + cur.step + ' / ' + s.steps : '단계 없음';
    dom.notes.querySelector('.notes-steps').innerHTML = s.steps ? new Array(s.steps + 1).join('.').split('').map(function (_, i) { return '<i class="' + (i < cur.step ? 'on' : '') + '"></i>'; }).join('') : '';
    renderNotesBody(dom.notes.querySelector('.notes-body'), cur);
    var nextHTML;
    if (cur.step < s.steps) nextHTML = '다음: <b>단계 ' + (cur.step + 1) + ' / ' + s.steps + '</b>' + (nxt ? ' · 그다음 장: ' + esc(nxt.title || nxt.id) : '');
    else nextHTML = nxt ? '다음 장: <b>' + esc(nxt.title || nxt.id) + '</b>' : '마지막 장이에요';
    dom.notes.querySelector('.notes-next').innerHTML = nextHTML;
  }
  function tickTimer() {
    if (!dom.notes || !state.notes) return;
    var t = Math.floor((Date.now() - state.startTime) / 1000);
    dom.notes.querySelector('.nh-timer').textContent = pad2(Math.floor(t / 60)) + ':' + pad2(t % 60);
  }

  /* ------------------------------------------------------------ hash */
  function writeHash() {
    if (!cur || state.presenter) return;
    var h = '#' + cur.slide.id + (cur.step ? '/' + cur.step : '');
    if (global.location.hash === h) return;
    /* replaceState fires no hashchange, so only the fallback marks the hash as self-written
       (a stale mark would make a later Back to that hash look self-written and be ignored) */
    try { global.history.replaceState(null, '', h); state.writingHash = null; }
    catch (e) { state.writingHash = h; try { global.location.hash = h; } catch (e2) { state.writingHash = null; } }
  }
  function parseHash(h) {
    h = decodeURIComponent((h || '').replace(/^#/, ''));
    if (!h) return null;
    var parts = h.split('/'), key = parts[0], step = parts[1] != null && parts[1] !== '' ? Math.max(0, parseInt(parts[1], 10) || 0) : 0;
    for (var i = 0; i < slides.length; i++) if (slides[i].id === key) return { index: i, step: step };
    for (var j = 0; j < sections.length; j++) if (sections[j].id === key && sections[j].slides.length) return { index: sections[j].slides[0].index, step: step };
    if (/^\d+$/.test(key)) return { index: Math.max(0, Math.min(slides.length - 1, parseInt(key, 10) - 1)), step: step };
    return null;
  }

  /* ------------------------------------------------------------ navigation core */
  function finishTransition() {
    var tr = state.transition;
    if (!tr) return;
    state.transition = null;
    try { tr.totalProgress(1); } catch (e) { pushError('transition', e); }
    tr.kill();
    dying.slice().forEach(destroyInstance);
    if (cur && !cur.entered) enterInstance(cur, true);
    if (cur && cur.ritualTitle && cur.ritualTitle.parentNode) { cur.ritualTitle.parentNode.removeChild(cur.ritualTitle); cur.ritualTitle = null; }
    if (cur) gsap.set([dom.hudName, dom.hudSep], { opacity: 1 });
  }
  /* delay: seconds by which every animation started in enter() is shifted, so that it
     begins when the slide is revealed (after the old slide's exit and the ritual) */
  function enterInstance(inst, instant, delay) {
    if (inst.entered) return;
    inst.entered = true;
    var s = inst.slide;
    inst.ctx.instant = !!instant;
    var mark = inst.gctx.data.length;
    if (s.enter) {
      var r = call(inst, 'enter', function () { return s.enter(inst.inner, inst.ctx); });
      if (typeof r === 'function') inst.cleanups.push(r);
    }
    if (s.tl) {
      inst.tl = call(inst, 'tl', function () { return s.tl(inst.inner, inst.ctx); }) || null;
      if (inst.tl) {
        inst.tl.pause();
        var p0 = labelTime(inst, 0);
        if (instant || reduced()) inst.tl.seek(p0, false);
        else inst.tlTween = call(inst, 'tl', function () { return inst.tl.tweenFromTo(0, p0); });
      }
    }
    if (instant) settleCtx(inst.gctx, inst.tl);
    else if (reduced() && s.reducedAuto !== false) { settleCtx(inst.gctx, inst.tl); pauseLoops(inst.gctx); }
    else if (delay > 0) {
      for (var i = mark; i < inst.gctx.data.length; i++) {
        var a = inst.gctx.data[i];
        if (a instanceof gsap.core.Animation && topLevel(a) && !a.paused()) a.startTime(a.startTime() + delay);
      }
    }
    inst.ctx.instant = false;
    inst.threes.forEach(function (T) { T.render(); });
  }
  function labelTime(inst, k) {
    var tl = inst.tl; if (!tl) return 0;
    var name = 'step' + k;
    if (tl.labels && tl.labels[name] != null) return tl.labels[name];
    if (k === 0) return 0;
    if (k >= inst.slide.steps) return tl.duration();
    return tl.duration();
  }
  function runStep(inst, target, dir, instant) {
    var s = inst.slide;
    inst.ctx.step = target; inst.ctx.dir = dir; inst.ctx.instant = !!instant;
    call(inst, 'fragments', function () { applyFragments(inst, target, !instant && dir > 0); });
    if (inst.tl) {
      if (inst.tlTween) { inst.tlTween.kill(); inst.tlTween = null; }
      var to = labelTime(inst, target);
      if (instant || dir <= 0 || reduced()) inst.tl.seek(to, false);
      else inst.tlTween = call(inst, 'tl step', function () { return inst.tl.tweenFromTo(labelTime(inst, target - 1), to); });
    }
    if (s.step && (dir >= 0 || s.back === 'custom')) call(inst, 'step ' + target, function () { s.step(inst.inner, target, inst.ctx, dir); });
    if (instant) settleCtx(inst.gctx, inst.tl);
    else if (reduced() && s.reducedAuto !== false) { settleCtx(inst.gctx, inst.tl); pauseLoops(inst.gctx); }
    inst.ctx.instant = false;
    inst.step = target;
    inst.threes.forEach(function (T) { T.render(); });
  }
  function settleCurrent() {
    if (!cur) return false;
    if (state.transition) { finishTransition(); settleCtx(cur.gctx, cur.tl); return true; }
    if (ctxBusy(cur.gctx, cur.tl)) { settleCtx(cur.gctx, cur.tl); return true; }
    return false;
  }

  /* show slide `index` at build state `step`. opts: {dir, instant, animate} */
  function show(index, step, opts) {
    opts = opts || {};
    if (!slides.length) return;
    index = Math.max(0, Math.min(slides.length - 1, index | 0));
    var slide = slides[index];
    step = Math.max(0, Math.min(slide.steps, step | 0));
    if (state.transition) finishTransition();

    /* same slide: animated forward step, or rebuild-and-fast-forward */
    if (cur && cur.index === index) {
      if (step === cur.step) return;
      if (step === cur.step + 1 && !opts.instant) {
        if (ctxBusy(cur.gctx, cur.tl)) settleCtx(cur.gctx, cur.tl);
        runStep(cur, step, +1, false);
      } else if (step < cur.step && (cur.tl || slide.back === 'custom')) {
        if (ctxBusy(cur.gctx, cur.tl)) settleCtx(cur.gctx, cur.tl);
        if (slide.back === 'custom' && step === cur.step - 1) runStep(cur, step, -1, false);
        else runStep(cur, step, -1, true);
      } else {
        rebuild(index, step);
      }
      afterNav(false);
      return;
    }

    var old = cur;
    var dir = opts.dir != null ? opts.dir : (old && index < old.index ? -1 : 1);
    var inst = createInstance(index);
    /* capture the boxes of the old shared elements before anything moves */
    var sharedOld = {};
    if (old) $$(old.inner, '[data-shared]').forEach(function (n) { sharedOld[n.getAttribute('data-shared')] = { el: n, rect: stageRect(n) }; });
    inst.ctx.prev = old ? { id: old.slide.id, index: old.index, el: old.inner, rect: function (key) { return sharedOld[key] ? sharedOld[key].rect : null; } } : null;
    mountInstance(inst);
    if (carrier.visible && !slide.carrier) carrierAPI.hide();

    var ritual = !!slide.ritual && step === 0 && !opts.instant && !reduced() &&
      !(old && old.slide.section === slide.section && old.index > index);
    var instantBuild = step > 0 || !!opts.instant;

    if (old) { dying.push(old); }
    cur = inst;
    state.index = index;

    if (opts.instant || !old && instantBuild) {
      if (old) destroyInstance(old);
      updateHUD(inst, false);              /* before the steps, which may change the HUD */
      enterInstance(inst, true);
      for (var k = 1; k <= step; k++) runStep(inst, k, 0, true);
      markHighlights(inst, step);
      if (inst.ghost) gsap.set(inst.ghost, { opacity: inst.ghostRest });
      afterNav(true);
      return;
    }

    var tl = gsap.timeline({ onComplete: function () { if (state.transition === tl) finishTransition(); } });
    state.transition = tl;
    var tIn = old ? (reduced() ? 0.2 : 0.3) : 0;        /* the new slide appears */
    if (old) {
      var keepKeys = {};
      $$(inst.inner, '[data-shared]').forEach(function (n) { keepKeys[n.getAttribute('data-shared')] = 1; });
      tl.add(exitTimeline(old, dir, keepKeys), 0);
      gsap.set(inst.el, { autoAlpha: 0 });
      tl.set(inst.el, { autoAlpha: 1 }, tIn);
    }
    /* shared elements: the old copy stays until tIn, then the new copy flies from its box */
    $$(inst.inner, '[data-shared]').forEach(function (n) {
      var key = n.getAttribute('data-shared'), o = sharedOld[key];
      if (!o || n.getAttribute('data-shared-mode') === 'manual') return;
      var r = stageRect(n);
      tl.set(o.el, { visibility: 'hidden' }, tIn);
      if (reduced()) return;
      tl.fromTo(n, { x: o.rect.x - r.x, y: o.rect.y - r.y, scaleX: o.rect.w / Math.max(1, r.w), scaleY: o.rect.h / Math.max(1, r.h), transformOrigin: '0 0' },
        { x: 0, y: 0, scaleX: 1, scaleY: 1, duration: D.l, ease: E.io, immediateRender: true }, tIn);
    });
    var tContent = tIn;
    if (ritual) {
      updateHUD(inst, true, true);
      var rt = ritualTimeline(inst);
      tl.add(rt, tIn);
      tContent = tIn + rt.contentAt;
    } else {
      updateHUD(inst, true, false);
      if (inst.ghost) gsap.set(inst.ghost, { opacity: inst.ghostRest });
    }
    if (instantBuild) {
      enterInstance(inst, true);
      for (var j = 1; j <= step; j++) runStep(inst, j, 0, true);
      markHighlights(inst, step);
    } else {
      /* enter() runs now so the generic entry can skip what it animates; its
         animations are shifted to start when the content is revealed */
      enterInstance(inst, false, tContent);
    }
    tl.add(entryTimeline(inst, dir), tContent);
    afterNav(true);
  }
  function markHighlights(inst, step) {
    $$(inst.inner, '.hl').forEach(function (h) {
      var f = h.closest('[data-step]');
      if (!f || +f.getAttribute('data-step') <= step) h.style.setProperty('--hl-x', '1');
    });
  }
  function rebuild(index, step) {
    var old = cur;
    var inst = createInstance(index);
    mountInstance(inst);
    if (old && old.el.parentNode) dom.slides.insertBefore(inst.el, old.el.nextSibling);
    inst.ctx.prev = old ? old.ctx.prev : null;
    cur = inst;
    if (old) destroyInstance(old);
    updateHUD(inst, false);
    enterInstance(inst, true);
    for (var k = 1; k <= step; k++) runStep(inst, k, 0, true);
    if (inst.ghost) gsap.set(inst.ghost, { opacity: inst.ghostRest });
    markHighlights(inst, step);
    inst.threes.forEach(function (T) { T.render(); });
  }
  function afterNav() {
    if (!cur) return;
    renderTags(cur, true);
    updateNotes();
    writeHash();
    postSync();
    if (state.overview) renderOverview();
  }

  function next() {
    if (!cur) return;
    if (settleCurrent()) return;
    if (cur.step < cur.slide.steps) show(cur.index, cur.step + 1);
    else if (cur.index < slides.length - 1) show(cur.index + 1, 0, { dir: 1 });
  }
  function prev() {
    if (!cur) return;
    if (state.transition) finishTransition();
    if (cur.step > 0) show(cur.index, cur.step - 1, { dir: -1 });
    else if (cur.index > 0) show(cur.index - 1, slides[cur.index - 1].steps, { dir: -1 });
  }
  function nextSlide() { if (!cur) return; if (state.transition) finishTransition(); if (cur.index < slides.length - 1) show(cur.index + 1, 0, { dir: 1 }); }
  function prevSlide() { if (!cur) return; if (state.transition) finishTransition(); if (cur.index > 0) show(cur.index - 1, 0, { dir: -1 }); }

  /* ------------------------------------------------------------ overview / notes / misc */
  function renderOverview() {
    var h = '<div class="ov-help">O 또는 Esc로 닫기 · 카드를 누르면 그 장으로 가요</div>';
    sections.forEach(function (s) {
      h += '<h3>' + pad2(s.num) + '<b>' + esc(s.title) + '</b></h3><div class="ov-grid">';
      s.slides.forEach(function (sl) {
        var dots = ''; for (var i = 0; i < sl.steps; i++) dots += '<i></i>';
        h += '<button class="ov-card' + (cur && cur.index === sl.index ? ' current' : '') + '" data-index="' + sl.index + '">' +
          '<div class="ov-no">' + (sl.index + 1) + ' · ' + esc(sl.id) + '</div><div class="ov-title">' + esc(sl.title || sl.id) + '</div>' +
          '<div class="ov-steps">' + dots + '</div><div class="ov-ghost">' + pad2(s.num) + '</div></button>';
      });
      h += '</div>';
    });
    dom.overview.innerHTML = h;
  }
  function toggleOverview(on) {
    state.overview = on == null ? !state.overview : !!on;
    doc.body.classList.toggle('overview-open', state.overview);
    if (state.overview) {
      renderOverview();
      var c = dom.overview.querySelector('.ov-card.current');
      if (c) { c.focus({ preventScroll: true }); c.scrollIntoView({ block: 'center' }); }
    }
  }
  function toggleNotes(on) {
    state.notes = on == null ? !state.notes : !!on;
    doc.body.classList.toggle('notes-open', state.notes);
    layout(); updateNotes(); tickTimer();
  }
  function toggleHelp(on) { state.help = on == null ? !state.help : !!on; doc.body.classList.toggle('help-open', state.help); }
  function toast(msg) {
    dom.toast.textContent = msg; dom.toast.classList.add('on');
    clearTimeout(state.toastTimer);
    state.toastTimer = setTimeout(function () { dom.toast.classList.remove('on'); }, 1400);
  }
  function setReduced(v) {
    state.reducedUser = v == null ? null : !!v;
    toast(reduced() ? '움직임 줄이기: 켬' : '움직임 줄이기: 끔');
    if (cur) rebuild(cur.index, cur.step);
  }
  function fullscreen() {
    var d = doc.documentElement;
    try {
      if (!doc.fullscreenElement) { if (d.requestFullscreen) d.requestFullscreen(); }
      else if (doc.exitFullscreen) doc.exitFullscreen();
    } catch (e) { pushError('fullscreen', e); }
  }

  /* ------------------------------------------------------------ presenter window (P)
     The audience window keeps the stage only. P opens this same page with #presenter in a second
     window: notes (current step marked), what comes next, timer, and a live copy of the current
     slide. The two windows talk by postMessage, which also works from file:// (opaque origins,
     so messages are checked by their source window, never by origin). Keys pressed in the
     presenter window (→ ← Space PageDown PageUp ↓ ↑ Home End, digits+Enter, a clicker) drive the
     audience window. */
  var MSG = 'deck-presenter-v1';
  function presenterAlive() { return state.presenterWin && !state.presenterWin.closed; }
  function postSync() {
    if (state.presenter || !cur || !presenterAlive()) return;
    try { state.presenterWin.postMessage({ deck: MSG, type: 'sync', index: cur.index, step: cur.step, startTime: state.startTime }, '*'); }
    catch (e) { pushError('presenter sync', e); }
  }
  function openPresenter() {
    if (state.presenter) return;
    if (presenterAlive()) { try { state.presenterWin.focus(); } catch (e) { /* ignore */ } postSync(); return; }
    var url = global.location.href.split('#')[0] + '#presenter';
    var w = null;
    try { w = global.open(url, 'deck-presenter', 'popup=yes,width=1280,height=800'); } catch (e) { pushError('presenter open', e); }
    if (!w) { toast('발표자 창이 막혔어요 · 팝업을 허용해 주세요'); return; }
    state.presenterWin = w;
    toast('발표자 창을 열었어요');
  }
  /* commands shared by the keyboard, clicks, swipes and the presenter window */
  function runCmd(cmd, arg) {
    switch (cmd) {
      case 'next': next(); break;
      case 'prev': prev(); break;
      case 'nextSlide': nextSlide(); break;
      case 'prevSlide': prevSlide(); break;
      case 'first': show(0, 0, { dir: -1 }); break;
      case 'last': show(slides.length - 1, 0, { dir: 1 }); break;
      case 'goto': if (arg >= 0) show(arg, 0, { dir: cur && arg < cur.index ? -1 : 1 }); break;
    }
  }
  /* in the presenter window navigation is forwarded to the audience window (when it is there) */
  function nav(cmd, arg) {
    if (state.presenter && global.opener && !global.opener.closed) {
      try { global.opener.postMessage({ deck: MSG, type: 'cmd', cmd: cmd, arg: arg }, '*'); return; }
      catch (e) { pushError('presenter cmd', e); }
    }
    runCmd(cmd, arg);
  }
  function onMessage(e) {
    var d = e.data;
    if (!d || d.deck !== MSG) return;
    if (state.presenter) {
      if (e.source !== global.opener || d.type !== 'sync') return;
      state.lastSync = Date.now();
      if (d.startTime) state.startTime = d.startTime;
      if (!state.booted) { state.pendingGoto = [d.index, d.step]; return; }
      if (!cur || cur.index !== d.index || cur.step !== d.step) show(d.index, d.step, { instant: true });
      tickTimer();
      return;
    }
    if (d.type === 'hello') { state.presenterWin = e.source; postSync(); return; }   /* (re)connect, e.g. after a reload */
    if (d.type === 'cmd' && e.source && e.source === state.presenterWin) runCmd(d.cmd, d.arg);
  }
  function presenterHello() {
    if (!state.presenter || !global.opener || global.opener.closed) return;
    if (state.lastSync && Date.now() - state.lastSync < 4000) return;
    try { global.opener.postMessage({ deck: MSG, type: 'hello' }, '*'); } catch (e) { /* ignore */ }
  }

  /* ------------------------------------------------------------ input */
  function onKey(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target, k = e.key;
    /* text fields keep every key; a focused range slider keeps only its own arrows/Home/End,
       so PageDown (clicker), Space, N, O, Esc … still drive the deck */
    if (t && (t.isContentEditable || /^(TEXTAREA|SELECT)$/.test(t.nodeName) || (t.nodeName === 'INPUT' && t.type !== 'range'))) return;
    if (t && t.nodeName === 'INPUT' && t.type === 'range' && /^(Arrow(Left|Right|Up|Down)|Home|End)$/.test(k)) return;
    if (state.overview) {
      if (k === 'Escape' || k === 'o' || k === 'O') { toggleOverview(false); e.preventDefault(); }
      else if (k === 'Enter' && doc.activeElement && doc.activeElement.classList.contains('ov-card')) { doc.activeElement.click(); e.preventDefault(); }
      else if (/^Arrow/.test(k)) {
        var cards = $$(dom.overview, '.ov-card'), i = cards.indexOf(doc.activeElement);
        if (i < 0) i = cur ? cur.index : 0;
        var cols = Math.max(1, Math.round(dom.overview.querySelector('.ov-grid').clientWidth / 244));
        i += k === 'ArrowRight' ? 1 : k === 'ArrowLeft' ? -1 : k === 'ArrowDown' ? cols : -cols;
        i = Math.max(0, Math.min(cards.length - 1, i));
        cards[i].focus(); e.preventDefault();
      }
      return;
    }
    if (state.help && (k === 'Escape' || k === '?')) { toggleHelp(false); e.preventDefault(); return; }
    if (/^[0-9]$/.test(k)) {
      state.jumpBuf = (state.jumpBuf + k).slice(-3);
      dom.jump.textContent = '→ ' + state.jumpBuf + ' (Enter)'; dom.jump.classList.add('on');
      clearTimeout(state.jumpTimer);
      state.jumpTimer = setTimeout(function () { state.jumpBuf = ''; dom.jump.classList.remove('on'); }, 2500);
      e.preventDefault(); return;
    }
    switch (k) {
      case 'Enter':
        if (state.jumpBuf) {
          var n = parseInt(state.jumpBuf, 10); state.jumpBuf = ''; dom.jump.classList.remove('on');
          if (n >= 1) nav('goto', Math.min(slides.length, n) - 1);
          e.preventDefault();
        }
        break;
      case 'ArrowRight': case ' ': case 'PageDown': case 'Spacebar': nav('next'); e.preventDefault(); break;
      case 'ArrowLeft': case 'PageUp': case 'Backspace': nav('prev'); e.preventDefault(); break;
      case 'ArrowDown': nav('nextSlide'); e.preventDefault(); break;
      case 'ArrowUp': nav('prevSlide'); e.preventDefault(); break;
      case 'Home': nav('first'); e.preventDefault(); break;
      case 'End': nav('last'); e.preventDefault(); break;
      case 'n': case 'N': if (!state.presenter) toggleNotes(); e.preventDefault(); break;
      case 'p': case 'P': openPresenter(); e.preventDefault(); break;
      case 'o': case 'O': toggleOverview(); e.preventDefault(); break;
      case 'm': case 'M': setReduced(!reduced()); e.preventDefault(); break;
      case 'f': case 'F': fullscreen(); e.preventDefault(); break;
      case '?': case 'h': case 'H': toggleHelp(); e.preventDefault(); break;
      case 'Escape': if (state.notes && !state.presenter) toggleNotes(false); break;
    }
  }
  var INTERACTIVE = 'a, button, input, select, textarea, label, summary, [data-interactive], .no-advance, .dial.interactive';
  function onClick(e) {
    if (state.suppressClick) { state.suppressClick = false; return; }
    if (e.button !== 0) return;
    if (e.target.closest && e.target.closest(INTERACTIVE)) return;
    if (e.shiftKey) nav('prev'); else nav('next');
  }
  var touch = null;
  function onTouchStart(e) { if (e.touches.length === 1) touch = { x: e.touches[0].clientX, y: e.touches[0].clientY }; }
  function onTouchEnd(e) {
    if (!touch) return;
    var t = e.changedTouches[0], dx = t.clientX - touch.x, dy = t.clientY - touch.y; touch = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) { state.suppressClick = true; nav(dx < 0 ? 'next' : 'prev'); }
  }

  /* ------------------------------------------------------------ boot */
  function start() {
    if (state.started) return;
    state.started = true;
    buildChrome();
    global.addEventListener('message', onMessage);
    if (state.presenter) {
      /* presenter window: notes panel always open beside a live copy of the current slide */
      doc.body.classList.add('presenter', 'notes-open');
      state.notes = true;
      doc.title = '발표자 화면 · ' + doc.title;
      setInterval(presenterHello, 2000);
    }
    layout();
    global.addEventListener('resize', layout);
    /* range sliders: the deck listens in the capture phase, because a slide may stop keydown
       propagation on its slider; every other target uses the normal (bubbling) listener */
    var isRange = function (t) { return !!(t && t.nodeName === 'INPUT' && t.type === 'range'); };
    doc.addEventListener('keydown', function (e) { if (isRange(e.target)) onKey(e); }, true);
    doc.addEventListener('keydown', function (e) { if (!isRange(e.target)) onKey(e); });
    dom.stage.addEventListener('click', onClick);
    dom.stage.addEventListener('touchstart', onTouchStart, { passive: true });
    dom.stage.addEventListener('touchend', onTouchEnd);
    /* a slider dragged with the mouse hands the keyboard back to the deck, so → advances again */
    dom.stage.addEventListener('pointerup', function (e) {
      var t = e.target;
      if (t && t.nodeName === 'INPUT' && t.type === 'range') setTimeout(function () { if (doc.activeElement === t) t.blur(); }, 0);
    });
    dom.overview.addEventListener('click', function (e) {
      var c = e.target.closest('.ov-card'); if (!c) return;
      toggleOverview(false); nav('goto', +c.getAttribute('data-index'));
    });
    dom.help.addEventListener('click', function () { toggleHelp(false); });
    global.addEventListener('hashchange', function () {
      if (state.presenter) return;
      if (state.writingHash && state.writingHash === global.location.hash) { state.writingHash = null; return; }
      state.writingHash = null;
      var p = parseHash(global.location.hash); if (p) show(p.index, p.step, { instant: true });
    });
    if (mq) {
      var onMq = function () { state.reducedSys = mq.matches; if (state.reducedUser == null && cur) rebuild(cur.index, cur.step); };
      if (mq.addEventListener) mq.addEventListener('change', onMq); else if (mq.addListener) mq.addListener(onMq);
    }
    state.startTime = Date.now();
    setInterval(tickTimer, 1000);
    var go = function () {
      if (state.booted) return;
      state.booted = true;
      if (!slides.length) { pushError('boot', new Error('no slides registered')); return; }
      var p = state.presenter ? null : parseHash(global.location.hash);
      if (state.pendingGoto) { show(state.pendingGoto[0], state.pendingGoto[1], { instant: true }); state.pendingGoto = null; }
      else if (p) show(p.index, p.step, { instant: p.step > 0 });
      else show(0, 0, state.presenter ? { instant: true } : {});
      if (state.presenter) { presenterHello(); tickTimer(); }
    };
    /* wait for the fonts so split text and FLIP measure the final glyphs (max 2.5 s) */
    var fontsReady = doc.fonts && doc.fonts.ready ? doc.fonts.ready : null;
    if (doc.fonts && doc.fonts.load) {
      try { doc.fonts.load('700 64px "Pretendard Variable"', '가A1'); doc.fonts.load('500 28px "Pretendard Variable"', '가A1'); } catch (e) { /* ignore */ }
    }
    if (fontsReady) { var done = false; fontsReady.then(function () { if (!done) { done = true; go(); } }); setTimeout(function () { if (!done) { done = true; go(); } }, 2500); }
    else go();
  }

  /* ------------------------------------------------------------ public API */
  var Deck = {
    section: section,
    start: start,
    list: function () {
      return slides.map(function (s) { return { index: s.index, id: s.id, steps: s.steps, title: s.title || '', section: s.section.id }; });
    },
    goto: function (i, step, opts) {
      if (typeof i === 'string') { var p = parseHash('#' + i); if (!p) return false; i = p.index; if (step == null) step = p.step; }
      if (!state.booted) { state.pendingGoto = [i, step || 0]; return true; }
      show(i, step || 0, opts || {});
      return true;
    },
    next: next, prev: prev, nextSlide: nextSlide, prevSlide: prevSlide,
    current: function () { return cur ? { index: cur.index, id: cur.slide.id, step: cur.step, steps: cur.slide.steps } : null; },
    idle: function () {
      if (!state.booted || !cur) return false;
      if (state.transition) return false;
      if (ctxBusy(cur.gctx, cur.tl)) return false;
      if (ctxBusy(carrier.ctx)) return false;
      return true;
    },
    settle: function () { if (state.transition) finishTransition(); if (cur) settleCtx(cur.gctx, cur.tl); },
    setReduced: setReduced,
    get reduced() { return reduced(); },
    toggleNotes: toggleNotes, toggleOverview: toggleOverview, openPresenter: openPresenter,
    get presenter() { return state.presenter; },
    tex: tex, renderMath: renderMath, tagHTML: tagHTML,
    TAGS: TAGS, ICONS: ICONS, COLORS: COLORS, D: D, E: E, TEX_MACROS: TEX_MACROS,
    STAGE: { w: STAGE_W, h: STAGE_H },
    get scale() { return state.scale; },
    pixelRatio: pixelRatio,
    util: { rng: mulberry32, fmt: fmt, pad2: pad2, splitWords: splitWords, esc: esc, lambdaColor: lambdaColor, stageRect: stageRect, decimalsOf: decimalsOf },
    get sections() { return sections.map(function (s) { return { id: s.id, num: s.num, title: s.title, slides: s.slides.map(function (x) { return x.id; }) }; }); },
    _cur: function () { return cur; },
    _debug: function () { return { instances: allInstances().length, dying: dying.length, pool: rendererPool.length, slidesInDom: dom.slides ? dom.slides.children.length : 0, ritual: dom.ritual ? dom.ritual.children.length : 0 }; }
  };
  global.Deck = Deck;

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start);
  else setTimeout(start, 0);
})(window);
