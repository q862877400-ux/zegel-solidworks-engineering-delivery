# -*- coding: utf-8 -*-
"""模态弹窗检测器 —— 解决「看不见弹窗导致所有操作白做」。

⚑⚑ 为什么之前检测不到（三个原因叠加）
# ----------------------------------------
# ① **PrintWindow 只抓窗口自身**，客户区之外的独立顶层浮窗**全部丢失**。
#    插件的提示框就是这种浮窗 ⇒ 我截的每张图里都没有它。
#    ⇒ 取证必须用 ``ImageGrab.grab()``（整屏），不是 PrintWindow。
# ② 我只枚举「标题含 SOLIDWORKS」或「进程名 sldworks.exe」的窗口，
#    而插件模态框**标题为空** ⇒ 两道过滤都漏掉。
#    ⇒ 检测**不能依赖标题或进程名**，要看**窗口结构特征**。
# ③ 最要命：我点完从不验「是否生效」，把「被弹窗拦住」误判成
#    「下拉选不中」，连续九轮都在错因上打转。
#    ⇒ 每个动作后必须断言结果。
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
import win32gui
import win32process
from pywinauto import Application

warnings.filterwarnings("ignore")


def owner_pids(hwnd):
    """一个窗口及其所有后代的 PID 集合（模态框常是独立顶层窗但属同进程）。"""
    pids = set()
    stack = [hwnd]
    while stack:
        cur = stack.pop()
        pid = win32process.GetWindowThreadProcessId(cur)[1]
        if pid in pids:
            continue
        pids.add(pid)
        kids = []
        try:
            win32gui.EnumChildWindows(cur, lambda h, _: kids.append(h) or True, None)
        except Exception:
            pass
        stack.extend(kids)
    return pids


def find_modals(main_hwnd) -> list[dict]:
    """找出**属于同一进程、但独立于主窗口**的可见顶层窗 = 候选模态框。

    ⚠ 不看标题、不看尺寸大小 —— 插件的提示框标题为空。
    """
    main_pid = win32process.GetWindowThreadProcessId(main_hwnd)[1]
    out = []

    def cb(h, _):
        if h == main_hwnd or not win32gui.IsWindowVisible(h):
            return
        pid = win32process.GetWindowThreadProcessId(h)[1]
        if pid != main_pid:
            return
        r = win32gui.GetWindowRect(h)
        title = win32gui.GetWindowText(h)
        cls = win32gui.GetClassName(h)
        # 主窗口的兄弟工具窗（如调色板）也会命中，靠「非主窗口 + 有一定尺寸」粗筛
        w, ht = r[2] - r[0], r[3] - r[1]
        if w < 60 or ht < 40:
            return
        out.append({"hwnd": h, "title": title, "cls": cls, "rect": r,
                    "owner": win32gui.GetWindow(h, 4)})   # GW_OWNER

    win32gui.EnumWindows(cb, None)
    return out


def modal_report(main_hwnd) -> dict:
    """给一份「有没有东西挡着」的体检报告。"""
    ms = find_modals(main_hwnd)
    # 有 owner 的通常是真正的对话框
    dialogs = [m for m in ms if m["owner"]]
    return {"total_siblings": len(ms), "dialogs": dialogs, "all": ms}


def screen_png(path):
    """★ 取证一律用整屏 —— PrintWindow 会丢客户区外的浮窗。"""
    from PIL import ImageGrab
    img = ImageGrab.grab()
    img.save(path)
    return img


if __name__ == "__main__":
    # 自检：当前有没有模态框
    import ctl
    hwnd, win = ctl.connect()
    rep = modal_report(hwnd)
    print("同进程独立顶层窗: %d 个，其中对话框 %d 个"
          % (rep["total_siblings"], len(rep["dialogs"])))
    for d in rep["dialogs"][:8]:
        print("   hwnd=%-9d owner=%-9d cls=%-22s title=%r rect=%s"
              % (d["hwnd"], d["owner"], d["cls"][:20], d["title"][:24], d["rect"]))
    if rep["all"]:
        print()
        print("  全部兄弟窗（含非对话框）:")
        for d in rep["all"][:10]:
            print("   hwnd=%-9d owner=%-9d cls=%-22s title=%r"
                  % (d["hwnd"], d["owner"], d["cls"][:20], d["title"][:24]))
