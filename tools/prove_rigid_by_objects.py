"""★ 真机：**按已知实体清单**加刚性连接件 —— ★ 事实 337 的正解（**不读选区**）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_rigid_by_objects.py
# 定位:   ★ 2026-10-03（轮 424）`plan-200r-v3` 段 1（B 组）—— ★ 而这是**换假设**之后的第一枪。
#   ★★ **事实 337 的正解**：★ `ISelectionMgr` 上"按序号取对象"那一族**只拿得到第 1 个**
#     （★ `GetSelectedObject6`/`4`/`5`/`GetSelectedObjectsFace` 五个入口都试过），
#     ★ 而 `GetSelectedObjectCount2(-1)` **如实报 2** ⇒ ★★ **"从选区读回多个"不通**。
#   ★★★ 而**实体对象本身**用 `entities_on_body` **就能直接拿到**（★ 事实 32 的"按对象"那条）
#     ⇒ ★★ 于是**把已知的那些对象直接装成数组**（`entities_as_array`）✓
#   ★★ 而本探针**照本轮的纪律**：★ **先验入口、再施加** ——
#     ★ 先量 `entities_as_array` 拿到的**数组长度**对不对（★ 那才是"验判据"），
#     ★ 长度对了才继续施加。
#   ★ 算例名用**唯一名**（事实 329/414 的教训）。
# 官方依据: `ICWLoadsAndRestraintsManager.AddRigidConnector(PersistIDFaceArray, PersistIDTargetArray)`
#   （★ 出厂类型库反射）· `IBody2.GetFaces` · `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ ① 数组长度 = 请求的序号个数（★ 入口可用）；★ ② 施加后回读计数**恰好 +1**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\rigid-by-objects-evidence.json")
STUDY = "DSH-ROBJ_%s" % time.strftime("%H%M%S")


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts.sw_selection_spec import entities_as_array, entities_on_body
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

        #: ★ ① **先验入口**：数组长度对不对（★ 那才是"验判据"）
        try:
            all_faces = entities_on_body(doc, "FACE")
            src = entities_as_array(doc, "FACE", [0])
            tgt = entities_as_array(doc, "FACE", [1])
            ev["steps"]["entry_check"] = {
                "ok": len(src) == 1 and len(tgt) == 1 and src[0] is not tgt[0],
                "body_face_count": len(all_faces),
                "src_len": len(src), "tgt_len": len(tgt),
                "src_is_tgt": src[0] is tgt[0],
                "note": "★ 先验入口：★ 长度对、且两组**不是同一个对象** ⇒ 才继续施加"}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["entry_check"] = {"ok": False,
                                          "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}

        #: ★ ② 施加（★ 它**不读选区**，★ 所以先清一下让它干净）
        if (ev["steps"].get("entry_check") or {}).get("ok"):
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                rep = SL.apply_rigid_connector_by_objects_report(mgr, doc, [0], [1])
                ev["steps"]["rigid_by_objects"] = {
                    "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                    "count": [rep.get("count_before"), rep.get("count_after")]
                    if isinstance(rep, dict) else None,
                    "error": (rep.get("error") or "")[:120] if isinstance(rep, dict) else None}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"]["rigid_by_objects"] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        else:
            ev["steps"]["rigid_by_objects"] = {"ok": False, "skipped": "★ 入口没验过 ⇒ 不施加（本轮纪律：先验再改）"}
        ok = bool((ev["steps"].get("rigid_by_objects") or {}).get("ok"))
        ev["verdict"] = "pass" if ok else "partial"
        ev["note"] = ("★ 事实 337 的正解第一枪：★ **按已知实体清单装数组**（`entities_as_array`）"
                      "★ 而**不读选区**。★ 判据：① 数组长度对且两组不同 ② 施加后计数恰好 +1。")
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
