r"""@brief 端到端链：**基体法兰 → 造折弯 → 用折弯的两面建 gusset**。

## 为什么这是本轮的目标
第 24/31 轮把 gusset 的阻塞定位到**官方步骤 2**：必须预选
「**一个折弯的两个平面**」（或一个圆柱折弯面 / 一个环形折弯面 …）。
**而夹具一直是**平板**（无折弯）⇒ 造不出那个前置。**

**⇒ 现在 `swFmSketchBend(35)` 已确证是 `CreateDefinition` 的合法类型（第 30 轮），
   所以**可以自己造折弯**，把整条链打通。**

## 链条
```
1. 基体法兰（平板）                                  ← 已能跑
2. 在顶面画一条**折弯线**（直线），选中它
3. `create_one_bend`（现用 swFmSketchBend(35)）→ **造出折弯**
4. 于是体上出现「折弯 + 两个平面」
5. 选中那两个平面 → `create_gusset`                 ← 本轮要打通的
```

## 注意（实测纪律）
* `CommandInProgress = True`；收尾关闭文档、**不保存**。
* 折弯线必须画在**面上**（先选面再进草图），不是基准面上。

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档
# 文件:   `C:\swapi\types\ISMGussetFeatureData\_overview.md` 的 Remarks 第 2 步
#           （预选「一个折弯的两个平面」…）
#         `C:\swapi\types\IFeatureManager\CreateDefinition.md`（35 个合法常量，含 swFmSketchBend）
# 定位:   打通「造折弯 → 建 gusset」这条链 —— 第 24/31 轮留下的**唯一未做的那一步**。
# 官方签名依据: 同上
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
from scripts import sw_part  # noqa: E402
from scripts import sw_sheet_metal as SM  # noqa: E402
from scripts.sw_selection_spec import (  # noqa: E402
    clear_selection, entities_on_body, get_selection_count, select_object,
)


def faces_of(model):
    return entities_on_body(model, "FACE")


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sm_mgr = get_com_member(model, "SketchManager")

        # ── 1. 基体法兰 ───────────────────────────────────────────────
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        SM.create_base_flange(model, "Sketch1",
                              SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002, depth=0.05))
        n0 = len(faces_of(model))
        print("[1] ✓ 基体法兰（平板）· 面数 %d" % n0)

        # ── 2. 在**顶面**画折弯线 ────────────────────────────────────
        faces = faces_of(model)
        # 顶面 = 法向 +Z 的那个（按 z 最大挑）
        best, best_z = None, None
        for f in faces:
            try:
                box = get_com_member(f, "GetBox")
                z = float(box[5]) if box and len(box) >= 6 else None
            except Exception:  # noqa: BLE001
                z = None
            if z is not None and (best_z is None or z > best_z):
                best, best_z = f, z
        print("[2] 顶面：z_max=%.4f" % (best_z if best_z is not None else float("nan")))
        clear_selection(model)
        select_object(model, best)
        print("    已选中顶面（选择计数 %d）" % get_selection_count(model))
        # 在选中的面上进草图
        try:
            get_com_member(sm_mgr, "InsertSketch", True)
            print("    ✓ 已在该面上进入草图")
        except Exception as exc:  # noqa: BLE001
            print("    ✗ InsertSketch 失败: %s" % str(exc)[:60])
            return 1
        # 画一条横穿板的直线（折弯线）
        try:
            get_com_member(sm_mgr, "CreateLine", -0.05, 0.0, best_z, 0.05, 0.0, best_z)
            get_com_member(sm_mgr, "InsertSketch", True)
            print("    ✓ 已画折弯线并退出草图")
        except Exception as exc:  # noqa: BLE001
            print("    ✗ 画线失败: %s" % str(exc)[:60])
            return 1

        # 草图名（BaseFlange 用了 Sketch1 ⇒ 新草图应为 Sketch2）
        for cand in ("Sketch2", "Sketch3", "Sketch4"):
            ok = False
            try:
                if get_com_member(model, "Extension").SelectByID2(
                        cand, "SKETCH", 0, 0, 0, False, 0, sw_part._empty_callout(), 0):
                    ok = True
            except Exception:  # noqa: BLE001
                pass
            if ok:
                print("[3] ✓ 草图名 = %r" % cand)
                break
        else:
            print("[3] ⚠ 找不到新草图名，直接试 Sketch2")
            cand = "Sketch2"

        # ── 3. 造折弯 ─────────────────────────────────────────────────
        print()
        print("=== ④ 造折弯（`create_one_bend`，现用 swFmSketchBend(35)）===")
        try:
            SM.create_one_bend(model, cand,
                               SM.OneBendSpec(bend_radius=0.002, angle=1.5707963267948966))
            print("  ✓ **折弯建成**")
        except Exception as exc:  # noqa: BLE001
            print("  ✗ %s" % str(exc)[:90])
        n1 = len(faces_of(model))
        print("  面数 %d → %d（**增加说明有折弯面**）" % (n0, n1))

        # ── 4. 用折弯的两面建 gusset ──────────────────────────────────
        print()
        print("=== ⑤ 试 gusset（按官方步骤 2 预选两个面）===")
        faces2 = faces_of(model)
        combos = [(0, 1), (1, 2), (2, 3), (0, 2)]
        for a, b in combos:
            if len(faces2) <= max(a, b):
                continue
            clear_selection(model)
            select_object(model, faces2[a])
            select_object(model, faces2[b], append=True)
            try:
                SM.create_gusset(model, SM.GussetSpec(thickness=0.002,
                                                      profile_distance_1=0.01))
                print("  面 (%d,%d) → ✓ **gusset 建成**" % (a, b))
                break
            except Exception as exc:  # noqa: BLE001
                print("  面 (%d,%d) → ✗ %s" % (a, b, str(exc)[:56]))

        print()
        print("=== 结论 ===")
        print("  若 ④ 成功 ⇒ **能自己造折弯**（这本身是新能力）")
        print("  若 ⑤ 成功 ⇒ 第 24/31 轮那条链**打通了**")
        print("  ⚠ 失败则如实记，**不宣称**。")
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
