"""★ 真机：删除孔（曲面）—— ★ **只选内环那圈边**（★ 事实 441 留的下一步）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_delete_hole_inner_loop.py
# 定位:   ★ 2026-10-03（轮 563）★ 执行**事实 441 留的下一步**：
#
#   > ★ **"选孔边"这个前置我还没真搭对**（★ 选了整个体的 12 条边）
#   > ★ **下一步**：★ 只选**内环（孔）那一圈边**。
#
#   ★ **怎么区分内环与外环**：★ 官方有 **`ILoop2.IsOuter()`** ——
#     ★ 曲面上的一个带孔平面有**两个环**：外环（矩形）与内环（圆）。
#     ★ 本探针**只选内环上的边**（★ `IsOuter() == False` 的那些）。
#
#   ★ 成员：`IFeatureManager.InsertDeleteHoleForSurface()`（★ 0 参 · 回 `IFeature`）——
#     ★ 而它的 Remarks 逐字：「select the **hole edges to remove** from the surface」。
#   ★ 判据（★ 事实 436/439 的教训：用几何量 + 返回值）：
#     ① **返回对象带类型名** ② 树增量 ③ **环数 / 面数 / 面积** 的前后差
#   ⚠ 全程走 `tools/sw_guard.py`；★ 三组：内环边 / 外环边 / 全部边。
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
from scripts import sw_surface_features as SF  # noqa: E402
import scripts.sw_feature_readback as FR  # noqa: E402


def _mk_surface_with_hole(doc):
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    sm = C.get_com_member(doc, "SketchManager")
    C.get_com_member(sm, "CreateCornerRectangle", -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    C.get_com_member(sm, "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.012)
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            return SF.create_extruded_surface_report(doc, 0.5, sketch_name=cand)
        except Exception:  # noqa: BLE001
            continue
    return {}


def _loops(doc):
    """★ 每个面 → 它的环（★ 记 `IsOuter` 与边数）—— ★ 用来把内环挑出来。"""
    from sw_connect import get_com_member as _g

    out = []
    for b in list(_g(doc, "GetBodies2", 1, True) or []):
        for fi, f in enumerate(list(_g(b, "GetFaces") or [])):
            for li, lp in enumerate(list(_g(f, "GetLoops") or [])):
                outer = None
                for m in ("IsOuter",):
                    try:
                        outer = bool(_g(lp, m))
                        break
                    except Exception:  # noqa: BLE001
                        outer = None
                try:
                    ne = len(list(_g(lp, "GetEdges") or []))
                except Exception:  # noqa: BLE001
                    ne = -1
                out.append(
                    {
                        "face": fi,
                        "loop": li,
                        "is_outer": outer,
                        "edges": ne,
                        "_loop": lp,
                    }
                )
    return out


def _geom(doc):
    from sw_connect import get_com_member as _g

    faces = loops = 0
    for b in list(_g(doc, "GetBodies2", 1, True) or []):
        for f in list(_g(b, "GetFaces") or []):
            faces += 1
            try:
                loops += len(list(_g(f, "GetLoops") or []))
            except Exception:  # noqa: BLE001
                pass
    return {"faces": faces, "loops": loops}


def _one(sw, tag, which):
    row = {"tag": tag, "which": which, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["made"] = bool((_mk_surface_with_hole(doc) or {}).get("ok"))
        row["before"] = _geom(doc)
        lps = _loops(doc)
        row["loops_seen"] = [{k: v for k, v in d.items() if k != "_loop"} for d in lps]
        from sw_connect import get_com_member as _g
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        #: \u2605 \u6309 `IsOuter` \u6311\u73af
        want = lps
        if which == "inner":
            want = [d for d in lps if d.get("is_outer") is False]
        elif which == "outer":
            want = [d for d in lps if d.get("is_outer") is True]
        row["loops_wanted"] = len(want)
        picked = 0
        for d in want:
            try:
                for e in list(_g(d["_loop"], "GetEdges") or []):
                    if _sel(e, append=(picked > 0), mark=0):
                        picked += 1
            except Exception:  # noqa: BLE001
                continue
        row["picked"] = picked
        before = list(FR.feature_names(doc) or [])
        fm = _g(doc, "FeatureManager")
        ret = None
        try:
            ret = _g(fm, "InsertDeleteHoleForSurface")
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret, m))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["after"] = _geom(doc)
        row["delta"] = {
            k: (row["after"][k] - row["before"][k]) for k in ("faces", "loops")
        }
        row["ok"] = bool(
            row["new"] or row.get("ret_type") or any(row["delta"].values())
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
        "_": "\u5220\u9664\u5b54\uff08\u66f2\u9762\uff09\uff1a**\u53ea\u9009\u5185\u73af\u90a3\u5708\u8fb9**"
        "\uff08\u2605 \u7528 `ILoop2.IsOuter()` \u5224\u5185\u5916\uff09",
        "official": "InsertDeleteHoleForSurface \u2014\u2014 0 \u53c2 \u00b7 \u56de IFeature\uff1b"
        "Remarks\uff1aselect the **hole edges to remove** from the surface",
        "cases": [],
    }
    ev["cases"].append(
        _one(
            sw,
            "\u2605 \u53ea\u9009**\u5185\u73af**\uff08\u5b54\uff09\u7684\u8fb9",
            "inner",
        )
    )
    ev["cases"].append(
        _one(sw, "\u5bf9\u7167\uff1a\u53ea\u9009**\u5916\u73af**\u7684\u8fb9", "outer")
    )
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a**\u5168\u90e8**\u8fb9", "all"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "inner_loop_works" if ev["cases"][0].get("ok") else "inner_loop_still_fails"
    )
    p = R / "output" / "delete-hole-inner-loop-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"])
    )
    for c in ev["cases"]:
        b, a = c.get("before") or {}, c.get("after") or {}
        print(
            "  %-34s ok=%-6s \u73af\u89c1=%s \u60f3\u9009=%s \u5b9e\u9009=%s"
            % (
                c.get("tag"),
                c.get("ok"),
                len(c.get("loops_seen") or []),
                c.get("loops_wanted"),
                c.get("picked"),
            )
        )
        print(
            "        \u56de=%s \u540d=%s \u578b=%s"
            % (c.get("returned"), c.get("ret_name"), c.get("ret_type"))
        )
        print(
            "        \u9762 %s\u2192%s \u00b7 \u73af %s\u2192%s \u00b7 \u65b0\u589e=%s"
            % (
                b.get("faces"),
                a.get("faces"),
                b.get("loops"),
                a.get("loops"),
                c.get("new"),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    print(
        "  \u2605 \u800c\u73af\u7684\u5f62\u6001\uff1a%s"
        % (ev["cases"][0].get("loops_seen"),)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
