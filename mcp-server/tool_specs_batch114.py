"""★ 批 114 —— 把 `tools/sw_guard.py` 的**弹窗三级分级器**正式注册成 MCP 工具。

★★★ **为什么要有这一批**（★ 业主 2026-10-10 逐字点破）：
  ★ 业主原话：「★ **这个报错出现了，你搜索记忆，以前专门以为这个弹窗，
    做了一套弹窗检测和自动点击的脚本**」→ ★★ 随即又补：
    「★ **把这个检测的，也注册成一个MCP工具什么的，加入你的工具列表，
     不然每次都不知道主动用**」✓
  ★★★ **实测缺口**（★ 本会话核过）：★ 工具面**已有 9 个** `solidworks_gui_*`
    （★ `find_modals` / `close_modals` / `modal_report` / `assert_no_modal` …），
    ★★ **但没有任何一个暴露 `classify_dialog`** —— ★ 而它才是那套机制的**大脑**
    （★ 决定「能不能自动点、点哪个、还是必须交给人/LLM」）。
  ★★ **后果（★ 我自己的实例）**：★ 本会话 EC09 求解时我**只用了 `--scan` 与 `--clear`**
    ⇒ ★ 看到弹窗却**没读出它的分级理由** ⇒ ★★ 把「求解**失败**（未定义载荷）」
    误读成「求解**很慢**」⇒ ★ **把根因判错了** ✗
  ★★★ **⇒ 本批把「读弹窗」这件事从「记得去翻 tools/」变成「工具列表里就有」** ✓
    （★ 这正是业主说的「不然每次都不知道主动用」）

★ 本批**只做注册**（★ 不改 `sw_guard.py` 一行 —— ★ 它的三级分级已被
  `tests/test_sw_guard_dialog_tiers.py` 验过）。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 不是第三方移植）
# 文件:   `tools/sw_guard.py`（★ 实现 · ★ `classify_dialog(d: dict) -> dict`）
#         `tests/test_sw_guard_dialog_tiers.py`（★ 三级的契约 + 负例）
#         `AGENTS.md` §十五（★ 弹窗护栏 —— ★ 「三级处置」是业主点破的那一层）
# 定位:   ★ 把**分级器**挂上工具面；★ 起因是业主点破「每次都不知道主动用」。
# 官方依据: 不适用（本仓自研的 GUI 护栏；★ 判据是 `classify_dialog` 的返回值）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH114"]


def _classify_from_text(params) -> dict:
    """★ 把「按钮清单 + 正文」拼成 `classify_dialog` 要的 `controls` 形状。

    ★★ **为什么在这里拼**（★ 与批 113 同一理由）：
      · ★ `classify_dialog(d)` 读的是 **`d["controls"]`** —— ★ 每项 `{"class": …, "text": …}`；
      · ★★ MCP 边界**只过标量**（★ 无 `list` 型 `Param` 先例 —— `tool_specs_batch15.py:21-25`）；
      · ★★★ ⇒ ★ **拼装发生在 `derived_args`**，★ 遵守全仓既有的「`str` + 分隔符」约定 ✓
    ★ 约定：★ `buttons` 用 **`,`** 分隔（★ 按钮名不含逗号）；
      ★ `texts` 用 **`|`** 分隔（★ 因为正文里**可能含逗号**，★ 用竖线更稳）。
    """
    buttons = [
        b.strip()
        for b in str(getattr(params, "buttons", "") or "").split(",")
        if b.strip()
    ]
    texts = [
        t.strip()
        for t in str(getattr(params, "texts", "") or "").split("|")
        if t.strip()
    ]
    controls = [{"class": "Static", "text": t} for t in texts]
    controls += [{"class": "Button", "text": b} for b in buttons]
    return {"title": str(getattr(params, "title", "") or ""), "controls": controls}


SPECS_BATCH114: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_gui_classify_dialog",
        title="Classify a SolidWorks Dialog into auto / needs_llm / forbidden / progress",
        #: ★★ **走 `scripts/sw_gui_dialog_classify`**（★ 工具层的**形状适配**）——
        #: ⚠ **为什么不直接挂 `sw_guard.classify_dialog`**（★ 实测）：★ 它的签名是 `(d:
        #: dict)`
        #:     ⇒ ★ 只吃 `controls` ⇒ ★ 多传 `title` 会 `TypeError` ✗
        #:   ★ 包装**收标量** · ★ **拼 `controls`** · ★ 再转交 ⇒ ★ **分级逻辑一行不改** ✓
        module="sw_gui_dialog_classify",
        function="classify_dialog",
        #: ★★ `inject=""` = **不注入宿主对象**（★ 约定俗成的四个取值之一）
        #:   ★ 本工具**纯离线**（★ 只读文本 ⇒ ★ 不需要 model/sw_app/study）✓
        inject="",
        params=[
            Param(
                "buttons",
                str,
                description=(
                    '★ **按钮文本**（★ **逗号 `,` 分隔**）。★ 例：`"确定"` / '
                    '`"是,否,确定"` / `"暂停,取消,更多>>"`。'
                    "★★ **这是分级的关键** —— 分级器先看按钮："
                    "★ 只有一个语义明确的确认按钮 ⇒ `auto`（**可自动点**）；"
                    "★ 有 否/取消/暂停/上一步/下一步，或**多个同权按钮** ⇒ `needs_llm`（**不点**）。"
                ),
            ),
            Param(
                "texts",
                str,
                default="",
                description=(
                    "★ **弹窗正文**（★ **竖线 `|` 分隔** —— ★ 因为正文里常含逗号）。"
                    '★ 例：`"未定义载荷或规定的位移|固定-刚性零件上的载荷将不处于活动状态。"`。'
                    "★★ 正文含**危险词**（删除/覆盖/替换/丢失/不可逆/remove/overwrite/delete…）"
                    "⇒ ★ **`forbidden`**（★ **绝不自动点**）。"
                ),
            ),
            Param(
                "title",
                str,
                default="",
                description="★ 弹窗标题（★ 如 `Simulation`）。",
            ),
        ],
        derived_args=_classify_from_text,
        evidence=(
            "★ **读一个弹窗，判「能不能自动点」**（★ 本仓弹窗护栏的**大脑**）。\n\n★★★ **为什么该主动用它**（★ 业主 202"
            "6-10-10 点破）：工具面已有 9 个 `solidworks_gui_*`，★ 但**只有这一个**能回答「★ 这个弹窗**该不该**点、★ 点"
            "了**会不会出事**」。★ 以前它只在 `tools/sw_guard.py` 里 ⇒ ★ **每次都想不到用** （★ 我本会话就因此把「求解"
            "失败」误读成「求解很慢」）。\n\n★★ **四级结论**（★ 逐字承 `tools/sw_guard.py::classify_dialog`）：\n· `aut"
            "o` —— ★ 只有一个语义明确的确认按钮 ⇒ **可自动点**；\n· `needs_llm` —— ★ 有 否/取消/暂停/上一步/下一步，或"
            "多同权按钮 ⇒ **不点**，把文本交给人/LLM 判；\n· `forbidden` —— ★ 正文含危险词（删除/覆盖/替换/丢失/不可逆…"
            "）⇒ **绝不自动点**；\n· `progress` —— ★★ **正常求解的进度窗**（含 `当前任务`/`已用时间`/`自由度`/`单元数`"
            "）⇒ ★ **既不点、也不中止**（★ 事实 297：点掉 = **中断一个正在跑的正常任务**）。\n\n★★ **配套工具（一起用）"
            "**：`solidworks_gui_find_modals`（找出来）→ **本工具**（判该不该点）→ `solidworks_gui_close_modals`（真去"
            "点）。\n★★ **纯离线**（★ 只读文本 ⇒ ★ **不碰窗口、不点任何东西**）。\n★ 契约测试：`tests/test_sw_guard_dia"
            "log_tiers.py`（★ 三级 + 负例）。"
        ),
        doc=(
            "★ **读一个弹窗，判「能不能自动点」**（★ 本仓弹窗护栏的**大脑**）。\n\n"
            "★★★ **为什么该主动用它**（★ 业主 2026-10-10 点破）："
            "工具面已有 9 个 `solidworks_gui_*`，★ 但**只有这一个**能回答"
            "「★ 这个弹窗**该不该**点、★ 点了**会不会出事**」。"
            "★ 以前它只在 `tools/sw_guard.py` 里 ⇒ ★ **每次都想不到用** "
            "（★ 我本会话就因此把「求解失败」误读成「求解很慢」）。\n\n"
            "★★ **四级结论**（★ 逐字承 `tools/sw_guard.py::classify_dialog`）：\n"
            "· `auto` —— ★ 只有一个语义明确的确认按钮 ⇒ **可自动点**；\n"
            "· `needs_llm` —— ★ 有 否/取消/暂停/上一步/下一步，或多同权按钮 "
            "⇒ **不点**，把文本交给人/LLM 判；\n"
            "· `forbidden` —— ★ 正文含危险词（删除/覆盖/替换/丢失/不可逆…）⇒ **绝不自动点**；\n"
            "· `progress` —— ★★ **正常求解的进度窗**（含 `当前任务`/`已用时间`/`自由度`/`单元数`）"
            "⇒ ★ **既不点、也不中止**（★ 事实 297：点掉 = **中断一个正在跑的正常任务**）。\n\n"
            "★★ **配套工具（一起用）**：`solidworks_gui_find_modals`（找出来）→ "
            "**本工具**（判该不该点）→ `solidworks_gui_close_modals`（真去点）。\n"
            "★★ **纯离线**（★ 只读文本 ⇒ ★ **不碰窗口、不点任何东西**）。\n"
            "★ 契约测试：`tests/test_sw_guard_dialog_tiers.py`（★ 三级 + 负例）。"
        ),
    ),
]
