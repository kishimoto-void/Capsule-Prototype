#!/usr/bin/env python3
"""実用層だけ見る。向きは本組の条件。状態ではない。"""
import unittest

from axiom_min3 import Alpha, Beta, BetaFact, Inner, Write
from BOX import BOX
from runtime import Runtime


def _box() -> BOX:
    inner = Inner(
        Alpha(),
        Beta(name="甲", tone="短い", center="本筋", values=("核を動かさない",)),
        facts=(BetaFact("K-1", "役", "甲"),),
    )
    return BOX.from_inner(inner, name="甲")


FILT = {"time_label": "2026-09", "project": "AXIOM", "topic": "BOX"}
KARI = {
    "taio": {"plus": "核は所与", "minus": "核を作るな", "cite": "核を動かさない"},
    "seigo": {"plus": "穴を残す", "minus": "完成和", "cite": "is"},
}
GROUNDS = [
    {"source": "核を動かさない", "plus": "核", "minus": "修復", "onto": "hon"},
    {"source": "is", "plus": "地点", "minus": "完成", "onto": "hon"},
    {"source": "AXIOM", "plus": "今の山", "minus": "配札", "onto": "hon"},
]
HON = {
    "gamma": dict(FILT),
    "delta": [{"field": "状態", "new_value": "試作2"}],
    "is": [{"field": "状態", "value": "試作2"}],
    "grounds": list(GROUNDS),
}
JITSUYO = {"toward": "閉じた語で残す", "not": "配札へ越境するな", "cite": "AXIOM"}


def _dual(jitsuyo=None, hon=None, kari=None):
    body = {"kari": dict(kari or KARI), "hon": dict(hon or HON)}
    if jitsuyo is not None:
        body["hon"] = {**body["hon"], "jitsuyo": jitsuyo}
    return body


class TestJitsuyo(unittest.TestCase):
    def setUp(self):
        self.box = _box()
        self.frame = self.box.generate_frame(FILT)
        self.frozen_a = self.box.hash_a()
        self.frozen_b = self.box.hash_b()

    def test_kari_does_not_need_heading(self):
        out = self.box.accept_inference(self.frame, {"kari": dict(KARI)})
        self.assertTrue(out["ok"])
        self.assertIsNone(out["jitsuyo"])
        self.assertFalse(out["hon_ready"])
        self.assertFalse(out["wrote"])
        self.assertEqual(self.box.hash_b(), self.frozen_b)

    def test_hon_without_heading_is_not_ready(self):
        out = self.box.accept_inference(self.frame, _dual())
        self.assertFalse(out["hon_ready"])
        self.assertEqual(out["hon_reason"], "jitsuyo_required")
        self.assertFalse(out["wrote"])
        self.assertEqual(self.box.cap.is_lines(FILT), [])

    def test_heading_short_is_rejected(self):
        cases = [
            ({"toward": "", "not": "越境", "cite": "AXIOM"}, "jitsuyo_short"),
            ({"toward": "残す", "not": "", "cite": "AXIOM"}, "jitsuyo_short"),
            ({"toward": "残す", "not": "越境", "cite": ""}, "jitsuyo_short"),
            ({"toward": "残す", "cite": "AXIOM"}, "jitsuyo_short"),
            ("前へ進め", "jitsuyo_bad"),
            ({"toward": "残す", "not": "越境", "cite": "AXIOM", "wish": "便利"}, "jitsuyo_bad"),
        ]
        for heading, reason in cases:
            out = self.box.accept_inference(self.frame, _dual(heading))
            self.assertFalse(out["hon_ready"], reason)
            self.assertEqual(out["hon_reason"], reason)

    def test_heading_must_cite_address(self):
        kernel = self.box.accept_inference(self.frame, _dual({"toward": "残す", "not": "越境", "cite": "核を動かさない"}))
        self.assertEqual(kernel["hon_reason"], "jitsuyo_class")
        state = self.box.accept_inference(self.frame, _dual({"toward": "残す", "not": "越境", "cite": "is"}))
        self.assertEqual(state["hon_reason"], "jitsuyo_class")
        ghost = self.box.accept_inference(self.frame, _dual({"toward": "残す", "not": "越境", "cite": "配札"}))
        self.assertEqual(ghost["hon_reason"], "jitsuyo_unbound")
        ok = self.box.accept_inference(self.frame, _dual(JITSUYO))
        self.assertTrue(ok["hon_ready"])
        self.assertEqual(ok["jitsuyo"]["class"], "address")
        self.assertFalse(ok["wrote"])

    def test_heading_is_not_state(self):
        out = self.box.accept_inference(self.frame, _dual(JITSUYO))
        self.assertTrue(out["hon_ready"])
        self.assertEqual(self.box.cap.is_lines(FILT), [])
        self.assertEqual(self.box.hash_a(), self.frozen_a)
        self.assertEqual(self.box.hash_b(), self.frozen_b)
        lines = "\n".join(self.box.cap.is_lines(FILT))
        self.assertNotIn("閉じた語で残す", lines)
        self.assertNotIn("配札へ越境するな", lines)

    def test_outer_heading_is_accepted(self):
        raw = {"kari": dict(KARI), "hon": dict(HON), "jitsuyo": dict(JITSUYO)}
        out = self.box.accept_inference(self.frame, raw)
        self.assertTrue(out["hon_ready"])
        self.assertEqual(out["jitsuyo"]["cite"], "AXIOM")

    def test_runtime_heading_needed_before_commit(self):
        rt = Runtime(self.box, name="甲")
        rt.bind(FILT)
        blocked = rt.turn("状態を残す", raw=_dual(), identity=1.0)
        self.assertFalse(blocked["committed"])
        self.assertEqual(blocked["commit"]["reason"], "jitsuyo_required")
        self.assertEqual(self.box.cap.is_lines(FILT), [])
        out = rt.turn("状態を残す", raw=_dual(JITSUYO), identity=1.0, authorize=True)
        self.assertTrue(out["committed"])
        self.assertEqual(out["write"], Write.IS)
        self.assertEqual(self.box.cap.is_lines(FILT), ["状態=試作2"])
        self.assertNotIn("閉じた語で残す", "\n".join(self.box.cap.is_lines(FILT)))
        self.assertEqual(out["hash_a_after"], self.frozen_a)
        self.assertFalse(out["hash_a_moved"])

    def test_runtime_heading_does_not_override_gamma(self):
        rt = Runtime(self.box, name="甲")
        rt.bind(FILT)
        raw = _dual(JITSUYO, hon={
            "gamma": {"time_label": "2026-09", "project": "AXIOM", "topic": "配札"},
            "is": [{"field": "状態", "value": "枚数は未確定"}],
            "grounds": list(GROUNDS),
        })
        out = rt.turn("配札も一緒に", raw=raw, identity=1.0)
        self.assertFalse(out["committed"])
        self.assertEqual(out["propose"]["reason"], "gamma_mismatch")
        self.assertEqual(self.box.cap.is_lines({"project": "AXIOM", "topic": "配札"}), [])

    def test_runtime_heading_does_not_skip_identity(self):
        rt = Runtime(self.box, name="甲")
        rt.bind(FILT)
        out = rt.turn("状態を残す", raw=_dual(JITSUYO))
        self.assertFalse(out["committed"])
        self.assertEqual(out["commit"]["reason"], "identity_required")
        self.assertEqual(self.box.cap.is_lines(FILT), [])


if __name__ == "__main__":
    unittest.main()
