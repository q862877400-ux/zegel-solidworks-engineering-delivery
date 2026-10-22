"""★ 真机：**删除孔** —— 在**带内环（缺口）的曲面体**上试（★ 事实 438 留的下一步）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_delete_hole_on_surface.py
# 定位:   ★ 2026-10-03（轮 560）★ 执行**事实 438 留的下一步**：
#
#   > ★ 故在**原生实体**上它是 no-op 是**应然的**（★ 名字误导）
#   > ★ **下一步**：★ 在**带缺口的曲面体**上试（★ 而不是在实体上）。
#
#   ★ **怎么造"带缺口的曲面"**：★ 一个草图里画**外框矩形 + 内圈圆** ⇒
#     ★ 用 `IFeatureManager` 的**曲面拉伸**拉它 ⇒ ★ 得到一张
#     **带内环（= 孔）的平面曲面** —— ★ 那才是"删除孔"要处理的形态。
#
#   ★ 成员仍是 **`IModelDoc2.InsertDeleteHole()`**（★ 0 参 · 回 `void`）。
#   ★ 判据（★ 三条一起，★ 事实 436/438 的教训：用几何量）：
#     ① **面数 / 环数** ② **面积**（★ 填孔会让面积变大）③ 树增量
#   ⚠ 全程走 `tools/sw_guard.py`；★ 三组：只选面 / 选孔边 / 不选（对照）。
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
    """★ 一张**带内环（孔）的平面曲面**。"""
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    sm = C.get_com_member(doc, "SketchManager")
    #: \u2605 \u5916\u6846
    C.get_com_member(sm, "CreateCornerRectangle", -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    #: \u2605 \u5185\u5708\uff08\u2605 \u90a3\u5c31\u662f\u201c\u5b54\u201d\uff09
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


def _geom(doc):
    from sw_connect import get_com_member as _g

    faces = loops = edges = 0
    area = 0.0
    for b in list(_g(doc, "GetBodies2", 1, True) or []):
        for f in list(_g(b, "GetFaces") or []):
            faces += 1
            try:
                loops += len(list(_g(f, "GetLoops") or []))
            except Exception:  # noqa: BLE001
                pass
            for m in ("GetArea",):
                try:
                    v = _g(f, m)
                    if v is not None:
                        area += float(v)
                except Exception:  # noqa: BLE001
                    pass
        try:
            edges += len(list(_g(b, "GetEdges") or []))
        except Exception:  # noqa: BLE001
            pass
    return {"faces": faces, "loops": loops, "edges": edges, "area": area}


def _one(sw, tag, pick):
    row = {"tag": tag, "pick": pick, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        rep = _mk_surface_with_hole(doc)
        row["made"] = bool((rep or {}).get("ok"))
        row["before"] = _geom(doc)
        from sw_connect import get_com_member as _g
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        picked = 0
        for b in list(_g(doc, "GetBodies2", 1, True) or []):
            if pick in ("face", "both"):
                for f in list(_g(b, "GetFaces") or [])[:1]:
                    if _sel(f, append=(picked > 0), mark=0):
                        picked += 1
            if pick in ("edge", "both"):
                #: \u2605 \u5185\u73af\u90a3\u5708\u8fb9\uff08\u2605 \u5c31\u662f\u201c\
                #: u5b54\u7684\u8fb9\u201d\uff09
                for e in list(_g(b, "GetEdges") or []):
                    try:
                        if _sel(e, append=True, mark=0):
                            picked += 1
                    except Exception:  # noqa: BLE001
                        pass
                    if picked >= 4:
                        break
            break
        row["picked"] = picked
        before = list(FR.feature_names(doc) or [])
        try:
            _g(doc, "InsertDeleteHole")
            row["called"] = True
        except Exception as exc:  # noqa: BLE001
            row["called"] = False
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["after"] = _geom(doc)
        d = row["after"]
        b0 = row["before"]
        row["delta"] = {k: (d[k] - b0[k]) for k in ("faces", "loops", "edges")}
        row["area_delta"] = d["area"] - b0["area"]
        #: \u2605 \u5224\u636e\uff1a**\u51e0\u4f55\u91cf\u53d8\u4e86** \u6216 \u6811\u58
        #: 9e\u91cf
        row["ok"] = bool(
            row["new"] or any(row["delta"].values()) or abs(row["area_delta"]) > 1e-12
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
        "_": "\u5220\u9664\u5b54\uff1a\u5728**\u5e26\u5185\u73af\uff08\u7f3a\u53e3\uff09\u7684\u66f2\u9762\u4f53**\u4e0a\u8bd5\uff08\u2605 \u800c\u4e0d\u662f\u5728\u5b9e\u4f53\u4e0a\uff09",
        "official": "IModelDoc2.InsertDeleteHole() \u2014\u2014 0 \u53c2 \u00b7 void\uff1b"
        "\u5b83\u662f**\u66f2\u9762 / \u5bfc\u5165\u4f53\u7684\u4fee\u8865**\u547d\u4ee4",
        "cases": [],
    }
    ev["cases"].append(_one(sw, "\u2460 \u53ea\u9009\u9762", "face"))
    ev["cases"].append(_one(sw, "\u2461 \u9009\u5b54\u7684\u8fb9", "edge"))
    ev["cases"].append(_one(sw, "\u2462 \u9762 + \u8fb9\u90fd\u9009", "both"))
    ev["cases"].append(
        _one(sw, "\u2463 \u5bf9\u7167\uff1a\u4ec0\u4e48\u90fd\u4e0d\u9009", "none")
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "delete_hole_works_on_surface"
        if ev["passed"]
        else "delete_hole_still_noop_on_surface"
    )
    p = R / "output" / "delete-hole-on-surface-evidence.json"
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
            "  %-26s ok=%-6s made=%s picked=%s"
            % (c.get("tag"), c.get("ok"), c.get("made"), c.get("picked"))
        )
        print(
            "        \u9762 %s\u2192%s \u00b7 \u73af %s\u2192%s \u00b7 \u8fb9 %s\u2192%s \u00b7 \u9762\u79ef\u0394=%.4e"
            % (
                b.get("faces"),
                a.get("faces"),
                b.get("loops"),
                a.get("loops"),
                b.get("edges"),
                a.get("edges"),
                c.get("area_delta") or 0.0,
            )
        )
        print("        \u65b0\u589e=%s" % (c.get("new"),))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
