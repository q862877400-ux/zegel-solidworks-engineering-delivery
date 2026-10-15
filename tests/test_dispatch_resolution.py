"""★ 判据：`check_dispatch_entry_guard.py` 的**解析面**（spec 230）。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_resolution.py
# 定位:   证 spec 230 的「解析面」**能红**（合成树端到端负例）、
#         **下界承重**（拔掉下界即红）、且**按文件作用域索引**（同名 `def` 不许合并）。
# 官方依据: 无（纯 AST）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_dispatch_entry_guard.py"

#: ★★ **门禁自己的下界**（★ 单一真源 —— 见 `test_real_tree_resolution_face_is_frozen_and_nonvacuous`）。
sys.path.insert(0, str(ROOT / "scripts"))
import check_dispatch_entry_guard as _entry_gate          # noqa: E402

BASELINE_RESOLVED_SITES = _entry_gate.BASELINE_RESOLVED_SITES

#: 分发口 + **同文件里的字面量调用点** ⇒ 应判 `resolved`。
RESOLVED_TREE = """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)


def use(obj):
    return _dispatch(obj, "GetSomething", 1)
"""

#: 分发口 + 调用点传的是**变量** ⇒ 应判 `unresolved`。
NONLITERAL_TREE = """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)


def use(obj, name):
    return _dispatch(obj, name, 1)
"""

#: 分发口 + **无调用点** ⇒ 应判 `no-callers`。
NO_CALLER_TREE = """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)
"""

#: ★ `*局部变量` 转发（二级数据流）⇒ 应判 `unresolved`（超出「一级解析」边界）。
LOCALVAR_TREE = """
def _dispatch(obj, member, *args):
    tail = list(args)
    return get_com_member(obj, member, *tail)


def use(obj):
    return _dispatch(obj, "GetSomething", 1)
"""

DECL = "#: dispatch-guard: exempt internal-helper\n"


def run_gate(root: Path | None, *, baseline: str = "1,1,0"):
    env = dict(os.environ)
    if root is not None:
        env["DSH_DISPATCH_ROOT"] = str(root)
    else:
        env.pop("DSH_DISPATCH_ROOT", None)
    env["DSH_DISPATCH_BASELINE_MIN"] = baseline
    env["DSH_DISPATCH_CLASSIFICATION"] = str(
        (root or ROOT) / "docs" / "nonexistent.json")
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=180,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def make_tree(files: dict[str, str]) -> Path:
    """⇒ 仓库**外**的临时树；`files` = `{"scripts/x.py": 源码}`。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh230-"))
    for rel, text in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp


def face(out: str) -> str:
    """⇒ 解析面那一行的读数段。"""
    m = re.search(r"★ 解析面（[^）]*）：(.+)", out)
    return m.group(1).strip() if m else ""


class TestRealTree(unittest.TestCase):
    """真树读数（★ 防止判据变成空判据）。"""

    def test_real_tree_resolution_face_is_frozen_and_nonvacuous(self):
        rc, out = run_gate(None)
        self.assertEqual(rc, 0, out)
        m = re.search(r"可解析 (\d+)/(\d+)", out)
        self.assertIsNotNone(m, out)
        self.assertGreaterEqual(int(m.group(1)), 18, out)
        f = face(out)
        self.assertIn("resolved 18", f, out)
        #: ★★★ **2026-10-10（规格 301）订正：改成读门禁自己的下界** ——
        #:   ★ **为什么是正当的**：★ 本判据的**意图**是「可解析调用点**不低于门禁钉的下界**」
        #:     ⇒ ★★ 两边必须**同源**；★ 而它原先硬写 `327`（★ 与门禁下界**恰好同值**，
        #:     所以**看不出**问题 —— ★ 但那是**巧合**）⇒ ★★ 一旦读数**涨**（★ 真树现在 **329**），
        #:     这条 `assertIn` 就**恒红**（★ 而「涨」是**好事**，不该红）。
        #:   ★★ **依据**（`MEMORY.md` 规则 16）：「★ **别拿一个数去核另一个**」+
        #:     ★ 本测试自己那条 `test_sites_baseline_shrink_is_red` **正是**在核「下界承重」✓
        _sites = int(re.search(r"可解析调用点 (\d+)", f).group(1))
        self.assertGreaterEqual(_sites, BASELINE_RESOLVED_SITES, f)

    def test_resolved_baseline_shrink_is_red(self):
        """★ 下界承重：把 `resolved` 下界抬到 19 ⇒ 当场红。"""
        rc, out = run_gate(None, baseline="37,85,1185,19,327")
        self.assertEqual(rc, 1, out)
        self.assertIn("baseline-shrunk", out)
        self.assertIn("可解析分发口 18 < 下界 19", out)

    def test_sites_baseline_shrink_is_red(self):
        """★ 下界承重：把 `sites` 下界抬到**实测 + 1** ⇒ 当场红。

        ★★ **2026-10-10（规格 301）改成**动态取实测值** —— ★ 原先硬写 `328`（★ 那时实测 327）。
          ★★ 而真树实测**会涨**（★ 现在 **329**）⇒ ★ 硬写的 `328` **不再承重**（★ 329 ≥ 328 ⇒ 不红）
          ⇒ ★★ **判据静默失效**（★ 它本该证明「下界承重」）。
          ★★★ **⇒ 正解：先跑一次读实测，再拿 `实测 + 1` 当假下界** —— ★ 这样**涨多少都不失效** ✓
        """
        rc0, out0 = run_gate(None)
        self.assertEqual(rc0, 0, out0)
        actual = int(re.search(r"可解析调用点 (\d+)", face(out0)).group(1))
        rc, out = run_gate(None, baseline="37,85,1180,18,%d" % (actual + 1))
        self.assertEqual(rc, 1, out)
        self.assertIn("可解析调用点 %d < 下界 %d" % (actual, actual + 1), out)

    def test_zero_resolved_with_nonzero_baseline_is_red(self):
        """★ 假绿守卫：下界非 0 而解析出 0 个 ⇒ 红（解析器失效不许 PASS）。"""
        tree = make_tree({"scripts/sw_fixture.py": DECL + NONLITERAL_TREE})
        rc, out = run_gate(tree, baseline="1,1,0,0,1")
        self.assertEqual(rc, 1, out)
        self.assertIn("zero-checked", out)


