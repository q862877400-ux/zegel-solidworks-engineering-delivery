from pathlib import Path
p = Path(r"D:\AI\SW\win32be.py")
s = p.read_text(encoding="utf-8")
s = s.replace('out.stdout.split(",")[0).strip', 'out.stdout.split(",")[0].strip')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("fixed")