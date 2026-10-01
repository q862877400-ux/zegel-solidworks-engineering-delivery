import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
d = json.loads(Path(r"D:\AI\SW\output\zero-arg-method-callsites.json").read_text(encoding="utf-8"))
MUT = ("Insert", "Add", "Delete", "Remove", "Create", "Set", "Run", "Update",
       "Mesh", "Scale", "Start", "Stop", "Save", "Close", "Open", "Edit", "Modify",
       "Rebuild", "Redraw", "Zoom", "Clear", "Reset", "Apply", "Execute", "Load",
       "Write", "Export", "Import", "Refresh", "Select", "Activate", "Break", "Merge")
hot = [x for x in d["danger"] if str(x[2]).startswith(MUT)]
print("  24 处「名字像改东西」的零参 `get_com_member` 调用点：")
print()
n = 0
for f, ln, m in hot:
    n += 1
    p = ROOT / f
    lines = p.read_text(encoding="utf-8").splitlines()
    #: 找出**所在函数名**（往上找最近的 def）
    fn = "?"
    for k in range(ln - 1, max(0, ln - 120), -1):
        s = lines[k].lstrip()
        if s.startswith("def "):
            fn = s[4:s.index("(")] if "(" in s else s[4:40]
            break
    print("  ── %2d) %s:%d  `%s`   （在 %s() 里）" % (n, f.replace("\\", "/"), ln, m, fn))
    for k in range(max(0, ln - 2), min(len(lines), ln + 2)):
        mark = ">>" if k == ln - 1 else "  "
        print("       %s %s" % (mark, lines[k].strip()[:96]))
    print()
