from pathlib import Path
p = Path(r"D:\AI\SW\pyw.py")
s = p.read_text(encoding="utf-8")
s = s.replace("from pywinauto import UIAWrapper",
              "from pywinauto.application import Application  # 0.6.x 用 Application(backend='uia')\n"
              "import pywinauto")
s = s.replace('w = UIAWrapper(hwnd)          # ← UIA 后端，不是 win32 后端',
              'app = Application(backend="uia").connect(handle=hwnd)\n'
              'w = app.window(handle=hwnd)   # ← UIA 后端（不是 win32），能按控件语义操作')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  改用 Application(backend='uia')")