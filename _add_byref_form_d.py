import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_outparam_object_byref.py")
t = P.read_text(encoding="utf-8")
old = """            forms = [
                ("A 不传出参", lambda: []),
                ("B 两个 VARIANT(VT_BYREF|VT_DISPATCH, None)", mk_byref),
                ("C 两个裸 None", lambda: [None, None]),
            ]"""
new = """            def mk_byref_variant():
                #: ★ 照 `probe_outparam_convention.py` 对 `Int32&` 的**已知good形态**
                #: （`VARIANT(VT_BYREF|VT_I4, 0)` 通过）类推：容器出参用 `VT_BYREF|VT_VARIANT`。
                import pythoncom as _pc
                return [VARIANT(_pc.VT_BYREF | _pc.VT_VARIANT, None),
                        VARIANT(_pc.VT_BYREF | _pc.VT_VARIANT, None)]

            forms = [
                ("A 不传出参", lambda: []),
                ("B 两个 VARIANT(VT_BYREF|VT_DISPATCH, None)", mk_byref),
                ("C 两个裸 None", lambda: [None, None]),
                ("D 两个 VARIANT(VT_BYREF|VT_VARIANT, None)", mk_byref_variant),
            ]"""
assert old in t, "forms 锚点不符"
P.write_text(t.replace(old, new, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已加 D 形态；语法 OK")
