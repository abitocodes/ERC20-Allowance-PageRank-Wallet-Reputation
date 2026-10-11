/* gallery-sections.js — demo slides for tools/gallery.html (developer reference, not the talk).
   Each slide shows one family of components from js/components.js and the engine features
   (fragments, steps, shared elements, timeline mode, KaTeX, three.js). Numbers shown here are
   either labelled 예시 or read from DECK_DATA exactly as stored. */
(function () {
  'use strict';
  var C = Deck.COLORS;

  /* ------------------------------------------------------------ g01: type, tags, counters */
  Deck.section({
    id: 's01-type', title: '글자·태그·숫자',
    slides: [{
      id: 'g01-type', title: '글자와 태그', time: 30,
      notes: ['진입: 제목이 낱말 단위로 떠올라요.', '단계 1: 큰 문장', '단계 2: 상태 태그', '단계 3: 카운터', '단계 4: 오도미터', '단계 5: 바꿔 쓰기·취소선·형광'],
      html:
        '<div class="title-block"><h1 class="t-h1">허락 화살표는 페이지랭크에 무엇을 [[더할까요?]]</h1>' +
        '<p class="sub">짧은 해요체 문장 · 강조어는 한 슬라이드에 하나</p></div>' +
        '<p class="t-body-l abs" style="left:96px;top:330px" data-step="1" data-in="words">점수를 받는 것은 지갑이 아니라 스마트 계약이에요.</p>' +
        '<div class="row abs" style="left:96px;top:430px" data-step="2" data-in="pop" data-stagger="0.08" id="tags"></div>' +
        '<div class="abs" style="left:96px;top:520px" data-step="3"><div class="t-stat num" id="cnt">0</div><div class="t-caption ink-2">ctx.count — 허락 기록(예시 표시용)</div></div>' +
        '<div class="abs" style="left:1000px;top:520px" data-step="4"><div class="t-stat num" id="odo">0</div><div class="t-caption ink-2">Comp.odometer</div></div>' +
        '<div class="abs t-body-l" style="left:96px;top:800px" data-step="5">허락은 <span id="sw">믿음</span>의 증거예요 · <span id="hl">보증으로 읽기</span></div>',
      steps: 5,
      build: function (el, ctx) {
        var t = el.querySelector('#tags');
        ['plan', 'registered', 'reanalysis', 'posthoc', 'exploratory', 'construct', 'registered-analysis', 'example'].forEach(function (k) { t.appendChild(Comp.tag(k)); });
      },
      step: function (el, i, ctx) {
        if (i === 3) ctx.count(el.querySelector('#cnt'), 0, 224954202, { final: '224,954,202' });
        if (i === 4) Comp.odometer(ctx, el.querySelector('#odo'), '1,149,168,538');
        if (i === 5) {
          var tl = ctx.tl();
          tl.add(Comp.strike(ctx, el.querySelector('#sw'), '보증'), 0.3);
          tl.add(Comp.hilite(ctx, el.querySelector('#hl')), 1.6);
        }
      },
      tags: function (step) { return step >= 2 ? ['example'] : []; }
    }, {
      id: 'g01-shared-a', title: '공유 요소 A', time: 10,
      notes: '다음 장으로 갈 때 카드가 날아가 자리를 잡아요(FLIP).',
      html: '<h1 class="t-h1">공유 요소 넘기기 (FLIP)</h1>' +
        '<div class="card abs" data-shared="card" style="left:96px;top:300px;width:420px;height:260px"><div class="t-h2">카드</div><p class="t-body ink-2">data-shared="card"</p></div>'
    }, {
      id: 'g01-shared-b', title: '공유 요소 B', time: 10,
      notes: '같은 data-shared 키를 가진 요소가 이전 자리에서 새 자리로 날아와요.',
      html: '<h1 class="t-h1">카드가 오른쪽으로 커져요</h1>' +
        '<div class="card abs" data-shared="card" style="left:900px;top:240px;width:880px;height:560px"><div class="t-h2">카드</div><p class="t-body ink-2">같은 키, 다른 상자</p></div>'
    }]
  });

  /* ------------------------------------------------------------ g02: glyphs */
  Deck.section({
    id: 's02-glyphs', title: '글리프 G1–G15',
    slides: [{
      id: 'g02-glyphs', title: '글리프', time: 40, steps: 9,
      notes: '1 화살표 그리기 · 2 동전 흐름 · 3 허락 거두기 · 4 세기 막대 · 5 도장 · 6 동결 핀 · 7 λ 다이얼 · 8 가짜 주소 농장 · 9 물 컵',
      html: '<h1 class="t-h1">글리프는 뜻마다 [[하나]]</h1><div id="stage" class="abs" style="left:96px;top:200px;width:1728px;height:780px"></div>',
      build: function (el, ctx) {
        var host = el.querySelector('#stage');
        var svg = Comp.svg(ctx, host, { w: 1728, h: 780 });
        var st = ctx.g = {};
        st.e1 = Comp.eoa(ctx, svg, { x: 60, y: 90, label: '주인 (EOA)' });
        st.c1 = Comp.contract(ctx, svg, { x: 460, y: 90, label: '스펜더 계약' });
        st.a1 = Comp.arrow(ctx, svg, { from: [60, 90], to: [460, 90], kind: 'allow', shorten: [20, 40], label: '1,000 USDC까지', hidden: true });
        st.e2 = Comp.eoa(ctx, svg, { x: 60, y: 260, label: '보낸 쪽' });
        st.c2 = Comp.contract(ctx, svg, { x: 460, y: 260, label: '받는 계약' });
        st.a2 = Comp.arrow(ctx, svg, { from: [60, 260], to: [460, 260], kind: 'xfer', shorten: [20, 40], hidden: true });
        st.e3 = Comp.contract(ctx, svg, { x: 60, y: 430, size: 48 });
        st.c3 = Comp.contract(ctx, svg, { x: 460, y: 430, size: 48 });
        st.a3 = Comp.arrow(ctx, svg, { from: [60, 430], to: [460, 430], kind: 'cpr', shorten: [36, 40], lambda: 0.5, hidden: true, label: 'λ = 0.5' });
        st.tally = Comp.tally(ctx, svg, { x: 40, y: 600, size: 48 });
        st.pin = Comp.pin(ctx, svg, { x: 760, y0: 80, y1: 520, label: '동결' });
        st.farm = Comp.farm(ctx, svg, { cx: 1050, cy: 300, n: 20, radius: 130 });
        st.cup = Comp.cup(ctx, svg, { x: 1500, y: 180, value: 0.25, max: 0.6, color: 'xfer' });
        st.stampHost = el.querySelector('#stage');
        st.stamp = Comp.stamp(ctx, st.stampHost, { ok: false, x: 1280, y: 560 });
        st.dial = Comp.dial(ctx, st.stampHost, { value: 1, size: 280, x: 820, y: 560, interactive: true });
      },
      step: function (el, i, ctx) {
        var st = ctx.g, tl = ctx.tl();
        if (i === 1) { tl.add(st.a1.draw(), 0); tl.add(st.a2.draw(), 0.3); tl.add(st.a3.draw(), 0.6); }
        if (i === 2) st.a1.setLabel('500 USDC까지');
        if (i === 3) tl.add(st.a1.cut());
        if (i === 4) tl.add(st.tally.add(7));
        if (i === 5) tl.add(st.stamp.slam());
        if (i === 6) tl.add(st.pin.drop());
        if (i === 7) { tl.add(st.dial.set(0.25)); tl.add(st.a3.setLambda(0.25), 0); tl.add(st.dial.arc(0, 0.25, 'hi'), 0.6); }
        if (i === 8) tl.add(st.farm.grow());
        if (i === 9) tl.add(st.cup.set(0.4706));
      },
      enter: function (el, ctx) {
        var st = ctx.g;
        [st.e1, st.c1, st.e2, st.c2, st.e3, st.c3].forEach(function (n, k) { n.pop({ delay: k * 0.06 }); });
      }
    }]
  });

  /* ------------------------------------------------------------ g02b: 2D canvas + back:'custom' */
  Deck.section({
    id: 's02-zcanvas', title: '캔버스 와플',
    slides: [{
      id: 'g02-canvas', title: '와플 (Comp.canvas, back:custom)', time: 20, steps: 2, back: 'custom',
      notes: '점 하나 = 100만 건(예시 계산). 단계 1: 허락 점, 단계 2: 송금 점. ←는 step(el, i, ctx, -1)로 되돌려요.',
      html: '<h1 class="t-h1">점 하나 = [[100만 건]]</h1><div id="cv" class="abs" style="left:96px;top:230px" data-in="none"></div>' +
        '<p class="abs t-caption ink-3" style="left:96px;top:930px">예시 · 224,954,202 → 225개, 1,149,168,538 → 1,149개 (100만으로 나눠 반올림)</p>',
      build: function (el, ctx) {
        var counts = [Math.round(224954202 / 1e6), Math.round(1149168538 / 1e6)];
        var cols = 60, gap = 26, r = 8;
        var g = ctx.g = { shown: [0, 0], counts: counts };
        function draw() {
          var K = g.K, c = K.g; K.clear();
          var i, n = 0;
          [[C.allow, g.shown[0]], [C.xfer, g.shown[1]]].forEach(function (pair, layer) {
            c.fillStyle = pair[0];
            for (i = 0; i < pair[1]; i++, n++) {
              var x = (n % cols) * gap + r, y = Math.floor(n / cols) * gap + r + layer * 20;
              c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
            }
          });
        }
        g.draw = draw;
        g.K = Comp.canvas(ctx, el.querySelector('#cv'), { w: cols * gap, h: 640, onResize: function () { if (g.draw) g.draw(); } });
        draw();
      },
      step: function (el, i, ctx, dir) {
        var g = ctx.g, st = { a: g.shown[0], b: g.shown[1] };
        var ta = i >= 1 ? g.counts[0] : 0, tb = i >= 2 ? g.counts[1] : 0;
        if (dir < 0) { g.shown = [ta, tb]; g.draw(); return; }
        ctx.gsap.to(st, { a: ta, b: tb, duration: 1.4, ease: 'power1.inOut', onUpdate: function () { g.shown = [Math.round(st.a), Math.round(st.b)]; g.draw(); } });
      },
      tags: ['calc']
    }]
  });

  /* ------------------------------------------------------------ g03: small world + derivation */
  var WE = (window.DECK_DATA.params || {}).worked_example || {};
  Deck.section({
    id: 's03-world', title: '작은 세계와 수식',
    slides: [{
      id: 'g03-world', title: '작은 세계 + 유도 판', time: 60, steps: 8, carrier: false,
      notes: '1 세계 그리기 · 2 기호 카드와 지시선 · 3–5 유도 줄 · 6 걷는 사람 · 7 물 컵을 정상 상태로 · 8 식의 조각 짚기',
      html: '<h1 class="t-h1">점 4개, 허락 화살표 4개로 [[시작]]해요</h1>' +
        '<div class="layout-derive"><div class="fig" id="fig"></div><div class="eq" id="eq"></div></div>' +
        '<div class="abs eq-hero" id="hero" style="left:96px;top:880px;width:1728px" data-step="8" data-in="fade"></div>',
      build: function (el, ctx) {
        var g = ctx.g = {};
        g.world = Comp.smallWorld(ctx, el.querySelector('#fig'), { x: 0, y: 40, cups: { dy: 96, max: 0.6, decimals: 4 }, hidden: true });
        g.card = Comp.symbolCard(ctx, el.querySelector('#fig'), { tex: 'o(u)', desc: 'u에서 나가는 무게의 합 · A: 2 + 1 = 3', x: 560, y: 560 });
        g.derive = Comp.derive(ctx, el.querySelector('#eq'), { head: '유도', lines: [
          { tex: 'P_{u,v}=\\dfrac{w(u,v)}{o(u)}', note: '무게를 나가는 무게의 합으로 나눠요' },
          { tex: 'r_v=\\part{sum}{\\sum_{u\\to v}} r_u\\,P_{u,v}', note: '내 몫 = 나를 가리키는 점들이 나눠 주는 몫의 합', mark: 'sum' },
          { tex: '\\mathbf r^{(t+1)}=\\part{tele}{(1-d)\\,\\boldsymbol\\pi}+\\ca{d\\,P^{\\top}\\mathbf r^{(t)}}+d\\,(\\mathbf r^{(t)\\top}\\mathbf 1_{\\mathrm{dang}})\\,\\boldsymbol\\pi', note: '논문 식 pagerank', mark: 'tele' }
        ] });
        g.hero = Comp.formula(ctx, el.querySelector('#hero'), '\\mathbf r=\\part{a}{(1-d)\\boldsymbol\\pi}+\\part{b}{d\\,P^{\\top}\\mathbf r}+\\part{c}{d\\,(\\mathbf r^{\\top}\\mathbf 1_{\\mathrm{dang}})\\,\\boldsymbol\\pi}');
      },
      enter: function (el, ctx) { ctx.g.world.drawIn(); ctx.g.world.setCups([0.25, 0.25, 0.25, 0.25], { duration: 0.8, delay: 1.2 }); },
      step: function (el, i, ctx) {
        var g = ctx.g;
        if (i === 1) g.world.edges.forEach(function (A, k) { A.setWidth(2 + 2.2 * A.w * 1.2, { duration: 0.4 }); void k; });
        if (i === 2) { var tl = ctx.tl(); tl.add(g.card.pop()); tl.add(Comp.leader(ctx, g.card.el, g.world.node('A').g, { color: 'ink2' }).draw(), 0.2); }
        if (i >= 3 && i <= 5) g.derive.show(i - 2);
        if (i === 6) { g.world.walker.place('A'); g.world.walker.walk(6, { seed: 7, d: 0.85, duration: 0.45 }); }
        if (i === 7) g.world.setCups(WE.stationary || [0.1375, 0.2154, 0.1765, 0.4706], { duration: 1 });
        if (i === 8) { var t2 = ctx.tl(); t2.add(g.hero.mark('a'), 0.3); t2.add(g.hero.dim(['b']), 1.0); t2.add(g.hero.undim(), 1.8); }
      },
      tags: ['thesis-example']
    }]
  });

  /* ------------------------------------------------------------ g04: forest plot + time axis */
  var R = window.DECK_DATA.results || {}, TLD = window.DECK_DATA.timeline || {};
  Deck.section({
    id: 's04-charts', title: '차트',
    slides: [{
      id: 'g04-forest', title: '구간 막대 (G9)', time: 40, steps: 5,
      notes: 'λ 다섯 값의 같은 기간 송금 가족 τ와 95% 구간 (results.lambda_sweep.revised.same_window.transfer).',
      html: '<h1 class="t-h1">λ마다 송금 지표 가족과의 τ</h1><div id="fp" class="abs" style="left:96px;top:230px"></div>' +
        '<p class="abs t-caption ink-3" style="left:96px;top:880px">값은 DECK_DATA.results.lambda_sweep.revised에서 그대로 · 소수 셋째 자리</p>',
      build: function (el, ctx) {
        var sw = ((R.lambda_sweep || {}).revised || {}).same_window || {};
        var rows = (sw.transfer || []).map(function (v, k) {
          return { label: 'C-PR λ = ' + [0, 0.25, 0.5, 0.75, 1][k], est: v[0], lo: v[1], hi: v[2], color: Deck.util.lambdaColor([0, 0.25, 0.5, 0.75, 1][k]) };
        });
        ctx.g = { F: Comp.forest(ctx, el.querySelector('#fp'), { w: 1700, rows: rows, domain: [0, 0.8], rowH: 104, hidden: true, axisLabel: '켄달의 타우 (τ_b)' }) };
      },
      step: function (el, i, ctx) { ctx.g.F.show(i - 1); },
      tags: ['construct']
    }, {
      id: 'g04-time', title: '시간 축 (G12 동결 핀)', time: 40, steps: 3,
      notes: '달마다 ego 허락·송금 건수(띠마다 따로 맞춤), t1과 T_obs 동결 핀, W0·W1 라벨 기간.',
      html: '<h1 class="t-h1">[[3년]]의 기록, 두 번의 시험</h1><div id="tl" class="abs" style="left:96px;top:250px"></div>',
      build: function (el, ctx) {
        var mc = (TLD.monthly_counts || {}).revised || {};
        var T = Comp.timeline(ctx, el.querySelector('#tl'), { w: 1728, h: 640, axisY: 560 });
        var g = ctx.g = { T: T };
        g.sA = T.stream((mc.approval_ego || []).map(function (r) { return r[1]; }), { color: 'allow', height: 220, base: 300 });
        g.sT = T.stream((mc.transfer_ego || []).map(function (r) { return r[1]; }), { color: 'xfer', height: 220, base: 550 });
        g.p1 = T.pin('2026-03-31', { label: 't₁', y0: 40 });
        g.p2 = T.pin('2026-06-30', { label: 'T_obs', y0: 40 });
        g.b0 = T.band('2026-04-01', '2026-07-01', { label: 'W0', y0: 60 });
        g.b1 = T.band('2026-07-01', '2026-10-01', { label: 'W1', y0: 60 });
      },
      enter: function (el, ctx) { var tl = ctx.tl(); tl.add(ctx.g.T.drawAxis()); tl.add(ctx.g.sA.reveal({ duration: 1.6 }), 0.2); tl.add(ctx.g.sT.reveal({ duration: 1.6 }), 0.2); },
      step: function (el, i, ctx) {
        var g = ctx.g, tl = ctx.tl();
        if (i === 1) { tl.add(g.p1.drop()); tl.add(g.b0.show(), 0.4); }
        if (i === 2) { tl.add(g.p2.drop()); tl.add(g.b1.show(), 0.4); }
        if (i === 3) tl.add(Comp.leader(ctx, g.p2.head, el.querySelector('h1'), { color: 'ink3', dashed: true }).draw());
      }
    }]
  });

  /* ------------------------------------------------------------ g05: three.js point cloud */
  Deck.section({
    id: 's05-cloud', title: '3D 점구름',
    slides: [{
      id: 'g05-cloud', title: '15,107개 계약, λ에 따라', time: 70, steps: 5,
      notes: '단계마다 λ = 0, .25, .5, .75, 1. 점은 x 순서대로 물결치며 이동. 끌어서 돌리고 휠로 확대.',
      html: '<h1 class="t-h1">λ를 돌리면 [[어느 쪽 수]]를 따라가는지가 바뀌어요</h1>' +
        '<div id="three" class="abs" style="left:0;top:150px;width:1920px;height:860px" data-in="none"></div>' +
        '<div id="dial" class="abs" style="left:96px;top:200px" data-in="none"></div>' +
        '<p class="abs t-caption ink-3" style="left:96px;top:960px">점 하나 = 계약 하나 · 가로 허락한 주인 수(로그) · 깊이 송금 보낸 주소 수(로그) · 높이 C-PR 백분위 · 0점은 바닥판</p>',
      build: function (el, ctx) {
        var K = Comp.data.contracts(); if (!K) return;
        var n = K.n, keys = Comp.data.lambdaKeys, lams = Comp.data.lambdas;
        var xa = new Float32Array(n), zt = new Float32Array(n), mx = 0, mz = 0;
        for (var i = 0; i < n; i++) {
          xa[i] = Math.log10(1 + K.raw.in_approve_degree[i]); zt[i] = Math.log10(1 + K.raw.in_degree[i]);
          if (xa[i] > mx) mx = xa[i]; if (zt[i] > mz) mz = zt[i];
        }
        var SX = 7 / mx, SZ = 7 / mz, HY = 4.2;
        var sets = keys.map(function (k, j) {
          var p = new Float32Array(n * 3), col = new Float32Array(n * 3), lc = Comp.rgb(Deck.util.lambdaColor(lams[j]));
          for (var i2 = 0; i2 < n; i2++) {
            var f = K.flags[i2], zero = lams[j] === 1 ? (f & 1) : lams[j] === 0 ? (f & 2) : f === 3;
            var y = zero ? -0.25 : K.pct[k][i2] * HY;
            p[i2 * 3] = xa[i2] * SX - 3.5; p[i2 * 3 + 1] = y; p[i2 * 3 + 2] = zt[i2] * SZ - 3.5;
            var b = zero ? 0.25 : 0.35 + 0.65 * K.pct[k][i2];
            col[i2 * 3] = lc[0] * b; col[i2 * 3 + 1] = lc[1] * b; col[i2 * 3 + 2] = lc[2] * b;
          }
          return { p: p, c: col };
        });
        var delays = new Float32Array(n);
        for (var i3 = 0; i3 < n; i3++) delays[i3] = xa[i3] / mx;
        var T = ctx.three(el.querySelector('#three'), { fov: 32, camera: { theta: 0.78, phi: 1.12, radius: 19, target: [0, 1.4, 0] }, autoRotate: 0.05 });
        Comp.floor(ctx, T, { size: 8, y: -0.3, divisions: 8 });
        Comp.axes3d(ctx, T, { origin: [-3.5, -0.3, -3.5], length: [7.6, 4.8, 7.6], colors: [C.allow, C.cpr, C.xfer], labels: ['허락한 주인 수', 'C-PR 백분위', '송금 보낸 주소 수'] });
        var cloud = Comp.cloud(ctx, T, { positions: sets[4].p, colors: sets[4].c, size: 3, opacity: 0.6 });
        var dial = Comp.dial(ctx, el.querySelector('#dial'), { value: 1, size: 280 });
        ctx.g = { T: T, cloud: cloud, sets: sets, delays: delays, dial: dial };
      },
      enter: function (el, ctx) {
        var g = ctx.g; if (!g) return;
        g.T.cameraTo({ radius: 14.5 }, { duration: 1.8 });
      },
      step: function (el, i, ctx) {
        var g = ctx.g; if (!g) return;
        var j = [0, 1, 2, 3, 4][i - 1] === undefined ? 4 : [0, 1, 2, 3, 4][i - 1];
        var lam = Comp.data.lambdas[j];
        g.cloud.morph(g.sets[j].p, { duration: 1.4, delays: g.delays, spread: 0.6 });
        g.cloud.recolor(g.sets[j].c, { duration: 1.0 });
        g.dial.set(lam);
        if (i === 1) g.T.cameraTo({ theta: 0.15 }, { duration: 1.8 });
        if (i === 5) g.T.cameraTo({ theta: 1.35 }, { duration: 1.8 });
      },
      tags: ['construct']
    }]
  });

  /* ------------------------------------------------------------ g06: timeline mode */
  Deck.section({
    id: 's06-tlmode', title: '타임라인 모드',
    slides: [{
      id: 'g06-tl', title: 'tl(el, ctx) 라벨 step0..3', time: 20, steps: 3,
      notes: '앞으로는 라벨 사이를 재생하고, 뒤로는 라벨로 바로 가요.',
      html: '<h1 class="t-h1">라벨로 단계 나누기</h1>' +
        '<div class="abs" style="left:96px;top:320px;display:flex;gap:48px">' +
        '<div class="card t-h2 box" data-in="none">하나</div><div class="card t-h2 box" data-in="none">둘</div><div class="card t-h2 box" data-in="none">셋</div></div>',
      tl: function (el, ctx) {
        var b = el.querySelectorAll('.box'), tl = gsap.timeline();
        tl.from(b, { autoAlpha: 0, y: 40, duration: 0.5, stagger: 0.1 }).addLabel('step0');
        tl.to(b[0], { backgroundColor: C.allow, color: C.bg, duration: 0.4 }).addLabel('step1');
        tl.to(b[1], { backgroundColor: C.xfer, color: C.bg, duration: 0.4 }).addLabel('step2');
        tl.to(b[2], { backgroundColor: C.cpr, color: C.bg, y: -30, duration: 0.5, ease: 'back.out(1.6)' }).addLabel('step3');
        return tl;
      }
    }]
  });
})();
