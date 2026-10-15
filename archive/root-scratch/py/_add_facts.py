import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① known-facts 加两条
P = Path(r"C:\swprojects\sw-skill-fork\docs\known-facts.md")
t = P.read_text(encoding="utf-8")
add = """

| # | 事实 | 依据 |
|---|---|---|
| 64 | **`ISldWorks.CommandInProgress = True` 不能抑制某些模态框** —— 2026-10-01 实测：在**空零件**上调 `sw_mold.insert_parting_surface` / `insert_core_cavity_solids` ⇒ 弹出**模态框**「**此拔模方向尚未定义。**」并**卡住会话**（用户截图报错两次）。⚠ 该框**不是** `CommandInProgress` 能压住的那类。⇒ **调「需要前置几何」的建模工具前必须先确认前置条件已满足**；光设 `CommandInProgress` 不够。★ 处置：`tools/verify_batch9_smoke.py` 改为**前置条件感知**（那两个**一个都不调**，只记录前置条件）。 | `tools/verify_batch9_smoke.py` 的来源块与其 `preconditions` 输出 |
| 65 | **改「视图/选择状态」的工具会把文档标脏** —— 2026-10-01 实测：批次 7 的 `activate_model_for_preview` / `clear_selection_for_preview` / `refresh_scene_graph` 在装配体上跑过后，主窗口标题变成 `mcp_avi_asm.SLDASM *`（**未保存标记**）。⚠ 它们**不碰几何**，但仍让文档 `IsDirty`。⇒ **这类工具的 doc 必须警告**，且**冒烟脚本不许在用户文档上跑**（本轮踩到）。 | SW 主窗口标题；轮 96 曾把它记为「未查证」，轮 99 得到答案 |
"""
if "不能抑制某些模态框" not in t:
    P.write_text(t.rstrip() + add, encoding="utf-8")
    print("  ✓ known-facts 已加 64/65")
else:
    print("  已有")

# ② batch7 三条 doc 加脏标警告
Q = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch7.py")
tq = Q.read_text(encoding="utf-8")
warn = " \u26a0 May mark the document as modified (view/selection state changes count)."
pairs = [
    ('doc="Activate the model for preview/review (prepares the document for capture)."',
     'doc="Activate the model for preview/review (prepares the document for capture)."' + warn),
    ('doc="Clear the selection so the preview does not show highlighted entities."',
     'doc="Clear the selection so the preview does not show highlighted entities."' + warn),
    ('doc="Refresh the graphics/scene graph, e.g. after an appearance change."',
     'doc="Refresh the graphics/scene graph, e.g. after an appearance change."' + warn),
]
n = 0
for old, new in pairs:
    if old in tq and warn not in tq:
        tq = tq.replace(old, new, 1)
        n += 1
if n:
    Q.write_text(tq, encoding="utf-8")
    print("  ✓ batch7 已给 %d 条 doc 加脏标警告" % n)
else:
    print("  batch7 无需改（或已加）")
