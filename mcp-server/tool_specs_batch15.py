"""第十五批 MCP 工具声明：**结构化审查报告** 1 个。

## 来源与筛选（2026-10-01 轮 208，Spec Kit `127`）

候选源：`D:/AI/SW/output/orphan-capabilities.json`（`tools/probe_unexposed_functions.py` 生成）。
队列 A4 原列 2 个，★ **实测后只挂 1 个**：

| 函数 | 真实签名（`inspect.signature`）| 首参 | 本批 |
|---|---|---|---|
| `sw_review.build_review_report` | `(model, output_dir, basename='review', views=None, expected_outputs=None)` | `model` ✓ | **挂**（但只暴露前 3 个参数）|
| `sw_simulation_results.activate_plot` | `(results, plot_name: str) -> bool` | ★ `results`（`ICWResults`）| **不挂** |

## ⚠ 两处"不硬挂"，各自的理由（**记录，不猜**）
```
① `activate_plot` 的首参是 **`results`（ICWResults）** —— 不在约定注入点里
   （约定四个：`""` / `model` / `sw_app` / `study`）⇒ ★ 与 `batch14` 的 `view` **同型**：
     要么加 `results` 注入器，要么写"`study` → `Results` → `activate_plot`"的**包装层**。
   ⇒ 记进队列 A10（先定"结果不存在时返回什么"，再动手）。

② 本批**只暴露** `output_dir` / `basename` 两个参数，**不暴露** `views` / `expected_outputs` ——
   因为它们是 **`list` 型**，而实测：`tool_specs_batch*.py` 里**没有任何 `list` 型 `Param` 的先例**
   （核查命令见 `specs/127-review-report-batch/tasks.md` T-12702）。
   ⇒ ★ **无先例的东西不顺手引入**：那两个是**可选参数（默认 `None`）**，
     不暴露**不影响**这个工具的主要用途（生成报告 + 落预览图）。
   ⇒ 记进队列 A10：若要暴露，先决定"list 怎么过 MCP 边界"（逗号串？JSON 串？），**并留下先例**。
```

| 不取 | 理由 |
|---|---|
| 真机验证这个工具 | ★ **暴露 ≠ 验证** —— 排队列 B 组 |

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch15.py
# 定位:   「孤立能力暴露」第十五批（Spec Kit `127`）—— 结构化审查报告。
# 官方签名依据: 不适用（只做参数搬运）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH15"]

SPECS_BATCH15 = [
    ToolSpec(
        name="solidworks_build_review_report",
        title="Build Review Report",
        module="sw_review",
        function="build_review_report",
        inject="model",
        evidence=(
            "Build structured review-report data (exports preview images and writes a report into output_dir). ⚠ The op"
            "tional `views` / `expected_outputs` list parameters are NOT exposed in this tool — see the batch header fo"
            "r why."
        ),
        doc=(
            "Build structured review-report data, export preview images and write a report into output_dir. It writes f"
            "iles and does not save the document; the optional view list and expected-output list are not exposed here,"
            " so the tool uses its own fixed defaults."
        ),
        params=[
            Param(
                "output_dir",
                str,
                description="Directory that receives the preview images and the report file.",
            ),
            Param(
                "basename", str, default="review", description="Filename prefix for the outputs. Defaults to review."
            ),
        ],
    ),
]
