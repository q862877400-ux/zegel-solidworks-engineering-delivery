"""★ 真机：**删除孔** `IModelDoc2.InsertDeleteHole()`（★ 0 参 · 回 void ⇒ 判据用几何量）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_delete_hole.py
# 定位:   ★ 2026-10-03（轮 559）★ 照新纪律（**官方文档是第 0 步**）攻台账曲面栏的「删除孔」。
#
#   ★★ **静态已定**（★ 全接口查）：
#     · 成员是 **`IModelDoc2.InsertDeleteHole()`** —— ★ **0 参**、★ 回 **`void`**（★ 无返回值）
#     · ★ 故**判据只能是几何量**（★ 事实 436 的教训：别只看树）
#
#   ★ 前置：★ 一个**带孔的实体**（★ 删除孔要有孔可删）。
#     ★ 而"孔"从哪来？★ 本仓有 `solidworks_create_hole_feature`（★ 已 verified）⇒ ★ 用它打一个孔。
#   ★ 判据（★ 三条一起记）：
#     ① **面数** —— 删孔会让面数**减少**
#     ② **体积** —— 删孔会把孔填上 ⇒ 体积**变大**
#     ③ 树增量
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两组（★ 有孔 / 无孔对照）。
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
import scripts.sw_feature_readback as FR                              # noqa: E402


def _mk_solid_with_hole(doc, with_hole=True):
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    ok = False
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            ok = True
            break
        except Exception:                                                 # noqa: BLE001
            continue
    if not with_hole:
        return ok
    #: \u2605 \u6253\u4e00\u4e2a**\u901a\u5b54**\uff08\u2605 \u7528\u672c\u4ed3\u73b0\u6210\u7684\u58f0\u660e\u5f0f\u5b54\uff09
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                     0.0, 0.0, 0.0, 5.0 / 1000.0)
    P.end_sketch(doc)
    names2 = [n for n in (P.feature_names(doc) or [])
              if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names2[-1] if names2 else "\u8349\u56fe2", "\u8349\u56fe2"):
        try:
            P.extrude_cut(doc, cand, 0.0)
            return ok
        except Exception:                                                 # noqa: BLE001
            try:
                P.extrude_cut(doc, cand, 0.02)
                return ok
            except Exception:                                             # noqa: BLE001
                pass
    return ok


def _geom(doc):
    from sw_connect import get_com_member as _g
    faces = 0
    for b in list(_g(doc, "GetBodies2", 0, True) or []):
        try:
            faces += len(list(_g(b, "GetFaces") or []))
        except Exception:                                                     # noqa: BLE001
            pass
    vol = None
    try:
        mp = _g(_g(doc, "Extension"), "CreateMassProperty")
        v = _g(mp, "Volume")
        vol = float(v) if v is not None else None
    except Exception:                                                         # noqa: BLE001
        pass
    return {"faces": faces, "volume": vol}


def _one(sw, tag, with_hole):
    row = {"tag": tag, "with_hole": with_hole, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["built"] = _mk_solid_with_hole(doc, with_hole)
        row["before"] = _geom(doc)
        before = list(FR.feature_names(doc) or [])
        try:
            C.get_com_member(doc, "InsertDeleteHole")
            row["called"] = True
        except Exception as exc:                                          # noqa: BLE001
            row["called"] = False
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["after"] = _geom(doc)
        b, a = row["before"], row["after"]
        row["face_delta"] = (a["faces"] - b["faces"]) if (a["faces"] and b["faces"]) else None
        row["vol_delta"] = ((a["volume"] - b["volume"]) if (a["volume"] and b["volume"]) else None)
        #: \u2605 \u5224\u636e\uff1a**\u51e0\u4f55\u91cf\u53d8\u4e86** \u6216 \u6811\u589e\u91cf
        row["ok"] = bool(row["new"] or row["face_delta"] or row["vol_delta"])
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
          "_": "\u5220\u9664\u5b54\uff1a`IModelDoc2.InsertDeleteHole()`\uff08\u2605 0 \u53c2 \u00b7 \u56de void \u21d2 \u5224\u636e\u7528\u51e0\u4f55\u91cf\uff09",
          "official": "IModelDoc2.InsertDeleteHole() \u2014\u2014 void InsertDeleteHole()\uff0c\u65e0\u53c2\u6570\u3001\u65e0\u8fd4\u56de\u503c",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 \u6709\u5b54\u65f6\u8c03\u5b83", True))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a**\u65e0\u5b54**\u65f6\u8c03\u5b83", False))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("delete_hole_changes_geometry" if ev["cases"][0].get("ok")
                     else "delete_hole_silent_noop")
    p = R / "output" / "delete-hole-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        b, a = c.get("before") or {}, c.get("after") or {}
        print("  %-28s ok=%-6s called=%s" % (c.get("tag"), c.get("ok"), c.get("called")))
        print("        \u9762 %s\u2192%s\uff08\u0394%s\uff09\u00b7 \u4f53\u79ef \u0394=%s \u00b7 \u65b0\u589e=%s" % (
            b.get("faces"), a.get("faces"), c.get("face_delta"),
            ("%.3e" % c["vol_delta"]) if c.get("vol_delta") else None, c.get("new")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
