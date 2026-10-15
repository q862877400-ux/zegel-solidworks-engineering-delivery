import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"C:\swprojects\sw-skill-fork\mcp-server", r"C:\swprojects\sw-skill-fork"]
import register_capabilities as rc

s = rc.all_specs()
print("  ── 我们的工具里，跟「工程图」有关的 ──")
n = 0
for x in s:
    blob = (x.name + " " + x.doc + " " + x.module).lower()
    if "drawing" in blob or "工程图" in blob:
        n += 1
        print("    %-46s module=%-20s fn=%s" % (x.name, x.module, x.function))
print("    （共 %d 个）" % n)

print()
print("  ── server.py（上游那 45 个）里的工程图工具 ──")
t = Path(r"C:\swprojects\sw-skill-fork\mcp-server\server.py").read_text(encoding="utf-8")
hits = sorted(set(re.findall(r"(?m)^def ([a-z_]*drawing[a-z_]*)\(", t))
              | set(re.findall(r'name="([^"]*drawing[^"]*)"', t)))
for h in hits:
    print("    %s" % h)
print("    （共 %d 个）" % len(hits))

print()
print("  ── specs 目录里已有的工程图特性 ──")
for d in sorted(Path(r"D:\AI\SW\specs").iterdir()):
    if d.is_dir() and ("drawing" in d.name or "工程图" in d.name):
        print("    %s" % d.name)
