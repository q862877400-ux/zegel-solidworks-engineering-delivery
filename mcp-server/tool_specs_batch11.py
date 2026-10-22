"""第十一批 MCP 工具声明：**拓扑研究的「目标 / 约束 / 控制」入口** 4 个。

## 来源与筛选（2026-10-01 轮 204，Spec Kit `123`）

**候选不是手挑的，是从一份**全量清单**里筛的** —— 而这份清单是本轮**先做出来**的：

```
`tools/probe_unexposed_functions.py`（既有工具）此前只印「孤立能力（前 30）」，
后面写「…（还有 272 个）」⇒ ★ **302 个里 87% 读者看不到** ⇒「选哪一批暴露」只能靠感觉。
⇒ 本批之前先给它加**结构化全量输出**（`D:/AI/SW/output/orphan-capabilities.json`），
  连**签名**一起落盘 ⇒ 于是"选哪批"**可从数据复现**。
实测：302 个孤立能力 · 首参可注入（`model`/`sw_app`/`study`）**51** · 含裸坐标（规则 3 会拒）**4**
```

**为什么先做拓扑这一族**（四条理由，逐条可核）：
1. `topology_optimization` 是 **`verified`**，且 **2026-10-01（轮 203）真机复验 `verdict: pass`**
   （85,748 单元 / 图数 2 / `材料质量1` / 228.9 s，证据 `output/topology-evidence.json`）；
2. `sw_topology` 是**孤立能力最集中的可注入模块**（12 个）；
3. ★ **先例已存在**：`solidworks_topology_create_study` / `_evidence` / `_run` 三个工具
   **已经在挂**，本批沿用**同一个** `inject="study"` + `param_alias={"study_name": None}` 模板；
4. 内聚：本批全部是**同一条真机链**上「目标 / 约束 / 控制」那一环的构造器。

| 取 | 函数 | 为什么 |
|---|---|---|
| ✅ | `sw_topology.create_mass_constraint` | 质量约束（减重百分比）—— 拓扑的核心约束 |
| ✅ | `sw_topology.create_factor_of_safety_constraint` | 安全系数约束 —— A9「刚性够不够」那一问的入口 |
| ✅ | `sw_topology.create_preserved_region` | 保留区 —— 决定"哪里不许挖" |
| ✅ | `sw_topology.create_thickness_control` | 厚度控制 —— 决定"能挖多薄" |

| 不取 | 理由 |
|---|---|
| `sw_topology.create_symmetry_control` / `create_demold_control` | ★ **枚举值未核**（对称类型 / 拔模方向）。本批**不猜枚举**（铁律 5）⇒ 留下批，先查官方枚举 |
| `sw_topology.create_stress_constraint` | 同族但**与本批的"两约束"重叠**（质量 + 安全系数已覆盖 A9 那一问）⇒ 分批做，避免一次改太多 |
| `sw_surface.create_*_surface`（7 个） | ★ `IModeler.Create*Surface` **返回值跨次会变**（已知事实 40），且 `create_bspline_surface` 报 `0x80010105` ⇒ **先暴露会把"不可靠"直接摊给用户**，需先定行为 |
| `sw_part` 的 14 个 | 多为草图/阵列辅助，且 `circular_pattern` 含 `angle_rad` ⇒ ★ **与规则 2（角度用 `_deg`）冲突**，要先决定换算边界 |

## ⚠⚠ 本批**不声称真机验证**（如实说）
```
实测：`tools/capture_topology_evidence.py` **直接调用过**的拓扑函数只有 4 个
  （create_topology_study · set_topology_goal · set_material · run_analysis）
⇒ ★ 而本批这 4 个**不在其中** ⇒ 它们**没有直接的真机证据**。
★ 本批只做**暴露**（把已有实现挂到柜台上）；`topology_optimization` 的真机证据
  仍以那条**已验证的整链**为准（`capture_topology_evidence.py`）——
  **不因为"挂上了"就给它们任何 `verified` 身份**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch11.py
# 定位:   「孤立能力暴露」第十一批（Spec Kit `123`）—— 拓扑的「目标/约束/控制」入口。
#         前十批见 tool_specs_batch1..10。
# 官方签名依据: 不适用（只做参数搬运；目标函数的签名已在 scripts/sw_topology.py 的来源块里核过）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH11"]

#: `study_name` 由**解析器**消费（不进目标函数）⇒ alias 映射到 `None` 表示「不传」。
#: ★ 与 `tool_specs_batch1.py` 里那三个拓扑工具**同一个约定**（先例，不另立一套）。
_STUDY_ALIAS = {"study_name": None}

SPECS_BATCH11 = [
    ToolSpec(
        name="solidworks_topology_create_mass_constraint",
        title="Create Topology Mass Constraint",
        module="sw_topology",
        function="create_mass_constraint",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Create a mass constraint for a topology study (mass-reduction percent "
        "semantics). Returns the constraint object.",
        params=[
            Param(
                "study_name",
                str,
                default="",
                description="Target study; omit to use the active study. "
                "Consumed by the resolver, NOT passed to the function.",
            ),
            Param(
                "reduce_percent",
                float,
                description="Target mass reduction in percent (e.g. 75 means -75%).",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_topology_create_factor_of_safety_constraint",
        title="Create Topology Factor-of-Safety Constraint",
        module="sw_topology",
        function="create_factor_of_safety_constraint",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Create a factor-of-safety constraint for a topology study (stress must "
        "stay below that percentage of yield strength).",
        params=[
            Param(
                "study_name",
                str,
                default="",
                description="Target study; omit to use the active study. "
                "Consumed by the resolver, NOT passed to the function.",
            ),
            Param(
                "specified_factor", float, description="Factor of safety (e.g. 1.5)."
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_topology_create_preserved_region",
        title="Create Topology Preserved Region",
        module="sw_topology",
        function="create_preserved_region",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Create a preserved region for a topology study (material that must not "
        "be removed). ⚠ `option` is an official enum value; omit to use the default.",
        params=[
            Param(
                "study_name",
                str,
                default="",
                description="Target study; omit to use the active study. "
                "Consumed by the resolver, NOT passed to the function.",
            ),
            Param(
                "option",
                int,
                default=0,
                description="Official option enum value; 0 means the module default.",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_topology_create_thickness_control",
        title="Create Topology Thickness Control",
        module="sw_topology",
        function="create_thickness_control",
        inject="study",
        doc="Create a thickness control for a topology study (minimum/maximum "
        "thickness). Units are millimetres (rule 2).",
        param_alias={
            "study_name": None,  # 由解析器消费，不进目标函数
            "min_thickness_mm": "min_thickness",
            "max_thickness_mm": "max_thickness",
        },
        params=[
            Param(
                "study_name",
                str,
                default="",
                description="Target study; omit to use the active study. "
                "Consumed by the resolver, NOT passed to the function.",
            ),
            Param(
                "min_thickness_mm",
                float,
                default=0.0,
                description="Minimum thickness in millimetres; 0 means the module default.",
            ),
            Param(
                "max_thickness_mm",
                float,
                default=0.0,
                description="Maximum thickness in millimetres; 0 means the module default.",
            ),
        ],
    ),
]
