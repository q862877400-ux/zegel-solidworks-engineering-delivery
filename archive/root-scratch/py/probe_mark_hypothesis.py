r"""@brief 探针：**选区 Mark** 是不是那 3 个函数「属性设不上」的真因？

## 假设的来源（**官方文档原话**）
`IFeatureManager.InsertGussetFeature3` 的 Remarks 写着：
> Before calling this method, you must call `IModelDocExtension::SelectByID2` to select
> two faces that are the supporting legs of this gusset **with a Mark of 1**.

**⇒ 官方在**别的**特征上明写「必须带 Mark 选择」。**
而本项目 AGENTS.md 的**并入规则 3** 恰好写着「选择用声明式 `selection`，不写裸坐标，
**并按 mark 分配**」—— 而 `sw_simulation.select_face_at` 的 `mark` 默认是 `0`。

**⇒ 假设**：`create_gusset` / `create_edge_flange` / `create_draft` 的
`Property ... can not be set` 是因为**选区没有带对的 mark**。

## 怎么测
`IEntity.Select4(Append, Callout)` **不收 mark** ⇒ 要另找入口。候选：
1. `SelectByID2(name, type, x, y, z, append, MARK, callout, option)`（第 7 参就是 mark）
2. `ISelectionMgr.SetSelectedObjectMark(Index, Mark, Member)`（选完再改 mark）
两个都试，看**设属性是否从「失败」变「成功」**。

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档（`C:\swapi\types\IFeatureManager\InsertGussetFeature3.md`
#         的 Remarks 段）+ 本项目真机实测
# 文件:   `ISelectionMgr.SetSelectedObjectMark(Int32 Index, Int32 Mark, Int32 Member)`
#         `IModelDocExtension.SelectByID2(String, String, Double, Double, Double,
#             Boolean, Int32 Mark, Callout, Int32)`
# 定位:   `scripts/sw_sheet_metal.py` 那 3 个「属性设不上」函数的**第四层根因**候选。
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
from scripts.sw_part import _empty_callout  # noqa: E402
from scripts.sw_selection_spec import (  # noqa: E402
    clear_selection, current_selection, entities_on_body, get_selection_count, select_object,
)


def try_set_thickness(model, label):
    """建一个 Gusset FeatureData，看 `Thickness` 能否设上（这就是本轮唯一判据）。"""
    mgr = get_com_member(model, "FeatureManager")
    d = get_com_member(mgr, "CreateDefinition", SM.SW_FM_SM_GUSSET)
    if d is None:
        print("    [%-34s] CreateDefinition(118) → None" % label)
        return None
    try:
        d.Thickness = 0.002
        print("    [%-34s] ✓ **Thickness 设成功**" % label)
        return True
    except Exception as exc:  # noqa: BLE001
        print("    [%-34s] ✗ %s" % (label, str(exc)[:56]))
        return False


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        SM.create_base_flange(model, "Sketch1",
                              SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002, depth=0.05))
        print("[1] 参照零件 %r（已有基体法兰）" % title)

        faces = entities_on_body(model, "FACE")
        print("[2] 体上 %d 个面" % len(faces))
        f0 = faces[0] if faces else None

        print()
        print("=== 基线：无 mark（现状）===")
        clear_selection(model)
        select_object(model, f0)
        try_set_thickness(model, "Select4 后（mark 未知/0）")

        print()
        print("=== 候选 A：`ISelectionMgr.SetSelectedObjectMark(1, 1, 0)` 之后再设 ===")
        for mk in (1, 2, 4, 0):
            clear_selection(model)
            select_object(model, f0)
            sm = get_com_member(model, "SelectionManager")
            try:
                r = get_com_member(sm, "SetSelectedObjectMark", 1, mk, 0)
                ok = try_set_thickness(model, "SetSelectedObjectMark(1,%d,0)→%r" % (mk, r))
                if ok:
                    print("      ★★★ **mark=%d 就是答案**" % mk)
                    break
            except Exception as exc:  # noqa: BLE001
                print("    SetSelectedObjectMark(1,%d,0) → ✗ %s" % (mk, str(exc)[:52]))

        print()
        print("=== 候选 B：`SelectByID2` 直接带 mark（用面上的点）===")
        ext = get_com_member(model, "Extension")
        box = get_com_member(entities_on_body(model, "FACE")[0], "GetBox") \
            if hasattr(entities_on_body(model, "FACE")[0], "GetBox") else None
        # 用体包围盒推一个面上的点
        bodies = get_com_member(model, "GetBodies2", 0, True)
        bb = get_com_member(bodies[0], "GetBodyBox")
        mid = ((float(bb[0]) + float(bb[3])) / 2, (float(bb[1]) + float(bb[4])) / 2, float(bb[5]))
        for mk in (1, 2, 4, 0):
            clear_selection(model)
            try:
                get_com_member(ext, "SelectByID2", "", "FACE", mid[0], mid[1], mid[2],
                               False, mk, _empty_callout(), 0)
                cnt = get_selection_count(model)
                ok = try_set_thickness(model, "SelectByID2(mark=%d) 计数=%d" % (mk, cnt))
                if ok:
                    print("      ★★★ **SelectByID2 的 mark=%d 就是答案**" % mk)
                    break
            except Exception as exc:  # noqa: BLE001
                print("    SelectByID2(mark=%d) → ✗ %s" % (mk, str(exc)[:52]))

        print()
        print("=== 结论 ===")
        print("  若上面出现 ★★★ ⇒ mark 就是真因；否则 mark 也被排除。")
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