class TestSyntheticTrees(unittest.TestCase):
    """合成树端到端（★ 夹具只含被测对象）。"""

    def test_literal_caller_makes_entry_resolved(self):
        tree = make_tree({"scripts/sw_fixture.py": DECL + RESOLVED_TREE})
        rc, out = run_gate(tree)
        self.assertEqual(rc, 0, out)
        self.assertIn("resolved 1", face(out), out)
        self.assertIn("可解析调用点 1", face(out), out)

    def test_variable_caller_makes_entry_unresolved(self):
        tree = make_tree({"scripts/sw_fixture.py": DECL + NONLITERAL_TREE})
        rc, out = run_gate(tree)
        self.assertEqual(rc, 0, out)
        self.assertIn("unresolved 1", face(out), out)
        self.assertIn("可解析调用点 0", face(out), out)

    def test_no_caller_is_no_callers(self):
        tree = make_tree({"scripts/sw_fixture.py": DECL + NO_CALLER_TREE})
        rc, out = run_gate(tree)
        self.assertEqual(rc, 0, out)
        self.assertIn("no-callers 1", face(out), out)

    def test_local_var_forwarding_is_not_one_level(self):
        """★ `*tail`（局部变量）⇒ 不是一级转发 ⇒ unresolved（哪怕调用点是字面量）。"""
        tree = make_tree({"scripts/sw_fixture.py": DECL + LOCALVAR_TREE})
        rc, out = run_gate(tree)
        self.assertEqual(rc, 0, out)
        self.assertIn("unresolved 1", face(out), out)
        self.assertIn("可解析调用点 0", face(out), out)

    def test_cross_file_import_caller_resolves(self):
        """别的文件 `from <模块> import <名>` 后调用 ⇒ 算该入口的调用点。"""
        tree = make_tree({
            "scripts/sw_a.py": DECL + """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)
""",
            "scripts/sw_b.py": """
from sw_a import _dispatch


def use(obj):
    return _dispatch(obj, "GetSomething", 1)
""",
        })
        rc, out = run_gate(tree)
        self.assertEqual(rc, 0, out)
        self.assertIn("resolved 1", face(out), out)
        self.assertIn("可解析调用点 1", face(out), out)

    def test_same_name_defs_are_not_merged(self):
        """★★ 同名 `def` 分属两文件 ⇒ **各算各的**（裸名索引会把它们合并 ⇒ 假命中）。"""
        tree = make_tree({
            "scripts/sw_a.py": DECL + """
def _checked(target, member, *args):
    return get_com_member(target, member, *args)


def use_a(target):
    return _checked(target, "GetSomething", 1)
""",
            "scripts/sw_b.py": DECL + """
def _checked(target, member, *args):
    return get_com_member(target, member, *args)


def use_b(target, name):
    return _checked(target, name, 1)
""",
        })
        rc, out = run_gate(tree)
        self.assertEqual(rc, 0, out)
        f = face(out)
        self.assertIn("resolved 1", f, out)
        self.assertIn("unresolved 1", f, out)
        self.assertIn("可解析调用点 1", f, out)

    def test_old_three_value_baseline_keeps_synthetic_green(self):
        """★ 向后兼容：3 值下界（旧口径）⇒ 解析面下界取 0 ⇒ 合成树不受影响。"""
        tree = make_tree({"scripts/sw_fixture.py": DECL + NONLITERAL_TREE})
        rc, out = run_gate(tree, baseline="1,1,0")
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
