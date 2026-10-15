from pathlib import Path
p = Path(r"D:\AI\SW\dbg_sb2.py")
s = p.read_text(encoding="utf-8")
s = s.replace("import sys, warnings", "import sys, time, warnings")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("fixed import")