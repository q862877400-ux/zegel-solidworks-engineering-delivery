"""★ 探针：B3 余下两项的**参数式入口** —— ★ 角撑板（`InsertGussetFeature3`）· 圆角焊缝（`…Feature3`）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B3-2/B3-3 的真机探针）
# 文件:   tools/probe_spec211_weld_misc.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B3-2「圆角焊缝」** 与 **B3-3「角撑
#           板（焊件）」**。
#   ★★ 两项的官方页都读了（★ 三样 ✓）：
#     · ★★ `IFeatureManager::InsertGussetFeature3` —— ★ **纯参数式 20 参**、
#       ★ **不带 `AccessSelections`**、★ **无 `object` 数组** ✓
#       ★ 参数里有 `BIsProfile`（"True to use a polygon profile, **false to use a triangle profile**"）⇒
#         ★★ **轮廓可能是它自己造的**（★ 不必预选 ✓）
#       ★ `CrvIndex`: "Index of the edge to use if multiple intersecting edges exist" ⇒
#         ★★ **它需要「两条相交的边」** ✓（★ 而边要选 —— ★ 本探针**无选择**下先看行为 ✓）
#     · `IFeatureManager::InsertFilletBeadFeature3` —— ★ **参数式 18 参**，
#       ★★ 其中 `FaceSet1` / `FaceSet2` 是 **`System.object`** ⇒ ★ **数组**（★ 事实 12/33 ✓）
#   ★★★ **本探针的存在理由（★ 最有判别力的一件事）**：
#     ★ **事实 47** 记着 `create_gusset` **到不了建成** ✗ —— ★★ 而那条用的是**属性式
#     `ISMGussetFeatureData`**（★ 事实 36：★ SM 与焊件的 gusset 是**两个不同接口** ✓）
#     ⇒ ★★★ **参数式 `InsertGussetFeature3` 从没试过** ✓ ⇒ ★ **不论成不成，都是「翻案」或「确认」** ✓
# 判据:   ★★ 第一步只"查行为"（★ 与"扫描曲面"/"裁剪焊件"**同型** ✓）：
#     · ★ **抛异常** ⇒ 记下（★ 形态被拒 ✓）
#     · ★ **静默回 `None` / 回对象而无特征** ⇒ ★ **还不算试死**（★ 前置没上 ——
#       ★ 定则：「读到静默」≠「判定试死」✓）
#     · ★ **特征树 +1** ⇒ ★★ **大发现** ✓（★ 参数式翻案 ✓）
# 官方依据: `C:\swapi\types\IFeatureManager\{InsertGussetFeature3,InsertFilletBeadFeatur
#           e3}.md`
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _behaviour(feat, before, after, exc) -> str:
    """★ **行为三分**（★ 三者的下一步完全不同 ✓）"""
    if exc is not None:
        return "★ **抛**：%s: %s" % (type(exc).__name__, str(exc)[:110])
    if len(after) > len(before):
        return "★★★★★ **建成**（★ 新增 %r）⇒ ★ **参数式翻案** ✓" % [
            n for n in after if n not in before]
    if feat is None:
        return "★★ **静默回 `None`** ⇒ ★ **还不算试死**（★ 前置没上 ✓）"
    return "★★ 回对象（`%r`）而**特征树没变** ⇒ ★ 还不算试死（★ 前置没上 ✓）" % (
        getattr(feat, "Name", None),)


def main() -> int:
    import sw_connect
    import sw_weldment as W

    out: dict = {"official": ["IFeatureManager.InsertGussetFeature3",
                              "IFeatureManager.InsertFilletBeadFeature3"],
                 "purpose": "试两项的**参数式入口**（★ 事实 47 那条用的是属性式 SM 接口 ✓）",
                 "step": "第一步：只查行为"}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    #: ══ A · 角撑板（★ `InsertGussetFeature3`，20 参、全标量 ✓）══════════
    model = sw_connect.new_document(sw, "part")
    before = W.feature_names(model)
    fm = sw_connect.get_com_member(model, "FeatureManager")
    exc = None
    feat = None
    try:
        #: ★ 按签名**逐位**给：★ Depth · DirType · LocType · BIsProfile · ProfileD1..D4 ·
        #:   ProfileAngle · BOffset · DProfileOffset · CrvIndex · BReverseDir · BReverseFace ·
        #:   BUseLenDim · ProfileD5 · ProfileD6 · ProfileChamferAngle · BUseLenDimForChamfer ·
        #:   BNeedChamferInGusset ✓（★ 20 位 ✓）
        feat = sw_connect.get_com_member(
            fm, "InsertGussetFeature3",
            float(sw_connect.mm(6.0)),   # Depth（厚度 6mm ⇒ 边界换算 ✓）
            0,                            # DirType
            0,                            # LocType
            False,                        # BIsProfile ⇒ **三角形轮廓**（★ 不让它找多边形 ✓）
            0.0, 0.0, 0.0, 0.0, 0.0,      # ProfileD1..D4 + ProfileAngle
            False, 0.0,                   # BOffset · DProfileOffset
            0,                            # CrvIndex
            False, False,                 # BReverseDir · BReverseFace
            False,                        # BUseLenDim
            0.0, 0.0, 0.0,                # ProfileD5 · ProfileD6 · ProfileChamferAngle
            False, False)                 # BUseLenDimForChamfer · BNeedChamferInGusset
    except Exception as e:                                              # noqa: BLE001
        exc = e
    after = W.feature_names(model)
    out["gusset_param_form"] = {
        "returned_name": getattr(feat, "Name", None) if feat is not None else None,
        "delta": [n for n in after if n not in before],
        "behaviour": _behaviour(feat, before, after, exc)}
    print("★ A 角撑板（InsertGussetFeature3 参数式）⇒ %s" % out["gusset_param_form"]["behaviour"])

    #: ══ B · 圆角焊缝（★ `InsertFilletBeadFeature3`，18 参、两数组 ✓）══════
    model2 = sw_connect.new_document(sw, "part")
    before2 = W.feature_names(model2)
    fm2 = sw_connect.get_com_member(model2, "FeatureManager")
    exc2 = None
    feat2 = None
    try:
        empty = sw_connect.create_empty_dispatch_variant()
        feat2 = sw_connect.get_com_member(
            fm2, "InsertFilletBeadFeature3",
            0, float(sw_connect.mm(5.0)), 0.0,      # Type1 · Size1 · Length1
            0, 0.0, 0.0,                             # PenetrationType1 · PenetrationValue1 · Pitch
            0, 0.0, 0.0,                             # Type2 · Size2 · Length2
            0, 0.0,                                  # PenetrationType2 · PenetrationValue2
            0, 0, empty, 0, empty,                   # Flag · EdgeNum1 · DeSelEdge1 · EdgeNum2 · DeSelEdge2
            empty, empty)                            # FaceSet1 · FaceSet2
    except Exception as e:                                              # noqa: BLE001
        exc2 = e
    after2 = W.feature_names(model2)
    out["fillet_bead_param_form"] = {
        "returned_name": getattr(feat2, "Name", None) if feat2 is not None else None,
        "delta": [n for n in after2 if n not in before2],
        "behaviour": _behaviour(feat2, before2, after2, exc2)}
    print("★ B 圆角焊缝（InsertFilletBeadFeature3 参数式 18 参）⇒ %s"
          % out["fillet_bead_param_form"]["behaviour"])

    p = ROOT / "output" / "spec211-b3-weld-misc.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
