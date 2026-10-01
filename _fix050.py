import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\specs\050-notice-and-audit-refresh\tasks.md")
t = P.read_text(encoding="utf-8")
OLD = "  `→ 验收:` `python _check_notice_claims.py`"
NEW = "  `→ 验收:` `Select-String THIRD-PARTY-NOTICES.md -Pattern 'source_verified'`"
if OLD in t:
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 已改成仓库内路径")
else:
    for l in t.splitlines():
        if "_check_notice_claims" in l:
            print("  待修: %r" % l)
