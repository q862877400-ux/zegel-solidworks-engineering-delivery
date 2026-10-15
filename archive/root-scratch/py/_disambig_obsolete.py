import re
import sys
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
TYPES = Path(r"C:\swapi\types")
CALL = re.compile(r'get_com_member\(\s*[^,]+,\s*"([A-Za-z_]\w*)"')

called = defaultdict(list)
for p in sorted((ROOT / "scripts").glob("sw_*.py")):
    for m in CALL.finditer(p.read_text(encoding="utf-8", errors="replace")):
        called[m.group(1)].append(p.name)
called_names = set(called)

idx = defaultdict(list)
for p in TYPES.rglob("*.md"):
    idx[p.stem].append(p)

rows = []
for name in sorted(called):
    docs = idx.get(name)
    if not docs:
        continue
    for d in docs:
        head = d.read_text(encoding="utf-8", errors="replace")[:1200]
        if "Obsolete" not in head:
            continue
        m = re.search(r"Obsolete\.\s*(?:Superseded by\s*(.+?)\.)?", head)
        sup = m.group(1) if m and m.group(1) else ""
        # 从后继文本里抽成员名（`[[IFoo::Bar]]` 或裸 `Bar2`）
        succ = re.findall(r"\[\[[^\]:]+::(\w+)\]\]", sup) or re.findall(r"\b(\w+)\b", sup)
        rows.append((name, d.parent.name, sup, succ, sorted(set(called[name]))))
        break

print("=== 逐条消歧：我们**是否也调了后继** ===")
real, likely_fp, unknown = [], [], []
for name, iface, sup, succ, files in rows:
    hits = [s for s in succ if s in called_names and s != name]
    if hits:
        likely_fp.append((name, iface, hits, files))
    elif succ:
        real.append((name, iface, sup, files))
    else:
        unknown.append((name, iface, files))

print()
print("★ **我们同时也调了后继** ⇒ 多半是**同名不同接口的假阳性**（%d 条）：" % len(likely_fp))
for name, iface, hits, files in likely_fp:
    print("   %-24s（文档在 %s）我们也调了 %s" % (name, iface, ", ".join(hits)))

print()
print("⚠ **有后继但我们没调** ⇒ **待人工判**（%d 条）：" % len(real))
for name, iface, sup, files in real:
    print("   %-24s 文档在 %-34s 用在哪: %s" % (name, iface, ", ".join(files[:2])))
    print("        后继: %s" % (sup[:70] if sup else "（未写）"))

print()
print("⚠ 文档**没写后继**（%d 条）：" % len(unknown))
for name, iface, files in unknown:
    print("   %-24s 文档在 %s" % (name, iface))
