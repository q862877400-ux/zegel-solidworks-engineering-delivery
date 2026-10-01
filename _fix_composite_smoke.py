import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_composite_curve_smoke.py")
t = P.read_text(encoding="utf-8")

#: ★★★ 修掉那个**硬编码 True** 的检查 —— 它让整个冒烟建在未验证的前提上
OLD = '''        chk("造出 2 个草图（各含一条线）", True, "草图1 / 草图2")'''
NEW = '''        #: ⚠⚠⚠ **第一版这里硬编码了 `True`** ⇒ 它**不可能失败** ⇒
        #: 整个冒烟建在一个**从未被验证的前提**上（而那个前提**实际不成立**：
        #: 真机上两次 `start_sketch`+`end_sketch` **只留下 1 个草图**）。
        #: ★ 这是本会话一直在记的那个反模式的**我自己犯的一次**：
        #: **一个不会失败的检查，等于没有检查。**
        #: ⇒ 现在**真的数**特征树里 SKETCH 型的条目。
        n_sketch = 0
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
        ev["sketch_count"] = n_sketch
        chk("★★ **真的数**：特征树里有 **2** 个草图", n_sketch == 2,
            "实际 %d 个（⚠ 第一版这里硬编码 True ⇒ 不可能失败）" % n_sketch)'''
assert OLD in t, "硬编码锚点不符"
t = t.replace(OLD, NEW, 1)

#: `insert_composite_curve` 那条改成"如实记"，而不是当成功能缺陷
OLD2 = '''        try:
            sw_part.insert_composite_curve(doc)
            chk("insert_composite_curve 返回 True", True, "ok")
        except Exception as exc:      # noqa: BLE001
            chk("insert_composite_curve", False, "%s: %s" % (type(exc).__name__, str(exc)[:120]))'''
NEW2 = '''        #: ⚑ 前提（2 个草图 + mark=1 选中）**未被满足**时，官方返回 `False` 是**应然的**
        #: ⇒ 这一条**不记成功能缺陷**，而是**如实记下"前提没成立"**。
        try:
            sw_part.insert_composite_curve(doc)
            chk("insert_composite_curve 返回 True", n_sketch == 2,
                "ok" if n_sketch == 2 else "⚠ **前提没成立**（只有 %d 个草图）" % n_sketch)
        except Exception as exc:      # noqa: BLE001
            chk("insert_composite_curve", n_sketch != 2,
                "返回 False —— ⚑ **前提未满足，属应然**（草图数 = %d）；"
                "⚠ **这条后端上"能不能建成"仍未查明**" % n_sketch)'''
assert OLD2 in t, "调用锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已修（硬编码 → 真的数；失败改成如实记）")
