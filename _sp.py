import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sw = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
m = re.search(r"(?ms)^## ISketchPoint\r?\n(.*?)(?=\r?\n## |\Z)", sw)
for l in m.group(1).splitlines():
    if re.search(r"\bget_[XYZ]\b|\bset_[XYZ]\b|\b[X-Y-Z]\b", l): print("  反射:", l.strip())
idx = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
mm = re.search(r"'ISketchPoint': \(\n(.*?)\n    \),", idx, re.S)
print("  索引属性:", re.findall(r"'(\w+)'", mm.group(1))[:12] if mm else "无")
