"""★ 批次 104：规格 217 · B3+B4 —— 工程图全图视图清单 + 质量属性/截面/筋参数三个读侧。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `specs/217-expose-orphans/plan.md` 的 **B3 + B4**
# 定位:   ★ 把「已实现但没暴露」的 4 个读侧公开函数补成工具；判据见 spec.md §四。
# 官方依据: ★ 逐个函数的官方依据在它们各自的 `scripts/` 源码块里（本仓铁律 1）——
#          本文件只做声明式包装，不重复抄签名 ⇒ 详见：
#            · `scripts/sw_mass_property.py` 的来源块（mass_property_object / crosscheck）
#            · `scripts/sw_feature_readback.py` 的来源块（rib_params）
#            · `scripts/sw_drawing_view.py` 的来源块（list_drawing_views_report）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **4 个工具** ⇒ 工具数 463 → **467**
# ★★★ 等级如实：★ 本条**只增加暴露面**，★ **不动台账任何 `level`** ✓
#   （★ 挂柜台定则：暴露成功 / 可运行 / 返回语义已验证是**三件事**；
#    ★★ 规格 204 的 P4–P6 曾把 339 暴露面缺口误当真实能力缺口而整阶段作废）✓
# ★★ 四个都是**读侧**（★ 不需要预选 ⇒ ★ 不会触发预选族门禁；★ doc 里也**不写**"需先选中"）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH104 = [
    ToolSpec(
        name="solidworks_drawing_list_views_report",
        title="List ALL Drawing Views (with scale / notes / visible count)",
        module="sw_drawing_view", function="list_drawing_views_report",
        inject="model",
        read_only=True,
        params=[],
        doc="★ **列出工程图的全部视图**（★ 名字 / **比例 / 注释数 / 可见件数**）—— ★ 读侧。"
            "★★ 与既有 `solidworks_drawing_list_views` 的区别（★ 逐字比对过，**不是重复**）："
            "★ 那个只列**当前图纸**上的视图、且只给**名字 + 类型码**；"
            "★ 这个列**整张工程图的所有视图**、并多给**比例 / 注释数 / 可见件数**三项读数 ⇒ "
            "★ **范围与读数都更全** ✓"
            "★ 判据：★ 回的是一份 JSON 化的清单（★ 每个视图一行），★ 不靠返回值真有内容来断言。"
            "⚠ 只对**工程图**有效（零件/装配会失败，★ 不静默回空表）。",
    ),
    ToolSpec(
        name="solidworks_mass_property_object",
        title="Get Mass Properties Object",
        module="sw_mass_property", function="mass_property_object",
        inject="model",
        read_only=True,
        params=[],
        doc="★ **取质量属性对象**（★ 读侧）。"
            "★ 用途：★ 这是本仓质量属性那一族的**底层读数入口**，★ 需要逐项读密度/体积/惯量时用它 ✓"
            "★ 与既有 `solidworks_part_mass_properties` 的区别：★ 那个给**算好的汇总**；"
            "★ 这个给**对象**（★ 供进一步的逐项读取）✓"
            "⚠ 取不到时应报错（★ 不返回 `None` 让人以为属性全零）。",
    ),
    ToolSpec(
        name="solidworks_section_area_crosscheck",
        title="Section-area Cross-check (IFace2.GetArea vs section properties)",
        module="sw_mass_property", function="section_area_crosscheck",
        inject="model",
        read_only=True,
        params=[],
        doc="★ **截面面积交叉验证**（★ 读侧）：★ 把 `GetSectionProperties2` 读到的面积与 "
            "`IFace2.GetArea()` 的读数**并排给出** ✓"
            "★★ 为什么值得暴露：★ 本仓用它验过 **12/12 次完全相同** ⇒ ★ 它是"
            "「截面属性那族读数可不可信」的**判据工具** ✓"
            "⚠ 单位那件事本仓**尚未确证**（★ 见 `solidworks_section_properties` 的 `units_verified`）"
            "⇒ ★ 本工具**同样不声称单位** ✓",
    ),
    ToolSpec(
        name="solidworks_rib_params",
        title="Read Rib Feature Parameters",
        module="sw_feature_readback", function="rib_params",
        inject="model",
        params=[
            Param("feature_name", str, default="",
                  description="★ 筋特征名（★ 空串 = 让能力层自己挑；★ 名字不是坐标 ⇒ 规则 3 合规）。",
                  required=False),
        ],
        doc="★ **读筋（Rib）特征的一组参数**（★ 读侧）。"
            "★ 与既有 `solidworks_part_rib` 的关系：★ 那个**建**筋、这个**读**筋的参数 ⇒ "
            "★ 建完回读是它最自然的用法 ✓"
            "★ 判据：★ 回的是**逐项参数读数**（★ 读不到就如实报，★ 不假装有值）✓",
    ),
]
