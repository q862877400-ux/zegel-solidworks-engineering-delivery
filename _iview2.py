import sys, io, re
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
methods = []
for s in blk:
    m = re.match(r"^(\S+)\s+(\w+)\s*\((.*)\)$", s)
    if not m: continue
    ret, name, args = m.groups()
    if re.match(r"^I[A-Z]", name): continue
    methods.append((ret, name, args))
base = [x for x in methods if not re.search(r"\d", x[1])]
numbered = [x for x in methods if re.search(r"\d", x[1])]
# 编号变体归约到基础名
def baseof(n): return re.sub(r"\d+$", "", n)
bases = sorted({baseof(x[1]) for x in methods})
print("  去掉 I 前缀后 = %d 条签名" % len(methods))
print("  其中无编号的 = %d，带编号的 = %d" % (len(base), len(numbered)))
print("  归约到基础名后 = %d 个**不同能力**" % len(bases))
print("\n  这些能力的前 40 个:")
for b in bases[:40]: print("    " + b)
