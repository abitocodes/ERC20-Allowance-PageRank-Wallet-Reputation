/* s03-data — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s03-01", "3년의 달력"], ["s03-02", "얼마나 많은 기록인가"], ["s03-03", "다섯 토큰과 달러 가격"], ["s03-04", "코호트 깔때기"], ["s03-05", "두 그래프의 크기"], ["s03-06", "15,107개 계약을 3D로"]];
  Deck.section({
    id: 's03-data',
    title: '데이터의 세계',
    slides: [{
      id: 's03-01',
      title: '데이터의 세계 (자리 표시)',
      notes: '데이터의 세계 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">데이터의 세계</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s03-data 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
