import sys, types, io, importlib.util, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
sys.path.insert(0, R + r"\scripts")
import importlib
for name in ("sw_hole_features","sw_assembly","sw_export"):
    try:
        m = importlib.import_module(name)
        fns = [k for k in dir(m) if k.startswith(("configure_","collect_","query_","set_mass","get_mass"))]
        print("  %-18s OK  新增: %s" % (name, ", ".join(fns)))
    except Exception as e:
        print("  %-18s FAIL %s: %s" % (name, type(e).__name__, e))
