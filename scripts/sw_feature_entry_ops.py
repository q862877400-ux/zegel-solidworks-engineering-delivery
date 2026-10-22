"""★ 把**已真机证明的直入法**抬进 `scripts/`（本批：装饰螺纹线）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**把探针里已验证的调用序抬成可挂工具的能力层**）。
# 文件:   scripts/sw_feature_entry_ops.py
# 定位:   ★★ **本文件的存在理由**（★ 一种反复出现的形态）：
# 有些能力**已经真机建成过**，但代码只留在 `tools/prove_*.py` 探针里、**没抬进 `scripts/
# `**
#   ⇒ 于是 `capabilities.yaml` 里是 `level: verified`、**却挂不上任何 MCP 工具** ——
#   ★ 而那正是台账 `limitations` **自己写明的下一步**：「⚠ **本包装未接进 MCP 工具层**」。
#   ★ 依据：`specs/202-user-coverage-gaps/recon/scan-S2b-ledger-vs-tools.md` 的 **A 表**
#     （台账有、但 `mcp_tools` 无挂 —— 41 条，扣自述豁免后 40 条候选）。
#   ★★ 本文件**不发明任何调用** —— 每一处调用序都**照抄已建成的那次真机探针**。
#   官方依据（逐页读过）:
#     · `C:\swapi\types\IFeatureManager\InsertCosmeticThread3.md`
#       `Feature InsertCosmeticThread3(int Standard, string StandardType, string Size,
# double Diameter, int EndType, double Depth, string Note)`（**7 参**，md **未标 Obsolet
# e**）
# · `ISurface.IsCylinder()` —— ★ **官方判形方法**（★ **不猜** `Surface.Identity` 的字符
# 串）
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.sw_connect import get_com_member                            # noqa: E402

#: ★ 官方枚举值（逐字取自 `InsertCosmeticThread3.md` 的 Parameters 段）
STD_ANSI_METRIC = 1          #: `Standard`：1 = ANSI Metric
END_TYPE_BLIND = 0           #: `EndType`：0 = Blind（此时 `Depth` 有效）
END_TYPE_THROUGH = 2         #: `EndType`：2 = Through


def _feature_names(model):
    """★ 读特征树的名字表 —— ★★ **委托给仓内规范助手**，不自己走树。

    ★★ **为什么改（2026-10-03 接手轮，自查发现）**：本函数**原来自己走**
      `GetFeatureTreeRootItem2` → `GetFirstChild`/`GetNext` → `GetFeature`，
      ★ 而真机跑下来它**回一个不完整的表** —— 证据：`tools/probe_flatten_tool.py` 里
      `ret_type` 明明是 **`FlattenSurface`**、`ret_name` 是 **`曲面-展平1`**，
      ★ 而 `new_features` 却是 **`[]`** ⇒ ★ 那说明"**树增量**"这条判据在本模块里**是假的**
      （★ 本格的 `ok` 是靠 `ret_type` 成立的，不是靠树）。
    ★ 修法：**委托** `scripts/sw_feature_readback.feature_names`（★ 仓内规范实现）。
    ★ **取不到回 `None`**（★ **降级，不猜空表** —— ★ 否则"没读到"会被当成"没变化"）。
    """
    try:
        from scripts import sw_feature_readback as FR
        return list(FR.feature_names(model) or [])
    except Exception:                                                   # noqa: BLE001
        return None


def find_cylindrical_face(model, *, visible_only: bool = True):
    """★ 找**第一个圆柱面** —— ★ 判形用**官方** `ISurface.IsCylinder()`（★ 不猜字符串）。"""
    for body in list(get_com_member(model, "GetBodies2", 0, bool(visible_only)) or []):
        for face in list(get_com_member(body, "GetFaces") or []):
            try:
                if bool(get_com_member(get_com_member(face, "GetSurface"), "IsCylinder")):
                    return face
            except Exception:                                           # noqa: BLE001
                continue
    return None


def insert_cosmetic_thread(model, *, standard: int = STD_ANSI_METRIC, standard_type: str = "",
                           size: str = "", diameter_mm: float = 8.0,
                           end_type: int = END_TYPE_THROUGH, depth_mm: float = 0.0,
                           note: str = "") -> dict:
    """★ **装饰螺纹线**：`IFeatureManager.InsertCosmeticThread3`（7 参 · 未废弃）。

    ★★ **官方前置（台账 `feature_cosmetic_thread.limitations` 逐字）**：选**圆柱面的一条边**
      —— ★ **不是那个面**（★ 本函数**自己找**：先用 `ISurface.IsCylinder()` 找圆柱面，
      再取它的**第一条边**并按 `mark=0` 选中 ⇒ ★ 调用方**不必**先选）。
    ★ **判据**：特征树**新增** + 返回对象的 `GetTypeName2`（★ 真机建成时是 **`CosmeticThread`**）。
    ⚠ `diameter` 官方是 `System.double`、**没写单位** ⇒ ★ 本函数对外收 `diameter_mm`（**毫米**），
      ★ 换算只在本函数边界发生一次；★ 而真机那次传的是 **0.008**（= 米制口径）⇒ ★ 口径一致。
    """
    if model is None:
        return {"ok": False, "op": "insert_cosmetic_thread", "error": "model 为 None"}
    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:                                                   # noqa: BLE001
        pass
    face = find_cylindrical_face(model)
    if face is None:
        return {"ok": False, "op": "insert_cosmetic_thread", "preconditions_held": False,
                "error": ("★ 前置未成立：该文档**找不到圆柱面**（`ISurface.IsCylinder()` 全 False）"
                          "⇒ 装饰螺纹线要在一个圆柱孔/轴的边上"),
                "verified_by": "特征树新增 + 返回对象 GetTypeName2（★ 真机建成时为 CosmeticThread）"}
    edges = list(get_com_member(face, "GetEdges") or [])
    out = {"op": "insert_cosmetic_thread", "cyl_face_found": True, "edge_count": len(edges),
           "verified_by": "特征树新增 + 返回对象 GetTypeName2（★ 真机建成时为 CosmeticThread）"}
    if not edges:
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = "★ 前置未成立：那个圆柱面**取不到边**"
        return out
    try:
        import scripts.sw_part as SP
        if not SP._select_com_object(edges[0], append=False, mark=0):
            out["ok"] = False
            out["preconditions_held"] = False
            out["error"] = "★ 前置未成立：圆柱面的第一条边**没选上**（`_select_com_object` 回假）"
            return out
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = "★ 前置未成立：选边抛错 %s: %s" % (type(exc).__name__, str(exc)[:160])
        return out
    out["preconditions_held"] = True
    before = _feature_names(model)
    try:
        ret = get_com_member(get_com_member(model, "FeatureManager"), "InsertCosmeticThread3",
                             int(standard), str(standard_type), str(size),
                             float(diameter_mm) / 1000.0, int(end_type),
                             float(depth_mm) / 1000.0, str(note))
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        return out
    after = _feature_names(model)
    out["ret_is_none"] = ret is None
    for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
        try:
            out[k] = str(get_com_member(ret, m))
        except Exception:                                               # noqa: BLE001
            pass
    if before is not None and after is not None:
        out["new_features"] = [n for n in after if n not in before]
    out["ok"] = bool(out.get("ret_type") == "CosmeticThread" or out.get("new_features"))
    return out


__all__ = ["insert_cosmetic_thread", "create_flatten_surface", "thicken_surface",
           "find_cylindrical_face",
           "STD_ANSI_METRIC", "END_TYPE_BLIND", "END_TYPE_THROUGH"]


def thicken_surface(model, *, thickness_mm: float, cut: bool = False, direction: int = 0,
                    fill_volume: bool = False, merge: bool = True, use_feat_scope: bool = True,
                    use_auto_select: bool = True) -> dict:
    """★ **加厚 / 加厚切除** —— ★★ **两个都未废弃的直入成员**（★ 这是 R4「换名重查」的产出）。

    ★★★ **为什么是这两个成员**（★ 都逐字读过官方页，见 `recon/r4-e-class-rename-lookup.md`）：
      · ✓ **未废弃**：`IFeatureManager.FeatureBossThicken`（**7 参**）·
        `IFeatureManager.FeatureCutThicken`（**6 参**）
      · ⛔ **废弃**：`IModelDoc2.FeatureBossThicken{,2}` / `FeatureCutThicken{,2}`
        （`FeatureBossThicken2` 头顶逐字：`Superseded by [[IFeatureManager::FeatureBossThicken]].`）
      · ★ 另一族 `IModeler.ThickenSheet` 造的是**片体**、**不是特征** ⇒ **不当入口**。
    ★★ **官方前置（Remarks 逐字）**：
      · 「by thickening a **selected reference surface**. **The surface must be selected with a mark of 1.**」
      · 「If **FillVolume** is true, **other arguments are ignored**. A **closed surface is required**
        when FillVolume is true.」
      · （切减）「When **UseAutoSelect is false**, the user must **select the bodies** that the feature
        will affect.」
      ⇒ ★ 本函数**自己把第一张面按 `mark=1` 选上**（★ 与展平那条同一手法），★ 选不上就**如实报前置**。
    ★ **判据**：特征树**新增** + 返回对象 `GetTypeName2`。
    ★ `thickness_mm` 对外收**毫米** ⇒ ★ **只在边界换算一次**（COM 吃**米**）。
    ⚠ **未真机验证**（★ 由 `tools/probe_thicken_tool.py` 单独验，★ 在那之前不许写 `verified`）。
    """
    if model is None:
        return {"ok": False, "op": "thicken_surface", "error": "model 为 None"}
    kind = "FeatureCutThicken" if cut else "FeatureBossThicken"
    out = {"op": "thicken_surface", "member": kind, "thickness_mm": float(thickness_mm),
           "cut": bool(cut), "fill_volume": bool(fill_volume),
           "official_precondition": "参考面必须按 **mark=1** 选中（官方 Remarks 逐字）",
           "verified_by": "特征树新增 + 返回对象 GetTypeName2"}
    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:                                                   # noqa: BLE001
        pass
    #: ★ 找一张**参考面**：先试**曲面体**（加厚曲面的常见情形），再退到实体体的面
    face = None
    for btype in (_BODY_TYPE_SURFACE, _BODY_TYPE_SOLID):
        for body in list(get_com_member(model, "GetBodies2", btype, True) or []):
            faces = list(get_com_member(body, "GetFaces") or [])
            if faces:
                face, out["body_type"] = faces[0], ("surface" if btype else "solid")
                break
        if face is not None:
            break
    if face is None:
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = ("★ 前置未成立：**找不到可作参考的面**（曲面体与实体体都取不到面）"
                        "⇒ 官方 Remarks 要求先有一张**参考面**并给 `mark=1`")
        return out
    try:
        import scripts.sw_part as SP
        if not SP._select_com_object(face, append=False, mark=1):
            out["ok"] = False
            out["preconditions_held"] = False
            out["error"] = "★ 前置未成立：参考面**没按 `mark=1` 选上**"
            return out
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = "★ 前置未成立：选面抛错 %s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["preconditions_held"] = True
    fm = get_com_member(model, "FeatureManager")
    before = _feature_names(model)
    thick_m = float(thickness_mm) / 1000.0                              #: ★ 规则 2：换算只此一次
    try:
        if cut:
            #: ★ `FeatureCutThicken(Thickness, Direction, FaceIndex, FillVolume, UseFeat
            #: Scope, UseAutoSelect)`
            ret = get_com_member(fm, kind, thick_m, int(direction), 0, bool(fill_volume),
                                 bool(use_feat_scope), bool(use_auto_select))
        else:
            #: ★ `FeatureBossThicken(Thickness, Direction, FaceIndex, FillVolume, Merge,
            #:   UseFeatScope, UseAutoSelect)`
            ret = get_com_member(fm, kind, thick_m, int(direction), 0, bool(fill_volume),
                                 bool(merge), bool(use_feat_scope), bool(use_auto_select))
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        return out
    after = _feature_names(model)
    out["ret_is_none"] = ret is None
    for k, memo in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
        try:
            out[k] = str(get_com_member(ret, memo))
        except Exception:                                               # noqa: BLE001
            pass
    if before is not None and after is not None:
        out["new_features"] = [n for n in after if n not in before]
    out["ok"] = bool(out.get("new_features") or out.get("ret_type"))
    return out


#: ★ `GetBodies2` 的 `Type` 参数：★ 0 = 实体体 · **1 = 曲面体**（★ 展平要的是**曲面体**
#: ）
_BODY_TYPE_SURFACE = 1
_BODY_TYPE_SOLID = 0


def create_flatten_surface(model, *, accuracy_factor: int = 4, should_use_tears: bool = False,
                           body_type: str = "surface") -> dict:
    """★ **曲面展平**：`IFeatureManager.InsertFlattenSurface2(AccuracyFactor, ShouldUseTears)`（**2 参**）。

    ★★ **官方前置（台账 `surface_flatten.limitations` 逐字）**：必须选中 **面（mark = 1）** 与
      **锚点（mark = 16）**；★ 另可选 **2 = 引导边** · **4 = 映射边** · **8 = 撕裂边**。
      ★ 本函数**自己选**（★ 调用方不必先选）：取**曲面体的第一张面**按 `mark=1`，
      再取**该体第一条边的一个顶点**按 `mark=16`（★ 与那次建成的探针同一手法）。
    ★ **`AccuracyFactor` 范围（台账逐字）：10 ≥ 精度 ≥ 1**（1 = 最高）；★ **真机用 4 成**。
    ★ **判据**：特征树**新增** + 返回对象 `GetTypeName2`（★ 真机建成时是 **`FlattenSurface`**、
      名 `曲面-展平1`）。
    ★ `body_type="surface"` ⇒ 取 **`GetBodies2(1, …)`**（曲面体）；`"solid"` ⇒ 取 `GetBodies2(0, …)`。
      ★ 取不到时**如实报** `preconditions_held=False`（★ 曲面展平需要一个**曲面体**）。
    """
    if model is None:
        return {"ok": False, "op": "create_flatten_surface", "error": "model 为 None"}
    btype = _BODY_TYPE_SURFACE if str(body_type).lower().startswith("surf") else _BODY_TYPE_SOLID
    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:                                                   # noqa: BLE001
        pass
    try:
        bodies = list(get_com_member(model, "GetBodies2", btype, True) or [])
    except Exception as exc:                                            # noqa: BLE001
        return {"ok": False, "op": "create_flatten_surface",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    out = {"op": "create_flatten_surface", "body_type": "surface" if btype else "solid",
           "body_count": len(bodies), "accuracy_factor": int(accuracy_factor),
           "should_use_tears": bool(should_use_tears),
           "official_marks": "面=1 · 锚点=16 · 引导边=2 · 映射边=4 · 撕裂边=8（官方 Remarks 逐字）",
           "verified_by": "特征树新增 + 返回对象 GetTypeName2（★ 真机建成时为 FlattenSurface）"}
    if not bodies:
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = ("★ 前置未成立：`GetBodies2(%d, True)` 回空 ⇒ ★ 该文档**没有%s体**"
                        % (btype, "曲面" if btype else "实体"))
        return out
    body = bodies[0]
    faces = list(get_com_member(body, "GetFaces") or [])
    if not faces:
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = "★ 前置未成立：那个体**取不到面**"
        return out
    try:
        import scripts.sw_part as SP
        if not SP._select_com_object(faces[0], append=False, mark=1):
            out["ok"] = False
            out["preconditions_held"] = False
            out["error"] = "★ 前置未成立：面**没按 mark=1 选上**"
            return out
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = "★ 前置未成立：选面抛错 %s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    got_anchor = False
    for edge in list(get_com_member(body, "GetEdges") or [])[:1]:
        for memo in ("GetStartVertex", "GetEndVertex"):
            try:
                v = get_com_member(edge, memo)
                if v is not None and SP._select_com_object(v, append=True, mark=16):
                    got_anchor = True
                    break
            except Exception:                                           # noqa: BLE001
                continue
        if got_anchor:
            break
    out["anchor_selected"] = got_anchor
    if not got_anchor:
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = ("★ 前置未成立：**锚点（mark=16）没选上** —— ★ 而台账逐字记着"
                        "「面-only（mark=1）**不够**」⇒ ★ 这正是那一格失败的原因")
        return out
    out["preconditions_held"] = True
    before = _feature_names(model)
    try:
        ret = get_com_member(get_com_member(model, "FeatureManager"), "InsertFlattenSurface2",
                             int(accuracy_factor), bool(should_use_tears))
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        return out
    after = _feature_names(model)
    out["ret_is_none"] = ret is None
    for k, memo in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
        try:
            out[k] = str(get_com_member(ret, memo))
        except Exception:                                               # noqa: BLE001
            pass
    if before is not None and after is not None:
        out["new_features"] = [n for n in after if n not in before]
    out["ok"] = bool(out.get("ret_type") == "FlattenSurface" or out.get("new_features"))
    return out
