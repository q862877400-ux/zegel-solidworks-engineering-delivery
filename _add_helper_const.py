r"""@brief 给检查器补「**把辅助函数的调用点常量代进去**」—— 把"未检查项"变成"可检查项"。

## 为什么（轮 176）
轮 175 把边界量化成「能查 214 / **查不了 47**（成员名是变量）」。★ 但**那 47 处里有一类是可以查的**：
```
    def _count(name):                      # ← 辅助函数，成员名是形参
        return get_com_member(fm, name)
    ...
    counts = {"parting_lines": _count("GetPartingLinesCount"), ...}   # ← 调用点传的是**常量**
```
⇒ ★★ **把调用点传的常量代进形参** ⇒ 静态**就能查** `fm.GetPartingLinesCount` 在不在 `IFeatureManager` 上。
★ 这正是**轮 172 真机查出的那 4+2 个成员** —— 也就是说，**本改动能自动抓出它**。

## 判据（可核验，不猜）
```
① 同文件内，某函数 F 的**某个形参**被用作 `get_com_member(owner, <那个形参>)` 的成员名；
② 收集 F 的**所有调用点** `F("X")`（实参是**字符串常量**）；
③ 若**所有**调用点给的常量**都一致地**该被判 ⇒ 逐个用那个常量做归属检查；
④ ⚠ **没有常量调用点 / 有分歧** ⇒ **仍然留白**（不猜 —— 事实 113/114 的定则）。
```
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

HELPER = '''

def helper_const_args(tree, iface_names: set) -> dict:
    """★ 收集「**辅助函数 → 调用点传的常量实参**」（轮 176）。

    返回 `{(函数名, 形参序号): [常量字符串, …]}` —— 只收**实参是字符串常量**的调用点。
    ⚠ **不猜**：一个调用点给不出常量，就**不算**（宁可留白）。
    """
    #: ① 找「辅助函数」：某个形参被当作 `get_com_member(owner, <形参>)` 的成员名
    helpers: dict = {}
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
        for idx, pname in enumerate(args):
            for n in ast.walk(fn):
                if not isinstance(n, ast.Call):
                    continue
                fname = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
                if fname not in ("get_com_member", "call_com_member", "safe_get_com_member"):
                    continue
                if len(n.args) >= 2 and isinstance(n.args[1], ast.Name) and n.args[1].id == pname:
                    helpers.setdefault((fn.name, idx), set())
    #: ② 收集调用点
    out: dict = {}
    for (fnname, idx), _s in helpers.items():
        vals: list = []
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            callee = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if callee != fnname:
                continue
            if len(n.args) > idx and isinstance(n.args[idx], ast.Constant) \\
                    and isinstance(n.args[idx].value, str):
                vals.append(n.args[idx].value)
        if vals:
            out[(fnname, idx)] = sorted(set(vals))
    return out
'''
if "def helper_const_args(" not in t:
    t = t.replace("def main() -> int:", HELPER.strip() + "\n\n\ndef main() -> int:", 1)
    P.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("  ok ① helper_const_args 已加")
else:
    print("  ⚠ 已有 helper_const_args")
