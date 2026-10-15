

# ── `create_axis_report`（★ 参考轴 —— 环形阵列的前置）──────────────────────────────
# ★★★ 2026-10-01（轮 317）三个真机坑（★ 见 `tool_specs_batch49.py` 的头注）：
#   ① **入口在 `IModelDoc2` 上，不在 `IFeatureManager` 上**（★ CHM 定的；★ 调后者报
#      `AttributeError: <unknown>.InsertAxis2`）；
#   ② **它回 `bool` 而不是 `Feature`** ⇒ ★ **判据要数特征树**（★ 读 `.Name` 会崩）；
#   ③ ★ 环形阵列的官方 mark 表要求 `1 = 方向轴` ⇒ ★ 没有轴就阵列不了。
# 依据: ★ CHM `IModelDoc2~InsertAxis2.html` · ★ 反射 `sw_api_sldworks.py:6267`（arity = 1）·
#   真机 `output/pattern-axis-evidence.json`（★ `InsertAxis2` 回 True · 出现 `基准轴1` ·
#   `阵列(圆周)1` type=`CirPattern`）· `output/mirror-fixed-evidence.json`（★ `镜向1` type=`MirrorPattern`）
# ─────────────────────────────────────────────────────────────────────────────


def create_axis_report(model, reverse: bool = True) -> dict:
    """★ **从当前选中的几何建参考轴**（`IModelDoc2.InsertAxis2`）。

    ★ 真机事实（2026-10-01 · 轮 317）：
      · ★ **入口在 `IModelDoc2`** —— ★ 调 `FeatureManager.InsertAxis2` 报 `<unknown>.InsertAxis2`；
      · ★ **返回 `bool`** —— ★ 所以**判据是"特征树多了新特征"**，★ 不是"返回值有 Name"；
      · ★ 阵列要用它：★ 官方 mark 表 `1 = 方向轴`。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    from sw_connect import get_com_member as _get
    try:
        sel_n = int(_get(_get(model, "SelectionManager"), "GetSelectedObjectCount2", -1))
    except Exception:                                          # noqa: BLE001
        sel_n = -1
    if sel_n == 0:
        return {"ok": False, "stage": "selection", "selected_count": sel_n,
                "error": "建轴要先选中几何（★ 圆柱面 / 圆锥面 / 两点等；★ 面没有名字，"
                         "按面上的对象选 —— 事实 32）"}
    before = feature_names(model)
    #: ★ 入口在 IModelDoc2 上（★ 不是 FeatureManager）—— ★ 真机定的
    try:
        ret = _get(model, "InsertAxis2", bool(reverse))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "selected_count": sel_n,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                "★": "⚠ 若报 `<unknown>.InsertAxis2` ⇒ 入口用错了（★ 该在 IModelDoc2 上，不是 FeatureManager）"}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(ret) and bool(new), "returned": repr(ret)[:20], "new_features": new,
            "axis_name": (new[-1] if new else None), "tree_before": len(before),
            "tree_after": len(after), "selected_count": sel_n, "reverse": bool(reverse),
            "★": "入口 = `IModelDoc2.InsertAxis2`（★ 不是 FeatureManager）· 回 `bool` ⇒ "
                 "★ 判据 = **特征树多了新特征**（★ 不要读返回值的 `.Name`）"}
