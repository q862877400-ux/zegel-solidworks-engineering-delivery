"""★ 探针：`InsertSweepSurface2` 的**两个未试变体** —— ★ 带引导线（mark 2）· 闭合路径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B2-2 的收口探针）
# 文件:   tools/probe_spec211_sweep_variants.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B2-2**。★ 上一轮**建成**了最基本的那一种
#   （★ 圆轮廓 mark 1 + 直线路径 mark 4 ⇒ ★ 特征树 +1 `曲面-扫描1` ✓）。
#   ★★★ 而 `capabilities.yaml` 的 `limitations` 里**明写了一条"不许推广"** ✓：
#     ★ 本次只试了**一条**几何 ⇒ **不许推广成"扫描曲面全形态都成"** ✗
#     ★ 未试的：★ **带引导线（mark 2）** · ★ **闭合路径** · ★ `TwistCtrlOption` 各档 · ★ `PathAlign` 各档 ✓
#   ⇒ ★★ 本探针**试掉其中两个**（★ 选它们是因为**几何上最容易造** ✓）：
#     ★ **变体 A：带引导线** —— 轮廓（前视·圆）+ 路径（上视·直线）+ **引导线（右视·直线）**，
#       ★ mark 依次 **1 / 4 / 2** ✓（★ 官方 mark 表逐字：`2 = Guide curve selection, if provided` ✓）
#     ★ **变体 B：闭合路径** —— 轮廓（前视·圆）+ **路径（上视·圆，闭合）**，mark **1 / 4** ✓
# 判据:   ★★ 每个变体**各自一个零件**（★ 免得相互污染 —— ★ 规格 210 的教训：★ 同文档顺序标定会污染 ✓）
#   ★★ 主判据一律**回读**：★ **特征树多了新特征**（★ 不看返回值 ✓）
#   ★★★ **三种结果，三种记法**（★ 这是本批的价值）：
#     · ★ **建成** ⇒ ★★ 那一条形态**可做** ✓（★ 记进 evidence ✓）
#     ★ · ★ **静默回 `None`**（★ 不抛、特征树不变）⇒ ★★ **那才是真正的「试死」** ✓
#       ★（★ 因为本轮**前置已完全对上** —— ★ 与上一轮「前置没上」**不同** ✓）
#     · ★ **抛异常** ⇒ ★ 记下来（★ 那说明形态本身被拒 ✓）
# 官方依据: `C:\swapi\types\IFeatureManager\InsertSweepSurface2.md`（签名 + Remarks 的 mark 表）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _classify(rep: dict) -> str:
    """★ **三种结果，三种记法**（★ 见文件头的判据段）✓"""
    if rep.get("ok"):
        return "★★★★ **建成** ⇒ ★ 该形态**可做** ✓"
    if rep.get("returned_is_none"):
        return "★★★★ **静默回 `None`**（★ 前置已完全对上）⇒ ★★ **这才是真正的「试死」** ✓"
    err = str(rep.get("error") or "")
    if err.startswith(("TypeError", "com_error", "AttributeError", "RuntimeError")):
        return "★★ **抛异常** ⇒ ★ 该形态被拒（★ 错误：%s）" % err[:90]
    return "★ 其它：%s" % err[:110]


def _new_part(sw):
    import sw_connect
    return sw_connect.new_document(sw, "part")


def main() -> int:
    import sw_connect
    import sw_part
    import sw_surface_features as sf
    import sw_selection_spec as SS

    out: dict = {"official": "IFeatureManager.InsertSweepSurface2",
                 "purpose": "试掉两个未试变体（★ 因为 limitations 明写「不许推广」✓）",
                 "marks": {"profile": 1, "guide": 2, "path": 4}, "variants": {}}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    #: ══ 变体 A：带引导线（★ mark 1 / 4 / 2）══════════════════════════════
    model = _new_part(sw)
    sw_part.start_sketch(model, "Front Plane")
    sw_part.sketch_circle(model, 0.0, 0.0, 10.0)
    sk_p = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    sw_part.start_sketch(model, "Top Plane")
    sw_part.sketch_line(model, 0.0, 0.0, 0.0, 60.0)
    sk_path = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    sw_part.start_sketch(model, "Right Plane")
    sw_part.sketch_line(model, 0.0, 0.0, 0.0, 60.0)
    sk_guide = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    before = sf.feature_names(model)
    ext = sw_connect.get_com_member(model, "Extension")
    sw_part._select_by_id(ext, sk_p, "SKETCH", append=False, mark=1)
    sw_part._select_by_id(ext, sk_path, "SKETCH", append=True, mark=4)
    sel_before_guide = SS.get_selection_count(model)
    sw_part._select_by_id(ext, sk_guide, "SKETCH", append=True, mark=2)
    rep_a = sf.sweep_surface_report(model, use_auto_select=True)
    out["variants"]["A_with_guide"] = {
        "sketches": {"profile": sk_p, "path": sk_path, "guide": sk_guide},
        "selection_before_guide": sel_before_guide,
        "selection_after": SS.get_selection_count(model),
        "features_delta": [n for n in sf.feature_names(model) if n not in before],
        "report": {k: rep_a.get(k) for k in ("ok", "returned_is_none", "new_features",
                                             "feature_count_before", "feature_count_after",
                                             "error")},
        "verdict": _classify(rep_a)}
    print("★ 变体 A（带引导线 mark 1/4/2）⇒ %s" % _classify(rep_a))
    print("   新增特征 = %r" % out["variants"]["A_with_guide"]["features_delta"])

    #: ══ 变体 B：闭合路径（★ mark 1 / 4）══════════════════════════════════
    model2 = _new_part(sw)
    sw_part.start_sketch(model2, "Front Plane")
    sw_part.sketch_circle(model2, 0.0, 0.0, 5.0)
    b_p = sw_part.current_sketch_name(model2)
    sw_part.end_sketch(model2)
    sw_part.start_sketch(model2, "Top Plane")
    #: ★ **闭合路径**：用**圆**作路径（★ 首尾相接 ✓）
    sw_part.sketch_circle(model2, 0.0, 0.0, 30.0)
    b_path = sw_part.current_sketch_name(model2)
    sw_part.end_sketch(model2)
    before2 = sf.feature_names(model2)
    ext2 = sw_connect.get_com_member(model2, "Extension")
    sw_part._select_by_id(ext2, b_p, "SKETCH", append=False, mark=1)
    sw_part._select_by_id(ext2, b_path, "SKETCH", append=True, mark=4)
    rep_b = sf.sweep_surface_report(model2, use_auto_select=True)
    out["variants"]["B_closed_path"] = {
        "sketches": {"profile": b_p, "path": b_path},
        "selection_count": SS.get_selection_count(model2),
        "features_delta": [n for n in sf.feature_names(model2) if n not in before2],
        "report": {k: rep_b.get(k) for k in ("ok", "returned_is_none", "new_features",
                                             "feature_count_before", "feature_count_after",
                                             "error")},
        "verdict": _classify(rep_b)}
    print("★ 变体 B（闭合路径 mark 1/4）⇒ %s" % _classify(rep_b))
    print("   新增特征 = %r" % out["variants"]["B_closed_path"]["features_delta"])

    p = ROOT / "output" / "spec211-b2-sweep-variants.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
