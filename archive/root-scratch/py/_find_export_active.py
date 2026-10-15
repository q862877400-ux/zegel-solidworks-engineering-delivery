import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
#: 找 solidworks_export_active 背后的模块/函数
for p in sorted((ROOT / "mcp-server").glob("tool_specs_batch*.py")):
    t = p.read_text(encoding="utf-8")
    for m in re.finditer(r'(?s)name="solidworks_export_active".{0,600}?(?=\n    ToolSpec|\Z)', t):
        seg = m.group(0)
        mm = re.search(r'module="(\w+)"', seg)
        mf = re.search(r'function="(\w+)"', seg)
        print("  %s ⇒ module=%s function=%s" % (p.name, mm.group(1) if mm else "?",
                                                mf.group(1) if mf else "?"))
        for l in seg.splitlines():
            if "FORMAT" in l or "format" in l or "png" in l.lower() or "bmp" in l.lower():
                print("      %s" % l.strip()[:100])
#: 该函数的实现
t = (ROOT / "scripts" / "sw_delivery.py").read_text(encoding="utf-8")
for name in ("export_active", "def export_document", "EXPORT_FORMATS"):
    i = t.find(name)
    if i >= 0:
        print()
        print("  ── %s ──" % name)
        print(t[i:i + 700])
        break
