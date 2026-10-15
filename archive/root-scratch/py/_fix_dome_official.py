import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_dome_smoke.py")
t = P.read_text(encoding="utf-8")

#: ① 选面用 **mark=1**（官方 Remarks + 官方 C# 示例）
OLD = '''            callout = sw_part._empty_callout()
            ok_sel = bool(doc.Extension.SelectByID2(
                "", "FACE", W / 2.0, H / 2.0, D, False, 0, callout, 0))'''
NEW = '''            callout = sw_part._empty_callout()
            #: ★★ 官方 `IModelDoc2.InsertDome` 的 Remarks 原文：
            #:   「Before using this method, you must select the face for the dome
            #:     using a **selection mark of 1**.」
            #: 官方 C# 示例也是先 mark=0 选一次、清选、再 **mark=1** 选一次。
            #: ⚠ 传 mark=0 时 `InsertDome` 报 **`0x8002000F` 非选择性的参数** ——
            #: 那个错误**看不出是 mark 的问题**（与事实 33 同一类坑）。
            doc.Extension.SelectByID2("", "FACE", W / 2.0, H / 2.0, D, True, 0, callout, 0)
            doc.ClearSelection2(True)
            ok_sel = bool(doc.Extension.SelectByID2(
                "", "FACE", W / 2.0, H / 2.0, D, False, 1, callout, 0))'''
assert OLD in t, "选面锚点不符"
t = t.replace(OLD, NEW, 1)
t = t.replace('chk("★ 按面上的点选中顶面（事实 32 的可行路径）", ok_sel, "SelectByID2 返回 %s" % ok_sel)',
              'chk("★★ 按面上的点 + **mark=1** 选中顶面（官方 Remarks 要求）", ok_sel,\n'
              '            "SelectByID2 返回 %s" % ok_sel)', 1)

#: ② 换成官方那条**往返**验证：读回 `IDomeFeatureData2.Height`
OLD2 = '''        #: ⑤ **证据 B：特征树**
        names = feature_names(doc)'''
NEW2 = '''        #: ④b ★★★ **证据 A2：官方示例那条路 —— 读回 `IDomeFeatureData2.Height`**
        #: 官方 C# 示例：
        #:   `SelectByID2("Dome1","BODYFEATURE",…)` ⇒ `SelectionMgr.GetSelectedObject6(1,-1)`
        #:   ⇒ `(DomeFeatureData2)swFeature.GetDefinition()` ⇒ `Debug.Print(… .Height)`
        #: ⇒ ★ **这是"往返一致"级的证据**（写进去的高度能读回来），
        #:   比"边界框长了一点"强得多（已知事实 40 那一族：**void 返回要靠别的东西**）。
        h_read = None
        try:
            doc.Extension.SelectByID2("Dome1", "BODYFEATURE", 0, 0, 0, False, 0,
                                      sw_part._empty_callout(), 0)
            sel = doc.SelectionManager
            feat = sel.GetSelectedObject6(1, -1)
            if feat is not None:
                data = feat.GetDefinition()
                if data is not None:
                    try:
                        data.AccessSelections(doc, None)      # ⚠ 事实 47：BYREF 可能不行
                        ev["access_selections"] = "ok"
                    except Exception as exc:      # noqa: BLE001
                        ev["access_selections"] = "EXC: %s" % str(exc)[:70]
                    h_read = float(data.Height)
                    ev["dome_height_read_back_m"] = h_read
                    try:
                        ev["dome_elliptical"] = bool(data.Elliptical)
                    except Exception:      # noqa: BLE001
                        pass
        except Exception as exc:      # noqa: BLE001
            ev["height_read_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
        if h_read is None:
            chk("★★★ **证据 A2**：读回 `IDomeFeatureData2.Height`", False,
                ev.get("height_read_error") or ev.get("access_selections") or "拿不到")
        else:
            #: ⚠ 官方文档说 Height 是**米** ⇒ 若真如此，写 8 mm 应读回 0.008
            as_mm = h_read * 1000.0
            chk("★★★ **证据 A2**：读回高度 = %s ⇒ %s"
                % (h_read, "**毫米**（与文档的「meters」矛盾）"
                   if abs(as_mm - DOME_H) < 0.5 else "（与写入的 %.0f 不符）" % DOME_H),
                abs(as_mm - DOME_H) < 0.5 or abs(h_read - DOME_H) < 0.5,
                "写 %.0f ⇒ 读 %.6f（×1000 = %.3f）" % (DOME_H, h_read, as_mm))

        #: ⑤ **证据 B：特征树**
        names = feature_names(doc)'''
assert OLD2 in t, "证据 B 锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改成官方那条路（mark=1 + 读回 Height）")
