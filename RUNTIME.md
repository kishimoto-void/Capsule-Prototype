# Runtime

日付: 2026-09-06  
対象: `runtime.py` のみ。金型と min3 と BOX の核は未変更。

## 何を足したか

```
Capsule  何であるか
BOX      今どう扱うか
Runtime  今どの経路で通すか
```

一本の入口:

```
bind → pull → infer → propose → reject / accept → commit
```

毎ターン `Hash-A_before == Hash-A_after` を見る。壊れていれば生成器を呼ばない。

## 入れないもの

- 生成文と α の照合
- Observer による β / Hash-A 更新
- 自動 γ 定着
- 新しい IS / Δ の語
- API 接続

## 測ったこと

`python3 -m unittest test_axiom_min3.py test_BOX.py test_runtime.py` → 89/89 OK

| 入力 | 結果 |
|------|------|
| 自由文 | commit しない |
| 未知語 | IS に残らない |
| 完成答え / Frame 埋め | wrote=False |
| identity 欠落・低値 | NONE |
| facts 改変 | 生成器を呼ばない |
| γ 越境 | gamma_mismatch。別山に書かない |
| 閉じた packet + identity | IS は動く。Hash-A は動かない |
