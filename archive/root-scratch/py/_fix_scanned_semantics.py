import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
files = sorted(list((R / "tools").glob("*.py")) + list((R / "scripts").glob("*.py")))

#: ⚠⚠⚠ **修我自己引入的静默误报**（轮 169）：
#: 我上一版把 `X, Y = residual_dialogs()` 换成了 `X, Y, Z = settle_residual_dialogs()`，
#: 而 3 元组是 `(found, dismissed, scanned)`、旧 2 元组是 `(dialogs, all_windows)`
#: ⇒ **第 2 位从「扫过的窗口数」变成了「点掉的个数」** ⇒ 打印出来是「扫了 0 个窗口」（假）。
#: ★ 修法：让 **`scanned` 回到第 3 个名字**，第 2 个位置给一个**明确不用的**名字。
PAT = re.compile(r"(?m)^(\s*)(\w+), (\w+), (\w+_扫过) = ((?:_sc|sw_connect|_sw_connect)\.)settle_residual_dialogs\(\)\s*$")
changed = []
for f in files:
    t = f.read_text(encoding="utf-8")
    def repl(m):
        ind, a, b, _z, pre = m.groups()
        #: ★ 形状 (found, dismissed, scanned) ⇒ 把 `scanned` 放回旧名 `b` 的位置
        return "%s%s, _点掉, %s = %ssettle_residual_dialogs()" % (ind, a, b, pre)
    new, n = PAT.subn(repl, t)
    if n:
        ast.parse(new)
        f.write_text(new, encoding="utf-8")
        changed.append((f.name, n))
print("  修好 **%d** 个脚本 · 共 **%d** 处（scanned 已回到原位）"
      % (len(changed), sum(k for _f, k in changed)))
for n, k in changed:
    print("    %s" % n)
