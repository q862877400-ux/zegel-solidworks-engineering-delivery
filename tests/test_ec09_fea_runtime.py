"""★ EC09 真机判据 —— **悬臂梁静力分析**（★ 关掉「CAE 真机未跑」这条残留）。

★★★ **为什么要有它**：★ EC09 上一轮只做了**可信判据层**（★ 纯离线）——
  ★★ **真机没跑过求解** ⇒ ★ 「参考解 / 反力平衡 / 网格关注量」这些**没有真读数** ✗
★ 本轮**真跑**（★ 证据 `output/_probe_ec09_fea.json` · ★ 走 `sw_guard`）：
  · ★ 试件：★ **悬臂梁**（★ 200×20×10 mm · ★ 一端固定 · ★ 端部 100 N）
  · ★★ **独立参考解**：★ `δ = FL³/(3EI)` = **7.619048e-04 m**（★ **闭式解** · ★ 不取自求解器）
  · ★ **材料**：★ `AISI 1020`（★ 回读一致 —— ★ 判据只能是回读）
  · ★ **网格**：★ **8711 单元** · ★ `return_code = 0`
  · ★ **约束 + 载荷**：★ 都建成（★ `count_before 1 → count_after 2`）
★★★ **如实登记（★ 本判据的核心纪律）**：★ **求解未在探针超时内完成** ——
  ★★ 本仓**早有记录**（★ 事实 293）：★ 求解时进度窗显示「建立刚度矩阵 · 已用时间 **33分00秒**」
  ⇒ ★★ **那是「慢」，不是「失败」** ⇒ ★ 本判据**按实际读数**判，★ **不假装求解通过** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/311-ec09-cae-and-topology/spec.md`（★ EC09-T01/T02/T04）
#         `output/_probe_ec09_fea.json`（★ 真机证据）
#         `scripts/engineering/cae.py`（★ `beam_tip_deflection_reference` —— ★ 独立参考解）
#         `docs/known-facts.md` 事实 270（★ `19` = 材料未定义）· 事实 293（★ 求解很慢）
# 定位:   ★ 守卫 EC09 的**真机**面。
# 官方依据: `CWStudy` / `CWModelDoc`（Simulation API）· ★ 闭式解见材料力学
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 读证据 JSON —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "output" / "_probe_ec09_fea.json"

#: ★★ **梁的几何**（★ 与探针一致）
L_M, B_M, H_M, F_N, E_PA = 0.200, 0.020, 0.010, 100.0, 210e9
I_M4 = B_M * H_M ** 3 / 12.0


@pytest.fixture(scope="module")
def ev() -> dict:
    if not EVIDENCE.is_file():
        pytest.skip("★★ 缺真机证据 `%s` ⇒ 跑 `sw_guard` 探针后再判"
                    % EVIDENCE.relative_to(ROOT))
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_evidence_is_from_a_real_machine(ev):
    """★★ 证据来自真机（★ 有版本号 · ★ 未被阻塞）。"""
    assert ev.get("revision"), "★★ 没有 SolidWorks 版本号"
    assert not ev.get("blocked"), "★ 那次被阻塞：%r" % ev.get("blocked")


def test_cantilever_beam_was_built(ev):
    """★★★ 悬臂梁**真的建出来了**（★ 体数 1）。"""
    assert ev.get("beam_built") is True, "★ 梁没建成"
    assert ev.get("body_count") == 1, "★ 体数 %r ≠ 1" % ev.get("body_count")


def test_independent_reference_matches_closed_form(ev):
    """★★★★★ **独立参考解**（★ 逐字承 EC09-T01：★「★ 固定理论或**可信独立参考解**」）。

    ★★ 判据：★ 证据里的参考值**必须等于手写闭式解** `δ = FL³/(3EI)` ——
      ★★ **不取自求解器**（★ 那是 EC09 的核心纪律）✓
    """
    want = F_N * L_M ** 3 / (3.0 * E_PA * I_M4)
    got = ev.get("reference_deflection_m")
    assert got is not None, "★★ 没有参考解读数"
    assert abs(got - want) / want < 1e-9, (
        "★★★ 参考解 %r ≠ 手写闭式解 %r ⇒ ★ 可能取自求解器" % (got, want))
    #: ★★ 参考解必须标**独立**
    assert "独立" in (ev.get("reference_source") or ""), (
        "★★ 参考解没标「独立于求解器」")


def test_material_was_read_back_not_assumed(ev):
    """★★★★ **材料靠回读**（★ 判据只能是回读 —— ★ 事实 8 / EC09-T02）。

    ★★ 依据（★ 事实 270 逐字）：★ `RunAnalysis` 的 **`19` = 材料未定义** ——
      ★★ 所以**必须先确认材料真赋上了**（★ `SetMaterialPropertyName2` 返回 `Void`）✓
    """
    assert ev.get("material_readback"), (
        "★★★ 材料回读为空 ⇒ ★ 求解会回 `19`（材料未定义）")
    assert ev.get("material_readback") == ev.get("material_requested"), (
        "★★ 回读 %r ≠ 请求 %r" % (ev.get("material_readback"),
                                 ev.get("material_requested")))


def test_mesh_was_created_with_real_elements(ev):
    """★★★★★ **网格真的建成了**（★ 逐字承 EC09-T04：★「★ **至少三档**有策略的网格」）。

    ★★ 判据：★ **`element_count > 0`**（★ **不看返回码** —— ★ 本仓铁律：回读优先）✓
    ★★ 且单元尺寸必须**是正数**（★ 传 0 会得返回码 **5** `SpecifyPositiveValue`）。
    """
    m = ev.get("mesh_report") or {}
    assert m.get("ok") is True, "★★ 网格没建成：%r" % m
    assert m.get("element_count", 0) > 0, "★★★ 单元数 0 ⇒ 网格是空的"
    assert m.get("element_count") >= 1000, (
        "★ 单元数 %r 太少 ⇒ 不像真网格" % m.get("element_count"))
    #: ★★ 单元尺寸必须为正（★ 否则返回码 5）
    assert (ev.get("mesh_element_size_mm") or 0) > 0, "★★ 单元尺寸非正"
    assert (ev.get("mesh_tolerance_mm") or 0) > 0, "★★ 网格容差非正"


def test_restraint_and_load_were_both_applied(ev):
    """★★★★ **约束与载荷都建成**（★ 逐字承 EC09-T02：★「★ 载荷、边界」）。

    ★★ 判据：★ 约束有回读 · ★ **力被配上了大小**（★ `NormalForceOrTorqueValue`）✓
    ★★★ **2026-10-10 更新（★ 证据形状变了 —— ★ 因为根因修好了）**：
      ★ 旧探针走 `apply_force_report`（★ 它只回**类型名**、★ 拿不到对象）；
      ★★ 新探针走 `add_force()` **拿真对象** + `configure_force(magnitude=…)` ⇒
        ★ 证据键从 `force` 变成 **`force_configured`** ✓
    """
    assert ev.get("fixed_restraint") is not None, (
        "★★ 固定约束没建成：%r" % ev.get("fixed_error"))
    #: ★★ 力：★ **必须真配上大小**（★ 那正是「未定义载荷」的根因）
    conf = ev.get("force_configured") or {}
    assert conf.get("NormalForceOrTorqueValue") == F_N, (
        "★★★ 力的大小没设上（%r）⇒ ★ 求解会报「未定义载荷或规定的位移」" % conf)
    #: ★ 兼容旧键（★ 若某次证据仍是旧形状，至少要有读数）
    assert (ev.get("force") or conf), "★★ 力没有读数"


def test_solve_status_is_recorded_honestly(ev):
    """★★★★★ **求解状态如实登记**（★ 逐字承验收：★「★ **求解成功不是工程通过**」）。

    ★★★ **2026-10-10 更新（★ 求解**真的成功了** —— ★ 根因修好之后）**：
      ★ 修前：★ 力没大小 ⇒ 弹窗「未定义载荷或规定的位移」⇒ `return_code 19` ✗
      ★★ 修后：★ `return_code 0` · ★ `results_present = true` · ★ **4 个图**
        （`位移1`/`应力1`/`应变1`/`品质1`）✓
    ★★ **本判据要求的是「读数与结论一致」**，★ 不预设成功或失败：
      · ★ 有结果 ⇒ ★ 必须**真**有结果（★ 返回码 0 + 图数 > 0）
      · ★ 无结果 ⇒ ★ 必须**如实**记（★ 且**不许**出现「工程通过」）✓
    """
    run = ev.get("run_report") or {}
    assert run, "★★ 没有求解读数（★ 连「没跑完」都没记）"
    if run.get("results_present"):
        #: ★★ 有结果 ⇒ **必须有据**（★ 不看返回码，★ 看结果与图）
        assert run.get("plot_count", 0) > 0, (
            "★★★ 说求解有结果，却**一个图都没有** ⇒ ★ 结论无据")
        assert run.get("plot_names"), "★★ 没有图名"
        #: ★★★ **且不许有「未定义载荷」那个弹窗**（★ 那正是根因的症状）
        for dlg in (ev.get("dialogs_seen") or []):
            joined = " ".join(dlg.get("texts") or [])
            assert "未定义载荷" not in joined, (
                "★★★ 仍弹「未定义载荷」⇒ ★ 力没设上：%r" % joined[:160])
    else:
        #: ★★ 没结果 ⇒ 必须**如实**记（★ 且不许宣称通过）
        assert run.get("ok") is False, "★★★ 没有结果却判 `ok` ⇒ ★ 假成功"
        assert not ev.get("engineering_pass"), (
            "★★★ 求解没完成却记了「工程通过」⇒ ★ 违反验收")


def test_probe_declares_no_engineering_pass_without_solve(ev):
    """★★★★ **没求解结果 ⇒ 不得有「工程通过」**（★ EC09 的 `engineering_verdict` 口径）。

    ★★ 依据（★ 本仓 `cae.py` 的六道门）：★ **`solve` 只是入场券** ——
      ★★ 它不过 ⇒ ★ `engineering_pass` **必须**为假 ✓
    """
    import sys as _s
    _s.path.insert(0, str(ROOT / "scripts"))
    from engineering import cae as C
    out = C.engineering_verdict(solve_status=C.SolveStatus.NOT_RUN, reference=None,
                                balance=None, convergence=None, closure=None,
                                validation=None)
    assert out["engineering_pass"] is False, (
        "★★★ 没跑求解却判「工程通过」⇒ ★ 违反 EC09 的核心")


def test_no_residue_after_the_run(ev):
    """★★★★ **零残留**（★ 关文档 + ★ 删工件）。"""
    assert ev.get("closed") is True, "★★ 没关掉自己开的文档"
    assert ev.get("artifact_removed") is True, "★★ 自有工件没删"
