/* =========================================================================
   s08-discovery — 먼저 찾을까: 발견 순서 검증 (STORYBOARD.md §2, s08-01 … s08-06)

   SKELETON (batch 0 of _revision-plan-contract12m.md): six slide shells with the ids, titles
   and planned times of plan §4. Batch 4 fills them in from data/discovery.js (DD.discovery) only.
   CSS class prefix of this section: s8- (s09-results uses s9-).

   s08-01  웹 크롤러처럼 계약을 찾아가요
   s08-02  무엇으로 다음 계약을 고를까: 순서 규칙
   s08-03  무엇이 중요한 계약일까: 사용자 계정의 수요
   s08-04  얼마나 빨리 닿았나: AUC_10%
   s08-05  판정: D1과 D2 (RQ2)
   s08-06  판정 밖에서 본 것

   Status tag: discovery ('발견 순서 검증 · 규칙 아님').
   ========================================================================= */
(function () {
  'use strict';

  var CSS = [
    '.s8-ph{position:absolute;left:96px;top:300px;width:1728px;height:520px;border-radius:22px;border:1.5px dashed #2C3547;display:flex;align-items:center;justify-content:center;color:var(--ink-3);font-size:28px;line-height:40px}'
  ].join('\n');
  (function injectCss() {
    if (document.getElementById('s08-discovery-css')) return;
    var st = document.createElement('style'); st.id = 's08-discovery-css'; st.textContent = CSS;
    document.head.appendChild(st);
  })();

  function shell(id, title, time) {
    return {
      id: id, title: title, time: time, steps: 0, tags: ['discovery'],
      notes: ['(자리 표시) 이 장은 아직 비어 있어요.'],
      html: '<h1 class="t-h1">' + title + '</h1><div class="s8-ph">자리 표시 · 이 장은 아직 비어 있어요</div>'
    };
  }

  Deck.section({
    id: 's08-discovery',
    title: '먼저 찾을까: 발견 순서 검증',
    slides: [
      shell('s08-01', '웹 크롤러처럼 계약을 찾아가요', 50),
      shell('s08-02', '무엇으로 다음 계약을 고를까: 순서 규칙', 45),
      shell('s08-03', '무엇이 중요한 계약일까: 사용자 계정의 수요', 45),
      shell('s08-04', '얼마나 빨리 닿았나: AUC_10%', 50),
      shell('s08-05', '판정: D1과 D2 (RQ2)', 50),
      shell('s08-06', '판정 밖에서 본 것', 50)
    ]
  });
})();
