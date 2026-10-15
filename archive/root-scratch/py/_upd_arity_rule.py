import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")
t = P.read_text(encoding="utf-8")

OLD = """#     `Int32&` / `Int16&` / `Double&` / `Boolean&` 等**标量出参** ⇒ 调用方要传，**计入**
#     `Object&` / `Variant&` 等**数组出参**（纯 [out] 容器） ⇒ 调用方不传，**排除**"""

NEW = """#     ⚑⚑ **2026-10-01（轮 123）真机再改一次：`Object&` 也要计入。**
#     `Int32&` / `Int16&` / `Double&` / `Boolean&` 等**标量出参** ⇒ 调用方要传，**计入**
#     `Object&` / `Variant&` 等**数组出参**（纯 [out] 容器） ⇒ **同样要传，计入**
#
#     真机实验 `tools/probe_outparam_object_byref.py`（SW 2026 SP4.1 / 34.4.1）
#     对 `IHoleStandardsData.GetHoleStandards(Object& Standards, Object& Types)` 试四形态：
#     ```
#     A 不传出参                              ⇒ com_error -2147352561「**非选择性的参数**」
#     B VARIANT(VT_BYREF|VT_DISPATCH, None)   ⇒ com_error -2147352571「类型不匹配」
#     C 两个裸 None                            ⇒ com_error -2147352571「类型不匹配」
#     D VARIANT(VT_BYREF|VT_VARIANT, None)    ⇒ **返回 True**  ✓
#     ```
#     ⇒ ★ **A 报 `DISP_E_PARAMNOTOPTIONAL` ⇒ 出参是必填的** ⇒ 官方 arity = **2**（含两个出参）。
#     ⇒ ★★ **这条同时推翻了"两边"**：旧规则说「`Object&` 不传」（**错，必填**）；
#        而 `sw_hole_features.py` 虽然传了，**传的是裸值**（**传法也错** —— 要 `VT_BYREF|VT_VARIANT`）。
#     ⚠ 边界：只证了 `GetHoleStandards` **这一个**成员；「所有 `Object&` 都一样」是**外推**。
#     ⚠ 背景：该成员在仓库里**没有调用方**（`sw_hole_features.py` 的 4 个包装是孤儿），
#        所以这条修正**只影响本工具的判据**，不影响任何在跑的功能。"""

if "`Object&` 也要计入" not in t:
    assert OLD in t, "规则段锚点不符"
    t = t.replace(OLD, NEW, 1)
    print("  ok 规则说明已更新")
else:
    print("  规则说明已更新")

# 真正的判据逻辑：把 Object& 从"排除"挪到"计入"
import re
m = re.search(r"(?m)^.*(Object&|Variant&).*(EXCLUDE|exclude|排除|OUT_|BYREF).*$", t)
for i, l in enumerate(t.splitlines(), 1):
    if ("Object&" in l or "Variant&" in l) and ("排除" in l or "exclude" in l.lower() or "OUT" in l):
        print("  可疑判据行 L%d: %s" % (i, l.strip()[:96]))
P.write_text(t, encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
