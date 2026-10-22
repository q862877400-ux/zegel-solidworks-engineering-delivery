"""★ 真机：**每格一个新算例**重搭"实体种类 × 载荷"表（★ 做法①，★ 治上一版的格子污染）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_load_entity_kinds_clean.py
# 定位:   ★ 2026-10-03（轮 410）承**事实 324**：★ 上一版那张表**不成立** ——
#   ★★ 因为那些载荷都写在**同一个 `ICWLoadsAndRestraintsManager`** 上，
#     ★ 于是"**失败的** `Add*` 调用"会**污染下一格**（★ 真机表现：`heat_flux` 在 FACE 上
#     从轮 408 的 ✓ 变成 ✗，★ 而两次唯一差别是"中间夹了失败的 EDGE/VERTEX 尝试"）。
# ⇒ ★★ 正解用的是事实 324 里的**做法①**：★ **每一格建一个新算例**（★ 算例是载荷的宿主）
# 。
#   ★ 顺序也记下来（事实 324：★ "先试 A 再试 B"与反过来可能不同）。
# 官方依据: `D:\AI\SW\_raw\cosworks_signatures.md` 里各条的 Parameters 段
# （`AddConvection`「faces or shell edges」· `AddHeatPower`「bodies, faces, edges, and v
# ertices」·
#    `AddTemperature`「faces, edges, and vertices」）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每格 ⇒ **回读计数恰好 +1**；★ 而"哪一格成"要在**独立**的前提下才可信。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1]
    / "output"
    / "load-entity-kinds-clean-evidence.json"
)


def main() -> int:
    import sw_connect

    from scripts import sw_simulation as sim
    from scripts import sw_simulation_loads as sl
    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )
    from scripts.sw_selection_spec import select_entity_by_index

    ev: dict = {"grid": {}, "order": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)

        loads = [
            ("convection", sl.apply_convection_report, ()),
            ("heat_flux", sl.apply_heat_flux_report, ()),
            ("heat_power", sl.apply_heat_power_report, ()),
            ("temperature", sl.apply_temperature_report, ()),
            ("radiation", sl.apply_radiation_report, (0,)),
        ]
        kinds = ("FACE", "EDGE", "VERTEX")
        for label, fn, extra in loads:
            row = {}
            for kind in kinds:
                study = "K_%s_%s" % (label, kind)
                ev["order"].append(study)
                cell: dict = {"study": study}
                try:
                    #: ★★ **每一格一个新算例**（★ 做法① —— 那条宿主是"污染"的载体）
                    sim.create_static_study(sw, study, study_type=3)
                    mgr = sim._loads_and_restraints_manager(
                        sim.get_study_by_name(sw, study)
                    )
                    sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                    if kind == "FACE":
                        sim.select_face_at(doc, 0.0, 0.0, 0.0)
                    else:
                        select_entity_by_index(doc, kind, 0)
                    rep = fn(mgr, doc, *extra)
                    cell["ok"] = bool(isinstance(rep, dict) and rep.get("ok"))
                    cell["count"] = (
                        [rep.get("count_before"), rep.get("count_after")]
                        if isinstance(rep, dict)
                        else None
                    )
                    cell["err"] = (
                        (rep.get("error") or "")[:70] if isinstance(rep, dict) else None
                    )
                except Exception as exc:  # noqa: BLE001
                    cell["ok"] = False
                    cell["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
                row[kind] = cell
            ev["grid"][label] = row
        wins = [
            "%s/%s" % (k, kk)
            for k, r in ev["grid"].items()
            for kk, v in r.items()
            if v.get("ok")
        ]
        ev["successes"] = wins
        ev["verdict"] = "pass" if wins else "partial"
        ev["note"] = (
            "★ **每格一个新算例**（事实 324 的做法①）—— ★ 治的是「失败的调用污染下一格」。"
            "★ 顺序也记在 `order` 里。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        for label, _fn, _e in loads:
            cells = " | ".join(
                "%s:%s" % (kk, "✓" if ev["grid"][label][kk].get("ok") else "✗")
                for kk in kinds
            )
            print("  %-14s %s" % (label, cells))
        print("  成功格（%d）：%s" % (len(wins), wins))
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
