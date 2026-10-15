import sys, io, re
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
text = open(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt", encoding="utf-8", errors="replace").read()
cur, blk = None, []
for raw in text.splitlines():
    if raw.startswith("## "):
        if cur == "IView": break
        cur = raw[3:].strip()
        if cur == "IView": blk = []
    elif cur == "IView" and raw.strip():
        blk.append(raw.strip())
print("  IView 成员总数 =", len(blk))
def kind(sig):
    m = re.match(r"^(\S+)\s+(\w+)\s*\(", sig)
    return (m.group(1), m.group(2)) if m else (None, None)
rets = Counter(); prefixes = Counter(); idis = 0; props = 0; ndigits = Counter()
for s in blk:
    ret, name = kind(s)
    if name is None: continue
    rets[ret] += 1
    if re.match(r"^I[A-Z]", name): idis += 1
    if name.startswith(("get_","set_")): props += 1
    for d in re.findall(r"\d", name): ndigits[d] += 1
print("  I 前缀内部分发口 =", idis)
print("  属性（get_/set_） =", props)
print("  真正的方法 =", len(blk) - idis - props)
print("\n  返回类型 top 8:", rets.most_common(8))
print("\n  名字里带数字的（历史重载痕迹）:", sum(v for k,v in ndigits.items() if k!='0'), "个")
