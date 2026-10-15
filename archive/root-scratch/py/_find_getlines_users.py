import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
BAD = []
for p in list(ROOT.rglob("*.py")):
    if any(x in p.parts for x in (".git", "node_modules", "__pycache__")):
        continue
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    for i, l in enumerate(t.splitlines(), 1):
        if re.search(r"\bget_lines\b", l) and not l.strip().startswith("#"):
            rel = str(p.relative_to(ROOT))
            BAD.append((rel, i, l.strip()[:104]))
print("  出现 `get_lines` 的地方（%d 处）:" % len(BAD))
for rel, i, l in BAD:
    print("    %-46s L%-5d %s" % (rel, i, l))
print()
#: 谁把它的结果当"对象"用？
print("  ⚠ 判据：把结果**当对象**用的（取 .X / .GetStartPoint2 / len 当"几条第"）:")
for rel, i, l in BAD:
    if re.search(r"get_lines\(", l) and re.search(r"\.(X|Y|GetStartPoint|GetEndPoint|Construction)", l):
        print("    ★ %s L%d %s" % (rel, i, l))
print("    （上面为空 = 没有直接当对象用的）")
print()
#: docstring 里怎么说的
p = ROOT / "scripts" / "sw_sketch.py"
t = p.read_text(encoding="utf-8").splitlines()
for i, l in enumerate(t):
    if "def get_lines" in l:
        print("  `get_lines` 的 docstring 现状:")
        for k in range(i, min(len(t), i + 12)):
            print("    L%-4d %s" % (k + 1, t[k][:96]))
        break
