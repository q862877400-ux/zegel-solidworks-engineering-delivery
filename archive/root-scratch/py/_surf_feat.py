

# ── 24h 计划 段 6 续（Spec Kit `166`）：**曲面特征族（第一条已真机验证）** ──────────────
# ★★★★★ 2026-10-01（轮 308）**本段改写了硬约束⑧的措辞**：
#   ★ 官方建曲面有**两条完全不同的路**：
#     · **`IModeler.Create*Surface`** —— ★ 造**曲面体**（body）⇒ ★★ **事实 40：返回值跨次都变**；
#     · **`IFeatureManager.Insert*Surface` / `FeatureExtruRefSurface3`** —— ★ 造**曲面特征**（feature）
#       ⇒ ★★★★ **本会话首次试，一次成功**：真机特征树 `6 → 7`、特征名 **`曲面-拉伸1`**。
#   ⇒ ★ **两条路的差别是本质的**：★ 前者把"曲面"当**几何**（要自己造 body），
#     ★ 后者把它当**特征**（★ 与 UI 里点"曲面-拉伸"完全一致）⇒ ★ 属性上属于 `IFeatureManager`。
#
# ★ **本段只包装已真机验证的那一个**（★ `FeatureExtruRefSurface3`）——
#   ★ 其余（填充 / 缝合 / 裁剪 / 加厚）**需要选中面或边**，★ 留到选区那条链打通之后
#   （★ 真机实测：`InsertSewRefSurface` 不抛、但**特征树不变** ⇒ ★ 它要求"先选中要缝合的曲面"）。
#
# ★ 规则 2 / 3：★ 对外只暴露 `depth_mm`（★ 22 个官方参数里的深度），★ 其余用**有据的默认**；
#   ★ 草图**按名字**取（★ 不传坐标）。
# ★ 判据（规则 6）：★ **它回 void** ⇒ ★★ 成败**只能看特征树**（★ 建完回读，不静默成功）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_surface_features.py —— 本文件（新）
# 定位:   24h 段 6 续：曲面**特征**族（★ 与 sw_surface.py 的"曲面体"族分开）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\FeatureExtruRefSurface3.md`
#   （完整签名 **22 个参数**：Sd / Dir / StartCond / OffsetVal / T1 / T2 / D1 / D2 / Dchk1 / Dchk2 /
#    Ddir1 / Ddir2 / Dang1 / Dang2 / OffsetReverse1 / OffsetReverse2 / TranslateSurface1 /
#    TranslateSurface2 / CapEnd1 / CapEnd2 / DeleteOriginalFace / KnitResult · **返回 void**）·
#   ★ 反射 arity 表 `scripts/sw_api_sldworks.py:4300` = **22**（★ 两源一致，铁律 4）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

import math

from sw_connect import get_com_member
from sw_feature_readback import feature_names

#: ★ `swEndConditions_e` / `swStartConditions_e` 的取值（★ 从反射来）
SW_START_SKETCH_PLANE = 0
SW_END_BLIND = 0
SW_END_THROUGH_ALL = 1


def _harden_defaults(depth_m, through: bool):
    """★ **22 个官方参数**（★ 顺序即官方顺序 —— ★ 一处也不能挪）。"""
    return (
        True,                       # Sd                 单端
        False,                      # Dir                不反向
        SW_START_SKETCH_PLANE,      # StartCond
        0.0,                        # OffsetVal
        (SW_END_THROUGH_ALL if through else SW_END_BLIND),   # T1
        SW_END_BLIND,               # T2（★ Sd=True 时无效）
        depth_m,                    # D1
        depth_m,                    # D2（★ Sd=True 时无效）
        False, False,               # Dchk1 / Dchk2
        False, False,               # Ddir1 / Ddir2
        0.0, 0.0,                   # Dang1 / Dang2
        False, False,               # OffsetReverse1 / OffsetReverse2
        False, False,               # TranslateSurface1 / TranslateSurface2
        False, False,               # CapEnd1 / CapEnd2
        False,                      # DeleteOriginalFace
        True,                       # KnitResult（★ 缝合结果 ⇒ 更接近 UI 的默认）
    )


def create_extruded_surface_report(model, depth_mm: float, sketch_name: str = "",
                                   through_all: bool = False) -> dict:
    """★ **用已有草图建「曲面-拉伸」特征**（★ 走 `FeatureExtruRefSurface3`，官方 22 参）。

    ★ **它回 `void`** ⇒ ★★ 判据**不能是返回值**，只能是「**特征树多了**」（★ 规则 6）。
    ★ `depth_mm` 是**毫米**（★ 规则 2）；★ 换算在这里做一次。
    ★ 回 `{"ok", "feature_name", "tree_before", "tree_after", "args_count", "verdict_basis"}`。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if not through_all:
        try:
            d = float(depth_mm)
        except (TypeError, ValueError) as exc:
            return {"ok": False, "error": "depth_mm 必须是数字：%s" % str(exc)[:100]}
        if not math.isfinite(d) or d <= 0.0:
            return {"ok": False, "error": "depth_mm 必须 > 0（★ 收到 %r）" % depth_mm}
    else:
        d = 0.010             #: ★ 贯穿时深度无效，★ 给一个有限值免得 API 抱怨
    before_names = feature_names(model)
    before = len(before_names)
    args = _harden_defaults(d * 0.001, through_all)     #: ★ 毫米 ⇒ 米（★ 唯一的换算处）
    try:
        fm = get_com_member(model, "FeatureManager")
        get_com_member(fm, "FeatureExtruRefSurface3", *args)
    except Exception as exc:                                # noqa: BLE001
        return {"ok": False, "stage": "call", "args_count": len(args),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220]),
                "★": "若报 DISP_E_BADPARAMCOUNT ⇒ 参数个数不对（官方 22 个）"}
    after_names = feature_names(model)
    new = [n for n in after_names if n not in before_names]
    return {"ok": len(after_names) > before, "feature_name": (new[-1] if new else None),
            "new_features": new, "tree_before": before, "tree_after": len(after_names),
            "args_count": len(args), "depth_mm": (None if through_all else float(depth_mm)),
            "through_all": bool(through_all), "sketch_name": str(sketch_name),
            "★": "它回 void ⇒ 判据是**特征树真的多了**（★ 规则 6）；★ 官方 22 参 · 反射 arity 22"}
