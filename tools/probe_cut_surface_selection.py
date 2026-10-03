"""★ 真机：`InsertCutSurface` 的**选区变体**（★ 上一轮留的"另一个变量"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_cut_surface_selection.py
# 定位:   ★ 2026-10-03（轮 524）★ 执行**上一轮留在事实 404 里的那条下一步**：
#
#   > ★ 官方说「using the **preselected** surface or plane」—— ★ 而本包装用的是
#   >   `_select_all_surface_faces(mark=0)`（**全选所有面**）⇒
#   >   ★★ **可能只该选一张**（★ `KeepPieceIndex` 的 "Piece to keep **if there is
#   >   ambiguity**" 暗示有"哪一块"的语义），或改 **mark=1**。
#
#   ★ 而这是**另一个变量**（★ 不是重试已试过的参数）：上两轮动的是 **arity**（★ 已定死为 6），
#     本轮动的是**选什么 / 选几张 / mark 几** ✓
#
#   ★ 试的组：
#     ⓐ 全选曲面面 · mark=0（★ 上一轮那组 —— ★ 作为对照）
#     ⓑ **只选第一张**曲面面 · mark=0
#     ⓒ **只选第一张**曲面面 · **mark=1**
#     ⓓ 全选曲面面 · **mark=1**
#     ⓔ 只选一张**基准面** · mark=0
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
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from win32com.client import VARIANT as _V                            # noqa: E402
from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_surface_features as SF                         # noqa: E402


def _mk_solid(doc):
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:                                                 # noqa: BLE001
            continue
    return False


def _mk_surface(doc, plane="Front Plane"):
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name=plane)
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.02, -0.02, 0.0, 0.02, 0.02, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                return True
        except Exception:                                                 # noqa: BLE001
            continue
    return False


def _pick(doc, mode, mark):
    """★ mode: `all`（全选曲面面）/ `first`（只第一张）/ `plane`（一张基准面）。回选中数。"""
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel
    n = 0
    if mode == "plane":
        ext = _get(doc, "Extension")
        for plane in ("\u524d\u89c6\u57fa\u51c6\u9762", "Front Plane"):
            try:
                if _get(ext, "SelectByID2", plane, "PLANE", False, 0, 0.0, 0.0, 0.0,
                        False, mark, None, 0):
                    n += 1
                    break
            except Exception:                                             # noqa: BLE001
                continue
    else:
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            try:
                faces = list(_get(b, "GetFaces") or [])
            except Exception:                                             # noqa: BLE001
                continue
            for f in (faces[:1] if mode == "first" else faces):
                try:
                    if _sel(f, append=True, mark=mark):
                        n += 1
                except Exception:                                         # noqa: BLE001
                    continue
    return n


def _one(sw, tag, mode, mark):
    row = {"tag": tag, "mode": mode, "mark": mark, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["solid"] = _mk_solid(doc)
        row["surface"] = _mk_surface(doc)
        row["selected"] = _pick(doc, mode, mark)
        before = list(P.feature_names(doc) or [])
        from sw_connect import out_i4 as _oi4
        fm = C.get_com_member(doc, "FeatureManager")
        try:
            ret = C.get_com_member(fm, "InsertCutSurface", False, 0, False, True, [], _oi4())
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
        after = list(P.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"])
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
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
          "_": "InsertCutSurface \u7684**\u9009\u533a\u53d8\u4f53**\uff08\u2605 arity \u5df2\u5b9a\u4e3a 6\uff0c\u672c\u8f6e\u53ea\u52a8\u9009\u533a\uff09",
          "why": "\u4e8b\u5b9e 404\uff1a\u5b98\u65b9\u8bf4\u300cusing the **preselected** surface or plane\u300d"
                 "\uff0c\u800c\u672c\u5305\u88c5\u662f**\u5168\u9009**",
          "cases": []}
    for tag, mode, mark in (("\u5168\u9009\u66f2\u9762\u9762 mark=0", "all", 0),
                            ("\u53ea\u9009\u7b2c\u4e00\u5f20 mark=0", "first", 0),
                            ("\u53ea\u9009\u7b2c\u4e00\u5f20 **mark=1**", "first", 1),
                            ("\u5168\u9009\u66f2\u9762\u9762 **mark=1**", "all", 1),
                            ("\u53ea\u4e00\u5f20\u57fa\u51c6\u9762 mark=0", "plane", 0)):
        ev["cases"].append(_one(sw, tag, mode, mark))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "selection_variant_works" if ev["passed"] else "all_selection_variants_fail"
    p = R / "output" / "cut-surface-selection-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-32s ok=%-6s \u9009\u4e2d=%-4s \u56de=%-8s new=%s" % (
            c.get("tag"), c.get("ok"), c.get("selected"), c.get("returned"), c.get("new")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
