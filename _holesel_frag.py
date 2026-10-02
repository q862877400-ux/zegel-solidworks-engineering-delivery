

# ── 24h 计划 段 4 续（Spec Kit `151`）：**声明式建孔**（★ 规则 3 的精神）──────────────
# ★★★★ 为什么要有这一族（★ 而它比"把既有函数挂上去"更好）：
#   · 能力层既有的 `create_through_hole(model, center, ...)` 吃 **`center`（坐标元组）**；
#   · ★ 而**上游**的统一建孔工具 `solidworks_create_hole_feature`（`mcp-server/server.py` L2244）
#     吃的是 **`center_x_mm` / `center_y_mm`** —— ★★ **那是**裸坐标参数名****（规则 3 的**字面**红线）。
#   ⇒ ★★★ **所以本族是"规则 3 合规版"**：★ **只吃声明式 `selection`**，★ **内部用
#     `sw_selection_spec.selection_point` 从选区读点** ⇒ ★ **工具参数里没有坐标**。
#   ★ 而单位已由真机对照实验定死（★ 轮 267：`GetSelectionPoint2` 回的是**毫米**）。
#
# ★ 覆盖 5 种（★ 与能力层既有的一一对应）：通孔 · 盲孔 · 沉头孔 · 锥沉孔 · 半圆端槽。
# ⚠ **判据**：★ 每个包装都回**能力层既有的** `HoleFeatureEvidence`（★ 它本来就是回读证据）——
#   ★ 再套一层"选区点的坐标"（★ 于是调用方能看出**它建在哪个点上**）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_hole_features.py —— 本段
# 定位:   段 4 的"声明式建孔"（★ 规则 3 合规版，替代上游的裸坐标入口）。
# 官方依据: `IModelDoc2.HoleWizard5` 族（★ 既有函数的来源块）·
#          `ISelectionMgr.GetSelectionPoint2(Index, Mark)`（★ 读点，Index 从 1 起）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 5 个包装 + 1 个助手
# ─────────────────────────────────────────────────────────────────────────────


def _point_from_selection(model, selection: str):
    """★ **按声明式选择选点并读它的坐标**（毫米）—— 本族所有包装的前置。

    ★ 用法：★ `selection` 传 `index:N`（选第 N 个可选实体）或 `__current_selection__`
      （★ 用界面上已选好的）。★ **不传坐标**（★ 规则 3）。
    ⇒ 返回 `(point_tuple, err)`：★ 成功时 `err is None`。
    """
    try:
        from .sw_selection_spec import resolve_selection, selection_point
    except ImportError:                                        # pragma: no cover
        from sw_selection_spec import resolve_selection, selection_point
    if str(selection) == "__current_selection__":
        #: ★ 已选好的直接用（★ 与 `sw_part._ensure_sketch_selected` 同约定）
        pass
    else:
        try:
            resolve_selection(model, str(selection), "VERTEX")
        except Exception:
            #: ★ 顶点选不到就试**按面上的点**那条既有路径（★ 那是本仓库的通行做法）
            try:
                resolve_selection(model, str(selection), "EDGE")
            except Exception as exc:                           # noqa: BLE001
                return None, "选择 %r 失败：%s" % (selection, str(exc)[:120])
    r = selection_point(model)
    if not r.get("ok"):
        return None, "读不到点：%s" % str(r.get("error"))[:150]
    return tuple(r["point_mm"]), None


def create_through_hole_at_selection_report(model, selection: str, diameter_mm: float,
                                            plane_name: str = "Front Plane",
                                            name: str = "通孔") -> dict:
    """★ **声明式建通孔**：★ 从 `selection` 读点 ⇒ 建完全贯穿圆孔 ⇒ 回**回读证据 + 用的那个点**。

    ★★ 与 `create_through_hole` 的**唯一区别**：★ **它不要坐标**（★ 规则 3）。
    """
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "through", "selection": str(selection), "error": err}
    ev = create_through_hole(model, pt, diameter_mm, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "point_from_selection_mm": list(pt),
                "★": "点来自**声明式选择**（不是调用方传坐标）—— 规则 3"})
    return out


def create_blind_hole_at_selection_report(model, selection: str, diameter_mm: float, depth_mm: float,
                                          plane_name: str = "Front Plane",
                                          name: str = "盲孔") -> dict:
    """★ **声明式建盲孔**（★ 吃 `selection` 与 `depth_mm`，★ 不要坐标）。"""
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "blind", "selection": str(selection), "error": err}
    ev = create_blind_hole(model, pt, diameter_mm, depth_mm, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "point_from_selection_mm": list(pt),
                "★": "点来自**声明式选择** —— 规则 3"})
    return out


def create_counterbore_hole_at_selection_report(model, selection: str, hole_diameter_mm: float,
                                               counterbore_diameter_mm: float,
                                               counterbore_depth_mm: float,
                                               plane_name: str = "Front Plane",
                                               name: str = "沉头孔") -> dict:
    """★ **声明式建沉头孔**（★ 不要坐标）。"""
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "counterbore", "selection": str(selection), "error": err}
    ev = create_counterbore_hole(model, pt, hole_diameter_mm, counterbore_diameter_mm,
                                 counterbore_depth_mm, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "point_from_selection_mm": list(pt),
                "★": "点来自**声明式选择** —— 规则 3"})
    return out


def create_countersink_hole_at_selection_report(model, selection: str, hole_diameter_mm: float,
                                               countersink_diameter_mm: float,
                                               included_angle_deg: float = 90.0,
                                               plane_name: str = "Front Plane",
                                               name: str = "锥沉孔") -> dict:
    """★ **声明式建锥沉孔**（★ 不要坐标；★ 角度参数带 `_deg`，规则 2）。"""
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "countersink", "selection": str(selection), "error": err}
    ev = create_countersink_hole(model, pt, hole_diameter_mm, countersink_diameter_mm,
                                 included_angle_deg, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "point_from_selection_mm": list(pt),
                "★": "点来自**声明式选择** —— 规则 3"})
    return out


def create_semicircular_slot_at_selection_report(model, start_selection: str, end_selection: str,
                                                width_mm: float, depth_mm: float = 0.0,
                                                plane_name: str = "Front Plane",
                                                name: str = "半圆端槽") -> dict:
    """★ **声明式建半圆端槽**：★ **两端各用一次声明式选择**（★ 于是**两个点都不是坐标参数**）。"""
    pts = []
    for sel in (start_selection, end_selection):
        pt, err = _point_from_selection(model, sel)
        if err:
            return {"ok": False, "kind": "semicircular_slot", "selection": str(sel), "error": err}
        pts.append(pt)
    ev = create_semicircular_slot(model, pts[0], pts[1], width_mm, depth_mm,
                                  plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "start_selection": str(start_selection),
                "end_selection": str(end_selection),
                "points_from_selection_mm": [list(p) for p in pts],
                "★": "两个点都来自**声明式选择** —— 规则 3"})
    return out
