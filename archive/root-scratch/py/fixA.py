import sys
from pathlib import Path
p = Path(r"D:\AI\SW\build_complete_index.py")
s = p.read_text(encoding="utf-8")
s = s.replace('def _require(obj, {{what}}: str', 'def _require(obj, what: str')
p.write_text(s, encoding="utf-8")
print("fixed")