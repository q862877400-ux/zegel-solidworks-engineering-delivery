"""★ 判据：`check_dispatch_entry_guard.py` 的分发口守卫覆盖门禁（spec 229）。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_entry_guard.py
# 定位:   证 `scripts/check_dispatch_entry_guard.py` **能红**（合成树端到端负例）、
#         **每个 code 的自证都承重**、且真树读数**非 0**（不是空判据）。
# 官方依据: 无（纯 AST + `docs/gate-classification.json` + `audit_call_arity.WRAPPERS`）
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

#: ★★ **门禁自己的下界**（★ 单一真源 —— 见 `test_real_tree_is_green_and_nonvacuous` 的订正说明）。
#:   ★★ 2026-10-10（规格 301）：★ 本测试原先**硬写** `1183`、★ 而门禁的下界是 `1180`
#:     ⇒ ★ 两者不同源 ⇒ ★★ 门禁**正当下调**时本判据恒红 ⇒ ★ 改成**读门禁的值** ✓
sys.path.insert(0, str(ROOT / "scripts"))
import check_dispatch_entry_guard as _entry_gate          # noqa: E402

BASELINE_VISIBLE = _entry_gate.BASELINE_VISIBLE

#: 最小分发口：成员名是**形参** ⇒ 静态审计看不见 ⇒ 必须表态。
ENTRY = """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)
"""

#: 成员名是**字面量** ⇒ 审计可见 ⇒ **不是**分发口。
LITERAL = """
def _direct(obj):
    return get_com_member(obj, "GetSomething", 1)
"""


def run_gate(root: Path, *, baseline: str = "1,1,0", classification: Path | None = None):
    env = dict(os.environ)
    env["DSH_DISPATCH_ROOT"] = str(root)
    env["DSH_DISPATCH_BASELINE_MIN"] = baseline
    env["DSH_DISPATCH_CLASSIFICATION"] = str(classification or root / "docs" / "nonexistent.json")
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=180,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def make_tree(body: str, *, name: str = "sw_fixture.py", extra_files: dict | None = None,
              gates: list | None = None) -> Path:
    """⇒ 仓库**外**的临时树 `scripts/<name>`（+ 可选 `docs/gate-classification.json`）。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh229-"))
    (tmp / "scripts").mkdir(parents=True)
    (tmp / "scripts" / name).write_text(body, encoding="utf-8")
    for rel, text in (extra_files or {}).items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if gates is not None:
        (tmp / "docs").mkdir(parents=True, exist_ok=True)
        (tmp / "docs" / "gate-classification.json").write_text(
            json.dumps({"classification": gates}, ensure_ascii=False), encoding="utf-8")
    return tmp


class TestRealTree(unittest.TestCase):
    """真树读数（★ 防止判据变成空判据）。"""

    def test_real_tree_is_green_and_nonvacuous(self):
        proc = subprocess.run(
            [sys.executable, "-B", str(GATE)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), stdin=subprocess.DEVNULL, timeout=180,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, out)
        m = re.search(r"分发口 (\d+) · 已表态 (\d+) · 违规 (\d+) · 可见 (\d+) · 不可见 (\d+)", out)
        self.assertIsNotNone(m, out)
        entries, declared, violations, visible, invisible = (int(x) for x in m.groups())
        self.assertGreaterEqual(entries, 37, out)
        self.assertEqual(declared, entries, out)
        self.assertEqual(violations, 0, out)
        #: ★★★ **2026-10-10（规格 301）订正：硬写的 `1183` → 读门禁自己的下界** ——
        #:   ★ **为什么是正当的**：★ 本判据的**意图**是「可见调用点**不许低于门禁钉的下界**」
        #:     ⇒ ★★ **两边必须同源**。★ 而它原先硬写 `1183`、★ 门禁自己的 `BASELINE_VISIBLE` 是 **1180**
        #:     ⇒ ★ 两者**不同源** ⇒ ★★ 一旦有人**正当下调**门禁下界（★ spec 256 删了 3 处调废弃成员的兜底），
        #:       本判据就**恒红**（★ 而它本该跟着门禁走）。
        #:   ★★ **依据**（`MEMORY.md` 规则 16）：「门禁数三套口径别混 … ★ **别拿一个数去核另一个**」✓
        self.assertGreaterEqual(visible, BASELINE_VISIBLE, out)
        self.assertGreaterEqual(invisible, 85, out)    # spec 233：91 → 85（去重口径）


class TestDeclarations(unittest.TestCase):
    """声明 → 自证（★ 每条 code 都要有一条**能红**的判据）。"""

    def test_undeclared_dispatch_entry_is_red(self):
        rc, out = run_gate(make_tree(ENTRY))
        self.assertEqual(rc, 1, out)
        self.assertIn("undeclared", out)

    def test_declaration_above_def_is_green(self):
        rc, out = run_gate(make_tree(
            "#: dispatch-guard: exempt internal-helper\n" + ENTRY))
        self.assertEqual(rc, 0, out)

    def test_declaration_may_skip_blank_lines(self):
        rc, out = run_gate(make_tree(
            "#: dispatch-guard: exempt internal-helper\n\n\n" + ENTRY))
        self.assertEqual(rc, 0, out)

    def test_literal_member_name_is_not_a_dispatch_entry(self):
        #: ★ 只有 `_direct`（字面量）⇒ 分发口 0 ⇒ 触发假绿守卫（事实 46）。
        rc, out = run_gate(make_tree(LITERAL), baseline="0,0,0")
        self.assertEqual(rc, 1, out)
        self.assertIn("zero-checked", out)

    def test_only_param_forwarding_counts_as_entry(self):
        rc, out = run_gate(make_tree(LITERAL + "\n#: dispatch-guard: exempt internal-helper\n" + ENTRY))
        self.assertEqual(rc, 0, out)
        self.assertIn("分发口 1 ·", out)


