"""★ 真机：**复合曲线** —— 试**三种合法实体**（★ 事实 449 留的下一步）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_composite_curve_entities.py
# 定位:   ★ 2026-10-03（轮 571）★ 执行**事实 449 留的下一步**（★ 复合曲线）。
#
#   ★★ 事实 449 查明：`insert_composite_curve_report` 失败于
#     `RuntimeError: InsertCompositeCurve 返回 False`，★ 而**它自己的提示**写着两条前置：
#       · 必须先用 `SelectByID2(..., mark=1)` 选好实体
#       · ★★ **且实体类型要合法**（见 SOLIDWORKS Help）⚠
#
#   ★★★ **而本仓那个包装的 docstring 早就解决了另一半**（★ 已知事实 84）：
#     > 用 **`call_com_member` 而不是 `get_com_member`**：官方签名**零参**，
#     > 而 `get_com_member` 对零参成员会**先试调一次** ⇒ 会在"取"的时候把这个动作做掉。
#     ★ 故**那部分是对的** —— ★ 真因只剩**前置（选什么实体）**。
#
#   ★ 本探针试**三种**（★ 每组新开一个文档）：
#     ⓐ **同一草图里的两条相连段**（★ 用 `sw_sketch_edit_ops.select_sketch_segment` 按序号选）
#     ⓑ **实体的两条边**（★ `IEntity.Select4` 按对象选）
#     ⓒ **不选**（对照）
#   ★ 判据（★ 规则 6）：**特征树增量** **或** **创建对象**。
#   ⚠ 全程走 `tools/sw_guard.py`。
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


def _two_connected_segments(doc, plane="Front Plane"):
    """★ 一个草图里**两条相连的线**（★ 共用一个端点）。"""
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name=plane)
    sm = C.get_com_member(doc, "SketchManager")
    C.get_com_member(sm, "CreateLine", -0.02, -0.01, 0.0, 0.0, 0.0, 0.0)
    C.get_com_member(sm, "CreateLine", 0.0, 0.0, 0.0, 0.02, 0.01, 0.0)
    return True


def _one(sw, tag, mode):
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: \u2605 \u5148\u9020\u4e00\u4e2a\u5b9e\u4f53\uff08\u2605 \u4f9b \u24d1 \u7ec4\u7528\uff09
        P.start_sketch(doc, plane_name="Top Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                         -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or [])
                 if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
            try:
                P.extrude_boss(doc, cand, 0.01)
                break
            except Exception:                                             # noqa: BLE001
                continue
        _two_connected_segments(doc)
        nm2 = [n for n in (P.feature_names(doc) or [])
               if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        row["sketch"] = nm2[-1] if nm2 else None
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        picked = 0
        if mode == "segments":
            #: \u2605 \u24d0 **\u540c\u4e00\u8349\u56fe\u91cc\u7684\u4e24\u6761\u76f8\u8fde\u6bb5**\uff08\u2605 \u6309\u5e8f\u53f7\u9009\uff09
            P.end_sketch(doc)          #: \u2605 \u9009\u6bb5\u8981\u5148\u79bb\u5f00\u8349\u56fe\u5417\uff1f\u2605 \u672c\u4ed3\u90a3\u4e2a helper \u81ea\u5df1\u4f1a\u5904\u7406
            for i in (0, 1):
                try:
                    if SEO.select_sketch_segment(doc, i):
                        picked += 1
                except Exception:                                         # noqa: BLE001
                    try:
                        if SEO.select_sketch_segment(doc, i):
                            picked += 1
                    except Exception:                                     # noqa: BLE001
                        pass
        elif mode == "edges":
            from sw_connect import get_com_member as _g
            for b in list(_g(doc, "GetBodies2", 0, True) or []):
                for e in list(_g(b, "GetEdges") or [])[:2]:
                    if P._select_com_object(e, append=(picked > 0), mark=1):
                        picked += 1
                break
        row["picked"] = picked
        try:
            row["sel_count"] = int(C.get_com_member(
                C.get_com_member(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            row["sel_count"] = -1
        before = list(FR.feature_names(doc) or [])
        r = P.insert_composite_curve_report(doc, "")
        row["report"] = dict(r or {})
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"] or (r or {}).get("present"))
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


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u590d\u5408\u66f2\u7ebf\uff1a\u8bd5**\u4e09\u79cd\u5408\u6cd5\u5b9e\u4f53**\uff08\u2605 \u4e8b\u5b9e 449 \u7559\u7684\u4e0b\u4e00\u6b65\uff09",
          "official": "InsertCompositeCurve \u2014\u2014 \u96f6\u53c2 \u00b7 \u56de bool\uff1bRemarks\uff1a"
                      "\u5148\u7528 SelectByID2 mark=1 \u9009\u597d\u5b9e\u4f53\uff0c**\u4e14\u5b9e\u4f53\u7c7b\u578b\u8981\u5408\u6cd5**",
          "known": "\u4e8b\u5b9e 84\uff1a\u96f6\u53c2\u6210\u5458\u8981\u7528 call_com_member\uff08\u2605 \u672c\u4ed3\u5305\u88c5\u5df2\u5982\u6b64\uff09",
          "cases": []}
    ev["cases"].append(_one(sw, "\u24d0 **\u540c\u4e00\u8349\u56fe\u91cc\u7684\u4e24\u6761\u76f8\u8fde\u6bb5**", "segments"))
    ev["cases"].append(_one(sw, "\u24d1 **\u5b9e\u4f53\u7684\u4e24\u6761\u8fb9**", "edges"))
    ev["cases"].append(_one(sw, "\u24d2 \u5bf9\u7167\uff1a**\u4ec0\u4e48\u90fd\u4e0d\u9009**", "none"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("composite_works" if ev["passed"] else "composite_still_fails")
    p = R / "output" / "composite-curve-entities-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-42s ok=%-6s picked=%s sel=%s" % (
            c.get("tag"), c.get("ok"), c.get("picked"), c.get("sel_count")))
        rep = c.get("report") or {}
        print("        report.ok=%s present=%s error=%s" % (
            rep.get("ok"), (rep.get("readback") or {}).get("present")
            if isinstance(rep.get("readback"), dict) else None, str(rep.get("error"))[:80]))
        print("        \u65b0\u589e=%s" % (c.get("new"),))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
