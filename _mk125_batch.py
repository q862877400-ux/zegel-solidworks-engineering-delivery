import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ══════════════ ① batch13（实现） ══════════════
BATCH = '''"""第十三批 MCP 工具声明：**仿真研究的「报告 / 按控制划网格 / 建议网格尺寸」** 3 个。

## 来源与筛选（2026-10-01 轮 206，Spec Kit `125`）

候选源：`D:/AI/SW/output/orphan-capabilities.json`（`tools/probe_unexposed_functions.py` 生成）。
取自其中**首参可注入**（`study`）的仿真族 3 个。

| 取 | 函数（真实签名，`inspect.signature` 取）| 归属模块 |
|---|---|---|
| ✅ | `generate_report(study, template: str, path: str, append: bool = False) -> int` | `sw_simulation_study` |
| ✅ | `create_mesh_for_control(study, control_name: str) -> int` | `sw_simulation_study` |
| ✅ | `default_element_size_and_tolerance(study, units: int = -1) -> tuple[float, float]` | ★ `sw_simulation`（**不是** `_study`）|

★ **归属按实测改正**：队列里我把它写在 `_study` 名下，实测它在 `scripts/sw_simulation.py` ⇒ **以实测为准**。

## ⚠⚠ 一处**两源冲突**，如实写进描述（宪法 §II / §III）
```
既有工具 `solidworks_topology_run` 的 `units` 描述写：
    "swsUnit_e: 0=SI, 1=English, 2=Metric. Must be a VALID value (**-1 is rejected by the API**)."
而 `default_element_size_and_tolerance` 自己的 docstring 写：
    "取官方的**建议**单元尺寸与容差（**本机实测：`units=-1` 时返回毫米级数值**）"
⇒ ★ **两处矛盾**：一个说 -1 被拒，一个说 -1 实测可用。
★ 处置：**本批按该函数自己的真机实测**用默认 `-1`，并把**冲突本身写进参数描述** ——
  两个都保留、各自标注来源，**不合并成一个说法**（与事实 139 的"两个口径不合并"同型）。
```

## ⚠ 一处**查不到**（§III）
```
`generate_report` 的 `template` **合法取值**在本地源里**没查到** ——
`sw_simulation_study.generate_report` 的 docstring 只有一句「生成研究报告。」，
函数体只是把参数透传给 `GenerateReport(template, path, append)`。
⇒ ★ 所以 `template` 按**普通字符串**暴露，描述里**明写"合法取值未查到"**，不发明候选值。
   核查命令见 `specs/125-simulation-study-batch/spec.md`。
```

| 不取 | 理由 |
|---|---|
| 真机验证这 3 个 | ★ **暴露 ≠ 验证** —— 真机验证排队列 B 组 |

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch13.py
# 定位:   「孤立能力暴露」第十三批（Spec Kit `125`）—— 仿真研究的报告/网格入口。
# 官方签名依据: 不适用（只做参数搬运）；★ `units` 依据见上方冲突说明
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH13"]

#: `study_name` 由**解析器**消费（不进目标函数）⇒ alias 映射到 `None` 表示「不传」。
#: ★ 与 `batch1` / `batch11` / `batch12` **同一个约定**（先例，不另立一套）。
_STUDY_ALIAS = {"study_name": None}

SPECS_BATCH13 = [
    ToolSpec(
        name="solidworks_simulation_generate_report",
        title="Generate Simulation Study Report",
        module="sw_simulation_study", function="generate_report",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Generate a study report to a file. ⚠ `template` valid values were NOT found in the "
            "local sources (see the batch header); pass the template name your SolidWorks "
            "installation provides.",
        params=[
            Param("study_name", str, default="",
                  description="Target study; omit to use the active study. "
                              "Consumed by the resolver, NOT passed to the function."),
            Param("template", str,
                  description="Report template name. ⚠ Valid values not found in local sources."),
            Param("path", str,
                  description="Output file path for the generated report."),
            Param("append", bool, default=False,
                  description="Append to an existing report instead of replacing it."),
        ],
    ),
    ToolSpec(
        name="solidworks_simulation_create_mesh_for_control",
        title="Create Simulation Mesh For Mesh Control",
        module="sw_simulation_study", function="create_mesh_for_control",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Mesh the study using a named mesh control.",
        params=[
            Param("study_name", str, default="",
                  description="Target study; omit to use the active study. "
                              "Consumed by the resolver, NOT passed to the function."),
            Param("control_name", str,
                  description="Name of the mesh control to mesh with."),
        ],
    ),
    ToolSpec(
        name="solidworks_simulation_default_element_size_and_tolerance",
        title="Get Simulation Default Element Size And Tolerance",
        module="sw_simulation", function="default_element_size_and_tolerance",
        inject="study",
        param_alias=dict(_STUDY_ALIAS),
        doc="Get the suggested element size and tolerance (millimetre-scale when units=-1).",
        params=[
            Param("study_name", str, default="",
                  description="Target study; omit to use the active study. "
                              "Consumed by the resolver, NOT passed to the function."),
            Param("units", int, default=-1,
                  description="swsUnit_e. ⚠ TWO LOCAL SOURCES DISAGREE: the existing "
                              "`solidworks_topology_run` tool says \\"0=SI, 1=English, 2=Metric; "
                              "-1 is rejected by the API\\", while this function's own docstring "
                              "records a REAL-MACHINE result that `units=-1` returns "
                              "millimetre-scale values. This tool keeps the -1 default (per the "
                              "real-machine note) and does not merge the two statements."),
        ],
    ),
]
'''
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch13.py")
P.write_text(BATCH, encoding="utf-8")
print("  ok batch13 已写")
