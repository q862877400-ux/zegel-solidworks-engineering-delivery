r"""★ 判据：枚举表盲区必须**表态**，且表态必须**可核**（spec 224）。

背景（223 留下的口子）：
  · 223 让门禁**打印**了 44 张「自称官方却无 `# swXxx` 标注」的模块级整数表，
    但**退出码不变** ⇒ 一张表可以**不表态而门禁照样绿**。
  · 本轮实测：44 张共 **409 条**，其中**键就是官方成员名**的只有 **27 条**
    （26 条在 `ANNOTATION_TYPE_BITS` + 1 条在 `DIALOG_SUPPRESSORS`）
    ⇒ ★ **「逐行补 `# swXxx`」对 42 张表是错的解法** —— 它们的键是本地语义键，
      官方成员名不在键里；硬补只能靠人一一对表，成本高且易写错（223 抓的正是这类「冒官方名」）。

⇒ 本判据锁三件事：
  1. **表态存在**：44 张盲区表每一张都有 `#: enum-gate: …`（否则门禁**必须红**）；
  2. **表态可核**：`enum` 声明的枚举能在出厂反射里解析到、且表内值集 ⊆ 该枚举取值集；
     `member` 声明的成员在 `C:\swapi\types\*\` 有页；`not-enum` 的子类在封闭词表内；
  3. **负例**：合成一棵树，里面有一张**自称官方却没表态**的表 ⇒ 门禁**必须 exit 1**
     （★ 这条是防「表态机制本身退化成装饰品」—— 与 223 判过的「空判据」同族）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_enum_table_disposition.py —— 本文件自身
# 定位:   spec 224 FR-002/003/004/005 的判据；被测对象是 `scripts/check_enum_values_vs_reflection.py`。
# 官方依据: `_raw/enum_values_sldworks.txt` · `_raw/reflect/enum_cosworks.txt`（出厂反射转储）
#           · `C:\swapi\types\<Iface>\<Member>.md`（官方成员页）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "scripts" / "check_enum_values_vs_reflection.py"
PY = sys.executable
#: 官方成员页根（便携性：拿不到就跳过 `member` 校验，**不判罪**）。
SWAPI_TYPES = Path(os.environ.get("DSH_SWAPI_TYPES", r"C:\swapi\types"))

#: 44 —— 本 spec 的事实基线（`find_uncovered_claimed_tables()` 实测）。
#: ★ 用**下界**断言：将来新增的表**表态后**不该让本判据假红。
BASELINE_BLIND = 44


def _load_gate():
    spec = importlib.util.spec_from_file_location("enum_gate", GATE)
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


class TestDispositionExists(unittest.TestCase):
    """FR-003 / FR-004：44 张盲区表每一张都必须表态。"""

    def test_every_claimed_table_is_dispositioned(self):
        m = _load_gate()
        blind = m.find_uncovered_claimed_tables()
        self.assertGreaterEqual(
            len(blind), BASELINE_BLIND,
            "盲区表只有 %d 张（基线 %d）—— ★ 盲区清单本身变了，先查清再改本判据"
            % (len(blind), BASELINE_BLIND))
        disp = m.parse_dispositions()
        missing = [(f, lo, name) for f, lo, name, _n in blind if (f, lo) not in disp]
        self.assertEqual(
            missing, [],
            "★ 这些「自称官方却无 # swXxx 覆盖」的表**没有表态** ⇒ 门禁必须红：\n  %s"
            % "\n  ".join("%s:%d %s" % t for t in missing))

    def test_disposition_codes_are_closed(self):
        m = _load_gate()
        self.assertEqual(sorted(m.DISPOSITION_CODES), ["enum", "member", "not-enum"])
        self.assertEqual(
            sorted(m.NOT_ENUM_SUBS),
            ["arity", "derived", "index", "mark", "observed"])


class TestDispositionIsVerifiable(unittest.TestCase):
    """FR-002：表态必须能被三源之一坐实，不能是装饰品。"""

    def test_enum_dispositions_resolve_and_contain(self):
        m = _load_gate()
        sets = m.enum_value_sets()
        tables = {(f, lo): (name, hi) for f, lo, hi, name, _n in m.find_int_tables()}
        checked = 0
        for (fname, lo), (code, arg, _line) in m.parse_dispositions().items():
            if code != "enum":
                continue
            self.assertIn(
                arg, sets,
                "★ %s:%d 声明 `enum %s`，但该枚举在**出厂反射转储**里解析不到"
                " ⇒ 声明无法被核（要么枚举名写错，要么转储解析漏了）" % (fname, lo, arg))
            values = m.table_values(fname, lo)
            bad = sorted({v for v in values if v not in sets[arg]})
            self.assertEqual(
                bad, [],
                "★ %s:%d（%s）声明 `enum %s`，但这些值不在该枚举取值集里：%s"
                "（枚举值集 %s）"
                % (fname, lo, tables.get((fname, lo), ("?",))[0], arg, bad, sorted(sets[arg])))
            checked += 1
        self.assertGreaterEqual(checked, 20, "`enum` 类声明只有 %d 张，与分类表不符" % checked)

    def test_member_dispositions_have_official_pages(self):
        m = _load_gate()
        if not SWAPI_TYPES.is_dir():
            self.skipTest("拿不到 %s ⇒ 便携性跳过（不判罪）" % SWAPI_TYPES)
        checked = 0
        for (fname, lo), (code, arg, _line) in m.parse_dispositions().items():
            if code != "member":
                continue
            pages = list(SWAPI_TYPES.glob("*/%s.md" % arg))
            self.assertTrue(
                pages,
                "★ %s:%d 声明 `member %s`，但 %s\\*\\%s.md 一个都没有"
                " ⇒ 该成员在官方页里不存在（名字写错，或本就不该按成员表态）"
                % (fname, lo, arg, SWAPI_TYPES, arg))
            checked += 1
        self.assertGreaterEqual(checked, 8, "`member` 类声明只有 %d 张，与分类表不符" % checked)

    def test_not_enum_subs_are_in_the_closed_vocabulary(self):
        m = _load_gate()
        seen = 0
        for (fname, lo), (code, arg, _line) in m.parse_dispositions().items():
            if code != "not-enum":
                continue
            self.assertIn(
                arg, m.NOT_ENUM_SUBS,
                "★ %s:%d 的 `not-enum %s` 子类不在封闭词表 %s 里"
                % (fname, lo, arg, sorted(m.NOT_ENUM_SUBS)))
            seen += 1
        self.assertGreaterEqual(seen, 10, "`not-enum` 类声明只有 %d 张，与分类表不符" % seen)


class TestGateGoesRedOnUndeclared(unittest.TestCase):
    """FR-003 的**端到端负例**：未表态 ⇒ 门禁必须 exit 1（且点名那张表）。"""

    _DUMP = "## swFakeEnum_e\n  swFakeA = 0\n  swFakeB = 1\n"

    def _synthetic_tree(self, root: Path, body: str) -> None:
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "sw_fake.py").write_text(body, encoding="utf-8")
        (root / "fake_dump.txt").write_text(self._DUMP, encoding="utf-8")

    def test_undeclared_claimed_table_makes_the_gate_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, (
                "#: ★ 官方 swFakeEnum_e（★ 合成夹具）\n"
                "FAKE_TABLE = {'a': 0, 'b': 1}\n"))
            proc = _run_gate({
                "DSH_ENUM_GATE_ROOT": str(root),
                "DSH_ENUM_DUMP": str(root / "fake_dump.txt"),
            })
            self.assertEqual(
                proc.returncode, 1,
                "★ 合成树里有一张「自称官方却没表态」的表，门禁却 exit %d"
                " ⇒ 未表态没有判红 ⇒ 表态机制是装饰品\n--- stdout ---\n%s"
                % (proc.returncode, proc.stdout))
            self.assertIn("FAKE_TABLE", proc.stdout, "★ 判红却没点名是哪张表")
            self.assertIn("未表态", proc.stdout, "★ 判红却没说明理由")

    def test_declared_claimed_table_keeps_the_gate_green(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, (
                "#: ★ 官方 swFakeEnum_e（★ 合成夹具）\n"
                "#: enum-gate: enum swFakeEnum_e\n"
                "FAKE_TABLE = {'a': 0, 'b': 1}\n"))
            proc = _run_gate({
                "DSH_ENUM_GATE_ROOT": str(root),
                "DSH_ENUM_DUMP": str(root / "fake_dump.txt"),
            })
            self.assertEqual(
                proc.returncode, 0,
                "★ 已表态的表仍被判红 ⇒ 表态机制坏了\n--- stdout ---\n%s" % proc.stdout)

    def test_wrong_value_is_caught_by_the_enum_disposition(self):
        """★ 反向：声明了 `enum` 但**值不在枚举里** ⇒ 必须判红（否则表态是空判据）。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, (
                "#: ★ 官方 swFakeEnum_e（★ 合成夹具）\n"
                "#: enum-gate: enum swFakeEnum_e\n"
                "FAKE_TABLE = {'a': 0, 'b': 77}\n"))
            proc = _run_gate({
                "DSH_ENUM_GATE_ROOT": str(root),
                "DSH_ENUM_DUMP": str(root / "fake_dump.txt"),
            })
            self.assertEqual(
                proc.returncode, 1,
                "★ 值 77 不在 `swFakeEnum_e`（值集 {0,1}）里，门禁却 exit %d"
                " ⇒ `enum` 声明是空判据\n--- stdout ---\n%s" % (proc.returncode, proc.stdout))
            self.assertRegex(proc.stdout, re.compile(r"77"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
