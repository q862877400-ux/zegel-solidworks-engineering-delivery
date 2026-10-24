"""★ E1–E7 的三态样件：好输入 / 已知坏输入 / 缺证据。

## 为什么样件要单独一个模块

`docs/ENGINEERING-PATH.md` 第十节第 4 条：**每条新检查器必须能拒绝一个真实坏样件**，
不能只新增「字段存在」的门禁。

把样件集中在这里，是为了让「判定器有效」这件事**可被独立检验**：
换一个判定器实现，同一批样件仍应给出同样的三态结果。

## 三态

| 样件 | 期望 |
|---|---|
| `good_*` | `pass` |
| `bad_*` | `fail`（且原因指向**具体**缺陷） |
| `unknown_*` | `unknown`（采集不完整，**不是** fail） |
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/samples.py
# 定位:   `specs/349-e1-e7-acceptance` 的 SC-001 —— E1–E7 的三态样件。
#          ★ `docs/ENGINEERING-PATH.md` 第十节第 4 条：每条新检查器必须能拒绝
#            一个真实坏样件，不能只新增「字段存在」的门禁。
#          样件集中在这里，是为了让「判定器有效」可被独立检验：换一个判定器实现，
#          同一批样件仍应给出同样的三态结果。
# 官方依据: 不适用（合成样件，不含真机读数）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

from .e1_sketch import collect_sketch_constraint
from .e2_e3_solid import collect_feature_tree, collect_rebuild
from .e4_assembly import collect_assembly
from .e5_e6_drawing import collect_drawing, collect_process
from .e7_provenance import collect_provenance
from .result import Observation

# ────────────────────────────── E1 ──────────────────────────────


def good_e1() -> Observation:
    """全约束、无重复、有驱动尺寸。

    ★ 数据自洽：4 实体 ⇒ 2×4 = 8 个自由度；需要 8 条约束才能到 0。
      这里给 6 条关系 + 2 条尺寸 = 8 ⇒ DOF = 8 − 8 = 0。
    """
    return collect_sketch_constraint(
        target="plate-100x60",
        entities=4,
        relations=("h1", "h2", "v1", "v2", "coincident1", "coincident2"),
        dimensions=("d_width", "d_height"),
        intentional_dof=0,
        solver_state="fully_defined",
    )


def bad_e1_duplicate_relation() -> Observation:
    """★★ R-04 的伪造手法：同一条关系重复 8 次。"""
    return collect_sketch_constraint(
        target="plate-100x60",
        entities=4,
        relations=tuple(["same_relation"] * 8),
        dimensions=(),
        intentional_dof=0,
        solver_state="fully_defined",
    )


def bad_e1_all_fixed_no_dimension() -> Observation:
    """全固定但没有驱动尺寸 ⇒ 不可参数化。"""
    return collect_sketch_constraint(
        target="plate-100x60",
        entities=1,
        relations=("fix_all",),
        dimensions=(),
        intentional_dof=0,
        solver_state="fully_defined",
    )


def unknown_e1() -> Observation:
    """采集不完整：没取到求解状态。"""
    return collect_sketch_constraint(
        target="plate-100x60",
        entities=4,
        relations=("h1",),
        dimensions=("d1",),
        solver_state="",
    )


# ────────────────────────────── E2 ──────────────────────────────


def good_e2() -> Observation:
    return collect_rebuild(
        target="plate-rev1",
        opened_existing=True,
        changed_params=("w",),
        downstream_linked=True,
        rebuild_errors=0,
        reopened_ok=True,
        drawing_is_current=True,
    )


def bad_e2_new_document() -> Observation:
    """★ R-10 的替代品：新建文档重跑冒充「改已交付件」。"""
    return collect_rebuild(
        target="plate-rev2-new",
        opened_existing=False,
        changed_params=("w",),
        downstream_linked=True,
        rebuild_errors=0,
        reopened_ok=True,
        drawing_is_current=True,
    )


def bad_e2_no_downstream() -> Observation:
    """改了主参数但孔没跟着动。"""
    return collect_rebuild(
        target="plate-rev1",
        opened_existing=True,
        changed_params=("w",),
        downstream_linked=False,
        rebuild_errors=0,
        reopened_ok=True,
        drawing_is_current=True,
    )


def unknown_e2() -> Observation:
    return collect_rebuild(
        target="plate-rev1",
        opened_existing=True,
        changed_params=(),
        downstream_linked=True,
        rebuild_errors=0,
        reopened_ok=True,
        drawing_is_current=True,
    )


# ────────────────────────────── E3 ──────────────────────────────


def good_e3() -> Observation:
    return collect_feature_tree(
        target="plate-rev1",
        feature_count=6,
        native_features=6,
        imported_solids=0,
        dangling_refs=0,
        errors=0,
        warnings=0,
        editable_prefix_verified=True,
    )


def bad_e3_imported_solid() -> Observation:
    """导入死实体冒充原生特征。"""
    return collect_feature_tree(
        target="plate-imported",
        feature_count=1,
        native_features=0,
        imported_solids=1,
        dangling_refs=0,
        errors=0,
        warnings=0,
        editable_prefix_verified=False,
    )


def bad_e3_dangling() -> Observation:
    return collect_feature_tree(
        target="plate-rev1",
        feature_count=6,
        native_features=6,
        imported_solids=0,
        dangling_refs=2,
        errors=0,
        warnings=0,
        editable_prefix_verified=True,
    )


def unknown_e3() -> Observation:
    return collect_feature_tree(
        target="empty-doc",
        feature_count=0,
        native_features=0,
        imported_solids=0,
        dangling_refs=0,
        errors=0,
        warnings=0,
        editable_prefix_verified=False,
    )


# ────────────────────────────── E4 ──────────────────────────────


def good_e4() -> Observation:
    return collect_assembly(
        target="asm-locate",
        components=("ground:base", "moving:pin"),
        mates=(
            {"kind": "coincident", "a": "moving:pin", "b": "ground:base"},
            {"kind": "concentric", "a": "moving:pin", "b": "ground:base"},
        ),
        target_dof=0,
        interference_count=0,
        min_clearance_mm=0.5,
        clearance_basis="图纸标注 0.5 mm 配合间隙",
        configuration="默认",
    )


def bad_e4_duplicate_mate() -> Observation:
    """★★ R-05 的伪造手法：同一对组件重复贴 6 次 coincident。"""
    return collect_assembly(
        target="asm-locate",
        components=("ground:base", "moving:pin"),
        mates=tuple(
            {"kind": "coincident", "a": "moving:pin", "b": "ground:base"}
            for _ in range(6)
        ),
        target_dof=0,
        interference_count=0,
        min_clearance_mm=0.5,
        clearance_basis="图纸标注",
        configuration="默认",
    )


def bad_e4_interference() -> Observation:
    return collect_assembly(
        target="asm-locate",
        components=("ground:base", "moving:pin"),
        mates=(
            {"kind": "coincident", "a": "moving:pin", "b": "ground:base"},
            {"kind": "concentric", "a": "moving:pin", "b": "ground:base"},
        ),
        target_dof=0,
        interference_count=1,
        min_clearance_mm=-0.2,
        clearance_basis="图纸标注",
        configuration="默认",
    )


def unknown_e4() -> Observation:
    return collect_assembly(
        target="asm-locate",
        components=(),
        mates=(),
        target_dof=0,
        interference_count=0,
        min_clearance_mm=0.0,
        clearance_basis="",
        configuration="",
    )


# ────────────────────────────── E5 ──────────────────────────────


def good_e5() -> Observation:
    return collect_drawing(
        target="plate-drawing-rev1",
        required_items=("孔位", "基准A", "未注公差"),
        bound_items=(
            {"name": "孔位", "evidence": "尺寸 10±0.1 @ 视图1", "value_ok": True},
            {"name": "基准A", "evidence": "基准符号 @ 底面", "value_ok": True},
            {"name": "未注公差", "evidence": "GB/T 1804-m", "value_ok": True},
        ),
        model_revision="rev1",
        drawing_revision="rev1",
        material_from_requirement=True,
        template_ok=True,
    )


def bad_e5_empty_evidence() -> Observation:
    """★★ R-06 的伪造手法：covered 但 evidence 为空串。"""
    return collect_drawing(
        target="plate-drawing-rev1",
        required_items=("孔位", "基准A"),
        bound_items=(
            {"name": "孔位", "evidence": "", "value_ok": True},
            {"name": "基准A", "evidence": "", "value_ok": True},
        ),
        model_revision="rev1",
        drawing_revision="rev1",
        material_from_requirement=True,
        template_ok=True,
    )


def bad_e5_missing_item() -> Observation:
    return collect_drawing(
        target="plate-drawing-rev1",
        required_items=("孔位", "基准A", "未注公差"),
        bound_items=(
            {"name": "孔位", "evidence": "尺寸 @ 视图1", "value_ok": True},
        ),
        model_revision="rev1",
        drawing_revision="rev1",
        material_from_requirement=True,
        template_ok=True,
    )


def bad_e5_stale_drawing() -> Observation:
    return collect_drawing(
        target="plate-drawing-rev1",
        required_items=("孔位",),
        bound_items=({"name": "孔位", "evidence": "尺寸", "value_ok": True},),
        model_revision="rev2",
        drawing_revision="rev1",
        material_from_requirement=True,
        template_ok=True,
    )


def unknown_e5() -> Observation:
    return collect_drawing(
        target="plate-drawing-rev1",
        required_items=(),
        bound_items=(),
        model_revision="",
        drawing_revision="",
        material_from_requirement=False,
        template_ok=False,
    )


# ────────────────────────────── E6 ──────────────────────────────


def good_e6() -> Observation:
    return collect_process(
        target="plate-rev1",
        route="machined",
        checks=(
            {"name": "刀具可达", "applicable": True, "passed": True, "value": "φ6 通孔"},
            {"name": "壁厚余量", "applicable": True, "passed": True, "value": "8 mm"},
        ),
        verified_scope=("machined",),
    )


def bad_e6_tool_unreachable() -> Observation:
    return collect_process(
        target="plate-rev1",
        route="machined",
        checks=(
            {"name": "刀具可达", "applicable": True, "passed": False, "value": "φ2 深 40"},
        ),
        verified_scope=("machined",),
    )


def bad_e6_all_not_applicable() -> Observation:
    """靠「全不适用」通过 E6。"""
    return collect_process(
        target="plate-rev1",
        route="machined",
        checks=(
            {"name": "刀具可达", "applicable": False, "passed": True, "value": None},
            {"name": "壁厚余量", "applicable": False, "passed": True, "value": None},
        ),
        verified_scope=("machined",),
    )


def unknown_e6() -> Observation:
    return collect_process(
        target="plate-rev1",
        route="",
        checks=(),
        verified_scope=(),
    )


# ────────────────────────────── E7 ──────────────────────────────


def good_e7() -> Observation:
    return collect_provenance(
        target="plate-rev1",
        claims=({"id": "C1", "text": "板厚 20 mm 满足刚度要求"},),
        citations=({"claim_id": "C1", "locator": "GB/T 1804-m 表1", "resolved": True},),
        outputs={"deflection_mm": 0.03},
        source_kind="standard_clause",
        source_ref="GB/T 1804-2000 表1",
        artifact_version="rev1",
        evidence_version="rev1",
    )


def bad_e7_no_citations() -> Observation:
    """★★ R-09 的伪造手法：两个布尔 + 来源标签，citations 为空。"""
    return collect_provenance(
        target="plate-rev1",
        claims=({"id": "C1", "text": "这块板合格"},),
        citations=(),
        outputs={},
        source_kind="official_doc",
        source_ref="",
        artifact_version="rev1",
        evidence_version="rev1",
    )


def bad_e7_fake_source() -> Observation:
    """随意填来源标签。"""
    return collect_provenance(
        target="plate-rev1",
        claims=({"id": "C1", "text": "这块板合格"},),
        citations=({"claim_id": "C1", "locator": "x", "resolved": True},),
        outputs={"ok": 1},
        source_kind="我觉得对",
        source_ref="经验",
        artifact_version="rev1",
        evidence_version="rev1",
    )


def bad_e7_stale_evidence() -> Observation:
    return collect_provenance(
        target="plate-rev1",
        claims=({"id": "C1", "text": "板厚合格"},),
        citations=({"claim_id": "C1", "locator": "标准表", "resolved": True},),
        outputs={"t": 20},
        source_kind="standard_clause",
        source_ref="GB/T 1804 表1",
        artifact_version="rev2",
        evidence_version="rev1",
    )


def unknown_e7() -> Observation:
    return collect_provenance(
        target="plate-rev1",
        claims=(),
        citations=(),
        outputs={},
        source_kind="",
        source_ref="",
    )
