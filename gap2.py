import re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
root = Path(r"C:\swprojects\sw-skill-fork")
def stems(filt):
    r = subprocess.run(["git","-C",str(root),"diff","origin/main","--name-status","--diff-filter=A"],
                       capture_output=True, text=True, encoding="utf-8").stdout
    out=[]
    for l in r.splitlines():
        p = l.split("\t")[-1]
        if p.startswith("scripts/") and p.endswith(".py"):
            out.append((Path(p).stem, Path(p)))
    return out
mods = stems(None)
skill = (root/"SKILL.md").read_text(encoding="utf-8")
caps  = (root/"capabilities.yaml").read_text(encoding="utf-8")
syspy = (root/"mcp-server"/"server.py").read_text(encoding="utf-8")
missing_doc = [s for s,_ in mods if s not in skill]
print("★ SKILL.md 未提及的 %d 个:" % len(missing_doc))
for s in missing_doc: print("     %s" % s)
print()
print("★ capabilities.yaml 里登记了吗（抽样 6 个）:")
for s,_ in mods[:6]:
    print("     %-28s %s" % (s, "有" if s in caps else "✗ 没有"))