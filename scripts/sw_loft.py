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
# `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md`（**18 参** · 回 `Feature`）
# ：
#   ```
#   · 1 = profile selections          ← 轮廓（★ 要按期望的顺序选）
#   · 2 = guide curve selections      （可选）
#   · 4 = centerline selection        （可选）
#   · 8 = start tangency vector selection
# ★ 原文：「you must select the profiles in an order consistent with the desired result
# 」
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
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md`（18 参 · mark
#  1/2/4/8）·
#   ★ 反射 arity 表 `scripts/sw_api_sldworks.py:4426` = **18**（★ 两源一致，铁律 4）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────


#: ★ **18 个官方参数**（★ 顺序即官方顺序 —— ★ 一处也不能挪）
def _blend_args(
    closed: bool, keep_tangency: bool, thin: bool, thickness_m: float
) -> tuple:
    """★ `InsertProtrusionBlend2` 的 18 参（★ 我们只暴露少数，★ 其余给有据的默认）。"""
    return (
        bool(closed),  # Closed
        bool(keep_tangency),  # KeepTangency
        False,  # ForceNonRational
        1.0,  # TessToleranceFactor（★ 官方说默认 1.0）
        0,  # StartMatchingType（0 = none）
        0,  # EndMatchingType（0 = none）
        0.0,  # StartTangentLength
        0.0,  # EndTangentLength
        False,  # StartTangentDir
        False,  # EndTangentDir
        bool(thin),  # IsThinBody
        float(thickness_m),  # Thickness1
        float(thickness_m),  # Thickness2
        0,  # ThinType
        True,  # Merge
        False,  # UseFeatScope
        False,  # UseAutoSelect
        0,  # GuideCurveInfluence
    )


def create_loft_report(
    model, closed: bool = False, use_selected_profiles: bool = True
) -> dict:
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
    except Exception:  # noqa: BLE001
        sel_n = -1
    if use_selected_profiles and sel_n < 2:
        return {
            "ok": False,
            "stage": "selection",
            "mark1_count": sel_n,
            "error": "放样至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）；"
            "★ 当前 mark=1 的选中数是 %r" % (sel_n,),
        }
    before = feature_names(model)
    args = _blend_args(closed, True, False, 0.0)
    try:
        fm = get_com_member(model, "FeatureManager")
        get_com_member(fm, "InsertProtrusionBlend2", *args)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "stage": "call",
            "args_count": len(args),
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:220]),
            "★": "若报 DISP_E_BADPARAMCOUNT ⇒ 参数个数不对（官方 18 个）",
        }
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
                except Exception:  # noqa: BLE001
                    continue
        except Exception:  # noqa: BLE001
            tname = None
    ok_type = (tname == "Blend") if tname else False
    return {
        "ok": bool(new) and ok_type,
        "feature_name": (new[-1] if new else None),
        "new_features": new,
        "type_name": tname,
        "tree_before": len(before),
        "tree_after": len(after),
        "args_count": len(args),
        "mark1_selected": sel_n,
        "closed": bool(closed),
        "★": "官方 18 参 · mark=1 · 判据 = **特征树多了新特征** 且 "
        "**特征类型名 = `Blend`**（★ 真机定的；拉伸是 `Extrusion`）",
    }


def _cut_blend_args(
    closed: bool, keep_tangency: bool, thin: bool, thickness_m: float
) -> tuple:
    """★ `InsertCutBlend` 的 **12 参**（★ 顺序即官方顺序）。

    ★★★★ 2026-10-03（轮 561）★ **官方签名逐字**（`C:\\swapi\\types\\IFeatureManager\\InsertCutBlend.md`）：
      ```
      Feature InsertCutBlend(bool Closed, bool KeepTangency, bool ForceNonRational,
                             double TessToleranceFactor, short StartMatchingType,
                             short EndMatchingType, bool IsThinBody, double Thickness1,
                             double Thickness2, short ThinType,
                             bool UseFeatScope, bool UseAutoSelect)
      ```
    ★★ **而它与 `InsertProtrusionBlend2` 的 18 参是**同一族** ——
      ★ 12 参 = 18 参里**去掉 6 个**（`Start/EndTangentLength` · `Start/EndTangentDir` ·
      `Merge` · `GuideCurveInfluence`）**，★ 其余**逐位对齐** ✓
      ★ 而**两者的 `## Remarks` 逐字同一套**（剖面按顺序选 · 强烈建议引导线 · **mark 1/2/4**）。
    ★ 故本函数**照 `_blend_args` 的形状**写，★ 删除那 6 个位（★ 而不是另立一套默认值）。
    """
    return (
        bool(closed),  # Closed
        bool(keep_tangency),  # KeepTangency
        False,  # ForceNonRational
        1.0,  # TessToleranceFactor（★ 官方说默认 1.0）
        0,  # StartMatchingType（0 = none）
        0,  # EndMatchingType（0 = none）
        bool(thin),  # IsThinBody
        float(thickness_m),  # Thickness1
        float(thickness_m),  # Thickness2
        0,  # ThinType
        False,  # UseFeatScope
        False,  # UseAutoSelect
    )


def create_loft_cut_report(
    model, closed: bool = False, use_selected_profiles: bool = True
) -> dict:
    """★ **用选中的草图轮廓放样切除**（★ 走 `InsertCutBlend`，官方 **12 参**）。

    ★★★★ 2026-10-03（轮 561）★ 台账「**放样切除**」与「**边界切除**」两条的入口都是它。
      ★ 而官方 `InsertCutBlend.md` **头**上那句是 **「未标废弃」** 的
      （★ 对照：`InsertProtrusionSwept4` / `InsertFreeform` / `InsertFlattenSurface` /
      `InsertUntrimSurface` **四条都标了 `Obsolete`** —— ★ 见事实 433 的地图）✓

    ★ 前置与判据与 `create_loft_report` **同一套**（★ 官方 Remarks 逐字相同）：
      ★ 轮廓要**先选中**（**mark = 1**）、★ 且**按期望的顺序**；★ 引导线 mark=2、中心线 mark=4。
      ★ 判据 = **特征树多了新特征** **且** **类型名 = `Blend`**（★ 真机定的；拉伸是 `Extrusion`）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    #: \u2605 \u672c\u6a21\u5757**\u9876\u4e0a\u5df2\u7ecf\u5bfc\u597d**\uff08`from sw_f
    #: eature_readback import feature_names`\u3001
    #: `from sw_connect import get_com_member`\uff09\u2014\u2014 \u2605 **\u4e0d\u8981\u
    #: 518d\u5c40\u90e8\u91cd\u5bfc**\u3002
    #:   \u2605 2026-10-03\uff08\u8f6e 561\uff09\u6211\u7b2c\u4e00\u7248\u5199\u4e86
    #: `from sw_connect import get_com_member, feature_names` \u21d2 **`ImportError`** \
    #: u26a0
    #: \uff08\u2605 `feature_names` **\u4e0d\u5728 `sw_connect` \u91cc** \u2014\u2014 \u
    #: 2605 \u800c\u90a3\u4e2a\u9519**\u770b\u4e0d\u51fa\u662f\u5bfc\u5165\u7684\u95ee\u
    #: 9898**\uff09\u3002
    if not use_selected_profiles:
        return {
            "ok": False,
            "error": "本包装要求 use_selected_profiles=True（★ 官方 Remarks 要求先选）",
        }
    sel_n = 0
    try:
        sm = get_com_member(model, "SelectionManager")
        sel_n = int(get_com_member(sm, "GetSelectedObjectCount2", 1) or 0)
    except Exception:  # noqa: BLE001
        sel_n = 0
    if sel_n < 2:
        return {
            "ok": False,
            "stage": "selection",
            "mark1_count": sel_n,
            "error": "放样切除至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）；"
            "★ 当前 mark=1 的选中数是 %r" % (sel_n,),
        }
    before = feature_names(model)
    args = _cut_blend_args(closed, True, False, 0.0)
    try:
        fm = get_com_member(model, "FeatureManager")
        get_com_member(fm, "InsertCutBlend", *args)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "stage": "call",
            "args_count": len(args),
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:220]),
            "★": "若报 DISP_E_BADPARAMCOUNT ⇒ 参数个数不对（官方 12 个）",
        }
    after = feature_names(model)
    new = [n for n in after if n not in before]
    tname = None
    if new:
        try:
            fobj = get_com_member(model, "FeatureByName", new[-1])
            for _m in ("GetTypeName2", "GetTypeName"):
                try:
                    tname = str(get_com_member(fobj, _m))
                    break
                except Exception:  # noqa: BLE001
                    continue
        except Exception:  # noqa: BLE001
            tname = None
    #: ★★★ 2026-10-03（轮 561）**判据修正**：切与不切**类型名不同** ⚠
    #:   · 放样**凸台**（`InsertProtrusionBlend2`）⇒ 类型名 **`Blend`**
    #: · 放样**切除**（`InsertCutBlend`）        ⇒ 类型名 **`BlendCut`**  ← ★ **真机定的
    #: **
    #: ★ 我第一版照凸台抄成 `== "Blend"` ⇒ ★ **对已建成的 `切除-放样1` 判了 `ok=False`**
    #:  ⚠
    #:     （★ 而那正是**事实 420 / 431 那一类**：**失败在判据、不在 API**）
    #:   ★★★ 与**事实 429**（旋转切除用 `IsCut=True`）**同一族**：★ **"切"会换类型名**。
    ok_type = (tname in ("Blend", "BlendCut")) if tname else False
    return {
        "ok": bool(new) and ok_type,
        "feature_name": (new[-1] if new else None),
        "new_features": new,
        "type_name": tname,
        "tree_before": len(before),
        "tree_after": len(after),
        "args_count": len(args),
        "mark1_selected": sel_n,
        "closed": bool(closed),
        "★": "官方 **12 参** · mark=1 · 判据 = **特征树多了新特征** 且 "
        "**类型名 = `Blend`**（★ 与 `InsertProtrusionBlend2` 同一族、同一套 mark）",
    }
