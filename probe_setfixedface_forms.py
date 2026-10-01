r"""@brief `SetFixedFace` 第 4 个参数（`EdgeArray`）的**各种传法**实测。

## 已确证的（第 32 轮）
```
SetFixedFace(X, Y, Z, **None**) → `类型不匹配`（0x80028CA0）
⇒ 与已知事实 33（SelectByID2 的 Callout 传 None）**同一个错误类**
官方 GetFixedFace：「the location is a point on the fixed face, but **in the space of the
sketch** … Thus, **the z location is always 0**」
```

## 官方那条通用规则
`SetFixedFace` 的说明指向 **"Accessing Selections that Define Features"** ——
SolidWorks API 的标准形态是：**先 `SelectByID2` 选中实体，再把（空的或被选对象的）
数组传进这类方法**。

**⇒ 本探针把两种做法 × 几种数组包装都试一遍**，看哪一种能过。

## 本探针要回答
1. `EdgeArray` 收什么形态？（`None` / `[]` / 逐元素 VARIANT / `VT_ARRAY|VT_DISPATCH` / 传边对象）
2. **先选好边**再传空数组，能不能过？
3. 过了之后 `CreateFeature(35)` 能不能建成？

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档
# 文件:   `C:\swapi\types\ISketchedBendFeatureData\SetFixedFace.md`
#           （`void SetFixedFace( System.double X, System.double Y, System.double Z,
#             System.object EdgeArray )`，说明指向 "Accessing Selections that Define Features"）
#         `GetFixedFace.md`（点用**草图坐标系**，z 恒为 0）
# 定位:   已知事实 45 的直接续：`EdgeArray` 传 `None` 报 `类型不匹配` ⇒ 试**真正的数组**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；造参照几何 + 试建特征、**不保存**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from win32com.client import VARIANT
import pythoncom

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part, sw_sheet_metal as SM  # noqa: E402
from scripts.sw_selection_spec import (  # noqa: E402
    clear_selection, entities_on_body, get_selection_count, select_object,
)


def array_forms():
    """返回 ``[(标签, 取值函数)]`` —— 第 4 个参数的各种形态。"""
    empty_disp = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [])
    empty_var = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, [])
    return [
        ("None", lambda edges: None),
        ("[] 裸列表", lambda edges: []),
        ("VT_ARRAY|VT_DISPATCH([])", lambda edges: empty_disp),
        ("VT_ARRAY|VT_VARIANT([])", lambda edges: empty_var),
        ("边对象列表（裸）", lambda edges: list(edges)),
        ("逐元素 VARIANT", lambda edges: [VARIANT(pythoncom.VT_DISPATCH, e) for e in edges]),
        ("VT_ARRAY|VT_DISPATCH(边)", lambda edges: VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(edges))),
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

        # 在顶面画折弯线
        faces = entities_on_body(model, "FACE")
        top = max(faces, key=lambda f: float(get_com_member(f, "GetBox")[5]))
        z = float(get_com_member(top, "GetBox")[5])
        clear_selection(model)
        select_object(model, top)
        get_com_member(sm, "InsertSketch", True)
        get_com_member(sm, "CreateLine", -0.05, 0.0, z, 0.05, 0.0, z)
        get_com_member(sm, "InsertSketch", True)
        print("[准备] 基体法兰 ✓（面 %d）；折弯线 ✓（草图6）" % n0)

        # 取一些边（固定面的候选）
        edges = entities_on_body(model, "EDGE")
        print("[准备] 体上有 %d 条边（取前 3 条做 EdgeArray 素材）" % len(edges))
        sample_edges = edges[:3]

        ext = get_com_member(model, "Extension")
        mgr = get_com_member(model, "FeatureManager")

        def attempt(label, form, preselect_edges):
            clear_selection(model)
            try:
                ext.SelectByID2("草图6", "SKETCH", 0, 0, 0, False, 0,
                                sw_part._empty_callout(), 0)
            except Exception:
                pass
            if preselect_edges:
                for e in sample_edges:
                    try:
                        select_object(model, e, append=True)
                    except Exception:
                        pass
            d = get_com_member(mgr, "CreateDefinition", SM.SW_FM_SKETCH_BEND)
            if d is None:
                print("  %-34s CreateDefinition None" % label); return
            try:
                d.UseDefaultBendRadius = False
                d.BendAngle = 1.5707963267948966
                d.BendRadius = 0.002
                d.UseGaugeTable = False
            except Exception as exc:
                print("  %-34s 基础属性失败: %s" % (label, str(exc)[:40])); return
            try:
                d.SetFixedFace(0.0, 0.0, 0.0, form(sample_edges))
            except Exception as exc:
                print("  %-34s SetFixedFace ✗ %s" % (label, str(exc)[:46])); return
            f = get_com_member(mgr, "CreateFeature", d)
            print("  %-34s SetFixedFace ✓ → CreateFeature %s"
                  % (label, "**✓ 建成**" if f is not None else "✗ None"))

        print()
        print("=== ① 第 4 参数的七种形态（**不预选边**）===")
        for label, form in array_forms():
            attempt(label, form, preselect_edges=False)

        print()
        print("=== ② **先预选边**，再传空数组 ===")
        for label, form in array_forms()[:4]:
            attempt("预选边 + " + label, form, preselect_edges=True)

        n1 = len(entities_on_body(model, "FACE"))
        print()
        print("  面数 %d → %d" % (n0, n1))
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
