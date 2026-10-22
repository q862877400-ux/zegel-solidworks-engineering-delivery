"""★ 真机：★ **用 `AddRelation(COINCIDENT)` 强制闭合** —— 比 `MergePoints` 更规范。

★★★ **为什么优先用重合关系（★ 机械 CAD 的标准做法）**：
  ★ `MergePoints` 是**事后合并**（★ 把近点并掉）⇒ ★★ 它**会减少点数**（★ 实测 6→5），
    ★★★ 那是**丢几何**（★ 两条曲线被当成一条）✗
  ★★★ 而 `AddRelation(..., swConstraintType_COINCIDENT)` 是**显式声明**「这两点重合」——
    ★★ 那正是**设计意图**，★ 且**保留两条曲线**（★ 6 段仍是 6 段）✓
  ★ 官方 `MergePoints.md` 的 Remarks **逐字**也推荐这条路：
    ★★ 「To specify a distance below which points are automatically merged while creating
      the segments, use `ISketchRelationManager::AddRelation` … and
      **swConstraintType_COINCIDENT**.」✓

★ 判据：★ ① 段数 = **6**（★ 不丢曲线）· ★ ② 拉伸返回非 None · ★ ③ 体积 ≈ 解析 ✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_coincident.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 真曲线齿廓的**显式重合**闭合。
# 官方依据: `c:\swapi\types\ISketch\MergePoints.md`（★ Remarks 推荐 AddRelation+COINCIDE
#           NT）
#         `c:\swapi\types\ISketchRelationManager\AddRelation.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
import time
import traceback as _tb
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import gear_geometry as G  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from tools.probe_gear_tooth_pattern2 import tooth_curves  # noqa: E402


def _segments(doc):
    try:
        sk = c.get_com_member(doc, "GetActiveSketch2")
        return list(c.get_com_member(sk, "GetSketchSegments") or [])
    except Exception:  # noqa: BLE001
        return []


def _pt_of(seg, which):
    try:
        pt = c.get_com_member(seg, which)
        arr = list(pt) if pt is not None else None
        return (float(arr[0]), float(arr[1])) if arr and len(arr) >= 2 else None
    except Exception:  # noqa: BLE001
        return None


def _main() -> int:
    spec = G.GearSpec(
        module_mm=1.0,
        teeth=20,
        face_width_mm=10.0,
        pressure_angle_deg=20.0,
        bore_diameter_mm=8.0,
    )
    geo = G.calculate_gear_geometry(spec)
    curves, meta = tooth_curves(spec, geo)
    rep = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "★ AddRelation(COINCIDENT) 显式闭合真曲线齿廓",
        "tooth_meta": meta,
        "steps": [],
    }
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = c.get_com_member(doc, "SketchManager")
        ok = 0
        for name, x, y, t0, t1 in curves:
            try:
                c.get_com_member(
                    sm,
                    "CreateEquationSpline2",
                    x,
                    y,
                    "",
                    "%r" % t0,
                    "%r" % t1,
                    False,
                    0.0,
                    0.0,
                    0.0,
                    True,
                    True,
                )
                ok += 1
            except Exception:  # noqa: BLE001
                pass
        rep["steps"].append({"curves_ok": ok})
        segs = _segments(doc)
        rep["steps"].append({"segments_after_curves": len(segs)})

        #: ★★★ **逐对相邻曲线加重合关系**（★ 6 对，★ 首尾相接）
        #:   ★ 官方 `ISketchRelationManager::AddRelation(RelationType, EntitiesArray)`
        #:     ★★ `RelationType` 用 `swConstraintType_e` ⇒ ★ 真机试几种取值（★ 不臆造）
        sk = c.get_com_member(doc, "GetActiveSketch2")
        rm = None
        for g in ("RelationManager", "GetRelationManager"):
            try:
                rm = c.get_com_member(sk, g)
                if rm is not None:
                    break
            except Exception:  # noqa: BLE001
                pass
        rep["steps"].append({"relation_manager": rm is not None})
        added = []
        #: ★★ 先把每条曲线的两个端点取出来（★ 按段序 —— 与创建序一致）
        ends = []
        for i, s in enumerate(segs):
            ends.append((_pt_of(s, "GetStartPoint2"), _pt_of(s, "GetEndPoint2")))
        rep["segment_endpoints_m"] = [
            [[round(v, 9) for v in (a or (0, 0))], [round(v, 9) for v in (b or (0, 0))]]
            for a, b in ends
        ]
        #: ★ 找每对相邻段里**距离最小的端点对**（★ 那就是要合的接缝）
        import math as _m

        joints = []
        n = len(segs)
        for i in range(n):
            j = (i + 1) % n
            best = None
            for ai, a in ((0, ends[i][0]), (1, ends[i][1])):
                for bi, b in ((0, ends[j][0]), (1, ends[j][1])):
                    if a is None or b is None:
                        continue
                    d = _m.dist(a, b)
                    if best is None or d < best[0]:
                        best = (d, ai, bi)
            if best:
                joints.append(
                    {
                        "from_seg": i,
                        "to_seg": j,
                        "gap_um": best[0] * 1e6,
                        "end_a": best[1],
                        "end_b": best[2],
                    }
                )
        rep["joints"] = joints
        rep["max_gap_um"] = max((x["gap_um"] for x in joints), default=None)
        #: ★★ 用**选中端点 + AddRelation** 逐对加（★ 官方：★ 先选实体再 AddRelation）
        for jt in joints:
            try:
                ext = c.get_com_member(doc, "Extension")
                doc.ClearSelection2(True)
                #: ★ `ISketchPoint::Select4(Append, Callout)`（★ 事实 32：★ 点也没有名字
                #: ）
                ok_a = False
                for s_i, e_i in (
                    (jt["from_seg"], jt["end_a"]),
                    (jt["to_seg"], jt["end_b"]),
                ):
                    try:
                        pt = c.get_com_member(
                            segs[s_i], "GetStartPoint2" if e_i == 0 else "GetEndPoint2"
                        )
                        #: ★ 选**草图点对象**（★ 不是曲线）
                        obj = c.get_com_member(pt, "GetSketchPoint") if False else None
                        ok_a = bool(c.get_com_member(pt, "Select4", not ok_a, None))
                    except Exception:  # noqa: BLE001
                        pass
                got = None
                if rm is not None:
                    #: ★★ `swConstraintType_COINCIDENT` 的取值 ⇒ ★ 试几个（★ 真机判）
                    for val in (5, 4, 3, 2, 1, 0):
                        try:
                            got = c.get_com_member(rm, "AddRelation", val, None)
                            if got:
                                break
                        except Exception:  # noqa: BLE001
                            continue
                added.append({"joint": jt, "selected": ok_a, "relation_ret": got})
            except Exception as exc:  # noqa: BLE001
                added.append(
                    {
                        "joint": jt,
                        "error": "%s: %s" % (type(exc).__name__, str(exc)[:90]),
                    }
                )
        rep["steps"].append({"relations": added[:8]})
        rep["steps"].append({"segments_after_relations": len(_segments(doc))})
        try:
            rep["constrained_status"] = int(
                c.get_com_member(
                    c.get_com_member(doc, "GetActiveSketch2"), "GetConstrainedStatus"
                )
            )
        except Exception:  # noqa: BLE001
            pass
        P.end_sketch(doc)
        f = P.extrude_boss(doc, "草图1", 0.010)
        rep["extrude_ok"] = f is not None
        if f is not None:
            try:
                mp = c.get_com_member(
                    c.get_com_member(doc, "Extension"), "CreateMassProperty"
                )
                rep["volume_mm3"] = float(c.get_com_member(mp, "Volume")) * 1e9
            except Exception:  # noqa: BLE001
                pass
    except Exception as exc:  # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    p = R / "output" / "_probe_gear_coincident.json"
    p.write_text(
        json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  ★ 曲线 %s · 段数 %s"
        % (
            rep["steps"][0].get("curves_ok"),
            rep["steps"][1].get("segments_after_curves"),
        )
    )
    print(
        "  ★ 最大缝 = %s µm · 6 个接缝：%s"
        % (
            rep.get("max_gap_um"),
            [
                (round(x["gap_um"], 3), x["from_seg"], x["to_seg"])
                for x in (rep.get("joints") or [])
            ],
        )
    )
    for a in (rep["steps"][2].get("relations") or [])[:6]:
        print(
            "     接缝 %s 选中=%s AddRelation=%s %s"
            % (
                (a.get("joint") or {}).get("from_seg"),
                a.get("selected"),
                a.get("relation_ret"),
                (a.get("error") or "")[:70],
            )
        )
    print(
        "  ★ 加关系后段数 = %s · 约束状态 = %s"
        % (
            rep["steps"][3].get("segments_after_relations"),
            rep.get("constrained_status"),
        )
    )
    print(
        "  ★ 拉伸 = %s · 体积 = %s mm³" % (rep.get("extrude_ok"), rep.get("volume_mm3"))
    )
    if rep.get("error"):
        print("  ✗ %s" % rep["error"])
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:  # noqa: BLE001
        (R / "output" / "_probe_gear_coincident_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8"
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
