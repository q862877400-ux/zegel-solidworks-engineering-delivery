"""★ 真机：**验一个新判据** —— 它落在**载荷对象**上（读 `Type`），而不是落在管理器的 `Count` 上。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_judge_object_type.py
# 定位:   ★ 2026-10-03（轮 421）`specs/150-judge-first-rollout/spec.md` 的 **T1.1**：
# ★★ 「按 R1 先做**判据前置**：在一个**已知成功**的场景上，★ 验"新判据"能复现正向信号」
# 。
#   ★ 背景：★ 旧判据（`ICWLoadsAndRestraintsManager.Count`）在 B 组那条路上**间歇性不稳**
#     （事实 332/334）；★ 而 `GetLoadsAndRestraints(i, out_i4())` 那次也报了 `0x800706BA`。
#   ★★ 而**候选是从出厂类型库枚举出来的**（★ 不猜）：
#     ```
#     ICWLoadsAndRestraintsManager 的属性： ★ **只有 `Count` 一个**（没有别的计数）
#     ICWLoadsAndRestraints（载荷对象自己）：
#        P: **Name, Type, State, EntityCount**
#        M: SuppressUnSuppress, GetEntityAt, GetReferenceGeometry, GetDirection
#     ```
#     ⇒ ★★ **新判据：按序号取到那个对象 ⇒ 读它自己的 `Type`/`Name`** ——
#       ★ **不读 `Count`、也不读管理器**（拿到对象之后就在对象上读）。
#     ⇒ ★★★ 而它**比计数更强**：★ 计数只说明"多了一个"，★ `Type` 说明"多的是哪个"。
# 官方依据: 出厂类型库（`SolidWorks.Interop.cosworks.dll` **34.4.1.1011**）的元数据反射 
#           ·
#   `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 在**已知成功**的场景（`apply_force`）上，新判据能取到对象 **且** 它的 `Type`
#  有值
#   ⇒ ★ 那才叫"这个判据可用"。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "judge-object-type-evidence.json")
STUDY = "DSH-JOBJ_%s" % time.strftime("%H%M%S")


def _read_objects(manager) -> dict:
    """★ 新判据：**按序号取载荷对象，读它自己的属性**（★ 不读 `Count`）。"""
    from sw_connect import get_com_member, out_i4
    from sw_connect import safe_get_com_member
    items, err = [], None
    for i in range(0, 16):
        try:
            obj = get_com_member(manager, "GetLoadsAndRestraints", int(i), out_i4())
        except Exception as exc:                               # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:110])
            break
        if obj is None:
            break
        rec = {"index": i}
        for prop in ("Name", "Type", "State", "EntityCount"):
            try:
                rec[prop] = repr(safe_get_com_member(obj, prop))
            except Exception as exc:                           # noqa: BLE001
                rec[prop + "_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        items.append(rec)
    return {"count": len(items), "items": items, "err": err}


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

        ev["steps"]["before"] = _read_objects(mgr)
        #: ★ **已知成功**的场景：`apply_force`（★ 它已被真机验过会 +1）
        try:
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            sim.select_face_at(doc, 0.0, 0.0, 0.0)
            rep = SL.apply_force_report(mgr, doc, 1)
            ev["steps"]["apply_force"] = {
                "old_judge_ok": bool(isinstance(rep, dict) and rep.get("ok")),
                "count": [rep.get("count_before"), rep.get("count_after")]
                if isinstance(rep, dict) else None,
                "error": (rep.get("error") or "")[:100] if isinstance(rep, dict) else None}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["apply_force"] = {
                "old_judge_ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
        ev["steps"]["after"] = _read_objects(mgr)

        b = ev["steps"]["before"].get("count")
        a = ev["steps"]["after"].get("count")
        typed = any(("Type" in it) and (it.get("Type") not in (None, "None"))
                    for it in (ev["steps"]["after"].get("items") or []))
        ev["new_judge_usable"] = bool(a == (b or 0) + 1 and typed)
        ev["new_judge_signal"] = {"count": [b, a], "has_type": typed}
        ev["verdict"] = "pass" if ev["new_judge_usable"] else "partial"
        ev["note"] = ("★ T1.1 \u5224\u636e\u524d\u7f6e\uff1a\u2605 \u5728**\u5df2\u77e5\u6210\u529f**\u7684\u573a\u666f\uff08`apply_force`\uff09\u4e0a\uff0c"
                      "\u2605 \u9a8c**\u65b0\u5224\u636e**\uff08\u6309\u5e8f\u53f7\u53d6\u8f7d\u8377\u5bf9\u8c61 \u21d2 \u8bfb\u5b83\u81ea\u5df1\u7684 `Type`\uff09"
                      "\u80fd\u4e0d\u80fd\u590d\u73b0\u6b63\u5411\u4fe1\u53f7\u3002\u2605 \u65b0\u5224\u636e**\u4e0d\u8bfb `Count`**\u3002")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  \u4ea7\u7269: %s \u21d2 %s" % (OUT, str(ev["verdict"]).upper()))
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
