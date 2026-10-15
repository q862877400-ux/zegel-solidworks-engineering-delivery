import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")

NEW = '''

def settle_residual_dialogs(target=None, *, settle_seconds=1.0, poll_ms=200):
    """★★★ **收尾专用**：轮询查残留模态框，**发现就点掉**，并把三件事分开报。

    :returns: `(found, dismissed, scanned)` —— **发现几个 / 点掉几个 / 扫过多少窗口**。

    ⚠⚠⚠ **为什么需要它**（2026-10-01 轮 169 的审计发现）：
    仓库里 **35 个脚本**都会"查残留模态框"，而其中 **34 个只查、不点掉** ——
    它们**打印一行**就继续 ⇒ ★ **若真的发现了弹窗，弹窗还在**，
    于是**下一轮（或同一轮的后续调用）就挂在那儿**（这正是轮 167 用户看到的情形）。
    ⇒ ★★ **"发现"和"处置"是两件事**：
    * `residual_dialogs()`  —— **只读**（可证伪性、测试用），**默认不点掉**；
    * `count_residual_dialogs()` —— **只读**且只报计数；
    * `settle_residual_dialogs()` —— ★ **收尾用：查 + 点掉**（本函数）；
    * `dismiss_residual_dialogs()` —— 只点掉，不报发现数。

    ★ 点掉的方式与其它函数一致：**`WM_COMMAND` + `IDOK`**（Win32 标准命令）——
    **不看按钮文本、不按坐标**。
    """
    found = 0
    dismissed = 0
    scanned = 0
    import time
    pid = _resolve_pid(target)
    deadline = time.time() + max(0.0, float(settle_seconds))
    while True:
        handles, total = _dialog_handles(pid)
        scanned = max(scanned, total)
        found = max(found, len(handles))
        for h in handles:
            import ctypes
            ctypes.windll.user32.PostMessageW(h, _WM_COMMAND, _IDOK, 0)
            dismissed += 1
        if time.time() >= deadline:
            break
        time.sleep(max(0.02, poll_ms / 1000.0))
    return found, dismissed, scanned
'''
if "def settle_residual_dialogs(" not in t:
    t = t.replace("def residual_dialogs(", NEW.strip() + "\n\n\ndef residual_dialogs(", 1)
    P.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("  ok settle_residual_dialogs 已加（轮询 + 点掉 + 三计数）")
else:
    print("  已有")
