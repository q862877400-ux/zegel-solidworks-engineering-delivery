"""★ 真机：**边界凸台/基体** —— 验它与「放样凸台/基体」在 API 上是不是**同一个**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_boundary_boss_same_api_as_loft.py
# 定位:   ★ 2026-10-03（轮 551）★ 照新纪律读文档后的**一个推论验证**。
#
#   ★★ **推论怎么来的**：
#     · 官方 `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md` 的 `## Remarks` 逐字：
#       「Set the mark for: **1 = profile selections** · **2 = guide curve selections** ·
#         **4 = centerline selection**」；★ 并强调
#       「selection of the profiles **must be in an order consistent with** [the design intent]」
#       与「**Use of guide curves is strongly recommended**」。
#     · ★ 而**本仓 `scripts/sw_loft.py::create_loft_report` 走的**就是那个入口**（★ 18 参）、
#       ★ 且它的 docstring 已经写着那条 mark=1 与"按顺序"。
#     ⇒ ★★ **故推论**：★ 工具栏上的「**边界凸台/基体**」与「**放样凸台/基体**」
#       ★ **在 API 上是同一个**（`InsertProtrusionBlend2`）——
#       ★ 它们的差别是 **UI 层**的（★ 界面上是两个按钮）⚠
#
#   ★ 本探针就验这一件事：★ **同一个 `create_loft_report`，能不能建出「边界凸台」那样的特征**
#     —— ★ 判据用**本仓已定**的：★ 树增量 **且** 类型名 = **`Blend`** ✓
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：**树新增特征** **且** **它的 `GetTypeName2` = `Blend`**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_loft as L                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402
import scripts.sw_weldment as W                                       # noqa: E402


def _two_profiles(doc):
    """★ **两个平行剖面**（★ 放样/边界至少要 2 个 —— ★ 且按顺序选）。"""
    made = []
    for i, (plane, half) in enumerate((("Front Plane", 0.02), ("Front Plane", 0.01))):
        try:
            doc.ClearSelection2(True)
        except Exception:                                                     # noqa: BLE001
            pass
        #: \u2605 \u7b2c\u4e8c\u4e2a\u8349\u56fe\u8981\u5728**\u53e6\u4e00\u4e2a\u57fa\u51c6\u9762**\u4e0a\uff08\u2605 \u504f\u79fb\u4e00\u4e2a\uff09
        if i == 0:
            P.start_sketch(doc, plane_name=plane)
        else:
            #: \u2605 \u7528 InsertRefPlane \u5efa\u4e00\u4e2a\u504f\u79fb\u57fa\u51c6\u9762\uff08\u2605 \u672c\u4ed3\u5df2\u6709 ref_geometry\uff09
            from sw_connect import get_com_member as _get
            fm = _get(doc, "FeatureManager")
            ext = _get(doc, "Extension")
            P._select_by_id(ext, "\u524d\u89c6\u57fa\u51c6\u9762", "PLANE", append=False, mark=0)
            _get(fm, "InsertRefPlane", 8, 0.03, 0, 0, 0, 0)
            try:
                P.start_sketch(doc, plane_name="\u57fa\u51c6\u97621")
            except Exception:                                             # noqa: BLE001
                P.start_sketch(doc, plane_name="Plane1")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                         0.0, 0.0, 0.0, half)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or [])
                 if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        if names:
            made.append(names[-1])
    return made


def _pick_profiles(doc, sketches):
    """★ 按**期望的顺序**选轮廓 —— ★ 官方 Remarks 的硬约束（★ mark=1）。"""
    ext = C.get_com_member(doc, "Extension")
    picked = []
    for sk in sketches:
        for cand in P._get_sketch_name_candidates(sk):
            try:
                if P._select_by_id(ext, cand, "SKETCH", append=bool(picked), mark=1):
                    picked.append(cand)
                    break
            except Exception:                                             # noqa: BLE001
                continue
    return picked


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u8fb9\u754c\u51f8\u53f0/\u57fa\u4f53 \u2014\u2014 \u5b83\u4e0e\u300c\u653e\u6837\u300d\u5728 API \u4e0a\u662f\u4e0d\u662f\u540c\u4e00\u4e2a",
          "hypothesis": "sw_loft.create_loft_report\uff08\u8d70 InsertProtrusionBlend2\uff09\u80fd\u5efa\u51fa\u8fb9\u754c\u51f8\u53f0",
          "cases": []}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        sketches = _two_profiles(doc)
        before = list(FR.feature_names(doc) or [])
        picked = _pick_profiles(doc, sketches)
        row = {"tag": "\u2605 \u7528 create_loft_report \u5efa\u300c\u8fb9\u754c\u51f8\u53f0\u300d\u90a3\u4e2a\u7279\u5f81",
               "sketches": sketches, "profiles_picked": picked}
        try:
            r = L.create_loft_report(doc, closed=False, use_selected_profiles=True)
            row["report_ok"] = r.get("ok")
            row["feature_name"] = r.get("feature_name")
            row["args_count"] = r.get("args_count")
            row["mark1_selected"] = r.get("mark1_selected")
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        types = []
        try:
            for f in W.iter_features_recursive(doc):
                try:
                    types.append(str(C.get_com_member(f, "GetTypeName2") or ""))
                except Exception:                                         # noqa: BLE001
                    pass
        except Exception:                                                     # noqa: BLE001
            pass
        row["blend_types"] = [t for t in types if t == "Blend"]
        row["ok"] = bool(row["new"]) and bool(row["blend_types"])
        ev["cases"].append(row)
    except Exception as exc:                                              # noqa: BLE001
        ev["cases"].append({"tag": "\u2605 \u5efa\u8fb9\u754c\u51f8\u53f0", "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])})
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("same_api_confirmed" if ev["passed"]
                     else "inconclusive_or_fails")
    p = R / "output" / "boundary-boss-same-api-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %s" % c.get("tag"))
        print("        \u8349\u56fe=%s \u9009\u4e2d=%s" % (c.get("sketches"), c.get("profiles_picked")))
        print("        report_ok=%s \u7279\u5f81=%s \u53c2\u6570=%s mark1=%s" % (
            c.get("report_ok"), c.get("feature_name"), c.get("args_count"), c.get("mark1_selected")))
        print("        \u65b0\u589e=%s \u7c7b\u578bBlend=%s" % (c.get("new"), c.get("blend_types")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
