import sys, re, json
from pathlib import Path
sys.path.insert(0, "mcp-server")
import importlib
targets = []
for i in range(11, 17):
    mod = importlib.import_module("tool_specs_batch%d" % i)
    specs = next(getattr(mod, n) for n in dir(mod) if n.startswith("SPECS_"))
    for s in specs:
        targets.append((i, s.name, s.module, s.function))
kf = Path(r"D:\AI\SW\docs\known-facts.md").read_text(encoding="utf-8")
BAD = ("失败", "返回 False", "返回False", "到不了", "Obsolete", "不可达", "本来就坏", "一直返回", "打不通", "全 False")
for i, name, mod, fn in targets:
    hits = []
    for m in re.finditer(re.escape(fn), kf):
        line = kf[:m.start()].count("\n") + 1
        ctx = kf[max(0, m.start()-200):m.start()+200].replace("\n", " ")
        if any(b in ctx for b in BAD):
            hits.append((line, ctx))
    if hits:
        print("### batch%d  %s  ->  %s.%s" % (i, name, mod, fn))
        for line, ctx in hits[:3]:
            print("    known-facts line %d: ...%s..." % (line, ctx[:300]))
    else:
        print("### batch%d  %s  ->  %s.%s : no known-facts failure mention" % (i, name, mod, fn))
