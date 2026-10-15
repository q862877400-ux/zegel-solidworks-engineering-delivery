import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path[:0] = [r"C:\swprojects\sw-skill-fork\mcp-server"]
import register_capabilities as rc

exposed = {x.function for x in rc.all_specs()}
import sw_sketch as m

INJECTABLE = ("model", "sw_app", "study")

have_model, need_other = [], []
for n in sorted(dir(m)):
    if n.startswith("_"):
        continue
    o = getattr(m, n)
    if not callable(o) or not getattr(o, "__module__", "").endswith("sw_sketch"):
        continue
    if n in exposed:
        continue
    try:
        sig = inspect.signature(o)
    except Exception:
        continue
    params = list(sig.parameters)
    first = params[0] if params else ""
    (have_model if first in INJECTABLE else need_other).append((n, str(sig), first))

print("  ── ★ 首参**是注入点**（可直接挂）的未挂函数 ──")
for n, s, _f in have_model:
    print("    %-34s %s" % (n, s[:74]))
print("    （共 %d 个）" % len(have_model))
print()
print("  ── 首参**不是**注入点的（需包装层，同 view/results 那类）──")
for n, s, f in need_other:
    print("    %-34s 首参=%-12s %s" % (n, f, s[:56]))
print("    （共 %d 个）" % len(need_other))
print()
print("  ── 有没有「从 model 取活动草图」的 helper（包装层要用）──")
import sw_part
for modname, mod in (("sw_sketch", m), ("sw_part", sw_part)):
    for n in sorted(dir(mod)):
        if "sketch" in n.lower() and not n.startswith("__"):
            try:
                sig = str(inspect.signature(getattr(mod, n)))
            except Exception:
                continue
            if "model" in sig.split(")")[0]:
                print("    %s.%-30s %s" % (modname, n, sig[:64]))
