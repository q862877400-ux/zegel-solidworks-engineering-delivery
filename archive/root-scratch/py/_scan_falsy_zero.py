"""查 `or <默认值>` 的「零值被吞」bug 家族（本文件 + 全仓同款写法）。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")

#: 形态：`get_com_member(x, "Y") or <默认>` —— Y 若是**可能为 0 的数值**就中招
PAT = re.compile(r'([A-Za-z_][\w.]*)\s*,\s*"(\w+)"\s*\)\s*or\s+(-?\d+(?:\.\d+)?)')

files = [REPO / "scripts" / "sw_costing.py"]
files += sorted((REPO / "scripts").glob("sw_*.py"))
seen = set()
print("  扫 %d 个模块，找 `... or <数值>` 形态：" % len(files))
hits = []
for f in files:
    if f in seen:
        continue
    seen.add(f)
    txt = f.read_text(encoding="utf-8", errors="replace")
    for m in PAT.finditer(txt):
        ln = txt[:m.start()].count("\n") + 1
        hits.append((f.name, ln, m.group(0).strip(), m.group(2), m.group(3)))
print()
if not hits:
    print("  （无命中）")
for name, ln, txt, member, default in hits:
    # `or 0` 对 0 是幂等的（0 or 0 = 0）⇒ 无害；`or -1` / `or 0.0` 才有害
    harm = "⚠ **有害**（0 是合法值）" if default not in ("0",) else "（`or 0` 对 0 幂等 ⇒ 无害）"
    print("  %-22s L%-5d %-62s 默认=%s  %s" % (name, ln, txt[:60], default, harm))
