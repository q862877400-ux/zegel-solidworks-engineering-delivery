import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_in_context_reference_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''            b2 = sw_connect.safe_get_com_member(comps[1], "GetBody2")'''
NEW = '''            #: ⚠⚠ **我第一版把名字读错了**：反射里是 **`Body2 GetBody()`** ——
            #: `Body2` 是**返回类型**，方法名是 **`GetBody`**（**不带 2**）。
            #: ⇒ 传 `GetBody2` 会报 `<unknown>.GetBody2`。
            b2 = sw_connect.safe_get_com_member(comps[1], "GetBody")'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改成 GetBody()（不带 2）")
