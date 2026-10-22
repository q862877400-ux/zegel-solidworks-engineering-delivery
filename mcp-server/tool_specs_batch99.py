"""★ 批次 99：规格 209 · B4-1 —— 原生宏录制（`RecordLine` + `RunCommand(29)`，★ 永不点 31）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_macro.py`（本轮追加段）
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-1** · 外部项目 idx **211
#   `native_macro_recording`** —— 裁决书：正解是 `RecordLine` + `RunCommand` +
#   `DSldWorksEvents::BeginRecordNotify`/`EndRecordNotify` ✓
#   ★★★ 裁决书点名的**头号风险**：`swCommands_StopMacro`(31) **逐字会弹 Save As 对话框**
#     ⇒ ★★ 本工具**永不调用 31**，改用 `swCommands_RecordPauseMacro`(29) 这个**切换**成对开关 ✓
# 官方依据: `C:\\swapi\\types\\ISldWorks\\RecordLine.md`（★ `## Remarks` 逐字给两个硬事
#           实）·
#   `C:\\swapi\\types\\ISldWorks\\RunCommand.md` · `C:\\swapi\\enums\\swCommands_e.md`
#   （`RecordPauseMacro=29` · `StopMacro=31; **opens the Save As dialog**`）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 447 → **448**
# ★★ **诚实边界**：★ 真机只到「**成对调用可达 + 逐行回 True**」，
#   而 ★★ **`RecordLine` 在「未开录制」时也回 `True`** ⇒ ★ **返回值证明不了「写进去了」**；
#   ★ 要真证得**落盘的宏文件**，那要 `StopMacro` 的 Save As ⇒ **本工具不去点** ⇒ 标 **`stitched`** ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH99"]

SPECS_BATCH99 = [
    ToolSpec(
        name="solidworks_macro_record_lines",
        title="Record VBA Lines Natively (RecordLine + RunCommand RecordPauseMacro)",
        module="sw_macro", function="record_macro_lines",
        inject="sw_app",
        params=[
            Param("lines", str, default="",
                  description="要写进宏的代码行 —— ★ 收**换行分隔的字符串**"
                              "（★ 用 `\\n` 分隔；★ 空行会被丢掉）。"),
        ],
        doc="★ **原生宏录制**（官方 `ISldWorks::RecordLine` + `ISldWorks::RunCommand`）—— "
            "★★ **状态：`stitched`** ★ 真机走到「**成对调用可达**」这一级，"
            "而★ **「写进去了没有」证不了** ✓ "
            "★★★ **判据为什么不能是返回值（真机实测的硬证据）**：官方 `RecordLine` 的 "
            "`## Remarks` 逐字说「Text is **only written to macros if macro recording is enabled**」"
            "⇒ 可**真机读数相反**：★ **「未开录制」时 `RecordLine` 也回 `True`** "
            "⇒ ★★ **那个 bool 证明不了任何事**；★ 本工具因此把「开录制 / 逐行 / 停录制」"
            "**三个 bool 全部回报**、并**明写限度** ✓ "
            "★★★ **本工具永不调用 `swCommands_StopMacro`(31)**：官方枚举页**逐字**标注它"
            "「**opens the Save As dialog**」⇒ ★★ 无头/无人值守下点它会**弹模态框**"
            "（本仓头号死因）⇒ ★ 停录制改用 `swCommands_RecordPauseMacro`(29) 这个**切换**"
            "（★ 官方 `RecordLine` 的 Remarks 也正是这样用的）✓ "
            "★ 代价（如实记）：★ **「录下来写进哪个文件」就证不了** —— 那正是 31 的那一步 ✓ "
            "★★ **前置**：★ `RecordPauseMacro` **是切换、不是置位**（官方枚举逐字 "
            "「Record\\Pause Macro」）⇒ ★ 本工具**成对**做完（开 → 写 → 停），"
            "★ 并在 `finally` 里保证**录制一定被停掉**（★ 不给用户留「一直在录」的脏状态）✓",
    ),
]
