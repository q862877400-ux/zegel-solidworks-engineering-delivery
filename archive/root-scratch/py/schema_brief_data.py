import json, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"

print("=" * 66)
print("A. 上游现有 capabilities.yaml 的 shape（他要兼容这个）")
print("=" * 66)
d = json.load(open(R + r"\capabilities.yaml", encoding="utf-8"))
print("  顶层键: %s" % list(d.keys()))
caps = d["capabilities"]
print("  条目数: %d" % len(caps))
print("  每条字段: %s" % list(caps[0].keys()))
print("  level 分布: %s" % dict(collections.Counter(c.get("level") for c in caps)))
print()
print("  一条完整样例（最短的一条）:")
s = min(caps, key=lambda c: len(json.dumps(c, ensure_ascii=False)))
print("    " + json.dumps(s, ensure_ascii=False, indent=6).replace("\n", "\n    "))

print()
print("=" * 66)
print("B. 要登记的操作：域分布（384 条按 16 域）")
print("=" * 66)
src = json.load(open(R + r"\tools\union-sources.json", encoding="utf-8"))
dom = collections.Counter()
for s_ in src["sources"]:
    for k, v in s_["domains"].items():
        dom[k] += len(v)
for k, v in dom.most_common():
    print("    %-14s %3d 个操作" % (k, v))
print("    合计（并集去重前）%d" % sum(dom.values()))
print("    并集去重后: %d" % src["union_size"])

print()
print("=" * 66)
print("C. 每家来源可用的字段（决定 level 能自动判到哪一级）")
print("=" * 66)
for s_ in src["sources"]:
    print("    %-38s declared_verified=%r" % (s_["repo"], s_["declared_verified"]))
    print("        license=%s  tool_count=%d  operation_count=%d" % (s_["license"], s_["tool_count"], s_["operation_count"]))