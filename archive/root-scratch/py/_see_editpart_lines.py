import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
p = R / "scripts" / "sw_assembly_doc.py"
t = p.read_text(encoding="utf-8").splitlines()
print("── sw_assembly_doc.py 里那几处 EditPart2 / EditAssembly 的**真实形态** ──")
for i, l in enumerate(t, 1):
    if any(k in l for k in ("EditPart2", "EditAssembly", "InsertNewPart2", "InsertNewVirtualPart")):
        print("  L%-4d %s" % (i, l[:104]))
print()
print("── 它们是不是在**注释/来源块**里（看上下文）──")
for i in (117, 122, 166):
    print("  --- 附近 ---")
    for k in range(max(0, i - 1), min(len(t), i + 5)):
        print("    L%-4d %s" % (k + 1, t[k][:98]))
    print()
