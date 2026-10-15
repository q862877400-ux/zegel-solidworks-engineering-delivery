import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = Path(r"C:\swapi\types\ISketchEllipse")
api = {p.stem for p in d.glob("*.md") if p.stem != "_overview"}
src = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
m = re.search(r"'ISketchEllipse': \{\n(.*?)\n    \},", src, re.S)
refl = set(re.findall(r"'(\w+)':", m.group(1))) if m else set()
m2 = re.search(r"'ISketchEllipse': \(\n(.*?)\n    \),", src, re.S)
props = set(re.findall(r"'(\w+)'", m2.group(1))) if m2 else set()
print("C:\\swapi  %d 个" % len(api))
print("反射 方法 %d 个" % len(refl))
print("反射 属性 %d 个" % len(props))
print()
print("swapi 有、反射没有的 (%d):" % len(api - refl - props))
print("  " + ", ".join(sorted(api - refl - props)))
