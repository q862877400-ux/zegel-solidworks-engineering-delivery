from pathlib import Path
p = Path(r"D:\AI\SW\jlc_auto.py")
s = p.read_text(encoding="utf-8")
guard = '''

def ensure_window(hwnd: int) -> tuple:
    """★ 护栏：每次操作前确认窗口**没被最小化、尺寸正常**。

    ⚠⚑ 加这条的原因（2026-09-30 实测踩坑）：
    早先 refresh_pane() 拖动幅度过大，**把 SolidWorks 拖到最小化**，
    窗口 rect 变成 (-32000,-32000,-31801,-31966)（Win32 最小化的固定坐标），
    之后所有点击都落在屏幕外 —— 表现为「点搜索框没反应」，
    实则是窗口根本不在屏幕上。**症状离原因很远**，只能靠状态断言拦住。
    """
    import win32con
    if win32gui.IsIconic(hwnd):
        log("  [护栏] 窗口已最小化 -> 恢复")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(1.2)
    r = win32gui.GetWindowRect(hwnd)
    w, h = r[2] - r[0], r[3] - r[1]
    if w < 600 or h < 400 or r[0] < -100:
        raise RuntimeError(
            "窗口状态异常 rect=%s 尺寸=%dx%d —— 拒绝操作（可能又被最小化/移出屏幕）" % (r, w, h))
    return r
'''
s = s.replace("def click(x: int, y: int", guard + "\n\ndef click(x: int, y: int")
# refresh_pane 改成小幅度、只拖分隔条附近
s = s.replace('''    r = rect
    # 面板左边缘（标签列左侧）来回拖一下
    x_edge = r.left - 4
    drag(x_edge, r.top + 40, x_edge - 120, r.top + 60, steps=10)
    drag(x_edge - 120, r.top + 60, x_edge, r.top + 40, steps=10)
    log("  已拖动面板（刷新卡住的内容）")''',
'''    # ⚠⚑ 幅度必须小：早先拖 120px 把整个 SolidWorks 窗口拖到最小化了。
    #   只在**标签列左边缘**做 30px 往返，不碰标题栏、不跨出面板。
    r = rect
    x_edge = max(r.left - 2, 1)
    y_mid = r.top + 60
    drag(x_edge, y_mid, x_edge - 30, y_mid, steps=8)
    drag(x_edge - 30, y_mid, x_edge, y_mid, steps=8)
    log("  已拖动面板（30px 小幅度，刷新卡住的内容）")''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已加 ensure_window 护栏 + 缩小拖动幅度")