import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
changed = 0
for p in sorted((ROOT / "tests").glob("*.py")):
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    out, added = [], 0
    for l in lines:
        out.append(l)
        #: `X.get_com_member = <expr>` ⇒ 紧跟一行 `X.call_com_member = <同一个 expr>`
        m = re.match(r"^(\s*)([\w.]+)\.get_com_member\s*=\s*(.+?)\s*$", l)
        if m:
            indent, obj, expr = m.group(1), m.group(2), m.group(3)
            if expr.endswith(("(", ",")) or expr == "":
                continue          # 跨行的赋值，跳过（本仓不是这种形态）
            out.append("%s%s.call_com_member = %s\n" % (indent, obj, expr))
            added += 1
        #: `"safe_get_com_member": lambda ...` 这种字典桩 ⇒ 旁边补一项
        m2 = re.match(r"^(\s*)[\"']safe_get_com_member[\"']\s*:\s*(.+?),\s*$", l)
        if m2:
            out.append("%s\"call_com_member\": %s,\n" % (m2.group(1), m2.group(2)))
            added += 1
    if added:
        p.write_text("".join(out), encoding="utf-8")
        ast.parse(p.read_text(encoding="utf-8"))
        changed += 1
        print("  ✓ %-46s 补 %d 处" % (p.name, added))
print()
print("  共 %d 个测试文件" % changed)
