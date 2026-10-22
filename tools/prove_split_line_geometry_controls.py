"""★ 真机：投影型分割线的**正例复核 + 三个负例对照**（★ 证明几何条件才是承重的）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_split_line_geometry_controls.py
# 定位:   ★ 承接 `tools/prove_split_line_geometry_per_example.py`（★ 它已把投影型分割
#           线**建成了**）。
#     ★★ **为什么还要跑这一轮**：★ 单次"成了"**不是结论** ——
#       ★ 必须证明**是哪一处几何使之成立**（★ 否则下次换个零件又不知道怎么办）。
#
#   ★★ 四个格子（★ 只动**一处**变量，其余全等）：
#     | 格 | 变动 | 预期 |
#     |---|---|---|
#     | A | **正例复核**：落点在环内 + 选**近面** | ★ 该成 |
#     | B | **只**把落点移到**环外**（★ 仍在同一张面上 ⇒ mark 1 计数仍应为 1） | ★ 该不成 |
#     | C | **只**把面换成**远面**（★ 投影落在近面，远面拿不到） | ★ 该不成 |
# | D | **复现上一会话的几何**：草图在实体**内部** + 取 `GetFaces()[0]` | ★ 该不成（★ 对
# 照事实 419） |
#
#   ★★★ **结构判据**（★ 本轮新增，★ 比"树长了"硬）：
# · `IFace2.GetLoopCount()` —— ★ 闭合环投影到面上 ⇒ **该面从 1 个环变成 2 个环**（外环 +
#  内环）；
#     · 新特征的 `GetTypeName2` —— ★ 直接读类型名，不靠中文名猜。
#     ⇒ ★ 三条一起（树增量 · 面数 +1 · 有面出现 2 个环）才算"真切开"。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每格新开文档；★ 收尾关掉自己开的文档。
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
import scripts.sw_feature_readback as FR  # noqa: E402
from scripts.sw_simulation import select_face_at  # noqa: E402
import prove_split_line_geometry_per_example as G  # noqa: E402


def _loops_per_face(doc):
    """★ **结构判据**：逐面读 `IFace2.GetLoopCount()` ⇒ 切开的那张面会出现 **2 个环**。"""
    out = []
    for b in list(G._get(doc, "GetBodies2", 0, True) or []):
        for f in list(G._get(b, "GetFaces") or []):
            try:
                out.append(int(G._get(f, "GetLoopCount")))
            except Exception:  # noqa: BLE001
                out.append(-1)
    return sorted(out)


def _inner_loop_edges(doc):
    """★ 找到"有 2 个环"的那张面，回报**内环**的边数（★ 投影一个圆 ⇒ 内环应为 1 条边）。"""
    for b in list(G._get(doc, "GetBodies2", 0, True) or []):
        for f in list(G._get(b, "GetFaces") or []):
            try:
                if int(G._get(f, "GetLoopCount")) != 2:
                    continue
                loops = list(G._get(f, "GetLoops") or [])
                if len(loops) != 2:
                    continue
                counts = []
                for lp in loops:
                    try:
                        counts.append(int(G._get(lp, "GetEdgeCount")))
                    except Exception:  # noqa: BLE001
                        counts.append(-1)
                return counts
            except Exception:  # noqa: BLE001
                continue
    return None


def _run_case(sw, tag, mode):
    """★ `mode` 决定**只动哪一处**：near/near_outside/far/legacy。"""
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        if mode == "legacy":
            #: ★ 复现上一会话的几何：Top Plane 拉 20 mm（实体 z∈[-30,30]）· 投影草图在 F
            #: ront Plane（z=0，**在实体内部**）
            P.start_sketch(doc, plane_name="Top Plane")
            G._get(
                G._get(doc, "SketchManager"),
                "CreateCornerRectangle",
                -0.03,
                -0.03,
                0.0,
                0.03,
                0.03,
                0.0,
            )
            P.end_sketch(doc)
            for cand in (G._sketch_names(doc) or ["\u8349\u56fe1"])[::-1]:
                try:
                    P.extrude_boss(doc, cand, 0.02)
                    break
                except Exception:  # noqa: BLE001
                    continue
            box = G._bbox(doc)
            row["bbox_m"] = box
            P.start_sketch(doc, plane_name="Front Plane")
            G._get(
                G._get(doc, "SketchManager"),
                "CreateCircleByRadius",
                0.0,
                0.0,
                0.0,
                0.008,
            )
            P.end_sketch(doc)
            doc.ClearSelection2(True)
            picked = {}
            for nm in ("\u51f8\u53f0-\u62c9\u4f381", "Boss-Extrude1"):
                try:
                    if P._select_by_id(
                        G._get(doc, "Extension"),
                        nm,
                        "BODYFEATURE",
                        append=False,
                        mark=0,
                    ):
                        picked["feature"] = nm
                        break
                except Exception:  # noqa: BLE001
                    continue
            try:
                if P._select_by_id(
                    G._get(doc, "Extension"),
                    G._sketch_names(doc)[-1],
                    "SKETCH",
                    append=True,
                    mark=4,
                ):
                    picked["sketch"] = G._sketch_names(doc)[-1]
            except Exception:  # noqa: BLE001
                pass
            #: ★ 上一会话取的就是**第一张面**
            try:
                faces = list(
                    G._get(list(G._get(doc, "GetBodies2", 0, True))[0], "GetFaces")
                    or []
                )
                if faces and G._get(faces[0], "Select4", True, P._empty_callout()):
                    picked["face"] = "GetFaces()[0]"
            except Exception:  # noqa: BLE001
                pass
            per = {}
            for m in (0, 1, 4):
                try:
                    per[str(m)] = int(
                        G._get(
                            G._get(doc, "SelectionManager"),
                            "GetSelectedObjectCount2",
                            m,
                        )
                    )
                except Exception:  # noqa: BLE001
                    per[str(m)] = -1
            row["picked"], row["sel_by_mark"] = picked, per
            return _call_and_read(doc, row)
        #: ★ A / B / C 共用**同一个**（正确的）几何搭建
        ok_build, info = G._build(doc)
        row.update({k: v for k, v in info.items() if k != "bbox_m"})
        row["built"] = ok_build
        if not ok_build:
            row["err"] = "build failed"
            return row
        #: ★★★ **只改落点**：三种模式各自的落点
        xmin, ymin, zmin, xmax, ymax, zmax = info["bbox_m"]
        if mode == "near_outside":
            #: ★ 仍在**同一张面**上，但落在投影环**之外**（★ 离圆心 ~43 mm >> 半径 8 mm
            #: ）
            info["pick_m"] = [xmax - 0.005, ymax - 0.005, min(zmin, zmax)]
        elif mode == "far":
            #: ★ 换成**远面**（投影落在近面 ⇒ 远面拿不到）
            info["pick_m"] = [(xmin + xmax) / 2.0, (ymin + ymax) / 2.0, max(zmin, zmax)]
            row["projection_lands_on"] = [0.0, 0.0, min(zmin, zmax)]
        picked, per = G._select(doc, info)
        row["picked"], row["sel_by_mark"] = picked, per
        row["pick_m"] = info["pick_m"]
        return _call_and_read(doc, row)
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


def _call_and_read(
    doc,
    row,
    is_directional=True,
    flip_dir=True,
    member="InsertSplitLineProject",
    args=None,
    require_inner_loop=True,
):
    """★ 调分割线入口并三条判据一起读（★ 树增量 · 面数 · 环数）。

    ★★ **`require_inner_loop` 是必须的一个开关**：★ 投影型切出的是**内环**
      （该面 1 环 → 2 环），★ 而**轮廓型**是沿曲面切出**两张独立的面**（★ **内环不会出现**）
      ⇒ ★ 用同一个判据会把轮廓型的成功误判成失败。
    """
    faces_before = G._face_count(doc)
    loops_before = _loops_per_face(doc)
    before = list(FR.feature_names(doc) or [])
    call_args = (
        list(args) if args is not None else [bool(is_directional), bool(flip_dir)]
    )
    row["called_with"] = "%s(%s)" % (member, ", ".join(str(a) for a in call_args))
    try:
        ret = C.get_com_member(doc, member, *call_args)
        row["ret_is_none"] = ret is None
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    after = list(FR.feature_names(doc) or [])
    row["new"] = [n for n in after if n not in before]
    row["face_delta"] = G._face_count(doc) - faces_before
    row["loops_before"] = loops_before
    row["loops_after"] = _loops_per_face(doc)
    row["split_face_loop_edge_counts"] = _inner_loop_edges(doc)
    #: ★ 直接读新特征的**类型名**（★ 不靠中文名猜）
    types = {}
    for n in row["new"]:
        try:
            f = _feature_by_name(doc, n)
            if f is not None:
                types[n] = str(G._get(f, "GetTypeName2") or "")
        except Exception:  # noqa: BLE001
            pass
    row["new_feature_types"] = types
    ok = bool(row["new"]) and row["face_delta"] > 0
    if require_inner_loop:
        ok = ok and 2 in row["loops_after"]
    row["ok"] = ok
    return row


def _call_and_read_sil(doc, row):
    """★ **轮廓型**：`InsertSplitLineSil()`（★ 零参数）—— ★ 判据**不要求内环**。"""
    return _call_and_read(
        doc, row, member="InsertSplitLineSil", args=(), require_inner_loop=False
    )


def _feature_by_name(doc, name):
    for f in G.W.iter_features_recursive(doc):
        try:
            if str(G._get(f, "Name") or "") == name:
                return f
        except Exception:  # noqa: BLE001
            continue
    return None


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u6295\u5f71\u578b\u5206\u5272\u7ebf\uff1a**\u6b63\u4f8b\u590d\u6838 + \u4e09\u4e2a\u8d1f\u4f8b\u5bf9\u7167**"
        "\uff08\u53ea\u6539\u4e00\u5904\u53d8\u91cf\uff09",
        "cases": [],
    }
    for tag, mode in (
        (
            "\u2605 A \u6b63\u4f8b\u590d\u6838\uff08\u843d\u70b9\u5728\u73af\u5185 + \u8fd1\u9762\uff09",
            "near",
        ),
        (
            "\u2605 B \u53ea\u6539\u843d\u70b9\u5230\u73af\u5916\uff08\u540c\u4e00\u5f20\u9762\uff09",
            "near_outside",
        ),
        ("\u2605 C \u53ea\u6539\u6210\u8fdc\u9762", "far"),
        ("\u2605 D \u590d\u73b0\u4e0a\u4e00\u4f1a\u8bdd\u7684\u51e0\u4f55", "legacy"),
    ):
        ev["cases"].append(_run_case(sw, tag, mode))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "split-line-geometry-controls-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a\u6210 %d / %d" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print(
            "  %-34s ok=%-6s new=%-12s face_delta=%-3s loops=%s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("new"),
                c.get("face_delta"),
                c.get("loops_after"),
            )
        )
        print(
            "        pick=%s sel_by_mark=%s types=%s"
            % (
                c.get("pick_m"),
                c.get("sel_by_mark"),
                json.dumps(c.get("new_feature_types"), ensure_ascii=False),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
