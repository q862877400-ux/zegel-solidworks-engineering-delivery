import sys, importlib
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"D:\AI\SW\mcp-server")
sys.path.insert(0, r"D:\AI\SW\scripts")
out = []
for b in range(31, 46):
    try:
        m = importlib.import_module("tool_specs_batch%d" % b)
    except Exception as e:
        out.append("BATCH %d IMPORT FAIL %s" % (b, e)); continue
    names = [a for a in dir(m) if a.startswith("SPECS")]
    specs = []
    for a in names:
        v = getattr(m, a)
        specs.extend(v if isinstance(v, list) else [v])
    for sp in specs:
        out.append("%d|%s|%s.%s" % (b, sp.name, sp.module, sp.function))
print(len(out))
print("\n".join(out))
