import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\output\gtol-frame-xml-schema.txt")
t = p.read_text(encoding="utf-8")
print("  行数 %d · 字节 %d" % (t.count("\n"), len(t)))
print()
print("  ── 头 20 行 ──")
for l in t.splitlines()[:20]:
    print("    %s" % l.strip()[:100])
print()
names = re.findall(r'<xs:element\s+name="([^"]+)"', t)
print("  ── xs:element 声明（%d 个，前 14）──" % len(names))
for n in names[:14]:
    print("    %s" % n)
print()
#: 找"根"：出现在 schema 顶层、且其它元素**引用它**的那个
refs = re.findall(r'<xs:element\s+ref="([^"]+)"', t)
from collections import Counter
print("  ── 被引用最多的元素（= 结构的入口候选）──")
for n, c in Counter(refs).most_common(6):
    print("    %-28s 被引用 %d 次" % (n, c))
print()
#: 看第一个 complexType 的内容（结构的样子）
m = re.search(r"(?s)<xs:complexType\s+name=\"([^\"]+)\">(.{0,900})", t)
if m:
    print("  ── 第一个 complexType: %s ──" % m.group(1))
    for l in m.group(2).splitlines()[:14]:
        print("      %s" % l.strip()[:100])
