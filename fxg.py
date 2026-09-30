from pathlib import Path
p = Path(r"D:\AI\SW\sw_gui.py")
s = p.read_text(encoding="utf-8")
# ① 去掉那行没意义的占位赋值
s = s.replace("                win32process.AttachThreadInputSafe = None      # 占位，见下\n", "")
# ② 顶层只 import 用到的东西
s = s.replace("    import ctypes\n    from ctypes import wintypes\n    from PIL import Image\n",
              "    from PIL import Image\n")
s = s.replace("    from PIL import Image\n\n    left, top, right, bottom = _window_rect(hwnd)",
              "    from PIL import Image\n\n    left, top, right, bottom = _window_rect(hwnd)")
# ③ 把 win32 helper 收进函数内联，去掉一地散装函数
old = s[s.index("# ── win32 句柄小工具"):]
new = '''# ── win32 句柄小工具（内联，保持模块只有一个公开面）──────────────────
def _dc_for(hwnd: int):
    """建 PrintWindow 需要的四个 GDI 句柄，返回 (mfcDC, saveDC, bmp, w, h)。"""
    import win32gui
    import win32guiui
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32guiui.CreateDCFromHandle(hwndDC)
    saveDC = win32guiui.CreateCompatibleDC(mfcDC)
    bmp = win32guiui.CreateCompatibleBitmap(mfcDC, w, h)
    win32guiui.SelectObject(saveDC, bmp)
    return hwndDC, mfcDC, saveDC, bmp, w, h
'''
s = s.replace(old, new)
# capture_window 改用 _dc_for
s = s.replace('''    hwndDC = win32gui_GetWindowDC(hwnd)
    mfcDC = win32gui_CreateDCFromHandle(hwndDC)
    saveDC = win32gui_CreateCompatibleDC(mfcDC)
    bmp = win32gui_CreateCompatibleBitmap(mfcDC, w, h)
    win32gui_SelectObject(saveDC, bmp)
''', '''    hwndDC, mfcDC, saveDC, bmp, w, h = _dc_for(hwnd)
''')
s = s.replace('''    win32gui_DeleteObject(bmp.GetHandle())
    win32gui_DeleteDC(saveDC)
    win32gui_DeleteDC(mfcDC)
    win32gui_ReleaseDC(hwnd, hwndDC)
''', '''    import win32gui
    import win32guiui
    win32guiui.DeleteObject(bmp.GetHandle())
    win32guiui.DeleteDC(saveDC)
    win32guiui.DeleteDC(mfcDC)
    win32gui.ReleaseDC(hwnd, hwndDC)
''')
s = s.replace('''    from PIL import Image

    left, top, right, bottom = _window_rect(hwnd)
    w, h = right - left, bottom - top
''', '''    from PIL import Image

''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已清理")