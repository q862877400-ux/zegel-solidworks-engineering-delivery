import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\merge_final.py")
s = p.read_text(encoding="utf-8")
old = '''    for r in rows:
        f, n = short(r["type"]), r["name"]'''
new = '''    for r in rows:
        f = short(r["type"])
        # ⚑ 属性形态在 interop 里带 ``get_``/``set_`` 前缀，**COM 名没有** ——
        #   与本索引其余部分（ARITY / PROPERTIES）保持同一套归一。
        n = r["name"]
        if r["kind"] == "property" and n[:4] in ("get_", "set_"):
            n = n[4:]'''
assert old in s
p.write_text(s.replace(old, new, 1), encoding="utf-8")
import ast; ast.parse(s.replace(old, new, 1))
print("  属性名归一化已补")