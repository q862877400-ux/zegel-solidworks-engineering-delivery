"""★ 判据：分发口调用点的**去重口径**（spec 233）—— 嵌套 `def` 不得重复计数。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_call_site_dedup.py
# 定位:   证 `scripts/check_dispatch_entry_guard.py` 的**调用点计数口径**能红 ——
#         嵌套 `def` 里的调用点只许计一次（按最内层包围 `def` 归属），
#         且桶之和与不可见调用点数**必须自洽**。
# 官方依据: 无（纯 AST 量测口径）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_dispatch_entry_guard.py"

#: ★★ **门禁自己的下界**（★ 单一真源 —— 见 `test_real_tree_counts_are_deduped` 的订正说明）。
sys.path.insert(0, str(ROOT / "scripts"))
import check_dispatch_entry_guard as _entry_gate          # noqa: E402

BASELINE_VISIBLE = _entry_gate.BASELINE_VISIBLE

#: 外层 `def` 里**嵌套** `def`，包装器调用写在**内层** —— 旧口径会**计两次**。
NESTED_LITERAL = """
def outer(obj):
    def inner(o):
        return get_com_member(o, "GetSomething")
    return inner(obj)

#: dispatch-guard: exempt internal-helper
def _covered(obj, member, *args):
    return get_com_member(obj, member, *args)
"""

#: 嵌套 `def` 的**形参**被转发 ⇒ 该调用点归属**内层**（`形参转发 1`），不是外层。
NESTED_PARAM = """
def outer(obj, member):
    #: dispatch-guard: exempt internal-helper
    def _inner(o, member):
        return get_com_member(o, member)
    return _inner(obj, member)

#: dispatch-guard: exempt internal-helper
def _covered(obj, member, *args):
    return get_com_member(obj, member, *args)
"""

#: 两个**并列** `def` 各有一个调用点 ⇒ 必须**各计一次**（防「去重去过头」）。
SIBLING_LITERAL = """
def a(obj):
    return get_com_member(obj, "GetA")


def b(obj):
    return get_com_member(obj, "GetB")

#: dispatch-guard: exempt internal-helper
def _covered(obj, member, *args):
    return get_com_member(obj, member, *args)
"""


def run_gate(root: Path, *, baseline: str = "0,0,0"):
    env = dict(os.environ)
    env["DSH_DISPATCH_ROOT"] = str(root)
    env["DSH_DISPATCH_BASELINE_MIN"] = baseline
    env["DSH_DISPATCH_CLASSIFICATION"] = str(root / "docs" / "nonexistent.json")
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=180,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def make_tree(body: str) -> Path:
    """⇒ 仓库**外**的临时树 `scripts/sw_fixture.py`。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh233-"))
    (tmp / "scripts").mkdir(parents=True)
    (tmp / "scripts" / "sw_fixture.py").write_text(body, encoding="utf-8")
    return tmp


def counts(out: str) -> tuple[int, int]:
    """⇒ `(可见, 不可见)`；找不到即抛（★ 不许静默降级成 0）。"""
    m = re.search(r"调用点：可见（字面量）(\d+) · 不可见 (\d+)", out)
    if m is None:
        raise AssertionError("取不到读数：\n" + out)
    return int(m.group(1)), int(m.group(2))


def buckets_of(out: str) -> tuple[int, int, int]:
    m = re.search(r"不可见 \d+（形参转发 (\d+) / 局部变量 (\d+) / 计算式 (\d+)）", out)
    if m is None:
        raise AssertionError("取不到桶读数：\n" + out)
    return tuple(int(x) for x in m.groups())


def load_gate():
    spec = importlib.util.spec_from_file_location("cdeg233t", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdeg233t"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestRealTree(unittest.TestCase):
    """真树读数（★ 防止判据变成空判据）。"""

    def test_real_tree_counts_are_deduped(self):
        proc = subprocess.run(
            [sys.executable, "-B", str(GATE)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), stdin=subprocess.DEVNULL, timeout=180,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, out)
        visible, invisible = counts(out)
        #: ★ spec 233 修正后的读数（旧口径虚增：1219 / 91 / local 52）。
        #: ★ spec 240：`visible` 1185 → **1183** —— `sw_weldment._create_from_definition`
        #:   整体删除后少 4 个字面量 COM 调用点（**正当减少**，非探测器漏了）。
        #: ★★ **2026-10-10（规格 301）订正：改成读门禁自己的下界** ——
        #:   ★ **为什么是正当的**：★ 本判据的**意图**是「读数**不低于门禁钉的下界**」
        #:     ⇒ ★★ 两边必须**同源**；★ 而它原先硬写 `1183`、★ 门禁的 `BASELINE_VISIBLE` 是 **1180**
        #:     ⇒ ★ 门禁**正当下调**（★ spec 256 删了 3 处调废弃成员的兜底）时本判据**恒红**。
        #:   ★★ **依据**（`MEMORY.md` 规则 16）：「★ **别拿一个数去核另一个**」✓
        self.assertGreaterEqual(visible, BASELINE_VISIBLE, out)
        self.assertEqual(invisible, 85, out)
        self.assertEqual(buckets_of(out), (37, 46, 2), out)

    def test_real_tree_bucket_sum_is_self_consistent(self):
        proc = subprocess.run(
            [sys.executable, "-B", str(GATE)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), stdin=subprocess.DEVNULL, timeout=180,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        _v, invisible = counts(out)
        self.assertEqual(sum(buckets_of(out)), invisible, out)


class TestDedup(unittest.TestCase):
    """★ 去重口径的承重判据（合成树端到端）。"""

    def test_nested_def_call_site_counted_once(self):
        """★ 旧口径：外层 + 内层各计一次 ⇒ 可见 = 2；修正后 = **1**。"""
        rc, out = run_gate(make_tree(NESTED_LITERAL))
        self.assertEqual(rc, 0, out)
        self.assertEqual(counts(out), (1, 1), out)   # +1 = 夹具自带的已表态分发口

    def test_nested_def_param_forward_counted_once(self):
        """★ 旧口径：内层算 `param`、外层算 `local` ⇒ 两边都虚增；修正后 `形参转发 1`。"""
        rc, out = run_gate(make_tree(NESTED_PARAM))
        self.assertEqual(rc, 0, out)
        self.assertEqual(counts(out), (0, 2), out)   # +1 = 夹具自带的已表态分发口
        self.assertEqual(buckets_of(out), (2, 0, 0), out)

    def test_sibling_defs_are_not_over_deduped(self):
        """★ 防「去重去过头」：并列 `def` 各一个调用点 ⇒ 必须 **2**。"""
        rc, out = run_gate(make_tree(SIBLING_LITERAL))
        self.assertEqual(rc, 0, out)
        self.assertEqual(counts(out), (2, 1), out)   # +1 = 夹具自带的已表态分发口

    def test_bucket_mismatch_helper_is_load_bearing(self):
        """★ 自洽断言本体承重：喂**历史缺陷的那组数** ⇒ 必须判出来。"""
        mod = load_gate()
        bad = mod.bucket_consistency({"param": 37, "local": 52, "computed": 2}, 85)
        self.assertIsNotNone(bad)
        self.assertIn("口径不自洽", bad)
        self.assertIn("91", bad)
        #: 自洽时必须是 `None`（否则门禁永远红）。
        self.assertIsNone(mod.bucket_consistency({"param": 37, "local": 46, "computed": 2}, 85))


if __name__ == "__main__":
    unittest.main()
