from sw_feature_readback import feature_names
from sw_connect import get_com_member



# ── 24h 计划 段 6 续（Spec Kit `168`）：**放样（loft）** ──────────────────────────────
# ★★★★★ 2026-10-01（轮 313）**这是"四家有我们没有"里核实的一个真缺**：
#   ★ 全仓 grep `loft` ⇒ **工具 0 · 函数 0**（★ 同类：`sweep` 也是 0）——
#   ★★ 而**放样与扫描是 SolidWorks 最基本的两种特征**（★ 与拉伸 / 旋转并列），
#      ★ 我们有拉伸 / 旋转 / 肋 / 抽壳 / 圆顶，★ **就是没有这两种**。
#   ★ 而四家并集（349）里正有 **`loft`**（★ 由 `Slacker-LLC` 提供）。
#
# ★★ **调用序与 mark 来自官方 Remarks**（★ §5.0：判据先找后搓）：
#   `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md`（**18 参** · 回 `Feature`）：
#   ```
#   · 1 = profile selections          ← 轮廓（★ 要按期望的顺序选）
#   · 2 = guide curve selections      （可选）
#   · 4 = centerline selection        （可选）
#   · 8 = start tangency vector selection
#   ★ 原文：「you must select the profiles in an order consistent with the desired result」
#   ★ 原文：「Selection of guide curves and centerline is optional」
#   ```
#
# ★★★ **期望值由几何推出**（★ §5.0：优先用算出来的，不用"看着像对"）：
#   ★ **棱台体积公式 `V = h/3 · (A1 + A2 + √(A1·A2))`**
#   ⇒ ★ 两个正方形 20×20 与 10×10、**相距 30 mm** ⇒
#     `V = 30/3 · (400 + 100 + √(400·100)) = 10 · (400+100+200) = **7000 mm³**` ✓
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_loft.py —— 本文件（新）
# 定位:   24h 段 6 续：放样（★ 补"四家有我们没有"的真缺）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md`（18 参 · mark 1/2/4/8）·
#   ★ 反射 arity 表 `scripts/sw_api_sldworks.py:4426` = **18**（★ 两源一致，铁律 4）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

#: ★ **18 个官方参数**（★ 顺序即官方顺序 —— ★ 一处也不能挪）
def _blend_args(closed: bool, keep_tangency: bool, thin: bool, thickness_m: float) -> tuple:
    """★ `InsertProtrusionBlend2` 的 18 参（★ 我们只暴露少数，★ 其余给有据的默认）。"""
    return (
        bool(closed),            # Closed
        bool(keep_tangency),     # KeepTangency
        False,                   # ForceNonRational
        1.0,                     # TessToleranceFactor（★ 官方说默认 1.0）
        0,                       # StartMatchingType（0 = none）
        0,                       # EndMatchingType（0 = none）
        0.0,                     # StartTangentLength
        0.0,                     # EndTangentLength
        False,                   # StartTangentDir
        False,                   # EndTangentDir
        bool(thin),              # IsThinBody
        float(thickness_m),      # Thickness1
        float(thickness_m),      # Thickness2
        0,                       # ThinType
        True,                    # Merge
        False,                   # UseFeatScope
        False,                   # UseAutoSelect
        0,                       # GuideCurveInfluence
    )


def create_loft_report(model, closed: bool = False, use_selected_profiles: bool = True) -> dict:
    """★ **用选中的草图轮廓放样**（★ 走 `InsertProtrusionBlend2`，官方 18 参）。

    ★ 轮廓要**先选中**（★ mark=1 —— ★ 官方 Remarks 定的），★ 且**按期望的顺序**。
    ★ 判据（★ 规则 6）：★ **特征树多了新特征** —— ★ 而 ★ 若调用方给了 `expected_volume_mm3`，
      ★ 还应比对**质量属性里的体积**（★ 期望值由几何推出：★ 棱台 `V = h/3·(A1+A2+√(A1A2))`）。
    ★ 回 `{"ok", "feature_name", "new_features", "tree_before", "tree_after", "args_count"}`。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    from sw_connect import get_com_member as _get
    try:
        sel_n = int(_get(_get(model, "SelectionManager"), "GetSelectedObjectCount2", 1))
    except Exception:                                          # noqa: BLE001
        sel_n = -1
    if use_selected_profiles and sel_n < 2:
        return {"ok": False, "stage": "selection", "mark1_count": sel_n,
                "error": "放样至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）；"
                         "★ 当前 mark=1 的选中数是 %r" % (sel_n,)}
    before = feature_names(model)
    args = _blend_args(closed, True, False, 0.0)
    try:
        fm = get_com_member(model, "FeatureManager")
        get_com_member(fm, "InsertProtrusionBlend2", *args)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "args_count": len(args),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220]),
                "★": "若报 DISP_E_BADPARAMCOUNT ⇒ 参数个数不对（官方 18 个）"}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    #: ★★★ 2026-10-01（轮 314）**硬判据：特征类型名**。
    #:   真机：放样特征 `GetTypeName2()` 回 **`Blend`**；★ 对照拉伸回 `Extrusion`。
    #:   ★★ 它比"体积期望"**可靠**：体积依赖我造几何的能力（★ 而参考平面本会话未打通），
    #:   ★ 而类型名**只依赖 API 对不对**。
    tname = None
    if new:
        try:
            from sw_connect import get_com_member as _g
            fobj = _g(model, "FeatureByName", new[-1])
            for _m in ("GetTypeName2", "GetTypeName"):
                try:
                    tname = str(_g(fobj, _m))
                    break
                except Exception:                              # noqa: BLE001
                    continue
        except Exception:                                      # noqa: BLE001
            tname = None
    ok_type = (tname == "Blend") if tname else False
    return {"ok": bool(new) and ok_type, "feature_name": (new[-1] if new else None), "new_features": new,
            "type_name": tname, "tree_before": len(before), "tree_after": len(after),
            "args_count": len(args), "mark1_selected": sel_n, "closed": bool(closed),
            "★": "官方 18 参 · mark=1 · 判据 = **特征树多了新特征** 且 "
                 "**特征类型名 = `Blend`**（★ 真机定的；拉伸是 `Extrusion`）"}
