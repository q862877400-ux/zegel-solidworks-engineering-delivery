from pathlib import Path
p = Path(r"D:\AI\SW\shot.py")
s = p.read_text(encoding="utf-8")
a = s.index("# ⚠⚑ GDI/USER 句柄")
b = s.index("SRCCOPY = 0x00CC0020")
s = s[:a] + '''# ⚠⚑ 64 位下 GDI/USER 句柄是 64 位；ctypes 的 restype/argtypes 默认按 32 位
#   ⇒ 不声明就报 "int too long to convert"。
#   逐个按**真实签名**声明（不要图省事统一套，那个会让调用错位）。
c_void_p = ctypes.c_void_p
c_int = ctypes.c_int
gdi32.CreateCompatibleDC.restype = c_void_p
gdi32.CreateCompatibleDC.argtypes = [c_void_p]
gdi32.CreateCompatibleBitmap.restype = c_void_p
gdi32.CreateCompatibleBitmap.argtypes = [c_void_p, c_int, c_int]
gdi32.SelectObject.restype = c_void_p
gdi32.SelectObject.argtypes = [c_void_p, c_void_p]
gdi32.DeleteObject.argtypes = [c_void_p]
gdi32.DeleteDC.argtypes = [c_void_p]
gdi32.GetDIBits.restype = c_int
gdi32.GetDIBits.argtypes = [c_void_p, c_void_p, c_uint, c_uint,
                            c_void_p, c_void_p, c_uint]
user32.GetWindowDC.restype = c_void_p
user32.GetWindowDC.argtypes = [c_void_p]
user32.ReleaseDC.argtypes = [c_void_p, c_void_p]
user32.PrintWindow.restype = ctypes.c_bool
user32.PrintWindow.argtypes = [c_void_p, c_void_p, c_uint]

''' + s[b:]
if "c_uint = ctypes.c_uint" not in s:
    s = s.replace("c_int = ctypes.c_int", "c_int = ctypes.c_int\nc_uint = ctypes.c_uint")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  逐函数精确声明已写入")