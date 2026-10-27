"""★ 批次 85：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_costing · sw_drawing_expose
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 85；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **2 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 0 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH85"]

SPECS_BATCH85 = [
    ToolSpec(
        name="solidworks_drawing_create_three_standard_views",
        title="Drawing Three Standard Views (First/Third Angle)",
        module="sw_drawing_expose",
        function="create_three_standard_views",
        inject="drawing_model",
        params=[
            Param(
                "part_path",
                str,
                default="...",
                description=(
                    "Full path of the model the views are drawn from, extension included; an unsaved document has no pa"
                    "th, so save it first. Defaults to '...'."
                ),
            ),
            Param(
                "projection",
                str,
                default="first_angle",
                description=(
                    "Projection: first_angle calls the first-angle member, third_angle calls the third-angle member, an"
                    "d any other value raises a value error. Defaults to first_angle."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 Create1stAngleViews2.md）：`System.bool Create1stAngleViews2( System.string ModelNa"
            "me )`。两页的 `## Remarks` **逐字相同、只有一行**：「The views honor the automatic scaling behavior as spe"
            "cified in the document setting.」（视图的比例走文档设置里的自动缩放行为 ⇒ ★ 本工具**不传比例**，比例由图纸"
            "设置决定）。Returns 逐字：「True if successful, false if not」。Parameters 逐字：「ModelName: Name of the "
            "document from which to create views」。★★ `Create1stAn"
        ),
        doc=(
            "Create the three standard views of a saved model on the active drawing. Creates drawing views and does not"
            " save the document; projection picks first or third angle and no scale is passed, so view scale follows th"
            "e drawing document setting, and the model must already be saved because the call takes its path."
        ),
    ),
    ToolSpec(
        name="solidworks_costing_defaults",
        title="Get the Costing Defaults Object",
        module="sw_costing",
        function="get_costing_defaults",
        inject="cost_manager",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_costing.py）：`Object get_CostingDefaults()`。★ 真源是**本仓** `scripts/sw_costi"
            "ng.py` 的 `get_costing_defaults`（★ 它不是 SolidWorks API 成员，故无官方页）—— ★ 反射转储只给签名、**没有"
            "参数语义**：官方 CHM 无 costing 册（sw_costing.py 模块 docstring L30-31 逐字记载「本族官方 CHM 没有文档页"
            "（四册 CHM 里没有 costing 册），故只有签名、没有参数语义」）⇒ 仓库 docstring 只写「取成本默认值对象（属性"
            "）」，★ 不编合理解释。★ 派发名差异：COM 迟到绑定把属性 `get_CostingDe"
        ),
        doc=(
            "Read the Costing defaults object of the active document. Read-only; it hands back the defaults object itse"
            "lf rather than individual fields, and the costing interfaces have no official documentation pages, so no f"
            "ield semantics are claimed here."
        ),
    ),
]
