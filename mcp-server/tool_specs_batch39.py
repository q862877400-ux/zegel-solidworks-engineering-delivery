"""第三十九批 MCP 工具声明：**方程 4 + 螺旋 1 + 形位公差 1**（24h 段 5 续 / Spec Kit `156`）。

## ★★★★ 为什么这一批是**填真缺口**（★ 而不是凑数）
```
★ 清点「`mcp_tools` 为空的条目」⇒ ★★ 发现**多个 `verified` 条目根本没有工具**，
  而它们**下游的公开函数一直都在**（★ 且**真机验过**）：
   · `equations`（verified · 0 工具）⇒ ★ 而 `sw_equation` 有 **4 个公开函数**，
     ★★ **`tools/verify_equation_smoke.py` 真机 5/5 pass 过**；
   · `helix_and_spiral`（verified · 0 工具）⇒ `sw_helix.insert_helix` 一个（★ 未单验）；
   · `gtol_insert`（verified · 0 工具）⇒ `sw_gtol.insert_gtol(model)`（**零参**）
     ★ 而 `verify_gtol_smoke.py` 真机 **3/5**（★ `insert_gtol` 那半通过）。
⇒ ★★★ **所以本批 = "把已验过的能力接上工具"** —— ★ `all_specs()` **152 → 158**，
   ★★ 且**三条空条目被填实**（★ 与事实 209 的"空壳条目"同一处置）。
```

## ★ 参数命名（规则 2 / 3）
```
★ `height_mm` / `pitch_mm` 带 `_mm`（★ 规则 2）；★ `revolution` 是**圈数**（★ 不是长度、不是角度）；
★ `index` 是**下标**；★ **无裸坐标** ✓
★ ⚠ `insert_helix` 的完整形参以其源码为准（★ 本批只暴露已确认的）。
```

## 判据
```
★ `add_equation` ⇒ ★ 判「**加进去之后读回来含它**」（★ 读写配对 —— 那是 `verify_equation_smoke.py`
  已经在用的判据：加 `"SMOKE_B" = 2` ⇒ `list_equations` 含它 ⇒ `evaluate_equations` ok）。
★ `list_equations` / `evaluate_equations` / `delete_equation` ⇒ 判"回 list / ok / 删后不含"。
★ `insert_helix` / `insert_gtol` ⇒ 判"不抛异常 **且** 特征树有变化"（★ 规则 6：不静默成功）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch39.py
# 定位:   24h 计划 段 5 续（Spec Kit `156`）—— 填 `equations` / `helix_and_spiral` / `
#           gtol_insert` 三条空条目。
# 官方依据: `IModelDoc2.AddEquation` / `IEquationMgr`（★ 见 `scripts/sw_equation.py`）·
#          `IFeatureManager.InsertHelix`（★ 见 `scripts/sw_helix.py`）·
#          `IModelDoc2.InsertGtol`（★ 见 `scripts/sw_gtol.py`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH39"]


SPECS_BATCH39 = [
    #: ── 方程（★ 空条目 `equations` 的填实）─────────────────────────────
    ToolSpec(
        name="solidworks_equation_add",
        title="Add a Global Equation (read-back verified)",
        module="sw_equation",
        function="add_equation",
        inject="model",
        params=[
            Param(
                "equation",
                str,
                description=(
                    "Equation text as written in the user interface, with dimension names in double quotes, for example"
                    " \"D2@Sketch1\" = 2 * \"D1@Sketch1\"."
                ),
            ),
            Param("index", int, default=-1, description=(
                                                "Zero-based position to insert at, where -1 appends at the end. Default"
                                                "s to -1."
                                            )),
            Param(
                "solve",
                bool,
                default=True,
                description="Whether to solve the equations immediately after adding. Defaults to true.",
            ),
        ],
        evidence=(
            "Add a global equation. ★ Verify by reading the equations back (the criterion the existing smoke uses). ⚠ D"
            "oes NOT save the document."
        ),
        doc=(
            "Add one global equation to the active document. It writes an equation and does not save the document; it t"
            "hrows instead of succeeding silently when the string is empty or the call returns -1, and the index of the"
            " new equation comes back in the report."
        ),
    ),
    ToolSpec(
        name="solidworks_equation_list",
        title="List the Global Equations (and their values)",
        module="sw_equation",
        function="list_equations",
        inject="model",
        params=[],
        evidence=(
            "Return the document's global equations as a list. ★ Read-only."
        ),
        doc=(
            "List every global equation in the active document. Read-only; it reads the equation count and then each eq"
            "uation by index, and it changes nothing in the model."
        ),
    ),
    ToolSpec(
        name="solidworks_equation_evaluate",
        title="Evaluate (Solve) the Global Equations",
        module="sw_equation",
        function="evaluate_equations",
        inject="model",
        params=[],
        evidence=(
            "Solve the global equations and return the result. ⚠ Does NOT save the document."
        ),
        doc=(
            "Solve all global equations and return the result. It re-evaluates the equations in the active document and"
            " does not save it; use solidworks_equation_list when you only need the equation text."
        ),
    ),
    ToolSpec(
        name="solidworks_equation_delete",
        title="Delete a Global Equation by Index",
        module="sw_equation",
        function="delete_equation",
        inject="model",
        params=[
            Param(
                "index",
                int,
                description="Zero-based index of the equation to delete, as listed by solidworks_equation_list.",
            )
        ],
        evidence=(
            "Delete one global equation by index. ⚠ Does NOT save the document."
        ),
        doc=(
            "Delete one global equation by its zero-based index. It writes the deletion into the active document and do"
            "es not save it; read solidworks_equation_list first so the index points at the equation you mean."
        ),
    ),
    #: ── 螺旋（★ 空条目 `helix_and_spiral` 的填实）───────────────────────
    ToolSpec(
        name="solidworks_helix_insert",
        title="Insert a Helix / Spiral",
        module="sw_helix",
        function="insert_helix",
        inject="model",
        params=[
            Param("height_mm", float, description=(
                                          "Helix height in millimetres; the API takes metres, so it is converted here."
                                      )),
            Param(
                "pitch_mm",
                float,
                default=0.0,
                description="Pitch in millimetres; 0 leaves it to the document default. Defaults to 0.",
            ),
            Param(
                "revolution",
                float,
                default=0.0,
                description="Number of revolutions; 0 leaves it to the document default. Defaults to 0.",
            ),
        ],
        evidence=(
            "Insert a helix/spiral. ★ Needs the document state the official API requires (a circular sketch to revolve "
            "about) — the capability layer reports it if not."
        ),
        doc=(
            "Insert a fixed-pitch helix or spiral as a curve feature. It writes the feature and does not save the docum"
            "ent; it throws when the call returns nothing, which usually means the defining circle was not selected bef"
            "ore calling."
        ),
    ),
    #: ── 形位公差（★ 空条目 `gtol_insert` 的填实）────────────────────────
    ToolSpec(
        name="solidworks_gtol_insert",
        title="Insert a GTol Annotation (gets the object back)",
        module="sw_gtol",
        function="insert_gtol",
        inject="model",
        params=[],
        evidence=(
            "Insert a GTol annotation (★ zero-argument: IModelDoc2.InsertGtol()). ★ The criterion is that it returns an"
            " object and the feature tree changes. ⚠ Does NOT save the document."
        ),
        doc=(
            "Insert an empty geometric tolerance symbol. It writes an annotation and does not save the document; the le"
            "ader attaches to whatever is selected before the call, and with no selection the symbol sits at the origin"
            " without a leader."
        ),
    ),
]
