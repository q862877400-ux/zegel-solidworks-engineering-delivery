"""第十四批 MCP 工具声明：**视图读取 / 体上实体枚举** 2 个。

## 来源与筛选（2026-10-01 轮 207，Spec Kit `126`）

候选源：`D:/AI/SW/output/orphan-capabilities.json`（`tools/probe_unexposed_functions.py` 生成）。
队列 A3 原本列了 4 个（`get_active_view` / `activate_view` / `add_perspective` / `entities_on_body`），
★ **实测后只挂 2 个** —— 另外 2 个的**首参不是约定注入点**：

| 函数 | 真实签名（`inspect.signature`）| 首参 | 本批 |
|---|---|---|---|
| `sw_view.get_active_view` | `(model)` | `model` ✓ | **挂** |
| `sw_selection_spec.entities_on_body` | `(model, kind: str, *, body_index: int = 0)` | `model` ✓ | **挂** |
| `sw_view.activate_view` | `(view) -> bool` | ★ `view` **不在** `model`/`sw_app`/`study` 里 | **不挂** |
| `sw_view.add_perspective` | `(view) -> bool` | ★ 同上 | **不挂** |

## ⚠ 为什么另 2 个不挂（**记录理由，不硬挂**）
```
`activate_view` / `add_perspective` 要的是 **`IView` 对象**（`IModelDoc.ActiveView`），
而既有注入器只有 `""` / `"model"` / `"sw_app"` / `"study"` 四个 —— **没有 `view`**。
★ 而且实测：**既有 `tool_specs_batch*.py` 里没有任何"靠 model 取 view"的先例**可照抄。
⇒ 处置：**本批不挂**，把它记进队列 A10（"找第二类可挂形态"）——
   要么加一个 `view` 注入器（改基础设施），要么写"`model` → `ActiveView` → 调用"的**包装层**。
   ★ 两条路都要**先定行为**（`ActiveView` 在无活动文档/无视图时返回什么），不在本批顺手做。
```

| 不取 | 理由 |
|---|---|
| 真机验证这 2 个 | ★ **暴露 ≠ 验证** —— 排队列 B 组 |

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch14.py
# 定位:   「孤立能力暴露」第十四批（Spec Kit `126`）—— 视图读取 + 体上实体枚举。
# 官方签名依据: 不适用（只做参数搬运）；`kind` 的合法值取自 `sw_selection_spec.ENTITY_KINDS`（**本项目自己的常量**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH14"]

SPECS_BATCH14 = [
    ToolSpec(
        name="solidworks_get_active_view",
        title="Get Active View",
        module="sw_view",
        function="get_active_view",
        inject="model",
        evidence=(
            "Get the currently active 3D view (the official member is IModelDoc.ActiveView)."
        ),
        doc=(
            "Get the currently active three-dimensional model view. Read-only; it reads the view of the active document"
            " and changes nothing, so it is the handle that later view operations address."
        ),
        params=[],
    ),
    ToolSpec(
        name="solidworks_entities_on_body",
        title="List Entities On Body (with geometry)",
        #: ★★ 2026-10-06（规格 209 · B3-1 · idx 115+145）：**指向改成 `entities_report`*
        #: * ——
        #: ★ 裁决书强制「**扩已有的 `solidworks_entities_on_body`**，**不许开平行工具**
        #: 」✓
        #:   ★★ 而改指向的**理由是可核的**：`entities_on_body` **返回 COM 对象** ⇒
        #: **过不了 MCP 的 JSON 边界** ⇒ 那条工具**经工具层其实拿不到东西**（★ 名字没变
        #: 、能力变了）✓
        module="sw_selection_spec",
        function="entities_report",
        inject="model",
        evidence=(
            "List the entities of one body **with geometry** (kind EDGE, FACE, or VERTEX). ★ 每条带可 JSON 化的读数：ED"
            "GE ⇒ 两个端点 + **自己算的**边长（★ 官方 `IEdge` **没有**长度成员）· FACE ⇒ `IFace2.GetArea()` · VERTEX ⇒ "
            "`IVertex.GetPoint()`。★★ 同时回 **欧拉校验 `V−E+F=2`**（★ 本仓既有判据，不需新 API）✓ ⚠ Index order is NOT"
            " promised stable by the official API — do not treat body_index as a persistent reference across rebuilds. "
            "★ 别名: body, edge, edges, entit, vertex, vertices"
        ),
        doc=(
            "List the edges, faces or vertices of one solid body with their geometry readings. Read-only. An edge repor"
            "ts its two end points and a computed length, a face reports its area, a vertex reports its point, and the "
            "reply also carries the V minus E plus F check. The index order is not promised stable, so never use it as "
            "a reference across rebuilds."
        ),
        params=[
            Param(
                "kind",
                str,
                description="Entity kind to list: EDGE, FACE or VERTEX.",
            ),
            Param(
                "body_index",
                int,
                default=0,
                description=(
                    "Zero-based index of the solid body, not a persistent reference across rebuilds. Defaults to 0."
                ),
            ),
        ],
    ),
]
