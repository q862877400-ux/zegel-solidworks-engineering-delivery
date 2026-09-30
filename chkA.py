import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
M = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
for fam in ("ITableAnnotation", "ISectionViewData", "IAnnotationView", "IModelViewManager"):
    g = re.search(r"^    '%s': \{(.*?)\n    \}," % fam, M, re.M | re.S)
    if g:
        members = re.findall(r"^        '(\w+)': (\d+),", g.group(1), re.M)
        print("  %-22s 已登记 %3d 成员  例: %s" % (fam, len(members), ", ".join(m[0] for m in members[:4])))
    else:
        print("  %-22s ** 索引里没有 **" % fam)