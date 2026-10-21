"""★ 负例测试：`scripts/check_assumption_ledger.py` 必须能抓到真实违规。

依据 `docs/known-facts.md` 事实 62：「一个门禁『写了』不等于它『有效』」。
依据 `docs/text-to-cad-lessons-verdict.md` §7：负例测试三条判据。

★ 本文件**独立**构造输入，不依赖门禁自己的 `selftest()` ——
若判据写窄了，本测试会红而 `selftest()` 可能仍绿（那是自证盲区）。
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_gate():
    p = ROOT / "scripts" / "check_assumption_ledger.py"
    spec = importlib.util.spec_from_file_location("gate_assumption_ledger", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class AssumptionLedgerGateTest(unittest.TestCase):
    """★ 门禁的三条判据：封闭词表 / 已验证须带证据 / 未验证不得当证据。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = _load_gate()

    def _validate(self, line: str) -> list[str]:
        rows, probs = self.gate.parse_ledger(line)
        return self.gate.validate(rows, probs)

    # ── 判据①：封闭词表 ──────────────────────────────────────────────
    def test_illegal_status_reported(self) -> None:
        """★ 状态不在 open/confirmed/refuted 内必须报。"""
        for bad in ("done", "verified", "OK", "", "已确认"):
            with self.subTest(status=bad):
                probs = self._validate("| AS001 | 某假设 | 4-assumption | %s | 证据 |" % bad)
                self.assertTrue(any("状态" in p for p in probs),
                                "★ 漏报：非法状态 %r 没被抓到（实得 %r）" % (bad, probs))

    def test_illegal_tier_reported(self) -> None:
        """★ 档位不在四档内必须报（★ 封闭词表，同上游 closed vocabularies）。"""
        for bad in ("5-猜的", "official", "", "TBD"):
            with self.subTest(tier=bad):
                probs = self._validate("| AS002 | 某假设 | %s | open | - |" % bad)
                self.assertTrue(any("档位" in p for p in probs),
                                "★ 漏报：非法档位 %r 没被抓到" % bad)

    # ── 判据②：已验证必须带证据 ──────────────────────────────────────
    def test_confirmed_without_evidence_reported(self) -> None:
        """★ confirmed 无证据必须报 —— 「已验证」不能是空话。"""
        for placeholder in ("-", "—", "", "N/A", "待补", "TBD"):
            with self.subTest(evidence=placeholder):
                probs = self._validate(
                    "| AS003 | 某假设 | 3-measured | confirmed | %s |" % placeholder)
                self.assertTrue(any("没有证据" in p for p in probs),
                                "★ 漏报：confirmed 的占位证据 %r 被当成真证据" % placeholder)

    def test_refuted_without_evidence_reported(self) -> None:
        """★ refuted 同样要证据（★ 证伪也要有依据）。"""
        probs = self._validate("| AS004 | 某假设 | 3-measured | refuted | - |")
        self.assertTrue(any("没有证据" in p for p in probs),
                        "★ 漏报：refuted 无证据未被抓到")

    def test_open_needs_no_evidence(self) -> None:
        """★ open 不需要证据（★ 它就是「还没验证」，要求证据是悖论）。"""
        probs = self._validate("| AS005 | 某假设 | 4-assumption | open | - |")
        self.assertEqual(probs, [], "★ 误报：open 无证据被报 %r" % (probs,))

    # ── 判据③：id 唯一 ────────────────────────────────────────────────
    def test_duplicate_id_reported(self) -> None:
        """★ id 重复必须报（★ 否则「未验证不得当证据」的查表会误伤）。"""
        rows, probs = self.gate.parse_ledger(
            "| AS006 | 假设一 | 4-assumption | open | - |\n"
            "| AS006 | 假设二 | 4-assumption | open | - |")
        probs = self.gate.validate(rows, probs)
        self.assertTrue(any("重复" in p for p in probs),
                        "★ 漏报：重复 id 未被抓到")

    # ── 合规必须放过 ──────────────────────────────────────────────────
    def test_compliant_rows_pass(self) -> None:
        """★ 全部合规的台账必须零问题（★ 防恒红门禁，事实 53 同族）。"""
        text = (
            "| AS101 | 假设一 | 1-user | confirmed | 用户 2026-10-19 会话原话 |\n"
            "| AS102 | 假设二 | 2-official | confirmed | `docs/known-facts.md` 事实 62 |\n"
            "| AS103 | 假设三 | 3-measured | refuted | `python scripts/x.py` 输出 0 命中 |\n"
            "| AS104 | 假设四 | 4-assumption | open | - |\n"
        )
        rows, probs = self.gate.parse_ledger(text)
        self.assertEqual(self.gate.validate(rows, probs), [],
                         "★ 误报：合规台账被报")

    # ── 格式 ──────────────────────────────────────────────────────────
    def test_malformed_row_reported(self) -> None:
        """★ 像表格行但列数不对必须报（★ 否则整行被静默跳过 = 假绿）。"""
        probs = self._validate("| AS007 | 只有三列 | open |")
        self.assertTrue(probs, "★ 漏报：列数不足的表格行被静默跳过")

    # ── 真实台账必须过 ────────────────────────────────────────────────
    def test_real_ledger_passes(self) -> None:
        """★ 仓库里真实的台账必须通过（★ 这是门禁的实际工作负载）。"""
        problems = self.gate.check()
        self.assertEqual(problems, [],
                         "★ 真实台账不通过：%r" % (problems,))

    def test_selftest_passes(self) -> None:
        """★ 门禁自带自证也必须过。"""
        self.assertTrue(self.gate.selftest(), "★ 门禁 selftest() 失败")


if __name__ == "__main__":
    unittest.main(verbosity=2)
