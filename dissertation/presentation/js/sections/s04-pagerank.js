/* s04-pagerank — PLACEHOLDER. The section builder replaces this whole file.
   It registers one title slide so the deck runs end to end (see STORYBOARD.md, js/deck.js). */
(function () {
  'use strict';
  var PLANNED = [["s04-01", "작은 세계"], ["s04-02", "무작위로 돌아다니는 사람"], ["s04-03", "오래 걸으면: 머무는 비율 → 균형식"], ["s04-04", "표로 한 번에: 이동 행렬"], ["s04-05", "두 가지 문제: 새는 물과 함정"], ["s04-06", "고치기: 감쇠 d와 다시 출발"], ["s04-07", "되풀이하면 멈춰요: 거듭제곱 반복"]];
  Deck.section({
    id: 's04-pagerank',
    title: '페이지랭크 유도',
    slides: [{
      id: 's04-01',
      title: '페이지랭크 유도 (자리 표시)',
      notes: '페이지랭크 유도 섹션의 자리 표시 장이에요. 실제 슬라이드는 STORYBOARD.md를 따라 만들 거예요.',
      html: '<div class="title-block"><h1 class="t-h1">페이지랭크 유도</h1>' +
        '<p class="sub">이 섹션의 슬라이드는 아직 만드는 중이에요.</p></div>' +
        '<div class="ph-list" data-in="rise" data-stagger="0.06">' +
        PLANNED.map(function (p) { return '<div class="ph-item"><span class="mono">' + p[0] + '</span><span>' + Deck.util.esc(p[1]) + '</span></div>'; }).join('') +
        '</div>' +
        '<div class="ph-note t-micro ink-3">자리 표시 장 · STORYBOARD.md의 s04-pagerank 절을 따라 이 파일을 바꿔 주세요</div>',
      steps: 0,
      time: 30
    }]
  });
})();
