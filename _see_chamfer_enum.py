import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
from scripts import sw_sketch_edit as se
print("  仓库的 SKETCH_CHAMFER_TYPE = %s" % getattr(se, "SKETCH_CHAMFER_TYPE", "（没有）"))
print()
print("  ── 反射里 swSketchChamferType_e 的取值 ──")
for f in Path(r"D:\AI\SW\_raw").rglob("enum_values_sldworks.txt"):
    t = f.read_text(encoding="utf-8", errors="replace")
    import re
    seg = re.search(r"(?s)swSketchChamferType_e(.{0,600})", t)
    if seg:
        for l in seg.group(1).splitlines()[:14]:
            print("    %s" % l.strip()[:80])
    break
print()
print("  ── swapi 的枚举页 ──")
f2 = Path(r"C:\swapi\enums\swSketchChamferType_e.md")
if f2.is_file():
    for l in f2.read_text(encoding="utf-8").splitlines()[:22]:
        if l.strip():
            print("    %s" % l.strip()[:90])
