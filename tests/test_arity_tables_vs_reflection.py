r"""★ 判据：`*_ARITY` 表的值必须与出厂反射在**显式声明的 by-ref 约定**下对得上（spec 227）。

背景（224/225/226 三次登记的未过门）：
  · 那三轮让每张「自称有出处」的整数表**表态**，`not-enum arity` 是其中一档 ——
    ★ 但那一档**只验子类、不验值**：`'AddMate5': 15` 这个 **15** 此前没有任何机器判据在守。
  · 2026-10-09 第 4 轮量测：552 条声明按「原样计数」不符 **37**、按「剔除 by-ref」不符 **15**
    ⇒ 看着像 37 条真错；★ 真相是**两种约定并存**（`ASSEMBLY_DOC_ARITY` 含 by-ref、其余 13 张不含），
    各自约定下 552/552 全对。

⇒ 本判据锁四件事：
  1. **每张表都表态**（`#: arity-reflect: byref=included|excluded`），且约定分布 = **1 included + 13 excluded**；
  2. **声明必须紧邻表**（向上跳过空行取第一行非空行）—— ★ 关联是**确定性**的，不用行窗口启发式；
  3. **端到端负例**：合成树里把某条表值改错 ⇒ 门禁**必须 exit 1**；
     ★ 合成夹具**只含被测的那一张表**（放别的表会「因错误的原因」通过）；
  4. **约定是承重的**（不是装饰）：同一条 by-ref 成员，`included` 下绿、`excluded` 下红
     ⇒ ★ 否则「显式声明约定」这件事**没有可红的判据** = 空判据。

★ **按表名定位，不按行号** —— 本轮往这些表上方插了声明行，行号已移位。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_arity_tables_vs_reflection.py —— 本文件自身
# 定位:   spec 227 FR-001～FR-005 的判据；被测对象是 `scripts/check_arity_tables_vs_reflection.py`。
# 官方依据: `_raw/reflect_sldworks/iface_sldworks.txt`（出厂反射转储）
#           · `C:\swapi\types\IModelView\ShowMagnifyingGlass.md`（官方签名，6 个形参、无 by-ref）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "scripts" / "check_arity_tables_vs_reflection.py"
PY = sys.executable

#: ★ 基线（**下界**断言）：14 张表 · 552 条声明 · `included` **1** 张（`ASSEMBLY_DOC_ARITY`）。
BASELINE_TABLES = 14
BASELINE_ENTRIES = 552
INCLUDED_TABLE = "ASSEMBLY_DOC_ARITY"

#: ★ 合成夹具的反射转储：`FooBar` 原始 2 个形参、其中 1 个是 by-ref ⇒ included=2 / excluded=1。
_FAKE_DUMP = "## IFake\n  Void FooBar(Double, Double&)\n  Void Zero()\n"


def _load_gate():
    spec = importlib.util.spec_from_file_location("arity_gate_227", GATE)
    assert spec and spec.loader, "加载不了 %s" % GATE
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_gate(env_extra: dict) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(env_extra)
    return subprocess.run(
        [PY, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO_ROOT), env=env, stdin=subprocess.DEVNULL, timeout=300,
    )


def _synthetic_tree(root: Path, body: str, with_dump: bool = True) -> None:
    """★ 夹具**只含被测的那一张表**（`FOO_ARITY`）—— 放别的表会「因错误的原因」通过。"""
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "sw_fake.py").write_text(body, encoding="utf-8")
    if with_dump:
        (root / "fake_dump.txt").write_text(_FAKE_DUMP, encoding="utf-8")


def _env(root: Path) -> dict:
    return {
        "DSH_ARITY_GATE_ROOT": str(root),
        "DSH_ARITY_DUMPS": str(root / "fake_dump.txt"),
    }


# ── FR-001 / FR-002：真树上的表态与约定分布 ──────────────────────────

class TestRealTreeDeclaresConventions(unittest.TestCase):

    def test_every_arity_table_declares_its_byref_convention(self):
        m = _load_gate()
        tables = m.find_arity_tables()
        self.assertGreaterEqual(
            len(tables), BASELINE_TABLES,
            "只找到 %d 张 `*_ARITY` 表（基线 %d）—— ★ 扫描面漏了，先查清再改本判据"
            % (len(tables), BASELINE_TABLES))
        missing = [(t["file"], t["line"], t["name"]) for t in tables if t["decl"] is None]
        self.assertEqual(
            missing, [],
            "★ 这些表**没有** `#: arity-reflect: byref=…` 声明 ⇒ 门禁必须红：\n  %s"
            % "\n  ".join("%s:%d %s" % t for t in missing))

    def test_convention_split_is_one_included_thirteen_excluded(self):
        """★ 约定分布是**实测结论**（两种 by-ref 约定并存），不是随手填的。"""
        m = _load_gate()
        by_mode = {}
        for t in m.find_arity_tables():
            by_mode.setdefault(t["decl"], []).append(t["name"])
        self.assertEqual(
            sorted(by_mode.get("included") or []), [INCLUDED_TABLE],
            "★ `included` 应**只有** %s（含 by-ref 的那一张），实为 %s"
            % (INCLUDED_TABLE, sorted(by_mode.get("included") or [])))
        self.assertGreaterEqual(
            len(by_mode.get("excluded") or []), 13,
            "`excluded` 只有 %d 张（基线 13）" % len(by_mode.get("excluded") or []))

    def test_entry_count_matches_baseline(self):
        m = _load_gate()
        total = sum(len(t["entries"]) for t in m.find_arity_tables())
        self.assertGreaterEqual(
            total, BASELINE_ENTRIES,
            "声明条目只有 %d 条（基线 %d）" % (total, BASELINE_ENTRIES))

    def test_real_tree_is_green(self):
        proc = _run_gate({})
        self.assertEqual(
            proc.returncode, 0,
            "★ 真树上门禁不绿 ⇒ 要么有值不符、要么有表未表态\n--- stdout ---\n%s" % proc.stdout)
        self.assertIn("[PASS]", proc.stdout)

    def test_missing_dumps_is_a_skip_not_a_failure(self):
        """★ 便携性：反射转储在**工作区** ⇒ 一份都没有时 `[SKIP]` 且 exit 0（与枚举门禁同口径）。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            _synthetic_tree(root, "#: arity-reflect: byref=excluded\nFOO_ARITY = {'FooBar': 1}\n",
                            with_dump=False)
            proc = _run_gate({"DSH_ARITY_GATE_ROOT": str(root), "DSH_ARITY_DUMPS": ""})
            self.assertEqual(proc.returncode, 0,
                             "拿不到转储却判红 ⇒ 便携性坏了\n%s" % proc.stdout)
            self.assertIn("[SKIP]", proc.stdout)


