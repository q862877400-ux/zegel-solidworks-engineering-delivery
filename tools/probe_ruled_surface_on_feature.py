"""★ 真机：直纹曲面（T608）—— 官方原话里的「**on this feature**」该怎么落实。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_ruled_surface_on_feature.py
# 定位:   ★ 2026-10-03（轮 531）★ 第二把锁，仍用上一轮固化的那把钥匙（事实 410）：
#     ★ **官方原话里的每个名词都要落实**。
#
#   ★ 锁：`IFeatureManager.InsertRuledSurfaceFromEdge2`（直纹曲面 · B6/T608）。
#     它到轮 505 为止的账：**arity 已修对（11 参）**、选区 `{1:1, 4:1}`、
#     ★ **侧棱 4 条 + 水平边 4 条**都试过 ⇒ **回了对象而树不动**（事实 398 里那条）。
#
#   ★★ **而官方原话逐字是**：
#     > "Inserts a ruled surface from the selected edge **on this feature**."
#     ⇒ ★★ **"on this feature"** —— ★ 那两个词**本仓从未当回事** ⚠
#
#   ★ 两种读法（★ 本探针都试）：
#     ⓐ ★ **先选一个特征**（让"this feature"有指代）+ 再选边
#     ⓑ ★ **选"某个特定特征产生的边"**（★ 而前几轮选的是 `GetEdges()[0]` 那种**按索引**的边）
#
#   ★ 试的组：
#     ⓐ 只选边（★ 前几轮那组 —— 对照）
#     ⓑ ★ **先选实体特征（按名字）** + 再选边
#     ⓒ ★ **选"拉伸特征的顶面那条边"**（★ 按**边中点坐标**挑，★ 而不是按索引 0）
#     ⓓ ★ **先选曲面特征** + 再选边
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
from scripts import sw_surface_features as SF                         # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _mk_solid(doc):
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.02, -0.02, 0.0, 0.02, 0.02, 0.0)
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


def _edge_list(doc, body_type=0):
    """★ 回 [(index, edge, 中点 mm)] —— ★ 供**按坐标**挑边（★ 而不是按索引）。"""
    from sw_connect import get_com_member as _get
    out = []
    for b in list(_get(doc, "GetBodies2", body_type, True) or []):
        for i, e in enumerate(list(_get(b, "GetEdges") or [])):
            mid = None
            try:
                a = [float(x) for x in (_get(_get(e, "GetStartVertex"), "GetPoint") or [])]
                z = [float(x) for x in (_get(_get(e, "GetEndVertex"), "GetPoint") or [])]
                if a and z:
                    mid = [round((a[k] + z[k]) / 2.0 * 1000.0, 2) for k in range(3)]
            except Exception:                                             # noqa: BLE001
                pass
            out.append((i, e, mid))
        break
    return out


def _one(sw, tag, mode):
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_solid(doc)
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        ext = _get(doc, "Extension")
        picked = {}
        #: \u2605 \u2460 \u5148\u9009\u4e00\u4e2a**\u7279\u5f81**\uff08\u2605 \u8ba9 "this feature" \u6709\u6307\u4ee3\uff09
        if mode in ("feature_then_edge", "surface_feature_then_edge"):
            want = "\u51f8\u53f0-\u62c9\u4f381" if mode == "feature_then_edge" else "\u66f2\u9762-\u62c9\u4f381"
            #: ⚠ **修**：`_get_sketch_name_candidates` 回的是 **list** ⇒ ★ 不能直接 `+ (want,)`
            #:   （★ 第一版就死在这 —— `TypeError: can only concatenate list (not "tuple") to list`，
            #:    ★ 而那两组**正是最关键的两组**）
            cands = list(P._get_sketch_name_candidates(want)) + [want]
            for cand in cands:
                try:
                    if P._select_by_id(ext, cand, "BODYFEATURE", append=False, mark=0):
                        picked["feature"] = cand
                        break
                except Exception:                                         # noqa: BLE001
                    continue
        #: \u2605 \u2461 \u9009\u8fb9
        edges = _edge_list(doc)
        target = None
        if mode == "top_edge_by_coord":
            #: ★ 挑**端点 Z 最大（= 0）的水平边** —— ★ 按**坐标**，不按索引
            #:   ⚠ **修**：拉伸是从 Z=-20 到 Z=0（前视面拉 20mm）⇒ ★ 顶面在 **Z = 0**，
            #:     ★ 而第一版我筛 `|m[2] - 20| < 0.5` ⇒ **筛空了、退回边 0**
            horiz = [(i, e, m) for (i, e, m) in edges
                     if m is not None and abs(m[2] - 0.0) < 0.5]
            if horiz:
                target = horiz[0]
        if target is None and edges:
            target = edges[0]
        if target is not None:
            if _sel(target[1], append=bool(picked), mark=0):
                picked["edge"] = target[0]
                picked["edge_mid"] = target[2]
        row["picked"] = picked
        try:
            row["sel"] = int(_get(_get(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            row["sel"] = -1
        before = list(FR.feature_names(doc) or [])
        ret = None
        try:
            ret = SF.insert_ruled_surface_report(doc, surface_type=1, length_mm=10.0)
            row["ok"] = bool(ret.get("ok"))
            row["new"] = ret.get("new_features")
            row["returned_none"] = ret.get("returned_none")
            row["error"] = str(ret.get("error") or "")[:120]
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        if row.get("new") is None:
            row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["ok"] or row["new"])
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
          "_": "\u76f4\u7eb9\u66f2\u9762\uff1a\u5b98\u65b9\u539f\u8bdd\u91cc\u7684 **on this feature** \u600e\u4e48\u843d\u5b9e",
          "why": "\u4e8b\u5b9e 410 \u7684\u94a5\u5319\uff1a\u539f\u8bdd\u91cc\u7684\u6bcf\u4e2a\u540d\u8bcd\u90fd\u8981\u843d\u5b9e",
          "cases": []}
    for tag, mode in (("\u2460 \u53ea\u9009\u8fb9\uff08\u2605 \u5bf9\u7167\uff09", "edge_only"),
                      ("\u2461 **\u5148\u9009\u4f53\u7279\u5f81** + \u8fb9", "feature_then_edge"),
                      ("\u2462 **\u6309\u5750\u6807\u6311\u9876\u90e8\u6c34\u5e73\u8fb9**", "top_edge_by_coord"),
                      ("\u2463 \u5148\u9009\u66f2\u9762\u7279\u5f81 + \u8fb9", "surface_feature_then_edge")):
        ev["cases"].append(_one(sw, tag, mode))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "on_feature_matters" if ev["passed"] else "on_feature_does_not_matter"
    p = R / "output" / "ruled-surface-on-feature-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-42s ok=%-6s \u9009\u4e2d=%-3s picked=%s" % (
            c.get("tag"), c.get("ok"), c.get("sel"), json.dumps(c.get("picked"), ensure_ascii=False)[:64]))
        print("        new=%s \u56deNone=%s err=%s" % (c.get("new"), c.get("returned_none"), str(c.get("error") or "")[:70]))
        if c.get("err"):
            print("        ERR=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
