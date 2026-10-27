"""第四十二批 MCP 工具声明：**工程图读数 2 个**（24h 段 6 续 / Spec Kit `159`）。

## ★★★ 为什么挂这 2 个
```
★ 轮 284 拆 `drawing_current_sheet_query` 时，想给新条目
  `drawing_views_and_summary` 认领 3 个工具（`list_views` / `sheets_summary` / `current_sheet_info`）
  ⇒ ★★ **核名字时发现后两个**不在仓库的工具名里****
  ⇒ ★★★ **而它们的函数一直都在**（`scripts/sw_drawing_query.py`，★ 与 `list_views` 同模块）
    ⇒ ★ **所以那是**「函数在、工具没挂」** —— ★ 与本会话主线（事实 210）**同一类型**
⇒ ★ `all_specs()` **173 → 175**，★ 而 `drawing_views_and_summary` 因此**有 3 个工具**（★ 不是 1 个）。
```

## ★ 判据
```
★ 两个都是**读数** ⇒ 判「回 dict 且非空」；★ `require_drawing` 的那类守卫由能力层在内部做
  （★ 非工程图文档会如实报，★ 不静默回空 dict）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch42.py
# 定位:   24h 计划 段 6 续（Spec Kit `159`）—— 工程图读数 2 个（补上漂在外面的函数）。
# 官方依据: `IDrawingDoc` 的 GetViews / GetSheetNames / IView 族（★ 见 `scripts/sw_drawi
#           ng_query.py`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**只读、不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import ToolSpec

__all__ = ["SPECS_BATCH42"]


SPECS_BATCH42 = [
    ToolSpec(
        name="solidworks_drawing_sheets_summary",
        title="Summarise Every Drawing Sheet",
        module="sw_drawing_query",
        function="sheets_summary",
        inject="model",
        params=[],
        evidence=(
            "Return a per-sheet summary dict for the active drawing (★ 页名 / 视图数 等). ★ Read-only."
        ),
        doc=(
            "Return a per-sheet summary of the active drawing, including sheet names and view counts. Read-only; it ans"
            "wers several sheet questions in one call so the caller does not need two round trips."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_current_sheet_info",
        title="Get the Current Drawing Sheet's Info",
        module="sw_drawing_query",
        function="current_sheet_info",
        inject="model",
        params=[],
        evidence=(
            "Return info about the sheet currently being edited as a dict. ★ Read-only."
        ),
        doc=(
            "Return information about the sheet currently being edited as a dict. Read-only; use it when only the curre"
            "nt sheet matters, and solidworks_drawing_list_sheets when every sheet is wanted."
        ),
    ),
]
