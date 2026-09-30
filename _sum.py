import sys, io
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
import importlib.util, types
c = types.ModuleType("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
R = Path(r"C:\swprojects\sw-skill-fork\scripts")
tot_f = tot_c = 0
for p in sorted(R.glob("sw_api_*.py")):
    n = p.stem[7:]
    sp = importlib.util.spec_from_file_location(p.stem, p)
    m = importlib.util.module_from_spec(sp); sys.modules[p.stem]=m; sp.loader.exec_module(m)
    nc = sum(len(v) for v in m.ARITY.values())
    tot_f += len(m.FAMILIES); tot_c += nc
    print("  %-18s %4d 族 / %5d 能力" % (n, len(m.FAMILIES), nc))
print("  合计 %d 族 / %d 能力" % (tot_f, tot_c))
