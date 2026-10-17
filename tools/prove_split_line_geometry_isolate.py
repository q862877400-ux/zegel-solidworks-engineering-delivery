"""★ 真机：投影型分割线的**因果隔离** —— 到底是"几何"还是"选面的方式"让它成立的？"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_split_line_geometry_isolate.py
# 定位:   ★ 承接 `prove_split_line_geometry_controls.py`（★ 它推翻了我自己的假设）。
#
#   ★★ **上一轮 A/B/C/D 的结果（逐字读数，★ 含"不利于我"的）**：
#     ```
#     A 正例（落点在环内 + 近面）      ⇒ 成 · 新特征「分割线1」· 面数 6→7 · 有面 1→2 环
#     B 只把落点移到环外（同一张面）   ⇒ **也成** ⚠ ⇒ ★ 我原以为"落点必须在环内"是**错的**
#     C 只把面换成远面                 ⇒ **也成** ⚠ ⇒ ★ 面选哪一张**几乎不影响**
#     D 复现上一会话的几何             ⇒ 不成（★ 而读数显示是**两个**变量同时变了：
#                                        几何 + 面改用了裸 `Select4` ⇒ **mark 1 计数 = 0**）
#     ```
#     ⇒ ★★ **故 D 不是干净的对照**（它同时动了"几何"与"选面的方式"）——
#       ★ 这正是本探针要修掉的东西：**一次只动一个变量**。
#
#   ★★★ **三个格子（★ 每个只留一处差异）**：
#     | 格 | 几何 | 选面方式 | 该看什么 |
#     |---|---|---|---|
#     | E1 | **上一会话的几何**（实体 z∈[-30,30] · 草图在 z=0 **实体内**） | ★ **按点**（mark 1） | 几何是不是承重的那一个 |
#     | E2 | **正确几何**（草图在实体之外） | ★ 按**第一张面**（mark 1） | 选面方式是不是承重的 |
#     | E3 | 上一会话的几何 | 按点，★ 但**朝 -Z** 投 | 实体内部能不能朝任一方向切 |
#
#   ★ 判据同前（三条一起）：★ 树增量 · ★ 面数 +1 · ★ 有面出现 **2 个环**（`IFace2.GetLoopCount`）。
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
sys.path.insert(0, str(R / "tools"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402
from scripts.sw_simulation import select_face_at                      # noqa: E402
import prove_split_line_geometry_per_example as G                     # noqa: E402
import prove_split_line_geometry_controls as K                        # noqa: E402


def _legacy_geometry(doc):
    """★ **上一会话的几何**：Top Plane 上 -30..30 的矩形拉 20 mm ⇒ 实体 z∈[-30,30]。

    ★ 投影草图留在 **Front Plane（z = 0）** ⇒ ★ **草图被实体夹在中间**（★ 这正是它与例子的差别）。
    """
    P.start_sketch(doc, plane_name="Top Plane")
    G._get(G._get(doc, "SketchManager"), "CreateCornerRectangle",
           -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    box = None
    for d in (True, False):
        made = None
        for cand in (G._sketch_names(doc) or ["\u8349\u56fe1"])[::-1]:
            try:
                P.extrude_boss(doc, cand, 0.02, direction=d)
                made = cand
                break
            except Exception:                                             # noqa: BLE001
                continue
        if made is None:
            continue
        box = G._bbox(doc)
        if box is not None:
            break
    P.start_sketch(doc, plane_name="Front Plane")
    G._get(G._get(doc, "SketchManager"), "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.008)
    P.end_sketch(doc)
    return box


def _select_common(doc, picked):
    """★ 实体特征（mark 0）+ 投影草图（mark 4）—— ★ 与例子一致的选择序。"""
    ext = G._get(doc, "Extension")
    for nm in ("\u51f8\u53f0-\u62c9\u4f381", "Boss-Extrude1"):
        try:
            if P._select_by_id(ext, nm, "BODYFEATURE", append=False, mark=0):
                picked["feature"] = nm
                break
        except Exception:                                                 # noqa: BLE001
            continue
    sk = G._sketch_names(doc)
    if sk:
        try:
            if P._select_by_id(ext, sk[-1], "SKETCH", append=bool(picked), mark=4):
                picked["sketch"] = sk[-1]
        except Exception:                                                 # noqa: BLE001
            pass
    return picked


def _mark_counts(doc):
    per = {}
    for m in (0, 1, 4):
        try:
            per[str(m)] = int(G._get(G._get(doc, "SelectionManager"),
                                     "GetSelectedObjectCount2", m))
        except Exception:                                                 # noqa: BLE001
            per[str(m)] = -1
    return per


def _case(sw, tag, mode):
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        picked = {}
        if mode in ("legacy_point_plus", "legacy_point_minus"):
            box = _legacy_geometry(doc)
            row["bbox_m"] = box
            row["geometry"] = "legacy:\u5b9e\u4f53 z\u2208[-30,30] \u00b7 \u8349\u56fe z=0\uff08\u5b9e\u4f53\u5185\uff09"
            picked = _select_common(doc, picked)
            #: ★ **只按点选面**（mark 1）—— 与上一会话的差别就在这里
            z = box[5] if mode.endswith("plus") else box[2]
            directed = mode.endswith("plus")
            row["direction"] = "+Z" if directed else "-Z"
            try:
                if select_face_at(doc, 0.0, 0.0, z, mark=1, append=bool(picked)):
                    picked["face"] = [0.0, 0.0, z]
            except Exception as exc:                                      # noqa: BLE001
                row["err_face"] = str(exc)[:120]
            row["picked"], row["sel_by_mark"] = picked, _mark_counts(doc)
            return K._call_and_read(doc, row, True, directed)
        #: ★ E2：**正确几何**，而选面改用"**第一张面**"（★ 只这一处不同）
        ok, info = G._build(doc)
        row["geometry"] = "correct:\u8349\u56fe\u5728\u5b9e\u4f53\u4e4b\u5916"
        row["built"] = ok
        if not ok:
            row["err"] = "build failed"
            return row
        doc.ClearSelection2(True)
        picked = _select_common(doc, picked)
        try:
            body = list(G._get(doc, "GetBodies2", 0, True))[0]
            faces = list(G._get(body, "GetFaces") or [])
            if faces and P._select_com_object(faces[0], append=bool(picked), mark=1):
                picked["face"] = "GetFaces()[0]\uff08\u2605 \u800c mark \u6b63\u5f53\u8bbe\u4e3a 1\uff09"
        except Exception as exc:                                          # noqa: BLE001
            row["err_face"] = str(exc)[:120]
        row["picked"], row["sel_by_mark"] = picked, _mark_counts(doc)
        return K._call_and_read(doc, row, True, True)
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        return row
    finally:
        if doc is not None:
            try:
                t = str(G._get(doc, "GetTitle") or "")
                if t:
                    G._get(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u6295\u5f71\u578b\u5206\u5272\u7ebf\uff1a**\u56e0\u679c\u9694\u79bb**"
               "\uff08\u4e00\u6b21\u53ea\u52a8\u4e00\u5904\u53d8\u91cf\uff09",
          "cases": []}
    for tag, mode in (
        ("\u2605 E1 \u4e0a\u4e00\u4f1a\u8bdd\u51e0\u4f55 + **\u6309\u70b9\u9009\u9762**\uff08+Z\uff09", "legacy_point_plus"),
        ("\u2605 E2 \u6b63\u786e\u51e0\u4f55 + **\u6309\u7b2c\u4e00\u5f20\u9762\u9009**", "correct_firstface"),
        ("\u2605 E3 \u4e0a\u4e00\u4f1a\u8bdd\u51e0\u4f55 + \u6309\u70b9\u9009\u9762\uff08-Z\uff09", "legacy_point_minus"),
    ):
        ev["cases"].append(_case(sw, tag, mode))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "split-line-geometry-isolate-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    print("  \u5224\u522b\uff1a\u6210 %d / %d" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-40s ok=%-6s new=%-12s face_delta=%-3s loops=%s"
              % (c.get("tag"), c.get("ok"), c.get("new"), c.get("face_delta"),
                 c.get("loops_after")))
        print("        geometry=%s picked_face=%s sel_by_mark=%s"
              % (c.get("geometry"), c.get("picked", {}).get("face") if c.get("picked") else None,
                 c.get("sel_by_mark")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