class TestSelfVerification(unittest.TestCase):
    """★ 声明**不等于**通过 —— 每个 code 都要自证。"""

    def test_generated_api_claim_on_normal_file_is_red(self):
        rc, out = run_gate(make_tree(
            "#: dispatch-guard: exempt generated-api\n" + ENTRY))
        self.assertEqual(rc, 1, out)
        self.assertIn("generated-api", out)

    def test_generated_api_claim_on_generated_file_is_green(self):
        rc, out = run_gate(make_tree(
            "#: dispatch-guard: exempt generated-api\n" + ENTRY, name="sw_api_fixture.py"))
        self.assertEqual(rc, 0, out)

    def test_internal_helper_requires_underscore(self):
        body = ENTRY.replace("_dispatch", "public_dispatch")
        rc, out = run_gate(make_tree(
            "#: dispatch-guard: exempt internal-helper\n" + body))
        self.assertEqual(rc, 1, out)
        self.assertIn("internal-helper", out)

    def test_covered_wrappers_requires_membership(self):
        rc, out = run_gate(make_tree(
            "#: dispatch-guard: covered-wrappers\n" + ENTRY))
        self.assertEqual(rc, 1, out)
        self.assertIn("covered-wrappers", out)

    def test_covered_wrappers_on_real_wrapper_is_green(self):
        body = """
def call_com_member(obj, attr_name, *args):
    return get_com_member(obj, attr_name, *args)
"""
        rc, out = run_gate(make_tree("#: dispatch-guard: covered-wrappers\n" + body))
        self.assertEqual(rc, 0, out)

    def test_covered_gate_must_be_registered(self):
        #: 登记表**存在**但没登记 `check_x.py` ⇒ 承重性判红（不是「读不到就放行」）。
        tmp = make_tree("#: dispatch-guard: covered check_x.py\n" + ENTRY)
        (tmp / "docs").mkdir(parents=True, exist_ok=True)
        (tmp / "docs" / "gate-classification.json").write_text(
            json.dumps({"classification": [{"gate": "check_other.py"}]}), encoding="utf-8")
        rc, out = run_gate(tmp, classification=tmp / "docs" / "gate-classification.json")
        self.assertEqual(rc, 1, out)
        self.assertIn("承重性", out)

    def test_covered_gate_missing_registry_is_not_judged(self):
        #: 登记表**读不到** ⇒ 缺数据源 ≠ 检查失败（便携性）。
        rc, out = run_gate(make_tree("#: dispatch-guard: covered check_x.py\n" + ENTRY))
        self.assertEqual(rc, 0, out)

    def test_covered_gate_registered_is_green(self):
        tmp = make_tree("#: dispatch-guard: covered check_x.py\n" + ENTRY)
        (tmp / "docs").mkdir(parents=True, exist_ok=True)
        (tmp / "docs" / "gate-classification.json").write_text(
            json.dumps({"classification": [{"gate": "check_x.py"}]}), encoding="utf-8")
        rc, out = run_gate(tmp, classification=tmp / "docs" / "gate-classification.json")
        self.assertEqual(rc, 0, out)

    def test_module_local_requires_unique_definition(self):
        #: 同名 `def` 出现在两个文件 ⇒ 不能自称 module-local（★ 不判第二个文件，
        #: 那里**没有**分发口 —— 只让名字重复）。
        tmp = make_tree("#: dispatch-guard: exempt module-local\n" + ENTRY, name="sw_a.py",
                        extra_files={"scripts/sw_b.py":
                                     "def _dispatch(obj, member, *args):\n    return None\n"})
        rc, out = run_gate(tmp)
        self.assertEqual(rc, 1, out)
        self.assertIn("module-local", out)

    def test_module_local_requires_in_file_callers(self):
        tmp = make_tree("#: dispatch-guard: exempt module-local\n" + ENTRY, name="sw_a.py",
                        extra_files={"scripts/sw_b.py": "def use(o):\n    return _dispatch(o, 'X')\n"})
        rc, out = run_gate(tmp)
        self.assertEqual(rc, 1, out)
        self.assertIn("别的文件", out)

    def test_unknown_code_is_red(self):
        rc, out = run_gate(make_tree("#: dispatch-guard: whatever\n" + ENTRY))
        self.assertEqual(rc, 1, out)
        self.assertIn("未知 code", out)

    def test_exempt_without_subcode_is_red(self):
        rc, out = run_gate(make_tree("#: dispatch-guard: exempt\n" + ENTRY))
        self.assertEqual(rc, 1, out)
        self.assertIn("格式不合法", out)


class TestBaseline(unittest.TestCase):
    """★ 只增不减（下界冻结）。"""

    def test_baseline_shrink_is_red(self):
        rc, out = run_gate(make_tree("#: dispatch-guard: exempt internal-helper\n" + ENTRY),
                           baseline="99,99,99")
        self.assertEqual(rc, 1, out)
        self.assertIn("baseline-shrunk", out)

    def test_baseline_met_is_green(self):
        rc, out = run_gate(make_tree("#: dispatch-guard: exempt internal-helper\n" + ENTRY),
                           baseline="1,1,0")
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
