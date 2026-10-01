import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_export_bmp_contract.py")
t = P.read_text(encoding="utf-8")
OLD = '''    for name in ("sw_document_data", "sw_preflight", "sw_capture"):
        sys.modules.setdefault(name, types.ModuleType(name))'''
NEW = '''    #: ⚠ `sw_export` 在导入时会调 `import_com_dependencies()`（要 3 元组）
    #: 与 `read_custom_property` ⇒ 桩要把这两个都提供，否则**导入即失败**。
    pre = types.ModuleType("sw_preflight")
    pre.import_com_dependencies = lambda: (None, None, None)
    dd = types.ModuleType("sw_document_data")
    dd.read_custom_property = lambda *a, **k: None
    sys.modules["sw_preflight"] = pre
    sys.modules["sw_document_data"] = dd
    sys.modules.setdefault("sw_capture", types.ModuleType("sw_capture"))'''
assert OLD in t, "桩锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 桩已补齐")
