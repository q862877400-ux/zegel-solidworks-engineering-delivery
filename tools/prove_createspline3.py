"""★ 真机：**`CreateSpline3`** —— 2D 样条 · **曲面上的样条**（★ `CreateSpline2` 的继任者）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_createspline3.py
# 定位:   ★ 2026-10-03（轮 576）★ 照新纪律（**官方文档是第 0 步**）攻台账「样式样条曲线 / 曲面上的样条曲线」。
#
#   ★★★★★ **而本轮先把一条关系查清了**：
#     `ISketchManager.CreateSpline2.md` 逐字：**Obsolete. Superseded by `ISketchManager::CreateSpline3`** ⚠
#     ⇒ ★★ **故 `CreateSpline2`（我上一轮刚证的）**只是第一代****，
#       ★ 而 `CreateSpline3` **未标废弃**、★ **且它才是"曲面上的样条"的正主** ✓
#
#   ★★★★★ **`CreateSpline3` 的签名与 Remarks（逐字）**：
#     ```
#     object CreateSpline3(object PointData, object Surfs, object Direction,
#                          bool SimulateNaturalEnds, out object Status)      \u2190 **5 \u53c2**
#
#     \u2605 **2D \u6837\u6761**\uff1aPointData \u81f3\u5c11 **6 \u4e2a\u5750\u6807**\uff08\u9996\u5c3e\u4e24\u70b9\uff09\uff1b
#        SimulateNaturalEnds = true/false\uff1b\u2605 **\u5176\u4f59\u53c2\u6570\u5168\u7ed9 `null`/`Nothing`**
#     \u2605 **\u66f2\u9762\u4e0a\u7684\u6837\u6761**\uff1aPointData = \u4e24\u4e2a\u4ee5\u4e0a 3D \u70b9\uff1b
#        **Surfs** = `ISurface` \u6570\u7ec4\uff1b**Direction** = `IMathVector` \u6570\u7ec4\uff1b
#        **Status** = \u6bcf\u70b9\u7684\u72b6\u6001\u6570\u7ec4\uff08\u2605 \u4ec5 on-surface \u7528\uff09
#     ```
#
#   ★ 判据（★ 规则 6 + 事实 436）：**草图段数增加**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 三格：2D（6 坐标）/ on-surface（曲面 + 方向）/ 对照（参数给错）。
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

import pythoncom                                                     # noqa: E402
import win32com.client                                               # noqa: E402
from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_surface_features as SF                         # noqa: E402

#: \u2605 **2D**\uff1a\u81f3\u5c11 6 \u4e2a\u5750\u6807
PTS_2D = [-0.02, -0.01, 0.0,
          0.0, 0.02, 0.0,
          0.02, -0.01, 0.0]


def _arr(values, vt=pythoncom.VT_R8):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | vt, list(values))


def _byref():
    #: \u2605 `out Status`\uff1a\u2605 \u7528 byref-variant \u63a5
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:                                                     # noqa: BLE001
        return -1


def _mk_surface(doc):
    """★ 一张**平面曲面**（★ 供 on-surface 那格用 —— ★ 用**平面区域**，★ 事实 443 那招）。"""
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.05, -0.05, 0.0, 0.05, 0.05, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    sk = names[-1] if names else None
    ext = C.get_com_member(doc, "Extension")
    for cand in (P._get_sketch_name_candidates(sk) if sk else []):
        try:
            if P._select_by_id(ext, cand, "SKETCH", append=False, mark=1):
                break
        except Exception:                                                 # noqa: BLE001
            continue
    try:
        C.get_com_member(doc, "InsertPlanarRefSurface")
    except Exception:                                                     # noqa: BLE001
        return None
    from sw_connect import get_com_member as _g
    for b in list(_g(doc, "GetBodies2", 1, True) or []):
        for f in list(_g(b, "GetFaces") or []):
            try:
                return _g(f, "GetSurface")
            except Exception:                                             # noqa: BLE001
                continue
    return None


def _one(sw, tag, mode):
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        sm = C.get_com_member(doc, "SketchManager")
        if mode == "on_surface":
            surf = _mk_surface(doc)
            row["surface"] = surf is not None
        else:
            surf = None
        P.start_sketch(doc, plane_name="Front Plane")
        before = _seg_count(doc)
        row["seg_before"] = before
        ret = None
        try:
            if mode == "on_surface":
                #: \u2605 **on-surface**\uff1aPointData(3D \u70b9) + Surfs + Direction + Status
                #: ★★ 2026-10-03\uff08\u8f6e 577\uff09**\u4fee\u6b63\u5165\u53e3**\uff1a
                #:   `GetMathUtility` \u5728 **`ISldWorks`** \u4e0a\uff08\u2605 **0 \u53c2**\uff09\u3001
                #:   \u2605 **\u800c\u4e0d\u5728 `IModelDoc2` \u4e0a** \u2014\u2014
                #:   \u2605 \u4e0a\u4e00\u8f6e\u6211\u5728 doc \u4e0a\u53d6\u5b83 \u21d2 `AttributeError`\uff08**\u7b2c\u56db\u7c7b\u5f62\u6001**\uff09\u3002
                #: \u2605\u2605 **\u800c\u672c\u8f6e\u53c8\u628a\u6bcf\u4e00\u6b65\u5206\u5f00\u8bb0\u8d26** \u2014\u2014
                #:   \u2605 \u4e0a\u4e00\u7248\u628a\u5b83\u4eec\u5305\u5728\u540c\u4e00\u4e2a `try` \u91cc \u21d2 **\u5206\u4e0d\u6e05\u662f\u54ea\u4e00\u6b65\u62a5\u7684** \u26a0
                steps = {}
                mv = None
                try:
                    mv = C.get_com_member(sw, "GetMathUtility")
                    steps["GetMathUtility"] = "ok" if mv is not None else "None"
                except Exception as exc:                                  # noqa: BLE001
                    steps["GetMathUtility"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
                v = None
                if mv is not None:
                    #: \u2605\u2605 2026-10-03\uff08\u8f6e 577\uff09\uff1a`CreateVector(object)` \u62a5**\u627e\u4e0d\u5230\u6210\u5458**
                    #:   \uff08\u2605 **\u7b2c\u56db\u7c7b\u5f62\u6001**\uff09\u21d2 \u2605 \u6539\u8bd5\u53cd\u5c04\u91cc\u90a3\u4e2a **`ICreateVector`**
                    #:   \uff08\u2605 `MathVector ICreateVector(ref double ArrayDataIn)` \u2014\u2014 \u2605 \u4e0e `out_i4` \u90a3\u65cf**\u540c\u7406**\uff09
                    for nm in ("CreateVector", "ICreateVector"):
                        try:
                            v = C.call_com_member(mv, nm, _arr([0.0, 0.0, -1.0]))
                            steps["CreateVector(%s)" % nm] = type(v).__name__ if v is not None else "None"
                            if v is not None:
                                break
                        except Exception as exc:                          # noqa: BLE001
                            steps["CreateVector(%s)" % nm] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
                row["steps"] = steps
                if v is not None:
                    ret = C.get_com_member(sm, "CreateSpline3",
                                           _arr([0.0, 0.0, 0.02, 0.02, 0.0, 0.02]),
                                           _arr([surf], pythoncom.VT_DISPATCH),
                                           _arr([v, v], pythoncom.VT_DISPATCH),
                                           False, _byref())
            elif mode == "2d":
                #: \u2605 **2D**\uff1a\u81f3\u5c11 6 \u4e2a\u5750\u6807\uff1b\u2605 \u5176\u4f59\u53c2\u6570 **null**
                ret = C.get_com_member(sm, "CreateSpline3",
                                       _arr(PTS_2D), None, None, False, _byref())
            else:
                #: \u2605 \u5bf9\u7167\uff1a\u2605 \u53c2\u6570\u7ed9**\u9519**\uff08\u2605 \u628a 2D \u7684\u5750\u6807\u7ed9\u6210\u4e00\u4e2a\u70b9\uff09
                ret = C.get_com_member(sm, "CreateSpline3",
                                       _arr([0.0, 0.0, 0.0]), None, None, False, _byref())
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


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "`CreateSpline3`\uff08\u2605 `CreateSpline2` \u7684**\u7ee7\u4efb\u8005**\uff0c\u2605 \u800c\u5b83\u624d\u662f"
               "\u201c\u66f2\u9762\u4e0a\u7684\u6837\u6761\u201d\u7684\u6b63\u4e3b\uff09",
          "official": "CreateSpline2.md \u9010\u5b57\uff1aObsolete. Superseded by CreateSpline3\uff1b"
                      "CreateSpline3 \u7684 Remarks\uff1a2D\uff08\u81f3\u5c11 6 \u5750\u6807\u3001\u5176\u4f59 null\uff09"
                      "\u00b7 on-surface\uff08Surfs = ISurface \u6570\u7ec4\u3001Direction = IMathVector \u6570\u7ec4\uff09",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 **2D** \u6837\u6761\uff08\u2605 6 \u5750\u6807 + \u5176\u4f59 null\uff09", "2d"))
    ev["cases"].append(_one(sw, "\u2605 **\u66f2\u9762\u4e0a\u7684\u6837\u6761**\uff08Surfs + Direction\uff09", "on_surface"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u53ea\u7ed9**\u4e00\u4e2a\u70b9**\uff08\u2605 \u4e0d\u8db3 6 \u5750\u6807\uff09", "bad"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("spline3_2d_%s_on_surface_%s" % (ev["cases"][0].get("ok"), ev["cases"][1].get("ok")))
    p = R / "output" / "createspline3-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-46s ok=%-6s \u6bb5 %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s" % (
            c.get("tag"), c.get("ok"), c.get("seg_before"), c.get("seg_after"),
            c.get("new_segments"), c.get("returned")))
        if c.get("surface") is not None:
            print("        surface=%s" % c.get("surface"))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
