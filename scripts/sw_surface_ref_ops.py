"""★ B6-b 曲面特征（第二组）：旋转曲面 / 放样曲面（另 2 条单列，见模块尾的"查不到"段）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_surface_ref_ops.py
# 定位:   ★ 2026-10-03（轮 475）★ 承 `specs/201-toolbar-gaps` 的 **B6-b**。
#   台账「曲面」栏判「不能」的 13 条里，B6-a 收了 5 条，本模块收**第 2 组 2 条**，
#   并把**另 2 条为什么不做**写在下面。
#
# ==================  ================================================  ================
# ==
#   工具栏原文           官方成员（★ 台账给的名字**两条都不对**）              判据
# ==================  ================================================  ================
# ==
# 旋转曲面             `IFeatureManager.InsertRevolvedRefSurface` → **IFeature**   回 Fe
# ature + 树增量
# 放样曲面             `IModelDoc2.InsertLoftRefSurface2` → void                   树增
# 量
# ==================  ================================================  ================
# ==
#
# ★★★ **台账给的两个名字都不对**（★ 这是本轮最大的发现，★ 也解释了它们为什么一直"不能"）
# ：
#     · 台账写 **`FeatureRevolveRefSurface`** ⇒ ★ **swapi 里根本没有这个名字**；
#       真名是 **`IFeatureManager.InsertRevolvedRefSurface`**（★ 我按"含 Revolve/RefSurface"
#       全仓搜出来的，★ 而同族 `FeatureExtruRefSurface{,2,3}` 命名不同 ⇒ **不能按前缀猜**）⚠
#     · 台账写 `InsertProtrusionBlend2(Surface)` ⇒ ★ 那是**实体凸台**那族；
#       曲面放样的真名是 **`IModelDoc2.InsertLoftRefSurface2`** ✓
#
#   ★★ **代际（★ 铁律 4：以后继版为准）**：
# · `IModelDoc2.InsertLoftRefSurface` **官方标 Obsolete** ⇒ 被 `…RefSurface2` 取代 ⇒ ★ 
# 用 `…2`
#     · `IModelDoc2.InsertSweepRefSurface` 与 `…RefSurface2` **两个都标 Obsolete**
#       （继任者写的是 `IFeatureManager::InsertProtrusionSwept3`）⇒ ★ 见下面"查不到"段
#
#   ★★★ **两个 mark 表**（★ 官方 Remarks 逐字，★ 铁律 3 第三句）：
#     · 放样曲面：profile selections **should be 1**
#     · 旋转曲面：Remarks 只说 "Make the selections using `SelectByID2` before calling"
#       ⇒ ★ **没给 mark** ⇒ ★ 本模块**不假定 mark**，如实把这一点写进返回值 ✓
#
# 官方依据（三源）:
#   · `C:\swapi\types\IFeatureManager\InsertRevolvedRefSurface.md`
#     （`Feature (Angle: double, ReverseDir: bool, Angle2: double, RevType: int)`；
#      ★ **RevType 0=One direction · 1=MidPlane · 2=Two direction**；
# ★ "Make the selections using `SelectByID2` before calling" · "does not support 3D sket
# ches"）
#   · `C:\swapi\types\IModelDoc2\InsertLoftRefSurface2.md`
#     （6 参 `void`；★ "profile selections should be **1**"）
#   · `C:\swapi\types\IModelDoc2\InsertLoftRefSurface.md`（★ **Obsolete** 那一行）
#   · `C:\swapi\types\IModelDoc2\InsertSweepRefSurface{,2}.md`（★ **两个都 Obsolete**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件（★ 逐函数另有来源块）。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个函数回 `{"ok": …, "verified_by": …}`；★ 判据 = **回 Feature 非 None** + 
# **特征树增量**
#   （★ 事实 8：COM 返回值单独不可信；★ 规则 6：不静默成功）。

from __future__ import annotations

import math

try:
    from .sw_connect import get_com_member, set_com_member          # noqa: F401
except ImportError:                                                 # 顶层载入（脚本 / 探针）
    from sw_connect import get_com_member, set_com_member           # noqa: F401

__all__ = [
    "insert_revolved_ref_surface",
    "insert_lofted_ref_surface",
    "REVOLVE_TYPE_MEANINGS",
    "SURFACE_REF_STATUS",
]

#: ★ 官方给的 `RevType` 取值表（★ 逐字来自 `InsertRevolvedRefSurface.md` 的 Remarks）
REVOLVE_TYPE_MEANINGS = {
    0: "One direction revolution",
    1: "MidPlane revolution（★ 此时 `angle_deg` 是**全角**）",
    2: "Two direction revolution（★ `angle_deg` 是一向、`angle2_deg` 是另一向）",
}

#: ★ 本模块覆盖到的工具栏项 ⇒ 官方成员（★ 与 `docs/toolbar-ledger.json` 对齐用）
SURFACE_REF_STATUS = {
    "旋转曲面": "IFeatureManager.InsertRevolvedRefSurface",
    "放样曲面": "IModelDoc2.InsertLoftRefSurface2",
    "扫描曲面": "★ 查不到未废弃的**曲面版**入口（两个曲面版都标 Obsolete，继任者写的是实体那族）",
    "边界曲面": "★ swapi 里**没有任何** Boundary 特征成员（台账给的 `InsertBoundaryBoss` 也不在）",
}


#: ★ 2026-10-22（仓库统一化）：`_tree_names` 原在本文件与另外 3 个模块各有一份（逻辑逐字
#: 相同）
#:   ⇒ 收敛到单一实现 `scripts/sw_feature_tree.py`，此处只做导入别名 ✓
try:
    from .sw_feature_tree import tree_names as _tree_names
except ImportError:
    from sw_feature_tree import tree_names as _tree_names


#: ★ 2026-10-22 统一化：本函数原与另 3 个模块各有一份（另一处叫 _new_features），
#:   现收敛到 scripts/sw_feature_tree.new_features；本文件调用点已直接改名
try:
    from .sw_feature_tree import new_features
except ImportError:
    from sw_feature_tree import new_features



def insert_revolved_ref_surface(model, angle_deg: float, rev_type: int = 0,
                                reverse_dir: bool = False, angle2_deg: float = 0.0) -> dict:
    """★ **旋转曲面**：`IFeatureManager.InsertRevolvedRefSurface(…)` → **IFeature**。

    ★★★ 官方原话：「Creates a **revolved reference surface** by revolving a profile around a
      centerline.」⇒ ★ 与实体版 `sw_part.revolve_boss` 同形，★ 只是产出**曲面**。

    :param angle_deg: 旋**角**（度；★ 只在本边界换算成弧度一次 —— 规则 2）。
      ★ `rev_type=1`（MidPlane）时它是**全角**（★ 官方逐字）。
    :param rev_type: 官方 `RevType`，取值表见 `REVOLVE_TYPE_MEANINGS`（0/1/2）。
    :param angle2_deg: 第二向的角（★ 只对 `rev_type=2` 有意义）。

    ⚠ **调用前要选好轮廓**（★ 官方 Remarks 逐字："Make the selections using
      `IModelDocExtension::SelectByID2` before calling this method"）。
      ★★ 而官方**没给 mark** ⇒ ★ 本模块**不假定 mark**，把这一点写进返回值 ✓
    ⚠ 官方另注「does not support **3D sketches**」。

    ★ 判据 = **回 `IFeature` 非 None** **且** **特征树有新特征**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if int(rev_type) not in REVOLVE_TYPE_MEANINGS:
        return {"ok": False, "error": "rev_type 不在官方取值表 0..2 内：%r（表：%s）"
                % (rev_type, REVOLVE_TYPE_MEANINGS)}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "error": "取不到 FeatureManager"}
    before = _tree_names(model)
    feat = get_com_member(fm, "InsertRevolvedRefSurface",
                          math.radians(float(angle_deg)), bool(reverse_dir),
                          math.radians(float(angle2_deg)), int(rev_type))
    after = _tree_names(model)
    added = new_features(before, after)
    return {"ok": feat is not None and bool(added), "op": "revolved_ref_surface",
            "returned_is_none": feat is None,
            "rev_type": int(rev_type), "rev_type_meaning": REVOLVE_TYPE_MEANINGS[int(rev_type)],
            "asked_deg": angle_deg, "asked2_deg": angle2_deg, "reverse_dir": bool(reverse_dir),
            "selection_mark": "★ 官方 Remarks **没给** mark —— 本模块不假定",
            "tree_before": before, "tree_after": after, "new_features": added,
            "verified_by": "feature_not_none + tree_delta"}


