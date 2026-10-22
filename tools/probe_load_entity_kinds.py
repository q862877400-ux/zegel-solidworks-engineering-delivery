"""★ 真机：**实体种类 × 载荷** 的穷举表（★ 官方文本说这族各自要求的实体种类不同）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_load_entity_kinds.py
# 定位:   ★ 2026-10-03（轮 409）承事实 323 的**具体下一步**，并落实轮 408 新立的纪律：
#   ★★ 「**判「未建成」之前，先穷举"调用前提"这一维**」—— 候选维度四选：
# ① 选区卫生 ✓（已排除）② **算例类型** ✓（已排除：thermal 让 4 条成了、temperature 仍不
# 成）
# ③ **参数单位与个数** ✓（已排除：读了 `_check` 的实现 —— arity 校核对得上、`out_i4()` 
# 也补了）
#     ④ ★ **实体种类** ← **本表要穷举的就是它**。
# ★ 而**官方文本**正好指着这个维度：`ICWLoadsAndRestraintsManager` 各条的 Parameters 段
# 写着
#     · `AddConvection`「faces or **shell edges**」· `AddHeatFlux`「faces or shell edges」
#     · `AddHeatPower`「bodies, faces, edges, and **vertices**」
#     · `AddTemperature`「entities (**faces, edges, and vertices**)」
#     ⇒ ★★ 即：★ **它们各自允许的实体种类不同** —— ★ 而我此前**一律只给"一个面"**。
# 官方依据: `D:\AI\SW\_raw\cosworks_signatures.md`（★ 逐条的 Parameters 段，转储自官方页
#           ）·
#   `ICWLoadsAndRestraintsManager~Add*.html`（CHM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每格 ⇒ **回读计数恰好 +1**（★ 而"哪一格成"就是这张表的价值）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "load-entity-kinds-evidence.json")
STUDY = "DSH-KINDS"


def main() -> int:
    import sw_connect
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts.sw_selection_spec import select_entity_by_index
    from scripts import sw_simulation_loads as SL

    ev: dict = {"grid": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        sim.create_static_study(sw, STUDY, study_type=3)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, STUDY))
        ev["study_type"] = 3

        loads = [
            ("convection", SL.apply_convection_report, ()),
            ("heat_flux", SL.apply_heat_flux_report, ()),
            ("heat_power", SL.apply_heat_power_report, ()),
            ("temperature", SL.apply_temperature_report, ()),
            ("radiation", SL.apply_radiation_report, (0,)),
        ]
        kinds = ("FACE", "EDGE", "VERTEX")
        for label, fn, extra in loads:
            row = {}
            for kind in kinds:
                try:
                    sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                    if kind == "FACE":
                        sim.select_face_at(doc, 0.0, 0.0, 0.0)
                    else:
                        select_entity_by_index(doc, kind, 0)
                    rep = fn(mgr, doc, *extra)
                    row[kind] = {"ok": bool(isinstance(rep, dict) and rep.get("ok")),
                                 "count": [rep.get("count_before"), rep.get("count_after")]
                                 if isinstance(rep, dict) else None,
                                 "err": (rep.get("error") or "")[:60]
                                 if isinstance(rep, dict) else None}
                except Exception as exc:                       # noqa: BLE001
                    row[kind] = {"ok": False,
                                 "err": "%s: %s" % (type(exc).__name__, str(exc)[:70])}
            ev["grid"][label] = row
        wins = {"%s/%s" % (k, kk) for k, r in ev["grid"].items()
                for kk, v in r.items() if v.get("ok")}
        ev["successes"] = sorted(wins)
        ev["verdict"] = "pass" if wins else "partial"
        ev["note"] = ("★ **实体种类 × 载荷** 的穷举表（★ 官方文本说这族各自要求的实体种类不同）—— "
                      "★ 落成一张表而不是「改一处试一次」。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        for label, _fn, _e in loads:
            cells = " | ".join("%s:%s" % (kk, "✓" if ev["grid"][label][kk].get("ok") else "✗")
                               for kk in kinds)
            print("  %-14s %s" % (label, cells))
        print("  成功格：%s" % (ev["successes"] or "（无）"))
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
