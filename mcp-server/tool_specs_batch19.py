"""第十九批 MCP 工具声明：**当前活动工程图的轻量只读读数** 3 个（砌墙 W2）。

## ★★ 本批的由来：⑪工程图那 49 个"缺口"逐个核过之后，**只读那一类已经被覆盖**
```
① **名字差异（已覆盖）**：`drawing_views` / `drawing_dimensions` / `drawing_annotations` /
   `drawing_tables` / `sheets` / `analyze_drawing_*` … ⇒ `solidworks_inspect_drawing` **已经覆盖**
   （其实现的内核正是 `drawing_workflow.inspect_drawing_structure`）。
② **写操作**（加视图 / 标注 / 表格 / BOM）：本阶段不做。
③ ★ **真缺的一小批**（本批）：`solidworks_inspect_drawing` 要 **`drawing_path`**、
   **自己开件 + 出三视图预览 + 往 output_dir 落一份 JSON** ⇒
   ★ **对"当前已经打开的那张图纸"没有轻量读数**。
   而 AI 的常见需求恰恰是：「这图几张纸？当前图幅多大？有几个视图？」
   —— 不需要出预览、不需要落文件、不需要知道路径。
```
（缺口名是**名字级**匹配 —— `build_union_map` 的 `_normalize` 机制 ⇒ 「名字不同」会被算成「缺口」。
 ★ 所以不照着缺口数字排活，否则会把已经做过的事再做一遍。）

## ★★★ 三个关键事实由**真机探针**定（`tools/probe_drawing_object_routes.py`，轮 224）
```
  model.GetType()            **3**（swDocDRAWING；零件 1）
  model.GetCurrentSheet()    ★ **能直接调** —— pywin32 迟到绑定下 model 本身就是 IDrawingDoc
  ISheet.GetProperties2()    ★ **8 个 double**（官方 GetProperties 文档写 7，后继多一个）
                              实测 [6.0, 12.0, 1.0, 1.0, 1.0, 0.297, 0.21, 1.0]
                              ⇒ paperSize=6 = swDwgPaperA4size（swapi 与反射两源一致）
                              ⇒ 宽高**单位是米** ⇒ 本批对外回**毫米**（规则 2）
  GetFirstView()             ★ **空图纸上返回"图纸本身"（Type == 1）**，不是 None
                              ⇒ ★ 列视图时必须排除它，否则会列出名叫「图纸1」的**假视图**
```
★ 官方示例依据：`C:\\swapi\\examples\\Get_Drawing_View_Names_and_Types_Example_CSharp.md`
  （`swDraw = (DrawingDoc)swModel; swSheet = swDraw.GetCurrentSheet(); swView = swDraw.GetFirstView();`
   `while (swView != null) { swView.GetName2(); swView.Type; swView = swView.GetNextView(); }`）

## 参数
| 参数 | 说明 |
|---|---|
| 无 | ★ 本批**全部针对"当前活动文档"** —— 这正是它与 `solidworks_inspect_drawing` 的分工 |

★ 因此 `inject` 用默认的 `"model"`（目标函数首参就是 `model`），**不需要 `derived_args`**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch19.py
# 定位:   「孤立能力暴露」第十九批 / 砌墙 W2（Spec Kit `132`）。
# 官方签名依据: 不适用（只做参数搬运）；取对象的依据是真机探针
#          `tools/probe_drawing_object_routes.py` + 官方示例（见上）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH19"]


#: 本批三个工具**共用**的说明（它们都只作用于"当前活动文档"）
_CURRENT_ONLY = ("★ Works on the CURRENTLY ACTIVE document only — no path needed. "
                 "This is the difference from solidworks_inspect_drawing, which takes a "
                 "drawing_path, opens the file itself and writes previews + a report. "
                 "Raises if the active document is not a drawing (GetType() != 3).")


SPECS_BATCH19 = [
    ToolSpec(
        name="solidworks_drawing_list_sheets",
        title="List Drawing Sheets",
        module="sw_drawing_query", function="sheets_summary",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0 个实参 ⇒
        #:   `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidworks_part_bounding_box` 写着 `inject='model'` ✓
        params=[],
        doc="Sheet overview of the active drawing: how many sheets, their names, and which one is "
            "current. " + _CURRENT_ONLY,
    ),
    ToolSpec(
        name="solidworks_drawing_get_current_sheet",
        title="Get Current Drawing Sheet",
        module="sw_drawing_query", function="current_sheet_info",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0 个实参 ⇒
        #:   `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidworks_part_bounding_box` 写着 `inject='model'` ✓
        params=[],
        doc="Read the current sheet: paper size (name + code), WIDTH/HEIGHT IN MILLIMETRES, scale, "
            "projection angle and sheet-format name. ⚠ The API returns width/height in METRES; this "
            "tool converts once, at the boundary, and reports millimetres. " + _CURRENT_ONLY,
    ),
    ToolSpec(
        name="solidworks_drawing_list_views",
        title="List Drawing Views",
        module="sw_drawing_query", function="list_views",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0 个实参 ⇒
        #:   `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidworks_part_bounding_box` 写着 `inject='model'` ✓
        params=[],
        doc="List the views on the CURRENT SHEET: name + type code. ⚠ The sheet itself is NOT "
            "reported as a view — the raw API returns it as a pseudo-view (Type == 1) and that is "
            "filtered out here. " + _CURRENT_ONLY,
    ),
]
