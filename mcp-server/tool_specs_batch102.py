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
        module="sw_assembly_doc", function="insert_explode_line_sketch_report",
        #: ★★ 2026-10-07（接手轮）订正：★ 目标函数首参是 **`doc`**，★ 不是 `model` ✗ ——
        #: ★ `register()` 不传 `inject_as` ⇒ **注入键字面上等于 `inject` 的值**（事实 50
        #: 2）
        #: ⇒ 写成 `inject="model"` 真调用时必 `TypeError: unexpected keyword argument 'm
        #: odel'` ✓
        #: ★ 同模块的**其余 spec 全部用 `inject="doc"`**（★ 例 `tool_specs_batch79.py:38
        #: `）✓
        inject="doc",
        params=[],
        doc=
            "爆炸直线：在当前爆炸视图里插入/关闭爆炸直线草图。""★ **爆炸直线**（官方 `ISketchManager::InsertExplodeLineSketch`，★ **零参**）—— "
            "★★ **会插入或关闭爆炸直线草图**（★ 同一个零参调用是**切换** ✓）"
            "★★★ **入口在 `ISketchManager` 上、★ 不在装配文档上** ✗ —— "
            "★ 本工具内部先取 `SketchManager` 再调 ✓ "
            "★★ **判据 = 回读**（★ 不是那个 `bool` ✓）：★ 官方 `## Returns` 逐字说的是"
            "「True if the explode line sketch is **inserted or closed**」⇒ "
            "★★ **两种结果都回真，那个 bool 分辨不了它们** ✓ ⇒ "
            "★ 本工具用 **特征树增量 + `ISketchManager::ActiveSketch`** 两条腿判 ✓ "
            "★★★ **前置是爆炸状态**：★ 装配体没有爆炸视图时它没有可依附的对象 ⇒ "
            "★ 返回体里带 `explode_view_count`，★ **没有爆炸视图就先别下「建不出来」的结论** ✓",
    ),
    #: ── ② SpeedPak（★ 规格 211 B6 · ★ 真机建成）────────────────────────────────
    ToolSpec(
        name="solidworks_create_speedpak",
        title="Create SpeedPak (IAssemblyDoc::CreateSpeedPak)",
        module="sw_assembly_doc", function="create_speedpak_report",
        #: ★★ 2026-10-07（接手轮）订正：★ 同上 —— 目标函数的**必填形参是 `doc`**
        #: （`create_speedpak_report(doc, *, speedpak_type, component_name, component_in
        #: dex)`）✓
        #: ⇒ ★ `inject` 必须是 `"doc"`（★ 它是 `RESOLVERS` 的键，指向同一个 `resolve_mod
        #: el`）✓
        inject="doc",
        params=[
            Param("speedpak_type", int, default=1,
                  description="SpeedPak 类型 —— ★ 官方 `## Parameters` 逐字："
                              "**1 = Mated** · **2 = Graphics** ✓（★ **枚举** ⇒ 无量纲 ✓）"),
            Param("component_name", str, default=None,
                  description="要选中的**子装配名**（★ 官方示例按名字选 ✓）；"
                              "★ 缺省时本工具**自行从组件列表解析名字** ✓"),
            Param("component_index", int, default=0,
                  description="取第几个组件（★ 仅在没给 `component_name` 时用 ✓）。"),
        ],
        doc=
            "SpeedPak：对选中的子装配建立 SpeedPak 简化配置。""★ **SpeedPak**（官方 `IAssemblyDoc::CreateSpeedPak`，★ **参数式 1 参**）—— "
            "★★ **会改装配的组件状态** ✓ "
            "★★★ **判据只能落在回读上**：★ 顶层**特征树看不见 SpeedPak** ✗ ⇒ "
            "★ 本工具回读 **`IComponent2::IsSpeedPak` 的**前后对比**」✓ —— "
            "★★ 「这次建成了」与「它一直是开的」**要分开记**（★ 返回体里 `is_speedpak_before` / "
            "`is_speedpak_after` 两个字段 ✓）✓ "
            "★★ **前置是「选中的子装配」**，★ 用官方示例的调用序："
            "`SelectByID2(<组件名>, \"COMPONENT\", 0,0,0, append, mark, callout, 0)` ✓；"
            "★ 本工具**逐个前置单列布尔**（组件数 · 名字访问器 · 选中 · 初始状态）—— "
            "★★ 因为「读数无效」与「真的不建」长得一样 ✓",
    ),
    #: ── ③ 曲线驱动阵列（★ **`stitched`** —— ★ 官方已宣布 Obsolete）────────────────
    ToolSpec(
        name="solidworks_insert_local_curve_driven_pattern",
        title="Local Curve-Driven Pattern (parameter-based, Obsolete path)",
        module="sw_pattern", function="insert_local_curve_driven_pattern_report",
        inject="model",
        params=[
            Param("flip_dir1", bool, default=False, description="★ 官方 `FlipDir1` ✓（方向 1 是否翻转）。"),
            Param("num1", int, default=3,
                  description="★ 官方 `Num1` —— ★ 方向 1 的实例数**含原始实例** ✓"),
            Param("equal_spacing1", bool, default=False,
                  description="★ 官方 `EqualSpacing1` ✓（方向 1 是否等间距）。"),
            Param("spacing1_mm", float, default=30.0,
                  description="方向 1 的间距（**毫米**）—— ★ 官方 `## Parameters` 逐字"
                              "「Distance between pattern instances along the curve」⇒ ★ **是长度** ✓；"
                              "★ 仅在 `equal_spacing1` 为真时有意义。"),
            Param("reference_point", int, default=0,
                  description="★ 官方 `ReferencePoint`（`swLocalCurvePatternReferencePoint_e`）"
                              "—— ★ **枚举** ⇒ 无量纲 ✓"),
            Param("curve_method", int, default=0,
                  description="★ 官方 `CurveMethod`（`swLocalCurvePatternCurveMethod_e`）—— ★ 枚举 ✓"),
            Param("align_method", int, default=0,
                  description="★ 官方 `AlignMethod`（`swLocalCurvePatternAlignment_e`）—— ★ 枚举 ✓"),
            Param("direction2", bool, default=False, description="★ 官方 `Direction2` ✓。"),
            Param("flip_dir2", bool, default=False, description="★ 官方 `FlipDir2` ✓。"),
            Param("num2", int, default=1, description="★ 官方 `Num2` ✓（方向 2 的实例数）。"),
            Param("equal_spacing2", bool, default=False, description="★ 官方 `EqualSpacing2` ✓。"),
            Param("spacing2_mm", float, default=0.0,
                  description="方向 2 的间距（**毫米**）—— ★ 同上、★ 是长度 ✓。"),
            Param("pattern_seed_only", bool, default=False,
                  description="★ 官方 `PatternSeedOnly` ✓（方向 2 是否只复制方向 1 的种子）。"),
            Param("seed_feature", str, default=None,
                  description="要阵列的**体/特征名** —— ★ 官方 mark 表逐字 **1 = Components to "
                              "pattern** ✓（★ **前置**）。"),
            Param("curve_sketch", str, default=None,
                  description="方向 1 的**曲线草图名** —— ★ 官方 mark 表逐字 **2 = Curve, edge, "
                              "sketch, or sketch entity for Direction 1** ✓（★ **前置**）。"),
        ],
        doc=
            "曲线驱动阵列（参数式入口；官方标记 Obsolete）。""★★★ **曲线驱动阵列的**参数式**入口**（官方 `IFeatureManager.FeatureLocalCurveDrivenPattern`）"
            "—— ★★ **状态：`stitched`** ✗ "
            "★★★★ **为什么只到 `stitched`（★ 两条独立理由、★ 都要说）**："
            "★ **① 官方页第一行就写着 `Obsolete`** ✗ —— 逐字："
            "「Obsolete. See `IFeatureManager::CreateFeature` and the Remarks in "
            "`ILocalCurvePatternFeatureData`.」⇒ ★★ **官方自己指向属性式那条** ✓；"
            "★★ **② 真机两档有效读数皆不建** ✗（★ 第 0 / 1 档：`mark1=True · mark2=True · 选区=2` "
            "而特征树新增 `[]`）✓ "
            "★★★ **而本工具仍有价值**：★ 它把那条路的**两处前置（mark 1 / mark 2）与返回值"
            "单列回报**，★ 让「前置没上」与「真的不建」**分得开** ✓ "
            "★⚠ **别与 `configure_curve_driven_pattern` 混淆**：★ 那条是**属性式**（走 "
            "`AccessSelections` ✗）—— ★ **两者不是同一件事** ✓",
    ),
]
