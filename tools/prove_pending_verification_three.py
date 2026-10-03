"""★ 真机：复验「待验证」那桶里的三条 —— **筋** · **复合曲线** · **交叉曲线**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_pending_verification_three.py
# 定位:   ★ 2026-10-03（轮 570）★ 执行**第 100 轮盘点定的优先序**（★ 待验证桶成本最低）。
#
#   ★★ 盘点（`docs/milestone-round100.md` §2.1）查明：「**待验证**」这一桶的 `entry`
#     **全在 `scripts/` 里** —— ★ 即**代码已经有了**，★ 而**验证状态没跟上** ⚠
#     ⇒ ★ 故该做的是**真机复验**（★ 而不是从头实现）。
#
#   ★ 本轮验其中**三条**（★ 另外两条：线性阵列 = **已知边界**、曲面圆角 = 能力已 verified）：
#     · **筋**        `sw_part.rib_report(model, sketch_name, thickness_mm, feature_name, direction)`
#     · **复合曲线**   `sw_part.insert_composite_curve_report(model, feature_name)`
#       ★ 它的 docstring 逐字：「**调用前必须先用 mark = 1 选好实体**」⚠
#     · **交叉曲线**   `sw_sketch_edit_ops.sketch_intersect_curves(model)`
#       ★ 走 `SketchManager.IntersectCurves()`（★ **0 参**）
#
#   ★ 判据（★ 规则 6）：**特征树增量** **或** **返回对象** **或** **草图段数变化**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_sketch_edit_ops as SEO                         # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _solid(doc, h=0.02):
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, h)
            return True
        except Exception:                                                 # noqa: BLE001
            continue
    return False


def _new_sketch(doc, plane, draw):
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name=plane)
    draw(C.get_com_member(doc, "SketchManager"))
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    return names[-1] if names else None


def _segs(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:                                                     # noqa: BLE001
        return -1


def _case(sw, tag, fn):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["built"] = fn(doc, row)
        row["ok"] = bool(row.get("ok_flag"))
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


def _do_rib(doc, row):
    _solid(doc, 0.02)
    #: \u2605 **\u7b4b**\uff1a\u4e00\u6761**\u7a7f\u8fc7\u5b9e\u4f53\u7684\u7ebf**\uff08\u2605 \u5728\u4e0a\u89c6\u9762\u4e0a\uff09
    sk = _new_sketch(doc, "Top Plane",
                     lambda sm: C.get_com_member(sm, "CreateLine", -0.025, 0.0, 0.0, 0.025, 0.0, 0.0))
    row["sketch"] = sk
    before = list(FR.feature_names(doc) or [])
    r = P.rib_report(doc, sk, 0.003, "\u7b4b1", True)
    row["report"] = dict(r or {})
    after = list(FR.feature_names(doc) or [])
    row["new"] = [n for n in after if n not in before]
    row["ok_flag"] = bool(row["new"] or (r or {}).get("present"))
    return True


def _do_composite(doc, row):
    _solid(doc, 0.01)
    #: \u2605 **\u590d\u5408\u66f2\u7ebf**\uff1a\u4e24\u6761**\u76f8\u8fde\u7684\u7ebf**\uff08\u2605 \u5408\u8d77\u6765\u6210\u4e00\u6761\uff09
    sk = _new_sketch(doc, "Front Plane", lambda sm: (
        C.get_com_member(sm, "CreateLine", -0.02, -0.01, 0.0, 0.0, 0.0, 0.0),
        C.get_com_member(sm, "CreateLine", 0.0, 0.0, 0.0, 0.02, 0.01, 0.0)))
    row["sketch"] = sk
    #: \u2605 \u5b98\u65b9 Remarks\uff1a**\u5148\u7528 mark = 1 \u9009\u597d\u5b9e\u4f53**
    ext = C.get_com_member(doc, "Extension")
    picked = 0
    from sw_connect import get_com_member as _g
    for b in list(_g(doc, "GetBodies2", 0, True) or []):
        for e in list(_g(b, "GetEdges") or [])[:2]:
            try:
                if P._select_com_object(e, append=(picked > 0), mark=1):
                    picked += 1
            except Exception:                                             # noqa: BLE001
                pass
        break
    if picked < 2 and sk:
        for cand in P._get_sketch_name_candidates(sk):
            try:
                if P._select_by_id(ext, cand, "SKETCH", append=bool(picked), mark=1):
                    picked += 1
                    break
            except Exception:                                             # noqa: BLE001
                continue
    row["picked_mark1"] = picked
    before = list(FR.feature_names(doc) or [])
    r = P.insert_composite_curve_report(doc, "")
    row["report"] = dict(r or {})
    after = list(FR.feature_names(doc) or [])
    row["new"] = [n for n in after if n not in before]
    row["ok_flag"] = bool(row["new"] or (r or {}).get("present"))
    return True


def _do_intersect(doc, row):
    _solid(doc, 0.02)
    #: \u2605 **\u4ea4\u53c9\u66f2\u7ebf**\uff1a\u5728\u4e00\u4e2a\u8349\u56fe\u91cc\uff0c\u62ff**\u5b9e\u4f53\u7684\u9762**\u53bb\u4ea4
    #:   \u2605 \u5148\u9009\u4e00\u4e2a\u9762\uff08\u2605 \u4ea4\u53c9\u66f2\u7ebf\u8981\u6709\u4e1c\u897f\u53ef\u4ea4\uff09
    from sw_connect import get_com_member as _g
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    picked = 0
    for b in list(_g(doc, "GetBodies2", 0, True) or []):
        for f in list(_g(b, "GetFaces") or []):
            try:
                if bool(_g(_g(f, "GetSurface"), "IsCylinder")):
                    if P._select_com_object(f, append=False, mark=0):
                        picked += 1
                    break
            except Exception:                                             # noqa: BLE001
                continue
        break
    row["picked_cyl"] = picked
    P.start_sketch(doc, plane_name="Right Plane")
    before = _segs(doc)
    row["seg_before"] = before
    ret = None
    try:
        ret = SEO.sketch_intersect_curves(doc)
        row["returned"] = type(ret).__name__ if ret is not None else "None"
    except Exception as exc:                                              # noqa: BLE001
        row["err2"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
    after = _segs(doc)
    row["seg_after"] = after
    row["new_segments"] = (after - before) if (after >= 0 and before >= 0) else None
    try:
        P.end_sketch(doc)
    except Exception:                                                     # noqa: BLE001
        pass
    row["ok_flag"] = bool(row["new_segments"] and row["new_segments"] > 0)
    return True


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u590d\u9a8c\u300c\u5f85\u9a8c\u8bc1\u300d\u6876\uff1a**\u7b4b** \u00b7 **\u590d\u5408\u66f2\u7ebf** \u00b7 **\u4ea4\u53c9\u66f2\u7ebf**",
          "why": "\u7b2c 100 \u8f6e\u76d8\u70b9\u67e5\u660e\u8fd9\u4e00\u6876\u7684 entry **\u5168\u5728 scripts/ \u91cc**"
                 "\uff08\u2605 \u4ee3\u7801\u5df2\u6709\uff09\u21d2 \u2605 \u8be5\u505a\u7684\u662f**\u771f\u673a\u590d\u9a8c**",
          "cases": []}
    ev["cases"].append(_case(sw, "\u2605 **\u7b4b**\uff08rib_report\uff09", _do_rib))
    ev["cases"].append(_case(sw, "\u2605 **\u590d\u5408\u66f2\u7ebf**\uff08insert_composite_curve_report\uff09", _do_composite))
    ev["cases"].append(_case(sw, "\u2605 **\u4ea4\u53c9\u66f2\u7ebf**\uff08sketch_intersect_curves\uff09", _do_intersect))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("pending_three_%d_of_%d" % (ev["passed"], ev["total"]))
    p = R / "output" / "pending-verification-three-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  %-46s ok=%-6s" % (c.get("tag"), c.get("ok")))
        for k in ("sketch", "picked_mark1", "picked_cyl", "seg_before", "seg_after",
                  "new_segments", "returned", "new", "report"):
            if c.get(k) not in (None, [], {}):
                print("        %-14s %s" % (k, str(c.get(k))[:120]))
        for k in ("err", "err2"):
            if c.get(k):
                print("        %-14s %s" % (k, str(c[k])[:130]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
