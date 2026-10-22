"""★ 真机：直纹曲面（`IFeatureManager.InsertRuledSurfaceFromEdge2`）—— B6/T608。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_ruled_surface.py
# 定位:   ★ 2026-10-03（轮 505）★ 给 `sw_surface_features.insert_ruled_surface_report`
#            留真机证据。
#   ★ 对应 `specs/201-toolbar-gaps` 的 **T608**（★ 而 T605-T609 这几条一直空着）。
#
# ★★ **本轮逮到一处两源冲突**（★ 正是**铁律 4** 的活教材）⚠：
#   · 官方 `c_:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge2.md` 的**参数表**：
#     `Type` ⇒ **0 = Tangent to Surface · 1 = Normal · 2 = Tapered to Vector ·
#     3 = Perpendicular to Vector · 4 = Sweep**（★ 看着是 **0-based**）
#   · 而**反射转储** `_raw/enum_values_sldworks.txt` 的 `swRuledSurfaceType_e`：
#     `TangentToSurface = **1**` · `NormalToSurface = **2**` · `TaperedToVector = **3**` ·
#     `PerpendicularToVector = **4**` · `Sweep = **5**`（★ **1-based** ⇒ **整体差 1**）
#   ⇒ ★★ **铁律 4：冲突以出厂类型库为准** ⇒ 本探针**两组都试**，★ 用真机定谁对 ✓
#
# ★ 官方第一句：「Inserts a ruled surface from the **selected edge**」⇒ ★ **要先选一条边
# **
#     （★ 而边**没有名字** ⇒ ★ 按对象选 —— **事实 32**）。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：★ **特征树多了新特征**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


def _build_solid(sw):
    """★ 建一个**实体盒**（★ 直纹曲面要"从一个边"长出来）。"""
    doc = c_.new_document(sw, "part")
    p_.start_sketch(doc, plane_name="Front Plane")
    c_.get_com_member(
        c_.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.02,
        -0.02,
        0.0,
        0.02,
        0.02,
        0.0,
    )
    p_.end_sketch(doc)
    for cand in ("\u8349\u56fe1", "Sketch1"):
        try:
            p_.extrude_boss(doc, cand, 0.02)
            break
        except Exception:  # noqa: BLE001
            continue
    return doc


def _pick_edge(doc, idx=0, mark=0):
    """★ **按对象选一条边**（★ 边没有名字 —— 事实 32）⇒ 回来读计数。"""
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    n = 0
    for b in list(c_.get_com_member(doc, "GetBodies2", 0, True) or []):
        try:
            edges = list(c_.get_com_member(b, "GetEdges") or [])
        except Exception:  # noqa: BLE001
            continue
        if idx < len(edges):
            if p_._select_com_object(edges[idx], append=True, mark=mark):
                n += 1
        break
    return n


def _one(sw, tag, *, surface_type, need_edge=True, length_mm=10.0):
    row = {"tag": tag, "surface_type": surface_type, "ok": False}
    doc = None
    try:
        doc = _build_solid(sw)
        row["solid"] = sf._solid_body_count(doc)
        row["sel"] = _pick_edge(doc, 0) if need_edge else 0
        r = sf.insert_ruled_surface_report(
            doc, surface_type=surface_type, length_mm=length_mm
        )
        row["result"] = {k: v for k, v in r.items() if k != "\u2605"}
        row["ok"] = bool(r.get("ok"))
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(c_.get_com_member(doc, "GetTitle") or "")
                if t:
                    c_.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = c_.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u76f4\u7eb9\u66f2\u9762\uff08InsertRuledSurfaceFromEdge2\uff09\u2014\u2014 B6/T608",
        "judge": "\u7279\u5f81\u6811\u589e\u91cf\uff08\u89c4\u5219 6\uff09",
        "two_source_conflict": {
            "swapi_md_param_table": "Type: 0=Tangent to Surface \u00b7 1=Normal \u00b7 2=Tapered to Vector \u00b7 3=Perpendicular to Vector \u00b7 4=Sweep",
            "reflection_enum": "swRuledSurfaceType_e: TangentToSurface=1 \u00b7 NormalToSurface=2 \u00b7 TaperedToVector=3 \u00b7 PerpendicularToVector=4 \u00b7 Sweep=5",
            "rule":
            "\u94c1\u5f8b 4\uff1a\u51b2\u7a81\u4ee5\u51fa\u5382\u7c7b\u578b\u5e93\u4e3a\u51c6 \u21d2 \u672c\u63a2\u9488\
            u4e24\u7ec4\u90fd\u8bd5\uff0c\u7528\u771f\u673a\u5b9a",
        },
        "cases": [],
    }
    #: ★ \u2460 \u6309**\u679a\u4e3e\u53e3\u5f84**\uff081 = TangentToSurface\uff09
    ev["cases"].append(
        _one(
            sw,
            "\u679a\u4e3e\u53e3\u5f84 type=1\uff08\u2605 \u94c1\u5f8b 4 \u7684\u9009\u6cd5\uff09",
            surface_type=1,
        )
    )
    #: \u2605 \u2461 \u6309**md \u53c2\u6570\u8868\u53e3\u5f84**\uff080 = Tangent to Sur
    #: face\uff09
    ev["cases"].append(
        _one(sw, "\u2605 md \u53e3\u5f84\u90a3\u4e00\u7ec4 type=0", surface_type=0)
    )
    #: \u2605 \u2462 \u679a\u4e3e\u53e3\u5f84\u7684 5 = Sweep
    ev["cases"].append(
        _one(sw, "\u679a\u4e3e\u53e3\u5f84 type=5\uff08Sweep\uff09", surface_type=5)
    )
    #: \u2605 \u2463 \u8d1f\u4f8b\uff1a\u4e0d\u9009\u8fb9
    ev["cases"].append(
        _one(
            sw, "\u8d1f\u4f8b\uff1a\u4e0d\u9009\u8fb9", surface_type=1, need_edge=False
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "ruled-surface-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u6210\u4e86 **%d / %d**" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print(
            "  %-32s ok=%-6s sel=%-3s %s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("sel"),
                json.dumps(c.get("result") or c.get("err"), ensure_ascii=False)[:130],
            )
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
