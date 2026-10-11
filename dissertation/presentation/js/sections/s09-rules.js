/* s09-rules — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s09-01", "언제, 무엇을 정했나"], ["s09-02", "규칙 A"], ["s09-03", "규칙 B"], ["s09-04", "등록 분석과 수정 분석"], ["s09-05", "두 화살표 어디에도 없는 결과: R1–R3"]];
  Deck.section({
    id: 's09-rules',
    title: '미리 정한 규칙',
    slides: [{
      id: 's09-01',
      title: '미리 정한 규칙 (자리 표시)',
      notes: '미리 정한 규칙 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">미리 정한 규칙</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s09-rules 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
