r"""@brief 探针：`create_one_bend` 改用 **`swFmSketchBend(35)`** 能否建成？

## 已确证的链路（全部来自官方源，没有一步是猜的）
```
① 官方 `IFeatureManager.CreateDefinition.md` 的 **Parameters** 段列出**35 个**合法常量，
   其中**有** `swFmSketchBend (sheet metal sketched bend)`，
   而**没有** `swFmOneBend`、也**没有** `swFmDraft`。
② 反射转储 `enum_values_sldworks.txt` 给出数值：
   `swFmSketchBend = 35`、`swFmOneBend = 33`、`swFmDraft = 3`（三者都是**合法枚举成员**）。
③ 由此：`CreateDefinition(33)` 返回 None **是应然的** —— 它是枚举成员，
   **但不是 `CreateDefinition` 接受的类型**。
④ 官方链路还给出接口：`swFmSketchBend → ISketchedBendFeatureData`
   （由 `CreateDefinition.md` 的括注 "sheet metal sketched bend" 与
     `ISketchedBendFeatureData/_overview.md` 的 Description 匹配得到，**唯一命中**）。
```

## 本探针要回答
把 `create_one_bend` 的常量从 `SW_FM_ONE_BEND(33)` 换成 `SW_FM_SKETCH_BEND(35)` 后，
**能不能真建出特征？**

**⚠ 若成 ⇒ 这是把「已暴露但真机不可用」的 4 条之一**修好**的实证。
   若不成 ⇒ 如实记，**不宣称**。**

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档 + 出厂类型库反射
# 文件:   `C:\swapi\types\IFeatureManager\CreateDefinition.md`（35 个合法常量）
#         `D:\AI\SW\_raw\**\enum_values_sldworks.txt`（枚举数值，130 个成员）
#         `C:\swapi\types\ISketchedBendFeatureData\_overview.md`
# 定位:   已知事实 34 里 `create_one_bend` 的 `CreateDefinition(33) 返回 None` 的**修复验证**。
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

SW_FM_SKETCH_BEND = 35   # 反射 enum_values_sldworks.txt 核实


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        # 先建一块基体法兰（折弯必须先有钣金体）
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        try:
            SM.create_base_flange(model, "Sketch1",
                                  SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002,
                                                    depth=0.05))
            print("[1] ✓ 基体法兰已建（钣金体存在）")
        except Exception as exc:  # noqa: BLE001
            print("[1] ✗ 基体法兰失败: %s" % str(exc)[:70])
            return 1
        mgr = get_com_member(model, "FeatureManager")

        print()
        print("=== ① 直接试 `CreateDefinition(35)`（swFmSketchBend）===")
        d35 = get_com_member(mgr, "CreateDefinition", SW_FM_SKETCH_BEND)
        print("  CreateDefinition(35) → %s" % ("✓ 非 None" if d35 is not None else "✗ **None**"))
        if d35 is not None:
            iface = get_com_member(d35, "GetType") if hasattr(d35, "GetType") else None
            print("  ⇒ **拿到了 FeatureData** ⇒ 35 是 `CreateDefinition` 接受的类型")

        print()
        print("=== ② 对照：`CreateDefinition(33)`（swFmOneBend，当前模块用的）===")
        d33 = get_com_member(mgr, "CreateDefinition", SM.SW_FM_ONE_BEND)
        print("  CreateDefinition(33) → %s" % ("✓ 非 None" if d33 is not None else "✗ **None**"))
        print("  ⇒ 官方 `CreateDefinition.md` 的合法名单里**没有** `swFmOneBend` ⇒ None **是应然的**")

        print()
        print("=== ③ 用 35 试着真建一个折弯（需要一条折弯线草图）===")
        # 在面上画一条折弯线，再选它 + 设属性
        try:
            sk2 = sw_part.sketch(model, "Front Plane")
            sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
            print("  ⚠ 折弯线的构造与选择未定型（需要面上的线 + 固定面）")
        except Exception as exc:  # noqa: BLE001
            print("  ⚠ %s" % str(exc)[:60])

        print()
        print("=== ④ 若 35 的 FeatureData 里能读到属性，列出**接口自查** ===")
        if d35 is not None:
            for prop in ("BendRadius", "BendAngle", "ReverseDirection", "UseDefaultBendRadius",
                         "UseDefaultBendAllowance", "FixedFace", "BendLine"):
                try:
                    v = getattr(d35, prop)
                    print("    %-26s → ✓ %r" % (prop, v))
                except Exception as exc:  # noqa: BLE001
                    print("    %-26s → ✗ %s" % (prop, str(exc)[:44]))

        print()
        print("=== 结论 ===")
        print("  若 ① 非 None 而 ② 是 None ⇒ **官方名单解释了 `create_one_bend` 的失败**，")
        print("     且 `SW_FM_SKETCH_BEND = 35` 是**有官方依据的候选入口**。")
        print("     ⚠ 但「能拿到 FeatureData」≠「能建出特征」—— 后者需选折弯线，**本轮未定型**。")
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
