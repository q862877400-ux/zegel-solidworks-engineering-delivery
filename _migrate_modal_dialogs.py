import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
TOOLS = ROOT / "tools"

NEW_FN = '''def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。

    :returns: `(dialogs, all_windows)` —— 与 `sw_connect.residual_dialogs` 同形。

    ⚠⚠ 此前本文件**自己抄了一份**枚举，且带 **`IsWindowVisible` 过滤** ——
    实测 SolidWorks 的 **49 个顶层窗口里只有 1 个可见** ⇒ 那份抄本**漏检 48/49（约 98%）**。
    ⇒ 现在委托给共享实现，并把**扫到的窗口总数**一并返回
    （★ 空列表只有在总数 > 0 时才有意义，否则分不清「没有」与「没扫到」）。
    """
    return sw_connect.residual_dialogs(SW_PID)
'''

changed, skipped = [], []
for p in sorted(TOOLS.glob("*.py")):
    src = p.read_text(encoding="utf-8")
    if "def modal_dialogs(" not in src:
        continue
    if "residual_dialogs(SW_PID)" in src:
        skipped.append((p.name, "已迁移"))
        continue
    lines = src.splitlines(keepends=True)
    i = next(k for k, l in enumerate(lines) if l.startswith("def modal_dialogs("))
    #: 找到该函数的结尾（下一个顶格 `def `/`class `/`if __name__`）
    j = next((k for k in range(i + 1, len(lines))
              if re.match(r"^(def |class |if __name__)", lines[k])), len(lines))
    old_fn = "".join(lines[i:j])
    if "IsWindowVisible" not in old_fn:
        skipped.append((p.name, "函数里没有 IsWindowVisible（形态不同）"))
        continue
    new = lines[:i] + [NEW_FN, "\n", "\n"] + lines[j:]
    t = "".join(new)
    #: 调用点：`modals = modal_dialogs()` → 解包两元组
    if "modals = modal_dialogs()" not in t:
        skipped.append((p.name, "调用点形态不同"))
        continue
    t = t.replace("modals = modal_dialogs()", "modals, _win_scanned = modal_dialogs()", 1)
    #: chk 的判据：加上「扫到了东西」这一条
    t2, n = re.subn(r'(chk\("★ 收尾无残留模态框[^"]*",\s*)not modals\b',
                    r'\1(not modals) and _win_scanned > 0', t, count=1)
    if n == 0:
        skipped.append((p.name, "chk 判据形态不同"))
        continue
    t = t2
    #: 详情里带上扫到的窗口数
    t = t.replace('"无" if not modals else "有 %d 个: %s" % (len(modals), modals))',
                  '"扫了 %d 个窗口 · %s" % (_win_scanned, "无模态框" if not modals '
                  'else "有 %d 个: %s" % (len(modals), modals)))', 1)
    try:
        ast.parse(t)
    except SyntaxError as e:
        skipped.append((p.name, "改完语法错 L%s（**已跳过**）" % e.lineno))
        continue
    p.write_text(t, encoding="utf-8")
    changed.append(p.name)

print("  ✓ 已迁移 %d 个文件:" % len(changed))
for n in changed:
    print("      %s" % n)
print()
print("  ⚠ 跳过 %d 个:" % len(skipped))
for n, why in skipped:
    print("      %-42s %s" % (n, why))
