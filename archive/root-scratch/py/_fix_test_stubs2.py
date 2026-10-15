import ast
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

#: ① 先把 tests/ 恢复到 git 状态（撤销我那次坏改动）
r = subprocess.run(["git", "checkout", "--", "tests"], capture_output=True, text=True,
                   encoding="utf-8", errors="replace", cwd=str(ROOT))
print("  恢复 tests/：%s" % (r.stdout.strip() or r.stderr.strip() or "ok"))

#: ② 只用**安全形态**：RHS 是**简单名或点号名**（不含括号/逗号/lambda）
SIMPLE = re.compile(r"^(\s*)([\w.]+)\.get_com_member\s*=\s*([A-Za-z_][\w.]*)\s*$")
changed = 0
for p in sorted((ROOT / "tests").glob("*.py")):
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    out, added = [], 0
    for l in lines:
        out.append(l)
        m = SIMPLE.match(l)
        if m:
            indent, obj, expr = m.group(1), m.group(2), m.group(3)
            out.append("%s%s.call_com_member = %s\n" % (indent, obj, expr))
            added += 1
    if added:
        p.write_text("".join(out), encoding="utf-8")
        ast.parse(p.read_text(encoding="utf-8"))
        changed += 1
        print("  ✓ %-46s 补 %d 处" % (p.name, added))
print()
print("  共 %d 个测试文件（只处理「简单名 RHS」）" % changed)
