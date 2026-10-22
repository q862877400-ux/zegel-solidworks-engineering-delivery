"""★ 真机：**界定**事实 406 那个「回读盲区」的边界（★ 哪些特征 `feature_names` 看得见）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_readback_blindspot_bounds.py
# 定位:   ★ 2026-10-03（轮 527）★ 把事实 406 那条**笼统的**「回读有盲区」查成**有边界
#           的**。
#
#   ★★ 事实 406 逐字：「本仓有**大量**判据写着『**特征树增量**』（规则 6 的落地）
#     ⇒ ★ 故**它们都可能在同一个盲区上误判**」⚠
#     ★ 而那条事实的**证据只有一条**：`InsertCutSurface` 的返回值（`SurfCut`）
#       在 `FirstFeature` 链与递归链上**都看不见**。
#   ⇒ ★★ **故本轮要问**：★ **这个盲区是"所有特征"还是"某些特征"？**
#     ★ 用一个**已成过**的特征做对照最干净 —— ★ 而本仓恰好有三条**真机验过建成**的：
# 等距曲面 `曲面-等距1`（事实 398）· 平面区域 `曲面-基准面1` · 替换面 `替换面1`（事实 39
# 8）。
#     · ★ 若它们**看得见** ⇒ ★★ **盲区是**特定特征**的**（★ 而 `SurfCut` 属于那种）
#     · ★ 若它们**也看不见** ⇒ ★★ **盲区是**通用**的**（★ 那全仓判据都危险）
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 本探针**不求建成** —— ★ 它要的是**哪些建成的特征在树上看得见**。

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
import scripts.sw_weldment as W  # noqa: E402


def _mk_surface(doc, plane="Front Plane", rect=(-0.02, -0.02, 0.02, 0.02)):
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
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
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


def _visible(doc, tag):
    """★ 回 ① `feature_names` ② 递归链 ③ 两边的**类型名集合**。"""
    names = list(FR.feature_names(doc) or [])
    types = []
    try:
        for f in W.iter_features_recursive(doc):
            try:
                types.append(str(C.get_com_member(f, "GetTypeName2") or ""))
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass
    return {
        "tag": tag,
        "names": names,
        "n_names": len(names),
        "types": types,
        "n_types": len(types),
    }


def _run(sw, tag, build):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        ret = build(doc)
        row["build"] = (
            ret
            if not isinstance(ret, dict)
            else {k: v for k, v in ret.items() if k != "\u2605"}
        )
        row["vis"] = _visible(doc, tag)
        row["new_names"] = (row["vis"] or {}).get("names")
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


def _c_extend(doc):
    _mk_surface(doc)
    return SF.insert_extend_surface_report(doc, 5.0)


def _c_offset(doc):
    _mk_surface(doc)
    return SF.insert_offset_surface_report(doc, 5.0)


def _c_planar(doc):
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
    return SF.insert_planar_ref_surface_report(doc)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "**\u754c\u5b9a**\u56de\u8bfb\u76f2\u533a\u7684\u8fb9\u754c\uff08\u2605 \u54ea\u4e9b\u5df2\u5efa\u6210\u7684\u7279\u5f81\u5728\u6811\u4e0a\u770b\u5f97\u89c1\uff09",
        "why": "\u4e8b\u5b9e 406 \u53ea\u6709\u4e00\u6761\u8bc1\u636e\uff08SurfCut\uff09\uff0c\u800c\u5b83\u5f71\u54cd\u9762\u5199\u5f97\u5f88\u5bbd",
        "cases": [],
    }
    for tag, fn in (
        (
            "\u2605 \u5ef6\u4f38\u66f2\u9762\uff08\u2605 \u5df2\u9a8c\u6210\uff09",
            _c_extend,
        ),
        (
            "\u2605 \u7b49\u8ddd\u66f2\u9762\uff08\u2605 \u5df2\u9a8c\u6210\uff09",
            _c_offset,
        ),
        (
            "\u2605 \u5e73\u9762\u533a\u57df\uff08\u2605 \u5df2\u9a8c\u6210\uff09",
            _c_planar,
        ),
    ):
        ev["cases"].append(_run(sw, tag, fn))
    for c in ev["cases"]:
        v = c.get("vis") or {}
        b = c.get("build") or {}
        c["visible_in_names"] = bool(b.get("new_features")) and any(
            n in (v.get("names") or []) for n in (b.get("new_features") or [])
        )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("visible_in_names"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "blindspot_is_narrow" if ev["passed"] == ev["total"] else "blindspot_is_broad"
    )
    p = R / "output" / "readback-blindspot-bounds-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u770b\u5f97\u89c1 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"])
    )
    for c in ev["cases"]:
        b = c.get("build") or {}
        v = c.get("vis") or {}
        print(
            "  %-30s ok=%-6s \u65b0\u5efa=%s"
            % (c.get("tag"), b.get("ok"), b.get("new_features"))
        )
        print(
            "        \u5728 feature_names \u91cc\u770b\u5f97\u89c1=%s \u00b7 \u5171 %d \u4e2a\u540d\u5b57"
            % (c.get("visible_in_names"), v.get("n_names", -1))
        )
        if c.get("err"):
            print("        ERR=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
