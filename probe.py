import importlib.util, io, re, sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
spec = importlib.util.spec_from_file_location("g", r"D:\AI\SW\tools\gen_family_coverage.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
line = "        'X',"
p = g.LITERAL.pattern
print("pattern repr =", repr(p))
print("findall      =", g.LITERAL.findall(line))
for probe in (r"[\"']", r"[A-Za-z_]\w+", r"[A-Za-z_]\w*", r"\w+", r"[,:}]", r"[\"']\s*[,:}]"):
    try:
        print("  %-22r -> %r" % (probe, re.findall(probe, line)))
    except Exception as e:
        print("  %-22r !! %s" % (probe, e))