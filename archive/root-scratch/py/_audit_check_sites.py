import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
files = sorted(list((R / "tools").glob("*.py")) + list((R / "scripts").glob("*.py")))

#: 分类：调用点所在的那一行/下一行，有没有把它喂给"判据"（chk / assert / fail）
forms = {"feeds_check": [], "prints_only": [], "other": []}
for f in files:
    try:
        src = f.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except SyntaxError:
        continue
    lines = src.splitlines()
    for n in ast.walk(tree):
        if not isinstance(n, ast.Assign):
            continue
        #: 形如  dialogs, scanned = _sc.residual_dialogs(...)
        call = n.value
        if not isinstance(call, ast.Call):
            continue
        name = getattr(call.func, "attr", None) or getattr(call.func, "id", None)
        if name != "residual_dialogs":
            continue
        #: 看**后面 6 行**里有没有 chk( / assert
        win = "\n".join(lines[n.lineno - 1: n.lineno + 6])
        rec = (f.name, n.lineno)
        if "chk(" in win or "assert " in win:
            forms["feeds_check"].append(rec)
        elif "print(" in win:
            forms["prints_only"].append(rec)
        else:
            forms["other"].append(rec)

print("  `dialogs, ... = residual_dialogs(...)` 的调用点共 **%d** 处"
      % sum(len(v) for v in forms.values()))
print("    ★ 结果**喂给判据**（chk/assert）: **%d** 处" % len(forms["feeds_check"]))
print("    ⚠ 只在 **print** 里用掉（不会让检查失败）: **%d** 处" % len(forms["prints_only"]))
print("    ? 其它: **%d** 处" % len(forms["other"]))
print()
print("  ── ⚠ 只在 print 里的（前 12）──")
for n, i in forms["prints_only"][:12]:
    print("    %-44s L%d" % (n, i))
print()
print("  ── ★ 喂给判据的（前 6）──")
for n, i in forms["feeds_check"][:6]:
    print("    %-44s L%d" % (n, i))
