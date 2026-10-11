/* s10-sybil-speed — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s10-01", "가짜 주소 농장: 제 몫의 3배를 모아요"], ["s10-02", "별 모양 농장: 한 계약에 몰아주기"], ["s10-03", "꼭대기까지 가짜 주소가 몇 개 필요할까"], ["s10-04", "속도는 화살표 수에서 와요"]];
  Deck.section({
    id: 's10-sybil-speed',
    title: '공격 비용과 속도',
    slides: [{
      id: 's10-01',
      title: '공격 비용과 속도 (자리 표시)',
      notes: '공격 비용과 속도 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">공격 비용과 속도</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s10-sybil-speed 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
