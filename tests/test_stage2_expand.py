"""★ 阶段 2 契约测试：子方法展开 + 共享基准（规格 317 的 D1/D2）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage2_expand.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D1/D2 契约测试
# 官方依据: ① 方法真源 `scripts/engineering/compiler.METHOD_LIBRARY`
#           ② 本仓**事实 53**（启发式 ≥3 次修补即回退 ⇒ 展开只用确定性规则）
#           ③ 阶段 1 给 `hole_group` 的拒绝码 `sub-method-not-expanded`
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

from scripts.engineering import expand as E                            # noqa: E402
from scripts.engineering import registry as R                          # noqa: E402


@pytest.fixture(scope="module")
def reg():
    return R.build_registry()


def _bracket_plan() -> R.ExecutablePlan:
    """★ 含子方法 `hole_group` 的计划（★ 复刻 `mounting_bracket`）。"""
    return R.ExecutablePlan(method_id="mounting_bracket", steps=(
        R.PlanStep(step="sketch_start", params={"plane_name": "Front Plane"}),
        R.PlanStep(step="sketch_add_rectangle",
                   params={"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 80.0, "y2_mm": 50.0}),
        R.PlanStep(step="sketch_end", params={}),
        R.PlanStep(step="extrude_boss",
                   params={"sketch_name": "草图1", "depth_mm": 10.0}),
        R.PlanStep(step="hole_group",
                   params={"hole_diameter_mm": 6.0, "count": 4},
                   derive="★ 4 个 φ6 孔（hole_diameter_mm / count）"),
    ))


#: ══ D1 子方法展开 ═══════════════════════════════════════════════════

def test_expand_replaces_sub_method(reg) -> None:
    """★ FR-001：方法 id 形式的步骤被展开成工具序列。"""
    ex = E.expand_plan(_bracket_plan(), reg)
    names = [s.step for s in ex.steps]
    assert "hole_group" not in names, "★ 展开后不该有方法 id"
    for want in ("sketch_add_circle", "extrude_cut", "circular_pattern"):
        assert want in names, "★ 缺展开产物：%s" % want


def test_expand_recursively_resolvable(reg) -> None:
    """★ FR-002 / J1：展开后**递归可解析**（0 个方法 id 残留）。"""
    from scripts.engineering.compiler import METHOD_LIBRARY
    ex = E.expand_plan(_bracket_plan(), reg)
    left = [s.step for s in ex.steps if s.step in METHOD_LIBRARY]
    assert left == [], "★ 残留方法 id：%s" % left
    #: ★ 每个都解析到规范工具名
    for s in ex.steps:
        assert s.tool.startswith("solidworks_"), s


def test_expand_inherits_params(reg) -> None:
    """★ FR-003 / J3：子步骤**继承父步骤的参数**（★ 不丢）。"""
    ex = E.expand_plan(_bracket_plan(), reg)
    sub = [s for s in ex.steps if s.step in ("sketch_add_circle", "extrude_cut",
                                             "circular_pattern")]
    assert sub, "★ 没展开出子步骤"
    for s in sub:
        assert "hole_diameter_mm" in s.params, "★ %s 没继承 hole_diameter_mm" % s.step
        assert "count" in s.params, "★ %s 没继承 count" % s.step


def test_expand_trace_records(reg) -> None:
    """★ J4：`expand_trace` 记录每一步替换（★ 可审计）。"""
    ex = E.expand_plan(_bracket_plan(), reg)
    assert ex.expand_trace, "★ 展开轨迹为空"
    t = ex.expand_trace[0]
    assert t["expanded"] == "hole_group"
    assert "sketch_add_circle" in t["into"]


def test_expand_depth_limited(reg) -> None:
    """★ FR-004 / J2：展开深度有上限（★ 防循环）。"""
    with pytest.raises(E.ExpandError) as ei:
        E.expand_plan(_bracket_plan(), reg, max_depth=0)
    assert ei.value.code == "depth-exceeded"


def test_expand_no_sub_method_is_noop(reg) -> None:
    """★ 纯工具计划 ⇒ 展开是**恒等**（★ 不改动）。"""
    plan = R.ExecutablePlan(method_id="plate", steps=(
        R.PlanStep(step="sketch_start", params={"plane_name": "Front Plane"}),
        R.PlanStep(step="sketch_end", params={}),
    ))
    ex = E.expand_plan(plan, reg)
    assert [s.step for s in ex.steps] == ["sketch_start", "sketch_end"]


#: ══ D2 共享基准 ═════════════════════════════════════════════════════

def test_datum_index_finds_referrers() -> None:
    """★ J5：基准名 → 引用它的步骤下标。"""
    steps = (
        R.PlanStep(step="sketch_start", params={}, datums=("板主平面",)),
        R.PlanStep(step="sketch_end", params={}),
        R.PlanStep(step="hole_wizard", params={}, datums=("板主平面",)),
    )
    idx = E.datum_index(steps)
    assert idx["板主平面"] == [0, 2], idx


def test_rename_datum_updates_all_referrers() -> None:
    """★★ J5：**改基准名 ⇒ 所有引用它的步骤都改**（★ 一处不漏）。"""
    steps = (
        R.PlanStep(step="sketch_start", params={}, datums=("旧名",)),
        R.PlanStep(step="sketch_end", params={}, datums=("别的",)),
        R.PlanStep(step="hole_wizard", params={}, datums=("旧名",)),
    )
    new = E.rename_datum(steps, "旧名", "新名")
    got = [s.datums for s in new]
    assert got[0] == ("新名",), got
    assert got[1] == ("别的",), got
    assert got[2] == ("新名",), got
    #: ★ 改名后**没有残留**
    assert "旧名" not in E.datum_index(new)
