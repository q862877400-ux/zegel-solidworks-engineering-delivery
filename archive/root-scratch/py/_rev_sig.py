import sys, inspect, importlib
sys.path.insert(0, "mcp-server")
sys.path.insert(0, ".")
import register_capabilities as rc

BATCHES = ["tool_specs_batch%d" % i for i in range(11, 17)]
for bname in BATCHES:
    mod = importlib.import_module(bname)
    specs = next(getattr(mod, n) for n in dir(mod) if n.startswith("SPECS_"))
    print("=== %s: %d specs ===" % (bname, len(specs)))
    for spec in specs:
        try:
            tmod = importlib.import_module("scripts.%s" % spec.module)
            fn = getattr(tmod, spec.function)
            sig = inspect.signature(fn)
        except Exception as e:
            print("  [ERR] %s -> %s.%s : %r" % (spec.name, spec.module, spec.function, e))
            continue
        real = [(p.name, p.kind, p.default) for p in sig.parameters.values()]
        realnames = [n for n, k, d in real]
        # declared mapping
        decl = []
        for p in spec.params:
            if p.name in spec.param_alias and spec.param_alias[p.name] is None:
                continue
            decl.append(spec.param_alias.get(p.name, p.name))
        inj = spec.inject
        allpos = ([inj] if inj else []) + decl
        problems = []
        if inj and inj not in realnames:
            problems.append("inject=%r is NOT a real param name" % inj)
        for d in decl:
            if d not in realnames:
                problems.append("param %r not in signature" % d)
        # order check (subset)
        present = [n for n in realnames if n in allpos]
        want = [n for n in allpos if n in present]
        if present != want:
            problems.append("order: declared=%r real=%r" % (want, present))
        # required/positional check
        for n, k, d in real:
            if n in allpos and k is inspect.Parameter.VAR_KEYWORD:
                problems.append("%r is **kwargs" % n)
        flag = "OK " if not problems else "BAD"
        print("  [%s] %s" % (flag, spec.name))
        print("        decl order: %r" % (allpos,))
        print("        real sig  : %r" % ([ (n, str(k), ("<req>" if d is inspect.Parameter.empty else d)) for n,k,d in real],))
        for pr in problems:
            print("        !! %s" % pr)
