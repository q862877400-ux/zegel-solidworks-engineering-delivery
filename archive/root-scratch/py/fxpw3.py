from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_locate.py")
lines = p.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines):
    if "bmp.GetHandle()" in ln:
        lines[i] = "    gdi32.DeleteObject(bmp)   # ctypes 句柄是 int，没有 GetHandle()"
        print("  改行", i + 1)
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
import ast; ast.parse("\n".join(lines))
print("ok")