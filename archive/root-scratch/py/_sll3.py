import sys, io, re, importlib.util, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sll", R + r"\scripts\sw_simulation_loads.py")
m = importlib.util.module_from_spec(spec); sys.modules["sll"] = m
spec.loader.exec_module(m)
src = open(R + r"\scripts\sw_simulation_loads.py", encoding="utf-8").read()
bad = 0
for fn in m.__all__:
    f = getattr(m, fn, None)
    if not callable(f) or fn.startswith("SWS") or fn in ("OFFICIAL_LOAD_SIGNATURES","_require","_check"):
        continue
    # 找该函数体内 _check(..., "Member", N, ...) 的 N
    m2 = re.search(r'def %s\(.*?(?=\ndef |\Z)' % fn, src, re.S)
    if not m2: continue
    n = re.search(r'_check\(\s*manager,\s*"(\w+)",\s*(\d+)', m2.group(0))
    if not n: continue
    member, arity = n.group(1), int(n.group(2))
    exp = m.OFFICIAL_LOAD_SIGNATURES.get(member)
    ok = "OK " if exp == arity else "BAD"
    if exp != arity: bad += 1
    print("  %s %-32s 声明=%s 官方=%s" % (ok, fn, arity, exp))
print("  不一致 %d 处" % bad)
