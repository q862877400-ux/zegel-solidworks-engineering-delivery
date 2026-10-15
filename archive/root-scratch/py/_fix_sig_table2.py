import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\signature-audit.md")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
#: 精确定位 L508 那行（5 列表，紧跟在 sw_topology 49 之后）
for i, l in enumerate(lines):
    if l.startswith("| `sw_simulation.py` | 44 | **44** | 0 | 0 |"):
        lines[i] = "| `sw_simulation.py` | 45 | **45** | 0 | 0 |\n"
        print("  ✓ L%d 已改 44 → 45" % (i + 1))
        break
else:
    print("  ⚠ 没找到 5 列那一行")
P.write_text("".join(lines), encoding="utf-8")
print("  语法无关（markdown）")
