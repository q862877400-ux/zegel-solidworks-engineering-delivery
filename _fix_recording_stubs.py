import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

#: ① `sw_assembly.py` 补 `call_com_member` 导入
P = ROOT / "scripts" / "sw_assembly.py"
t = P.read_text(encoding="utf-8")
b = t
t = t.replace("from .sw_connect import get_com_member, open_document, safe_get_com_member",
              "from .sw_connect import call_com_member, get_com_member, open_document, safe_get_com_member")
t = t.replace("from sw_connect import get_com_member, open_document, safe_get_com_member",
              "from sw_connect import call_com_member, get_com_member, open_document, safe_get_com_member")
if t != b:
    P.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("  ✓ sw_assembly.py 已补 call_com_member 导入")
else:
    print("  ⚠ sw_assembly 导入锚点不符")

#: ② 测试里 `X.get_com_member = lambda ...` 的**记录式桩**要有个孪生
TWIN = re.compile(r"^(\s*)([\w.]+)\.get_com_member\s*=\s*(lambda\b.+)$")
n = 0
for p in sorted((ROOT / "tests").glob("*.py")):
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    out, added = [], 0
    for l in lines:
        out.append(l)
        m = TWIN.match(l.rstrip("\n"))
        if m:
            indent, obj, expr = m.group(1), m.group(2), m.group(3)
            out.append("%s%s.call_com_member = %s\n" % (indent, obj, expr))
            added += 1
    if added:
        p.write_text("".join(out), encoding="utf-8")
        ast.parse(p.read_text(encoding="utf-8"))
        n += 1
        print("  ✓ %-46s 记录式桩补 %d 处" % (p.name, added))
print()
print("  共 %d 个测试文件" % n)
