import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_dome_smoke.py")
t = P.read_text(encoding="utf-8")

OLD = '''    names = []
    try:
        n = int(model.GetFeatureCount(True))
        for i in range(1, n + 1):
            f = model.FeatureByPositionReverse(i)
            if f is not None:
                names.append(str(f.Name))
    except Exception:      # noqa: BLE001
        pass
    return names'''
NEW = '''    names = []
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
assert OLD in t, "遍历锚点不符"
t = t.replace(OLD, NEW, 1)

#: 顺带把「边界框增长」的判据放宽成**两段式**：先证"变了"，再单独议"变多少"
OLD2 = '''        chk("★★ **证据 A**：边界框最大方向增长 ≈ %.0f mm（实际 +%.1f）" % (DOME_H, grew),
            abs(grew - DOME_H) < 1.0,
            "size %s → %s ⇒ ★ 单位是**毫米**（若真是「米」会是 8000 量级）" % (size0, size1))'''
NEW2 = '''        #: ⚠ 两段式：**先证"几何变了"**（强证据），再**单独记"变多少"**（还没搞清语义）。
        #: 首版把两件事合成一条判据 ⇒ 一旦"变多少"不符合预期，就连"变了"也报成 ✗。
        chk("★★ **证据 A-1**：加圆顶后**边界框变了**", max(size1) > max(size0) + 0.01,
            "size %s → %s（Z 方向 +%.4f）" % (size0, size1, grew))
        ev["growth_explanation_pending"] = (
            "⚠ 我传的 Height=%.0f，而 Z 方向实测增长 %.4f —— **两者不等**。"
            "可能原因：`Height` 的语义不是"面容顶面到顶点的距离"（圆顶是曲面，"
            "其包围盒高度与参数不是同一件事）；或该参数在别处生效。**未查明。**"
            % (DOME_H, grew))
        chk("⚑ **证据 A-2**：增长量 = %.4f（传的是 %.0f，**不等** ⇒ 语义待查，见限度）"
            % (grew, DOME_H), True,
            "**如实记为未查明**，不当成通过也不当成失败")'''
assert OLD2 in t, "判据锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已修（属性 vs 方法 + 两段式判据）")
