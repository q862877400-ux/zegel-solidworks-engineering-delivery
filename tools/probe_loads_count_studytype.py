"""★ 真机诊断：`ICWLoadsAndRestraintsManager.Count` 在**静力**与**热**算例上分别是什么。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_loads_count_studytype.py
# 定位:   ★ 2026-10-03（轮 414）承 A 组收尾三条的**实测异常**：★ 它们在**静力**算例上
#   回 `count: [-1, -1]`（★ `-1` 是 `sw_simulation_loads._loads_count` 约定的
#   「**取不到**」—— ★ 它**不静默成 0**，★ 那是对的）。
#   ★★ 而**热算例**上同一条路（轮 408）回的是 `0→1→2→3` 的**正常计数** ⇒ 矛盾。
#   ⇒ ★ 本探针只做一件事：★ **把 `manager.Count` 的原始取值/报错**分别打出来
#     （★ 而不是继续在能力层猜）。
# 官方依据: `ICWLoadsAndRestraintsManager.Count`（官方属性）·
#   `swsAnalysisStudyTypeStatic = 0` / `swsAnalysisStudyTypeThermal = 3`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "loads-count-studytype-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)

    ev: dict = {"cases": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        for label, st in (("static", 0), ("thermal", 3)):
            case: dict = {"study_type": st}
            try:
                name = "DSH-C_%s" % label
                sim.create_static_study(sw, name, study_type=st)
                stud = sim.get_study_by_name(sw, name)
                mgr = sim._loads_and_restraints_manager(stud)
                case["manager"] = type(mgr).__name__
                try:
                    case["count_via_get"] = repr(get_com_member(mgr, "Count"))
                except Exception as exc:                       # noqa: BLE001
                    case["count_via_get_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
                try:
                    case["count_via_attr"] = repr(mgr.Count)
                except Exception as exc:                       # noqa: BLE001
                    case["count_via_attr_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
                #: ★ 也试一下"取载荷对象"那条路（`GetLoadsAndRestraints`？）—— ★ 只试名
                #: 字，不猜语义
                for attr in ("GetLoadsAndRestraints", "GetLoadCount"):
                    try:
                        case["%s" % attr] = repr(get_com_member(mgr, attr))[:70]
                    except Exception as exc:                   # noqa: BLE001
                        case["%s_err" % attr] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
            except Exception as exc:                           # noqa: BLE001
                case["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
            ev["cases"][label] = case
        ev["verdict"] = "pass" if ev["cases"] else "partial"
        ev["note"] = ("★ 只问一件事：★ `ICWLoadsAndRestraintsManager.Count` 在**静力**与**热**算例上"
                      "分别是什么（★ 原始取值/报错）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1400])
        print("  产物: %s" % OUT)
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
