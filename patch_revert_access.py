"""撤回**被否证的** `AccessSelections` 修改；保留**已验证为真**的 `ReverseDirection` 修复。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论，非第三方移植）
# 文件:   D:\\AI\\SW\\probe_featuredata_access.py（证据脚本）
# 定位:   2026-10-01 真机把三个层次全测清了：
#
#   **① `CreateDefinition(fm)`**（实测）
#       ✓ 34 BaseFlange / 37 EdgeFlange / 118 Gusset → 非 None
#       ✗ **3 Draft / 33 OneBend → None**（**这两个不走 `CreateDefinition`**）
#       ⇒ 反射里有专用入口：`InsertSheetMetal3dBend` / `IInsertSheetMetalEdgeFlange2`
#         / `InsertGussetFeature3` / `InsertSheetMetalBaseFlange2`（**均存在**）。
#
#   **② `AccessSelections(model, Component)`**（实测，**我的假设被否证**）
#       `Python None`      → `'类型不匹配'`（`TYPE_E_TYPEMISMATCH`）
#       `_empty_callout()` → `'服务器出现意外情况'`（`RPC_E_SERVERFAULT`）
#       `False`            → `'类型不匹配'`
#       **⇒ 三种 `Component` 形式全失败。**
#       官方文档：「Gains access to the selections that **describe this feature**」——
#       那是**编辑已有特征**用的，**不是创建用的**。
#       **⇒ 我上一版把 `AccessSelections` 加进 `_apply` 是**方向错了**，撤回。**
#
#   **③ `ReverseDirection` 的跨接口泄漏**（**已修复且已验证**）
#       `IEdgeFlangeFeatureData`（43 成员）里**没有**它；
#       它是 `IDraftFeatureData2`（25 成员）的成员。
#       删掉那一行后，真机报错**从** `Property ... can not be set`
#       **变成** `CreateFeature(37) 创建失败` ⇒ **属性那一层确实通了**（根因① 确认修好）。
#
#   **⇒ 仍未查明**：`create_gusset` 的 `Thickness` 设不上（在**能**拿到 FeatureData 的情况下）、
#     以及 4 个函数的**正确创建路径**（是否该改用专用 `Insert*` 入口）。
#     **不猜、不硬改** —— 维持「已知不可用」状态。
#
# 官方签名依据: 不适用（本补丁**撤回**改动）
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

# 撤回 gusset 的 AccessSelections
OLD_GU = """    def _apply(data):
        # ⚠ 必须先 `AccessSelections` 才能设属性 —— 这三个接口的成员表里都有它，
        #   且本文件 `_create_from_definition` 的文档串就写着「边/面引用类特征
        #   须在其内部自行配对 AccessSelections / ReleaseSelectionAccess」。
        #   **原代码漏了这一步** ⇒ 真机报 `Property '<unknown>.Thickness' can not be set`。
        _access_selections(data, model)
        data.Thickness = float(spec.thickness)"""
NEW_GU = """    def _apply(data):
        # ⚠⚠ 真机实测（2026-10-01）：`Thickness` **确实**是 `IGussetFeatureData` 的成员
        #   （19 个成员里有），但设不上 —— 报 `Property '<unknown>.Thickness' can not be set`。
        #   **曾试过先 `AccessSelections`，三种 `Component` 形式全失败**
        #   （`None`/`_empty_callout()`/`False` → `'类型不匹配'` 或 `'服务器出现意外情况'`），
        #   且官方文档说它是「取得描述**该特征**的选区」= **编辑**用，不是创建用。
        #   **⇒ 正确创建路径**尚未查明；见 `SHEET_METAL_RUNTIME_STATUS`。
        data.Thickness = float(spec.thickness)"""

OLD_DR = """    def _apply(data):
        # ⚠ 同 `create_gusset`：`IDraftFeatureData2` 有 `AccessSelections`，必须先调。
        _access_selections(data, model)
        data.Angle = float(spec.angle)"""
NEW_DR = """    def _apply(data):
        # ⚠ 本函数甚至**拿不到 FeatureData**：`CreateDefinition(3)` 返回 None
        #   （真机实测；同族里 34/37/118 都正常返回）⇒ **Draft 不走 `CreateDefinition`**。
        #   反射里有专用入口，但本轮**未查明**正确用法 ⇒ 见 `SHEET_METAL_RUNTIME_STATUS`。
        data.Angle = float(spec.angle)"""

# 撤回 helper 调用与 release 配对
OLD_REL = """    # ⚠ 与 `_apply` 里的 `AccessSelections` 配对（见 _access_selections 的来源块）
    _release_selection_access(data)
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)"""
NEW_REL = """    error_code = int(get_com_member(feature, "GetErrorCode") or 0)"""


def main() -> int:
    t = SM.read_text(encoding="utf-8")
    missed = []
    for label, old, new in (
        ("撤回 gusset 的 AccessSelections", OLD_GU, NEW_GU),
        ("撤回 draft 的 AccessSelections", OLD_DR, NEW_DR),
        ("撤回 release 配对", OLD_REL, NEW_REL),
    ):
        if old not in t:
            missed.append(label)
            continue
        t = t.replace(old, new, 1)
        print("  ✓ %s" % label)

    # 删掉两个 helper（连同其来源块）
    start = t.find("# ── 来源 ─────────────────────────────────────────────────────────────\n"
                   "# 仓库:   SolidWorks 官方 API 成员表（`C:\\swapi\\types\\I*FeatureData\\`）")
    if start >= 0:
        end = t.find("def _create_from_definition(model, fm_type: int, apply_definition):", start)
        if end > start:
            t = t[:start] + t[end:]
            print("  ✓ 已删除 _access_selections / _release_selection_access 及其来源块")
    else:
        missed.append("删除 helper")

    SM.write_text(t, encoding="utf-8")
    if missed:
        print("  ✗ 未匹配：%r" % missed)
        return 1
    print("  ⇒ 全部命中（保留了 ReverseDirection 的修复）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
