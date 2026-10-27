"""★ 批次 102：规格 213 · B3（后半）—— B 类余下三项（爆炸直线 · SpeedPak · 曲线驱动阵列）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `specs/213-hook-up-tools/plan.md` 的 **B3**（★ 后半）
# 定位:   ★★ B 类 5 项的**最后三项** ✓ —— ★ 两步都已完成：
#   ★ **B2**：★ 把探针里已证实的调用序**缝进模块** ✓
#     · `scripts/sw_assembly_doc.py` 的 `insert_explode_line_sketch_report`
#       （★ 来自 `tools/probe_spec211_explodeline.py` ✓）
#     · `scripts/sw_assembly_doc.py` 的 `create_speedpak_report`
#       （★ 来自 `tools/probe_spec211_speedpak.py` ✓）
#     · `scripts/sw_pattern.py` 的 `insert_local_curve_driven_pattern_report`
#       （★ 来自 `tools/probe_spec211_curvedriven.py` ✓）
#   ★ **B3**：本文件 ✓
# 官方依据: 见三个模块函数各自的来源块（`swapi` 签名 + `## Remarks` 的 mark 表 / 前置）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **3 个工具** ⇒ 工具数 456 → **459**
# ★★★ **等级要如实分两档**（★ A7：★ 全文不许把 `stitched` 写成 `verified`）：
# · ★ **`explode_line_sketch`** ⇒ 真机建成（★ `ActiveSketch` 在 + 特征树增量 ✓）⇒ **`ver
# ified`** ✓
# · ★ **`speedpak`** ⇒ 真机建成（★ `IComponent2::IsSpeedPak` 前后对比 ✓）⇒ **`verified`*
# * ✓
#   · ★★ **`curve_driven_pattern`** ⇒ ★ **官方页第一行就是 `Obsolete`** ✗，
#     且★ 真机**两档有效读数皆不建** ✗ ⇒ ★★ **只到 `stitched`** ✓（★ 不许写成 `verified` ✓）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH102"]


SPECS_BATCH102 = [
    #: ── ① 爆炸直线（★ 规格 211 B6 · ★ 真机建成）────────────────────────────────
    ToolSpec(
        name="solidworks_insert_explode_line_sketch",
        title="Insert/Close Explode Line Sketch (ISketchManager)",
        module="sw_assembly_doc",
        function="insert_explode_line_sketch_report",
        #: ★★ 2026-10-07（接手轮）订正：★ 目标函数首参是 **`doc`**，★ 不是 `model` ✗ ——
        #: ★ `register()` 不传 `inject_as` ⇒ **注入键字面上等于 `inject` 的值**（事实 50
        #: 2）
        #: ⇒ 写成 `inject="model"` 真调用时必 `TypeError: unexpected keyword argument 'm
        #: odel'` ✓
        #: ★ 同模块的**其余 spec 全部用 `inject="doc"`**（★ 例 `tool_specs_batch79.py:38
        #: `）✓
        inject="doc",
        params=[],
        evidence=(
            "爆炸直线：在当前爆炸视图里插入/关闭爆炸直线草图。★ **爆炸直线**（官方 `ISketchManager::InsertExplodeLineSk"
            "etch`，★ **零参**）—— ★★ **会插入或关闭爆炸直线草图**（★ 同一个零参调用是**切换** ✓）★★★ **入口在 `ISketch"
            "Manager` 上、★ 不在装配文档上** ✗ —— ★ 本工具内部先取 `SketchManager` 再调 ✓ ★★ **判据 = 回读**（★ 不是那"
            "个 `bool` ✓）：★ 官方 `## Returns` 逐字说的是「True if the explode line sketch is **inserted or closed**」"
            "⇒ ★★ **两种结果都回真，那个 bool 分辨不了它们** ✓ ⇒ ★ 本工具用 **特征树增量 + `ISketchManager::ActiveSketc"
            "h`** 两条腿判 ✓ ★★★ **前置是爆炸状态**：★ 装配体没有爆炸视图时它没有可依附的对象 ⇒ ★ 返回体里带 `explode_v"
            "iew_count`，★ **没有爆炸视图就先别下「建不出来」的结论** ✓"
        ),
        doc=(
            "Insert or close the explode-line sketch of the active assembly. It toggles the sketch on each call, writes"
            " a sketch into the assembly and does not save the document. The assembly must already have an exploded vie"
            "w, and the feature tree plus the active sketch are read back because the boolean return cannot tell insert"
            " from close."
        ),
    ),
    #: ── ② SpeedPak（★ 规格 211 B6 · ★ 真机建成）────────────────────────────────
    ToolSpec(
        name="solidworks_create_speedpak",
        title="Create SpeedPak (IAssemblyDoc::CreateSpeedPak)",
        module="sw_assembly_doc",
        function="create_speedpak_report",
        #: ★★ 2026-10-07（接手轮）订正：★ 同上 —— 目标函数的**必填形参是 `doc`**
        #: （`create_speedpak_report(doc, *, speedpak_type, component_name, component_in
        #: dex)`）✓
        #: ⇒ ★ `inject` 必须是 `"doc"`（★ 它是 `RESOLVERS` 的键，指向同一个 `resolve_mod
        #: el`）✓
        inject="doc",
        params=[
            Param(
                "speedpak_type",
                int,
                default=1,
                description="SpeedPak type: 1=Mated, 2=Graphics. Defaults to 1.",
            ),
            Param(
                "component_name",
                str,
                default=None,
                description=(
                    "Name of the sub-assembly component to select. Defaults to None, in which case the tool resolves th"
                    "e name from the component list itself."
                ),
            ),
            Param(
                "component_index",
                int,
                default=0,
                description="Index of the component to use when component_name is empty. Defaults to 0.",
            ),
        ],
        evidence=(
            "SpeedPak：对选中的子装配建立 SpeedPak 简化配置。★ **SpeedPak**（官方 `IAssemblyDoc::CreateSpeedPak`，★ **"
            "参数式 1 参**）—— ★★ **会改装配的组件状态** ✓ ★★★ **判据只能落在回读上**：★ 顶层**特征树看不见 SpeedPak** "
            "✗ ⇒ ★ 本工具回读 **`IComponent2::IsSpeedPak` 的**前后对比**」✓ —— ★★ 「这次建成了」与「它一直是开的」**要"
            "分开记**（★ 返回体里 `is_speedpak_before` / `is_speedpak_after` 两个字段 ✓）✓ ★★ **前置是「选中的子装配」*"
            "*，★ 用官方示例的调用序：`SelectByID2(<组件名>, \"COMPONENT\", 0,0,0, append, mark, callout, 0)` ✓；★ 本工"
            "具**逐个前置单列布尔**（组件数 · 名字访问器 · 选中 · 初始状态）—— ★★ 因为「读数无效」与「真的不建」长得一"
            "样 ✓"
        ),
        doc=(
            "Create a SpeedPak simplified configuration on a selected sub-assembly. Writes the component state and does"
            " not save the document; the top-level feature tree does not show SpeedPak, so the component SpeedPak flag "
            "is read before and after. Each precondition is reported as its own boolean, because an invalid reading loo"
            "ks the same as a feature that was not built."
        ),
    ),
    #: ── ③ 曲线驱动阵列（★ **`stitched`** —— ★ 官方已宣布 Obsolete）────────────────
    ToolSpec(
        name="solidworks_insert_local_curve_driven_pattern",
        title="Local Curve-Driven Pattern (parameter-based, Obsolete path)",
        module="sw_pattern",
        function="insert_local_curve_driven_pattern_report",
        inject="model",
        params=[
            Param(
                "flip_dir1",
                bool,
                default=False,
                description="Whether to flip direction 1. Defaults to false.",
            ),
            Param(
                "num1",
                int,
                default=3,
                description="Number of instances in direction 1, including the seed. Defaults to 3.",
            ),
            Param(
                "equal_spacing1",
                bool,
                default=False,
                description="Whether to space direction 1 equally. Defaults to false.",
            ),
            Param(
                "spacing1_mm",
                float,
                default=30.0,
                description=(
                    "Spacing between instances along the curve in millimetres; it only matters when equal_spacing1 is t"
                    "rue. Defaults to 30.0."
                ),
            ),
            Param(
                "reference_point",
                int,
                default=0,
                description="Reference point enum for the curve pattern. Defaults to 0.",
            ),
            Param(
                "curve_method",
                int,
                default=0,
                description="Curve method enum for direction 1. Defaults to 0.",
            ),
            Param(
                "align_method",
                int,
                default=0,
                description="Alignment enum for the pattern. Defaults to 0.",
            ),
            Param(
                "direction2", bool, default=False, description="Whether to use a second direction. Defaults to false."
            ),
            Param(
                "flip_dir2", bool, default=False, description="Whether to flip direction 2. Defaults to false."
            ),
            Param(
                "num2",
                int,
                default=1,
                description="Number of instances in direction 2. Defaults to 1.",
            ),
            Param(
                "equal_spacing2",
                bool,
                default=False,
                description="Whether to space direction 2 equally. Defaults to false.",
            ),
            Param(
                "spacing2_mm",
                float,
                default=0.0,
                description="Spacing between instances in direction 2 in millimetres. Defaults to 0.0.",
            ),
            Param(
                "pattern_seed_only",
                bool,
                default=False,
                description="Whether direction 2 copies only the seeds of direction 1. Defaults to false.",
            ),
            Param(
                "seed_feature",
                str,
                default=None,
                description=(
                    "Name of the body or feature to pattern, selected with mark 1. Defaults to None, which fails the fi"
                    "rst precondition."
                ),
            ),
            Param(
                "curve_sketch",
                str,
                default=None,
                description=(
                    "Name of the curve, edge or sketch entity for direction 1, selected with mark 2. Defaults to None, "
                    "which fails the second precondition."
                ),
            ),
        ],
        evidence=(
            "曲线驱动阵列（参数式入口；官方标记 Obsolete）。★★★ **曲线驱动阵列的**参数式**入口**（官方 `IFeatureManager"
            ".FeatureLocalCurveDrivenPattern`）—— ★★ **状态：`stitched`** ✗ ★★★★ **为什么只到 `stitched`（★ 两条独立理"
            "由、★ 都要说）**：★ **① 官方页第一行就写着 `Obsolete`** ✗ —— 逐字：「Obsolete. See `IFeatureManager::Creat"
            "eFeature` and the Remarks in `ILocalCurvePatternFeatureData`.」⇒ ★★ **官方自己指向属性式那条** ✓；★★ **② "
            "真机两档有效读数皆不建** ✗（★ 第 0 / 1 档：`mark1=True · mark2=True · 选区=2` 而特征树新增 `[]`）✓ ★★★ **"
            "而本工具仍有价值**：★ 它把那条路的**两处前置（mark 1 / mark 2）与返回值单列回报**，★ 让「前置没上」与「真"
            "的不建」**分得开** ✓ ★⚠ **别与 `configure_curve_driven_pattern` 混淆**：★ 那条是**属性式**（走 `AccessSele"
            "ctions` ✗）—— ★ **两者不是同一件事** ✓"
        ),
        doc=(
            "Skip this tool, NOT USABLE on this machine: both valid runs created no feature. The entry point is obsolet"
            "e as well; both selection marks were held while the feature tree gained nothing, so the remaining value is"
            " diagnosis, since the mark-1 and mark-2 preconditions are reported separately. Do not confuse it with the "
            "property-based curve-driven pattern, which is a different path."
        ),
    ),
]
