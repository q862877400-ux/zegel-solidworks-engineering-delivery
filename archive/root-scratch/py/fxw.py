from pathlib import Path
p = Path(r"D:\AI\SW\jlc_auto.py")
s = p.read_text(encoding="utf-8")
add = '''

def wheel(x: int, y: int, clicks: int = -3, pause: float = 0.4) -> None:
    """真滚轮事件（MOUSEEVENTF_WHEEL）。

    ⚠⚑ **不能用拖动代替滚轮**（2026-09-30 实测）：拖动只是移动光标，
    WinForms 的 Panel 不会滚动 —— 截图字节数完全一样，内容零变化。
    """
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.2)
    for _ in range(abs(clicks)):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0,
                             clicks * 120, 0)
        time.sleep(0.12)
    time.sleep(pause)
'''
s = s.replace("def find_node(", add + "\n\ndef find_node(")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已加 wheel()")