/* =========================================================================
   s11-closing — 정리 (STORYBOARD.md §2, s11-01 … s11-05)

   s11-01  연구 질문에 대한 답   five RQ cards (RQ order of 22 October 2026: RQ1 the two single-edge
                                 walks, RQ2 cost, RQ3 holdout and counts, RQ4 rule A, RQ5 rule B); on
                                 entry the representative pictures of the talk fly back in as dim
                                 thumbnails (rank scatter of the real 6,483 contracts, race bars with
                                 C-PR, interval bars, one verdict stamp each for A and B); each click
                                 brings one card forward with its answer and status; then the
                                 out-of-both-edges line and the five objective chips
   s11-02  새로 보탠 다섯 가지   bento of five tiles, C-PR first (G13 dial + stamp in the large tile),
                                 then EndorseRank (G1), the counts (G8), the closed form and a waffle
                                 of the W1 traders
   s11-03  한계                  eight lines with icons, four per click
   s11-04  지갑 창과 다음 일     the brandless wallet window of s01-01 opens again (DeckParts.wallet; 46 px
                                 lower than in s01-01 so it clears the title), now with "주인 주소 N개"
                                 (owners are addresses, not people); the cursor rests on 허락 without
                                 pressing; two lines; four next steps, the first tagged 가설
   s11-05  감사합니다            the small world as a constellation; the allowance arrow underlines
                                 the thanks; then everything stops for the questions

   Numbers and sources (R = revised digest, revised-usd-12m = the thesis's main analysis)
     τ 0.199 [0.181, 0.221]                    R§3 inter_method.endorserank_vs_awp
     0.560 (EndorseRank × allowance), 0.736 (AWP × transfer)        R§2 families
     time 3.21, edges 2.21, iterations 94 / 57, C-PR 1.36 × AWP      R§10 benchmark (main, derived)
     W1 contrasts in the RQ3 thumbnail: AWP − transfer in-degree −0.041 [−0.047, −0.034],
       EndorseRank − in-approve degree −0.082 [−0.090, −0.073]       R§7 (after the labels)
     P (W1) +0.141, 97.5 % [0.026, 0.256]: R1 met (re-analysis)      R§7 neutral_w1.grid.P
     objectives O1–O5: thesis Ch. 5, Table objectives-achievement (Outcome column)
     70 / 87 traders (W1 / W0)                 R§7 neutral_w1.n / neutral_w0.n
     next steps: thesis Ch. 6, future work ("N": a placeholder, no contract is meant;
       "2026년 10–12월": the example window of the registered test); the contract-risk labels
       of the fourth card are the deck's own suggestion
     repository: thesis Ch. 3, Reproducibility; digest folder: thesis App. (revised-usd-12m)
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
  var TAU = pick(RV, ['same_window', 'inter_method', 'endorserank_vs_awp'], [0.19948, 0.1809, 0.2211]);
  var FAM = pick(RV, ['same_window', 'families'], {});
  var F_ER_A = pick(FAM, ['endorserank', 'allowance', 0], 0.5598), F_ER_T = pick(FAM, ['endorserank', 'transfer', 0], 0.19649);
  var F_AWP_T = pick(FAM, ['awp', 'transfer', 0], 0.7358), F_AWP_A = pick(FAM, ['awp', 'allowance', 0], 0.2263);
  var BM = pick(DATA, ['benchmark', 'revised', 'main'], {});
  var T_ER = pick(BM, ['endorserank', 'mean_s'], 2.6569), T_AWP = pick(BM, ['awp', 'mean_s'], 8.5296);
  var T_CPR = pick(BM, ['cpr_l50', 'mean_s'], 11.5635);
  var IT_ER = pick(BM, ['endorserank', 'iterations'], 57), IT_AWP = pick(BM, ['awp', 'iterations'], 94);
  var R_TIME = pick(DATA, ['benchmark', 'revised', 'derived', 'time_ratio_awp_over_er'], 3.2104);
  var R_EDGE = pick(DATA, ['benchmark', 'revised', 'derived', 'edge_ratio_awp_over_er'], 2.2122);
  /* the time ratio = the ratio of iterations × the ratio of the time per iteration (thesis Ch. 4: 1.65 × 1.95) */
  var R_ITER = IT_AWP / IT_ER, R_PER_IT = (T_AWP / IT_AWP) / (T_ER / IT_ER), R_CPR_AWP = T_CPR / T_AWP;
  var W1C_AWP = pick(RV, ['w1', 'endorserank_results', 'awp_minus_degree_send', 'd'], [-0.0409, -0.04729, -0.03445]);
  var W1C_ER = pick(RV, ['w1', 'endorserank_results', 'endorserank_minus_degree_appr', 'd'], [-0.08169, -0.09001, -0.07284]);
  var N_W1 = pick(RV, ['w1', 'neutral_w1', 'n'], 70), N_W0 = pick(RV, ['w1', 'neutral_w0', 'n'], 87);
  /* R1: P = in-approve degree − transfer in-degree on the W1 traders' liquidation-free close rate
     (Bonferroni 97.5 % interval d975) */
  var P_W1 = pick(RV, ['w1', 'neutral_w1', 'grid', 'P', 'liquidation_free_rate'], { d: [0.1413, 0.03688, 0.24], d975: [0.02599, 0.2559] });
  var P_W1_D = P_W1.d || [0.1413], P_W1_CI = P_W1.d975 || [0.02599, 0.2559];

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
    { k: 'RQ1', q: '한 화살표만 걷는 두 점수는?', a: '순서가 다르고 각자 자기 지표와', sb: 'τ = ' + fmt(TAU[0], 3) + ' (0도 1도 아니에요)<br>엔도스랭크 × 허락 <b>' + fmt(F_ER_A, 3) + '</b> · AWP × 송금 <b>' + fmt(F_AWP_T, 3) + '</b>', tags: [plainPill('만든 방식 때문에 대체로 저절로')] },
    { k: 'RQ2', q: '얼마나 걸릴까?', a: '시간은 그래프 크기와 반복 수를 따라가요', sb: '시간 <b>' + fmt(R_TIME, 2) + '배</b> · 화살표 <b>' + fmt(R_EDGE, 2) + '배</b><br>반복 <b>' + fmt(R_ITER, 2) + '배</b> × 한 번 <b>' + fmt(R_PER_IT, 2) + '배</b><br>두 화살표를 함께 걷는 C-PR이 가장 느려요', tags: [] },
    { k: 'RQ3', q: '나중 일을 맞힐까? 센 수보다 나을까?', a: '모든 점수가 맞혀요', sb: '하지만 <span class="em" id="em4">센 수를 넘은 페이지랭크는 없어요</span> · AWP는 송금 입차수에, 엔도스랭크는 받은 허락 수에 져요 · C-PR도 마찬가지', tags: [Deck.tagHTML('posthoc')] },
    { k: 'RQ4', q: 'C-PR은 한 층만 걷기보다 나을까?', a: '아니요 — 규칙 A 미충족', sb: '허락 층보다 못하지 않지만<br>새 송금자에서 송금 층보다 뒤져요<br>등록 분석도 같아요', tags: [Deck.tagHTML('reanalysis')] },
    { k: 'RQ5', q: '송금 걷기에 허락을 더하면?', a: '아니요 — 규칙 B 미충족', sb: '새 허락 쌍은 나아지고 새 송금자는 허용 폭보다 더 뒤져요<br>사후: 엔도스랭크보다는 두 스펜더 라벨 모두에서 위', tags: [Deck.tagHTML('reanalysis'), Deck.tagHTML('posthoc')] }
  ];
  var OCH = [
    { cls: '', html: '<b>O1</b>충족' }, { cls: '', html: '<b>O2</b>충족' },
    { cls: 'part', html: '<b>O3 일부 충족</b>예측은 충족,<br>센 수를 넘은 걷기는 없음' },
    { cls: 'fail', html: '<b>O4 미충족</b>규칙 A, 등록 분석에서도' },
    { cls: 'fail', html: '<b>O5 미충족</b>규칙 B, 등록 분석에서도' }
  ];
  var slide1 = {
    id: 's11-01', title: '연구 질문에 대한 답', time: 40, steps: 7,
    notes: [
      '다섯 질문에 답해 볼게요. 지금까지 본 대표 그림들이 작은 타일로 돌아왔어요. 각 질문에는 같은 번호의 목표가 하나씩 짝지어져 있어요.',
      '첫째, 한 화살표만 걷는 엔도스랭크와 AWP는 계약을 다른 순서로 세워요. 켄달의 타우가 ' + fmt(TAU[0], 3) + '로, 0도 1도 아니에요. 그리고 각자 자기 화살표로 만든 지표와 가장 잘 맞아요. 엔도스랭크는 허락 지표와 ' + fmt(F_ER_A, 3) + ', AWP는 송금 지표와 ' + fmt(F_AWP_T, 3) + '이에요. 둘 다 만든 방식 때문에 어느 정도 저절로 나오는 결과예요.',
      '둘째, 계산 시간은 그래프 크기와, 답이 자리 잡을 때까지 되풀이하는 반복 수를 함께 따라가요. AWP는 엔도스랭크보다 시간이 ' + fmt(R_TIME, 2) + '배 걸리고, 화살표는 ' + fmt(R_EDGE, 2) + '배예요. 반복 수가 ' + IT_AWP + '번 대 ' + IT_ER + '번으로 ' + fmt(R_ITER, 2) + '배이고, 반복 한 번에 ' + fmt(R_PER_IT, 2) + '배라서, 둘을 곱하면 시간 차이가 나와요. 같은 풀이 프로그램이라 빠른 것은 알고리즘 덕분이 아니라 그래프와 반복 수 덕분이고, 두 화살표를 함께 걷는 C-PR이 AWP의 ' + fmt(R_CPR_AWP, 2) + '배로 가장 오래 걸려요.',
      '셋째, 나중 일은 모든 점수가 어느 정도 맞혔어요. 그런데 그냥 센 수를 넘은 페이지랭크는 하나도 없었어요. 두 기간 모두 송금 쪽에서는 송금 입차수가 AWP를, 허락 쪽에서는 받은 허락 수가 엔도스랭크를 이겼어요. 다시 출발을 AWP처럼 바꾼 엔도스랭크도 덜 뒤졌을 뿐 졌고, C-PR도 같은 화살표의 센 수를 넘지 못했어요. 다시 출발 규칙은 얼마나 뒤지는지를 바꿀 뿐, 뒤지는지는 바꾸지 못했어요. 이 비교들은 라벨을 본 뒤에 한 사후 비교예요.',
      '넷째, 이 논문의 점수 C-PR은 한 층만 걷기보다 낫다는 규칙 A를 채우지 못했어요. 허락 층보다 못하지는 않았지만 새 송금자에서 송금 층보다 뒤졌어요. 수정 점수에 규칙을 적용한 재분석이고, 등록 분석에서도 같았어요.',
      '다섯째, 송금 걷기에 허락 층을 더하면 나아지는지 묻는 규칙 B도 미충족이었어요. 새 허락 쌍은 나아졌지만 새 송금자에서 허용 폭보다 더 뒤졌고, 트레이더가 청산 없이 마감한 비율에서도 허용 폭을 넘어 뒤질 가능성을 지우지 못했어요. 규칙 밖의 사후 비교로는 C-PR이 두 기간 모두 두 스펜더 라벨에서 엔도스랭크보다 위였어요. AWP를 앞선 새 허락 쌍의 몫은 주로 AWP가 0을 주는 계약에서 나왔고, 나머지 계약에서는 W0에서 비슷하고 W1에서 조금 앞섰어요.',
      '덧붙여, 청산을 피했는지처럼 두 화살표 어디에도 없는 결과에서는, 등록한 기간인 W1에서 받은 허락 수가 송금 입차수보다 앞섰어요. 차이가 +' + fmt(P_W1_D[0], 3) + '이고, 97.5% 구간 ' + fmt(P_W1_CI[0], 3) + '–' + fmt(P_W1_CI[1], 3) + '이 0 위에 있어서 R1을 채웠어요. W0에서는 양수였지만 가려지지 않았고, 페이지랭크끼리의 비교도 가려지지 않았어요. 이 신호는 강제 청산을 피하는 것이지 거래를 잘하는 것이 아니고, 트레이더 표본도 작아요. 이것도 수정 점수에 등록한 규칙을 적용한 재분석이에요. 등록 분석은 W0에서만 가려져서 R1을 채우지 못했어요.',
      '목표로 보면, 첫째와 둘째는 이뤘지만 둘 다 만든 방식 때문에 대체로 저절로예요. 셋째는 일부만 이뤘어요. 예측은 충족했지만 센 수보다 나은 페이지랭크는 없었어요. 넷째와 다섯째는 이루지 못했고, 등록 분석에서도 같았어요.'
    ],
    html: function () {
      var cards = CARDS.map(function (c, i) {
        return '<div class="s11-card" data-in="none" data-k="' + i + '" style="left:' + CX[i] + 'px"><div class="th"></div><div class="bd">' +
          '<div class="rq"><span class="k">' + c.k + '</span><span class="qq">' + esc(c.q) + '</span></div>' +
          '<div class="an">' + esc(c.a) + '</div><div class="sb">' + c.sb + '</div>' +
          '<div class="tg">' + c.tags.join('') + '</div></div></div>';
      }).join('');
      var och = OCH.map(function (o, i) { return '<div class="s11-oc ' + o.cls + '" data-in="none" style="left:' + CX[i] + 'px">' + o.html + '</div>'; }).join('');
      return '<h1 class="t-h1">다섯 질문, [[다섯 답]]</h1>' + cards + och +
        '<div class="s11-brk" id="brk" data-in="none" style="left:' + (CX[0] + 20) + 'px;width:' + (CX[1] + 326 - CX[0] - 40) + 'px"><span>둘 다 만든 방식 때문에 대체로 저절로</span></div>' +
        '<div class="abs s11-add" id="add" data-in="none" style="left:96px;top:880px;width:1500px"><span><b>두 화살표 어디에도 없는 결과</b>(청산 피하기): W1에서 받은 허락 수가 송금 입차수를 앞서요(R1 충족) · W0과 페이지랭크 쌍은 가려지지 않음</span>' + Deck.tagHTML('reanalysis') + '</div>';
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
        if (k === 2) tl.fromTo(q(el, '#em4'), { backgroundSize: '0% 100%' }, { backgroundSize: '100% 100%', duration: 0.6, ease: E.out }, 0.9);
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
    /* RQ1: rank scatter, EndorseRank percentile × AWP percentile, all contracts of the matched cohort;
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
    /* RQ2: race bars (EndorseRank, AWP, C-PR solve times), the slowest 240 px long */
    var s3 = Comp.svg(ctx, g.ths[1], { w: W, h: H });
    var sc = 240 / Math.max(T_ER, T_AWP, T_CPR);
    svgEl('rect', { x: 20, y: 24, width: T_ER * sc, height: 20, rx: 6, fill: C.allow }, s3);
    svgEl('rect', { x: 20, y: 54, width: T_AWP * sc, height: 20, rx: 6, fill: C.xfer }, s3);
    svgEl('rect', { x: 20, y: 84, width: T_CPR * sc, height: 20, rx: 6, fill: C.cpr }, s3);
    svgEl('line', { x1: 20, x2: 20, y1: 16, y2: 112, stroke: C.ink3, 'stroke-width': 1.5 }, s3);
    /* RQ3: interval bars against zero (W1, after the labels: PageRank − its own count); the scale
       spans both intervals and zero, so a bar left of the dashed line means the count is better */
    var s4 = Comp.svg(ctx, g.ths[2], { w: W, h: H });
    var lo = Math.min(0, W1C_AWP[1], W1C_ER[1]), hi = Math.max(0, W1C_AWP[2], W1C_ER[2]);
    function X(v) { return 24 + (v - lo) / ((hi - lo) || 1) * (W - 48); }
    svgEl('line', { x1: X(0), x2: X(0), y1: 14, y2: H - 14, stroke: C.ink2, 'stroke-width': 1.5, 'stroke-dasharray': '4 4' }, s4);
    [[W1C_AWP, 44, C.xfer], [W1C_ER, 86, C.allow]].forEach(function (r) {
      svgEl('line', { x1: X(r[0][1]), x2: X(r[0][2]), y1: r[1], y2: r[1], stroke: r[2], 'stroke-width': 5, 'stroke-linecap': 'round' }, s4);
      svgEl('circle', { cx: X(r[0][0]), cy: r[1], r: 7, fill: r[2] }, s4);
    });
    /* RQ4, RQ5: one verdict stamp each */
    function stampThumb(host, text, rot) {
      var d = h('div', '', host);
      d.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center';
      d.innerHTML = '<span class="stamp fail" style="font-size:22px;padding:6px 14px;border-width:2.5px;transform:rotate(' + rot + 'deg)">' + text + '</span>';
    }
    stampThumb(g.ths[3], 'A 미충족 ✕', -6);
    stampThumb(g.ths[4], 'B 미충족 ✕', 4);
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
    id: 's11-02', title: '이 연구가 새로 보탠 것', time: 30, steps: 2,
    notes: [
      '이 연구가 새로 보탠 것은 다섯 가지예요.',
      '첫째, 두 화살표를 한 걸음으로 걷는 C-PR과, 미리 정한 규칙으로 한 시험이에요. 규칙은 미충족이었지만, 규칙 밖에서 보면 두 기간 모두 두 스펜더 라벨에서 엔도스랭크보다 위였어요. 둘째, 허락을 계약 평판의 화살표로 쓴 기준 점수 엔도스랭크예요. 셋째, 모든 점수를 다듬기 전의 센 수와, 같은 기간과 두 기간 밖에서 견준 평가 설계예요. 기간 밖에서 센 수를 넘은 페이지랭크는 없었어요. 넷째, 고르게 다시 출발하는 걸음이 한 단계 스펜더에서 실제로 무엇을 계산하는지 보여 주는 닫힌 식이에요. 다섯째, 어느 화살표에도 없는 결과에서 미리 등록한 비교예요. 등록한 기간 W1에서 받은 허락 수가 송금 입차수보다 청산 피하기를 더 잘 맞혔어요. 수정 점수에 한 재분석이에요.',
      '페이지랭크 알고리즘과 AWP의 무게는 빌려 온 것이고, 새것은 두 화살표를 한 걸음으로 묶는 규칙, 화살표의 종류, 그리고 그것을 시험한 방법이에요.'
    ],
    html: function () {
      var t = TILES;
      function tile(i, inner) { var T = t[i]; return '<div class="s11-tile" data-in="none" data-i="' + i + '" style="left:' + T.x + 'px;top:' + T.y + 'px;width:' + T.w + 'px;height:' + T.h + 'px"><span class="no">' + T.n + '</span>' + inner + '</div>'; }
      return '<h1 class="t-h1">새로 보탠 [[다섯]] 가지</h1>' +
        tile(0, '<div class="vis" id="v4" style="top:90px;height:300px"></div>' +
          '<div class="tx"><span class="big c-cpr">C-PR</span><br>두 화살표를 한 걸음으로 걷는 점수<small>미리 정한 규칙 A·B로 시험해 둘 다 미충족 · 규칙 밖에서는 두 스펜더 라벨 모두 엔도스랭크보다 위</small></div>') +
        tile(1, '<svg class="vis" id="v1" width="532" height="190" viewBox="0 0 600 380" style="top:40px"></svg>' +
          '<div class="tx">엔도스랭크: 허락을 계약 평판의<br>화살표로 쓴 기준 점수</div>') +
        tile(2, '<svg class="vis" id="v2" width="532" height="150" viewBox="0 0 532 150" style="top:44px"></svg>' +
          '<div class="tx">모든 점수를 다듬기 전의 센 수와 견줌<small>같은 기간 · 두 기간 밖(W0, W1)</small></div>') +
        tile(3, '<div class="vis fx" id="v3" style="top:62px;text-align:center">$r_v=c\\,\\bigl(1+d\\,\\delta(v)\\bigr)$</div>' +
          '<div class="tx">닫힌 식: 한 단계 스펜더에서<br>고르게 다시 출발하는 걸음이 계산하는 것</div>') +
        tile(4, '<svg class="vis" id="v5" width="532" height="150" viewBox="0 0 532 150" style="top:44px"></svg>' +
          '<div class="tx">두 화살표 어디에도 없는 결과에서<br>등록한 비교<small>GMX V2 계약 트레이더의 청산 피하기</small></div>') +
        '<p class="abs s11-note" data-step="2" style="left:96px;top:870px;width:1728px">알고리즘(페이지랭크)과 무게(AWP)는 <b>빌려 왔어요</b> — 새것은 <b>두 화살표를 묶는 걸음</b>, <b>화살표</b>, <b>시험 방법</b>이에요</p>';
    },
    build: function (el, ctx) {
      var g = ctx.g = {};
      g.tiles = qa(el, '.s11-tile');
      gsap.set(g.tiles, { autoAlpha: 0 });
      /* ① owner → spender, the G1 arrow */
      var v1 = q(el, '#v1');
      g.o1s = [[110, 60], [110, 170], [110, 280]].map(function (p, k) { return Comp.eoa(ctx, v1, { x: p[0], y: p[1], r: 24, label: k === 2 ? '주인들' : null }); });
      g.c1 = Comp.contract(ctx, v1, { x: 470, y: 170, size: 104, label: '스펜더 계약' });
      g.c1.label.setAttribute('y', 92); g.c1.label.setAttribute('font-size', 24);
      g.a1s = [[110, 60], [110, 170], [110, 280]].map(function (p, k) {
        return Comp.arrow(ctx, v1, { from: p, to: [470, 170], kind: 'allow', width: k === 1 ? 6 : 4, head: k === 1 ? 22 : 17, shorten: [38, 70], label: k === 1 ? '허락' : null, labelOffset: 30, labelSize: 26, hidden: true });
      });
      /* ② the count beside the walk: tally + three windows */
      var v2 = q(el, '#v2');
      g.tally = Comp.tally(ctx, v2, { x: 36, y: 34, size: 56 });
      [['같은 기간', 230], ['W0', 360], ['W1', 446]].forEach(function (b, k) {
        var w = k ? 70 : 110;
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
      g.stamp = Comp.stamp(ctx, v4, { ok: false, text: '규칙 A·B 미충족', x: 300, y: 64 });
      g.stamp.el.style.fontSize = '24px';
      /* ⑤ waffle: one dot per W1 trader contract */
      var v5 = q(el, '#v5');
      g.waf = [];
      for (var i = 0; i < N_W1; i++) {
        var cx = 40 + (i % 18) * 25, cy = 22 + Math.floor(i / 18) * 24;
        g.waf.push(svgEl('circle', { cx: cx, cy: cy, r: 8.5, fill: C.ink2, 'fill-opacity': 0.75 }, v5));
      }
      var wt = svgEl('text', { x: 31, y: 22 + 3 * 24 + 32, fill: C.ink3, 'font-size': 17 }, v5);
      wt.textContent = '점 하나 = W1 트레이더 계약 하나 (' + N_W1 + '개)';
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
    { i: ico('<circle cx="13" cy="20" r="7"/><path d="M20 20h16M30 20v6M35 20v4"/>'), t: '가격과 토큰 목록 말고는 블록체인 밖 정보가 없어요 — <span>허락한 주인들이 서로 다른 사람인지 몰라요</span>' },
    { i: ico('<path d="M14 11l-9 9 9 9M26 11l9 9-9 9M23 8l-6 24"/>'), t: '계약의 평판일 뿐, <span>코드가 안전한지는 말하지 않아요</span>' },
    { i: '<svg viewBox="0 0 40 40" fill="none"><rect x="5" y="5" width="30" height="30" rx="8" stroke="#A3ADBF" stroke-width="2.4"/><text x="20" y="21" text-anchor="middle" dominant-baseline="middle" fill="#A3ADBF" font-size="13" class="svg-mono">{ }</text></svg>', t: '점수를 받은 것은 계약뿐이에요 — <span>EOA에 대해서는 말하지 않아요</span>' },
    { i: Deck.ICONS.loop, t: '달러 금액·다섯 토큰·12개월 점수 기간은 등록 결과를 본 뒤 정했어요 → <span>판정은 재분석</span>' },
    { i: Deck.ICONS.eye, t: '센 수와의 비교, 활발함 변형은 <span>사후예요</span>' },
    { i: ico('<circle cx="8" cy="10" r="3"/><circle cx="32" cy="9" r="3"/><circle cx="20" cy="22" r="3.5"/><circle cx="9" cy="32" r="3"/><circle cx="33" cy="31" r="3"/><path d="M10.5 12l7 8M29.5 11l-7 9M11 30l7-6M31 29l-8.5-5"/>'), t: '에고 네트워크(코호트에 닿는 화살표만) · 다섯 토큰 · 아비트럼 원 · <span>이 기간만</span>' },
    { i: ico('<circle cx="10" cy="10" r="3"/><circle cx="20" cy="10" r="3"/><circle cx="30" cy="10" r="3"/><circle cx="10" cy="20" r="3"/><circle cx="20" cy="20" r="3"/><circle cx="10" cy="30" r="3"/>'), t: '트레이더 표본이 작아요 <span>(W1 ' + N_W1 + '개 · W0 ' + N_W0 + '개)</span>' },
    { i: '<svg viewBox="0 0 40 40" fill="none" stroke="#A3ADBF" stroke-width="2.2" stroke-dasharray="3 3"><circle cx="20" cy="8" r="4.5"/><circle cx="31" cy="16" r="4.5"/><circle cx="28" cy="30" r="4.5"/><circle cx="12" cy="30" r="4.5"/><circle cx="9" cy="16" r="4.5"/></svg>', t: '고르게 다시 출발하면 <span>닫힌 농장에 약해요</span>' }
  ];
  var slide3 = {
    id: 's11-03', title: '한계', time: 35, steps: 2,
    notes: [
      '한계도 분명히 말씀드릴게요.',
      '이 점수는 하루 가격과 토큰 목록 말고는 블록체인 밖 정보를 쓰지 않아서, 허락한 주인들이 정말 서로 다른 사람인지 알 수 없어요. 계약의 평판일 뿐 코드가 안전한지는 말하지 않아요. 점수를 받은 것은 계약뿐이라서, EOA에 대해서는 아무것도 말하지 않아요. 본문의 수정 분석, 곧 달러 금액과 다섯 토큰, 동결 전 12개월의 점수 기간은 등록 분석의 결과를 본 뒤에 정했으니, 그 판정은 재분석이에요.',
      '센 수와의 비교와 활발함 다시 출발 변형은 라벨을 본 뒤에 한 비교예요. 그리고 코호트에 닿는 화살표만 모은 에고 네트워크, 다섯 토큰, 아비트럼 원 한 체인, 이 기간만 본 결과예요. 트레이더 표본은 W1 ' + N_W1 + '개, W0 ' + N_W0 + '개로 작고, 고르게 다시 출발하는 점수는 닫힌 농장에 약해요.'
    ],
    html: function () {
      function rows(a, step) {
        return '<div class="s11-lim" data-in="none" data-k="' + step + '" data-stagger="0.08">' + a.map(function (l) {
          return '<div class="r"><span class="ic">' + l.i + '</span><span class="t">' + l.t + '</span></div>';
        }).join('') + '</div>';
      }
      return '<h1 class="t-h1">이 연구가 [[말하지 않는]] 것</h1>' +
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
      '<div class="q" style="position:absolute;left:40px;right:40px;top:262px;text-align:center;font-size:30px;line-height:42px;font-weight:600">이 계약이 내 USDC를 꺼내 써도 되도록 허락할까요?</div>' +
      '<div class="cd" style="position:absolute;left:0;right:0;top:318px;text-align:center"></div>' +
      '<div class="btns" style="position:absolute;left:0;right:0;top:396px;display:flex;justify-content:center;gap:20px"><div class="btn no">거절</div><div class="btn yes">허락</div></div></div>';
  }
  var NEXT = [
    { t: '더 깊은 표본에서 전파가 센 수에 보태는지 시험', s: '새 데이터에서 엔도스랭크와 활발함 변형을 센 수와 견줌 · 한 단계와 더 깊은 스펜더를 따로', hyp: true },
    { t: '수정 분석 자체를 등록 시험', s: '달러·다섯 토큰·12개월 점수 기간을 고정하고, 예: 2026년 10–12월 로그를 뽑기 전에 등록' },
    { t: '믿을 만한 씨앗에서만 다시 출발 — 농장 막기', s: '고르게 다시 출발하면 닫힌 농장이 몫을 모아요' },
    { t: '계약 위험 라벨(드레이너, 러그풀)과 비교', s: '활동량과 따로, 위험을 말해 주는지 보기' }
  ];
  var slide4 = {
    id: 's11-04', title: '지갑 프로그램이 보여 줄 수 있는 것, 그리고 다음 일', time: 40, steps: 3,
    carrier: false,
    notes: [
      '그러면 처음의 그 창에는 무엇을 보여 줄 수 있을까요?',
      '처음에 본 창이 다시 열려요. 이번에는 한 줄이 더 있어요. 이 계약을 허락한 서로 다른 주인 주소의 수예요. 주인은 사람이 아니라 주소라서, 몇 명이 아니라 몇 개라고 세요. 이 연구의 결과로 보면, 이 수는 어떤 서비스든 페이지랭크 없이 계산할 수 있는 공개 신호이고, 기간 밖에서는 두 기간 모두 나중에 생길 허락을 이 연구의 어떤 페이지랭크보다도 잘 맞혔어요. 라벨을 본 뒤에 한 비교예요. 화면의 N은 자리 표시이고 특정 계약을 가리키지 않아요.',
      '다만 이 수는 얼마나 널리 허락받았는지일 뿐이에요. 낮으면 더 살펴볼 이유가 되지만, 높다고 서명할 이유가 되지는 않아요. 그래서 커서는 허락 버튼 위에 머물기만 해요.',
      '다음 연구로는 네 가지를 생각하고 있어요. 먼저 더 깊은 표본을 뽑아, 엔도스랭크와 그 활발함 다시 출발 변형을 새 데이터에서 센 수와 견주는 것이에요. 한 단계 스펜더와 더 깊은 스펜더를 따로 보면, 걸음이 센 수에 무엇을 보태는지 알 수 있어요. 이것은 아직 가설이에요. 그리고 수정 분석 자체를, 달러 금액과 다섯 토큰, 12개월 점수 기간을 고정한 채 등록 시험으로 다시 하는 것, 믿을 만한 씨앗에서만 다시 출발하게 해서 농장을 막는 것, 실제 계약 위험 라벨과 견주는 것이에요.'
    ],
    html: function () {
      var win = WP ? WP.html({ id: 'win', top: WT, question: '이 계약이 내 USDC를 꺼내 써도 되도록 허락할까요?', code: '' }) : fallbackWallet();
      return '<h1 class="t-h1">그 창에 보여 줄 수 있는 것</h1>' + win +
        '<div class="s01-spark" id="sp1" data-in="none" style="position:absolute;left:0;top:0;width:14px;height:14px;border-radius:8px;background:#fff;box-shadow:0 0 14px 3px rgba(255,255,255,.75)"></div>' +
        '<div class="s01-spark" id="sp2" data-in="none" style="position:absolute;left:0;top:0;width:14px;height:14px;border-radius:8px;background:#fff;box-shadow:0 0 14px 3px rgba(255,255,255,.75)"></div>' +
        '<p class="abs s11-nnote" id="nnote" data-in="none" style="left:' + WX + 'px;top:' + (WY + WG.h * WS + 14) + 'px;width:' + (WG.w * WS) + 'px">N은 자리 표시예요 — 특정 계약을 가리키지 않아요</p>' +
        '<div class="abs s11-two" id="two" data-in="none" style="left:' + WX + 'px;top:' + (WY + WG.h * WS + 74) + 'px;width:700px">' +
          '<div>낮은 수 <span class="ne">=</span> <span class="ink-2">더 살펴볼 이유</span></div>' +
          '<div>높은 수 <span class="ne" id="ne">≠</span> [[서명할 이유]]</div></div>' +
        '<div class="abs s11-nx" id="nx" data-in="none" style="left:820px;top:196px;width:1004px"><h2 class="t-h2">다음 일</h2>' +
          NEXT.map(function (n, i) {
            return '<div class="s11-nc"><span class="n">' + (i + 1) + '</span><span class="t">' + esc(n.t) + '<small>' + esc(n.s) + '</small></span>' +
              (n.hyp ? '<span class="s11-hyp" id="hyp">' + Deck.tagHTML({ ko: '가설', icon: 'hollow', key: 'hypothesis' }) + '</span>' : '') + '</div>';
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
      g.nlText = '이 계약을 허락한 서로 다른 주인 주소: ';
      var ns = h('div', 's11-ns', g.win, '얼마나 널리 허락받았는지일 뿐 — 안전하다는 뜻은 아니에요');
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
        }, onComplete: function () { g.nl.innerHTML = esc(full) + '<b>N</b>개'; } }, 1.45);
        tl.fromTo(g.ns, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 2.65);
        /* the cursor comes to rest on 허락 — and does not press */
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
    id: 's11-05', title: '감사합니다', time: 20, steps: 2,
    hud: false,
    notes: [
      '(작은 세계의 네 점이 별자리처럼 떠요.)',
      '들어 주셔서 감사합니다. 이제 질문을 받을게요.',
      '지도해 주신 Mnkandla 교수님, Moulla 교수님, Attipoe 박사님께 감사드려요. 이 연구의 코드와 모든 결과 숫자는 공개 저장소에 있고, 이 발표의 숫자마다 어느 파일의 어느 값에서 왔는지 적어 두었어요.'
    ],
    html: function () {
      var sup = esc(META.supervisor || 'Prof. Ernest Mnkandla'), co = esc((META.co_supervisors || ['Prof. Donatien Koulla Moulla', 'Dr. David Sena Attipoe']).join(', '));
      return '<svg class="abs" id="sky" data-in="none" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible;pointer-events:none"></svg>' +
        '<div class="s11-thx" id="thx" data-in="none" style="top:500px"><div class="t-display" id="ty">감사합니다</div></div>' +
        '<svg class="abs" id="ul" data-in="none" width="1920" height="60" viewBox="0 0 1920 60" style="left:0;top:628px;overflow:visible"></svg>' +
        '<p class="s11-thx t-body-l ink-2" id="qa" data-in="none" style="top:690px">질문을 받을게요</p>' +
        '<p class="s11-small" id="sm1" data-in="none" style="top:846px">지도교수 <b>' + sup + '</b> · 공동 지도교수 <b>' + co + '</b> · ' + esc(META.university || 'University of South Africa') + '</p>' +
        '<p class="s11-mono" id="sm2" data-in="none" style="top:892px">코드·결과: github.com/abitocodes/phd_works · 결과 digest: experiments/data/3-published-results-for-thesis/revised-usd-12m/</p>';
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

  Deck.section({ id: 's11-closing', title: '정리', slides: [slide1, slide2, slide3, slide4, slide5] });
})();
