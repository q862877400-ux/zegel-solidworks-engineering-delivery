import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
mm = re.search(r"(?ms)^## ISldWorks\s*\r?\n(.*?)(?=\r?\n## |\Z)", txt)
for l in mm.group(1).splitlines():
    s = l.strip()
    if re.match(r"^\S+\s+NewDocument\w*\(", s) or re.match(r"^\S+\s+ExitApp\(", s):
        nm = re.match(r"^\S+\s+(\w+)\(", s).group(1)
        ps = s[s.index("(")+1:s.rindex(")")]
        args = [a.strip() for a in ps.split(",") if a.strip()]
        print("  %-12s %2d 参: %s" % (nm, len(args), ", ".join(args)))
print()
print("  我索引里登记的值:")
import importlib.util
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_connect
sp = importlib.util.spec_from_file_location("swapi", r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp); sys.modules["swapi"]=sw
sp.loader.exec_module(sw); sw.get_com_member = sw_connect.get_com_member
for k in ("NewDocument","ExitApp","GetDocuments","ActivateDoc3"):
    print("    %-16s %s" % (k, sw.ARITY["ISldWorks"].get(k)))