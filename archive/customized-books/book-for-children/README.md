# book-for-children — 『허락의 화살표』

학위 논문 *Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring*을 초등학생도 읽을 수 있게 풀어 쓴 책입니다. 찰스 펫졸드의 『CODE』처럼, 교실의 아주 쉬운 이야기에서 시작해 한 장에 한 계단씩 올라가며 논문의 한가운데까지 갑니다.

- 결과물: [`main.pdf`](main.pdf) (152 × 225 mm, 83쪽)
- 숫자는 모두 `../wallet-reputation-experiments/data/3-published-results-for-thesis/`의 결과 파일과 같습니다.
- 본문은 어린이용, 파란 상자("조금 더 알고 싶은 사람에게")는 고학년·어른용으로 진짜 용어와 정확한 숫자를 담았습니다.
- 책 전체를 한국어로 썼습니다. 방법 이름은 아이들이 부르기 쉽게 바꾸었고, 논문의 이름은 처음 소개할 때와 낱말 사전에만 적었습니다: 송금 랭크 = AWP, 동전 랭크 = C-PR, 앞면 랭크 = C-PR (λ=1), 뒷면 랭크 = C-PR (λ=0), 씨앗 랭크 = S-PR, 약속 1~3 = F1–F3. 저자 이름은 권태홍, 학교는 남아프리카공화국 유니사로 적었습니다.

## 차례

| 파일 | 장 | 다루는 논문 내용 |
|---|---|---|
| `chapters/00-title.tex`, `00-preface.tex` | 표지, 머리말 | 책 읽는 법, 어른 독자에게 |
| `01-trust.tex` | 1. 누구를 믿을까? | 평판, 연구 질문 |
| `02-notebook.tex` | 2. 지울 수 없는 큰 공책 | 블록체인, 지갑, 토큰, ERC-20, 스마트 계약 |
| `03-send-and-allow.tex` | 3. "보냈어"와 "써도 돼" | Transfer와 Approval, 허락 = 보증 |
| `04-dots-and-arrows.tex` | 4. 점과 화살표 | 그래프, 두 지도, 진입 차수 |
| `05-fake-friends.tex` | 5. 가짜 친구 작전 | 시빌 공격 |
| `06-passing-notes.tex` | 6. 쪽지 돌리기 놀이 | PageRank, 거듭제곱법(손 계산 예시) |
| `07-heavy-arrows.tex` | 7. 무게가 다른 화살표 | 가중치, 송금 한 번을 “한 번”으로 세기, 시간 감쇠, 활발한 송신자에서 다시 출발, 이미 나와 있는 방법인 송금 랭크(AWP) |
| `08-endorserank.tex` | 8. 허락으로 걷기: 엔도스랭크 | EndorseRank: AWP와 같은 가중치, 고른 재시작과 그 이유 |
| `09-mixing-maps.tex` | 9. 두 지도를 섞으면? | 동전 랭크(C-PR, 원금액 두 층), 앞면·뒷면 랭크(λ=1, 0), 씨앗 랭크(S-PR), 9월 14일 규칙 |
| `10-real-notebook.tex` | 10. 진짜 공책을 펼치다 | Arbitrum One, BigQuery, GMX, 매칭 코호트, 연구 일정 |
| `11-lining-up.tex` | 11. 줄 세우기 비교 | 켄달의 τ, 모든 점수의 같은 기간 정렬(점수마다 자기 지도의 검사와 닮음), 부트스트랩 |
| `12-speed.tex` | 12. 누가 더 빨리 계산할까 | 실행 시간 벤치마크 |
| `13-sealed-envelope.tex` | 13. 봉투에 넣은 예측 | 봄 홀드아웃: 모든 점수를 함께 세움, 받은 화살표 수(원시 차수)를 넘은 쪽지 놀이 점수 없음, 적용 범위(송금 받은 스펜더 977개), 9월 14일 규칙 실패 |
| `14-promise-first.tex` | 14. 먼저 약속하고 시험 보기 | 사전 등록, 6~8월 재현, 약속 1~3(F1–F3, 비교 대상은 뒷면 랭크), 판정 미충족, AWP 민감도 분석, 엔도스랭크 사후 채점 |
| `15-what-we-learned.tex` | 15. 그래서 무엇을 알게 되었을까 | 결론, 주장하지 않는 것, 남은 질문 |
| `16-appendix.tex` | 낱말 사전, 숫자로 보는 이 연구, 엔도스랭크와 송금 랭크를 맞대어 보면, 더 읽을거리 | 맞대어 보기는 논문 부록 8.5에 해당 |

`main.tex`는 장을 묶고, `preamble.tex`에는 판형, 글꼴, 상자와 그림 모양이 있습니다.

## 빌드

XeLaTeX와 `kotex`(TeX Live의 `collection-langkorean`, MiKTeX는 자동 설치)가 필요합니다. 차례와 그림 번호를 맞추려고 두 번 실행합니다.

```powershell
cd 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\customized-books\book-for-children
.\build.ps1
```

글꼴은 나눔바른고딕·나눔스퀘어라운드를 쓰고, 없으면 Windows의 맑은 고딕으로 바뀝니다. 같은 모양으로 만들려면 [나눔 글꼴](https://hangeul.naver.com/font)을 설치하세요.
