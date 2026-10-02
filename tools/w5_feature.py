import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])

sys.path.insert(0, r"" + _ROOT_S + r"\scripts")
import sw_part as p


for n in ("extrude_boss", "extrude_cut", "extrude_midplane", "chamfer", "fillet"):
    fn = getattr(p, n, None)
    if fn is None:
        print("  %-20s （不存在）" % n)
        continue
    print("  ══ %s%s ══" % (n, inspect.signature(fn)))
    for l in (inspect.getdoc(fn) or "").splitlines()[:12]:
        print("      %s" % l[:104])
    print()
