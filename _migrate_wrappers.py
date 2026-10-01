import ast
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
files = sorted(list((R / "tools").glob("*.py")) + list((R / "scripts").glob("*.py")))

#: 形态：`return residual_dialogs()`（在每个脚本自己的包装函数里）
#: ⇒ 改成「先只读查；**发现了就点掉**（兜底，避免挂起）；返回形状**保持不变**」
PAT = re.compile(r"(?m)^(\s*)return ((?:_sc|sw_connect|_sw_connect)\.)?residual_dialogs\(\)\s*$")
changed = []
for f in files:
    t = f.read_text(encoding="utf-8")
    if "settle_residual_dialogs(" in t or "dismiss_residual_dialogs(" in t:
        continue
    def repl(m):
        ind, pre = m.group(1), (m.group(2) or "")
        return (
            "%s#: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——\n"
            "%s#: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。\n"
            "%s_dialogs, _scanned = %sresidual_dialogs()\n"
            "%sif _dialogs:\n"
            "%s    %sdismiss_residual_dialogs()\n"
            "%sreturn _dialogs, _scanned"
            % (ind, ind, ind, pre, ind, ind + "    ", pre, ind)
        )
    new, n = PAT.subn(repl, t)
    if n:
        ast.parse(new)
        f.write_text(new, encoding="utf-8")
        changed.append((f.name, n))
print("  迁移脚本 **%d** 个 · 共 **%d** 处" % (len(changed), sum(k for _f, k in changed)))
for n, k in changed[:8]:
    print("    %-44s %d 处" % (n, k))

out = subprocess.run(["git", "diff", "-U0", "--stat", "--", "tools", "scripts"], cwd=str(R),
                     capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
last = [l for l in out.strip().splitlines() if "changed" in l]
print("  git diff --stat(tools+scripts): %s" % (last[-1].strip() if last else "（无）"))

left = []
for f in files:
    t = f.read_text(encoding="utf-8")
    if ("residual_dialogs(" in t) and ("dismiss_residual_dialogs(" not in t) \
            and ("settle_residual_dialogs(" not in t):
        left.append(f.name)
print("  仍「只查不点」的脚本: **%d** 个 %s" % (len(left), left[:5]))
