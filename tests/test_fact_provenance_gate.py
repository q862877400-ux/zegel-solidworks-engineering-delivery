"""★ 负例测试：`scripts/check_fact_provenance.py` 必须能抓到真实的违规。

依据 `docs/known-facts.md` 事实 62：「一个门禁『写了』不等于它『有效』—— 负例测试是唯一的证明」。
依据 `docs/text-to-cad-lessons-verdict.md` §7：负例测试的三条判据（违规必报 / 合规必过 / 真实样本）。

★ 本文件不只测 `selftest()`，而是**独立**构造输入 —— 若门禁的正则写窄了/写宽了，
本测试会红，而门禁自己的 `selftest()` 可能仍然绿（★ 那是自证盲区）。
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load_gate():
    """★ 按路径加载门禁模块（★ 它不是包，import 不了）。"""
    p = ROOT / "scripts" / "check_fact_provenance.py"
    spec = importlib.util.spec_from_file_location("gate_fact_provenance", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class FactProvenanceGateTest(unittest.TestCase):
    """★ 门禁的判据：量化断言必须有可追溯出处。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = _load_gate()

    # ── 违规必须被抓到 ────────────────────────────────────────────────
    def test_bare_quantities_are_reported(self) -> None:
        """★ 无出处的量化断言：每一个量词形态都要抓得到。"""
        cases = [
            "共 37 条能力没有实现",
            "扫了 120 个文件",
            "命中 5 处",
            "耗时 144 秒",
            "占用 12 MB",
            "占 87%",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertTrue(self.gate.scan_text(text),
                                "★ 漏报：%r 没被当成无出处的量化断言" % text)

    def test_multiple_quantities_one_line_reports_once(self) -> None:
        """★ 一行多个量化断言只报一次（★ 防噪声淹没真问题）。"""
        got = self.gate.scan_text("共 37 条、5 处、12 秒都没有出处")
        self.assertEqual(len(got), 1, "★ 同一行应只报一次，实得 %r" % (got,))

    # ── 合规必须放过 ──────────────────────────────────────────────────
    def test_traced_quantities_pass(self) -> None:
        """★ 带出处的量化断言不得误报（★ 恒红门禁与恒绿同样无用，事实 53）。"""
        cases = [
            "共 37 条能力没有实现（实测：`python scripts/check_x.py`）",
            "扫了 120 个文件，见 `scripts/release_check.py:88`",
            "命中 5 处（依据：`docs/known-facts.md`）",
            "耗时 144 秒（事实 62 记录）",
            "占用 12 MB，核验：`output/gate.log`",
            "占 87%（实测：`Get-ChildItem output -Recurse`）",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(self.gate.scan_text(text), [],
                                 "★ 误报：带出处的 %r 被报" % text)

    def test_paragraph_level_trace_accepted(self) -> None:
        """★ 出处在上/下一行也算（★ 文档写作的常见形态）。"""
        text = "核验命令：\n`python scripts/release_check.py`\n结果：37 条能力没有实现。"
        self.assertEqual(self.gate.scan_text(text), [],
                         "★ 段落级出处未被接受")

    # ── 边界：不该被当成量化断言的东西 ────────────────────────────────
    def test_structural_lines_skipped(self) -> None:
        """★ 标题 / 代码围栏 / 表格分隔行不参与扫描（★ 否则报一堆噪声）。"""
        for line in ("## 3 个步骤", "```", "|---|", "> 共 37 条"):
            with self.subTest(line=line):
                self.assertEqual(self.gate.scan_text(line), [],
                                 "★ 结构性行被误扫：%r" % line)

    def test_quotation_marker_is_not_a_backdoor(self) -> None:
        """★★ 引文标记（「原文引述」）只免掉**引文里的**数字，不免掉自己写的断言。

        ★ 为什么专门测这条：给门禁加豁免词是**最容易开后门**的改动 ——
          一旦「原文引述」被当成万能通行证，任何断言加四个字就能绕过门禁。
        ★ 判据两侧都要成立：
          ① 带标记的引文 ⇒ 放过（数字的责任方是被引的那份原文）；
          ② 不带标记的同类断言 ⇒ **必须报**（否则标记就成了后门）。
        """
        #: ① 引文：放过
        quoted = "某脚本说「共 534 条」（原文引述，文件已删）"
        self.assertEqual(self.gate.scan_text(quoted), [],
                         "★ 引文标记未被接受：%r" % (self.gate.scan_text(quoted),))
        #: ② 同一句话去掉标记 ⇒ 必须报（证明标记是**必要条件**，不是装饰）
        bare = "某脚本说「共 534 条」"
        self.assertTrue(self.gate.scan_text(bare),
                        "★ 后门：去掉引文标记后仍被放过 ⇒ 标记成了万能通行证")

    def test_version_strings_not_quantities(self) -> None:
        """★ 版本号不是量化断言（★ `0.7.22` / `2.0` 不该报）。"""
        for text in ("版本 `0.7.22`", "schema_version 是 `2.0`", "见第 62 条事实"):
            with self.subTest(text=text):
                got = self.gate.scan_text(text)
                #: 「见第 62 条事实」里「条」会命中，但同行有「事实 62」⇒ 应放过
                self.assertEqual(got, [], "★ 版本号/序号被误判：%r -> %r" % (text, got))

    # ── 真实样本（事实 62 的手法）────────────────────────────────────
    def test_real_regression_sample_from_this_session(self) -> None:
        """★ 真实样本：本轮裁决书里真实出现过的两行（★ 门禁当场抓到的）。

        ★ 这是事实 62 说的「用修复前的原文验证」—— 那两行确实是先被抓到、
        后补出处的，不是我为测试编的。
        """
        before = "- `output/` 里 3,060 个 `.SLDPRT` 是二进制，无可查文本；"
        self.assertTrue(self.gate.scan_text(before),
                        "★ 真实历史样本没被抓到 —— 门禁退化了")
        after = ("- `output/` 里的 `.SLDPRT` 是二进制，无可查文本"
                 "（数量见 §1.1 表，实测命令：`Get-ChildItem output -Recurse -File`）；")
        self.assertEqual(self.gate.scan_text(after), [],
                         "★ 修复后的样本被误报")

    # ── 门禁自身的入口 ────────────────────────────────────────────────
    def test_selftest_passes(self) -> None:
        """★ 门禁自带的自证也必须过（★ 它是第一道保险）。"""
        self.assertTrue(self.gate.selftest(), "★ 门禁 selftest() 失败")


if __name__ == "__main__":
    unittest.main(verbosity=2)
