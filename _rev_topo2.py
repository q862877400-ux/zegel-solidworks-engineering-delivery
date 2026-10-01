import sys, inspect
sys.path.insert(0, ".")
import importlib
m = importlib.import_module("scripts.sw_topology")
for f in ("create_demold_control", "create_symmetry_control", "create_stress_constraint"):
    fn = getattr(m, f)
    print("="*72)
    print(f, inspect.signature(fn))
    print(inspect.getsource(fn))
