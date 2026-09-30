from pathlib import Path
p = Path(r"D:\AI\SW\modal.py")
s = p.read_text(encoding="utf-8")
s = s.replace("import win32gui\nfrom pywinauto import Application",
              "import win32gui\nimport win32process\nfrom pywinauto import Application")
s = s.replace("win32gui.GetWindowThreadProcessId", "win32process.GetWindowThreadProcessId")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("fixed: GetWindowThreadProcessId 来自 win32process")