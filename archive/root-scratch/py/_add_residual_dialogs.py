import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")

ANCHOR = "def get_com_member_raw(obj, attr_name):"
ADD = '''def residual_dialogs(pid, *, only_visible=False):
    """★★ 数某个进程的**残留模态框**（Win32 类名 `#32770`）—— **可证伪**版。

    :param pid: 目标进程 ID（SolidWorks 的）。
    :param only_visible: ⚠⚠ **默认 `False`** —— 见下。
    :returns: `(dialogs, all_windows)`：前者是 `#32770` 的标题列表，
        后者是**扫到的全部顶层窗口数**（用于判断这次扫描**有没有真的扫到东西**）。

    ⚠⚠⚠ **为什么要返回 `all_windows`**（2026-10-01 轮 148 查出的一个真问题）：
    此前本仓库在 **21 个工具**里各复制了一份"查残留模态框"的代码，
    **每份都带 `IsWindowVisible(h)` 过滤**。而本轮实测：
    ```
    PID 20456 的顶层窗口 **49 个，全部 IsWindowVisible == 0**（SolidWorks 主框架不可见）
    ⇒ 那个过滤让**枚举结果恒为空** ⇒ 检查**永远报「无残留」** ⇒ **一个不可能失败的门禁**
    ```
    ⇒ ★ 所以本函数**默认不过滤可见性**，并**把 `all_windows` 一并返回** ——
    调用方应当**先看 `all_windows > 0`** 再相信 `dialogs` 为空（否则是"没扫到"，不是"没有"）。

    ⚠ 这与已知事实 62/79/81 同族（**"绿"不等于"对"**），但更严重：
    它守的是**每轮收尾的安全底线**（模态框会把会话永久挂起）。
    """
    import ctypes
    import ctypes.wintypes as _w
    u = ctypes.windll.user32
    dialogs: list = []
    total = [0]

    @ctypes.WINFUNCTYPE(ctypes.c_bool, _w.HWND, _w.LPARAM)
    def cb(h, _l):      # noqa: ANN001
        p = _w.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value != pid:
            return True
        if only_visible and not u.IsWindowVisible(h):
            return True
        total[0] += 1
        cls = ctypes.create_unicode_buffer(128)
        u.GetClassNameW(h, cls, 128)
        if cls.value == "#32770":
            txt = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, txt, 256)
            dialogs.append(txt.value)
        return True

    u.EnumWindows(cb, 0)
    return dialogs, total[0]


'''
if "def residual_dialogs(" not in t:
    assert ANCHOR in t, "锚点不符"
    t = t.replace(ANCHOR, ADD + ANCHOR, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 residual_dialogs（共享、可证伪）")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

#: ★★ 立刻验证：**它不空**（能扫到 49 个窗口）—— 这是"不空即非门禁空转"的证据
sys.path.insert(0, str(Path(r"C:\swprojects\sw-skill-fork\scripts")))
sys.path.insert(0, str(Path(r"C:\swprojects\sw-skill-fork")))
import importlib
sc = importlib.import_module("scripts.sw_connect") if False else None
import sw_connect
sc = sw_connect
d_all, n_all = sc.residual_dialogs(20456)
d_vis, n_vis = sc.residual_dialogs(20456, only_visible=True)
print()
print("  默认（不过滤可见性）: #32770 = %d 个 · 扫到窗口 **%d** 个" % (len(d_all), n_all))
print("  旧口径（只可见）    : #32770 = %d 个 · 扫到窗口 **%d** 个  ← ★ 恒为 0" % (len(d_vis), n_vis))
