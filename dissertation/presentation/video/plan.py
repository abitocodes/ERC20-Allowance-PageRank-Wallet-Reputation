#!/usr/bin/env python3
"""video/plan.py -- the render plan: every slide, step and narration line with its spoken length and
motion cues (anchor ids resolved to stage boxes), plus the texts of the opening and closing cards.

  python3 plan.py --lang ko --steps EXTRACT/ko/steps.json --scripts SCRIPTDIR --audio AUDIODIR --out plan-ko.json
"""
import argparse
import glob
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument('--lang', required=True)
ap.add_argument('--steps', required=True, help='steps.json written by extract.mjs')
ap.add_argument('--scripts', required=True)
ap.add_argument('--audio', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--gap', type=float, default=None)
A = ap.parse_args()

ex = json.load(open(A.steps, encoding='utf-8'))
anchors = {(s['slide'], s['step']): {a['id']: a for a in s['anchors']} for s in ex['steps']}
durs = {r['id']: r['dur'] for r in json.load(open(os.path.join(A.audio, A.lang, 'lines.json'), encoding='utf-8'))}

META = {
    'ko': {
        'intro': {'eyebrow': '박사 학위 논문 해설 영상', 'title': ['ERC-20 허락 화살표를 페이지랭크에 넣어', '온체인 지갑 평판 점수를 더 좋게 만들기'],
                  'author': '권태홍', 'affiliation': 'University of South Africa · 컴퓨터과학 박사 학위 논문 · 2026년 10월',
                  'legendAllow': '허락 화살표 (allowance)', 'legendTransfer': '송금 화살표 (transfer)'},
        'outro': {'eyebrow': '시청해 주셔서 감사합니다', 'title': ['ERC-20 허락 화살표를 페이지랭크에 넣어', '온체인 지갑 평판 점수를 더 좋게 만들기'],
                  'author': '권태홍', 'affiliation': 'University of South Africa · 컴퓨터과학 박사 학위 논문',
                  'credits': ['목소리: Supertonic 2 음성 합성 (Supertone, OpenRAIL-M)', '배경 음악: 이 영상을 위해 코드로 지은 곡', '화면: 논문 발표 슬라이드']},
    },
    'en': {
        'intro': {'eyebrow': 'A PhD thesis, explained', 'title': ['Integrating ERC-20 Allowance Edges', 'into PageRank for Enhanced', 'On-Chain Wallet Reputation Scoring'],
                  'author': 'Taehong Kwon', 'affiliation': 'University of South Africa · PhD thesis in Computer Science · October 2026',
                  'legendAllow': 'Allowance edge (approval)', 'legendTransfer': 'Transfer edge'},
        'outro': {'eyebrow': 'Thank you for watching', 'title': ['Integrating ERC-20 Allowance Edges', 'into PageRank for Enhanced', 'On-Chain Wallet Reputation Scoring'],
                  'author': 'Taehong Kwon', 'affiliation': 'University of South Africa · PhD thesis in Computer Science',
                  'credits': ['Voice: Supertonic 2 speech synthesis (Supertone, OpenRAIL-M)', 'Music: written in code for this video', 'Picture: the thesis defence slides']},
    },
}

problems = []


def dur(lid):
    if lid not in durs:
        problems.append('no audio for ' + lid)
        return 1.0
    return durs[lid]


scripts = {}
for f in sorted(glob.glob(os.path.join(A.scripts, A.lang, 'u*.json'))):
    sc = json.load(open(f, encoding='utf-8'))
    for st in sc['steps']:
        scripts[(st['slide'], st['step'])] = st['lines']
    scripts.setdefault('_units', []).append(sc)

intro, outro, chapters = [], [], {}
for sc in scripts['_units']:
    for i, _ in enumerate(sc.get('intro') or []):
        intro.append({'id': 'intro/%d' % i, 'dur': dur('intro/%d' % i)})
    for i, _ in enumerate(sc.get('outro') or []):
        outro.append({'id': 'outro/%d' % i, 'dur': dur('outro/%d' % i)})
    if sc.get('chapter'):
        sec = sc['steps'][0]['slide'][:3]
        chapters[sec] = [{'id': 'chapter/' + sec, 'dur': dur('chapter/' + sec)}]

slides = []
seen = set()
for sl in ex['slides']:
    steps = []
    for k in range(sl['steps'] + 1):
        lines = []
        for i, ln in enumerate(scripts.get((sl['id'], k)) or []):
            lid = '%s/%d/%d' % (sl['id'], k, i)
            A_ = anchors.get((sl['id'], k), {})
            boxes = [A_[a]['box'] for a in (ln.get('focus') or []) if a in A_]
            if len(boxes) != len(ln.get('focus') or []):
                problems.append(lid + ': unknown anchor in focus')
            lines.append({'id': lid, 'dur': dur(lid), 'boxes': boxes, 'zoom': ln.get('zoom', 'none') if boxes else 'none',
                          'mark': ln.get('mark', 'ring') if boxes else 'none', 'card': ln.get('card')})
        if not lines:
            problems.append('%s/%d: no narration' % (sl['id'], k))
        # the text and formulas on screen at this step: the marks keep their padding clear of them
        avoid = [a['box'] for a in anchors.get((sl['id'], k), {}).values() if a['kind'] in ('text', 'formula')]
        steps.append({'step': k, 'avoid': avoid, 'lines': lines})
    sec = sl['id'][:3]
    first = sec not in seen
    seen.add(sec)
    slides.append({'index': sl['index'], 'id': sl['id'], 'lastStep': sl['steps'], 'chapter': chapters.get(sec) if first else None, 'steps': steps})

gap = A.gap if A.gap is not None else (0.38 if A.lang == 'ko' else 0.32)
plan = {'lang': A.lang, 'fps': 30, 'gap': gap, 'meta': META[A.lang], 'intro': intro, 'outro': outro, 'slides': slides}
json.dump(plan, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False)
speech = sum(l['dur'] for s in slides for st in s['steps'] for l in st['lines']) + sum(l['dur'] for l in intro + outro) + \
    sum(c[0]['dur'] for c in chapters.values())
n = sum(len(st['lines']) for s in slides for st in s['steps'])
print(f'{len(slides)} slides, {n} step lines, speech {speech / 60:.1f} min, estimated video {(speech + n * gap + 304 * 1.6) / 60:.1f} min')
print(f'problems: {len(problems)}')
for p in problems[:30]:
    print('  ' + p)
