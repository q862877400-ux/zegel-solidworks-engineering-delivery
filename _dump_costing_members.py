"""列 ICostAnalysis / ICostPart 的反射成员 + read_cost_analysis 的实现。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

t = Path(r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt").read_text(
    encoding="utf-8", errors="replace").splitlines()
cur = None
for l in t:
    s = l.strip()
    if s.startswith("## "):
        cur = s[3:]
        if cur in ("ICostAnalysis", "ICostPart", "ICostBody", "ICostingDefaults"):
            print("  ── %s ──" % cur)
        continue
    if cur in ("ICostAnalysis", "ICostPart", "ICostBody", "ICostingDefaults") and s:
        print("     %s" % s)

print()
print("  ══ read_cost_analysis 的实现 ══")
src = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_costing.py").read_text(
    encoding="utf-8").splitlines()
i = next(k for k, l in enumerate(src) if l.startswith("def read_cost_analysis"))
for j in range(i, min(i + 28, len(src))):
    if j > i and (src[j].startswith("def ") or src[j].startswith("# ── 来源")):
        break
    print("    %s" % src[j])
