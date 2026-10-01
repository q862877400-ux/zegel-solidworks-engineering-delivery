"""补上 `create_gusset` **整步缺失的第 3 步**：官方要求的 `ProfileDimensionScheme` 等属性。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 文档（`C:\\swapi\\`）
# 文件:   `types\\ISMGussetFeatureData\\_overview.md` 的 **Remarks** —— 官方把创建步骤写全了：
#           ```
#           To create a sheet metal gusset feature:
#           1. Call IFeatureManager::CreateDefinition …
#           2. **Pre-select** faces/lines/edges/vertices/points …（legs）
#           3. **Specify ISMGussetFeatureData::ProfileDimensionScheme and modify other properties**
#           4. Call IFeatureManager::CreateFeature.
#           ```
#         `types\\ISMGussetFeatureData\\ProfileDimensionScheme.md` → "See the … Remarks."
#         `types\\ISMGussetFeatureData\\UseOffset.md` → "**After setting this property to true,
#              set the offset distance. If a reference point is not set, the offset is
#              applied to an assumed reference point.**"
#         `types\\ISMGussetFeatureData\\OffsetDistance.md` → "valid only if UseOffset is true"
#         `types\\ISMGussetFeatureData\\UseAngleDimForProfile.md` → "**valid only if
#              ProfileDimensionScheme is set to 1**. After setting this property to true,
#              set ProfileAngleDim."
#         `enums\\swSheetMetalGussetProfileDimType_e.md` → IndentDepth=0, **ProfileDimensions=1**
# 定位:   **已知事实 34/43 里「三条卡在 `CreateFeature` 那一层」的第一条具体修复尝试。**
#
#   **发现**：模块的 `_apply` 只设了 `GussetThickness` / `ProfileHeightDim` /
#   `ProfileLengthDim` / `ProfileAngleDim` —— **而官方步骤 3 的头一句是
#   「Specify `ProfileDimensionScheme`」，模块**从未设过它**。**
#   官方的 `UseAngleDimForProfile` 更明写「valid only if ProfileDimensionScheme is set to 1」
#   ⇒ **不设 scheme 就设角度维，那个属性可能根本不生效**。
#   另：官方说「若未预选参照点，则**必须**把 `UseOffset` 设为 true」，模块也没设。
#
#  ⚠ **本补丁只是**补上官方要求的属性**，不宣称能让它跑起来** ——
#    真机结果由 `probe_sheet_metal_e2e.py` 复核，**以实测为准**。
#
# 官方签名依据: 上述 5 份官方页
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

SM = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sheet_metal.py")

OLD = """    def _apply(data):
        data.GussetThickness = float(spec.thickness)          # 原 Thickness（焊件名）
        data.ProfileHeightDim = float(spec.profile_distance_1)   # 原 ProfileDistance1
        data.ProfileLengthDim = float(spec.profile_distance_2)   # 原 ProfileDistance2
        data.ProfileAngleDim = float(spec.profile_angle)         # 原 ProfileAngle"""

NEW = """    def _apply(data):
        # ⚠⚠ **官方步骤 3 的头一句是「Specify `ProfileDimensionScheme`」，
        #   而本函数原先**从未设过它**（只设了 4 个尺寸属性）。**
        #   官方 `UseAngleDimForProfile` 更明写「**valid only if
        #   ProfileDimensionScheme is set to 1**」⇒ 不设 scheme 就设角度维，
        #   那个属性**可能根本不生效**。
        #   ⇒ 先设 scheme（`ProfileDimensions = 1`，与下面设的尺寸属性相配）。
        data.ProfileDimensionScheme = GUSSET_PROFILE_DIMENSIONS
        # 官方 `UseAngleDimForProfile`：「设为 true 后**必须**设 `ProfileAngleDim`」
        #   —— 本函数确实设了 ProfileAngleDim ⇒ 置 true。
        data.UseAngleDimForProfile = True
        data.GussetThickness = float(spec.thickness)          # 原 Thickness（焊件名）
        data.ProfileHeightDim = float(spec.profile_distance_1)   # 原 ProfileDistance1
        data.ProfileLengthDim = float(spec.profile_distance_2)   # 原 ProfileDistance2
        data.ProfileAngleDim = float(spec.profile_angle)         # 原 ProfileAngle
        # 官方 `UseOffset`：「**After setting this property to true, set the offset distance.**
        #   **If a reference point is not set, the offset is applied to an assumed
        #   reference point.**」 + Remarks 第 2 步：「**If you do not pre-select any of these
        #   entities, then you must set `UseOffset` to true**」
        #   ⇒ 本函数**不预选参照点** ⇒ **必须**置 true 并给 offset 距离。
        data.UseOffset = True
        data.OffsetDistance = 0.0"""

CONST_ANCHOR = "SW_FM_SKETCH_BEND = 35"
CONST_ADD = """SW_FM_SKETCH_BEND = 35

#: `swSheetMetalGussetProfileDimType_e` 的取值（官方枚举页）：
#: `IndentDepth = 0` · **`ProfileDimensions = 1`**。
#: 钣金加强筋的 `ProfileDimensionScheme` 必须显式指定 ——
#: 官方 `ISMGussetFeatureData` 的 Remarks 把它列为创建步骤 3 的**头一句**。
#: 数值来源：`C:\\swapi\\enums\\swSheetMetalGussetProfileDimType_e.md`。
GUSSET_PROFILE_DIMENSIONS = 1"""


def main() -> int:
    t = SM.read_text(encoding="utf-8")
    if OLD not in t:
        print("  ✗ 未匹配 create_gusset 的 _apply")
        return 1
    t = t.replace(OLD, NEW, 1)
    print("  ✓ ① create_gusset 的 _apply 已补上官方要求的属性")
    if CONST_ANCHOR in t and "GUSSET_PROFILE_DIMENSIONS" not in t.split("def ")[0]:
        t = t.replace(CONST_ANCHOR, CONST_ADD, 1)
        print("  ✓ ② 已加常量 GUSSET_PROFILE_DIMENSIONS = 1（官方枚举值）")
    SM.write_text(t, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
