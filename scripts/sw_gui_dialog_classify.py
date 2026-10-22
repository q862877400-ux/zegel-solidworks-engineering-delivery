"""★ 弹窗分级的**工具层包装** —— 把 `sw_guard.classify_dialog` 接成 MCP 可调的形状。

★★★ **为什么要有这一层**（★ 业主 2026-10-10 点破）：
  ★ 业主原话：「★ **把这个检测的，也注册成一个MCP工具什么的，加入你的工具列表，
    不然每次都不知道主动用**」✓
  ★★ **实测缺口**：★ 工具面**已有 9 个** `solidworks_gui_*`，★ **但没有任何一个**
    暴露 `classify_dialog` —— ★ 而它才是那套机制的**大脑**（★ 判「能不能自动点」）。
  ★★★ **本模块只做「形状适配」** —— ★ **分级逻辑一行不改**（★ 那是 `sw_guard.classify_dialog`，
    已由 `tests/test_sw_guard_dialog_tiers.py` 验过）✓
  ★★ **为什么不能直接挂 `classify_dialog`**（★ 实测）：★ 它的签名是 `(d: dict)`
    ⇒ ★ 只吃 `controls` 一个键 ⇒ ★ 多传 `title` 会 `TypeError` ✗
    ⇒ ★ 本包装**收标量**（`buttons`/`texts`/`title`）· ★ **拼 `controls`** · ★ 再转交 ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 不是第三方移植）
# 文件:   `tools/sw_guard.py`（★ `classify_dialog(d: dict) -> dict` —— ★ **分级逻辑的真
# 源**）
#         `tests/test_sw_guard_dialog_tiers.py`（★ 三级的契约 + 负例）
#         `mcp-server/tool_specs_batch114.py`（★ 本包装的 ToolSpec 声明）
#         `AGENTS.md` §十五（★ 弹窗护栏的三级处置）
# 定位:   ★ 把分级器**接上工具面**；★ 起因是业主点破「每次都不知道主动用」。
# 官方依据: 不适用（本仓自研的 GUI 护栏）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 只读文本，★ **不碰窗口**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

#: ★★ `sw_guard.py` 在 `tools/` 下 —— ★ 该目录**不是包**（无 `__init__.py`）
#:   ⇒ ★ 按**文件路径**把它加载进来（★ 不污染 `sys.path` 的其它解析）
_TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))


def classify_dialog(buttons: str, texts: str = "", title: str = "") -> dict:
    """★ **读一个弹窗，判「能不能自动点」**（★ 本仓弹窗护栏的**大脑**）。

    ★★★ **为什么该主动用它**：★ 工具面已有 9 个 `solidworks_gui_*`，
      ★★ 但**只有这一个**能回答「★ 这个弹窗**该不该**点、★ 点了**会不会出事**」✓
      ★ 以前它只在 `tools/sw_guard.py` 里 ⇒ ★ **每次都想不到用**
      （★ 我 2026-10-10 就因此把「求解**失败**」误读成「求解**很慢**」）✗

    :param buttons: ★ 按钮文本（★ **逗号 `,` 分隔**）。★ 例：`"确定"` / `"是,否,确定"`。
    :param texts: ★ 弹窗正文（★ **竖线 `|` 分隔** —— ★ 正文里常含逗号）。
    :param title: ★ 弹窗标题（★ 如 `"Simulation"`）。
    :returns: ★ `{"mode": …, "needs_llm": …, "reason": …}`
      · `auto` —— ★ 只有一个语义明确的确认按钮 ⇒ **可自动点**；
      · `needs_llm` —— ★ 有 否/取消/暂停/上一步/下一步，或多同权按钮 ⇒ **不点**；
      · `forbidden` —— ★ 正文含危险词（删除/覆盖/替换/丢失/不可逆…）⇒ **绝不自动点**；
      · `progress` —— ★★ **正常求解的进度窗** ⇒ ★ **既不点、也不中止**（★ 事实 297）。
    """
    #: ★ 按 `classify_dialog(d)` 的契约拼 `controls`（★ 它读 `d["controls"]`）
    ctrls: list[dict[str, str]] = []
    for t in str(texts or "").split("|"):
        t = t.strip()
        if t:
            ctrls.append({"class": "Static", "text": t})
    for b in str(buttons or "").split(","):
        b = b.strip()
        if b:
            ctrls.append({"class": "Button", "text": b})

    import sw_guard as _G
    verdict = _G.classify_dialog({"title": str(title or ""), "controls": ctrls})

    #: ★★ **回一份**可判**的结果**（★ 附上「该不该点」的**显式**结论 —— ★ 少一步推断）
    mode = verdict.get("mode")
    out: dict[str, Any] = dict(verdict)
    out["buttons_parsed"] = [c["text"] for c in ctrls if c["class"] == "Button"]
    out["texts_parsed"] = [c["text"] for c in ctrls if c["class"] != "Button"]
    out["should_auto_dismiss"] = (mode == "auto")
    out["must_not_touch"] = mode in ("forbidden", "progress")
    out["escalate_to_human_or_llm"] = (mode == "needs_llm")
    out["next_tool"] = {
        "auto": "solidworks_gui_close_modals（★ 可放心点）",
        "needs_llm": "★ **不要自动点** —— 把文本交给人/LLM 判",
        "forbidden": "★ **绝不自动点**（★ 含危险词）",
        "progress": "★ **不要点也不要中止** —— 它在报告一个正在跑的正常任务（★ 事实 297）",
    }.get(mode, "★ 未知 mode ⇒ 不要点")
    return out
