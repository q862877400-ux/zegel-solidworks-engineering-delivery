import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")
import sw_part as p

TARGETS = ["start_sketch", "end_sketch", "sketch_line", "sketch_circle",
           "sketch_corner_rectangle", "sketch_rectangle"]
for n in TARGETS:
    fn = getattr(p, n, None)
    if fn is None:
        print("  %-26s （不存在）" % n)
        continue
    print("  ══ %s%s ══" % (n, inspect.signature(fn)))
    doc = (inspect.getdoc(fn) or "").splitlines()
    for l in doc[:8]:
        print("      %s" % l[:104])
    print()