# ── FR-002：声明必须**紧邻**表（确定性关联，不用行窗口）────────────────

class TestDeclarationAssociation(unittest.TestCase):

    def test_declaration_directly_above_the_table_is_associated(self):
        m = _load_gate()
        lines = ["x = 1", "#: arity-reflect: byref=included", "FOO_ARITY = {}"]
        self.assertEqual(m.declaration_above(lines, 3), "included")

    def test_blank_lines_between_are_skipped(self):
        m = _load_gate()
        lines = ["#: arity-reflect: byref=excluded", "", "", "FOO_ARITY = {}"]
        self.assertEqual(m.declaration_above(lines, 4), "excluded")

    def test_other_comment_between_breaks_the_association(self):
        """★ 与枚举门禁的「块内取最后一条」不同：本门禁要求声明**紧邻**（否则未表态）。"""
        m = _load_gate()
        lines = ["#: arity-reflect: byref=excluded", "# 别的一句话", "FOO_ARITY = {}"]
        self.assertIsNone(m.declaration_above(lines, 3))

    def test_unknown_mode_is_not_accepted(self):
        m = _load_gate()
        lines = ["#: arity-reflect: byref=maybe", "FOO_ARITY = {}"]
        self.assertIsNone(m.declaration_above(lines, 2))


# ── FR-003 / FR-004：端到端负例（★ 本判据的核心）────────────────────

class TestGateGoesRedOnWrongValues(unittest.TestCase):

    def test_correct_values_keep_the_gate_green(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            _synthetic_tree(root, (
                "#: arity-reflect: byref=excluded\n"
                "FOO_ARITY = {'FooBar': 1, 'Zero': 0}\n"))
            proc = _run_gate(_env(root))
            self.assertEqual(
                proc.returncode, 0,
                "★ 值对（excluded：FooBar=1、Zero=0）却判红 ⇒ 比对逻辑坏了\n%s" % proc.stdout)

    def test_a_single_bad_value_makes_the_gate_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            _synthetic_tree(root, (
                "#: arity-reflect: byref=excluded\n"
                "FOO_ARITY = {'FooBar': 1, 'Zero': 7}\n"))
            proc = _run_gate(_env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ `Zero` 反射是 0 个形参、夹具写 7 ⇒ 门禁却 exit %d ⇒ 值比对是空判据\n%s"
                % (proc.returncode, proc.stdout))
            self.assertIn("值不符", proc.stdout)
            self.assertIn("Zero", proc.stdout, "★ 判红却没点名是哪条")

    def test_undeclared_table_makes_the_gate_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            _synthetic_tree(root, "FOO_ARITY = {'FooBar': 1, 'Zero': 0}\n")
            proc = _run_gate(_env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ 表没有 `#: arity-reflect:` 声明 ⇒ 必须 exit 1（未表态即红）\n%s" % proc.stdout)
            self.assertIn("未表态", proc.stdout)
            self.assertIn("FOO_ARITY", proc.stdout)

    def test_byref_convention_is_load_bearing(self):
        """★★ 同一条 by-ref 成员：`included` 下绿、`excluded` 下红。

        ⇒ 若两者都绿（或都红），「显式声明约定」就是**装饰品** —— 本判据就是防这件事。
        """
        body_ok = "#: arity-reflect: byref=included\nFOO_ARITY = {'FooBar': 2, 'Zero': 0}\n"
        body_bad = "#: arity-reflect: byref=excluded\nFOO_ARITY = {'FooBar': 2, 'Zero': 0}\n"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            _synthetic_tree(root, body_ok)
            self.assertEqual(
                _run_gate(_env(root)).returncode, 0,
                "★ `included` 下 `FooBar=2`（原始形参个数）应绿")
            _synthetic_tree(root, body_bad)
            proc = _run_gate(_env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ 同一份夹具换成 `excluded` 仍绿 ⇒ 约定声明**不是承重的** ⇒ 空判据\n%s"
                % proc.stdout)

    def test_member_absent_from_dump_is_reported_as_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            _synthetic_tree(root, (
                "#: arity-reflect: byref=excluded\n"
                "FOO_ARITY = {'NoSuchMemberInDump': 0}\n"))
            proc = _run_gate(_env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ 转储里查不到的成员必须报出来（铁律 5：不猜）\n%s" % proc.stdout)
            self.assertIn("NoSuchMemberInDump", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
