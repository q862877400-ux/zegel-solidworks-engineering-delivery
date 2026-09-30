import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("h", r"C:\swprojects\sw-skill-fork\scripts\sw_hubs.py")
m = importlib.util.module_from_spec(spec); sys.modules["h"] = m
spec.loader.exec_module(m)
print("  GetFeatureCount arity =", m.HUB_ARITY["IFeatureManager"].get("GetFeatureCount"))
try:
    m.call_hub(None, "IFeatureManager", "GetFeatureCount")
    print("  未拦截！")
except Exception as e:
    print("  拦住了:", type(e).__name__, e)
