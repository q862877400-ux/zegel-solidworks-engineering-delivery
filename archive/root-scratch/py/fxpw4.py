from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_locate.py")
s = p.read_text(encoding="utf-8")
# ⚠ win32ui 只有 CreateDCFromHandle，没有 DeleteDC/DeleteObject —— 全走 gdi32
s = s.replace("    win32ui.DeleteDC(mem)\n    win32ui.DeleteDC(mfc)\n",
              "    gdi32.DeleteDC(mem)\n    gdi32.DeleteDC(mfc)\n")
# 并声明 DeleteDC
s = s.replace("    gdi32.DeleteDC.argtypes = [vp]",
              "    gdi32.DeleteDC.argtypes = [vp]\n    gdi32.DeleteDC.restype = c_void_p")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已统一到 gdi32")