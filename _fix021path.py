import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\specs\021-alias-bucket-audit\tasks.md")
t = P.read_text(encoding="utf-8")
D = "\u2192 \u9a8c\u6536:"
bad = [l for l in t.splitlines() if D in l and "triage_union_gaps" in l]
print("  待修行: %r" % (bad,))
if bad:
    t = t.replace(bad[0], "  `" + D + "` `Select-String docs\\union-gap-triage-sample.md -Pattern 'aliases'`")
    P.write_text(t, encoding="utf-8")
    print("  已改成真实路径的验收命令")
else:
    print("  没找到该行")
