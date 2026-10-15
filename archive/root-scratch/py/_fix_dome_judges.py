import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_dome_smoke.py")
t = P.read_text(encoding="utf-8")

#: ① A-1 改成**逐分量**比较（首版用 max() —— 而变的是**最小的那个方向**）
OLD = '''        chk("★★ **证据 A-1**：加圆顶后**边界框变了**", max(size1) > max(size0) + 0.01,
            "size %s → %s（Z 方向 +%.4f）" % (size0, size1, grew))'''
NEW = '''        #: ⚠ 首版用 `max(size1) > max(size0)` —— **错**：变的那个方向（20→34.2）
        #: 在 `max` 里排不上号（最大是 X 的 100，没变）⇒ 判据报 ✗ 而几何明明变了。
        #: ⇒ 改成**逐分量**比较（排好序逐个对）。
        changed = [round(b - a, 4) for a, b in zip(size0, size1) if abs(b - a) > 0.01]
        chk("★★ **证据 A-1**：加圆顶后**边界框逐分量变了**", bool(changed),
            "size %s → %s ⇒ 变化的分量 %s" % (size0, size1, changed))'''
assert OLD in t, "A-1 锚点不符"
t = t.replace(OLD, NEW, 1)

#: `grew` 改成"变化最大的那个分量"
OLD2 = '''        grew = round(max(size1) - max(size0), 4)'''
NEW2 = '''        #: 变化最大的那个分量（首版取 max()-max() ⇒ 抓不到"最小方向在长"）
        grew = round(max(abs(b - a) for a, b in zip(size0, size1)), 4)'''
assert OLD2 in t, "grew 锚点不符"
t = t.replace(OLD2, NEW2, 1)

#: ② 特征树"新增"要取**最前面**（`FeatureByPositionReverse` 从新到旧）
OLD3 = '''    names = []
    try:
        #: ⚠⚠ 第二版仍错：`GetFeatureCount` 是**属性**（`int`），**不是方法** ——
        #: 调它会得到 `'int' object is not callable`（轮 143 实测）。
        n = int(model.GetFeatureCount)
        for i in range(1, n + 1):
            f = model.FeatureByPositionReverse(i)
            if f is not None:
                names.append(str(f.Name))
    except Exception:      # noqa: BLE001
        pass
    return names'''
NEW3 = '''    names = []
    try:
        #: ⚠⚠ 第二版仍错：`GetFeatureCount` 是**属性**（`int`），**不是方法** ——
        #: 调它会得到 `'int' object is not callable`（轮 143 实测）。
        #: ⚠ 第三版把"新增"取成 `names[n_before:]` —— **也错**：
        #: `FeatureByPositionReverse(1)` 是**最新的**（树里从新到旧）
        #: ⇒ 新增的在**列表最前面**，不在末尾。
        n = int(model.GetFeatureCount)
        for i in range(1, n + 1):
            f = model.FeatureByPositionReverse(i)
            if f is not None:
                names.append(str(f.Name))
    except Exception:      # noqa: BLE001
        pass
    return names'''
assert OLD3 in t, "遍历锚点不符"
t = t.replace(OLD3, NEW3, 1)

OLD4 = '''        names = feature_names(doc)
        new_feats = names[n_before:] if len(names) >= n_before else names'''
NEW4 = '''        names = feature_names(doc)
        #: ★ `FeatureByPositionReverse` 从**新到旧** ⇒ 新增的在**最前面**。
        new_feats = names[:max(0, len(names) - n_before)]'''
assert OLD4 in t, "新增锚点不符"
t = t.replace(OLD4, NEW4, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 三处判据已修（逐分量 + grew + 新增取最前）")
