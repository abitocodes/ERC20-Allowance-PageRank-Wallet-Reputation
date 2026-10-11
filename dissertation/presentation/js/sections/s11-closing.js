/* s11-closing — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s11-01", "연구 질문에 대한 답"], ["s11-02", "이 연구가 새로 보탠 것"], ["s11-03", "한계"], ["s11-04", "지갑 프로그램이 보여 줄 수 있는 것, 그리고 다음 일"], ["s11-05", "감사합니다"]];
  Deck.section({
    id: 's11-closing',
    title: '정리',
    slides: [{
      id: 's11-01',
      title: '정리 (자리 표시)',
      notes: '정리 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">정리</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s11-closing 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
