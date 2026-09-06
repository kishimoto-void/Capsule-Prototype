# AXIOM Capsule Prototype

LLM の外に着ける参照境界。知能ではない。製品ではない。

空白を埋める装置ではない。そのターンで空白を参照不能にする着脱部品である。

本リポジトリは **min3 作業線のプロトタイプ** である。履歴の全層は入っていない。金型 `axiom_min.py` は凍結。触らない。

親リポジトリ: https://github.com/kishimoto-void/Capsule  
ライセンス: PolyForm Noncommercial 1.0.0（研究・個人・非営利の再現と改変は可。商用は不可）

---

## いまの定義

```
αβ     封印された基準。Hash-A。観察から書かない
γ      本筋の住所（time / project / topic）
Δ      住所上の更新。閉じた語のみ
IS     正の確定だけ。最大3行。不知は書かない。語は上書き。状態はピン
η      非保存の距離。次の bind を変えうる
Gate   いまは書き込み政策のみ。生成文は見ていない
Render 見える世界
LLM    次トークン予測のまま。アルゴリズムは変えない
Runtime bind / pull / infer / propose / commit。核ではない
```

α は法律ではない。Gate は生成文を α と照合しない。

閉じた Δ 語: 課題 / 改善点 / 結論 / 立場 / 状態  
未知語は `adopt_word` するまで書けない。

---

## 動かす

```bash
python3 -m unittest test_axiom_min3.py test_BOX.py test_runtime.py
python3 runtime.py
```

| ファイル | 役割 |
|----------|------|
| `axiom_min.py` | 金型。触らない |
| `axiom_min3.py` | 作業線。γ = time + project + topic |
| `test_axiom_min3.py` | min3 単体 |
| `BOX.py` | 着脱面。Hash-B、換装、不全 Frame（start + ? = goal） |
| `test_BOX.py` | BOX 単体 |
| `runtime.py` | 薄い経路。BOX の上。核ではない |
| `test_runtime.py` | Runtime 耐圧。毎ターン Hash-A 不変 |
| `phase3_prototype.py` | Baseline 全載せと min3 Render の比較 |

Runtime の生成器は `Callable[[str], str]`。既定は stub。API は足していない。  
bind した γ 以外の packet は commit しない。推論埋めは Capsule に書かない。  
Hash-A が壊れていれば生成器を呼ばない。修復しない。

---

## このプロトタイプで入れた閉じた政策

1. IS は語ごとに上書きする。同じ語の旧行はスロットを食わない。
2. 4語目が来たら、ピン以外の最古を落とす。ピンは `状態`。
3. `ingest` の `evicted` は監査。記憶層ではない。
4. Runtime は経路だけ。Hash-A を観察から書かない。

IS_MAX=3 は据え置き。Render は IS だけ。Δ を見える世界に混ぜない。

---

## 証明していないこと

- モデル非依存の一般
- 履歴ありの F
- ハルシネーション全般
- α が法律として強制されること
- カーネル配置
- 実 LLM API 接続後の口調維持
