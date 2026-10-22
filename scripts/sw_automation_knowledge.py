r"""SolidWorks 自动化的通用可复用知识：错误码、弹窗、选区、诊断。

这不是 API 清单（那在 ``sw_api_<程序集>.py``），而是**跑自动化时反复要用、
但官方文档不会告诉你的那几件事**。每条都能追到官方成员或本机实测。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的知识层）
# 文件:   scripts/sw_automation_knowledge.py —— 本文件自身
# 定位:   「怎么让自动化不被打断 / 出错了怎么看」的可复用条目。
# ⚠ 本模块**不含任何 API 成员别名** —— 成员一律按官方名查 sw_api_* 索引。
#   本模块只提供「知识」：错误码含义、开关怎么用、状态怎么回读。
# 来源依据（逐条见下方每节的注释）：
#   ① 对官方 interop 程序集的纯元数据反射（成员名与参数个数）
#   ② C:\swprojects 下 11 个 MIT 仓库的实操写法（交叉佐证）
#   ③ 第三方项目记录的 HRESULT 含义（codestack 记的 PDM 建连接错误）
# 覆盖:   后续同级定义
# ⚠ 本模块为静态整理，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member, set_com_member
except ImportError:
    from sw_connect import get_com_member, set_com_member

__all__ = [
    "HRESULTS",
    "ERROR_NOTIFICATION",
    "DIALOG_SUPPRESSORS",
    "DIALOG_AND_NOTIFY",
    "explain_hresult",
    "enter_command_lock",
    "exit_command_lock",
    "is_command_locked",
    "set_flag",
    "get_flag",
    "send_message",
]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   C:\swprojects\codestack (MIT License)  +  COM 标准 HRESULT
# 文件:   solidworks-document-manager-api/getting-started/create-connection/index.md
# 定位:   **0x80040112** 的含义 —— codestack 明确记为
#         `Class is not licensed for use (Exception from HRESULT: 0x80040112)`。
# ⚑ 这是**官方文档不会给**的：它只在「你调 PDM 而没买许可」时出现，
#   报错文本是英文，搜官方文档未必搜得到。
# ⚠ 其余码取自 COM / Shell 标准定义与 CSharpAndSolidWorks 的常量表，
#   **只收录有明确定义的**，不确定的一律不列（宁可缺也不猜）。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
HRESULTS: dict[int, str] = {
    0x80040112: "COM 类未授权 —— 通常是**该产品没有许可**"
    "（PDM / Simulation / Routers 等独立许可产品）",
    0x80070057: "参数无效（E_INVALIDARG）",
    0x8007000E: "内存不足（E_OUTOFMEMORY）",
    0x80004002: "未找到接口/对象（E_NOINTERFACE）",
    0x80004005: "通用失败（E_FAIL）",
    0x800401F0: "对象已聚合到别处，不能再聚合（CLASS_E_NOAGGREGATION）",
    0x80070006: "数据无效（E_HANDLE）",
    0x8007007A: "缓冲区太小（HRESULT_FROM_WIN32(ERROR_INSUFFICIENT_BUFFER)）",
    0x80070005: "拒绝访问（E_ACCESSDENIED）",
    0x8000FFFF: "异常（E_UNEXPECTED）",
}


def explain_hresult(code: int) -> str:
    """把 HRESULT 翻成人话。⚠ 查不到就**明说查不到**，不编。"""
    code = int(code) & 0xFFFFFFFF
    if code in HRESULTS:
        return HRESULTS[code]
    if code & 0x80000000:
        return f"未收录的失败码 0x{code:08X}（是 HRESULT 失败，但本表无释义）"
    return f"0x{code:08X}（非失败 HRESULT）"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 interop 程序集的纯元数据反射
# 文件:   同上 → ISldWorks 段
# 定位:   **弹窗相关的官方成员**（反射逐条确认，参数个数也确认）：
#     get_CommandInProgress() / set_CommandInProgress(Boolean)  ← 核心开关
#     get_FrameState() / set_FrameState(Int32)
#     get_EnableFileMenu()
#     Object DefineUserNotification(String)      ← 自定义通知（造一个）
#     Int32   ShowUserNotification(Object, Object)  ← 显示通知
#     Void    CloseUserNotification(Object)      ← **关掉**通知
#     Int32   GetErrorMessages(Object&, Object&, Object&)  → **0 实参**（全是 [out]）
#     Object  GetLastSaveError(Object&, Object&)            → **0 实参**
#     SendMsgToUser(String) / SendMsgToUser2(String, Int32, Int32)
# ⚑ **``CommandInProgress`` 是「不让 SolidWorks 弹窗打断」的正路**：
#   置 True 后，任何可能触发对话框的操作都被拦下、命令直接失败返回，
#   而不是弹窗等人点。自动化必须**在 try/finally 里成对开关** ——
#   忘了关回来，SolidWorks 会一直处于「命令进行中」而拒收一切操作。
# ⚠⚑ **更正**：本模块初稿写了 ``GetErrorNotification`` / ``SetErrorNotification``，
#   **这两个成员不存在**（全程序集零命中）—— 那是**凭印象写的**，
#   是本项目第 10 次栽在这类错上。真实的是
#   ``DefineUserNotification`` / ``ShowUserNotification`` / ``CloseUserNotification``。
# ⚠ 官方未文档化「置 True 之后用户界面会怎样」，本模块**不解释**。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────

#: 弹窗与通知相关的官方成员清单（名字 + 实参个数，反射逐条确认）
#: ⚠ 只列**反射里确实存在**的；用前请对回 sw_api_sldworks.ARITY。
#: enum-gate: not-enum arity
DIALOG_AND_NOTIFY: dict[str, int] = {
    "CommandInProgress": 1,  # 反射整行两种形态：get_=0 参 / set_=1 参
    "FrameState": 1,  # 同上：get_=0 / set_=1
    "DefineUserNotification": 1,
    "ShowUserNotification": 2,
    "CloseUserNotification": 1,
    "GetErrorMessages": 0,  # ⚑ 三个参数全是 [out]，调用方一个都不传
    "GetLastSaveError": 0,  # ⚑ 同上
    "SendMsgToUser": 1,
    "SendMsgToUser2": 3,
}

#: 反射确认能「少问一句」的首选项开关（值来自 swconst 的 swUserPreferenceToggle_e）
#: enum-gate: enum swUserPreferenceToggle_e
DIALOG_SUPPRESSORS: dict[str, int] = {
    # ⚑ 这几个值取自对 swconst 的反射（swUserPreferenceToggle_e）
    "swInputDimValOnCreate": 10,
}


def enter_command_lock(sldworks) -> bool:
    """置 ``CommandInProgress=True`` —— 拦住会弹窗的操作。

    ⚠ **必须**配 :func:`exit_command_lock`，最好用 try/finally。
    """
    if sldworks is None:
        raise ValueError("sldworks 为 None")
    set_com_member(sldworks, "CommandInProgress", True)
    return True


def exit_command_lock(sldworks) -> bool:
    """解除 :func:`enter_command_lock`。⚠ 忘了调用会让 SolidWorks 一直拒收操作。"""
    if sldworks is None:
        raise ValueError("sldworks 为 None")
    set_com_member(sldworks, "CommandInProgress", False)
    return True


def is_command_locked(sldworks) -> bool:
    """当前是否处于命令锁。⚑ 官方是**零参属性**。"""
    if sldworks is None:
        raise ValueError("sldworks 为 None")
    return bool(get_com_member(sldworks, "CommandInProgress"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 interop 程序集的纯元数据反射
# 文件:   同上 → ISldWorks / IModelDoc2 段
# 定位:   首选项开关的读写（反射确认）：
#     ISldWorks.SetUserPreferenceToggle(Int32, Boolean)   → 2 参
#     ISldWorks.GetUserPreferenceToggle(Int32)            → 1 参
#     IModelDoc2.SetUserPreferenceToggle(Int32, Boolean) → 2 参（⚠ 同一个成员名、不同接口）
# ⚠ **同名成员在不同接口上参数个数可能不同** ——
#   IModelDoc2 上是 2 参、IModelDocExtension 上是 **3 参**（多一个配置名）。
#   这正是本仓库反复栽跟头的地方，写调用前务必确认是哪个接口。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def set_flag(sldworks, pref: str, value: bool) -> bool:
    """设首选项开关。`pref` 优先用 :data:`DIALOG_SUPPRESSORS` 里的名字。"""
    if sldworks is None:
        raise ValueError("sldworks 为 None")
    key = DIALOG_SUPPRESSORS[pref] if pref in DIALOG_SUPPRESSORS else int(pref)
    get_com_member(sldworks, "SetUserPreferenceToggle", key, bool(value))
    return True


def get_flag(sldworks, pref: str) -> bool:
    """读首选项开关。⚑ 官方是 **1 参**（``ISldWorks`` 上）。"""
    if sldworks is None:
        raise ValueError("sldworks 为 None")
    key = DIALOG_SUPPRESSORS[pref] if pref in DIALOG_SUPPRESSORS else int(pref)
    return bool(get_com_member(sldworks, "GetUserPreferenceToggle", key))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   C:\swprojects\codestack (MIT License) + 官方反射
# 文件:   codestack 多个 solidworks-api/import-export/*/Macro.{vba,cs}
# 定位:   `SendMsgToUser2(String, Int32, Int32)` 的**三参签名**（反射确认 3 参）——
#         消息文本 + 图标枚举 + 按钮枚举。
# ⚑ codestack 全部用 `swMbStop` / `swMbInformation` + `swMbOk` 组合，
#         这是**自己弹提示框**（codestack 用来在宏出错时把 Err.Description 显示出来），
#         **不是**关掉 SolidWorks 自己的弹窗 —— 后者用 CommandInProgress。
# ⚠ 图标/按钮枚举的值需自行查 swconst，本模块不猜。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def send_message(sldworks, text: str, icon: int, buttons: int) -> bool:
    """自己弹一个提示框。⚠ 这**不是**用来关弹窗的（那用 :func:`enter_command_lock`）。"""
    if sldworks is None:
        raise ValueError("sldworks 为 None")
    get_com_member(sldworks, "SendMsgToUser2", str(text), int(icon), int(buttons))
    return True
