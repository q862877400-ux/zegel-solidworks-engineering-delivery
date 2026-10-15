"""★ EC06 T06/T07 判据 —— 两个受控案例 / BOM 可追溯 / 替换件稳定性。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/assembly.py`（★ `CASE_LIBRARY` · `bom_traceability` · `replacement_stability`）
#         `specs/308-ec06-assembly-and-mechanism/spec.md`（★ EC06-T06/T07）
# 定位:   ★ EC06 **T06**（★ 双导杆滑台 / 轴承支撑轴系）与 **T07**（★ BOM / 替换件稳定性）。
# 官方依据: 不适用（本仓的装配分析层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from engineering import assembly as A


# ══════════════════════════════════════════════════════════════════════
# T06 · 两个受控案例
# ══════════════════════════════════════════════════════════════════════

def test_t06_two_controlled_cases_exist():
    """★★★ T06：★ **双导杆滑台 / 轴承支撑轴系两类案例必须齐**（★ 逐字承 EC06-T06）。"""
    assert set(A.CASE_LIBRARY) == {"double_rod_slide", "bearing_supported_shaft"}, (
        "★ 案例不齐：%r" % sorted(A.CASE_LIBRARY))


@pytest.mark.parametrize("case_id,target", [("double_rod_slide", 1),
                                            ("bearing_supported_shaft", 1)])
def test_t06_case_dof_matches_its_target(case_id, target):
    """★★★★ T06：★ **案例的目标自由度与实际一致**（★ 逐字承验收）。"""
    g = A.build_case(case_id)
    out = g.target_matches_actual()
    assert out["ok"] is True, (
        "★★ 案例 `%s` 的目标 %r ≠ 实际 %r ⇒ ★ 冻结参数自相矛盾"
        % (case_id, out["target"], out["actual"]))
    assert out["actual"] == target, "★ 自由度不是 %d：%d" % (target, out["actual"])


@pytest.mark.parametrize("case_id", ["double_rod_slide", "bearing_supported_shaft"])
def test_t06_cases_are_expected_motion_not_under_constrained(case_id):
    """★★★★ T06：★ **两个案例都是「预期运动」**（★ 不是欠约束）。

    ★★ 依据（★ EC06-T06/T02）：★ 滑台**本就该能滑**、★ 轴**本就该能转**
      ⇒ ★★ **那是有意保留的自由度** ✓
    """
    g = A.build_case(case_id)
    out = g.verdict()
    assert out["verdict"] == A.DofVerdict.EXPECTED_MOTION, (
        "★★ 案例 `%s` 被判 %r ⇒ ★ 把「功能要求的运动」当成了「没锁住」"
        % (case_id, out["verdict"]))
    assert out["releasing"] is True


@pytest.mark.parametrize("case_id", ["double_rod_slide", "bearing_supported_shaft"])
def test_t06_cases_have_no_axis_errors(case_id):
    """★★ T06：★ 两个案例**不该有错轴向**（★ 它们是**正确**装配的样板）。"""
    g = A.build_case(case_id)
    assert g.axis_errors() == [], "★★ 样板案例自己就有轴向冲突：%r" % g.axis_errors()


def test_t06_unknown_case_is_rejected():
    """★★ T06：★ **未知案例 ⇒ 拒绝**（★ 不硬套一个）。"""
    with pytest.raises(KeyError):
        A.build_case("no_such_case")


def test_t06_every_case_states_why():
    """★★ T06：★ 每个案例必须写**为什么这样设计**（★ 可复核）。"""
    for cid, c in A.CASE_LIBRARY.items():
        assert c["why"], "★ 案例 `%s` 没写 why" % cid
        assert c["expected_motions"], "★ 案例 `%s` 没写预期运动" % cid


def test_t06_gear_is_explicitly_not_in_the_cases():
    """★★ T06：★ **齿轮不在两类案例里**（★ 逐字承 EC06-T06：★「★ **齿轮列为附加挑战**」）。"""
    assert "gear" not in A.CASE_LIBRARY, (
        "★★ 齿轮被当成了**基本**案例 ⇒ ★ 违反「齿轮列为附加挑战」")
    assert not any("gear" in cid for cid in A.CASE_LIBRARY)


# ══════════════════════════════════════════════════════════════════════
# T07 · BOM 可追溯
# ══════════════════════════════════════════════════════════════════════

def test_t07_bom_requires_traceable_fields():
    """★★★ T07：★ **BOM 每行必须带可指认字段**（★ 否则是一张纸）。"""
    good = [{"name": "base", "quantity": 1, "file_path": "output/base.SLDPRT"}]
    assert A.bom_traceability(good)["ok"] is True
    #: ★★ 缺字段 ⇒ 失败（★ **且点名缺哪个**）
    bad = A.bom_traceability([{"name": "base", "quantity": 1}])
    assert bad["ok"] is False
    assert bad["bad_rows"][0]["missing"] == ["file_path"]


def test_t07_empty_bom_is_not_a_pass():
    """★★★ T07：★ **空 BOM ⇒ 不算通过**（★ 不能「没有 BOM」也算 ok）。"""
    out = A.bom_traceability([])
    assert out["ok"] is False, "★★ 空 BOM 被判通过"
    assert "空 BOM" in out["reason"]


def test_t07_assembly_tools_are_the_existing_ones():
    """★★★ T07：★ **BOM/替换件用的是工具面已有的工具**（★ 铁律 1 —— ★ 不另建）。"""
    for key in ("bom_read", "bom_export", "replace_component", "component_list"):
        assert key in A.ASSEMBLY_TOOLS, "★ 缺 `%s`" % key
        assert A.ASSEMBLY_TOOLS[key].startswith("solidworks_"), (
            "★★ `%s` 不是工具面的名字：%r" % (key, A.ASSEMBLY_TOOLS[key]))


# ══════════════════════════════════════════════════════════════════════
# T07 · 替换件稳定性
# ══════════════════════════════════════════════════════════════════════

def test_t07_replacement_is_stable_when_nothing_changes():
    """★★★ T07：★ **替换后配合稳定 ⇒ ok**（★ 逐字承 EC06-T07）。"""
    before = {"mate_count": 4, "total_dof": 1, "verdict": "expected_motion"}
    after = dict(before)
    out = A.replacement_stability(before, after)
    assert out["ok"] is True, "★ 什么都没变却判不稳定：%r" % out


def test_t07_replacement_instability_is_detected():
    """★★★★ T07：★ **替换后配合数/自由度变了 ⇒ 报出来**（★ 且**具名**）。"""
    before = {"mate_count": 4, "total_dof": 1, "verdict": "expected_motion"}
    after = {"mate_count": 2, "total_dof": 3, "verdict": "under_constrained"}
    out = A.replacement_stability(before, after)
    assert out["ok"] is False, "★★ 换件换坏了却判稳定"
    assert set(out["diffs"]) == {"mate_count", "total_dof", "verdict"}, (
        "★ 没把变了的都列出来：%r" % sorted(out["diffs"]))
    #: ★★ 且**逐条给前后值**
    assert out["diffs"]["total_dof"] == {"before": 1, "after": 3}
