import re, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
# ① 全量登记 vs 官方反射全量：逐程序集核对「官方有、我们没有」的
print("=== 覆盖率硬核对：官方反射 vs 12 份索引 ===")
tot_off = tot_mine = 0
gaps = []
for rf in sorted(Path(r"D:\AI\SW\_raw").rglob("iface_*.txt")):
    asm = re.search(r"iface_(.+)\.txt$", rf.name).group(1)
    off = set()
    for l in rf.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*\S+\s+(\w+)\s*\(", l.strip())
        if m:
            off.add(re.sub(r"^(get|set)_", "", m.group(1)))
    # 内部分发口不算能力
    off = {n for n in off if not n.startswith("I") or n[1:2].isupper()}
    mine = set()
    for p in S.glob("sw_api_*.py"):
        c = p.read_text(encoding="utf-8")
        if asm.lower().replace("sldworks", "") in p.stem.lower() or (
                asm in ("sldworks",) and p.stem == "sw_api_sldworks"):
            mine |= set(re.findall(r"^        '(\w+)': \d+,", c, re.M))
    if not off:
        continue
    miss = off - mine
    tot_off += len(off); tot_mine += len(off & mine)
    pct = 100.0 * len(off & mine) / len(off)
    print("  %-16s 官方 %5d / 登记 %5d = %6.2f%%  缺 %d" % (asm, len(off), len(off & mine), pct, len(miss)))
    if miss:
        gaps.append((asm, sorted(miss)))
print()
print("  合计: 官方 %d / 登记 %d = %.3f%%" % (tot_off, tot_mine, 100.0*tot_mine/max(tot_off,1)))
for asm, m in gaps[:6]:
    print("    %-14s 缺 %d: %s" % (asm, len(m), ", ".join(m[:8])))