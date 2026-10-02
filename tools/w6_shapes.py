import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])

sys.path.insert(0, r"" + _ROOT_S + r"\scripts")
import sw_assembly as a


for n in ("get_components", "collect_mate_feature_summary", "get_interference_detection"):
    fn = getattr(a, n, None)
    if fn is None:
        print("  %-30s （不存在）" % n)
        continue
    print("  ══ %s%s ══" % (n, inspect.signature(fn)))
    src = inspect.getsource(fn).splitlines()
    print("     ── 实现（前 22 行）──")
    for l in src[:22]:
        print("     %s" % l[:104])
    print()
