import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
t = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md").read_text(encoding="utf-8")
seg = t[t.index("## 真缺"):]
rows = dict(re.findall(r"(?m)^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|", seg))

#: 本会话确实补过的（有 spec 目录为证）
FILLED = {
    "helix": "023-helix-from-true-missing",
    "sketch_chamfer": "024-sketch-edit-from-true-missing",
    "equation": "028-equations-from-true-missing",
    "convert_entities": "034-convert-entities",
    "bbox": "046-bbox-and-the-approximate-warning",
    "ellipse": "051-ellipse-and-the-unit-correction",
}
print("  真缺表里这些名字的现状：")
for k, spec in FILLED.items():
    hit = [n for n in rows if k in n]
    for n in hit:
        print("    %-34s 表里写的是 %-8r ← 实际已有 %s" % (n, rows[n][:8], spec))
    if not hit:
        print("    %-34s **不在真缺表里**（在别的档）" % k)
print()
print("  含 'gdt' / 'geometric' 的行:", [n for n in rows if 'gdt' in n.lower() or 'geometric' in n.lower()])
print("  含 'convert' 的行:", [n for n in rows if 'convert' in n.lower()])
print()
print("  表里所有仍标 '—' 的条数: %d" % sum(1 for n in rows if rows[n] == '—'))
print("  总行数: %d" % len(rows))
