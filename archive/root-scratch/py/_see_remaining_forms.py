import ast
import sys
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
files = sorted(list((R / "tools").glob("*.py")) + list((R / "scripts").glob("*.py")))
shapes = Counter()
examples = {}
for f in files:
    t = f.read_text(encoding="utf-8")
    if "residual_dialogs(" not in t:
        continue
    if ("settle_residual_dialogs(" in t) or ("dismiss_residual_dialogs(" in t):
        continue
    for i, l in enumerate(t.splitlines(), 1):
        if "residual_dialogs(" in l and "def " not in l:
            s = l.strip()
            #: 归一化：把变量名/前缀抹掉，只看形态
            key = s
            for pref in ("_sc.", "sw_connect.", "_sw_connect."):
                key = key.replace(pref, "")
            key = key[:78]
            shapes[key] += 1
            examples.setdefault(key, (f.name, i))
print("  仍「只查不点」的调用**形态**（归并后）:")
for s, n in shapes.most_common(12):
    fn, i = examples[s]
    print("  %2d × %s" % (n, s))
    print("       例: %s:%d" % (fn, i))
