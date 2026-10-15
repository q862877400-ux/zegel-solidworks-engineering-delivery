import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
rows = []
for f in sorted(list((R / "tools").glob("*.py")) + list((R / "scripts").glob("*.py"))):
    try:
        src = f.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except SyntaxError:
        continue
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            nm = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
            if nm in ("residual_dialogs", "dismiss_residual_dialogs"):
                names.add(nm)
    if "residual_dialogs" in names:
        rows.append((f.name, "dismiss_residual_dialogs" in names))

print("  检测到模态框的脚本共 **%d** 个" % len(rows))
no_dismiss = [(n, d) for n, d in rows if not d]
print()
print("  ⚠⚠ **只检测、不点掉**的: **%d** 个 —— 若它真发现弹窗，**会话会挂起**（检测救不了挂起）"
      % len(no_dismiss))
for n, _ in no_dismiss:
    print("    %s" % n)
print()
print("  ★ 检测**且**会点掉的: **%d** 个" % sum(1 for _n, d in rows if d))
for n, d in rows:
    if d:
        print("    %s" % n)
