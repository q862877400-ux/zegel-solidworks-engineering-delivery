"""★ 真机：解除剪裁 —— 把上一轮收窄的三个可能**一次试完**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_untrim_matrix.py
# 定位:   ★ 2026-10-03（轮 558）★ 执行**事实 436 收窄出的三个可能**。
#
#   ★★ 事实 436 已定：★ **前置可以造对**（用 `PreTrimSurface`+`PostTrimSurface` 真剪，
#     面数 8→7），★ 而 `InsertUntrimSurface2` 仍回 `None`。
#     ⇒ ★ 剩下三个可能：
#       ⓐ 该选**边**而不是面（★ 官方 Remarks 逐字说 "face **or edges**"）
#       ⓑ `FaceUntrimType` / `EdgeUntrimType` 的**取值**不对
#       ⓒ 需要 `BTrimOppositeSide = True`
#
#   ★ 官方取值（★ 反射 · 铁律 4）：
#     ```
#     swFaceUntrimType_e : 0 = AllEdges · 1 = InternalEdges · 2 = ExternalEdges
#     swEdgeUntrimType_e : 1 = ConnectEndPoints · 2 = ExtendEdges
#     ```
#   ★ 本探针做**矩阵**（★ 每组新开文档、都先造出真被剪裁的曲面）：
#     ⓐ 选**面**，FaceUntrimType ∈ {0, 1, 2}
#     ⓑ 选**边**，EdgeUntrimType ∈ {1, 2}
#     ⓒ 面 + `BTrimOppositeSide = True`
#
#   ⚠ 全程走 `tools/sw_guard.py`。★ 判据：**面数变化**（★ 事实 436 的教训：数几何量）
#     **或** 树增量。
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

import scripts.sw_feature_readback as fr  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402
from scripts.sw_connect import create_empty_dispatch_variant as _av  # noqa: E402


def _mk_two(doc):
    made = 0
    for i, (plane, rect) in enumerate(
        (
            ("Front Plane", (-0.02, -0.02, 0.02, 0.02)),
            ("Top Plane", (-0.02, -0.01, 0.02, 0.01)),
        )
    ):
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name=plane)
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateCornerRectangle",
            rect[0],
            rect[1],
            0.0,
            rect[2],
            rect[3],
            0.0,
        )
        P.end_sketch(doc)
        names = [
            n
            for n in (P.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        for cand in ((names[-1],) + tuple(names) + ("\u8349\u56fe%d" % (i + 1),))[:4]:
            try:
                if sf.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get(
                    "ok"
                ):
                    made += 1
                    break
            except Exception:  # noqa: BLE001
                continue
    return made


def _faces(doc):
    from sw_connect import get_com_member as _g

    n = 0
    for b in list(_g(doc, "GetBodies2", 1, True) or []):
        try:
            n += len(list(_g(b, "GetFaces") or []))
        except Exception:  # noqa: BLE001
            pass
    return n


def _pre_trim(doc):
    """★ 造出**真被剪裁过的曲面**（★ 事实 436：面数 8 → 7）。"""
    from sw_connect import get_com_member as _g

    fm = _g(doc, "FeatureManager")
    _g(fm, "PreTrimSurface", False, True, False, False)
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    ext = _g(doc, "Extension")
    for pt in ((0.0, 0.0, 0.0), (0.005, 0.0, 0.005), (-0.005, 0.0, -0.005)):
        try:
            if _g(
                ext,
                "SelectByID2",
                "",
                "SURFACEBODY",
                pt[0],
                pt[1],
                pt[2],
                True,
                0,
                _av(),
                0,
            ):
                break
        except Exception:  # noqa: BLE001
            continue
    _g(fm, "PostTrimSurface", True)


def _one(sw, tag, pick, face_type, edge_type, b_trim):
    row = {
        "tag": tag,
        "pick": pick,
        "face_type": face_type,
        "edge_type": edge_type,
        "b_trim": b_trim,
        "ok": False,
    }
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["made"] = _mk_two(doc)
        row["faces_before_trim"] = _faces(doc)
        _pre_trim(doc)
        row["faces_after_trim"] = _faces(doc)
        from sw_connect import get_com_member as _g
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        picked = 0
        for b in list(_g(doc, "GetBodies2", 1, True) or []):
            if pick == "face":
                for f in list(_g(b, "GetFaces") or [])[:1]:
                    if _sel(f, append=(picked > 0), mark=0):
                        picked += 1
            else:
                for e in list(_g(b, "GetEdges") or [])[:2]:
                    if _sel(e, append=(picked > 0), mark=0):
                        picked += 1
            break
        row["picked"] = picked
        before = list(fr.feature_names(doc) or [])
        fm = _g(doc, "FeatureManager")
        ret = None
        try:
            ret = _g(
                fm,
                "InsertUntrimSurface2",
                int(face_type),
                int(edge_type),
                0.005,
                True,
                bool(b_trim),
            )
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret, m))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["faces_after_untrim"] = _faces(doc)
        row["face_delta"] = row["faces_after_untrim"] - row["faces_after_trim"]
        #: \u2605 \u5224\u636e\uff08\u2605 \u4e8b\u5b9e 436\uff1a\u6570\u51e0\u4f55\u91c
        #: f\uff09
        row["ok"] = bool(row["new"] or row.get("ret_type") or row["face_delta"])
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
        "_": "\u89e3\u9664\u526a\u88c1\uff1a**\u628a\u4e8b\u5b9e 436 \u6536\u7a84\u51fa\u7684\u4e09\u4e2a\u53ef\u80fd\u4e00\u6b21\u8bd5\u5b8c**",
        "official": "InsertUntrimSurface2(FaceUntrimType, EdgeUntrimType, Distance, BMerge, BTrimOppositeSide)\uff1b"
        "swFaceUntrimType_e 0/1/2 \u00b7 swEdgeUntrimType_e 1/2\uff1bRemarks: face **or edges**",
        "cases": [],
    }
    for tag, pick, ft, et, bt in (
        ("\u2460 \u9762 \u00b7 Face=0(AllEdges)", "face", 0, 2, False),
        ("\u2461 \u9762 \u00b7 Face=1(InternalEdges)", "face", 1, 2, False),
        ("\u2462 \u9762 \u00b7 Face=2(ExternalEdges)", "face", 2, 2, False),
        ("\u2463 \u8fb9 \u00b7 Edge=1(ConnectEndPoints)", "edge", 0, 1, False),
        ("\u2464 \u8fb9 \u00b7 Edge=2(ExtendEdges)", "edge", 0, 2, False),
        ("\u2465 \u9762 \u00b7 BTrimOppositeSide=True", "face", 0, 2, True),
    ):
        ev["cases"].append(_one(sw, tag, pick, ft, et, bt))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "untrim_works" if ev["passed"] else "untrim_still_fails"
    p = R / "output" / "untrim-matrix-evidence.json"
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
        print(
            "  %-38s ok=%-6s \u9762 %s\u2192%s\u2192%s\uff08\u0394%s\uff09"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("faces_before_trim"),
                c.get("faces_after_trim"),
                c.get("faces_after_untrim"),
                c.get("face_delta"),
            )
        )
        print(
            "        \u9009\u4e2d=%s \u56de=%s \u540d=%s \u578b=%s \u65b0\u589e=%s"
            % (
                c.get("picked"),
                c.get("returned"),
                c.get("ret_name"),
                c.get("ret_type"),
                c.get("new"),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
