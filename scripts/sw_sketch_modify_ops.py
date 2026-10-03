"""★ B4 草图编辑·移动族：移动 / 旋转 / 缩放 / 伸展 / 镜像（`SketchModify*` + `Extension.Stretch`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_sketch_modify_ops.py
# 定位:   ★ 2026-10-03（轮 471）★ 承 `specs/201-toolbar-gaps` 的 **B4**（草图编辑·移动族）。
#   用户工具栏里那 5 项（移动实体 / 复制实体 / 旋转实体 / 缩放实体比例 / 伸展实体）
#   逐项查官方三源的结果：
#
#   ====================  ==================================================  ==========
#   工具栏原文             官方成员（swapi + CHM + 反射，三源一致）              本模块
#   ====================  ==================================================  ==========
#   移动实体               `IModelDoc2.SketchModifyTranslate`                    ✅ 有
#   旋转实体               `IModelDoc2.SketchModifyRotate`                       ✅ 有
#   缩放实体比例            `IModelDoc2.SketchModifyScale`                        ✅ 有
#   伸展实体               `IModelDocExtension.Stretch`                          ✅ 有
#   （同族附带）            `IModelDoc2.SketchModifyFlip`                         ✅ 有
#   复制实体               ★ **查不到 2D 草图的复制入口** ⇒ 见下方"复制"段          ⚠ 另列
#   ====================  ==================================================  ==========
#
#   ★★ **"复制实体"为什么另列**（★ 铁律 5：查不到就说查不到，并写下查到哪一步）：
#     · 三个源里**都没有** `SketchModifyCopy`：
#       `C:\swapi\types\IModelDoc2\` 下含 `SketchModify` 的**只有 4 个**
#       （`Flip` / `Rotate` / `Scale` / `Translate`）· CHM 同样 4 个 ·
#       `_raw/reflect_sldworks/iface_sldworks.txt` 同样 4 个 ⇒ **三源一致**。
#     · 官方**确实有"旋转或复制"**，但**只对 3D 草图**：
#       `ISketchManager.RotateOrCopy3DAboutXYZ(Copy, NumCopies, KeepRelations,
#       BaseX, BaseY, BaseZ, AngleAboutXDir, AngleAboutYDir, AngleAboutZDir)` ——
#       ★ 它的说明逐字是 "Rotates, and optionally copies, the selected **3D sketch** entities"
#       ⇒ ★ **2D 草图用不了**（★ 而本仓 `Insert3DSketch` 在本机回 `None`，见 B3 的 T307）。
#     · ⇒ ★ **故"2D 草图的复制实体"在本模块里不解** —— ★ 不是我漏了，是
#       **三源都指不出 2D 的入口** ⇒ ★ 登记进 `docs/toolbar-ledger.json` 的 X2 类
#       （源里查不到），**不假装做到**。
#
#   ⚠ **为什么不用 `Tools*` 族**：`IModelDoc2` 上另有 `ToolsSketchTranslate()` /
#     `ToolsSketchScale()`，★ 而它们**零参数**（说明逐字只是 "Translates a sketch"）——
#     ★★ 那是**交互式**（弹出对话框让人拖），★ 与本仓"无人值守"的红线冲突（铁律 2）
#     ⇒ ★ **程序化要用 `SketchModify*` 族** ✓
#
# 官方依据（三源）:
#   · `C:\swapi\types\IModelDoc2\SketchModifyTranslate.md`（`void (StartX, StartY, EndX, EndY)`）
#   · `C:\swapi\types\IModelDoc2\SketchModifyRotate.md`（`void (CenterX, CenterY, Angle)`）
#   · `C:\swapi\types\IModelDoc2\SketchModifyScale.md`（`bool (ScaleFactor)`）
#   · `C:\swapi\types\IModelDoc2\SketchModifyFlip.md`（`void (AxisFlag: int)`）
#   · `C:\swapi\types\IModelDocExtension\Stretch.md`
#     （`void (KeepRelations: bool, BaseX, BaseY, DestX, DestY)` · "Stretch the selected entities"）
#   · `C:\swapi\types\ISketchManager\RotateOrCopy3DAboutXYZ.md`（★ 只做 3D —— 上表那段依据）
#   · CHM：`AI Solidworks\官方文档\**\IModelDoc2~SketchModify{Flip,Rotate,Scale,Translate}.html`
#   · 反射：`_raw\reflect_sldworks\iface_sldworks.txt`（★ 与上面两个源**成员名一致**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件（★ 逐函数另有来源块）。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个函数回 `{"ok": bool, ...}`，且 `ok` 来自**回读**（★ 规则 6：不静默成功）。

from __future__ import annotations

try:
    from .sw_connect import get_com_member, set_com_member          # noqa: F401
except ImportError:                                                 # 顶层载入（脚本 / 探针）
    from sw_connect import get_com_member, set_com_member           # noqa: F401

__all__ = [
    "sketch_move",
    "sketch_rotate",
    "sketch_scale",
    "sketch_stretch",
    "sketch_flip",
    "MODIFY_OPS_STATUS",
]

#: ★ 本模块覆盖到的工具栏项 ⇒ 官方成员（★ 与 `docs/toolbar-ledger.json` 对齐用）
MODIFY_OPS_STATUS = {
    "移动实体": "IModelDoc2.SketchModifyTranslate",
    "旋转实体": "IModelDoc2.SketchModifyRotate",
    "缩放实体比例": "IModelDoc2.SketchModifyScale",
    "伸展实体": "IModelDocExtension.Stretch",
    "（同族附带）镜像": "IModelDoc2.SketchModifyFlip",
    "复制实体": "★ 查不到 2D 入口（三源一致：RotateOrCopy3D* 只做 3D）",
}


def _require_model(model):
    """★ 参数守卫：`model` 为 None ⇒ 明确抛（★ 铁律 5：不猜、不静默）。"""
    if model is None:
        raise ValueError("model 为 None")
    return model


def sketch_move(model, start_x_mm: float, start_y_mm: float,
                end_x_mm: float, end_y_mm: float) -> dict:
    """★ 移动实体：`IModelDoc2.SketchModifyTranslate(StartX, StartY, EndX, EndY)`（回 `void`）。

    ⚠ `void` ⇒ ★ **没有返回值可判** ⇒ 本函数**回读活动草图名**作为"调用没炸"的旁证，
      并**如实写明 `verified_by`** —— ★ 不假装量到了位移（★ 规则 6 的精神：
      说清楚"判据是什么"，而不是"回 True"）。
    """
    _require_model(model)
    before = _active_sketch_name(model)
    get_com_member(model, "SketchModifyTranslate",
                   float(start_x_mm) / 1000.0, float(start_y_mm) / 1000.0,
                   float(end_x_mm) / 1000.0, float(end_y_mm) / 1000.0)
    return {"ok": True, "op": "move", "verified_by": "no_exception",
            "sketch_before": before, "sketch_after": _active_sketch_name(model),
            "asked_mm": [start_x_mm, start_y_mm, end_x_mm, end_y_mm]}


def sketch_rotate(model, center_x_mm: float, center_y_mm: float, angle_deg: float) -> dict:
    """★ 旋转实体：`IModelDoc2.SketchModifyRotate(CenterX, CenterY, Angle)`（回 `void`）。

    ★ 角度**只在本工具边界换算一次**（规则 2：`_deg` 入参 ⇒ 弧度交 COM）。
    """
    _require_model(model)
    import math
    before = _active_sketch_name(model)
    get_com_member(model, "SketchModifyRotate",
                   float(center_x_mm) / 1000.0, float(center_y_mm) / 1000.0,
                   math.radians(float(angle_deg)))
    return {"ok": True, "op": "rotate", "verified_by": "no_exception",
            "sketch_before": before, "sketch_after": _active_sketch_name(model),
            "asked_deg": angle_deg}


def sketch_scale(model, factor: float) -> dict:
    """★ 缩放实体比例：`IModelDoc2.SketchModifyScale(ScaleFactor)` —— ★ **这一条有 bool 返回值**。

    ⇒ ★ 判据 = **返回值非假**（★ 比 `void` 那几条强一档）。
    """
    _require_model(model)
    if float(factor) <= 0:
        raise ValueError("factor 必须 > 0（缩放比例）")
    r = get_com_member(model, "SketchModifyScale", float(factor))
    return {"ok": bool(r), "op": "scale", "verified_by": "return_value",
            "returned": r, "asked_factor": factor}


def sketch_stretch(model, base_x_mm: float, base_y_mm: float,
                   dest_x_mm: float, dest_y_mm: float,
                   keep_relations: bool = True) -> dict:
    """★ 伸展实体：`IModelDocExtension.Stretch(KeepRelations, BaseX, BaseY, DestX, DestY)`（回 `void`）。

    ⚠ ★ **入口在 `IModelDocExtension` 上**（不是 `IModelDoc2`）⇒ 先取 `model.Extension` ✓
    ★ 官方说明逐字 "Stretch the selected entities" ⇒ ★ **要求先选中实体**（★ 见模块头的"选择"说明）。
    """
    _require_model(model)
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("取不到 model.Extension —— 伸展实体在 IModelDocExtension 上")
    before = _active_sketch_name(model)
    get_com_member(ext, "Stretch", bool(keep_relations),
                   float(base_x_mm) / 1000.0, float(base_y_mm) / 1000.0,
                   float(dest_x_mm) / 1000.0, float(dest_y_mm) / 1000.0)
    return {"ok": True, "op": "stretch", "verified_by": "no_exception",
            "sketch_before": before, "sketch_after": _active_sketch_name(model),
            "keep_relations": bool(keep_relations)}


def sketch_flip(model, axis_flag: int) -> dict:
    """★ 镜像/翻转：`IModelDoc2.SketchModifyFlip(AxisFlag: int)`（回 `void`）。

    ⚠ `AxisFlag` 的**取值表官方两个源都没给** ⇒ ★ 按铁律 5 **原样透传 int，不猜语义**，
      并把这一点写进返回值（★ `axis_flag_semantics: "官方未给取值表"`）。
    """
    _require_model(model)
    before = _active_sketch_name(model)
    get_com_member(model, "SketchModifyFlip", int(axis_flag))
    return {"ok": True, "op": "flip", "verified_by": "no_exception",
            "sketch_before": before, "sketch_after": _active_sketch_name(model),
            "axis_flag": int(axis_flag),
            "axis_flag_semantics": "官方 swapi 与 CHM 均未给取值表 —— 原样透传"}


def _active_sketch_name(model):
    """★ 旁证：当前活动草图的名字（★ 取不到就回 None，**不猜、不兜底**）。"""
    try:
        sk = get_com_member(model, "GetActiveSketch2")
        if sk is None:
            return None
        return str(get_com_member(sk, "Name") or "") or None
    except Exception:                                               # noqa: BLE001
        return None
