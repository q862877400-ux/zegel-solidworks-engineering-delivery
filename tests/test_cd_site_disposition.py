"""★ spec 237 判据：`CreateDefinition` 站点处置门禁（逐站点表态 + 自证 + 读取器宽化）。"""
# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_cd_site_disposition.py
# 定位:   钉住 `scripts/check_create_definition_site_disposition.py` 的契约：
#         ① 真树 8 个站点 · checked 6 · unmapped 0 · no-members-used 2
#            （★ spec 239 后 9/6/1/2 · ★ spec 240 后 8/6/**0**/2 —— 三个「该审却漏审」的常量
#             全部处置完毕）；
#         ② 非 checked 站点未表态即红；③ 四个 code 各自的自证条件；
#         ④ 下界冻结 / 零检查即红 / 官方源缺失走 [SKIP]；
#         ⑤ ★ FR-006：`module_consts` 必须读到**带行尾注释**的常量行。
# 官方依据: 合成树夹具（只含被测对象）+ 真树
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_create_definition_site_disposition.py"
PY = sys.executable

FIXTURE_DOC = "## Parameters\n\n- swFmAlpha (alpha)\n"
FIXTURE_OVERVIEW = "## Description\n\nalpha feature data\n"
FIXTURE_DUMPS = "swFmAlpha = 34\nswFmBeta = 3\n"


def _write_tree(tmp: Path, body: str, *, types: bool = True, dumps: bool = True) -> Path:
    """造一棵**只含被测对象**的合成树；返回其根。"""
    scripts = tmp / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "sw_fixture.py").write_text(textwrap.dedent(body), encoding="utf-8")
    if types:
        t = tmp / "types"
        (t / "IFeatureManager").mkdir(parents=True, exist_ok=True)
        (t / "IFeatureManager" / "CreateDefinition.md").write_text(FIXTURE_DOC, encoding="utf-8")
        a = t / "IFixtureAlpha"
        a.mkdir(parents=True, exist_ok=True)
        (a / "_overview.md").write_text(FIXTURE_OVERVIEW, encoding="utf-8")
        (a / "Alpha.md").write_text("x\n", encoding="utf-8")
        (a / "SetBeta.md").write_text("x\n", encoding="utf-8")
    if dumps:
        d = tmp / "dumps"
        d.mkdir(parents=True, exist_ok=True)
        (d / "enum_values_sldworks.txt").write_text(FIXTURE_DUMPS, encoding="utf-8")
    return tmp


