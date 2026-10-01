"""修 `sw_sheet_metal.py` 那 4 个真机失败的函数（根因已从**官方源**确认）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 成员表（`C:\\swapi\\types\\I*FeatureData\\`）+ 真机实测
# 文件:   `IEdgeFlangeFeatureData`（43 个成员）· `IGussetFeatureData`（19）
#         `IDraftFeatureData2`（25）· `IOneBendFeatureData`（34）
# 定位:   2026-10-01 真机验收发现的**两个根因**，各有**官方依据**：
#
#   **根因 ①（跨接口属性泄漏）**：`create_edge_flange` 设了 `data.ReverseDirection`，
#      而 `IEdgeFlangeFeatureData` 的 43 个成员里**没有它** ——
#      它是 **`IDraftFeatureData2`** 的成员（25 个成员里有）。
#      **⇒ 作者把「拔模」接口的属性抄到了「边法兰」代码里。**
#      真机表现：`Property '<unknown>.ReverseDirection' can not be set`。
#      **⇒ 修法：删掉该行**（边法兰没有「反向」这个语义；最接近的是 `ReverseOffset`
#      / `ReversePositionOffset`，那是**偏置**方向，不是法兰方向，**不臆造替代**）。
#
#   **根因 ②（缺 `AccessSelections` 配对）**：`create_gusset` / `create_draft` /
#      `create_edge_flange` 都在**没调** `AccessSelections` 的情况下设属性。
#      而这三个接口**都有** `AccessSelections(...)` / `ReleaseSelectionAccess()`，
#      且 `_create_from_definition` 的**自己的文档串**就写着
#      「边/面引用类特征须在其内部自行配对 AccessSelections / ReleaseSelectionAccess」。
#      **⇒ 修法：在 `_apply` 里先 `AccessSelections(model, None)`，建完再 release。**
#
#  ⚠ **关于 `create_one_bend` / `create_draft` 的 `CreateDefinition(33/3)` 返回 None**：
#    枚举值**经反射核实是对的**（`swFmDraft=3` / `swFmOneBend=33`）。
#    **⇒ 真因本轮**未查明**（可能是这些类型不通过 `CreateDefinition` 暴露，
#    而要专用 `IFeatureManager.Insert*` —— 反射里有 `InsertSheetMetal3dBend` /
#    `InsertGussetFeature3` / `IInsertSheetMetalEdgeFlange2`）。
#    **⇒ 不猜、不硬改**；维持「已知不可用」状态，留给后续。
#
# 官方签名依据: `AccessSelections(System.object TopDoc, System.object Component) -> System.bool`
#         （`C:\\swapi\\types\\IEdgeFlangeFeatureData\\AccessSelections.md` 等，四个接口同形）
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

# 根因 ①：删掉不存在的属性
OLD_EF = """    def _apply(data):
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        data.ReverseDirection = bool(spec.reverse_direction)
        data.UseDefaultBendAllowance = True

    return _create_from_definition(model, SW_FM_EDGE_FLANGE, _apply)"""
NEW_EF = """    def _apply(data):
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        # ⛔ 原代码在此设 `data.ReverseDirection` —— **该属性不属于本接口**。
        #    `IEdgeFlangeFeatureData` 的 43 个成员里没有它；
        #    它是 `IDraftFeatureData2`（拔模）的成员（**跨接口属性泄漏**）。
        #    真机表现：`Property '<unknown>.ReverseDirection' can not be set`。
        #    ⚠ **不臆造替代**：最接近的 `ReverseOffset` / `ReversePositionOffset`
        #    是**偏置**方向，语义不同 —— 边法兰没有「反向」这个开关。
        #    见 `C:\\swapi\\types\\IEdgeFlangeFeatureData\\`（43 个成员名）。
        data.UseDefaultBendAllowance = True

    return _create_from_definition(model, SW_FM_EDGE_FLANGE, _apply)"""

# 根因 ②：AccessSelections 配对（三个函数）
OLD_GU = """    def _apply(data):
        data.Thickness = float(spec.thickness)"""
NEW_GU = """    def _apply(data):
        # ⚠ 必须先 `AccessSelections` 才能设属性 —— 这三个接口的成员表里都有它，
        #   且本文件 `_create_from_definition` 的文档串就写着「边/面引用类特征
        #   须在其内部自行配对 AccessSelections / ReleaseSelectionAccess」。
        #   **原代码漏了这一步** ⇒ 真机报 `Property '<unknown>.Thickness' can not be set`。
        _access_selections(data, model)
        data.Thickness = float(spec.thickness)"""

OLD_DR = """    def _apply(data):
        data.Angle = float(spec.angle)
        data.ReverseDirection = bool(spec.reverse_direction)"""
NEW_DR = """    def _apply(data):
        # ⚠ 同 `create_gusset`：`IDraftFeatureData2` 有 `AccessSelections`，必须先调。
        _access_selections(data, model)
        data.Angle = float(spec.angle)
        # ⚠ `ReverseDirection` **是** `IDraftFeatureData2` 的成员（这里用对了）；
        #   注意它**不是** `IEdgeFlangeFeatureData` 的成员 —— 见 `create_edge_flange` 的注释。
        data.ReverseDirection = bool(spec.reverse_direction)"""

HELPER = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 成员表（`C:\\swapi\\types\\I*FeatureData\\`）
# 文件:   `AccessSelections(System.object TopDoc, System.object Component) -> System.bool`
#         —— `IEdgeFlangeFeatureData` / `IGussetFeatureData` / `IDraftFeatureData2`
#            / `IOneBendFeatureData` **四个接口同形**
# 定位:   **边/面引用类特征在设属性前必须先接管选区。**
#  ⚠ 本文件 `_create_from_definition` 的文档串早就写明这一点，
#    但三个调用方都漏了 ⇒ 2026-10-01 真机验收才发现（属性设不上）。
#  ⚠ 容错策略：拿到的 FeatureData 若**没有** `AccessSelections`（纯数据类），跳过即可 ——
#    不是所有 FeatureData 都引用选区。用 `getattr` 试探，**不硬失败**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
#         ↑ 本块说明 `_access_selections` 与 `_release_selection_access` **两个**函数。
#         ⚠ 标记必须写成**裸的** `覆盖: 后续同级定义`（加粗体会让正则匹配不到）。
# ⚠ 本补丁**未在本机实测**（补丁本身）；其正确性由随后的真机复测决定。
# ────────────────────────────────────────────────────────────────────
def _access_selections(data, model) -> bool:
    """设属性**前**接管选区。返回是否真的调用了（纯数据类没有该成员就返回 False）。"""
    access = getattr(data, "AccessSelections", None)
    if not callable(access):
        return False
    try:
        access(model, None)
        return True
    except Exception:      # noqa: BLE001 —— 拿不到选区不算致命，交由 CreateFeature 报错
        return False


def _release_selection_access(data) -> None:
    """建完特征**后**释放选区接管（与 :func:`_access_selections` 配对）。"""
    release = getattr(data, "ReleaseSelectionAccess", None)
    if callable(release):
        try:
            release()
        except Exception:  # noqa: BLE001
            pass
'''


def main() -> int:
    t = SM.read_text(encoding="utf-8")
    missed = []
    for label, old, new in (
        ("根因① 删 edge_flange 的跨接口属性", OLD_EF, NEW_EF),
        ("根因② gusset 加 AccessSelections", OLD_GU, NEW_GU),
        ("根因② draft 加 AccessSelections", OLD_DR, NEW_DR),
    ):
        if old not in t:
            missed.append(label)
            continue
        t = t.replace(old, new, 1)
        print("  ✓ %s" % label)

    # 插入两个 helper（放在 _create_from_definition 之前，便于阅读）
    anchor = "def _create_from_definition(model, fm_type: int, apply_definition):"
    if anchor in t:
        t = t.replace(anchor, HELPER.strip() + "\n\n\n" + anchor, 1)
        print("  ✓ 已插入 _access_selections / _release_selection_access")
    else:
        missed.append("插入 helper")

    # 建完特征后 release（在 _create_from_definition 里）
    old_ret = """    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
    if error_code:
        raise RuntimeError(f"钣金特征 {fm_type} 返回特征错误码: {error_code}")
    return feature"""
    new_ret = """    # ⚠ 与 `_apply` 里的 `AccessSelections` 配对（见 _access_selections 的来源块）
    _release_selection_access(data)
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
    if error_code:
        raise RuntimeError(f"钣金特征 {fm_type} 返回特征错误码: {error_code}")
    return feature"""
    if old_ret in t:
        t = t.replace(old_ret, new_ret, 1)
        print("  ✓ _create_from_definition 建完特征后 release")
    else:
        missed.append("release 配对")

    SM.write_text(t, encoding="utf-8")
    if missed:
        print("  ✗ 未匹配：%r" % missed)
        return 1
    print("  ⇒ 全部命中")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
