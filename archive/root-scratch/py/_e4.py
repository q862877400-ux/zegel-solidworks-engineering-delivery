import sys, io, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = Path(r"D:\AI\SW\_raw\enum_sldworks.txt")
txt = p.read_text(encoding="utf-8", errors="replace")
print("  文件大小 =", len(txt))
print("  前 8 行:")
for l in txt.splitlines()[:8]:
    print("    |", l[:100])
