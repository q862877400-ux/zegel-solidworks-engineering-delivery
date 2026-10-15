from pathlib import Path
p = Path(r"D:\AI\SW\tap.py")
s = p.read_text(encoding="utf-8")
s = s.replace('sys.path.insert(0, r"D:\\AI\\SW")',
              'sys.path.insert(0, r"D:\\AI\\SW")\nsys.path.insert(0, r"C:\\swprojects\\sw-skill-fork\\scripts")')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("path fixed")