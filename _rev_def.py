import sys, inspect
sys.path.insert(0, "mcp-server"); sys.path.insert(0, ".")
import importlib
from tool_registry import effective_inject
for i in range(11, 17):
    m = importlib.import_module("tool_specs_batch%d" % i)
    specs = next(getattr(m, n) for n in dir(m) if n.startswith("SPECS_"))
    for s in specs:
        mod = importlib.import_module("scripts.%s" % s.module)
        fn = getattr(mod, s.function)
        sig = inspect.signature(fn)
        for p in s.params:
            tgt = s.param_alias.get(p.name, p.name)
            if tgt is None:
                continue
            real = sig.parameters.get(tgt)
            if real is None:
                print("MISSING on target: %s.%s" % (s.name, tgt)); continue
            rd = real.default
            declared = p.default
            same = (declared is ... and rd is inspect.Parameter.empty) or (declared == rd)
            if not same:
                print("%-58s %-18s declared=%-8r real=%r" % (s.name, p.name, declared, rd))
