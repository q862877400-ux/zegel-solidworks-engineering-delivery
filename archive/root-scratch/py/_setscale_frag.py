

# ── 24h 计划 段 6 续（Spec Kit `162`）：**设视图比例的正确形态** ──────────────────────
# ★★★★★ 2026-10-01（轮 294）真机把三件事一次查清：
#   ① ★ **`ScaleRatio` 回的是**比例的两个数**** —— 真机 `(1.0, 500.0)`（★ 即 **1:500**）·
#      而 `ScaleDecimal` 回 **`0.002`**（★ = 1/500）⇒ ★★ **官方那句** "contain the same information,
#      but use the value in a different way" **正是此意**（★ 一个给"两个数"、一个给"小数"）。
#   ② ★★★ **"写"失败的原因**：`get_com_member(v, "ScaleRatio", (2.0, 1.0))` 报
#      `TypeError: 'tuple' object is not callable` —— ★★ **因为 `get_com_member(obj, name, *args)`
#      的语义是「取或调」：有实参就**一定调用****（★ 于是它在"调用"一个 tuple）。
#      ⇒ ★★★ **正解是 `set_com_member(obj, name, value)`** —— 它的 docstring 写着
#        「设置 COM 成员的**唯一被真机验证通过的形态**：**属性赋值**」。
#   ③ ★ **`UseSheetScale` 真机回 `True`** ⇒ ★★ **该视图**跟随图纸比例**** ——
#      ⇒ ★ **所以"设视图比例"之前要先把"跟随图纸"关掉**（★ 否则设了也可能被图纸覆盖）。
#
# ★ 判据：★ **设完**必须回读**，★ 并判"两个数真的变了"**（★ 规则 6 的精神 —— 不静默成功）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_view.py —— 本段
# 定位:   段 6 续：把"设视图比例"从**取值 helper** 改到**赋值 helper**，并处理 `UseSheetScale` 前置。
# 官方依据: `C:\swapi\types\IView\ScaleRatio.md`（★ ratio 形态 / Array of 2 doubles）·
#          `UseSheetScale.md`（★ 布尔：视图是否跟随图纸比例）·
#          ★ 本项目 `sw_connect.set_com_member` 的真机结论（"唯一被验证通过的形态：属性赋值"）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 2 个函数
# ─────────────────────────────────────────────────────────────────────────────


def set_view_scale_verified(view, scale: float) -> dict:
    """★ **设视图比例（走真机验证过的赋值形态）+ 回读核对**。

    ★ 步骤：① **先把 `UseSheetScale` 关掉**（★ 否则视图跟随图纸，设了也可能无效）；
      ② ★ 用 `set_com_member(view, "ScaleRatio", (scale, 1.0))`（★ **不是** `get_com_member` 带参）；
      ③ ★ **回读**并判"两个数真的变了"。
    ★ 回 `{"ok", "before", "after", "asked", "use_sheet_scale_before"}`；★ **任一步失败都如实写 stage**。
    """
    from sw_connect import set_com_member as _set
    if view is None:
        return {"ok": False, "stage": "view", "error": "view 为 None"}
    #: ★ ① 读前置
    try:
        uss = get_com_member(view, "UseSheetScale")
    except Exception as exc:                                   # noqa: BLE001
        uss = None
        _uss_err = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    else:
        _uss_err = None
    #: ★ ② 关掉"跟随图纸"
    uss_cleared = None
    if uss:
        try:
            _set(view, "UseSheetScale", False)
            uss_cleared = True
        except Exception as exc:                               # noqa: BLE001
            uss_cleared = False
            _uss_set_err = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        else:
            _uss_set_err = None
    #: ★ ③ 读 before
    before = None
    try:
        before = get_com_view_scale_ratio_raw(view)
    except Exception:                                          # noqa: BLE001
        before = None
    #: ★ ④ 赋值（★ 真机验证过的形态）
    try:
        _set(view, "ScaleRatio", (float(scale), 1.0))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "set", "asked": float(scale),
                "before": before, "use_sheet_scale_before": uss,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    #: ★ ⑤ 回读
    try:
        after = get_com_view_scale_ratio_raw(view)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "readback", "asked": float(scale),
                "before": before, "use_sheet_scale_before": uss,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    changed = (before is not None and after is not None and tuple(before) != tuple(after))
    return {"ok": bool(changed), "asked": float(scale), "before": before, "after": after,
            "use_sheet_scale_before": uss, "use_sheet_scale_cleared": uss_cleared,
            "use_sheet_scale_read_error": _uss_err, "use_sheet_scale_set_error": _uss_set_err}


def get_com_view_scale_ratio_raw(view):
    """★ **取 `ScaleRatio` 的原始两个数**（★ 真机 `(1.0, 500.0)` 即 **1:500**）。"""
    if view is None:
        raise ValueError("view 为 None")
    raw = get_com_member(view, "ScaleRatio")
    if raw is None:
        raise RuntimeError("IView.ScaleRatio 回 None")
    try:
        return tuple(float(x) for x in raw)
    except TypeError:
        return (float(raw),)
