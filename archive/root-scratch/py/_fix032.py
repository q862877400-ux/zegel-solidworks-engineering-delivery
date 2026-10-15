import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\specs\032-obsolete-ledger-complete\tasks.md")
t = P.read_text(encoding="utf-8")
bad = "  `→ 验收:` `python _triage20.py`（工作区脚本）"
good = "  `→ 验收:` `Select-String docs\\obsolete-member-candidates.md -Pattern '已逐条核完'`"
if bad in t:
    P.write_text(t.replace(bad, good, 1), encoding="utf-8")
    print("  ok 已改成仓库内路径")
else:
    for l in t.splitlines():
        if "triage20" in l:
            print("  待修: %r" % l)
