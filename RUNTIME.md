# Runtime

日付: 2026-09-06  
対象: `runtime.py` と Frame の仮組み / 本組。金型と min3 核は未変更。

## 何を足したか

```
Capsule  何であるか
BOX      今どう扱うか
Runtime  今どの経路で通すか
Frame    start + ? = goal。間は仮組み
```

一本の入口:

```
bind → pull → infer → propose → reject / accept → commit
```

毎ターン `Hash-A_before == Hash-A_after` を見る。壊れていれば生成器を呼ばない。

Frame の二重口:

```
start + 仮組み(?) = goal     非保存
本組                         閉じた packet だけ commit 可
```

仮組みは状態にならない。本組も identity と bound γ と根拠3本を通らなければ書かない。

仮組みに求めるもの: 事実軸 2 本（対応 / 整合）。cite は Frame の既知だけ
本組に求めるもの: 閉じた packet + kernel / state / address の根拠を各1本以上
古い Frame（Hash-A 不一致）と壊れた核は accept しない



## 入れないもの

- 生成文と α の照合
- Observer による β / Hash-A 更新
- 自動 γ 定着
- 新しい IS / Δ の語
- API 接続
- 仮組みの Capsule 書き込み

## 測ったこと

`python3 -m unittest test_axiom_min3.py test_BOX.py test_runtime.py` → 95/95 OK

| 入力 | 結果 |
|------|------|
| 自由文 | commit しない |
| 未知語 | IS に残らない |
| 完成答え / Frame 埋め | wrote=False |
| 仮組みだけ | 非保存。Hash-B も動かない |
| 仮組み + 本組、identity 無し | 本組は identity_required |
| 仮組み + 本組、identity あり | 本組の閉じた語だけ IS に残る |
| 本組の γ 越境 | gamma_mismatch。仮組みは残るが状態ではない |
| facts 改変 | 生成器を呼ばない |
