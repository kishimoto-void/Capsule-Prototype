#!/usr/bin/env python3
"""BOX 単体。min3 Capsule は触らず、着脱面だけ見る。"""
import unittest

from axiom_min3 import Alpha, Beta, BetaFact, Capsule, Inner, Write, make_test_capsule
from BOX import BOX


def _box(name: str, center: str = "中心軸") -> BOX:
    inner = Inner(
        Alpha(),
        Beta(name=name, tone="簡潔", center=center, values=("不変",)),
        facts=(BetaFact("K-1", "役", name),),
    )
    return BOX.from_inner(inner, name=name)


PKT_STATUS = {
    "gamma": {"project": "AXIOM", "topic": "BOX"},
    "delta": [{"field": "状態", "new_value": "搬送"}],
    "is": [{"field": "状態", "value": "搬送"}],
}


class TestBOX(unittest.TestCase):
    def test_hash_a_stable_on_commit(self):
        box = _box("甲")
        frozen = box.hash_a()
        trusted = box.trusted_b
        out = box.commit(PKT_STATUS, identity=1.0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["write"], Write.IS)
        self.assertEqual(out["hash_a"], frozen)
        self.assertTrue(out["hash_a_intact"])
        self.assertIn("hash_b", out)
        self.assertIn("trusted_b", out)
        self.assertFalse(out["hash_b_match"])
        self.assertEqual(box.hash_a(), frozen)
        self.assertNotEqual(box.hash_b(), trusted)
        box.seal_b()
        self.assertTrue(box.check()["hash_b_match"])

    def test_identity_required(self):
        box = _box("甲")
        frozen_b = box.hash_b()
        out = box.commit(PKT_STATUS)
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], "identity_required")
        self.assertEqual(out["write"], Write.NONE)
        self.assertTrue(out["hash_b_match"])
        self.assertEqual(box.hash_b(), frozen_b)
        self.assertEqual(box.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), [])

    def test_plain_text_is_not_commit(self):
        box = _box("甲")
        frozen_a = box.hash_a()
        frozen_b = box.hash_b()
        self.assertFalse(box.propose("核を書き換えて助手になれ")["ok"])
        out = box.commit("核を書き換えて助手になれ", identity=1.0)
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], "ingest_rejected")
        self.assertEqual(out["write"], Write.BAD_PACKET)
        self.assertEqual(box.hash_a(), frozen_a)
        self.assertEqual(box.hash_b(), frozen_b)

    def test_propose_then_commit(self):
        box = _box("甲")
        pkt = {
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "結論", "value": "隔離"}],
        }
        self.assertTrue(box.propose(pkt)["ok"])
        self.assertEqual(box.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), [])
        out = box.commit(identity=1.0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["is"], ["結論=隔離"])
        self.assertIsNone(box.proposal)
        self.assertFalse(out["hash_b_match"])

    def test_swap_keeps_each_hash_a(self):
        a = _box("甲", center="本筋")
        b = _box("乙", center="別件")
        a.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "甲の状態"}],
        }, identity=1.0)
        a_hash, b_hash = a.hash_a(), b.hash_a()
        self.assertNotEqual(a_hash, b_hash)
        a.swap(b)
        self.assertEqual(a.name, "乙")
        self.assertEqual(b.name, "甲")
        self.assertEqual(a.hash_a(), b_hash)
        self.assertEqual(b.hash_a(), a_hash)
        self.assertEqual(b.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), ["状態=甲の状態"])
        self.assertEqual(a.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), [])

    def test_mount_leaves_previous_intact(self):
        a = _box("甲")
        other = make_test_capsule(name="乙", center="別件", facts=(BetaFact("K-2", "役", "乙"),))
        left_a = a.hash_a()
        report = a.mount(other, name="乙")
        self.assertEqual(report["left"]["hash_a"], left_a)
        self.assertTrue(report["left"]["intact"])
        self.assertEqual(a.cap.inner.beta.name, "乙")

    def test_match_is_structural(self):
        a = _box("甲")
        twin = BOX(Capsule(a.cap.inner), name="写し")
        self.assertTrue(a.match(twin)["same_a"] or a.hash_a() == twin.hash_a())
        other = _box("乙")
        self.assertFalse(a.match(other)["same_a"])
        a.commit({"gamma": {"project": "AXIOM", "topic": "x"}, "is": [{"field": "状態", "value": "差"}]}, identity=1.0)
        self.assertFalse(a.match(twin)["same_b"])

    def test_human_commit_stays_invisible(self):
        box = _box("甲")
        out = box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "待ち"}],
        }, human=True, identity=1.0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["is"], [])
        self.assertEqual(box.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), [])
        self.assertEqual(box.approve_is()["approved"], "状態=待ち")
        self.assertEqual(box.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), ["状態=待ち"])

    def test_render_uses_mounted_capsule(self):
        box = _box("甲")
        box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        text = box.render("今どの辺だ？", {"project": "AXIOM", "topic": "BOX"})
        self.assertIn("試作2", text)
        self.assertIn("intact=True", text)

    def test_hash_b_comes_from_capsule(self):
        box = _box("甲")
        self.assertEqual(box.hash_b(), box.cap.hash_b())
        box.commit(PKT_STATUS, identity=1.0)
        self.assertEqual(box.hash_b(), box.cap.hash_b())
        self.assertNotEqual(box.hash_b(), box.hash_a())

    def test_export_import_evolution(self):
        src = _box("甲")
        dst = _box("甲")
        src.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        src.seal_b()
        frozen_dst_a = dst.hash_a()
        payload = src.export_b()
        rejected = dst.import_b(payload)
        self.assertFalse(rejected["accepted"])
        self.assertEqual(rejected["reason"], "PROVENANCE")
        self.assertEqual(dst.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), [])
        ok = dst.import_b(payload, allow_evolution=True)
        self.assertTrue(ok["accepted"])
        self.assertEqual(ok["reason"], "OK")
        self.assertTrue(ok["hash_b_match"])
        self.assertEqual(dst.hash_a(), frozen_dst_a)
        self.assertEqual(dst.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), ["状態=試作2"])

    def test_import_rejects_tamper(self):
        src = _box("甲")
        dst = _box("甲")
        src.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "本筋"}],
        }, identity=1.0)
        payload = src.export_b()
        payload["hash_b"] = "0" * 64
        out = dst.import_b(payload, allow_evolution=True)
        self.assertFalse(out["accepted"])
        self.assertEqual(out["reason"], "TAMPER")
        self.assertEqual(dst.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), [])
        self.assertTrue(dst.cap.inner.intact())

    def test_import_accepts_matching_trusted(self):
        src = _box("甲")
        src.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "結論", "value": "隔離"}],
        }, identity=1.0)
        src.seal_b()
        payload = src.export_b()
        dst = _box("甲")
        out = dst.import_b(payload, trusted_hash=payload["hash_b"])
        self.assertTrue(out["accepted"])
        self.assertEqual(dst.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), ["結論=隔離"])
        self.assertTrue(out["hash_b_match"])

    def test_frame_is_incomplete_and_read_only(self):
        box = _box("甲")
        box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "delta": [{"field": "課題", "new_value": "散る"}],
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        frozen_a = box.hash_a()
        frozen_b = box.hash_b()
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        self.assertEqual(frame.open_slots, ["interpretation", "inference", "response"])
        self.assertEqual(frame.purpose, "AXIOM / BOX")
        self.assertEqual(frame.desk, "situation")
        self.assertEqual(frame.closed, ["alpha", "beta", "gamma", "delta", "is"])
        self.assertIn("試作2", " ".join(frame.state["is"]))
        self.assertTrue(any(row["new_value"] == "散る" for row in frame.changes["delta"]))
        self.assertEqual(frame.constraints["beta"]["name"], "甲")
        self.assertTrue(frame.intact)
        raw = box.render_json(frame)
        self.assertIn("open_slots", raw)
        self.assertNotIn("answer", raw)
        self.assertEqual(box.hash_a(), frozen_a)
        self.assertEqual(box.hash_b(), frozen_b)

    def test_open_slots_subtract_freedom(self):
        box = _box("甲")
        tight = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, open_slots=["response"])
        self.assertEqual(tight.open_slots, ["response"])
        wide = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, open_slots=["interpretation", "inference", "alternative", "response"])
        self.assertIn("alternative", wide.open_slots)
        self.assertGreater(len(wide.open_slots), len(tight.open_slots))

    def test_desks_subtract_materials(self):
        box = _box("甲")
        box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "delta": [{"field": "課題", "new_value": "散る"}],
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        ident = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, desk="identity")
        self.assertEqual(ident.closed, ["alpha", "beta", "gamma"])
        self.assertEqual(ident.changes, {})
        self.assertEqual(ident.state, {})
        self.assertIn("beta", ident.constraints)
        bare = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, desk="bare")
        self.assertEqual(bare.closed, ["alpha", "gamma", "is"])
        self.assertNotIn("beta", bare.constraints)
        self.assertIn("試作2", " ".join(bare.state["is"]))
        omitted = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, omit=["delta", "is"])
        self.assertEqual(omitted.closed, ["alpha", "beta", "gamma"])
        custom = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, include=["alpha", "is"])
        self.assertEqual(custom.desk, "custom")
        self.assertEqual(custom.closed, ["alpha", "is"])
        self.assertTrue(box.cap.inner.intact())

    def test_qvk_frame_leaves_axes_blank(self):
        box = _box("甲")
        box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        frozen_a = box.hash_a()
        frozen_b = box.hash_b()
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, desk="qvk")
        self.assertEqual(frame.desk, "qvk")
        self.assertEqual(frame.open_slots, ["Q", "V", "K"])
        self.assertEqual(frame.qvk["Q"], {"plus": None, "minus": None})
        self.assertEqual(frame.qvk["V"], {"plus": None, "minus": None})
        self.assertEqual(frame.qvk["K"], {"plus": None, "minus": None})
        self.assertIn("alpha", frame.closed)
        self.assertNotIn("delta", frame.closed)
        self.assertIn("試作2", " ".join(frame.state["is"]))
        prompt = box.infer_prompt(frame)
        self.assertIn("fill_gap", prompt)
        self.assertIn("start + ? = goal", prompt)
        self.assertIn("minus", prompt)
        self.assertIn('"method":["seal","desk","start_goal","analogy","minus","plus","stop"]', prompt.replace(" ", ""))
        self.assertEqual(frame.goal, "AXIOM / BOX")
        self.assertEqual(frame.gap, {"plus": None, "minus": None})
        self.assertIn("試作2", " ".join(frame.start["is"]))
        self.assertEqual(frame.analogy, {"source": None, "plus": None, "minus": None, "onto": None})
        guess = {
            "Q": {"plus": "今どの辺だ", "minus": "人格を書き換えよ"},
            "V": {"plus": "核を動かさない", "minus": "先回り"},
            "K": {"plus": "状態=試作2", "minus": "未測の住所"},
            "answer": "完成した",
        }
        out = box.accept_inference(frame, guess)
        self.assertTrue(out["ok"])
        self.assertFalse(out["wrote"])
        self.assertEqual(out["accepted"]["Q"]["plus"], "今どの辺だ")
        self.assertEqual(out["accepted"]["Q"]["minus"], "人格を書き換えよ")
        self.assertIn("answer", out["rejected"])
        prose = box.accept_inference(frame, {"Q": "今どの辺だ", "V": "核", "K": "既知"})
        self.assertFalse(prose["ok"])
        self.assertEqual(prose["reason"], "malformed_pm")
        self.assertEqual(box.hash_a(), frozen_a)
        self.assertEqual(box.hash_b(), frozen_b)
        self.assertEqual(box.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), ["状態=試作2"])

    def test_analogy_fills_open_slot_only(self):
        box = _box("甲")
        box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        frozen_a = box.hash_a()
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"}, desk="qvk")
        out = box.accept_inference(frame, {
            "gap": {"plus": "-1", "minus": "完成した和を出す"},
            "analogy": {
                "source": "状態=試作2",
                "plus": "今どこまで来たかだけ写す",
                "minus": "人格や未測の住所は写さない",
                "onto": "gap",
            }
        })
        self.assertTrue(out["ok"])
        self.assertEqual(out["accepted"]["gap"]["plus"], "-1")
        self.assertEqual(out["analogy"]["onto"], "gap")
        self.assertFalse(out["wrote"])
        bad = box.accept_inference(frame, {
            "analogy": {
                "source": "別件",
                "plus": "全部写す",
                "minus": "",
                "onto": "new_address",
            }
        })
        self.assertFalse(bad["ok"])
        self.assertIn("analogy", bad["malformed"])
        self.assertEqual(box.hash_a(), frozen_a)

    def test_llm_adapter_does_not_answer(self):
        from BOX import LLM
        self.assertRaises(NotImplementedError, LLM().complete, "{}")

    def test_start_goal_leave_middle_free(self):
        box = _box("甲")
        box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        frozen_a = box.hash_a()
        frozen_b = box.hash_b()
        frame = box.generate_frame(
            {"project": "AXIOM", "topic": "BOX"},
            start="状態=試作2",
            goal="今どの辺かを閉じた語で残す",
        )
        self.assertEqual(frame.form, "start + ? = goal")
        self.assertEqual(frame.start, "状態=試作2")
        self.assertEqual(frame.goal, "今どの辺かを閉じた語で残す")
        self.assertEqual(frame.gap, {"plus": None, "minus": None})
        self.assertIsNone(frame.kari["gap"]["plus"])
        self.assertIsNone(frame.hon)
        prompt = box.infer_prompt(frame)
        self.assertIn("taio", prompt)
        self.assertIn("seigo", prompt)
        self.assertIn("仮組み", prompt)
        self.assertIn("本組", prompt)
        self.assertEqual(frame.kari["taio"], {"plus": None, "minus": None, "cite": None})
        self.assertEqual(frame.kari["seigo"], {"plus": None, "minus": None, "cite": None})
        self.assertEqual(box.hash_a(), frozen_a)
        self.assertEqual(box.hash_b(), frozen_b)

    def test_dual_kari_is_not_state(self):
        box = _box("甲")
        box.commit({
            "gamma": {"project": "AXIOM", "topic": "BOX"},
            "is": [{"field": "状態", "value": "試作2"}],
        }, identity=1.0)
        frozen_b = box.hash_b()
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        out = box.accept_inference(frame, {
            "kari": {
                "taio": {"plus": "start=試作2 に合う", "minus": "核を作るな", "cite": "核を動かさない"},
                "seigo": {"plus": "IS と穴を混ぜるな", "minus": "完成した和", "cite": "状態=試作2"},
                "gap": {"plus": "今どこまでかだけ", "minus": "完成した和"},
                "analogy": {
                    "source": "状態=試作2",
                    "plus": "進度だけ写す",
                    "minus": "配札を混ぜるな",
                    "onto": "gap",
                },
            },
            "hon": {
                "gamma": {"project": "AXIOM", "topic": "BOX"},
                "is": [{"field": "結論", "value": "未完成"}],
                "grounds": [
                    {"source": "核を動かさない", "plus": "核は所与", "minus": "修復するな", "onto": "hon"},
                    {"source": "状態=試作2", "plus": "今の地点", "minus": "完成答え", "onto": "hon"},
                    {"source": "AXIOM", "plus": "今の山", "minus": "配札", "onto": "hon"},
                ],
                "jitsuyo": {"toward": "閉じた語で残す", "not": "配札へ越境するな", "cite": "AXIOM"},
            },
        })
        self.assertTrue(out["ok"])
        self.assertFalse(out["wrote"])
        self.assertTrue(out["hon_ready"])
        self.assertEqual(out["jitsuyo"]["toward"], "閉じた語で残す")
        self.assertEqual(out["kari"]["axes"]["taio"]["plus"], "start=試作2 に合う")
        self.assertEqual(out["kari"]["accepted"]["gap"]["plus"], "今どこまでかだけ")
        self.assertEqual(len(out["grounds"]), 3)
        self.assertEqual(out["hon"]["is"][0]["value"], "未完成")
        self.assertEqual(box.cap.is_lines({"project": "AXIOM", "topic": "BOX"}), ["状態=試作2"])
        self.assertEqual(box.hash_b(), frozen_b)

    def test_dual_hon_prose_is_not_packet(self):
        box = _box("甲")
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        out = box.accept_inference(frame, {
            "kari": {
                "taio": {"plus": "仮", "minus": "核", "cite": "核を動かさない"},
                "seigo": {"plus": "穴", "minus": "完成", "cite": "is"},
                "gap": {"plus": "仮", "minus": "完成"},
            },
            "hon": "完成した答え",
        })
        self.assertTrue(out["ok"])
        self.assertIsNone(out["hon"])
        self.assertEqual(out["hon_reason"], "hon_not_packet")
        self.assertFalse(out["wrote"])

    def test_kari_needs_two_fact_axes(self):
        box = _box("甲")
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        short = box.accept_inference(frame, {
            "kari": {"gap": {"plus": "仮", "minus": "完成"}},
        })
        self.assertFalse(short["ok"])
        self.assertEqual(short["kari_reason"], "axes_short")
        self.assertFalse(short["wrote"])

    def test_hon_needs_three_grounds(self):
        box = _box("甲")
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        raw = {
            "kari": {
                "taio": {"plus": "対応", "minus": "核を作る", "cite": "核を動かさない"},
                "seigo": {"plus": "整合", "minus": "完成和", "cite": "is"},
            },
            "hon": {
                "gamma": {"project": "AXIOM", "topic": "BOX"},
                "is": [{"field": "状態", "value": "試作2"}],
                "grounds": [
                    {"source": "核を動かさない", "plus": "核", "minus": "修復", "onto": "hon"},
                    {"source": "is", "plus": "地点", "minus": "完成", "onto": "hon"},
                ],
            },
        }
        short = box.accept_inference(frame, raw)
        self.assertFalse(short["hon_ready"])
        self.assertEqual(short["hon_reason"], "grounds_class_short")
        self.assertFalse(short["wrote"])
        raw["hon"]["grounds"].append(
            {"source": "AXIOM", "plus": "今の山", "minus": "配札", "onto": "hon"}
        )
        still = box.accept_inference(frame, raw)
        self.assertFalse(still["hon_ready"])
        self.assertEqual(still["hon_reason"], "jitsuyo_required")
        raw["hon"]["jitsuyo"] = {"toward": "閉じた語で残す", "not": "核を動かすな", "cite": "AXIOM"}
        ok = box.accept_inference(frame, raw)
        self.assertTrue(ok["hon_ready"])
        self.assertEqual(ok["jitsuyo"]["class"], "address")
        self.assertFalse(ok["wrote"])

    def test_jitsuyo_faces_address(self):
        box = _box("甲")
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        raw = {
            "kari": {
                "taio": {"plus": "対応", "minus": "核を作る", "cite": "核を動かさない"},
                "seigo": {"plus": "整合", "minus": "完成和", "cite": "is"},
            },
            "hon": {
                "gamma": {"project": "AXIOM", "topic": "BOX"},
                "is": [{"field": "状態", "value": "試作2"}],
                "grounds": [
                    {"source": "核を動かさない", "plus": "核", "minus": "修復", "onto": "hon"},
                    {"source": "is", "plus": "地点", "minus": "完成", "onto": "hon"},
                    {"source": "AXIOM", "plus": "今の山", "minus": "配札", "onto": "hon"},
                ],
                "jitsuyo": {"toward": "残す", "not": "越境", "cite": "核を動かさない"},
            },
        }
        bad = box.accept_inference(frame, raw)
        self.assertFalse(bad["hon_ready"])
        self.assertEqual(bad["hon_reason"], "jitsuyo_class")
        raw["hon"]["jitsuyo"]["cite"] = "AXIOM"
        ok = box.accept_inference(frame, raw)
        self.assertTrue(ok["hon_ready"])
        self.assertFalse(ok["wrote"])

    def test_cite_must_bind_frame(self):
        box = _box("甲")
        frame = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        unbound = box.accept_inference(frame, {
            "kari": {
                "taio": {"plus": "対応", "minus": "核を作る", "cite": "存在しない根拠"},
                "seigo": {"plus": "整合", "minus": "完成和", "cite": "is"},
            }
        })
        self.assertFalse(unbound["ok"])
        self.assertEqual(unbound["kari_reason"], "cite_unbound")
        wrong = box.accept_inference(frame, {
            "kari": {
                "taio": {"plus": "対応", "minus": "核を作る", "cite": "is"},
                "seigo": {"plus": "整合", "minus": "完成和", "cite": "核を動かさない"},
            }
        })
        self.assertFalse(wrong["ok"])
        self.assertEqual(wrong["kari_reason"], "cite_class")
        stale = box.generate_frame({"project": "AXIOM", "topic": "BOX"})
        stale.hash_a = "dead" * 8
        frozen = box.accept_inference(stale, {
            "kari": {
                "taio": {"plus": "対応", "minus": "核を作る", "cite": "核を動かさない"},
                "seigo": {"plus": "整合", "minus": "完成和", "cite": "is"},
            }
        })
        self.assertEqual(frozen["reason"], "frame_stale")
        self.assertFalse(frozen["wrote"])


if __name__ == "__main__":
    unittest.main()
