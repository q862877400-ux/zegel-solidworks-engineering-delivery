from pathlib import Path
import re
p = Path(r"D:\AI\SW\shot.py")
s = p.read_text(encoding="utf-8")
start = s.index("# ⚠⚑ GDI/USER 句柄")
end = s.index("SRCCOPY = 0x00CC0020")
s = s[:start] + '''# ⚠⚑ GDI/USER 句柄在 64 位下是 64 位，ctypes 默认按 32 位 int 返回
#   ⇒ 不显式声明 restype 就报 "int too long to convert"。
#   ⚠ 只改 restype，不设 argtypes —— 各函数参数个数不同，
#   统一套 argtypes 会让调用错位（GetDIBits 6 参 vs CreateCompatibleDC 1 参）。
for _mod, _names in ((gdi32, ("CreateCompatibleDC", "CreateCompatibleBitmap",
                              "SelectObject", "DeleteObject", "DeleteDC", "GetDIBits")),
                     (user32, ("GetWindowDC", "ReleaseDC", "PrintWindow"))):
    for _n in _names:
        getattr(_mod, _n).restype = ctypes.c_void_p

''' + s[end:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  只设 restype，不碰 argtypes")