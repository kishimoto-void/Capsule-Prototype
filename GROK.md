# Grok / LLM の取り扱い

日付: 2026-09-07  
対象: Capsule-Prototype の作業線。金型 `axiom_min.py` は未変更。  
この文書は α ではない。Hash-A に封入しない。

Grok は LLM である。次トークン予測のまま。アルゴリズムは変えない。  
Capsule は Grok を賢くしない。Grok の文を核にしない。

---

## 置き場

```
αβ / Hash-A   封印。観察から書かない。Grok から書かない
γ             bind した住所。Grok が広げる場所ではない
Δ / IS        閉じた語だけ。生成文そのものではない
η / kari      非保存。次の bind を変えうる。状態ではない
Frame         start + ? = goal。間は仮組み
LLM / Grok    生成器。Callable[[str], str]。権限ではない
Runtime       経路。核ではない
人間          owner。authorize の印だけが書き込みを開く
```

会話に出た文と、Capsule として確定した行は別物である。

---

## 閉じた取り扱い

1. Grok を生成器として呼んでよい。既定 stub を実モデルに差し替えても、核の定義は動かない。
2. 生成は権限ではない。`identity` だけでは足りない。`authorize=True` が人間の印。
3. 自由文・完成答え・スロット散文は commit しない。
4. 仮組み（kari）は受けてよい。残さない。Hash-B も動かない。
5. 本組（hon）だけが閉じた packet の候補になる。根拠3本と実用の向きが要る。
6. 未知語は残らない。閉じた語は `課題 / 改善点 / 結論 / 立場 / 状態` だけ。
7. bind した γ 以外は `gamma_mismatch`。越境した予定も予報も書かない。
8. Hash-A が壊れていれば生成器を呼ばない。修復しない。
9. Gate は書き込み政策だけを見る。生成文を α と照合しない。
10. Grok が正しく答えたことと、Capsule が確定したことは一致しない。

---

## 埋め方

Frame の穴を Grok が埋めるとき、完成和を出さない。

```
start + ? = goal
```

`?` は答えの本文ではない。所与を goal 側の見出しへ向ける仮組みである。  
時刻・科目・買い物・天気を補完して一日を完成させる作業ではない。

Grok 埋めの形:

```json
{
  "kari": {
    "taio":  {"plus": "...", "minus": "...", "cite": "kernel か address"},
    "seigo": {"plus": "...", "minus": "...", "cite": "state"},
    "gap":   {"plus": "...", "minus": "..."}
  },
  "hon": {
    "gamma": {"time_label": "...", "project": "...", "topic": "..."},
    "is": [{"field": "状態", "value": "閉じた語の値"}],
    "grounds": [
      {"source": "kernel", "plus": "...", "minus": "...", "onto": "hon"},
      {"source": "state",  "plus": "...", "minus": "...", "onto": "hon"},
      {"source": "address","plus": "...", "minus": "...", "onto": "hon"}
    ],
    "jitsuyo": {"toward": "goal 側", "not": "越境・核改変", "cite": "address"}
  }
}
```

cite は Frame の catalog から取る。  
start の全文は state に入りうる。goal の全文は address に入りうる。  
catalog に無い語を cite しても通らない。

hon を省略して kari だけ返すのが、検査としては先である。

---

## 実測（2026-09-07）

生成器を Grok 埋めに差し、同じ Runtime に通した。

式1: `明日の天気 + ? = 姫路市の天気`  
式2: `明日、病院に行く + ? = 明日の予定`

| 埋め | 分類 | 結果 |
|------|------|------|
| 自然文の答え | `free_text` | 書かない。`not_packet` |
| `{answer: ...}` で和を完成 | `finished` | 書かない。`answer` reject |
| open_slots へ散文 | `inference` | 書かない。`malformed_pm` |
| kari だけ | `dual` | 受付。非保存。IS 空。Hash-B 不変 |
| hon に未知語（`天気` / `予定`） | `dual` | `hon_ready` でも `unknown_word`。残らない |
| hon を閉じた語 + 印なし | `dual` | 候補。書かない。`human_required` |
| hon を閉じた語 + `authorize=True` | `dual` | 書く。Hash-A 不変。Hash-B だけ動く |

stub の既定文は `基準の外は埋めない。核は変えない。` であり、commit しない。

閉じた語へ予報や予定を入れ、人間が印を押すと残る。  
これは正しさの証明ではない。Gate が意味を見ていないことの実測である。

---

## Grok にさせてよいこと / させないこと

させてよい:

- `infer_prompt` を読んで kari を埋める
- plus より先に minus を書く
- catalog に無いものは穴のまま残す
- hon を出さない判断をする
- Hash-A を観察として報告する（更新しない）

させない:

- 完成した一つの答えに畳む
- 住所を広げる
- 仮組みを IS に書く
- Hash-A / β / facts を生成から直す
- 印の代わりに「正しいから書け」と言う
- 会話の天気・予定を Capsule の確定と名乗る

---

## 経路

```
bind → pull → infer(Grok) → classify
  free_text / finished / malformed  → 捨てる
  kari only                         → 非保存
  hon_ready + bound γ + identity
    + authorize                     → BOX.commit → Capsule.ingest
```

毎ターン `Hash-A_before == Hash-A_after` を見る。  
壊れた核は修復しない。生成経路を止める。

---

## 言わないこと

- Grok 専用の記憶層ができた
- 口調維持やハルシネーション一般が解けた
- α が法律として Grok を縛る
- 実 API 接続済みである
- モデル非依存の一般が証明された

Runtime の生成器は差し替え口だけである。本リポジトリは API キーを持たない。
