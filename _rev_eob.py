import sys, inspect
sys.path.insert(0, ".")
import importlib
m = importlib.import_module("scripts.sw_selection_spec")
print(inspect.getsource(m.entities_on_body))
v = importlib.import_module("scripts.sw_view")
print(inspect.getsource(v.get_active_view))
