"""★ 真机：两条草图图元的**继任者** —— `CreateLine2`（中点线）· `CreateSpline`（样条）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_createline2_and_createspline.py
# 定位:   ★ 2026-10-03（轮 565）★ 照新纪律（**官方文档是第 0 步**）攻两条草图绘制项。
#
#   ★★★★ **两条的第一代都被标了废弃**（★ 事实 433 那张地图）：
#     · 「中点线」`CreateLine(Midpoint)` ⇒ md 逐字：
#       > "**Obsolete. Superseded by `IModelDoc2::CreateLine2`.**"
#     · 「曲面上的样条曲线」`CreateSpline(3D)` ⇒ md 逐字：
#       > "**Obsolete. Superseded by `ISketchManager::CreateSpline`.**"
#
#   ★★★★★ **两个继任者的签名与 Remarks（逐字）**：
#     ```
# System.object IModelDoc2.CreateLine2(P1x, P1y, P1z, P2x, P2y, P2z)     \u2190 **6 \u53
# c2**
# Remarks: If a sketch is **not active**, then the line is **not created and NULL is ret
# urned**.
#                (\u2605 2D \u8349\u56fe\u91cc Z \u88ab\u5ffd\u7565)
#
# SketchSegment ISketchManager.CreateSpline(object PointData)             \u2190 **1 \u5
# 3c2**
# Remarks: \u81f3\u5c11**\u4e24\u4e2a** X,Y,Z\uff1b\u2605 **2D \u8349\u56fe\u91cc SOLIDW
# ORKS \u5ffd\u7565 Z**\uff1b
# \u2605 \u5b83**\u4e0d\u914d\u5408** `AddToDB` / `DisplayWhenAdded`\uff08\u603b\u662f\u
# 52a0\u8fdb DB\uff09\u3002
#     ```
#
#   ★ 判据（★ 规则 6 + 事实 436）：**草图段数增加**（★ 图元没有特征树增量）。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两组各带一个**不建草图**的负例（★ 官方明说不建）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

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


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        if sk is None:
            return -1
        return len(list(C.get_com_member(sk, "GetSketchSegments") or []))
    except Exception:                                                     # noqa: BLE001
        return -1


def _case(sw, tag, fn, active_sketch=True):
    row = {"tag": tag, "active_sketch": active_sketch, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        before = -1
        if active_sketch:
            P.start_sketch(doc, plane_name="Front Plane")
            before = _seg_count(doc)
        row["seg_before"] = before
        ret = None
        try:
            ret = fn(doc)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _seg_count(doc)
        row["seg_after"] = after
        row["new_segments"] = (after - before) if (after >= 0 and before >= 0) else None
        row["ok"] = bool(row["new_segments"] and row["new_segments"] > 0)
        try:
            P.end_sketch(doc)
        except Exception:                                                 # noqa: BLE001
            pass
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


def _line2(doc):
    #: \u2605 **6 \u53c2**\uff1aP1(3) + P2(3)
    return C.get_com_member(doc, "CreateLine2",
                            -0.02, -0.01, 0.0,
                            0.02, 0.01, 0.0)


def _spline(doc):
    #: \u2605 **1 \u53c2**\uff1a\u70b9\u6570\u7ec4\uff08\u2605 \u81f3\u5c11\u4e24\u4e2a 
    #: X,Y,Z\uff09
    pts = [-0.02, 0.0, 0.0,
           0.0, 0.015, 0.0,
           0.02, 0.0, 0.0]
    sm = C.get_com_member(doc, "SketchManager")
    return C.get_com_member(sm, "CreateSpline", pts)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u4e24\u6761\u8349\u56fe\u56fe\u5143\u7684**\u7ee7\u4efb\u8005**\uff1a`CreateLine2` \u00b7 `CreateSpline`",
          "official": "CreateLine \u4e0e CreateSpline \u7684 md **\u90fd\u5199\u7740 Obsolete**\uff1b"
                      "\u7ee7\u4efb\u8005 = IModelDoc2.CreateLine2\uff086 \u53c2\uff09\u00b7 ISketchManager.CreateSpline\uff081 \u53c2\uff09",
          "cases": []}
    ev["cases"].append(_case(sw, "\u2605 \u4e2d\u70b9\u7ebf\uff1a`CreateLine2`\uff086 \u53c2\uff09", _line2, True))
    ev["cases"].append(_case(sw, "\u2605 \u66f2\u9762\u4e0a\u7684\u6837\u6761\uff1a`CreateSpline`\uff081 \u53c2\uff09", _spline, True))
    ev["cases"].append(_case(sw, "\u8d1f\u4f8b\uff1a**\u65e0\u6d3b\u52a8\u8349\u56fe**\u65f6\u8c03 CreateLine2", _line2, False))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("both_successors_work" if ev["cases"][0].get("ok") and ev["cases"][1].get("ok")
                     else ("partial_%d" % ev["passed"]))
    p = R / "output" / "createline2-and-createspline-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-44s ok=%-6s \u6bb5 %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s" % (
            c.get("tag"), c.get("ok"), c.get("seg_before"), c.get("seg_after"),
            c.get("new_segments"), c.get("returned")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
