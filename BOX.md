# BOX

着脱面。Capsule ではない。記憶層ではない。

```
Capsule  何であるか。Hash-A と Hash-B の定義
BOX      それを今どう扱うか。監査・搬入・換装
Hash-A   核。BOX は観察から書かない
Hash-B   可変の完全性。trusted は採用してよいか
```

## 動かす

```bash
python3 -m unittest test_BOX.py
python3 BOX.py
```

## 入れるもの

- `propose`：閉じたパケットの構文だけ見る。書かない
- `commit`：`Capsule.ingest` だけ。identity 必須。欠落は書かない。Hash-A が動いたら例外。戻りに hash_b / trusted_b / hash_b_match を付ける。自動 seal しない
- `export_b` / `import_b`：claimed Hash-B と中身が違うと TAMPER。trusted と違うと PROVENANCE。`allow_evolution` か `trusted_hash` で搬入する
- `seal_b`：今の可変を trusted にする
- `swap` / `mount`：換装。各 Hash-A は自分の Capsule に残る
- `match`：構造一致。意味スコアではない
- `generate_frame` / `render_json`：不全 Frame。desk / omit で材料を引き、open_slots で穴を引く。生成は Capsule に書かない

机:
- `identity` = αβγ
- `situation` = αβγΔIS（既定）
- `bare` = α γ IS
- `qvk` = αβγ IS。Q/V/K は空。推測は穴だけ。核にも IS にも書かない
- 思考順は `seal → desk → start_goal → analogy → minus → plus → stop`
- Frame は `start + ? = goal`。start と goal は所与。間は仮組み。完成形は出さない
- 仮組み `kari` は非保存。本組 `hon` は閉じた packet だけ。Frame から Capsule へ自動 write しない


## 入れないもの

- QVK
- 生成文と Hash-A の照合
- Frame から Capsule への自動 write
- Concierge.commit
- 新しい IS / Δ の語
