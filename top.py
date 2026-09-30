import sys, re, pickle
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
hits = pickle.load(open(r"D:\AI\SW\_hits.pkl","rb"))
# 真正有价值的：带具体 API 名 / 数字参数 / 具体错误码
KEEP = re.compile(r"(Nothing|Empty|DumbDispatch|VARIANT|0x800|TypeError|"
                  r"SelectByID2|FeatureCut4|FeatureExtrusion|OpenDoc|LoadFile|"
                  r"\d+\s*参|不是\s*\d|第\s*\d+\s*步|swEndCond|AccessSelections|"
                  r"ReleaseSelectionAccess|GetMassProperties|_IDispatch|"
                  r"Base64|Variant|invoke|sys\.argv|DllImport|"
                  r"swSelect|eight|seven|twenty|seventy|33\s*参|23\s*参)", re.I)
out = []
for repo, items in hits.items():
    for path, line in items:
        if KEEP.search(line):
            out.append((repo, path, line))
print("高价值线索 %d 条\n" % len(out))
for repo, path, line in out[:38]:
    print("[%s] %s" % (repo, path))
    print("   " + line[:150])