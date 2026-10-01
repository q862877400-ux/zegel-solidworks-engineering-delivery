import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_gtol_smoke.py")
t = P.read_text(encoding="utf-8")
n = 0
#: ⚠ 官方 `IGtolFrame.AddIndicator` 的 TolType **只能是** ang(20)/parallel(22)/perp(21)/
#: circrunout(25)/symmetry(13) ⇒ 改用**清单内**的
for old, new in (
    ('sw_gtol.GTOL_GEOM_SYMBOL["position"]', 'sw_gtol.GTOL_GEOM_SYMBOL["parallelism"]'),
    ('sw_gtol.GTOL_GEOM_SYMBOL["flatness"]', 'sw_gtol.GTOL_GEOM_SYMBOL["perpendicularity"]'),
    ('add_gtol_indicator(position, 基准 A)', 'add_gtol_indicator(parallelism, 基准 A)'),
    ('再加一个（flatness，无基准）', '再加一个（perpendicularity，无基准）'),
):
    if old in t:
        t = t.replace(old, new)
        n += 1
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  改了 %d 处" % n)
for i, l in enumerate(t.splitlines(), 1):
    if "tol_type=" in l or "chk(\"★ add_gtol" in l or "chk(\"  再加" in l:
        print("    L%-4d %s" % (i, l.strip()[:98]))
