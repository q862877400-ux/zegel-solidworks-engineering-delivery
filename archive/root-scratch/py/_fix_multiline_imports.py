import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

#: 找 `from [.]?sw_connect import (` … `)` 的多行块，若块里没有 call_com_member 就补一项
BLOCK = re.compile(r"((?:^|\n)([ \t]*)from \.?sw_connect import \(\n)(.*?)(\n[ \t]*\))",
                   re.S)
changed = 0
for p in sorted((ROOT / "scripts").glob("sw_*.py")):
    t = p.read_text(encoding="utf-8")
    orig = t

    def fix(m):
        head, indent, body, tail = m.group(1), m.group(2), m.group(3), m.group(4)
        if "call_com_member" in body:
            return m.group(0)
        #: 插一项（保持字母序：call_com_member 通常在 create_ 之前）
        items = [x.strip().rstrip(",") for x in body.splitlines() if x.strip()]
        items = sorted(set(items) | {"call_com_member"})
        inner = "".join("%s    %s,\n" % (indent, x) for x in items)
        return "%s%s%s" % (head, inner, tail)

    t = BLOCK.sub(fix, t)
    if t != orig:
        p.write_text(t, encoding="utf-8")
        ast.parse(t)
        changed += 1
        print("  ✓ %s" % p.name)
print()
print("  共 %d 个文件（多行导入块）" % changed)
