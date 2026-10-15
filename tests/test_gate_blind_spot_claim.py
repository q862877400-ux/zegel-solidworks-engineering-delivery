r"""★ 判据：门禁盲区探测器必须认得出 `sws[A-Z]` 名族与「反射/转储/CHM」自称（spec 225）。

背景（224 留下的口子）：
  · 223 造出「盲区探测器」= `find_uncovered_claimed_tables()`：未覆盖 **且** 上方 15 行窗口里
    `CLAIM` 命中 ⇒ 算「自称官方却无标注」。
  · 224 让「未表态」**判红**，并把 44 张逐张表态。
  · ★★ 而**探测器自己的正则**是 `官方|swapi|sw[A-Z]\w+` ——
    `sw[A-Z]` 要求 `sw` 后**紧跟大写** ⇒ **`sws*` 全族（Simulation/Cosworks 的 300+ 个枚举名）
    一律不命中** ⇒ 那些表**从没进过盲区清单**，224 的判红对它们**完全无效**。
  · ★ 同族：只认「官方/swapi/`swXxx`」，不认「反射/转储/CHM/`_raw`」这几种**同样是在自称有出处**的写法。

⇒ 本判据锁四件事：
  1. **探测器认得出** `sws[A-Z]` 名族与「反射/转储/CHM/`_raw`」（且**仍**认得出旧探针）；
  2. **新暴露的 10 张表进了盲区清单**（3 张 `enum` + 6 张 `not-enum arity` + 1 张 `not-enum index`）；
  3. **10 张全部表态**，且 `enum` 声明的枚举能在出厂反射里解析到、值集 ⊆ 该枚举取值集；
  4. **端到端负例**：合成一棵树，里面有一张注释自称 `swsFakeEnum_e` 却没表态的表
     ⇒ 门禁**必须 exit 1** 且点名那张表（★ 否则「放宽正则」这件事**没有可红的判据** = 空判据）。

★ **按表名定位，不按行号** —— 本轮要往这些表上方插声明行，**行号会移位**；
  行号写死在判据里 = 一插就假红（与「把偶然当判据」同族）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_gate_blind_spot_claim.py —— 本文件自身
# 定位:   spec 225 FR-001～FR-005 的判据；被测对象是 `scripts/check_enum_values_vs_reflection.py`。
# 官方依据: `_raw/reflect/enum_cosworks.txt`（出厂反射转储，`sws*` 枚举节）
#           · `_raw/enum_values_sldworks.txt` · `_raw/chm_cosworks/`（CHM 解包，交叉核对用）
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

#: ★ 本轮实测基线：放宽后盲区 = **54**（原 44 + `sws` 3 + 「反射/转储/CHM/_raw」7）。
#: ★ 用**下界**断言：将来新增的表**表态后**不该让本判据假红。
BASELINE_BLIND = 54

#: ★ 三张「自称 `sws*` 官方枚举」却从没进过盲区清单的表 —— `(文件, 表名, 应声明的枚举名)`。
#: ★ 按**表名**定位（插声明会移行号，行号不可当判据）。
SWS_ENUM_TABLES = (
    ("sw_simulation.py", "SWS_SOLVER_TYPES", "swsSolverType_e"),
    ("sw_topology.py", "SWS_TOPOLOGY_DEMOLD_DIRECTIONS", "swsTopologyDemoldDirectionOption_e"),
    ("sw_topology.py", "SWS_TOPOLOGY_ACTIVATION", "swsTopologyActivationOption_e"),
)

#: ★ 七张「窗口里自称反射/转储/CHM/`_raw`」的表 —— `(文件, 表名, 应声明的 not-enum 子类)`。
REFLECTION_DERIVED_TABLES = (
    ("sw_costing.py", "COSTING_ARITY", "arity"),
    ("sw_featureworks.py", "FEATUREWORKS_ARITY", "arity"),
    ("sw_pdm.py", "DOCUMENT_ARITY", "arity"),
    ("sw_pdm.py", "TABLE_ARITY", "arity"),
    ("sw_routing.py", "ROUTING_ARITY", "arity"),
    ("sw_selection.py", "SELECTION_ARITY", "arity"),
    ("sw_simulation_loads.py", "_REFGEOM_POSITIONS", "index"),
)


def _load_gate():
    spec = importlib.util.spec_from_file_location("enum_gate_225", GATE)
    assert spec and spec.loader, "加载不了 %s" % GATE
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _table_line(m, fname: str, name: str):
    """⇒ 该表的**起始行号**（按名定位；找不到 ⇒ `None`）。"""
    for f, lo, _hi, n, _c in m.find_int_tables():
        if f == fname and n == name:
            return lo
    return None


def _run_gate(env_extra: dict) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(env_extra)
    return subprocess.run(
        [PY, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO_ROOT), env=env, stdin=subprocess.DEVNULL, timeout=300,
    )


# ── FR-001 / FR-002：探测器认得出 ────────────────────────────────────

class TestClaimPatternCoversSwsFamily(unittest.TestCase):
    """FR-001：`sw[A-Z]\\w+` 要求 `sw` 后紧跟大写 ⇒ `sws*` 全族不命中（本轮实测）。"""

    def test_claim_matches_sws_name_family(self):
        m = _load_gate()
        for probe in ("swsSolverType_e",
                      "swsTopologyDemoldDirectionOption_e",
                      "swsTopologyActivationOption_e",
                      "反射：swsTopologyDemoldDirectionOption_e"):
            self.assertRegex(
                probe, m.CLAIM,
                "★ 探测器认不出 %r ⇒ `sws*` 全族（转储里 300+ 个枚举名）落在盲区外" % probe)

    def test_claim_matches_reflection_provenance_words(self):
        """FR-002：本仓的出处自称**不止**「官方」一种写法。"""
        m = _load_gate()
        for probe in ("反射确认的实参个数（**不含**末尾 by-ref 出参）",
                      "反射：swsTopologyDemoldDirectionOption_e",
                      "由转储生成",
                      "CHM 那页顶上的 Example",
                      "★ 出处：本仓 `_raw` 的 cosworks 枚举页"):
            self.assertRegex(
                probe, m.CLAIM,
                "★ 探测器认不出 %r ⇒ 该表「自称有出处」却看不见" % probe)

    def test_claim_still_matches_legacy_official_probes(self):
        """★ 放宽不许**丢掉**旧探针 —— 否则 44 张已表态的表会掉出清单（本判据会立刻抓）。"""
        m = _load_gate()
        for probe in ("官方", "swapi", "swSolverType_e", "swViewEntityType_e"):
            self.assertRegex(probe, m.CLAIM, "★ 放宽后旧探针 %r 反而认不出了" % probe)


# ── FR-003：新暴露的表进了盲区清单，且逐张表态 ──────────────────────

class TestNewlyVisibleTablesAreDispositioned(unittest.TestCase):

    def test_sws_tables_are_now_visible_in_the_blind_inventory(self):
        m = _load_gate()
        blind = {(f, lo) for f, lo, _name, _n in m.find_uncovered_claimed_tables()}
        for fname, name, _enum in SWS_ENUM_TABLES:
            lo = _table_line(m, fname, name)
            self.assertIsNotNone(lo, "★ 表 %s:%s 不存在（名字写错？）" % (fname, name))
            self.assertIn(
                (fname, lo), blind,
                "★ %s:%s 自称 `sws*` 官方枚举，却没进盲区清单 ⇒ 224 的判红对它无效"
                % (fname, name))

    def test_reflection_derived_tables_are_now_visible_in_the_blind_inventory(self):
        m = _load_gate()
        blind = {(f, lo) for f, lo, _name, _n in m.find_uncovered_claimed_tables()}
        for fname, name, _sub in REFLECTION_DERIVED_TABLES:
            lo = _table_line(m, fname, name)
            self.assertIsNotNone(lo, "★ 表 %s:%s 不存在（名字写错？）" % (fname, name))
            self.assertIn(
                (fname, lo), blind,
                "★ %s:%s 的窗口里自称「反射/转储/CHM/_raw」，却没进盲区清单" % (fname, name))

    def test_every_blind_table_is_dispositioned(self):
        m = _load_gate()
        blind = m.find_uncovered_claimed_tables()
        self.assertGreaterEqual(
            len(blind), BASELINE_BLIND,
            "盲区表只有 %d 张（基线 %d）—— ★ 探测器又漏了，先查清再改本判据"
            % (len(blind), BASELINE_BLIND))
        disp = m.parse_dispositions()
        missing = [(f, lo, name) for f, lo, name, _n in blind if (f, lo) not in disp]
        self.assertEqual(
            missing, [],
            "★ 这些「自称有出处却无 # swXxx 覆盖」的表**没有表态** ⇒ 门禁必须红：\n  %s"
            % "\n  ".join("%s:%d %s" % t for t in missing))

    def test_the_three_sws_enums_declare_the_matching_official_enum(self):
        """FR-003：三张表的 `enum` 声明必须**指对枚举**，且表内值集 ⊆ 该枚举取值集。"""
        m = _load_gate()
        disp = m.parse_dispositions()
        sets = m.enum_value_sets()
        for fname, name, enum_name in SWS_ENUM_TABLES:
            lo = _table_line(m, fname, name)
            self.assertIsNotNone(lo, "★ 表 %s:%s 不存在（名字写错？）" % (fname, name))
            self.assertIn(
                (fname, lo), disp,
                "★ %s:%s 没有表级出处声明" % (fname, name))
            code, arg, _line = disp[(fname, lo)]
            self.assertEqual(
                (code, arg), ("enum", enum_name),
                "★ %s:%s 应声明 `enum %s`，实为 `%s %s`"
                % (fname, name, enum_name, code, arg))
            self.assertIn(
                enum_name, sets,
                "★ 枚举 %r 在出厂反射转储里解析不到 ⇒ 声明无法被核" % enum_name)
            bad = sorted({v for v in m.table_values(fname, lo) if v not in sets[enum_name]})
            self.assertEqual(
                bad, [],
                "★ %s:%s 的值 %s 不在 `%s` 取值集 %s 里"
                % (fname, name, bad, enum_name, sorted(sets[enum_name])))

    def test_reflection_derived_tables_declare_the_expected_subclass(self):
        """FR-003：6 张 `*_ARITY` ⇒ `not-enum arity`；`_REFGEOM_POSITIONS` ⇒ `not-enum index`。"""
        m = _load_gate()
        disp = m.parse_dispositions()
        for fname, name, sub in REFLECTION_DERIVED_TABLES:
            lo = _table_line(m, fname, name)
            self.assertIsNotNone(lo, "★ 表 %s:%s 不存在（名字写错？）" % (fname, name))
            self.assertIn((fname, lo), disp, "★ %s:%s 没有表级出处声明" % (fname, name))
            code, arg, _line = disp[(fname, lo)]
            self.assertEqual(
                (code, arg), ("not-enum", sub),
                "★ %s:%s 应声明 `not-enum %s`，实为 `%s %s`"
                % (fname, name, sub, code, arg))
            self.assertIn(arg, m.NOT_ENUM_SUBS, "★ `not-enum %s` 不在封闭词表里" % arg)


# ── FR-004：端到端负例（★ 本轮唯一能让「放宽正则」这件事**红**的判据）──

class TestGateGoesRedOnSwsClaimWithoutDisposition(unittest.TestCase):
    """★ 合成树：注释自称 `sws*` 官方枚举，表上**没有** `#: enum-gate:` ⇒ 门禁必须 exit 1。"""

    _DUMP = "## swsFakeEnum_e\n  swsFakeA = 0\n  swsFakeB = 1\n"
    #: ★ 注释里**只有** `sws*` 名（不含「官方」二字）—— 专测 FR-001 那一条。
    _CLAIM_LINE = "#: ★ 反射：swsFakeEnum_e（★ 合成夹具）\n"

    def _synthetic_tree(self, root: Path, body: str) -> None:
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "sw_fake.py").write_text(body, encoding="utf-8")
        (root / "fake_dump.txt").write_text(self._DUMP, encoding="utf-8")

    def _env(self, root: Path) -> dict:
        return {
            "DSH_ENUM_GATE_ROOT": str(root),
            "DSH_ENUM_DUMP": str(root / "fake_dump.txt"),
        }

    def test_undeclared_sws_claim_makes_the_gate_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, self._CLAIM_LINE + "FAKE_TABLE = {'a': 0, 'b': 1}\n")
            proc = _run_gate(self._env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ 合成树里有一张注释自称 `swsFakeEnum_e` 却没表态的表，门禁却 exit %d"
                " ⇒ 探测器认不出 `sws*` ⇒ 判红机制对 `sws*` 全族失效\n--- stdout ---\n%s"
                % (proc.returncode, proc.stdout))
            self.assertIn("FAKE_TABLE", proc.stdout, "★ 判红却没点名是哪张表")
            self.assertIn("未表态", proc.stdout, "★ 判红却没说明理由")

    def test_declared_sws_claim_keeps_the_gate_green(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, (
                self._CLAIM_LINE
                + "#: enum-gate: enum swsFakeEnum_e\n"
                + "FAKE_TABLE = {'a': 0, 'b': 1}\n"))
            proc = _run_gate(self._env(root))
            self.assertEqual(
                proc.returncode, 0,
                "★ 已表态的表仍被判红 ⇒ 表态机制坏了\n--- stdout ---\n%s" % proc.stdout)

    def test_wrong_value_in_a_sws_enum_table_is_caught(self):
        """★ 反向：声明了 `enum swsFakeEnum_e` 但值不在枚举里 ⇒ 必须判红（否则表态是空判据）。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, (
                self._CLAIM_LINE
                + "#: enum-gate: enum swsFakeEnum_e\n"
                + "FAKE_TABLE = {'a': 0, 'b': 77}\n"))
            proc = _run_gate(self._env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ 值 77 不在 `swsFakeEnum_e`（值集 {0,1}）里，门禁却 exit %d"
                " ⇒ `enum` 声明是空判据\n--- stdout ---\n%s" % (proc.returncode, proc.stdout))
            self.assertRegex(proc.stdout, re.compile(r"77"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
