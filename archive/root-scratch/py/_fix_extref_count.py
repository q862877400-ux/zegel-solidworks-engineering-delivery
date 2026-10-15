import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
t = P.read_text(encoding="utf-8")
OLD = '''    return int(call_com_member(component, "ListExternalFileReferencesCount",
                               bool(include_hidden)) or 0)'''
NEW = '''    #: ⚠⚠ **实测（轮 161）**：反射里有 **两个**形式
    #: （`Int32 ListExternalFileReferencesCount()` 与 `Int32 …(Boolean)`），
    #: 但在 pywin32 迟到绑定下它**表现为属性** ⇒ 传 0 个实参就拿到 `int`；
    #: ⚠ 若按 1 参调，会先拿到那个 int、再把它当函数调 ⇒
    #: **`TypeError: 'int' object is not callable`**（报错完全看不出是"属性还是方法"的问题）。
    #: ⇒ 先按 **0 参**取；取不到再退回 1 参。
    try:
        return int(call_com_member(component, "ListExternalFileReferencesCount") or 0)
    except TypeError:
        return int(call_com_member(component, "ListExternalFileReferencesCount",
                                   bool(include_hidden)) or 0)'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已改成「先 0 参、再退回 1 参」")
