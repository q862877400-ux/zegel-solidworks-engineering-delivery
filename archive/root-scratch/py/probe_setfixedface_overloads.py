r"""@brief `SetFixedFace` 的**两个重载**实测 —— 出厂类型库里有文档没写的单参数版。

## 🎯 本轮的根据（**出厂类型库 > 文档**，铁律 4）
```
反射（D:\AI\SW\_raw\**\iface_sldworks.txt）:
  Void  SetFixedFace(Object)                       ← ★ **单参数重载**（官方文档**没写**）
  Void  SetFixedFace(Double, Double, Double, Object)
官方文档只写了四参版。
⇒ 上一轮**四种形态 × 七种数组包装**全部报
   `(-2147352567, '类型不匹配', None, **4**)`（**第 4 个参数**位置）
⇒ 这与「late binding 解析到错的重载」的表现一致 ⇒ **试单参数版**。
```

## 本探针要回答
1. `SetFixedFace(**)单参数**版` 收什么？（空数组 / 边对象数组 / VARIANT 数组 / 直接传对象）
2. 过了之后 `CreateFeature(35)` 能不能建成？

## ⚠ 通用教训（值得记）
**同名方法有多个重载时，late binding 的调用可能解析到**错的那个**，
而错误信息只说「第 N 个参数类型不匹配」—— 指向不了「其实该用另一个重载」。**
**⇒ 查反射时要把**所有**同名重载都列出来，不能只看文档写的那一个。**

# ── 来源 ──
# 仓库:   SolidWorks 出厂类型库反射（冲突时的裁决者，见 AGENTS.md 铁律 4）
# 文件:   `D:\AI\SW\_raw\**\iface_sldworks.txt`
#           `Void SetFixedFace(Object)` 与 `Void SetFixedFace(Double, Double, Double, Object)`
#         `C:\swapi\types\ISketchedBendFeatureData\SetFixedFace.md`（只写了四参版）
# 定位:   已知事实 45 的续：`EdgeArray` 传各种数组都报 `类型不匹配`（位置 4）
#         ⇒ 怀疑**重载选错** ⇒ 改调**单参数版**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；造参照几何 + 试建特征、**不保存**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

import pythoncom
from win32com.client import VARIANT

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part, sw_sheet_metal as SM  # noqa: E402
from scripts.sw_selection_spec import (  # noqa: E402
    clear_selection, entities_on_body, get_selection_count, select_object,
)


def one_param_forms(edges):
    """单参数重载的各种取值。"""
    return [
        ("边对象列表（裸 list）", list(edges)),
        ("VT_ARRAY|VT_DISPATCH(边)", VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(edges))),
        ("VT_ARRAY|VT_VARIANT(边)", VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, list(edges))),
        ("空列表 []", []),
        ("VT_ARRAY|VT_DISPATCH([])", VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [])),
        ("单条边（裸）", edges[0] if edges else None),
        ("VT_DISPATCH(单条边)", VARIANT(pythoncom.VT_DISPATCH, edges[0]) if edges else None),
    ]


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

        edges = entities_on_body(model, "EDGE")
        # 顶面的边：z 接近 top 的那些
        top_edges = []
        for e in edges:
            try:
                box = get_com_member(e, "GetBox")
                if box and abs(float(box[5]) - z) < 1e-6:
                    top_edges.append(e)
            except Exception:  # noqa: BLE001
                pass
        print("[准备] 基体法兰 ✓（面 %d）；折弯线 ✓；体上 %d 边，其中顶面边 %d 条"
              % (n0, len(edges), len(top_edges)))
        use_edges = top_edges or edges[:2]

        ext = get_com_member(model, "Extension")
        mgr = get_com_member(model, "FeatureManager")

        def attempt(label, call):
            clear_selection(model)
            try:
                ext.SelectByID2("草图6", "SKETCH", 0, 0, 0, False, 0,
                                sw_part._empty_callout(), 0)
            except Exception:
                pass
            d = get_com_member(mgr, "CreateDefinition", SM.SW_FM_SKETCH_BEND)
            if d is None:
                print("  %-30s CreateDefinition None" % label); return
            try:
                d.UseDefaultBendRadius = False
                d.BendAngle = 1.5707963267948966
                d.BendRadius = 0.002
                d.UseGaugeTable = False
            except Exception as exc:
                print("  %-30s 基础属性失败: %s" % (label, str(exc)[:36])); return
            try:
                call(d)
            except Exception as exc:
                print("  %-30s 设固定面 ✗ %s" % (label, str(exc)[:50])); return
            f = get_com_member(mgr, "CreateFeature", d)
            print("  %-30s ✓ → CreateFeature %s"
                  % (label, "**✓ 建成**" if f is not None else "✗ None"))

        print()
        print("=== ① **单参数重载** `SetFixedFace(Array)` 的各种取值 ===")
        for label, val in one_param_forms(use_edges):
            attempt("1参: " + label, lambda d, v=val: d.SetFixedFace(v))

        print()
        print("=== ② 对照：**四参重载**（上一轮失败的那个）===")
        attempt("4参: (0,0,0,边列表)", lambda d: d.SetFixedFace(0.0, 0.0, 0.0, list(use_edges)))

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
