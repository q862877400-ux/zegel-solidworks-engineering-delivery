# -*- coding: utf-8 -*-
"""A 验证：GUI 自动化能不能识别 SolidWorks 的控件树。

⚠ 本轮**只读**：
  · 不建文档、不点任何按钮、不发 COM 建模调用
  · 只启动 SolidWorks + 枚举窗口与控件 + 截图
  · 结束 ExitApp，不留进程
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(r"D:\AI\SW\shots")
OUT.mkdir(exist_ok=True)


def main() -> int:
    import win32com.client as w32
    print("  ① 启动 SolidWorks（不加载任何插件操作）")
    app = w32.dynamic.Dispatch("SldWorks.Application")
    for _ in range(60):
        try:
            _ = app.RevisionNumber
            break
        except Exception:
            time.sleep(1)
    print("     版本:", app.RevisionNumber)
    try:
        app.Visible = True          # GUI 自动化需要真实窗口
        print("     窗口已显示")
    except Exception as e:
        print("     显示失败:", str(e)[:50])

    time.sleep(3)
    try:
        print()
        print("  ② 窗口枚举（win32gui）")
        import win32gui
        found = []

        def cb(h, _):
            if win32gui.IsWindowVisible(h):
                t = win32gui.GetWindowText(h)
                if t and ("SOLIDWORKS" in t.upper() or "SolidWorks" in t):
                    found.append((h, t, win32gui.GetWindowRect(h)))
        win32gui.EnumWindows(cb, None)
        for h, t, r in found[:6]:
            print("     hwnd=%-10d %-40s %s" % (h, t[:38], r))
        if not found:
            print("     ** 没找到 SolidWorks 主窗口 **")

        print()
        print("  ③ UI 树探测（uiautomation）—— 这是能点的前提")
        import uiautomation as auto
        for h, t, _r in found[:2]:
            print("     窗口 %r" % t[:30])
            try:
                w = auto.ControlFromHandle(h)
                w.SetActive()
                time.sleep(0.6)
                tree = w.GetChildren()
                print("       直接子控件 %d 个" % len(tree))
                for c in tree[:8]:
                    print("         %-22s %-20s rect=%s" % (
                        c.ControlTypeName[:20], c.Name[:18], c.BoundingRectangle))
            except Exception as e:
                print("       探测失败:", str(e)[:60])

        print()
        print("  ④ 截图取证")
        if found:
            h = found[0][0]
            try:
                import win32ui
                from PIL import ImageGrab
                img = ImageGrab.grab(bbox=found[0][2])
                p = OUT / "sw_window.png"
                img.save(p)
                print("     存到", p, img.size)
            except Exception as e:
                print("     截图失败:", str(e)[:60])
        return 0
    finally:
        try:
            app.CommandInProgress = False
        except Exception:
            pass
        try:
            app.ExitApp()
            print("\n  收尾: ExitApp（无残留进程）")
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
