/* s06-methods — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s06-01", "엔도스랭크"], ["s06-02", "AWP와 원시 차수 기준선"], ["s06-03", "C-PR: 두 갈림길 표를 섞어요"], ["s06-04", "λ를 돌리면: 15,107개 계약이 움직여요"], ["s06-05", "S-PR: 허락은 '출발점'만 정해요"]];
  Deck.section({
    id: 's06-methods',
    title: '네 가지 점수',
    slides: [{
      id: 's06-01',
      title: '네 가지 점수 (자리 표시)',
      notes: '네 가지 점수 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">네 가지 점수</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s06-methods 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
