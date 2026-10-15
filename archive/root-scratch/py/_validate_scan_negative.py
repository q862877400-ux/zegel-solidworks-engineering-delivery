import ast
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\tools")
import scan_bare_array_args as S

R = r"C:\swprojects\sw-skill-fork"
#: ★ 负例 = 轮 183 **修复前**的 `sketch_relations.py`（它里面 `CreateSpline` 收了**形参** `points`）
old = subprocess.run(["git", "show", "482b2f3^:scripts/sketch_relations.py"], cwd=R,
                     capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
print("  负例文本: %d 字节" % len(old))
tree = ast.parse(old)
calls = []
for n in ast.walk(tree):
    if isinstance(n, ast.Call):
        nm = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
        if nm in S.CALLS:
            calls.append(n)
print("  负例里的 COM 调用: %d 个" % len(calls))
print()
print("  ── 与 CreateSpline 有关的那几处（应当命中）──")
for n in calls:
    if len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and "Spline" in str(n.args[1].value):
        member = n.args[1].value
        print("    L%-5d %s" % (n.lineno, ast.unparse(n)[:84]))
        for k, a in enumerate(n.args[2:], start=2):
            kinds = S.SIGS.get(member)
            is_obj = S.arg_is_object(member, k - 2)
            print("        第 %d 个实参 `%s` ⇒ 官方签名 %s ⇒ 是 Object? **%s**"
                  % (k - 2, ast.unparse(a), kinds, is_obj))
print()
print("  ── 签名表里 CreateSpline / CreateSpline2 的重载 ──")
for m in ("CreateSpline", "CreateSpline2"):
    print("    %-16s %s" % (m, S.SIGS.get(m)))
print()
print("  ── 反射文件的签名行（核对解析）──")
import re
t = Path(S.REFLECT).read_text(encoding="utf-8", errors="replace")
for line in t.splitlines():
    if re.search(r"\bCreateSpline2?\b\s*\(", line):
        print("    %s" % line.strip()[:88])
