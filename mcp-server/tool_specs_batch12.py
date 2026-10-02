"""第十二批 MCP 工具声明：**拓扑研究的「脱模 / 应力 / 对称」** 3 个 + 补全上批一个参数说明。

## 来源与筛选（2026-10-01 轮 205，Spec Kit `124`）

候选源：`D:/AI/SW/output/orphan-capabilities.json`（`tools/probe_unexposed_functions.py` 生成）。
本批取自其中**首参可注入**（`study`）且上批（`batch11`）**明确留批**的三个 ——
上批留批的理由是「**枚举值未核**」；★ **本轮先把枚举核清了再挂**（宪法 §II / §III）：

| 枚举 | 取值（**来自出厂反射** `D:/AI/SW/_raw/reflect/enum_cosworks.txt`）|
|---|---|
| `swsTopologyDemoldDirectionOption_e` | `0=TwoDirectionMidPlane` · `1=PullDirectionOnly` · `2=Stamping` |
| `swsTopologyStudyConstraintComparator_e` | `0=IsLessThan` · `1=IsGreaterThan` · `2=IsInBetween` |
| `swsTopologyPreservedRegionOption_e` | `0=LoadsOnly` · `1=FixturesOnly` · `2=LoadsAndFixtures` · `3=None` |

★ **一处查不到（如实写，不发明）**：
```
对称类型的**枚举名**（如 `swsTopologySymmetryType_e`）在本地转储里**没有** ——
可重跑的命令见 `specs/124-topology-batch2/tasks.md` T-12402（期望该名字为 `False`）。
只查到**官方 VBA 示例** `Create_Topology_Study_Example_VBA.txt` 的用法：
    CWTopoSymmetryControlObj.SelectSymmetryType 0 / 1 / 2
    注释：' Define topology one-half symmetry control
⇒ 所以 `symmetry_type` 的描述里**只声称"取值来自官方示例"，不声称枚举名与逐值语义**。
```

| 取 | 函数（真实签名，`inspect.signature` 取）| 为什么 |
|---|---|---|
| ✅ | `sw_topology.create_demold_control(study, *, direction: int = 0)` | 制造约束：铸造件要能拔模 |
| ✅ | `sw_topology.create_stress_constraint(study, *, value: float, comparator: int = 0)` | 应力约束（拓扑的另一类约束）|
| ✅ | `sw_topology.create_symmetry_control(study, *, symmetry_type: int = 0)` | 对称控制（省算力）|

| 不取 | 理由 |
|---|---|
| 真机验证这 3 个 | ★ **暴露 ≠ 验证** —— 真机链排队列 `135`（B2），本批**不给任何 `verified` 身份** |

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch12.py
# 定位:   「孤立能力暴露」第十二批（Spec Kit `124`）—— 拓扑的「脱模/应力/对称」入口。
# 官方签名依据: 不适用（只做参数搬运）；★ 枚举取值依据见上方表格（反射转储 + 官方 VBA 示例）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH12"]

#: `study_name` 由**解析器**消费（不进目标函数）⇒ alias 映射到 `None` 表示「不传」。
#: ★ 与 `tool_specs_batch1.py` / `batch11.py` **同一个约定**（先例，不另立一套）。
_STUDY_ALIAS = {"study_name": None}

SPECS_BATCH12 = [
    ToolSpec(
        name="solidworks_topology_create_demold_control",
        title="Create Topology Demold Control",
        module="sw_topology", function="create_demold_control",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Create a de-mold (manufacturing) control for a topology study. "
            "The caller must first select the pull-direction face/edge/plane, "
            "then choose the direction option.",
        params=[
            Param("study_name", str, default="",
                  description="Target study; omit to use the active study. "
                              "Consumed by the resolver, NOT passed to the function."),
            Param("direction", int, default=0,
                  description="swsTopologyDemoldDirectionOption_e (from the factory reflection dump): "
                              "0=TwoDirectionMidPlane, 1=PullDirectionOnly, 2=Stamping."),
        ],
    ),
    ToolSpec(
        name="solidworks_topology_create_stress_constraint",
        title="Create Topology Stress Constraint",
        module="sw_topology", function="create_stress_constraint",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Create a stress constraint for a topology study.",
        params=[
            Param("study_name", str, default="",
                  description="Target study; omit to use the active study. "
                              "Consumed by the resolver, NOT passed to the function."),
            Param("value", float,
                  description="Constraint value (stress)."),
            Param("comparator", int, default=0,
                  description="swsTopologyStudyConstraintComparator_e (from the factory reflection "
                              "dump): 0=IsLessThan, 1=IsGreaterThan, 2=IsInBetween."),
        ],
    ),
    ToolSpec(
        name="solidworks_topology_create_symmetry_control",
        title="Create Topology Symmetry Control",
        module="sw_topology", function="create_symmetry_control",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Create a symmetry control for a topology study. The caller must first select the "
            "symmetry plane(s).",
        params=[
            Param("study_name", str, default="",
                  description="Target study; omit to use the active study. "
                              "Consumed by the resolver, NOT passed to the function."),
            Param("symmetry_type", int, default=0,
                  description="⚠ Values 0/1/2 come from the OFFICIAL VBA example "
                              "(`Create_Topology_Study_Example_VBA.txt` uses SelectSymmetryType 0/1/2, "
                              "commented 'Define topology one-half symmetry control'). "
                              "The enum NAME was NOT found in the local reflection dump — so do not "
                              "assume per-value semantics beyond that."),
        ],
    ),
]
