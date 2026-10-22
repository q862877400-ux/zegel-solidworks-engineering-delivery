"""★ 真机：投影型分割线的**最小前置矩阵** —— 每个前置都先验明"真的选上了"再调。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_split_line_minimal_matrix.py
# 定位:   ★ 承接 `prove_split_line_geometry_isolate.py`（★ 它**又被同一个坑咬了**）。
#
#   ★★★ **上一轮 E1/E3 为什么不算数**（★ 我自己读出来的）：
#     `sel_by_mark = {'0': 1, '1': **0**, '4': 1}` ⇒ ★ **面根本没选上**（mark 1 计数 = 0）。
#     ★ 真因：我按 **包围盒 z 面中心** 取点，★ 而那一格的 `ymax = 0.0` ⇒
#       ★ **点恰好落在面的边界上** ⇒ 选不中。★ 于是那两格测的是"没选面"，不是"几何不对"。
#     ⇒ ★★ **定则：前置必须先回读、再调用**（★ 事实 8：`SelectByID2` 的返回值不可信，
#        ★ 只有**计数**算数）。
#
#   ★★★ **六个格子**（★ 每一格都**先验明标记计数**，不满足就在读数里写明"前置不成立"）：
#     | 格 | 几何 | 面（**按点**，都取面内部） | 草图 | 该回答什么 |
#     |---|---|---|---|---|
#     | M1 | 正确（草图在实体之外） | **近面**中心 | mark 4 | 正例基准 |
#     | M2 | 正确 | **+X 侧脸**（与投影方向**垂直**） | mark 4 | 垂直面会不会挡 |
#     | M3 | 正确 | **不选面** | mark 4 | 「面必须选」这条 Remarks **是否必要** |
#     | M4 | 正确 | 近面中心 | **不选草图** | 「草图必须选」是否必要 |
# | M5 | **上一会话**（草图在实体内） | +Z 面**内部**点（★ 修掉边界坑） | mark 4 | ★ **
# 决定性**：几何是不是承重的 |
#     | M6 | **上一会话** | -Z 面内部点 · 调 `(True, False)` | mark 4 | 朝 -Z 能不能切 |
#
#   ★ 判据三条一起：树增量 · 面数 +1 · 有面出现 2 个环（`IFace2.GetLoopCount`）。
#   ★ 并回报**切开的那张面在哪**（`IFace2.GetBox`）—— ★ 好知道投影到底落在哪。
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

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts.sw_simulation import select_face_at  # noqa: E402
import prove_split_line_geometry_per_example as G  # noqa: E402
import prove_split_line_geometry_controls as K  # noqa: E402
import prove_split_line_geometry_isolate as I  # noqa: E402


def _split_face_boxes(doc):
    """★ 回报"有 2 个环"的那张面的包围盒 ⇒ ★ 知道**切开的是哪一张面**。"""
    out = []
    for b in list(G._get(doc, "GetBodies2", 0, True) or []):
        for f in list(G._get(b, "GetFaces") or []):
            try:
                if int(G._get(f, "GetLoopCount")) != 2:
                    continue
                box = G._get(f, "GetBox")
                out.append([round(float(box[i]), 5) for i in range(6)] if box else None)
            except Exception:  # noqa: BLE001
                continue
    return out


def _select_for(doc, want_sketch, face_point):
    """★ 选：草图（mark 4，可选）→ 面（mark 1，按点，可选）⇒ ★ **回读计数**。"""
    ext = G._get(doc, "Extension")
    picked = {}
    doc.ClearSelection2(True)
    if want_sketch:
        sk = G._sketch_names(doc)
        if sk:
            try:
                if P._select_by_id(ext, sk[-1], "SKETCH", append=False, mark=4):
                    picked["sketch"] = sk[-1]
            except Exception:  # noqa: BLE001
                pass
    if face_point is not None:
        try:
            if select_face_at(
                doc,
                face_point[0],
                face_point[1],
                face_point[2],
                mark=1,
                append=bool(picked),
            ):
                picked["face"] = [round(v, 5) for v in face_point]
        except Exception as exc:  # noqa: BLE001
            picked["face_err"] = str(exc)[:100]
    per = {}
    for m in (0, 1, 4):
        try:
            per[str(m)] = int(
                G._get(G._get(doc, "SelectionManager"), "GetSelectedObjectCount2", m)
            )
        except Exception:  # noqa: BLE001
            per[str(m)] = -1
    return picked, per


def _case(sw, tag, mode):
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        if mode.startswith("legacy"):
            box = I._legacy_geometry(doc)
            row["bbox_m"] = box
            row["geometry"] = "legacy(\u8349\u56fe\u5728\u5b9e\u4f53\u5185)"
            y_mid = (box[1] + box[4]) / 2.0
            if mode == "legacy_plus":
                face_point, d1, d2 = (0.0, y_mid, box[5]), True, True
            else:
                face_point, d1, d2 = (0.0, y_mid, box[2]), True, False
        else:
            ok, info = G._build(doc)
            row["built"] = ok
            row["geometry"] = "correct(\u8349\u56fe\u5728\u5b9e\u4f53\u4e4b\u5916)"
            if not ok:
                row["err"] = "build failed"
                return row
            xmin, ymin, zmin, xmax, ymax, zmax = info["bbox_m"]
            row["bbox_m"] = info["bbox_m"]
            x_mid, y_mid = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0
            z_mid = (zmin + zmax) / 2.0
            face_point, d1, d2 = (x_mid, y_mid, min(zmin, zmax)), True, True
            if mode == "correct_side":  #: ★ 与投影方向**垂直**的侧脸
                face_point = (xmax, y_mid, z_mid)
            elif mode == "correct_noface":
                face_point = None
        want_sketch = mode != "correct_nosketch"
        picked, per = _select_for(doc, want_sketch, face_point)
        row["picked"], row["sel_by_mark"] = picked, per
        #: ★★ **前置先验明**：该选的没选上 ⇒ 如实标注，不把它读成"能力不成"
        need_face = face_point is not None
        need_sketch = want_sketch
        ok_pre = (per["1"] == 1 if need_face else per["1"] == 0) and (
            per["4"] >= 1 if need_sketch else per["4"] == 0
        )
        row["preconditions_held"] = ok_pre
        res = K._call_and_read(doc, row, d1, d2)
        res["split_face_boxes"] = _split_face_boxes(doc)
        if not ok_pre:
            res["ok"] = False
            res["note"] = (
                "\u2605 \u524d\u7f6e\u672a\u6210\u7acb \u21d2 \u672c\u683c\u4e0d\u80fd\u5f53"
                "\u201c\u80fd\u529b\u4e0d\u6210\u201d\u7684\u8bc1\u636e"
            )
        return res
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        return row
    finally:
        if doc is not None:
            try:
                t = str(G._get(doc, "GetTitle") or "")
                if t:
                    G._get(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass


CASES = (
    (
        "\u2605 M1 \u6b63\u786e\u51e0\u4f55 + \u8fd1\u9762\uff08\u57fa\u51c6\uff09",
        "correct_near",
    ),
    ("\u2605 M2 \u6b63\u786e\u51e0\u4f55 + \u5782\u76f4\u4fa7\u8138", "correct_side"),
    ("\u2605 M3 \u6b63\u786e\u51e0\u4f55 + **\u4e0d\u9009\u9762**", "correct_noface"),
    (
        "\u2605 M4 \u6b63\u786e\u51e0\u4f55 + **\u4e0d\u9009\u8349\u56fe**",
        "correct_nosketch",
    ),
    (
        "\u2605 M5 \u4e0a\u4e00\u4f1a\u8bdd\u51e0\u4f55 + +Z \u9762\uff08\u5185\u90e8\u70b9\uff09",
        "legacy_plus",
    ),
    ("\u2605 M6 \u4e0a\u4e00\u4f1a\u8bdd\u51e0\u4f55 + -Z \u9762", "legacy_minus"),
)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u6295\u5f71\u578b\u5206\u5272\u7ebf\uff1a**\u6700\u5c0f\u524d\u7f6e\u77e9\u9635**"
        "\uff08\u6bcf\u4e2a\u524d\u7f6e\u5148\u56de\u8bfb\u3001\u518d\u8c03\u7528\uff09",
        "cases": [],
    }
    for tag, mode in CASES:
        ev["cases"].append(_case(sw, tag, mode))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "split-line-minimal-matrix-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a\u6210 %d / %d" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print(
            "  %-40s ok=%-6s pre=%-6s new=%-10s face_delta=%-3s loops=%s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("preconditions_held"),
                c.get("new"),
                c.get("face_delta"),
                c.get("loops_after"),
            )
        )
        print(
            "        sel=%s split_face_boxes=%s"
            % (c.get("sel_by_mark"), c.get("split_face_boxes"))
        )
        if c.get("note"):
            print("        note=%s" % c["note"])
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
