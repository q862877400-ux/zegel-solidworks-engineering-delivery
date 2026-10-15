import ast
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
files = sorted(list((R / "tools").glob("*.py")) + list((R / "scripts").glob("*.py")))
changed, removed_def, changed_call = [], 0, 0
for f in files:
    t = f.read_text(encoding="utf-8")
    if "SW_PID" not in t:
        continue
    o = t
    #: ① 调用点：去掉实参（共享函数现在**自己从 COM 派生 PID**）
    t, n1 = re.subn(r"residual_dialogs\(SW_PID\)", "residual_dialogs()", t)
    #: ② 定义行：整行删除（**只删精确的那一行**）
    t, n2 = re.subn(r"(?m)^SW_PID = 20456\s*\n", "", t)
    if t != o:
        ast.parse(t)                    #: ★ 改完立刻验语法，坏了就抛
        f.write_text(t, encoding="utf-8")
        changed.append(f.name)
        changed_call += n1
        removed_def += n2
print("  改动文件 %d 个 · 调用点去掉实参 %d 处 · 删除常量定义 %d 行"
      % (len(changed), changed_call, removed_def))

#: ★ 事实 61：跑完**先看 diff 的删除数**，异常就当成自己的 bug
out = subprocess.run(["git", "diff", "--stat"], cwd=str(R), capture_output=True,
                     text=True, encoding="utf-8", errors="replace").stdout
last = [l for l in out.strip().splitlines() if "changed" in l]
print("  git diff --stat 汇总: %s" % (last[-1].strip() if last else "（无）"))

#: ★ 还剩多少硬编码
left = subprocess.run(["grep", "-rn", "--include=*.py", "-e", r"SW_PID = 20456", "tools", "scripts"],
                      cwd=str(R), capture_output=True, text=True, encoding="utf-8",
                      errors="replace").stdout
left = [l for l in left.strip().splitlines() if l]
print("  仍硬编码 `SW_PID = 20456` 的行数: **%d**" % len(left))
for l in left[:6]:
    print("    %s" % l[:100])
