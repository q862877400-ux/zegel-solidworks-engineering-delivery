import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
mm = re.search(r"(?ms)^## IAssemblyDoc\s*\r?\n(.*?)(?=\r?\n## |\Z)", txt)
print("  IAssemblyDoc 上 AddComponent* 的真实签名:")
for l in mm.group(1).splitlines():
    s = l.strip()
    if re.match(r"^\S+\s+AddComponent\d?\(", s):
        name = re.match(r"^\S+\s+(\w+)\(", s).group(1)
        ps = s[s.index("(")+1:s.rindex(")")]
        args = [a.strip() for a in ps.split(",") if a.strip()]
        print("    %-14s %2d 参: %s" % (name, len(args), ", ".join(args)))
print()
# 顺便看 IAssemblyDoc 上有没有 NewDocument / InsertFile
print("  建文档/插文件相关:")
for l in mm.group(1).splitlines():
    s = l.strip()
    m2 = re.match(r"^\S+\s+(\w*(?:NewDocument|NewMultiDoc|InsertFile|InsertVirtualFile|InsertComponentFile)\w*)\(", s)
    if m2:
        ps = s[s.index("(")+1:s.rindex(")")]
        args = [a.strip() for a in ps.split(",") if a.strip()]
        print("    %-22s %2d 参: %s" % (m2.group(1), len(args), ", ".join(args)))