from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_locate.py")
s = p.read_text(encoding="utf-8")
# ⚠ ctypes 返回的是 int 句柄，没有 .GetHandle()（那是 pywin32 的对象）
s = s.replace("    win32ui.DeleteObject(bmp.GetHandle())", "    gdi32.DeleteObject(bmp)")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已修 DeleteObject(bmp.GetHandle()) -> gdi32.DeleteObject(bmp)")