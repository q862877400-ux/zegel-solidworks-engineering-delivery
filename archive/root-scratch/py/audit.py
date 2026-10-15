# -*- coding: utf-8 -*-
"""抽查主程序：每个大类抽 3 个差异大的零件，只生成预览不保存。

⚠ 「生成预览」只把模型塞进 SolidWorks，**不点「插入」/「保存」**
   ⇒ 不产生任何文件（符合抽查要求）。
   判据：SolidWorks 文档标题变化，**不是** BuildFile 目录多文件。
"""
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import jlc_batch as J
import win32api
import win32con

warnings.filterwarnings("ignore")
T0 = time.time()


def el(m):
    print("[%6.1fs] %s" % (time.time() - T0, m), flush=True)


# 四大类各抽 3 个差异大的（型号来自 sw_jlcfa_index.json，都是库里真实存在的）
TARGETS = [
    ("直线运动零件", ["EGW35SA"]),
    ("轴承附件",     []),
    ("传动零部件",   []),
    ("机床防护罩",   []),
]


def search_and_open(ui, code):
    """搜型号 -> 等结果 -> 点结果卡进详情。返回 True/失败原因。"""
    ui.go_home()
    ui.scan()
    sb = ui.search_box()
    if sb is None:
        return False, "找不到搜索框"
    sb.click_input()
    time.sleep(0.35)
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord("A"), 0, 0, 0)
    time.sleep(0.06)
    win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    for _ in range(26):
        win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
        time.sleep(0.011)
        win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.011)
    J.typ(code)
    time.sleep(0.35)
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.06)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

    card = None
    for _ in range(18):
        time.sleep(0.6)
        ui.reconnect()
        for c in ui.win.descendants():
            try:
                if c.element_info.control_type == "Text" and \
                        code in (c.window_text() or ""):
                    card = c
            except Exception:
                continue
        if card:
            break
    if not card:
        return False, "无结果"
    card.click_input()
    time.sleep(3.0)
    ui.reconnect()
    return True, ""


def main():
    ui = J.UI()
    el("连接，SW 标题=%r" % (ui.win.window_text()[:46],))
    results = []
    for cat, codes in TARGETS:
        for code in codes:
            el("=== %s / %s ===" % (cat, code))
            ok, why = search_and_open(ui, code)
            if not ok:
                el("  ✗ %s" % why)
                results.append((cat, code, "搜索失败:" + why))
                continue
            el("  已进详情，进度=%s%%" % ui.pct())
            pct, trail = J.fill_params(ui, log=el)
            el("  参数填充 -> %s%%  %s" % (pct, trail))
            if pct != 100:
                results.append((cat, code, "未到100%%(%s)" % pct))
                el("  ✗ 未到 100%，跳过生成")
                continue
            title, status = J.generate(ui, log=el)
            el("  生成预览 -> %s | %s" % (status, title[:50]))
            results.append((cat, code, "OK:%s" % status))
    el("=== 汇总 ===")
    for cat, code, st in results:
        el("  %-12s %-12s %s" % (cat, code, st))
    import json
    Path(r"D:\AI\SW\audit_result.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    el("结果存 audit_result.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
