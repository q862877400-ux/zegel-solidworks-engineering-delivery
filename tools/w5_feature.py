import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_part as p

for n in ("extrude_boss", "extrude_cut", "extrude_midplane", "chamfer", "fillet"):
    fn = getattr(p, n, None)
    if fn is None:
        print("  %-20s （不存在）" % n)
        continue
    print("  ══ %s%s ══" % (n, inspect.signature(fn)))
    for l in (inspect.getdoc(fn) or "").splitlines()[:12]:
        print("      %s" % l[:104])
    print()
