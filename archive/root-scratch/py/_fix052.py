import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\specs\052-script-layer-units-unguardable\tasks.md")
t = P.read_text(encoding="utf-8")
OLD = "  `→ 验收:` `python _triage_unit_flags.py`（打印每个的形参/docstring）"
NEW = "  `→ 验收:` `Select-String docs\\script-layer-units.md -Pattern '4/4'`（逐条真相在那份文档里）"
if OLD in t:
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 已改成仓库内路径")
else:
    for l in t.splitlines():
        if "_triage_unit_flags" in l:
            print("  待修: %r" % l)
