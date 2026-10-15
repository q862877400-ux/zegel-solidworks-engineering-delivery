r"""@brief 探针：**造出折弯**再试钣金加强筋（验证「阻塞在测试夹具而非代码」这一判断）。

## 已经查明的
`ISMGussetFeatureData` 的官方 Remarks 明写创建钣金加强筋要：
1. `IFeatureManager::CreateDefinition` 取特征数据；
2. **预先选中**「**一个折弯的两个平面**」（`Two flat faces of a bend`）。

而官方示例（`Insert_Sheet_Metal_Gusset_Feature_Example_VB.md`）用的是
`InsertSheetMetalGussetFeature3` —— **但那个方法的官方文档写着
「Obsolete. Superseded by CreateDefinition and CreateFeature.」**
**⇒ 模块原本的路线（CreateDefinition + CreateFeature）**才是现代的**。**

**⇒ 所以 `create_gusset` 的 `CreateFeature(118) 创建失败`，很可能是
**我的测试零件里根本没有折弯**（平板基体法兰）⇒ **选不出「一个折弯的两个平面」。**

## 本探针要回答的
能否用**另一条路**造出折弯，从而给 gusset 提供合法的两个面？
* `InsertSheetMetal3dBend(Angle, BUseDefaultRadius, Radius, FlipDir, BendType, CustomBendAllowance)`
  —— 反射里有 `Feature` 与 `Void` 两个变体（**注意同名不同返回**）
* 若造出折弯，再按官方要求选**两个面**，试 `create_gusset`

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档 + 反射
# 文件:   `ISMGussetFeatureData._overview.md` 的 **Remarks**（创建步骤）
#         `IFeatureManager.InsertSheetMetalGussetFeature3.md`（**标注 Obsolete**）
#         `IFeatureManager.InsertSheetMetal3dBend(...)`（反射有两个变体）
# 定位:   `create_gusset` 的**最后一层**：是代码错还是测试夹具不对。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只造参照几何、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_sheet_metal as SM  # noqa: E402
from scripts.sw_selection_spec import (  # noqa: E402
    clear_selection, entities_on_body, get_selection_count, select_object,
)


def face_names(model):
    out = []
    for f in entities_on_body(model, "FACE"):
        try:
            out.append(str(get_com_member(f, "GetType")) if False else "")
        except Exception:  # noqa: BLE001
            out.append("")
    return out


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        # 造一段**折弯**：先画一条开放折线（两段），做成轮廓法兰（profile flange）
        sk = sw_part.sketch(model, "Front Plane")
        # 开放折线：L 形
        sm = get_com_member(model, "SketchManager")
        get_com_member(sm, "CreateLine", -0.05, 0.0, 0.0, 0.05, 0.0, 0.0)
        get_com_member(sm, "CreateLine", 0.05, 0.0, 0.0, 0.05, 0.05, 0.0)
        # ⚠ **必须退出草图**（`InsertSketch(True)` 是进出开关）——
        #   第一版没退 ⇒ 草图没成型 ⇒ `_ensure_sketch_selected` 找不到它
        #   ⇒ base_flange 报「无法选择草图: Sketch1」。
        get_com_member(sm, "InsertSketch", True)
        print("[1] 已画开放折线草图（L 形）并**退出草图**")

        mgr = get_com_member(model, "FeatureManager")
        # 官方示例用的构造：InsertSheetMetalBaseFlange2 不试；先用模块自己的 base_flange
        try:
            SM.create_base_flange(model, "Sketch1",
                                  SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002,
                                                    depth=0.05))
            print("[2] base_flange 成功（开放折线 ⇒ 轮廓法兰，**应含折弯**）")
        except Exception as exc:  # noqa: BLE001
            print("[2] ✗ base_flange 失败: %s" % str(exc)[:70])

        faces = entities_on_body(model, "FACE")
        print("[3] 现在体上有 **%d** 个面（平板时是 6；含折弯会更多）" % len(faces))

        print()
        print("=== ① 折弯造出来了吗（面数变化 ⇒ 有折弯）===")
        print("  ⇒ %s" % ("**有折弯**（面数 > 6）" if len(faces) > 6 else "**仍像平板**（面数 ≤ 6）"))

        print()
        print("=== ② 按官方要求选**两个面**后试 create_gusset ===")
        for combo in ((0, 1), (0, 2), (1, 2)):
            if len(faces) <= max(combo):
                continue
            clear_selection(model)
            select_object(model, faces[combo[0]])
            select_object(model, faces[combo[1]], append=True)
            cnt = get_selection_count(model)
            try:
                SM.create_gusset(model, SM.GussetSpec(thickness=0.002,
                                                      profile_distance_1=0.01))
                print("  面 %r 组合 → 计数 %d ⇒ **✓ 建成**" % (combo, cnt))
                break
            except Exception as exc:  # noqa: BLE001
                print("  面 %r 组合 → 计数 %d ⇒ ✗ %s" % (combo, cnt, str(exc)[:56]))

        print()
        print("=== ③ 若仍不成：试专用入口 InsertSheetMetalGussetFeature3（尽管已标 Obsolete）===")
        try:
            clear_selection(model)
            select_object(model, faces[0])
            select_object(model, faces[1], append=True)
            f3 = get_com_member(
                mgr, "InsertSheetMetalGussetFeature3",
                True, 0.05, False, 0, 0.01, 0.0, False, 0.0, 0.0,
                True, 0.01, 0.003, True, 3 * 0.0175, True, 0.002, True, 0.001,
                0, False, 0.0, True, True, True)
            print("  ⇒ %s" % ("✓ 返回非 None" if f3 is not None else "✗ None"))
        except Exception as exc:  # noqa: BLE001
            print("  ⇒ ✗ %s" % str(exc)[:80])

        print()
        print("=== 结论 ===")
        print("  若 ① 显示面数 > 6 且 ② 成功 ⇒ **原判断成立：之前失败是因为测试零件没有折弯**")
        print("  若 ① 显示面数 ≤ 6 ⇒ 我的夹具仍没造出折弯，本轮**未定性**")
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
