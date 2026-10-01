import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\mcp-server")
sys.stdout.reconfigure(encoding="utf-8")
import register_capabilities as rc

ANGLE_WORDS = ("angle", "degrees", "deg", "radians", "rad", "draft", "taper")
specs = rc.all_specs()
bad = []
for s in specs:
    for p in s.params:
        low = p.name.lower()
        if any(w in low for w in ANGLE_WORDS) and not low.endswith("_deg"):
            bad.append((s.name, p.name, p.kind.__name__, s.module))
print("  参数名像角度、却不以 `_deg` 结尾: **%d 处**" % len(bad))
for name, pname, kind, mod in bad:
    print("    %-48s %-24s %-6s (%s)" % (name, pname, kind, mod))
