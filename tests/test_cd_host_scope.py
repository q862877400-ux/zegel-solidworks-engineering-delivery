"""★ spec 238/239 判据：`CreateDefinition` 站点的**宿主域**门禁（官方点名 + 四个违规码）。"""
# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_cd_host_scope.py
# 定位:   钉住 `scripts/check_cd_host_scope.py` 的契约：
#         ① 真树 8 个站点 · 常量被官方点名 1 · **无宿主常量站点 0**（spec 239：10 → 9 ·
#            ★ spec 240：9 → 8 且 no-host 1 → 0 —— 两个「官方不支持」的靶子**全部处置完毕**）；
#         ② 四个违规码各自**有靶子**（`should-map` / `unsupported-path` 走端到端或纯函数，
#            `host-mismatch` / `ambiguous-host` 直接喂 `judge_sites()` —— 正常跑时映射表先由
#            官方点名播种，这两个码不会自然触发）；
#         ③ 下界冻结 / 零检查即红 / 官方源缺失走 `[SKIP]`；
#         ④ 源隔离：合成树读数必须与真树不同。
#         ★ spec 239 新增：`unsupported-path` 的 `alt` 两条自证（成员页必须存在 · 不得 Obsolete）
#           —— 用 `judge_unsupported()` 纯函数**直接喂靶子**（真树上 `alt` 只写 `unknown`）。
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
GATE = ROOT / "scripts" / "check_cd_host_scope.py"
PY = sys.executable

#: 散文标签（**匹配不上**任何描述）⇒ 该常量在官方清单里却映射不出 ⇒ `should-map`。
FIXTURE_FM_DOC = "## Parameters\n\n- swFmAlpha (zzz)\n"
#: 官方**逐条点名**返回接口 ⇒ 直接映射。
FIXTURE_MS_DOC = "## Parameters\n\n- swFmAlpha ([[IFixtureAlpha]])\n"
FIXTURE_OVERVIEW = "## Description\n\nalpha feature data\n"
FIXTURE_DUMPS = "swFmAlpha = 34\nswFmBeta = 3\n"

#: ★★ 声明的挂载点是 **`CreateDefinition(...)` 调用行**（不是调用方的行）。
_BODY = """
    SW_FM_A = 34
    SW_FM_B = 3

    def build(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        data = get_com_member(manager, "CreateDefinition", int(fm_type))
        data.Alpha = 1
        return data

    def use_ok(model):
        return build(model, SW_FM_A)
"""

#: ★ spec 239 夹具：**两个**站点 —— `SW_FM_A`（被官方点名 ⇒ `checked`，**自带已覆盖样本**，
#:   否则 `[zero-checked]` 会先红 ⇒ 负例「因错误的原因」通过）+ `SW_FM_B`（**无任何宿主页** ⇒
#:   `unsupported-path` 的靶子）。★ 两者**共用同一个 `CreateDefinition` 调用行** ⇒ 同一份声明块。
_BODY_TWO = """
    SW_FM_A = 34
    SW_FM_B = 3

    def build(model, fm_type):
        manager = get_com_member(model, "FeatureManager")
        data = get_com_member(manager, "CreateDefinition", int(fm_type))
        data.Alpha = 1
        return data

    def use_named(model):
        return build(model, SW_FM_A)

    def use_no_host(model):
        return build(model, SW_FM_B)
"""


def _write_tree(tmp: Path, body: str, *, fm_doc: str = FIXTURE_FM_DOC,
                ms_doc: str | None = None, types: bool = True) -> Path:
    """造一棵**只含被测对象**的合成树；返回其根。"""
    scripts = tmp / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "sw_fixture.py").write_text(textwrap.dedent(body), encoding="utf-8")
    if types:
        t = tmp / "types"
        (t / "IFeatureManager").mkdir(parents=True, exist_ok=True)
        (t / "IFeatureManager" / "CreateDefinition.md").write_text(fm_doc, encoding="utf-8")
        if ms_doc is not None:
            (t / "IMotionStudy").mkdir(parents=True, exist_ok=True)
            (t / "IMotionStudy" / "CreateDefinition.md").write_text(ms_doc, encoding="utf-8")
        a = t / "IFixtureAlpha"
        a.mkdir(parents=True, exist_ok=True)
        (a / "_overview.md").write_text(FIXTURE_OVERVIEW, encoding="utf-8")
        (a / "Alpha.md").write_text("x\n", encoding="utf-8")
        (a / "SetBeta.md").write_text("x\n", encoding="utf-8")
        d = tmp / "dumps"
        d.mkdir(parents=True, exist_ok=True)
        (d / "enum_values_sldworks.txt").write_text(FIXTURE_DUMPS, encoding="utf-8")
    return tmp


