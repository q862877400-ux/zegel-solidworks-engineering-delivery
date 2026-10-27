"""第四十三批 MCP 工具声明：**工程图视图 4 个**（24h 段 6 续 / Spec Kit `160`）。

## ★★★★ 为什么这一批是**真有内容**的补口（★ 而它同时让能力数回到 75）
```
★ 清点发现：`sw_drawing_view` 有 **12 个公开函数**，★ **而工具层一个都没挂**（`caps=[]`）
  ⇒ ★★ 那是**一个完整的、独立的能力**（工程图视图：取视图 / 名字 / 比例 / 注释数 / 可见件数 / 设比例）
  ⇒ ★★★ **与 `equations` 同型**：「**函数一直在、工具没挂**」（事实 210 的那一类）
★ 而它的 12 个函数**全部吃一个 `view` 对象** ⇒ ★ 工具层给不了
  ⇒ ★★★ **正解 = 注入 `model` + 包装内部往下取 view**（★ **本会话第四次**同法）
    ★ 入口链：`model` → `get_first_view(drawing)` → `get_next_view(view)` → 逐个读
⇒ ★ 批：**4 个工具** + **新能力 `drawing_view_operations`** ⇒ ★ 能力 **74 → 75** ✓
```

## ★ 参数命名（规则 2 / 3）
```
★ `scale` 是**比例**（★ 不是长度、不是角度）⇒ 不带后缀 ✓
★ `view_name` 是**视图名**（★ 合法值由 `solidworks_drawing_list_views` 给出）
★ **无裸坐标** ✓ · ★ 不涉及的 mark 分配（★ 不选实体）
```

## 判据
```
★ `list_views` / `collect_view_evidence` ⇒ 判"回 dict 且 `count > 0`"；
★ `get_view_scale` ⇒ ★ **按名查找失败时**列出合法值**（事实 204 的形态）；
★ `set_view_scale` ⇒ ★★ **判"回读值真的变了"**（★ 而不是"没报错"）—— ★ 规则 6 的精神。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch43.py
# 定位:   24h 计划 段 6 续（Spec Kit `160`）—— 工程图视图 4 个（★ 补上此前完全没挂的那
#           一族）。
# 官方依据: `IView` 族（★ `Name` / `ScaleDecimal` / `GetAnnotationCount` /
#          `GetVisibleComponentCount` / `SetScale`）—— ★ 见 `scripts/sw_drawing_view.py`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH43"]


SPECS_BATCH43 = [
    ToolSpec(
        name="solidworks_drawing_view_scale",
        title="Get a Drawing View's Scale (by name)",
        module="sw_drawing_view",
        function="get_view_scale_report",
        inject="model",
        params=[
            Param(
                "view_name",
                str,
                description="Name of the drawing view, as listed by solidworks_drawing_list_views.",
            )
        ],
        evidence=(
            "Get one view's scale by name. ★ An unknown name fails with the list of valid names. ★ Read-only."
        ),
        doc=(
            "Get the scale of one drawing view by its name. Read-only. An unknown name fails and lists the valid view n"
            "ames, so a failed call still tells you what to pass next."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_view_set_scale",
        title="Set a Drawing View's Scale (read-back verified)",
        module="sw_drawing_view",
        function="set_view_scale_report",
        inject="model",
        params=[
            Param(
                "view_name",
                str,
                description="Name of the drawing view, as listed by solidworks_drawing_list_views.",
            ),
            Param(
                "scale",
                float,
                description="New view scale, which is neither a length nor an angle.",
            ),
        ],
        evidence=(
            "Set one view's scale and return before/after. ★ The criterion is that the READ-BACK scale actually changed"
            " (rule 6 — never a silent success). ⚠ Does NOT save the document."
        ),
        doc=(
            "Set the scale of one drawing view and return the scale before and after. Modifies the view scale and does "
            "not save the document. The criterion is that the read-back scale really changed, so a returned call is not"
            " proof on its own."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_collect_view_evidence",
        title="Collect Every Drawing View's Evidence",
        module="sw_drawing_view",
        function="collect_view_evidence_report",
        inject="model",
        params=[],
        evidence=(
            "Collect the capability layer's per-view evidence for every view on the drawing. ★ Read-only."
        ),
        doc=(
            "Collect the per-view evidence that the capability layer records for every view on the drawing. Read-only, "
            "so it reports what each view holds and changes nothing."
        ),
    ),
]
