import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_helix.py")
t = P.read_text(encoding="utf-8")

OLD_START = "def _newest_feature_name(model):"
i = t.index(OLD_START)
j = t.index("\n\n\n# ── 来源", i)
OLD = t[i:j]

NEW = '''def _newest_feature_name(model):
    """取**刚加进去的那个特征**的名字。

    ⚠⚠ **轮 121 真机实测：本函数原来写错了。**
    原实现读 `model.FirstFeature` 并取它的 `Name` ——
    但 `FirstFeature` 是**特征树的第一个**，**不是最新加的那个**。
    实测（新零件画圆后建螺旋线）它返回 **`'收藏'`**（树里的收藏夹），
    而真正新建的是 **`'螺旋线/涡状线1'`**。
    ★ 这个错**不抛异常、返回一个看起来合理的字符串** ⇒ 静态测试抓不到。

    ⇒ 改用官方 **`IModelDocExtension.GetLastFeatureAdded()`**
    （官方原文：「Gets the **last feature added** to the model」）。

    ⚠ 官方 Remarks 提醒：该方法**可能返回子特征**（如配合、工程图视图等）。
    """
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("IModelDoc2.Extension 为 None ⇒ 取不到最后加的特征")
    feat = get_com_member(ext, "GetLastFeatureAdded")
    if feat is None:
        raise RuntimeError(
            "IModelDocExtension.GetLastFeatureAdded() 返回 None ⇒ 螺旋线**没有建出来**。"
            "最常见原因：**没有选中定义直径的圆**（官方示例先 SelectByID2 选圆再调）。"
        )
    name = get_com_member(feat, "Name")
    if not name:
        raise RuntimeError("最后加的特征没有 Name ⇒ 无法确认螺旋线是否建成")
    return name'''

t = t[:i] + NEW + t[j:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok _newest_feature_name 已改用 GetLastFeatureAdded")
print("  台词核对: %s" % ("GetLastFeatureAdded" in t))
