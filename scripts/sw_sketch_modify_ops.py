"""★ B4 草图编辑·移动族：移动 / 旋转 / 缩放 / 伸展 / 镜像（`SketchModify*` + `Extension.Stretch`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_sketch_modify_ops.py
# 定位:   ★ 2026-10-03（轮 471）★ 承 `specs/201-toolbar-gaps` 的 **B4**（草图编辑·移动
#           族）。
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
# · `C:\swapi\types\IModelDoc2\SketchModifyTranslate.md`（`void (StartX, StartY, EndX, E
# ndY)`）
# · `C:\swapi\types\IModelDoc2\SketchModifyRotate.md`（`void (CenterX, CenterY, Angle)`
# ）
#   · `C:\swapi\types\IModelDoc2\SketchModifyScale.md`（`bool (ScaleFactor)`）
#   · `C:\swapi\types\IModelDoc2\SketchModifyFlip.md`（`void (AxisFlag: int)`）
#   · `C:\swapi\types\IModelDocExtension\Stretch.md`
# （`void (KeepRelations: bool, BaseX, BaseY, DestX, DestY)` · "Stretch the selected ent
# ities"）
# · `C:\swapi\types\ISketchManager\RotateOrCopy3DAboutXYZ.md`（★ 只做 3D —— 上表那段依据
# ）
# · CHM：`AI Solidworks\官方文档\**\IModelDoc2~SketchModify{Flip,Rotate,Scale,Translate}
# .html`
#   · 反射：`_raw\reflect_sldworks\iface_sldworks.txt`（★ 与上面两个源**成员名一致**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件（★ 逐函数另有来源块）。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个函数回 `{"ok": bool, ...}`，且 `ok` 来自**回读**（★ 规则 6：不静默成功）
# 。

from __future__ import annotations

from pathlib import Path as _Path

#: ★★ 本仓库 `scripts/` 的绝对路径（★ 供两个取样助手**按顶层路径** import `sw_sketch`）✓
_REPO_SCRIPTS = _Path(__file__).resolve().parent

try:
    from .sw_connect import get_com_member, set_com_member  # noqa: F401
except ImportError:  # 顶层载入（脚本 / 探针）
    from sw_connect import get_com_member, set_com_member  # noqa: F401

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


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 复用本仓既有读法，★ 不发明）
# 文件:   `scripts/sw_sketch.py::get_lines` · `get_arcs` · `get_model_to_sketch_transfor
# m`
# 定位:   ★★★★ 2026-10-04（接手轮）**新增两个取样助手** —— ★ 处置 `JUDGE-C_D_E.md` 的
# 🔴 #1 · **E5-1**（★ 裁判逐字：「★ 仓内 doc：`★ 判据 = ModelToSketchTransform.ArrayData
#  的
#   平移分量变化` ／ 改几何的 ⇒ `判据 = 草图线段端点的 bbox 变没变` · ★ 而目标：
#   `return {"ok": True, "op": "move", "verified_by": "no_exception", …}` ／
# ★★ **`ModelToSketchTransform` 与 `ArrayData` 在该文件各 0 次**」· ★ 判定「**确认**」）
# ✓
# ★★★ **病灶**：★ 本文件头 L54 逐字承诺「★ 每个函数回 `{"ok": bool, …}`，★ 且 `ok` **来
# 自回读**」
#     ★★ 而 `sketch_move` / `sketch_rotate` / `sketch_stretch` / `sketch_flip` 四处逐字都写
#       `"ok": True, … "verified_by": "no_exception"` ⇒ ★★★★ **"没抛异常"当成了"做成了"** ✓
#     ★ （★ 那四处的 docstring **自己承认**判据弱 —— ★ 但**结果仍是无条件 `True`**，
#        ★★ 所以规则 6 要的"不静默成功"**没有兑现** ✓）
#   ⇒ 修法：★ **把 doc 承诺的两个判据都实现**（★ 而**两个都有现成读法**，★ 不用发明）：
# · ★ **`_sketch_bbox_mm(model)`** —— ★ 从 `get_lines` / `get_arcs` 的坐标算**端点 bbox*
# * ✓
# · ★★ **`_sketch_transform_translation(model)`** —— ★ 从 `get_model_to_sketch_transform
# `
#       取**平移分量** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def _sketch_bbox_mm(model):
    """★ 活动草图里**所有线段/圆弧端点**的轴对齐包围盒（★ 毫米；★ 取不到 ⇒ `None`）。

    ★ 这实现的是 doc 承诺的**第二个判据**（★「改几何的 ⇒ 判据 = 草图线段端点的 bbox 变没变」）✓
    ★★ **不发明读法**：★ 直接复用 `sw_sketch.get_lines` / `get_arcs` —— 它们回**坐标数组** ✓
    ⚠ 取不到就回 `None`（★ 而那**不是** `ok` —— ★ 见调用处的三态处理）✓
    """
    try:
        import sys as _sys

        if str(_REPO_SCRIPTS) not in _sys.path:
            _sys.path.insert(0, str(_REPO_SCRIPTS))
        from sw_sketch import get_arcs, get_lines  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        return None
    xs, ys = [], []
    try:
        #: ★ `get_lines` 每 12 个 float 一条线（★ 见 `sw_sketch.ELEMS_PER_LINE`）
        for i in range(0, len(get_lines(model) or []) - 11, 12):
            row = get_lines(model)[i : i + 12]
            xs += [float(row[0]), float(row[3])]
            ys += [float(row[1]), float(row[4])]
    except Exception:  # noqa: BLE001
        pass
    try:
        for i in range(0, len(get_arcs(model) or []) - 15, 16):
            row = get_arcs(model)[i : i + 16]
            xs += [float(row[0])]
            ys += [float(row[1])]
    except Exception:  # noqa: BLE001
        pass
    if not xs or not ys:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def _sketch_transform_translation(model):
    """★ `ModelToSketchTransform.ArrayData` 的**平移分量**（★ 毫米 `[tx, ty, tz]`；取不到 ⇒ `None`）。

    ★ 这实现的是 doc 承诺的**第一个判据**（★「判据 = `ModelToSketchTransform.ArrayData`
    的**平移分量变化**」）✓
    ★★ 复用 `sw_sketch.get_model_to_sketch_transform`（★ 本仓既有读法）✓
    ★ 官方 `IMathTransform.ArrayData` 是 **16 个 double**（★ 4×4 行主序）⇒ ★ 平移在 **[9][10][11]** ✓
    """
    try:
        import sys as _sys

        if str(_REPO_SCRIPTS) not in _sys.path:
            _sys.path.insert(0, str(_REPO_SCRIPTS))
        from sw_sketch import get_model_to_sketch_transform  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        return None
    try:
        data = get_model_to_sketch_transform(model)
        if data is None:
            return None
        seq = list(data)
        if len(seq) < 12:
            return None
        return [float(seq[9]), float(seq[10]), float(seq[11])]
    except Exception:  # noqa: BLE001
        return None


def _moved(before, after) -> "bool | None":
    """★ 三态：★ **变了 `True`** · ★ **没变 `False`** · ★★ **取不到 `None`**（★ 不许当成"变了"）。

    ★★★ 为什么必须三态（★ 本条的关键）：★ 若把"取不到"当成"变了"，
    那就**又回到了 `ok: True` 无条件**那个病灶 ✓
    """
    if before is None or after is None:
        return None
    return bool(before != after)


def _geom_evidence(model, before_bbox, before_tf) -> dict:
    """★ 把两个量在**调用后**取一次，★ 并按三态给 `ok`（★ 与 `verified_by`）✓。"""
    after_bbox = _sketch_bbox_mm(model)
    after_tf = _sketch_transform_translation(model)
    bbox_moved = _moved(before_bbox, after_bbox)
    tf_moved = _moved(before_tf, after_tf)
    #: ★★ `ok` 的判据：★ **两个量里至少一个明确变了**；
    #: ★★★ 而"两个都取不到"（★ `None`）⇒ ★ **`ok=None`**（★ 如实说"量不到"，★ **不报成功
    #: **）✓
    if bbox_moved is None and tf_moved is None:
        ok = None
    else:
        ok = bool(bbox_moved) or bool(tf_moved)
    return {
        "ok": ok,
        "bbox_before_mm": before_bbox,
        "bbox_after_mm": after_bbox,
        "bbox_moved": bbox_moved,
        "transform_before": before_tf,
        "transform_after": after_tf,
        "transform_translation_moved": tf_moved,
        "verified_by": (
            "★ 草图段端点 bbox 变化 **或** ModelToSketchTransform.ArrayData "
            "平移分量变化（★ doc 承诺的两个判据；★ 取不到时 ok 为 None，不报成功）"
        ),
    }


def sketch_move(
    model, start_x_mm: float, start_y_mm: float, end_x_mm: float, end_y_mm: float
) -> dict:
    """★ 移动实体：`IModelDoc2.SketchModifyTranslate(StartX, StartY, EndX, EndY)`（回 `void`）。

    ⚠ `void` ⇒ ★ **没有返回值可判** ⇒ 本函数**回读活动草图名**作为"调用没炸"的旁证，
      并**如实写明 `verified_by`** —— ★ 不假装量到了位移（★ 规则 6 的精神：
      说清楚"判据是什么"，而不是"回 True"）。
    """
    _require_model(model)
    before = _active_sketch_name(model)
    before_bbox = _sketch_bbox_mm(model)
    before_tf = _sketch_transform_translation(model)
    get_com_member(
        model,
        "SketchModifyTranslate",
        float(start_x_mm) / 1000.0,
        float(start_y_mm) / 1000.0,
        float(end_x_mm) / 1000.0,
        float(end_y_mm) / 1000.0,
    )
    out = {
        "op": "move",
        "sketch_before": before,
        "sketch_after": _active_sketch_name(model),
        "asked_mm": [start_x_mm, start_y_mm, end_x_mm, end_y_mm],
    }
    #: ★★★★ 2026-10-04（接手轮）**改成 doc 承诺的判据**（★ 原来是 `"ok": True` + `no_exc
    #: eption`）✓
    out.update(_geom_evidence(model, before_bbox, before_tf))
    return out


def sketch_rotate(
    model, center_x_mm: float, center_y_mm: float, angle_deg: float
) -> dict:
    """★ 旋转实体：`IModelDoc2.SketchModifyRotate(CenterX, CenterY, Angle)`（回 `void`）。

    ★ 角度**只在本工具边界换算一次**（规则 2：`_deg` 入参 ⇒ 弧度交 COM）。
    """
    _require_model(model)
    import math

    before = _active_sketch_name(model)
    before_bbox = _sketch_bbox_mm(model)
    before_tf = _sketch_transform_translation(model)
    get_com_member(
        model,
        "SketchModifyRotate",
        float(center_x_mm) / 1000.0,
        float(center_y_mm) / 1000.0,
        math.radians(float(angle_deg)),
    )
    out = {
        "op": "rotate",
        "sketch_before": before,
        "sketch_after": _active_sketch_name(model),
        "asked_deg": angle_deg,
    }
    out.update(_geom_evidence(model, before_bbox, before_tf))  #: ★ doc 承诺的判据
    return out


def sketch_scale(model, factor: float) -> dict:
    """★ 缩放实体比例：`IModelDoc2.SketchModifyScale(ScaleFactor)` —— ★ **这一条有 bool 返回值**。

    ⇒ ★ 判据 = **返回值非假**（★ 比 `void` 那几条强一档）。
    """
    _require_model(model)
    if float(factor) <= 0:
        raise ValueError("factor 必须 > 0（缩放比例）")
    before_bbox = _sketch_bbox_mm(model)
    before_tf = _sketch_transform_translation(model)
    r = get_com_member(model, "SketchModifyScale", float(factor))
    out = {"op": "scale", "returned": r, "asked_factor": factor}
    #: ★★★ 2026-10-04（接手轮）：★ 保留官方的 `bool` 返回值判据（★ 它比 `void` 那几条强
    #: ），
    #: ★★ **并叠加** doc 承诺的几何判据 ⇒ ★ 两者**都要**成立才算 `ok`（★ 跨种类 ⇒ `and`
    #: ）✓
    geom = _geom_evidence(model, before_bbox, before_tf)
    out.update(geom)
    out["ok"] = bool(bool(r) and geom["ok"] is True)
    out["verified_by"] = "★ `SketchModifyScale` 回非假 **且** " + str(
        geom["verified_by"]
    )
    return out


def sketch_stretch(
    model,
    base_x_mm: float,
    base_y_mm: float,
    dest_x_mm: float,
    dest_y_mm: float,
    keep_relations: bool = True,
    select_all: bool = True,
) -> dict:
    """★ 伸展实体：`IModelDocExtension.Stretch(KeepRelations, BaseX, BaseY, DestX, DestY)`（回 `void`）。

    ⚠ ★ **入口在 `IModelDocExtension` 上**（不是 `IModelDoc2`）⇒ 先取 `model.Extension` ✓
    ★ 官方说明逐字 "Stretch the selected entities" ⇒ ★ **要求先选中实体**（★ 见模块头的"选择"说明）。

    ★★ 2026-10-07（接手轮 · 规格 216 T-216-07）**加 `select_all`：自己把活动草图的段选上** ——
      ★ 起因：★ 上面那句"要求先选中"就是**官方前置**，★ 而**注入解析器会清空选区**（**事实 503**）
        ⇒ ★ 模型**没有任何办法**在调工具前选好 ⇒ ★ 缺选区时它**几乎不动**（★ 台账逐字：
        「变化很小（±20 → -19.997/20.003），★ 与「没选中时只有极小效应」一致」）✗
      ★ `select_all=True`（缺省）⇒ ★ 先把**活动草图的全部段**选上（★ = "伸展整张草图"）✓
        ★ 置 `False` ⇒ ★ 保持原样（★ 依赖调用方已选 —— ★ 而经 MCP 通常为空）✓
      ★ 实现见 :func:`select_active_sketch_segments`（★ 用官方 `GetSketchSegments` + `Select4`）✓
    """
    _require_model(model)
    #: ★★★ 先建选区（★ 必须紧贴 `Stretch` 之前 —— ★ 中间隔别的步骤会把选区清掉）✓
    selected = None
    if select_all:
        selected = select_active_sketch_segments(model)
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("取不到 model.Extension —— 伸展实体在 IModelDocExtension 上")
    before = _active_sketch_name(model)
    before_bbox = _sketch_bbox_mm(model)
    before_tf = _sketch_transform_translation(model)
    get_com_member(
        ext,
        "Stretch",
        bool(keep_relations),
        float(base_x_mm) / 1000.0,
        float(base_y_mm) / 1000.0,
        float(dest_x_mm) / 1000.0,
        float(dest_y_mm) / 1000.0,
    )
    out = {
        "op": "stretch",
        #: ★ 2026-10-07：把"选了多少段"**带进报告** —— ★ 它同时是**前置成立与否**的读
        #: 数 ✓
        "selected_count": selected,
        "select_all": bool(select_all),
        "sketch_before": before,
        "sketch_after": _active_sketch_name(model),
        "keep_relations": bool(keep_relations),
    }
    out.update(_geom_evidence(model, before_bbox, before_tf))  #: ★ doc 承诺的判据
    return out


def sketch_flip(model, axis_flag: int) -> dict:
    """★ 镜像/翻转：`IModelDoc2.SketchModifyFlip(AxisFlag: int)`（回 `void`）。

    ⚠ `AxisFlag` 的**取值表官方两个源都没给** ⇒ ★ 按铁律 5 **原样透传 int，不猜语义**，
      并把这一点写进返回值（★ `axis_flag_semantics: "官方未给取值表"`）。
    """
    _require_model(model)
    before = _active_sketch_name(model)
    before_bbox = _sketch_bbox_mm(model)
    before_tf = _sketch_transform_translation(model)
    get_com_member(model, "SketchModifyFlip", int(axis_flag))
    out = {
        "op": "flip",
        "sketch_before": before,
        "sketch_after": _active_sketch_name(model),
        "axis_flag": int(axis_flag),
        "axis_flag_semantics": "官方 swapi 与 CHM 均未给取值表 —— 原样透传",
    }
    out.update(_geom_evidence(model, before_bbox, before_tf))  #: ★ doc 承诺的判据
    return out


def select_active_sketch_segments(model, indices=None) -> int:
    """★ 选中**活动草图**里的段 —— 供 `Stretch the **selected** entities` 这类前置用。

    ★★ 2026-10-07（接手轮 · 规格 216 T-216-07）**为什么要它**：
      ★ `IModelDocExtension.Stretch` 的官方说明逐字是 "Stretch the **selected** entities"
        ⇒ ★ 缺选区时它**几乎不动**（★ 台账 `sketch_modify_ops` 逐字：「本次真机测到的变化很小
        （±20 → -19.997/20.003），★ 与「没选中时只有极小效应」一致」）✓
      ★★ 而**注入解析器会清空选区**（**事实 503**）⇒ ★ 模型**没有任何办法**在调工具前选好 ✗
      ★ 为什么不用 `resolve_selection`：★ 它只认 `FACE` / `EDGE` / `VERTEX`（★ 体上的实体），
        ★★ **草图段不在其列**（★ 草图段也没有名字 —— 事实 32）⇒ ★ 换用官方
        **`ISketch::GetSketchSegments()`**（零参）+ **`ISketchSegment::Select4(Append, Data)`** ✓
      ★ 「选哪个」的语义：★ `indices=None` ⇒ **全选**（= "伸展整张草图"）；★ 给了序号就按序号选 ✓
    :returns: ★ **回读**到的选区计数（★ 0 会抛 —— ★ 事实 8：不信返回值）✓
    """
    import sw_selection_spec as _SS
    from sw_connect import get_com_member as _get
    from sw_sketch import active_sketch

    sketch = active_sketch(model)
    if sketch is None:
        raise RuntimeError(
            "★ 没有活动草图 ⇒ ★ 先开一张草图的编辑态（★ 与「伸展不出效果」是两件事）"
        )
    segs = list(_get(sketch, "GetSketchSegments") or [])
    if not segs:
        raise RuntimeError("★ 活动草图里没有段（`GetSketchSegments()` 回了空）")
    pick = segs if indices is None else [segs[int(i)] for i in indices]
    got = 0
    for i, seg in enumerate(pick):
        got = _SS.select_object(model, seg, append=(i > 0))
    if int(got) <= 0:
        raise RuntimeError("★ 选草图段未成立：回读计数为 0（★ 事实 8：判据只有回读）")
    return int(got)


def _active_sketch_name(model):
    """★ 旁证：当前活动草图的名字（★ 取不到就回 None，**不猜、不兜底**）。

    ★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 `get_com_member(model, "GetActiveSketch2")`。
      ★ 官方 `IModelDoc2/GetActiveSketch2.md` 逐字：
        「**Obsolete. Superseded by [[ISketchManager::ActiveSketch]].**」
      ★★ 真机已验证两者行为等价（`output/activesketch-successor-evidence.json` · PASS）。
      ★ 共用帮手：`scripts/sw_sketch.py::active_sketch`（★ 事实 60 定则④）。
    """
    try:
        from sw_sketch import active_sketch as _active_sketch

        sk = _active_sketch(model)
        if sk is None:
            return None
        return str(get_com_member(sk, "Name") or "") or None
    except Exception:  # noqa: BLE001
        return None
