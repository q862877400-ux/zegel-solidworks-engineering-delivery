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
#: 只看最重的几个
PRIORITY = ("InsertMoldShutOffSurface", "InsertWeldmentFeature", "RunAnalysis",
            "MeshAndRun", "Scale", "UpdateCutList", "InsertGtol", "Activate")
for f, ln, m in hot:
    if m not in PRIORITY:
        continue
    p = ROOT / f
    lines = p.read_text(encoding="utf-8").splitlines()
    print("── %s:%d  `%s`" % (f, ln, m))
    for k in range(max(0, ln - 3), min(len(lines), ln + 2)):
        mark = ">>" if k == ln - 1 else "  "
        print("  %s L%-4d %s" % (mark, k + 1, lines[k][:100]))
    print()
