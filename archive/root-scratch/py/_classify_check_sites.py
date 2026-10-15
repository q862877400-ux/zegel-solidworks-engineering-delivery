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
    lines = src.splitlines()
    for n in ast.walk(tree):
        if not isinstance(n, ast.Assign) or not isinstance(n.value, ast.Call):
            continue
        name = getattr(n.value.func, "attr", None) or getattr(n.value.func, "id", None)
        if name != "residual_dialogs":
            continue
        win = "\n".join(lines[n.lineno - 1: n.lineno + 6])
        verdict = ("chk(" in win) or ("assert " in win)
        rows.append((f.name, n.lineno, verdict))
print("  ── 按「文件名前缀」分类（★ 前缀就是脚本自称的角色）──")
from collections import defaultdict
by_prefix = defaultdict(lambda: [0, 0])
for n, i, v in rows:
    p = n.split("_")[0]
    by_prefix[p][0] += 1
    if not v:
        by_prefix[p][1] += 1
for p, (tot, soft) in sorted(by_prefix.items()):
    tag = "★ 验收冒烟" if p == "verify" else "探针/诊断"
    print("    %-9s %s  共 %d 处 · ⚠ 软信号 %d 处" % (p, tag, tot, soft))
print()
bad = [(n, i) for n, i, v in rows if not v and n.startswith("verify_")]
print("  ★★ **真缺陷**（`verify_*` 却是软信号）: **%d** 处" % len(bad))
for n, i in bad:
    print("    %s L%d" % (n, i))
ok = [(n, i) for n, i, v in rows if v]
print()
print("  已有 verdict 的: %d 处" % len(ok))
for n, i in ok:
    print("    %s L%d" % (n, i))
