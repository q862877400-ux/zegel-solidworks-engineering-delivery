"""★ 真机：T605 平面区域 / T609 替换面的**选法变体**（上一轮各只试了一种）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_planar_replace_variants.py
# 定位:   ★ 2026-10-03（轮 517）★ 试**上一轮留在事实 398 里的两条下一步**：
#
#   | 能力 | 上轮试的选法 | 上轮结果 | 本轮要试的 |
#   |---|---|---|---|
# | T605 平面区域 | **曲面体的边**（12 条，mark=1） | 0 增量 | ★ **草图边界**（mark=1）
# |
#   | T609 替换面 | 实体面 mark=1 + 曲面面 mark=2 | 0 增量 | ★ **把两个 mark 调过来** |
#
#   官方 `Remarks`（逐字，只有它给了线索）：
#   · `InsertPlanarRefSurface` ⇒ 「select the surface's **boundary entities** using
#     `SelectByID2` with **Marks of 1**」⇒ ★ 「boundary **entities**」**没说是边还是草图**
#     ⇒ ★ 故两种都试（★ 上轮试了边，本轮试草图）✓
# · `InsertFeatureReplaceFace` ⇒ 「select the faces to **replace** … with **Marks of 1**
#  and
#     select the re[placement face] …」⇒ ★★ **替换面那个 mark 官方句子被截断了** ⚠
#     ⇒ ★ 故 mark 分工只能**两种都试** ✓
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：**特征树多了新特征**。

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


def _mk_surface(doc, plane="Front Plane", depth=20.0):
    P.start_sketch(doc, plane_name=plane)
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.02,
        -0.02,
        0.0,
        0.02,
        0.02,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if SF.create_extruded_surface_report(doc, depth, sketch_name=cand).get(
                "ok"
            ):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _mk_solid(doc):
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
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _sel_sketch_by_name(doc, name, mark=1, append=False):
    """★ 按**名字**选草图（★ 特征按名字选是可行的 —— 事实 32 只对**实体**说不可行）。"""
    ext = C.get_com_member(doc, "Extension")
    for cand in P._get_sketch_name_candidates(name):
        try:
            if P._select_by_id(ext, cand, "SKETCH", append=append, mark=mark):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _two_face_marks(doc, solid_mark, surface_mark):
    """★ 两张面、★ mark 分工由调用方给（★ 用来把两种分工都试一遍）。"""
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel

    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    n = 0
    for body_type, mk in ((0, solid_mark), (1, surface_mark)):
        try:
            bodies = list(_get(doc, "GetBodies2", body_type, True) or [])
        except Exception:  # noqa: BLE001
            bodies = []
        for b in bodies[:1]:
            try:
                faces = list(_get(b, "GetFaces") or [])
            except Exception:  # noqa: BLE001
                continue
            if faces and _sel(faces[0], append=True, mark=mk):
                n += 1
    return n


def _case_planar_sketch(doc):
    """★ T605 变体：★ 先建曲面 + ★ **草图**（闭合轮廓）⇒ 按 mark=1 选草图。"""
    _mk_surface(doc)
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.01,
        -0.01,
        0.0,
        0.01,
        0.01,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    picked = _sel_sketch_by_name(doc, names[-1] if names else "\u8349\u56fe2", mark=1)
    try:
        sel = int(
            C.get_com_member(
                C.get_com_member(doc, "SelectionManager"), "GetSelectedObjectCount2", -1
            )
            or 0
        )
    except Exception:  # noqa: BLE001
        sel = -1
    before = list(P.feature_names(doc) or [])
    ret = None
    err = None
    try:
        ret = C.get_com_member(doc, "InsertPlanarRefSurface")
    except Exception as exc:  # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    after = list(P.feature_names(doc) or [])
    new = [n for n in after if n not in before]
    return {
        "ok": bool(new),
        "variant": "\u9009**\u8349\u56fe**\uff08mark=1\uff09",
        "picked": picked,
        "sel_count": sel,
        "returned": repr(ret)[:30],
        "new_features": new,
        "error": err,
    }


def _case_replace(doc, solid_mark, surface_mark):
    _mk_solid(doc)
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    _mk_surface(doc, plane="Right Plane")
    n = _two_face_marks(doc, solid_mark, surface_mark)
    before = list(P.feature_names(doc) or [])
    err = None
    try:
        C.get_com_member(doc, "InsertFeatureReplaceFace")
    except Exception as exc:  # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    after = list(P.feature_names(doc) or [])
    new = [n for n in after if n not in before]
    return {
        "ok": bool(new),
        "variant": "\u5b9e\u4f53\u9762 mark=%d \u00b7 \u66f2\u9762\u9762 mark=%d"
        % (solid_mark, surface_mark),
        "faces_selected": n,
        "new_features": new,
        "error": err,
    }


def _run(sw, tag, fn):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        r = fn(doc)
        row["result"] = r
        row["ok"] = bool(r.get("ok"))
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
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
        "_": "T605 / T609 \u7684**\u9009\u6cd5\u53d8\u4f53**\uff08\u2605 \u4e0a\u4e00\u8f6e\u5404\u53ea\u8bd5\u4e86\u4e00\u79cd\uff09",
        "cases": [],
    }
    ev["cases"].append(
        _run(sw, "T605 \u53d8\u4f53\uff1a\u9009\u8349\u56fe", _case_planar_sketch)
    )
    ev["cases"].append(
        _run(
            sw,
            "T609 \u53d8\u4f53 A\uff1a\u5b9e\u4f53\u9762=1 \u66f2\u9762\u9762=2",
            lambda d: _case_replace(d, 1, 2),
        )
    )
    ev["cases"].append(
        _run(
            sw,
            "T609 \u53d8\u4f53 B\uff1a\u5b9e\u4f53\u9762=2 \u66f2\u9762\u9762=1",
            lambda d: _case_replace(d, 2, 1),
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "planar-replace-variants-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u6210\u4e86 **%d / %d**" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-34s ok=%-6s" % (c.get("tag"), c.get("ok")))
        print(
            "        %s"
            % json.dumps(c.get("result") or c.get("err"), ensure_ascii=False)[:190]
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
