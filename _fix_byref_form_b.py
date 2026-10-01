import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_outparam_object_byref.py")
t = P.read_text(encoding="utf-8")
old = """    import pythoncom
    import pywintypes
"""
new = """    import pywintypes
    from win32com.client import VARIANT      # ⚠ `pythoncom.VARIANT` **不存在**（第一版就栽在这）
"""
assert old in t, "导入锚点不符"
t = t.replace(old, new, 1)

old2 = """            def mk_byref():
                v = pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_DISPATCH, None)
                return [v, pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_DISPATCH, None)]

            forms = [
                ("A 不传出参", lambda: []),
                ("B 两个 VARIANT(VT_BYREF|VT_DISPATCH, None)",
                 lambda: [pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_DISPATCH, None),
                          pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_DISPATCH, None)]),
                ("C 两个裸 None", lambda: [None, None]),
            ]"""
new2 = """            def mk_byref():
                #: ⚠ 用 `win32com.client.VARIANT`，不是 `pythoncom.VARIANT`（后者不存在）
                import pythoncom as _pc
                return [VARIANT(_pc.VT_BYREF | _pc.VT_DISPATCH, None),
                        VARIANT(_pc.VT_BYREF | _pc.VT_DISPATCH, None)]

            forms = [
                ("A 不传出参", lambda: []),
                ("B 两个 VARIANT(VT_BYREF|VT_DISPATCH, None)", mk_byref),
                ("C 两个裸 None", lambda: [None, None]),
            ]"""
assert old2 in t, "forms 锚点不符"
t = t.replace(old2, new2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok B 形态已改用 win32com.client.VARIANT；语法 OK")
