import sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sp = importlib.util.spec_from_file_location("j", r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_index.py")
m = importlib.util.module_from_spec(sp); sys.modules["j"]=m; sp.loader.exec_module(m)
print("规模:", m.summarize())
cats = m.list_categories()
print("分类 %d 个，含关键词的:" % len(cats))
for kw in ("导轨","型材","直线","丝杆","轴承"):
    hit = [c for c in cats if kw in c]
    print("   %-4s %d: %s" % (kw, len(hit), hit[:4]))
print()
for kw in ("导轨","铝型材","减速机","电磁阀"):
    h = m.search(kw)
    print("search(%-8s) -> %d 条  例: %s" % (kw, len(h), h[0]["code"] if h else "-"))