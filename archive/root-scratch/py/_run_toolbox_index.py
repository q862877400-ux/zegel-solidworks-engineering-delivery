import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
import sw_toolbox_index as tb

#: ① 索引能不能读（**这是 `verified` 要求的"我们自己的运行证据"**）
idx = tb.load_index()
print("  load_index() 类型 = %s" % type(idx).__name__)
if isinstance(idx, dict):
    print("  顶层键: %s" % list(idx.keys())[:8])

#: ② 标准数
stds = tb.list_standards()
print("  list_standards() ⇒ **%d** 套标准" % (len(stds) if hasattr(stds, "__len__") else -1))
print("    前 8 套: %s" % (list(stds)[:8] if hasattr(stds, "__iter__") else stds))

#: ③ 零件总数（从索引里数，**不猜**）
total = None
if isinstance(idx, dict):
    for k in ("parts", "items", "entries"):
        v = idx.get(k)
        if isinstance(v, list):
            total = len(v)
            break
    if total is None:
        #: 也许是 {标准: [零件…]} 的形状
        try:
            total = sum(len(v) for v in idx.values() if isinstance(v, list))
            print("  （按 标准→零件列表 的形状求和）")
        except Exception:      # noqa: BLE001
            total = None
print("  **零件总数 = %s**" % total)

#: ④ search 能不能用（端到端一小步）
try:
    got = tb.search("bearing")
    n = len(got) if hasattr(got, "__len__") else -1
    print("  search('bearing') ⇒ %d 条" % n)
except Exception as exc:      # noqa: BLE001
    print("  search('bearing') 抛错: %s" % str(exc)[:70])
