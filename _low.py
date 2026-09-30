import sys, io, re, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW\tools")
text = open(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt", encoding="utf-8", errors="replace").read()
blocks, cur = {}, None
for raw in text.splitlines():
    if raw.startswith("## "): cur = raw[3:].strip(); blocks[cur] = []
    elif cur and raw.strip(): blocks[cur].append(raw.strip())
SIG = re.compile(r"^(\S+)\s+(\w+)\s*\((.*)\)$")
# 当前覆盖表里低于 50% 的族
import subprocess
doc = Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.md").read_text(encoding="utf-8")
low = []
for m in re.finditer(r"^\| [^|]+ \| `(\w+)` \| (\d+) \| [^|]*\| (\d+)% \|", doc, re.M):
    if int(m.group(3)) < 50: low.append((m.group(1), int(m.group(2)), int(m.group(3))))
low.sort(key=lambda x: (x[2], -x[1]))
print("  低于 50%% 的族共 %d 个。前 14 个的构成：" % len(low))
print("    %-32s %5s %6s %6s %6s %8s" % ("族","原始","I前缀","属性","方法","归约能力"))
for name, members, pct in low[:14]:
    blk = blocks.get(name, [])
    i=p=meth=0; bases=set()
    for line in blk:
        hit = SIG.match(line)
        if not hit: continue
        _, n, _a = hit.groups()
        if re.match(r"^I[A-Z]", n): i+=1
        elif n.startswith(("get_","set_")): p+=1
        else: meth+=1; bases.add(re.sub(r"\d+$","",n))
    print("    %-32s %5d %6d %6d %6d %8d" % (name, len(blk), i, p, meth, len(bases)))
