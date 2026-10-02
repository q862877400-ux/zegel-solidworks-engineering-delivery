

# ── 24h 计划 段 4 续（Spec Kit `150`）：**从选区读点**（★ 规则 3 的关键一环）─────────────
# ★★★ 为什么需要它（★ 规则 3 的**精神**，不只是字面）：
#   孔族那几个建孔函数吃 **`center`（一个坐标元组）**。★ 规则 3 的红线**字面**只管**参数名**
#   （`x` / `y` / `cx` …）⇒ ★ `center` **不在** `_BARE_COORD_NAMES` 里
#   （★ 它在 `_COORD_COMPONENT_NOTE`，★ 那条的定性是"**名字不表态**，只登记不判"）。
#   ⇒ ★★ **所以严格说它们能挂 —— 但那会绕过规则 3 的**精神****（"选择必须用声明式 `selection`"）。
#   ⇒ ★★★ **正解与官方一致**：★ **官方 `HoleWizard` 的工作流就是"先在面上选一个点"**
#     ⇒ ★★ **包一层**：★ **用声明式 `selection` 选点 ⇒ 从选区读坐标**
#       ⇒ ★★★ **于是工具参数里**没有坐标**，★ 只有 `selection`** ✓
#
# ★ 官方依据：`C:\swapi\types\ISelectionMgr\GetSelectionPoint.md`（★ 索引里确认存在）
#   ⚠ 另有 `GetSelectionPoint2` / `GetSelectionPointInSketchSpace(2)` ——
#   ★ 本函数**只用 `GetSelectionPoint`**（★ 取不到就如实报，★ 不去猜别的重载）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_selection_spec.py —— 本段
# 定位:   段 4 的孔族声明式包装所需的"从选区读点"。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面这个函数
# ─────────────────────────────────────────────────────────────────────────────


def selection_point(model) -> dict:
    """★ **读当前选区那个点的坐标**（★ 毫米）—— 供"用声明式选择代替裸坐标"的包装使用。

    ★★ 用途：★ 孔族（`create_through_hole` 等）吃 `center`（**一个坐标元组**）⇒
      ★ 包一层「**先选点、再建孔**」⇒ ★ **工具层的参数里就没有坐标了**（★ 规则 3 的精神）。

    返回 `{"ok": bool, "point_mm": (x, y, z) | None, "selection_count": int, "error": str | None}`。
    ⚠ **不猜**：★ `GetSelectionPoint` 取不到就 `ok=False` + 写明原因（★ 铁律 5）。
    """
    out: dict = {"ok": False, "point_mm": None, "selection_count": None, "error": None}
    try:
        mgr = get_com_member(model, "SelectionManager")
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "取不到 SelectionManager：%s" % str(exc)[:120]
        return out
    try:
        n = int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        out["selection_count"] = n
    except Exception:                                          # noqa: BLE001
        pass
    if not out["selection_count"]:
        out["error"] = ("当前**没有选中任何东西** ⇒ 读不到点。"
                        "★ 先用声明式选择选中一个点 / 草图点 / 面，再调本函数。")
        return out
    try:
        pt = get_com_member(mgr, "GetSelectionPoint")
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "GetSelectionPoint 报错：%s" % str(exc)[:150]
        return out
    if pt is None:
        out["error"] = ("GetSelectionPoint 回 None ⇒ "
                        "★ 选中的**不是**一个点（可能是面 / 边 / 特征）。"
                        "★ 本函数不猜别的重载，如实报「取不到」。")
        return out
    try:
        vals = [float(x) for x in pt][:3]
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "返回值不是可转 float 的序列：%s（%s）" % (str(pt)[:60], type(pt).__name__)
        return out
    if len(vals) < 3:
        out["error"] = "返回值长度 %d < 3" % len(vals)
        return out
    out["ok"] = True
    out["point_mm"] = tuple(vals)
    return out
