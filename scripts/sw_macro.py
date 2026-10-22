"""★ 宏执行：`ISldWorks.RunMacro2`（★ 规格 202 的 FR-008「宏/VBA 执行」那一半）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）+ 官方结构化页
# 文件:   `C:\swapi\types\ISldWorks\RunMacro2.md` —— 官方签名**四个入参 + 一个 out**：
#             System.bool RunMacro2( String FilePathName, String ModuleName,
#                                   String ProcedureName, Int32 Options, out Int32 Error )
#         `C:\swapi\enums\swRunMacroOption_e.md`（2 成员）·
#         `C:\swapi\enums\swRunMacroError_e.md`（28 成员）·
#         `_raw\enum_values_sldworks.txt`（出厂反射，**与官方页逐条一致**）
# 定位:   宏执行域此前**完全空白** —— 实测 `capabilities.yaml` 里没有一条与 `RunMacro`
#            有关；
#         `scripts/sw_macro_guard.py` 只做**生成 / 校验 / 落盘** VBA 文本，**不执行**。
#         ★ 规格 202 的 FR-008 逐字要求「**宏/VBA 执行** MUST 可用」⇒ 本模块补的就是它。
# ⚠ 官方 `## Remarks` 对本机版本**是空的**（该页 Remarks 段无内容）⇒ 本模块不替它补语义
# ，
#   只按签名与枚举调用；语义未证之处一律标注「未查证」。
# ⚠ `swRunMacroOption_e` / `swRunMacroError_e` 的**两套源逐条一致**（官方页 == 出厂反射
# ）✓
#   ★ 顺带更正仓库一处旧记载：`scripts/sw_com_traps.py` 写「`swRunMacroError_e` **不在官方
#     interop 类型库中**」——★ 实测**在**（反射里 28 个成员齐全），该句已过时（见事实 531）。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any

#: `swRunMacroOption_e` —— 两源一致（官方页表格 == 出厂反射）
RUN_MACRO_OPTIONS = {
    "default": 0,  # swRunMacroDefault
    "unload_after_run": 1,  # swRunMacroUnloadAfterRun
}

#: `swRunMacroError_e` —— **全 28 个成员**，★ 两源**按成员逐一比对一致**
#: （实测：官方页 28 个 == 出厂反射 28 个，`{成员: 值}` 字典相等；**只有排列顺序不同**）
#: ✓
#: enum-gate: enum swRunMacroError_e
RUN_MACRO_ERRORS = {
    "InvalidArg": 1,
    "MacrosAreDisabled": 2,
    "NotInDesignMode": 3,
    "OnlyCodeModules": 4,
    "OutOfMemory": 5,
    "InvalidProcname": 6,
    "InvalidPropertyType": 7,
    "SuborfuncExpected": 8,
    "BadParmCount": 9,
    "BadVarType": 10,
    "UserInterrupt": 11,
    "Exception": 12,
    "Overflow": 13,
    "TypeMismatch": 14,
    "ParmNotOptional": 15,
    "UnknownLcid": 16,
    "Busy": 17,
    "ConnectionTerminated": 18,
    "CallRejected": 19,
    "CallFailed": 20,
    "Zombied": 21,
    "Invalidindex": 22,
    "NoPermission": 23,
    "Reverted": 24,
    "TooManyOpenFiles": 25,
    "DiskError": 26,
    "CantSave": 27,
    "OpenFileFailed": 28,
}
_ERROR_NAME_BY_VALUE = {v: k for k, v in RUN_MACRO_ERRORS.items()}


# ── 规格 209 · B4-1（idx 211 `native_macro_recording`）────────────────────────────────
# ────────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）· ★ 铁律 1「只缝合不发明」
# 文件:   scripts/sw_macro.py —— 追加 `toggle_macro_recording` / `record_line` / `record
# _macro_lines`
#   （★ 裁决书指定的落点就是本模块）
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-1** · 外部项目 idx **211
# `native_macro_recording`** —— 裁决书：正解是 **`RecordLine`（写行）+ `RunCommand`（开
# 关录制）
# + `DSldWorksEvents::BeginRecordNotify`/`EndRecordNotify`（录制起止事件）**，三者都在官
# 方源里 ✓
#   ★★★ 裁决书点名的**头号风险**：「`swCommands_e.md` 对 `swCommands_StopMacro` 逐字写着
#     『**opens the Save As dialog**』⇒ 无头/无人值守下 `RunCommand(31)` **会弹模态框**」✓
#     ⇒ ★★ 本模块**永不调用 31**，改用 **`swCommands_RecordPauseMacro`(29) 这个「切换」**
#       来**开/停**录制 —— ★ 停录制走**暂停**那条路，**不触发 Save As** ✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
# · `C:\swapi\types\ISldWorks\RecordLine.md` —— `System.bool RecordLine(System.string Te
# xt)`
# ★ 摘要逐字：「Adds a line of code to a VBA macro **and** the SOLIDWORKS **journal file
# **.」
#     ★★ `## Remarks` 逐字给**两个硬事实**（★ 本模块的口径就照它）：
#       「Text is **only written to macros if macro recording is enabled** when the method is
#        called (`ISldWorks::Run Command` **swCommands_RecordPauseMacro** "").」
# 「**Users are prompted to select the type of macros to create when recording is stoppe
# d**
#        (`ISldWorks::Run Command` **swCommands_StopMacro** "").」
# · `C:\swapi\types\ISldWorks\RunCommand.md` —— `System.bool RunCommand(System.int Comma
# ndID,
# System.string NewTitle)`；`NewTitle` = 该命令拉起的 PropertyManager 页标题（★ 本模块传
#  `""`）
#   · `C:\swapi\enums\swCommands_e.md` —— ★ 逐字两条：
#       `swCommands_RecordPauseMacro | 29`（Macro toolbar > **Record\Pause Macro**）
#       `swCommands_StopMacro | 31; valid for a running macro, **opens the Save As dialog**`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **判据**（规则 6）：★ 这几个调用回的都是 `bool`（**返回值**）⇒ ★ 本模块**不拿它当唯
# 一判据**：
#   `RecordLine` 的 Remarks 已给出**语义前提** —— 「**只有录制开着才写得进去**」
#   ⇒ ★ 本模块把**三个返回值**（开录制 / 写行 / 停录制）**都回报**，
#     并在返回值里写明「★ **"真写进去了没有"要落盘的宏文件才能证**，
#     而那要 `swCommands_StopMacro`（**弹 Save As**）⇒ **本模块不去点它**」✓

#: ★ 官方 `swCommands_e` 里与「原生录制」有关的两条（★ 逐字抄；★ **130 多个 UserMacro 不
#: 抄**）
RECORD_COMMANDS = {
    "record_pause_macro": 29,  # swCommands_RecordPauseMacro —— Record\Pause Macro（**切换**）
    "stop_macro": 31,  # swCommands_StopMacro —— ★ 枚举页逐字「**opens the Save As dialog**」
}

#: ★★ **本模块明确不去点的那个命令**（★ 理由逐字，不静默）
STOP_MACRO_DIALOG_WARNING = (
    "★★ `swCommands_StopMacro`(31) 在官方枚举页里**逐字**被标注为「**opens the Save As dialog**」"
    "（`C:\\swapi\\enums\\swCommands_e.md`）⇒ ★★ 无头/无人值守下点它会**弹模态框**"
    "（本仓头号死因）⇒ ★ 本模块**永不调用 31**；★ 停录制走 `swCommands_RecordPauseMacro`(29) "
    "这个**切换**（官方 `RecordLine` 的 `## Remarks` 也是这样用的）✓ "
    "★ 代价（如实记）：**「录下来到底写进哪个文件」证不了** —— 那要 StopMacro 的 Save As 对话框 ✓"
)


def toggle_macro_recording(sw_app) -> dict[str, Any]:
    """★ **切换「录制/暂停」**（`ISldWorks::RunCommand(swCommands_RecordPauseMacro=29, "")`）。

    ⚠⚠ **它是个切换**（官方枚举逐字：「Macro toolbar > **Record\\Pause Macro**」）——
      ★ 同一个调用**既开也停** ⇒ ★ 本函数**不声称**"现在是开还是关"（★ 那是**猜**）；
      ★ 调用方要么自己保证成对调用，要么用 :func:`record_macro_lines`（★ 它成对做）✓
    :returns: `{ok, entry_used, command_id, returned, note, error}`
    """
    from sw_connect import get_com_member  # noqa: E402

    out: dict[str, Any] = {
        "ok": False,
        "entry_used": 'ISldWorks::RunCommand(swCommands_RecordPauseMacro=29, "")',
        "command_id": RECORD_COMMANDS["record_pause_macro"],
        "returned": None,
        "note": (
            "★ **这是切换、不是置位** —— ★ 本函数**不声称**切换后的状态"
            "（★ 官方页没说怎么读它；★ 本仓不猜）"
        ),
        "error": None,
    }
    if sw_app is None:
        out["error"] = "sw_app 为 None"
        return out
    try:
        out["returned"] = get_com_member(
            sw_app, "RunCommand", int(RECORD_COMMANDS["record_pause_macro"]), ""
        )
    except Exception as exc:  # noqa: BLE001
        out["error"] = "RunCommand 失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    out["ok"] = bool(out["returned"])
    if not out["ok"]:
        out["error"] = (
            "RunCommand(29) 回 %r（官方 Returns 逐字：True = 命令跑了）"
            % out["returned"]
        )
    return out


def record_line(sw_app, text: str) -> dict[str, Any]:
    """★ **往（正在录制的）宏与 journal 文件里写一行**（`ISldWorks::RecordLine(Text)`）。

    ★★ 官方 `## Remarks` 逐字：「Text is **only written to macros if macro recording is enabled**
      when the method is called」⇒ ★ **"写进去了没有「的前提是」录制开着"** ——
      ★ 本函数**只回报那个 `bool`**，★ **不把它当成「已写入」的证明** ✓
    :returns: `{ok, entry_used, text_len, returned, precondition_note, error}`
    """
    from sw_connect import get_com_member  # noqa: E402

    out: dict[str, Any] = {
        "ok": False,
        "entry_used": "ISldWorks::RecordLine(System.string Text)",
        "text_len": len(str(text or "")),
        "returned": None,
        "error": None,
        "precondition_note": (
            "★★ 官方 Remarks 逐字：**只有录制开着时** Text 才被写进宏 ⇒ "
            "★ 调用前先 `RunCommand(swCommands_RecordPauseMacro)` ✓ "
            "★ 而「真写进去了没有」**要落盘的宏文件才能证** —— 那要 "
            "`swCommands_StopMacro`（**弹 Save As**）⇒ ★ 本模块不去点它 ✓"
        ),
    }
    if sw_app is None:
        out["error"] = "sw_app 为 None"
        return out
    if not str(text or "").strip():
        out["error"] = "text 不能为空（★ 官方 Parameters 逐字：Text = 要写入的那行）"
        return out
    try:
        out["returned"] = get_com_member(sw_app, "RecordLine", str(text))
    except Exception as exc:  # noqa: BLE001
        out["error"] = "RecordLine 失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    out["ok"] = bool(out["returned"])
    if not out["ok"]:
        out["error"] = (
            "RecordLine 回 %r（官方 Returns 逐字：True = 成功）—— "
            "★ 也可能是**录制没开**（★ 见 precondition_note）" % out["returned"]
        )
    return out


def record_macro_lines(sw_app, lines) -> dict[str, Any]:
    """★ **成对地开关录制并写若干行**（★ 一次调用完成「开 → 写 → 停」）。

    ★★ **停录制走 `swCommands_RecordPauseMacro`(29) 这个切换，不走 `StopMacro`(31)** ——
      ★ 因为 31 **会弹 Save As**（见 :data:`STOP_MACRO_DIALOG_WARNING`）✓
    :param lines: 要写的行 —— 收 `list[str]` **或**换行分隔的字符串。
    :returns: `{ok, lines_written, open_returned, line_returns, close_returned,
        stop_macro_warning, error}`

    ★★ **判据（规则 6）**：★ 三个 `RunCommand`/`RecordLine` 的 **bool 都只是回报** ⇒
      ★ 本函数的 `ok` = **成对调用都回了 True 且每一行都回了 True**，
      ★ 并在返回值里**写明限度**：★ **"宏文件真的落了盘"证不了**（那要弹 Save As 的 31）✓
    """
    out: dict[str, Any] = {
        "ok": False,
        "entry_used": "RunCommand(29) → RecordLine × N → RunCommand(29)",
        "lines_written": 0,
        "open_returned": None,
        "line_returns": [],
        "close_returned": None,
        "stop_macro_warning": STOP_MACRO_DIALOG_WARNING,
        "error": None,
        "★": "判据 = **成对调用 + 逐行返回值都为 True**；★★ 但**「宏文件落了盘」证不了** —— "
        "那要 `swCommands_StopMacro`(31)，而它**弹 Save As** ⇒ 本模块**不点它** ✓",
    }
    if sw_app is None:
        out["error"] = "sw_app 为 None"
        return out
    if isinstance(lines, str):
        items = [x for x in lines.splitlines() if x.strip()]
    else:
        items = [str(x) for x in (lines or []) if str(x).strip()]
    if not items:
        out["error"] = "lines 为空 ⇒ 没有要写的行"
        return out
    opened = toggle_macro_recording(sw_app)
    out["open_returned"] = opened.get("returned")
    if not opened.get("ok"):
        out["error"] = "开录制失败：%s" % opened.get("error")
        return out
    try:
        for text in items:
            r = record_line(sw_app, text)
            out["line_returns"].append(bool(r.get("ok")))
        out["lines_written"] = sum(1 for x in out["line_returns"] if x)
    finally:
        #: ★★ 无论成功失败都要**把录制停掉**（否则 SW 会一直录着 —— ★ 那是留给用户的脏状
        #: 态）✓
        closed = toggle_macro_recording(sw_app)
        out["close_returned"] = closed.get("returned")
        if not closed.get("ok") and not out["error"]:
            out["error"] = "停录制失败：%s" % closed.get("error")
    out["ok"] = (
        bool(out["open_returned"])
        and bool(out["close_returned"])
        and out["lines_written"] == len(items)
    )
    if not out["ok"] and not out["error"]:
        out["error"] = "回读判据未过：开 %r · 逐行 %r · 停 %r" % (
            out["open_returned"],
            out["line_returns"],
            out["close_returned"],
        )
    return out


def run_macro(
    sw_app,
    file_path: str,
    module_name: str,
    procedure_name: str,
    *,
    options: int = RUN_MACRO_OPTIONS["default"],
) -> dict[str, Any]:
    """执行一个宏文件，返回**可 JSON 化**的结果（★ 不回 COM 对象）。

    ★ 判据（★ 与仓库其余「回读优先」一致）：★ **`ok` 取官方那个 bool 返回值**，
    ★★ 并**同时**带回 `Error` 出参 —— ★ 因为该 bool 在 pywin32 迟到绑定下**没有别的办法自证**
    （事实 40 那一族：返回值不可信的成员要让失败**可见**）✓

    :param sw_app: `ISldWorks`（★ 该成员在 **ISldWorks** 上，不是在 IModelDoc2 上）。
    :param file_path: 宏工程文件路径（`.swp` / `.swb` …）。
    :param module_name: 模块名（★ `.swp` 里就是 VBA 模块名；`.swb` 见 `## Remarks` 未查证）。
    :param procedure_name: 过程名（如 `main`）。
    :param options: `swRunMacroOption_e`（默认 0 = `swRunMacroDefault`）。
    :returns: `{ok, return_value, error_code, error_name, file, module, procedure, options}`
    """
    import os

    from .sw_connect import get_com_member, out_i4

    err_holder = out_i4()
    ret = None
    raised = None
    try:
        ret = get_com_member(
            sw_app,
            "RunMacro2",
            str(file_path),
            str(module_name),
            str(procedure_name),
            int(options),
            err_holder,
        )
    except Exception as exc:  # noqa: BLE001
        raised = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    code = None
    try:
        code = int(err_holder.value)
    except Exception:  # noqa: BLE001
        code = None
    return {
        "ok": bool(ret) and raised is None,
        "return_value": None if ret is None else bool(ret),
        "error_code": code,
        "error_name": _ERROR_NAME_BY_VALUE.get(code, "") if code is not None else "",
        "raised": raised,
        "file": os.path.basename(str(file_path)),
        "file_exists": os.path.isfile(str(file_path)),
        "module": str(module_name),
        "procedure": str(procedure_name),
        "options": int(options),
        "★": "★ `ok` = 官方 bool 返回值且**未抛异常**；★★ 失败原因看 `error_name`（★ 名字取自 "
        "`swRunMacroError_e`，两源一致）✓ ⚠ 该 bool 的**语义**官方页没写细（Remarks 为空）⇒ "
        "只回读数、不替官方下结论 ✓",
    }
