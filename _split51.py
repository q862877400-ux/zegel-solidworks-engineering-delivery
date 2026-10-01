import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SWAPI = Path(r"C:\swapi\types")
d = json.loads(Path(r"D:\AI\SW\output\candidate-51.json").read_text(encoding="utf-8"))
rows = d["with_source"] + d["without_source"]


def kinds(iface):
    dd = SWAPI / iface
    m = p = o = 0
    if dd.is_dir():
        for f in dd.glob("*.md"):
            if f.name == "_overview.md":
                continue
            t = f.read_text(encoding="utf-8", errors="replace")[:800]
            k = re.search(r"(?m)^kind:\s*(\w+)", t)
            k = k.group(1).lower() if k else "?"
            if k == "method":
                m += 1
            elif k == "property":
                p += 1
            else:
                o += 1
    return m, p, o


#: 名字里带这些词的，多半是「数据容器」（一个特征的内部数据结构），不是动作
CONTAINER = re.compile(r"FeatureData|Properties|Options|Parameters|Data$|Def$")

print("  %-46s %6s %8s %8s  %s" % ("接口", "成员", "方法", "属性", "像什么"))
act, cont = [], []
for r in rows:
    m, p, o = kinds(r["family"])
    is_c = bool(CONTAINER.search(r["family"]))
    (cont if is_c else act).append(r["family"])
    if len(act) + len(cont) <= 20:
        print("  %-46s %6d %8d %8d  %s" % (r["family"], r["members"], m, p, "容器" if is_c else "?"))

print("")
print("  ── 汇总（51 个候选）──")
print("    名字像【数据容器】的: **%d 个**" % len(cont))
print("    名字不像容器的      : **%d 个**" % len(act))
print("      后者可能是动作: %s" % ", ".join(act))
