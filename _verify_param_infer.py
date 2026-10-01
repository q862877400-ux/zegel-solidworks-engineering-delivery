import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, str(R / "scripts"))
import check_member_owner_interface as C

ifaces = C.load_interfaces(C.REFLECT)
names = set(ifaces.keys())
print("  反射接口名里有没有裸 `Feature`:", "Feature" in names)
print("  有没有 `IFeature`:", "IFeature" in names)
print()

t = (R / "scripts" / "sw_mold.py").read_text(encoding="utf-8")
tree = ast.parse(t)
for fn in ast.walk(tree):
    if not isinstance(fn, ast.FunctionDef):
        continue
    pi = C.param_ifaces_from_docstring(fn, names)
    if pi:
        print("  %-28s 形参接口推断 = %s" % (fn.name, pi))
print()
#: ★ 关键：mold_evidence / mold_undercut_detect 的 docstring 里出现了哪些接口名
for want in ("mold_evidence", "mold_undercut_detect"):
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef) and fn.name == want:
            doc = ast.get_docstring(fn) or ""
            found = sorted({c for c in names
                            if re.search(r"(?<![A-Za-z0-9_])" + re.escape(c) + r"(?![A-Za-z0-9_])", doc)})
            print("  ── %s：形参 %s · docstring 里出现的接口名 %d 个 ──"
                  % (want, [a.arg for a in fn.args.args], len(found)))
            for c in found[:8]:
                print("       %s" % c)
