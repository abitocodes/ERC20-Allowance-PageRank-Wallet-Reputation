/* s07-measure — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s07-01", "무엇과 견줄까: 점검과 시험"], ["s07-02", "켄달의 타우: 쌍을 세요"], ["s07-03", "동점이 있으면: τ_b (그리고 스피어먼 ρ)"], ["s07-04", "부트스트랩: 다시 뽑아 400번"], ["s07-05", "짝지어 빼기 Δτ, 허용 폭, 본페로니"]];
  Deck.section({
    id: 's07-measure',
    title: '맞았는지 재는 법',
    slides: [{
      id: 's07-01',
      title: '맞았는지 재는 법 (자리 표시)',
      notes: '맞았는지 재는 법 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">맞았는지 재는 법</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s07-measure 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
