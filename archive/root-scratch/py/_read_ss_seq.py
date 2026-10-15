import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
Q = chr(34)
root = Path(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp")
f = list(root.rglob("Access_Structure_System_Corner_Treatments_Example_VB.htm"))[0]
t = f.read_text(encoding="utf-8", errors="replace")
t2 = (t.replace("\\u003c", "<").replace("\\u003e", ">")
       .replace("\\" + Q, Q).replace("\\u0026nbsp;", " ").replace("\\u0026amp;", "&"))
t2 = re.sub(r"(?i)<br\s*/?>", "\n", t2)
t2 = re.sub(r"(?i)</p>", "\n", t2)
t2 = re.sub(r"<[^>]+>", "", t2)
lines = [l.rstrip() for l in t2.splitlines() if l.strip()]
print("  全文 %d 行（★ 先报数量）" % len(lines))
#: ★ 找 CreateStructureSystemMemberData / CreateStructureSystem 那几行，各印前后 12 行
for key in ("CreateStructureSystemMemberData", "CreateStructureSystem(", "InsertStructuralWeldment"):
    for i, l in enumerate(lines):
        if key in l:
            print("\n  ===== %s @L%d =====" % (key, i))
            for k in range(max(0, i - 13), min(len(lines), i + 9)):
                mark = ">>" if k == i else "  "
                print("   %s %s" % (mark, lines[k].strip()[:122]))
            break
