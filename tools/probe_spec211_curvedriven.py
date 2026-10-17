"""★ 探针：`FeatureLocalCurveDrivenPattern` —— ★ 一次试两项（曲线驱动阵列 / 零部件阵列）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B5 翻案后的真机探针）
# 文件:   tools/probe_spec211_curvedriven.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps`。★★ **本探针是一次翻案的兑现** ——
#   ★ 我 B5 原判「曲线驱动阵列 = 不做」，★ 依据链是：★ ① `IModelDoc2::FeatureCurvePattern`
#   **已 `Obsolete`** ✗ · ★ ② 现代入口 = `CreateFeature` + `ICurveDrivenPatternFeatureData`
#   （**属性式**）✗ · ★ ③ 那个 Data **带 `AccessSelections`** ✗ · ★ ④ **事实 47** ⇒ 到不了建成 ✗
#   ★★★ 而那四步**只覆盖了"别人家的入口"** ✗ —— ★★ **漏了这个名字里就写着 `CurveDriven` 的** ✓
#   ⇒ ★★★★ **「曲线驱动阵列」与「零部件阵列」共用它**（★ 覆盖表却分在**特征域/装配域**两行 ✓）
# 官方依据（★ 三样逐字读过）：
#   · `C:\swapi\types\IFeatureManager\FeatureLocalCurveDrivenPattern.md`
#     `Feature FeatureLocalCurveDrivenPattern( bool FlipDir1, int Num1, bool EqualSpacing1,
#      double Spacing1, int ReferencePoint, int CurveMethod, int AlignMethod, bool Direction2,
#      bool FlipDir2, int Num2, bool EqualSpacing2, double Spacing2, bool PatternSeedOnly )`
#     ★ **13 参 · 纯参数式 · 不带 `AccessSelections`** ✓
#   · ★★★ 同页 `## Remarks` **给了完整 mark 表**（★ 第 ③ 样的价值）：
#       **1 = Components to pattern** · **2 = Curve/edge/sketch for Direction 1** ·
#       4 = …Direction 2 · **32 = Reference point for `ReferencePoint`** · 64 = Face on which a 3D curve lies
#     ★ 且 NOTE 逐字：★ 若 `ReferencePoint` 取 `swLocalSketchPatternSelectedPoint`，
#       ★ **选中的参考点必须是 vertex** ✓
#   · ★ 故本探针只按 **mark 1 + 2** 选（★ Direction2 关、ReferencePoint 取 0 档 ✓）
# 判据:   ★★ 主判据一律**回读**：★ **特征树多了新特征**（★ 不看返回值 ✓）
#   ★★ 前置逐条落布尔字段（★ 让「选不上」与「选了没用」可分辨 —— ★ B3 那轮学到的：
#      ★★ "读数无效"的样子与"真的不建"**一模一样** ✗ ⇒ 每处前置一个字段是唯一防线 ✓）
#   ★★★ 三种结果三种记法（★ 与「扫描曲面」那条成功案例同型）：
#     · ★ **建成** ⇒ ★★★ **翻案成立** ✓
#     · ★ **不建** ⇒ ★★ **还不算试死**（★ 前置没上 ⇒ 定则：「读到静默」≠「判定试死」✓）
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

#: ★ 官方 `## Remarks` 的 mark 表（★ 逐字）✓
MARKS = {"components_to_pattern": 1, "direction1_curve": 2,
         "direction2_curve": 4, "reference_point": 32, "curve_face": 64}


#: ★★ 取特征名 —— **不要用 `sw_weldment.feature_names`** ✗（★ 它在 B8 收口时被移除了：
#:   ★ 撞 `check_relative_imports` 的棘轮 ✓）；★ 也不用 `iter_features_recursive`（★ 实测它
#:   在这条链上**取不到任何特征** ✗ ⇒ 会让 `特征树 = []`、**读数整体无效** ✓）
#:   ⇒ ★ 用 **B2-2 已验证可用**的 `sw_surface_features.feature_names` ✓
def _fnames(model):
    import sw_surface_features as SF
    return SF.feature_names(model)


def main() -> int:
    import sw_connect
    import sw_part
    import sw_weldment as W
    import sw_selection_spec as SS

    out: dict = {"official": "IFeatureManager.FeatureLocalCurveDrivenPattern",
                 "purpose": "★ 兑现一次翻案：参数式入口不带 ACL ⇒ 直接试",
                 "official_marks": dict(MARKS)}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    if model is None:
        print("★ 建不了零件")
        return 2

    #: ① **要阵列的特征**（★ 一个凸台 ✓）
    sw_part.start_sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, 0.0, 0.0, 20.0, 20.0)
    sk1 = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    sw_part.extrude_boss(model, sk1, 10.0)
    #: ② **方向曲线**（★ 另一张草图上的样条/直线 ✓）
    sw_part.start_sketch(model, "Top Plane")
    sw_part.sketch_line(model, 0.0, 0.0, 0.0, 100.0)
    sk2 = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    feats = _fnames(model)
    extrudes = [f for f in feats if "拉伸" in f or "Extrude" in f]
    out["features"] = feats
    out["extrudes"] = extrudes
    out["sketch2"] = sk2
    print("★ 特征树 = %r" % feats)

    #: ③ **按官方 mark 选**：★ 1 = 要阵列的特征 · 2 = 方向曲线 ✓
    ext = sw_connect.get_com_member(model, "Extension")
    ok1 = bool(sw_part._select_by_id(ext, extrudes[0], "BODYFEATURE", append=False, mark=1)) if extrudes else False
    ok2 = bool(sw_part._select_by_id(ext, sk2, "SKETCH", append=True, mark=2))
    out["select"] = {"mark1_components_to_pattern": ok1, "mark2_direction1_curve": ok2,
                     "selection_count": SS.get_selection_count(model)}
    print("★ 选择：★ mark1(要阵列的特征)=%r · mark2(方向曲线)=%r · 选区计数=%r"
          % (ok1, ok2, out["select"]["selection_count"]))

    #: ④ **调**（★ 13 参逐位：★ FlipDir1 · Num1(含原件) · EqualSpacing1 · Spacing1 ·
    #:    ReferencePoint · CurveMethod · AlignMethod · Direction2 · FlipDir2 · Num2 ·
    #:    EqualSpacing2 · Spacing2 · PatternSeedOnly ✓）
    before = _fnames(model)
    exc = None
    feat = None
    try:
        feat = sw_connect.get_com_member(
            sw_connect.get_com_member(model, "FeatureManager"),
            "FeatureLocalCurveDrivenPattern",
            False, 3, False, float(sw_connect.mm(30.0)), 0, 0, 0,
            False, False, 1, False, 0.0, False)
    except Exception as e:                                              # noqa: BLE001
        exc = e
    after = _fnames(model)
    added = [n for n in after if n not in before]
    out["new_features"] = added
    out["returned_is_none"] = feat is None
    out["returned_name"] = getattr(feat, "Name", None) if feat is not None else None
    out["exception"] = None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:150])

    if added:
        out["verdict"] = ("★★★★★ **建成**（★ 新增 %r）⇒ ★★ **翻案成立**："
                          "★ 参数式入口 `FeatureLocalCurveDrivenPattern` **不带 ACL、真机能建** ✓" % added)
    elif exc is not None:
        out["verdict"] = "★★ **抛**：%s" % out["exception"]
    else:
        out["verdict"] = ("★★ **不建**（★ 回 %r）⇒ ★ **还不算试死** —— ★ 前置复核："
                          "★ mark1=%r · mark2=%r · 选区=%r（★ 定则：「读到静默」≠「判定试死」✓）"
                          % (out["returned_name"], ok1, ok2, out["select"]["selection_count"]))
    print("★★ 调用后 ⇒ 新增 %r · 回 %r" % (added, out["returned_name"]))
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b5-curvedriven.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    #: ★★ 真机探针的异常要**落盘**（★ `sw_guard` 的 `stderr_tail` 会把开头当尾部显示 ✗
    #:   ⇒ 从它那里读不到内层帧 ✓）
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                          # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec211-b5-curvedriven-traceback.txt").write_text(
            tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1500:])
        raise SystemExit(3)
