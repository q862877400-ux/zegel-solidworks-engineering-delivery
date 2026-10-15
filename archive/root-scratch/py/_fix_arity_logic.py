import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")
t = P.read_text(encoding="utf-8")

OLD = '''            def _is_required_out(param: str) -> bool:
                """该 by-ref 出参是否**由调用方传入**（标量要传、纯 out 数组不传）。"""
                if not param.endswith("&"):
                    return False
                base = param[:-1].strip().lower()   # ⚠ `&` 是**一个**字符，不是两个
                # 纯 [out] 容器类型：调用方不传（反射里 `Void GetErrorMessages(Object&, …)` = 0 参）
                return not base.startswith(("object", "variant", "dispatch"))

            # ⚠ 口径：**不是**「排除所有出参」，而是「排除**纯 out 容器**出参」。
            #   标量出参（`Int32&` 等）由调用方传 ⇒ **计入**。
            count = len([p for p in _params if not p.endswith("&") or _is_required_out(p)])'''

NEW = '''            # ⚑⚑ **2026-10-01（轮 123）：特例全部去掉 —— arity 就是反射里的参数个数。**
            #   真机实验 `tools/probe_outparam_object_byref.py` 对
            #   `IHoleStandardsData.GetHoleStandards(Object& Standards, Object& Types)`：
            #     A 不传出参 ⇒ com_error -2147352561「**非选择性的参数**」（= `DISP_E_PARAMNOTOPTIONAL`）
            #     D `VARIANT(VT_BYREF|VT_VARIANT, None)` ×2 ⇒ **返回 True** ✓
            #   ⇒ ★ **`Object&` 出参是必填的** ⇒ 官方 arity = **2**。
            #   ⇒ 旧规则「`Object&` / `Variant&` / `Dispatch&` 一律排除」**是错的**。
            #   ★ 按**铁律 4**：arity 以**出厂反射的参数个数**为准，不做任何类型特例。
            #   ⚠ 边界：只证了 `GetHoleStandards` 一个成员；但"以反射为准"这条**不需要外推**，
            #     它本身就是本仓库的口径。
            count = len(_params)'''

if "特例全部去掉" not in t:
    assert OLD in t, "判据段锚点不符"
    t = t.replace(OLD, NEW, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 判据已改为『arity = 反射参数个数』")
else:
    print("  判据已是新规则")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
