# Capsule CORE（2026-09-05）

この文書は α ではない。Hash-A に封入しない。研究仮説を確定事実へ昇格させない。

## Purpose

Capsule は記憶庫ではない。
必要な状態だけを、整合性を壊さず次の推論へ搬送する容器である。

LLM に過去を大量に読ませる仕組みではない。
人格を生成する仕組みでもない。

## Boundaries

| 記号 | 役割 | min3 での場所 |
|------|------|----------------|
| α | 不変の制約 | `Alpha.rules`。法律ではない。生成照合はしない |
| β | 同一性の核 | `Beta` + `BetaFact` |
| γ | 座標 | `time_label` / `project` / `topic` |
| Δ | 更新 | 閉じた語のイベント流。IS へ自動採用しない |
| IS | Δ 側の確定 | 住所ごと最大3行。語上書き。状態はピン。facts を逃がさない |
| η | 作業面の偏差 | 非保存。bind 文を変えうる。記憶層ではない |
| Hash-B | Δ / IS / pending の完全性 | `Capsule.hash_b()`。Hash-A には入れない |

θ / Ζ / QVK / Concierge.commit は本作業線に無い。層として足さない。
Hash-B の定義は Capsule。trusted 比較・搬入・換装は `BOX.py`。

## Integrity

Hash-A は `Inner.payload()` だけを封印する。中身は α / β / β facts。

γ・Δ・IS・pending・η・adopted は payload に入らない。
だから「LLMがそう言った」と「Capsuleとして確定している」は分離できる。

Hash-A が壊れたら Render は生成を止める。
Hash-A が生きていても、生成文が核を守ったことにはならない。

## Write

LLM は閉じたパケット `{gamma, delta, is}` を提案できる。
自由文は `bad_packet`。
`human=True` は pending。承認するまで見えない。
identity が低いと `NONE` で捨てる。

公開確定の事務（`Concierge.commit(plan)`）は Capsule の外である。
Capsule ≠ Concierge。

## Principle

- 検証した状態を残す。LLM の解釈を残さない
- 不変の同一性と可変状態を混ぜない
- 基準に対する偏差を見る。人格を Capsule が作らない
- 相互肯定より、通過しなかったものを落とす
- 問題を新しい層で解かない

## Research hypothesis（Δ メモ。核にしない）

人間のフレーム可変性は、属性を細かく固定するより、座標を不完全／可変にした方が近い可能性がある。
QVK 3D は探索であり、正典ではない。

## この文書で実装しないこと

- Hash-B を Capsule.Inner に足す
- 生成文を Hash-A と照合する Gate
- QVK / SemanticJudge
- Concierge を Capsule に吸収する
- 「良い人」評価軸の細分化を α にする
