import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
mm = re.search(r"(?ms)^## IAssemblyDoc\s*\r?\n(.*?)(?=\r?\n## |\Z)", txt)
print("  IAssemblyDoc 上「取组件」的成员:")
for l in mm.group(1).splitlines():
    s = l.strip()
    m2 = re.match(r"^\S+\s+(\w*(?:Components|ComponentCount)\w*)\(", s)
    if m2:
        ps = s[s.index("(")+1:s.rindex(")")]
        args = [a.strip() for a in ps.split(",") if a.strip()]
        print("    %-26s %2d 参" % (m2.group(1), len(args)))