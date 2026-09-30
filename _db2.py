import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW\tools")
import gen_family_coverage as g
t = g.repo_members()
mems = g.family_members("ICWStaticStudyOptions")
print("  ICWStaticStudyOptions 成员数 =", len(mems), "前 5:", mems[:5])
for probe in ("AdaptiveMethodType", "BucklingModes", "CheckFlowPressure2", "GetMaterialName"):
    print("  %-24s family=%s  repo=%s" % (probe, probe in mems, probe in t))
src = open(r"C:\swprojects\sw-skill-fork\scripts\sw_simulation_study_options.py", encoding="utf-8").read()
i = src.find("AdaptiveMethodType")
print("  源码样本:", repr(src[i-30:i+40]))
