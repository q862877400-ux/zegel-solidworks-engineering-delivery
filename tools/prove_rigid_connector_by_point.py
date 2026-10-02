"""★ 真机：刚性连接件 —— ★ **换维度**：用「按面上的点」那条**已验证的路**选两组面（而非按序号选实体）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_rigid_connector_by_point.py
# 定位:   ★ 2026-10-03（轮 422）承**事实 335** 的具体下一步，`plan-200r-v3` 段 1 的收尾。
#   ★★ 事实 335 的结论：★ 崩的**不是判据**（老判据那次 `raw_Count=0` 好好的），
#     ★ 而**嫌疑在"选实体"那一步** —— ★ 因为：
#       · **崩的两条**（link / rigid）是**唯一**用 `select_entity_by_index`（按**序号**选实体）；
#       · 而**所有成功**的载荷探针都用 `sim.select_face_at`（**按面上的点**）。
#   ⇒ ★★ 本探针**换的是维度不是参数**：★ **刚性连接件只用"按面上的点"选两组面**。
#   ★ 而它**照 `select_face_at` 自己的文档要求**做了一件之前没做的事：
#     ★★ 「计数为 0 就说明没选中，**此时不要继续施夹/加载**（会得到空的 DispArray）」
#       ⇒ ★ **每一步都回读选区计数、为 0 就停下**（★ 早失败优于静默）。
#   ⚠ **link_connector 不在本探针里**：★ 它要**两个顶点**，而"按面上的点"选不出顶点
#     ⇒ ★ 顶点那条路**另算**（★ 而它没被事实 32 覆盖过）。
# 官方依据: 本仓事实 32（选实体的可行路径）· `SelectByID2("", "FACE", x, y, z, …)` ·
#   `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每一步的选择**回读计数不为 0**，★ 且施加后回读计数**恰好 +1**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\rigid-connector-by-point-evidence.json")
STUDY = "DSH-RIGID_%s" % time.strftime("%H%M%S")


def main() -> int:
    import sw_connect
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts import sw_simulation_loads as SL

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "study": STUDY}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        sim.create_static_study(sw, STUDY)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, STUDY))
        ev["steps"]["static_study"] = {"ok": mgr is not None}

        #: ★ **按面上的点**选两组面（★ 与所有成功探针同一条路）
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        c1 = sim.select_face_at(doc, 0.0, 0.0, 0.0)                  #: 前面 z=0（米）
        c2 = sim.select_face_at(doc, 0.0, 0.0, 0.02, append=True)    #: 后面 z=20mm
        ev["steps"]["select_two_faces"] = {"ok": c1 == 1 and c2 == 2, "counts": [c1, c2],
                                           "note": "★ 按面上的点；★ 回读 1 与 2 才算选对（事实 8：返回值不可信）"}
        if c1 == 1 and c2 == 2:
            try:
                rep = SL.apply_rigid_connector_report(mgr, doc)
                ev["steps"]["rigid_connector"] = {
                    "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                    "count": [rep.get("count_before"), rep.get("count_after")]
                    if isinstance(rep, dict) else None,
                    "error": (rep.get("error") or "")[:110] if isinstance(rep, dict) else None}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"]["rigid_connector"] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        else:
            ev["steps"]["rigid_connector"] = {"ok": False, "skipped": "选区没选对 ⇒ 不继续（早失败优于静默）"}
        ok = bool((ev["steps"].get("rigid_connector") or {}).get("ok"))
        ev["verdict"] = "pass" if ok else "partial"
        ev["note"] = ("★ 换维度：★ 刚性连接件只用**按面上的点**选两组面（★ 与所有成功探针同一条路），"
                      "★ 且**每步回读选区计数**。★ 判据：选择计数 1→2，★ 施加后载荷计数恰好 +1。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1400])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
