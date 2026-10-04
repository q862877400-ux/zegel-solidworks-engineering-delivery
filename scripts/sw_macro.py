"""★ 宏执行：`ISldWorks.RunMacro2`（★ 规格 202 的 FR-008「宏/VBA 执行」那一半）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）+ 官方结构化页
# 文件:   `C:\swapi\types\ISldWorks\RunMacro2.md` —— 官方签名**四个入参 + 一个 out**：
#             System.bool RunMacro2( String FilePathName, String ModuleName,
#                                   String ProcedureName, Int32 Options, out Int32 Error )
#         `C:\swapi\enums\swRunMacroOption_e.md`（2 成员）·
#         `C:\swapi\enums\swRunMacroError_e.md`（28 成员）·
#         `_raw\enum_values_sldworks.txt`（出厂反射，**与官方页逐条一致**）
# 定位:   宏执行域此前**完全空白** —— 实测 `capabilities.yaml` 里没有一条与 `RunMacro` 有关；
#         `scripts/sw_macro_guard.py` 只做**生成 / 校验 / 落盘** VBA 文本，**不执行**。
#         ★ 规格 202 的 FR-008 逐字要求「**宏/VBA 执行** MUST 可用」⇒ 本模块补的就是它。
# ⚠ 官方 `## Remarks` 对本机版本**是空的**（该页 Remarks 段无内容）⇒ 本模块不替它补语义，
#   只按签名与枚举调用；语义未证之处一律标注「未查证」。
# ⚠ `swRunMacroOption_e` / `swRunMacroError_e` 的**两套源逐条一致**（官方页 == 出厂反射）✓
#   ★ 顺带更正仓库一处旧记载：`scripts/sw_com_traps.py` 写「`swRunMacroError_e` **不在官方
#     interop 类型库中**」——★ 实测**在**（反射里 28 个成员齐全），该句已过时（见事实 531）。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any

#: `swRunMacroOption_e` —— 两源一致（官方页表格 == 出厂反射）
RUN_MACRO_OPTIONS = {
    "default": 0,              # swRunMacroDefault
    "unload_after_run": 1,     # swRunMacroUnloadAfterRun
}

#: `swRunMacroError_e` —— **全 28 个成员**，★ 两源**按成员逐一比对一致**
#:   （实测：官方页 28 个 == 出厂反射 28 个，`{成员: 值}` 字典相等；**只有排列顺序不同**）✓
RUN_MACRO_ERRORS = {
    "InvalidArg": 1, "MacrosAreDisabled": 2, "NotInDesignMode": 3, "OnlyCodeModules": 4,
    "OutOfMemory": 5, "InvalidProcname": 6, "InvalidPropertyType": 7, "SuborfuncExpected": 8,
    "BadParmCount": 9, "BadVarType": 10, "UserInterrupt": 11, "Exception": 12,
    "Overflow": 13, "TypeMismatch": 14, "ParmNotOptional": 15, "UnknownLcid": 16,
    "Busy": 17, "ConnectionTerminated": 18, "CallRejected": 19, "CallFailed": 20,
    "Zombied": 21, "Invalidindex": 22, "NoPermission": 23, "Reverted": 24,
    "TooManyOpenFiles": 25, "DiskError": 26, "CantSave": 27, "OpenFileFailed": 28,
}
_ERROR_NAME_BY_VALUE = {v: k for k, v in RUN_MACRO_ERRORS.items()}


def run_macro(sw_app, file_path: str, module_name: str, procedure_name: str,
              *, options: int = RUN_MACRO_OPTIONS["default"]) -> dict[str, Any]:
    """执行一个宏文件，返回**可 JSON 化**的结果（★ 不回 COM 对象）。

    ★ 判据（★ 与仓库其余"回读优先"一致）：★ **`ok` 取官方那个 bool 返回值**，
    ★★ 并**同时**带回 `Error` 出参 —— ★ 因为该 bool 在 pywin32 迟到绑定下**没有别的办法自证**
    （事实 40 那一族：返回值不可信的成员要让失败**可见**）✓

    :param sw_app: `ISldWorks`（★ 该成员在 **ISldWorks** 上，不是在 IModelDoc2 上）。
    :param file_path: 宏工程文件路径（`.swp` / `.swb` …）。
    :param module_name: 模块名（★ `.swp` 里就是 VBA 模块名；`.swb` 见 `## Remarks` 未查证）。
    :param procedure_name: 过程名（如 `main`）。
    :param options: `swRunMacroOption_e`（默认 0 = `swRunMacroDefault`）。
    :returns: `{ok, return_value, error_code, error_name, file, module, procedure, options}`
    """
    from .sw_connect import get_com_member, out_i4
    import os

    err_holder = out_i4()
    ret = None
    raised = None
    try:
        ret = get_com_member(sw_app, "RunMacro2", str(file_path), str(module_name),
                             str(procedure_name), int(options), err_holder)
    except Exception as exc:                                   # noqa: BLE001
        raised = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    code = None
    try:
        code = int(err_holder.value)
    except Exception:                                          # noqa: BLE001
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
