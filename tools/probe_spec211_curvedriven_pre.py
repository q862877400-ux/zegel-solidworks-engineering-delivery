"""★ 探针：`FeatureLocalCurveDrivenPattern` **第二步** —— ★ 追第二处成因「档位」。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B5 翻案的第二批探针）
# 文件:   tools/probe_spec211_curvedriven_pre.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps`。★ 第一批（`probe_spec211_curvedriven.p
#           y`）
#   把**前置**对上了（★ mark1 要阵列的特征 · mark2 方向曲线，★ 两条都 True、选区 2 ✓）
# ⇒ ★★ **而仍不建**（★ 回 None · 新增 [] ✓）—— ★ 我当时**不叫试死**，因为还有**第二处成
# 因没追** ✓
# 本批:   ★★★ **追「参数/档位」** —— ★ 关键发现（★ 官方枚举逐字读过）：
# `swLocalSketchPatternReferencePoint_e`：★ **SelectedPoint = 0** · **BoundingBoxCenter 
# = 1** ·
#       **ComponentOrigin = 2** ✓
#     ★★ 而官方 `## Remarks` 的 NOTE 逐字：「If `ReferencePoint` is set to
# **`swLocalSketchPatternSelectedPoint`**, then the selected reference point **must be a
#  vertex**」✗
#     ⇒ ★★★ **第一批我取的正是 0（SelectedPoint）、而 mark 32 没选顶点** ✗
#       ⇒ ★★ **那很可能就是"前置没上"的第二处** ✓
#   ★ 故本批**遍历 `ReferencePoint` ∈ {0, 1, 2}**（★ 各一个零件，★ 免得相互污染 ✓）——
#     ★★ 1 / 2 两档**不需要选点** ✓
# 判据:   ★★ 主判据一律**回读**：★ **特征树多了新特征**（★ 不看返回值 ✓）
# ★★ 前置逐条落布尔字段（★ 「读数无效」与「真的不建」长得一模一样 —— ★ 本规格已两次证明 
# ✓）
#   ★★★ 三种结果三种记法（★ 与「扫描曲面」那条成功案例同型）：
#     · ★ **建成** ⇒ ★★★ **翻案彻底成立** ✓
#     · ★ **仍不建** ⇒ ★★ **那才够格叫「试死」**（★ 前置 ✓ + 档位 ✓ 两处都追过 ✓）
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

MARKS = {"components_to_pattern": 1, "direction1_curve": 2,
         "direction2_curve": 4, "reference_point": 32, "curve_face": 64}
#: ★ 官方 `swLocalSketchPatternReferencePoint_e` 逐字 ✓
REF_POINT = {0: "swLocalSketchPatternSelectedPoint（★ 需选顶点 ✗）",
             1: "swLocalSketchPatternBoundingBoxCenter（★ 不需选点 ✓）",
             2: "swLocalSketchPatternComponentOrigin（★ 不需选点 ✓）"}


def _fnames(model):
    import sw_surface_features as SF
    return SF.feature_names(model)


def _one(sw, ref_point: int) -> dict:
    import sw_connect
    import sw_part
    import sw_selection_spec as SS

    model = sw_connect.new_document(sw, "part")
    if model is None:
        return {"ok": False, "error": "★ 建不了零件"}
    sw_part.start_sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, 0.0, 0.0, 20.0, 20.0)
    sk1 = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    sw_part.extrude_boss(model, sk1, 10.0)
    sw_part.start_sketch(model, "Top Plane")
    sw_part.sketch_line(model, 0.0, 0.0, 0.0, 100.0)
    sk2 = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)

    feats = _fnames(model)
    extrudes = [f for f in feats if "拉伸" in f or "Extrude" in f]
    ext = sw_connect.get_com_member(model, "Extension")
    ok1 = bool(sw_part._select_by_id(ext, extrudes[0], "BODYFEATURE",
                                     append=False, mark=1)) if extrudes else False
    ok2 = bool(sw_part._select_by_id(ext, sk2, "SKETCH", append=True, mark=2))
    sel = SS.get_selection_count(model)
    before = _fnames(model)
    exc = None
    feat = None
    try:
        feat = sw_connect.get_com_member(
            sw_connect.get_com_member(model, "FeatureManager"),
            "FeatureLocalCurveDrivenPattern",
            False, 3, False, float(sw_connect.mm(30.0)), int(ref_point), 0, 0,
            False, False, 1, False, 0.0, False)
    except Exception as e:                                              # noqa: BLE001
        exc = e
    added = [n for n in _fnames(model) if n not in before]
    return {"ref_point": ref_point, "ref_point_name": REF_POINT.get(ref_point),
            "mark1": ok1, "mark2": ok2, "selection_count": sel,
            "added": added, "returned_is_none": feat is None,
            "exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:140])}


def main() -> int:
    import sw_connect

    out: dict = {"official": "IFeatureManager.FeatureLocalCurveDrivenPattern",
                 "step": "第二步：追「档位」成因（ReferencePoint 遍历）",
                 "official_marks": dict(MARKS),
                 "ref_point_enum": {str(k): v for k, v in REF_POINT.items()},
                 "runs": []}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    for rp in (0, 1, 2):
        r = _one(sw, rp)
        out["runs"].append(r)
        print("★ ReferencePoint=%d（%s）⇒ mark1=%r mark2=%r 选区=%r · 新增 %r · 回 %r"
              % (rp, REF_POINT.get(rp, "?")[:34], r.get("mark1"), r.get("mark2"),
                 r.get("selection_count"), r.get("added"),
                 "None" if r.get("returned_is_none") else "对象"))
        if r.get("added"):
            out["verdict"] = ("★★★★★ **建成**（★ ReferencePoint=%d）⇒ ★★★ **翻案彻底成立**："
                              "★ 参数式入口**不带 ACL、真机能建** ✓" % rp)
            break
    if not out.get("verdict"):
        out["verdict"] = ("★★★★ **三档全试过、仍不建**（★ 而前置两处都追过：mark ✓ · 档位 ✓）"
                          "⇒ ★★ **这才够格叫「试死」** ✓")
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b5-curvedriven-pre.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec211-b5-curvedriven-pre-traceback.txt").write_text(
            tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
