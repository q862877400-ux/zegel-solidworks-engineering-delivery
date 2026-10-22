"""★ 批次 80：自动化**诊断知识**（HRESULT 释义 / 命令锁 / 首选项开关）+ COM 陷阱判定 + 会话忙闲检测。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_automation_knowledge.py`（HRESULT 释义 · 命令锁 · 首选项开关）
#         `scripts/sw_com_traps.py`（★ 本批只取 2 个**纯函数**：`deprecated_successor` /
#          `find_real_implementations`）
#         `scripts/sw_busy.py`（★ 本会话 2026-10-04 新建：SolidWorks 忙闲 / 卡死 / 求解器进程 / 等空闲）
# 定位:   ★ 规格 `specs/205-tool-ramp/` §8.3 的**批 80**（v3 批序第一坡）✓
#         ★ 选域依据：机械预筛 `output/prescreen-deduped.json`（本批候选 16 ⇒ 预估可挂 ~14，实得 12）✓
# 官方依据: ★ **本批多数是本仓自研**（`source_kind: repo_original`）——· `explain_hresult
#           ` / `explain` 的释义表出自本仓（★ 不是官方枚举页）；  ★ 而 `sw_com_traps` 的
#           来源块另记了第三方调研（andrewbartels1 / Millwright / chatsw，均 MIT）· `sw_
#           busy` 是本仓新建（事实 526：忙碌判定要**归属 SolidWorks 家族进程**，否则假阳
#           性）· `set_flag` / `get_flag` 的 `pref` 优先用本仓 `DIALOG_SUPPRESSORS` 里的
#           名字⚠ 故本批**不声明** `official_file`（★ 那些函数没有官方 md 页），  ★ 而由
#           本文件头 + 各 `doc` 指明**真源是本仓代码**（铁律 1 的"本项目自身既有模式"那
#           一栏）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **12 个工具**（automation 6 · com_traps 2 · busy 4）⇒ 工具数 313 → **325**
# ★★ 本批**不做**的（FR-002/D-5 要求记"不做 + 原因"）：
#     · `sw_automation_knowledge.send_message` —— ★ 它**自己弹一个模态提示框** ⇒
#       与「无人值守」和「常驻弹窗监控」（事实 527）**直接冲突**：监控会把它记成 `needs_llm`，
#       而没人去点它 ⇒ **会话就停在那儿**。★ 故不挂；要跟用户说话，用工具返回值/报告，不用弹框 ✓
#     · `sw_com_traps.explain` —— ★ 与 `sw_automation_knowledge.explain_hresult` **同一件事**
#       （FR-006 去重：换名不重挂）✓
#     · `sw_com_traps.is_type_mismatch` —— ★ 等价于一次 `== 0x80020005`，**没有独立价值**；
#       ★ 且 `tool_specs_batch7.py` 已有先例把同模块的 `byref_pair` 判为"内部用·不暴露" ✓
#     · `byref_long` / `byref_pair` —— ★ COM 出参 VARIANT 工厂，**内部管道**（同上先例）✓
#     · `adaptive_arity` —— ★ 首参是**可调用对象**，MCP 的 JSON 边界装不下 ✓
#     · `is_swp_macro(data)` —— ★ 首参是**字节串**，JSON 边界装不下（★ 要挂得先改成收路径）✓
#     · `iter_real_sources(root, pattern)` —— ★ 它是 **generator**，返回值过不了 MCP 边界 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH80"]

SPECS_BATCH80 = [
    # ── ① HRESULT 释义与命令锁（6）────────────────────────────────────────
    ToolSpec(
        name="solidworks_automation_explain_hresult",
        title="Explain an HRESULT in Plain Words (repo's own table)",
        module="sw_automation_knowledge", function="explain_hresult",
        inject="",
        params=[Param("code", int, description="The HRESULT as an integer (e.g. -2147352571 for "
                                               "the classic 'type mismatch' / DISP_E_TYPEMISMATCH). "
                                               "★ Accepts the signed value Python's COM layer "
                                               "raises, not only the unsigned hex form.")],
        doc="Turn an HRESULT into plain words using THIS REPO's table. ★★ Its own docstring states the discipline: when the code is not in the table it says so — it does NOT invent a meaning (repo rule 5). ★ Source is the repo's own table, NOT an official enum page, so treat the text as a repo-authored hint.",
    ),
    ToolSpec(
        name="solidworks_automation_enter_command_lock",
        title="Suppress Modal Dialogs (CommandInProgress = True)",
        module="sw_automation_knowledge", function="enter_command_lock",
        inject="sldworks",
        params=[],
        doc="Set `ISldWorks.CommandInProgress = True` to stop the operations that pop modal dialogs. "
            "★ This is the repo's prescribed pre-flight before risky COM work (rule 2). "
            "⚠ Official note from this repo: an unreleased lock makes SolidWorks keep refusing "
            "operations — pair it with `solidworks_automation_exit_command_lock`.",
    ),
    ToolSpec(
        name="solidworks_automation_exit_command_lock",
        title="Release the Command Lock (CommandInProgress = False)",
        module="sw_automation_knowledge", function="exit_command_lock",
        inject="sldworks",
        params=[],
        doc="Release the lock set by `solidworks_automation_enter_command_lock`. "
            "⚠ The wrapped function's own docstring warns: forgetting this call leaves SolidWorks "
            "refusing operations.",
    ),
    ToolSpec(
        name="solidworks_automation_is_command_locked",
        title="Is the Command Lock Currently On?",
        module="sw_automation_knowledge", function="is_command_locked",
        inject="sldworks",
        params=[],
        doc="Read whether `CommandInProgress` is currently set. ★ The wrapped function notes the "
            "official member is a **zero-argument property** on `ISldWorks`.",
    ),
    ToolSpec(
        name="solidworks_automation_set_flag",
        title="Set a Dialog/Preference Flag",
        module="sw_automation_knowledge", function="set_flag",
        inject="sldworks",
        params=[
            Param("pref", str, description="Flag name. ★ Prefer the names in this repo's "
                                           "`DIALOG_SUPPRESSORS` table — they are the ones the repo "
                                           "has mapped to real preference ids."),
            Param("value", bool, description="True to enable the flag, False to disable it."),
        ],
        doc="Set a preference switch on `ISldWorks`. ★ Use it to mute the dialogs a given operation "
            "would otherwise raise. ⚠ This repo's non-invasiveness contract applies: these are "
            "the documented, restorable preferences (see `references/deployment-boundary.md`) — "
            "the repo's preference-write gate covers every such site.",
    ),
    ToolSpec(
        name="solidworks_automation_get_flag",
        title="Read a Dialog/Preference Flag",
        module="sw_automation_knowledge", function="get_flag",
        inject="sldworks",
        params=[Param("pref", str, description="Flag name (same table as "
                                               "`solidworks_automation_set_flag`).")],
        doc="Read a preference switch back from `ISldWorks`. ★ The wrapped function notes the "
            "official member takes **one argument**.",
    ),
    # ── ② COM 陷阱的纯函数判定（2）────────────────────────────────────────
    ToolSpec(
        name="solidworks_api_deprecated_successor",
        title="Which Member Should Replace This Deprecated One?",
        module="sw_com_traps", function="deprecated_successor",
        inject="",
        params=[Param("member", str, description="An official member name, e.g. `CreateDefinition` "
                                                 "or a numbered variant like `AddMate2`."),
                Param("interface", str, default="", description="Optional interface name (e.g. "
                      "`IEntity`). ★ Leave EMPTY to look up by member name alone — which returns "
                      "`None` when that name maps to different successors on different interfaces "
                      "(the tool refuses to guess). Pass the interface to get the exact answer.")],
        doc="Given a member name, return the successor this repo maps it to — and `None` when it "
            "does not know it (★ the wrapped function's docstring is explicit: it does NOT guess, "
            "repo rule 5). ★★ `None` also means \"ambiguous by name\": some members share a name "
            "across interfaces with DIFFERENT successors (e.g. `Select2` — 6 different endpoints), "
            "so an unqualified lookup has no single right answer. Pass `interface` to disambiguate. "
            "★ Pure function: no SolidWorks call, no COM.",
    ),
    ToolSpec(
        name="solidworks_repo_find_real_implementations",
        title="Find Where a Member Is REALLY Implemented (excludes reflection dumps)",
        module="sw_com_traps", function="find_real_implementations",
        inject="",
        params=[
            Param("needle", str, description="Member name or fragment to look for, e.g. "
                                             "`HoleWizard5`."),
            Param("root", str, default="", description="Directory to search. Leave EMPTY to use the "
                                                       "repo's `scripts/` directory."),
        ],
        doc="Search the repo for real implementations and return `[\"file:line\", …]`. "
            "★★ **Why this exists**: the repo's `sw_api_*.py` files are machine-generated reflection "
            "dumps that mention every member name — a naive grep matches those and tells you nothing. "
            "This function excludes them, so the answer is \"where is it actually USED\". "
            "★ Pure function (filesystem only, no SolidWorks). ⚠ `root` empty means the repo default, "
            "not the current directory.",
    ),
    # ── ③ 会话忙闲 / 卡死 / 求解器进程 / 等空闲（4）───────────────────────
    ToolSpec(
        name="solidworks_session_busy_status",
        title="Is SolidWorks Busy Right Now? (attributable windows only)",
        module="sw_busy", function="solidworks_busy",
        inject="",
        params=[],
        doc="Report whether SolidWorks is busy, with the evidence that decided it. "
            "★★ The judgement is deliberately strict (fact 526): a progress window counts only when "
            "it is **attributable to the SolidWorks process family** (matched by executable path), "
            "because an ORPHAN `OperationStatusWindow` left behind by Explorer otherwise produces a "
            "false 'busy'. ★ Also requires `SLDWORKS.exe` to be present. "
            "★ Reads only: it inspects windows, it does not touch the model.",
    ),
    ToolSpec(
        name="solidworks_session_stuck_status",
        title="Is SolidWorks STUCK? (not responding AND no solver alive)",
        module="sw_busy", function="solidworks_stuck",
        inject="",
        params=[],
        doc="Report whether SolidWorks looks stuck, using BOTH signals: it is not responding **and** "
            "no solver process is alive. ★★ That second half matters — during a long solve the main "
            "window can look 'not responding' while `star.exe` is happily working, and calling that "
            "'stuck' is how a normal solve gets killed (facts 293/526).",
    ),
    ToolSpec(
        name="solidworks_session_solver_processes",
        title="List the Live Solver Processes",
        module="sw_busy", function="solver_processes",
        inject="",
        params=[],
        doc="List the solver kernels currently running (the COSMOS/M family, enumerated via the "
            "Toolhelp32 snapshot — no `tasklist` parsing). ★ Use it to tell 'still solving' from "
            "'crashed', and to confirm a solver actually exited.",
    ),
    ToolSpec(
        name="solidworks_session_wait_until_idle",
        title="Wait Until SolidWorks Is Idle (bounded)",
        module="sw_busy", function="wait_until_idle",
        inject="",
        params=[
            Param("timeout", float, default=60.0,
                  description="Give up after this many SECONDS (★ this is a duration, not a length)."),
            Param("interval", float, default=3.0,
                  description="Poll interval in SECONDS."),
        ],
        doc="Block until `solidworks_session_busy_status` reports idle, or until the timeout — "
            "★ it always returns, and says whether it actually reached idle. "
            "★★ Use it before driving COM: landing a call while SolidWorks is busy is the documented "
            "route to a hung session (fact 526). ⚠ It polls; it does not touch the model.",
    ),
]
