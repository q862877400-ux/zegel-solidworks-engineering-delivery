import sys, importlib, inspect
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"D:\AI\SW\mcp-server"); sys.path.insert(0, r"D:\AI\SW\scripts")
rows=[]
for b in range(31,46):
    m = importlib.import_module("tool_specs_batch%d" % b)
    specs=[]
    for a in [x for x in dir(m) if x.startswith("SPECS")]:
        v=getattr(m,a); specs.extend(v if isinstance(v,list) else [v])
    for sp in specs:
        try:
            fn=getattr(importlib.import_module(sp.module), sp.function)
            sig=inspect.signature(fn)
        except Exception as e:
            rows.append("B%d %s SIGFAIL %r"%(b,sp.name,e)); continue
        params=sig.parameters
        for p in sp.params:
            if p.name not in params:
                rows.append("B%d %s PARAM_NOT_IN_FN %s"%(b,sp.name,p.name)); continue
            tp=params[p.name]
            if p.default is not None and tp.default is inspect._empty:
                rows.append("B%d %s FN_HAS_NO_DEFAULT_BUT_SPEC_DOES %s"%(b,sp.name,p.name))
            if p.default is None and tp.default is not inspect._empty:
                rows.append("B%d %s SPEC_REQUIRED_BUT_FN_HAS_DEFAULT %s (fn=%r)"%(b,sp.name,p.name,tp.default))
        req=[n for n,v in params.items() if v.default is inspect._empty and v.kind in (v.POSITIONAL_OR_KEYWORD,v.KEYWORD_ONLY)]
        alias=set((sp.param_alias or {}).values())
        miss=[n for n in req if n not in [p.name for p in sp.params] and n not in alias]
        if miss: rows.append("B%d %s FN_REQUIRED_UNDECLARED %s"%(b,sp.name,miss))
print("\n".join(rows) if rows else "NONE")
