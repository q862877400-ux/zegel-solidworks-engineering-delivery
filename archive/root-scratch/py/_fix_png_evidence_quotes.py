import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\_add_png_evidence.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
for i, l in enumerate(lines):
    if '"窗口 vs 绘图区"' in l:
        lines[i] = l.replace('"窗口 vs 绘图区"', "「窗口 vs 绘图区」")
        print("  L%d 已修" % (i + 1))
P.write_text("".join(lines), encoding="utf-8")
ast.parse("".join(lines))
print("  语法 OK")
