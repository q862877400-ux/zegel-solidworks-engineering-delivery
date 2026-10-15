import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\tools\verify_sketch_getters_smoke.py")
lines = Q.read_text(encoding="utf-8").splitlines(keepends=True)
i = next(k for k, l in enumerate(lines) if "get_lines **非空**" in l)
ADD = [
    "\n",
    "            #: ★★ 轮 140 新增：**定量**判据 —— 「非空」太弱（12 对 1 也绿）。\n",
    "            #: 实测：每条直线占 **12 个 float**（`tools/probe_getlines_count.py`）。\n",
    '            chk("★★ **定量**：`get_lines` 的元素个数 = 条数 × 12（实测语义）",\n',
    "                got_lines == 1 * 12,\n",
    '                "lines=%s，期望 1×12=12" % got_lines)\n',
]
lines[i + 2:i + 2] = ADD
Q.write_text("".join(lines), encoding="utf-8")
ast.parse(Q.read_text(encoding="utf-8"))
print("  ok 冒烟已加定量判据（插在非空那条之后）")
for k in range(i, i + 8):
    print("    L%-4d %s" % (k + 1, Q.read_text(encoding='utf-8').splitlines()[k][:96]))
