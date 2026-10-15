import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

#: ① `helper_const_args` 连**形参名**一起返回（避免在调用处再去找函数对象 —— 那会踩变量覆盖）
OLD1 = """        if vals:
            out[(fnname, idx)] = sorted(set(vals))
    return out"""
NEW1 = """        if vals:
            #: ★ 连**形参名**一起返回（调用处不必再去 AST 里找那个函数对象 ——
            #: 那会踩"循环变量被覆盖"的坑，轮 176 第一次就是这么崩的）
            out[(fnname, idx)] = {"param": param_names[(fnname, idx)], "consts": sorted(set(vals))}
    return out"""
assert OLD1 in t, "锚点1不符"
t = t.replace(OLD1, NEW1, 1)

#: 建 helpers 时记下形参名
OLD2 = """                    helpers.setdefault((fn.name, idx), set())"""
NEW2 = """                    helpers.setdefault((fn.name, idx), set())"""
assert OLD2 in t
#: 加一个 param_names 表
OLD3 = """    helpers: dict = {}
    for fn in ast.walk(tree):"""
NEW3 = """    helpers: dict = {}
    param_names: dict = {}          #: ★ `(函数名, 序号) → 形参名`（轮 176）
    for fn in ast.walk(tree):"""
assert OLD3 in t, "锚点2不符"
t = t.replace(OLD3, NEW3, 1)

OLD4 = """                    helpers.setdefault((fn.name, idx), set())"""
NEW4 = """                    helpers.setdefault((fn.name, idx), set())
                    param_names[(fn.name, idx)] = pname"""
assert OLD4 in t
t = t.replace(OLD4, NEW4, 1)

#: ② 调用处：用返回的 param，别再找 `fn`
OLD5 = """            for (hfname, hidx), consts in hc.items():
                for hn in ast.walk(tree):
                    if not isinstance(hn, ast.Call):
                        continue
                    hf = getattr(hn.func, "attr", None) or getattr(hn.func, "id", None)
                    if hf not in ("get_com_member", "call_com_member", "safe_get_com_member"):
                        continue
                    if len(hn.args) < 2 or not isinstance(hn.args[1], ast.Name):
                        continue
                    if hn.args[1].id != (fn.args.args[hidx].arg
                                         if hidx < len(fn.args.args) else None):
                        continue"""
NEW5 = """            for (hfname, hidx), info in hc.items():
                hparam = info["param"]
                consts = info["consts"]
                for hn in ast.walk(tree):
                    if not isinstance(hn, ast.Call):
                        continue
                    hf = getattr(hn.func, "attr", None) or getattr(hn.func, "id", None)
                    if hf not in ("get_com_member", "call_com_member", "safe_get_com_member"):
                        continue
                    if len(hn.args) < 2 or not isinstance(hn.args[1], ast.Name):
                        continue
                    if hn.args[1].id != hparam:          #: ★ 用返回的形参名比对
                        continue"""
assert OLD5 in t, "锚点3不符"
t = t.replace(OLD5, NEW5, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改成返回形参名（不再去 AST 里找函数对象）")
