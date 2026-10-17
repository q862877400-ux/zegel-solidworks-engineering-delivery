"""★ 真机：**轮廓型分割线**（`InsertSplitLineSil`）—— ★ 照官方 mark 表（方向项 **2** · 面 **1**）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_split_line_silhouette_marks.py
# 定位:   ★ 2026-10-03（接手轮）★ **由新门禁逼出来的一条**（★ 不是我自己想到的）。
#
#   ★★★ **门禁怎么逼出来的**：★ 我新写的 `scripts/check_official_md_claims.py`
#     扫"官方没给 mark"这类断言、★ 拿官方页核对 ⇒ ★ 它报了 `mcp-server/tool_specs_batch71.py:26`：
#     ```
#     我方断言：（★ 官方 Remarks 没给 mark 表）
#     官方页（InsertSplitLineSil.md）逐字：
#       The item selected for direction must be selected using SelectByID2
#       with a mark value of **2**. The faces to split must be selected using
#       SelectByID2 with mark values of **1**.
#     ```
#     ⇒ ★★ **同一个错的形态**（把"官方有 mark"当"没有"）★ 而它**又一次把失败归因错了**。
#
#   ★★ **上一会话在这条上做的**（★ 事实 417/418/420）：★ 轮廓型**只选了一个基准面、mark = 0**
#     ⇒ ★ 而官方要的是 **mark = 2** ⇒ ★ **前置从第一步就错了**。
#
#   ★ 官方 `## Remarks` 逐字（`C:\swapi\types\IModelDoc2\InsertSplitLineSil.md`）：
#     ```
#     The silhouette curves differ based on your orientation. Therefore, this
#     method requires a selection to specify the desired direction.
#     Valid items to select to specify the direction are:
#       reference plane · planar face · edge · axis · two points
#     ```
#     ⇒ ★ 方向项（mark 2）· ★ 要切的面（mark 1）。
#
#   ★★ **几何**：轮廓 = 曲面与视线**相切**的那条线 ⇒ ★ 必须有一个**曲面**（圆柱面）
#     ⇒ 圆柱（圆的凸台拉伸）· ★ 视线方向用**前视基准面**（法向 = +Z）。
#
#   ★★ **四个格子**（★ 只动 mark / 有无面）：
#     | 格 | 方向项 | 要切的面 | 该回答什么 |
#     |---|---|---|---|
#     | S1 | 前视基准面 **mark 2** | 圆柱面 **mark 1** | 照官方 ⇒ 该成 |
#     | S2 | 前视基准面 **mark 0** | 圆柱面 mark 1 | ★ 上一会话的选法 ⇒ 该不成 |
#     | S3 | 前视基准面 mark 2 | **不选面** | 面这条 Remarks 是否必要 |
#     | S4 | **不选方向项** | 圆柱面 mark 1 | 方向项是否必要 |
#
#   ★ 判据（★ 同投影型，★ 三条一起）：树增量 · **面数增量** · 环数变化。
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
import prove_split_line_minimal_matrix as M                           # noqa: E402


def _build_cylinder(doc):
    """★ 圆柱：前视面画圆 ⇒ 沿法向拉 30 mm（★ 有一个**曲面**才有轮廓线可切）。"""
    P.start_sketch(doc, plane_name="Front Plane")
    G._get(G._get(doc, "SketchManager"), "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.015)
    P.end_sketch(doc)
    for cand in (G._sketch_names(doc) or ["\u8349\u56fe1"])[::-1]:
        try:
            P.extrude_boss(doc, cand, 0.03)
            break
        except Exception:                                                 # noqa: BLE001
            continue
    box = G._bbox(doc)
    #: ★ 侧面上的一点：★ 半径 15 mm 处的 (x, 0)，z 取高度中点
    z_mid = (box[2] + box[5]) / 2.0
    return box, (0.015, 0.0, z_mid)


def _case(sw, tag, dir_name, dir_mark, pick_face):
    row = {"tag": tag, "dir_name": dir_name, "dir_mark": dir_mark,
           "pick_face": pick_face, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        box, face_pt = _build_cylinder(doc)
        row["bbox_m"] = box
        ext = G._get(doc, "Extension")
        doc.ClearSelection2(True)
        picked = {}
        if dir_mark is not None:
            #: ★ 官方：方向项用 `SelectByID2` + **mark 2**（★ 上一会话用的是 mark 0）
            try:
                if P._select_by_id(ext, dir_name, "PLANE",
                                   append=False, mark=dir_mark):
                    picked["direction"] = "%s(mark %d)" % (dir_name, dir_mark)
            except Exception as exc:                                      # noqa: BLE001
                row["err_dir"] = str(exc)[:100]
        if pick_face:
            try:
                if select_face_at(doc, face_pt[0], face_pt[1], face_pt[2],
                                  mark=1, append=bool(picked)):
                    picked["face"] = [round(v, 5) for v in face_pt]
            except Exception as exc:                                      # noqa: BLE001
                row["err_face"] = str(exc)[:100]
        per = {}
        for m in (0, 1, 2, 4):
            try:
                per[str(m)] = int(G._get(G._get(doc, "SelectionManager"),
                                         "GetSelectedObjectCount2", m))
            except Exception:                                             # noqa: BLE001
                per[str(m)] = -1
        row["picked"], row["sel_by_mark"] = picked, per
        res = K._call_and_read_sil(doc, row)
        res["split_face_boxes"] = M._split_face_boxes(doc)
        return res
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


CASES = (
    ("\u2605 S1 \u524d\u89c6\u9762 mark 2 + \u9762 mark 1\uff08\u7167\u5b98\u65b9\uff09", "\u524d\u89c6\u57fa\u51c6\u9762", 2, True),
    ("\u2605 S2 \u524d\u89c6\u9762 mark 0 + \u9762 mark 1\uff08\u4e0a\u4e00\u4f1a\u8bdd\u7684\u9009\u6cd5\uff09", "\u524d\u89c6\u57fa\u51c6\u9762", 0, True),
    ("\u2605 S3 \u524d\u89c6\u9762 mark 2 + **\u4e0d\u9009\u9762**", "\u524d\u89c6\u57fa\u51c6\u9762", 2, False),
    ("\u2605 S4 **\u4e0d\u9009\u65b9\u5411\u9879** + \u9762 mark 1", "\u524d\u89c6\u57fa\u51c6\u9762", None, True),
    #: ★★ S5/S6：★ 圆柱的轴是 +Z，而**前视面的法向也是 +Z** ⇒ 视线**顺着轴**
    #:   ⇒ 轮廓退化成圆环本身（与已有边重合）⇒ ★ 换**上视面**（法向 +Y）**横着看**。
    ("\u2605 S5 **\u4e0a\u89c6\u9762** mark 2 + \u9762 mark 1\uff08\u6a2a\u7740\u770b\uff09", "\u4e0a\u89c6\u57fa\u51c6\u9762", 2, True),
    ("\u2605 S6 \u4e0a\u89c6\u9762 mark 2 + **\u4e0d\u9009\u9762**", "\u4e0a\u89c6\u57fa\u51c6\u9762", 2, False),
    #: ★★ S7：★ **只把 mark 2 换成 mark 0**（几何正确）—— ★ 隔离"官方那个 2 到底承不承重"
    ("\u2605 S7 \u4e0a\u89c6\u9762 **mark 0** + \u9762 mark 1\uff08\u53ea\u6539 mark\uff09", "\u4e0a\u89c6\u57fa\u51c6\u9762", 0, True),
)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u8f6e\u5ed3\u578b\u5206\u5272\u7ebf\uff08InsertSplitLineSil\uff09\uff1a"
               "\u7167\u5b98\u65b9 mark \u8868\uff08\u65b9\u5411\u9879 2 \u00b7 \u9762 1\uff09",
          "official": "mark 2 = direction item \u00b7 mark 1 = faces to split",
          "cases": []}
    for tag, dn, dm, pf in CASES:
        ev["cases"].append(_case(sw, tag, dn, dm, pf))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "silhouette_split_line_works" if ev["passed"] else "still_fails"
    p = R / "output" / "split-line-silhouette-marks-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-42s ok=%-6s new=%-12s dFaces=%-3s loops=%s"
              % (c.get("tag"), c.get("ok"), c.get("new"), c.get("face_delta"),
                 c.get("loops_after")))
        print("        sel=%s split_face_boxes=%s" % (c.get("sel_by_mark"),
                                                      c.get("split_face_boxes")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
