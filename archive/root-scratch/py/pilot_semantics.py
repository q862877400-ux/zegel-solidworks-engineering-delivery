import json, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"C:\swprojects\sw-skill-fork\capabilities.yaml", encoding="utf-8"))
caps = d["capabilities"]
print("  按 level × allowed_modes 交叉：")
tab = collections.defaultdict(collections.Counter)
for c in caps:
    tab[c["level"]]["+".join(sorted(c.get("allowed_modes") or []))] += 1
for lv in ("verified", "pilot", "not_implemented"):
    for modes, n in sorted(tab[lv].items()):
        print("     %-16s %-32s %d 条" % (lv, modes, n))
print()
print("  pilot 且 verified_versions 非空（= 有运行证据）:")
for c in caps:
    if c["level"] == "pilot" and c.get("verified_versions"):
        print("     %-40s vv=%-18s modes=%s" % (c["id"], c["verified_versions"], c.get("allowed_modes")))