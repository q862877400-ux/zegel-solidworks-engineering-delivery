import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
body = (W / "_fact152.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
if "| 152 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("  ok known-facts 已加 152")
else:
    print("  152 已在")
print("  核对（精确）:", "| 152 |" in K.read_text(encoding="utf-8"))
