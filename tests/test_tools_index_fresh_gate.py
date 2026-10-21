"""★ 负例测试：`scripts/check_tools_index_fresh.py` 必须能抓到索引腐化。

依据 `docs/known-facts.md` 事实 62：「门禁『写了』不等于『有效』——负例测试是唯一的证明」。
★ 本文件**独立**构造输入（注入索引文本），不依赖门禁自己的 `selftest()`。
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_gate():
    p = ROOT / "scripts" / "check_tools_index_fresh.py"
    spec = importlib.util.spec_from_file_location("gate_tools_index", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ToolsIndexFreshGateTest(unittest.TestCase):
    """★ 判据：索引的**集合**与**描述**都要与 `tools/` 实际一致。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = _load_gate()
        cls.real = cls.gate.INDEX.read_text(encoding="utf-8", errors="replace")
        cls.actual = cls.gate.actual_tools()

    # ── 真实索引必须过 ────────────────────────────────────────────────
    def test_real_index_is_clean(self) -> None:
        """★ 仓库里真实的索引必须零问题（★ 否则门禁自己就是红的）。"""
        self.assertEqual(self.gate.check(), [],
                         "★ 真实索引不一致：%r" % (self.gate.check(),))

    def test_real_index_covers_every_tool(self) -> None:
        """★ 每个 `tools/*.py`（非 `_` 开头）都必须在索引里出现。"""
        idx = self.gate.parse_index(self.real)
        missing = [n for n in self.actual if n not in idx]
        self.assertEqual(missing, [], "★ 索引漏了：%r" % (missing,))

    # ── 违规必须被抓到 ────────────────────────────────────────────────
    def test_missing_tool_is_reported(self) -> None:
        """★ 索引缺一个脚本 ⇒ 必须报「缺」。"""
        victim = self.actual[0]
        lines = [ln for ln in self.real.splitlines()
                 if not (self.gate.ROW.match(ln.strip())
                         and self.gate.ROW.match(ln.strip()).group(1) == victim)]
        got = self.gate._check_with("\n".join(lines))
        self.assertTrue(any("缺" in g for g in got),
                        "★ 漏报：缺 %s 没被抓到（实得 %r）" % (victim, got))

    def test_ghost_row_is_reported(self) -> None:
        """★ 索引里多一个不存在的脚本 ⇒ 必须报「多」（★ 已删脚本没清索引）。"""
        fake = self.real + "\n| `probe_ghost_that_never_existed.py` | 伪造 |\n"
        got = self.gate._check_with(fake)
        self.assertTrue(any("多" in g for g in got),
                        "★ 漏报：幽灵行没被抓到（实得 %r）" % (got,))

    def test_stale_description_is_reported(self) -> None:
        """★ 描述被改 ⇒ 必须报「描述过期」（★ 这是「索引变成谎言」的主形态）。"""
        victim = self.actual[0]
        gen = self.gate._load_generator()
        now = gen.first_line_of(self.gate.TOOLS / victim) or self.gate.NODESC
        tampered = self.real.replace(
            "| `%s` | %s |" % (victim, now),
            "| `%s` | ★ 伪造描述 |" % victim, 1)
        self.assertNotEqual(tampered, self.real, "★ 篡改没生效（找不到原行）")
        got = self.gate._check_with(tampered)
        self.assertTrue(any("描述过期" in g for g in got),
                        "★ 漏报：描述被改没被抓到（实得 %r）" % (got,))

    # ── 边界：不该被误判的 ────────────────────────────────────────────
    def test_underscore_scripts_excluded(self) -> None:
        """★ `_` 开头的内部件不进检索面（★ 与生成器同口径）。"""
        idx = self.gate.parse_index(self.real)
        unders = [n for n in idx if n.startswith("_")]
        self.assertEqual(unders, [], "★ 索引里出现了 `_` 开头的内部件：%r" % (unders,))

    def test_nondesc_placeholder_matches_between_generator_and_gate(self) -> None:
        """★★ 生成器与门禁的「无说明」占位文案必须**同一句**。

        ⚠ 实测教训：两处文案不一致时，凡是「无文件头说明」的脚本都会**永久假红**
          —— 而且报的是「描述过期」，人会去改文件头（其实文件头没问题是文案打架）。
        """
        gen = self.gate._load_generator()
        self.assertEqual(gen.NODESC, self.gate.NODESC,
                         "★ 生成器与门禁的 NODESC 不一致 ⇒ 无说明的脚本会永久假红")

    def test_selftest_passes(self) -> None:
        """★ 门禁自带自证也必须过。"""
        self.assertTrue(self.gate.selftest(), "★ 门禁 selftest() 失败")


if __name__ == "__main__":
    unittest.main(verbosity=2)
