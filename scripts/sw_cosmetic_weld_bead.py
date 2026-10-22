"""★ 装饰焊缝（官方 `IFeatureManager::InsertCosmeticWeldBead`，**一个参数**）—— 选两个面 + 回读判据。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（取面沿用 sw_selection_spec；选实体沿用 IEntity.Select4 的既有定案
# ）
# 文件:   scripts/sw_cosmetic_weld_bead.py
# 定位:   ★ 规格 220（续）第 55 轮 —— ★ **焊件/圆角焊缝的换路实现**（★ 事实 53：≥3 次
#           同处 ⇒ 换做法 ✓）
# 官方依据: ★★ **三样都读过**（★ 铁律 4）：
#   · 签名 `C:\swapi\types\IFeatureManager\InsertCosmeticWeldBead.md`：★ `Feature
#     InsertCosmeticWeldBead( System.double WeldSize )` —— ★★ **只有一个参数** ✓
# · ★ **官方示例的调用序**（★ `C:\swapi\examples\Insert_Cosmetic_Weld_Bead_Example_CShar
# p.md`
#     第 47–52 行**逐字**）：★ **选两个面（mark 0）⇒ `InsertCosmeticWeldBead(0.51)` ⇒
#     `ClearSelection2(true)`** ✓ —— ★★ **示例给的就是这条最短路径** ✓
# · `## Remarks`（★ `InsertCosmeticWeldBead2` 页）：★ `WeldGeometry` 模式用 faces 或 edg
# es ·
#     ★ 两侧必须**同类型** · ★ marks **4/8**；★ 而 v1 示例里用 **mark 0** ✓
# ★★ 关于 `Obsolete`：★ 官方把 v1 标为 `Obsolete` ✗ —— ★ 但**示例本身用的就是它** ✓
#   ⇒ ★ **"标废弃" ≠ "已移除"** ✓（★ 且它能用最小的契约把事办成 ✓）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ★★ 判据：★ **特征树回读增量 ≥ 1**（★ 事实 8：★ 返回值不可信 —— ★ 边界特征上刚栽过 ✓）
# ★★ 等级如实：★★ 尚未真机验证 ⇒ ★ 台账**不提 level**（★ 红线⑥）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any

_MM = 0.001                                                                        #: ★ 毫米 → 米（事实 2）


#: ★ 2026-10-22（仓库统一化）：`_feature_count` 原在本文件与 `sw_net_blend.py` /
#:   `sw_weld_bead.py` 各有一份（逻辑逐字相同）⇒ 收敛到 `scripts/sw_feature_tree.py` ✓
try:
    from .sw_feature_tree import feature_count as _feature_count
except ImportError:
    from sw_feature_tree import feature_count as _feature_count


def _faces_all_bodies(model) -> list[Any]:
    """★ 遍历**所有体**取面（★ 两块凸台是两个独立的体 —— ★ 边界特征真机读数 ✓）"""
    import sw_selection_spec as _SS

    faces: list[Any] = []
    _bi = 0
    while _bi <= 32:                                                               #: ★ 兜底，防死循环
        try:
            _b = list(_SS.entities_on_body(model, "FACE", body_index=_bi) or [])
        except Exception:                                                          # noqa: BLE001
            break
        if not _b:
            break
        faces.extend(_b)
        _bi += 1
    return faces


def insert_cosmetic_weld_bead_report(
    model,
    *,
    face_index_1: int = 0,
    face_index_2: int = 1,
    weld_size_mm: float = 12.95,               #: ★ 官方示例是 0.51 **英寸** ≈ 12.95 mm ✓
) -> dict[str, Any]:
    """★ 插一条**装饰焊缝**（★ 官方 `InsertCosmeticWeldBead(WeldSize)`，★ **一个参数**）✓

    ★★ 调用序**照官方示例逐字**：★ ① 选两个面（★ 示例按点选 ✗ ⇒ ★ 我用 `Select4` ✓ 因为
      **按点对某些面永远选不上** —— ★ 219 真机定案 ✓）② `InsertCosmeticWeldBead(尺寸)` ③ 清选区 ✓
    ★★ 判据：★ **特征树回读增量 ≥ 1**（★ 事实 8）✓ —— ★ **不看返回值** ✓
    ★ 单位：★ 入参**毫米**，★ 内部转米（★ 事实 2）✓
    """
    import sw_part as _sp

    steps: list[dict[str, Any]] = []
    try:
        model.ClearSelection2(True)
    except Exception:                                                              # noqa: BLE001
        pass
    before = _feature_count(model)

    faces = _faces_all_bodies(model)
    steps.append({"step": "faces", "count": len(faces)})
    for i, idx in enumerate((face_index_1, face_index_2)):
        if idx < 0 or idx >= len(faces):
            return {"ok": False, "error": "★ 面序号越界：%r（共 %d 个面）" % (idx, len(faces)),
                    "feature_count_before": before, "steps": steps}
        f = faces[idx]
        try:
            f.Select4(bool(i == 1), _sp._empty_callout())                          #: ★ 第二个 append ✓
        except Exception as exc:                                                   # noqa: BLE001
            steps.append({"step": "select_face_%d" % i, "error": str(exc)[:140]})
        steps.append({"step": "select_face_%d" % i, "index": idx,
                      "selection_count": int(model.SelectionManager.GetSelectedObjectCount2(-1))})
    #: ★★ 守卫用**回读计数**：★ 两个面都要在选区里（★ 事实 8 ✓）
    cnt = int(model.SelectionManager.GetSelectedObjectCount2(-1))
    if cnt < 2:
        return {"ok": False, "error": "★ 选面只到 %d（判据是回读计数，不是 bool）" % cnt,
                "selection_count": cnt, "feature_count_before": before, "steps": steps}

    feat = model.FeatureManager.InsertCosmeticWeldBead(float(weld_size_mm) * _MM)
    after = _feature_count(model)
    steps.append({"step": "InsertCosmeticWeldBead", "returned": feat is not None,
                  "before": before, "after": after})

    return {
        #: ★★ 判据**只留回读**（★ 事实 8）—— ★ 返回值 `None` **不代表失败** ✓（★ 边界特
        #: 征实测 ✓）
        "ok": after > before,
        "weld_size_mm": float(weld_size_mm),
        "feature_count_before": before,
        "feature_count_after": after,
        "steps": steps,
        "official": "IFeatureManager::InsertCosmeticWeldBead（★ v1 标 Obsolete，★ 但官方示例用的就是它 ✓）",
        "units": "★ 入参毫米；COM 侧米（事实 2）✓",
        #: ★★★ 2026-10-07（规格 220 续 · 第 58 轮）★ **等级按真机证据提上来**（★ 红线⑥ 
        #: 的正面用例 ✓）
        #: ★ 真机逐字（`tools/probe_spec220_cosmetic_bead.py`）：★ **6.38 s** · ★ **0 弹
        #: 窗** · ★
        #:   `sw_alive: true` · ★★ **`faces=[0,7]` ⇒ `ok=True`** · ★★ **特征树 22 → 23** ✓
        #:   ★ 前置（★ 真机验过 ✓）：★ **两个体 + 贴合 + 不合并**（★ `merge=False` ✓）
        #: ★★ 判据 = **特征树回读增量 ≥ 1**（★ 事实 8 ✓）；★ 返回值 `None` **不代表失败*
        #: * ✓
        "verification": "verified —— ★ 真机建成（faces=[0,7] · 特征树 22→23 · 6.38 s · 0 弹窗）"
                        "（★ 规格 220 续 第 57/58 轮；判据 = 特征树回读增量，事实 8）",
    }
