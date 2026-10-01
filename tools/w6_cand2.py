import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
sys.path[:0] = [str(REPO / "scripts"), str(REPO / "mcp-server"), str(REPO)]

import register_capabilities as rc
exposed = {x.function for x in rc.all_specs()}

CAND = ["get_components", "collect_mate_feature_summary", "get_interference_detection",
        "suppress_component", "unsuppress_component", "replace_component",
        "collect_assembly_doc_evidence", "add_component", "collect_mate_entity_evidence"]

print("  ══ 能力层里的装配函数：签名 + 是否已挂 ══")
for mod_name in ("sw_assembly", "sw_assembly_doc"):
    m = __import__(mod_name)
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if not callable(o) or not getattr(o, "__module__", "").endswith(mod_name):
            continue
        if n not in CAND:
            continue
        try:
            sig = str(inspect.signature(o))
        except Exception:                                      # noqa: BLE001
            sig = "?"
        first = list(inspect.signature(o).parameters)[:1]
        print("    %-18s %-34s %-46s 首参=%-10s 已挂=%s"
              % (mod_name, n, sig[:44], first[0] if first else "", n in exposed))

print()
print("  ══ 装配相关模块里的其他候选（首参 model 且未挂）══")
for mod_name in ("sw_assembly", "sw_assembly_doc"):
    m = __import__(mod_name)
    for n in sorted(dir(m)):
        if n.startswith("_") or n in exposed:
            continue
        o = getattr(m, n)
        if callable(o) and getattr(o, "__module__", "").endswith(mod_name):
            try:
                sig = inspect.signature(o)
            except Exception:                                  # noqa: BLE001
                continue
            ps = list(sig.parameters)
            if ps and ps[0] == "model":
                print("    %-18s %-38s %s" % (mod_name, n, str(sig)[:56]))
