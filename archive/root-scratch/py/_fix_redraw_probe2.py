import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_spline_redraw.py")
t = P.read_text(encoding="utf-8")
OLD = '''            mv = sw.ActiveView'''
NEW = '''            #: ⚠ `sw.ActiveView` 在迟到绑定下**没有**（`AttributeError`）⇒
            #: 按官方走 `IModelDoc2::ActiveView`（即 `ActiveDoc.ActiveView`）。
            #: ⚠ 这是**第二次**试（事实 53：同一处不试第三种）。
            mv = sw.ActiveDoc.ActiveView'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已改为 ActiveDoc.ActiveView")
