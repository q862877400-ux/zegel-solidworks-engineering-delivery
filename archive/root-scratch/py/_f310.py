import sys
from pathlib import Path

K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact310.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
if "| 310 |" in tk:
    print("already")
else:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("wrote 310")
