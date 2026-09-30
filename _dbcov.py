import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW\tools")
import gen_family_coverage as g
mems = g.family_members("ICWResults")
print("  ICWResults 抽出成员数 =", len(mems))
print("  前 8 个:", mems[:8])
t = g.repo_members()
print("  repo_members() 总成员名数 =", len(t))
for probe in ("CreatePlot", "ActivatePlot", "DeletePlot", "GetPlot", "GetCoordinateSystem"):
    print("  %-20s 在 family_members=%s  在 repo_members=%s" % (probe, probe in mems, probe in t))
