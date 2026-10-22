"""★ B6 曲面特征（第一组 5 条）：平面区域 / 等距曲面 / 直纹曲面 / 删除面 / 替换面。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_surface_edit_ops.py
# 定位:   ★ 2026-10-03（轮 473）★ 承 `specs/201-toolbar-gaps` 的 **B6**（曲面特征）。
#   用户工具栏「曲面」栏里**判为「不能」**的那 13 条，本模块收**第一组 5 条**：
#
#   ==================  ==============================================  ==================
#   工具栏原文           官方成员（swapi 第一源 + 备注）                    判据
#   ==================  ==============================================  ==================
#   平面区域             `IModelDoc2.InsertPlanarRefSurface()` → **bool**   返回值 + 特征树增量
#   等距曲面             `IModelDoc2.InsertOffsetSurface(Thickness, Reverse)` → void  特征树增量
#   直纹曲面             `IFeatureManager.InsertRuledSurfaceFromEdge2(…)` → Feature   回 Feature + 树增量
#   删除面               `IModelDoc2.InsertDeleteFace2(Refill)` → **bool**  返回值 + 树增量
#   替换面               `IModelDoc2.InsertFeatureReplaceFace()` → void    树增量
#   ==================  ==============================================  ==================
#
#   ★★ **两个"台账给的名字是旧的"**（★ 铁律 5 的正当用法：查不到就换名字再查，查到了要写明）：
#     · 台账写 `InsertRuledSurface` ⇒ ★ **`IModelDoc2` 上没有它**；真名分两处：
#       `IFeatureManager.InsertRuledSurfaceFromEdge`（★ **官方标 Obsolete**）
#       与 **`InsertRuledSurfaceFromEdge2`**（★ 后继版）⇒ ★ **本模块用 `…2`**（铁律 4）
#     · 台账写 `InsertReplaceFace` ⇒ ★ 真名是 **`IModelDoc2.InsertFeatureReplaceFace`** ✓
#
#   ★★★ **两个"要按 mark 选"的**（★ 铁律 3 的第三句：多引用特征读 mark，不读选择顺序）：
#     · 替换面：官方 Remarks 逐字 —— "Before calling this method, **select the faces to replace**
#       by calling `IModelDocExtension::SelectByID2` with **Marks of 1** and 2"
#     · 直纹曲面：官方 Remarks 逐字 —— "If you **select an edge with a selection mark of 4**,
#       the default face is used."
#
#   ⚠ **`InsertRuledSurfaceFromEdge2` 的 `Type` 取值表官方给了**（0..4），本模块**原样透传**并在
#     返回里带上语义 —— ★ 不替调用方收窄（★ 但也不假装知道未列出的值）。
#
# 官方依据（三源）:
#   · `C:\swapi\types\IModelDoc2\InsertPlanarRefSurface.md`（`bool ()`）
#   · `C:\swapi\types\IModelDoc2\InsertOffsetSurface.md`（`void (Thickness: double, Reverse: bool)`）
#   · `C:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge2.md`
#     （11 参 · Type 0..4 · mark 4 的 Remarks）
#   · `C:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge.md`（★ **Obsolete** 那一行）
#   · `C:\swapi\types\IModelDoc2\InsertDeleteFace2.md`（`bool (Refill: int)`）
#   · `C:\swapi\types\IModelDoc2\InsertFeatureReplaceFace.md`（`void ()` + mark 1/2 的 Remarks）
#   · CHM / 反射：见同轮的 `docs/toolbar-ledger.md` 逐条核验
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件（★ 逐函数另有来源块）。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个函数回 `{"ok": …, "verified_by": …}`；★ `ok` 必须来自**特征树增量**或**回读**
#   （★ 规则 6：不静默成功）。

from __future__ import annotations

try:
    from .sw_connect import get_com_member, set_com_member          # noqa: F401
except ImportError:                                                 # 顶层载入（脚本 / 探针）
    from sw_connect import get_com_member, set_com_member           # noqa: F401

__all__ = [
    "insert_planar_surface",
    "insert_offset_surface",
    "insert_ruled_surface",
    "insert_delete_face",
    "insert_replace_face",
    "RULED_TYPE_MEANINGS",
    "SURFACE_EDIT_STATUS",
]

#: ★ 官方给的 `Type` 取值表（★ 逐字来自 `InsertRuledSurfaceFromEdge2.md` 的 Parameters）
RULED_TYPE_MEANINGS = {
    0: "Tangent to Surface",
    1: "Normal to Surface",
    2: "Tapered to Vector",
    3: "Perpendicular to Vector",
    4: "Sweep",
}

#: ★ 本模块覆盖到的工具栏项 ⇒ 官方成员（★ 与 `docs/toolbar-ledger.json` 对齐用）
SURFACE_EDIT_STATUS = {
    "平面区域": "IModelDoc2.InsertPlanarRefSurface",
    "等距曲面": "IModelDoc2.InsertOffsetSurface",
    "直纹曲面": "IFeatureManager.InsertRuledSurfaceFromEdge2",
    "删除面": "IModelDocExtension.InsertDeleteFace",
    "替换面": "IModelDoc2.InsertFeatureReplaceFace",
}


#: ★ 2026-10-22（仓库统一化）：`_tree_names` 原在本文件与另外 3 个模块各有一份（逻辑逐字相同）
#:   ⇒ 收敛到单一实现 `scripts/sw_feature_tree.py`（★ 轮 473 那条教训的完整说明也搬过去了 ✓）
try:
    from .sw_feature_tree import tree_names as _tree_names
except ImportError:
    from sw_feature_tree import tree_names as _tree_names


def _delta(before, after):
    """★ 新增的特征名（★ `None` 表示量不到 ⇒ 判据降级，★ 不猜）。"""
    if before is None or after is None:
        return None
    return [x for x in after if x not in before]


def insert_planar_surface(model) -> dict:
    """★ **平面区域**：`IModelDoc2.InsertPlanarRefSurface()` —— ★ **零参数**，回 `bool`。

    ★ 官方语义：用**当前选中的封闭边界**（草图 / 边）生成一张平面曲面 ⇒ ★ **调用前要选好边界**。
    ★ 判据 = **返回值非假** **且** **特征树有新特征**（★ 两判据都要 —— 返回值单独不可信，事实 8）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    before = _tree_names(model)
    r = get_com_member(model, "InsertPlanarRefSurface")
    after = _tree_names(model)
    added = _delta(before, after)
    return {"ok": bool(r) and bool(added), "op": "planar_surface",
            "returned": r, "tree_before": before, "tree_after": after, "new_features": added,
            "verified_by": "return_value + tree_delta"}


