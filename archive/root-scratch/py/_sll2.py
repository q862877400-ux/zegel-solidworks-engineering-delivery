import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: ("CALL", n, a)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sll", R + r"\scripts\sw_simulation_loads.py")
m = importlib.util.module_from_spec(spec); sys.modules["sll"] = m
spec.loader.exec_module(m)
try:
    m._check(object(), "AddPressure", 9, "a","b","c")
    print("  [FAIL] 错 arity 没被拦")
except ValueError as e:
    print("  [OK] 错 arity 被拦:", str(e)[:70])
print("  正确 arity 返回:", m._check(object(), "AddForce", 3, 1, "E", None))
