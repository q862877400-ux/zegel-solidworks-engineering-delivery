import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

#: ① 选面用 `_empty_callout()`（事实 33）
P = R / "tools" / "verify_dome_smoke.py"
t = P.read_text(encoding="utf-8")
OLD = '''        ok_sel = False
        try:
            #: 顶面中心（板从 z=0 拉伸到 z=D）
            ok_sel = bool(doc.Extension.SelectByID2(
                "", "FACE", W / 2.0, H / 2.0, D, False, 0, None, 0))
        except Exception as exc:      # noqa: BLE001
            chk("选顶面", False, "EXC: %s" % str(exc)[:80])'''
NEW = '''        ok_sel = False
        try:
            #: ⚠⚠ **事实 33**：`SelectByID2` 的 `Callout` 参数**必须**传
            #: `VARIANT(VT_DISPATCH, None)`；传 `None` 得到 `类型不匹配`（`0x80028CA0`），
            #: 而该错误**看不出是 Callout 的问题**（本轮又踩一次）。
            callout = sw_part._empty_callout()
            ok_sel = bool(doc.Extension.SelectByID2(
                "", "FACE", W / 2.0, H / 2.0, D, False, 0, callout, 0))
        except Exception as exc:      # noqa: BLE001
            chk("选顶面", False, "EXC: %s" % str(exc)[:80])'''
assert OLD in t, "选面锚点不符"
t = t.replace(OLD, NEW, 1)

#: ② 特征名遍历：改用 `GetFeatureCount` + `FeatureByPositionReverse`
OLD2 = '''def feature_names(model) -> list:
    """特征树里的特征名（沿 `IFeature::GetNextFeature` 走一层）。"""
    names = []
    try:
        feat = model.FirstFeature()
        while feat is not None:
            names.append(str(feat.Name))
            feat = feat.GetNextFeature()
    except Exception:      # noqa: BLE001
        pass
    return names'''
NEW2 = '''def feature_names(model) -> list:
    """特征树里的特征名。

    ⚠ 第一版沿 `FirstFeature()` / `GetNextFeature()` 走 ⇒ **返回 0 个**。
    ⚠ 而**轮 121 已经在同一处栽过**：`FirstFeature` 拿到的是 `'收藏'` 那个**收藏夹**
    （事实 40 那一族的"失败信号长得像正常值"）。
    ⇒ 改用**计数 + 按位置取**（`GetFeatureCount` / `FeatureByPositionReverse`）——
    这两个不依赖树的"起点在哪"。
    """
    names = []
    try:
        n = int(model.GetFeatureCount(True))
        for i in range(1, n + 1):
            f = model.FeatureByPositionReverse(i)
            if f is not None:
                names.append(str(f.Name))
    except Exception:      # noqa: BLE001
        pass
    return names'''
assert OLD2 in t, "特征遍历锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 两处已修（Callout 用 VARIANT + 特征遍历改用计数/按位置）")
