"""★ 真机：**分割线**（三条入口：轮廓 / 投影 / 交叉）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_split_line.py
# 定位:   ★ 2026-10-03（轮 537）★ 攻 **B7/T705（分割线）** —— ★ 目标范围里**还没碰**的
#           一条。
#
#   ★★ **三条入口**（★ 对应 SolidWorks 分割线对话框里的三个类型）：
#     | 类型 | 入口 | 官方签名 |
#     |---|---|---|
# | **轮廓** | `IModelDoc2.InsertSplitLineSil()` | `void InsertSplitLineSil()` ⇒ **0 参*
# * |
# | **投影** | `IModelDoc2.InsertSplitLineProject(IsDirectional, FlipDir)` | ⇒ **2 参** 
# |
#     | **交叉** | `IFeatureManager.InsertSplitLineIntersect(CompleteOption)` | ⇒ **1 in** |
#     ★ 三者都取自**类型库**（第 3 源 · 冲突裁决者）✓
#
#   ★ 而 B7/T705 此前的账是：★ **"分割线两条真机树无增量（前置还不够）"**（★ 计划里那句）
#     ⇒ ★★ **而那时我试的是哪个入口、什么前置，计划里没写清** ⚠
#     ⇒ ★ 故本轮**三条都试、且前置写清**。
#
# ★ 前置（★ 本轮统一）：★ 一个**实体盒** + ★ 一张**穿过它的曲面**（★ 分割线要"分割"某物
# ）。
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
from scripts import sw_surface_features as SF                         # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402
import scripts.sw_weldment as W                                       # noqa: E402


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


def _pick_all_faces(doc):
    """★ 选**所有体的面**（★ 事实 416：面能按对象选、体不能）。"""
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    n = 0
    for bt in (0, 1):
        for b in list(_get(doc, "GetBodies2", bt, True) or []):
            for f in list(_get(b, "GetFaces") or []):
                try:
                    if _sel(f, append=True, mark=0):
                        n += 1
                except Exception:                                         # noqa: BLE001
                    continue
    return n


def _pick_plane(doc, names=("\u524d\u89c6\u57fa\u51c6\u9762", "Front Plane")):
    from sw_connect import get_com_member as _get
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    ext = _get(doc, "Extension")
    #: ★★★★ 2026-10-03（轮 538）**修**：`Callout` **不能传 `None`** —— ★ 本仓要 `_empty_
    #: callout()`
    #: （★ **事实 33**：传 `None` 报 `类型不匹配`、★ 而那个错**看不出是 Callout 的问题**
    #: ）。
    #:   ⚠ **轮 537 第一版就是踩在这**：★ 报错被 `except: continue` 吞掉 ⇒
    #:     `picked={"plane": null}` ⇒ ★ 两条**根本没真试到**，★ 而读起来像"前置不够"。
    from sw_part import _empty_callout as _ec
    from sw_part import _select_by_id as _sel_id
    errs = []
    for nm in names:
        try:
            #: ★★★★ 2026-10-03（轮 538）**第二次修** —— ★ 手搓的 `get_com_member(ext, "S
            #: electByID2", …)`
            #:   即使传了 `_empty_callout()` **仍报 `类型不匹配`（位置 8）** ⚠
            #: ⇒ ★★ **改用本仓现成的 `sw_part._select_by_id`**（★ 它内部处理的形态才是对
            #: 的）✓
            if _sel_id(ext, nm, "PLANE", append=False, mark=0):
                return nm
        except Exception as exc:                                          # noqa: BLE001
            errs.append("%s: %s" % (nm, str(exc)[:50]))
            continue
    #: ★ 不再静默：把错带回去（事实 417 的教训）
    return {"ERR": errs} if errs else None


def _one(sw, tag, kind):
    row = {"tag": tag, "kind": kind, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["solid"] = _mk_solid(doc)
        row["surface"] = _mk_surface(doc)
        before = list(FR.feature_names(doc) or [])
        fm = C.get_com_member(doc, "FeatureManager")
        picked = {}
        ret = None
        if kind == "sil":
            #: ★ \u8f6e\u5ed3\u578b\uff1a\u9009\u4e00\u4e2a**\u57fa\u51c6\u9762**\uff08\
            #: u2605 0 \u53c2\uff09
            picked["plane"] = _pick_plane(doc)
            ret = C.get_com_member(doc, "InsertSplitLineSil")
        elif kind == "project":
            #: ★ \u6295\u5f71\u578b\uff1a\u9009\u9762/\u57fa\u51c6\u9762\uff08\u2605 2 \
            #: u53c2\uff09
            picked["plane"] = _pick_plane(doc)
            ret = C.get_com_member(doc, "InsertSplitLineProject", False, False)
        else:
            #: ★ \u4ea4\u53c9\u578b\uff1a\u5168\u9009\u9762\uff08\u2605 1 in\uff09
            picked["faces"] = _pick_all_faces(doc)
            ret = C.get_com_member(fm, "InsertSplitLineIntersect", 0)
        row["picked"] = picked
        row["returned"] = type(ret).__name__ if ret is not None else "None"
        if ret is not None:
            for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                try:
                    row[k] = str(C.get_com_member(ret, m))
                except Exception:                                         # noqa: BLE001
                    pass
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
        row["ok"] = bool(row["new"] or row.get("ret_type"))
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
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
          "_": "\u5206\u5272\u7ebf\uff08B7/T705\uff09\u4e09\u6761\u5165\u53e3\uff1a\u8f6e\u5ed3 / \u6295\u5f71 / \u4ea4\u53c9",
          "why": "\u8ba1\u5212\u91cc\u90a3\u53e5\u201c\u5206\u5272\u7ebf\u4e24\u6761\u771f\u673a\u6811\u65e0\u589e\u91cf\u201d**\u6ca1\u5199\u6e05\u662f\u54ea\u4e2a\u5165\u53e3\u4e0e\u4ec0\u4e48\u524d\u7f6e**",
          "cases": []}
    for tag, kind in (("\u2605 \u8f6e\u5ed3\u578b InsertSplitLineSil", "sil"),
                      ("\u2605 \u6295\u5f71\u578b InsertSplitLineProject", "project"),
                      ("\u2605 \u4ea4\u53c9\u578b InsertSplitLineIntersect", "intersect")):
        ev["cases"].append(_one(sw, tag, kind))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "split_line_works" if ev["passed"] else "split_line_fails"
    p = R / "output" / "split-line-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-38s ok=%-6s picked=%s \u56de=%s" % (
            c.get("tag"), c.get("ok"), json.dumps(c.get("picked"), ensure_ascii=False)[:44], c.get("returned")))
        print("        \u540d=%s \u578b=%s new=%s new_types=%s" % (
            c.get("ret_name"), c.get("ret_type"), c.get("new"), c.get("new_types")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
