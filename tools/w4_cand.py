import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"" + _ROOT_S + r"\scripts", r"" + _ROOT_S + r"\mcp-server",
                r"" + _ROOT_S + r""]
import register_capabilities as rc


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
exposed = {x.function for x in rc.all_specs()}
INJECTABLE = ("model", "sw_app", "study")

CAND = ["chamfer", "fillet", "extrude", "extrude_cut", "revolve_boss", "shell", "linear_pattern",
        "circular_pattern", "mirror_feature", "insert_dome", "insert_helix", "create_draft",
        "configure_linear_pattern", "configure_curve_driven_pattern", "create_sketch_chamfer"]

print("  ══ 能力层里的「建/改特征」函数：哪些没挂、且首参可注入 ══")
rows = []
for mod in sorted(p.stem for p in Path(r"" + _ROOT_S + r"\scripts").glob("sw_*.py")):
    try:
        m = __import__(mod)
    except Exception:                                          # noqa: BLE001
        continue
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if not callable(o) or not getattr(o, "__module__", "").endswith(mod):
            continue
        if n in exposed:
            continue
        if not any(k in n for k in CAND):
            continue
        try:
            sig = inspect.signature(o)
        except Exception:                                      # noqa: BLE001
            continue
        first = list(sig.parameters)[0] if sig.parameters else ""
        rows.append((mod, n, str(sig), first in INJECTABLE, first))

print("  合计 %d 个" % len(rows))
print()
print("  ★ 首参**可注入**（可直接挂）:")
for mod, n, sig, ok, first in rows:
    if ok:
        print("    %-18s %-34s %s" % (mod, n, sig[:62]))
print()
print("  ⚠ 首参不是注入点的（需包装层）:")
for mod, n, sig, ok, first in rows:
    if not ok:
        print("    %-18s %-34s 首参=%-10s %s" % (mod, n, first, sig[:44]))
