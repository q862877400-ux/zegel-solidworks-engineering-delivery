"""★ 批次 95：规格 209 · B4-3 —— 相交特征（`PreIntersect2` → `PostIntersect`，官方两步）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_boolean_ops.py`（★ **新建**，铁律 3：`scripts/` 白名单内；
#         ★ 本仓既有零件特征模块里**没有多体/布尔这一族** —— 裁决书指定的落点就是它）
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-3** · 外部项目 idx **181 `interse
#           ct`**。
#   ★★ 裁决书逐字：「真名是**两步** `PreIntersect2` → `PostIntersect`；RegionType 三值表 +
#   示例 mark=0 + 排除数组形状齐备；★ 读侧 `IIntersectFeatureData` **零指针族** ⇒
#   ★ **唯一要实测的只有 `System.object` 布尔 SafeArray 的包装**」✓
# 官方依据: `C:\\swapi\\types\\IFeatureManager\\{PreIntersect2,PostIntersect}.md` ·
#   `C:\\swapi\\types\\IIntersectFeatureData\\{GetIntersectionsCount,CapPlanar,Merge,Consume}.md` ·
#   ★★ `C:\\swapi\\examples\\Create_Intersect_Feature_Example_VB.md`（**调用序**：按**名字 + 类型**
#   选 `SOLIDBODY` / `PLANE`，都 **mark 0** ⇒ `PreIntersect2` ⇒ 清选区 ⇒ 拼**与体数等长**的
#   布尔数组 ⇒ `PostIntersect(excludeArray, True, False)`）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入（全部按官方签名与官方示例自建）。
# 规模:   **1 个工具** ⇒ 工具数 443 → **444**
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH95"]

SPECS_BATCH95 = [
    ToolSpec(
        name="solidworks_part_intersect",
        title="Create an Intersect Feature (PreIntersect2 → PostIntersect)",
        module="sw_boolean_ops", function="create_intersect",
        inject="model",
        params=[
            Param("selection", str, default="__current_selection__",
                  description="**声明式选择器**（★ 规则 3）—— `\"__current_selection__\"` 或"
                              "**逗号分隔的 `<类型>:<名字>`**（★ 官方示例就是按名字+类型选："
                              "`SelectByID2(\"Shell1\", \"SOLIDBODY\", …)` / "
                              "`SelectByID2(\"Plane6\", \"PLANE\", …)`），"
                              "例如 `\"SOLIDBODY:凸台-拉伸1,PLANE:上视基准面\"`；"
                              "★ 省略类型时默认 `SOLIDBODY`。"),
            Param("cap_planar", bool, default=False,
                  description="官方 `CapPlanar`：`True` 把曲面的**平面开口封盖**成闭合体积。"),
            Param("region_type", str, default="intersecting_and_internal",
                  description="官方 `PreIntersect2` 的 `RegionType` **三值**："
                              "`intersecting`(0) · `internal`(1) · `intersecting_and_internal`(2)。"),
            Param("exclude", str, default="",
                  description="**要排除的体序号**（逗号分隔，0 基）—— 对应官方 "
                              "`IntersectionsToExclude` 那个**布尔数组**；"
                              "★ 本工具替你拼成**与 `PreIntersect2` 回的体数等长**的数组 ✓ "
                              "⚠ 把**唯一的体**排除掉 ⇒ 建不出特征（★ 真机实测，属应然）。"),
            Param("merge", bool, default=True,
                  description="官方 `Merge`：`True` 把所有相交区域**合并成一个体**。"),
            Param("consume", bool, default=False,
                  description="官方 `Consume`：`True` 把**输入曲面从特征树里移除**"
                              "（⚠ 有副作用 ⇒ 默认 False）。"),
        ],
        doc="★ **相交特征**（官方**两步**：`IFeatureManager::PreIntersect2` → `PostIntersect`）—— "
            "★★ 状态：**真机建成 `相交1`**（2026-10-06 · SW 2026 SP4.1）✓ "
            "★★ **裁决书点名「唯一要实测」的那件事已验**：`PostIntersect` 第 1 参是 `System.object`"
            "（**布尔 SafeArray**）—— ★ 本工具包 **`VARIANT(VT_ARRAY | VT_BOOL)`**，"
            "★ 真机**双向都成立**：不排除 ⇒ 建出 `相交1`；**排除唯一的体** ⇒ `PostIntersect` 回 `None`、"
            "**特征没建出来** ⇒ ★★ **说明那个 `True` 真被 SW 读走了**（不是「没报错」）✓ "
            "★ 另两条本仓既有纪律也照做：★ 数组实参**必须包 `VARIANT`**（裸 list 会**静默回 None** —— "
            "见 `scripts/sketch_relations.py` 的真机教训）；★ 选择走官方示例的**名字 + 类型**"
            "（`SOLIDBODY` / `PLANE`，都 **mark 0**）✓ "
            "★ 判据（规则 6，全回读）：**`PreIntersect2` 回的体数** + **特征树增量** + "
            "**`IIntersectFeatureData::GetIntersectionsCount()`**（零参回 int）—— "
            "★ **不拿** `PostIntersect` 回的那个 `IFeature` 当判据 ✓",
    ),
]