def insert_offset_surface(model, thickness_mm: float, reverse: bool = False) -> dict:
    """★ **等距曲面**：`IModelDoc2.InsertOffsetSurface(Thickness, Reverse)` —— 回 `void`。

    :param thickness_mm: 与参考面的距离（毫米；★ 只在本边界换算成米一次，规则 2）。
    :param reverse: 反向偏移（官方 `Reverse`：True 就反向）。

    ⚠ ★ 官方回 `void` ⇒ ★ 没有返回值可判 ⇒ 判据**只能**靠**特征树增量**（★ 并如实写 `verified_by`）。
    ⚠ ★ 官方没写"要不要先选面"，而语义上要（参考面）；★ 调用方负责先选。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if float(thickness_mm) <= 0:
        return {"ok": False, "error": "thickness_mm 必须 > 0"}
    before = _tree_names(model)
    get_com_member(model, "InsertOffsetSurface", float(thickness_mm) / 1000.0, bool(reverse))
    after = _tree_names(model)
    added = _delta(before, after)
    return {"ok": bool(added), "op": "offset_surface",
            "tree_before": before, "tree_after": after, "new_features": added,
            "asked_mm": thickness_mm, "reverse": bool(reverse),
            "verified_by": "tree_delta"}


def insert_ruled_surface(model, ruled_type: int, length_mm: float = 0.0,
                         flip_pull_dir: bool = False, flip_dir: bool = False,
                         trim_and_sew: bool = True, angle_deg: float = 0.0,
                         coord_input: bool = False, x_mm: float = 0.0,
                         y_mm: float = 0.0, z_mm: float = 0.0,
                         b_connect_surface: bool = False) -> dict:
    """★ **直纹曲面**：`IFeatureManager.InsertRuledSurfaceFromEdge2(…)` —— **11 参**，回 `Feature`。

    ★ 官方 Remarks 逐字：「If you **select an edge with a selection mark of 4**, the default face
      is used.」⇒ ★★ **调用前先把边按 `mark=4` 选中**（铁律 3 第三句）。

    :param ruled_type: 官方的 `Type`（★ 取值表见 `RULED_TYPE_MEANINGS`，本函数**原样透传**）。
    :param length_mm: 距离（毫米）；★ 官方说**只对** Tangent / Tapered / Perpendicular 有效。
    :param angle_deg: 角度（度）；★ 官方说**只对** `Tapered to Vector` 有效。

    ⚠ ★ 用的是 `…FromEdge2`（★ `…FromEdge` 官方标 **Obsolete**，铁律 4：以后继版为准）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if int(ruled_type) not in RULED_TYPE_MEANINGS:
        return {"ok": False, "error": "ruled_type 不在官方取值表 0..4 内：%r（表：%s）"
                % (ruled_type, RULED_TYPE_MEANINGS)}
    import math
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "error": "取不到 FeatureManager"}
    before = _tree_names(model)
    feat = get_com_member(fm, "InsertRuledSurfaceFromEdge2",
                          int(ruled_type), float(length_mm) / 1000.0,
                          bool(flip_pull_dir), bool(flip_dir), bool(trim_and_sew),
                          math.radians(float(angle_deg)), bool(coord_input),
                          float(x_mm) / 1000.0, float(y_mm) / 1000.0, float(z_mm) / 1000.0,
                          bool(b_connect_surface))
    after = _tree_names(model)
    added = _delta(before, after)
    return {"ok": feat is not None and bool(added), "op": "ruled_surface",
            "returned_is_none": feat is None,
            "type": int(ruled_type), "type_meaning": RULED_TYPE_MEANINGS[int(ruled_type)],
            "tree_before": before, "tree_after": after, "new_features": added,
            "verified_by": "feature_not_none + tree_delta"}


