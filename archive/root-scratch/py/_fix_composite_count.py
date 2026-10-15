import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 修掉上轮那条**用错方法**的判据（位置枚举会滞后一格）
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_composite_curve_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''        n_sketch = 0
        try:
            n_all = int(doc.GetFeatureCount)
            for k in range(1, n_all + 1):
                f = doc.FeatureByPositionReverse(k)
                if f is None:
                    continue
                if str(f.Name).startswith("草图") or str(f.Name).startswith("Sketch"):
                    n_sketch += 1
        except Exception as exc:      # noqa: BLE001
            chk("数特征树里的草图", False, "%s: %s" % (type(exc).__name__, str(exc)[:80]))
        ev["sketch_count"] = n_sketch'''
NEW = '''        #: ⚠⚠⚠ **两种数法都要用**（轮 152 查出位置枚举**滞后一格**）：
        #: `FeatureByPositionReverse` 枚举的是**已提交**的特征，
        #: 而「**最后建的那个草图**」要等下一个特征建了才出现
        #: ⇒ 单用它数"刚建了几个"会**少数一个**（★ 轮 151 我就是这么得出错误根因的）。
        by_pos = []
        try:
            n_all = int(doc.GetFeatureCount)
            for k in range(1, n_all + 1):
                f = doc.FeatureByPositionReverse(k)
                if f is not None and str(f.Name).startswith(("草图", "Sketch")):
                    by_pos.append(str(f.Name))
        except Exception as exc:      # noqa: BLE001
            chk("位置枚举草图", False, "%s: %s" % (type(exc).__name__, str(exc)[:80]))
        by_name = []
        for nm in ("草图1", "草图2", "草图3"):
            try:
                if doc.FeatureByName(nm) is not None:
                    by_name.append(nm)
            except Exception:      # noqa: BLE001
                pass
        #: ★ **按名查**才是可靠的那个（不依赖"提交"状态）
        n_sketch = len(by_name)
        ev["sketch_by_position"] = by_pos
        ev["sketch_by_name"] = by_name
        ev["sketch_count"] = n_sketch
        print("     ⚠ 位置枚举=%s（**滞后一格**）· 按名查=%s" % (by_pos, by_name))'''
assert OLD in t, "判据锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ✓ 冒烟的判据已改用**按名查**（并打印位置枚举做对照）")
