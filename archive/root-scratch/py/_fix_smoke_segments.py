import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_in_context_reference_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''            ents = sk.GetSketchSegments() if sk is not None else None
            ents = list(ents) if ents else []'''
NEW = '''            #: ⚠ 用**仓库已验证的**取法（`sw_sketch.get_sketch_segments`）——
            #: 第一版我自己写 `sk.GetSketchSegments()` ⇒ 拿到的东西不对
            #: ⇒ 报 `TypeError: 'NoneType' object is not callable`（**不是** `add_relation` 的错）。
            from scripts import sw_sketch
            ents = sw_sketch.get_sketch_segments(sk) if sk is not None else []
            ents = list(ents) if ents else []'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改用 sw_sketch.get_sketch_segments")
