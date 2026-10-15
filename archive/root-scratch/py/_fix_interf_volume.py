import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_interference_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''        named = [it for it in items if it.get("name")]
        chk("★ 逐项能拿到 `Name`（此前**静默降级**拿不到）", bool(named),
            "有名字的项 %d/%d：%s" % (len(named), len(items),
                                     [it.get("name") for it in items[:3]]))
        if not named and items:
            chk("⚠ 逐项的错误原文（**如实记**）", True, str(items[0])[:120])'''
NEW = '''        #: ★★★ **定量判据（最强的那个）**：两个 40×40×20 的块沿 X 偏 20mm
        #: ⇒ 重叠区 = **20 × 40 × 20 = 16000 mm³** ⇒ **算得出来、对得上**。
        vols = [it.get("volume") for it in items if isinstance(it.get("volume"), (int, float))]
        ev["volumes"] = vols
        chk("★★★ **定量**：干涉体积 ≈ **16000 mm³**（20×40×20，算得出来）",
            bool(vols) and abs(max(vols) - 16000.0) <= 2.0,
            "读回体积 = %s（期望 16000 ± 2）" % (vols,))
        cc = [it.get("component_count") for it in items]
        chk("★ 逐项能拿到 `GetComponentCount`（官方成员）", any(cc), "component_count = %s" % (cc,))
        if not vols and items:
            chk("⚠ 逐项的错误原文（**如实记**）", True, str(items[0])[:140])'''
assert OLD in t, "判据锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
import ast
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 判据已换成**体积定量**（16000 mm³）")
