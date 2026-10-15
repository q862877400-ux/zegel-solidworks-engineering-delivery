import re, sys
sys.stdout.reconfigure(encoding="utf-8")
BANNED = {0x26A0:"警告", 0x2B50:"星标", 0x2705:"对勾", 0x274C:"叉号", 0x2757:"惊叹"}
targets = {
 "AGENTS.md（工作区，D4 管辖）": r"D:\AI\SW\AGENTS.md",
 "docs/ 下 6 份委托文档": None,
}
t = open(r"D:\AI\SW\AGENTS.md", encoding="utf-8").read()
hits = {}
for i, line in enumerate(t.splitlines(), 1):
    for ch in line:
        if ord(ch) in BANNED:
            hits.setdefault(BANNED[ord(ch)], []).append(i)
print("  AGENTS.md（工作区）:")
if hits:
    for k, v in hits.items(): print("     ⚠ %s × %d  行 %s" % (k, len(v), v[:6]))
else:
    print("     ✓ 0 处（D4 五类全无）")
print()
import pathlib
print("  docs/ 下 6 份（D4 是否管辖待定，先看事实）:")
for f in sorted(pathlib.Path(r"D:\AI\SW\docs").glob("*.md")):
    s = f.read_text(encoding="utf-8")
    n = sum(s.count(chr(cp)) for cp in BANNED)
    print("     %-34s %s" % (f.name, ("%d 处" % n) if n else "·"))
print()
print("  代码副本 docs/union-conventions.md（不是 AGENTS.md）:")
s = open(r"C:\swprojects\sw-skill-fork\docs\union-conventions.md", encoding="utf-8").read()
print("     %d 处" % sum(s.count(chr(cp)) for cp in BANNED))