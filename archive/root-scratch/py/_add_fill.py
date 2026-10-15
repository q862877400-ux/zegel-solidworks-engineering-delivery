import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface_features.py")
t = p.read_text(encoding="utf-8")

NEW = '''

# ── objective② / 第二个真缺：**填充曲面（`IFeatureManager.InsertFillSurface2`）** ──────────
# ★★★★★ 2026-10-02（轮 388）真机**打通的组合**（★ 事实 305）：
#   ```
#   ① SelectByID2("", "EDGE", <边的中点>, False, **mark = 1**, callout, 0)
#        ⇒ ★ **回 true 且 GetSelectedObjectCount2(-1) = 4**（★ 计数对上 ⇒ 真选中了）✓
#   ② InsertFillSurface2(Resolutions=2, **Options = 1**（swOptimizeSurface）, None, None, None, None)
#        ⇒ ★ **回 Feature（非 None）且特征树多出 `曲面填充1`** ✓
#   ```
# ★★ **两个关键细节**（★ 都是真机撞出来的）：
#   · **mark 必须是 1**（★ 官方 Remarks：`Boundary curves = 1`）——
#     ★ 我先前传 **mark = 4**（★ 那是"约束曲线"的 mark）⇒ `SelectByID2` **回 true 而计数 0**
#     （★ **静默失败** —— 事实 8 那条；★ **mark 值决定成败**）。
#   · **`Options = 1`（`swOptimizeSurface`）** —— 与官方示例一致；
#     ★ 枚举是 **Bitmask**（`swOptimizeSurface=1` · `swTryToFormSolid=2` · `swMergeResult=4` ·
#     `swReverseDirection=8` · `swReverseSurface=16`，★ md 表与反射两源一致）。
# 官方签名依据: `C:\\swapi\\types\\IFeatureManager\\InsertFillSurface2.md`
#   （**6 参** `int Resolutions, int Options, object VPatchBoundaries, object VCurvatureControlType,
#     object VFaces, object VConstraintCurves`；★ `Resolutions` = 1/2/3；
#     ★ Remarks 的 mark 表：Boundary = **1** · contact curvature = 257 · tangent = 513 · 约束曲线 = 4）·
#   官方示例 `Insert_Fill-surface_Feature_Example_CSharp`（★ 两平面各一圆 ⇒ 填充）。
# ★ 规则 2 / 3 / 6：★ 对外只暴露 `resolutions` / `options`；★ 边界边**按中点 + mark 选中**（声明式）；
#   ★ **判据 = 回 `Feature` 非 None 且特征树**增量**非空**（★ 两判据都要 —— 只看 diff 会踩"前面已建"）。

_SW_OPTIMIZE_SURFACE = 1
#: ★ 官方 Remarks 的 mark 表（★ 只列我们用的那个；★ 其余三个待真机验）
MARK_BOUNDARY = 1


def insert_fill_surface_report(model, resolutions: int = 2, *, options: int = _SW_OPTIMIZE_SURFACE,
                               boundary_z: float | None = None) -> dict:
    """★ **填充曲面**（★ 官方 `IFeatureManager.InsertFillSurface2`，**6 参**，★ 回 `Feature`）。

    :param resolutions: 分辨率 **1 / 2 / 3**（★ 越大质量越好，官方原话）。
    :param options: `swFeatureFillSurfaceOptions_e` 的 **Bitmask**；★ 默认 `1`（`swOptimizeSurface`）。
    :param boundary_z: 要填的**那一圈边所在的 z**；★ 留空 = **自动取最高那一圈**（★ 坐标单位是**米**）。
    :returns: `{ok, feature_name, new_features, tree_before, tree_after, points_selected, boundary_z}`
        ★★ **判据 = 回 `Feature` 非 None** **且** **特征树增量非空**（★ 两判据都要）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        res = int(resolutions)
    except (TypeError, ValueError):
        return {"ok": False, "error": "resolutions 必须是整数（1/2/3）"}
    if res not in (1, 2, 3):
        return {"ok": False, "error": "resolutions 只支持 1 / 2 / 3（官方 Remarks）：%r" % resolutions}
    if not (1 <= int(options) <= 31):
        return {"ok": False, "error": "options 超出 Bitmask 范围（1..31）：%r" % options}
    #: ★ 取全部边 ⇒ 按**起点/终点的中点**算 z ⇒ 选出一圈（★ 坐标单位是**米**，★ 不换算）
    edges, mids = [], []
    try:
        for b in (get_com_member(model, "GetBodies2", -1, True) or []):
            for e in (get_com_member(b, "GetEdges") or []):
                try:
                    a = [float(x) for x in get_com_member(
                        get_com_member(e, "GetStartVertex"), "GetPoint")]
                    c = [float(x) for x in get_com_member(
                        get_com_member(e, "GetEndVertex"), "GetPoint")]
                    edges.append(e)
                    mids.append([(a[i] + c[i]) / 2.0 for i in range(3)])
                except Exception:                              # noqa: BLE001
                    continue
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "collect_edges", "error": str(exc)[:140]}
    if not edges:
        return {"ok": False, "stage": "collect_edges", "error": "模型上没有可选边（★ 填充要一个封闭边界）"}
    z = float(boundary_z) if boundary_z is not None else max(m[2] for m in mids)
    picked = [(m, e) for m, e in zip(mids, edges) if abs(m[2] - z) < 1e-9]
    if len(picked) < 3:
        return {"ok": False, "stage": "pick_boundary", "at_z": z,
                "error": "z=%.6f 上只找到 %d 条边（★ 封闭边界至少要 3 条）" % (z, len(picked))}
    #: ★★ **按中点 + mark=1 选中**（★ 官方 Remarks 要的 mark；★ `Select4` 没有 mark 参数 —— 事实 32）
    callout = _empty_callout()
    ext = get_com_member(model, "Extension")
    try:
        model.ClearSelection2(True)
    except Exception:                                          # noqa: BLE001
        pass
    for m, _e in picked:
        try:
            ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, MARK_BOUNDARY, callout, 0)
        except Exception:                                      # noqa: BLE001
            pass
    selected = 0
    try:
        selected = int(get_com_member(get_com_member(model, "SelectionManager"),
                                      "GetSelectedObjectCount2", -1) or 0)
    except Exception:                                          # noqa: BLE001
        selected = 0
    #: ★★ **回读计数为零 ⇒ 选择其实没生效**（★ 事实 8：bool 返回值不可信）⇒ **早退，不假装成功**
    if selected <= 0:
        return {"ok": False, "stage": "select", "points_selected": 0, "boundary_z": z,
                "error": "SelectByID2 选了 %d 条边而回读计数为 0（★ 事实 8：静默失败）" % len(picked),
                "★": "检查 mark 是否为 1（★ 传 4 会静默失败）"}
    before_names = feature_names(model)
    before = len(before_names)
    try:
        feat = get_com_member(get_com_member(model, "FeatureManager"), "InsertFillSurface2",
                              res, int(options), None, None, None, None)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "points_selected": selected,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after_names = feature_names(model)
    new = [n for n in after_names if n not in before_names]
    return {"ok": (feat is not None) and len(after_names) > before,
            "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": before, "tree_after": len(after_names),
            "points_selected": selected, "boundary_z": z,
            "resolutions": res, "options": int(options),
            "★": "判据 = **回 Feature 非 None** **且** **特征树增量非空**（★ 两判据都要）；"
                 "★ 边界按**中点 + mark=1** 选（★ 官方 Remarks；★ 传 mark=4 会静默失败）"}


def _empty_callout():
    """★ 空 `Callout`（`VARIANT(VT_DISPATCH, None)`）—— ★ 事实 33：传 `None` 会报"类型不匹配"。"""
    from sw_connect import create_empty_dispatch_variant
    return create_empty_dispatch_variant()
'''

if "def insert_fill_surface_report" not in t:
    p.write_text(t.rstrip() + NEW, encoding="utf-8")
    print("  已追加 insert_fill_surface_report")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
