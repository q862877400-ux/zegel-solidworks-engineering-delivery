"""★ 真机：**双体零件**上试刚性连接件 —— ★ 事实 338 那个"它要两个体"的假设。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_rigid_twobody.py
# 定位:   ★ 2026-10-03（轮 425）承**事实 338** 的新假设。
#   ★★ 那一轮的定性：★ 换成"按已知实体清单装数组"之后**不再崩**了，★ 而
#     `AddRigidConnector` **成功返回却不建**（★ 计数 `0→0`、★ 无错误）。
#   ★★★ 而**同族形参名自己给了线索**：★ `AddPinConnector(**DispArrayComp1**, **DispArrayComp2**)` ·
#     `AddSpringConnector(…, DispArrayComp1, DispArrayComp2)` ⇒ ★★ **写的是 `Comp`（零件）**
#     ⇒ ★ **这一族"连接件"本来就是**连接两个东西**的** —— ★ 而**我一直在单体零件上试** ⚠
#   ★★ **本探针用一个更干净的测法**：★ **双体零件**（★ 而非装配体）——
#     · ★ `entities_on_body` **本来就收 `body_index`** ⇒ ★ 两个体的面都能直接拿到 ✓
#     · ★ **不用保存、不用装配**（★ 硬约束⑦ 禁保存 ⇒ 这条路绕开它）✓
#   ★ 造法：★ 两个矩形 + 两次拉伸，★ 第二次 **`merge=False`**（★ 即留成**新体**）——
#     ★ 两次的矩形**在 x 方向错开**，★ 于是是两个**分开的**实体。
# 官方依据: `ICWLoadsAndRestraintsManager.AddRigidConnector(PersistIDFaceArray, PersistIDTargetArray)`
#   （★ 出厂类型库反射）· `IBody2.GetFaces` · `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 体数为 **2** ★ 且施加后回读计数**恰好 +1**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\rigid-twobody-evidence.json")
STUDY = "DSH-R2B_%s" % time.strftime("%H%M%S")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
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
        #: ★ 体 1：x ∈ [-30, -5]
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, -5.0, 20.0)
        sk1 = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk1, 20.0)
        #: ★ 体 2：x ∈ [5, 30]，★ **merge=False ⇒ 留成新体**
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 5.0, -20.0, 30.0, 20.0)
        sk2 = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk2, 20.0, merge=False)

        bodies = safe_get_com_member(doc, "GetBodies2", 0, True)
        ev["steps"]["two_bodies"] = {"ok": bool(bodies) and len(list(bodies)) == 2,
                                     "body_count": len(list(bodies)) if bodies else 0}
        sim.create_static_study(sw, STUDY)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, STUDY))

        #: ★ 先验入口（★ 本轮的纪律）：★ 两个体上各取一个面
        try:
            f0 = entities_as_array(doc, "FACE", [0], body_index=0)
            f1 = entities_as_array(doc, "FACE", [0], body_index=1)
            n0 = len(entities_on_body(doc, "FACE", body_index=0))
            n1 = len(entities_on_body(doc, "FACE", body_index=1))
            ev["steps"]["entry_check"] = {"ok": len(f0) == 1 and len(f1) == 1 and f0[0] is not f1[0],
                                          "faces_per_body": [n0, n1]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["entry_check"] = {"ok": False,
                                          "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}
        if (ev["steps"].get("entry_check") or {}).get("ok"):
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                rep = SL.apply_rigid_connector_by_objects_report(
                    mgr, doc, [0], [0], source_body_index=0, target_body_index=1)
                ev["steps"]["rigid_twobody"] = {
                    "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                    "count": [rep.get("count_before"), rep.get("count_after")]
                    if isinstance(rep, dict) else None,
                    "error": (rep.get("error") or "")[:120] if isinstance(rep, dict) else None}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"]["rigid_twobody"] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        else:
            ev["steps"]["rigid_twobody"] = {"ok": False, "skipped": "★ 入口没验过 ⇒ 不施加"}
        ev["verdict"] = "pass" if (ev["steps"].get("rigid_twobody") or {}).get("ok") else "partial"
        ev["note"] = ("★ 双体零件（★ 不用保存、不用装配）上试刚性连接件 —— "
                      "★ 验事实 338 的假设「它要**两个体**才能连」。"
                      "★ 判据：① 体数 2 ★ 两个体上各取到一个面 ★ ② 施加后计数恰好 +1。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
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
