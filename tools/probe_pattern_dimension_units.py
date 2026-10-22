"""★ 测单位：`FeatureLinearPattern3` 的间距与 `AddDimension2` 的坐标究竟是米还是毫米。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_pattern_dimension_units.py
# 定位:   ★ 2026-10-03（轮 400）24h 计划 v2 段 3 的**S0 前置**：`add_dimension` 与 `li
#           near_pattern`
#   的包装**都不做单位换算**，★ 而官方 API 吃**米**、`linear_pattern` 的文档串却写着**毫米**
#   （★ 并注明"间距已测"）⇒ ★★ **在测清楚之前挂出去会把"单位"这个错固化进工具面**。
# 官方依据: `IFeatureManager.FeatureLinearPattern3` · `IModelDoc2.AddDimension2` ·
#   `IAnnotation.GetPosition`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 实验设计（★ 两条都做成**符号可判**的，不靠肉眼估）：
# ```
# ① `FeatureLinearPattern3` 的**间距**：
#    ★ 造一个 40 mm 宽的板（x ∈ [-20, 20]），★ 在 x ∈ [15, 19] 上再加一个小凸台。
#    ★ 用间距 **0.01**、数量 3 做线性阵列：
#      · 若 API 吃**米** ⇒ 步距 10 mm ⇒ 实例落在 15 / 25 / 35 ⇒ **包围盒 xmax > 20** ✓
#      · 若 API 吃**毫米** ⇒ 步距 0.01 mm ⇒ 实例几乎重合 ⇒ **包围盒 xmax = 20**（板边）
#    ⇒ ★★ **判据是符号**：`xmax > 20` ⇒ 米；`xmax == 20` ⇒ 毫米（★ 不依赖绝对精度）。
# ② `AddDimension2` 的**坐标**：★ 传 **10.0**，再读回标注位置 `IAnnotation.GetPosition()`：
#      · 若回 ≈ **10**   ⇒ API 吃**米**（10 m）
#      · 若回 ≈ **0.01** ⇒ API 吃**毫米**（10 mm = 0.01 m）
# ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "pattern-dimension-units-evidence.json")
# ⚑ 2026-10-03（轮 470）：这里曾有一个 `_bbox_xmax(doc)` ——
#   ★★ 而它本身**是坏的**：它最后一行写 `return bb, bb`（★ 两个返回值**都是
#   同一个字典**，而上一行的注释说明本意是“分别取 x 的 min/max”）
#   ⇒ 它**从来没被调过**（★ 实测：全仓出现 **1** 次）⇒ 删。
#   ★ 依据：本仓先例（同上）与门禁 `tests/test_no_uncalled_helpers.py`。


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from sw_part import (current_sketch_name, end_sketch, extrude_boss, linear_pattern,
                         sketch_corner_rectangle, start_sketch)
    import sw_part as P

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    doc2 = None
    try:
        #: ── ① 线性阵列的间距单位 ──────────────────────────────────────
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 10.0)
        #: ★ 在 x∈[15,19] 上再加一个小凸台（★ 阵列对象）
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 15.0, -2.0, 19.0, 2.0)
        sk2 = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk2, 20.0)
        feats = [str(get_com_member(f, "Name") or "")
                 for f in (get_com_member(doc, "FeatureManager").GetFeatureTreeRootItem2(0)
                           and [] or [])] if False else []
        #: ★ 直接按名字找那个凸台（★ 中文 UI 下是「凸台-拉伸2」）
        boss = None
        for nm in ("凸台-拉伸2", "Boss-Extrude2", "凸台-拉伸1", "Boss-Extrude1"):
            f = get_com_member(doc, "FeatureByName", nm)
            if f is not None:
                boss = nm
                break
        bb0 = P.get_bounding_box(doc, body_index=0)
        ev["steps"]["before_pattern"] = {"ok": bool(bb0), "boss": boss, "bbox": bb0}
        try:
            linear_pattern(doc, boss or "凸台-拉伸2", 1.0, 0.0, 0.0, 0.01, 3)
            bb1 = P.get_bounding_box(doc, body_index=0)
            ev["steps"]["pattern_spacing_0p01"] = {"ok": True, "bbox": bb1}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["pattern_spacing_0p01"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}

        #: ── ② AddDimension2 的坐标单位 ───────────────────────────────
        doc2 = sw_connect.new_document(sw, "part")
        start_sketch(doc2, plane_name="Front Plane")
        sketch_corner_rectangle(doc2, -20.0, -10.0, 20.0, 10.0)
        end_sketch(doc2)
        try:
            dd = get_com_member(doc2, "AddDimension2", 10.0, 0.0, 0.0)
            ann = get_com_member(dd, "GetAnnotation") if dd is not None else None
            pos = get_com_member(ann, "GetPosition") if ann is not None else None
            ev["steps"]["add_dimension_at_10"] = {
                "ok": dd is not None,
                "position": (list(pos)[:3] if pos is not None else None),
                "note": "★ 传 10.0：回 ≈10 ⇒ 米；回 ≈0.01 ⇒ 毫米"}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["add_dimension_at_10"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = "★ 段 3 的 S0：先测单位，再决定包装怎么写。"
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1600])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        for d in (doc, doc2):
            if d is not None:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
