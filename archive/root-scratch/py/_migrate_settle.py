import ast
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
files = sorted(list((R / "tools").glob("*.py")) + list((R / "scripts").glob("*.py")))

#: 迁移形态（轮 167 已经统一成"无参调用"）：
#:   `X, Y = (sw_connect|_sc).residual_dialogs()`  →  `X, Y, Z = ...settle_residual_dialogs()`
#: ⚠ 只改**赋值形态**（`= ...residual_dialogs()`），不动 `return residual_dialogs(...)` 那种包装。
PAT = re.compile(r"(?m)^(\s*)(\w+), (\w+) = ((?:_sc|sw_connect|_sw_connect)\.)residual_dialogs\(\)\s*$")
changed = []
for f in files:
    t = f.read_text(encoding="utf-8")
    new, n = PAT.subn(
        lambda m: "%s%s, %s, %s_扫过 = %ssettle_residual_dialogs()"
                  % (m.group(1), m.group(2), m.group(3), m.group(2)[:3], m.group(4)),
        t)
    if n:
        ast.parse(new)
        f.write_text(new, encoding="utf-8")
        changed.append((f.name, n))
print("  迁移脚本 **%d** 个 · 共 **%d** 处" % (len(changed), sum(n for _f, n in changed)))
for n, k in changed[:10]:
    print("    %-44s %d 处" % (n, k))

#: ★ 事实 61：跑完先看 diff 的删除数
out = subprocess.run(["git", "diff", "-U0", "--stat"], cwd=str(R), capture_output=True,
                     text=True, encoding="utf-8", errors="replace").stdout
last = [l for l in out.strip().splitlines() if "changed" in l]
print("  git diff --stat: %s" % (last[-1].strip() if last else "（无）"))

#: 还剩多少只查不点
left = []
for f in files:
    t = f.read_text(encoding="utf-8")
    has_detect = "residual_dialogs(" in t
    has_dispose = ("settle_residual_dialogs(" in t) or ("dismiss_residual_dialogs(" in t)
    if has_detect and not has_dispose:
        left.append(f.name)
print("  仍「只查不点」的脚本: **%d** 个" % len(left))
for n in left[:8]:
    print("    %s" % n)