def _run(tree: Path | None = None, *, types: bool | None = None,
         baseline: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if tree is not None:
        env["DSH_CD_HOST_ROOT"] = str(tree)
        env["DSH_CD_HOST_TYPES"] = str(tree / "types") if types is not False else str(tree / "_nope")
        env["DSH_CD_HOST_DUMPS"] = str(tree / "dumps")
    #: ★ 合成树的下界必须归零 —— 否则 `[baseline-shrunk]` 会**先红**，
    #:   负例就「因错误的原因」通过了（232/233/237 的坑）。
    #: ★ spec 239：下界是 **3 个**数（`sites,named,no-host`）—— 少给一个会**静默退回真树下界**。
    env["DSH_CD_HOST_BASELINE_MIN"] = baseline or ("0,0,0" if tree is not None else "")
    return subprocess.run([PY, "-B", str(GATE)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env, cwd=str(ROOT))


def _site(const: str, code: str, name: str = "sw_x.py", line: int = 1) -> dict:
    return {"path": Path(name), "line": line, "const": const, "code": code}


class CdHostScopeTest(unittest.TestCase):

    # ── 真树 ────────────────────────────────────────────────────────
    def test_real_tree_passes(self):
        r = _run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[PASS]", r.stdout)

    def test_real_tree_reads_eight_sites_one_named_and_no_no_host(self):
        r = _run()
        self.assertIn("站点 8", r.stdout)
        self.assertIn("常量被官方点名 1", r.stdout)
        #: ★ spec 240：`无宿主常量站点` 1 → **0** —— `sw_weldment.create_profile_center_mate`
        #:   改走官方入口 `IAssemblyDoc::CreateMateData` + `CreateMate` 后，
        #:   真树上**再无**「用了官方不支持的 `CreateDefinition` 常量」的站点。
        #:   ★ 这不代表本码失效：`unsupported-path` 的触发条件是「站点存在 + 无宿主 + 未表态」。
        self.assertIn("无宿主常量站点 0", r.stdout)

    # ── 端到端：`should-map`（★ 改实现前本用例必红）────────────────
    def test_const_in_official_list_but_unmapped_is_red(self):
        """★ 常量**在官方宿主页的 `Type` 清单里**却报 `unmapped` ⇒ 红（不许逃避）。"""
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _BODY)
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[should-map]", r.stdout)

    def test_officially_named_const_makes_the_site_checked(self):
        """★ 官方**点名**返回接口 ⇒ 进映射表 ⇒ 站点 `checked` ⇒ 绿。"""
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _BODY, fm_doc="## Parameters\n\n- swFmBeta (beta)\n",
                               ms_doc=FIXTURE_MS_DOC)
            r = _run(tree)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[PASS]", r.stdout)
        self.assertIn("常量被官方点名 1", r.stdout)

    # ── 两个码的**靶子**（直接喂 `judge_sites()`）────────────────────
    @staticmethod
    def _judge():
        sys.path.insert(0, str(ROOT / "scripts"))
        import check_cd_host_scope as gate  # noqa: PLC0415

        return gate

    def test_host_mismatch_when_map_disagrees_with_official_naming(self):
        """★★ 映射表与官方点名不一致 ⇒ 红（官方断言不得被覆盖）。"""
        gate = self._judge()
        v, _gaps, named, _nh = gate.judge_sites(
            [_site("swFmAlpha", "checked")],
            {"swFmAlpha": {"IMotionStudy": "IFixtureAlpha"}},
            {"swFmAlpha": ["IMotionStudy"]},
            {"swFmAlpha": "ISomethingElse"},
            lambda i: {"Alpha"},
        )
        self.assertEqual(named, 1)
        self.assertEqual([x["kind"] for x in v], ["host-mismatch"])

    def test_ambiguous_host_when_two_pages_name_different_interfaces(self):
        """★★ 同一常量在两个宿主页被点名成**不同**接口 ⇒ 不猜，红。"""
        gate = self._judge()
        v, _gaps, _n, _nh = gate.judge_sites(
            [_site("swFmAlpha", "checked")],
            {"swFmAlpha": {"IFeatureManager": "IA", "IMotionStudy": "IB"}},
            {"swFmAlpha": ["IFeatureManager", "IMotionStudy"]},
            {"swFmAlpha": "IA"},
            lambda i: {"Alpha"},
        )
        self.assertEqual([x["kind"] for x in v], ["ambiguous-host"])

    def test_missing_interface_docs_is_a_gap_not_a_violation(self):
        """★ 官方点名了但**接口文档缺失** ⇒ 缺数据源，**不拦发布**（事实 46 同族）。"""
        gate = self._judge()
        v, gaps, _n, _nh = gate.judge_sites(
            [_site("swFmAlpha", "unmapped")],
            {"swFmAlpha": {"IMotionStudy": "IMissing"}},
            {"swFmAlpha": ["IMotionStudy"]},
            {},
            lambda i: set(),
        )
        self.assertEqual(v, [])
        self.assertEqual(len(gaps), 1)

    # ── spec 239：`unsupported-path`（官方**不支持**这条路径）────────
    def test_const_with_no_host_page_at_all_is_red(self):
        """★★ 常量**没有任何**官方宿主页收录 ⇒ 代码走了官方不支持的路径 ⇒ 红（不许静默放过）。

        ★ 夹具自带一个**被官方点名**的站点（`SW_FM_A`）⇒ 红的原因**只可能是** `unsupported-path`。
        """
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _BODY_TWO, fm_doc="## Parameters\n\n- swFmZeta (zzz)\n",
                               ms_doc=FIXTURE_MS_DOC)
            r = _run(tree)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[unsupported-path]", r.stdout)
        self.assertNotIn("[zero-checked]", r.stdout)
        self.assertIn("无宿主常量站点 1", r.stdout)

    def test_declared_official_alt_entry_makes_the_site_green(self):
        """★ 声明 `alt <官方成员名>` 且该成员**有官方页、且不带 `Obsolete`** ⇒ 绿。"""
        body = _BODY_TWO.replace(
            '        data = get_com_member(manager, "CreateDefinition", int(fm_type))\n',
            "        #: create-entry: alt InsertMultiFaceDraft 官方取代入口\n"
            '        data = get_com_member(manager, "CreateDefinition", int(fm_type))\n')
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), body, fm_doc="## Parameters\n\n- swFmZeta (zzz)\n",
                               ms_doc=FIXTURE_MS_DOC)
            #: ★ 该成员页必须**存在**（自证①）
            (tree / "types" / "IFeatureManager" / "InsertMultiFaceDraft.md").write_text(
                "Inserts a multiface draft feature.\n", encoding="utf-8")
            r = _run(tree)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[PASS]", r.stdout)
        self.assertIn("无宿主常量站点 1", r.stdout)

    def test_alt_pointing_at_an_obsolete_entry_is_red(self):
        """★★ `alt` 指向一个带 `Obsolete` 标注的成员 ⇒ 红（★ 换回已废弃的前代入口 = 没解决）。"""
        gate = self._judge()
        bad = gate.judge_unsupported(
            ["#: create-entry: alt InsertMfDraft2 前代入口"],
            "swFmDraft", lambda n: True, lambda n: True)
        self.assertIsNotNone(bad)
        self.assertIn("Obsolete", bad)

    def test_alt_pointing_at_a_member_without_an_official_page_is_red(self):
        """★ `alt` 指向一个官方文档树里**没有页**的成员 ⇒ 红（不许写一个官方没有的入口）。"""
        gate = self._judge()
        bad = gate.judge_unsupported(
            ["#: create-entry: alt NoSuchEntry 编的"],
            "swFmDraft", lambda n: False, lambda n: False)
        self.assertIsNotNone(bad)
        self.assertIn("查不到", bad)

    def test_alt_unknown_is_a_bounded_escape_hatch(self):
        """★ `alt unknown <理由>` 是**有界逃生门**：写了理由 ⇒ 过；只写 `unknown` ⇒ 红。"""
        gate = self._judge()
        self.assertIsNone(gate.judge_unsupported(
            ["#: create-entry: alt unknown 官方替代入口尚未查明"],
            "swFmDraft", lambda n: False, lambda n: False))
        self.assertIsNotNone(gate.judge_unsupported(
            ["#: create-entry: alt unknown"],
            "swFmDraft", lambda n: False, lambda n: False))
        self.assertIsNotNone(gate.judge_unsupported(
            [], "swFmDraft", lambda n: False, lambda n: False))

    def test_unsupported_site_counts_toward_no_host_and_calls_the_judge(self):
        """★ 接线：`unmapped` 且无宿主 ⇒ `no_host` 计数 +1，且**调用注入的判官**（不静默放过）。"""
        gate = self._judge()
        v, _gaps, _n, no_host = gate.judge_sites(
            [_site("swFmDraft", "unmapped")], {}, {}, {}, lambda i: set(),
            lambda s: "★注入的判词")
        self.assertEqual(no_host, 1)
        self.assertEqual([x["kind"] for x in v], ["unsupported-path"])
        self.assertEqual(v[0]["detail"], "★注入的判词")

    # ── 下界冻结 / 便携 / 源隔离 ────────────────────────────────────
    def test_baseline_shrunk_is_red(self):
        r = _run(baseline="99,99,99")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[baseline-shrunk]", r.stdout)

    def test_skipped_when_official_docs_absent(self):
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _BODY, types=False)
            r = _run(tree, types=False)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("[SKIP]", r.stdout)

    def test_synthetic_tree_does_not_read_real_sources(self):
        """★ 源隔离：合成树的读数必须**与真树不同**（证明没读真树）。"""
        with tempfile.TemporaryDirectory() as d:
            tree = _write_tree(Path(d), _BODY, fm_doc="## Parameters\n\n- swFmBeta (beta)\n",
                               ms_doc=FIXTURE_MS_DOC)
            r = _run(tree)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("站点 1", r.stdout)
        self.assertNotIn("站点 8", r.stdout)


if __name__ == "__main__":
    unittest.main()
