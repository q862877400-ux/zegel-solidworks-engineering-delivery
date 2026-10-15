"""★ 判据：`check_assembly_doc_call_shape.py` 的调用形状门禁（spec 228）。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_assembly_doc_call_shape.py
# 定位:   证 `scripts/check_assembly_doc_call_shape.py` **能红**（合成树端到端负例）
#         且**不是空判据**（真树读数非 0）。
# 官方依据: `_raw/**/iface_*.txt` 的 `## <Iface>` + `Ret Name(params)` 两行式；
#           `sw_connect.out_i4` 的真机结论（by-ref 必须给占位，不能省）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_assembly_doc_call_shape.py"

#: ★ 合成夹具的反射转储：`AddMate5` 15 参（末位 `Int32&`）；`EditPart2` 3 参（末位 `Int32&`）。
DUMP = """## IAssemblyDoc
    Int32 AddMate5(Int32, Int32, Boolean, Double, Double, Double, Double, Double, Double, Double, Double, Boolean, Boolean, Int32, Int32&)
    Int32 EditPart2(Boolean, Boolean, Int32&)
    Int32 FixComponent()
"""

#: ★ 表体：与上面转储对得上（`AddMate5` 15 / `EditPart2` 3 / `FixComponent` 0）。
TABLE = """ASSEMBLY_DOC_ARITY: dict[str, int] = {
    'AddMate5': 15,
    'EditPart2': 3,
    'FixComponent': 0,
}
"""

ADD_MATE_14 = ", ".join(["1", "2", "True"] + ["0.0"] * 8 + ["False", "False", "0"])


def run_gate(root: Path, dumps: Path | None, *, unset_dumps: bool = False):
    env = dict(os.environ)
    env["DSH_ASSEMBLY_CALL_ROOT"] = str(root)
    if unset_dumps:
        env.pop("DSH_ARITY_DUMPS", None)
    elif dumps:
        env["DSH_ARITY_DUMPS"] = str(dumps)
    else:
        #: ★ 指向一个**不存在**的路径 —— 合成树里 `_raw/dumps/` 是真的存在的，
        #:   若把它留空，门禁会回退去 glob 它 ⇒ 「缺数据源」这条路径根本走不到。
        env["DSH_ARITY_DUMPS"] = str(root / "_nonexistent" / "none.txt")
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=180,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


class SyntheticTree:
    """在**仓库外**的临时树里搭一个最小 `scripts/` + `_raw/`。"""

    def __init__(self, body: str, *, declaration: str | None = "#: arity-reflect: byref=included"):
        self.tmp = Path(tempfile.mkdtemp(prefix="dsh228-"))
        (self.tmp / "scripts").mkdir(parents=True)
        (self.tmp / "_raw" / "dumps").mkdir(parents=True)
        self.dump = self.tmp / "_raw" / "dumps" / "iface_fixture.txt"
        self.dump.write_text(DUMP, encoding="utf-8")
        decl = (declaration + "\n") if declaration else ""
        (self.tmp / "scripts" / "fixture.py").write_text(
            "from __future__ import annotations\n\n"
            "#: enum-gate: not-enum arity\n"
            + decl
            + TABLE
            + "\n\ndef go(doc):\n"
            + body
            + "\n",
            encoding="utf-8")

    def run(self, **kw):
        return run_gate(self.tmp, kw.pop("dumps", self.dump), **kw)


class TestRealTree(unittest.TestCase):
    def test_real_tree_is_green_and_nonvacuous(self):
        code, out = run_gate(ROOT, None, unset_dumps=True)
        self.assertEqual(code, 0, out)
        m = re.search(r"已核 (\d+)", out)
        self.assertIsNotNone(m, out)
        self.assertGreaterEqual(int(m.group(1)), 10, "★ 检查量过小 ⇒ 近似空判据：\n" + out)
        self.assertIn("[PASS]", out)


class TestSyntheticNegative(unittest.TestCase):
    def test_clean_tree_is_green(self):
        t = SyntheticTree('    return call_assembly_doc(doc, "FixComponent")')
        code, out = t.run()
        self.assertEqual(code, 0, out)
        self.assertIn("已核 1", out)

    def test_bad_arity_makes_it_red(self):
        t = SyntheticTree('    return call_assembly_doc(doc, "FixComponent", 1)')
        code, out = t.run()
        self.assertEqual(code, 1, out)
        self.assertIn("表值 0，调用给了 1 个", out)

    def test_unknown_member_makes_it_red(self):
        t = SyntheticTree('    return call_assembly_doc(doc, "NoSuchMember", 1)')
        code, out = t.run()
        self.assertEqual(code, 1, out)
        self.assertIn("不在 `ASSEMBLY_DOC_ARITY` 里", out)

    def test_bare_byref_makes_it_red(self):
        t = SyntheticTree(
            '    return call_assembly_doc(doc, "AddMate5", %s, 0)' % ADD_MATE_14)
        code, out = t.run()
        self.assertEqual(code, 1, out)
        self.assertIn("bare-byref", out)
        self.assertIn("第 14 位形参是 `Int32&`", out)

    def test_wrapped_byref_is_green(self):
        """★ **承重性**：同一个调用点，把末位换成 `out_i4()` ⇒ 绿。

        与上一条**只差一个实参文本** ⇒ 证明「by-ref 占位」这条规则**真的在承重**，
        而不是被别的规则顺带放过。
        """
        t = SyntheticTree(
            '    return call_assembly_doc(doc, "AddMate5", %s, out_i4())' % ADD_MATE_14)
        code, out = t.run()
        self.assertEqual(code, 0, out)
        self.assertIn("含 by-ref 的调用点 1 个", out)

    def test_zero_call_sites_is_red(self):
        """事实 46：`检查过 0 个` 不许 PASS。"""
        t = SyntheticTree("    return None")
        code, out = t.run()
        self.assertEqual(code, 1, out)
        self.assertIn("检查过的调用点 == 0", out)

    def test_undeclared_table_is_red(self):
        t = SyntheticTree('    return call_assembly_doc(doc, "FixComponent")',
                          declaration=None)
        code, out = t.run()
        self.assertEqual(code, 1, out)
        self.assertIn("缺 `#: arity-reflect:", out)

    def test_excluded_declaration_conflicts_with_contract(self):
        t = SyntheticTree('    return call_assembly_doc(doc, "FixComponent")',
                          declaration="#: arity-reflect: byref=excluded")
        code, out = t.run()
        self.assertEqual(code, 1, out)
        self.assertIn("契约冲突", out)

    def test_missing_dumps_still_checks_arity(self):
        """缺数据源 ≠ 检查失败：arity 仍判（表值在源码里），by-ref 标为未核。"""
        t = SyntheticTree('    return call_assembly_doc(doc, "FixComponent", 1)')
        code, out = t.run(dumps=None)
        self.assertEqual(code, 1, out)
        self.assertIn("表值 0，调用给了 1 个", out)

    def test_missing_dumps_marks_byref_unverified(self):
        t = SyntheticTree(
            '    return call_assembly_doc(doc, "AddMate5", %s, 0)' % ADD_MATE_14)
        code, out = t.run(dumps=None)
        self.assertEqual(code, 0, out)
        self.assertIn("未核 by-ref 1 个", out)


class TestWrapperBoundaryFrozen(unittest.TestCase):
    """★ **边界冻结**（226 的教训）：放宽/加宽必须有「不加什么」的断言钉住。"""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import audit_byref_args as abr
        self.rx = abr.BYREF_OK

    def test_accepts_byref_wrappers(self):
        for text in ("out_i4()", "out_i4(0)", "sw_connect.out_i4()", "_out_i4()",
                     "VARIANT(VT_BYREF | VT_I4, 0)", "win32com.client.VARIANT(x)"):
            self.assertTrue(self.rx.match(text), text)

    def test_rejects_bare_values(self):
        for text in ("0", "0.0", "None", "False", '""', "value", "out", "output"):
            self.assertFalse(self.rx.match(text), text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
