from pathlib import Path
p = Path(r"D:\AI\SW\shot.py")
s = p.read_text(encoding="utf-8")
# ctypes 默认把返回值当 32 位 int，GDI 句柄是 64 位 -> 需显式声明
s = s.replace("user32 = ctypes.windll.user32\ngdi32 = ctypes.windll.gdi32",
"""user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
# ⚠⚑ GDI/USER 句柄在 64 位下是 64 位，ctypes 默认按 32 位 int 返回
#   ⇒ 不显式声明 restype 就报 "int too long to convert"。
for _fn in ("GetWindowDC", "CreateCompatibleDC", "CreateCompatibleBitmap",
            "SelectObject", "DeleteObject", "DeleteDC", "ReleaseDC",
            "PrintWindow", "GetDIBits"):
    _f = getattr(gdi32, _fn, None) or getattr(user32, _fn, None)
    if _f is not None:
        _f.restype = ctypes.c_void_p
        _f.argtypes = [ctypes.c_void_p] * max(_f.argtypes and len(_f.argtypes) or 1, 1) \\
            if _fn in ("GetDIBits",) else [ctypes.c_void_p] * 6""")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已加 restype 声明")