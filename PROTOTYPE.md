# Prototype freeze

日付: 2026-09-06

このリポジトリは Capsule の全履史ではない。min3 作業線の動く最小核である。

1. Capsule はこれ以上賢くしない。
2. Observer の結果で β / Hash-A を更新しない。
3. 生成文は見ない。Gate は書き込み政策のみ。
4. 金型 `axiom_min.py` は触らない。
5. Runtime / bind は核の外。BOX の上に置く。
6. 毎ターン `Hash-A_before == Hash-A_after` を機械的に見る。
7. 壊れた核は修復しない。生成経路を止める。
