"""★ 真机：投影型分割线**照官方例子重做** —— 草图 mark=4 · 面 mark=1。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_split_line_projection_per_example.py
# 定位:   ★ 2026-10-03（轮 539）★ **第六种源的第二次使用**（★ 事实 415 立的）：
#     ★ **官方例子给的是**调用序**，而那是签名与 Remarks 都给不了的**。
#
#   ★★ **怎么找到的**：上一轮（事实 418）留的下一步是"读官方例子"⇒ 在本机 CHM 里搜到
#     **`Create_Projection_Split_Line_Example_{CSharp,VB,VBNET}.htm`** ✓
#
#   ★★★★★ **例子里的关键四行**（逐字）：
#     ```
#     ① SelectByID2("Boss-Extrude1", "BODYFEATURE", 0, 0, 0, False, 0, Nothing, 0)
#     ② SelectByID2("Sketch1",       "SKETCH",      x, y, 0, True,  **4**, Nothing, 0)
#     ③ SelectByID2("",              "FACE",        x, y, z, True,  **1**, Nothing, 0)
#     ④ Part.InsertSplitLineProject(True, True)
#     ```
#     ⇒ ★★★★ **故两个 mark 是：★ 草图 = 4 · ★ 面 = 1** ⚠
#     ★ 而本仓轮 537/538 **只选了一个基准面、且 mark = 0** ⇒ ★ **前置完全不对** ⚠
#
#   ★ 本探针照例子搭前置：
#     · 一个**实体**（`FeatureExtrusion` 拉一个矩形）
#     · 一个**草图**（★ 要在实体**之上**，★ 用作分割轮廓）
#     · **按 mark 选**：草图的段 → mark 4；实体的面 → mark 1
#   ★ 并试例子的 `(True, True)` 之外另两组布尔（★ 唯一没照抄的两个值）。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 406）：**树增量** **或** **返回对象带类型名**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402
import scripts.sw_weldment as W                                       # noqa: E402


def _build(doc):
    """★ 实体 + ★ 一个在它上面的**草图**（★ 用作分割轮廓）。"""
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    ok_solid = False
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            ok_solid = True
            break
        except Exception:                                                 # noqa: BLE001
            continue
    #: \u2605 \u7b2c\u4e8c\u4e2a\u8349\u56fe\uff08\u2605 \u5728\u524d\u89c6\u9762\u4e0a\
    #: uff0c\u2605 \u7528\u4f5c\u5206\u5272\u8f6e\u5ed3\uff09
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.01, -0.005, 0.0, 0.01, 0.015, 0.0)
    P.end_sketch(doc)
    return ok_solid


def _pick(doc):
    """★ 照例子选：**实体特征**（mark 0）→ **草图**（mark 4）→ **面**（mark 1）。"""
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel, _select_by_id as _sel_id
    ext = _get(doc, "Extension")
    picked = {}
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    names = list(FR.feature_names(doc) or [])
    sk = [n for n in names if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    #: \u2605 \u2460 \u5b9e\u4f53\u7279\u5f81\uff08\u2605 \u6309\u540d\u5b57\uff1a\u7279
    #: \u5f81\u53ef\u6309\u540d\u9009 \u2014\u2014 \u4e8b\u5b9e 32\uff09
    for nm in ("\u51f8\u53f0-\u62c9\u4f381", "Boss-Extrude1"):
        try:
            if _sel_id(ext, nm, "BODYFEATURE", append=False, mark=0):
                picked["feature"] = nm
                break
        except Exception:                                                 # noqa: BLE001
            continue
    #: \u2605 \u2461 \u8349\u56fe\u7684**\u6bb5**\uff08\u2605 mark = **4**\uff09
    if len(sk) >= 2:
        try:
            if _sel_id(ext, sk[-1], "SKETCH", append=bool(picked), mark=4):
                picked["sketch"] = sk[-1]
        except Exception:                                                 # noqa: BLE001
            pass
    #: \u2605 \u2462 \u5b9e\u4f53\u7684**\u9762**\uff08\u2605 mark = **1**\uff09
    try:
        for b in list(_get(doc, "GetBodies2", 0, True) or []):
            for f in list(_get(b, "GetFaces") or [])[:1]:
                if _sel(f, append=bool(picked), mark=1):
                    picked["face"] = True
                break
            break
    except Exception:                                                     # noqa: BLE001
        pass
    per = {}
    for m in (0, 1, 4):
        try:
            per[str(m)] = int(_get(_get(doc, "SelectionManager"), "GetSelectedObjectCount2", m))
        except Exception:                                                 # noqa: BLE001
            per[str(m)] = -1
    return picked, per


def _one(sw, tag, is_directional, flip_dir):
    row = {"tag": tag, "is_directional": is_directional, "flip_dir": flip_dir, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["built"] = _build(doc)
        picked, per = _pick(doc)
        row["picked"] = picked
        row["sel_by_mark"] = per
        before = list(FR.feature_names(doc) or [])
        try:
            C.get_com_member(doc, "InsertSplitLineProject", bool(is_directional), bool(flip_dir))
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        types = []
        try:
            for f in W.iter_features_recursive(doc):
                try:
                    types.append(str(C.get_com_member(f, "GetTypeName2") or ""))
                except Exception:                                         # noqa: BLE001
                    pass
        except Exception:                                                 # noqa: BLE001
            pass
        row["new_types"] = [t for t in types if "Split" in t]
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
          "_": "\u6295\u5f71\u578b\u5206\u5272\u7ebf\uff1a**\u7167\u5b98\u65b9\u4f8b\u5b50**\uff08\u8349\u56fe mark=4 \u00b7 \u9762 mark=1\uff09",
          "example": "Create_Projection_Split_Line_Example_VBNET.htm",
          "cases": []}
    for tag, d1, d2 in (("\u2605 (True, True)\uff08\u2605 \u4f8b\u5b50\u90a3\u7ec4\uff09", True, True),
                        ("(True, False)", True, False),
                        ("(False, True)", False, True)):
        ev["cases"].append(_one(sw, tag, d1, d2))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "projection_split_line_works" if ev["passed"] else "still_fails"
    p = R / "output" / "split-line-projection-per-example-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-32s ok=%-6s picked=%s" % (c.get("tag"), c.get("ok"),
                                             json.dumps(c.get("picked"), ensure_ascii=False)[:60]))
        print("        sel_by_mark=%s new=%s new_types=%s" % (
            c.get("sel_by_mark"), c.get("new"), c.get("new_types")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
