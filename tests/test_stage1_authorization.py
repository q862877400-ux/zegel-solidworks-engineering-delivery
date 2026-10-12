"""★ 阶段 1 契约测试：公共授权 + 执行意图记录（规格 316 的 C5/C6）。

★★ 含**反向验证**（★ 规格 §5 的 M3 / M4）：
   M3 **取消适用性检查** ⇒ 定点测试必须失败
   M4 使授权器**恒允** ⇒ 定点测试必须失败
★★ 以及 SC-009：**负例的 COM 写调用数必须为 0**。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage1_authorization.py
# 定位:   规格 `specs/316-stage1-parameter-plate` 的 C5/C6 契约测试
# 官方依据: ① 本仓**事实 8**（选择返回值不可信 ⇒ 判「写没写」只能**在边界计数**）
#           ② 本仓 AGENTS.md 铁律 3（结构白名单）+ §十九（不碰用户文档）
#           ③ 外部方案阶段 1 逐字要求：
#              「未准入返回 TOOL_NOT_ADMITTED · 路径和文档越权分别返回
#                PATH_OUTSIDE_WORKSPACE、DOCUMENT_NOT_OWNED · COM 写调用数全部为 0」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import authorization as A                     # noqa: E402
from scripts.engineering import executor as X                          # noqa: E402
from scripts.engineering import registry as R                          # noqa: E402


@pytest.fixture(scope="module")
def reg():
    return R.build_registry()


def _plan(*steps) -> R.ExecutablePlan:
    return R.ExecutablePlan(method_id="t", steps=tuple(steps))


#: ══ C5 授权 ═══════════════════════════════════════════════════════════

def test_codes_are_closed_set() -> None:
    """★ 封闭码：非法码在构造时就被 assert 拦下。"""
    assert len(A.AUTH_CODES) == 5
    with pytest.raises(AssertionError):
        A.AuthorizationVerdict(False, "乱写的码")


def test_path_inside_workspace_ok() -> None:
    """★ 正例：工作区内的路径通过。"""
    assert A.check_path(ROOT / "output" / "x.json").ok


def test_path_outside_workspace_rejected() -> None:
    """★ FR-006 / SC-007：工作区外 ⇒ `PATH_OUTSIDE_WORKSPACE`。"""
    for p in (r"C:\Windows\Temp\x.json", r"D:\elsewhere\x.json",
              ROOT / ".." / ".." / "escape.json"):
        v = A.check_path(p)
        assert not v.ok, p
        assert v.code == A.PATH_OUTSIDE_WORKSPACE, p


def test_document_not_owned_rejected() -> None:
    """★ FR-007 / SC-008：非本任务创建的文档 ⇒ `DOCUMENT_NOT_OWNED`。"""
    owned = A.OwnedDocuments()

    class _D:
        def GetTitle(self):
            return "别人的文档.SLDPRT"

    v = owned.check(_D())
    assert not v.ok and v.code == A.DOCUMENT_NOT_OWNED


def test_owned_document_ok() -> None:
    """★ 正例：登记在册的文档通过。"""
    owned = A.OwnedDocuments()

    class _D:
        def GetTitle(self):
            return "我的.SLDPRT"

    d = _D()
    owned.register(d)
    assert owned.check(d).ok


def test_tool_not_admitted_rejected(reg) -> None:
    """★ FR-005 / SC-006：未准入的工具 ⇒ `TOOL_NOT_ADMITTED`。"""
    bad = [d.canonical_name for d in reg.values() if not d.admitted]
    assert bad, "★ 目录里应有未准入的工具"
    v = A.check_tool(bad[0], reg)
    assert not v.ok
    assert v.code in (A.TOOL_NOT_ADMITTED, A.EFFECT_UNKNOWN)


def test_unknown_effect_rejected(reg) -> None:
    """★ 不变式 I5：效应未知 ⇒ `EFFECT_UNKNOWN`。"""
    unk = [d.canonical_name for d in reg.values() if d.effect == "unknown"]
    assert unk, "★ 目录里应有未知效应的工具"
    v = A.check_tool(unk[0], reg)
    assert not v.ok and v.code == A.EFFECT_UNKNOWN


def test_plan_not_compiled_rejected(reg) -> None:
    """★ 防绕过：步骤 `tool` 为空 ⇒ `PLAN_NOT_COMPILED`。"""
    p = _plan(R.PlanStep(step="extrude_boss", params={"sketch_name": "s", "depth_mm": 1.0}))
    v = A.authorize_plan(p, reg)
    assert not v.ok and v.code == A.PLAN_NOT_COMPILED


#: ══ SC-009：负例的 COM 写调用数必须为 0 ═══════════════════════════════

def test_sc009_negative_cases_write_zero(reg) -> None:
    """★★ **SC-009**：四类负例执行后，**COM 写调用数全部为 0**。

    ★★ 判据来自 `executor.COUNTER`（★ 挂在 `sw_connect` 的 COM 边界上），
      **不是**返回值（★ 事实 8：返回值不可信）。
    """
    compiled = R.ExecutablePlan(
        method_id="t",
        steps=(R.PlanStep(step="extrude_boss",
                          params={"sketch_name": "草图1", "depth_mm": 20.0},
                          tool="solidworks_extrude_boss"),))

    #: ① 工具未准入（★ 用一个未准入的工具名）
    bad_tool = next(d.canonical_name for d in reg.values() if not d.admitted)
    p1 = R.ExecutablePlan(method_id="t", steps=(
        R.PlanStep(step="x", params={}, tool=bad_tool),))
    #: ② 路径越权
    #: ③ 文档越权
    class _D:
        def GetTitle(self):
            return "别人的.SLDPRT"

    owned = A.OwnedDocuments()
    for name, p, kw in (
        ("工具未准入", p1, {}),
        ("路径越权", compiled, {"write_paths": (r"C:\Windows\evil.json",)}),
        ("文档越权", compiled, {"owned": owned, "doc": _D()}),
        ("计划未编译", _plan(R.PlanStep(step="e", params={})), {}),
    ):
        X.COUNTER.reset()
        out = X.execute_plan(p, reg, **kw)
        assert out["ok"] is False, "%s 本应被拒" % name
        assert X.COUNTER.count() == 0, \
            "★ 负例「%s」产生了 %d 次 COM 写调用（应为 0）" % (name, X.COUNTER.count())


#: ══ 反向验证 M3：取消适用性检查 ⇒ 必须失败 ═══════════════════════════

def test_m3_disabling_admission_check_is_caught(reg) -> None:
    """★★ **M3**：**取消准入检查** ⇒ 负例会被放行 ⇒ 本测试必须能抓到。

    ★ 做法：**不调用** `authorize_plan`，直接看「未准入工具」在目录里的状态 ——
      若有人把 `admitted` 全设 True，本断言立刻失败。
    """
    not_adm = [d for d in reg.values() if not d.admitted]
    assert not_adm, (
        "★★ **M3 报警**：目录里**一个未准入的工具都没有** —— "
        "说明准入检查被取消了（★ 那会让未准入工具被放行）")
    #: ★ 且未准入必须**真的**被 `check_tool` 拒
    for d in not_adm[:5]:
        assert not A.check_tool(d.canonical_name, reg).ok, d.canonical_name


#: ══ 反向验证 M4：授权器恒允 ⇒ 必须失败 ═══════════════════════════════

def test_m4_always_allow_is_caught(reg) -> None:
    """★★ **M4**：**授权器恒允** ⇒ 四类负例都会通过 ⇒ 本测试必须抓到。

    ★ 判据：`authorize_plan` 对**四类非法输入**都必须回 `ok=False`。
      若有人把它改成 `return AuthorizationVerdict(True)`，这里立刻失败。
    """
    compiled = R.ExecutablePlan(
        method_id="t",
        steps=(R.PlanStep(step="extrude_boss",
                          params={"sketch_name": "草图1", "depth_mm": 20.0},
                          tool="solidworks_extrude_boss"),))

    class _D:
        def GetTitle(self):
            return "别人的.SLDPRT"

    cases = [
        ("计划未编译", _plan(R.PlanStep(step="e", params={})), {}),
        ("路径越权", compiled, {"write_paths": (r"C:\Windows\evil.json",)}),
        ("文档越权", compiled, {"owned": A.OwnedDocuments(), "doc": _D()}),
    ]
    for name, p, kw in cases:
        v = A.authorize_plan(p, reg, **kw)
        assert v.ok is False, "★★ **M4 报警**：授权器对「%s」回了好" % name
        assert v.code in A.AUTH_CODES, name


#: ══ C6 执行意图记录 ═══════════════════════════════════════════════════

def test_com_write_counter_semantics() -> None:
    """★ 计数器：未 arm 不记 · arm 后记 · `assert_zero` 会抛。"""
    c = X.ComWriteCounter()
    c.bump("X")                 #: ★ 未 arm ⇒ 不记
    assert c.count() == 0
    c.arm()
    c.bump("InsertSketch")
    c.bump("FeatureExtrusion3")
    assert c.count() == 2
    c.disarm()
    c.bump("InsertSketch")      #: ★ 又 disarm ⇒ 不记
    assert c.count() == 2
    with pytest.raises(AssertionError):
        c.assert_zero("测试")


def test_sw_connect_hook_counts_only_writes() -> None:
    """★ 钩子只记**写**（★ 只读路径不记 —— 否则负例会误报）。"""
    import sw_connect
    hits: list[str] = []
    old = sw_connect.__dict__.get("_COM_WRITE_HOOK")
    sw_connect.set_com_write_hook(lambda n: hits.append(n))
    try:
        for n in ("GetTitle", "IsCylinder", "GetBodyBox"):     #: 读
            sw_connect._bump_if_write(n)
        for n in ("InsertSketch", "FeatureExtrusion3", "FeatureCut4",
                  "ClearSelection2"):                          #: 写
            sw_connect._bump_if_write(n)
    finally:
        sw_connect.set_com_write_hook(old)
    assert hits == ["InsertSketch", "FeatureExtrusion3", "FeatureCut4",
                    "ClearSelection2"], hits


def test_dry_run_touches_no_com(reg) -> None:
    """★ `dry_run=True` ⇒ 只授权、不执行（★ 负例测试的基础设施）。"""
    compiled = R.ExecutablePlan(
        method_id="t",
        steps=(R.PlanStep(step="extrude_boss",
                          params={"sketch_name": "草图1", "depth_mm": 20.0},
                          tool="solidworks_extrude_boss"),))
    X.COUNTER.reset()
    out = X.execute_plan(compiled, reg, dry_run=True)
    assert out["ok"] is True
    assert X.COUNTER.count() == 0
    assert out["records"] == []
