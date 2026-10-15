import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_export.py")
t = P.read_text(encoding="utf-8")
OLD = '''        str(p), 0, SW_SAVE_AS_SILENT if silent else 0,
        None, None, out_i4(), out_i4())'''
NEW = '''        str(p), 0, SW_SAVE_AS_SILENT if silent else 0,
        #: ⚠⚠ **实测（轮 147）**：`ExportData` / `AdvancedSaveAsOptions` 传 `None`
        #: 报 **`类型不匹配`**（位置 4）—— 与事实 12 / 33 同一个坑
        #: ⇒ 必须用 `create_empty_dispatch_variant()`（本模块已导入）给出空 Dispatch。
        create_empty_dispatch_variant(), create_empty_dispatch_variant(),
        out_i4(), out_i4())'''
assert OLD in t, "调用锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已改用 create_empty_dispatch_variant()")
