import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
text = open(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt", encoding="utf-8", errors="replace").read()
cur, blk = None, []
for raw in text.splitlines():
    if raw.startswith("## "):
        if cur == "IAssemblyDoc": break
        cur = raw[3:].strip()
        if cur == "IAssemblyDoc": blk = []
    elif cur == "IAssemblyDoc" and raw.strip():
        blk.append(raw.strip())
lines = 0; names = set()
for line in blk:
    m = re.match(r"^\S+\s+(get_|set_)(\w+)\s*\(", line)
    if m: lines += 1; names.add(m.group(2))
print("  get_/set_ 行数 =", lines, " 唯一名 =", len(names))
