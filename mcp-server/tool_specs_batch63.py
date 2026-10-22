
# ── 200 轮计划 v3 · 段 5（该挂清理）：**按声明式选择器选面** ──────────────────────────
# ★★★★★ 2026-10-03（轮 452）★ 来源：**规则 3 的判断** + 真机证据 `output/face-selector-e
# vidence.json`（**PASS**）。
#
# ★★ **为什么这一条能做，而它旁边两条不能**（★ 那是**规则 3** 的边界，★ 而不是"难不难"）
# ：
#   ```
#   ★ `select_object(model, obj)`          ⇒ 吃 **COM 对象** ⇒ ★ **没法人参数表达** ⇒ 不做
# ★ `resolve_face_selector(model, sel)`  ⇒ 回 **`(x, y, z)` 米** ⇒ ★★ **暴露它就是暴露裸
# 坐标** ⇒ 不做
#   ★★ `select_face_by_selector(model, selection: str)` ⇒ ★ **对外的参数是**选择器****，
#      ★ 而坐标**只在内部用** ⇒ ★★ **完全符合规则 3** ⇒ **做** ✓✓✓
#   ```
# ★ 真机判据（★ 三条，★ 全过）：
#   ```
#   ① ★ 合法选择器单次调用 ⇒ 回读计数 **== 1**
#   ② ★ **六个**选择器（`+x -x +y -y +z -z`）**各都是 1**
#   ③ ★ 非法选择器 ⇒ **抛** `ValueError`（★ 而**不是**静默回 0；★ 错误信息里列出合法值）
#   ```
# ⚠★ **而真机顺带发现一条行为**：★ `append=False` 时**它并没清掉上一次的选区**（★ 回读 1
#  → **2**）——
#   ★★ 故**调用方要自己先 `ClearSelection2`**；★ 已写进工具文档与包装的 docstring ✓
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch63.py —— 本文件
# 定位:   把 `select_face_by_selector_report` 挂成 MCP 工具（★ 段 5 该挂清理的一件）。
# 官方依据: `IModelDocExtension.SelectByID2("", "FACE", x, y, z, …)`（★ 按**面上的点**定
#           位 —— 事实 32）·
# 本仓 `scripts/sw_simulation.py` 的 `select_face_by_selector` / `resolve_face_selector`
#  / `select_face_at` ·
#   `FACE_SELECTORS = ('+x', '-x', '+y', '-y', '+z', '-z')`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH63"]

_SEL = ("Declarative face selector — ★ one of `+x` / `-x` / `+y` / `-y` / `+z` / `-z`"
        "（★ 它指**面朝的那个方向**，例如 `+z` 是朝上的那个面）。"
        "⚠★ 非法值会**抛**（★ 而**不是**静默不选），★ 错误信息里会列出合法值。")

SPECS_BATCH63 = [
    ToolSpec(
        name="solidworks_select_face_selector",
        title="Select a Face by Declarative Selector",
        module="sw_simulation", function="select_face_by_selector_report",
        inject="model",
        params=[
            Param("selection", str, description=_SEL),
            Param("mark", int, default=0,
                  description="★ 选择标记（★ 多引用特征读 mark 0/1/2 —— 规则 3 的第三句）"),
            Param("append", bool, default=False,
                  description="★ 传给底层的 `Append`。⚠★ **真机：`append=False` 时它并没清掉上一次的选区**"
                              "（★ 回读 1 → 2）⇒ ★★ **要换一个面就自己先 `ClearSelection2`**"),
        ],
        doc=("Select ONE face by a **declarative selector** and return a READ-BACK report. "
             "★★ 这是「**按面上的点定位**」那条路（★ 事实 32：`SelectByID2` 对边/面**按名字不可行**，"
             "而**按点可行**）—— ★ 而本工具把它包成**声明式**（★ 规则 3）。"
             "★ `ok` 的判据是**回读计数 == 1**（★ **不是**返回值 —— 事实 8）。"
             "★★ **不接受裸坐标**：★ 坐标在能力层内部算，★ 对外的参数**只有选择器**。"),
    ),
]
