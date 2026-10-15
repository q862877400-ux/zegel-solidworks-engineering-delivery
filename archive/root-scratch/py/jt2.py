import sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
sp = importlib.util.spec_from_file_location("j", r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_index.py")
m = importlib.util.module_from_spec(sp); sys.modules["j"]=m; sp.loader.exec_module(m)
print("规模:", m.summarize())
for kw in ("铝型材","导轨","丝杆","直线导轨","工业铝型材及配件"):
    h = m.search(kw)
    c = m.search(category=kw)
    print("  %-14s 关键词 %-6d 条   按分类 %-6d 条" % (kw, len(h), len(c)))