def insert_delete_face(model, option: int = 0) -> dict:
    """★ **删除面**：`IModelDocExtension.InsertDeleteFace(Option)` —— ★★ **官方后继版**。

    ★★★ 2026-10-03（轮 474）**换了两处，都是"没查就用了旧的"** ——
      · ★ 上一版走 `IModelDoc2.InsertDeleteFace2(Refill)`，★ 而它**官方标 Obsolete**：
        > Obsolete. Superseded by [[IModelDocExtension::InsertDeleteFace]].
        ⇒ ★ 按**铁律 4**（以后继版为准）改用 `IModelDocExtension.InsertDeleteFace` ✓
      · ★ 而 `Option` **有正经枚举**（`swFaceDeleteOption_e`，★ 官方 swapi 给了取值表）：
        | 成员 | 值 |
        |---|---|
        | `swFaceDelete_Default` | **0** |
        | `swFaceDelete_Patch` | **1** |
        | `swFaceDelete_Fill` | **2** |
        | `swFaceDelete_FillWithTangent` | **3** |
        ⇒ ★ 默认用 **`0`（Default）** —— ★ 而**旧版那个 `Refill` 的功能位与这一代语义不同**，
          两者**不可互译**（★ 我上轮直接传 `1` 是**把旧版的位当新版的位**）⚠

    :param option: `swFaceDeleteOption_e` 的值（★ 默认 `0` = Default）。

    ★ 判据 = 返回值非假 **且** 特征树有新特征（★ 官方 Returns 逐字：
      "True if a **DeleteFace feature** is inserted, false if not"）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if int(option) not in (0, 1, 2, 3):
        return {"ok": False, "error": "option 不在 swFaceDeleteOption_e 的取值表 0..3 内：%r" % option}
    ext = get_com_member(model, "Extension")
    if ext is None:
        return {"ok": False, "error": "取不到 model.Extension"}
    before = _tree_names(model)
    r = get_com_member(ext, "InsertDeleteFace", int(option))
    after = _tree_names(model)
    added = _delta(before, after)
    return {"ok": bool(r) and bool(added), "op": "delete_face",
            "returned": r, "option": int(option),
            "option_meaning": {0: "swFaceDelete_Default", 1: "swFaceDelete_Patch",
                               2: "swFaceDelete_Fill", 3: "swFaceDelete_FillWithTangent"}[int(option)],
            "tree_before": before, "tree_after": after, "new_features": added,
            "verified_by": "return_value + tree_delta"}


def insert_replace_face(model) -> dict:
    """★ **替换面**：`IModelDoc2.InsertFeatureReplaceFace()` —— **零参数**，回 `void`。

    ★★ 官方 Remarks 逐字：「Before calling this method, **select the faces to replace** by calling
      `IModelDocExtension::SelectByID2` with **Marks of 1** and 2」
      ⇒ ★ **调用方必须先把「要替换的面」按 `mark=1`、「替换成哪个面」按 `mark=2` 选好** ✓
      （★ 铁律 3 第三句：多引用特征读 mark，不读选择顺序。）

    ⚠ 回 `void` ⇒ 判据只能靠**特征树增量**（★ 并如实写 `verified_by`）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    before = _tree_names(model)
    get_com_member(model, "InsertFeatureReplaceFace")
    after = _tree_names(model)
    added = _delta(before, after)
    return {"ok": bool(added), "op": "replace_face",
            "tree_before": before, "tree_after": after, "new_features": added,
            "requires_selection": "要被替换的面 mark=1 · 替换面 mark=2（官方 Remarks）",
            "verified_by": "tree_delta"}
