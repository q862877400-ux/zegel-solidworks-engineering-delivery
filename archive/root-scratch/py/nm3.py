import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
mm = re.search(r"(?ms)^## ISldWorks\s*\r?\n(.*?)(?=\r?\n## |\Z)", txt)
print("  ISldWorks 上 AddIn/Command 相关成员:")
for l in mm.group(1).splitlines():
    s = l.strip()
    m = re.match(r"^\S+\s+(\w*(?:AddIn|Addin|Command)\w*)\(", s)
    if m:
        ps = s[s.index("(")+1:s.rindex(")")]
        args = [a.strip() for a in ps.split(",") if a.strip()]
        print("    %-28s %2d 参" % (m.group(1), len(args)))