# 온체인 마진거래 계약 — 유저 지갑 노출 조사

## 원칙

성공률 순위는 **실제 트레이더 지갑** 기준이어야 합니다. `transaction.from`만 사용하면 ExchangeRouter·Keeper·LiquidationHandler 등 **중개/실행 지갑**이 집계되어 의미가 없어집니다.

| 식별 방식 | 적합 여부 |
|-----------|-----------|
| `tx.from` | 부적합 — 라우터/키퍼가 발신자인 경우 다수 |
| 이벤트 `account` / `user` / `onBehalfOf` | 적합 — 포지션·대출 소유자 |

## 추천 1순위: GMX V2 (Arbitrum One)

| 항목 | 내용 |
|------|------|
| EventEmitter | `0xC8ee91A54287DB53897056e12D9819156D3822Fb` |
| 트레이더 식별 | `PositionDecrease` / `PositionIncrease`의 `EventLog1` **topic2** = `bytes32(account)`; `eventData.addressItems["account"]`와 동일 |
| PnL | `eventData.intItems["basePnlUsd"]` |
| 청산 | `orderType == 7` (Liquidation) 또는 `msgSender == LiquidationHandler` (`0xaf157Eb8...`) |
| BigQuery | `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs` |

`msgSender`는 OrderHandler·LiquidationHandler일 수 있으므로 순위 집계에 **사용하지 않음**.

## 본 구현 선택

**GMX V2 @ Arbitrum** — 마진/퍼프 의미, 트레이더 지갑 직접 노출, 실현 PnL 이벤트를 모두 충족. 렌딩 프로토콜 디폴트 라벨은 이론적으로 적합하나, 동일 체인에서 관측 가능한 under-collateralized lending 볼륨이 부족하여 본 연구에서는 채택하지 않음.
