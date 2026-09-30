import sys, io, types, dataclasses, importlib.util
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
def faithful(obj, name, *a, **k):
    if obj is None: return None
    at = getattr(obj, name, None)
    if at is None: return None
    if callable(at):
        try: return at(*a, **k)
        except TypeError: return at()
    return at
class Stub(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"): raise AttributeError(n)
        return lambda *a, **k: None
sys.modules["sw_connect"] = Stub("sw_connect"); sys.modules["sw_connect"].get_com_member = faithful
sys.modules["sw_part"] = Stub("sw_part")
sys.modules.setdefault("sw_document_data", Stub("sw_document_data"))
sys.modules.setdefault("sw_preflight", Stub("sw_preflight"))
sys.path.insert(0, str(R / "scripts"))
import sw_hole_features as m
straight, tapered = [], []
class El:
    def __getattr__(self, name):
        def _set(v):
            (tapered if name in {"EndConditionOverride","UseStandardDepth"} else straight).append(name)
        return _set
m.configure_straight_tap(El(), custom_sizing=1, end_shape=2, equation=3, thread_class=4,
                         thread_class_override=True, drill_point_angle=118.0, drill_point_angle_override=True)
print("  straight:", straight)
tapered.clear()
m.configure_tapered_tap(El(), custom_sizing=1, thread_class=2, thread_class_override=True,
                        end_condition_override=True, use_standard_depth=True)
print("  tapered :", tapered)
