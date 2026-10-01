import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import check_member_owner_interface as C

ifaces = C.load_interfaces(C.REFLECT)
names = set(ifaces.keys())

#: ① `mold_evidence` 的 :param 推出来了吗
t = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_mold.py").read_text(encoding="utf-8")
tree = ast.parse(t)
for fn in ast.walk(tree):
    if isinstance(fn, ast.FunctionDef) and fn.name == "mold_evidence":
        pi = C.param_ifaces_from_docstring(fn, names)
        print("  ① mold_evidence 的 :param 推断 = %s" % pi)
        args = [a.arg for a in fn.args.args]
        print("     形参 = %s" % args)

#: ② `FeatureManager` 在 IModelDoc2 上的返回类型
d = ifaces.get("IModelDoc2") or ifaces.get("ModelDoc2")
if d:
    ret = d["returns"].get("FeatureManager") or d["returns"].get("get_FeatureManager")
    print("  ② IModelDoc2.FeatureManager 的返回类型 = %r ⇒ norm = %r"
          % (ret, C.norm(ret) if ret else None))
    mem = d["members"]
    print("     IModelDoc2 的成员名里有 FeatureManager 吗:", "FeatureManager" in mem)
    print("     有 get_FeatureManager 吗:", "get_FeatureManager" in mem)

#: ③ 建表逻辑单独跑一遍，看 fm 有没有进表
tree_ = tree
var_iface = dict(C.ROOTS)
iface_names = set(ifaces.keys())
fn_scopes = []
for fn in ast.walk(tree_):
    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        p = C.param_ifaces_from_docstring(fn, iface_names)
        if p:
            fn_scopes.append((fn, p))


def _lookup(name, node):
    chain = []
    for fn, p in fn_scopes:
        if fn.lineno <= getattr(node, "lineno", 0) <= (fn.end_lineno or fn.lineno):
            chain.append((fn.lineno, p))
    chain.sort(key=lambda x: -x[0])
    for _l, p in chain:
        if name in p:
            return p[name]
    return var_iface.get(name)


for n in ast.walk(tree_):
    if not isinstance(n, ast.Assign) or not isinstance(n.value, ast.Call):
        continue
    f = getattr(n.value.func, "attr", None) or getattr(n.value.func, "id", None)
    if f not in ("get_com_member", "call_com_member", "safe_get_com_member"):
        continue
    if len(n.value.args) < 2 or not isinstance(n.value.args[1], ast.Constant):
        continue
    owner = n.value.args[0]
    mem = n.value.args[1].value
    oi = _lookup(owner.id, n) if isinstance(owner, ast.Name) else None
    ret = None
    if oi:
        for cand in (oi, oi[1:] if oi.startswith("I") else oi):
            dd = ifaces.get(cand) or ifaces.get(C.norm(cand))
            if dd and mem in dd["returns"]:
                ret = dd["returns"][mem]
                break
    tgt = getattr(n.targets[0], "id", "?")
    print("     赋值 %-14s = get_com_member(%s, %r) ⇒ owner=%s · ret=%r"
          % (tgt, ast.unparse(owner), mem, oi, ret))
