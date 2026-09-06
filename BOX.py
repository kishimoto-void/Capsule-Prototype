#!/usr/bin/env python3
"""BOX — detachable work surface around min3 Capsule.

Not a memory layer. Not intelligence. Not Concierge.
Capsule = what is sealed. BOX = how it is handled now.

    Hash-A  Capsule.Inner (αβ + facts)
    Hash-B  Capsule.hash_b() — integrity of Δ/IS/pending. not sealed into A
    Frame   incomplete problem JSON. start and goal are given. middle stays free
    write   generate_frame does not write Capsule
    kari    provisional middle. never state
    hon     closed packet candidate. BOX does not auto-commit it
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from axiom_min3 import Capsule, Inner, Write, gamma_line, hash_mutable, parse_packet

DEFAULT_OPEN_SLOTS = ("interpretation", "inference", "response")
MATERIALS = ("alpha", "beta", "gamma", "delta", "is")
DESKS = {
    "identity": ("alpha", "beta", "gamma"),
    "situation": ("alpha", "beta", "gamma", "delta", "is"),
    "bare": ("alpha", "gamma", "is"),
    "qvk": ("alpha", "beta", "gamma", "is"),
}
QVK_SLOTS = ("Q", "V", "K")
QVK_AXES = {
    "Q": "問い。今何を問うているか。BOXは埋めない",
    "V": "価値。何を重く見るか。BOXは埋めない",
    "K": "既知。何が確定済みか。BOXは埋めない",
}


def pm_blank(keys=None) -> dict:
    return {k: {"plus": None, "minus": None} for k in (keys or QVK_SLOTS)}


METHOD = (
    "seal",
    "desk",
    "start_goal",
    "analogy",
    "minus",
    "plus",
    "stop",
)
METHOD_STEPS = {
    "seal": "Hash-A と closed の αβ だけを真と見る。核は作らない。",
    "desk": "closed に無い γΔIS は無い。住所を広げない。",
    "start_goal": "start と goal は与える。間の ? は仮組み。1+1=2 の完成形は出さない。",
    "analogy": "source は start / closed から取る。onto は gap。未知の住所へ写さない。",
    "minus": "先に引く。goal に届かせないもの、写してはいけない対応を minus に書く。",
    "plus": "引けてから ? を足す。minus と矛盾する plus は書かない。",
    "stop": "完成した一つの答えに畳まない。仮組みは書かない。本組だけ閉じた packet にする。",
}


FORM = "start + ? = goal"


def analogy_blank() -> dict:
    return {"source": None, "plus": None, "minus": None, "onto": None}


def gap_blank() -> dict:
    return {"plus": None, "minus": None}


def kari_blank() -> dict:
    return {"gap": gap_blank(), "analogy": analogy_blank(), "note": None}


def split_dual(filled: Any) -> tuple[Any, Any]:
    """Outer {kari, hon} is dual. Legacy fills are kari only."""
    if not isinstance(filled, dict):
        return filled, None
    if "kari" in filled or "hon" in filled:
        return filled.get("kari"), filled.get("hon")
    return filled, None


def as_analogy(value: Any) -> Optional[dict]:
    if not isinstance(value, dict):
        return None
    if set(value) - {"source", "plus", "minus", "onto"}:
        return None
    if any(k not in value for k in ("source", "plus", "minus", "onto")):
        return None
    return {k: value.get(k) for k in ("source", "plus", "minus", "onto")}


def as_pm(value: Any) -> Optional[dict]:
    if not isinstance(value, dict):
        return None
    if set(value) - {"plus", "minus"}:
        return None
    if "plus" not in value or "minus" not in value:
        return None
    return {"plus": value.get("plus"), "minus": value.get("minus")}


@dataclass
class Frame:
    """Deliberately incomplete reasoning frame. None / open_slots are left to the LLM."""

    purpose: Optional[str] = None
    constraints: dict = field(default_factory=dict)
    context: dict = field(default_factory=dict)
    changes: dict = field(default_factory=dict)
    state: dict = field(default_factory=dict)
    open_slots: list = field(default_factory=list)
    closed: list = field(default_factory=list)
    desk: str = "situation"
    qvk: dict = field(default_factory=dict)
    analogy: dict = field(default_factory=dict)
    start: Any = None
    goal: Any = None
    gap: dict = field(default_factory=dict)
    kari: dict = field(default_factory=dict)
    hon: Any = None
    form: str = FORM
    hash_a: str = ""
    hash_b: str = ""
    intact: bool = True

    def to_dict(self) -> dict:
        return {
            "purpose": self.purpose,
            "constraints": self.constraints,
            "context": self.context,
            "changes": self.changes,
            "state": self.state,
            "closed": list(self.closed),
            "open_slots": list(self.open_slots),
            "desk": self.desk,
            "qvk": dict(self.qvk),
            "analogy": dict(self.analogy) if self.analogy else analogy_blank(),
            "form": self.form or FORM,
            "start": self.start,
            "goal": self.goal,
            "gap": dict(self.gap) if self.gap else gap_blank(),
            "kari": dict(self.kari) if self.kari else kari_blank(),
            "hon": self.hon,
            "method": list(METHOD),
            "hash_a": self.hash_a,
            "hash_b": self.hash_b,
            "intact": self.intact,
        }


class LLM:
    """Model adapter. BOX does not complete the frame."""

    def complete(self, frame_json: str) -> str:
        raise NotImplementedError("BOX does not generate the answer")


class BOX:
    def __init__(self, capsule: Capsule, name: str = ""):
        if not isinstance(capsule, Capsule):
            raise TypeError("BOX mounts axiom_min3.Capsule only")
        self.name = name
        self.cap = capsule
        self.trusted_b = self.hash_b()
        self.proposal: Optional[dict] = None

    def hash_a(self) -> str:
        return self.cap.inner.hash_a

    def mutable(self) -> dict:
        return self.cap.mutable_payload()

    def hash_b(self) -> str:
        return self.cap.hash_b()

    def seal_b(self) -> str:
        """Accept current mutable as trusted. Does not touch Hash-A."""
        self.trusted_b = self.hash_b()
        return self.trusted_b

    def check(self) -> dict:
        current_b = self.hash_b()
        return {
            "name": self.name,
            "hash_a": self.hash_a(),
            "hash_a_intact": self.cap.inner.intact(),
            "hash_b": current_b,
            "trusted_b": self.trusted_b,
            "hash_b_match": current_b == self.trusted_b,
            "pending": bool(self.cap.pending() or self.cap.pending_is()),
            "proposal": self.proposal is not None,
        }

    def _report(self, ingest: Optional[dict] = None, **extra) -> dict:
        out = self.check()
        out.update(extra)
        out["ingest"] = ingest
        if ingest:
            for k in ("write", "is", "delta", "dropped", "evicted", "wrote", "gamma"):
                if k in ingest and k not in extra:
                    out[k] = ingest[k]
        return out

    def match(self, other: "BOX") -> dict:
        """Structural match against another sealed box. Not a meaning score."""
        if not isinstance(other, BOX):
            raise TypeError("match needs a BOX")
        return {
            "same_a": self.hash_a() == other.hash_a() and self.cap.inner.intact() and other.cap.inner.intact(),
            "same_b": self.hash_b() == other.hash_b(),
            "a_intact": self.cap.inner.intact(),
        }

    def propose(self, raw: Any) -> dict:
        """Parse only. LLM text is not a commit."""
        pkt = parse_packet(raw)
        self.proposal = pkt
        return {"ok": pkt is not None, "packet": pkt}

    def commit(self, raw: Any = None, human: bool = False, identity: Optional[float] = None, grain: str = "month") -> Optional[dict]:
        """Write through Capsule.ingest only. Hash-A must not move.

        identity is required. missing score does not open the 0.20 gate.
        Does not auto seal Hash-B. caller sees hash_b_match and may seal_b().
        """
        src = raw if raw is not None else self.proposal
        if src is None:
            return None
        if identity is None:
            return self._report(ok=False, write=Write.NONE, reason="identity_required")
        frozen_a = self.hash_a()
        out = self.cap.ingest(src, human=human, identity=identity, grain=grain)
        if out is not None:
            self.proposal = None
        if self.hash_a() != frozen_a:
            raise RuntimeError("Hash-A moved on commit")
        if out is None:
            return self._report(ok=False, write=self.cap.last_write, reason="ingest_rejected")
        return self._report(ok=True, reason="", ingest=out)

    def approve(self, keep_history: bool = True) -> dict:
        frozen_a = self.hash_a()
        d = self.cap.approve_pending(keep_history=keep_history)
        if self.hash_a() != frozen_a:
            raise RuntimeError("Hash-A moved on approve")
        return self._report(ok=d is not None, approved=d, write=self.cap.last_write)

    def approve_is(self) -> dict:
        frozen_a = self.hash_a()
        line = self.cap.approve_is()
        if self.hash_a() != frozen_a:
            raise RuntimeError("Hash-A moved on approve_is")
        return self._report(ok=line is not None, approved=line, write=self.cap.last_write)

    def render(self, user: str, filt: dict, exact: bool = True, grain: str = "month") -> str:
        return self.cap.render(user, filt, exact=exact, grain=grain)

    def situation(self, filt: dict, exact: bool = True, grain: str = "month") -> dict:
        """Read-only view of γ / Δ / IS. Not a second store."""
        addresses = [asdict(g) for g in self.cap.query_gamma(filt, exact=exact, grain=grain)]
        changes = [
            {"gamma": asdict(g), "field": d.field, "new_value": d.new_value, "old_value": d.old_value}
            for g, d in self.cap.query_delta(filt, exact=exact, grain=grain)
        ]
        return {
            "gamma": dict(filt or {}),
            "addresses": addresses,
            "delta": changes,
            "is": list(self.cap.is_lines(filt, exact=exact, grain=grain)),
        }

    def generate_frame(
        self,
        filt: dict,
        *,
        purpose: Optional[str] = None,
        open_slots: Optional[list] = None,
        desk: str = "situation",
        include: Optional[list] = None,
        omit: Optional[list] = None,
        exact: bool = True,
        grain: str = "month",
        start: Any = None,
        goal: Any = None,
    ) -> Frame:
        """Build an incomplete frame. Does not write Capsule. Does not answer.

        start and goal are given. middle stays blank (kari). hon is not filled here.
        desk / include / omit subtract materials. open_slots subtract freedom.
        """
        if include is not None:
            used = tuple(include)
            desk_name = "custom"
        elif desk not in DESKS:
            raise ValueError(f"unknown desk: {desk}")
        else:
            used = DESKS[desk]
            desk_name = desk
        skip = set(omit or ())
        used = tuple(x for x in used if x in MATERIALS and x not in skip)
        inn = self.cap.inner
        sit = self.situation(filt, exact=exact, grain=grain)
        if open_slots is not None:
            slots = list(open_slots)
        elif desk_name == "qvk":
            slots = list(QVK_SLOTS)
        else:
            slots = list(DEFAULT_OPEN_SLOTS)
        qvk = {}
        if desk_name == "qvk" or any(s in QVK_SLOTS for s in slots):
            qvk = pm_blank()
        constraints: dict = {}
        if "alpha" in used:
            constraints["alpha"] = list(inn.alpha.rules)
        if "beta" in used:
            constraints["beta"] = {
                "name": inn.beta.name,
                "tone": inn.beta.tone,
                "center": inn.beta.center,
                "values": list(inn.beta.values),
            }
            constraints["facts"] = list(inn.fact_lines())
        context: dict = {}
        if "gamma" in used:
            context = {"filter": sit["gamma"], "addresses": sit["addresses"]}
        changes: dict = {}
        if "delta" in used:
            changes = {"delta": sit["delta"]}
        state: dict = {}
        if "is" in used:
            state = {"is": sit["is"], "pending": bool(self.cap.pending() or self.cap.pending_is())}
        if purpose is not None:
            why = purpose
        elif "gamma" in used:
            why = gamma_line(dict(filt or {}))
        else:
            why = None
        start_val = start if start is not None else {"is": sit["is"], "delta": sit["delta"] if "delta" in used else []}
        goal_val = goal if goal is not None else why
        return Frame(
            purpose=why,
            constraints=constraints,
            context=context,
            changes=changes,
            state=state,
            open_slots=slots,
            closed=list(used),
            desk=desk_name,
            qvk=qvk,
            analogy=analogy_blank(),
            start=start_val,
            goal=goal_val,
            gap=gap_blank(),
            kari=kari_blank(),
            hon=None,
            form=FORM,
            hash_a=self.hash_a(),
            hash_b=self.hash_b(),
            intact=inn.intact(),
        )

    def render_json(self, frame: Frame) -> str:
        return json.dumps(frame.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def infer_prompt(self, frame: Frame) -> str:
        """Instruction for an LLM. Think in plus/minus. Do not write Capsule."""
        keys = list(frame.open_slots) or list(QVK_SLOTS)
        blank = pm_blank(keys)
        if frame.qvk:
            for k, v in frame.qvk.items():
                if k in blank and isinstance(v, dict):
                    blank[k] = {"plus": v.get("plus"), "minus": v.get("minus")}
        return json.dumps(
            {
                "task": "fill_gap",
                "form": frame.form or FORM,
                "not": "1+1=2 の完成形を一つの答えとして出すこと",
                "method": list(METHOD),
                "steps": METHOD_STEPS,
                "rule": "start と goal は所与。間の ? は仮組み。本組は閉じた packet だけ。完成した和を書くな。住所を広げるな。Capsule に書き戻すな。",
                "dual": {
                    "kari": "仮組み。gap / analogy / open_slots だけ。状態ではない。",
                    "hon": "本組。閉じた {gamma, delta, is} だけ。identity 無しでは書かない。",
                },
                "plus": "start から goal へ足すもの",
                "minus": "start から goal へ引くもの・写してはいけないもの",
                "analogy": "start / closed の既知を gap へ写す。onto は gap か open_slots。",
                "axes": QVK_AXES if frame.desk == "qvk" or frame.qvk else {},
                "closed": frame.closed,
                "open_slots": list(frame.open_slots) + (["gap"] if "gap" not in frame.open_slots else []),
                "start": frame.start,
                "goal": frame.goal,
                "blank": blank,
                "gap": frame.gap or gap_blank(),
                "kari_blank": frame.kari or kari_blank(),
                "hon": None,
                "analogy_blank": frame.analogy or analogy_blank(),
                "frame": frame.to_dict(),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def accept_inference(self, frame: Frame, filled: Any) -> dict:
        """Take plus/minus fills as 仮組み. Optional 本組 packet is parsed only.

        Does not commit to Capsule. hon is a candidate, not a write.
        """
        if isinstance(filled, str):
            try:
                filled = json.loads(filled)
            except json.JSONDecodeError:
                return {"ok": False, "reason": "bad_inference", "qvk": dict(frame.qvk), "wrote": False, "kari": None, "hon": None}
        if not isinstance(filled, dict):
            return {"ok": False, "reason": "bad_inference", "qvk": dict(frame.qvk), "wrote": False, "kari": None, "hon": None}
        kari_raw, hon_raw = split_dual(filled)
        hon = parse_packet(hon_raw) if hon_raw is not None else None
        hon_reason = ""
        if hon_raw is not None and hon is None:
            hon_reason = "hon_not_packet"
        if kari_raw is None and hon is None and hon_raw is None:
            return {"ok": False, "reason": "empty", "qvk": dict(frame.qvk), "wrote": False, "kari": None, "hon": None}
        allowed = set(frame.open_slots) | set(frame.qvk) | {"gap"}
        accepted = {}
        malformed = []
        analogy = None
        rejected = []
        if isinstance(kari_raw, dict):
            for k in allowed:
                if k not in kari_raw or kari_raw[k] is None:
                    continue
                pair = as_pm(kari_raw[k])
                if pair is None:
                    malformed.append(k)
                    continue
                accepted[k] = pair
            if "analogy" in kari_raw and kari_raw["analogy"] is not None:
                analogy = as_analogy(kari_raw["analogy"])
                if analogy is None:
                    malformed.append("analogy")
                elif analogy.get("onto") not in (None, "") and analogy.get("onto") not in allowed:
                    malformed.append("analogy")
                    analogy = None
            rejected = [k for k in kari_raw if k not in allowed and k not in {"analogy", "note"}]
        elif kari_raw is not None:
            malformed.append("kari")
        if not isinstance(filled.get("kari"), dict) and "kari" not in filled and "hon" not in filled:
            # legacy body already handled as kari_raw == filled
            pass
        if "kari" in filled or "hon" in filled:
            rejected.extend(k for k in filled if k not in {"kari", "hon"} and k not in rejected)
        kari_ok = (bool(accepted) or analogy is not None) and not malformed
        if isinstance(kari_raw, dict) and not accepted and analogy is None and not malformed and hon is not None:
            kari_ok = False
        ok = (kari_ok or hon is not None) and not malformed
        if hon_raw is not None and hon is None and not kari_ok:
            ok = False
        reason = "proposal" if ok else ("malformed_pm" if malformed else (hon_reason or "empty"))
        return {
            "ok": ok,
            "reason": reason,
            "qvk": {**pm_blank(), **{k: accepted[k] for k in accepted if k in QVK_SLOTS}},
            "analogy": analogy,
            "accepted": accepted,
            "rejected": rejected,
            "malformed": malformed,
            "wrote": False,
            "kari": {"accepted": accepted, "analogy": analogy, "note": (kari_raw or {}).get("note") if isinstance(kari_raw, dict) else None} if (accepted or analogy) else None,
            "hon": hon,
            "hon_reason": hon_reason,
        }

    def export_b(self) -> dict:
        """Carry mutable state + claimed Hash-B. Hash-A is reference only."""
        return {
            "name": self.name,
            "mutable": self.mutable(),
            "hash_b": self.hash_b(),
            "hash_a": self.hash_a(),
        }

    def import_b(
        self,
        payload: Any,
        trusted_hash: Optional[str] = None,
        allow_evolution: bool = False,
    ) -> dict:
        """Accept mutable only if claimed Hash-B matches content.

        provenance: claimed must equal trusted_hash or current trusted_b
        unless allow_evolution. Does not write Hash-A. Does not load adopted.
        """
        frozen_a = self.hash_a()
        if not isinstance(payload, dict) or "mutable" not in payload or "hash_b" not in payload:
            return self._report(ok=False, accepted=False, reason="bad_payload")
        mutable = payload.get("mutable")
        if not isinstance(mutable, dict):
            return self._report(ok=False, accepted=False, reason="bad_payload")
        claimed = payload.get("hash_b")
        computed = hash_mutable(mutable)
        if claimed != computed:
            return self._report(ok=False, accepted=False, reason="TAMPER", claimed_b=claimed, computed_b=computed)
        expected = self.trusted_b if trusted_hash is None else trusted_hash
        if not allow_evolution and expected and claimed != expected:
            return self._report(ok=False, accepted=False, reason="PROVENANCE", claimed_b=claimed, expected_b=expected)
        self.cap.restore({
            "deltas": mutable.get("deltas") or [],
            "is": mutable.get("is") or {},
            "pending": mutable.get("pending") or [],
            "is_pending": mutable.get("is_pending") or [],
        })
        if self.hash_a() != frozen_a:
            raise RuntimeError("Hash-A moved on import_b")
        self.trusted_b = self.hash_b()
        self.proposal = None
        return self._report(ok=True, accepted=True, reason="OK")

    def mount(self, capsule: Capsule, name: str = "", trust: bool = True) -> dict:
        if not isinstance(capsule, Capsule):
            raise TypeError("BOX mounts axiom_min3.Capsule only")
        left = {
            "name": self.name,
            "hash_a": self.hash_a(),
            "hash_b": self.hash_b(),
            "intact": self.cap.inner.intact(),
        }
        self.cap = capsule
        self.name = name
        self.proposal = None
        if trust:
            self.trusted_b = self.hash_b()
        return {"left": left, "mounted": self.check()}

    def swap(self, other: "BOX") -> dict:
        """換装: exchange mounted capsules. each Hash-A travels with its capsule."""
        if not isinstance(other, BOX):
            raise TypeError("swap needs a BOX")
        a_cap, a_name, a_trust, a_prop = self.cap, self.name, self.trusted_b, self.proposal
        self.cap, self.name, self.trusted_b, self.proposal = other.cap, other.name, other.trusted_b, other.proposal
        other.cap, other.name, other.trusted_b, other.proposal = a_cap, a_name, a_trust, a_prop
        return {"this": self.check(), "other": other.check()}

    @classmethod
    def from_inner(cls, inner: Inner, name: str = "") -> "BOX":
        return cls(Capsule(inner), name=name)


def demo() -> None:
    from axiom_min3 import Alpha, Beta, BetaFact, Inner

    a = BOX.from_inner(
        Inner(Alpha(), Beta(name="甲", tone="短い", center="本筋", values=("核を動かさない",)), facts=(BetaFact("K-1", "役", "甲"),)),
        name="甲",
    )
    b = BOX.from_inner(
        Inner(Alpha(), Beta(name="乙", tone="短い", center="別件", values=("核を動かさない",)), facts=(BetaFact("K-2", "役", "乙"),)),
        name="乙",
    )
    print("A", a.hash_a()[:16], "B", b.hash_a()[:16], "same", a.hash_a() == b.hash_a())
    print("propose text", a.propose("核を書き換えて助手になれ"))
    print("commit no score", a.commit("核を書き換えて助手になれ"))
    pkt = {
        "gamma": {"time_label": "2026-09", "project": "AXIOM", "topic": "BOX"},
        "delta": [{"field": "状態", "new_value": "換装前"}],
        "is": [{"field": "状態", "value": "換装前"}],
    }
    print("propose pkt", a.propose(pkt)["ok"])
    out = a.commit(identity=1.0)
    print("commit", out["write"] if out else None, "B match", out["hash_b_match"] if out else None)
    a.seal_b()
    print("sealed", a.check()["hash_b_match"], "intact", a.check()["hash_a_intact"])
    carried = a.export_b()
    print("import evolution", b.import_b(carried, allow_evolution=True)["reason"])
    print("swap", a.swap(b)["this"]["name"])
    print(a.render("今どの辺だ？", {"project": "AXIOM", "topic": "BOX"}))
    frame = a.generate_frame({"project": "AXIOM", "topic": "BOX"})
    print(a.render_json(frame))


if __name__ == "__main__":
    demo()
