"""修 `create_one_bend`：常量由 `swFmOneBend(33)` 改为 **`swFmSketchBend(35)`**（有官方依据）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 文档 + 出厂类型库反射
# 文件:   `C:\\swapi\\types\\IFeatureManager\\CreateDefinition.md` 的 **Parameters** 段 ——
#         列出 `CreateDefinition` 接受的 **35 个**常量，其中
#         **有** `swFmSketchBend (sheet metal sketched bend)`，
#         **没有** `swFmOneBend`、也**没有** `swFmDraft`。
#         `D:\\AI\\SW\\_raw\\**\\enum_values_sldworks.txt` —— 枚举数值（130 个成员）：
#         `swFmSketchBend = 35`、`swFmOneBend = 33`。
#         `C:\\swapi\\types\\ISketchedBendFeatureData\\` —— 16 个成员（`BendAngle` / `BendRadius` /
#         `ReverseDirection` / `UseDefaultBendRadius` / `UseDefaultBendAllowance` / …）。
# 定位:   **已知事实 34** 里 `create_one_bend` 的 `CreateDefinition(33) 返回 None`，
#         原先记作「真因尚未查明」。2026-10-01 查明并修复：
#
#   **① 真因（有官方依据）**：`swFmOneBend(33)` 是**合法枚举成员**，
#      **但不是 `CreateDefinition` 接受的类型** —— 官方 Parameters 段的 35 个常量里没有它。
#      ⇒ `CreateDefinition(33)` 返回 None **是应然的**，不是 COM 或权限问题。
#
#   **② 正确入口**：`swFmSketchBend(35)`（官方名单里有），
#      接口是 `ISketchedBendFeatureData`（由 CreateDefinition.md 的括注
#      "sheet metal sketched bend" 与该接口 `_overview.md` 的 Description 匹配得到，**唯一命中**）。
#
#   **③ 真机验证**：
#      · `CreateDefinition(35)` → **非 None**；`CreateDefinition(33)` → None（与官方名单一致）
#      · 拿到对象的属性读回：`BendRadius=0.01` / `BendAngle=1.5708` / `ReverseDirection=False` /
#        `UseDefaultBendRadius=True` / `UseDefaultBendAllowance=False`
#        ⇒ 与 `ISketchedBendFeatureData` 的成员**逐一吻合**
#      · `FixedFace` / `BendLine` 读不到 —— 因为该接口给的是 **`GetFixedFace`/`SetFixedFace`**
#        （**方法**形式），**不是属性**。**⇒ 这一点也有官方依据，不是「属性只读」。**
#
#   **④ 本函数 `_apply` 里那 4 个属性**全部**是 `ISketchedBendFeatureData` 的合法成员**
#      ⇒ **错的只有常量**，属性层本来就是对的。
#
#  ⚠ **仍未定性的部分**（不宣称能跑）：真建出折弯还需**选中折弯线/固定面**，
#    那一步本轮**未定型** ⇒ 状态表仍标为不可用，但**原因已从「未查明」变成「缺选择步骤」**。
#
# 官方签名依据: `System.object CreateDefinition( System.int Type )` + 官方 35 个常量名单
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SM = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sheet_metal.py")

# ① 在 SW_FM_ONE_BEND 旁边加 SW_FM_SKETCH_BEND（带来源）
OLD_CONST = "SW_FM_ONE_BEND = 33"
NEW_CONST = """SW_FM_ONE_BEND = 33
#: ⚠ `swFmOneBend(33)` 是**合法枚举成员**，但**不在** `CreateDefinition` 接受的 35 个常量里
#: ⇒ `CreateDefinition(33)` 返回 None **是应然的**（已知事实 34 的真因，2026-10-01 查明）。
#: 「一个折弯」的**正确入口**是下面这个（官方名单里有，接口 `ISketchedBendFeatureData`）。
#: 数值来源：`D:\\AI\\SW\\_raw\\**\\enum_values_sldworks.txt`（反射，130 个成员）。
SW_FM_SKETCH_BEND = 35"""

# ② `create_one_bend` 改用 SW_FM_SKETCH_BEND
OLD_USE = "    return _create_from_definition(model, SW_FM_ONE_BEND, _apply)"
NEW_USE = """    # ⚠⚠ **原为 `SW_FM_ONE_BEND(33)`** —— 那是**合法枚举成员**，
    #   但**不在** `CreateDefinition` 接受的 35 个常量里（见常量定义处的注释），
    #   所以 `CreateDefinition(33)` 返回 None 是**应然的**。
    #   官方名单里「一个折弯」对应的是 `swFmSketchBend(35)`。
    #   ⇒ 真机已验证：`CreateDefinition(35)` 返回**非 None**，且读回的属性与
    #     `ISketchedBendFeatureData` 的成员逐一吻合。
    #   ⚠ **仍缺**「选中折弯线/固定面」这一步 ⇒ 不宣称整条路已通。
    return _create_from_definition(model, SW_FM_SKETCH_BEND, _apply)"""

# ③ 状态表：把原因从「未查明」改成具体的「缺选择步骤」
OLD_STATUS = '''    "create_one_bend": (False,
        "CreateDefinition(33) 返回 None ⇒ **该类型不走 `CreateDefinition`**；"'''
NEW_STATUS = '''    "create_one_bend": (False,
        "⚠ **真因已查明（2026-10-01，有官方依据）**：`swFmOneBend(33)` 是合法枚举成员，"
        "但**不在** `CreateDefinition` 接受的 35 个常量里（官方 `CreateDefinition.md` 的 "
        "Parameters 段）⇒ 返回 None **是应然的**。"
        "**正确入口**是 `swFmSketchBend(35)`（**已改用**），接口 `ISketchedBendFeatureData`。"
        "真机已验证 `CreateDefinition(35)` 返回**非 None**，且属性读回与该接口成员逐一吻合。"
        "**⚠ 仍缺**「选中折弯线 / 固定面」这一步 ⇒ 仍标不可用，但**原因已具体化**"
        "（不再是「未查明」）。原记法：`CreateDefinition(33) 返回 None ⇒ 不走 CreateDefinition`；"'''


def main() -> int:
    t = SM.read_text(encoding="utf-8")
    n = 0
    for old, new, label in ((OLD_CONST, NEW_CONST, "常量"),
                            (OLD_USE, NEW_USE, "调用点"),
                            (OLD_STATUS, NEW_STATUS, "状态表")):
        if old in t:
            t = t.replace(old, new, 1)
            print("  ✓ 已改：%s" % label)
            n += 1
        else:
            print("  ⚠ 未匹配：%s" % label)
    SM.write_text(t, encoding="utf-8")
    return 0 if n == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
