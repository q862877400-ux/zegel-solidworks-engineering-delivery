r"""@brief 给 `check_member_owner_interface.py` 补「**从 docstring 推形参接口**」。

## 为什么（轮 174）
轮 173 的检查器**抓不到它自己的动机**：`mold_evidence(model)` 的 owner 是**形参** ⇒ 推不出接口 ⇒ 留白。
★ 本仓库的 docstring 很规范（常写 `ISketchRelationManager` / `IModelDoc2` 之类）⇒ **可作依据**。

## 判据（可核验）
```
① 对每个函数，取参数表；
② 在它的 docstring 里找 `:param <参数名>:` 那一段（到下一个 `:param` / `:return` 为止），
   在其中匹配**反射里真实存在的接口名**（从 1032 个接口名里挑，**不猜**）；
③ 命中 ⇒ 该参数在**本函数体内**的接口 = 那个接口 ⇒ 参与后面的成员归属检查。
★ 若一个参数在 docstring 里**没有**接口名 ⇒ **仍然留白**（不许兜底）。
```
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

NEW = '''

def param_ifaces_from_docstring(fn, iface_names: set) -> dict:
    """★ 从 `:param <名>: …` 的说明里推**形参的接口**（轮 174）。

    ⚠⚠ **为什么需要**（轮 173 的局限）：检查器**抓不到它自己的动机** ——
    `mold_evidence(model)` 里的 owner 是**形参** ⇒ 静态推不出接口 ⇒ 被留白排除。
    ★ 而本仓库的 docstring 很规范，常写接口名（如 `:param model: IModelDoc2 …`）⇒ **可作依据**。

    ⚠ **依据必须来自反射**：只在 `iface_names`（**反射里真实存在的接口名**）里挑，
    **不猜、不兜底** —— 挑不到就留白（事实 113 的教训：**兜底会把「我不知道」变成「它有错」**）。
    """
    doc = ast.get_docstring(fn) or ""
    if not doc:
        return {}
    out: dict = {}
    #: 分段：`:param <名>:` 到下一个 `:param` / `:return` / `:raises` / 空行块结束
    blocks = re.split(r"(?m)^\\s*:(?:param|return|returns|raises)\\b", doc)
    for b in blocks:
        m = re.match(r"\\s*(\\w+)\\s*:", b)
        if not m:
            continue
        pname = m.group(1)
        body = b
        #: ★ 只认**反射里存在**的接口名（按长度倒序，先配长名，避免 `ISketch` 抢 `ISketchManager`）
        for cand in sorted(iface_names, key=len, reverse=True):
            if re.search(r"(?<![A-Za-z0-9_])" + re.escape(cand) + r"(?![A-Za-z0-9_])", body):
                out[pname] = cand
                break
    return out
'''
if "def param_ifaces_from_docstring(" not in t:
    t = t.replace("def main() -> int:", NEW.strip() + "\n\n\ndef main() -> int:", 1)
    print("  ok ① param_ifaces_from_docstring 已加")

#: ② 在 main 里：把「函数定义 → 形参接口」表建起来，并在解析时用上
OLD = '''            #: ① 建「变量 → 接口名」表（只看本文件，够用）
            var_iface: dict = dict(ROOTS)'''
NEW2 = '''            #: ① 建「变量 → 接口名」表（只看本文件，够用）
            var_iface: dict = dict(ROOTS)
            #: ★ 2026-10-01（轮 174）：**每个函数**的「形参 → 接口」表（从 docstring 推）
            iface_names = set(ifaces.keys())
            fn_scopes: list = []
            for fn in ast.walk(tree):
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    pi = param_ifaces_from_docstring(fn, iface_names)
                    if pi:
                        fn_scopes.append((fn, pi))
            def _scope_of(node):
                """返回包含 `node` 的**最内层**函数（用于取它的形参接口表）。"""
                best = None
                for fn, pi in fn_scopes:
                    if fn.lineno <= getattr(node, "lineno", 0) <= (fn.end_lineno or fn.lineno):
                        if best is None or fn.lineno > best[0].lineno:
                            best = (fn, pi)
                return best[1] if best else {}'''
assert OLD in t, "锚点①不符"
t = t.replace(OLD, NEW2, 1)

#: ③ 两处 owner 推导都加上「形参接口表」这一层
OLD3 = '''                owner_iface = None
                if isinstance(owner, ast.Name):
                    owner_iface = var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    owner_iface = var_iface.get(owner.attr)
                #: ★★ 推不出接口 ⇒ **留白**（**不许**落到 `IObject` 兜底 —— 那必然误报）
                if not owner_iface or owner_iface == "IObject":
                    continue'''
NEW3 = '''                owner_iface = None
                scope_pi = _scope_of(n)
                if isinstance(owner, ast.Name):
                    #: ★ 先看**本函数的形参接口**（docstring 推出的），再看模块级变量表
                    owner_iface = scope_pi.get(owner.id) or var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    owner_iface = scope_pi.get(owner.attr) or var_iface.get(owner.attr)
                #: ★★ 推不出接口 ⇒ **留白**（**不许**落到 `IObject` 兜底 —— 那必然误报）
                if not owner_iface or owner_iface == "IObject":
                    continue'''
assert OLD3 in t, "锚点②不符"
t = t.replace(OLD3, NEW3, 1)

OLD4 = '''                oiface = None
                if isinstance(owner, ast.Name):
                    oiface = var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    oiface = var_iface.get(owner.attr)'''
NEW4 = '''                oiface = None
                scope_pi = _scope_of(n)
                if isinstance(owner, ast.Name):
                    oiface = scope_pi.get(owner.id) or var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    oiface = scope_pi.get(owner.attr) or var_iface.get(owner.attr)'''
assert OLD4 in t, "锚点③不符"
t = t.replace(OLD4, NEW4, 1)

P.write_text(t, encoding="utf-8")
import ast as _ast
_ast.parse(t)
print("  ok ②③ 形参接口表已接进两处 owner 推导")
