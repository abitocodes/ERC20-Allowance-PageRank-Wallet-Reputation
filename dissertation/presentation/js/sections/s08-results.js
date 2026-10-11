/* s08-results — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s08-01", "같은 기간: 각 점수는 자기 화살표의 지표와 맞아요"], ["s08-02", "두 점수는 순서가 달라요"], ["s08-03", "기간 밖 시험: 점수를 얼리고 기다려요"], ["s08-04", "송금 쪽: AWP가 그냥 센 수를 이겨요"], ["s08-05", "허락 쪽: 그냥 센 수가 이겨요"], ["s08-06", "다시 출발 규칙만 바꾸면? (사후 — 가설)"], ["s08-07", "닫힌 식: 엔도스랭크는 사실 무엇을 계산할까"], ["s08-08", "닫힌 식은 얼마나 맞을까, 그리고 결과 한 장"]];
  Deck.section({
    id: 's08-results',
    title: '결과',
    slides: [{
      id: 's08-01',
      title: '결과 (자리 표시)',
      notes: '결과 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">결과</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s08-results 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
