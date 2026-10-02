"""★ 真机：销钉连接件到底要**组件**还是**面** —— ★ 用"多体零件 + 两个面"做分辨实验。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_pin_wants_faces.py
# 定位:   ★ 2026-10-03（轮 426）承本轮的**两步排除**：
#   ★★ ① 传**裸组件对象** ⇒ `TypeError: must be real number, not dict`（★ 因为形参是**数组**）
#   ★★ ② 改成 `[comp1]` / `[comp2]` **且** 用 `GetComponents` 的**原始 COM 对象**
#     （★ `sw_assembly.get_components` 回的是**字典记录**，★ 不是 COM 对象）⇒
#     ★★★ 而结果是 **计数 `[0, 0]`、★ 无错误** —— ★★ **与 rigid 在单体零件上那次形态相同**
#       （★ 而 rigid 的定论是"**没有东西可连**"）。
#   ★★★ **而这里已经是两个零件了** ⇒ ★ 于是**两个候选**：
#     ```
#     ① ★ 它要的**不是"组件"而是"组件上的面"**（★ 官方形参名是 `DispArrayComp1`，
#        而 rigid 成功那次的配方正是「**两个体 + 每侧一个面**」）⇒ ★ 那就要**再往里一层**；
#     ② ★ 它要**装配体**（★ 而装配体上还得给"组件上的面"）。
#     ```
#   ★★ **本探针分辨它们**：★ **在多体零件上、传"两个体上的面"** ——
#     · 若**成** ⇒ ★ 候选①成立（★ 而"装配体"**根本不是前提**）✓
#     · 若**不成** ⇒ ★ 候选②（★ 装配体才是前提）
#   ★★ 而它**便宜**：★ 复用 rigid 那条已验证的造法（双体零件 + `entities_as_array`）✓
# 官方依据: 出厂类型库反射（`AddPinConnector(DispArrayComp1, DispArrayComp2, ErrorCode&)`）·
#   `IBody2.GetFaces` · `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 在多体零件上传两个面 ⇒ 计数**恰好 +1** ?

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\pin-wants-faces-evidence.json")
STUDY = "DSH-PINF_%s" % time.strftime("%H%M%S")


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts.sw_selection_spec import entities_as_array
    from scripts import sw_simulation_loads as SL

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "study": STUDY}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, -5.0, 20.0)
        sk1 = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk1, 20.0)
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
        try:
            f0 = entities_as_array(doc, "FACE", [0], body_index=0)
            f1 = entities_as_array(doc, "FACE", [0], body_index=1)
            ev["steps"]["entry_check"] = {"ok": len(f0) == 1 and len(f1) == 1 and f0[0] is not f1[0]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["entry_check"] = {"ok": False,
                                          "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
        if (ev["steps"].get("entry_check") or {}).get("ok"):
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                #: ★ **直接调裸函数**（★ 这是分辨实验，★ 包装还没定型）
                rep = SL._report(mgr, lambda: SL.add_pin_connector(mgr, f0, f1), "pin_with_faces", doc)
                ev["steps"]["pin_with_faces"] = {
                    "ok": bool(rep.get("ok")), "count": [rep.get("count_before"), rep.get("count_after")],
                    "error": (rep.get("error") or "")[:130]}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"]["pin_with_faces"] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        ev["verdict"] = "pass" if (ev["steps"].get("pin_with_faces") or {}).get("ok") else "partial"
        ev["note"] = ("★ 分辨实验：★ 销钉连接件要**组件**还是要**面** —— "
                      "★ 在多体零件上、传**两个体上的面**。★ 成 ⇒ 它要面（装配体不是前提）；"
                      "★ 不成 ⇒ 装配体才是前提。")
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
