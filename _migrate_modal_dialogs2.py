import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
TOOLS = ROOT / "tools"

#: ★ 函数内**双路导入**（照本仓既有模式：`try: from scripts.x / except: from x`）
DELEGATE = '''def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import residual_dialogs
    return residual_dialogs(SW_PID)
'''

changed, skipped = [], []
for p in sorted(TOOLS.glob("*.py")):
    src = p.read_text(encoding="utf-8")
    if "def modal_dialogs(" not in src:
        continue
    lines = src.splitlines(keepends=True)
    i = next(k for k, l in enumerate(lines) if l.startswith("def modal_dialogs("))
    j = next((k for k in range(i + 1, len(lines))
              if re.match(r"^(def |class |if __name__)", lines[k])), len(lines))
    old = "".join(lines[i:j])
    if "IsWindowVisible" not in old:
        skipped.append((p.name, "已是委托形态或形态不同"))
        continue
    t = "".join(lines[:i]) + DELEGATE + "\n\n" + "".join(lines[j:])
    #: 探针那 7 个：`modals = modal_dialogs()` 直接改解包；打印行带上总数
    if "modals = modal_dialogs()" in t and "_win_scanned" not in t:
        t = t.replace("modals = modal_dialogs()", "modals, _win_scanned = modal_dialogs()", 1)
    t = t.replace('print("   收尾模态框: %s" % ("无" if not modals else modals))',
                  'print("   收尾模态框: %s（扫了 %d 个窗口）"\n'
                  '          % ("无" if not modals else modals, _win_scanned))', 1)
    t = t.replace('print("   收尾模态框: %s" % ("无" if not modals else modals))',
                  'print("   收尾模态框: %s" % ("无" if not modals else modals))', 1)
    try:
        ast.parse(t)
    except SyntaxError as e:
        skipped.append((p.name, "改完语法错 L%s（**已跳过**）" % e.lineno))
        continue
    p.write_text(t, encoding="utf-8")
    changed.append(p.name)

print("  ✓ 本轮改了 %d 个:" % len(changed))
for n in changed:
    print("      %s" % n)
print()
print("  ⚠ 跳过 %d 个:" % len(skipped))
for n, why in skipped:
    print("      %-44s %s" % (n, why))
