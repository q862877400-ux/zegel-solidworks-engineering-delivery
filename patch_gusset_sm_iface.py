"""修 `create_gusset`：改用**钣金**接口 `ISMGussetFeatureData` 的属性名（根因已确证）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 类型表（`C:\\swapi\\types\\ISMGussetFeatureData\\`）
# 文件:   `ISMGussetFeatureData` —— `category: Feature Interfaces/**Sheet Metal**`，
#         `property_count: 28` / `method_count: 2`，说明「Allows access to a
#         **sheet metal gusset** feature」。
# 定位:   **完整根因（第四层，也是最后一层）**：
#
#   本模块的 `create_gusset` 用 `SW_FM_SM_GUSSET = 118`（枚举名
#   `swFmSMGusset` = "**Sheet metal** gusset"），**这是钣金加强筋**；
#   但它设属性时用的是 **`IGussetFeatureData`** —— 那是 **`Feature Interfaces/Weldments`**
#   （焊件加强筋）的接口！
#
#   两个接口的成员**几乎完全不同**：
#     SM（钣金，28 个）: GussetThickness, ProfileHeightDim, ProfileLengthDim,
#                        ProfileAngleDim, SupportingFaces, DraftAngle, IndentDepth, …
#     焊件（19 个）:     Thickness, ProfileDistance1..4, ProfileAngle, ProfileLocation, …
#     **共有成员只有 3 个**：AccessSelections / ProfileType / ReleaseSelectionAccess
#
#   原代码设的 4 个属性 `Thickness` / `ProfileDistance1` / `ProfileDistance2` /
#   `ProfileAngle` **全部来自焊件接口** ⇒ `CreateDefinition(118)` 返回的对象
#   **不是那个接口** ⇒ **对任何成员都没反应**（真机实测：连**读**都读不到，
#   `read Thickness → ✗ <unknown>.Thickness`），表现为
#   `Property '<unknown>.Thickness' can not be set`。
#
#   **⇒ 修法：改用 SM 接口的成员名。字段映射：**
#     `spec.thickness`          → `GussetThickness`
#     `spec.profile_distance_1` → `ProfileHeightDim`
#     `spec.profile_distance_2` → `ProfileLengthDim`
#     `spec.profile_angle`      → `ProfileAngleDim`
#
#  ⚠ **`ProfileType` 是两个接口的**共有成员** ⇒ 不动它（本函数原也没设它）。
#  ⚠ 字段语义：`GussetSpec` 的 docstring 说「长度单位为米、角度为度」——
#    与 SM 接口的 `ProfileHeightDim` / `ProfileLengthDim` / `ProfileAngleDim` 对齐，
#    **不额外换算**（MCP 层已在边界做过 mm→m）。
#
# 官方签名依据: `ISMGussetFeatureData.GussetThickness {get; set}` 等 4 个属性
#         （`C:\\swapi\\types\\ISMGussetFeatureData\\*.md`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SM = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sheet_metal.py")

OLD = """    def _apply(data):
        # ⚠⚠ 真机实测（2026-10-01）：`Thickness` **确实**是 `IGussetFeatureData` 的成员
        #   （19 个成员里有），但设不上 —— 报 `Property '<unknown>.Thickness' can not be set`。
        #   **曾试过先 `AccessSelections`，三种 `Component` 形式全失败**
        #   （`None`/`_empty_callout()`/`False` → `'类型不匹配'` 或 `'服务器出现意外情况'`），
        #   且官方文档说它是「取得描述**该特征**的选区」= **编辑**用，不是创建用。
        #   **⇒ 正确创建路径**尚未查明；见 `SHEET_METAL_RUNTIME_STATUS`。
        data.Thickness = float(spec.thickness)
        data.ProfileDistance1 = float(spec.profile_distance_1)
        data.ProfileDistance2 = float(spec.profile_distance_2)
        data.ProfileAngle = float(spec.profile_angle)"""

NEW = """    def _apply(data):
        # ⚠⚠⚠ **完整根因（2026-10-01 真机 + 官方类型表确证）**：
        #   本函数创建的是 **钣金**加强筋（`swFmSMGusset=118`，枚举描述明写
        #   "**Sheet metal** gusset"），其特征数据接口是
        #   **`ISMGussetFeatureData`**（`category: Feature Interfaces/Sheet metal`，
        #   28 个属性）；而**原代码用的是 `IGussetFeatureData`** ——
        #   那是 **`Feature Interfaces/Weldments`**（焊件）的接口（19 个成员）。
        #
        #   **两个接口共有成员只有 3 个**（`AccessSelections` / `ProfileType` /
        #   `ReleaseSelectionAccess`）⇒ 原设的 4 个属性名**全部来自焊件接口**
        #   ⇒ 拿到的对象**不是那个接口** ⇒ **对任何成员都没反应**
        #   （真机实测：连**读**都读不到），表现为
        #   `Property '<unknown>.Thickness' can not be set`。
        #
        #   **⇒ 改名为 SM 接口的成员**（映射见下），长度/角度语义不变。
        data.GussetThickness = float(spec.thickness)          # 原 Thickness（焊件名）
        data.ProfileHeightDim = float(spec.profile_distance_1)   # 原 ProfileDistance1
        data.ProfileLengthDim = float(spec.profile_distance_2)   # 原 ProfileDistance2
        data.ProfileAngleDim = float(spec.profile_angle)         # 原 ProfileAngle"""


def main() -> int:
    t = SM.read_text(encoding="utf-8")
    if OLD not in t:
        print("  ✗ 未匹配 create_gusset 的 _apply")
        return 1
    t = t.replace(OLD, NEW, 1)
    SM.write_text(t, encoding="utf-8")
    print("  ✓ create_gusset 已改用 ISMGussetFeatureData 的成员名")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
