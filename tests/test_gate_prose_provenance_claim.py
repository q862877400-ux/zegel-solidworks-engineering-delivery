r"""★ 判据：门禁盲区探测器必须认得出「散文式出处自称」（spec 226）。

背景（225 登记的头号未过门）：
  · 223 造出「盲区探测器」`find_uncovered_claimed_tables()`：未覆盖 **且** 上方 15 行窗口里
    `CLAIM` 命中 ⇒ 算「自称有出处」；224 让「未表态」**判红**；225 把 `CLAIM` 放宽到认
    `sws[A-Z]` 名族与「反射/转储/CHM/`_raw`」。
  · ★★ 225 自己写明：`CLAIM` 是**启发式** —— 用**散文**（不含那些词）声称出处的表**仍看不见**，
    登记为未过门。本轮**先量后收口**：量到 **1 张**（`sw_import_mesh_reference.py:69 SW_LENGTH_UNITS`，
    注释自称「本机 SolidWorks 2024 swconst.dll 验证值」——`本机`/`swconst`/`.dll` **一个都不在** `CLAIM` 里）。

⇒ 本判据锁五件事：
  1. **探测器认得出**「真机观测 / DLL 反射 / 离线文档 / 摘录动词」四类散文自称（FR-001）；
  2. **★ 但不认**有歧义的 `参考`/`据`/`按`（FR-001 的有意排除边界 —— 防将来被顺手加宽）；
  3. **旧探针一个不丢**（FR-005：放宽最常坏在原处）；
  4. **新暴露的 1 张表进了盲区清单且表态正确**（`enum swLengthUnit_e`，值集 ⊆ 官方，FR-002）；
  5. **端到端负例**：合成树里一张注释自称「本机…swconst.dll 验证值」却没表态的表
     ⇒ 门禁**必须 exit 1** 且点名（★ 否则「放宽正则」这件事**没有可红的判据** = 空判据，FR-003）。

★ **按表名定位，不按行号** —— 本轮要往表上方插声明行，**行号会移位**；
  行号写死在判据里 = 一插就假红（与「把偶然当判据」同族）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_gate_prose_provenance_claim.py —— 本文件自身
# 定位:   spec 226 FR-001～FR-005 的判据；被测对象是 `scripts/check_enum_values_vs_reflection.py`。
# 官方依据: `C:\swapi\enums\swLengthUnit_e.md`（官方 SDK 解包）
#           · `_raw/enum_values_sldworks.txt` 第 959–970 行（出厂反射转储）—— 两源独立、逐条一致
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

#: ★ 本轮实测基线：放宽后盲区 = **55**（225 的 54 + 散文自称新暴露 1 张）。
#: ★ 用**下界**断言：将来新增的表**表态后**不该让本判据假红。
BASELINE_BLIND = 55

#: ★ 本轮新暴露的那 1 张 —— `(文件, 表名, 应声明的枚举名)`。★ 按表名定位。
PROSE_CLAIM_TABLE = ("sw_import_mesh_reference.py", "SW_LENGTH_UNITS", "swLengthUnit_e")

#: ★ 四类「散文式出处自称」各挑代表（FR-001）。★ 全部取自本仓真实注释的写法。
PROSE_CLAIM_PROBES = (
    "本机 SolidWorks 2024 swconst.dll 验证值",          # ① 真机观测 + ② 程序集
    "实测确认的实参个数",                                # ① 真机观测
    "真机观测得到",                                      # ① 真机观测
    "本地 SolidWorks 导出",                              # ① 真机观测
    "对 swdocumentmgr.dll 的纯元数据反射",               # ② 程序集/反射
    "按 SolidWorks 帮助手册抄录",                        # ③ 离线文档
    "摘自 CHM 那页",                                     # ④ 摘录动词（★ CHM 本身已在 CLAIM 里）
    "取自官方文档页",                                    # ④ 摘录动词
)

#: ★ **有意排除**的歧义写法（FR-001 边界）——它们**不是**出处自称，加进去只会制造噪声。
#: ★ 这条断言的作用是**冻结边界**：将来若有人顺手把 `参考` 加进 `CLAIM`，本判据立刻红。
AMBIGUOUS_PROBES = (
    "仅供参考，不作依据",
    "按需展开",
    "据当前配置",
)

#: ★ 旧探针（225 及更早能认出的写法）—— 放宽**不许**把它们弄丢（FR-005）。
LEGACY_PROBES = (
    "官方",
    "swapi",
    "swSolverType_e",
    "swViewEntityType_e",
    "swsSolverType_e",
    "swsTopologyDemoldDirectionOption_e",
    "反射：swsTopologyDemoldDirectionOption_e",
    "由转储生成",
    "CHM 那页顶上的 Example",
    "★ 出处：本仓 `_raw` 的 cosworks 枚举页",
)


def _load_gate():
    spec = importlib.util.spec_from_file_location("enum_gate_226", GATE)
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


# ── FR-001：探测器认得出散文式自称 ───────────────────────────────────

class TestClaimPatternCoversProseProvenance(unittest.TestCase):
    """FR-001：`本机`/`实测`/`.dll`/`swconst`/`手册`/`摘自` 这类写法必须命中。"""

    def test_claim_matches_prose_provenance_words(self):
        m = _load_gate()
        for probe in PROSE_CLAIM_PROBES:
            self.assertRegex(
                probe, m.CLAIM,
                "★ 探测器认不出散文式出处自称 %r ⇒ 该表「自称有出处」却看不见" % probe)

    def test_claim_does_not_match_ambiguous_prose(self):
        """★ FR-001 的**有意排除边界**：`参考`/`据`/`按` 歧义太大，不进 `CLAIM`。

        ★ 这条断言的作用是**冻结边界** —— 将来若有人顺手把 `参考` 加进 `CLAIM`，
          本判据立刻红（否则「加宽」会以「顺手」的方式无限蔓延）。
        """
        m = _load_gate()
        for probe in AMBIGUOUS_PROBES:
            self.assertNotRegex(
                probe, m.CLAIM,
                "★ %r 不是出处自称（歧义写法），不该被认成「自称有出处」" % probe)

    def test_claim_still_matches_legacy_probes(self):
        """★ FR-005：放宽不许**丢掉**旧探针 —— 否则 54 张已表态的表会掉出清单。"""
        m = _load_gate()
        for probe in LEGACY_PROBES:
            self.assertRegex(probe, m.CLAIM, "★ 放宽后旧探针 %r 反而认不出了" % probe)


# ── FR-002：新暴露的 1 张表进了盲区清单，且表态正确 ──────────────────

class TestProseClaimTableIsDispositioned(unittest.TestCase):

    def test_prose_claim_table_is_now_visible_in_the_blind_inventory(self):
        m = _load_gate()
        fname, name, _enum = PROSE_CLAIM_TABLE
        lo = _table_line(m, fname, name)
        self.assertIsNotNone(lo, "★ 表 %s:%s 不存在（名字写错？）" % (fname, name))
        blind = {(f, line) for f, line, _n, _c in m.find_uncovered_claimed_tables()}
        self.assertIn(
            (fname, lo), blind,
            "★ %s:%s 注释自称「本机 … swconst.dll 验证值」，却没进盲区清单"
            " ⇒ 224 的判红对它无效" % (fname, name))

    def test_prose_claim_table_declares_the_matching_official_enum(self):
        """FR-002：声明必须**指对枚举**，且表内值集 ⊆ 该枚举取值集（两源已核，无冲突）。"""
        m = _load_gate()
        fname, name, enum_name = PROSE_CLAIM_TABLE
        lo = _table_line(m, fname, name)
        self.assertIsNotNone(lo, "★ 表 %s:%s 不存在（名字写错？）" % (fname, name))
        disp = m.parse_dispositions()
        self.assertIn((fname, lo), disp, "★ %s:%s 没有表级出处声明" % (fname, name))
        code, arg, _line = disp[(fname, lo)]
        self.assertEqual(
            (code, arg), ("enum", enum_name),
            "★ %s:%s 应声明 `enum %s`，实为 `%s %s`" % (fname, name, enum_name, code, arg))
        sets = m.enum_value_sets()
        self.assertIn(
            enum_name, sets,
            "★ 枚举 %r 在出厂反射转储里解析不到 ⇒ 声明无法被核" % enum_name)
        bad = sorted({v for v in m.table_values(fname, lo) if v not in sets[enum_name]})
        self.assertEqual(
            bad, [],
            "★ %s:%s 的值 %s 不在 `%s` 取值集 %s 里"
            % (fname, name, bad, enum_name, sorted(sets[enum_name])))

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


# ── FR-003：端到端负例（★ 本轮唯一能让「放宽正则」这件事**红**的判据）──

class TestGateGoesRedOnProseClaimWithoutDisposition(unittest.TestCase):
    """★ 合成树：注释自称「本机…验证值」，表上**没有** `#: enum-gate:` ⇒ 门禁必须 exit 1。"""

    _DUMP = "## swLengthUnit_e\n  swMM = 0\n  swCM = 1\n  swMETER = 2\n"
    #: ★ 注释**只含散文自称**（`本机` + `.dll`），**不含** `官方`/`swapi`/`反射`/`转储`/`CHM`/`_raw`/`sws*`
    #: ⇒ 专测 FR-001 这一条（旧 `CLAIM` 对它**必然不命中**）。
    _CLAIM_LINE = "# 本机 SolidWorks 2024 swconst.dll 验证值（★ 合成夹具）\n"

    def _synthetic_tree(self, root: Path, body: str) -> None:
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "sw_fake.py").write_text(body, encoding="utf-8")
        (root / "fake_dump.txt").write_text(self._DUMP, encoding="utf-8")

    def _env(self, root: Path) -> dict:
        return {
            "DSH_ENUM_GATE_ROOT": str(root),
            "DSH_ENUM_DUMP": str(root / "fake_dump.txt"),
        }

    def test_undeclared_prose_claim_makes_the_gate_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, self._CLAIM_LINE + "FAKE_UNITS = {'mm': 0, 'cm': 1}\n")
            proc = _run_gate(self._env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ 合成树里有一张注释自称「本机…swconst.dll 验证值」却没表态的表，门禁却 exit %d"
                " ⇒ 探测器认不出散文式自称 ⇒ 判红机制对这类表失效\n--- stdout ---\n%s"
                % (proc.returncode, proc.stdout))
            self.assertIn("FAKE_UNITS", proc.stdout, "★ 判红却没点名是哪张表")
            self.assertIn("未表态", proc.stdout, "★ 判红却没说明理由")

    def test_declared_prose_claim_keeps_the_gate_green(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, (
                self._CLAIM_LINE
                + "#: enum-gate: enum swLengthUnit_e\n"
                + "FAKE_UNITS = {'mm': 0, 'cm': 1}\n"))
            proc = _run_gate(self._env(root))
            self.assertEqual(
                proc.returncode, 0,
                "★ 已表态的表仍被判红 ⇒ 表态机制坏了\n--- stdout ---\n%s" % proc.stdout)

    def test_wrong_value_in_a_prose_claim_table_is_caught(self):
        """★ 反向：声明了 `enum swLengthUnit_e` 但值不在枚举里 ⇒ 必须判红（否则表态是空判据）。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._synthetic_tree(root, (
                self._CLAIM_LINE
                + "#: enum-gate: enum swLengthUnit_e\n"
                + "FAKE_UNITS = {'mm': 0, 'cm': 77}\n"))
            proc = _run_gate(self._env(root))
            self.assertEqual(
                proc.returncode, 1,
                "★ 值 77 不在 `swLengthUnit_e`（值集 {0,1,2}）里，门禁却 exit %d"
                " ⇒ `enum` 声明是空判据\n--- stdout ---\n%s" % (proc.returncode, proc.stdout))
            self.assertRegex(proc.stdout, re.compile(r"77"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
