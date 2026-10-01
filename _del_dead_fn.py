import ast
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\propose_capability_sources.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)

#: 定位 match_modules 整个函数（L133 起，到它的 return 后的两个空行）
start = next(i for i, l in enumerate(lines) if l.startswith("def match_modules("))
end = next(i for i in range(start + 1, len(lines))
           if lines[i].startswith("def ") or lines[i].startswith("#:") or lines[i].startswith("NOTES"))
print("  将删除 L%d..L%d:" % (start + 1, end))
for i in range(start, end):
    print("    %s" % lines[i].rstrip()[:96])

#: ⚠ 留一条**墓碑注释**（比彻底消失更好：下一个人知道这里曾有什么、为什么删）
TOMB = [
    "# ⚑ 2026-10-01（轮 136）：这里曾有一个 `match_modules(kws, files)` ——\n",
    "#   它是 `stems_only()` 的**旧版**（会**扫文件体**，命中面失控），已被取代但**一直留着**。\n",
    "#   `tools/probe_uncalled_helpers.py` 扫出它**在整个仓库里 0 次调用** ⇒ 删除。\n",
    "#   ⚠ 留这条注释而不是无声删掉：**读代码的人该知道这里发生过什么**。\n",
    "\n",
    "\n",
]
lines[start:end] = TOMB
P.write_text("".join(lines), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已删除并留墓碑注释；语法 OK")
r = subprocess.run(["git", "diff", "--stat", "--", "tools/propose_capability_sources.py"],
                   capture_output=True, text=True, encoding="utf-8",
                   cwd=r"C:\swprojects\sw-skill-fork")
print("  git diff --stat: %s" % r.stdout.strip())
