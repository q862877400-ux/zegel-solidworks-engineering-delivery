import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import importlib.util
spec = importlib.util.spec_from_file_location("g", r"D:\AI\SW\tools\gen_family_coverage.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
hits = set()
skipped = 0
for line in p.read_text(encoding="utf-8").splitlines():
    if g.SKIP.match(line):
        skipped += 1
        continue
    hits |= set(g.LITERAL.findall(line))
print("LITERAL 模式 =", g.LITERAL.pattern)
print("扫到 X/Y/Z =", sorted(h for h in hits if h in ("X","Y","Z")))
print("被 SKIP 掉的行数 =", skipped)
# 看 ISketchPoint 附近那几行到底长什么样
lines = p.read_text(encoding="utf-8").splitlines()
i = next(k for k,l in enumerate(lines) if "'ISketchPoint': (" in l)
for k in range(i, i+14):
    print("  %d| %r" % (k+1, lines[k]))
