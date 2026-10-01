import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\specs\071-the-lagging-enumeration\tasks.md")
t = P.read_text(encoding="utf-8")
OLD = "`→ 验收:` `python _diag_sketch_visibility.py`（**滞后一格**）"
NEW = ("`→ 验收:` `python tools/probe_sketch_enumeration_lag.py`"
       "（三种数法对照，末行打印 **滞后一格观测到: True**）")
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
print("  ✓ tasks.md 已指向仓库内探针")
