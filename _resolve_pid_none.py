import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① `_resolve_pid(None)` ⇒ 自己连 COM 派生（零硬编码、零调用点负担）──
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")
OLD = '''def _resolve_pid(target):
    """`target` 可以是 `ISldWorks`（**自动派生 PID**）或 `int`（显式 PID）。"""
    if isinstance(target, int):
        return target
    return solidworks_process_id(target)'''
NEW = '''def _resolve_pid(target=None):
    """把 `target` 解析成 PID —— **三种来源，全部零硬编码**。

    * `ISldWorks` 对象 ⇒ `solidworks_process_id(sw)`（官方 `GetProcessID()`）
    * `int` ⇒ 直接用（**调用方明确给了就用它**，不覆盖）
    * `None`（**默认**）⇒ ★ **本函数自己连上正在运行的 SolidWorks 再派生**
      ⇒ 这样调用方**不必**知道 PID，也**不必**先拿到 `sw`：
      `residual_dialogs()` / `dismiss_residual_dialogs()` 无参调用即可。

    ⚠⚠⚠ **为什么要有 `None` 这条**（2026-10-01 轮 167）：此前 **36 处**工具里写死
    `SW_PID = 20456` 再传给 `residual_dialogs(SW_PID)` —— **硬编码**，
    换机器 / 换会话 / SolidWorks 重启后**全部失效**，而失效的表现是
    「**查不到残留模态框**」⇒ **一个静默失效的安全检查**（比没有更糟）。
    """
    if target is None:
        import win32com.client
        return int(win32com.client.GetActiveObject("SldWorks.Application").GetProcessID())
    if isinstance(target, int):
        return target
    return solidworks_process_id(target)'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
#: 两个公开函数的签名默认值也要跟上
t = t.replace("def dismiss_residual_dialogs(target, *, settle_seconds=0.0, poll_ms=200):",
              "def dismiss_residual_dialogs(target=None, *, settle_seconds=0.0, poll_ms=200):", 1)
t = t.replace("def count_residual_dialogs(target, *, settle_seconds=0.0, poll_ms=200):",
              "def count_residual_dialogs(target=None, *, settle_seconds=0.0, poll_ms=200):", 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok ① _resolve_pid(None) 自己连 COM 派生")
