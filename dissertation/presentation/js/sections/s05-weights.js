/* s05-weights — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s05-01", "왜 화살표마다 무게가 다를까"], ["s05-02", "시간 무게 σ(Δt): 180일이면 반"], ["s05-03", "금액 무게 V(z): 커져도 1을 넘지 않아요"], ["s05-04", "b = ln 3 / m: 중앙값이 반이 되게"], ["s05-05", "두 그래프의 무게와 다시 출발"], ["s05-06", "달러로 바꾸기와 상한 U (C-PR용)"]];
  Deck.section({
    id: 's05-weights',
    title: '화살표의 무게',
    slides: [{
      id: 's05-01',
      title: '화살표의 무게 (자리 표시)',
      notes: '화살표의 무게 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">화살표의 무게</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s05-weights 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