def insert_lofted_ref_surface(model, closed: bool = False, keep_tangency: bool = True,
                              force_non_rational: bool = False, tess_tolerance_factor: float = 0.0,
                              start_matching_type: int = 0, end_matching_type: int = 0) -> dict:
    """★ **放样曲面**：`IModelDoc2.InsertLoftRefSurface2(…)`（6 参）→ `void`。

    ★ 官方原话：「Creates a **loft surface** from the **selected profiles**, centerline, and
      guide curves.」

    :param closed: ★ 官方逐字："if True, then you must have **at least three profiles** selected,
      and if…"（★ 闭合放样对轮廓数有要求）。
    :param keep_tangency: 相切时是否保持相切（★ 官方："If the section curves are tangent…"）。
    :param force_non_rational: 强制非有理曲面。
    :param tess_tolerance_factor: 带中心线放样时控制中间截面数；★ 官方给了默认值 ⇒ 0.0 表示**用默认**。
    :param start_matching_type / end_matching_type: 起 / 末轮廓的相切类型（★ 官方"see Remarks"，
      ★ 而本工具**不编造取值表** ⇒ 原样透传 int）。

    ★★ **调用前要选好轮廓**，且官方 Remarks 逐字：
      「Use `IModelDocExtension::SelectByID2` to select the profiles and guide curves.
        The mark for: **profile selections should be 1**」⇒ ★ **轮廓 mark=1** ✓（铁律 3 第三句）。

    ⚠ ★ 官方回 `void` ⇒ 判据**只能**靠**特征树增量**（★ 并如实写 `verified_by`）。
    ⚠ 用的是 `…RefSurface2`（★ `…RefSurface` 官方标 **Obsolete**，铁律 4）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    before = _tree_names(model)
    get_com_member(model, "InsertLoftRefSurface2",
                   bool(closed), bool(keep_tangency), bool(force_non_rational),
                   float(tess_tolerance_factor), int(start_matching_type), int(end_matching_type))
    after = _tree_names(model)
    added = new_features(before, after)
    return {"ok": bool(added), "op": "lofted_ref_surface",
            "closed": bool(closed), "keep_tangency": bool(keep_tangency),
            "selection_mark": "profile selections **should be 1**（官方 Remarks 逐字）",
            "tree_before": before, "tree_after": after, "new_features": added,
            "verified_by": "tree_delta"}


# ── ★★ 本轮**不做**的两条，以及为什么（★ 铁律 5：查不到就说查不到）─────────────
#
# ① **扫描曲面**（台账写 `InsertProtrusionSwept4(Surface)`）：
#    ★ 曲面版有两个 —— `IModelDoc2.InsertSweepRefSurface` 与 `…RefSurface2` ——
#      ★ **两个的 `kind: method` 下面都写着 Obsolete**，且都把继任者指向
#      **`IFeatureManager::InsertProtrusionSwept3`**。
#    ★★ 而 `InsertProtrusionSwept3` 是**凸台（实体）**那族 ⇒ ★ **曲面版在新架构里走哪条，
#      两个源都没给出对应入口**。
#    ★ 已知线索：SOLIDWORKS 2018 起扫描改走 **`ISweepFeatureData`**（★ 本仓
#      `sw_sweep.create_sweep_report` 用的就是它）⇒ ★ 若它里面有"曲面/实体"开关，
#      那才是正路 ⇒ ★★ **留待下一轮查 `ISweepFeatureData` 的成员**，**不猜**。
#
# ② **边界曲面**（台账写 `InsertBoundaryBoss`）：
#    ★ 全 `C:\swapi\types` 搜 `*Boundary*`，**没有任何** Boss/Surface/Feature 成员；
#      `InsertBoundaryBoss` 这个名字**也不在**。
#    ★★ 可能的解释（★ 只是可能）：边界曲面在 API 里**并入放样**（`InsertLoftRefSurface*`
#      或 `ISurfaceFinishFeatureData` 那族）⇒ ★ **但那是推断，不是查到的** ⇒
#      ★★★ 按**铁律 5**：写"查不到"并**单列**，★ **不假装做到**。
