"""★ 圆角焊缝（官方 `IFeatureManager::InsertFilletBeadFeature2`，16 参）—— 选实体 + 回读判据。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（选实体沿用 scripts/sw_selection_spec.py；特征计数沿用 sw_net_blend 的助手）
# 文件:   scripts/sw_weld_bead.py
# 定位:   ★ 规格 220（续）第 46 轮 —— 补 **焊件/圆角焊缝**（生成器关键词 `("fillet_bead","weld_bead")`）✓
# 官方依据: ★★ **三样都读过**（★ 铁律 4）：
#   · 签名 `C:\swapi\types\IFeatureManager\InsertFilletBeadFeature2.md` 第 14 行**逐字 16 参** ✓
#   · 第 12 行**逐字**：★「…also fills the gap between the **pre-selected part bodies**, if any.」
#     ⇒ ★★ **前置 = 预先选中的实体** ✓（★ **不是"面集合"** ✗ —— ★ 台账那句二手概括是错的 ✓）
#   · 参数语义（★ 逐字抄）：★ `Type1/2` 0=Full length·1=Intermittent·2=Staggered ·
#     ★ `PenetrationType1/2` 0=Full·1=Partial·2=No penetration · ★ `Flag` 0/1/2/3 ·
#     ★ `EdgeNum1/2` = 各侧**相交边条数** · ★ `DeSelEdge1/2` = 各侧相交边**选中(0)/取消(1) 的数组** ✓
#   · ★★ **v1 已 `Obsolete`**（★ 官方第 12 行逐字「Superseded by …Feature2」）⇒ ★ 只用 **v2** ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ★★ 判据：★ **特征树回读增量 ≥ 1**（★ 事实 8：★ 返回值不可信 —— ★ 边界特征上刚栽过 ✓）
# ★★ 等级如实：★★ 尚未真机验证 ⇒ ★ 台账**不提 level**（★ 红线⑥）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any

#: ★ 官方枚举（★ 逐字抄自上页参数表）✓
BEAD_TYPE = {"full_length": 0, "intermittent": 1, "staggered": 2}
PENETRATION_TYPE = {"full": 0, "partial": 1, "no": 2}
FLAG = {"one_side": 0, "two_side": 1, "tangent": 2, "two_side_tangent": 3}

_MM = 0.001                                                                        #: ★ 毫米 → 米（事实 2）


def _feature_count(model) -> int:
    """★ 特征树计数 —— ★ 本绑定里 `GetFeatureCount` 是**属性**（★ 事实：调 `()` 会报 not callable）✓"""
    attr = getattr(model, "GetFeatureCount", None)
    if attr is None:
        return -1
    if callable(attr):
        try:
            return int(attr())
        except TypeError:
            pass
    try:
        return int(attr)
    except (TypeError, ValueError):
        return -1


def _select_edge_by_index(model, edge_index: int, append: bool) -> dict[str, Any]:
    """★ 按**边序号**选中一条边（★ 声明式，★ 不收坐标 —— 规则 3）⇒ ★ 回读报告 ✓

    ★★ 为什么走**按对象选**：★ 官方第 12 行说前置是 `pre-selected part bodies` ✓；
      ★ 而本仓真机已定案（★ 事实 32 + 边界特征实测）：★ **`SelectByID2` 按点对某些面/边永远选不上** ✗
      ⇒ ★ 必须 **`IEntity.Select4(Append, Callout)`** ✓
    """
    import sw_selection_spec as _SS
    import sw_part as _sp

    edges = []
    _bi = 0
    while _bi <= 32:                                                               #: ★ 遍历所有体（★ 两次拉伸会有多个体 ✓）
        try:
            _b = list(_SS.entities_on_body(model, "EDGE", body_index=_bi) or [])
        except Exception:                                                          # noqa: BLE001
            break
        if not _b:
            break
        edges.extend(_b)
        _bi += 1
    if edge_index < 0 or edge_index >= len(edges):
        raise RuntimeError("★ 边序号越界：edge_index=%r，共 %d 条边" % (edge_index, len(edges)))
    before = int(model.SelectionManager.GetSelectedObjectCount2(-1))
    ok = edges[edge_index].Select4(bool(append), _sp._empty_callout())
    cnt = int(model.SelectionManager.GetSelectedObjectCount2(-1))
    return {"ok": bool(cnt > before), "returned": bool(ok), "selection_count": cnt,
            "edge_count": len(edges)}


def insert_fillet_bead_report(
    model,
    *,
    edge_index_1: int = 0,
    edge_index_2: int = 1,
    size_mm: float = 5.0,
    length_mm: float = 0.0,
    bead_type_1: int = 0,
    bead_type_2: int = 0,
    penetration_type_1: int = 0,
    penetration_type_2: int = 0,
    penetration_value_1: float = 0.0,
    penetration_value_2: float = 0.0,
    pitch_mm: float = 0.0,
    flag: int = 1,
) -> dict[str, Any]:
    """★ 插一条**圆角焊缝**（★ 官方 `InsertFilletBeadFeature2`）⇒ ★ 回一份**回读报告** ✓

    ★★ 判据：★ **特征树回读增量 ≥ 1**（★ 事实 8）✓ —— ★ **不看返回值**（★ 边界特征上栽过 ✗）
    ★★ 前置：★ **先在本函数内选中实体（边）** ✓ —— ★ 本仓事实 503：★ 注入解析器会清空选区，
      ★ 所以"调用方先选好"经 MCP 表面**不可能成立** ⇒ ★ 必须自选 ✓
    ★ 单位：★ 入参按**毫米**，★ 内部转**米**（★ 事实 2）✓
    """
    import sw_part as _sp

    steps: list[dict[str, Any]] = []
    try:
        model.ClearSelection2(True)
    except Exception:                                                              # noqa: BLE001
        pass
    before = _feature_count(model)

    s1 = _select_edge_by_index(model, edge_index_1, False)
    steps.append({"step": "select_edge_1", **s1})
    s2 = _select_edge_by_index(model, edge_index_2, True)
    steps.append({"step": "select_edge_2", **s2})
    if s1["selection_count"] < 1 or s2["selection_count"] < 2:
        return {"ok": False, "error": "★ 选实体没落到 2 条边（判据是回读计数，不是 bool）",
                "selection_counts": [s1["selection_count"], s2["selection_count"]],
                "feature_count_before": before, "steps": steps}

    fm = model.FeatureManager
    feat = fm.InsertFilletBeadFeature2(
        int(bead_type_1),                                              #: ★ Type1（0/1/2 ✓）
        float(size_mm) * _MM,                                          #: ★ Size1（米 ✓）
        float(length_mm) * _MM,                                        #: ★ Length1
        int(penetration_type_1),                                       #: ★ PenetrationType1（0/1/2 ✓）
        float(penetration_value_1) * _MM,                              #: ★ PenetrationValue1
        float(pitch_mm) * _MM,                                         #: ★ Pitch
        int(bead_type_2),                                              #: ★ Type2
        float(size_mm) * _MM,                                          #: ★ Size2
        float(length_mm) * _MM,                                        #: ★ Length2
        int(penetration_type_2),                                       #: ★ PenetrationType2
        float(penetration_value_2) * _MM,                              #: ★ PenetrationValue2
        int(flag),                                                     #: ★ Flag（0/1/2/3 ✓）
        1, (0,),                                                       #: ★ EdgeNum1 + DeSelEdge1（数组 ✓）
        1, (0,),                                                       #: ★ EdgeNum2 + DeSelEdge2（数组 ✓）
    )
    after = _feature_count(model)
    steps.append({"step": "InsertFilletBeadFeature2", "returned": feat is not None,
                  "before": before, "after": after})

    return {
        #: ★★ 判据**只留回读**（★ 事实 8）—— ★ 返回值 `None` **不代表失败** ✓（★ 边界特征实测 ✓）
        "ok": after > before,
        "size_mm": float(size_mm),
        "flag": int(flag),
        "feature_count_before": before,
        "feature_count_after": after,
        "steps": steps,
        "official": "IFeatureManager::InsertFilletBeadFeature2（★ v1 已 Obsolete ⇒ 只用 v2 ✓）",
        "units": "★ 入参毫米；COM 侧米（事实 2）✓",
        "verification": "stitched —— ★ 尚未真机验证（★ 红线⑥：level 只按真机证据变）",
    }
