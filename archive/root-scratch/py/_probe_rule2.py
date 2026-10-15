import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\mcp-server")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import importlib
import register_capabilities as rc

specs = rc.all_specs()
print("  all_specs(): %d 条" % len(specs))

#: ① 哪些工具的**实现模块**是 sw_part / 其它几何模块
from collections import defaultdict
bymod = defaultdict(list)
for s in specs:
    bymod[s.module].append(s)
print()
print("  按实现模块分组（前 12）:")
for m, ss in sorted(bymod.items(), key=lambda kv: -len(kv[1]))[:12]:
    print("    %-24s %d 条" % (m, len(ss)))

#: ② 长度名可疑但**没有 `_mm` 后缀**的参数
LEN_WORDS = ("radius", "diameter", "depth", "thickness", "distance", "width",
             "height", "length", "offset", "spacing", "pitch", "size")
bad = []
for s in specs:
    for p in s.params:
        n = p.name.lower()
        if any(w in n for w in LEN_WORDS) and not n.endswith("_mm"):
            bad.append((s.name, p.name, s.module))
print()
print("  ⚠ 参数名像长度、却**不以 `_mm` 结尾**: %d 处" % len(bad))
for name, pname, mod in bad[:20]:
    print("    %-46s %-18s (%s)" % (name, pname, mod))
