import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("app", r"C:\swprojects\sw-skill-fork\scripts\sw_sldworks_app.py")
m = importlib.util.module_from_spec(spec); sys.modules["app"] = m
spec.loader.exec_module(m)
print("  枚举表:", {k: len(getattr(m, k)) for k in
      ("SW_DOC_TYPES","SW_OPEN_DOC_OPTIONS","SW_SAVE_AS_OPTIONS","SW_SAVE_AS_VERSION",
       "SW_PREF_STRINGS","SW_PREF_INTEGERS","SW_PREF_TOGGLES","SW_PREF_DOUBLES","SW_SELECT_TYPES")})
seen = []
def fake(o, n, *a, **k):
    seen.append((n, a))
    return 2 if n == "GetDocuments" else ("zh-CN" if n == "GetCurrentLanguage" else 1234)
m.get_com_member = fake
print("  证据回读:", m.collect_app_evidence(object()))
print("  set_selection_filter(swSelFACES):", m.set_selection_filter(object(), "swSelFACES", True))
print("  该次调用参数:", seen[-1])
try:
    m.set_selection_filter(object(), "swSelNotReal", True); print("  [FAIL] 未知枚举未拦")
except KeyError as e:
    print("  [OK] 未知枚举被拦:", str(e)[:60])
try:
    m._checked(object(), "GetFirstDocument", 1); print("  [FAIL] 错 arity 未拦")
except ValueError:
    print("  [OK] 错 arity 被拦")
