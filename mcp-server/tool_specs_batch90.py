"""★ 批次 90：Costing **写侧**最后 3 个（批量 / 加价 / 自定义成本）—— ★ C 类勘探后的收尾批。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_costing.py`（`set_lot_size` / `set_markup` / `assign_custom_cost`
# ）
# 定位:   ★ 规格 `specs/205-tool-ramp/` §8 的**批 90** —— ★ 走"加解析器换工具"：
#         同笔加两个注入键 `"cost_analysis"` / `"cost_body"` ✓
#         ★ 选域依据（**SC-009 要求的预筛**，跑的是 `output` 的 C 类普查）：
#           C 类未覆盖候选 **281** 个，其中 ★ **97 个属"取哪一个"的歧义组**（`win`/`hwnd`/
# `route_manager`/`target`/`pdm_document`/`ctrl`/`study_name`/`obj`/`h`）⇒ **一律不碰**
# ；
#           `cost_analysis`(3) + `cost_body`(2) 这 **5 个**可加键 ⇒ ★ **组内真新 3 个** ✓
# 官方依据: ★★ **本批三个都没有官方 md 页** —— `C:\swapi\types` 下 `glob`
# `set_LotSize` / `set_MarkUpType` / `AssignCustomCost` **均 0 命中**（那套源不含 `sldco
# stingapi` 册）
#   ⇒ ★ 真源是**本仓** `scripts/sw_costing.py`（其来源块逐字写着依据是
# 「**反射确认的实参个数** `COSTING_ARITY`」，接口 `ICostManager` / `ICostModel` / `ICos
# tAnalysis`）
#   ⇒ ★ **不编官方签名**（铁律 5），doc 里如实说明真源与"官方是属性还是方法" ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **3 个工具** ⇒ 工具数 419 → **422**
# ★★ 本批**不做**的（FR-006/D-5）：
#     · `sw_costing.read_cost_analysis` —— ★ 早已挂成 `solidworks_costing_read_analysis` ✓
#     · `sw_costing.read_cost_body`     —— ★ 早已挂成 `solidworks_costing_read_body` ✓
#     （★ 这两个是**只读侧**，`*_report` 包装一早就建好了 ⇒ 只取**写侧**这 3 个）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH90"]

SPECS_BATCH90 = [
    ToolSpec(
        name="solidworks_costing_set_lot_size",
        title="Set the Costing Lot Size (batch quantity)",
        module="sw_costing",
        function="set_lot_size",
        inject="cost_analysis",
        params=[
            Param(
                "lot_size",
                int,
                description="Batch size in parts, a count rather than a length.",
            ),
        ],
        evidence=(
            "设成本分析的**批量大小**。★ 官方依据：`C:\\swapi\\types` **无该成员的页** ⇒ ★ 真源是**本仓** `scripts/sw_c"
            "osting.py:292-297`，其 docstring 逐字标注「⚑ 官方是**属性**（`set_LotSize`），不是方法」⇒ ★ 本工具走**属性"
            "写**那条路 ✓。★ 注入键 `cost_analysis` 给的是该零件的**成本分析对象**（取法 `cost_part` → `GetCostAnalysis"
            "`，不是猜的）✓ ⚠ **未在本机实测**（铁律 2）。"
        ),
        doc=(
            "Set the lot size of the part cost analysis. It modifies the cost analysis to the batch count the cost is c"
            "omputed for; run the cost-update tool afterwards so the cost is recomputed."
        ),
    ),
    ToolSpec(
        name="solidworks_costing_set_markup",
        title="Set the Costing Markup (type and percent)",
        module="sw_costing",
        function="set_markup",
        inject="cost_analysis",
        params=[
            Param(
                "markup_type",
                int,
                default=None,
                description=(
                    "Markup type as an integer, passed through unchanged because the valid values are not documented in"
                    " the local sources. Defaults to null."
                ),
            ),
            Param(
                "markup_percent",
                float,
                default=None,
                description="Markup percentage as a plain ratio with no unit. Defaults to null.",
            ),
        ],
        evidence=(
            "设成本分析的**加价**（类型 + 百分比）。★ 官方依据：`C:\\swapi\\types` **无该成员的页** ⇒ ★ 真源是**本仓** "
            "`scripts/sw_costing.py:300-...`，其 docstring 逐字标注「⚑ `MarkUpType` / `MarkUpPercent` 都是**属性**」且"
            "「⚠ `MarkUpType` 的取值（按成本/按价格/按数量？）**两套源都查不到**」⇒ ★ 如实照抄，不编 ✓ ★ 两个参数都有默"
            "认值 ⇒ **只传一个也行**（未传的那个走函数默认）✓ ⚠ **未在本机实测**（铁律 2）。"
        ),
        doc=(
            "Set the markup type and the markup percentage of the part cost analysis. It modifies the cost analysis; bo"
            "th arguments are optional, so you may pass only one, and the markup type values are not documented in the "
            "local sources."
        ),
    ),
    ToolSpec(
        name="solidworks_costing_assign_custom_cost",
        title="Assign a Custom Cost to One Cost Body",
        module="sw_costing",
        function="assign_custom_cost",
        inject="cost_body",
        #: ★★ `body_name` 由**解析器消费**（`resolve_cost_body` 读它来决定注哪个实体）
        #:   ⇒ ★ `param_alias={名字: None}` —— 即 `tool_registry.py:511-513` 那条机制
        #:   「`param_alias` 里 None = 由解析器消费，不进目标函数」✓
        #:   ★ 不这么写就会被 `check_param_binding` 当场抓到（本会话已踩两次）✓
        param_alias={"body_name": None},
        params=[
            Param(
                "amount",
                float,
                description="Custom cost amount, passed through in document units without conversion.",
            ),
            Param(
                "body_name",
                str,
                default="",
                description=(
                    "Cost body name; empty uses the only body when the list holds exactly one, and otherwise the call a"
                    "sks for a name. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "给**一个成本实体**指定自定义成本。★ 官方依据：`C:\\swapi\\types` **无该成员的页** ⇒ ★ 真源是**本仓** `scri"
            "pts/sw_costing.py:439-442`（`_checked(cost_body, \"AssignCustomCost\", float(amount))`），其 docstring 逐"
            "字标注「⚠ 与哪些费用项相加/相抵，**官方无说明**」⇒ ★ 如实照抄，不替官方解释 ✓ ★ 改完通常要 `solidworks_cos"
            "ting_update_cost_for_all_bodies` 让成本刷新 ✓ ⚠ **未在本机实测**（铁律 2）。"
        ),
        doc=(
            "Assign a custom cost to one cost body of the part. It modifies the cost analysis; the reference does not s"
            "ay which cost items the amount adds to or offsets, and the amount is passed through in document units with"
            "out conversion."
        ),
    ),
]
