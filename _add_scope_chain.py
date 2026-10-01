import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

#: ★★ 轮 175：把「只看最内层函数」改成「**沿词法作用域链向外找**」。
#: ⚠ 起因：`mold_evidence` 里 `fm` 是在**外层函数**赋值的，而用它的
#: `get_com_member(fm, name)` 在**嵌套函数 `_count`** 里 ⇒ 只看最内层**永远推不出**。
#: ★ 词法作用域是**语言规则**（有依据），**不是猜测** —— 与事实 114 回退的那条推断不同。
OLD = '''            def _scope_of(node):
                """返回包含 `node` 的**最内层**函数（用于取它的形参接口表）。"""
                best = None
                for fn, pi in fn_scopes:
                    if fn.lineno <= getattr(node, "lineno", 0) <= (fn.end_lineno or fn.lineno):
                        if best is None or fn.lineno > best[0].lineno:
                            best = (fn, pi)
                return best[1] if best else {}'''
NEW = '''            def _scope_chain(node):
                """★★ 沿**词法作用域链**返回包含 `node` 的函数（**最内层在前**）。

                ⚠⚠ **为什么要链、而不只是最内层**（轮 175）：`mold_evidence` 的形状是
                ```
                    def mold_evidence(model):
                        fm = get_com_member(model, "FeatureManager")   # ← 外层函数里赋值
                        def _count(name):
                            return get_com_member(fm, name)            # ← 嵌套函数里用它
                ```
                ⇒ 只看最内层时 `fm` **不是形参** ⇒ 推不出 ⇒ 留白（**检查器因此抓不到它的动机**）。
                ★ 而**词法作用域是语言规则**（内层能看见外层的名字）—— 这是**有依据**的推导，
                **不是猜测**（★ 与事实 114 回退的那条"从散文猜接口名"**性质不同**）。
                """
                out = []
                for fn, pi in fn_scopes:
                    if fn.lineno <= getattr(node, "lineno", 0) <= (fn.end_lineno or fn.lineno):
                        out.append((fn.lineno, pi))
                out.sort(key=lambda x: -x[0])            #: 最内层在前
                return [pi for _ln, pi in out]

            def _lookup(name, node):
                """沿作用域链找 `name` 的接口（**内层优先**）；找不到返回 `None`。"""
                for pi in _scope_chain(node):
                    if name in pi:
                        return pi[name]
                return var_iface.get(name)'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)

#: 两处 owner 推导改用 `_lookup`
OLD2 = '''                owner_iface = None
                if isinstance(owner, ast.Name):
                    owner_iface = var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    owner_iface = var_iface.get(owner.attr)
                #: ★★ 推不出接口 ⇒ **留白**（**不许**落到 `IObject` 兜底 —— 那必然误报）
                if not owner_iface or owner_iface == "IObject":
                    continue'''
NEW2 = '''                owner_iface = None
                if isinstance(owner, ast.Name):
                    owner_iface = _lookup(owner.id, n)          #: ★ 沿作用域链找
                elif isinstance(owner, ast.Attribute):
                    owner_iface = _lookup(owner.attr, n)
                #: ★★ 推不出接口 ⇒ **留白**（**不许**落到 `IObject` 兜底 —— 那必然误报）
                if not owner_iface or owner_iface == "IObject":
                    continue'''
assert OLD2 in t, "锚点②不符"
t = t.replace(OLD2, NEW2, 1)

OLD3 = '''                oiface = None
                if isinstance(owner, ast.Name):
                    oiface = var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    oiface = var_iface.get(owner.attr)'''
NEW3 = '''                oiface = None
                if isinstance(owner, ast.Name):
                    oiface = _lookup(owner.id, n)               #: ★ 沿作用域链找
                elif isinstance(owner, ast.Attribute):
                    oiface = _lookup(owner.attr, n)'''
assert OLD3 in t, "锚点③不符"
t = t.replace(OLD3, NEW3, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改成沿词法作用域链查找")
