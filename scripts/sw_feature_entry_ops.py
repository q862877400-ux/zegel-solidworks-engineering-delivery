"""★ 把**已真机证明的直入法**抬进 `scripts/`（本批：装饰螺纹线）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**把探针里已验证的调用序抬成可挂工具的能力层**）。
# 文件:   scripts/sw_feature_entry_ops.py
# 定位:   ★★ **本文件的存在理由**（★ 一种反复出现的形态）：
#   有些能力**已经真机建成过**，但代码只留在 `tools/prove_*.py` 探针里、**没抬进 `scripts/`**
#   ⇒ 于是 `capabilities.yaml` 里是 `level: verified`、**却挂不上任何 MCP 工具** ——
#   ★ 而那正是台账 `limitations` **自己写明的下一步**：「⚠ **本包装未接进 MCP 工具层**」。
#   ★ 依据：`specs/202-user-coverage-gaps/recon/scan-S2b-ledger-vs-tools.md` 的 **A 表**
#     （台账有、但 `mcp_tools` 无挂 —— 41 条，扣自述豁免后 40 条候选）。
#   ★★ 本文件**不发明任何调用** —— 每一处调用序都**照抄已建成的那次真机探针**。
#   官方依据（逐页读过）:
#     · `C:\swapi\types\IFeatureManager\InsertCosmeticThread3.md`
#       `Feature InsertCosmeticThread3(int Standard, string StandardType, string Size,
#        double Diameter, int EndType, double Depth, string Note)`（**7 参**，md **未标 Obsolete**）
#     · `ISurface.IsCylinder()` —— ★ **官方判形方法**（★ **不猜** `Surface.Identity` 的字符串）
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
    """★ 读特征树的名字表（★ 取不到回 None —— **降级，不猜空表**）。"""
    try:
        fm = get_com_member(model, "FeatureManager")
        f = get_com_member(fm, "GetFeatureTreeRootItem2", 0)
        out = []

        def walk(item, depth=0):
            if item is None or depth > 6:
                return
            try:
                fobj = get_com_member(item, "GetFeature")
                if fobj is not None:
                    out.append(str(get_com_member(fobj, "Name") or ""))
            except Exception:                                           # noqa: BLE001
                pass
            try:
                child = get_com_member(item, "GetFirstChild")
                while child is not None:
                    walk(child, depth + 1)
                    child = get_com_member(child, "GetNext")
            except Exception:                                           # noqa: BLE001
                pass

        walk(f)
        return out
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


__all__ = ["insert_cosmetic_thread", "find_cylindrical_face",
           "STD_ANSI_METRIC", "END_TYPE_BLIND", "END_TYPE_THROUGH"]
