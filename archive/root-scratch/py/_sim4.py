import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KEY = re.compile(r"force|pressure|gravity|restraint|fixture|load|bearing|simulation|study|cosmos", re.I)

print("  ── 四家的工具里，跟「仿真 / 载荷 / 约束」有关的有几个 ──")
for name, root in (("Eduardof0nt", r"C:\swprojects\Eduardof0nt"),
                   ("andrewbartels1", r"C:\swprojects\andrewbartels1"),
                   ("vespo92", r"C:\swprojects\SolidworksMCP-TS"),
                   ("Slacker-LLC", r"C:\swprojects\Slacker-LLC")):
    r = Path(root)
    if not r.is_dir():
        print("    %-16s （不在本机）" % name)
        continue
    hits = []
    for p in list(r.rglob("*.py")) + list(r.rglob("*.ts")):
        if ".git" in str(p) or "node_modules" in str(p) or "test" in p.name.lower():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?:@\w*\.tool|server\.tool)\s*\(([^)]*)\)", t, re.S):
            nm = re.findall(r'name="([^"]+)"|"([a-z_][a-z0-9_]*)"', m.group(1))
            flat = " ".join(x for tup in nm for x in tup if x)
            if KEY.search(flat):
                hits.append(flat)
    print("    %-16s 命中 **%d** 个  %s" % (name, len(hits), (", ".join(hits[:8]) if hits else "（无）")))

print("")
print("  ── 四家有没有「仿真」相关的模块文件 ──")
for name, root in (("Eduardof0nt", r"C:\swprojects\Eduardof0nt"),
                   ("andrewbartels1", r"C:\swprojects\andrewbartels1"),
                   ("vespo92", r"C:\swprojects\SolidworksMCP-TS"),
                   ("Slacker-LLC", r"C:\swprojects\Slacker-LLC")):
    r = Path(root)
    if not r.is_dir():
        continue
    f = [p for p in list(r.rglob("*.py")) + list(r.rglob("*.ts"))
         if ".git" not in str(p) and "node_modules" not in str(p)
         and re.search(r"simul|load|study|cosmos|cw", p.name, re.I)]
    print("    %-16s %d 个  %s" % (name, len(f), ", ".join(p.name for p in f[:4])))
