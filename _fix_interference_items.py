import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly.py")
t = P.read_text(encoding="utf-8")
OLD = '''                items.append({
                    "index": index,
                    "name": safe_get_com_member(item, "Name"),
                    "volume": safe_get_com_member(item, "Volume"),
                })'''
NEW = '''                #: ⚠⚠⚠ **第三处成员名错**（轮 159 真机暴露）：`IInterference` 上
                #: **没有 `Name`**（`C:\\swapi\\types\\IInterference\\` 的成员是
                #: `Components` / `GetComponentCount` / `GetInterferenceBody` /
                #: `IGetComponents` / `Ignore` / `IsFastener` / `IsPossibleInterference` / **`Volume`**）。
                #: ⇒ 改用**官方有的**两个：`Volume` 与 `GetComponentCount()`。
                items.append({
                    "index": index,
                    "volume": safe_get_com_member(item, "Volume"),
                    "component_count": safe_get_com_member(item, "GetComponentCount"),
                })'''
assert OLD in t, "取项锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已去掉不存在的 Name，改用 Volume + GetComponentCount")
