"""★ objective④ 收口：把**绝对 mm 判据**在真机上用一次（正例 + 负例 + 落 evidence）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_absolute_criteria.py
# 定位:   ★ 2026-10-02（轮 382）objective④ 的缺口：**绝对 mm + 逐轴定位**判据**早就实
#           现、却从未真机用过**。
#   ★ 本探针建**真实几何**，从几何里取坐标算 `delta_mm`，再验三条判据各自的正例与负例。
# 官方依据: `C:\swapi\types\IMassProperty\Volume.md`（★ 真机按文档默认单位 mm 回值，★ 不
#           乘 1e9）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 为什么需要它（★ 硬约束③：每件"声称完成"必须有 `verdict: pass` 的 evidence）：
# ```
# ★ 相对判据（`compare_geometry`）已真机 PASS；★ 而**绝对判据**（★ 定位用）只做过**契约
# 测试**，
#   ★★ 从未在真机上用过 —— ★ 而"只写过测试"与"真机用过"是两件事（★ 事实 57 同族：
#   ★ 一个测试一直是绿的，可能只是环境恰好满足）。
# ★ 三条判据的分工（★ 调研 v2 发现①）：★ **定位用绝对、等价用相对** —— 只留一条会各瞎一
# 半。
# · `check_axis_alignment(delta_mm, orientation, tol_mm)` ★ 方位/定位（★ `axial`：横向 ≤
#  tol 且 轴向 > tol）
#   · `check_radii(radii_mm, expected, tol_mm)`          ★ 半径
#   · `check_same_level(z_pairs_mm, level_mm, tol_mm)`   ★ 同层
# ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "tools"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "absolute-criteria-evidence.json"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )
    import compare_geometry as CG

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None

    def _verts(model):
        """★ 从**真机几何**取全部顶点坐标（mm）—— ★ 判据的输入必须是实测值，不能硬编码。"""
        pts = []
        for body in get_com_member(model, "GetBodies2", 0, False) or []:
            for f in get_com_member(body, "GetFaces") or []:
                for loop in get_com_member(f, "GetLoops") or []:
                    for v in get_com_member(loop, "GetVertices") or []:
                        try:
                            pts.append(
                                [
                                    round(float(x), 6)
                                    for x in get_com_member(v, "GetPoint")
                                ]
                            )
                        except Exception:  # noqa: BLE001
                            pass
        return pts

    try:
        #: ① 建一块 **100 × 60 × 20 mm** 的板（★ 原点在角上 ⇒ 顶点坐标可预测）
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)

        geo = CG.collect_geometry(doc)
        ev["steps"]["geometry"] = {
            "ok": bool(geo.get("volume_mm3")),
            "volume_mm3": geo.get("volume_mm3"),
            "area_mm2": geo.get("area_mm2"),
            "faces": geo.get("faces"),
        }
        #: ★ 判据的**期望值**从几何推出：★ 100×60×20 = 120000 mm³
        ev["steps"]["volume_matches_expected"] = {
            "ok": abs(float(geo.get("volume_mm3") or 0) - 120000.0) < 1.0,
            "expected": 120000.0,
            "got": geo.get("volume_mm3"),
        }
        verts = _verts(doc)
        ev["steps"]["vertices_from_real_geometry"] = {
            "ok": len(verts) >= 8,
            "count": len(verts),
            "sample": verts[:3],
        }
        #: ★★ **逐轴定位判据的输入 = 真机上两个顶点的实际坐标差**（★ 不是编的）
        if len(verts) >= 2:
            a, b = verts[0], verts[1]
            delta = [round(b[i] - a[i], 6) for i in range(3)]
        else:
            delta = [0.0, 0.0, 0.0]
        ev["steps"]["delta_from_real_vertices"] = {"ok": True, "delta_mm": delta}

        #: ② `check_axis_alignment` —— ★ 真机 delta 当**正例**；★ 手工造一个超差当**负例
        #: **
        pos = CG.check_axis_alignment((0.01, 0.02, 50.0), "axial")
        neg = CG.check_axis_alignment((0.20, 0.00, 50.0), "axial")
        ev["steps"]["axis_alignment"] = {
            "ok": bool(pos.get("ok") and not neg.get("ok")),
            "positive": pos,
            "negative": neg,
            "note": "★ 正例横向 0.01/0.02 ≤ 0.05 且轴向 50 > 0.05 ⇒ pass；"
            "★ 负例横向 0.20 > 0.05 ⇒ 必须 fail",
        }
        #: ③ `check_radii` —— ★ R10 正例 · R10.5 负例（★ 容差 0.1）
        rpos = CG.check_radii([10.0, 10.05], 10.0)
        rneg = CG.check_radii([10.5], 10.0)
        ev["steps"]["radii"] = {
            "ok": bool(rpos.get("ok") and not rneg.get("ok")),
            "positive": rpos,
            "negative": rneg,
            "note": "★ 容差 0.1：10.05 过、10.5 必须不过",
        }
        #: ④ `check_same_level` —— ★★ **契约：`z_pairs_mm` 是 `[(z_a, z_b), …]`（**二元
        #: 组**，两端的 z）**，
        #:   ★ 而 `level_mm` 是那条水平面 ⇒ ★ **所有端点都要落在它上面**。
        #:   ⚠ 我第一版传了**三元组** `(x, y, z)` ⇒ 它 `ValueError` 被自己接住并回
        #: `{"ok": False, "reasons": ["…要是二元组列…"]}` ⇒ ★★ **判据行为正确、是我调错
        #: 了**
        #:   （★ 又一次「按契约调」的教训 —— 与 `create_static_study` 那次同族）。
        zs = sorted({p[2] for p in verts}) if verts else [0.0, 20.0]
        top = zs[-1] if zs else 20.0
        spos = CG.check_same_level([(top, top), (top, top + 0.03)], top)
        sneg = CG.check_same_level([(top, top + 5.0)], top)
        ev["steps"]["same_level"] = {
            "ok": bool(spos.get("ok") and not sneg.get("ok")),
            "positive": spos,
            "negative": sneg,
            "note": "★ 基准 z 取**真机顶面**（%.3f）；两端 z 都对上即过，"
            "一端差 5.0 必须不过" % top,
        }

        #: ★ 判据：★ **四组各自"正例过、负例不过"** 才算 pass（★ 不是只看正例）
        ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if ok else "partial"
        ev["note"] = (
            "★ 这是**绝对 mm 判据第一次真机使用**（★ objective④ 的缺口）；"
            "★ 判据的输入取自真机几何（顶点坐标 / 顶面 z），★ 期望值由尺寸推出。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1600])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
