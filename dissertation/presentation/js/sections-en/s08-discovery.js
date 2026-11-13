/* =========================================================================
   s08-discovery — Found first? The discovery-order test (STORYBOARD.md §2, s08-01 … s08-06)

   SKELETON (batch 0 of _revision-plan-contract12m.md): six slide shells with the ids, titles
   and planned times of plan §4. Batch 4 fills them in from data/discovery.js (DD.discovery) only.
   CSS class prefix of this section: s8- (s09-results uses s9-).

   s08-01  Visiting contracts like a web crawler
   s08-02  Which contract next? The ordering rules
   s08-03  Which contracts matter? Demand from user accounts
   s08-04  How fast did the crawl get there? AUC_10%
   s08-05  The verdict: D1 and D2 (RQ2)
   s08-06  What we saw outside the verdict

   Status tag: discovery ('Discovery-order test · decides no rule').
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
      notes: ['(Placeholder) This slide is still empty.'],
      html: '<h1 class="t-h1">' + title + '</h1><div class="s8-ph">Placeholder · this slide is still empty</div>'
    };
  }

  Deck.section({
    id: 's08-discovery',
    title: 'Found first? The discovery-order test',
    slides: [
      shell('s08-01', 'Visiting contracts like a web crawler', 50),
      shell('s08-02', 'Which contract next? The ordering rules', 45),
      shell('s08-03', 'Which contracts matter? Demand from user accounts', 45),
      shell('s08-04', 'How fast did the crawl get there? AUC_10%', 50),
      shell('s08-05', 'The verdict: D1 and D2 (RQ2)', 50),
      shell('s08-06', 'What we saw outside the verdict', 50)
    ]
  });
})();
