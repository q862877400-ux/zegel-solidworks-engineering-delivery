import sys, io, importlib.util, types
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = types.ModuleType("sw_connect")
c.get_com_member = lambda o, n, *a, **k: f"调用了 {n}，实参 {len(a)} 个"
sys.modules["sw_connect"] = c
sp = importlib.util.spec_from_file_location("h", r"C:\swprojects\sw-skill-fork\scripts\sw_hubs.py")
h = importlib.util.module_from_spec(sp); sys.modules["h"] = h; sp.loader.exec_module(h)

print("问：表里有的成员，能不能不写新函数就直接调？")
print()
# 1) 挑一个我「没封装」的成员
fam = "IFeatureManager"
t = h.HUB_ARITY[fam]
print(f"  {fam} 登记了 {len(t)} 项能力")
for name, ar in list(t.items())[:4]:
    args = [0] * ar
    print(f"    call_hub(obj, {fam!r}, {name!r}{', ' + str(args) if args else ''})")
    print(f"      -> {h.call_hub(object(), fam, name, *args)}")
print()
# 2) 一个 27 参的大函数（上游真实用来做切除的那个）
big = [n for n, a in t.items() if a == 27]
print("  27 参的成员:", big)
if big:
    n = big[0]
    print(f"    call_hub(obj, {fam!r}, {n!r}, x1..x27)")
    print(f"      -> {h.call_hub(object(), fam, n, *range(27))}")
