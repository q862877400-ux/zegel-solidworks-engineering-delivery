"""★ 真机：投影型分割线 —— 照官方例子重建**几何**（★ 不只是 marks）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_split_line_geometry_per_example.py
# 定位:   ★ 2026-10-03（接手轮）★ 攻台账 `特征下拉 · 曲线-分割线`（tier=可攻关）。
#
#   ★★ **为什么还要再试一次**（★ 上一会话轮 537/538/539 已试 3 轮、按事实 53 停手）：
#     · 事实 419 的结论是「★ **前置已照官方例子完全对上、而特征仍不建**」。
#     · 而**逐字读那份官方例子**后，我认为**那句话对了一半**：
#       ★ 对的是 **marks**（草图 = 4 · 面 = 1）—— 上一轮确实照做了；
#       ★ **错的是「前置」**：例子给的不只是 mark，★ **它还给了一个几何关系**，
#         而上一轮的探针**没有复现那个几何关系**。
#
#   ★★★★★ **官方例子的几何**（`Create_Projection_Split_Line_Example_VB.htm`，逐字）：
#     ```
#     ① CreateEllipse(center=(-21.25, 12.25, 0) mm, …)          ' ★ 在**前视面**（z = 0）
# InsertSketch True                                        ' ★ 收尾 ⇒ 草图1（★ **不被任
# 何特征消耗**）
#     ② SelectByID2("Front Plane","PLANE",…,0) + InsertRefPlane(8, 0.01778, …)
#        ⇒ 基准面1（★ 距前视面 **17.78 mm**）
#     ③ 在基准面1 上 CreateCornerRectangle(…)  ⇒ 草图2 ⇒ FeatureExtrusion2(… 0.00254 …)
#        ⇒ 凸台-拉伸1（★ 实体在**基准面1 那一侧**）
#     ④ SelectByID2("Boss-Extrude1","BODYFEATURE",…,False, 0, …)
#        SelectByID2("Sketch1",      "SKETCH",     … ,True,  **4**, …)
#        SelectByID2("",             "FACE",  -0.0182, 0.0132, **0.01778**, True, **1**, …)
#        ⇒ Part.InsertSplitLineProject True, True
#     ```
#     ⇒ ★★★ **两个几何条件**（★ 而它们才是这条命令的**真前置**）：
#       (a) ★ **投影草图的基准面在实体的外面**、且与**目标面平行**、沿投影方向隔开
#           （★ 例子：草图 z=0 · 实体 z∈[17.78, 20.32] ⇒ 草图**在实体之外**）；
#       (b) ★ **面的定位点是"投影落点"** —— z **恰好 = 0.01778**（＝目标面所在平面），
#           ★ 而 (x, y) = (-18.18, 13.24) **落在椭圆内部**（椭圆中心 (-21.25, 12.25)）。
#
# ★★ **上一轮探针（`probe_split_line_projection_per_example.py`）与例子的差异**（逐条比
# 过）：
#     · 实体：Top Plane 上画 -30..30 的矩形、拉 20 mm ⇒ 实体 **z∈[-30, 30]**，
#       ★ 而投影草图在 **Front Plane（z=0）** ⇒ ★★ **草图被实体夹在中间**（(a) 不成立）；
#     · 面：`list(body.GetFaces())[0]` —— ★ **第一张面，与投影落点无关**（(b) 不成立）。
#     ⇒ ★ 即：**mark 对了、几何没对**。本探针只改这两处、mark 与调用序逐字照抄。
#
#   ★ 另加一条**独立判据**（★ 补上一轮只记 `new=[]` 的缺口）：
#     ★ **分割线会切开面** ⇒ ★ **实体面数**应 +1（闭合环切出内环）。
#     ★ 这条判据**不依赖特征树**，与事实 420 的分类判据互补。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每格**新开一个文档**；★ 收尾关掉自己开的文档。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 420）：**树增量** **或** **面数增量** **或** **返回对象非 None
# **。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_feature_readback as FR  # noqa: E402
import scripts.sw_weldment as W  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts.sw_simulation import select_face_at  # noqa: E402

#: ★ 例子逐字：基准面偏移 0.01778 m
PLANE_OFFSET_M = 0.01778
#: ★ 例子逐字的两个布尔
EXAMPLE_COMBO = (True, True)


def _get(o, name, *args):
    return C.get_com_member(o, name, *args)


def _faces(doc):
    out = []
    for b in list(_get(doc, "GetBodies2", 0, True) or []):
        out.extend(list(_get(b, "GetFaces") or []))
    return out


def _face_count(doc):
    return len(_faces(doc))


def _bbox(doc):
    """★ `IBody2.GetBodyBox()` ⇒ 6 个 Double（★ 单位**米** —— 与 `select_face_at` 口径一致）。"""
    bodies = list(_get(doc, "GetBodies2", 0, True) or [])
    if not bodies:
        return None
    box = _get(bodies[0], "GetBodyBox")
    if not box or len(box) < 6:
        return None
    return [float(box[i]) for i in range(6)]


def _sketch_names(doc):
    return [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]


def _build(doc):
    """★ **照例子的几何**：投影草图留在前视面 · 实体建在偏移基准面上。

    :returns: ``(ok, info)``；``info`` 里有 bbox / 目标面 z / 落点 / 投影草图名 —— 全为**可核对的读数**。
    """
    info = {}
    ext = _get(doc, "Extension")
    fm = _get(doc, "FeatureManager")
    #: ★ ② 偏移基准面（★ 例子：InsertRefPlane(8, 0.01778, 0,0,0,0)）
    doc.ClearSelection2(True)
    P._select_by_id(
        ext, "\u524d\u89c6\u57fa\u51c6\u9762", "PLANE", append=False, mark=0
    )
    try:
        _get(fm, "InsertRefPlane", 8, PLANE_OFFSET_M, 0, 0, 0, 0)
    except Exception as exc:  # noqa: BLE001
        info["err_refplane"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        return False, info
    doc.ClearSelection2(True)
    plane = None
    for cand in ("\u57fa\u51c6\u97621", "Plane1"):
        if cand in (P.feature_names(doc) or []):
            plane = cand
            break
    if plane is None:
        for n in P.feature_names(doc) or []:
            if "\u57fa\u51c6\u9762" in n or n.lower().startswith("plane"):
                plane = n
                break
    info["ref_plane"] = plane
    if plane is None:
        return False, info
    #: ★ ③ 实体：偏移基准面上的矩形 ⇒ 拉 20 mm（★ 比例子厚，只为让落点在面内更宽裕）
    try:
        P.start_sketch(doc, plane_name=plane)
    except Exception as exc:  # noqa: BLE001
        info["err_sketch_on_plane"] = str(exc)[:120]
        return False, info
    _get(
        _get(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.04,
        -0.03,
        0.0,
        0.04,
        0.03,
        0.0,
    )
    P.end_sketch(doc)
    #: ★★ 几何条件 (a)：实体必须**整个**在投影草图的 +z 一侧（★ 草图 z=0 在实体之外）。
    #: ★ 而 `extrude_boss(direction=)` 落到 `FeatureExtrusion3` 的 `Dir` 上，
    #:   它的**实际朝向跟草图的局部坐标系走** ⇒ 本机实测 `direction=True` 得到 **-Z**。
    #: ★ 故这里**不硬编符号**：拉一次 → 读包围盒 → 不对就 `EditUndo2(1)` 撤掉换向重拉。
    box = None
    used_dir = None
    for d in (True, False):
        made = None
        for cand in (_sketch_names(doc) or ["\u8349\u56fe1"])[::-1]:
            try:
                P.extrude_boss(doc, cand, 0.02, direction=d)
                made = cand
                break
            except Exception:  # noqa: BLE001
                continue
        if made is None:
            continue
        box = _bbox(doc)
        if box is None:
            continue
        if min(box[2], box[5]) > 1e-4:
            used_dir = d
            info["boss_sketch"] = made
            break
        try:
            _get(doc, "EditUndo2", 1)  # ★ 方向反了 ⇒ 撤掉这一次拉伸、换向重来
        except Exception:  # noqa: BLE001
            pass
        box = None
    info["extrude_direction"] = used_dir
    info["bbox_m"] = box
    if box is None:
        info["err_geometry"] = (
            "两种拉伸方向都试过，实体始终未整体位于草图 +z 一侧"
            "\u21d2 几何条件 (a) 不成立"
        )
        return False, info
    xmin, ymin, zmin, xmax, ymax, zmax = box
    z_near = min(zmin, zmax)
    info["z_near_m"] = z_near
    if z_near <= 1e-4:
        info["err_geometry"] = (
            "实体未整体位于草图 +z 一侧（zmin=%.5f zmax=%.5f）"
            "\u21d2 草图被实体夹住，条件 (a) 不成立" % (zmin, zmax)
        )
        return False, info
    #: ★ 投影草图（★ 前视面 z=0）：圆心 = 目标面中心的 (x, y) ⇒ 落点必然在面内**且**在环
    #: 内
    cx, cy = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0
    rad = min(0.008, 0.4 * min((xmax - xmin) / 2.0, (ymax - ymin) / 2.0))
    info["circle"] = {"center_m": [cx, cy, 0.0], "radius_m": rad}
    doc.ClearSelection2(True)
    P.start_sketch(doc, plane_name="\u524d\u89c6\u57fa\u51c6\u9762")
    _get(_get(doc, "SketchManager"), "CreateCircleByRadius", cx, cy, 0.0, rad)
    P.end_sketch(doc)
    #: ★ 落点 = 目标面上的一点（★ 例子给的就是一个坐标，z 恰在目标面平面上）
    info["pick_m"] = [cx, cy, z_near]
    return True, info


def _select(doc, info):
    """★ 照例子选：实体特征（mark 0）→ 投影草图（mark 4）→ 面（mark 1，**按点**）。"""
    ext = _get(doc, "Extension")
    picked = {}
    doc.ClearSelection2(True)
    for nm in ("\u51f8\u53f0-\u62c9\u4f381", "Boss-Extrude1"):
        try:
            if P._select_by_id(ext, nm, "BODYFEATURE", append=False, mark=0):
                picked["feature"] = nm
                break
        except Exception:  # noqa: BLE001
            continue
    sk = _sketch_names(doc)
    #: ★ 投影草图 = **最后一张**草图（★ 前一张是实体的轮廓草图）
    proj = sk[-1] if sk else None
    info["project_sketch"] = proj
    if proj:
        try:
            if P._select_by_id(ext, proj, "SKETCH", append=bool(picked), mark=4):
                picked["sketch"] = proj
        except Exception:  # noqa: BLE001
            pass
    #: ★★★ 与上一轮的关键差别：面**按落点选**，不是 `GetFaces()[0]`
    px, py, pz = info["pick_m"]
    try:
        if select_face_at(doc, px, py, pz, mark=1, append=bool(picked)):
            picked["face"] = [round(px, 5), round(py, 5), round(pz, 5)]
    except Exception as exc:  # noqa: BLE001
        info["err_face"] = str(exc)[:120]
    per = {}
    for m in (0, 1, 4):
        try:
            per[str(m)] = int(
                _get(_get(doc, "SelectionManager"), "GetSelectedObjectCount2", m)
            )
        except Exception:  # noqa: BLE001
            per[str(m)] = -1
    return picked, per


def _one(sw, tag, is_directional, flip_dir):
    row = {
        "tag": tag,
        "is_directional": bool(is_directional),
        "flip_dir": bool(flip_dir),
        "ok": False,
    }
    doc = None
    try:
        doc = C.new_document(sw, "part")
        ok_build, info = _build(doc)
        row.update({k: v for k, v in info.items() if k != "bbox_m"})
        row["built"] = ok_build
        if not ok_build:
            row["err"] = (
                info.get("err_geometry")
                or info.get("err_refplane")
                or info.get("err_sketch_on_plane")
                or "build failed"
            )
            return row
        picked, per = _select(doc, info)
        row["picked"] = picked
        row["sel_by_mark"] = per
        faces_before = _face_count(doc)
        before = list(FR.feature_names(doc) or [])
        try:
            ret = C.get_com_member(
                doc, "InsertSplitLineProject", bool(is_directional), bool(flip_dir)
            )
            row["ret_is_none"] = ret is None
            if ret is not None:
                try:
                    row["ret_name"] = str(_get(ret, "Name") or "")
                    row["ret_type"] = str(_get(ret, "GetTypeName2") or "")
                except Exception:  # noqa: BLE001
                    pass
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["faces_before"] = faces_before
        row["faces_after"] = _face_count(doc)
        row["face_delta"] = row["faces_after"] - faces_before
        types = []
        try:
            for f in W.iter_features_recursive(doc):
                try:
                    types.append(str(_get(f, "GetTypeName2") or ""))
                except Exception:  # noqa: BLE001
                    pass
        except Exception:  # noqa: BLE001
            pass
        row["split_types"] = [t for t in types if "Split" in t]
        row["ok"] = bool(row["new"]) or row["face_delta"] > 0
        #: ★ 二次读回：★ 面数涨了就是真切开了（★ 不依赖特征树）
        row["split_line_feature"] = None
        for n in after:
            if "Split" in n or "\u5206\u5272\u7ebf" in n:
                row["split_line_feature"] = n
                break
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(_get(doc, "GetTitle") or "")
                if t:
                    _get(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u6295\u5f71\u578b\u5206\u5272\u7ebf\uff1a**\u7167\u5b98\u65b9\u4f8b\u5b50\u91cd\u5efa\u51e0\u4f55**"
        "\uff08\u8349\u56fe\u5728\u5b9e\u4f53\u4e4b\u5916 \u00b7 \u9762\u6309\u843d\u70b9\u9009\uff09",
        "example": "Create_Projection_Split_Line_Example_VB.htm",
        "plane_offset_m": PLANE_OFFSET_M,
        "cases": [],
    }
    combos = [
        (("\u2605 \u4f8b\u5b50\u90a3\u7ec4 (True, True)"), True, True),
        ("(True, False)", True, False),
        ("(False, True)", False, True),
    ]
    for tag, d1, d2 in combos:
        ev["cases"].append(_one(sw, tag, d1, d2))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "projection_split_line_works" if ev["passed"] else "still_fails"
    p = R / "output" / "split-line-geometry-per-example-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"])
    )
    for c in ev["cases"]:
        print("  %-28s ok=%-6s built=%s" % (c.get("tag"), c.get("ok"), c.get("built")))
        print(
            "        ref=%s z_near=%s pick=%s"
            % (c.get("ref_plane"), c.get("z_near_m"), c.get("pick_m"))
        )
        print("        picked=%s" % json.dumps(c.get("picked"), ensure_ascii=False))
        print(
            "        sel_by_mark=%s new=%s face_delta=%s split_types=%s"
            % (
                c.get("sel_by_mark"),
                c.get("new"),
                c.get("face_delta"),
                c.get("split_types"),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
