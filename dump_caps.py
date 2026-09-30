import json, sys
sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
d = json.load(open(R + r"\capabilities.yaml", encoding="utf-8"))
caps = d["capabilities"]
print("  schema_version = %r   （提案要求迁到 \"2.0\"）" % d.get("schema_version"))
print("  条数 = %d" % len(caps))
print()
CAD = ("solidworks", "autocad")
for lv in ("verified", "pilot", "not_implemented"):
    rows = [c for c in caps if c.get("level") == lv]
    if not rows: continue
    print("  ── level=%s（%d 条）──" % (lv, len(rows)))
    for c in rows:
        be = c.get("backends") or []
        is_cad = any(b.startswith(CAD) for b in be)
        vv = c.get("verified_versions")
        print("     %-42s backends=%-24s vv=%-14s %s" % (
            c["id"], ",".join(be) or "-", repr(vv), "CAD" if is_cad else ""))
    print()