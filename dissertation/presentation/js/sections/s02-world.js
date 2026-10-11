/* s02-world — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s02-01", "디파이를 한 장으로"], ["s02-02", "송금과 허락은 다른 일이에요"], ["s02-03", "허락은 믿음처럼 보여요 — 하지만"], ["s02-04", "점수를 받는 쪽은 계약이에요"], ["s02-05", "무대: 아비트럼 원"]];
  Deck.section({
    id: 's02-world',
    title: '허락과 송금',
    slides: [{
      id: 's02-01',
      title: '허락과 송금 (자리 표시)',
      notes: '허락과 송금 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">허락과 송금</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s02-world 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
