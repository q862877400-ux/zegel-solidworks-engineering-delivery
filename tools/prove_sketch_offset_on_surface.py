"""★ 真机：**曲面上偏移** —— `IModelDocExtension.SketchOffsetOnSurface`（4 参）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_sketch_offset_on_surface.py
# 定位:   ★ 2026-10-03（轮 583）★ 照新纪律（**官方文档是第 0 步**）攻台账「曲面上偏移
#           」。
#
# ★★★★★ **官方那页（`C:\swapi\types\IModelDocExtension\SketchOffsetOnSurface.md`，★ 未标
# 废弃）**：
#     ```
# bool SketchOffsetOnSurface(double Offset, bool Reverse, bool UseFront, bool MakeConstr
# uct)
#     \u2605 Parameters\uff1a
# - **UseFront**: "**Although not currently used, must be set to true**"   \u2190 \u2605
#  \u5fc5\u987b\u7ed9 True
#     \u2605 Remarks\uff08\u9010\u5b57\uff09\uff1a
# "Before calling this method, call **`IModelDocExtension::SelectByID2` for each edge**
# to offset
#        and set **Append** \u2026"
# "**After calling this method, call `ISketchManager::InsertSketch` to rebuild the model
#  with the
#        **3D sketch**."
# \u2605 \u8fd1\u4eb2\uff1a`GeodesicSketchOffset`\uff08\u6cbf\u66f2\u7387\u7684**\u6d4b\
# u5730**\u504f\u79fb\uff09
#     ```
# \u21d2 \u2605\u2605 **\u6545\u4e09\u4e2a\u524d\u7f6e**\uff1a\u2460 **3D \u8349\u56fe**
# \uff1b\u2461 **\u5148\u628a\u8981\u504f\u79fb\u7684\u8fb9\u9009\u597d**\uff1b
# \u2462 `UseFront` **\u5fc5\u987b True**\uff1b\u2605 \u800c**\u4e4b\u540e\u8fd8\u8981\u
# 8c03 `InsertSketch`** \u624d\u91cd\u5efa\u6a21\u578b\u3002
#
# ★★ **而本探针按轮 107 的教训\uff1a每一步分开记账** —— \u2605 \u5426\u5219\u5206\u4e0d\
# u6e05\u54ea\u4e00\u6b65\u62a5\u7684\u3002
#   ★ 判据（★ 规则 6）：**草图段数 / 特征树增量**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两组：**给 `UseFront=True`** / 对照 `False`。
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

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
import scripts.sw_feature_readback as FR  # noqa: E402


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:  # noqa: BLE001
        return -1


def _solid(doc):
    """★ 一个**带直边的实体**（★ 方盒）—— ★ 供选边用。"""
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.03,
        -0.03,
        0.0,
        0.03,
        0.03,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in ((names[-1] if names else "\u8349\u56fe1"), "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _one(sw, tag, use_front, by_point=True):
    row = {"tag": tag, "use_front": use_front, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["solid"] = _solid(doc)
        from sw_connect import get_com_member as _g

        #: \u2605 **\u524d\u7f6e \u2460**\uff1a\u5148\u9009**\u8981\u504f\u79fb\u7684\u8
        #: fb9**
        #: \u2605\u2605 2026-10-03\uff08\u8f6e 583\uff09**\u4fee\u6b63**\uff1a\u5b98\u65
        #: b9 Remarks \u9010\u5b57\u8bf4\u7684\u662f
        #:   \u300ccall **`IModelDocExtension::SelectByID2`** for each edge\u300d\u3002
        #: \u2605 \u800c\u4e8b\u5b9e 32\uff1a**\u8fb9\u6309\u540d\u5b57\u9009\u4e0d\u4e2
        #: d**\uff08`("Edge1","EDGE")` \u8ba1\u6570 0\uff09\uff0c
        #: \u2605 \u800c**\u6309\u300c\u9762\u4e0a\u7684\u70b9\u300d\u5b9a\u4f4d\u53ef\u
        #: 884c**\uff08`SelectByID2("", "EDGE", x, y, z, \u2026)`\uff09\u2713
        #: \u21d2 \u6545\u672c\u8f6e\u4e24\u79cd\u90fd\u8bd5\uff1a**by_point**\uff08\u53
        #: d6\u8fb9\u7684**\u4e2d\u70b9**\uff09/ **by_object**\uff08\u65e7\u6cd5\uff09\u
        #: 3002
        picked = 0
        hint = None
        ext0 = _g(doc, "Extension")
        for b in list(_g(doc, "GetBodies2", 0, True) or []):
            edges = list(_g(b, "GetEdges") or [])
            if by_point:
                for e in edges[:2]:
                    try:
                        #: \u2605 \u53d6\u8fb9\u7684**\u4e2d\u70b9**\uff08`ICurve.Evalua
                        #: te` \u62ff\u76f8\u53c2\u6570\u4e2d\u70b9\uff09
                        cv = _g(e, "GetCurve")
                        #: \u2605 \u5148\u62ff\u8d77\u70b9\uff08`GetCurveParams2` \u7b2c
                        #:  1/2 \u4e2a\u662f u/v \u8303\u56f4\uff09
                        pr = list(_g(cv, "GetCurveParams2") or [])
                        umid = (
                            (float(pr[0]) + float(pr[1])) / 2.0 if len(pr) >= 2 else 0.5
                        )
                        pt = list(_g(cv, "Evaluate", umid) or [])
                        if len(pt) >= 3:
                            ok = P._select_by_id(
                                ext0,
                                "",
                                "EDGE",
                                float(pt[0]),
                                float(pt[1]),
                                float(pt[2]),
                                append=(picked > 0),
                                mark=1,
                            )
                            if ok:
                                picked += 1
                    except Exception as exc:  # noqa: BLE001
                        hint = "%s: %s" % (type(exc).__name__, str(exc)[:60])
                row["by_point_hint"] = hint
            else:
                for e in edges[:2]:
                    try:
                        if P._select_com_object(e, append=(picked > 0), mark=1):
                            picked += 1
                    except Exception:  # noqa: BLE001
                        pass
            break
        row["picked_edges"] = picked
        #: \u2605 **\u524d\u7f6e \u2461**\uff1a\u5f00\u4e00\u4e2a **3D \u8349\u56fe**
        try:
            C.get_com_member(_g(doc, "SketchManager"), "Insert3DSketch", True)
            row["sketch3d"] = "ok"
        except Exception as exc:  # noqa: BLE001
            row["sketch3d"] = "%s: %s" % (type(exc).__name__, str(exc)[:60])
        before_seg = _seg_count(doc)
        before_feat = list(FR.feature_names(doc) or [])
        row["seg_before"] = before_seg
        #: \u2605 **\u4e3b\u8c03\u7528**\uff08\u2605 `UseFront` \u5b98\u65b9\u8bf4**\u5f
        #: c5\u987b True**\uff09
        ext = _g(doc, "Extension")
        steps = {}
        try:
            ret = _g(ext, "SketchOffsetOnSurface", 0.005, False, bool(use_front), False)
            steps["SketchOffsetOnSurface"] = str(ret)
        except Exception as exc:  # noqa: BLE001
            steps["SketchOffsetOnSurface"] = "%s: %s" % (
                type(exc).__name__,
                str(exc)[:80],
            )
        #: \u2605 **\u5b98\u65b9\u8bf4\u300cAfter\uff1a\u8c03 `InsertSketch` \u91cd\u5ef
        #: a\u6a21\u578b\u300d**
        try:
            _g(_g(doc, "SketchManager"), "InsertSketch", True)
            steps["InsertSketch"] = "ok"
        except Exception as exc:  # noqa: BLE001
            steps["InsertSketch"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        row["steps"] = steps
        after_seg = _seg_count(doc)
        after_feat = list(FR.feature_names(doc) or [])
        row["seg_after"] = after_seg
        row["new_features"] = [n for n in after_feat if n not in before_feat]
        row["ok"] = bool(
            (after_seg > before_seg and before_seg >= 0) or row["new_features"]
        )
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u66f2\u9762\u4e0a\u504f\u79fb\uff1a`IModelDocExtension.SketchOffsetOnSurface`\uff08**4 \u53c2**\uff09",
        "official": "Remarks \u9010\u5b57\uff1a\u5148 `SelectByID2` **\u6bcf\u6761\u8981\u504f\u79fb\u7684\u8fb9**\uff1b"
        '\u2605 `UseFront`\uff1a"**Although not currently used, must be set to true**"\uff1b'
        "\u2605 \u4e4b\u540e\u8981 `ISketchManager::InsertSketch` \u91cd\u5efa\uff08\u4ea7\u51fa **3D \u8349\u56fe**\uff09",
        "cases": [],
    }
    ev["cases"].append(
        _one(
            sw,
            "\u2605 **by_point**\uff08\u2605 \u5b98\u65b9\u8bf4\u7684 `SelectByID2`\uff09",
            True,
            True,
        )
    )
    ev["cases"].append(
        _one(sw, "\u5bf9\u7167\uff1a**by_object**\uff08\u65e7\u6cd5\uff09", True, False)
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "offset_on_surface_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "sketch-offset-on-surface-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print(
            "  %-42s ok=%-6s \u6bb5 %s \u2192 %s"
            % (c.get("tag"), c.get("ok"), c.get("seg_before"), c.get("seg_after"))
        )
        print(
            "        \u5b9e\u4f53=%s \u9009\u8fb9=%s 3D\u8349\u56fe=%s"
            % (c.get("solid"), c.get("picked_edges"), c.get("sketch3d"))
        )
        print("        \u65b0\u589e\u7279\u5f81=%s" % (c.get("new_features"),))
        for k, v in (c.get("steps") or {}).items():
            print("        step %-24s %s" % (k, str(v)[:96]))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
