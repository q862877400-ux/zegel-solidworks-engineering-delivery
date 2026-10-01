import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SWAPI = Path(r"C:\swapi\types")
rows = json.loads(
    Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.json").read_text(encoding="utf-8"))


def kinds(iface):
    dd = SWAPI / iface
    m = p = 0
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
    return m, p


#: 候选判据：方法数 >= 属性数 ⇒ 像「动作接口」；否则像「查询/数据接口」
def is_action(iface):
    m, p = kinds(iface)
    return m > 0 and m >= p


done = [r["family"] for r in rows if (r.get("used") or 0) > 0]
todo = [r["family"] for r in rows if (r.get("used") or 0) == 0 and (r.get("members") or 0) > 0]

print("  ── 在这个判据下：动作型接口的占比 ──")
for label, arr in (("★ 我们做过的", done), ("  有成员但没做过", todo)):
    n = sum(1 for f in arr if is_action(f))
    print("    %-18s %4d 族 · **动作型 %3d（%.0f%%）**" % (label, len(arr), n, 100.0 * n / max(len(arr), 1)))

d = json.loads(Path(r"D:\AI\SW\output\candidate-51.json").read_text(encoding="utf-8"))
pool = [r["family"] for r in d["with_source"] + d["without_source"]]
print("")
print("  ── 51 个候选池里，**动作型**的有几个 ──")
acts = [f for f in pool if is_action(f)]
print("    **%d / %d**" % (len(acts), len(pool)))
for f in acts:
    m, p = kinds(f)
    print("      %-46s 方法 %2d · 属性 %2d" % (f, m, p))
print("")
print("  ── 容器型（属性占多数）的 %d 个，举几个 ──" % (len(pool) - len(acts)))
for f in [x for x in pool if not is_action(x)][:10]:
    m, p = kinds(f)
    print("      %-46s 方法 %2d · 属性 %2d" % (f, m, p))
