from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_locate.py")
s = p.read_text(encoding="utf-8")
# ⚠ 正确模块名是 win32ui（我误写成 win32guiui）
s = s.replace("import win32guiui", "import win32ui")
s = s.replace("win32guiui.", "win32ui.")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已修 win32guiui -> win32ui")