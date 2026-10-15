import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW\tools")
REPO_MARK = "sw-skill-fork"

#: ★ 决定性判据：写出**目标表达式**，看它是不是拼到仓库根下。
#:   形态一：OUT = REPO / "docs" / "x.md"     （变量拼路径）
#:   形态二：Path(r"C:\\swprojects\\sw-skill-fork\\docs\\x")
#:   形态三：REPO = Path(r"C:\\swprojects\\sw-skill-fork") 用于写
VARROOT = re.compile(r"^\s*([A-Z_]\w*)\s*=\s*(?:Path\()?\s*r?[\"']([^\"']*sw-skill-fork[^\"']*)[\"']", re.M)
WRITECALL = re.compile(r"([A-Za-z_][\w\.\[\]\"'()/ ]{0,80}?)\.(write_text|write_bytes|save)\s*\(")
OPENW = re.compile(r"open\(\s*([^,]{0,120}?),\s*[\"'][wa]")

print("  逐个看：它的**写盘目标**在哪")
movers, stayers = [], []
for p in sorted(WS.glob("*.py")):
    t = p.read_text(encoding="utf-8", errors="replace")
    roots = {m.group(1): m.group(2) for m in VARROOT.finditer(t)}
    #: 若某变量被绑到仓库路径，再看它是否出现在写调用里
    hit = []
    for var, path in roots.items():
        if re.search(r"\b%s\b\s*/" % re.escape(var), t) and re.search(r"\b%s\b" % re.escape(var),
                                                                     t.split("def ")[-1] or t):
            hit.append("%s = %s" % (var, path[:52]))
    for m in WRITECALL.finditer(t):
        if REPO_MARK in m.group(1):
            hit.append("write → %s" % m.group(1).strip()[:60])
    for m in OPENW.finditer(t):
        if REPO_MARK in m.group(1):
            hit.append("open(w) → %s" % m.group(1).strip()[:60])
    (movers if hit else stayers).append((p.name, hit))

print("")
print("  ── ★ 写盘目标**在代码仓库下** ⇒ 该搬 ──")
for n, hit in movers:
    print("    %-34s %s" % (n, hit[0] if hit else ""))
print("  （共 %d 个）" % len(movers))
print("")
print("  ── 写盘目标在工作区（或纯读）⇒ 不搬 ──")
for n, _ in stayers:
    print("    %s" % n)
print("  （共 %d 个）" % len(stayers))
