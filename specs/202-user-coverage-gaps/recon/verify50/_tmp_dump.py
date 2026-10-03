import sys, importlib, inspect, os
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"D:\AI\SW\mcp-server")
sys.path.insert(0, r"D:\AI\SW\scripts")
rows = []
for b in range(31, 46):
    m = importlib.import_module("tool_specs_batch%d" % b)
    specs = []
    for a in [x for x in dir(m) if x.startswith("SPECS")]:
        v = getattr(m, a)
        specs.extend(v if isinstance(v, list) else [v])
    for sp in specs:
        try:
            mod = importlib.import_module(sp.module)
        except Exception as e:
            rows.append("### %d %s :: IMPORT FAIL %r" % (b, sp.name, e)); continue
        fn = getattr(mod, sp.function, None)
        if fn is None:
            rows.append("### %d %s :: MISSING %s.%s" % (b, sp.name, sp.module, sp.function)); continue
        try:
            src = inspect.getsource(fn)
        except Exception as e:
            src = "SRCFAIL %r" % e
        try:
            ds = inspect.getdoc(fn) or ""
        except Exception as e:
            ds = "DOCFAIL %r" % e
        rows.append("### B%d %s -> %s.%s\n--- SPEC DOC ---\n%s\n--- FN DOCSTRING ---\n%s\n--- FN SOURCE ---\n%s" % (b, sp.name, sp.module, sp.function, sp.doc, ds, src))
open(r"D:\AI\SW\specs\202-user-coverage-gaps\recon\verify50\_dump.txt","w",encoding="utf-8").write("\n".join(rows))
print("ok", len(rows))
