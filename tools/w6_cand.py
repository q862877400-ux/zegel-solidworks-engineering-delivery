import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])

sys.path[:0] = [r"" + _ROOT_S + r"\scripts", r"" + _ROOT_S + r"\mcp-server",
                r"" + _ROOT_S + r""]

print("  ══ ① selection 机制（W4 那批没用它；本批第一次用）══")
import sw_selection_spec as ss
for n in ("resolve_selection", "resolve_entity", "ENTITY_KINDS"):
    o = getattr(ss, n, None)
    if o is None:
        print("    %s: 不存在" % n)
    elif callable(o):
        print("    %-20s %s" % (n, inspect.signature(o)))
    else:
        print("    %-20s %r" % (n, o))
print()
print("  ══ ② 断言「倒角真的做了」能用什么读数 ══")
import register_capabilities as rc

for x in rc.all_specs():
    if any(k in x.name for k in ("mass", "volume", "bbox", "bounding", "model_summary", "evidence")):
        print("    %-48s module=%-18s fn=%s" % (x.name, x.module, x.function))
print()
print("  ══ ③ 能力层里有没有「体积/质量属性」的函数 ══")
for mod in ("sw_part", "sw_delivery", "sw_inspect"):
    try:
        m = __import__(mod)
    except Exception:                                          # noqa: BLE001
        continue
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if callable(o) and getattr(o, "__module__", "").endswith(mod):
            if any(k in n.lower() for k in ("mass", "volume", "propert", "body_box", "count")):
                try:
                    print("    %-16s %-32s %s" % (mod, n, str(inspect.signature(o))[:52]))
                except Exception:                              # noqa: BLE001
                    pass
