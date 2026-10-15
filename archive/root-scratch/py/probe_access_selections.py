r"""@brief 决定性测试：**先调 `AccessSelections`**，再设属性 / `SetFixedFace`。

## 🎯 根据（反射 + 官方那句「Accessing Selections that Define Features」）
```
ISketchedBendFeatureData 的成员（**出厂类型库反射**）:
  **Boolean AccessSelections(Object, Object)**      ← ★ 官方文档里 SetFixedFace 的说明
                                                      指向的就是这个主题
  Void SetFixedFace(Double, Double, Double, Object)
  Void ReleaseSelectionAccess()
```
**⇒ 官方那套标准形态是**三段**：**
```
1. data.AccessSelections(model, component)   ← 打开选择访问
2. 设属性；**与选择集有关的参数此时传空**（`None` / `Nothing`）
3. data.ReleaseSelectionAccess()             ← 关闭
```

**⚠ 前两轮（18 种形态）全失败，**共同点是从没调过 `AccessSelections`**。**
**⇒ 本探针先补上它。**

## ⚠ 为什么这可能一次解锁**四个**工具
`sw_sheet_metal` 的 4 个不可用入口（`create_one_bend` / `create_edge_flange` /
`create_gusset` / `create_draft`）**全部**走 `_create_from_definition`，
**全部**卡在 `CreateFeature(N)`，而它们**全部**有 `AccessSelections` ——
**⇒ 若真因是「缺 `AccessSelections`」，那是一处修、四处受益。**

# ── 来源 ──
# 仓库:   SolidWorks 出厂类型库反射（冲突裁决者）+ 官方 API 文档
# 文件:   `D:\AI\SW\_raw\**\iface_sldworks.txt` 的 `ISketchedBendFeatureData` 段
#           （`Boolean AccessSelections(Object, Object)` / `ReleaseSelectionAccess()`）
#         `C:\swapi\types\ISketchedBendFeatureData\SetFixedFace.md`
#           （说明指向 "Accessing Selections that Define Features"）
# 定位:   已知事实 45 的**第三层**：`SetFixedFace` 传什么都报 `类型不匹配`
#         ⇒ 怀疑缺**前置的 `AccessSelections`**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；造参照几何 + 试建特征、**不保存**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part, sw_sheet_metal as SM  # noqa: E402
from scripts.sw_selection_spec import (  # noqa: E402
    clear_selection, entities_on_body, get_selection_count, select_object,
)


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sm = get_com_member(model, "SketchManager")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        SM.create_base_flange(model, "Sketch1",
                              SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002, depth=0.05))
        n0 = len(entities_on_body(model, "FACE"))
        faces = entities_on_body(model, "FACE")
        top = max(faces, key=lambda f: float(get_com_member(f, "GetBox")[5]))
        z = float(get_com_member(top, "GetBox")[5])
        clear_selection(model)
        select_object(model, top)
        get_com_member(sm, "InsertSketch", True)
        get_com_member(sm, "CreateLine", -0.05, 0.0, z, 0.05, 0.0, z)
        get_com_member(sm, "InsertSketch", True)
        print("[准备] 基体法兰 ✓（面 %d）；折弯线 ✓" % n0)

        ext = get_com_member(model, "Extension")
        mgr = get_com_member(model, "FeatureManager")

        def attempt(label, with_access, edges_for_fixed):
            clear_selection(model)
            try:
                ext.SelectByID2("草图6", "SKETCH", 0, 0, 0, False, 0,
                                sw_part._empty_callout(), 0)
            except Exception:
                pass
            d = get_com_member(mgr, "CreateDefinition", SM.SW_FM_SKETCH_BEND)
            if d is None:
                print("  %-40s CreateDefinition None" % label); return
            accessed = False
            if with_access:
                try:
                    ok = get_com_member(d, "AccessSelections", model, None)
                    accessed = True
                    print("  %-40s AccessSelections → %r" % (label, ok))
                except Exception as exc:
                    print("  %-40s AccessSelections ✗ %s" % (label, str(exc)[:44])); return
            try:
                d.UseDefaultBendRadius = False
                d.BendAngle = 1.5707963267948966
                d.BendRadius = 0.002
                d.UseGaugeTable = False
            except Exception as exc:
                print("  %-40s 属性 ✗ %s" % (label, str(exc)[:44]))
            r = None
            try:
                r = d.SetFixedFace(0.0, 0.0, 0.0, edges_for_fixed)
                print("  %-40s SetFixedFace ✓ 返回 %r" % (label, r))
            except Exception as exc:
                print("  %-40s SetFixedFace ✗ %s" % (label, str(exc)[:48]))
            if with_access and accessed:
                try:
                    get_com_member(d, "ReleaseSelectionAccess")
                except Exception:
                    pass
            f = get_com_member(mgr, "CreateFeature", d)
            print("  %-40s → CreateFeature %s"
                  % ("", "**✓ 建成**" if f is not None else "✗ None"))

        print()
        print("=== ① 先 AccessSelections，SetFixedFace 传 None ===")
        attempt("access + SetFixedFace(0,0,0,None)", True, None)

        print()
        print("=== ② 先 AccessSelections，**不调** SetFixedFace ===")
        attempt("access + 不设固定面", True, "SKIP")

        print()
        print("=== ③ 对照：**不调** AccessSelections（前两轮的做法）===")
        attempt("no-access + SetFixedFace(0,0,0,None)", False, None)

        n1 = len(entities_on_body(model, "FACE"))
        print()
        print("  面数 %d → %d %s" % (n0, n1, "（**增加 ⇒ 折弯建成**）" if n1 > n0 else ""))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
                print("  [收尾] 文档已关闭（未保存）")
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
