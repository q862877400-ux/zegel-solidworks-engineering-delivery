"""只读诊断：`GetAddInObject('SldWorks.Simulation')` 为什么返回 None。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（只读诊断）+ SolidWorks 官方 API 文档
# 文件:   `scripts/sw_simulation.py` 的 `get_cw_document`（被测入口）
# 官方签名依据:
#   · `C:\\swapi\\types\\ISldWorks\\GetAddInObject.md`：「Clsid = **GUID or ProgID**…
#     a GUID, use curly brackets as in "{GUID}", or the string is interpreted as a ProgID」
#   · `LoadAddIn.md`：`FileName` = **fully qualified file name**；返回 `swLoadAddinError_e`；
#     特例「You cannot load MBD using its add-in path… swApp.LoadAddIn('MBD')」
# 定位:   轮 51 真机跑 T-007 探针时撞到 `GetAddInObject(...) 返回 None`，
#         而 **003 的证据（2026-09-30）里同一个调用是成功的**（T-001 记「✓」）
#         ⇒ 需要分清是「**加载项没注册**」还是「**注册了但没启用**」还是「**ProgID 写错**」。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **只读**：不 `LoadAddIn`（那会改会话状态）、不动注册表、不写模型。
# ⚠ 铁律 2：`CommandInProgress = True` 抑制弹窗；收尾恢复。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

import win32com.client as win32  # noqa: E402
import pythoncom  # noqa: E402

T0 = time.time()


def log(m: str) -> None:
    print("  [%5.2fs] %s" % (time.time() - T0, m))


#: 候选 ProgID（`GetAddInObject` 的 clsid 参数）。第一个是**本项目一直在用的**那个，
#: 且它在 `sw_simulation.py` 里**自己标着「待二次确认」** ⇒ 一并试几个近邻名字。
CANDIDATES = (
    "SldWorks.Simulation",
    "SldWorks.SimulationWorks",
    "COSMOSWorks.CosmosWorks",
    "SldWorks.CosmosWorks",
    "SldWorks.Simulation.2026",
)


def main() -> int:
    pythoncom.CoInitialize()
    sw = win32.GetActiveObject("SldWorks.Application")
    log("revision = %s" % sw.RevisionNumber)

    sw.CommandInProgress = True
    try:
        # ① 先看 SolidWorks **自己报的**加载项列表（最权威的「注册没注册」判据）
        try:
            n = sw.GetAddInCount()
            log("GetAddInCount() = %r" % n)
            for i in range(int(n or 0)):
                info = sw.GetAddInInfo(i)
                log("  [%d] %r" % (i, (str(info)[:140],)))
        except Exception as exc:  # noqa: BLE001
            log("⚠ GetAddInCount/Info 取不到: %s: %s" % (type(exc).__name__, str(exc)[:110]))

        # ② 再逐个试候选 ProgID
        print()
        log("── GetAddInObject 逐个候选 ──")
        for pid in CANDIDATES:
            try:
                obj = sw.GetAddInObject(pid)
                log("  %-32s ⇒ %s" % (pid, "✓ 非 None" if obj is not None else "None"))
            except Exception as exc:  # noqa: BLE001
                log("  %-32s ⇒ 异常 %s: %s" % (pid, type(exc).__name__, str(exc)[:90]))
    finally:
        sw.CommandInProgress = False
        log("已恢复 CommandInProgress = False")
        pythoncom.CoUninitialize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