def _run(tree: Path | None = None, *, types: bool | None = None,
         baseline: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if tree is not None:
        env["DSH_CD_SITE_ROOT"] = str(tree)
        env["DSH_CD_SITE_TYPES"] = str(tree / "types") if types is not False else str(tree / "_nope")
        env["DSH_CD_SITE_DUMPS"] = str(tree / "dumps")
    #: ★ 合成树的下界必须归零 —— 否则 `[baseline-shrunk]` 会**先红**，
    #:   负例就「因错误的原因」通过了（232/233 的坑）。下界本身由专门用例覆盖。
    env["DSH_CD_SITE_BASELINE_MIN"] = baseline or ("0,0,0,0,0,0" if tree is not None else "")
    return subprocess.run([PY, "-B", str(GATE)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env, cwd=str(ROOT))


#: ★★ 声明的挂载点是 **`CreateDefinition(...)` 调用行**（不是调用方的行）——
#:   与真树同构：`sw_sheet_metal.py` 的 helper 一行 5 个计划共用一个声明。
_HELPER = """
    SW_FM_A = 34
    SW_FM_B = 3

    def build(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        DECL
        data = get_com_member(manager, "CreateDefinition", int(fm_type))
        data.Alpha = 1
        return data
"""

_BARE = """
    SW_FM_A = 34
    SW_FM_B = 3

    def build_bare(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        DECL
        data = get_com_member(manager, "CreateDefinition", int(fm_type))
        return get_com_member(manager, "CreateFeature", data)
"""

_CALLERS = """
    def use_ok(model):
        return build(model, SW_FM_A)

    def use_bad(model):
        return build(model, SW_FM_B)
"""

_CALL_OK = """
    def use_ok(model):
        return build(model, SW_FM_A)
"""


def _src(tmpl: str, decl: str = "", tail: str = _CALLERS, helper: str = "build") -> str:
    """把声明插到 helper 的 `CreateDefinition` 行上方（`DECL` 占位符）。"""
    return tmpl.replace("DECL", decl) + (tail.replace("build(", helper + "(") if helper != "build"
                                         else tail)


class CdSiteDispositionTest(unittest.TestCase):

    # ── 真树 ────────────────────────────────────────────────────────
    def test_real_tree_passes(self):
        r = _run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[PASS]", r.stdout)

    def test_real_tree_reads_ten_sites(self):
        r = _run()
        self.assertIn("站点 8", r.stdout)
        #: ★ spec 239：`sites` 10 → **9**、`unmapped` 2 → **1** —— `sw_sheet_metal.create_draft`
        #:   改走官方入口 `InsertMultiFaceDraft` 后，它的 `CreateDefinition(swFmDraft)` 站点**消失**。
        #:   ★ spec 240：`sites` 9 → **8**、`unmapped` 1 → **0** ——
        #:   `sw_weldment.create_profile_center_mate` 改走官方入口
        #:   `IAssemblyDoc::CreateMateData` + `CreateMate` 后，它唯一的站点（连同无调用方的
        #:   共用骨架 `_create_from_definition`）**整体消失** ⇒ ★ **三个「该审却漏审」的常量
        #:   全部处置完毕**，`unmapped` 归零**不是**读取器漏了。
        #:   ★ spec 238：`checked` 5 → **6** —— `sw_motion.py` 那个站点的
        #:   常量被官方 `IMotionStudy::CreateDefinition` 页**逐条点名** ⇒ 进了映射表。
        self.assertIn("checked 6", r.stdout)
        self.assertIn("unmapped 0", r.stdout)
        self.assertIn("no-members-used 2", r.stdout)

    # ── FR-006：读取器宽化（★ 改实现前本用例必红）────────────────────
    def test_module_consts_reads_trailing_comment(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import check_interface_member_ownership as cimo  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.py"
            p.write_text("SW_FM_A = 34\nSW_FM_B = 3  # swFmBeta\nSW_FM_C = 7\t# tab\n",
                         encoding="utf-8")
            got = cimo.module_consts(p)
        self.assertEqual(got.get("SW_FM_A"), "34")
        self.assertEqual(got.get("SW_FM_B"), "3", "带行尾注释的常量行必须读得到")
        self.assertEqual(got.get("SW_FM_C"), "7", "制表符 + 注释也必须读得到")

    # ── 未表态即红 / 表态即绿 ────────────────────────────────────────
    def test_undeclared_site_makes_the_gate_red(self):
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(_HELPER))
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[undeclared]", r.stdout)

    def test_declared_site_passes(self):
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(
                _HELPER, "#: cd-site: unmapped swFmBeta 该常量未进 `CONST → 接口` 映射表"))
            r = _run(tree)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[PASS]", r.stdout)

    def test_unknown_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(_HELPER, "#: cd-site: whatever 编的 code"))
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("未知 code", r.stdout)

    # ── 各 code 的自证条件 ──────────────────────────────────────────
    def test_unmapped_const_list_must_be_complete(self):
        """声明 `unmapped` 却列错常量 ⇒ 红（集合必须相等）。"""
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(
                _HELPER, "#: cd-site: unmapped swFmGamma 列了个不相干的常量"))
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("集合不符", r.stdout)

    def test_redundant_declaration_on_checked_site_is_red(self):
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(
                _HELPER, "#: cd-site: no-members-used 这个站点其实是 checked", tail=_CALL_OK))
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[redundant-decl]", r.stdout)

    #: ★ 两个 helper：`build` = checked 站点（保证 `checked != 0`），
    #:   `build_bare` = 待测的「建了 data 但不设成员」站点。
    _TWO = """
    SW_FM_A = 34
    SW_FM_B = 3

    def build(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        data = get_com_member(manager, "CreateDefinition", int(fm_type))
        data.Alpha = 1
        return data

    def build_bare(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        DECL
        data = get_com_member(manager, "CreateDefinition", int(fm_type))
        return get_com_member(manager, "CreateFeature", data)

    def use_ok(model):
        return build(model, SW_FM_A)

    def use_bare(model):
        return build_bare(model, BARE_CONST)
"""

    def test_no_members_used_self_proof(self):
        """★ 声明 `no-members-used`，但该站点**实际是 `unmapped`** ⇒ 红（自证失败）。"""
        body = self._TWO.replace("BARE_CONST", "SW_FM_B").replace(
            "DECL", "#: cd-site: no-members-used 声明与事实不符")
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), body)
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("与实际处置不符", r.stdout)

    def test_no_members_used_declared_correctly_passes(self):
        body = self._TWO.replace("BARE_CONST", "SW_FM_A").replace(
            "DECL", "#: cd-site: no-members-used 建了 data 但不设任何成员")
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), body)
            r = _run(tree)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[PASS]", r.stdout)

    def test_dynamic_self_proof_rejects_resolvable_const(self):
        """★★ `dynamic` 的守卫：实参其实是**带尾注释的模块常量** ⇒ 红 `reader-too-narrow`。"""
        tmpl = """
    SW_FM_A = 34
    SW_FM_B = 3  # swFmBeta

    def build(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        DECL
        data = get_com_member(manager, "CreateDefinition", int(fm_type))
        data.Alpha = 1
        return data
"""
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(tmpl, "#: cd-site: dynamic 读不出常量，所以声明动态"))
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("reader-too-narrow", r.stdout)

    # ── 下界冻结 / 零检查 / 便携 ────────────────────────────────────
    def test_baseline_shrunk_is_red(self):
        r = _run(baseline="99,99,99,99,99,99")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[baseline-shrunk]", r.stdout)

    def test_zero_checked_is_red(self):
        tmpl = """
    def build(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        DECL
        return get_com_member(manager, "CreateDefinition", int(fm_type))

    def use_dyn(model, t):
        return build(model, t)
"""
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(tmpl, "#: cd-site: dynamic 运行期给的常量"))
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[zero-checked]", r.stdout)

    def test_skipped_when_official_docs_absent(self):
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(_HELPER), types=False)
            r = _run(tree, types=False)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("[SKIP]", r.stdout)

    def test_synthetic_tree_does_not_read_real_sources(self):
        """★ 源隔离：合成树的读数必须**与真树不同**（证明没读真树）。"""
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _src(_HELPER, tail=_CALL_OK))
            r = _run(tree)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("站点 1", r.stdout)
        self.assertNotIn("站点 8", r.stdout)


if __name__ == "__main__":
    unittest.main()
