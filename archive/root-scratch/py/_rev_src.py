import sys, inspect
sys.path.insert(0, ".")
import importlib
for m, f in [("scripts.sw_topology","create_thickness_control"),
             ("scripts.sw_topology","create_preserved_region"),
             ("scripts.sw_topology","create_mass_constraint"),
             ("scripts.sw_topology","create_factor_of_safety_constraint")]:
    mod = importlib.import_module(m)
    fn = getattr(mod, f)
    print("="*70)
    print(m, f, inspect.signature(fn))
    src = inspect.getsource(fn)
    print(src[:2200])
